using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Net.WebSockets;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

[InitializeOnLoad]
public static class MCPBridge
{
    static MCPBridge() => Start();
    public const int Port = 6400;

    public enum Status { Stopped, Running }

    public static Status CurrentStatus { get; private set; } = Status.Stopped;
    public static int ConnectedClients => Volatile.Read(ref _clientCount);
    public static event Action StateChanged;

    static TcpListener _listener;
    static CancellationTokenSource _cts;
    static int _clientCount;

    static readonly Queue<(string payload, Action<string> respond)> _mainThreadQueue = new();
    static readonly object _queueLock = new();

    // ── Lifecycle ──────────────────────────────────────────────────────────

    public static void Start()
    {
        if (CurrentStatus == Status.Running) return;

        _cts = new CancellationTokenSource();
        _listener = new TcpListener(IPAddress.Any, Port);
        _listener.Start();

        _clientCount = 0;
        CurrentStatus = Status.Running;

        Task.Run(() => AcceptLoop(_cts.Token));
        EditorApplication.update += FlushMainThreadQueue;

        StateChanged?.Invoke();
        Debug.Log($"[MCPBridge] Listening on ws://localhost:{Port}/");
    }

    public static void Stop()
    {
        if (CurrentStatus == Status.Stopped) return;

        EditorApplication.update -= FlushMainThreadQueue;
        _cts?.Cancel();

        var listenerToStop = _listener;
        _listener = null;
        Task.Run(() => { try { listenerToStop?.Stop(); } catch { } });

        _clientCount = 0;
        CurrentStatus = Status.Stopped;

        StateChanged?.Invoke();
        Debug.Log("[MCPBridge] Stopped.");
    }

    static bool _pendingStateChanged;

    static void NotifyStateChanged() =>
        Volatile.Write(ref _pendingStateChanged, true);

    // ── TCP accept loop (background thread) ────────────────────────────────

    static async Task AcceptLoop(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            TcpClient client;
            try { client = await _listener.AcceptTcpClientAsync(); }
            catch { break; }

            _ = Task.Run(() => HandleClient(client, ct), ct);
        }
    }

    static async Task HandleClient(TcpClient client, CancellationToken ct)
    {
        using (client)
        {
            var stream = client.GetStream();
            try
            {
                if (!await DoWebSocketHandshake(stream, ct)) return;
            }
            catch { return; }

            Interlocked.Increment(ref _clientCount);
            NotifyStateChanged();

            try { await ServeWebSocket(stream, ct); }
            catch { }

            InterlockedDecrementClamp(ref _clientCount);
            NotifyStateChanged();
        }
    }

    // ── WebSocket handshake ────────────────────────────────────────────────

    static async Task<bool> DoWebSocketHandshake(NetworkStream stream, CancellationToken ct)
    {
        var buf = new byte[4096];
        int total = 0;
        while (total < buf.Length)
        {
            int n = await stream.ReadAsync(buf, total, buf.Length - total, ct);
            if (n == 0) return false;
            total += n;
            string text = Encoding.UTF8.GetString(buf, 0, total);
            if (text.Contains("\r\n\r\n")) break;
        }

        string request = Encoding.UTF8.GetString(buf, 0, total);
        string wsKey = null;
        foreach (string line in request.Split('\n'))
        {
            if (line.StartsWith("Sec-WebSocket-Key:", StringComparison.OrdinalIgnoreCase))
            {
                wsKey = line.Substring("Sec-WebSocket-Key:".Length).Trim();
                break;
            }
        }

        if (wsKey == null)
        {
            byte[] reject = Encoding.UTF8.GetBytes("HTTP/1.1 400 Bad Request\r\n\r\n");
            await stream.WriteAsync(reject, 0, reject.Length, ct);
            return false;
        }

        string accept = Convert.ToBase64String(
            SHA1.Create().ComputeHash(
                Encoding.UTF8.GetBytes(wsKey + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11")));

        string response =
            "HTTP/1.1 101 Switching Protocols\r\n" +
            "Upgrade: websocket\r\n" +
            "Connection: Upgrade\r\n" +
            $"Sec-WebSocket-Accept: {accept}\r\n\r\n";

        byte[] responseBytes = Encoding.UTF8.GetBytes(response);
        await stream.WriteAsync(responseBytes, 0, responseBytes.Length, ct);
        return true;
    }

    // ── WebSocket frame I/O ────────────────────────────────────────────────

    static async Task ServeWebSocket(NetworkStream stream, CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            string message = await ReadFrame(stream, ct);
            if (message == null) return;

            var tcs = new TaskCompletionSource<string>();
            lock (_queueLock)
                _mainThreadQueue.Enqueue((message, r => tcs.SetResult(r)));

            string reply;
            try { reply = await tcs.Task; }
            catch (Exception ex) { reply = Error(ex.Message); }

            await WriteFrame(stream, reply, ct);
        }
    }

    static async Task<string> ReadFrame(NetworkStream stream, CancellationToken ct)
    {
        byte[] header = new byte[2];
        if (!await ReadExact(stream, header, ct)) return null;

        bool masked = (header[1] & 0x80) != 0;
        int opcode = header[0] & 0x0F;
        if (opcode == 8) return null; // close frame

        long length = header[1] & 0x7F;
        if (length == 126)
        {
            byte[] ext = new byte[2];
            if (!await ReadExact(stream, ext, ct)) return null;
            length = (ext[0] << 8) | ext[1];
        }
        else if (length == 127)
        {
            byte[] ext = new byte[8];
            if (!await ReadExact(stream, ext, ct)) return null;
            length = 0;
            for (int i = 0; i < 8; i++) length = (length << 8) | ext[i];
        }

        byte[] mask = new byte[4];
        if (masked && !await ReadExact(stream, mask, ct)) return null;

        byte[] data = new byte[length];
        if (!await ReadExact(stream, data, ct)) return null;

        if (masked)
            for (int i = 0; i < data.Length; i++)
                data[i] ^= mask[i % 4];

        return Encoding.UTF8.GetString(data);
    }

    static async Task WriteFrame(NetworkStream stream, string message, CancellationToken ct)
    {
        byte[] payload = Encoding.UTF8.GetBytes(message);
        var frame = new List<byte>();
        frame.Add(0x81); // FIN + text opcode
        if (payload.Length <= 125)
            frame.Add((byte)payload.Length);
        else if (payload.Length <= 65535)
        {
            frame.Add(126);
            frame.Add((byte)(payload.Length >> 8));
            frame.Add((byte)(payload.Length & 0xFF));
        }
        else
        {
            frame.Add(127);
            for (int i = 7; i >= 0; i--)
                frame.Add((byte)((payload.Length >> (i * 8)) & 0xFF));
        }
        frame.AddRange(payload);
        byte[] frameArr = frame.ToArray();
        await stream.WriteAsync(frameArr, 0, frameArr.Length, ct);
    }

    static async Task<bool> ReadExact(NetworkStream stream, byte[] buf, CancellationToken ct)
    {
        int offset = 0;
        while (offset < buf.Length)
        {
            int n = await stream.ReadAsync(buf, offset, buf.Length - offset, ct);
            if (n == 0) return false;
            offset += n;
        }
        return true;
    }

    // ── Main-thread dispatcher ─────────────────────────────────────────────

    static void FlushMainThreadQueue()
    {
        if (Volatile.Read(ref _pendingStateChanged))
        {
            Volatile.Write(ref _pendingStateChanged, false);
            StateChanged?.Invoke();
        }

        while (true)
        {
            (string payload, Action<string> respond) item;
            lock (_queueLock)
            {
                if (_mainThreadQueue.Count == 0) return;
                item = _mainThreadQueue.Dequeue();
            }
            string response;
            try { response = Dispatch(item.payload); }
            catch (Exception ex) { response = Error(ex.Message); }
            item.respond(response);
        }
    }

    // ── Command dispatcher ─────────────────────────────────────────────────

    static string Dispatch(string payload)
    {
        var req = JsonUtility.FromJson<Request>(payload);
        return req.command switch
        {
            "ping"              => Ok(JsonString("pong")),
            "get_scene_info"    => GetSceneInfo(),
            "list_gameobjects"  => ListGameObjects(),
            "get_components"    => GetComponents(req.arg),
            "execute_menu_item" => ExecuteMenuItem(req.arg),
            "play"              => SetPlayMode(true),
            "stop"              => SetPlayMode(false),
            "get_logs"          => GetLogs(),
            "read_file"         => ReadFile(req.arg),
            "write_file"        => WriteFile(req.arg, req.content),
            "list_scripts"      => ListScripts(req.arg),
            "refresh_assets"    => RefreshAssets(),
            "destroy_gameobject"  => DestroyGameObject(req.arg),
            "create_gameobject"   => CreateGameObject(req.arg, req.content),
            "set_transform"       => SetTransform(req.arg, req.content),
            "set_parent"          => SetParent(req.arg, req.content),
            "batch"               => Batch(req.content),
            "add_component"       => AddComponent(req.arg, req.content),
            _                     => Error($"Unknown command: {req.command}")
        };
    }

    // ── Commands ───────────────────────────────────────────────────────────

    static string GetSceneInfo()
    {
        var scene = SceneManager.GetActiveScene();
        return Ok(JsonUtility.ToJson(new SceneInfo
        {
            name = scene.name,
            path = scene.path,
            isDirty = scene.isDirty,
            rootCount = scene.rootCount
        }));
    }

    static string ListGameObjects()
    {
        var scene = SceneManager.GetActiveScene();
        var roots = scene.GetRootGameObjects();
        var sb = new StringBuilder("[");
        bool first = true;
        foreach (var go in roots)
            AppendGameObject(sb, go, 0, ref first);
        sb.Append("]");
        return Ok(sb.ToString());
    }

    static void AppendGameObject(StringBuilder sb, GameObject go, int depth, ref bool first)
    {
        if (!first) sb.Append(",");
        first = false;
        sb.Append($"{{\"name\":{JsonString(go.name)},\"path\":{JsonString(GetPath(go))},\"active\":{go.activeSelf.ToString().ToLower()},\"depth\":{depth},\"childCount\":{go.transform.childCount}}}");
        foreach (Transform child in go.transform)
            AppendGameObject(sb, child.gameObject, depth + 1, ref first);
    }

    static string GetComponents(string goPath)
    {
        var go = GameObject.Find(goPath);
        if (go == null) return Error($"GameObject not found: {goPath}");
        var components = go.GetComponents<Component>();
        var sb = new StringBuilder("[");
        for (int i = 0; i < components.Length; i++)
        {
            if (i > 0) sb.Append(",");
            var c = components[i];
            sb.Append($"{{\"type\":{JsonString(c?.GetType().FullName ?? "null")}}}");
        }
        sb.Append("]");
        return Ok(sb.ToString());
    }

    static string ExecuteMenuItem(string menuPath)
    {
        bool ok = EditorApplication.ExecuteMenuItem(menuPath);
        return ok ? Ok(JsonString($"Executed: {menuPath}")) : Error($"MenuItem not found: {menuPath}");
    }

    static string SetPlayMode(bool play)
    {
        EditorApplication.isPlaying = play;
        return Ok(JsonString(play ? "Entering play mode" : "Exiting play mode"));
    }

    static string GetLogs()
    {
        string logPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
            ".config/unity3d/Editor.log");

        if (!File.Exists(logPath)) return Error("Editor.log not found");

        var lines = File.ReadAllLines(logPath);
        int start = Math.Max(0, lines.Length - 200);
        var tail = string.Join("\n", lines, start, lines.Length - start);
        return Ok(JsonString(tail));
    }

    static string ReadFile(string projectRelativePath)
    {
        string full = Path.Combine(Application.dataPath, "..", projectRelativePath);
        if (!File.Exists(full)) return Error($"File not found: {projectRelativePath}");
        return Ok(JsonString(File.ReadAllText(full)));
    }

    static string WriteFile(string projectRelativePath, string content)
    {
        string full = Path.Combine(Application.dataPath, "..", projectRelativePath);
        Directory.CreateDirectory(Path.GetDirectoryName(full)!);
        File.WriteAllText(full, content);
        AssetDatabase.Refresh();
        return Ok(JsonString($"Written: {projectRelativePath}"));
    }

    static string ListScripts(string folder)
    {
        string root = string.IsNullOrEmpty(folder)
            ? Application.dataPath
            : Path.Combine(Application.dataPath, folder);

        if (!Directory.Exists(root)) return Error($"Folder not found: {folder}");

        var files = Directory.GetFiles(root, "*.cs", SearchOption.AllDirectories);
        var sb = new StringBuilder("[");
        for (int i = 0; i < files.Length; i++)
        {
            if (i > 0) sb.Append(",");
            string rel = files[i].Replace(Application.dataPath, "Assets").Replace("\\", "/");
            sb.Append(JsonString(rel));
        }
        sb.Append("]");
        return Ok(sb.ToString());
    }

    static string RefreshAssets()
    {
        AssetDatabase.Refresh();
        return Ok(JsonString("Asset database refreshed"));
    }

    static string DestroyGameObject(string goPath)
    {
        var go = GameObject.Find(goPath);
        if (go == null) return Error($"GameObject not found: {goPath}");
        Undo.DestroyObjectImmediate(go);
        return Ok(JsonString($"Destroyed: {goPath}"));
    }

    // arg: name, content: "Cube"|"Sphere"|"Empty" (primitive type or empty)
    static string CreateGameObject(string name, string type)
    {
        GameObject go;
        if (string.IsNullOrEmpty(type) || type == "Empty")
        {
            go = new GameObject(name);
            Undo.RegisterCreatedObjectUndo(go, "Create GameObject");
        }
        else if (System.Enum.TryParse<PrimitiveType>(type, true, out var pt))
        {
            go = GameObject.CreatePrimitive(pt);
            go.name = name;
            Undo.RegisterCreatedObjectUndo(go, "Create GameObject");
        }
        else
        {
            return Error($"Unknown type: {type}. Use Empty, Cube, Sphere, Cylinder, Capsule, Plane, Quad.");
        }
        return Ok(JsonString(GetPath(go)));
    }

    // arg: path, content: "px,py,pz|sx,sy,sz|rx,ry,rz"
    static string SetTransform(string goPath, string data)
    {
        var go = GameObject.Find(goPath);
        if (go == null) return Error($"GameObject not found: {goPath}");

        var parts = data.Split('|');
        if (parts.Length != 3) return Error("content must be 'px,py,pz|sx,sy,sz|rx,ry,rz'");

        if (TryParseVec3(parts[0], out var pos)) go.transform.localPosition = pos;
        if (TryParseVec3(parts[1], out var scale)) go.transform.localScale = scale;
        if (TryParseVec3(parts[2], out var rot)) go.transform.localEulerAngles = rot;

        Undo.RecordObject(go.transform, "Set Transform");
        return Ok(JsonString($"Transform set: {goPath}"));
    }

    // arg: child path, content: parent path (empty = unparent)
    static string SetParent(string childPath, string parentPath)
    {
        var child = GameObject.Find(childPath);
        if (child == null) return Error($"Child not found: {childPath}");

        Transform parentT = null;
        if (!string.IsNullOrEmpty(parentPath))
        {
            var parent = GameObject.Find(parentPath);
            if (parent == null) return Error($"Parent not found: {parentPath}");
            parentT = parent.transform;
        }

        Undo.SetTransformParent(child.transform, parentT, "Set Parent");
        return Ok(JsonString($"Parented {childPath} -> {parentPath}"));
    }

    static string AddComponent(string goPath, string typeName)
    {
        var go = GameObject.Find(goPath);
        if (go == null) return Error($"GameObject not found: {goPath}");
        var type = System.AppDomain.CurrentDomain.GetAssemblies()
            .SelectMany(a => { try { return a.GetTypes(); } catch { return System.Array.Empty<System.Type>(); } })
            .FirstOrDefault(t => t.Name == typeName || t.FullName == typeName);
        if (type == null) return Error($"Type not found: {typeName}");
        Undo.AddComponent(go, type);
        return Ok(JsonString($"Added {typeName} to {goPath}"));
    }

    static string Batch(string jsonArray)
    {
        // Parse a JSON array of {command, arg, content} objects manually
        // Format: [{"command":"...","arg":"...","content":"..."},...]
        var results = new StringBuilder("[");
        bool first = true;

        // Use a simple approach: split on top-level objects
        var reqs = ParseBatchRequests(jsonArray);
        foreach (var r in reqs)
        {
            if (!first) results.Append(",");
            first = false;
            try { results.Append(Dispatch(JsonUtility.ToJson(r))); }
            catch (Exception ex) { results.Append(Error(ex.Message)); }
        }
        results.Append("]");
        return $"{{\"ok\":true,\"data\":{results}}}";
    }

    static List<Request> ParseBatchRequests(string json)
    {
        var list = new List<Request>();
        // Strip outer brackets
        json = json.Trim();
        if (json.StartsWith("[")) json = json.Substring(1);
        if (json.EndsWith("]")) json = json.Substring(0, json.Length - 1);

        // Split on top-level }, { boundaries
        int depth = 0;
        int start = -1;
        for (int i = 0; i < json.Length; i++)
        {
            if (json[i] == '{') { if (depth++ == 0) start = i; }
            else if (json[i] == '}')
            {
                if (--depth == 0 && start >= 0)
                {
                    var obj = json.Substring(start, i - start + 1);
                    list.Add(JsonUtility.FromJson<Request>(obj));
                    start = -1;
                }
            }
        }
        return list;
    }

    static bool TryParseVec3(string s, out Vector3 v)
    {
        v = Vector3.zero;
        var p = s.Trim().Split(',');
        if (p.Length != 3) return false;
        if (!float.TryParse(p[0], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float x)) return false;
        if (!float.TryParse(p[1], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float y)) return false;
        if (!float.TryParse(p[2], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float z)) return false;
        v = new Vector3(x, y, z);
        return true;
    }

    // ── Helpers ────────────────────────────────────────────────────────────

    static void InterlockedDecrementClamp(ref int val)
    {
        int current, next;
        do {
            current = Volatile.Read(ref val);
            next = Math.Max(0, current - 1);
        } while (Interlocked.CompareExchange(ref val, next, current) != current);
    }

    static string GetPath(GameObject go)
    {
        var sb = new StringBuilder(go.name);
        var t = go.transform.parent;
        while (t != null) { sb.Insert(0, t.name + "/"); t = t.parent; }
        return sb.ToString();
    }

    static string JsonString(string s) =>
        "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n").Replace("\r", "\\r") + "\"";

    static string Ok(string data) => $"{{\"ok\":true,\"data\":{data}}}";
    static string Error(string msg) => $"{{\"ok\":false,\"error\":{JsonString(msg)}}}";

    [Serializable] class Request { public string command; public string arg; public string content; }
    [Serializable] class SceneInfo { public string name; public string path; public bool isDirty; public int rootCount; }
}
