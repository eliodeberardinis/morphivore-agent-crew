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

    GameConfig.BiomeData CurrentBiome => useContent
        ? GameConfig.VisualsForBiome(ContentBiome.id, ContentBiome.name)
        : LegacyBiomes[currentBiomeIndex];

    // Population and respawn pacing come from the biome when content is loaded.
    int StandingPopulation => useContent
        ? Mathf.Max(1, ContentBiome.standing_population)
        : GameConfig.MaxEnemies;

    float SpawnInterval => useContent && ContentBiome.respawn_per_min > 0f
        ? 60f / ContentBiome.respawn_per_min
        : GameConfig.SpawnInterval;

    bool initialized  = false;
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

        // Boss trigger
        if (!bossSpawned && player.totalKills > 0 && player.totalKills % GameConfig.Boss.SpawnIntervalKills == 0)
        {
            SpawnBoss();
        }

        // Biome progression. On the content path each biome declares the
        // player_rank it expects (1..6), which is the player's limb count.
        // The real §2.6 gates (distinct forms + coloured prey eaten) land with
        // the Alpha work; until then rank alone opens the next biome — and rank
        // itself only moves through breeding (§2.5), so this holds at biome one.
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
                if (enemy != null && enemy.isBoss) bossSpawned = false;
                enemies.RemoveAt(i);
            }
        }

        // Clean up destroyed enemies
        enemies.RemoveAll(e => e == null);
    }

    void SetBiome(int index)
    {
        currentBiomeIndex = index;
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

        // Spawn on the island, standing on whatever ground is under the roll.
        float limit = BiomeTerrain.Radius * 0.9f;
        float sx = Random.Range(-limit, limit), sz = Random.Range(-limit, limit);
        go.transform.position = new Vector3(sx, BiomeTerrain.HeightAt(sx, sz) + 1f, sz);

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
            // "Apex predator" = this biome's alpha. One of the five colour alphas
            // that hold its lair, picked uniformly — the roster is the roster.
            if (biome.alpha_roster == null || biome.alpha_roster.Length == 0) return false;

            var def = ContentDatabase.ById(biome.alpha_roster[Random.Range(0, biome.alpha_roster.Length)]);
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
