using UnityEngine;

public static class GameConfig
{
    // ── The five families (§2.4) ──────────────────────────────────────────────
    // Colour is a playstyle, not a power level. White is not a family: it is the
    // empty state — a bare limb, a newborn, a grazer.
    public static class Colors
    {
        public static readonly Color Yellow = new Color(1f, 0.647f, 0.008f);
        public static readonly Color Red    = new Color(1f, 0.278f, 0.341f);
        public static readonly Color Blue   = new Color(0.180f, 0.525f, 0.871f);
        public static readonly Color Purple = new Color(0.647f, 0.369f, 0.918f);
        public static readonly Color Grey   = new Color(0.549f, 0.549f, 0.549f);
        public static readonly Color White  = new Color(0.945f, 0.949f, 0.965f);
        // Not a family — the tint of the dormant mate, which GDD §2.5 supersedes.
        public static readonly Color Pink   = new Color(1f, 0.41f, 0.71f);

        public static Color ForFamily(string family) => family switch
        {
            "Yellow" => Yellow,
            "Red"    => Red,
            "Blue"   => Blue,
            "Purple" => Purple,
            "Grey"   => Grey,
            _        => White   // no family = white, the empty state
        };
    }

    // Each family's trade, written as its full (Rage) expression. Intensity
    // expresses a fraction of each multiplier's distance from 1.0, so the same
    // row describes a Pale Yellow and a Rage Yellow — only weaker or stronger.
    public struct FamilyProfile
    {
        public string name;       // the colour itself
        public string className;  // the playstyle it reads as
        public float  healthMult;
        public float  speedMult;
        public float  damageMult;
        public float  reachMult;
        public float  dashMult;
    }

    // Written in the design's own order, which is also the birth precedence a
    // family tie falls back on (§2.4b): Yellow → Red → Blue → Purple → Grey.
    public static readonly FamilyProfile[] Families = new FamilyProfile[]
    {
        new FamilyProfile { name = "Yellow", className = "Brawler", healthMult = 1.5f,  speedMult = 0.85f, damageMult = 1.5f,  reachMult = 0.9f,  dashMult = 0.8f },
        new FamilyProfile { name = "Red",    className = "Leaper",  healthMult = 0.8f,  speedMult = 1.3f,  damageMult = 0.7f,  reachMult = 1.0f,  dashMult = 1.6f },
        new FamilyProfile { name = "Blue",   className = "Sniper",  healthMult = 0.9f,  speedMult = 1.0f,  damageMult = 1.0f,  reachMult = 1.7f,  dashMult = 1.0f },
        new FamilyProfile { name = "Purple", className = "Stalker", healthMult = 0.9f,  speedMult = 1.15f, damageMult = 0.95f, reachMult = 1.2f,  dashMult = 1.2f },
        new FamilyProfile { name = "Grey",   className = "Apex",    healthMult = 1.3f,  speedMult = 1.2f,  damageMult = 1.3f,  reachMult = 1.15f, dashMult = 1.3f },
    };

    // The blank (form zero): a white cube with one bare limb, multiplier 1.0 on
    // every axis. Not one of the 150 — it is what you are before your first meal.
    public const string BlankFormName = "The Blank";

    static readonly FamilyProfile Blank = new FamilyProfile
    {
        name = null, className = "Blank",
        healthMult = 1f, speedMult = 1f, damageMult = 1f, reachMult = 1f, dashMult = 1f
    };

    public static FamilyProfile FamilyFor(string family)
    {
        for (int i = 0; i < Families.Length; i++)
            if (Families[i].name == family) return Families[i];
        return Blank;   // white carries no trade
    }

    // ── Intensity (§2.4, §2.4b) ───────────────────────────────────────────────
    // Meat carries a tier, and the tier decides how much of the family's trade
    // the form expresses. Clash sits *beside* Rage at ~90%, not above it.
    public struct IntensityData
    {
        public string name;
        public float  pct;   // share of each multiplier's distance from 1.0
    }

    public const int Pale = 0, Dusk = 1, Deep = 2, Clash = 3, Rage = 4;

    public static readonly IntensityData[] Intensities = new IntensityData[]
    {
        new IntensityData { name = "Pale",  pct = 0.25f },
        new IntensityData { name = "Dusk",  pct = 0.50f },
        new IntensityData { name = "Deep",  pct = 0.75f },
        new IntensityData { name = "Clash", pct = 0.90f },
        new IntensityData { name = "Rage",  pct = 1.00f },
    };

    // Dilution walks the four *wild* tiers only; Clash and Rage share the top
    // rung, so diluting either one slides it to Deep (§2.4b).
    public static readonly int[] WildLadder = new[] { Pale, Dusk, Deep, Rage };

    public static int LadderRung(int intensity) =>
        intensity == Clash ? WildLadder.Length - 1 : System.Array.IndexOf(WildLadder, intensity);

    // ── The limb baseline (§2.4) ──────────────────────────────────────────────
    // Limbs set the baseline, colour multiplies it. Health climbs steepest — a
    // new limb reads first as durability — and speed only creeps.
    public struct RankData
    {
        public float health;
        public float damage;
        public float speed;
        public float reach;
        public float scale;   // body size; see below
    }

    // The design authors no body size per rank, so the scale column is the
    // prototype's own read of "more animal": a cube that grows a little per limb.
    public static readonly RankData[] Ranks = new RankData[]
    {
        new RankData { health = 100f, damage =  40f, speed = 12f, reach = 16f, scale = 1.0f },
        new RankData { health = 150f, damage =  55f, speed = 13f, reach = 19f, scale = 1.2f },
        new RankData { health = 200f, damage =  70f, speed = 14f, reach = 22f, scale = 1.4f },
        new RankData { health = 250f, damage =  85f, speed = 15f, reach = 25f, scale = 1.6f },
        new RankData { health = 300f, damage = 100f, speed = 16f, reach = 28f, scale = 1.8f },
        new RankData { health = 350f, damage = 115f, speed = 17f, reach = 31f, scale = 2.0f },
    };

    /// <summary>The baseline for a body of `rank` limbs (1–6). Rank 0 — a
    /// limbless grazer — stands on the same baseline as a one-limbed body.</summary>
    public static RankData RankFor(int rank) => Ranks[Mathf.Clamp(rank, 1, Ranks.Length) - 1];

    // ── Final stat composition (§2.4) ─────────────────────────────────────────

    public struct StatLine
    {
        public float health;
        public float damage;
        public float speed;
        public float reach;
        public float dash;
    }

    /// <summary>Limb baseline × family multiplier, scaled by intensity. This is
    /// the rule forms.json is authored on; when the file is missing, this
    /// composes the same numbers so a form still has a stat line.</summary>
    public static StatLine StatsFor(string family, int intensity, int rank)
    {
        RankData      r = RankFor(rank);
        FamilyProfile f = FamilyFor(family);
        float pct = Intensities[Mathf.Clamp(intensity, 0, Intensities.Length - 1)].pct;

        float Express(float mult) => 1f + pct * (mult - 1f);

        var s = new StatLine
        {
            health = r.health * Express(f.healthMult),
            damage = r.damage * Express(f.damageMult),
            speed  = r.speed  * Express(f.speedMult),
            reach  = r.reach  * Express(f.reachMult),
        };
        // Dash is a speed, not a multiplier: the form's own speed geared by the
        // family's dash trade — the same relation the authored forms carry.
        s.dash = s.speed * Express(f.dashMult);
        return s;
    }

    /// <summary>What to call a form when forms.json isn't there to name it.</summary>
    public static string FormNameFor(string family, int intensity) =>
        string.IsNullOrEmpty(family)
            ? BlankFormName
            : $"{Intensities[Mathf.Clamp(intensity, 0, Intensities.Length - 1)].name} {FamilyFor(family).className}";

    public const float WorldSize       = 100f;
    public const int   InitialEnemies  = 20;
    public const int   MaxEnemies      = 40;
    public const float SpawnInterval   = 2f;
    public const float DamageCooldown  = 0.5f;
    public const float RegenRate       = 0.05f;

    // ── Ecology tuning (content path only) ────────────────────────────────────
    // creatures.json authors stats on the design doc's scale, not the prototype's.
    // A Prairies Pale prey carries damage 45 against a 100-HP starting player,
    // speed 11.55 against the player's 12, and reach 15.6. Stamped in raw that
    // makes the first biome a field of unshakeable two-hit killers. These dials
    // scale the authored numbers into the game's feel without editing the data —
    // turn these first if the ecosystem still bites too hard (or too softly).
    // The prototype fallback (hasContentStats == false) ignores all of them, and
    // so does the player, whose stats are its own form's (§2.4).
    public static class Ecology
    {
        public const float ContactDamageScale = 0.35f; // 45 → ~16: six contacts, not two
        public const float SpeedScale         = 0.6f;  // wildlife must be outrunnable, and runnable-down
        public const float ReachScale         = 0.45f; // authored reach is a design range, not a pounce
        public const float WanderPace         = 0.5f;  // authored speed is a sprint; wandering is an amble

        // Perception is not reach. Awareness used to be forced up to the authored
        // reach, turning a 15.6-unit pounce range into an 18.7-unit sight radius —
        // three times the prototype's field of view, so most of the biome noticed
        // the player at the same moment.
        public const float SightRadius = 7f;    // + intensity*2 + body size, as the prototype
        public const float SightJitter = 0.25f; // ± per creature, so they don't all react on one frame

        // Most content prey bolt — their own `when_locked` prose has them sprinting
        // for open ground, not brawling. This share is territorial and fights back.
        public const float TerritorialPreyShare = 0.25f;

        // How many creatures may hunt the player at once. Predator roles count
        // against the budget but are never blocked by it: an elite that noticed you
        // is the fight the design wants, and the field behind it should keep grazing.
        public const int MaxHunters = 3;
    }

    public struct BiomeData
    {
        public string   name;
        public Color    groundColor;
        public Color    accentColor;
        public Color    fogColor;
        public string[] enemyColors;   // families, for the no-content fallback
    }

    public static readonly BiomeData BiomeNeon = new BiomeData
    {
        name        = "Neon Grid",
        groundColor = new Color(0.039f, 0.039f, 0.039f),
        accentColor = new Color(0.180f, 0.835f, 0.451f),
        fogColor    = new Color(0f, 0.067f, 0f),
        enemyColors = new[] { "Yellow", "Blue", "Purple" }
    };

    public static readonly BiomeData BiomeMagma = new BiomeData
    {
        name        = "Magma Wastes",
        groundColor = new Color(0.102f, 0.020f, 0.020f),
        accentColor = new Color(1f, 0.278f, 0.341f),
        fogColor    = new Color(0.133f, 0f, 0f),
        enemyColors = new[] { "Red", "Yellow", "Grey" }
    };

    public static readonly BiomeData BiomeCrystal = new BiomeData
    {
        name        = "Crystal Forest",
        groundColor = new Color(0.020f, 0.020f, 0.102f),
        accentColor = new Color(0.180f, 0.525f, 0.871f),
        fogColor    = new Color(0f, 0f, 0.133f),
        enemyColors = new[] { "Blue", "Purple", "Grey" }
    };

    // Visual identity for the five biomes in biomes.json. The generated content
    // describes their terrain in prose but carries no colours — palette is an art
    // call, so it lives here and is looked up by the content's biome id.
    public static BiomeData VisualsForBiome(string biomeId, string displayName)
    {
        BiomeData d = biomeId switch
        {
            "prairies"  => new BiomeData { groundColor = new Color(0.153f, 0.290f, 0.145f),
                                           accentColor = new Color(0.706f, 0.827f, 0.318f),
                                           fogColor    = new Color(0.482f, 0.616f, 0.451f) },
            "wetlands"  => new BiomeData { groundColor = new Color(0.106f, 0.220f, 0.220f),
                                           accentColor = new Color(0.318f, 0.780f, 0.678f),
                                           fogColor    = new Color(0.310f, 0.443f, 0.435f) },
            "mountains" => new BiomeData { groundColor = new Color(0.263f, 0.278f, 0.318f),
                                           accentColor = new Color(0.784f, 0.831f, 0.898f),
                                           fogColor    = new Color(0.545f, 0.584f, 0.647f) },
            "beach"     => new BiomeData { groundColor = new Color(0.780f, 0.706f, 0.522f),
                                           accentColor = new Color(0.298f, 0.639f, 0.804f),
                                           fogColor    = new Color(0.749f, 0.784f, 0.788f) },
            "volcanic"  => new BiomeData { groundColor = new Color(0.145f, 0.086f, 0.086f),
                                           accentColor = new Color(1f, 0.365f, 0.129f),
                                           fogColor    = new Color(0.286f, 0.153f, 0.129f) },
            _           => new BiomeData { groundColor = BiomeNeon.groundColor,
                                           accentColor = BiomeNeon.accentColor,
                                           fogColor    = BiomeNeon.fogColor },
        };
        d.name        = string.IsNullOrEmpty(displayName) ? biomeId : displayName;
        d.enemyColors = System.Array.Empty<string>(); // content path rolls its own palette
        return d;
    }

    public static class Boss
    {
        public const int   SpawnIntervalKills = 20;
        public const float ScaleMultiplier    = 2.5f;
        public const float HealthMultiplier   = 5f;
        public const float DamageMultiplier   = 2f;
    }
}
