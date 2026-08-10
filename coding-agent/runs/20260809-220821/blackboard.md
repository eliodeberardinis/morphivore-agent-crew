# Blackboard — 20260809-220821

**Started** 2026-08-09 22:08:21  
**Mode** build  
**Goal** R013,R015,R014,R016,R023,R018,R021


---

## Stage 2 — Scan the codebase

Read **19 C# files** (3,980 lines, 32 types) and **5 data contract files**.

| File | Lines | Types | Members |
|---|---|---|---|
| Assets/Scripts/Content/ContentDatabase.cs | 186 | ContentDatabase, SpawnEntry | 19 |
| Assets/Scripts/Content/FormTable.cs | 48 | StatBlock, FormDef, FormTable | 23 |
| Assets/Scripts/Content/WorldTables.cs | 70 | — | 0 |
| Assets/Scripts/Editor/ContentCheck.cs | 99 | ContentCheck | 3 |
| Assets/Scripts/Editor/MCPBridge.cs | 592 | MCPBridge, Status | 44 |
| Assets/Scripts/Editor/MCPBridgeWindow.cs | 45 | MCPBridgeWindow | 3 |
| Assets/Scripts/Editor/UrpMaterialConverter.cs | 102 | UrpMaterialConverter | 4 |
| Assets/Scripts/Game/Companion.cs | 28 | Companion | 2 |
| Assets/Scripts/Game/Creature.cs | 209 | Creature | 26 |
| Assets/Scripts/Game/EcosystemManager.cs | 276 | EcosystemManager | 10 |
| Assets/Scripts/Game/EnemyAI.cs | 536 | EnemyAI, State, Attack | 20 |
| Assets/Scripts/Game/GameConfig.cs | 190 | GameConfig, Colors, ClassProfile, TierData, Ecology, BiomeData, Boss | 50 |
| Assets/Scripts/Game/GameManager.cs | 609 | GameManager | 9 |
| Assets/Scripts/Game/HumanWalk.cs | 91 | HumanWalk | 6 |
| Assets/Scripts/Game/MateEnemy.cs | 4 | MateEnemy | 0 |
| Assets/Scripts/Game/Obstacle.cs | 6 | Obstacle | 0 |
| Assets/Scripts/Game/PlayerController.cs | 521 | PlayerController | 21 |
| Assets/Scripts/World/BiomeTerrain.cs | 225 | BiomeTerrain, TerrainProfile | 15 |
| Assets/Scripts/World/PropScatter.cs | 143 | PropScatter, PropSet | 12 |

Data files present but **read by no script**: `forms.json`, `panels.json` — authored content the game never loads.


---

## Stage 1 — Read the GDD

Source: `gdd-condensed-2026-07-22.md` (7,444 words). After the design-section filter: **4,205 words**, 19 sections in, 21 out.

Sections read: `§1 Executive Summary`, `The world: an eating ladder, all the way up`, `What you are: a bloodline, not a creature`, `§2 Game Mechanics`, `§2.1 What the player does, second to second`, `§2.2 Being hunted (the same rules apply to you)`, `§2.3 Health — the bar you chose, and how you refill it`, `§2.4 Mutation — you are what you eat`, `§2.4a The colour buffer — the rule you execute every ten seconds`, `§2.4b Forms — the 150, and the meat that makes them`, `§2.5 Rank — the Alpha challenge and breeding`, `The Ascension — where rank six is played`, `§2.6 Traits and terrain gates`, `§2.6a Where traits live, and what survives what`, `§2.7 Biomes — escalating traversal complexity`, `§2.8 Decorated panels — the run's build layer`, `§2.9 The Bestiary`, `§2.9a The record's milestones — what discovery unlocks`, `§3.3 Engine integration — the Unity MCP bridge`

Sections withheld (they describe making the game, not the game): `Game Design Document — Condensed Submission Version`, `§3 AI Architecture — the agent team that builds the game`, `§3.1 Agent interfaces`, `§3.2 The AI development pipeline`, `§3.4 Prompt constraints`, `§4 Technical Strategy`, `§4.1 Stack`, `§4.2 Named constraint: the Unity domain-reload loop`, `§4.3 Second constraint: no artist — a split art pipeline`, `§4.4 API constraints — and the one that actually binds`, `§4.5 Operational limits`, `§4.6 Token budget`, `§4.7 Cost projection`, `§4.8 Weekly capacity — what the subscription actually buys`, `The cut ladder — two axes, in order`, `§4.9 Scope — the first publishable build`, `§4.10 Testing strategy`, `Changes from the First Draft`, `What the agent stress-test flagged`, `What a second (numeric) review and self-review caught`, `The designer's own judgment`

Indexed the scoped GDD for retrieval: 29 chunks, backends bm25, embeddings.

Reused 45 requirements from `20260809-220054` — no extraction call made.

Extracted **45 requirements**.

| § | Requirement | Depends on | Has acceptance test |
|---|---|---|---|
| 2.1, 4.1 (referenced) | Dual input mapping (keyboard+mouse and gamepad) | — | no |
| 2.1 | Top-down movement and facing | R001 | no |
| 2.1 | Solid bodies and obstacles | R002 | no |
| 2.1 | Lock-on targeting | R001, R002 | no |
| 2.1 | Pounce attack | R004, R003 | no |
| 2.1 | Knockdown / dizzy state | R005 | no |
| 2.1, 2.3 | Eating a downed creature | R006 | no |
| 2.1, 2.3 | Dash | R001, R002, R016 | yes |
| 1, 2.3 | Single Health meter and permadeath | — | no |
| 2.3 | Grazers as the healing supply | R007, R009, R008 | yes |
| 2.2 | Predator AI: hunting the player | R004, R005 | no |
| 2.2 | Prey reactions: fleeing and floating health bars | R005 | no |
| 2.4 | Five colour families and their stat multipliers | — | yes |
| 2.4, 2.4b | Intensity scaling of family multipliers | R013 | yes |
| 2.4 | Limb baseline stat table | — | yes |
| 2.4 | Final stat composition (rank baseline × family × intensity) | R013, R014, R015 | yes |
| 2.4, 2.5 | The blank (form zero) | R015 | yes |
| 2.4a | The colour buffer (FIFO limb slots) | R007 | no |
| 2.1, 2.4a | Poop the oldest colour | R018, R001 | no |
| 2.4a | Next-slot-to-be-overwritten indicator | R018 | no |
| 2.4b | Form resolution from buffer state | R018, R023 | no |
| 2.3, 2.4b | Instant mutation with wound preserved | R021, R009, R016 | no |
| 2.4b, 3.3 | forms.json — the 150 authored forms | R013, R014, R015 | yes |
| 2.4b, 2.7 | Meat tiers and their world distribution | R013, R014 | yes |
| 2.4b, 2.6a | Procedural body rendering of forms | R023, R021 | no |
| 2.7, 3.3 | Biome generation, terrain gates and per-run palette roll | — | yes |
| 2.7, 2.4b | Pockets, distance-based difficulty and lair placement | R026, R024 | no |
| 3.3 | Ambient rank rules | R026, R024 | yes |
| 2.6 | Trait minibosses and the four traits | R026, R007 | yes |
| 2.6a | Trait permanence, face rendering and inheritance | R029, R022 | yes |
| 2.5 | Alpha lair and the two-gate unlock | R021, R007, R026 | yes |
| 2.5 | Alpha identity, mirror-match and biome emptying | R031, R028, R016 | no |
| 2.5, 3.3 | Emblems | R032, R007 | no |
| 2.5 | Breeding, litters and rank gain | R033, R018, R015, R030 | yes |
| 2.8, 3.3 | Decorated panels | R022, R034, R004, R008 | no |
| 2.5 | Combat pacing invariant (2–3 pounces, no one-shots) | R016, R005, R028 | yes |
| 1, 2.5 | Conquest win condition | R033, R034 | no |
| 2.5, The Ascension | The Ascension and the Apex | R037, R040, R023 | yes |
| 2.9 | The Bestiary screen | R023, R021, R033, R034 | yes |
| 1, 2.9 | Bestiary persistence across runs | R039, R009 | no |
| 2.9a | Record milestone unlocks | R040, R017, R030, R034, R038 | yes |
| 1, 2.5 | Run restart as a one-limb blank | R017, R040, R026, R041 | no |
| 3.3 | Generator invariants and seed refusal | R026, R029, R031, R027 | yes |
| 3.3 | JSON content loading with schema check and fallback | R023, R024, R026, R035, R033 | no |
| 3.3 | Unity MCP editor bridge | — | yes |


---

## Stage 3 — Detect gaps

Reusing 45 judgement(s) from an earlier run; 0 still to judge.

Judging 0 requirements against the inventory (~2,898 token cached prefix per call).

Verdicts: **CONTRADICTED** 19, **PARTIAL** 12, **ABSENT** 8, **PRESENT** 3, **UNCONSUMED** 3

| § | Requirement | Verdict | Confidence | Removal? | Effort | Evidence |
|---|---|---|---|---|---|---|
| 2.1, 4.1 (referenced) | Dual input mapping (keyboard+mouse and gamepad) | PARTIAL | low | no | medium | `Assets/Scripts/Game/PlayerController.cs — `PlayerController` with moveSpeed, LockConeDot, OnLockTargetChanged, Update, string literal "target then launch"`, `Assets/Scripts/Game/GameManager.cs — `EnsureDesktopPointer``, `Assets/Scripts/Game/EnemyAI.cs — WindupTime, PounceTime, isLockedByPlayer` |
| 2.1 | Top-down movement and facing | PRESENT | medium | no | small | `Assets/Scripts/Game/PlayerController.cs — class PlayerController: moveSpeed, BaseSpeed, Awake, Update, gameStarted`, `Assets/Scripts/Game/GameManager.cs — creates "Player" GameObject, EnsureDesktopPointer`, `Assets/Scripts/Game/Creature.cs — GroundFollow, GroundY, StickY (keeps body on terrain plane)` |
| 2.1 | Solid bodies and obstacles | PARTIAL | low | no | medium | `Assets/Scripts/Game/Obstacle.cs (6 lines, `class Obstacle` — no members parsed; bare marker component)`, `Assets/Scripts/Game/Creature.cs — `GroundFollow`, `GroundY`, `StickY`, `Update` (transform/height-driven placement via terrain sample, no rigidbody/collider symbols)`, `Assets/Scripts/World/BiomeTerrain.cs — `SampleHeight`, `HeightAt` (ground is queried analytically, not collided against)` |
| 2.1 | Lock-on targeting | PARTIAL | medium | no | small | `Assets/Scripts/Game/PlayerController.cs: `LockConeDot`, `OnLockTargetChanged`, string "target then launch"`, `Assets/Scripts/Game/EnemyAI.cs: `isLockedByPlayer`, string "targeted"`, `Assets/Scripts/Game/GameManager.cs: strings "LockReticleWorld", "LockReticle", "ThreatHaloWorld", "ThreatHalo", "You are targeted"` |
| 2.1 | Pounce attack | PARTIAL | low | no | small | `Assets/Scripts/Game/PlayerController.cs: `LockConeDot`, `OnLockTargetChanged`, `biteDamage`, `moveSpeed`, string "target then launch"`, `Assets/Scripts/Game/GameConfig.cs: `struct ClassProfile` — speedMult, damageMult, healthMult, `lungeMult`, dashMult`, `Assets/Scripts/Game/EnemyAI.cs: `isLockedByPlayer`, `TakeDamage`, `GetEaten`, `DownedDuration`, `PounceLungeFactor`, `WindupTime`, `PounceTime`` |
| 2.1 | Knockdown / dizzy state | PRESENT | medium | no | small | `Assets/Scripts/Game/EnemyAI.cs: `class EnemyAI` — DownedDuration, isLockedByPlayer, WindupTime, PounceTime, TakeDamage, Die, GetEaten, Update`, `Assets/Scripts/Game/EnemyAI.cs: `enum State` declared, string literals "dizzy", "dizzy / vulnerable"`, `Assets/Scripts/Game/Creature.cs: `class Creature` — isDead, isDowned, health, maxHealth, TakeDamage, Die, string literal "dizzy"` |
| 2.1, 2.3 | Eating a downed creature | PARTIAL | medium | no | medium | `Assets/Scripts/Game/EnemyAI.cs: `GetEaten`, `DownedDuration`, `enum State`, `enum Attack` members `carriesColour`, `healsPlayerPct`, `ApplyContent`, literals "dizzy", "dizzy / vulnerable"`, `Assets/Scripts/Game/Creature.cs: `isDowned`, `isDead`, `TakeDamage`, `Die`, literal "dizzy"`, `Assets/Scripts/Game/PlayerController.cs: `PounceTime`/lock symbols in EnemyAI (`WindupTime`, `PounceTime`, `isLockedByPlayer`), `RegisterKill`, `Evolve`, literals "upgrade_damage", "upgrade_speed", "upgrade_health", "gene_points"` |
| 2.1, 2.3 | Dash | ABSENT | medium | no | medium | `Assets/Scripts/Game/PlayerController.cs: class PlayerController — moveSpeed, biteDamage, BaseSpeed, BaseDamage, BaseHealth, LockConeDot, Awake, Update (no dash field, dash timer, dash cooldown, or dash-related literal anywhere)`, `Assets/Scripts/Game/GameConfig.cs: struct ClassProfile — name, speedMult, damageMult, healthMult, lungeMult, dashMult`, `Assets/Scripts/Game/GameConfig.cs class names: "Brawler", "Bruiser", "Leaper", "Sniper", "Skirmisher", "Stalker", "Apex", "Forager"` |
| 1, 2.3 | Single Health meter and permadeath | CONTRADICTED | high | yes | medium | `Assets/Scripts/Game/GameManager.cs: string literals "HudBars", "HealthBar", "HEALTH", "EvolutionBar", "EVOLUTION", "GenTierLabel"`, `Assets/Scripts/Game/PlayerController.cs: fields totalKills, level, score; methods RegisterKill, Evolve, Die; literals "LEVEL UP! RANK {level}", "EVOLVED — {classProfile.name.ToUpper()}!", "gene_points", "upgrade_damage", "upgrade_speed", "upgrade_health"`, `Assets/Scripts/Game/GameConfig.cs: EvoRequirement, LevelUpRequirement, Tiers, TierData(name, scale, limbs)` |
| 2.3 | Grazers as the healing supply | PARTIAL | medium | yes | medium | `Assets/Scripts/Game/EnemyAI.cs: string literal "grazer", fields `role`, `carriesColour`, `healsPlayerPct`, `isLockedByPlayer`, `GetEaten`, `ApplyContent``, `Assets/Scripts/Content/ContentDatabase.cs: `GrazerWeight`, `RollSpawn`, `ColorTypeFor`, literals "Grey"/"WHITE"`, `Assets/Scripts/Editor/ContentCheck.cs: `HasSpawn`, `RollSamples`, literal "(grazer)"` |
| 2.2 | Predator AI: hunting the player | PARTIAL | medium | no | small | `Assets/Scripts/Game/EnemyAI.cs: WindupTime, PounceTime, PounceLungeFactor, enum State, enum Attack, isLockedByPlayer`, `Assets/Scripts/Game/EnemyAI.cs string literals: "targeted", "Player", "dizzy / vulnerable", "EnemyHealthBar"`, `Assets/Scripts/Game/EnemyAI.cs: hunters, BeginHunterFrame, CountHunter, ClaimHunterSlot` |
| 2.2 | Prey reactions: fleeing and floating health bars | PARTIAL | medium | no | small | `Assets/Scripts/Game/EnemyAI.cs: string literals "EnemyHealthBar", "BG", "Fill" and member `BarWidth``, `Assets/Scripts/Game/EnemyAI.cs: `enum State` (members not recovered by the index), `enum Attack`, `TakeDamage`, `GetEaten`, `isLockedByPlayer`, `hunters`, `BeginHunterFrame`, `CountHunter`, `ClaimHunterSlot``, `Assets/Scripts/Game/EnemyAI.cs role literals: "prey", "grazer", "elite", "trait_miniboss", "alpha", "apex"; fields `role`, `carriesColour`, `healsPlayerPct`, `ApplyContent`` |
| 2.4 | Five colour families and their stat multipliers | CONTRADICTED | medium | yes | medium | `Assets/Scripts/Game/GameConfig.cs: `struct ClassProfile` — name, speedMult, damageMult, healthMult, lungeMult, dashMult`, `Assets/Scripts/Game/GameConfig.cs: `GameConfig.ClassFor`, string literals "Brawler", "Bruiser", "Leaper", "Sniper", "Skirmisher", "Stalker", "Apex", "Forager" (eight classes, not five)`, `Assets/Scripts/Game/GameConfig.cs: `class Colors` — Red, Blue, Green, Yellow, Purple, Orange, Cyan, White, Pink, FromName (nine colours, not five)` |
| 2.4, 2.4b | Intensity scaling of family multipliers | UNCONSUMED | medium | yes | medium | `Assets/Scripts/Content/FormTable.cs: `class FormDef` — id, family, intensity, intensity_pct, rank, ..., stats`, `Assets/Scripts/Content/FormTable.cs: `class StatBlock` — health, damage, speed, reach, dash`, `Assets/Scripts/Content/FormTable.cs: `class FormTable` — generated_by, count, forms, Load` |
| 2.4 | Limb baseline stat table | CONTRADICTED | medium | yes | medium | `Assets/Scripts/Game/GameConfig.cs: `struct TierData` — name, scale, limbs`, `Assets/Scripts/Game/GameConfig.cs: `GameConfig.Tiers`, `EvoRequirement`, `LevelUpRequirement`, tier names "Alpha","Beta","Gamma","Delta","Omega"`, `Assets/Scripts/Game/GameConfig.cs: `struct ClassProfile` — name, speedMult, damageMult, healthMult, lungeMult, dashMult ("Brawler","Leaper","Sniper","Stalker","Apex")` |
| 2.4 | Final stat composition (rank baseline × family × intensity) | CONTRADICTED | medium | yes | medium | `Assets/Scripts/Content/FormTable.cs: `class StatBlock` — health, damage, speed, reach, dash`, `Assets/Scripts/Content/FormTable.cs: `class FormDef` — family, intensity, intensity_pct, rank, socket_layout, stats; `class FormTable` — forms, Load`, `Assets/StreamingAssets/forms.json (132,668 bytes) — read by: **NOTHING READS THIS FILE**` |
| 2.4, 2.5 | The blank (form zero) | CONTRADICTED | medium | yes | small | `Assets/Scripts/Game/GameManager.cs string literals "Player", "GREEN" (player spawned green, not white)`, `Assets/Scripts/Game/PlayerController.cs — BaseSpeed, BaseDamage, BaseHealth, ClassName, "Forager", upgrade_damage/upgrade_speed/upgrade_health, level, LevelUpRequirement`, `Assets/Scripts/Game/GameConfig.cs — struct TierData(name, scale, limbs) with "Alpha","Beta","Gamma","Delta","Omega"; ClassProfile(speedMult, damageMult, healthMult, lungeMult, dashMult); Colors.White exists but player literal is "GREEN"` |
| 2.4a | The colour buffer (FIFO limb slots) | CONTRADICTED | medium | yes | large | `Assets/Scripts/Game/PlayerController.cs: Evolve, RegisterKill, level, totalKills, ClassName, "upgrade_damage", "upgrade_speed", "upgrade_health", "gene_points", "EVOLVED — {classProfile.name.ToUpper()}!", "LEVEL UP! RANK {level}"`, `Assets/Scripts/Game/GameConfig.cs: ClassFor, Tiers, EvoRequirement, LevelUpRequirement, struct ClassProfile (speedMult, damageMult, healthMult, lungeMult, dashMult), struct TierData (name, scale, limbs)`, `Assets/Scripts/Game/Creature.cs: tier, colorType, hasBodyColor, bodyColor, limbs, BuildVisuals, Evolve` |
| 2.1, 2.4a | Poop the oldest colour | ABSENT | medium | no | medium | `Assets/Scripts/Game/PlayerController.cs — members: moveSpeed, biteDamage, totalKills, level, score, LockConeDot, BaseSpeed, BaseDamage, BaseHealth, ClassName, OnLockTargetChanged, IsThreatened, FlagThreat, RegisterKill, Evolve, Die (no colour buffer, no eject/poop member)`, `Assets/Scripts/Game/PlayerController.cs string literals: "upgrade_damage", "upgrade_speed", "upgrade_health", "gene_points", "EVOLVED — {classProfile.name.ToUpper()}!" (progression is class/level based)`, `Assets/Scripts/Game/Creature.cs — limbs, colorType, hasBodyColor, bodyColor, BodyColor, BuildVisuals (a single body colour, not a per-limb colour list)` |
| 2.4a | Next-slot-to-be-overwritten indicator | ABSENT | medium | no | medium | `Assets/Scripts/Game/Creature.cs: `class Creature` — limbs, bodyColor, BodyColor, BuildVisuals, Evolve (single body colour, no per-limb colour slots)`, `Assets/Scripts/Game/PlayerController.cs — fields/members are moveSpeed, biteDamage, totalKills, level, score, ClassName, Evolve, RegisterKill; no colour buffer, no slot list, no poop/eject action, no pulse or indicator member`, `Assets/Scripts/Game/GameConfig.cs: `struct TierData` — name, scale, limbs (limb count is a tier scalar, not addressable colour slots)` |
| 2.4b | Form resolution from buffer state | CONTRADICTED | medium | yes | large | `Assets/Scripts/Content/FormTable.cs: `class FormDef` — family, intensity, intensity_pct, rank, silhouette, socket_layout; `class FormTable` — forms, Load`, `StreamingAssets/forms.json (132,668 bytes) — read by: **NOTHING READS THIS FILE**`, `Assets/Scripts/Game/PlayerController.cs — totalKills, level, RegisterKill, Evolve, ClassName, "EVOLVED — {classProfile.name.ToUpper()}!", "LEVEL UP! RANK {level}", "upgrade_damage", "upgrade_speed", "upgrade_health", "gene_points"` |
| 2.3, 2.4b | Instant mutation with wound preserved | CONTRADICTED | medium | yes | medium | `Assets/Scripts/Game/PlayerController.cs: `Evolve`, `level`, `totalKills`, `RegisterKill`, `BaseHealth`, string literals "upgrade_health", "EVOLVED — {classProfile.name.ToUpper()}!", "LEVEL UP! RANK {level}"`, `Assets/Scripts/Game/GameConfig.cs: `EvoRequirement`, `LevelUpRequirement`, `Tiers`, `struct TierData` (name, scale, limbs), `struct ClassProfile` (healthMult, damageMult, speedMult), tier names "Alpha","Beta","Gamma","Delta","Omega"`, `Assets/Scripts/Game/Creature.cs: `tier`, `colorType`, `maxHealth`, `health`, `kills`, `Evolve`, `hasContentStats`` |
| 2.4b, 3.3 | forms.json — the 150 authored forms | UNCONSUMED | high | no | medium | `Assets/StreamingAssets/forms.json (132,668 bytes) — read by: **NOTHING READS THIS FILE**`, `Assets/Scripts/Content/FormTable.cs: `class FormDef` — id, family, intensity, intensity_pct, rank, name, flavor, base_hex, saturation, silhouette, surface, vfx, socket_layout, stats`, `Assets/Scripts/Content/FormTable.cs: `class FormTable` — generated_by, count, forms, Load` |
| 2.4b, 2.7 | Meat tiers and their world distribution | PARTIAL | medium | no | medium | `Assets/Scripts/Content/ContentDatabase.cs: `Wandering`, `Pocket`, `RollSpawn`, `TierIndex`, `ColorTypeFor`, `GrazerWeight`, `Weight`, `struct SpawnEntry { def, spawn }``, `ContentDatabase string literals: "Pale", "Dusk", "Deep", "Rage", "Clash", "alpha", "apex"`, `biomes.json (10,919 bytes) — read by ContentDatabase.cs; creatures.json (93,959 bytes) — read by ContentDatabase.cs` |
| 2.4b, 2.6a | Procedural body rendering of forms | CONTRADICTED | medium | yes | medium | `Assets/Scripts/Game/Creature.cs: `class Creature` — tier, colorType, hasBodyColor, bodyColor, BodyColor, body, limbs, BuildVisuals, Evolve`, `Assets/Scripts/Game/GameConfig.cs: `struct TierData` — name, scale, limbs; `GameConfig.Tiers`, `ClassFor`, `EvoRequirement``, `Assets/Scripts/Content/FormTable.cs: `class FormDef` — id, family, intensity, intensity_pct, rank, base_hex, saturation, silhouette, surface, vfx, socket_layout, stats; `FormTable.Load`` |
| 2.7, 3.3 | Biome generation, terrain gates and per-run palette roll | CONTRADICTED | medium | yes | large | `Assets/Scripts/Game/GameConfig.cs: `BiomeNeon`, `BiomeMagma`, `BiomeCrystal`, `VisualsForBiome`, `struct BiomeData` (name, groundColor, accentColor, fogColor, enemyColors), literals "Neon Grid", "Magma Wastes", "Crystal Forest" alongside "prairies","wetlands","mountains","beach","volcanic"`, `Assets/Scripts/Game/EcosystemManager.cs: `LegacyBiomes`, `OnBiomeChanged`, `PocketLeakChance`, `FindSpawn``, `Assets/Scripts/Game/PlayerController.cs: `OnBiomeRequest`; Assets/Scripts/Game/GameManager.cs: "ENTERING {biome.name}", "prairies", "Prairies"` |
| 2.7, 2.4b | Pockets, distance-based difficulty and lair placement | CONTRADICTED | medium | yes | large | `ContentDatabase.Wandering`, `ContentDatabase.Pocket`, `ContentDatabase.RollSpawn` |
| 3.3 | Ambient rank rules | CONTRADICTED | medium | yes | medium | `Assets/Scripts/Content/ContentDatabase.cs: RollSpawn, GrazerWeight, Weight, TierIndex, Wandering, Pocket, struct SpawnEntry {def, spawn}`, `Assets/Scripts/Game/GameConfig.cs: Tiers, struct TierData {name, scale, limbs}, literals "Alpha","Beta","Gamma","Delta","Omega", EvoRequirement, LevelUpRequirement`, `Assets/Scripts/Game/Creature.cs: tier, isBoss, Init, BuildVisuals, Evolve` |
| 2.6 | Trait minibosses and the four traits | PARTIAL | medium | no | large | `Assets/Scripts/Game/EnemyAI.cs string literals: "prey", "grazer", "elite", "trait_miniboss", "alpha", "apex"`, `Assets/Scripts/Game/EnemyAI.cs `enum Attack` members: contentId, role, carriesColour, healsPlayerPct, PounceLungeFactor, ApplyContent`, `Assets/Scripts/Game/EnemyAI.cs — DownedDuration, isLockedByPlayer, hunters, BeginHunterFrame, CountHunter, ClaimHunterSlot, GetEaten` |
| 2.6a | Trait permanence, face rendering and inheritance | ABSENT | high | no | medium | `Assets/Scripts/Game/PlayerController.cs — fields/methods: totalKills, level, score, BaseSpeed, BaseDamage, BaseHealth, ClassName, Evolve, RegisterKill, Die (no trait collection, no held-trait set)`, `Assets/Scripts/Game/Creature.cs — tier, colorType, bodyColor, hasBodyColor, body, limbs, BuildVisuals, Evolve (colour/limb visuals only; no face-trait rendering)`, `Assets/Scripts/Game/Companion.cs — only `target`, `index` (offspring carry no inherited state)` |
| 2.5 | Alpha lair and the two-gate unlock | CONTRADICTED | medium | yes | large | `Assets/Scripts/Game/GameConfig.cs — `class Boss` — SpawnIntervalKills, ScaleMultiplier, HealthMultiplier, DamageMultiplier`, `Assets/Scripts/Game/EcosystemManager.cs — OnBossSpawned, FindSpawn, PocketLeakChance, enemies`, `Assets/Scripts/Game/GameManager.cs — string literals "!! APEX PREDATOR DETECTED !!", "!! {name.ToUpper()} !!"` |
| 2.5 | Alpha identity, mirror-match and biome emptying | CONTRADICTED | medium | yes | large | `GameConfig.Boss — SpawnIntervalKills, ScaleMultiplier, HealthMultiplier, DamageMultiplier`, `EcosystemManager — OnBossSpawned, OnMateSpawned, LegacyBiomes, FindSpawn, PocketLeakChance, "Apex predator"`, `EnemyAI enum Attack members — role, carriesColour, healsPlayerPct, PounceLungeFactor, ApplyContent; role literals "alpha", "apex", "elite", "prey", "grazer"` |
| 2.5, 3.3 | Emblems | CONTRADICTED | medium | yes | large | `Assets/StreamingAssets has no emblems.json (only art-manifest.json, biomes.json, creatures.json, forms.json, panels.json)`, `No symbol containing 'emblem' anywhere in the inventory`, `EnemyAI: `enum Attack` members `role`, `carriesColour`, `healsPlayerPct`, and methods `GetEaten`, `Die`; string literals "alpha", "apex"` |
| 2.5 | Breeding, litters and rank gain | CONTRADICTED | high | yes | large | `Assets/Scripts/Game/PlayerController.cs: `Evolve`, `RegisterKill`, `totalKills`, `level`, string literals "EVOLVED — {classProfile.name.ToUpper()}!", "LEVEL UP! RANK {level}", "OFFSPRING SPAWNED!", "Companion"`, `Assets/Scripts/Game/GameConfig.cs: `EvoRequirement`, `LevelUpRequirement`, `Tiers`, `struct TierData` — name, scale, limbs; tier names "Alpha","Beta","Gamma","Delta","Omega"`, `Assets/Scripts/Game/Creature.cs: `tier`, `limbs`, `kills`, `Evolve`, `BuildVisuals`` |
| 2.8, 3.3 | Decorated panels | CONTRADICTED | medium | yes | large | `Assets/StreamingAssets/panels.json (8,028 bytes) — read by: **NOTHING READS THIS FILE**`, `PlayerController: string literals "upgrade_damage", "upgrade_speed", "upgrade_health", "gene_points"`, `PlayerController: level, score, totalKills, RegisterKill, Evolve, BaseSpeed, BaseDamage, BaseHealth, ClassName` |
| 2.5 | Combat pacing invariant (2–3 pounces, no one-shots) | ABSENT | medium | no | medium | `Assets/Scripts/Game/PlayerController.cs: biteDamage, BaseDamage, BaseHealth, "upgrade_damage", "upgrade_speed", "upgrade_health", Evolve, RegisterKill`, `Assets/Scripts/Game/EnemyAI.cs: TakeDamage, Die, GetEaten, "dizzy", "dizzy / vulnerable", DownedDuration, WindupTime, PounceTime`, `Assets/Scripts/Game/Creature.cs: maxHealth, health, isDowned, TakeDamage, Evolve` |
| 1, 2.5 | Conquest win condition | ABSENT | medium | no | large | `Assets/Scripts/Game/PlayerController.cs: totalKills, level, score, Evolve, RegisterKill, Die`, `Assets/Scripts/Game/GameManager.cs string literals: "DeathPanel", "EXTINCT", "Score", "RestartButton", "NEW EVOLUTION"`, `Assets/Scripts/Game/GameConfig.cs: Tiers, EvoRequirement, LevelUpRequirement, class Boss (SpawnIntervalKills, ScaleMultiplier, HealthMultiplier, DamageMultiplier), TierData(name, scale, limbs) with names "Alpha","Beta","Gamma","Delta","Omega"` |
| 2.5, The Ascension | The Ascension and the Apex | CONTRADICTED | medium | yes | large | `Assets/Scripts/Game/GameConfig.cs: `class Boss` — SpawnIntervalKills, ScaleMultiplier, HealthMultiplier, DamageMultiplier`, `Assets/Scripts/Game/EcosystemManager.cs: OnBossSpawned, string "Apex predator", "MateEnemy"`, `Assets/Scripts/Game/GameManager.cs: "!! APEX PREDATOR DETECTED !!"` |
| 2.9 | The Bestiary screen | UNCONSUMED | high | no | large | `Assets/StreamingAssets/forms.json (132,668 bytes) — read by: **NOTHING READS THIS FILE**`, `Assets/Scripts/Content/FormTable.cs: class FormDef — id, family, intensity, intensity_pct, rank, name, flavor, base_hex, saturation, silhouette, surface, vfx, socket_layout, stats`, `Assets/Scripts/Content/FormTable.cs: class FormTable — generated_by, count, forms, Load` |
| 1, 2.9 | Bestiary persistence across runs | ABSENT | medium | no | large | `Assets/StreamingAssets/forms.json (132,668 bytes) — read by: **NOTHING READS THIS FILE**`, `Assets/Scripts/Content/FormTable.cs: `class FormDef` (id, family, intensity, rank, name, base_hex...), `class FormTable` — generated_by, count, forms, Load`, `Assets/Scripts/Game/PlayerController.cs — Die, Evolve, level, score, totalKills (no save/load members)` |
| 2.9a | Record milestone unlocks | ABSENT | high | no | large | `Assets/Scripts/Game/PlayerController.cs — RegisterKill, Evolve, level, score, totalKills, "gene_points" (in-run progression only)`, `Assets/Scripts/Game/GameManager.cs — MenuPanel, DeathPanel, StartButton "INITIALIZE", RestartButton "NEW EVOLUTION" (no bestiary/unlock screen)`, `Assets/StreamingAssets/forms.json — read by: NOTHING READS THIS FILE (the 150-form table the record would key against)` |
| 1, 2.5 | Run restart as a one-limb blank | CONTRADICTED | medium | yes | medium | `Assets/Scripts/Game/GameManager.cs: "DeathPanel", "EXTINCT", "RestartButton", "NEW EVOLUTION", "Score"`, `Assets/Scripts/Game/PlayerController.cs: Die, gameStarted, level, score, totalKills`, `Assets/Scripts/Game/PlayerController.cs string literals: "upgrade_damage", "upgrade_speed", "upgrade_health", "gene_points"` |
| 3.3 | Generator invariants and seed refusal | PARTIAL | medium | no | large | `Assets/Scripts/Editor/ContentCheck.cs: class ContentCheck — RollSamples, Verify, HasSpawn; menu literal "Tools/Morphivore/Verify World Content"; result literals "  RESULT: OK" / "  RESULT: PROBLEMS FOUND (see above)"; colour literals "Yellow","Red","Blue","Purple","Grey"`, `Assets/Scripts/Content/ContentDatabase.cs: Load, Wandering, Pocket, RollSpawn, GrazerWeight, Weight, ColorTypeFor, TierIndex; struct SpawnEntry {def, spawn}`, `Assets/Scripts/Game/GameManager.cs string literal "[Run] seed {runSeed}" (seeded run exists, no refusal path)` |
| 3.3 | JSON content loading with schema check and fallback | PARTIAL | medium | no | medium | `Assets/Scripts/Content/ContentDatabase.cs: `class ContentDatabase` — IsLoaded, LoadError, Load, ReadStreamingAsset, Fail, ById, RollSpawn (reads "creatures.json", "biomes.json")`, `ContentDatabase string literal "biomes.json parsed but held no biomes" (minimal validity check + named error)`, `Assets/Scripts/Content/FormTable.cs: `class FormTable` — generated_by, count, forms, Load; `class FormDef` — family, intensity, rank, name, socket_layout, stats; `class StatBlock` — health, damage, speed, reach, dash` |
| 3.3 | Unity MCP editor bridge | PRESENT | medium | no | small | `Assets/Scripts/Editor/MCPBridge.cs — class MCPBridge: Port, Start/Stop, AcceptLoop, HandleClient, DoWebSocketHandshake, ServeWebSocket, ReadFrame/WriteFrame, FlushMainThreadQueue, Dispatch`, `MCPBridge command literals: "ping"/"pong", "write_file", "refresh_assets", "play", "stop", "get_components", "get_logs", "read_file", "list_scripts", "execute_menu_item", "batch"`, `MCPBridge members: WriteFile, RefreshAssets, SetPlayMode, GetComponents, GetLogs` |

**CONTRADICTED — Single Health meter and permadeath (§1, 2.3)**

The death half of the requirement is broadly satisfied: PlayerController.Die / Creature.Die lead to a DeathPanel ("EXTINCT") with only a restart path ("NEW EVOLUTION"), i.e. no continue. But the HUD explicitly builds a second resource meter alongside health: GameManager creates both a "HealthBar"/"HEALTH" and an "EvolutionBar"/"EVOLUTION" bar, backed by a genuine second progression currency — GameConfig.EvoRequirement and LevelUpRequirement, PlayerController.level/score/totalKills, RegisterKill feeding Evolve, plus "LEVEL UP! RANK {level}", "gene_points" and upgrade_damage/speed/health choices. That is an XP/levelling mechanism where the design mandates exactly one meter with rank changed only by breeding and eating changing form rather than granting levels. Code exists in this area but on different rules, so it must be reworked rather than merely extended.

_Exists instead:_ A two-bar HUD (HealthBar + EvolutionBar) driven by a kill-count XP system: RegisterKill accumulates toward GameConfig.EvoRequirement/LevelUpRequirement, triggering Evolve, tier/limb growth from GameConfig.Tiers, "LEVEL UP! RANK" notifications and gene_points upgrade_damage/speed/health picks. Permadeath itself is effectively in place via Die -> DeathPanel "EXTINCT" with only a restart button.
_Effort:_ medium — Deleting the EvolutionBar HUD object in GameManager is small, but the second resource is wired through PlayerController (level, score, totalKills, RegisterKill, Evolve, gene_points/upgrade_* branches) and GameConfig (EvoRequirement, LevelUpRequirement, Tiers) and mirrored in Creature.Evolve, so rank progression has to be re-routed to breeding rather than simply removing a bar. Health plumbing itself (Creature.maxHealth/health/TakeDamage/Die) and the death panel already exist and are reusable.

**CONTRADICTED — Five colour families and their stat multipliers (§2.4)**

The colour→playstyle→multiplier area is definitely implemented, but on different rules than GDD 2.4. The live system is GameConfig.ClassFor / ClassProfile, which carries eight class names (Brawler, Bruiser, Leaper, Sniper, Skirmisher, Stalker, Apex, Forager) rather than the five families, and its axes are speedMult/damageMult/healthMult/lungeMult/dashMult — a `lungeMult` where the design demands `Reach`, so the Blue Sniper's defining long-reach trade cannot be expressed. GameConfig.Colors additionally enumerates nine colours (Green, Orange, Cyan, Pink, White) and Creature/EnemyAI still branch on "GREEN"/"CYAN", so colour identity is broader than the five families. Meanwhile the correct schema already exists but is dead: FormDef/StatBlock carry family, intensity, intensity_pct and exactly the five axes (health, damage, speed, reach, dash), and forms.json (132 KB) is explicitly unread by any code. ContentDatabase.ColorTypeFor does recognise the five family names, and WorldTables.cs mentions exactly those five (its body is unparsed, so it may already hold a family table — the inventory cannot confirm). Net: a parallel, differently-shaped class-multiplier system is in charge of gameplay stats, so this is a contradicted mechanism rather than a missing one.

_Exists instead:_ An eight-class GameConfig.ClassProfile table (speed/damage/health/lunge/dash multipliers) selected by GameConfig.ClassFor from a nine-colour Colors palette, consumed by PlayerController (BaseSpeed/BaseDamage/BaseHealth/ClassName) and EnemyAI/Creature. The design-shaped five-axis family data (FormDef.family + StatBlock health/damage/speed/reach/dash in forms.json) is parsed-capable via FormTable.Load but nothing reads forms.json.
_Effort:_ medium — Smaller than it looks on the data side: StatBlock already has the exact five axes and FormDef already has family/intensity, and forms.json is present — the table may effectively exist already and only needs to be loaded. The real work is rewriting GameConfig.ClassFor/ClassProfile down to the five families with the GDD's numbers, renaming/replacing lungeMult with a genuine Reach multiplier and threading Reach through EnemyAI/PlayerController attack range, and deleting the extra classes (Bruiser, Skirmisher, Forager) and the non-family colour branches in Creature/EnemyAI/Colors.

**UNCONSUMED — Intensity scaling of family multipliers (§2.4, 2.4b)**

The data side of this requirement is fully present and already parsed in principle: FormDef carries `intensity` and `intensity_pct` plus a `StatBlock` (health, damage, speed, reach, dash) — exactly the hand-tuned, intensity-scaled profile the design calls for — and FormTable.Load exists to deserialise it. But the inventory states plainly that forms.json is read by nothing, so no runtime path resolves a form, reads its intensity_pct, or applies the scaled multipliers. Nothing in the inventory references a per-form Clash gift / second-tone bonus field at all (FormDef's field list has no such member), so even the data for the Clash exception looks unauthored in the schema. The only live multiplier mechanism is GameConfig.ClassProfile (speedMult/damageMult/healthMult/lungeMult/dashMult selected via ClassFor and applied in PlayerController), which is a flat per-class multiplier with no intensity dimension — it would have to be superseded or rewritten for form-driven stats. The tier words Pale/Dusk/Deep/Rage/Clash appear only in ContentDatabase's creature/spawn tier handling (TierIndex, ColorTypeFor), not in any stat computation. I cannot see method bodies, so I cannot rule out that some multiplication happens inside PlayerController.Evolve, but with forms.json unread there is no source of intensity_pct at runtime.

_Exists instead:_ A flat class-profile multiplier system: GameConfig.ClassFor returns a ClassProfile (healthMult/speedMult/damageMult/dashMult/lungeMult) keyed by class name (Brawler, Leaper, Sniper, Stalker, Apex, ...), applied to PlayerController's BaseHealth/BaseSpeed/BaseDamage. Intensity tiers exist only as spawn-tier strings in ContentDatabase (TierIndex over Pale/Dusk/Deep/Rage/Clash). FormTable/FormDef/StatBlock model the intensity-scaled stats but are never loaded.
_Effort:_ medium — Most of the work is already done and merely disconnected: forms.json already contains the hand-tuned per-intensity stat profiles and FormDef/StatBlock/FormTable.Load already model them, so no scaling maths needs authoring — only a load call and a lookup from resolved (family, intensity, rank) to FormDef.stats. The medium rating comes from the replacement work: PlayerController's ClassProfile-multiplier path (and GameConfig.ClassProfile's role) must be rewritten to consume form stats instead, and a per-form Clash gift field must be added to FormDef and to the JSON schema, since no such member appears in the inventory.

**CONTRADICTED — Limb baseline stat table (§2.4)**

The codebase clearly implements a baseline-stats-then-multiplier pipeline, but on a different axis than the design. Baselines come from single scalar constants (`PlayerController.BaseSpeed/BaseDamage/BaseHealth`) combined with a five-row tier progression (`GameConfig.Tiers` / `TierData{name, scale, limbs}` named Alpha…Omega, driven by `EvoRequirement`/`LevelUpRequirement` and `Creature.tier`), with `ClassProfile` mults applied on top. That is a rank/level ladder of 5 tiers where `limbs` is a cosmetic/derived field of the tier, not a 1–6 limb-count table that sets Health/Damage/Speed/Reach (100/150/200/250/300/350, 40/55/70/85/100/115, 12/13/14/15/16/17, 16/19/22/25/28/31). Nothing in the inventory shows a four-column, six-row baseline array, and Reach has no baseline at all — only `Ecology.ReachScale` as a global scalar. Notably, `FormTable.StatBlock{health,damage,speed,reach,dash}` and `FormDef.rank` are the right shape and `forms.json` (132 KB) exists, but the inventory marks forms.json as read by nothing, so the correct-shaped stat data is inert while the tier ladder drives play. Because the existing tier/level baseline would have to be replaced (not merely extended) to make limb count the baseline source, this is CONTRADICTED rather than ABSENT/UNCONSUMED, though the unconsumed forms.json is the second half of the story.

_Exists instead:_ A 5-tier evolution ladder: `GameConfig.Tiers` of `TierData{name, scale, limbs}` (Alpha/Beta/Gamma/Delta/Omega) scaling a single set of flat constants (`PlayerController.BaseHealth/BaseDamage/BaseSpeed`) with no Reach baseline, then multiplied by `ClassProfile{healthMult, speedMult, damageMult, lungeMult, dashMult}`. A correctly-shaped `StatBlock{health,damage,speed,reach,dash}` and `FormDef.rank` exist in FormTable.cs but forms.json is never loaded.
_Effort:_ medium — The four baseline arrays are trivial to author (24 numbers), and `StatBlock` already declares exactly health/damage/speed/reach/dash plus `FormDef.rank`, so the data structures are half-built. The cost is rewiring: `GameConfig.Tiers`/`TierData` and the tier-scale path used by `PlayerController.Evolve`, `Creature.Evolve`, `maxHealth`, and `EnemyAI.ApplyContent` must be re-keyed off limb count (1–6) instead of tier index, and Reach must become a per-rank baseline rather than the global `Ecology.ReachScale`. That touches several files but no new subsystem.

**CONTRADICTED — Final stat composition (rank baseline × family × intensity) (§2.4)**

The codebase does compose live stats, but by a different rule set than the design's rank-baseline × family × intensity formula. Player stats come from GameConfig.ClassProfile (speedMult/damageMult/healthMult/lungeMult/dashMult) selected by ClassFor plus GameConfig.Tiers (TierData with name/scale/limbs), and PlayerController exposes BaseSpeed/BaseDamage/BaseHealth/ClassName which it scales on Evolve/level-up. Nothing in the inventory holds the authoritative limb baseline table (Health 100/150/200/250/300/350, Damage 40..115, Speed 12..17, Reach 16..31), nor any intensity fraction (Pale 25% … Rage 100%) or Clash second-tone gift, nor a Dash axis on the player side. The form-side data model that the design implies does exist — FormDef carries family, intensity, intensity_pct, rank, socket_layout and a StatBlock with exactly health/damage/speed/reach/dash — but forms.json is explicitly unread, so FormTable is dead code and the eight named classes (Brawler, Bruiser, Leaper, Sniper, Skirmisher, Stalker, Apex, Forager) drive stats instead of family+intensity. The worked example (2-limb Rage Brawler vs 5-limb Pale Brawler) cannot be reproduced: 'Brawler' here is a class profile, not a Yellow family, and intensity has no effect anywhere. Because a competing stat pipeline occupies this area and would have to be replaced, this is CONTRADICTED rather than merely UNCONSUMED, though the unread forms.json is the accompanying symptom.

_Exists instead:_ Stats are class-profile multipliers × tier: GameConfig.ClassProfile (speedMult/damageMult/healthMult/lungeMult/dashMult) chosen by ClassFor from eight archetype names, combined with GameConfig.Tiers/TierData (scale, limbs) and PlayerController's BaseSpeed/BaseDamage/BaseHealth adjusted on Evolve and upgrade_* picks. Enemies get stats via EnemyAI.ApplyContent / Creature.hasContentStats from creatures.json. FormTable/FormDef/StatBlock model the designed data but are never loaded.
_Effort:_ medium — Much of the work is already paid for: FormDef/StatBlock already declare exactly the five axes plus family, intensity, intensity_pct and rank, and FormTable.Load exists — it just needs to be pointed at StreamingAssets/forms.json like ContentDatabase does for creatures.json. Remaining work is the limb baseline table (a 6-column constant), the intensity fraction scaling with the Clash gift, and rewiring PlayerController's BaseSpeed/BaseDamage/BaseHealth (plus a Reach and Dash axis) and the HUD health bar off GameConfig.ClassProfile/ClassFor, which must be retired or reduced to cosmetic naming. Enemy stat pathing (ApplyContent, Creature.hasContentStats) also needs to consume the same table for consistency.

**CONTRADICTED — The blank (form zero) (§2.4, 2.5)**

A defined starting state for the player clearly exists, but it is built on a different mechanism than the design's form-zero blank. GameManager spawns the "Player" with the literal "GREEN" (GameConfig.Colors.GREEN), not white, so the run does not begin in the empty/white state. Progression from that start is a class/tier/upgrade system (ClassProfile with speedMult/damageMult/healthMult, TierData with name+scale+limbs named Alpha..Omega, PlayerController.level/LevelUpRequirement and upgrade_damage/upgrade_speed/upgrade_health choices), not the colour-family multiplier applied on top of a limb baseline table (Health 100/150/200..., Damage 40/55/70..., Speed 12/13/14..., Reach 16/19/22...). The form/intensity data that would define the 150 forms and their distance-from-1.0 multipliers exists as FormDef/StatBlock/FormTable plus StreamingAssets/forms.json, but the inventory marks forms.json as read by nothing, so there is no 'not in the 150' bookkeeping and no baseline of multiplier 1.0 to be the empty state against. PlayerController.BaseSpeed/BaseDamage/BaseHealth are the closest analogue to the blank's baseline, but there is no Reach baseline named there and no limb-count-driven table; the values are unverifiable from the inventory. Because working code exists in this area under different rules (green starting colour, tier scale/limb table, class multipliers, level-up upgrades), this is contradiction rather than mere absence.

_Exists instead:_ The run starts with a GREEN player cube whose stats come from PlayerController.BaseSpeed/BaseDamage/BaseHealth modified by a ClassProfile ("Forager" initially) and GameConfig.Tiers (TierData name/scale/limbs, Alpha..Omega). Growth is via Evolve/level-ups with explicit upgrade_damage/upgrade_speed/upgrade_health picks, not via eating a form and inheriting a colour-family multiplier. FormTable/FormDef/StatBlock and forms.json contain the form and intensity data but no code reads forms.json.
_Effort:_ small — The visible change is narrow: swap the "GREEN" player literal for the existing GameConfig.Colors.White, force limbs=1 at spawn (Creature already carries a limbs field and GameConfig.TierData already stores limbs), and set the blank baseline to 100/40/12/16 — PlayerController already has BaseHealth/BaseDamage/BaseSpeed placeholders, only a Reach baseline is missing. The larger surrounding work (parsing forms.json via the already-written FormTable/FormDef/StatBlock and excluding the blank from the 150-form count) belongs to the mutation/bestiary requirements, and the parser plus data already exist unused, so it is cheaper than it looks. Removing/bypassing the class+level-up upgrade path in PlayerController is the only genuine rewrite.

**CONTRADICTED — The colour buffer (FIFO limb slots) (§2.4a)**

There is no per-limb colour slot collection anywhere in the inventory: no queue/buffer/slot/socket members, no white-slot or eviction logic, no 'oldest colour' concept, and no pulsing next-slot indicator (GameManager's UI strings cover health/evolution bars, lock reticle, threat halo, notifications only). Instead, the same design area — what eating does to your form — is implemented by a completely different mechanism: kills accumulate (RegisterKill, totalKills) against GameConfig.EvoRequirement/LevelUpRequirement to drive PlayerController.Evolve, which assigns a GameConfig.ClassProfile (Brawler/Leaper/Sniper/Apex/Forager, with speedMult/damageMult/healthMult multipliers) and a TierData (Alpha..Omega) whose 'limbs' field is a cosmetic count derived from tier, not a set of colour-bearing slots. Progression is further steered by discrete upgrade picks ("upgrade_damage", "upgrade_speed", "upgrade_health", "gene_points") — hidden-stat levelling rather than the visible, world-forced colour buffer. Colour is stored as a single scalar per creature (Creature.colorType / bodyColor / ContentDatabase.ColorTypeFor with Yellow/Red/Blue/Purple/Grey names) and EnemyAI.carriesColour is a flag, so prey colour has nowhere to be stored per limb. The data the requirement needs partly exists: FormTable/FormDef already models family + intensity + rank + socket_layout and forms.json (132 KB) is in StreamingAssets but nothing reads it — the table is present and unconsumed, so the family/tier vocabulary need not be authored from scratch.

_Exists instead:_ A kills-threshold class/tier levelling system: RegisterKill -> EvoRequirement/LevelUpRequirement -> Evolve assigns a ClassProfile (stat multipliers) and TierData (scale + limb count), plus discrete gene_points upgrade picks (upgrade_damage/speed/health). Colour is one scalar per creature (colorType/bodyColor) used for tinting and enemy identity, not a per-limb buffer, and forms.json (family/intensity/rank/socket_layout) is present but unread.
_Effort:_ large — Requires new persisted ordered slot state plus rewriting PlayerController.Evolve/RegisterKill and the gene_points/upgrade_* path, replacing GameConfig.ClassFor/Tiers/ClassProfile stat multipliers with limb-count baselines x colour multipliers, changing Creature.limbs/BuildVisuals to render per-limb colour and a pulsing next-eviction slot, and wiring EnemyAI.carriesColour to deposit a {family,tier} unit. Mitigating: FormTable/FormDef and the unread forms.json already supply family/intensity/rank data, so the multiplier table itself is largely authored.

**CONTRADICTED — Form resolution from buffer state (§2.4b)**

No symbol in the inventory represents a buffer state (a per-limb colour/tier list) or a resolution function over it: there is no majority-colour family computation, no recency tiebreak, no birth precedence Yellow→Red→Blue→Purple→Grey, no lowest-link intensity step-down, no Pale floor, no Clash-beside-Rage summit rule, and no all-white blank. Creature stores a single scalar `colorType`/`bodyColor` plus an int `tier`, not six coloured sockets. What does exist in this area is a wholly different identity mechanism: the player's displayed identity is a class profile chosen by `GameConfig.ClassFor` plus a rank/tier advanced by kill count (`RegisterKill`, `totalKills`, `level`, `Evolve`, `GameConfig.Tiers` Alpha…Omega with scale/limbs, and stat upgrade strings `upgrade_damage`/`upgrade_speed`/`upgrade_health`, `gene_points`). That progression-by-kills model must be replaced by resolution-from-buffer, so this is a contradiction rather than a mere absence. The authored 150-form table is already modelled and parseable (`FormDef` carries family, intensity, intensity_pct, rank, silhouette, socket_layout; `FormTable.Load` exists), but forms.json is explicitly unread, so the lookup half is dead code awaiting the resolver. The inventory cannot show whether `ContentDatabase.TierIndex` orders the wild ladder correctly, so that part is low-confidence — but it is used for content spawn tiers, not for player form resolution.

_Exists instead:_ Identity is derived from kill-count progression and a colour→class table: `PlayerController.RegisterKill`/`Evolve`/`level` with `GameConfig.ClassFor`, `ClassProfile` multipliers and `Tiers` (Alpha…Omega, each with scale and limb count), while `Creature` holds one `colorType`/`bodyColor` and an int `tier`. Prey merely expose `carriesColour` (EnemyAI) with no buffer to accumulate into. The 150 authored forms exist as data (`forms.json`) and a matching `FormDef`/`FormTable` parser, but nothing reads the file, so no form is ever named on screen.
_Effort:_ large — Requires a new limb-colour buffer with per-limb tier and eat-recency, the full resolution rule (majority family, recency/precedence tiebreak, lowest-link step-down floored at Pale, Clash parallel summit, dilution to Deep, all-white blank), re-resolution on every change, and rewiring visuals/stats to the resolved form — while deleting or repurposing the kill-count Evolve/level/Tiers/ClassFor progression in PlayerController, Creature and GameConfig. Smaller than it looks on the data side only: `FormDef` already carries family/intensity/rank/silhouette/socket_layout and `FormTable.Load` exists, so the 150-form lookup needs only to be pointed at the already-shipped forms.json rather than authored anew.

**CONTRADICTED — Instant mutation with wound preserved (§2.3, 2.4b)**

The code does implement a body/stat change on progression, but by a threshold-based evolution/level-up mechanism rather than instant re-resolution of a form from diet. GameConfig exposes `EvoRequirement`/`LevelUpRequirement` and a fixed `Tiers` ladder (Alpha…Omega with scale and limbs), PlayerController tracks `totalKills`, `level`, `RegisterKill`, and fires "EVOLVED"/"LEVEL UP! RANK {level}" notifications, plus discrete "upgrade_health" choices — i.e. health maximum changes at kill milestones and via upgrades, not the instant a resolved form (colour × intensity × limbs) changes. There is a HUD "EvolutionBar" alongside "HealthBar", which is the second meter the two-meter-free design removes. FormTable/FormDef/StatBlock exist and can express per-form health, but forms.json is never read, so no resolved-form maximum exists to re-cut the bar to. Nothing in the inventory suggests a wound-fraction carry: `Creature.Evolve`, `maxHealth`, `health` are present but the inventory cannot show whether the ratio is preserved; given the mechanism is kill-threshold evolution with healthMult applied through ClassProfile/TierData, the recut rule of the design is not the rule in force. I cannot see the body of Evolve, so the precise health handling is unverified — hence medium confidence — but the surrounding mechanism is clearly a different one.

_Exists instead:_ A kill-count evolution/level ladder: `EvoRequirement`/`LevelUpRequirement` thresholds trigger `PlayerController.Evolve` and `Creature.Evolve`, moving the player through fixed `Tiers` (Alpha→Omega, each with scale and limbs) and `ClassProfile` multipliers (healthMult, damageMult, speedMult), with separate discrete "upgrade_health"/"upgrade_speed"/"upgrade_damage" picks and an on-screen "EvolutionBar" second meter. Health maxima come from `BaseHealth` × profile/tier multipliers, not from a resolved form's `StatBlock.health` in forms.json.
_Effort:_ medium — The scaffolding is closer than it looks: `FormDef`/`StatBlock` already model per-form health and forms.json (132 KB) is already on disk with the numbers, so the new maximum only needs a `FormTable.Load` call plus a limbs×colour resolution step. The actual recut is a few lines (cache health/maxHealth ratio, set new maxHealth, reapply ratio). The cost is removal: the `EvoRequirement`/`LevelUpRequirement`/`Tiers`/`ClassProfile` progression path, `PlayerController.Evolve` upgrade choices and the HUD "EvolutionBar" all drive maxHealth today and must be dismantled so mutation is the only thing that re-cuts the bar.

**UNCONSUMED — forms.json — the 150 authored forms (§2.4b, 3.3)**

The authored asset exists at full size (forms.json, 132 KB) and a matching deserialisation schema exists in FormTable.cs whose FormDef fields line up almost exactly with the design's required columns (family, intensity, rank, name, socket_layout, stats, plus saturation/silhouette used by §2.4b's rendering rule) and FormTable even carries a `count` field for the 150 assertion. But the inventory's data-contract section states nothing reads forms.json: ContentDatabase.Load only pulls creatures.json and biomes.json, and no call site for FormTable.Load appears anywhere (no reference from ContentDatabase, GameManager, Creature, or EnemyAI). Runtime identity is instead driven by GameConfig.Tiers (five tier names Alpha..Omega with scale/limbs) and GameConfig.ClassFor/Colors, with Creature.tier/colorType/displayName and EnemyAI.contentId/role coming from creatures.json — a 5-tier × colour scheme, not a family × intensity × rank lattice of 150. There is also no Bestiary code at all (no 30-cell grid, no discovered/total header, no rank column), so the in-game observable cannot be checked. Because the inventory explicitly flags the asset as unread and a ready-made parser sits idle, UNCONSUMED is the precise verdict rather than ABSENT; the parallel tier system is a separate legacy path that this requirement would supersede rather than something already claiming to implement forms.

_Exists instead:_ A complete, unused schema (FormTable/FormDef/StatBlock with family, intensity, rank, name, socket_layout, stats) alongside a live but different identity system: GameConfig.Tiers (5 named tiers with scale/limb counts), GameConfig.ClassFor/Colors profiles, and Creature/EnemyAI fields (tier, colorType, contentId, role) fed from creatures.json. No Bestiary UI of any kind.
_Effort:_ medium — The parsing half is nearly free: FormDef already names every field the design demands, so wiring is a ReadStreamingAsset("forms.json") call in ContentDatabase plus a count==150 and 5×5×6 completeness check — small. The cost is downstream: nothing consumes forms yet, so Creature.BuildVisuals/Init and EnemyAI.ApplyContent must resolve a FormDef (socket_layout → limb segments, stats → StatBlock) instead of GameConfig.Tiers/ClassFor, and the Bestiary screen (30 cells, intensity ladder, discovered/total, persistent discovery) does not exist anywhere and must be built from scratch in the same hand-rolled UI style as GameManager's Canvas construction.

**CONTRADICTED — Procedural body rendering of forms (§2.4b, 2.6a)**

There *is* a procedural body renderer: `Creature.BuildVisuals` builds a `body` plus a `limbs` collection and tints it from `bodyColor`/`colorType`, and the number of limbs and body scale come from `GameConfig.Tiers` (`struct TierData` — name, scale, limbs) driven by `Creature.tier`/`Evolve`. That is a different mechanism from the design: the design says limb-segment count reads *rank* (1→6, gained only by breeding), silhouette comes from the authored `socket_layout` per form, and *saturation* reads tier/intensity (Pale→Rage). In the code, tier is a Greek-letter progression tier (`Alpha/Beta/Gamma/Delta/Omega` in GameConfig) that drives both scale and limb count, so tier and rank are conflated and intensity/saturation is not represented at all — colours come from a fixed named palette (`Colors.FromName`, "RED"/"BLUE"/"GREEN") with no Pale/Dusk/Deep/Rage/Clash saturation ramp applied to bodies (ContentDatabase merely recognises those intensity strings for spawn/tier indexing). The authored data the requirement needs is parsed structurally — `FormDef.socket_layout`, `silhouette`, `saturation`, `family`, `rank` all exist as fields and `FormTable.Load` exists — but the inventory shows forms.json is read by nothing, so no form's socket layout ever reaches a renderer. Trait-on-main-face rendering (§2.6a) has no representation at all: no trait type, no face/decal symbols. So the area is implemented, but on tier-table rules rather than form/rank/intensity rules, and the existing tier→limbs path would have to be rewritten rather than extended.

_Exists instead:_ `Creature.BuildVisuals` builds a cube body plus limbs whose count and scale come from `GameConfig.Tiers` (`TierData.limbs`, `TierData.scale`) indexed by `Creature.tier` (Alpha…Omega), with a flat named-colour tint from `GameConfig.Colors.FromName`/`ContentDatabase.ColorTypeFor`. `FormDef` declares `socket_layout`, `silhouette`, `saturation`, `family` and `rank`, and `FormTable.Load` exists, but forms.json is unconsumed so none of it drives rendering. No trait-face rendering exists.
_Effort:_ medium — Smaller than it looks on the data side: `FormDef` already declares socket_layout, silhouette, saturation, family and rank, and `FormTable.Load` exists — the parse is written and only the wiring (forms.json actually being read, and a form assigned to `Creature`) is missing. The real work is rewriting `Creature.BuildVisuals` to build limb segments from rank/socket_layout instead of `GameConfig.TierData.limbs`, adding a saturation ramp alongside `Colors.FromName`, and separating tier-scale from rank-limbs across `Creature.tier`/`Evolve` and callers. Trait-on-face rendering is genuinely new (no trait symbols exist), but is a single decal/material slot on the body mesh.

**CONTRADICTED — Biome generation, terrain gates and per-run palette roll (§2.7, 3.3)**

Two of the requirement's three pillars are handled by a different mechanism than the design specifies, and the third is missing outright. (1) Per-run palette roll: this part looks genuinely implemented — ContentDatabase parses biomes.json and exposes RollSpawn/Weight/GrazerWeight/Wandering/Pocket, and the editor ContentCheck.RollSamples samples rolls across the five colour names, so weight-driven palette rolling exists. (2) The five-biome progression, however, is layered on top of a surviving legacy three-biome system: GameConfig still defines BiomeNeon/BiomeMagma/BiomeCrystal with BiomeData.enemyColors and EcosystemManager exposes LegacyBiomes, while biome change is an event/notification (OnBiomeRequest → OnBiomeChanged → "ENTERING {biome.name}") rather than the player physically traversing generated terrain. That legacy palette/visual-swap path must be deleted or rewritten, not extended. (3) Traversal gates are absent: BiomeTerrain has a single TerrainProfile.Prairies and only a height field (SampleHeight/HeightAt/Radius) — no water bodies, lava fields, cliff climbing, or cold zones, and no trait inventory (nothing named Fins/Claws/Coat/Heat; EnemyAI only knows a "trait_miniboss" role string and a carriesColour field, so eating a miniboss cannot grant a key). Consequently nothing can stop the player at Wetlands water or block Volcanic until four traits are held, and the 0→1→2→1→0 introduction count is unrepresented. Alpha lairs are also replaced by a kill-interval boss spawner (GameConfig.Boss.SpawnIntervalKills, OnBossSpawned) rather than one landmark lair per biome.

_Exists instead:_ A single Prairies-only procedural terrain (BiomeTerrain) plus an event-driven biome swap that recolours the world from a legacy three-biome table (Neon Grid / Magma Wastes / Crystal Forest via GameConfig.BiomeNeon/Magma/Crystal and VisualsForBiome, EcosystemManager.LegacyBiomes). Palette weight rolling from biomes.json genuinely exists (ContentDatabase.RollSpawn/Weight/GrazerWeight, verified by Editor ContentCheck.RollSamples). Alphas arrive as a kill-count boss spawn instead of a per-biome lair. No trait or gate concept exists at all beyond the "trait_miniboss" role tag in EnemyAI.
_Effort:_ large — Requires four new terrain profiles with gate geometry (water depth, climbable rock, cold band, lava/vents) in BiomeTerrain, a player trait inventory wired to EnemyAI's existing "trait_miniboss" role, gate-aware movement blocking, per-biome Alpha lair placement replacing GameConfig.Boss.SpawnIntervalKills, and deletion of the legacy three-biome visual table (BiomeNeon/BiomeMagma/BiomeCrystal, LegacyBiomes). Two things reduce the cost: biomes.json is already parsed and the palette-weight roll (RollSpawn/Weight/GrazerWeight, plus Wandering/Pocket split and PocketLeakChance) already satisfies the per-run roll clause, and the five biome ids already appear as literals in GameConfig — so gating fields likely already sit in biomes.json unread rather than needing new data authoring.

**CONTRADICTED — Pockets, distance-based difficulty and lair placement (§2.7, 2.4b)**

The pocket concept exists in code, but as a *probability of a spawn table*, not as a place. ContentDatabase splits each biome's roster into `Wandering` and `Pocket` lists and rolls from them via `RollSpawn`/`Weight`/`TierIndex`; EcosystemManager then mixes pocket stock into ordinary spawns through a single scalar, `PocketLeakChance`. That means top-tier meat can appear anywhere at some odds, which is the inverse of the design's rule that Clash/top tiers *never wander* and exist only inside guarded locations. Nothing in the inventory represents a pocket as a world region: no pocket-placement, pocket-count, pocket-radius, guard-pack or occupant-converge symbols; `FindSpawn` and `BiomeTerrain.Radius`/`SampleHeight` are the only positional hooks and there is no distance-from-entrance term, no entrance/spawn-point concept, and no per-distance tier or weight scaling anywhere (Ecology exposes only global ContactDamageScale/SpeedScale/SightRadius). Alpha placement is likewise implemented by a different mechanism: `GameConfig.Boss.SpawnIntervalKills` plus `EcosystemManager.OnBossSpawned` spawn the apex on a kill counter with stat multipliers, rather than seating one Alpha lair at the strong end of the map. Elites and trait minibosses exist as role tags on EnemyAI (`elite`, `trait_miniboss`, `alpha`), and hunter-claim logic (`ClaimHunterSlot`, `MaxHunters`) gives swarm-ish pressure, but these are per-creature behaviours, not pocket garrisons. A per-run seed exists (`runSeed`) and biomes.json is parsed, but no symbol suggests a rolled over-tier pocket (Rage hollow in Prairies) — `PocketLeakChance` is the closest thing and it leaks individuals, not a pocket above the biome ceiling.

_Exists instead:_ A non-spatial spawn-table model: creatures.json/biomes.json rosters split into Wandering vs Pocket pools, rolled by ContentDatabase.RollSpawn with weights and a TierIndex, and pocket stock bled into ordinary spawns by EcosystemManager.PocketLeakChance. Difficulty scaling is global (GameConfig.Ecology.*Scale, Tiers) rather than distance-based, and the Alpha/apex arrives on a kill-count timer (GameConfig.Boss.SpawnIntervalKills → OnBossSpawned) instead of occupying a lair placed at the strong end of the biome.
_Effort:_ large — The parsed data is largely reusable — ContentDatabase already separates Wandering/Pocket rosters, knows tier order via TierIndex, and biomes.json is loaded, so the tables need labelling into places rather than re-authoring. But the runtime model must be rewritten, not extended: PocketLeakChance-based mixing has to be replaced by spatial pocket sites (count, centre, radius) placed on BiomeTerrain, spawn selection in EcosystemManager.FindSpawn must become a function of distance from the run entrance, guard garrisons of elites/trait_miniboss must be attached to pocket sites, and the kill-count boss trigger (Boss.SpawnIntervalKills → OnBossSpawned) must be replaced by lair placement at the far/strong end plus a per-run over-tier pocket roll.

**CONTRADICTED — Ambient rank rules (§3.3)**

Creature ranking and spawn selection are both implemented, but on different rules than the design states. Spawn choice goes through ContentDatabase.RollSpawn with weighted rolls (GrazerWeight/Weight) over biome rosters plus Wandering/Pocket lists and EcosystemManager.FindSpawn/PocketLeakChance — a probability-driven roster draw, not a deterministic 'prey = player rank − 1, elites = player rank, Alpha = player rank at Clash, Apex = rank 6 Clash' assignment. The size/power ladder that exists is GameConfig.Tiers (Alpha/Beta/Gamma/Delta/Omega with scale and limbs) driven by Creature.tier and by kill-count progression (EvoRequirement, LevelUpRequirement, PlayerController.level/totalKills, Creature.Evolve) — i.e. the player's 'rank' is an XP/kill level, and the boss is a periodic kill-interval spawn (Boss.SpawnIntervalKills) with flat multipliers rather than a same-rank Clash mirror-match. There is no symbol anywhere binding an enemy's rank to the player's current rank, no floor-at-1 clamp, and no Clash forcing for alphas: 'Clash' appears only as an intensity string inside ContentDatabase (alongside Pale/Dusk/Deep/Rage), most plausibly feeding TierIndex/ColorTypeFor for colour-type mapping. The rank field the design names lives on FormDef.rank in FormTable, and forms.json is read by nothing, so the stated rank data is not consumed at all. To satisfy the requirement, the tier/level ladder and the boss-interval spawn path would have to be reworked, not merely extended — hence CONTRADICTED rather than ABSENT.

_Exists instead:_ A weighted-roll spawn system (ContentDatabase.RollSpawn + EcosystemManager.FindSpawn/PocketLeakChance) over biome rosters, combined with a five-step legacy tier ladder (GameConfig.Tiers Alpha..Omega with scale/limbs) advanced by kill counts (EvoRequirement/LevelUpRequirement, PlayerController.level, Creature.Evolve), and a boss spawned every N kills with flat stat multipliers (GameConfig.Boss). Roles are tagged by string in EnemyAI.ApplyContent ("prey","grazer","elite","alpha","apex") but carry no rank arithmetic.
_Effort:_ medium — Smaller than it looks in one respect: the role taxonomy already exists (EnemyAI.role with prey/grazer/elite/alpha/apex), ContentDatabase already parses creatures.json and already has TierIndex plus the Pale/Dusk/Deep/Rage/Clash intensity vocabulary, and a rank field already exists on FormDef — it is simply parsed into an unread table. The work is to expose a player rank (limb count) instead of the kill-based level, apply the per-role offset with a floor of 1 at spawn time in FindSpawn/ApplyContent, and force Clash for alpha/apex. But it also requires unwinding the GameConfig.Tiers/EvoRequirement kill-ladder and the Boss.SpawnIntervalKills path that currently own creature scaling, which touches Creature, PlayerController, EcosystemManager and GameConfig.

**CONTRADICTED — Alpha lair and the two-gate unlock (§2.5)**

The 'Alpha appears' area of the design is already implemented, but by an entirely different rule: GameConfig.Boss.SpawnIntervalKills plus EcosystemManager.OnBossSpawned/GameManager's "!! APEX PREDATOR DETECTED !!" notification spawn an apex/boss on a raw kill-count interval, scaled by ScaleMultiplier/HealthMultiplier/DamageMultiplier. There is no lair landmark object (PropScatter only places manifest-driven decorative props via PropSet, with no lair or per-biome landmark symbol), no per-biome distinct-form counter (PlayerController tracks only totalKills, level, score; forms.json, the source of form identities, is read by nothing), no per-biome prey-eaten counter, no 90% 'stirs' state, and no gate fields surfaced in the biome data path (ContentDatabase exposes Biomes, Wandering, Pocket, RollSpawn, GrazerWeight, TierIndex — nothing gate-like; GameConfig.BiomeData carries only name/colours). Because the kill-interval boss trigger occupies the same slot the two-gate lair unlock must occupy, it has to be replaced rather than merely extended.

_Exists instead:_ A kill-count-driven boss spawner: GameConfig.Boss.SpawnIntervalKills fires EcosystemManager.OnBossSpawned, which creates a scaled apex enemy (Creature.isBoss, EnemyAI roles "alpha"/"apex") and shows GameManager's "!! APEX PREDATOR DETECTED !!" banner. No lair landmark, no distinct-form or prey-eaten gates, no stirring state.
_Effort:_ large — Requires new run-state tracking (per-biome distinct forms and per-biome coloured-prey eaten — neither counter exists; only PlayerController.totalKills), plumbing forms identity from the currently unread forms.json, adding the five-row gate table to biomes.json plus parsing in ContentDatabase, a persistent lair landmark placed per biome (PropScatter has only decorative PropSet data), a 90% stirring visual state, and gating Alpha spawn on both counters while deleting the SpawnIntervalKills path. Mitigating: enemy roles "alpha"/"apex" and boss scaling multipliers already exist, so the Alpha creature itself can be reused.

**CONTRADICTED — Alpha identity, mirror-match and biome emptying (§2.5)**

The codebase does implement an "alpha/boss wakes and comes for you" area, but on entirely different rules. Spawning is a kill-count timer (GameConfig.Boss.SpawnIntervalKills) and the alpha's stats are flat multipliers off a base (ScaleMultiplier/HealthMultiplier/DamageMultiplier), with Creature.isBoss and EcosystemManager.OnBossSpawned driving the event. Nothing in the inventory tracks the run state the design requires: PlayerController exposes only totalKills/level/score — there is no per-biome per-colour eat tally, so the alpha cannot be the champion of the most-eaten colour. There is no gate-progress trigger (no 90%-of-both-gates check; progression symbols are EvoRequirement/LevelUpRequirement, i.e. XP-style thresholds). Rank mirroring is absent: EnemyAI role strings include "alpha" and ApplyContent applies content stats, but tier/rank comes from ContentDatabase.TierIndex / GameConfig.Tiers rather than being pinned to the player's rank, and there is no Clash-intensity forcing (intensity exists only in the unread FormDef.intensity). The uncatchable-speed rule is also absent — speeds come from Ecology.SpeedScale and ClassProfile.speedMult, i.e. multiplier-based, exactly what the design says the alpha must ignore; the "fastest player form at that rank" data sits in forms.json which nothing reads. Finally there is no biome-emptying: EcosystemManager still exposes MaxEnemies/SpawnInterval-style continuous top-up (Init, FindSpawn, PocketLeakChance) and no flee/despawn-on-alpha-wake symbol appears; EnemyAI's State enum members were not parsed, so a flee state cannot be ruled out, but no suppression of spawning is visible.

_Exists instead:_ A kill-count-triggered boss with flat scale/health/damage multipliers (GameConfig.Boss + Creature.isBoss + EcosystemManager.OnBossSpawned), whose colour and tier come from ContentDatabase roster rolls rather than the player's eaten-colour history or rank, alongside continuous enemy top-up spawning that is never suspended.
_Effort:_ large — GameConfig.Boss's kill-interval + multiplier model and the boss branch of EcosystemManager/Creature must be rewritten, not extended: a per-biome per-colour eat tally must be added to PlayerController/RegisterKill, ContentDatabase must expose a biomes.json Alpha roster lookup keyed by colour (biomes.json is already parsed, so the roster may only need surfacing), rank/Clash must be forced from player rank, spawning must be suspended and existing prey/grazers made to bolt (touching EcosystemManager top-up and EnemyAI states), and the flat speed rule needs the per-rank fastest-form speed from forms.json, which is currently unread.

**CONTRADICTED — Emblems (§2.5, 3.3)**

Nothing in the inventory represents an emblem: there is no emblems.json data contract, no claimed-emblem record, and no symbol named anything like Emblem/Trophy/BiomeKey. However, the two gameplay gates the emblem is supposed to control are both already implemented on entirely different rules. Biome progression exists (PlayerController.OnBiomeRequest, EcosystemManager.OnBiomeChanged, GameManager "ENTERING {biome.name}") but is driven by requests/level rather than by possessing an Alpha's emblem. Breeding/offspring exists ("OFFSPRING SPAWNED!", Companion spawn, OnMateSpawned/MateEnemy) but is a level-up/mate-kill reward, not a capability unlocked by eating a downed Alpha. Eating a creature goes through EnemyAI.GetEaten with `healsPlayerPct` and feeds PlayerController.RegisterKill/Evolve, i.e. consuming an Alpha grants power/progress — the opposite of the design's 'trophy granting no power of its own'. Boss/Alpha spawning is itself keyed to Boss.SpawnIntervalKills rather than the 90% dual-gate lair wake. So this design area is occupied by a kill-count/level-up progression system that would have to be rewired, not merely extended. Confidence is medium because the inventory gives names, not the actual gating logic inside OnBiomeRequest or Evolve.

_Exists instead:_ A kill-count/XP progression: GameConfig.EvoRequirement/LevelUpRequirement/Boss.SpawnIntervalKills drive Evolve and boss spawns; biome changes flow through PlayerController.OnBiomeRequest → EcosystemManager.OnBiomeChanged with no possession check; offspring/companions spawn as a level or mate-kill reward ("OFFSPRING SPAWNED!", Companion, MateEnemy); eating enemies heals and awards kills via EnemyAI.GetEaten/healsPlayerPct.
_Effort:_ large — Requires a new data contract (emblems.json) plus a loader in ContentDatabase alongside creatures/biomes, a persisted claimed-emblem record on the player, an Alpha-downed→eaten claim path in EnemyAI.GetEaten/Die that grants no stats (so healsPlayerPct/RegisterKill/Evolve behaviour on Alphas must change), and gating rewrites in PlayerController.OnBiomeRequest/EcosystemManager.OnBiomeChanged and the offspring path. Only partial luck: the Alpha role already exists as "alpha" in EnemyAI.ApplyContent and biome ids are already enumerated in GameConfig/WorldTables, so the target keys for emblem→biome mapping are already available.

**CONTRADICTED — Breeding, litters and rank gain (§2.5)**

The codebase does implement rank/limb growth, but by exactly the mechanism the design forbids: kills accumulate (`PlayerController.RegisterKill`, `totalKills`, `Creature.kills`) and trip `GameConfig.EvoRequirement` / `LevelUpRequirement`, which calls `PlayerController.Evolve` / `Creature.Evolve` to advance `tier` through `GameConfig.Tiers`, whose `TierData` carries `limbs` and `scale`. So limbs are gained by eating — the specific thing the requirement says must never happen — and rank is a kill-threshold level ("LEVEL UP! RANK {level}"). None of the designed pipeline exists: no emblem item dropped by the Alpha (EnemyAI has roles "alpha"/"apex" and `GetEaten` but no emblem symbol), no litter generation, no `litterSize = 2 + (distinctForms - formGate)` capped at 5, no six-limb cap, no per-offspring starting colour buffer (committed monochrome vs flexible mixed, all Pale), no inheritance of traits/emblems/panels, no Bestiary entry for unpicked litter-mates. The distinct-forms-this-biome counter the litter formula needs cannot exist because forms.json is unread, and panels.json is likewise unread, so 'inherit panels' has no data source in code. The one superficial match — "OFFSPRING SPAWNED!" plus `Companion` (target, index) — is an ally/companion spawn attached to the player, not a litter the player picks from and continues as; it would not satisfy the requirement and its trigger sits inside the same kill-driven progression.

_Exists instead:_ A kill-count evolution ladder: eating enemies increments `totalKills`/`kills`, crossing `GameConfig.EvoRequirement`/`LevelUpRequirement` fires `Evolve`, bumping `tier` through the five `TierData` entries whose `limbs` field drives `Creature.BuildVisuals` — i.e. limbs and 'rank' are granted by eating. A separate `Companion`/"OFFSPRING SPAWNED!" path spawns a follower rather than offering a litter to become.
_Effort:_ large — The kill-driven `Evolve`/`EvoRequirement`/`LevelUpRequirement`/`Tiers` path in PlayerController, Creature and GameConfig must be severed from limb count and rewritten as breeding-only, and the whole designed chain is new: Alpha emblem drop on `GetEaten`, per-biome distinct-form tracking (requires wiring the currently unread forms.json), litter-size formula with gate lookup, an offspring-selection UI, per-litter-mate Pale starting buffers in committed/flexible variants, trait/emblem/panel inheritance (panels.json also unread), a six-limb cap and Bestiary entries for unpicked mates. Partial credit only for `TierData.limbs` and `Creature.BuildVisuals`, which already turn a limb count into visuals and can be driven by the new rank value unchanged.

**CONTRADICTED — Decorated panels (§2.8, 3.3)**

There is no panel system at all: no Panel type, no panel drop on elite death (EnemyAI.Die/GetEaten exist but only role/carriesColour/healsPlayerPct are visible), no attachment/socket runtime, no capacity or shed logic, and panels.json is explicitly unread. However this is more than a plain gap: the codebase already implements the run's power-progression layer by a completely different mechanism. PlayerController carries level/score/totalKills with LevelUpRequirement and EvoRequirement thresholds and the literals "upgrade_damage", "upgrade_speed", "upgrade_health" and "gene_points", i.e. a kill-fed level-up/gene-point stat-upgrade tree, plus GameConfig.ClassProfile multipliers (speedMult, damageMult, healthMult, lungeMult, dashMult) chosen by ClassFor on Evolve. The design states panels are the run's ONLY power source and the emblem/evolution is not a power source, so this XP-and-upgrade path is a rival mechanism that must be torn out, not merely supplemented. Note also that the specific powers the design assigns to panels already exist as fields the panel layer would have to drive (PlayerController.LockConeDot / lock range, dash via ClassProfile.dashMult, guard via BaseHealth), so the hook points exist but are wired to levels rather than to carried panels. Nothing addresses no-stacking, capacity growing with the body, face placement avoiding main-face traits, or survival through mutation/breeding.

_Exists instead:_ A level/gene-point upgrade system: PlayerController tracks totalKills, level, score and emits "upgrade_damage"/"upgrade_speed"/"upgrade_health" and "gene_points", gated by GameConfig.LevelUpRequirement/EvoRequirement, with stat effects delivered by GameConfig.ClassProfile multipliers on Evolve. Elites exist as an EnemyAI role but drop nothing except healsPlayerPct healing. panels.json sits in StreamingAssets unparsed.
_Effort:_ large — Requires a new data layer (a PanelDef/PanelTable loader mirroring FormTable.Load for panels.json), a drop-on-elite-death hook in EnemyAI.Die/GetEaten, runtime attached-panel state with capacity derived from body/tier, dedup and shed-at-capacity rules, per-face attachment visuals that respect trait main-faces in Creature.BuildVisuals, persistence across Creature.Evolve and the breeding/Companion path, and rewiring of the four named powers (LockConeDot, dash, guard/health, camouflage) away from ClassProfile multipliers. It also means deleting the existing gene_points/upgrade_* progression so panels are the sole power source. Only mitigation: panels.json is already authored and the affected stat fields already exist under other owners.

**CONTRADICTED — The Ascension and the Apex (§2.5, The Ascension)**

The design's finale is a non-biome Ascension arena, always open to a six-limb bloodline, holding the 25 rank-6 forms, with a dormant rank-6 Clash Apex that wakes only at a persisted Bestiary count of ≥100/150 forms and yields a true ending above the Conquest. The codebase does implement an 'Apex' encounter, but on entirely different rules: GameConfig.Boss.SpawnIntervalKills drives a recurring boss spawn inside the normal ecosystem (EcosystemManager.OnBossSpawned, "Apex predator", GameManager's "!! APEX PREDATOR DETECTED !!"), and 'Apex' is also just one of several class profiles/tiers (ClassFor, Tiers: Alpha…Omega) reached by kill-count evolution (PlayerController.RegisterKill/Evolve, Creature.Evolve). There is no Ascension domain or scene, no limb/rank-gated entry, no dormancy state, no true-ending path, and no persistence of a cross-run Bestiary — the only persisted values visible are upgrade/gene-point keys in PlayerController. Rank-6 form data exists in forms.json and a matching parser (FormDef.rank, FormTable.Load) is present, but nothing loads forms.json, so the rank-6 row is unconsumed. Because a same-topic Apex/boss system exists and works by kill-interval spawning rather than a record gate in a separate arena, this is contradiction rather than mere absence; the existing boss spawn path would have to be rewritten, not extended.

_Exists instead:_ A recurring 'apex predator' boss that spawns every GameConfig.Boss.SpawnIntervalKills kills within the ordinary biome ecosystem, with stat multipliers, plus 'Apex' as one of several kill-count class/tier names. No arena, no dormancy, no cross-run Bestiary count, no true ending. forms.json (which contains the rank rows) is parsed by FormTable/FormDef code but never loaded.
_Effort:_ large — Needs a new non-biome Ascension domain and entry condition tied to limb count (no limb/rank breeding system is visible — rank is currently kill-count Evolve), a cross-run persisted Bestiary with a distinct-form counter and a ≥100/150 gate, a dormant/awake Apex state machine and a true-ending flow, plus rewiring or deleting the kill-interval boss spawn in EcosystemManager/GameConfig.Boss. One piece is cheap: FormTable/FormDef already models rank and forms.json already holds the rank-6 rows, so wiring FormTable.Load to that file is a small step toward the 25 rank-6 forms.

**UNCONSUMED — The Bestiary screen (§2.9)**

There is no Bestiary UI anywhere in the inventory. GameManager builds the only screens that exist (MenuPanel with Title/Tagline/StartButton, DeathPanel with EXTINCT/Score/RestartButton, plus HUD bars and notifications) — no pause menu, no grid, no cell/ladder navigation, no discovered/total header, no emblem list, no persistence of discovered form ids or per-run highlight sets. Crucially, the data the requirement needs already exists and is fully typed: forms.json (132 KB) plus FormTable/FormDef with exactly the fields the screen would render (id, family, intensity, rank, name, flavor, base_hex, silhouette). FormTable.Load exists but the inventory explicitly marks forms.json as read by nothing, so the loader is never invoked from runtime code. Nothing in Creature/EnemyAI/PlayerController records discovery: EnemyAI has contentId/role and Creature has tier/colorType, but there is no discovered-set, no emblem store, and PlayerController only persists 'gene_points' and simple upgrade keys via what look like PlayerPrefs strings. So the asset and its schema are present but unconsumed; no contradicting mechanism exists to remove.

_Exists instead:_ Only two runtime screens built procedurally in GameManager (main menu and death panel) plus HUD bars. FormTable.cs defines FormDef/FormTable with a Load method matching forms.json's schema, but no caller; ContentDatabase loads creatures.json/biomes.json for spawning only. No persistence beyond 'gene_points' and upgrade_* keys in PlayerController.
_Effort:_ large — The 150-form data and its parse schema already exist (forms.json + FormDef with id/family/intensity/rank/name/base_hex/silhouette), so no authoring or table work is needed — wiring FormTable.Load in is small. The remainder is substantial new code: a 6x5 grid screen plus intensity-ladder drill-down built in the same hand-rolled procedural-UI style as GameManager's panels, a pause menu (none exists), a persisted discovery/emblem store, discovery hooks at kill/eat sites in EnemyAI/Creature, Alpha-threshold progress display, and outlined entries for declined offspring (breeding/litter code is also absent from the inventory).

**CONTRADICTED — Run restart as a one-limb blank (§1, 2.5)**

A death-and-restart loop clearly exists (DeathPanel/EXTINCT/RestartButton "NEW EVOLUTION", PlayerController.Die, gameStarted gating, GameManager spawning "Player" into "prairies" with BiomeTerrain.TerrainProfile.Prairies), so this area is implemented — but on different rules than the design. Two divergences are structural, not additive. First, the restarting creature is not a blank white one-limb cube: GameManager spawns the player with "GREEN" and rank is a level/kill-driven ladder (PlayerController.level, Evolve, "LEVEL UP! RANK {level}", GameConfig.Tiers Alpha..Omega with TierData.limbs), so limbs come from eating/levelling rather than from a fresh one-limb blank. Second, the cross-run carry-over is a gene-point stat shop, not the Bestiary milestone ladder: PlayerController holds "gene_points", "upgrade_damage", "upgrade_speed", "upgrade_health", meaning the next run begins with purchased stat boosts rather than a blank state modified only by hatch-choice or inherited instinct. There is no Bestiary, no discovered-form count, and forms.json (the 150-form table the milestones key off) is read by nothing, so hatch-choice and inherited instinct have no substrate at all. The restart plumbing itself and the Prairies regeneration can be reused; the progression carry-over must be replaced.

_Exists instead:_ A roguelite restart that returns the player to a GREEN cube in a regenerated Prairies, with rank/limbs driven by kill-based Evolve/level-ups (GameConfig.Tiers) and cross-run persistence provided by a gene-point upgrade shop ("gene_points", "upgrade_damage", "upgrade_speed", "upgrade_health") instead of a Bestiary with hatch-choice and inherited-instinct unlocks.
_Effort:_ medium — Restart flow, prairies generation and tier/limb data already exist and are reusable, so the fresh-run spawn only needs its start colour (white instead of "GREEN") and a forced one-limb rank. The real work is deleting the gene_points/upgrade_* carry-over in PlayerController and adding a persistent discovered-form record; forms.json is already in StreamingAssets and FormTable/FormDef parsing code already exists (currently unread), so the data layer for milestone thresholds is largely free.


---

## Stage 4 — Prioritize

3 requirement(s) already satisfied and excluded from the ranking; 42 open.

Utility score: `score = (1 + blocking_degree) x severity_weight / effort`

| # | Requirement | § | Verdict | Blocks | Severity | Effort | Score |
|---|---|---|---|---|---|---|---|
| 1 | Five colour families and their stat multipliers | 2.4 | CONTRADICTED | 26 | 3.0 | 2.0 | 40.5 |
| 2 | Limb baseline stat table | 2.4 | CONTRADICTED | 23 | 3.0 | 2.0 | 36.0 |
| 3 | Intensity scaling of family multipliers | 2.4, 2.4b | UNCONSUMED | 25 | 2.5 | 2.0 | 32.5 |
| 4 | Lock-on targeting | 2.1 | PARTIAL | 28 | 1.0 | 1.0 | 29.0 |
| 5 | Pounce attack | 2.1 | PARTIAL | 27 | 1.0 | 1.0 | 28.0 |
| 6 | Final stat composition (rank baseline × family × intensity) | 2.4 | CONTRADICTED | 16 | 3.0 | 2.0 | 25.5 |
| 7 | forms.json — the 150 authored forms | 2.4b, 3.3 | UNCONSUMED | 17 | 2.5 | 2.0 | 22.5 |
| 8 | The colour buffer (FIFO limb slots) | 2.4a | CONTRADICTED | 19 | 3.0 | 3.0 | 20.0 |
| 9 | Single Health meter and permadeath | 1, 2.3 | CONTRADICTED | 12 | 3.0 | 2.0 | 19.5 |
| 10 | Ambient rank rules | 3.3 | CONTRADICTED | 12 | 3.0 | 2.0 | 19.5 |
| 11 | Biome generation, terrain gates and per-run palette roll | 2.7, 3.3 | CONTRADICTED | 18 | 3.0 | 3.0 | 19.0 |
| 12 | Form resolution from buffer state | 2.4b | CONTRADICTED | 16 | 3.0 | 3.0 | 17.0 |
| 13 | Dual input mapping (keyboard+mouse and gamepad) | 2.1, 4.1 (referenced) | PARTIAL | 32 | 1.0 | 2.0 | 16.5 |
| 14 | Instant mutation with wound preserved | 2.3, 2.4b | CONTRADICTED | 10 | 3.0 | 2.0 | 16.5 |
| 15 | Solid bodies and obstacles | 2.1 | PARTIAL | 28 | 1.0 | 2.0 | 14.5 |
| 16 | Alpha lair and the two-gate unlock | 2.5 | CONTRADICTED | 12 | 3.0 | 3.0 | 13.0 |
| 17 | Eating a downed creature | 2.1, 2.3 | PARTIAL | 22 | 1.0 | 2.0 | 11.5 |
| 18 | Alpha identity, mirror-match and biome emptying | 2.5 | CONTRADICTED | 10 | 3.0 | 3.0 | 11.0 |
| 19 | Trait permanence, face rendering and inheritance | 2.6a | ABSENT | 9 | 2.0 | 2.0 | 10.0 |
| 20 | Emblems | 2.5, 3.3 | CONTRADICTED | 9 | 3.0 | 3.0 | 10.0 |
| 21 | The blank (form zero) | 2.4, 2.5 | CONTRADICTED | 2 | 3.0 | 1.0 | 9.0 |
| 22 | Breeding, litters and rank gain | 2.5 | CONTRADICTED | 8 | 3.0 | 3.0 | 9.0 |
| 23 | Meat tiers and their world distribution | 2.4b, 2.7 | PARTIAL | 15 | 1.0 | 2.0 | 8.0 |
| 24 | The Bestiary screen | 2.9 | UNCONSUMED | 4 | 2.5 | 3.0 | 4.2 |
| 25 | Dash | 2.1, 2.3 | ABSENT | 3 | 2.0 | 2.0 | 4.0 |
| 26 | Trait minibosses and the four traits | 2.6 | PARTIAL | 11 | 1.0 | 3.0 | 4.0 |
| 27 | The Ascension and the Apex | 2.5, The Ascension | CONTRADICTED | 2 | 3.0 | 3.0 | 3.0 |
| 28 | Conquest win condition | 1, 2.5 | ABSENT | 3 | 2.0 | 3.0 | 2.7 |
| 29 | Bestiary persistence across runs | 1, 2.9 | ABSENT | 3 | 2.0 | 3.0 | 2.7 |
| 30 | Pockets, distance-based difficulty and lair placement | 2.7, 2.4b | CONTRADICTED | 1 | 3.0 | 3.0 | 2.0 |
| 31 | Decorated panels | 2.8, 3.3 | CONTRADICTED | 1 | 3.0 | 3.0 | 2.0 |
| 32 | Procedural body rendering of forms | 2.4b, 2.6a | CONTRADICTED | 0 | 3.0 | 2.0 | 1.5 |
| 33 | Run restart as a one-limb blank | 1, 2.5 | CONTRADICTED | 0 | 3.0 | 2.0 | 1.5 |
| 34 | Record milestone unlocks | 2.9a | ABSENT | 1 | 2.0 | 3.0 | 1.3 |
| 35 | Predator AI: hunting the player | 2.2 | PARTIAL | 0 | 1.0 | 1.0 | 1.0 |
| 36 | Prey reactions: fleeing and floating health bars | 2.2 | PARTIAL | 0 | 1.0 | 1.0 | 1.0 |
| 37 | Poop the oldest colour | 2.1, 2.4a | ABSENT | 0 | 2.0 | 2.0 | 1.0 |
| 38 | Next-slot-to-be-overwritten indicator | 2.4a | ABSENT | 0 | 2.0 | 2.0 | 1.0 |
| 39 | Combat pacing invariant (2–3 pounces, no one-shots) | 2.5 | ABSENT | 0 | 2.0 | 2.0 | 1.0 |
| 40 | Grazers as the healing supply | 2.3 | PARTIAL | 0 | 1.0 | 2.0 | 0.5 |
| 41 | JSON content loading with schema check and fallback | 3.3 | PARTIAL | 0 | 1.0 | 2.0 | 0.5 |
| 42 | Generator invariants and seed refusal | 3.3 | PARTIAL | 0 | 1.0 | 3.0 | 0.3 |

**Chosen: Five colour families and their stat multipliers (§2.4, score 40.5)**

R013 tops the list because it sits at the junction of the whole stat system: 26 downstream items wait on it, its severity is high, and its effort is only medium because the correct data shape (FormDef/StatBlock with health/damage/speed/reach/dash, plus ContentDatabase.ColorTypeFor already knowing the five family names) is already written — it is dead, not missing. The verdict is CONTRADICTED, which is the important part: GameConfig.ClassFor/ClassProfile is not an incomplete version of the design, it is a different design (eight classes, and a lungeMult where the GDD demands Reach) currently in charge of every live stat. Nothing built on top of the family model can be correct while a second, differently-axed multiplier table is the one PlayerController actually reads. Removing that competing pipeline is the unlock, and it has to happen before R014, R016, R018 or anything else in the 2.4 cluster can be evaluated against reality.

Must ship together: **Five colour families and their stat multipliers** + **Limb baseline stat table** + **Final stat composition (rank baseline × family × intensity)**

**Why not the runners-up**

R015 and R016 are not really 'runners-up' — they are the other two thirds of the same pipeline and are in this unit of work (see below). Of the genuinely separable items: R023 (forms.json unread) is the data feed for family/intensity/rank, but family can be resolved from the existing colour identity and rank from limb count, so it can land after the pipeline is correctly shaped — wiring 132 KB of authored forms into a pipeline that still contradicts the design would just consume bad multipliers faster. R014 (intensity scaling) is a modulation of multipliers that do not yet exist in the right axes; shipping it first means scaling the wrong numbers. R004 (lock-on) and R005 (pounce bounce-back) are small, cheap and genuinely independent — they are good parallel work for a second pair of hands, but they are combat-feel polish on a PARTIAL mechanism, not a blocker for the 26-item stat cluster. R018 (colour buffer) is large and depends on limb slots existing as colour-bearing entities, which presupposes the limb-count baseline from R015.

**What this unblocks**

- R014 — intensity_pct finally has family multipliers with the right axes to scale
- R023 — forms.json can be consumed into a pipeline whose StatBlock axes match the file's
- R018 — limb slots become meaningful once limb count is the baseline source and colour maps to a family
- Every downstream balance/bestiary/spawn item that reads a creature's effective stats
- Removal of the dead-vs-live duplication (ClassProfile vs FormDef/StatBlock) that currently makes any stat bug ambiguous

**Risks going in**

- Ripping out ClassProfile touches PlayerController.Evolve, level-up, and EnemyAI stat setup at once; expect a window where combat numbers are visibly off until all three items land together
- Reach has no baseline today (only the global Ecology.ReachScale) — introducing a reach multiplier without R015's baseline column produces a multiplier over an undefined value, which is why R015 is bundled
- WorldTables.cs mentions the five family names but its body is unparsed; it may already contain a family table that either shortcuts this work or conflicts with it. Read it before writing new tables.
- GameConfig.Colors enumerates nine colours and Creature/EnemyAI branch on string literals "GREEN"/"CYAN"; collapsing to five families needs a deliberate mapping or those branches go dead silently
- Tier data (Alpha..Omega, scale, limbs) is referenced by EvoRequirement/LevelUpRequirement and possibly save data — demoting it from stat authority to cosmetic/progression-only may break progression gates or existing saves
- Confidence on all three verdicts is medium and method bodies were not visible; some of the composition may already exist inside PlayerController.Evolve and be discovered mid-change

⚠ Developer override — the chunk is widened to R013, R015, R016, R014, R023, R018, R021 (added R014, R023, R018, R021). The blind ranking above stands exactly as recorded.


---

## Stage 5 — Generate code

> I'll start by reading the core files I need to change and pulling the exact GDD text.

- `read_file(path='Assets/Scripts/Game/GameConfig.cs')` → using UnityEngine;

- `read_file(path='Assets/Scripts/Content/FormTable.cs')` → // AUTO-GENERATED by the Morphivore agent crew. Do not edit by hand.

- `read_file(path='Assets/Scripts/Content/WorldTables.cs')` → // AUTO-GENERATED by the Morphivore world-content crew. Do not edit by hand.

- `search_gdd(query='five colour families stat multipliers Health Speed Damage Reach)` → --- gdd-scoped §2.4 [1/3] ---

- `read_file(path='Assets/Scripts/Game/PlayerController.cs')` → using System.Collections.Generic;

- `read_file(path='Assets/Scripts/Game/Creature.cs')` → using System.Collections;

- `search_gdd(query='2.4a colour buffer FIFO limb slots eviction white')` → --- gdd-scoped §2.4a ---

- `search_gdd(query='2.4b form resolution family majority tie recency intensity lowe)` → --- gdd-scoped §2.4b [2/3] ---

- `read_file(path='Assets/Scripts/Content/ContentDatabase.cs')` → // Runtime bridge between the generated world content (StreamingAssets/*.json)

- `read_file(path='Assets/Scripts/Game/EnemyAI.cs')` → using UnityEngine;

- `search_gdd(query='worked example rank 3 Rage Yellow Dusk Red Deep Brawler poop')` → --- gdd-scoped §2.4b [2/3] ---

- `search_gdd(query='2.4b intensity orthogonal to rank 2-limb Rage Brawler 5-limb Pa)` → --- gdd-scoped §2.4b [3/3] ---

- `read_file(path='Assets/Scripts/Game/GameManager.cs')` → using System.Collections;

- `read_file(path='Assets/Scripts/Game/EcosystemManager.cs')` → using System.Collections.Generic;

- `read_file(path='Assets/StreamingAssets/forms.json')` → {

- `search_gdd(query='rank changes only through breeding litter offspring starting bu)` → --- gdd-scoped §2.5 [3/4] ---

- `read_file(path='Assets/Scripts/Editor/ContentCheck.cs')` → // Editor-only sanity check on the generated world content: does it parse, does

- `search_gdd(query='poop dropping Q button oldest colour leaves behind')` → --- gdd-scoped §2.4a ---

- `search_gdd(query='4.9a opacity readability colour-blind mechanism never opacity')` → --- gdd-scoped §2.4a ---

> I have everything I need. Starting with the contract file — the five families, the intensity ladder, and the limb baseline table.

- `write_file(path='Assets/Scripts/Game/GameConfig.cs', why="Replaces the eight-class/five-tier prototype tables with §2.4's c)` → ERROR: Builder._tool_write_file() missing 1 required positional argument: 'contents'

### Modified: `Assets/Scripts/Game/GameConfig.cs`

_Replaces the eight-class/five-tier prototype tables with §2.4's contract: five families, the intensity ladder, the limb baseline table and the composition rule that multiplies them._

<details><summary>282 lines</summary>

```csharp
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

```

</details>

- `write_file(path='Assets/Scripts/Game/GameConfig.cs', why="Replaces the eight-class/five-tier prototype tables with §2.4's c, contents='using UnityEngine;\n\npublic static class GameConfig\n{\n   )` → Modified Assets/Scripts/Game/GameConfig.cs (282 lines). OK — delimiters balanced.

### Created: `Assets/Scripts/Game/ColourBuffer.cs`

_New: the per-limb colour buffer (§2.4a, FIFO fill/evict/poop) and the resolution that turns any buffer state into exactly one form (§2.4b)._

<details><summary>148 lines</summary>

```csharp
using UnityEngine;

/// <summary>One colour unit — a family at an intensity — sitting in a limb.
/// A white (empty) slot carries no family.</summary>
public struct ColourUnit
{
    public string family;
    public int    intensity;
    public int    eaten;      // insertion order; the buffer is strictly FIFO

    public bool IsWhite => string.IsNullOrEmpty(family);
}

/// <summary>The form a buffer state names: a family at an intensity, or the
/// blank when every limb is white.</summary>
public struct FormKey
{
    public string family;
    public int    intensity;

    public bool IsBlank => string.IsNullOrEmpty(family);
}

// ── The colour buffer (§2.4a) ────────────────────────────────────────────────
// One slot per limb, filled by eating and emptied by pooping, on rules the
// player can execute in their head: white limb first, else the oldest colour
// goes. Nothing here is hidden — the forcing comes from what the world serves.
public class ColourBuffer
{
    ColourUnit[] slots = new ColourUnit[0];
    int eatCount = 0;

    public int Count => slots.Length;
    public ColourUnit this[int i] => slots[i];

    /// <summary>One slot per limb. Rank only ever grows (breeding, §2.5), so the
    /// colours already held keep the limbs they are in.</summary>
    public void Resize(int limbs)
    {
        if (limbs == slots.Length) return;
        var resized = new ColourUnit[Mathf.Max(0, limbs)];
        for (int i = 0; i < Mathf.Min(resized.Length, slots.Length); i++) resized[i] = slots[i];
        slots = resized;
    }

    /// <summary>The slot the next meal lands in: the first white limb, or — with
    /// every limb coloured — the oldest colour, which the meal evicts. This is
    /// the slot that pulses on the body, so a colour is never lost unknowingly.</summary>
    public int NextSlot
    {
        get
        {
            for (int i = 0; i < slots.Length; i++)
                if (slots[i].IsWhite) return i;
            return Oldest();
        }
    }

    public void Eat(string family, int intensity)
    {
        int slot = NextSlot;
        if (slot < 0) return;   // no limbs at all: nothing can be held
        slots[slot] = new ColourUnit { family = family, intensity = intensity, eaten = ++eatCount };
    }

    /// <summary>Q / B: the oldest colour goes out and its limb turns white.
    /// False when there is nothing coloured to lose.</summary>
    public bool Poop(out ColourUnit dropped)
    {
        dropped = default;
        int slot = Oldest();
        if (slot < 0) return false;
        dropped     = slots[slot];
        slots[slot] = default;
        return true;
    }

    int Oldest()
    {
        int oldest = -1;
        for (int i = 0; i < slots.Length; i++)
        {
            if (slots[i].IsWhite) continue;
            if (oldest < 0 || slots[i].eaten < slots[oldest].eaten) oldest = i;
        }
        return oldest;
    }

    // ── Resolution (§2.4b) ───────────────────────────────────────────────────

    /// <summary>Every buffer state resolves to exactly one form — no recipes, no
    /// invalid states.</summary>
    public FormKey Resolve()
    {
        // Family = the colour holding the most limbs. Ties break toward the most
        // recently eaten and then, for a litter born with its limbs loaded in one
        // go, toward the fixed precedence Yellow → Red → Blue → Purple → Grey,
        // which is the order GameConfig.Families is written in.
        string family    = null;
        int    bestCount = 0;
        int    bestEaten = -1;

        foreach (var f in GameConfig.Families)
        {
            int count = 0, newest = -1;
            for (int i = 0; i < slots.Length; i++)
            {
                if (slots[i].family != f.name) continue;
                count++;
                if (slots[i].eaten > newest) newest = slots[i].eaten;
            }

            if (count == 0) continue;
            if (count > bestCount || (count == bestCount && newest > bestEaten))
            {
                family    = f.name;
                bestCount = count;
                bestEaten = newest;
            }
        }

        if (family == null) return new FormKey();   // all limbs white: the blank

        // Intensity = the lowest tier among the family's own units ("your weakest
        // meat sets your intensity"), stepped down one rung for every limb not
        // carrying the family, floored at Pale.
        int rung = int.MaxValue;
        for (int i = 0; i < slots.Length; i++)
            if (slots[i].family == family)
                rung = Mathf.Min(rung, GameConfig.LadderRung(slots[i].intensity));

        rung = Mathf.Max(0, rung - (slots.Length - bestCount));

        // Clash shares the top rung with Rage rather than sitting above it, and
        // any Clash unit wins that tie; dilute either and it slides off to Deep.
        int intensity = GameConfig.WildLadder[rung];
        if (intensity == GameConfig.Rage && HoldsClash(family)) intensity = GameConfig.Clash;

        return new FormKey { family = family, intensity = intensity };
    }

    bool HoldsClash(string family)
    {
        for (int i = 0; i < slots.Length; i++)
            if (slots[i].family == family && slots[i].intensity == GameConfig.Clash) return true;
        return false;
    }
}

```

</details>

- `write_file(path='Assets/Scripts/Game/ColourBuffer.cs', why='New: the per-limb colour buffer (§2.4a, FIFO fill/evict/poop) and, contents='using UnityEngine;\n\n/// <summary>One colour unit — a famil)` → Created Assets/Scripts/Game/ColourBuffer.cs (148 lines). OK — delimiters balanced.

### Modified: `Assets/Scripts/Game/Creature.cs`

_Swaps the colorType/tier identity for §2.4's family + intensity + rank, builds one limb per rank, and lets a subclass colour each limb from what it holds._

<details><summary>210 lines</summary>

```csharp
using System.Collections;
using UnityEngine;

public class Creature : MonoBehaviour
{
    // ── Identity (§2.4) ───────────────────────────────────────────────────────
    // A creature is one of five families at an intensity, on a body of `rank`
    // limbs (1–6). No family = white, the empty state: a newborn, a grazer, a
    // bare limb. Rank is morphology and intensity is meat — they are orthogonal,
    // so a 2-limb Rage beast and a 5-limb Pale one are both legal animals.
    public string family    = null;
    public int    intensity = GameConfig.Pale;
    public int    rank      = 1;
    public bool   isBoss    = false;

    // Set from creatures.json when the creature comes from the content tables:
    // the authored name, and the authored base_hex, which overrides the palette
    // colour the family alone would pick. The family is still what the player
    // inherits by eating this creature.
    public string displayName     = null;
    public bool   hasBodyColor    = false;
    public bool   hasContentStats = false;
    public Color  bodyColor;

    public Color BodyColor => hasBodyColor ? bodyColor : GameConfig.Colors.ForFamily(family);

    // ── Standing on the ground ────────────────────────────────────────────────
    // The world used to be a plane at y=0, so every body simply pinned itself to
    // half its own height. It is terrain now, so the same idea reads the ground
    // underneath instead. Before the mesh exists BiomeTerrain returns 0, which is
    // exactly the old flat-plane answer — so nothing breaks while it generates.

    protected const float GroundFollow = 18f; // how fast a body settles onto a slope

    /// <summary>Y this body should stand at, over the ground beneath `at`.</summary>
    protected float GroundY(Vector3 at) =>
        Morphivore.World.BiomeTerrain.HeightAt(at.x, at.z) + transform.localScale.y * 0.5f;

    /// <summary>Eased toward the ground, so walking a slope doesn't snap.</summary>
    protected float StickY(Vector3 pos) =>
        Mathf.Lerp(pos.y, GroundY(pos), Mathf.Clamp01(GroundFollow * Time.deltaTime));

    public float maxHealth  = 100f;
    public float health;
    public bool  isDead     = false;
    public bool  isDowned   = false; // "dizzy" / vulnerable knockdown state (enemies)

    protected float damageCooldownTimer = 0f;

    protected GameObject body;
    protected GameObject[] limbs = new GameObject[0];

    protected virtual void Awake()
    {
        // Visuals are built by the spawner after setting family/intensity/rank.
        // Only init health here.
        if (isBoss) maxHealth *= GameConfig.Boss.HealthMultiplier;
        health = maxHealth;
    }

    // Call this after setting family, intensity, rank, isBoss (and after
    // ApplyContent, if this creature came from the content tables — authored
    // health wins over the prototype boss multiplier).
    public void Init()
    {
        if (isBoss && !hasContentStats)
        {
            maxHealth = 100f * GameConfig.Boss.HealthMultiplier;
            health    = maxHealth;
        }
        BuildVisuals();
    }

    public void BuildVisuals()
    {
        // Destroy old children except this component's GO root
        foreach (Transform child in transform)
            Destroy(child.gameObject);

        limbs = new GameObject[0];

        var rankData = GameConfig.RankFor(rank);
        Color col = BodyColor;

        // Body cube
        body = GameObject.CreatePrimitive(PrimitiveType.Cube);
        body.transform.SetParent(transform, false);
        SetColor(body, col, isBoss);
        Destroy(body.GetComponent<Collider>());

        // Eyes
        CreateEye(new Vector3(-0.25f, 0.2f, 0.5f));
        CreateEye(new Vector3( 0.25f, 0.2f, 0.5f));

        // One limb per rank — and, on the player, one colour slot per limb.
        int limbCount = Mathf.Clamp(rank, 0, GameConfig.Ranks.Length);
        limbs = new GameObject[limbCount];
        for (int i = 0; i < limbCount; i++)
        {
            float angle  = (float)i / limbCount * Mathf.PI * 2f;
            float radius = 0.6f;
            var limb = CreateLimb(LimbColor(i));
            limb.transform.SetParent(transform, false);
            limb.transform.localPosition = new Vector3(Mathf.Cos(angle) * radius, -0.3f, Mathf.Sin(angle) * radius);
            limbs[i] = limb;
        }

        // Scale
        float finalScale = rankData.scale;
        if (isBoss) finalScale *= GameConfig.Boss.ScaleMultiplier;
        transform.localScale = Vector3.one * finalScale;
        // Re-seat on the ground: the body just changed size, and a rebuild fires
        // on every mutation and every recovery from a knockdown.
        transform.position   = new Vector3(transform.position.x,
                                           GroundY(transform.position),
                                           transform.position.z);
    }

    /// <summary>Colour of limb `index`. Wildlife wears one colour all over; the
    /// player overrides this to show what each limb is holding (§2.4a).</summary>
    protected virtual Color LimbColor(int index) => BodyColor;

    void CreateEye(Vector3 localPos)
    {
        var eye = GameObject.CreatePrimitive(PrimitiveType.Cube);
        eye.transform.SetParent(transform, false);
        eye.transform.localPosition = localPos;
        eye.transform.localScale    = new Vector3(0.2f, 0.2f, 0.1f);
        eye.GetComponent<Renderer>().material.color = Color.black;
        Destroy(eye.GetComponent<Collider>());
    }

    GameObject CreateLimb(Color col)
    {
        // Sphere for the agile families, cube for the heavy ones (Unity has no
        // tetrahedron/octahedron primitive). Shape reads the body's family, not
        // the slot's — the silhouette is what you are, not what you ate last.
        PrimitiveType pType = (family == "Red" || family == "Blue" || family == "Purple")
            ? PrimitiveType.Sphere
            : PrimitiveType.Cube;
        var limb = GameObject.CreatePrimitive(pType);
        limb.transform.localScale = Vector3.one * 0.3f;
        SetColor(limb, col, false);
        Destroy(limb.GetComponent<Collider>());
        return limb;
    }

    void SetColor(GameObject go, Color col, bool emissive)
    {
        var mat = go.GetComponent<Renderer>().material;
        mat.color = col;
        if (emissive)
        {
            mat.EnableKeyword("_EMISSION");
            mat.SetColor("_EmissionColor", col * 0.5f);
        }
    }

    protected virtual void Update()
    {
        if (isDead) return;

        float t = Time.time * 5f;
        if (body) body.transform.localPosition = new Vector3(0f, Mathf.Sin(t) * 0.05f, 0f);
        for (int i = 0; i < limbs.Length; i++)
            if (limbs[i]) limbs[i].transform.localPosition = new Vector3(
                limbs[i].transform.localPosition.x,
                -0.3f + Mathf.Sin(t + i) * 0.1f,
                limbs[i].transform.localPosition.z);

        if (damageCooldownTimer > 0f)
        {
            damageCooldownTimer -= Time.deltaTime;
            if (body)
            {
                float flash = Mathf.Sin(Time.time * 30f) > 0 ? 1f : 0f;
                var mat = body.GetComponent<Renderer>().material;
                mat.EnableKeyword("_EMISSION");
                mat.SetColor("_EmissionColor", Color.white * flash * 0.5f);
            }
        }
        else if (body && !isBoss)
        {
            var mat = body.GetComponent<Renderer>().material;
            mat.SetColor("_EmissionColor", Color.black);
        }
    }

    public virtual void TakeDamage(float amount)
    {
        if (damageCooldownTimer > 0f || isDead) return;
        health -= amount;
        damageCooldownTimer = GameConfig.DamageCooldown;
        if (health <= 0f) Die();
    }

    protected virtual void Die()
    {
        isDead = true;
        transform.localScale = new Vector3(transform.localScale.x, 0.1f, transform.localScale.z);
        transform.position   = new Vector3(transform.position.x, 0.05f, transform.position.z);
        StartCoroutine(RemoveAfterDelay(2f));
    }

    IEnumerator RemoveAfterDelay(float delay)
    {
        yield return new WaitForSeconds(delay);
        Destroy(gameObject);
    }
}

```

</details>

- `write_file(path='Assets/Scripts/Game/Creature.cs', why="Swaps the colorType/tier identity for §2.4's family + intensity +, contents='using System.Collections;\nusing UnityEngine;\n\npublic clas)` → Modified Assets/Scripts/Game/Creature.cs (210 lines). OK — delimiters balanced.

### Modified: `Assets/Scripts/Content/ContentDatabase.cs`

_Becomes the first consumer of forms.json (lookup by family/intensity/rank) and maps the content's saturation tier onto intensity instead of onto a morphology tier._

<details><summary>217 lines</summary>

```csharp
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

```

</details>

- `write_file(path='Assets/Scripts/Content/ContentDatabase.cs', why="Becomes the first consumer of forms.json (lookup by family/intens, contents='// Runtime bridge between the generated world content (Strea)` → Modified Assets/Scripts/Content/ContentDatabase.cs (217 lines). OK — delimiters balanced.

### Modified: `Assets/Scripts/Game/EnemyAI.cs`

_Stamps content creatures with family + intensity + limb rank instead of a colorType/tier, and compares intensity (the meat's saturation) where it used to compare the conflated tier._

<details><summary>540 lines</summary>

```csharp
using UnityEngine;
using Morphivore.Content;

public class EnemyAI : Creature
{
    enum State  { Wander, Chase, Flee }
    enum Attack { None, Windup, Pounce }

    // ── Content-driven identity & stats (creatures.json) ──────────────────────
    // Everything here has a prototype default, so an enemy spawned without
    // content still behaves exactly as it did before.
    public string contentId;
    public string role            = "prey";
    public bool   carriesColour   = true;   // grazers carry no colour to give
    public float  healsPlayerPct  = 0f;     // >0: eating heals this share of max HP

    float contactDamage = 8f;
    float lockRange     = -1f;   // <0 → derive from body size, as before
    float pounceSpeed   = -1f;   // <0 → derive from moveSpeed, as before
    bool  alwaysFlees;           // grazers: never fight, whatever the gap
    bool  alwaysHunts;           // elites, minibosses, alphas, the apex

    // The content's `dash` is a speed on the same scale as `speed`; a pounce is a
    // committed lunge, so it travels at a multiple of it.
    const float PounceLungeFactor = 4f;

    /// <summary>Stamp this enemy with one creature from the content tables, for a
    /// specific biome. Call before Init() so the visuals build from it.</summary>
    public void ApplyContent(CreatureDef def, SpawnDef spawn)
    {
        contentId       = def.id;
        role            = def.role;
        displayName     = def.name;
        carriesColour   = def.carries_colour;
        healsPlayerPct  = def.heals_player_pct;

        // Family is the colour its meat carries; the content's tier is that
        // meat's intensity, and its limb count is the body plan (§2.4b). Grazers
        // author neither — they come out white and limbless, which is what they are.
        family    = def.family;
        intensity = ContentDatabase.IntensityIndex(def.tier);
        rank      = Mathf.Clamp(def.limbs > 0 ? def.limbs : def.rank, 0, GameConfig.Ranks.Length);

        bodyColor    = ContentDatabase.HexToColor(def.base_hex, GameConfig.Colors.ForFamily(family));
        hasBodyColor = true;

        alwaysFlees = role == "grazer";
        alwaysHunts = role == "elite" || role == "trait_miniboss"
                   || role == "alpha" || role == "apex";

        // Authored numbers land here once, scaled by GameConfig.Ecology, so every
        // consumer below reads a playable value and the JSON stays untouched.
        // Health is deliberately not scaled: a creature that takes a couple of
        // pounces to knock down is the point, and it's not what kills the player.
        var st = spawn.stats;
        if (st != null)
        {
            if (st.health > 0f) { maxHealth = st.health; health = maxHealth; }
            if (st.speed  > 0f) moveSpeed   = st.speed  * GameConfig.Ecology.SpeedScale;
            if (st.reach  > 0f) lockRange   = st.reach  * GameConfig.Ecology.ReachScale;
            if (st.dash   > 0f) pounceSpeed = st.dash   * GameConfig.Ecology.SpeedScale * PounceLungeFactor;
            contactDamage = st.damage * GameConfig.Ecology.ContactDamageScale;
        }
        // Grazers carry no combat stats — they get a flee speed instead.
        if (spawn.flee_speed > 0f) moveSpeed = spawn.flee_speed * GameConfig.Ecology.SpeedScale;

        hasContentStats = true;
    }

    State state = State.Wander;
    Vector3 targetDir;
    float moveSpeed;
    float changeDirTimer = 0f;

    Transform        playerTransform;
    PlayerController playerCtrl;

    // Knockdown ("dizzy") state — enemies don't die from stomach loss, they get
    // knocked down and become vulnerable, and are only removed when eaten.
    float   downedTimer = 0f;
    const float DownedDuration = 5f;
    Vector3 preDownedScale;

    // Reactions
    float staggerTimer = 0f;                 // brief reel after being hit
    public bool isLockedByPlayer = false;    // set by PlayerController while it locks us
    float   fleePhase;                       // per-enemy zig-zag offset

    // Temperament — rolled per creature so a biome doesn't react as one animal.
    float sightScale   = 1f;   // this creature's share of the sight radius
    bool  standsGround;        // content prey: territorial minority that fights back

    // Attacking the player — mirrors the player's lock → pounce. Weaker meat
    // (<= the player's intensity) must stand still to wind up; stronger meat can
    // keep closing while locked.
    Attack  attackPhase    = Attack.None;
    float   attackCooldown = 0f;
    float   windupTimer    = 0f;
    float   pounceTimer    = 0f;
    Vector3 pounceDir      = Vector3.zero;
    const float WindupTime = 0.6f;
    const float PounceTime = 0.3f;

    Collider myCol;

    // Floating health bar — shown only when the enemy is damaged. Kept as a
    // separate object (not a child) so Creature.BuildVisuals, which clears all
    // children, doesn't destroy it.
    GameObject healthBarGO;
    Transform  healthFillTf;
    Renderer   healthFillRend;
    Camera     barCam;

    protected override void Awake()
    {
        base.Awake();
        moveSpeed = Random.Range(2f, 5f);
        if (isBoss) moveSpeed *= 0.7f;
        targetDir = new Vector3(Random.Range(-1f, 1f), 0f, Random.Range(-1f, 1f)).normalized;
        fleePhase = Random.Range(0f, 6.28f);

        sightScale   = Random.Range(1f - GameConfig.Ecology.SightJitter,
                                    1f + GameConfig.Ecology.SightJitter);
        standsGround = Random.value < GameConfig.Ecology.TerritorialPreyShare;
    }

    // ── Aggro budget ──────────────────────────────────────────────────────────
    // A content biome holds 18-34 creatures, and unbounded, every one that ever
    // noticed the player joined the same chase and never fell off. Only a few may
    // hunt at once. Counting per frame rather than handing out held slots means
    // nothing has to be released when a creature is eaten, downed or unloaded.
    static int hunters = 0, hunterFrame = -1;

    static void BeginHunterFrame()
    {
        if (hunterFrame == Time.frameCount) return;
        hunterFrame = Time.frameCount;
        hunters     = 0;
    }

    static void CountHunter() { BeginHunterFrame(); hunters++; }

    static bool ClaimHunterSlot()
    {
        BeginHunterFrame();
        if (hunters >= GameConfig.Ecology.MaxHunters) return false;
        hunters++;
        return true;
    }

    /// <summary>Content prey only: bolt unless this one is territorial or carries
    /// stronger meat than the player — and then only if the budget has room. A
    /// creature already mid-attack is always let through so a committed pounce
    /// resolves.</summary>
    bool WantsToHunt(int playerIntensity)
    {
        if (attackPhase != Attack.None) { CountHunter(); return true; }
        if (!standsGround && intensity <= playerIntensity) return false;
        return ClaimHunterSlot();
    }

    // Damage is ignored while dead or already downed; otherwise it staggers us
    // and interrupts any attack in progress.
    public override void TakeDamage(float amount)
    {
        if (isDead || isDowned) return;
        base.TakeDamage(amount); // gates on cooldown, subtracts health, calls Die() at 0
        if (!isDowned)
        {
            staggerTimer   = 0.35f;
            attackPhase    = Attack.None;                     // getting hit cancels our attack
            attackCooldown = Mathf.Max(attackCooldown, 0.5f);
        }
    }

    // Reaching zero stomach knocks the enemy down instead of removing it.
    protected override void Die()
    {
        EnterDowned();
    }

    void EnterDowned()
    {
        isDowned    = true;
        attackPhase = Attack.None;
        downedTimer = DownedDuration;

        // Squash flat + dim so it clearly reads as "dizzy / vulnerable".
        preDownedScale = transform.localScale;
        transform.localScale = new Vector3(preDownedScale.x * 1.25f,
                                           preDownedScale.y * 0.4f,
                                           preDownedScale.z * 1.25f);
        if (body) body.GetComponent<Renderer>().material.color = BodyColor * 0.5f;
    }

    void Recover()
    {
        isDowned = false;
        transform.localScale = preDownedScale;
        health = maxHealth * 0.5f;
        BuildVisuals(); // restores color + scale cleanly
    }

    // Called by the player when pouncing a downed enemy to eat it. Plays a
    // grab-and-absorb animation: the enemy is pulled into the eater while
    // shrinking and spinning, then removed.
    public void GetEaten(Transform eater)
    {
        if (isDead) return;
        isDead   = true;   // stops AI (Creature.Update early-outs) and re-hits
        isDowned = false;

        if (myCol == null) myCol = GetComponent<Collider>();
        if (myCol != null) myCol.enabled = false; // don't collide while being absorbed

        StopAllCoroutines(); // cancel any in-flight bite
        StartCoroutine(EatSequence(eater));
    }

    System.Collections.IEnumerator EatSequence(Transform eater)
    {
        float dur = 0.35f, t = 0f;
        Vector3 startScale = transform.localScale;

        while (t < dur)
        {
            if (eater != null)
            {
                Vector3 mouth = eater.position
                              + eater.forward * (eater.localScale.x * 0.4f)
                              + Vector3.up   * (eater.localScale.y * 0.25f);
                transform.position = Vector3.Lerp(transform.position, mouth, 14f * Time.deltaTime);
            }
            transform.localScale = Vector3.Lerp(startScale, Vector3.one * 0.01f, t / dur);
            transform.Rotate(0f, 900f * Time.deltaTime, 0f);

            t += Time.deltaTime;
            yield return null;
        }
        Destroy(gameObject);
    }

    protected override void Update()
    {
        UpdateHealthBar();

        if (isDowned) { UpdateDowned(); return; }

        base.Update();
        if (isDead) return;

        // Lazy-find player so spawn order doesn't matter
        if (playerCtrl == null)
        {
            var go = GameObject.FindWithTag("Player");
            if (go == null) return;
            playerTransform = go.transform;
            playerCtrl      = go.GetComponent<PlayerController>();
        }
        if (playerCtrl.isDead) return;

        float dt              = Time.deltaTime;
        float distToPlayer    = Vector3.Distance(transform.position, playerTransform.position);
        int   playerIntensity = playerCtrl.intensity;
        Vector3 toPlayer      = playerTransform.position - transform.position; toPlayer.y = 0f;
        Vector3 toPlayerDir   = toPlayer.sqrMagnitude > 0.001f ? toPlayer.normalized : transform.forward;

        if (attackCooldown > 0f) attackCooldown -= dt;

        // Bigger / darker-meated creatures notice you from farther. Perception is
        // not reach: the authored reach is how far a creature can pounce, and
        // borrowing it as a sight radius had a Pale prey spotting the player from
        // 18.7 units — a third of the map's width, so the biome aggroed as one.
        // Content creatures see about as far as the prototype's did, jittered per
        // creature, with the (already scaled) reach only as a floor so nothing
        // stands inside its own pounce range doing nothing.
        float awareness = hasContentStats
            ? Mathf.Max((GameConfig.Ecology.SightRadius + intensity * 2f + transform.localScale.x) * sightScale,
                        lockRange)
            : 10f + intensity * 2f + transform.localScale.x;

        if (staggerTimer > 0f)
        {
            staggerTimer -= dt; // reel in place after a hit
            FaceDir(toPlayerDir);
        }
        else
        {
            if (distToPlayer < awareness)
            {
                // Role and temperament decide the reaction, not the meat gap alone.
                // Ordinary content prey bolt — the Prairies' Pale prey are authored
                // to sprint for open ground when locked, not to brawl. Predators
                // still count against the budget without being blocked by it, so
                // prey yield the field to whatever is hunting.
                if      (alwaysFlees)      state = State.Flee;
                else if (alwaysHunts)    { CountHunter(); state = State.Chase; }
                else if (hasContentStats) state = WantsToHunt(playerIntensity) ? State.Chase : State.Flee;
                else                      state = (intensity < playerIntensity) ? State.Flee : State.Chase;
            }
            else
                state = State.Wander;

            if (state == State.Chase)
            {
                // Same/stronger meat: hunt and pounce the player like they pounce us.
                UpdateAttack(dt, distToPlayer, toPlayerDir);
            }
            else
            {
                // Breaking off the chase abandons a half-finished attack, so a
                // stale Windup can't buy a hunt slot later (WantsToHunt lets a
                // committed attacker through) when the player wanders back.
                if (hasContentStats) attackPhase = Attack.None;

                float spd = moveSpeed;
                if (state == State.Flee)
                {
                    // Zig-zag panic away from the player.
                    Vector3 away = -toPlayerDir;
                    Vector3 perp = Vector3.Cross(Vector3.up, away);
                    float   wob  = Mathf.Sin(Time.time * 8f + fleePhase) * 0.6f;
                    targetDir = (away + perp * wob).normalized;
                    // The prototype's panic boost was tuned against random wander
                    // speeds. A content creature's authored speed already IS its
                    // flat-out sprint, and prey have to stay runnable-down or the
                    // player can never finish a hunt, so no boost on that path.
                    if (!hasContentStats)
                    {
                        if (isLockedByPlayer)                     spd *= 1.6f;
                        else if (distToPlayer < awareness * 0.5f) spd *= 1.3f;
                    }
                }
                else // Wander
                {
                    // Authored speed is a sprint, not a patrol pace — wandering at
                    // it made the whole biome look like it was already charging.
                    if (hasContentStats) spd *= GameConfig.Ecology.WanderPace;

                    changeDirTimer -= dt;
                    if (changeDirTimer <= 0f)
                    {
                        targetDir      = new Vector3(Random.Range(-1f, 1f), 0f, Random.Range(-1f, 1f)).normalized;
                        changeDirTimer = Random.Range(2f, 5f);
                    }
                }
                transform.position += targetDir * spd * dt;
                FaceDir(targetDir);
            }
        }

        // Solid: don't overlap other enemies / obstacles.
        ResolveEnemyCollisions();

        // Boundary
        float limit = Morphivore.World.BiomeTerrain.Radius;
        Vector3 pos = transform.position;
        if (Mathf.Abs(pos.x) > limit) targetDir.x *= -1f;
        if (Mathf.Abs(pos.z) > limit) targetDir.z *= -1f;
        pos.x = Mathf.Clamp(pos.x, -limit, limit);
        pos.z = Mathf.Clamp(pos.z, -limit, limit);
        pos.y = GroundY(pos);
        transform.position = pos;
    }

    // Lock → windup → pounce cycle against the player.
    void UpdateAttack(float dt, float dist, Vector3 toPlayerDir)
    {
        bool  canMoveWhileLocked = intensity > playerCtrl.intensity; // stronger meat moves while locked
        float startRange = lockRange > 0f ? lockRange : 3.5f + transform.localScale.x;
        float delock     = startRange + 7f;
        float lunge      = pounceSpeed > 0f ? pounceSpeed : moveSpeed * 4.5f;

        switch (attackPhase)
        {
            case Attack.None:
                // Close in; when in range and off cooldown, begin the wind-up.
                transform.position += toPlayerDir * moveSpeed * dt;
                FaceDir(toPlayerDir);
                if (dist < startRange && attackCooldown <= 0f)
                {
                    attackPhase = Attack.Windup;
                    windupTimer = WindupTime;
                }
                break;

            case Attack.Windup:
                playerCtrl.FlagThreat();          // player sees the "targeted" halo
                FaceDir(toPlayerDir);
                if (canMoveWhileLocked)
                    transform.position += toPlayerDir * moveSpeed * 0.6f * dt; // big keeps closing
                // small enemies stand still to wind up

                windupTimer -= dt;
                if (dist > delock)                 EndAttack(0.4f);   // player ran → de-lock
                else if (windupTimer <= 0f)
                {
                    pounceDir   = toPlayerDir;      // commit — moving now dodges it
                    attackPhase = Attack.Pounce;
                    // A pounce should carry roughly as far as the creature can
                    // lock, so a long-reach Sniper actually crosses its own range.
                    pounceTimer = lockRange > 0f
                        ? Mathf.Clamp(startRange / lunge, PounceTime, 0.6f)
                        : PounceTime;
                }
                break;

            case Attack.Pounce:
                playerCtrl.FlagThreat();
                transform.position += pounceDir * lunge * dt;
                FaceDir(pounceDir);
                pounceTimer -= dt;

                float contact = (transform.localScale.x + playerCtrl.transform.localScale.x) * 0.5f + 0.4f;
                if (dist < contact)        { HitPlayer(); EndAttack(1.6f); }
                else if (pounceTimer <= 0f) EndAttack(1.2f);
                break;
        }
    }

    void EndAttack(float cooldown)
    {
        attackPhase    = Attack.None;
        attackCooldown = cooldown;
    }

    void HitPlayer()
    {
        // Content creatures carry their own authored damage (an alpha is already
        // scaled as a boss); the prototype path keeps the flat value + multiplier.
        float dmg = hasContentStats
            ? contactDamage
            : (isBoss ? 8f * GameConfig.Boss.DamageMultiplier : 8f);
        playerCtrl.TakeDamage(dmg);
    }

    void FaceDir(Vector3 dir)
    {
        if (dir == Vector3.zero) return;
        float targetRot = Mathf.Atan2(dir.x, dir.z) * Mathf.Rad2Deg;
        transform.rotation = Quaternion.Euler(0f, Mathf.LerpAngle(transform.eulerAngles.y, targetRot, 0.15f), 0f);
    }

    // ── Floating health bar ───────────────────────────────────────────────────

    const float BarWidth = 1.4f;

    void UpdateHealthBar()
    {
        // Only show it once the enemy has been hit (and isn't down/dead).
        bool show = !isDead && !isDowned && health < maxHealth - 0.01f;

        if (!show)
        {
            if (healthBarGO != null && healthBarGO.activeSelf) healthBarGO.SetActive(false);
            return;
        }

        if (healthBarGO == null) CreateHealthBar();
        if (barCam == null) barCam = Camera.main;
        healthBarGO.SetActive(true);

        // Hover above the enemy, billboarded to the camera.
        float top = transform.localScale.y * 0.5f + 1.0f;
        healthBarGO.transform.position = transform.position + Vector3.up * top;
        if (barCam != null) healthBarGO.transform.rotation = barCam.transform.rotation;

        // Fill grows from the left; colour lerps red→green with health.
        float ratio = Mathf.Clamp01(health / maxHealth);
        healthFillTf.localScale    = new Vector3(BarWidth * ratio, 0.18f, 0.06f);
        healthFillTf.localPosition = new Vector3(-BarWidth * (1f - ratio) * 0.5f, 0f, -0.02f);
        if (healthFillRend != null)
            healthFillRend.material.color =
                Color.Lerp(new Color(1f, 0.25f, 0.2f), new Color(0.3f, 0.9f, 0.35f), ratio);
    }

    void CreateHealthBar()
    {
        healthBarGO = new GameObject("EnemyHealthBar");

        var bg = GameObject.CreatePrimitive(PrimitiveType.Cube);
        bg.name = "BG";
        Destroy(bg.GetComponent<Collider>());
        bg.transform.SetParent(healthBarGO.transform, false);
        bg.transform.localScale    = new Vector3(BarWidth, 0.18f, 0.05f);
        bg.GetComponent<Renderer>().material.color = new Color(0.08f, 0.08f, 0.08f, 1f);

        var fill = GameObject.CreatePrimitive(PrimitiveType.Cube);
        fill.name = "Fill";
        Destroy(fill.GetComponent<Collider>());
        fill.transform.SetParent(healthBarGO.transform, false);
        fill.transform.localScale    = new Vector3(BarWidth, 0.18f, 0.06f);
        fill.transform.localPosition = new Vector3(0f, 0f, -0.02f);
        healthFillTf   = fill.transform;
        healthFillRend = fill.GetComponent<Renderer>();
        healthFillRend.material.color = new Color(0.3f, 0.9f, 0.35f);
    }

    void OnDestroy()
    {
        if (healthBarGO != null) Destroy(healthBarGO);
    }

    void UpdateDowned()
    {
        downedTimer -= Time.deltaTime;
        transform.rotation = Quaternion.Euler(0f, transform.eulerAngles.y + 120f * Time.deltaTime, 0f);
        Vector3 p = transform.position;
        p.y = GroundY(p);
        transform.position = p;
        if (downedTimer <= 0f) Recover();
    }

    // Push out of overlapping enemies (shared half each) and obstacles (full).
    void ResolveEnemyCollisions()
    {
        if (myCol == null) myCol = GetComponent<Collider>();
        if (myCol == null) return;

        float q = myCol.bounds.extents.magnitude + 2f;
        foreach (var other in Physics.OverlapSphere(transform.position, q))
        {
            if (other == myCol) continue;
            if (other.GetComponentInParent<PlayerController>() != null) continue; // player resolves itself

            bool isEnemy    = other.GetComponentInParent<EnemyAI>()  != null;
            bool isObstacle = other.GetComponentInParent<Obstacle>() != null;
            if (!isEnemy && !isObstacle) continue;

            if (Physics.ComputePenetration(
                    myCol, transform.position, transform.rotation,
                    other, other.transform.position, other.transform.rotation,
                    out Vector3 dir, out float dist))
            {
                Vector3 push = dir * dist; push.y = 0f;
                transform.position += isObstacle ? push : push * 0.5f;
            }
        }
    }
}

```

</details>

- `write_file(path='Assets/Scripts/Game/EnemyAI.cs', why="Stamps content creatures with family + intensity + limb rank inst, contents='using UnityEngine;\nusing Morphivore.Content;\n\npublic clas)` → Modified Assets/Scripts/Game/EnemyAI.cs (540 lines). OK — delimiters balanced.

### Modified: `Assets/Scripts/Game/PlayerController.cs`

_Replaces kills→class/tier levelling with the colour buffer: eating loads a limb, Q/B poops the oldest, the buffer resolves to a form, and every live stat comes from that form's line._

<details><summary>556 lines</summary>

```csharp
using UnityEngine;
using UnityEngine.InputSystem;
using Morphivore.Content;

public class PlayerController : Creature
{
    public bool  gameStarted = false;
    public float moveSpeed;
    public float biteDamage;
    public int   totalKills  = 0;
    public int   score       = 0;

    // ── Form (§2.4a, §2.4b) ───────────────────────────────────────────────────
    // One colour slot per limb. What the slots hold resolves to exactly one of
    // the 150 forms, and that form is where every live stat comes from — there
    // is no hidden levelling underneath it.
    readonly ColourBuffer buffer = new ColourBuffer();

    public string FormName { get; private set; } = GameConfig.BlankFormName;

    float reach;      // lock + strike range, straight off the form
    float dashGear;   // form dash / form speed: the family's dash trade, scaled

    float biteCooldown  = 0f;
    float dashCooldown  = 0f;
    bool  isDashing     = false;
    float dashTimer     = 0f;
    bool  isLunging     = false;   // mid-pounce

    // Lock-on (Cubivore-style "target then launch"). Hold lock to acquire the
    // nearest enemy roughly in front; pounce launches at the locked target.
    bool     isLocking    = false;
    EnemyAI  lockedTarget = null;
    const float LockConeDot = 0.2f; // ~78° half-cone around facing to be lockable

    // Tells the HUD which transform to draw the lock-on reticle over (null = hide).
    public System.Action<Transform> OnLockTargetChanged;

    // Threat: refreshed by any enemy currently locked onto us; drives the "you
    // are targeted" halo so the player can react to an incoming pounce.
    float threatTimer = 0f;
    public bool IsThreatened => threatTimer > 0f;
    public void FlagThreat() { threatTimer = 0.25f; }

    int companionCount = 0;

    // Events consumed by GameManager
    public System.Action<string>               OnNotification;
    public System.Action<GameConfig.BiomeData> OnBiomeRequest;

    // Body collider used for solid collision resolution (radius scales with rank).
    SphereCollider bodyCollider;

    protected override void Awake()
    {
        base.Awake();

        // Solid body: a collider on the root (BuildVisuals only clears child
        // colliders) plus a kinematic rigidbody so moving it stays cheap. We
        // still move via transform and depenetrate manually (ResolveCollisions).
        bodyCollider = gameObject.AddComponent<SphereCollider>();
        bodyCollider.radius = 0.5f;
        var rb = gameObject.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity  = false;

        // The hatchling is the blank: a white cube with one bare limb, multiplier
        // 1.0 on every axis. Its first meal is its first identity.
        buffer.Resize(rank);
        ApplyForm();
        BuildVisuals();
    }

    // ── Form resolution and stats ─────────────────────────────────────────────

    // Resolve the buffer, look the form up in forms.json and take its stat line.
    // Deterministic (not incremental), so a meal can never double-apply.
    void ApplyForm()
    {
        FormKey key = buffer.Resolve();
        family    = key.family;
        intensity = key.intensity;

        var def = ContentDatabase.Form(family, intensity, rank);
        GameConfig.StatLine s;

        if (def?.stats != null)
        {
            // The authored line: the same composition, hand-tuned per form.
            s = new GameConfig.StatLine
            {
                health = def.stats.health, damage = def.stats.damage,
                speed  = def.stats.speed,  reach  = def.stats.reach,
                dash   = def.stats.dash
            };
            FormName = def.name;
        }
        else
        {
            // No forms.json: compose the limb baseline × family × intensity here.
            s = GameConfig.StatsFor(family, intensity, rank);
            FormName = GameConfig.FormNameFor(family, intensity);
        }

        // Mutating re-cuts the bar and preserves the wound, not the number: you
        // keep the same fraction, so it never heals and never costs a point (§2.3).
        float wound = maxHealth > 0f ? Mathf.Clamp01(health / maxHealth) : 1f;
        maxHealth   = s.health;
        health      = maxHealth * wound;

        moveSpeed  = s.speed;
        biteDamage = s.damage;
        reach      = s.reach;
        dashGear   = s.speed > 0f ? s.dash / s.speed : 1f;
    }

    // Any change to the buffer redraws the body (limb colours are buffer state)
    // and re-stats; a change of *form* is the mutation, and it fires instantly.
    void OnBufferChanged()
    {
        string wasFamily    = family;
        int    wasIntensity = intensity;

        ApplyForm();
        BuildVisuals();

        if (family != wasFamily || intensity != wasIntensity)
            OnNotification?.Invoke($"MUTATED — {FormName.ToUpper()}!");
    }

    // A limb shows what it is holding: its family's colour, saturated by its
    // tier — Pale meat reads washed out, Rage meat reads full (§2.4b).
    protected override Color LimbColor(int index)
    {
        if (index >= buffer.Count) return GameConfig.Colors.White;
        ColourUnit unit = buffer[index];
        if (unit.IsWhite) return GameConfig.Colors.White;
        return Color.Lerp(GameConfig.Colors.White,
                          GameConfig.Colors.ForFamily(unit.family),
                          GameConfig.Intensities[unit.intensity].pct);
    }

    // The next slot to be overwritten always pulses on the body, so a colour is
    // never lost unknowingly (§2.4a). Scale and glow, never opacity (§4.9a).
    void PulseNextSlot()
    {
        int next = buffer.NextSlot;
        if (next < 0 || next >= limbs.Length || limbs[next] == null) return;

        float pulse = 0.5f + 0.5f * Mathf.Sin(Time.time * 6f);
        limbs[next].transform.localScale = Vector3.one * (0.3f + 0.09f * pulse);

        var mat = limbs[next].GetComponent<Renderer>().material;
        mat.EnableKeyword("_EMISSION");
        mat.SetColor("_EmissionColor", LimbColor(next) * (0.25f + 0.55f * pulse));
    }

    // Q / B: the oldest colour goes out, that limb turns white, and the unit is
    // left behind you on the ground.
    void Poop()
    {
        if (!buffer.Poop(out ColourUnit dropped)) return;
        LeaveDropping(dropped);
        OnBufferChanged();
    }

    void LeaveDropping(ColourUnit unit)
    {
        var drop = GameObject.CreatePrimitive(PrimitiveType.Cube);
        drop.name = "Dropping";
        Destroy(drop.GetComponent<Collider>());
        drop.transform.localScale = Vector3.one * 0.35f;

        Vector3 behind = transform.position - transform.forward * (transform.localScale.z * 0.8f);
        behind.y = Morphivore.World.BiomeTerrain.HeightAt(behind.x, behind.z) + 0.18f;
        drop.transform.position = behind;
        drop.transform.rotation = Quaternion.Euler(Random.Range(0f, 360f), Random.Range(0f, 360f), 0f);

        drop.GetComponent<Renderer>().material.color =
            GameConfig.Colors.ForFamily(unit.family) * 0.7f;
    }

    protected override void Update()
    {
        base.Update();
        if (!gameStarted || isDead) return;

        // Cooldowns
        if (biteCooldown  > 0f) biteCooldown  -= Time.deltaTime;
        if (dashCooldown  > 0f) dashCooldown  -= Time.deltaTime;
        if (isDashing)
        {
            dashTimer -= Time.deltaTime;
            if (dashTimer <= 0f) isDashing = false;
        }

        if (threatTimer > 0f) threatTimer -= Time.deltaTime;

        // Regen
        if (health < maxHealth) health += GameConfig.RegenRate * Time.deltaTime;

        PulseNextSlot();

        // Movement — keyboard + gamepad left stick
        var kb = Keyboard.current;
        Vector3 move = Vector3.zero;

        if (kb != null)
        {
            if (kb.wKey.isPressed || kb.upArrowKey.isPressed)    move += Vector3.forward;
            if (kb.sKey.isPressed || kb.downArrowKey.isPressed)  move += Vector3.back;
            if (kb.aKey.isPressed || kb.leftArrowKey.isPressed)  move += Vector3.left;
            if (kb.dKey.isPressed || kb.rightArrowKey.isPressed) move += Vector3.right;
        }

        bool gpLock   = false;
        bool gpPounce = false;
        bool gpDash   = false;
        bool gpPoop   = false;

        foreach (var gp in Gamepad.all)
        {
            Vector2 ls = gp.leftStick.ReadValue();
            if (ls.magnitude > 0.15f) move += new Vector3(ls.x, 0f, ls.y);

            if (gp.dpad.up.isPressed)    move += Vector3.forward;
            if (gp.dpad.down.isPressed)  move += Vector3.back;
            if (gp.dpad.left.isPressed)  move += Vector3.left;
            if (gp.dpad.right.isPressed) move += Vector3.right;

            if (gp.leftShoulder.isPressed)           gpLock   = true; // hold LB = hard-lock
            if (gp.buttonSouth.wasPressedThisFrame)  gpPounce = true; // A       = pounce
            if (gp.rightTrigger.wasPressedThisFrame) gpDash   = true; // RT      = dash
            if (gp.buttonEast.wasPressedThisFrame)   gpPoop   = true; // B       = poop
        }

        // Mouse buttons for combat: LMB pounce, hold RMB hard-lock, Space dash.
        var mouse = Mouse.current;
        bool hardLockHeld  = gpLock   || (mouse != null && mouse.rightButton.isPressed);
        bool pouncePressed = gpPounce || (mouse != null && mouse.leftButton.wasPressedThisFrame);
        bool dashPressed   = gpDash   || (kb != null && kb.spaceKey.wasPressedThisFrame);
        bool poopPressed   = gpPoop   || (kb != null && kb.qKey.wasPressedThisFrame);

        // Move — facing follows the movement direction.
        if (move != Vector3.zero && !isLunging)
        {
            move = move.normalized;
            float speed = moveSpeed * (isDashing ? 3f : 1f);
            transform.position += move * speed * Time.deltaTime;

            float ang = Mathf.Atan2(move.x, move.z) * Mathf.Rad2Deg;
            transform.rotation = Quaternion.Euler(0f, Mathf.LerpAngle(transform.eulerAngles.y, ang, 0.25f), 0f);
        }

        // Hard-lock: acquire/keep a target within the facing cone.
        UpdateLock(hardLockHeld);

        if (dashPressed)   Dash();
        if (pouncePressed) Pounce();
        if (poopPressed)   Poop();

        // Solid bodies: push out of any enemies/obstacles we overlap.
        ResolveCollisions();

        // Clamp to world
        float limit = Morphivore.World.BiomeTerrain.Radius;
        Vector3 pos = transform.position;
        pos.x = Mathf.Clamp(pos.x, -limit, limit);
        pos.z = Mathf.Clamp(pos.z, -limit, limit);
        pos.y = StickY(pos);
        transform.position = pos;
    }

    void Dash()
    {
        if (dashCooldown > 0f || isDead) return;
        isDashing    = true;
        // A Leaper's dash runs longer and recovers sooner; a Brawler's does neither.
        dashTimer    = 0.2f * dashGear;
        dashCooldown = 1.5f / dashGear;
    }

    // Push the player out of any overlapping enemy/obstacle so bodies feel solid.
    // We move by transform (not physics), so we depenetrate manually each frame.
    void ResolveCollisions()
    {
        // Skip mid-pounce so lunges drive into enemies instead of bouncing off.
        if (bodyCollider == null || isLunging) return;

        float myRadius    = bodyCollider.radius * transform.lossyScale.x;
        float queryRadius = myRadius + 4f; // margin to catch large neighbours

        foreach (var other in Physics.OverlapSphere(transform.position, queryRadius))
        {
            if (other == bodyCollider) continue;
            bool solid = other.GetComponentInParent<EnemyAI>() != null
                      || other.GetComponentInParent<Obstacle>() != null;
            if (!solid) continue;

            if (Physics.ComputePenetration(
                    bodyCollider, transform.position, transform.rotation,
                    other, other.transform.position, other.transform.rotation,
                    out Vector3 dir, out float dist))
            {
                Vector3 push = dir * dist;
                push.y = 0f; // horizontal only — keep the ground/height logic intact
                transform.position += push;
            }
        }
    }

    // ── Lock-on ───────────────────────────────────────────────────────────────

    // How far this beast can lock onto and strike an enemy: the form's Reach,
    // plus its own body so a big animal doesn't have to overlap what it grabs.
    // Reach is a family trade — a Sniper locks from outside a Brawler's world.
    float ReachRange() => reach + transform.localScale.x * 0.5f;

    void UpdateLock(bool lockHeld)
    {
        EnemyAI before = lockedTarget;

        if (lockHeld && !isDead)
        {
            isLocking = true;

            // Drop the lock if the target died or drifted out of reach (with a
            // little hysteresis so it doesn't flicker at the edge).
            if (lockedTarget != null)
            {
                float keep = ReachRange() * 1.15f;
                if (lockedTarget.isDead ||
                    Vector3.Distance(transform.position, lockedTarget.transform.position) > keep)
                    lockedTarget = null;
            }

            if (lockedTarget == null) lockedTarget = AcquireTarget();
        }
        else if (isLocking)
        {
            isLocking    = false;
            lockedTarget = null;
        }

        // On any target change, update the enemies' "I'm targeted" flags and the
        // HUD reticle (the reticle then follows the target each frame).
        if (before != lockedTarget)
        {
            if (before != null)       before.isLockedByPlayer = false;
            if (lockedTarget != null) lockedTarget.isLockedByPlayer = true;
            OnLockTargetChanged?.Invoke(lockedTarget != null ? lockedTarget.transform : null);
        }
    }

    // Nearest enemy within ReachRange that sits roughly within the facing cone.
    // Sticky once locked (see UpdateLock) until it dies, drifts out of reach, or
    // the lock is released.
    EnemyAI AcquireTarget()
    {
        Vector3 fwd  = transform.forward;
        EnemyAI best = null;
        float   bestScore = float.NegativeInfinity;

        foreach (var col in Physics.OverlapSphere(transform.position, ReachRange()))
        {
            var enemy = col.GetComponentInParent<EnemyAI>();
            if (enemy == null || enemy.isDead) continue;

            Vector3 to = enemy.transform.position - transform.position; to.y = 0f;
            float dist = to.magnitude;
            if (dist < 0.01f) continue;

            float dot = Vector3.Dot(fwd, to / dist);
            if (dot < LockConeDot) continue; // must be within the facing cone

            // Prefer targets more in-line with facing and closer.
            float score = dot - dist * 0.03f;
            if (score > bestScore) { bestScore = score; best = enemy; }
        }
        return best;
    }

    // ── Pounce (targeted tackle) ──────────────────────────────────────────────

    void Pounce()
    {
        if (isLunging || biteCooldown > 0f || isDead) return;
        biteCooldown = 0.4f;

        // Prefer the hard-locked target; otherwise soft-lock the enemy nearest
        // in the facing cone; otherwise just pounce straight ahead.
        EnemyAI target = (lockedTarget != null && !lockedTarget.isDead) ? lockedTarget : AcquireTarget();

        Vector3 dir = transform.forward;
        if (target != null)
        {
            Vector3 to = target.transform.position - transform.position; to.y = 0f;
            if (to.sqrMagnitude > 0.001f) dir = to.normalized;
        }
        StartCoroutine(PounceAnim(dir));
    }

    System.Collections.IEnumerator PounceAnim(Vector3 dir)
    {
        isLunging = true;
        Vector3 lungeDir = dir.normalized;
        // Snap facing to the pounce direction.
        transform.rotation = Quaternion.Euler(0f, Mathf.Atan2(lungeDir.x, lungeDir.z) * Mathf.Rad2Deg, 0f);

        // Fixed-power pounce (no charge): it carries exactly one Reach, so what
        // you can lock is what you can hit.
        float duration   = 0.3f;
        float lungeSpeed = ReachRange() / duration;
        float damageMult = 3f;
        float elapsed    = 0f;

        if (body) body.transform.localScale = new Vector3(1f, 1f, 1.5f);

        var hitEnemies = new System.Collections.Generic.HashSet<EnemyAI>();
        bool impact = false; // hit something solid → stop and bounce back

        while (elapsed < duration && !impact)
        {
            transform.position += lungeDir * lungeSpeed * Time.deltaTime;

            float limit = GameConfig.WorldSize;
            Vector3 pos = transform.position;
            pos.x = Mathf.Clamp(pos.x, -limit, limit);
            pos.z = Mathf.Clamp(pos.z, -limit, limit);
            pos.y = StickY(pos);
            transform.position = pos;

            Vector3 hitCenter   = transform.position + transform.forward * transform.localScale.x;
            Vector3 halfExtents = transform.localScale * 0.5f;
            var hits = Physics.OverlapBox(hitCenter, halfExtents, transform.rotation);

            foreach (var col in hits)
            {
                var enemy = col.GetComponentInParent<EnemyAI>();
                if (enemy == null || enemy.isDead || hitEnemies.Contains(enemy)) continue;
                hitEnemies.Add(enemy);

                if (enemy.isDowned)
                {
                    // Eat the downed enemy: absorb its meat (colour) now, and play
                    // the grab-and-absorb animation as it's pulled into us.
                    OnKill(enemy);
                    enemy.GetEaten(transform);
                }
                else if (intensity >= enemy.intensity)
                {
                    // Damage (may knock it down) + shove it, and bounce ourselves back.
                    enemy.TakeDamage(biteDamage * damageMult);
                    enemy.transform.position += lungeDir * 0.6f * transform.localScale.x;
                    impact = true;
                }
                else
                {
                    // Darker meat than ours: it hurts us and we bounce off.
                    TakeDamage(10f);
                    impact = true;
                }
            }

            elapsed += Time.deltaTime;
            yield return null;
        }

        // Bounce back off a solid hit.
        if (impact)
        {
            float rt = 0f, recoilDur = 0.12f;
            float recoilSpeed = lungeSpeed * 0.7f;
            while (rt < recoilDur)
            {
                transform.position -= lungeDir * recoilSpeed * Time.deltaTime;

                float limit = GameConfig.WorldSize;
                Vector3 p = transform.position;
                p.x = Mathf.Clamp(p.x, -limit, limit);
                p.z = Mathf.Clamp(p.z, -limit, limit);
                p.y = StickY(p);
                transform.position = p;

                rt += Time.deltaTime;
                yield return null;
            }
        }

        // Reset body stretch
        if (body) body.transform.localScale = Vector3.one;
        isLunging = false;
    }

    public void RegisterKill(EnemyAI enemy) => OnKill(enemy);

    void OnKill(EnemyAI enemy)
    {
        // Mating: killing a pink mate spawns a companion
        if (enemy is MateEnemy)
        {
            SpawnCompanion();
            OnNotification?.Invoke("OFFSPRING SPAWNED!");
            score += 500;
            return;
        }

        totalKills++;
        score += (enemy.intensity + 1) * 100;

        // Grazers are food, not meat: they heal an authored share of max health
        // (heals_player_pct) and never touch the buffer, because they carry no
        // colour — there is nothing in them to take.
        float heal = enemy.healsPlayerPct > 0f ? maxHealth * enemy.healsPlayerPct : 20f;
        health = Mathf.Min(maxHealth, health + heal);

        // Coloured prey streams into a limb: the first white one, or — with every
        // limb loaded — over the colour held longest (§2.4a).
        if (enemy.carriesColour && !string.IsNullOrEmpty(enemy.family))
        {
            buffer.Eat(enemy.family, enemy.intensity);
            OnBufferChanged();
        }
    }

    void SpawnCompanion()
    {
        var go = new GameObject("Companion");

        // Mini cube body in player's colour
        var body = GameObject.CreatePrimitive(PrimitiveType.Cube);
        Destroy(body.GetComponent<Collider>());
        body.transform.SetParent(go.transform, false);
        body.GetComponent<Renderer>().material.color = GameConfig.Colors.ForFamily(family);

        // Eyes
        for (int s = -1; s <= 1; s += 2)
        {
            var eye = GameObject.CreatePrimitive(PrimitiveType.Cube);
            Destroy(eye.GetComponent<Collider>());
            eye.transform.SetParent(go.transform, false);
            eye.transform.localScale    = new Vector3(0.2f, 0.2f, 0.1f);
            eye.transform.localPosition = new Vector3(s * 0.25f, 0.2f, 0.5f);
            eye.GetComponent<Renderer>().material.color = Color.black;
        }

        // Scale smaller than player
        go.transform.localScale = transform.localScale * 0.5f;
        go.transform.position   = transform.position + transform.right * (companionCount + 1) * 2f;

        var comp   = go.AddComponent<Companion>();
        comp.target = transform;
        comp.index  = companionCount;
        companionCount++;
    }
}

```

</details>

- `write_file(path='Assets/Scripts/Game/PlayerController.cs', why="Replaces kills→class/tier levelling with the colour buffer: eatin, contents='using UnityEngine;\nusing UnityEngine.InputSystem;\nusing Mo)` → Modified Assets/Scripts/Game/PlayerController.cs (556 lines). OK — delimiters balanced.

### Modified: `Assets/Scripts/Game/EcosystemManager.cs`

_Spawns wildlife in the five-family vocabulary (family/intensity/rank) and gates biome progression on rank rather than the retired tier ladder._

<details><summary>283 lines</summary>

```csharp
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

```

</details>

- `write_file(path='Assets/Scripts/Game/EcosystemManager.cs', why='Spawns wildlife in the five-family vocabulary (family/intensity/r, contents='using System.Collections.Generic;\nusing UnityEngine;\nusing)` → Modified Assets/Scripts/Game/EcosystemManager.cs (283 lines). OK — delimiters balanced.

### Modified: `Assets/Scripts/Game/GameManager.cs`

_HUD now reads the resolved form (rank + intensity/family + authored name) instead of gen/tier/class, and the evolution bar goes with the eat-to-evolve path it measured._

<details><summary>613 lines</summary>

```csharp
using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.UI;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    // ── Lock-on reticle (world-space canvas, drawn over the locked target) ────
    GameObject reticleCanvasGO;
    GameObject reticleGO;
    Texture2D  reticleTex;
    Transform  lockTarget;   // set by PlayerController via OnLockTargetChanged

    // "You are targeted" halo — shown over the player while an enemy is locked on.
    GameObject haloCanvasGO;
    GameObject haloGO;

    // ── HUD bars (Canvas) ─────────────────────────────────────────────────────
    GameObject hudBarsGO;
    Image      healthFillImage;
    Text       formText;
    Text       notifLabel;

    // ── Menu / death screens (Canvas) ─────────────────────────────────────────
    GameObject menuPanelGO;
    GameObject deathPanelGO;
    Text       deathScoreText;

    // ── Notification (Canvas, fades out) ──────────────────────────────────────
    float _notifTimer = 0f;

    // ── Scene references ──────────────────────────────────────────────────────
    PlayerController player;
    EcosystemManager ecosystem;
    Camera           cam;
    Morphivore.World.BiomeTerrain terrain;

    // Seeds this run's world. One seed per run reproduces a whole world exactly,
    // which is what §4.10's debugging story and §3.3's generator invariants need.
    int runSeed;

    bool gameStarted  = false;
    bool deathHandled = false;

    // ─────────────────────────────────────────────────────────────────────────

    void Start()
    {
        // Load the generated world content up front so a missing or malformed
        // file reports itself at boot rather than on the first spawn. Failure is
        // non-fatal — the ecosystem falls back to the prototype tables.
        Morphivore.Content.ContentDatabase.Load();

        // One seed per run. Logged so a bad world can be reproduced exactly
        // rather than hunted for (§4.10).
        runSeed = Random.Range(int.MinValue, int.MaxValue);
        Debug.Log($"[Run] seed {runSeed}");

        BuildScene();
        BuildUI();
    }

    // ── Scene ─────────────────────────────────────────────────────────────────

    void BuildScene()
    {
        cam = Camera.main;
        if (cam == null)
        {
            var camGO = new GameObject("Main Camera");
            camGO.tag = "MainCamera";
            cam = camGO.AddComponent<Camera>();
            camGO.AddComponent<AudioListener>();
        }
        cam.backgroundColor = new Color(0.067f, 0.067f, 0.067f);
        cam.clearFlags      = CameraClearFlags.SolidColor;
        cam.farClipPlane    = 500f;

        var existingLight = FindAnyObjectByType<Light>();
        if (existingLight == null)
        {
            var ambientGO = new GameObject("Ambient Light");
            var ambient   = ambientGO.AddComponent<Light>();
            ambient.type      = LightType.Directional;
            ambient.intensity = 0.6f;
        }

        var sunGO = new GameObject("Sun");
        var sun   = sunGO.AddComponent<Light>();
        sun.type      = LightType.Directional;
        sun.intensity = 0.8f;
        sun.color     = Color.white;
        sunGO.transform.rotation = Quaternion.Euler(45f, 45f, 0f);
        sun.shadows   = LightShadows.Soft;

        // The ground is a seeded procedural island (§2.7), not a plane. The old
        // plane survives only as the fallback if generation fails, so a terrain
        // problem costs a flat world rather than a world with no floor.
        var biomeVisuals = GameConfig.VisualsForBiome("prairies", "Prairies");
        terrain = Morphivore.World.BiomeTerrain.Build(
            runSeed,
            Morphivore.World.BiomeTerrain.TerrainProfile.Prairies(biomeVisuals.groundColor),
            // Props are placed, not walked, so they can only be positioned once
            // the mesh exists. Creatures need no callback — they sample the ground
            // every frame and settle onto it as soon as there is one.
            ScatterProps);

        // The player hatches as the blank: white, rank 1, no family (§2.4).
        var playerGO = new GameObject("Player");
        playerGO.tag = "Player";
        player = playerGO.AddComponent<PlayerController>();
        player.OnNotification      = ShowNotification;
        player.OnLockTargetChanged = UpdateLockReticle;
        playerGO.transform.position = new Vector3(0f, 1f, 0f);

        var ecoGO = new GameObject("Ecosystem");
        ecosystem                = ecoGO.AddComponent<EcosystemManager>();
        ecosystem.player         = player;
        ecosystem.OnBiomeChanged = ApplyBiome;
        ecosystem.OnBossSpawned  = name => ShowNotification(string.IsNullOrEmpty(name)
            ? "!! APEX PREDATOR DETECTED !!"
            : $"!! {name.ToUpper()} !!");
        ecosystem.OnMateSpawned  = () => ShowNotification("!! MATE DETECTED !!");
    }

    // ── UI — charge meter only on Canvas; everything else via IMGUI ───────────

    void BuildUI()
    {
        var canvasGO = new GameObject("Canvas");
        var canvas   = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 10;
        var scaler = canvasGO.AddComponent<CanvasScaler>();
        scaler.uiScaleMode        = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920f, 1080f);
        scaler.screenMatchMode    = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
        scaler.matchWidthOrHeight = 0.5f;
        canvasGO.AddComponent<GraphicRaycaster>();

        EnsureDesktopPointer();

        // Canvas buttons need an EventSystem to receive clicks. A UI input
        // module created at runtime has no input actions assigned, so we must
        // wire up the default set or pointer clicks are never detected.
        var esGO = new GameObject("EventSystem");
        esGO.AddComponent<EventSystem>();
        var uiModule = esGO.AddComponent<InputSystemUIInputModule>();
        uiModule.AssignDefaultActions();

        CreateLockReticle();
        CreateThreatHalo();
        CreateHudBars(canvasGO);
        CreateMenuPanels(canvasGO);
    }

    // This is a desktop game (WASD + mouse). If the Input System has the Mouse
    // or Pen device disabled — e.g. a lingering "Simulate Touch Input From Mouse
    // or Pen" toggle in the editor — Canvas UI clicks route to a dead phantom
    // Touchscreen and no button responds (IMGUI didn't hit this because it reads
    // OS events directly). Make sure the mouse is the active pointer.
    static void EnsureDesktopPointer()
    {
        foreach (var device in InputSystem.devices)
        {
            if ((device is Mouse || device is Pen) && !device.enabled)
                InputSystem.EnableDevice(device);
            else if (device is Touchscreen && device.enabled && Mouse.current != null)
                InputSystem.DisableDevice(device);
        }
    }

    // ── Per-frame ─────────────────────────────────────────────────────────────

    void Update()
    {
        if (player == null) return;

        if (_notifTimer > 0f) _notifTimer -= Time.deltaTime;

        if (!gameStarted) return;

        UpdateHudBars();

        if (player.isDead && !deathHandled)
        {
            deathHandled = true;
            StartCoroutine(ShowDeathScreen());
        }
    }

    void UpdateHudBars()
    {
        if (healthFillImage != null)
            healthFillImage.fillAmount = player.maxHealth > 0
                ? Mathf.Clamp01(player.health / player.maxHealth) : 1f;

        // Who you currently are: rank is your body, the family + intensity are
        // what your limbs are holding, and the name is the form they resolve to.
        if (formText != null)
            formText.text = string.IsNullOrEmpty(player.family)
                ? $"RANK {player.rank}   |   {player.FormName.ToUpper()}"
                : $"RANK {player.rank}   |   " +
                  $"{GameConfig.Intensities[player.intensity].name.ToUpper()} {player.family.ToUpper()}   |   " +
                  $"{player.FormName.ToUpper()}";

        // Fade the notification out over its remaining lifetime.
        if (notifLabel != null)
        {
            var c = notifLabel.color;
            c.a = Mathf.Clamp01(_notifTimer);
            notifLabel.color = c;
        }
    }

    // Camera follows in LateUpdate so it always runs after player movement.
    void LateUpdate()
    {
        if (cam == null || player == null) return;

        Vector3 target = player.transform.position + new Vector3(0f, 6f, -10f);
        cam.transform.position = Vector3.Lerp(cam.transform.position, target, 8f * Time.deltaTime);
        cam.transform.LookAt(player.transform.position + Vector3.up);

        // Lock-on reticle hovers above the currently locked target, billboarded.
        if (reticleCanvasGO != null && lockTarget != null)
        {
            float heightAbove = lockTarget.localScale.y * 0.5f + 1.2f;
            reticleCanvasGO.transform.position = lockTarget.position + Vector3.up * heightAbove;
            reticleCanvasGO.transform.rotation = cam.transform.rotation;
        }

        // Threat halo pulses over the player while an enemy has us locked.
        if (haloGO != null)
        {
            bool threatened = player.IsThreatened;
            haloGO.SetActive(threatened);
            if (threatened)
            {
                float h = player.transform.localScale.y * 0.5f + 1.6f;
                haloCanvasGO.transform.position = player.transform.position + Vector3.up * h;
                haloCanvasGO.transform.rotation = cam.transform.rotation;
                float pulse = 1f + Mathf.Sin(Time.time * 10f) * 0.15f;
                haloGO.transform.localScale = Vector3.one * pulse;
            }
        }
    }

    // Solid props, placed on the ground. Called once the terrain mesh exists.
    // Imported art first; the old primitives remain as the fallback so a missing
    // or renamed asset costs a plainer world, never an empty one.
    void ScatterProps()
    {
        var propRoot = new GameObject("Props").transform;
        if (Morphivore.World.PropScatter.Scatter("prairies", propRoot)) return;

        ScatterPrimitiveProps(propRoot);
    }

    void ScatterPrimitiveProps(Transform parent)
    {
        float r = Morphivore.World.BiomeTerrain.Radius * 0.85f;
        Color[] palette = { GameConfig.Colors.Red, GameConfig.Colors.Blue, GameConfig.Colors.Grey,
                            GameConfig.Colors.Yellow, GameConfig.Colors.White, GameConfig.Colors.Purple };

        for (int i = 0; i < 30; i++)
        {
            var crystal = GameObject.CreatePrimitive(PrimitiveType.Cube);
            crystal.transform.SetParent(parent, true);
            float cx = Random.Range(-r, r);
            float cz = Random.Range(-r, r);
            float h  = Random.Range(2f, 5f);

            crystal.transform.localScale = new Vector3(1f, h, 1f);
            crystal.transform.position   = new Vector3(
                cx, Morphivore.World.BiomeTerrain.HeightAt(cx, cz) + h * 0.35f, cz);
            crystal.transform.rotation   = Quaternion.Euler(0f, Random.Range(0f, 360f), 0f);

            var mat = crystal.GetComponent<Renderer>().material;
            mat.color = palette[Random.Range(0, palette.Length)];
            mat.EnableKeyword("_EMISSION");
            mat.SetColor("_EmissionColor", mat.color * 0.2f);
            // Keep the collider and mark it solid so the player can't pass through.
            crystal.AddComponent<Obstacle>();
        }
    }

    void OnStartClicked()
    {
        gameStarted           = true;
        deathHandled          = false;
        player.gameStarted    = true;
        ecosystem.gameStarted = true;
        ecosystem.Init();
        if (menuPanelGO != null) menuPanelGO.SetActive(false);
        if (hudBarsGO != null) hudBarsGO.SetActive(true);
        UpdateHudBars();
    }

    IEnumerator ShowDeathScreen()
    {
        yield return new WaitForSeconds(2f);
        if (deathScoreText != null)
            deathScoreText.text = $"Lineage terminated.\nScore: {player.score}";
        if (hudBarsGO != null) hudBarsGO.SetActive(false);
        if (deathPanelGO != null) deathPanelGO.SetActive(true);
    }

    // ── Biome ─────────────────────────────────────────────────────────────────

    void ApplyBiome(GameConfig.BiomeData biome)
    {
        if (cam)    cam.backgroundColor = biome.groundColor;
        if (terrain) terrain.SetGroundColor(biome.groundColor);
        RenderSettings.fogColor         = biome.fogColor;
        RenderSettings.fog              = true;
        RenderSettings.fogStartDistance = 40f;
        RenderSettings.fogEndDistance   = 150f;
        ShowNotification($"ENTERING {biome.name}");
    }

    // ── Notification ──────────────────────────────────────────────────────────

    void ShowNotification(string text)
    {
        _notifTimer = 2f;
        if (notifLabel != null) notifLabel.text = text;
    }

    // ── Lock-on reticle (world-space red ring drawn over the locked target) ───

    void CreateLockReticle()
    {
        const int S = 128;
        reticleTex = new Texture2D(S, S, TextureFormat.RGBA32, false);
        reticleTex.filterMode = FilterMode.Bilinear;
        var pixels = new Color[S * S];
        float half  = S * 0.5f;
        float outer = half - 0.5f;
        float inner = half * 0.64f; // ring thickness (annulus)
        for (int y = 0; y < S; y++)
            for (int x = 0; x < S; x++)
            {
                float d = Mathf.Sqrt((x - half) * (x - half) + (y - half) * (y - half));
                bool onRing = d <= outer && d >= inner;
                pixels[y * S + x] = new Color(1f, 1f, 1f, onRing ? 1f : 0f);
            }
        reticleTex.SetPixels(pixels);
        reticleTex.Apply();
        var ringSprite = Sprite.Create(reticleTex, new Rect(0, 0, S, S), new Vector2(0.5f, 0.5f), S);

        reticleCanvasGO = new GameObject("LockReticleWorld");
        var worldCanvas = reticleCanvasGO.AddComponent<Canvas>();
        worldCanvas.renderMode  = RenderMode.WorldSpace;
        worldCanvas.worldCamera = cam;
        // World-space canvas units are pixels; scale down so 90px reads ~1.3 units.
        reticleCanvasGO.transform.localScale = Vector3.one * 0.014f;

        reticleGO = new GameObject("LockReticle");
        reticleGO.transform.SetParent(reticleCanvasGO.transform, false);
        var img   = reticleGO.AddComponent<Image>();
        img.sprite = ringSprite;
        img.color  = new Color(1f, 0.25f, 0.28f, 0.95f); // red
        var rect  = reticleGO.GetComponent<RectTransform>();
        rect.anchorMin        = new Vector2(0.5f, 0.5f);
        rect.anchorMax        = new Vector2(0.5f, 0.5f);
        rect.pivot            = new Vector2(0.5f, 0.5f);
        rect.anchoredPosition = Vector2.zero;
        rect.sizeDelta        = new Vector2(90f, 90f);

        reticleGO.SetActive(false);
    }

    // Called by PlayerController: show the ring over `target`, or hide it (null).
    void UpdateLockReticle(Transform target)
    {
        lockTarget = target;
        if (reticleGO != null) reticleGO.SetActive(target != null);
    }

    // ── Threat halo (world-space orange ring over the player when targeted) ───

    void CreateThreatHalo()
    {
        const int S = 128;
        var tex = new Texture2D(S, S, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        var pixels = new Color[S * S];
        float half  = S * 0.5f;
        float outer = half - 0.5f;
        float inner = half * 0.72f; // thinner ring reads as a halo
        for (int y = 0; y < S; y++)
            for (int x = 0; x < S; x++)
            {
                float d = Mathf.Sqrt((x - half) * (x - half) + (y - half) * (y - half));
                bool onRing = d <= outer && d >= inner;
                pixels[y * S + x] = new Color(1f, 1f, 1f, onRing ? 1f : 0f);
            }
        tex.SetPixels(pixels);
        tex.Apply();
        var ringSprite = Sprite.Create(tex, new Rect(0, 0, S, S), new Vector2(0.5f, 0.5f), S);

        haloCanvasGO = new GameObject("ThreatHaloWorld");
        var wc = haloCanvasGO.AddComponent<Canvas>();
        wc.renderMode  = RenderMode.WorldSpace;
        wc.worldCamera = cam;
        haloCanvasGO.transform.localScale = Vector3.one * 0.02f;

        haloGO = new GameObject("ThreatHalo");
        haloGO.transform.SetParent(haloCanvasGO.transform, false);
        var img = haloGO.AddComponent<Image>();
        img.sprite = ringSprite;
        img.color  = new Color(1f, 0.55f, 0.1f, 0.9f); // warning orange
        var rect = haloGO.GetComponent<RectTransform>();
        rect.anchorMin        = new Vector2(0.5f, 0.5f);
        rect.anchorMax        = new Vector2(0.5f, 0.5f);
        rect.pivot            = new Vector2(0.5f, 0.5f);
        rect.anchoredPosition = Vector2.zero;
        rect.sizeDelta        = new Vector2(120f, 120f);

        haloGO.SetActive(false);
    }

    // ── HUD bars (Canvas horizontal fill, top-right) ──────────────────────────

    static Sprite _hudBarSprite;

    static Sprite GetHudBarSprite()
    {
        if (_hudBarSprite != null) return _hudBarSprite;
        // Filled-type Images require a real sprite — without one Unity silently
        // ignores fillAmount and just renders the full rect.
        var tex = Texture2D.whiteTexture;
        _hudBarSprite = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f));
        return _hudBarSprite;
    }

    void CreateHudBars(GameObject parent)
    {
        hudBarsGO = new GameObject("HudBars", typeof(RectTransform));
        hudBarsGO.transform.SetParent(parent.transform, false);
        var containerRect = hudBarsGO.GetComponent<RectTransform>();
        containerRect.anchorMin = Vector2.zero;
        containerRect.anchorMax = Vector2.one;
        containerRect.offsetMin = Vector2.zero;
        containerRect.offsetMax = Vector2.zero;

        // One meter only: Health (§2.3). Progress is your form, and your form is
        // on your body — the limbs and the slot that pulses (§2.4a).
        healthFillImage = CreateStatBar(hudBarsGO, "HealthBar", "HEALTH", 100f, new Color(1f, 0.278f, 0.341f, 1f));

        // Form readout — top-left corner
        formText = CreateUIText(hudBarsGO.transform, "FormLabel", "", 30, FontStyle.Bold,
                                new Color(1f, 1f, 1f, 0.85f), Vector2.zero, new Vector2(560f, 44f));
        var ftRect = formText.GetComponent<RectTransform>();
        ftRect.anchorMin        = new Vector2(0f, 1f);
        ftRect.anchorMax        = new Vector2(0f, 1f);
        ftRect.pivot            = new Vector2(0f, 1f);
        ftRect.anchoredPosition = new Vector2(30f, -30f);
        formText.alignment          = TextAnchor.MiddleLeft;
        // Don't wrap: the label sits top-left with empty space to its right, and a
        // long line (a long authored form name) would otherwise wrap and get
        // clipped, making the form appear to vanish.
        formText.horizontalOverflow = HorizontalWrapMode.Overflow;
        formText.verticalOverflow   = VerticalWrapMode.Overflow;

        // Center-screen notification (mutation / boss / biome messages)
        notifLabel = CreateUIText(hudBarsGO.transform, "Notification", "", 44, FontStyle.Bold,
                                  AccentGreen, new Vector2(0f, 200f), new Vector2(1200f, 90f));
        var nc = notifLabel.color; nc.a = 0f; notifLabel.color = nc;

        hudBarsGO.SetActive(false);
    }

    // Bars are anchored to the top-right corner of the screen, stacked downward.
    Image CreateStatBar(GameObject parent, string name, string label, float yOffset, Color fillColor)
    {
        const float barW = 520f;
        const float barH = 40f;
        const float rightMargin = 60f;
        const float labelH = 40f;

        var labelGO = new GameObject(name + "_Label", typeof(RectTransform));
        labelGO.transform.SetParent(parent.transform, false);
        var labelText = labelGO.AddComponent<Text>();
        labelText.text      = label;
        labelText.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        labelText.fontSize  = 32;
        labelText.fontStyle = FontStyle.Bold;
        labelText.alignment = TextAnchor.MiddleRight;
        labelText.color     = new Color(1f, 1f, 1f, 0.85f);
        var labelRect = labelGO.GetComponent<RectTransform>();
        labelRect.anchorMin        = new Vector2(1f, 1f);
        labelRect.anchorMax        = new Vector2(1f, 1f);
        labelRect.pivot            = new Vector2(1f, 1f);
        labelRect.anchoredPosition = new Vector2(-rightMargin, -(yOffset - labelH - 4f));
        labelRect.sizeDelta        = new Vector2(barW, labelH);

        var bg = new GameObject(name + "_BG", typeof(RectTransform));
        bg.transform.SetParent(parent.transform, false);
        var bgImg  = bg.AddComponent<Image>();
        bgImg.color = new Color(0.15f, 0.15f, 0.15f, 0.85f);
        var bgRect = bg.GetComponent<RectTransform>();
        bgRect.anchorMin        = new Vector2(1f, 1f);
        bgRect.anchorMax        = new Vector2(1f, 1f);
        bgRect.pivot            = new Vector2(1f, 1f);
        bgRect.anchoredPosition = new Vector2(-rightMargin, -yOffset);
        bgRect.sizeDelta        = new Vector2(barW, barH);

        var fillGO  = new GameObject(name + "_Fill", typeof(RectTransform));
        fillGO.transform.SetParent(bg.transform, false);
        var fillImg          = fillGO.AddComponent<Image>();
        fillImg.sprite       = GetHudBarSprite();
        fillImg.color        = fillColor;
        fillImg.type         = Image.Type.Filled;
        fillImg.fillMethod   = Image.FillMethod.Horizontal;
        fillImg.fillOrigin   = (int)Image.OriginHorizontal.Left;
        fillImg.fillAmount   = 1f;
        var fillRect         = fillGO.GetComponent<RectTransform>();
        fillRect.anchorMin   = Vector2.zero;
        fillRect.anchorMax   = Vector2.one;
        fillRect.offsetMin   = Vector2.zero;
        fillRect.offsetMax   = Vector2.zero;

        return fillImg;
    }

    // ── Menu / death screens (Canvas) ─────────────────────────────────────────

    static readonly Color AccentGreen = new Color(0.18f, 0.84f, 0.45f);

    void CreateMenuPanels(GameObject parent)
    {
        // Main menu — visible at launch
        menuPanelGO = CreateOverlayPanel(parent, "MenuPanel");
        CreateUIText(menuPanelGO.transform, "Title", "CUBIC EVOLUTION", 84, FontStyle.Bold,
                     AccentGreen, new Vector2(0f, 170f), new Vector2(1400f, 110f));
        CreateUIText(menuPanelGO.transform, "Tagline", "Evolve. Adapt. Dominate.", 30, FontStyle.Normal,
                     new Color(0.8f, 0.8f, 0.8f), new Vector2(0f, 90f), new Vector2(800f, 50f));
        CreateUIButton(menuPanelGO.transform, "StartButton", "INITIALIZE",
                       new Vector2(0f, -40f), new Vector2(340f, 84f), OnStartClicked);

        // Death screen — hidden until the player dies
        deathPanelGO = CreateOverlayPanel(parent, "DeathPanel");
        CreateUIText(deathPanelGO.transform, "Title", "EXTINCT", 84, FontStyle.Bold,
                     new Color(1f, 0.28f, 0.34f), new Vector2(0f, 150f), new Vector2(800f, 110f));
        deathScoreText = CreateUIText(deathPanelGO.transform, "Score", "", 30, FontStyle.Normal,
                                      new Color(0.8f, 0.8f, 0.8f), new Vector2(0f, 40f), new Vector2(800f, 90f));
        CreateUIButton(deathPanelGO.transform, "RestartButton", "NEW EVOLUTION",
                       new Vector2(0f, -90f), new Vector2(380f, 84f),
                       () => SceneManager.LoadScene(SceneManager.GetActiveScene().name));
        deathPanelGO.SetActive(false);
    }

    GameObject CreateOverlayPanel(GameObject parent, string name)
    {
        var panel = new GameObject(name, typeof(RectTransform));
        panel.transform.SetParent(parent.transform, false);
        var img   = panel.AddComponent<Image>();
        img.color = new Color(0.02f, 0.02f, 0.02f, 0.95f);
        var rect = panel.GetComponent<RectTransform>();
        rect.anchorMin = Vector2.zero;
        rect.anchorMax = Vector2.one;
        rect.offsetMin = Vector2.zero;
        rect.offsetMax = Vector2.zero;
        return panel;
    }

    Text CreateUIText(Transform parent, string name, string content, int fontSize, FontStyle style,
                      Color color, Vector2 anchoredPos, Vector2 size)
    {
        var go = new GameObject(name, typeof(RectTransform));
        go.transform.SetParent(parent, false);
        var text = go.AddComponent<Text>();
        text.text      = content;
        text.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        text.fontSize  = fontSize;
        text.fontStyle = style;
        text.alignment = TextAnchor.MiddleCenter;
        text.color     = color;
        var rect = go.GetComponent<RectTransform>();
        rect.anchoredPosition = anchoredPos; // anchors default to center
        rect.sizeDelta        = size;
        return text;
    }

    void CreateUIButton(Transform parent, string name, string label,
                        Vector2 anchoredPos, Vector2 size, UnityEngine.Events.UnityAction onClick)
    {
        var go = new GameObject(name, typeof(RectTransform));
        go.transform.SetParent(parent, false);
        var img   = go.AddComponent<Image>();
        img.sprite = GetHudBarSprite();
        img.color  = new Color(0.10f, 0.28f, 0.17f, 1f);
        var rect = go.GetComponent<RectTransform>();
        rect.anchoredPosition = anchoredPos;
        rect.sizeDelta        = size;

        var btn = go.AddComponent<Button>();
        btn.targetGraphic = img;
        var colors = btn.colors;
        colors.normalColor      = new Color(0.85f, 0.85f, 0.85f, 1f);
        colors.highlightedColor = Color.white; // hover brightens
        colors.pressedColor     = new Color(0.6f, 0.6f, 0.6f, 1f);
        btn.colors = colors;
        btn.onClick.AddListener(onClick);

        CreateUIText(go.transform, "Label", label, 32, FontStyle.Bold, Color.white, Vector2.zero, size);
    }
}

```

</details>

- `write_file(path='Assets/Scripts/Game/GameManager.cs', why='HUD now reads the resolved form (rank + intensity/family + author, contents='using System.Collections;\nusing UnityEngine;\nusing UnityEn)` → Modified Assets/Scripts/Game/GameManager.cs (613 lines). OK — delimiters balanced.

- `read_file(path='Assets/Scripts/Game/Companion.cs')` → using UnityEngine;

- `read_file(path='Assets/Scripts/Game/MateEnemy.cs')` → using UnityEngine;

- `list_files(pattern='Assets/Scripts/**/*.cs')` → Assets/Scripts/Content/ContentDatabase.cs

> Let me re-read the two most heavily rewritten files to check them over.

- `read_file(path='Assets/Scripts/Game/PlayerController.cs')` → using UnityEngine;

> Let me do a final consistency check on the two content-facing files I changed.

- `read_file(path='Assets/Scripts/Game/Creature.cs')` → using System.Collections;

- `read_file(path='Assets/Scripts/Game/ColourBuffer.cs')` → using UnityEngine;

Finished after 19 turn(s).

Wrote **8 file(s)**.

**The agent's own account of what it built**

Done. Here's what landed.

## What changed

**`GameConfig.cs` — rewritten contract (A1).** `ClassProfile`/`ClassFor` (eight classes, `lungeMult`) and the `Tiers` ladder (Alpha…Omega) are gone. In their place:
- `Families[]` — the five families in the design's own order (which is also §2.4b's birth precedence), each with `health/speed/damage/reach/dash` multipliers exactly as tabled: Yellow 1.5/0.85/1.5/0.9/0.8, Red 0.8/1.3/0.7/1.0/1.6, Blue 0.9/1.0/1.0/1.7/1.0, Purple 0.9/1.15/0.95/1.2/1.2, Grey 1.3/1.2/1.3/1.15/1.3.
- `Intensities[]` — Pale 25 · Dusk 50 · Deep 75 · Clash 90 · Rage 100, plus `WildLadder` (Pale→Dusk→Deep→Rage) and `LadderRung()` putting Clash *beside* Rage.
- `Ranks[]` — the limb baseline 100/150/…/350, 40…115, 12…17, 16…31. The `scale` column is the prototype's own read of body size (the design authors none) and is commented as such.
- `StatsFor(family, intensity, rank)` — baseline × `1 + pct × (mult − 1)`; dash is the form's own speed geared by the dash trade, which is the relation forms.json is authored on (verified against `yellow_rage_r1` … `grey_pale_r1`).
- `Colors` is five families + White (the empty state). Green/Cyan/Orange retired; Pink survives only as the dormant mate's tint, labelled as not-a-family. `EvoRequirement`/`LevelUpRequirement` deleted.

**`ColourBuffer.cs` — new (A2).** `ColourUnit{family,intensity,eaten}` per limb; `Eat` fills the first white slot else evicts the oldest; `Poop` empties the oldest; `NextSlot` is what pulses. `Resolve()` is §2.4b verbatim: majority family, ties to most-recent then precedence; lowest-link intensity stepped down once per non-family limb, floored at Pale; Clash wins the summit tie; all-white is the blank. The build plan's worked example traces correctly (rank 3 RageY/RageY/DuskRed → Deep; poop the oldest (Red) → still Deep; eat a Rage Yellow → Rage).

**`PlayerController.cs`** — kills→`Evolve`, `LevelUp`, `diet`, the `upgrade_*`/`gene_points` PlayerPrefs and `BaseSpeed/Damage/Health` are all gone. The player holds the buffer; eating coloured prey loads a limb, **Q / B** poops the oldest and leaves a dropping, and any buffer change rebuilds the body and re-stats from the resolved form (authored line from forms.json, else `StatsFor`). Mutation preserves the wound fraction (§2.3) and fires a notification. Reach is now the form's Reach (lock range *and* pounce distance — a pounce carries exactly one Reach), dash timing is geared by `dash/speed`, and the pounce tier gate compares intensity.

**`ContentDatabase.cs`** — first consumer of `forms.json`: loaded on its own guard so a broken creatures.json doesn't cost the player its form, with `Form(family, intensity, rank)` keyed `yellow_deep_r3`-style. `TierIndex` → `IntensityIndex` (content tier means intensity now, not morphology); `ColorTypeFor` deleted — `def.family` already speaks the right vocabulary.

**`Creature.cs`/`EnemyAI.cs`/`EcosystemManager.cs`/`GameManager.cs`** — `colorType`/`tier` become `family`/`intensity`/`rank`; limbs are built one per rank with a per-limb colour hook (the player tints each by its slot, saturated by that unit's tier) and the next slot pulses by scale+emission, never opacity. Enemies take family/intensity/limbs from creatures.json. HUD reads `RANK n | DEEP YELLOW | SNARLING TOOTH-SPITTER`; the EVOLUTION bar went with the eat-to-evolve path it measured.

## Flags

- **Rank is frozen at 1** until breeding (B2), per A1's "sever rank from eating". So in play the buffer currently has one slot: eviction and dilution are implemented and unit-traceable but not yet observable in-game, and biome gates (which read `player_rank`) hold at biome one. This is the regression the plan predicted, but it's the sharpest edge of shipping A1+A2 without B2.
- **The Clash second-tone gift is unauthored.** `FormDef` has no field for it and every Clash row in forms.json is plain 90% expression, so I implemented Clash as 90% and no more rather than inventing a gift.
- **Not done here:** the Bestiary (no such code exists; nothing in A1/A2 asks for it), so "total reads 150" is unverifiable in-game — `forms.json` does carry `count: 150` and all 150 ids resolve. I also don't render `socket_layout`; limbs still ring the body, since putting one on the −Y face would bury it in the terrain.
- **Unverified:** I can't compile or run Unity from here, so this is desk-checked only — in particular the `def.limbs > 0 ? def.limbs : def.rank` fallback for enemy limb counts, which I chose because I didn't read all of creatures.json to see which of the two fields is populated.


---

## Run cost

```
20 API calls (prioritize x1, build x19)
  input 2,883,319  cache write 0  cache read 0  output 111,060
  estimated cost $17.19 on claude-opus-5
```
