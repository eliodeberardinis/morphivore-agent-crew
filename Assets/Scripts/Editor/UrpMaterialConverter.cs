// Converts imported art from Built-in Render Pipeline shaders to URP.
//
// This project renders with URP; most Asset Store art still ships with Built-in
// Standard materials, which render magenta here. GDD §3.1 makes URP material
// conversion the Asset Integration Agent's job, so it lives as a repeatable tool
// rather than a hand-edit — the next pack needs the same pass.
//
// Tools → Morphivore → Convert Imported Art to URP
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

public static class UrpMaterialConverter
{
    // Only art folders. Nothing under Assets/Scripts or Settings is touched.
    static readonly string[] SearchFolders =
    {
        "Assets/Low Poly Trees Pack",
        "Assets/Tboxfinn",
        "Assets/Resources",
    };

    const string UrpLit = "Universal Render Pipeline/Lit";

    [MenuItem("Tools/Morphivore/Convert Imported Art to URP")]
    public static void Convert()
    {
        var lit = Shader.Find(UrpLit);
        if (lit == null)
        {
            Debug.LogError($"[URP] '{UrpLit}' not found — is the URP package installed?");
            return;
        }

        var folders = new List<string>();
        foreach (var f in SearchFolders)
            if (AssetDatabase.IsValidFolder(f)) folders.Add(f);

        if (folders.Count == 0) { Debug.LogWarning("[URP] no art folders found."); return; }

        var guids = AssetDatabase.FindAssets("t:Material", folders.ToArray());
        int converted = 0, skipped = 0;
        var names = new List<string>();

        foreach (var guid in guids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) continue;

            if (!NeedsConversion(mat)) { skipped++; continue; }

            // Read the Built-in properties before swapping the shader — assigning
            // a new shader drops any property the new one doesn't declare.
            Texture main   = mat.HasProperty("_MainTex")     ? mat.GetTexture("_MainTex")   : null;
            Texture bump   = mat.HasProperty("_BumpMap")     ? mat.GetTexture("_BumpMap")   : null;
            Color   tint   = mat.HasProperty("_Color")       ? mat.GetColor("_Color")       : Color.white;
            float   metal  = mat.HasProperty("_Metallic")    ? mat.GetFloat("_Metallic")    : 0f;
            float   gloss  = mat.HasProperty("_Glossiness")  ? mat.GetFloat("_Glossiness")  : 0.5f;

            mat.shader = lit;

            if (main != null) { mat.SetTexture("_BaseMap", main); mat.mainTexture = main; }
            if (bump != null)
            {
                mat.SetTexture("_BumpMap", bump);
                mat.EnableKeyword("_NORMALMAP");
            }
            mat.SetColor("_BaseColor", tint);
            mat.SetFloat("_Metallic", metal);
            // URP calls it smoothness, and it maps 1:1 from Built-in glossiness.
            mat.SetFloat("_Smoothness", gloss);

            EditorUtility.SetDirty(mat);
            converted++;
            names.Add(System.IO.Path.GetFileName(path));
        }

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        Debug.Log($"[URP] converted {converted} material(s), left {skipped} already-URP alone." +
                  (converted > 0 ? "\n  " + string.Join("\n  ", names) : ""));
    }

    // A material needs converting if its shader is missing, or is one of the
    // Built-in pipeline families that URP cannot render.
    static bool NeedsConversion(Material mat)
    {
        if (mat.shader == null) return true;

        string n = mat.shader.name;
        if (n.StartsWith("Universal Render Pipeline/")) return false;
        if (n.StartsWith("Shader Graphs/"))             return false; // authored for URP already

        return n == "Standard"
            || n == "Standard (Specular setup)"
            || n.StartsWith("Legacy Shaders/")
            || n.StartsWith("Mobile/")
            || n == "Hidden/InternalErrorShader";
    }
}
