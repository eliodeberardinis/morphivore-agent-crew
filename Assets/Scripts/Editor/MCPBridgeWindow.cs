using UnityEditor;
using UnityEngine;

public class MCPBridgeWindow : EditorWindow
{
    static readonly Color _green = new(0.2f, 0.8f, 0.3f);
    static readonly Color _red   = new(0.9f, 0.3f, 0.3f);

    [MenuItem("MCP/Bridge Window")]
    static void Open() => GetWindow<MCPBridgeWindow>("MCP Bridge");

    void OnEnable()  => MCPBridge.StateChanged += Repaint;
    void OnDisable() => MCPBridge.StateChanged -= Repaint;

    void OnGUI()
    {
        bool running = MCPBridge.CurrentStatus == MCPBridge.Status.Running;

        GUILayout.Space(12);

        // ── Status indicator ───────────────────────────────────────────────
        var prevColor = GUI.color;
        GUI.color = running ? _green : _red;
        GUILayout.Label(
            running
                ? $"● Connected  —  {MCPBridge.ConnectedClients} client{(MCPBridge.ConnectedClients == 1 ? "" : "s")}  (port {MCPBridge.Port})"
                : "● Stopped",
            EditorStyles.boldLabel);
        GUI.color = prevColor;

        GUILayout.Space(8);

        // ── Start / Stop button ────────────────────────────────────────────
        if (running)
        {
            if (GUILayout.Button("Stop Bridge", GUILayout.Height(32)))
                MCPBridge.Stop();
        }
        else
        {
            if (GUILayout.Button("Start Bridge", GUILayout.Height(32)))
                MCPBridge.Start();
        }
    }
}
