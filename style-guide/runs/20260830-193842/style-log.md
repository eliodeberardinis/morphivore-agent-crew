# Morphivore Style Guide Agent

**Started** 2026-08-30 19:38:42

---

## The style guide (derived, not invented)

- GDD §3.1 — "owns the voice: primal, crude, comedic (the Cubivore tone). With no dialogue, narrator, item text or lore, form names are the *entire* authorial voice."  ✓
- GDD §1 — "There is no kingdom to save, but there is a world to rule"  ✓
- GDD §1 — "Morphivore refuses Cubivore's world-restoration wrapper; you are not saving anything, you are trying to sit on top."  ✓
- GDD §2.8 — "Panels are the run's only power source"  ✓

C3's limits are measured from the 235 flavour lines already shipped (creatures 60, forms 150, emblems 25): at most 24 words, 2 sentences, and 0 exclamation marks in the entire corpus.

---

## Gate — sample-creatures.json

Scoring 10 record(s) against the style guide. Anything below 9/10 is refined.
- `prey_blue_pale` **8/10 → 9/10** (C2_vocabulary) — Strong, on-brand prey line: 14 words, one sentence, no exclamation, concrete body-and-violence imagery, and 'Scrawny Needler' is a clean 2-word prey n
- `prey_blue_dusk` **8/10 → 9/10** (C2_vocabulary) — The name is textbook prey ('Mangy' is already shipped, two words) and the flavour has the house rhythm — 'One good eye' echoes 'The good eye gone milk

**10 scored** — mean first score 8.80/10, 2 needed refining.
Score distribution: 8/10 × 2, 9/10 × 8
Gated copy written to `gated-sample-creatures.json` (the source file is not modified).

---

## Cost

```
16 API calls (evaluate-alpha_beach_yellow x1, evaluate-alpha_mountains_grey x1, evaluate-alpha_mountains_purple x1, evaluate-alpha_mountains_yellow x1, evaluate-alpha_prairies_grey x1, evaluate-alpha_prairies_yellow x1, evaluate-alpha_wetlands_purple x1, evaluate-alpha_wetlands_yellow x1, evaluate-prey_blue_dusk x3, evaluate-prey_blue_pale x2, refine-p1 x2, refine-p2 x1)
  input 8,621  cache read 19,497  output 18,453
  estimated cost $0.51 on claude-opus-5
```
