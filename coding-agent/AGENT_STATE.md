# Morphivore coding agent — state

Markdown is the agent's memory. Read it, edit it, hand it to the next run.
Anything you change here is what the next session believes.

## BUILT
- 2026-08-09 22:29 — Modified `Assets/Scripts/Game/GameConfig.cs` — Replaces the eight-class/five-tier prototype tables with §2.4's contract: five families, the intensity ladder, the limb baseline table and the composition rule that multiplies them.
- 2026-08-09 22:29 — Created `Assets/Scripts/Game/ColourBuffer.cs` — New: the per-limb colour buffer (§2.4a, FIFO fill/evict/poop) and the resolution that turns any buffer state into exactly one form (§2.4b).
- 2026-08-09 22:29 — Modified `Assets/Scripts/Game/Creature.cs` — Swaps the colorType/tier identity for §2.4's family + intensity + rank, builds one limb per rank, and lets a subclass colour each limb from what it holds.
- 2026-08-09 22:29 — Modified `Assets/Scripts/Content/ContentDatabase.cs` — Becomes the first consumer of forms.json (lookup by family/intensity/rank) and maps the content's saturation tier onto intensity instead of onto a morphology tier.
- 2026-08-09 22:29 — Modified `Assets/Scripts/Game/EnemyAI.cs` — Stamps content creatures with family + intensity + limb rank instead of a colorType/tier, and compares intensity (the meat's saturation) where it used to compare the conflated tier.
- 2026-08-09 22:29 — Modified `Assets/Scripts/Game/PlayerController.cs` — Replaces kills→class/tier levelling with the colour buffer: eating loads a limb, Q/B poops the oldest, the buffer resolves to a form, and every live stat comes from that form's line.
- 2026-08-09 22:29 — Modified `Assets/Scripts/Game/EcosystemManager.cs` — Spawns wildlife in the five-family vocabulary (family/intensity/rank) and gates biome progression on rank rather than the retired tier ladder.
- 2026-08-09 22:29 — Modified `Assets/Scripts/Game/GameManager.cs` — HUD now reads the resolved form (rank + intensity/family + authored name) instead of gen/tier/class, and the evolution bar goes with the eat-to-evolve path it measured.

## DECISIONS
- 2026-08-09 22:29 — R013 tops the list because it sits at the junction of the whole stat system: 26 downstream items wait on it, its severity is high, and its effort is only medium because the correct data shape (FormDef/StatBlock with health/damage/speed/reach/dash, plus ContentDatabase.ColorTypeFor already knowing th

## NEXT
- 2026-08-09 22:29 — Five colour families and their stat multipliers (§2.4, CONTRADICTED, score 40.5)
- 2026-08-09 22:29 — Limb baseline stat table (§2.4, CONTRADICTED, score 36.0)
- 2026-08-09 22:29 — Intensity scaling of family multipliers (§2.4, 2.4b, UNCONSUMED, score 32.5)
- 2026-08-09 22:29 — Lock-on targeting (§2.1, PARTIAL, score 29.0)
- 2026-08-09 22:29 — Pounce attack (§2.1, PARTIAL, score 28.0)
- 2026-08-09 22:06 — Five colour families and their stat multipliers (§2.4, CONTRADICTED, score 40.5)
- 2026-08-09 22:06 — Limb baseline stat table (§2.4, CONTRADICTED, score 36.0)
- 2026-08-09 22:06 — Intensity scaling of family multipliers (§2.4, 2.4b, UNCONSUMED, score 32.5)
- 2026-08-09 22:06 — Lock-on targeting (§2.1, PARTIAL, score 29.0)
- 2026-08-09 22:06 — Pounce attack (§2.1, PARTIAL, score 28.0)

## FAILED
