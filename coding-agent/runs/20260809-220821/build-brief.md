# Build brief

Implement the following chunk. It was selected by this agent's own gap analysis of the codebase against the design document.

## Five colour families and their stat multipliers  (GDD §2.4)

**The design requires:** Coloured creatures and player forms belong to one of five families — Yellow Brawler, Red Leaper, Blue Sniper, Purple Stalker, Grey Apex — each defined by multipliers on Health, Speed, Damage, Reach and Dash representing its full (Rage) expression.

**Working means:** Switching family visibly changes how the beast plays: a Yellow form carries the longest bar and hits hardest but is slowest; a Blue form strikes from far outside a Yellow's reach.

**Current state of the code:** CONTRADICTED — The colour→playstyle→multiplier area is definitely implemented, but on different rules than GDD 2.4. The live system is GameConfig.ClassFor / ClassProfile, which carries eight class names (Brawler, Bruiser, Leaper, Sniper, Skirmisher, Stalker, Apex, Forager) rather than the five families, and its axes are speedMult/damageMult/healthMult/lungeMult/dashMult — a `lungeMult` where the design demands `Reach`, so the Blue Sniper's defining long-reach trade cannot be expressed. GameConfig.Colors additionally enumerates nine colours (Green, Orange, Cyan, Pink, White) and Creature/EnemyAI still branch on "GREEN"/"CYAN", so colour identity is broader than the five families. Meanwhile the correct schema already exists but is dead: FormDef/StatBlock carry family, intensity, intensity_pct and exactly the five axes (health, damage, speed, reach, dash), and forms.json (132 KB) is explicitly unread by any code. ContentDatabase.ColorTypeFor does recognise the five family names, and WorldTables.cs mentions exactly those five (its body is unparsed, so it may already hold a family table — the inventory cannot confirm). Net: a parallel, differently-shaped class-multiplier system is in charge of gameplay stats, so this is a contradicted mechanism rather than a missing one.

**What exists instead:** An eight-class GameConfig.ClassProfile table (speed/damage/health/lunge/dash multipliers) selected by GameConfig.ClassFor from a nine-colour Colors palette, consumed by PlayerController (BaseSpeed/BaseDamage/BaseHealth/ClassName) and EnemyAI/Creature. The design-shaped five-axis family data (FormDef.family + StatBlock health/damage/speed/reach/dash in forms.json) is parsed-capable via FormTable.Load but nothing reads forms.json.

**This requires removing or rewriting existing code, not only adding to it.**

**Acceptance test from the design document:** Yellow 1.5/0.85/1.5/0.9/0.8; Red 0.8/1.3/0.7/1.0/1.6; Blue 0.9/1.0/1.0/1.7/1.0; Purple 0.9/1.15/0.95/1.2/1.2; Grey 1.3/1.2/1.3/1.15/1.3 (Health/Speed/Damage/Reach/Dash).

**Data it must read:** forms.json / creatures.json: family field; per-family multiplier set (Health, Speed, Damage, Reach, Dash)

## Limb baseline stat table  (GDD §2.4)

**The design requires:** Limb count (1–6) sets baseline Health, Damage, Speed and Reach before family and intensity multipliers apply.

**Working means:** Gaining a limb raises the raw bar most noticeably as durability, with speed creeping up only slightly.

**Current state of the code:** CONTRADICTED — The codebase clearly implements a baseline-stats-then-multiplier pipeline, but on a different axis than the design. Baselines come from single scalar constants (`PlayerController.BaseSpeed/BaseDamage/BaseHealth`) combined with a five-row tier progression (`GameConfig.Tiers` / `TierData{name, scale, limbs}` named Alpha…Omega, driven by `EvoRequirement`/`LevelUpRequirement` and `Creature.tier`), with `ClassProfile` mults applied on top. That is a rank/level ladder of 5 tiers where `limbs` is a cosmetic/derived field of the tier, not a 1–6 limb-count table that sets Health/Damage/Speed/Reach (100/150/200/250/300/350, 40/55/70/85/100/115, 12/13/14/15/16/17, 16/19/22/25/28/31). Nothing in the inventory shows a four-column, six-row baseline array, and Reach has no baseline at all — only `Ecology.ReachScale` as a global scalar. Notably, `FormTable.StatBlock{health,damage,speed,reach,dash}` and `FormDef.rank` are the right shape and `forms.json` (132 KB) exists, but the inventory marks forms.json as read by nothing, so the correct-shaped stat data is inert while the tier ladder drives play. Because the existing tier/level baseline would have to be replaced (not merely extended) to make limb count the baseline source, this is CONTRADICTED rather than ABSENT/UNCONSUMED, though the unconsumed forms.json is the second half of the story.

**What exists instead:** A 5-tier evolution ladder: `GameConfig.Tiers` of `TierData{name, scale, limbs}` (Alpha/Beta/Gamma/Delta/Omega) scaling a single set of flat constants (`PlayerController.BaseHealth/BaseDamage/BaseSpeed`) with no Reach baseline, then multiplied by `ClassProfile{healthMult, speedMult, damageMult, lungeMult, dashMult}`. A correctly-shaped `StatBlock{health,damage,speed,reach,dash}` and `FormDef.rank` exist in FormTable.cs but forms.json is never loaded.

**This requires removing or rewriting existing code, not only adding to it.**

**Acceptance test from the design document:** Health 100/150/200/250/300/350; Damage 40/55/70/85/100/115; Speed 12/13/14/15/16/17; Reach 16/19/22/25/28/31 for limbs 1→6.

**Data it must read:** Rank baseline table (limbs → Health/Damage/Speed/Reach)

## Final stat composition (rank baseline × family × intensity)  (GDD §2.4)

**The design requires:** A form's live stats are the limb baseline multiplied by the family multiplier scaled by intensity, producing the player's current Health max, Damage, Speed, Reach and Dash.

**Working means:** The HUD bar length and observable damage/speed change immediately and consistently when either rank or form changes; no colour is strictly best because Health is one of the multiplied axes.

**Current state of the code:** CONTRADICTED — The codebase does compose live stats, but by a different rule set than the design's rank-baseline × family × intensity formula. Player stats come from GameConfig.ClassProfile (speedMult/damageMult/healthMult/lungeMult/dashMult) selected by ClassFor plus GameConfig.Tiers (TierData with name/scale/limbs), and PlayerController exposes BaseSpeed/BaseDamage/BaseHealth/ClassName which it scales on Evolve/level-up. Nothing in the inventory holds the authoritative limb baseline table (Health 100/150/200/250/300/350, Damage 40..115, Speed 12..17, Reach 16..31), nor any intensity fraction (Pale 25% … Rage 100%) or Clash second-tone gift, nor a Dash axis on the player side. The form-side data model that the design implies does exist — FormDef carries family, intensity, intensity_pct, rank, socket_layout and a StatBlock with exactly health/damage/speed/reach/dash — but forms.json is explicitly unread, so FormTable is dead code and the eight named classes (Brawler, Bruiser, Leaper, Sniper, Skirmisher, Stalker, Apex, Forager) drive stats instead of family+intensity. The worked example (2-limb Rage Brawler vs 5-limb Pale Brawler) cannot be reproduced: 'Brawler' here is a class profile, not a Yellow family, and intensity has no effect anywhere. Because a competing stat pipeline occupies this area and would have to be replaced, this is CONTRADICTED rather than merely UNCONSUMED, though the unread forms.json is the accompanying symptom.

**What exists instead:** Stats are class-profile multipliers × tier: GameConfig.ClassProfile (speedMult/damageMult/healthMult/lungeMult/dashMult) chosen by ClassFor from eight archetype names, combined with GameConfig.Tiers/TierData (scale, limbs) and PlayerController's BaseSpeed/BaseDamage/BaseHealth adjusted on Evolve and upgrade_* picks. Enemies get stats via EnemyAI.ApplyContent / Creature.hasContentStats from creatures.json. FormTable/FormDef/StatBlock model the designed data but are never loaded.

**This requires removing or rewriting existing code, not only adding to it.**

**Acceptance test from the design document:** A 2-limb Rage Brawler and a 5-limb Pale Brawler are both Yellow and must produce clearly different stat lines from the same tables.

**Data it must read:** forms.json stat profile per form

## Intensity scaling of family multipliers  (GDD §2.4, 2.4b)

**The design requires:** An intensity tier scales each family multiplier's distance from 1.0: Pale 25%, Dusk 50%, Deep 75%, Clash ~90% plus a minor second-tone gift, Rage 100%. The Clash gift is authored per form.

**Working means:** A Pale Yellow form plays only slightly tougher and slower than the blank, while a Rage Yellow form expresses the full 1.5/0.85/1.5 trade; a Clash form shows near-full expression plus its authored second-tone bonus.

**Current state of the code:** UNCONSUMED — The data side of this requirement is fully present and already parsed in principle: FormDef carries `intensity` and `intensity_pct` plus a `StatBlock` (health, damage, speed, reach, dash) — exactly the hand-tuned, intensity-scaled profile the design calls for — and FormTable.Load exists to deserialise it. But the inventory states plainly that forms.json is read by nothing, so no runtime path resolves a form, reads its intensity_pct, or applies the scaled multipliers. Nothing in the inventory references a per-form Clash gift / second-tone bonus field at all (FormDef's field list has no such member), so even the data for the Clash exception looks unauthored in the schema. The only live multiplier mechanism is GameConfig.ClassProfile (speedMult/damageMult/healthMult/lungeMult/dashMult selected via ClassFor and applied in PlayerController), which is a flat per-class multiplier with no intensity dimension — it would have to be superseded or rewritten for form-driven stats. The tier words Pale/Dusk/Deep/Rage/Clash appear only in ContentDatabase's creature/spawn tier handling (TierIndex, ColorTypeFor), not in any stat computation. I cannot see method bodies, so I cannot rule out that some multiplication happens inside PlayerController.Evolve, but with forms.json unread there is no source of intensity_pct at runtime.

**What exists instead:** A flat class-profile multiplier system: GameConfig.ClassFor returns a ClassProfile (healthMult/speedMult/damageMult/dashMult/lungeMult) keyed by class name (Brawler, Leaper, Sniper, Stalker, Apex, ...), applied to PlayerController's BaseHealth/BaseSpeed/BaseDamage. Intensity tiers exist only as spawn-tier strings in ContentDatabase (TierIndex over Pale/Dusk/Deep/Rage/Clash). FormTable/FormDef/StatBlock model the intensity-scaled stats but are never loaded.

**This requires removing or rewriting existing code, not only adding to it.**

**Acceptance test from the design document:** Pale Yellow Health multiplier = 1 + 0.25×(1.5−1) = 1.125; Deep Yellow = 1.375; Rage Yellow = 1.5.

**Data it must read:** forms.json: intensity field, stat profile derived from the scaling rule (hand-tuned), per-form Clash gift

## forms.json — the 150 authored forms  (GDD §2.4b, 3.3)

**The design requires:** Exactly 150 forms are authored as family × intensity × rank (5 × 5 × 6), each with an authored name, socket layout and stat profile.

**Working means:** The Bestiary total reads 150, each rank opens a fresh 25-form column, and every reached form displays an authored name.

**Current state of the code:** UNCONSUMED — The authored asset exists at full size (forms.json, 132 KB) and a matching deserialisation schema exists in FormTable.cs whose FormDef fields line up almost exactly with the design's required columns (family, intensity, rank, name, socket_layout, stats, plus saturation/silhouette used by §2.4b's rendering rule) and FormTable even carries a `count` field for the 150 assertion. But the inventory's data-contract section states nothing reads forms.json: ContentDatabase.Load only pulls creatures.json and biomes.json, and no call site for FormTable.Load appears anywhere (no reference from ContentDatabase, GameManager, Creature, or EnemyAI). Runtime identity is instead driven by GameConfig.Tiers (five tier names Alpha..Omega with scale/limbs) and GameConfig.ClassFor/Colors, with Creature.tier/colorType/displayName and EnemyAI.contentId/role coming from creatures.json — a 5-tier × colour scheme, not a family × intensity × rank lattice of 150. There is also no Bestiary code at all (no 30-cell grid, no discovered/total header, no rank column), so the in-game observable cannot be checked. Because the inventory explicitly flags the asset as unread and a ready-made parser sits idle, UNCONSUMED is the precise verdict rather than ABSENT; the parallel tier system is a separate legacy path that this requirement would supersede rather than something already claiming to implement forms.

**What exists instead:** A complete, unused schema (FormTable/FormDef/StatBlock with family, intensity, rank, name, socket_layout, stats) alongside a live but different identity system: GameConfig.Tiers (5 named tiers with scale/limb counts), GameConfig.ClassFor/Colors profiles, and Creature/EnemyAI fields (tier, colorType, contentId, role) fed from creatures.json. No Bestiary UI of any kind.

**Acceptance test from the design document:** 5 families × 5 intensities × 6 ranks = 150 entries; 150 authored, 150 reachable.

**Data it must read:** forms.json: family, intensity, rank, authored name, socket layout, stat profile

## The colour buffer (FIFO limb slots)  (GDD §2.4a)

**The design requires:** Each limb holds exactly one colour unit (family + tier) or white; eating fills a white limb first, and if no limb is white the meal evicts the oldest colour, strictly FIFO.

**Working means:** With a white limb free, a meal loads that limb; with all limbs coloured, the next meal replaces the colour that has been held longest, never a newer one.

**Current state of the code:** CONTRADICTED — There is no per-limb colour slot collection anywhere in the inventory: no queue/buffer/slot/socket members, no white-slot or eviction logic, no 'oldest colour' concept, and no pulsing next-slot indicator (GameManager's UI strings cover health/evolution bars, lock reticle, threat halo, notifications only). Instead, the same design area — what eating does to your form — is implemented by a completely different mechanism: kills accumulate (RegisterKill, totalKills) against GameConfig.EvoRequirement/LevelUpRequirement to drive PlayerController.Evolve, which assigns a GameConfig.ClassProfile (Brawler/Leaper/Sniper/Apex/Forager, with speedMult/damageMult/healthMult multipliers) and a TierData (Alpha..Omega) whose 'limbs' field is a cosmetic count derived from tier, not a set of colour-bearing slots. Progression is further steered by discrete upgrade picks ("upgrade_damage", "upgrade_speed", "upgrade_health", "gene_points") — hidden-stat levelling rather than the visible, world-forced colour buffer. Colour is stored as a single scalar per creature (Creature.colorType / bodyColor / ContentDatabase.ColorTypeFor with Yellow/Red/Blue/Purple/Grey names) and EnemyAI.carriesColour is a flag, so prey colour has nowhere to be stored per limb. The data the requirement needs partly exists: FormTable/FormDef already models family + intensity + rank + socket_layout and forms.json (132 KB) is in StreamingAssets but nothing reads it — the table is present and unconsumed, so the family/tier vocabulary need not be authored from scratch.

**What exists instead:** A kills-threshold class/tier levelling system: RegisterKill -> EvoRequirement/LevelUpRequirement -> Evolve assigns a ClassProfile (stat multipliers) and TierData (scale + limb count), plus discrete gene_points upgrade picks (upgrade_damage/speed/health). Colour is one scalar per creature (colorType/bodyColor) used for tinting and enemy identity, not a per-limb buffer, and forms.json (family/intensity/rank/socket_layout) is present but unread.

**This requires removing or rewriting existing code, not only adding to it.**

**Data it must read:** Persisted run state: ordered list of limb slots, each {family, tier} or white, with insertion order

## Form resolution from buffer state  (GDD §2.4b)

**The design requires:** Every buffer state resolves deterministically to exactly one form: family = the colour holding the most limbs with ties broken toward the most recently eaten (at birth by fixed precedence Yellow→Red→Blue→Purple→Grey); intensity = the lowest tier among the family-colour units, stepped down one rung per limb not carrying the family, floored at Pale, along the wild ladder Pale→Dusk→Deep→Rage; Clash sits beside Rage as a parallel summit that any held Clash unit wins the tie for, and diluting Clash or Rage slides to Deep; all-white resolves to the blank.

**Working means:** Any combination of limb colours names one form on screen and never an invalid state; adding a weak unit to a strong monochrome body visibly drops the displayed intensity.

**Current state of the code:** CONTRADICTED — No symbol in the inventory represents a buffer state (a per-limb colour/tier list) or a resolution function over it: there is no majority-colour family computation, no recency tiebreak, no birth precedence Yellow→Red→Blue→Purple→Grey, no lowest-link intensity step-down, no Pale floor, no Clash-beside-Rage summit rule, and no all-white blank. Creature stores a single scalar `colorType`/`bodyColor` plus an int `tier`, not six coloured sockets. What does exist in this area is a wholly different identity mechanism: the player's displayed identity is a class profile chosen by `GameConfig.ClassFor` plus a rank/tier advanced by kill count (`RegisterKill`, `totalKills`, `level`, `Evolve`, `GameConfig.Tiers` Alpha…Omega with scale/limbs, and stat upgrade strings `upgrade_damage`/`upgrade_speed`/`upgrade_health`, `gene_points`). That progression-by-kills model must be replaced by resolution-from-buffer, so this is a contradiction rather than a mere absence. The authored 150-form table is already modelled and parseable (`FormDef` carries family, intensity, intensity_pct, rank, silhouette, socket_layout; `FormTable.Load` exists), but forms.json is explicitly unread, so the lookup half is dead code awaiting the resolver. The inventory cannot show whether `ContentDatabase.TierIndex` orders the wild ladder correctly, so that part is low-confidence — but it is used for content spawn tiers, not for player form resolution.

**What exists instead:** Identity is derived from kill-count progression and a colour→class table: `PlayerController.RegisterKill`/`Evolve`/`level` with `GameConfig.ClassFor`, `ClassProfile` multipliers and `Tiers` (Alpha…Omega, each with scale and limb count), while `Creature` holds one `colorType`/`bodyColor` and an int `tier`. Prey merely expose `carriesColour` (EnemyAI) with no buffer to accumulate into. The 150 authored forms exist as data (`forms.json`) and a matching `FormDef`/`FormTable` parser, but nothing reads the file, so no form is ever named on screen.

**This requires removing or rewriting existing code, not only adding to it.**

## These ship together

R013 tops the list because it sits at the junction of the whole stat system: 26 downstream items wait on it, its severity is high, and its effort is only medium because the correct data shape (FormDef/StatBlock with health/damage/speed/reach/dash, plus ContentDatabase.ColorTypeFor already knowing the five family names) is already written — it is dead, not missing. The verdict is CONTRADICTED, which is the important part: GameConfig.ClassFor/ClassProfile is not an incomplete version of the design, it is a different design (eight classes, and a lungeMult where the GDD demands Reach) currently in charge of every live stat. Nothing built on top of the family model can be correct while a second, differently-axed multiplier table is the one PlayerController actually reads. Removing that competing pipeline is the unlock, and it has to happen before R014, R016, R018 or anything else in the 2.4 cluster can be evaluated against reality.

Do not land one without the other — R015 and R016 are not really 'runners-up' — they are the other two thirds of the same pipeline and are in this unit of work (see below). Of the genuinely separable items: R023 (forms.json unread) is the data feed for family/intensity/rank, but family can be resolved from the existing colour identity and rank from limb count, so it can land after the pipeline is correctly shaped — wiring 132 KB of authored forms into a pipeline that still contradicts the design would just consume bad multipliers faster. R014 (intensity scaling) is a modulation of multipliers that do not yet exist in the right axes; shipping it first means scaling the wrong numbers. R004 (lock-on) and R005 (pounce bounce-back) are small, cheap and genuinely independent — they are good parallel work for a second pair of hands, but they are combat-feel polish on a PARTIAL mechanism, not a blocker for the 26-item stat cluster. R018 (colour buffer) is large and depends on limb slots existing as colour-bearing entities, which presupposes the limb-count baseline from R015.

## Implementation notes from the project's build plan

The developer's own notes on this chunk. Where these and the design document disagree, the design document wins.

### A1 · The family and rank contract
**Owner:** Director (owns the contract) + Gameplay Engineer · **Touches:** `GameConfig.cs`, `Creature.cs`, `PlayerController.cs`, `EnemyAI.cs`, `ContentDatabase.cs`

- Five families only. Rename `WHITE` → `GREY` (the numbers are already Grey's); retire Green/Cyan/Orange/Pink as families; White becomes the empty state — a bare limb, a newborn, a grazer.
- Replace the `Tiers` array (Alpha…Omega) with §2.4's **limb table**, ranks 1–6: Health 100→350, Damage 40→115, Speed 12→17, Reach 16→31.
- Add the **intensity** axis: Pale 25% · Dusk 50% · Deep 75% · Clash ~90% · Rage 100%, applied as a fraction of each family multiplier's distance from 1.0.
- Sever rank from eating. `EvoRequirement` and the eat-to-evolve path come out; rank changes only through breeding (B2).
- `ContentDatabase.TierIndex` currently maps the content's saturation tiers onto morphology tiers — that conflation is exactly the bug this chunk fixes. Content tier → **intensity**; rank → **limbs**.

> **Expect the game to get worse before better.** This chunk removes the only progression the prototype has and doesn't add its replacement until A2. Do A1 and A2 back to back.

### A2 · The colour buffer and form resolution
**Owner:** Gameplay Engineer · **Reads:** `forms.json` (150) — first consumer of `FormTable`

- Buffer = one slot per limb, each holding `{family, intensity}` or white.
- Fill rules: white limb first, else **FIFO** eviction of the oldest colour.
- **Q / B poops** the oldest colour; the limb goes white; a dropping is left behind.
- The next slot to be overwritten **pulses on the body** — the GDD permits opacity in the menu, never in the mechanism (§4.9a).
- Resolution, exactly as §2.4b states it: family = most limbs (ties → most recent; at birth, precedence Yellow → Red → Blue → Purple → Grey); intensity = lowest tier among family units, stepped down one rung per non-family limb, floored at Pale; **Clash sits beside Rage**, not above it, and any Clash unit wins the tie; all-white = form zero.
- Mutation fires the instant resolution changes; stats recompute from the resolved form.

**Test it against the GDD's own worked example:** rank 3 holding Rage Yellow / Rage Yellow / Dusk Red → **Deep Brawler**. Poop the Red → still Deep. Eat one Rage Yellow → **Rage Brawler**.

## Codebase index

Declarations only — read any file before you change it.

# Codebase inventory

Regex-derived index of Assets/Scripts. Declarations only -- it recovers names, not semantics, and members are attributed to the most recent enclosing type. Treat absence as weak evidence and presence as strong evidence.

## Assets/Scripts/Content/ContentDatabase.cs  (186 lines)
- `class ContentDatabase` — IsLoaded, LoadError, Creatures, Biomes, Reset, Load, ReadStreamingAsset, Fail, Wandering, Pocket, ById, RollSpawn, GrazerWeight, Weight, TierIndex, ColorTypeFor, HexToColor
- `struct SpawnEntry` — def, spawn
- string literals: "creatures.json", "biomes.json", "biomes.json parsed but held no biomes", "alpha", "apex", "Pale", "Dusk", "Deep", "Rage", "Clash", "Yellow", "YELLOW", "Red", "RED", "Blue", "BLUE", "Purple", "PURPLE", "Grey", "WHITE", "GREEN"

## Assets/Scripts/Content/FormTable.cs  (48 lines)
- `class StatBlock` — health, damage, speed, reach, dash
- `class FormDef` — id, family, intensity, intensity_pct, rank, name, flavor, base_hex, saturation, silhouette, surface, vfx, socket_layout, stats
- `class FormTable` — generated_by, count, forms, Load
- string literals: "class", "forms"

## Assets/Scripts/Content/WorldTables.cs  (70 lines)
- string literals: "Yellow", "Red", "Blue", "Purple", "Grey"

## Assets/Scripts/Editor/ContentCheck.cs  (99 lines)
- `class ContentCheck` — RollSamples, Verify, HasSpawn
- string literals: "Tools/Morphivore/Verify World Content", "(grazer)", "    rolled: ", "Yellow", "Red", "Blue", "Purple", "Grey", "  RESULT: OK", "  RESULT: PROBLEMS FOUND (see above)"

## Assets/Scripts/Editor/MCPBridge.cs  (592 lines)
- `class MCPBridge` — Port, Stop, _pendingStateChanged, NotifyStateChanged, AcceptLoop, HandleClient, DoWebSocketHandshake, ServeWebSocket, ReadFrame, WriteFrame, ReadExact, FlushMainThreadQueue, Dispatch, GetSceneInfo, ListGameObjects, AppendGameObject, GetComponents, ExecuteMenuItem, SetPlayMode, GetLogs, ReadFile, WriteFile, ListScripts, RefreshAssets, DestroyGameObject, CreateGameObject, SetTransform, SetParent, AddComponent, Batch, ParseBatchRequests, TryParseVec3, InterlockedDecrementClamp, GetPath, JsonString, Ok, Error
- `enum Status` — CurrentStatus, ConnectedClients, _listener, _cts, _clientCount, _queueLock, Start
- string literals: "[MCPBridge] Stopped.", "Sec-WebSocket-Key:", "258EAFA5-E914-47DA-95CA-C5AB0DC85B11", "ping", "pong", "get_scene_info", "list_gameobjects", "get_components", "execute_menu_item", "play", "stop", "get_logs", "read_file", "write_file", "list_scripts", "refresh_assets", "destroy_gameobject", "create_gameobject", "set_transform", "set_parent", "batch", "add_component", "Unknown command: {req.command}", ":{go.transform.childCount}}}", "GameObject not found: {goPath}", ":{JsonString(c?.GetType().FullName ?? ", ")}}}", "Executed: {menuPath}", "MenuItem not found: {menuPath}", "Entering play mode", "Exiting play mode", ".config/unity3d/Editor.log", "Editor.log not found", "File not found: {projectRelativePath}", "Written: {projectRelativePath}", "Folder not found: {folder}", "*.cs", "Assets", ", ", "Asset database refreshed", "Destroyed: {goPath}", "Cube", "Sphere", "Empty", "Create GameObject", "px,py,pz|sx,sy,sz|rx,ry,rz", "Set Transform", "Transform set: {goPath}", "Child not found: {childPath}", "Parent not found: {parentPath}", "Set Parent", "Parented {childPath} -> {parentPath}", "Type not found: {typeName}", "Added {typeName} to {goPath}", "command", "arg", "content", ":{results}}}", " + (s ?? ", ").Replace("

## Assets/Scripts/Editor/MCPBridgeWindow.cs  (45 lines)
- `class MCPBridgeWindow` — _green, _red, Open
- string literals: "MCP/Bridge Window", "MCP Bridge", " : ", ")}  (port {MCPBridge.Port})", "● Stopped", "Stop Bridge", "Start Bridge"

## Assets/Scripts/Editor/UrpMaterialConverter.cs  (102 lines)
- `class UrpMaterialConverter` — SearchFolders, UrpLit, Convert, NeedsConversion
- string literals: "Universal Render Pipeline/Lit", "[URP] no art folders found.", "t:Material", "_MainTex", "_BumpMap", "_Color", "_Metallic", "_Glossiness", "_BaseMap", "_NORMALMAP", "_BaseColor", "_Smoothness", " + string.Join(", ", names) : ", "Universal Render Pipeline/", "Shader Graphs/", "Standard", "Standard (Specular setup)", "Legacy Shaders/", "Mobile/", "Hidden/InternalErrorShader"

## Assets/Scripts/Game/Companion.cs  (28 lines)
- `class Companion` — target, index

## Assets/Scripts/Game/Creature.cs  (209 lines)
- `class Creature` — tier, colorType, isBoss, displayName, hasBodyColor, hasContentStats, bodyColor, BodyColor, GroundFollow, GroundY, StickY, maxHealth, health, kills, isDead, isDowned, damageCooldownTimer, body, limbs, Awake, Init, BuildVisuals, Update, TakeDamage, Die, Evolve
- string literals: "GREEN", "dizzy", "RED", "BLUE", "CYAN", "_EMISSION", "_EmissionColor"

## Assets/Scripts/Game/EcosystemManager.cs  (276 lines)
- `class EcosystemManager` — player, OnBiomeChanged, OnBossSpawned, OnMateSpawned, enemies, LegacyBiomes, gameStarted, Init, PocketLeakChance, FindSpawn
- string literals: "Enemy", "enemy", "Apex predator", "MateEnemy", "PINK"

## Assets/Scripts/Game/EnemyAI.cs  (536 lines)
- `class EnemyAI` — DownedDuration, isLockedByPlayer, WindupTime, PounceTime, Awake, hunters, BeginHunterFrame, CountHunter, ClaimHunterSlot, TakeDamage, Die, GetEaten, Update, BarWidth
- `enum State` — (none parsed)
- `enum Attack` — contentId, role, carriesColour, healsPlayerPct, PounceLungeFactor, ApplyContent
- string literals: "prey", "grazer", "elite", "trait_miniboss", "alpha", "apex", "dizzy", "dizzy / vulnerable", "Player", "targeted", "EnemyHealthBar", "BG", "Fill"

## Assets/Scripts/Game/GameConfig.cs  (190 lines)
- `class GameConfig` — ClassFor, Tiers, WorldSize, InitialEnemies, MaxEnemies, EvoRequirement, LevelUpRequirement, SpawnInterval, DamageCooldown, RegenRate, BiomeNeon, BiomeMagma, BiomeCrystal, VisualsForBiome
- `class Colors` — Red, Blue, Green, Yellow, Purple, Orange, Cyan, White, Pink, FromName
- `struct ClassProfile` — name, speedMult, damageMult, healthMult, lungeMult, dashMult
- `struct TierData` — name, scale, limbs
- `class Ecology` — ContactDamageScale, SpeedScale, ReachScale, WanderPace, SightRadius, SightJitter, TerritorialPreyShare, MaxHunters
- `struct BiomeData` — name, groundColor, accentColor, fogColor, enemyColors
- `class Boss` — SpawnIntervalKills, ScaleMultiplier, HealthMultiplier, DamageMultiplier
- string literals: "RED", "BLUE", "GREEN", "YELLOW", "PURPLE", "ORANGE", "CYAN", "WHITE", "PINK", "Brawler", "Bruiser", "Leaper", "Sniper", "Skirmisher", "Stalker", "Apex", "Forager", "Alpha", "Beta", "Gamma", "Delta", "Omega", "Neon Grid", "Magma Wastes", "Crystal Forest", "prairies", "wetlands", "mountains", "beach", "volcanic"

## Assets/Scripts/Game/GameManager.cs  (609 lines)
- `class GameManager` — EnsureDesktopPointer, S, _hudBarSprite, GetHudBarSprite, barW, barH, rightMargin, labelH, AccentGreen
- string literals: "You are targeted", "[Run] seed {runSeed}", "Main Camera", "MainCamera", "Ambient Light", "Sun", "prairies", "Prairies", "Player", "GREEN", "Ecosystem", "!! APEX PREDATOR DETECTED !!", "!! {name.ToUpper()} !!", "!! MATE DETECTED !!", "Canvas", "EventSystem", "Props", "_EMISSION", "_EmissionColor", "ENTERING {biome.name}", "LockReticleWorld", "LockReticle", "ThreatHaloWorld", "ThreatHalo", "HudBars", "HealthBar", "HEALTH", "EvolutionBar", "EVOLUTION", "GenTierLabel", "Notification", "_Label", "LegacyRuntime.ttf", "_BG", "_Fill", "MenuPanel", "Title", "CUBIC EVOLUTION", "Tagline", "Evolve. Adapt. Dominate.", "StartButton", "INITIALIZE", "DeathPanel", "EXTINCT", "Score", "RestartButton", "NEW EVOLUTION", "Label"

## Assets/Scripts/Game/HumanWalk.cs  (91 lines)
- `class HumanWalk` — speed, distance, legSwingAngle, legFrequency, armSwingAngle, bobAmount
- string literals: "Movement", "Leg swing", "Arm swing", "Body bob", "Hips/UpperLeg_L", "Hips/UpperLeg_R", "Hips/UpperLeg_L/LowerLeg_L", "Hips/UpperLeg_R/LowerLeg_R", "Torso/UpperArm_L", "Torso/UpperArm_R", "Torso/UpperArm_L/LowerArm_L", "Torso/UpperArm_R/LowerArm_R", "Torso"

## Assets/Scripts/Game/MateEnemy.cs  (4 lines)
- `class MateEnemy` — (none parsed)

## Assets/Scripts/Game/Obstacle.cs  (6 lines)
- `class Obstacle` — (none parsed)

## Assets/Scripts/Game/PlayerController.cs  (521 lines)
- `class PlayerController` — gameStarted, moveSpeed, biteDamage, totalKills, level, score, LockConeDot, BaseSpeed, BaseDamage, BaseHealth, ClassName, OnLockTargetChanged, IsThreatened, FlagThreat, OnNotification, OnBiomeRequest, Awake, Update, RegisterKill, Evolve, Die
- string literals: "target then launch", "Forager", "upgrade_damage", "upgrade_speed", "upgrade_health", "I'm targeted", "OFFSPRING SPAWNED!", "EVOLVED — {classProfile.name.ToUpper()}!", "LEVEL UP! RANK {level}", "Companion", "gene_points"

## Assets/Scripts/World/BiomeTerrain.cs  (225 lines)
- `class BiomeTerrain` — Active, IsReady, Build, BuildHeightCurve, Radius, SampleHeight, HeightAt, SetGroundColor
- `struct TerrainProfile` — noiseScale, octaves, persistance, lacunarity, heightMultiplier, groundColor, Prairies
- string literals: "BiomeTerrain", "Universal Render Pipeline/Lit", "centre {SampleHeight(Vector3.zero):0.0}"

## Assets/Scripts/World/PropScatter.cs  (143 lines)
- `class PropScatter` — manifest, manifestLoaded, SetFor, Scatter, MeasureHeight
- `class PropSet` — biome, count, clusters, cluster_radius, min_height, max_height, props
- string literals: "art-manifest.json", "[Art] no prop set for biome '{biomeId}'.", ", "

## Data contract files (Assets/StreamingAssets)

- `art-manifest.json` (1,453 bytes) — read by: Assets/Scripts/World/PropScatter.cs
- `biomes.json` (10,919 bytes) — read by: Assets/Scripts/Content/ContentDatabase.cs
- `creatures.json` (93,959 bytes) — read by: Assets/Scripts/Content/ContentDatabase.cs
- `forms.json` (132,668 bytes) — read by: **NOTHING READS THIS FILE**
- `panels.json` (8,028 bytes) — read by: **NOTHING READS THIS FILE**