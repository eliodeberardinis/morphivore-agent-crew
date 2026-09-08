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

            /// <summary>The shape of a biome by id. biomes.json describes its
            /// terrain in prose, not parameters (§2.7), so the prose is read here
            /// and the numbers live in code — the ids are the contract, and an
            /// unknown one falls back to the Prairies rather than a flat plane.
            ///
            /// None of these gate traversal yet: Fins, Claws, Coat and Heat are
            /// unbuilt, so a shape a player cannot cross would strand them. Relief
            /// reads as character here, not as a wall.</summary>
            public static TerrainProfile For(string biomeId, Color ground) => biomeId switch
            {
                // Marsh: low, wide and soft, with sunken hollows where the ponds
                // and reed channels will sit once water exists.
                "wetlands" => new TerrainProfile
                {
                    noiseScale = 55f, octaves = 3, persistance = 0.40f,
                    lacunarity = 1.8f, heightMultiplier = 7f, groundColor = ground
                },

                // Foothills into peaks: the tallest, roughest ground in the run.
                "mountains" => new TerrainProfile
                {
                    noiseScale = 30f, octaves = 5, persistance = 0.55f,
                    lacunarity = 2.3f, heightMultiplier = 30f, groundColor = ground
                },

                // Tidal flats and channels: flattest of all, cut by long troughs.
                "beach" => new TerrainProfile
                {
                    noiseScale = 65f, octaves = 3, persistance = 0.35f,
                    lacunarity = 2.0f, heightMultiplier = 6f, groundColor = ground
                },

                // Lava fields and sheer rock: high-frequency, jagged, broken.
                "volcanic" => new TerrainProfile
                {
                    noiseScale = 24f, octaves = 5, persistance = 0.62f,
                    lacunarity = 2.6f, heightMultiplier = 22f, groundColor = ground
                },

                _ => Prairies(ground)
            };
        }

        /// <summary>One run seed reproduces the whole world (§4.10), so a biome's
        /// seed is derived from the run's rather than rolled fresh — otherwise the
        /// first biome would be reproducible and the next four would not.</summary>
        public static int SeedForBiome(int runSeed, int biomeIndex)
            => runSeed * 31 + biomeIndex * 7919;

        /// <summary>Rebuild this terrain as a different biome: a new seed and a new
        /// shape, on the same object. Entering a biome used to change only the
        /// palette, so all five territories were one island wearing five coats of
        /// paint. <paramref name="onReady"/> fires when the new mesh exists —
        /// anything *placed* on the ground (props, the player) must wait for it,
        /// exactly as at boot; creatures self-correct, since they read the ground
        /// every frame.</summary>
        public void Regenerate(int seed, TerrainProfile profile, System.Action onReady = null)
        {
            IsReady       = false;
            heightMap     = null;      // nothing may sample the old shape meanwhile
            readyCallback = onReady;

            // The generator caches nothing between runs, but it does read its
            // tuning at call time, so re-stamping the fields is enough.
            ApplyProfile(seed, profile);
            StartCoroutine(BuildMesh());
        }

        void Generate(int seed, TerrainProfile profile)
        {
            meshFilter   = GetComponent<MeshFilter>();
            meshRenderer = GetComponent<MeshRenderer>();
            meshCollider = GetComponent<MeshCollider>();

            // AddComponent runs MapGenerator.Awake, which builds the falloff maps
            // that turn the noise into an island. Tuning fields are set after,
            // because GenerateMapData reads them at call time.
            gen = gameObject.AddComponent<MapGenerator>();

            ApplyProfile(seed, profile);
            StartCoroutine(BuildMesh());
        }

        /// <summary>Stamp a seed and a shape onto the generator. Shared by the
        /// first build and every biome change after it, so the two can never drift
        /// apart — a setting added for one is a setting the other gets.</summary>
        void ApplyProfile(int seed, TerrainProfile profile)
        {
            // Low-poly ground sits well beside procedurally-built cube creatures.
            // Rebuilt per biome rather than recoloured: each gets its own material.
            var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
            mat.color = profile.groundColor;
            meshRenderer.sharedMaterial = mat;

            gen.seed          = seed;
            gen.GameSeed      = "";           // numeric seed wins; ours comes from the run
            gen.noiseScale    = profile.noiseScale;
            gen.octaves       = profile.octaves;
            gen.persistance   = profile.persistance;
            gen.lacunarity    = profile.lacunarity;
            gen.offset        = Vector2.zero;
            gen.normalizeMode = Noise.NormalizeMode.Local; // one bounded island, not a chunk of many
            // The island shape is ours, not the package's (see ShapeIsland).
            gen.useFallofMap  = false;
            gen.useFallofMap2 = false;
            // MUST stay false, and it is not an aesthetic choice.
            //
            // MeshGenerator's flat-shading path emits three unique vertices per
            // triangle: 119 x 119 x 2 x 3 = ~84,000 for this map. CreateMesh()
            // builds `new Mesh { vertices, triangles }` and never sets
            // indexFormat, so the mesh keeps Unity's default 16-bit index buffer
            // — a hard ceiling of 65,535 vertices. Everything past that ceiling
            // cannot be indexed and is never drawn: a whole region of the island
            // renders as nothing while the ground stays solid under the player,
            // because bodies read their height from the height-map array (§C1b)
            // and never from the mesh. Seen from inside, the hills look hollow.
            //
            // Shared vertices with baked normals put the same 119x119 grid at
            // ~14,600 vertices, comfortably under the ceiling, at full terrain
            // resolution — so SampleHeight still agrees exactly with what is
            // drawn. If the faceted look is wanted back, it needs the package's
            // CreateMesh to set IndexFormat.UInt32, not this flag.
            gen.useFlatShading = false;
            gen.meshHeightMultiplier = profile.heightMultiplier;

            // GenerateTerrainMesh evaluates this curve per vertex, and an empty
            // AnimationCurve evaluates to 0 everywhere — which silently yields a
            // flat plane. It must be set.
            gen.meshHeightCurve = heightCurve = BuildHeightCurve();
            heightMultiplier    = profile.heightMultiplier;

            worldScale = GameConfig.WorldSize / MapGenerator.mapChunkSize;
            transform.localScale = new Vector3(worldScale, worldScale, worldScale);
        }

        // Flat near the bottom so low ground reads as a level plain rather than a
        // shallow bowl, then rising — the shape that gives an island a beach.
        static AnimationCurve BuildHeightCurve() => new AnimationCurve(
            new Keyframe(0f,   0f,   0f, 0f),
            new Keyframe(0.3f, 0.05f, 0.5f, 0.5f),
            new Keyframe(1f,   1f,   2f, 0f));

        IEnumerator BuildMesh()
        {
            // Generated on this thread, deliberately.
            //
            // MapGenerator.RequestMapData / RequestMeshData each spawn a real OS
            // thread (`new Thread(...)`) and hand the result back through a locked
            // queue drained in the generator's own Update. **WebGL has no
            // threads.** There, the work would never run, the queue would never
            // fill, and the `while (map == null) yield return null` this used to
            // wait on would spin for ever: the game boots, the player exists, and
            // there is no ground — with no exception to say why. The editor would
            // never show it, because the editor has threads.
            //
            // The two functions the package runs on those threads are public,
            // static and pure, so calling them directly costs nothing and removes
            // the platform difference entirely — desktop and web now run the same
            // path. The yield between them splits the frame cost rather than
            // stalling on noise and mesh in one go.
            //
            // This is also why ShapeIsland lives here: with the generator's own
            // falloff disabled, GenerateMapData had nothing left to do for us.
            var clock = System.Diagnostics.Stopwatch.StartNew();

            int size = MapGenerator.mapChunkSize + 2;
            float[,] map = Noise.GenerateNoiseMap(
                size, size, gen.seed, gen.noiseScale, gen.octaves,
                gen.persistance, gen.lacunarity, gen.offset, gen.normalizeMode);

            ShapeIsland(map);
            double noiseMs = clock.Elapsed.TotalMilliseconds;
            yield return null;

            clock.Restart();
            MeshData mesh = MeshGenerator.GenerateTerrainMesh(
                map, gen.meshHeightMultiplier, gen.meshHeightCurve, 0, gen.useFlatShading);
            double meshMs = clock.Elapsed.TotalMilliseconds;

            heightMap = map;

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
            // The two timings are why generation runs on this thread rather than
            // the package's: they are the whole cost the threading was hiding, and
            // they are spread over two frames already.
            Debug.Log($"[Terrain] seed {gen.seed}: {built.vertexCount} verts, " +
                      $"{GameConfig.WorldSize:0}u across, height {lo:0.0}–{hi:0.0}, " +
                      $"centre {SampleHeight(Vector3.zero):0.0} " +
                      $"(noise {noiseMs:0.0}ms + mesh {meshMs:0.0}ms)");

            readyCallback?.Invoke();
            readyCallback = null;
        }

        // Where the island stops being land, as a fraction of the map's half-width.
        // Ground is untouched inside `IslandShoreStart` and has fallen to sea level
        // by `IslandShoreEnd`. Tuned against the probe, not by eye: the aim is land
        // across the whole walkable disc (Radius = 48 of a 49.6 half-extent) with
        // the drop confined to the strip the player cannot reach.
        const float IslandShoreStart = 0.86f;
        const float IslandShoreEnd   = 1.00f;

        /// <summary>Cut the island out of the raw noise.
        ///
        /// This replaces MapGenerator's own falloff, which could not be used:
        ///
        /// 1. It is built in the generator's <c>Awake()</c>, which runs the instant
        ///    <c>AddComponent</c> is called — before this class can set
        ///    <c>fallofIntensity</c>. Any tuning here arrived too late to matter.
        /// 2. Its curve reaches full strength at ~69% of the half-width, so land
        ///    stopped near 30 units while the player could walk to 48. A probe
        ///    measured land reaching 31/32/30 units on three axes and 11 on the
        ///    fourth. The rest was real mesh lying flat at height zero — which in
        ///    play reads as the world simply not being there.
        /// 3. It is applied in a loop bounded by <c>mapChunkSize</c> over a map of
        ///    <c>mapChunkSize + 2</c>, so the last two rows and columns never get
        ///    it at all.
        ///
        /// Doing it here fixes all three, keeps the package untouched (this class
        /// is the only one that may touch it), and puts the shore where the code
        /// says it is.</summary>
        void ShapeIsland(float[,] heightMap)
        {
            if (heightMap == null) return;

            int n = heightMap.GetLength(0);
            if (n < 2) return;

            for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
            {
                // Normalised to [-1, 1] across the whole map, including the border
                // ring — so the edge is the edge, with nothing left over.
                float x = i / (float)(n - 1) * 2f - 1f;
                float y = j / (float)(n - 1) * 2f - 1f;

                // Square envelope (max, not distance): the mesh is square, and a
                // radial falloff would cut the corners off a world the player is
                // bounded to as a square.
                float v = Mathf.Max(Mathf.Abs(x), Mathf.Abs(y));

                float t = Mathf.InverseLerp(IslandShoreStart, IslandShoreEnd, v);
                float shore = t * t * (3f - 2f * t);            // smoothstep
                heightMap[i, j] = Mathf.Clamp01(heightMap[i, j] * (1f - shore));
            }
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
