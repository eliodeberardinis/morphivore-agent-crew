// Headless WebGL build, driven from the command line by agent-crew/ship/ship.py.
//
// This is the last mile: without it, "get the agent's content into a playable
// build" ends with a human opening Unity and clicking through a dialog, which
// is the manual step Assignment #10 exists to remove.
//
//   Unity -quit -batchmode -nographics -projectPath . \
//         -executeMethod Morphivore.Editor.BuildScript.BuildWebGL \
//         -logFile Logs/webgl-build.log
//
// Exits non-zero on failure so the calling pipeline can tell a broken build from
// a working one without parsing the log.
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace Morphivore.Editor
{
    public static class BuildScript
    {
        const string DefaultOutput = "Builds/WebGL";

        [MenuItem("Tools/Morphivore/Build WebGL")]
        public static void BuildWebGLMenu() => Run(DefaultOutput);

        /// <summary>Entry point for -executeMethod. Reads -buildOutput from the
        /// command line if given.</summary>
        public static void BuildWebGL()
        {
            string output = ArgValue("-buildOutput") ?? DefaultOutput;
            Run(output);
        }

        static void Run(string output)
        {
            string[] scenes = EditorBuildSettings.scenes
                .Where(s => s.enabled)
                .Select(s => s.path)
                .ToArray();

            // An empty scene list silently produces a build that boots to
            // nothing, which looks like a working build until someone opens it.
            if (scenes.Length == 0)
            {
                scenes = new[] { "Assets/Scenes/SampleScene.unity" };
                Debug.Log("[Build] no scenes enabled in Build Settings; " +
                          "falling back to SampleScene.");
            }

            ConfigureWebGL();

            string absolute = Path.GetFullPath(output);
            Directory.CreateDirectory(absolute);
            Debug.Log($"[Build] WebGL -> {absolute}");
            Debug.Log($"[Build] scenes: {string.Join(", ", scenes)}");

            var options = new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = absolute,
                target = BuildTarget.WebGL,
                targetGroup = BuildTargetGroup.WebGL,
                options = BuildOptions.None,
            };

            BuildReport report = BuildPipeline.BuildPlayer(options);
            BuildSummary summary = report.summary;

            Debug.Log($"[Build] result {summary.result} — "
                      + $"{summary.totalSize / (1024 * 1024)} MB in "
                      + $"{summary.totalTime.TotalSeconds:F0}s, "
                      + $"{summary.totalErrors} error(s)");

            if (summary.result != BuildResult.Succeeded)
            {
                foreach (var step in report.steps)
                    foreach (var msg in step.messages)
                        if (msg.type == LogType.Error || msg.type == LogType.Exception)
                            Debug.LogError($"[Build] {step.name}: {msg.content}");

                if (Application.isBatchMode) EditorApplication.Exit(1);
                return;
            }

            Debug.Log("[Build] SUCCESS");
            if (Application.isBatchMode) EditorApplication.Exit(0);
        }

        /// <summary>Settings the build needs to actually run on a games host.</summary>
        static void ConfigureWebGL()
        {
            // itch.io serves .gz and .br only with the right Content-Encoding
            // headers, which it does not set on a plain zip upload. Disabling
            // compression trades a larger download for a build that loads at all.
            PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Disabled;

            // Without this the player shows Unity's default "decompression
            // fallback" warning banner on some hosts.
            PlayerSettings.WebGL.decompressionFallback = false;

            // The game builds its whole UI at 1920x1080 reference; give the
            // canvas a matching default so the HUD is legible in an itch frame.
            PlayerSettings.defaultWebScreenWidth = 1280;
            PlayerSettings.defaultWebScreenHeight = 720;

            PlayerSettings.runInBackground = true;
            PlayerSettings.WebGL.template = "APPLICATION:Default";

            // Faster, smaller builds; this project has no code that needs the
            // full exception stack at runtime.
            PlayerSettings.SetManagedStrippingLevel(
                UnityEditor.Build.NamedBuildTarget.WebGL, ManagedStrippingLevel.Low);

            PlayerSettings.productName = "Morphivore";
        }

        static string ArgValue(string flag)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length - 1; i++)
                if (args[i] == flag) return args[i + 1];
            return null;
        }
    }
}
