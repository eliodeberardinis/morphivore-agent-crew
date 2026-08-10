# Prompt 1 — prioritize

## System

```
You are the technical lead choosing the next chunk of work.

A ranking has already been computed for you by this formula:

    score = (1 + blocking_degree) x severity_weight / effort

You are NOT being asked to re-rank. The order is arithmetic over facts gathered from the codebase, and it stands. Your job is to explain it and to answer one question the formula cannot: is the top-ranked item a single shippable unit, or does shipping it alone leave the project in a worse state than before?

That second question matters. Removing a mechanism the design contradicts can strip out the only working version of that system, and if its replacement is a separate item further down the list, the two have to land together or the game is left with neither. When that is the case, list every id that must ship alongside the leader in `one_unit_of_work` (include the leader itself).

If you think the ranking is wrong, say so plainly in `disagreement` and set `disagrees_with_ranking`. Disagreeing is recorded, not suppressed — but it does not change the order, and the developer decides.
```

## User

```
# Ranked open gaps

1. **Five colour families and their stat multipliers** (id `R013`, GDD 2.4) — score 40.5
   - verdict CONTRADICTED (medium confidence), blocks 26, effort medium
   - The colour→playstyle→multiplier area is definitely implemented, but on different rules than GDD 2.4. The live system is GameConfig.ClassFor / ClassProfile, which carries eight class names (Brawler, Bruiser, Leaper, Sniper, Skirmisher, Stalker, Apex, Forager) rather than the five families, and its axes are speedMult/damageMult/healthMult/lungeMult/dashMult — a `lungeMult` where the design demands `Reach`, so the Blue Sniper's defining long-reach trade cannot be expressed. GameConfig.Colors additionally enumerates nine colours (Green, Orange, Cyan, Pink, White) and Creature/EnemyAI still branch on "GREEN"/"CYAN", so colour identity is broader than the five families. Meanwhile the correct schema already exists but is dead: FormDef/StatBlock carry family, intensity, intensity_pct and exactly the five axes (health, damage, speed, reach, dash), and forms.json (132 KB) is explicitly unread by any code. ContentDatabase.ColorTypeFor does recognise the five family names, and WorldTables.cs mentions exactly those five (its body is unparsed, so it may already hold a family table — the inventory cannot confirm). Net: a parallel, differently-shaped class-multiplier system is in charge of gameplay stats, so this is a contradicted mechanism rather than a missing one.
   - requires removing existing code: yes

2. **Limb baseline stat table** (id `R015`, GDD 2.4) — score 36.0
   - verdict CONTRADICTED (medium confidence), blocks 23, effort medium
   - The codebase clearly implements a baseline-stats-then-multiplier pipeline, but on a different axis than the design. Baselines come from single scalar constants (`PlayerController.BaseSpeed/BaseDamage/BaseHealth`) combined with a five-row tier progression (`GameConfig.Tiers` / `TierData{name, scale, limbs}` named Alpha…Omega, driven by `EvoRequirement`/`LevelUpRequirement` and `Creature.tier`), with `ClassProfile` mults applied on top. That is a rank/level ladder of 5 tiers where `limbs` is a cosmetic/derived field of the tier, not a 1–6 limb-count table that sets Health/Damage/Speed/Reach (100/150/200/250/300/350, 40/55/70/85/100/115, 12/13/14/15/16/17, 16/19/22/25/28/31). Nothing in the inventory shows a four-column, six-row baseline array, and Reach has no baseline at all — only `Ecology.ReachScale` as a global scalar. Notably, `FormTable.StatBlock{health,damage,speed,reach,dash}` and `FormDef.rank` are the right shape and `forms.json` (132 KB) exists, but the inventory marks forms.json as read by nothing, so the correct-shaped stat data is inert while the tier ladder drives play. Because the existing tier/level baseline would have to be replaced (not merely extended) to make limb count the baseline source, this is CONTRADICTED rather than ABSENT/UNCONSUMED, though the unconsumed forms.json is the second half of the story.
   - requires removing existing code: yes

3. **Intensity scaling of family multipliers** (id `R014`, GDD 2.4, 2.4b) — score 32.5
   - verdict UNCONSUMED (medium confidence), blocks 25, effort medium
   - The data side of this requirement is fully present and already parsed in principle: FormDef carries `intensity` and `intensity_pct` plus a `StatBlock` (health, damage, speed, reach, dash) — exactly the hand-tuned, intensity-scaled profile the design calls for — and FormTable.Load exists to deserialise it. But the inventory states plainly that forms.json is read by nothing, so no runtime path resolves a form, reads its intensity_pct, or applies the scaled multipliers. Nothing in the inventory references a per-form Clash gift / second-tone bonus field at all (FormDef's field list has no such member), so even the data for the Clash exception looks unauthored in the schema. The only live multiplier mechanism is GameConfig.ClassProfile (speedMult/damageMult/healthMult/lungeMult/dashMult selected via ClassFor and applied in PlayerController), which is a flat per-class multiplier with no intensity dimension — it would have to be superseded or rewritten for form-driven stats. The tier words Pale/Dusk/Deep/Rage/Clash appear only in ContentDatabase's creature/spawn tier handling (TierIndex, ColorTypeFor), not in any stat computation. I cannot see method bodies, so I cannot rule out that some multiplication happens inside PlayerController.Evolve, but with forms.json unread there is no source of intensity_pct at runtime.
   - requires removing existing code: yes

4. **Lock-on targeting** (id `R004`, GDD 2.1) — score 29.0
   - verdict PARTIAL (medium confidence), blocks 28, effort small
   - 
   - requires removing existing code: no

5. **Pounce attack** (id `R005`, GDD 2.1) — score 28.0
   - verdict PARTIAL (low confidence), blocks 27, effort small
   - The lock-then-launch loop clearly exists on the player side: `LockConeDot`/`OnLockTargetChanged` implement the facing-cone lock, the HUD hint string "target then launch" names the pounce action, `ClassProfile.lungeMult` is a per-class lunge scalar consumed by the player, and `biteDamage` plus `EnemyAI.TakeDamage` / `Creature.TakeDamage` supply the Health drain on a standing target. `EnemyAI.GetEaten` and `isDowned`/`DownedDuration` show the downed-then-eat follow-up also exists. There is no evidence of a charge meter anywhere (no charge/hold fields), which matches the design's "no charge meter". What I cannot see in a declarations-only index is the third clause: the player being **bounced back** off a solid body on impact. No recoil/knockback/impulse member appears on `PlayerController`, and the only lunge-physics-named symbol (`PounceLungeFactor`) sits on `EnemyAI`, i.e. the creature side. Recoil could plausibly be a few lines inside `PlayerController.Update` with no declaration of its own, so this is a genuine limit of the inventory rather than proof of absence. I therefore mark PARTIAL: the launch and damage beats are demonstrably implemented, the bounce-back is unverified.
   - requires removing existing code: no

6. **Final stat composition (rank baseline × family × intensity)** (id `R016`, GDD 2.4) — score 25.5
   - verdict CONTRADICTED (medium confidence), blocks 16, effort medium
   - The codebase does compose live stats, but by a different rule set than the design's rank-baseline × family × intensity formula. Player stats come from GameConfig.ClassProfile (speedMult/damageMult/healthMult/lungeMult/dashMult) selected by ClassFor plus GameConfig.Tiers (TierData with name/scale/limbs), and PlayerController exposes BaseSpeed/BaseDamage/BaseHealth/ClassName which it scales on Evolve/level-up. Nothing in the inventory holds the authoritative limb baseline table (Health 100/150/200/250/300/350, Damage 40..115, Speed 12..17, Reach 16..31), nor any intensity fraction (Pale 25% … Rage 100%) or Clash second-tone gift, nor a Dash axis on the player side. The form-side data model that the design implies does exist — FormDef carries family, intensity, intensity_pct, rank, socket_layout and a StatBlock with exactly health/damage/speed/reach/dash — but forms.json is explicitly unread, so FormTable is dead code and the eight named classes (Brawler, Bruiser, Leaper, Sniper, Skirmisher, Stalker, Apex, Forager) drive stats instead of family+intensity. The worked example (2-limb Rage Brawler vs 5-limb Pale Brawler) cannot be reproduced: 'Brawler' here is a class profile, not a Yellow family, and intensity has no effect anywhere. Because a competing stat pipeline occupies this area and would have to be replaced, this is CONTRADICTED rather than merely UNCONSUMED, though the unread forms.json is the accompanying symptom.
   - requires removing existing code: yes

7. **forms.json — the 150 authored forms** (id `R023`, GDD 2.4b, 3.3) — score 22.5
   - verdict UNCONSUMED (high confidence), blocks 17, effort medium
   - The authored asset exists at full size (forms.json, 132 KB) and a matching deserialisation schema exists in FormTable.cs whose FormDef fields line up almost exactly with the design's required columns (family, intensity, rank, name, socket_layout, stats, plus saturation/silhouette used by §2.4b's rendering rule) and FormTable even carries a `count` field for the 150 assertion. But the inventory's data-contract section states nothing reads forms.json: ContentDatabase.Load only pulls creatures.json and biomes.json, and no call site for FormTable.Load appears anywhere (no reference from ContentDatabase, GameManager, Creature, or EnemyAI). Runtime identity is instead driven by GameConfig.Tiers (five tier names Alpha..Omega with scale/limbs) and GameConfig.ClassFor/Colors, with Creature.tier/colorType/displayName and EnemyAI.contentId/role coming from creatures.json — a 5-tier × colour scheme, not a family × intensity × rank lattice of 150. There is also no Bestiary code at all (no 30-cell grid, no discovered/total header, no rank column), so the in-game observable cannot be checked. Because the inventory explicitly flags the asset as unread and a ready-made parser sits idle, UNCONSUMED is the precise verdict rather than ABSENT; the parallel tier system is a separate legacy path that this requirement would supersede rather than something already claiming to implement forms.
   - requires removing existing code: no

8. **The colour buffer (FIFO limb slots)** (id `R018`, GDD 2.4a) — score 20.0
   - verdict CONTRADICTED (medium confidence), blocks 19, effort large
   - There is no per-limb colour slot collection anywhere in the inventory: no queue/buffer/slot/socket members, no white-slot or eviction logic, no 'oldest colour' concept, and no pulsing next-slot indicator (GameManager's UI strings cover health/evolution bars, lock reticle, threat halo, notifications only). Instead, the same design area — what eating does to your form — is implemented by a completely different mechanism: kills accumulate (RegisterKill, totalKills) against GameConfig.EvoRequirement/LevelUpRequirement to drive PlayerController.Evolve, which assigns a GameConfig.ClassProfile (Brawler/Leaper/Sniper/Apex/Forager, with speedMult/damageMult/healthMult multipliers) and a TierData (Alpha..Omega) whose 'limbs' field is a cosmetic count derived from tier, not a set of colour-bearing slots. Progression is further steered by discrete upgrade picks ("upgrade_damage", "upgrade_speed", "upgrade_health", "gene_points") — hidden-stat levelling rather than the visible, world-forced colour buffer. Colour is stored as a single scalar per creature (Creature.colorType / bodyColor / ContentDatabase.ColorTypeFor with Yellow/Red/Blue/Purple/Grey names) and EnemyAI.carriesColour is a flag, so prey colour has nowhere to be stored per limb. The data the requirement needs partly exists: FormTable/FormDef already models family + intensity + rank + socket_layout and forms.json (132 KB) is in StreamingAssets but nothing reads it — the table is present and unconsumed, so the family/tier vocabulary need not be authored from scratch.
   - requires removing existing code: yes
```
