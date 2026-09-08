using System.Collections.Generic;
using UnityEngine;
using Morphivore.Content;
using Morphivore.World;

public class EcosystemManager : MonoBehaviour
{
    public PlayerController player;

    // Events consumed by GameManager
    public System.Action<GameConfig.BiomeData> OnBiomeChanged;
    public System.Action<string>               OnBossSpawned; // authored name, or null
    public System.Action                       OnMateSpawned;

    readonly List<EnemyAI> enemies = new List<EnemyAI>();

    float spawnTimer        = 0f;
    bool  bossSpawned       = false;

    // ── The Alpha's two gates (§2.5, thresholds from §4.10) ───────────────────
    // The Alpha does not arrive on a timer: it wakes once you have eaten enough
    // of this biome to be worth its attention. Two counters, both reset when the
    // biome changes. Grazers are food, not meat — they carry no colour and never
    // count toward either gate.
    //
    // This is the cheap half of build-plan chunk B1. The lair landmark, the 90%
    // stir warning and the biome emptying on wake are the expensive half and are
    // deliberately not here yet.
    readonly HashSet<string> formsThisBiome = new HashSet<string>();
    int  colouredPreyThisBiome = 0;
    bool alphaDefeated         = false;

    public int  FormsSeen    => formsThisBiome.Count;
    public int  FormGate     => 3 + 2 * currentBiomeIndex;   // 3, 5, 7, 9, 11
    public int  PreyEaten    => colouredPreyThisBiome;
    public int  PreyGate     => 15 + 5 * currentBiomeIndex;  // 15, 20, 25, 30, 35
    public bool AlphaAwake   => bossSpawned && !alphaDefeated;
    public bool AlphaDefeated => alphaDefeated;
    public bool GatesMet     => FormsSeen >= FormGate && PreyEaten >= PreyGate;

    // Which colour this biome has lost the most of. §2.5: the Alpha that comes is
    // "the champion of the colour you ate most" — so the fight you get is the one
    // your own diet chose, and it mirrors the family you are strongest in.
    readonly Dictionary<string, int> eatenByFamily = new Dictionary<string, int>();

    /// <summary>Called when the player eats something that carries colour.
    /// `formId` is the form the player resolved to after the meal, so the first
    /// gate counts what you have *become* here, not what you have chewed.</summary>
    public void RecordColouredPrey(string formId, string family)
    {
        colouredPreyThisBiome++;
        if (!string.IsNullOrEmpty(formId)) formsThisBiome.Add(formId);

        if (!string.IsNullOrEmpty(family))
            eatenByFamily[family] = eatenByFamily.TryGetValue(family, out int n) ? n + 1 : 1;
    }

    /// <summary>The colour eaten most in this biome, or null before the first
    /// meal. Ties break toward nothing in particular — the roster pick falls back
    /// to a roll, which is what the old behaviour was for every fight.</summary>
    string MostEatenFamily()
    {
        string best = null;
        int    top  = 0;
        foreach (var pair in eatenByFamily)
            if (pair.Value > top) { top = pair.Value; best = pair.Key; }
        return best;
    }

    // Mating is dormant (see the commented block in Update), so its timer is
    // parked here with the code that uses it rather than sitting in the live
    // fields unread. Note that GDD §2.5 supersedes this entirely — breeding is
    // now Alpha → emblem → litter, not a mate wandering the world.
    // float mateTimer          = 0f;
    // const float MateInterval = 30f;
    int   currentBiomeIndex = 0;

    // The ecosystem runs off creatures.json / biomes.json when they load, and off
    // the three prototype biomes below when they don't (GDD §3.3 fallback).
    bool useContent = false;

    static readonly GameConfig.BiomeData[] LegacyBiomes = new[]
    {
        GameConfig.BiomeNeon,   // 0
        GameConfig.BiomeMagma,  // 1
        GameConfig.BiomeCrystal // 2
    };

    int BiomeCount => useContent ? ContentDatabase.Biomes.biomes.Length : LegacyBiomes.Length;

    BiomeDef ContentBiome => ContentDatabase.Biomes.biomes[currentBiomeIndex];

    GameConfig.BiomeData CurrentBiome
    {
        get
        {
            var d = useContent
                ? GameConfig.VisualsForBiome(ContentBiome.id, ContentBiome.name)
                : LegacyBiomes[currentBiomeIndex];
            // The scene builder needs to know *which* biome, not just its palette:
            // the id picks a terrain shape and a prop set, the index seeds it.
            d.index = currentBiomeIndex;
            return d;
        }
    }

    // Population and respawn pacing come from the biome when content is loaded.
    int StandingPopulation => useContent
        ? Mathf.Max(1, ContentBiome.standing_population)
        : GameConfig.MaxEnemies;

    float SpawnInterval => useContent && ContentBiome.respawn_per_min > 0f
        ? 60f / (ContentBiome.respawn_per_min * GameConfig.Ecology.RespawnPace)
        : GameConfig.SpawnInterval;

    bool initialized  = false;
    bool openingPopulationPlaced = false;
    public bool gameStarted = false;

    // Called explicitly by GameManager after scene is built
    public void Init()
    {
        initialized = true;
        useContent  = ContentDatabase.Load();

        int initial = useContent
            ? StandingPopulation
            : GameConfig.InitialEnemies;

        for (int i = 0; i < initial; i++)
            SpawnEnemy();

        // From here on, respawns ring the player rather than scattering.
        openingPopulationPlaced = true;

        // The content's first biome may not look like the prototype's, so push
        // its palette to the scene straight away.
        if (useContent) OnBiomeChanged?.Invoke(CurrentBiome);
    }

    void Update()
    {
        if (!initialized || !gameStarted || player == null || player.isDead) return;

        spawnTimer += Time.deltaTime;
        if (spawnTimer >= SpawnInterval)
        {
            SpawnEnemy();
            spawnTimer = 0f;
        }

        // Mating is disabled for now — to be reworked into the real Cubivore
        // mating/breeding system later. Re-enable this block to restore it.
        // mateTimer += Time.deltaTime;
        // if (mateTimer >= MateInterval)
        // {
        //     SpawnMate();
        //     mateTimer = 0f;
        // }

        // The Alpha wakes when both gates are met, not on a kill count.
        if (!bossSpawned && GatesMet)
        {
            SpawnBoss();
        }

        // Biome progression. On the content path each biome declares the
        // player_rank it expects (1..6), which is the player's limb count. Rank
        // moves only through breeding (§2.5, unbuilt), so this holds at biome one
        // in play — the Alpha's gates above are what the player actually works
        // toward, and the biome door opens behind them once breeding exists.
        if (useContent)
        {
            int next = currentBiomeIndex + 1;
            if (next < BiomeCount &&
                player.rank >= ContentDatabase.Biomes.biomes[next].player_rank)
                SetBiome(next);
        }
        else
        {
            if (player.rank >= 3 && currentBiomeIndex == 0) SetBiome(1);
            if (player.rank >= 5 && currentBiomeIndex == 1) SetBiome(2);
        }

        // Update enemies & contact damage
        for (int i = enemies.Count - 1; i >= 0; i--)
        {
            var enemy = enemies[i];

            if (enemy == null)
            {
                enemies.RemoveAt(i);
                continue;
            }

            if (!enemy.isDead) { }
            else if (enemy == null || !enemy.gameObject.activeSelf)
            {
                // A killed Alpha stays killed. It used to clear the flag and let
                // the next kill-count tick spawn another; now that the gates stay
                // satisfied once met, that would respawn it on the same frame.
                if (enemy != null && enemy.isBoss) alphaDefeated = true;
                enemies.RemoveAt(i);
            }
        }

        // Clean up destroyed enemies
        enemies.RemoveAll(e => e == null);
    }

    void SetBiome(int index)
    {
        currentBiomeIndex = index;

        // A new biome is a new Alpha with its own, higher gates. What you ate in
        // the Prairies does not count toward the Wetlands' attention.
        formsThisBiome.Clear();
        eatenByFamily.Clear();
        colouredPreyThisBiome = 0;
        bossSpawned           = false;
        alphaDefeated         = false;

        OnBiomeChanged?.Invoke(CurrentBiome);
    }

    EnemyAI SpawnEnemy(bool boss = false)
    {
        if (!boss && enemies.Count >= StandingPopulation) return null;

        var go    = new GameObject("Enemy");
        var enemy = go.AddComponent<EnemyAI>();
        enemy.isBoss = boss;

        if (!useContent || !StampFromContent(enemy, boss))
        {
            // Prototype fallback: a family off the biome palette, mostly weak meat.
            int intensity = GameConfig.Pale;
            float r = Random.value;
            if      (r > 0.95f) intensity = GameConfig.Clash;
            else if (r > 0.85f) intensity = GameConfig.Deep;
            else if (r > 0.60f) intensity = GameConfig.Dusk;

            string[] families = LegacyBiomes[Mathf.Min(currentBiomeIndex, LegacyBiomes.Length - 1)].enemyColors;

            enemy.family    = families[Random.Range(0, families.Length)];
            enemy.intensity = boss
                ? Mathf.Min(player ? player.intensity + 1 : GameConfig.Dusk, GameConfig.Intensities.Length - 1)
                : intensity;
            enemy.rank      = boss && player ? Mathf.Min(player.rank + 1, GameConfig.Ranks.Length) : 1;
        }

        enemy.Init();
        go.transform.position = SpawnPoint();

        // Non-trigger collider so the bite hitbox OnTriggerEnter fires against it
        var col = go.AddComponent<SphereCollider>();
        col.isTrigger = false;
        col.radius    = 0.6f;

        // Also add a Rigidbody (kinematic) so Unity's physics processes the collider correctly
        var rb = go.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity  = false;

        enemies.Add(enemy);
        return enemy;
    }

    /// <summary>Where a creature appears, standing on whatever ground is under it.
    /// The opening population is scattered across the whole island so the world
    /// looks inhabited; every later respawn rings the player, because a creature
    /// that spawns 40 units away is a walk, not an encounter.</summary>
    Vector3 SpawnPoint()
    {
        float limit = BiomeTerrain.Radius * 0.9f;
        float sx, sz;

        if (openingPopulationPlaced && player != null)
        {
            Vector2 dir = Random.insideUnitCircle.normalized;
            if (dir == Vector2.zero) dir = Vector2.right;
            float dist = Random.Range(GameConfig.Ecology.RespawnRingMin,
                                      GameConfig.Ecology.RespawnRingMax);

            Vector3 p = player.transform.position;
            sx = Mathf.Clamp(p.x + dir.x * dist, -limit, limit);
            sz = Mathf.Clamp(p.z + dir.y * dist, -limit, limit);
        }
        else
        {
            sx = Random.Range(-limit, limit);
            sz = Random.Range(-limit, limit);
        }

        return new Vector3(sx, BiomeTerrain.HeightAt(sx, sz) + 1f, sz);
    }

    // The world has no defended pockets yet (GDD §2.7), so pocket-only creatures
    // could leak into the ambient roll at this rate. Held at 0: half of the
    // Prairies pocket pool is Clash-tier elites, which out-tier a starting player
    // — they hunt on sight, and PlayerController.PounceAnim refuses to damage
    // anything carrying darker meat, so they were unkillable escorts in the
    // tutorial biome. Raise it only once pockets are placed and the creatures
    // spawn inside them, where the player chooses to walk in.
    const float PocketLeakChance = 0f;

    /// <summary>Picks one creature out of the content tables for the current
    /// biome and stamps it onto <paramref name="enemy"/>. False = nothing
    /// suitable found, so the caller falls back to the prototype roll.</summary>
    bool StampFromContent(EnemyAI enemy, bool boss)
    {
        var biome = ContentBiome;

        if (boss)
        {
            // This biome's Alpha: the champion of the colour the player ate most
            // (§2.5's mirror-match), falling back to a roll before the first meal
            // or when that colour holds no lair here.
            if (biome.alpha_roster == null || biome.alpha_roster.Length == 0) return false;

            var def = AlphaFor(biome, MostEatenFamily());
            var spawn = FindSpawn(def, biome.id);
            if (spawn == null) return false;

            enemy.ApplyContent(def, spawn);
            enemy.name = def.name;
            return true;
        }

        var pool = Random.value < PocketLeakChance
            ? ContentDatabase.Pocket(biome.id)
            : ContentDatabase.Wandering(biome.id);
        pool ??= ContentDatabase.Wandering(biome.id);

        if (!ContentDatabase.RollSpawn(biome, pool, out var picked)) return false;

        enemy.ApplyContent(picked.def, picked.spawn);
        enemy.name = picked.def.name;
        return true;
    }

    /// <summary>The roster member whose family is <paramref name="family"/>, or a
    /// uniform roll when there is no such champion (or no diet yet).</summary>
    static CreatureDef AlphaFor(BiomeDef biome, string family)
    {
        if (!string.IsNullOrEmpty(family))
            foreach (string id in biome.alpha_roster)
            {
                var candidate = ContentDatabase.ById(id);
                if (candidate != null && candidate.family == family) return candidate;
            }

        return ContentDatabase.ById(
            biome.alpha_roster[Random.Range(0, biome.alpha_roster.Length)]);
    }

    static SpawnDef FindSpawn(CreatureDef def, string biomeId)
    {
        if (def?.spawns == null) return null;
        foreach (var s in def.spawns)
            if (s != null && s.biome == biomeId) return s;
        return null;
    }

    void SpawnBoss()
    {
        bossSpawned = true;
        var boss = SpawnEnemy(boss: true);
        OnBossSpawned?.Invoke(boss != null ? boss.displayName : null);
    }

    void SpawnMate()
    {
        var go    = new GameObject("MateEnemy");
        var enemy = go.AddComponent<MateEnemy>();
        enemy.rank   = player.rank;
        enemy.isBoss = false;
        // A mate is not one of the five families: it carries no colour, and wears
        // pink so it reads as the odd one out.
        enemy.hasBodyColor = true;
        enemy.bodyColor    = GameConfig.Colors.Pink;
        enemy.Init();

        // Spawn on the island, standing on whatever ground is under the roll.
        float limit = BiomeTerrain.Radius * 0.9f;
        float sx = Random.Range(-limit, limit), sz = Random.Range(-limit, limit);
        go.transform.position = new Vector3(sx, BiomeTerrain.HeightAt(sx, sz) + 1f, sz);

        var col = go.AddComponent<SphereCollider>();
        col.isTrigger = false;
        col.radius    = 0.6f;

        var rb = go.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity  = false;

        enemies.Add(enemy);
        OnMateSpawned?.Invoke();
    }
}
