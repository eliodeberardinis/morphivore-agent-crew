# Morphivore Style Guide Agent

**Started** 2026-08-30 19:21:22

---

## The style guide (derived, not invented)

- GDD §3.1 — "owns the voice: primal, crude, comedic (the Cubivore tone). With no dialogue, narrator, item text or lore, form names are the *entire* authorial voice."  ✓
- GDD §1 — "There is no kingdom to save, but there is a world to rule"  ✓
- GDD §1 — "Morphivore refuses Cubivore's world-restoration wrapper; you are not saving anything, you are trying to sit on top."  ✓
- GDD §2.8 — "Panels are the run's only power source"  ✓

C3's limits are measured from the 235 flavour lines already shipped (creatures 60, forms 150, emblems 25): at most 24 words, 2 sentences, and 0 exclamation marks in the entire corpus.

---

## Gate — creatures.json

Scoring 60 record(s) against the style guide. Anything below 9/10 is refined.
- `elite_grey` **5/10 → 9/10** (C1_tone) — Formatting is clean (6 words, 2 sentences, no exclamation, no second-person, no 'This is a' opener), but 'Doesn't have a specialty. Doesn't need one.'
- `alpha_prairies_blue` **5/10 → 9/10** (C2_vocabulary) — The flavour's rhythm and physicality are close to house voice, and formatting is clean (14 words, one sentence, no exclamation), but 'a better trigger
- `alpha_wetlands_blue` **5/10 → 9/10** (C2_vocabulary) — The rhythm and length are right, but 'a better trigger' imports firearm/gunslinger vocabulary into a game whose entire fiction is teeth, meat and limb
- `alpha_mountains_yellow` **5/10 → 9/10** (C1_tone) — The flavour line is shipped-quality — "All knuckles and no neck, it complains right up until it doesn't" is exactly the house move: concrete body part
- `alpha_beach_blue` **5/10 → 9/10** (C2_vocabulary) — The flavour scans right and fits the length rules, but 'a better trigger' imports firearms vocabulary from a different genre entirely — nothing in Mor
- `alpha_volcanic_yellow` **5/10 → 9/10** (C1_tone) — The flavour line is shipped-quality — "All knuckles and no neck, it complains right up until it doesn't" is physical, crude, funny, 12 words, one sent
- `alpha_volcanic_blue` **5/10 → 9/10** (C2_vocabulary) — The flavour's hinge word is 'a better trigger' — a firearm. MORPHIVORE has no weapons, ranged or otherwise; a Clash Blue Alpha kills with limbs, teeth
- `grazer_volcanic` **6/10 → 9/10** (C1_tone) — Formatting and vocabulary are clean u2014 9 words, one sentence, no exclamation, no second person, no foreign RPG nouns u2014 but the tone is the we
- `prey_blue_pale` **6/10 → 9/10** (C2_vocabulary) — The rhythm and the cruelty are right — 'useless the second you're inside its arms' is exactly the house move of naming a creature's one advantage and 
- `elite_purple` **6/10 → 9/10** (C1_tone) — The name 'The Throatgrin' is perfect house voice — a body part plus a leer, exactly like 'Half mud, half meat, all squeal.' The flavour then throws it
- `alpha_wetlands_yellow` **6/10 → 9/10** (C1_tone) — The flavour line is genuinely shipped-quality — "All knuckles and no neck, it complains right up until it doesn't" is 13 words, one sentence, physical
- `alpha_mountains_red` **6/10 → 9/10** (C2_vocabulary) — The flavour line is genuinely house voice — 'Twitchy legs, empty head, gone before you blink twice.' is nine words, one sentence, concrete, unsentimen
- `alpha_mountains_blue` **6/10 → 9/10** (C2_vocabulary) — The flavour line's rhythm and the setup/punchline turn are right, but 'a better trigger' imports firearms into a game whose whole vocabulary is meat, 
- `alpha_mountains_purple` **6/10 → 9/10** (C1_tone) — The flavour line is shipped-quality — 'Slinks in, bites once, forgets to leave a body.' is nine words of concrete violence with a dry joke buried in '
- `alpha_volcanic_red` **6/10 → 9/10** (C1_tone) — The flavour line is genuinely house voice — 'Twitchy legs, empty head, gone before you blink twice.' is concrete, unsentimental and faintly funny, and
- `alpha_volcanic_purple` **6/10 → 9/10** (C1_tone) — The flavour line is close to shipped quality — 'Slinks in, bites once, forgets to leave a body.' is eight words, one sentence, concrete violence with 
- `prey_blue_deep` **7/10 → 9/10** (C2_vocabulary) — Rhythm and length are dead-on house voice (14 words, one sentence, no exclamation), and the shape — a strength followed by the exact condition that vo
- `prey_blue_rage` **7/10 → 9/10** (C2_vocabulary) — Tone and length are right, but the vocabulary drifts twice. 'a better trigger' imports a machine noun into a world made entirely of meat, bone and dir
- `prey_grey_pale` **7/10 → 9/10** (C1_tone) — Formatting is clean (12 words, one sentence, no exclamation, no 'This is a...' or instruction opener) and no foreign nouns appear, so the sink risk is
- `elite_yellow` **7/10 → 9/10** (C1_tone) — Formatting and vocabulary are clean — 17 words, one sentence, no exclamation mark, no foreign nouns, no second-person opener. The problem is register.
- `alpha_volcanic_grey` **7/10 → 9/10** (C1_tone) — The flavour line is excellent house voice — 'Doesn't have a weak side, and hates that you keep looking for one.' is concrete, unsentimental, quietly f
- `apex` **7/10 → 9/10** (C1_tone) — The name 'The Main Course' is good crude food-chain comedy and the vocabulary is clean — 'biomes' is this game's noun and nothing foreign creeps in. T
- `grazer_beach` **8/10 → 9/10** (C1_tone) — Solid, on-brand grazer line: 8 words, one sentence, no exclamation, no second-person or 'This is a' opener, and no foreign RPG nouns. The mockery-by-d
- `prey_blue_dusk` **8/10 → 9/10** (C2_vocabulary) — Solidly on-brand: 14 words, one sentence, no exclamation, no 'This is a...' opener, and the second-person 'you're inside its arms' matches shipped usa
- `prey_grey_dusk` **8/10 → 9/10** (C1_tone) — Strong, shippable line: 12 words, one sentence, no exclamation, no 'This is a...' opener, no foreign RPG nouns, and the second-person appears as the h
- `elite_red` **8/10 → 9/10** (C1_tone) — Strong, on-brand line: 15 words, one sentence, no exclamation, no banned opener, no foreign RPG nouns, and the joke lands the way the shipped lines la
- `elite_blue` **8/10 → 9/10** (C1_tone) — The flavour line is tight and on-brand: 10 words, one sentence, no exclamation, concrete and predatory, and the second-person 'you' is used as object/
- `miniboss_claws` **8/10 → 9/10** (C1_tone) — On-brand and shipped-adjacent: 'squats on' does the crude physical work the house voice wants, 'meaner' keeps it appetite-and-violence rather than des
- `miniboss_coat` **8/10 → 9/10** (C2_vocabulary) — Strong, compact, on-voice line: 14 words, one sentence, no exclamation, no second-person, and 'grew a second hide out of spite for the cold' is exactl
- `alpha_prairies_yellow` **8/10 → 9/10** (C1_tone) — The flavour line is house voice at full strength — "All knuckles and no neck, it complains right up until it doesn't." is concrete, bodily, comedic, a
- `alpha_prairies_grey` **8/10 → 9/10** (C1_tone) — The flavour line is close to shipped quality: 'Doesn't have a weak side, and hates that you keep looking for one.' is 13 words, one sentence, no excla
- `alpha_wetlands_red` **8/10 → 9/10** (C2_vocabulary) — The flavour line itself is close to shipped voice — nine words, one sentence, concrete body parts, dry joke in 'empty head' — and it mirrors the house
- `alpha_wetlands_purple` **8/10 → 9/10** (C1_tone) — The flavour line is house voice done right: 'Slinks in, bites once, forgets to leave a body' is nine words, one sentence, concrete violence with a dry
- `alpha_wetlands_grey` **8/10 → 9/10** (C1_tone) — The flavour line is house-voice clean: 13 words, one sentence, no exclamation, and the comedy is physical and unsentimental — the creature's irritatio
- `alpha_mountains_grey` **8/10 → 9/10** (C1_tone) — The flavour line is near-perfect house voice: 'Doesn't have a weak side, and hates that you keep looking for one.' is physical, unsentimental, faintly
- `alpha_beach_yellow` **8/10 → 9/10** (C1_tone) — The flavour line is essentially shipped-quality: "All knuckles and no neck, it complains right up until it doesn't" is the same trick as "Half mud, ha
- `alpha_beach_red` **8/10 → 9/10** (C1_tone) — Solidly on-brand. The flavour line is concrete, bodily and dismissive — 'Twitchy legs, empty head' has the shipped rhythm of 'Half mud, half meat, all
- `alpha_beach_purple` **8/10 → 9/10** (C1_tone) — The flavour line is close to shipped quality: 'Slinks in, bites once, forgets to leave a body' is nine words, one sentence, physical, violent, and dry

**60 scored** — mean first score 7.63/10, 38 needed refining.
Score distribution: 5/10 × 7, 6/10 × 9, 7/10 × 6, 8/10 × 16, 9/10 × 21, 10/10 × 1
Gated copy written to `gated-creatures.json` (the source file is not modified).

---

## Cost

```
152 API calls (evaluate-alpha_beach_blue x2, evaluate-alpha_beach_grey x1, evaluate-alpha_beach_purple x2, evaluate-alpha_beach_red x2, evaluate-alpha_beach_yellow x2, evaluate-alpha_mountains_blue x2, evaluate-alpha_mountains_grey x2, evaluate-alpha_mountains_purple x2, evaluate-alpha_mountains_red x2, evaluate-alpha_mountains_yellow x2, evaluate-alpha_prairies_blue x2, evaluate-alpha_prairies_grey x2, evaluate-alpha_prairies_purple x1, evaluate-alpha_prairies_red x1, evaluate-alpha_prairies_yellow x2, evaluate-alpha_volcanic_blue x2, evaluate-alpha_volcanic_grey x3, evaluate-alpha_volcanic_purple x2, evaluate-alpha_volcanic_red x3, evaluate-alpha_volcanic_yellow x2, evaluate-alpha_wetlands_blue x3, evaluate-alpha_wetlands_grey x3, evaluate-alpha_wetlands_purple x2, evaluate-alpha_wetlands_red x2, evaluate-alpha_wetlands_yellow x2, evaluate-apex x2, evaluate-elite_blue x2, evaluate-elite_grey x2, evaluate-elite_purple x2, evaluate-elite_red x3, evaluate-elite_yellow x2, evaluate-grazer_beach x2, evaluate-grazer_mountains x1, evaluate-grazer_prairies x1, evaluate-grazer_volcanic x2, evaluate-grazer_wetlands x1, evaluate-miniboss_claws x2, evaluate-miniboss_coat x2, evaluate-miniboss_fins x1, evaluate-miniboss_heat x1, evaluate-prey_blue_deep x3, evaluate-prey_blue_dusk x3, evaluate-prey_blue_pale x2, evaluate-prey_blue_rage x3, evaluate-prey_grey_deep x1, evaluate-prey_grey_dusk x2, evaluate-prey_grey_pale x2, evaluate-prey_grey_rage x1, evaluate-prey_purple_deep x1, evaluate-prey_purple_dusk x1, evaluate-prey_purple_pale x1, evaluate-prey_purple_rage x1, evaluate-prey_red_deep x1, evaluate-prey_red_dusk x1, evaluate-prey_red_pale x1, evaluate-prey_red_rage x1, evaluate-prey_yellow_deep x1, evaluate-prey_yellow_dusk x1, evaluate-prey_yellow_pale x1, evaluate-prey_yellow_rage x1, refine-p1 x38, refine-p2 x8)
  input 114,226  cache read 252,210  output 145,760
  estimated cost $4.34 on claude-opus-5
```
