// Scatters a biome's imported props across the terrain.
//
// Art is referenced through art-manifest.json rather than by direct path, which
// is §4.10's rule: once imported prefabs exist, a code revert can otherwise leave
// the generator pointing at a renamed asset, producing a build that compiles,
// enters Play mode, and spawns nothing. Every failed lookup is named in the log,
// and if a set resolves to nothing at all the caller's fallback runs instead.
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Morphivore.World
{
    public static class PropScatter
    {
        [System.Serializable]
        public class PropSet
        {
            public string   biome;
            public int      count;
            public int      clusters;
            public float    cluster_radius;
            public float    min_height;
            public float    max_height;
            public string[] props;
        }

        [System.Serializable] class Manifest { public PropSet[] sets; }

        static Manifest manifest;
        static bool     manifestLoaded;

        public static PropSet SetFor(string biomeId)
        {
            if (!manifestLoaded)
            {
                manifestLoaded = true;
                try
                {
                    string path = Path.Combine(Application.streamingAssetsPath, "art-manifest.json");
                    manifest = JsonUtility.FromJson<Manifest>(File.ReadAllText(path));
                }
                catch (System.Exception e)
                {
                    Debug.LogWarning($"[Art] art-manifest.json unreadable ({e.Message}) — props fall back to primitives.");
                    manifest = null;
                }
            }

            if (manifest?.sets == null) return null;
            foreach (var s in manifest.sets)
                if (s != null && s.biome == biomeId) return s;
            return null;
        }

        /// <summary>Scatters the biome's props onto the live terrain. Returns false
        /// if the manifest or its art is missing, so the caller can fall back.</summary>
        public static bool Scatter(string biomeId, Transform parent)
        {
            var set = SetFor(biomeId);
            if (set?.props == null || set.props.Length == 0)
            {
                Debug.LogWarning($"[Art] no prop set for biome '{biomeId}'.");
                return false;
            }

            // Resolve every path up front and name the ones that fail — a renamed
            // asset should be a line in the console, not an empty field.
            var loaded  = new List<GameObject>();
            var missing = new List<string>();
            foreach (var p in set.props)
            {
                var go = Resources.Load<GameObject>(p);
                if (go != null) loaded.Add(go);
                else            missing.Add(p);
            }

            if (missing.Count > 0)
                Debug.LogError($"[Art] {missing.Count} prop(s) in art-manifest.json did not resolve: " +
                               string.Join(", ", missing));

            if (loaded.Count == 0)
            {
                Debug.LogError($"[Art] biome '{biomeId}' resolved no props at all — falling back to primitives.");
                return false;
            }

            // Clustered rather than uniform: the Prairies is "rolling fields and
            // scattered treelines" (§2.7), and evenly-spread trees read as an
            // orchard rather than open grassland.
            float r = BiomeTerrain.Radius * 0.92f;
            int   clusterCount = Mathf.Max(1, set.clusters);
            var   centres = new Vector2[clusterCount];
            for (int i = 0; i < clusterCount; i++)
                centres[i] = new Vector2(Random.Range(-r, r), Random.Range(-r, r));

            int placed = 0;
            for (int i = 0; i < set.count; i++)
            {
                Vector2 c = centres[Random.Range(0, clusterCount)];
                Vector2 o = Random.insideUnitCircle * set.cluster_radius;
                float x = Mathf.Clamp(c.x + o.x, -r, r);
                float z = Mathf.Clamp(c.y + o.y, -r, r);

                var src  = loaded[Random.Range(0, loaded.Count)];
                var tree = Object.Instantiate(src, parent);

                // Scale to a real height in world units. The pack's own units are
                // whatever they are; what matters is how a tree reads beside a
                // ~1-unit creature, so normalise by measured bounds.
                float target = Random.Range(set.min_height, set.max_height);
                float native = MeasureHeight(tree);
                float scale  = native > 0.01f ? target / native : 1f;
                tree.transform.localScale = Vector3.one * scale;

                tree.transform.position = new Vector3(x, BiomeTerrain.HeightAt(x, z), z);
                tree.transform.rotation = Quaternion.Euler(0f, Random.Range(0f, 360f), 0f);

                // Solid, so the player and enemies depenetrate against them. The
                // capsule-collider prefab variant is chosen deliberately: obstacle
                // resolution uses Physics.ComputePenetration, which is exact
                // against convex primitives and unreliable against concave meshes.
                tree.AddComponent<Obstacle>();
                placed++;
            }

            Debug.Log($"[Art] scattered {placed} props across {clusterCount} clusters " +
                      $"in '{biomeId}' from {loaded.Count} prefab(s).");
            return true;
        }

        // World-space height of an instantiated prefab at scale 1.
        static float MeasureHeight(GameObject go)
        {
            var rends = go.GetComponentsInChildren<Renderer>();
            if (rends.Length == 0) return 0f;

            var b = rends[0].bounds;
            for (int i = 1; i < rends.Length; i++) b.Encapsulate(rends[i].bounds);
            return b.size.y;
        }
    }
}
