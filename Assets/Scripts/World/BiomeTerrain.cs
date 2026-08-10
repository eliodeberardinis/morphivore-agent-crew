// Owns the ground. Wraps the Tboxfinn Procedural Map Generator, which produces
// exactly the shape the GDD asks for (§2.7): a seeded, bounded, flat-shaded
// island rather than endless chunks.
//
// The package's components are ordinary MonoBehaviours with public fields, so
// they are created and driven entirely from code here — the scene stays empty
// and the whole terrain remains a `git revert` of Assets/Scripts/ away, which is
// the property §4.10 leans on.
//
// The package is Asset Store licensed: it ships fine inside a built game, but
// Assets/Tboxfinn/ must never reach a public repo. This file is the only place
// the rest of the codebase touches it — swapping the generator means rewriting
// BuildMesh() and nothing else.
using System.Collections;
using UnityEngine;
using Tboxfinn.ProceduralMap;

namespace Morphivore.World
{
    [RequireComponent(typeof(MeshFilter), typeof(MeshRenderer), typeof(MeshCollider))]
    public class BiomeTerrain : MonoBehaviour
    {
        public static BiomeTerrain Active { get; private set; }

        /// <summary>True once a mesh exists and heights can be sampled.</summary>
        public bool IsReady { get; private set; }

        MapGenerator  gen;
        MeshFilter    meshFilter;
        MeshRenderer  meshRenderer;
        MeshCollider  meshCollider;

        // The height map the live mesh was built from, kept for SampleHeight.
        float[,] heightMap;
        float    heightMultiplier;
        AnimationCurve heightCurve;

        // The generator emits a mesh `mapChunkSize` units across, centred on the
        // origin. The world is GameConfig.WorldSize across, so the whole object is
        // scaled to fit — heights included, which is why the multiplier is tuned
        // against the scaled result rather than raw units.
        float worldScale = 1f;

        /// <summary>Generation runs on a worker thread, so the mesh does not exist
        /// in the calling frame. Anything that must be *placed* on the ground —
        /// as opposed to walking, which self-corrects — waits for onReady.</summary>
        public static BiomeTerrain Build(int seed, TerrainProfile profile, System.Action onReady = null)
        {
            var go = new GameObject("BiomeTerrain");
            var terrain = go.AddComponent<BiomeTerrain>();
            terrain.readyCallback = onReady;
            terrain.Generate(seed, profile);
            Active = terrain;
            return terrain;
        }

        System.Action readyCallback;

        /// <summary>Per-biome terrain shape. Defaults produce the Prairies: open,
        /// gently rolling ground with no traversal gates anywhere (§2.7).</summary>
        public struct TerrainProfile
        {
            public float noiseScale;
            public int   octaves;
            public float persistance;
            public float lacunarity;
            public float heightMultiplier;
            public Color groundColor;

            public static TerrainProfile Prairies(Color ground) => new TerrainProfile
            {
                noiseScale       = 42f,
                octaves          = 4,
                persistance      = 0.45f,
                lacunarity       = 2f,
                // Rolling, not mountainous: relief you can read and walk over from
                // anywhere, because the Prairies has no traversal gates at all.
                heightMultiplier = 14f,
                groundColor      = ground
            };
        }

        void Generate(int seed, TerrainProfile profile)
        {
            meshFilter   = GetComponent<MeshFilter>();
            meshRenderer = GetComponent<MeshRenderer>();
            meshCollider = GetComponent<MeshCollider>();

            // Flat-shaded low-poly sits well beside procedurally-built cube
            // creatures, and is what the package is built for.
            var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            mat.color = profile.groundColor;
            meshRenderer.sharedMaterial = mat;

            // AddComponent runs MapGenerator.Awake, which builds the falloff maps
            // that turn the noise into an island. Tuning fields are set after,
            // because GenerateMapData reads them at call time.
            gen = gameObject.AddComponent<MapGenerator>();
            gen.seed          = seed;
            gen.GameSeed      = "";           // numeric seed wins; ours comes from the run
            gen.noiseScale    = profile.noiseScale;
            gen.octaves       = profile.octaves;
            gen.persistance   = profile.persistance;
            gen.lacunarity    = profile.lacunarity;
            gen.offset        = Vector2.zero;
            gen.normalizeMode = Noise.NormalizeMode.Local; // one bounded island, not a chunk of many
            gen.useFallofMap  = true;                      // island shape: land in the middle, edges fall away
            gen.useFallofMap2 = false;
            gen.useFlatShading = true;
            gen.meshHeightMultiplier = profile.heightMultiplier;

            // GenerateTerrainMesh evaluates this curve per vertex, and an empty
            // AnimationCurve evaluates to 0 everywhere — which silently yields a
            // flat plane. It must be set.
            gen.meshHeightCurve = heightCurve = BuildHeightCurve();
            heightMultiplier    = profile.heightMultiplier;

            worldScale = GameConfig.WorldSize / MapGenerator.mapChunkSize;
            transform.localScale = new Vector3(worldScale, worldScale, worldScale);

            StartCoroutine(BuildMesh());
        }

        // Flat near the bottom so low ground reads as a level plain rather than a
        // shallow bowl, then rising — the shape that gives an island a beach.
        static AnimationCurve BuildHeightCurve() => new AnimationCurve(
            new Keyframe(0f,   0f,   0f, 0f),
            new Keyframe(0.3f, 0.05f, 0.5f, 0.5f),
            new Keyframe(1f,   1f,   2f, 0f));

        IEnumerator BuildMesh()
        {
            // The package generates on a worker thread and dispatches the result
            // from its own Update, so both steps are awaited rather than called.
            MapData? map = null;
            gen.RequestMapData(Vector2.zero, d => map = d);
            while (map == null) yield return null;

            MeshData mesh = null;
            gen.RequestMeshData(map.Value, 0, m => mesh = m);
            while (mesh == null) yield return null;

            heightMap = map.Value.heightMap;

            var built = mesh.CreateMesh();
            meshFilter.sharedMesh   = built;
            meshCollider.sharedMesh = built;

            IsReady = true;

            // Terrain is generated, so its extent and relief are worth stating:
            // a flat log line here is the difference between "the island is a
            // bowl" being a five-minute look and a half-hour hunt.
            float lo = float.MaxValue, hi = float.MinValue;
            for (int y = 0; y < heightMap.GetLength(1); y++)
            for (int x = 0; x < heightMap.GetLength(0); x++)
            {
                float h = heightCurve.Evaluate(heightMap[x, y]) * heightMultiplier * worldScale;
                if (h < lo) lo = h;
                if (h > hi) hi = h;
            }
            Debug.Log($"[Terrain] seed {gen.seed}: {built.vertexCount} verts, " +
                      $"{GameConfig.WorldSize:0}u across, height {lo:0.0}–{hi:0.0}, " +
                      $"centre {SampleHeight(Vector3.zero):0.0}");

            readyCallback?.Invoke();
            readyCallback = null;
        }

        /// <summary>Half-width of the island. Bodies are kept inside this so
        /// nothing walks off the mesh into empty space.</summary>
        public static float Radius => GameConfig.WorldSize * 0.5f - 2f;

        // ── Height sampling ───────────────────────────────────────────────────
        // Everything that walks reads its Y from here (C1b). Sampled off the
        // height map rather than raycast: it is exact, allocation-free, and works
        // for creatures standing inside each other's colliders.

        /// <summary>Ground height in world space under a world-space position.
        /// Returns 0 until the mesh exists, which is the old flat-plane height —
        /// so anything calling this before the terrain is ready behaves as it did.</summary>
        public float SampleHeight(Vector3 worldPos)
        {
            if (!IsReady || heightMap == null) return 0f;

            int bordered = heightMap.GetLength(0);
            int size     = bordered - 2;           // the mesh spans `size` units, centred

            // World → height-map indices. The mesh's top-left is (-size/2, +size/2)
            // in local space, and z runs negative as the map's y runs positive.
            float local = 1f / Mathf.Max(worldScale, 0.0001f);
            float lx = worldPos.x * local;
            float lz = worldPos.z * local;

            float u = (lx + (size - 1) / 2f) / size;
            float v = ((size - 1) / 2f - lz) / size;

            // +1 skips the border ring the generator carries for seamless normals.
            float fx = Mathf.Clamp(u * size + 1f, 0f, bordered - 1.001f);
            float fy = Mathf.Clamp(v * size + 1f, 0f, bordered - 1.001f);

            int x0 = Mathf.FloorToInt(fx), y0 = Mathf.FloorToInt(fy);
            int x1 = Mathf.Min(x0 + 1, bordered - 1), y1 = Mathf.Min(y0 + 1, bordered - 1);
            float tx = fx - x0, ty = fy - y0;

            // Bilinear over the four samples, so walking never steps.
            float h = Mathf.Lerp(
                Mathf.Lerp(heightMap[x0, y0], heightMap[x1, y0], tx),
                Mathf.Lerp(heightMap[x0, y1], heightMap[x1, y1], tx), ty);

            return heightCurve.Evaluate(h) * heightMultiplier * worldScale;
        }

        /// <summary>Ground height under (x, z), for callers that have no Vector3.</summary>
        public static float HeightAt(float x, float z) =>
            Active != null ? Active.SampleHeight(new Vector3(x, 0f, z)) : 0f;

        public void SetGroundColor(Color c)
        {
            if (meshRenderer != null) meshRenderer.sharedMaterial.color = c;
        }

        void OnDestroy() { if (Active == this) Active = null; }
    }
}
