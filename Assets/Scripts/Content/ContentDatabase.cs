// Runtime bridge between the generated world content (StreamingAssets/*.json)
// and the game's own vocabulary (GameConfig families, intensities, BiomeData).
//
// GDD §3.3 requires the game to keep running if the content is missing or
// malformed, so every load failure is non-fatal: IsLoaded stays false and the
// callers fall back to the hardcoded prototype tables in GameConfig.
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Morphivore.Content
{
    public static class ContentDatabase
    {
        public static bool IsLoaded { get; private set; }
        public static string LoadError { get; private set; }

        public static CreatureTable Creatures { get; private set; }
        public static BiomeTable    Biomes    { get; private set; }
        public static FormTable     Forms     { get; private set; }

        // biome id → creatures that spawn there, split by where they live.
        static readonly Dictionary<string, List<SpawnEntry>> wandering = new();
        static readonly Dictionary<string, List<SpawnEntry>> pocket    = new();
        static readonly Dictionary<string, CreatureDef>      byId      = new();
        static readonly Dictionary<string, FormDef>          byFormId  = new();

        // One creature as it appears in one biome: the definition plus the
        // biome-specific stat block, so callers never re-search the spawn list.
        public struct SpawnEntry
        {
            public CreatureDef def;
            public SpawnDef    spawn;
        }

        /// <summary>Drops the cached tables so the next Load() re-reads disk.
        /// Used by the editor content check; the game loads once at boot.</summary>
        public static void Reset() { IsLoaded = false; LoadError = null; }

        /// <summary>Loads forms.json + creatures.json + biomes.json. Safe to call
        /// repeatedly; only the first successful load does work.</summary>
        public static bool Load()
        {
            if (IsLoaded) return true;

            wandering.Clear();
            pocket.Clear();
            byId.Clear();

            // Forms load first and on their own guard: the player's own form
            // resolves against them (§2.4b), so a broken creatures.json must not
            // cost the player its name and stat line as well.
            LoadForms();

            try
            {
                Creatures = CreatureTable.Load(ReadStreamingAsset("creatures.json"));
                Biomes    = BiomeTable.Load(ReadStreamingAsset("biomes.json"));
            }
            catch (System.Exception e)
            {
                return Fail($"could not read world content: {e.Message}");
            }

            if (Creatures?.creatures == null || Creatures.creatures.Length == 0)
                return Fail("creatures.json parsed but held no creatures");
            if (Biomes?.biomes == null || Biomes.biomes.Length == 0)
                return Fail("biomes.json parsed but held no biomes");

            foreach (var c in Creatures.creatures)
            {
                if (string.IsNullOrEmpty(c.id) || c.spawns == null) continue;
                byId[c.id] = c;

                // Alphas and the apex are not wildlife: an alpha holds its biome's
                // lair and is reached through alpha_roster, the apex only in the
                // Ascension. Their spawns say pocket_only:false, which would
                // otherwise drop them straight into the ambient population.
                if (c.role == "alpha" || c.role == "apex") continue;

                foreach (var s in c.spawns)
                {
                    if (s == null || string.IsNullOrEmpty(s.biome)) continue;
                    var bucket = s.pocket_only ? pocket : wandering;
                    if (!bucket.TryGetValue(s.biome, out var list))
                        bucket[s.biome] = list = new List<SpawnEntry>();
                    list.Add(new SpawnEntry { def = c, spawn = s });
                }
            }

            // Biomes come back in authored order; the game walks them by index.
            System.Array.Sort(Biomes.biomes, (a, b) => a.order.CompareTo(b.order));

            IsLoaded  = true;
            LoadError = null;
            Debug.Log($"[Content] loaded {Creatures.creatures.Length} creatures, " +
                      $"{Biomes.biomes.Length} biomes, {byFormId.Count} forms from StreamingAssets.");
            return true;
        }

        // The 150 authored forms (§2.4b), keyed the way forms.json keys them:
        // family_intensity_rRANK. Missing forms are survivable — GameConfig
        // composes the same stat line from its own tables — so this failure only
        // warns and never trips IsLoaded.
        static void LoadForms()
        {
            byFormId.Clear();

            try
            {
                Forms = FormTable.Load(ReadStreamingAsset("forms.json"));
            }
            catch (System.Exception e)
            {
                Forms = null;
                Debug.LogWarning($"[Content] could not read forms.json: {e.Message} — " +
                                 "forms fall back to the composed tables in GameConfig.");
                return;
            }

            if (Forms?.forms == null) return;
            foreach (var f in Forms.forms)
                if (!string.IsNullOrEmpty(f.id)) byFormId[f.id] = f;
        }

        static string ReadStreamingAsset(string file) =>
            File.ReadAllText(Path.Combine(Application.streamingAssetsPath, file));

        static bool Fail(string why)
        {
            IsLoaded  = false;
            LoadError = why;
            Creatures = null;
            Biomes    = null;
            Debug.LogWarning($"[Content] {why} — falling back to the built-in prototype tables.");
            return false;
        }

        // ── Queries ───────────────────────────────────────────────────────────

        /// <summary>The ambient population of a biome: everything that roams it
        /// freely (grazers + the tiers listed in wandering_tiers).</summary>
        public static List<SpawnEntry> Wandering(string biomeId) =>
            wandering.TryGetValue(biomeId, out var l) ? l : null;

        /// <summary>Creatures confined to a biome's defended pockets — the harder
        /// prey tiers, the elites and the trait minibosses.</summary>
        public static List<SpawnEntry> Pocket(string biomeId) =>
            pocket.TryGetValue(biomeId, out var l) ? l : null;

        public static CreatureDef ById(string id) =>
            id != null && byId.TryGetValue(id, out var c) ? c : null;

        /// <summary>The authored form a family + intensity + rank names, or null
        /// when forms.json isn't there — the caller then composes the same
        /// numbers from GameConfig's own tables.</summary>
        public static FormDef Form(string family, int intensity, int rank)
        {
            if (string.IsNullOrEmpty(family) || byFormId.Count == 0) return null;
            string id = $"{family.ToLowerInvariant()}_" +
                        $"{GameConfig.Intensities[intensity].name.ToLowerInvariant()}_r{rank}";
            return byFormId.TryGetValue(id, out var f) ? f : null;
        }

        /// <summary>Picks a spawn weighted by the biome's family palette. Families
        /// weighted 0 (e.g. Grey in the Prairies) never come up; entries with no
        /// family — the grazers — carry a fixed baseline share.</summary>
        public static bool RollSpawn(BiomeDef biome, List<SpawnEntry> pool, out SpawnEntry picked)
        {
            picked = default;
            if (pool == null || pool.Count == 0) return false;

            float total = 0f;
            for (int i = 0; i < pool.Count; i++) total += Weight(biome, pool[i]);
            if (total <= 0f) return false;

            float roll = Random.value * total;
            for (int i = 0; i < pool.Count; i++)
            {
                roll -= Weight(biome, pool[i]);
                if (roll <= 0f) { picked = pool[i]; return true; }
            }
            picked = pool[pool.Count - 1];
            return true;
        }

        const float GrazerWeight = 0.2f; // grazers have no family to weight by

        static float Weight(BiomeDef biome, SpawnEntry e)
        {
            if (string.IsNullOrEmpty(e.def.family)) return GrazerWeight;
            if (biome?.palette_weights == null)     return 1f;
            return biome.palette_weights.For(e.def.family);
        }

        // ── Mapping into the game's vocabulary ────────────────────────────────

        // A creature's tier is its meat's saturation, and meat carries intensity
        // into your limbs — it is not a morphology rank. Rank is limbs (§2.4b).
        public static int IntensityIndex(string contentTier) => contentTier switch
        {
            "Pale"  => GameConfig.Pale,
            "Dusk"  => GameConfig.Dusk,
            "Deep"  => GameConfig.Deep,
            "Clash" => GameConfig.Clash,
            "Rage"  => GameConfig.Rage,
            _       => GameConfig.Pale   // grazers carry no tier
        };

        public static Color HexToColor(string hex, Color fallback)
        {
            if (!string.IsNullOrEmpty(hex) && ColorUtility.TryParseHtmlString(hex, out var c))
                return c;
            return fallback;
        }
    }
}
