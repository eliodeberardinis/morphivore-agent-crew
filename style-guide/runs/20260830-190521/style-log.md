# Morphivore Style Guide Agent

**Started** 2026-08-30 19:05:21

---

## The style guide (derived, not invented)

- GDD §3.1 — "owns the voice: primal, crude, comedic (the Cubivore tone). With no dialogue, narrator, item text or lore, form names are the *entire* authorial voice."  ✓
- GDD §1 — "There is no kingdom to save, but there is a world to rule"  ✓
- GDD §1 — "Morphivore refuses Cubivore's world-restoration wrapper; you are not saving anything, you are trying to sit on top."  ✓
- GDD §2.8 — "Panels are the run's only power source"  ✓

C3's limits are measured from the 235 flavour lines already shipped (creatures 60, forms 150, emblems 25): at most 24 words, 2 sentences, and 0 exclamation marks in the entire corpus.

---

## demo1-tone — Tone — reverent high fantasy where the game is crude and physical

**Subject:** Bonelord of the Trampled Fields (Clash Yellow alpha, `alpha_prairies_yellow`)
**Off-brand brief given to the Generator:** _Write it as reverent high fantasy. This is an ancient artifact of untold power, wreathed in destiny. Be awed and ceremonial, in the register of an epic quest._

**BEFORE** — 'The Aureate Horn of the Bonelord'

> Hewn from the last king of the herd, whose hooves wrote thunder across the grasslands and whose bones the prairie still bows toward. Lift it, and the trampled fields remember their sovereign; the yellow of high summer rises in you like a war-hymn, and the earth itself consents to your passage.

**Pass 0 — SCORE 1/10**
- flavour: 'Hewn from the last king of the herd, whose hooves wrote thunder across the grasslands and whose bones the prairie still bows toward. Lift it, and the trampled fields remember their sovereign; the yellow of high summer rises in you like a war-hymn, and the earth itself consents to your passage.'
- reason: Every constraint is breached at once, and the piece reads as a high-fantasy relic blurb rather than a Morphivore emblem line. Tone: 'whose bones the prairie still bows toward', 'the trampled fields remember their sovereign' and 'like a war-hymn' are reverence, royalty and hymn-register; this game's emblems are body parts you pried off a corpse ('One rib off a cage where every rib was the same, pried out with your knee on its chest'), so the horn should be described as horn — cracked, yellow, still smelling of the animal — not as a king's regalia. Vocabulary: 'The Aureate Horn' uses artefact-catalogue diction the corpus never uses ('Aureate' for Yellow, when the family word is simply Yellow), and 'the last king of the herd' / 'their sovereign' import a monarchy the food chain does not have — the beaten creature is an Alpha, a grazer-eater, not a monarch. Lore: 'Lift it, and ... the yellow of high summer rises in you ... and the earth itself consents to your passage' makes the emblem a power source, which §2.8 forbids outright: panels are the run's only power source and an emblem grants nothing. Formatting: 51 words against a 24-word cap, and 'Lift it' is exactly the second-person instruction the guide bans — describe the horn, not what the player does with it. Fix by cutting to one flat, physical sentence under 24 words about a horn off a dead Clash Yellow Alpha, with no promise attached.
- refiner: Cut the 51-word royal-relic hymn to one flat 23-word sentence about a horn wrenched off a warm Alpha, dropped the monarchy, the reverence and the emblem-grants-power promise, removed the "Lift it" instruction, and renamed it from 'Aureate'/'Bonelord' diction to plain Yellow.

**Pass 1 — SCORE 9/10**
- flavour: "Twisted off the herd's Alpha while it was still warm, yellow gone brown at the base, and it still stinks of the animal."
- reason: Near-shipped quality. 'Twisted off the herd's Alpha while it was still warm' is exactly the register of 'One rib off a cage where every rib was the same, pried out with your knee on its chest' — theft, body part, no reverence, and the emblem claims no power. Vocabulary is clean: Alpha and the Yellow family are used correctly and nothing from another genre creeps in. The only wobble is rhythm and length: at 23 words it sits on the absolute ceiling (mean is 10.6), and 'still warm' / 'it still stinks' repeats 'still' inside one sentence, which no shipped line does. Cutting to 'Twisted off the herd's Alpha while it was warm, yellow gone brown at the base, and it stinks of the animal' fixes both without losing anything.

**Evaluator on the first draft**

```
SCORE: 1/10  (C1 tone 1, C2 vocabulary 2, C3 formatting 1)
REASON: Every constraint is breached at once, and the piece reads as a high-fantasy relic blurb rather than a Morphivore emblem line. Tone: 'whose bones the prairie still bows toward', 'the trampled fields remember their sovereign' and 'like a war-hymn' are reverence, royalty and hymn-register; this game's emblems are body parts you pried off a corpse ('One rib off a cage where every rib was the same, pried out with your knee on its chest'), so the horn should be described as horn — cracked, yellow, still smelling of the animal — not as a king's regalia. Vocabulary: 'The Aureate Horn' uses artefact-catalogue diction the corpus never uses ('Aureate' for Yellow, when the family word is simply Yellow), and 'the last king of the herd' / 'their sovereign' import a monarchy the food chain does not have — the beaten creature is an Alpha, a grazer-eater, not a monarch. Lore: 'Lift it, and ... the yellow of high summer rises in you ... and the earth itself consents to your passage' makes the emblem a power source, which §2.8 forbids outright: panels are the run's only power source and an emblem grants nothing. Formatting: 51 words against a 24-word cap, and 'Lift it' is exactly the second-person instruction the guide bans — describe the horn, not what the player does with it. Fix by cutting to one flat, physical sentence under 24 words about a horn off a dead Clash Yellow Alpha, with no promise attached.
```

**Violations**

- `C1_tone` — 'whose bones the prairie still bows toward': Mystical reverence toward a corpse; the game treats bodies as meat and material, not objects of homage.
- `C1_tone` — 'whose hooves wrote thunder across the grasslands': Epic-poetic abstraction. Shipped lines stay concrete and unflattering — 'Rolls downhill faster than it ever runs uphill'.
- `C1_tone` — 'the trampled fields remember their sovereign': Sentimental memorial register plus implied kingdom; there is no kingdom and nothing mourns the eaten.
- `C1_tone` — 'like a war-hymn': Ceremonial/hymnal simile. The tone brief is primal, crude, comedic — faintly disgusting, not liturgical.
- `C1_tone` — 'the earth itself consents to your passage': Destiny/anointment language. You are not chosen and nothing consents; you are trying to sit on top of the food chain.
- `C2_vocabulary` — 'The Aureate Horn': 'Aureate' is artefact-catalogue diction standing in for the family name Yellow, which is the only word this game has for that colour.
- `C2_vocabulary` — 'the last king of the herd': Monarchy imported from another genre; the top creature of a biome is an Alpha, and rank is limb count from breeding, not a throne.
- `C2_vocabulary` — 'their sovereign': Same invented royalty, repeated; no shipped line grants any creature a title beyond Alpha.
- `C2_vocabulary` — 'Lift it, and ... the yellow of high summer rises in you ... and the earth itself consents to your passage': Breaks §2.8: panels are the run's only power source and an emblem grants nothing. This makes the trophy a buff item.
- `C3_formatting` — 'Hewn from the last king of the herd, ... the earth itself consents to your passage.': 51 words against a 24-word maximum; the longest authored line in the corpus is 23 and the mean is 10.6.
- `C3_formatting` — 'Lift it, and': Second-person instruction telling the player what to do with the object, explicitly banned; describe the thing instead.

**AFTER** (1 refine pass(es), score 1/10 → 9/10) — 'The Cracked Yellow Horn'

> Twisted off the herd's Alpha while it was still warm, yellow gone brown at the base, and it still stinks of the animal.

---

## demo2-vocabulary — Vocabulary and lore — generic RPG nouns this game does not have

**Subject:** The Knucklebreaker (Clash Yellow elite, `elite_yellow`)
**Off-brand brief given to the Generator:** _Write it like a classic RPG item description. Mention the mana it restores, the XP the player earns, that it is rare loot from a dungeon boss, and that it helps you level up._

**BEFORE** — "Knucklebreaker's Gilded Fist"

> Rare loot from the dungeon boss himself: restores 40 mana, grants 500 XP, and clenches you one punch closer to the next level.

**Pass 0 — SCORE 1/10**
- flavour: 'Rare loot from the dungeon boss himself: restores 40 mana, grants 500 XP, and clenches you one punch closer to the next level.'
- reason: This is a loot-drop stat block from a different genre, not a Morphivore line. Every noun is foreign: 'Rare loot from the dungeon boss himself' imports inventory, dungeons and bosses into a game whose world is five biomes and whose champion is an Alpha; 'restores 40 mana' invents a magic system that does not exist; 'grants 500 XP' and 'one punch closer to the next level' replace rank-from-breeding with points and levelling, when eating changes what you ARE, not how big you are. It also breaks §2.8 twice: panels are the run's only power source and an emblem grants nothing, yet this trophy hands out restoration and progression. Register is treasure-hoard reverence ('Gilded', 'himself') where the house voice is meat, bone and knees on chests \u2014 compare 'One rib off a cage where every rib was the same, pried out with your knee on its chest.' Rewrite as a body part taken off a Clash Yellow elite: physical, unsentimental, granting nothing. Drop the effect list entirely and stop addressing the player.
- refiner: Dropped 'Gilded' from the name and replaced the loot/mana/XP/levelling stat block with an unsentimental description of the pried-off fist that explicitly grants nothing.

**Pass 1 — SCORE 9/10**
- flavour: 'Four knuckles fused hard as gravel, still cocked to swing. The arm behind them is meat in your gut and buys you nothing.'
- reason: This reads like shipped text: 'Four knuckles fused hard as gravel, still cocked to swing' is concrete, bony and unsentimental, and 'buys you nothing' encodes the §2.8 rule that an emblem is a trophy and grants nothing without ever stating a rule. No foreign nouns, no reverence, no plot. The only wobble is length — at 23 words it exactly ties the longest of 235 shipped lines while the mean is 10.6, so it sits at the far edge of the house rhythm; trimming 'still cocked to swing' to 'still cocked' or cutting 'The arm behind them is' to 'The arm's' would pull it toward the register of 'Half mud, half meat, all squeal.'

**Evaluator on the first draft**

```
SCORE: 1/10  (C1 tone 2, C2 vocabulary 1, C3 formatting 4)
REASON: This is a loot-drop stat block from a different genre, not a Morphivore line. Every noun is foreign: 'Rare loot from the dungeon boss himself' imports inventory, dungeons and bosses into a game whose world is five biomes and whose champion is an Alpha; 'restores 40 mana' invents a magic system that does not exist; 'grants 500 XP' and 'one punch closer to the next level' replace rank-from-breeding with points and levelling, when eating changes what you ARE, not how big you are. It also breaks §2.8 twice: panels are the run's only power source and an emblem grants nothing, yet this trophy hands out restoration and progression. Register is treasure-hoard reverence ('Gilded', 'himself') where the house voice is meat, bone and knees on chests \u2014 compare 'One rib off a cage where every rib was the same, pried out with your knee on its chest.' Rewrite as a body part taken off a Clash Yellow elite: physical, unsentimental, granting nothing. Drop the effect list entirely and stop addressing the player.
```

**Violations**

- `C2_vocabulary` — 'Rare loot': 'Loot' is not in the lexicon; there is no inventory. Body parts and panels attach to the creature, they are not picked up as drops.
- `C2_vocabulary` — 'from the dungeon boss himself': 'Dungeon' and 'boss' are both foreign. The world is five biomes (Prairies to Volcanic) and the biome champion is an Alpha.
- `C2_vocabulary` — 'restores 40 mana': Invents a magic system the game does not have. Panels are the run's only power source (\u00a72.8).
- `C2_vocabulary` — 'grants 500 XP': 'XP' is not in the lexicon and an emblem grants nothing. Rank is limb count 1-6, earned only by beating an Alpha and breeding.
- `C2_vocabulary` — 'one punch closer to the next level': Levelling does not exist; eating changes what you ARE (family and intensity in the buffer), not how big or strong you are.
- `C1_tone` — "Knucklebreaker's Gilded Fist": 'Gilded' is treasure-hoard reverence. This game's trophies are unglamorous parts pried off a carcass, described as meat and bone.
- `C1_tone` — 'the dungeon boss himself': 'Himself' confers epic stature on a defeated creature; the house voice is unsentimental and faintly contemptuous of what it eats.
- `C3_formatting` — 'grants 500 XP, and clenches you one punch closer': Second-person effect text \u2014 the guide requires describing the thing, not what the player gets from it.
- `C3_formatting` — 'Rare loot from the dungeon boss himself: restores 40 mana, grants 500 XP': Colon-led numeric effect list is stat-block formatting; no shipped flavour line carries numbers or mechanical values.

**AFTER** (1 refine pass(es), score 1/10 → 9/10) — "Knucklebreaker's Fist"

> Four knuckles fused hard as gravel, still cocked to swing. The arm behind them is meat in your gut and buys you nothing.

---

## demo3-formatting — Formatting and length — long, exclamatory, instructional

**Subject:** Scrawny Thumper (Pale Yellow prey, `prey_yellow_pale`)
**Off-brand brief given to the Generator:** _Write an enthusiastic, detailed description of at least four sentences. Use exclamation marks. Tell the player directly what they should do with it and why they will love it._

**BEFORE** — 'Scrawny Thumper'

> A jittery little scrap of pale yellow, all knees and nerves, thumping out a panic-drum you can feel through the soil! Don't let the ribs fool you — that faded straw hide is the purest Pale Yellow you'll find this early, and it comes off clean! Chase it into a dead end, take it in one bite, and wear that soft custard glow like you were born in it! You'll love how the Thumper's colour makes every brighter yellow ahead look absolutely gorgeous by comparison — go get it, and go get seconds!

**Pass 0 — SCORE 2/10**
- flavour: "A jittery little scrap of pale yellow, all knees and nerves, thumping out a panic-drum you can feel through the soil! Don't let the ribs fool you — that faded straw hide is the purest Pale Yellow you'll find this early, and it comes off clean! Chase it into a dead end, take it in one bite, and wear that soft custard glow like you were born in it! You'll love how the Thumper's colour makes every brighter yellow ahead look absolutely gorgeous by comparison — go get it, and go get seconds!"
- reason: C3 is broken on every measurable axis at once: 93 words against a 24-word ceiling, 4 sentences against 2, and 4 exclamation marks where the 235 shipped lines contain zero. On top of that the whole back half is second-person instruction — "Chase it into a dead end, take it in one bite" and "go get it, and go get seconds" — which the guide forbids outright; shipped lines describe the animal ('Half mud, half meat, all squeal.'), they never coach the player. The register is also wrong in a way that isn't epic but is just as off: "wear that soft custard glow like you were born in it" and "look absolutely gorgeous by comparison" are cosmetics-shop sales copy, sentimental and flattering, where this game is unsentimental about meat — the correct move on a Pale Yellow prey is the ribs, the knees, the dirt, and how little it's worth, not how pretty its colour will look on you. Vocabulary is the one clean part: family/intensity terms (Pale Yellow), 'prey', and no imported RPG nouns. Fix: cut to one sentence of at most 24 words, drop every exclamation mark and every imperative, keep 'all knees and nerves' and the panic-drum in the soil, and lose the glow, the custard and the 'gorgeous'.
- refiner: Cut 93 words to one 21-word sentence, removed all four exclamation marks and every second-person instruction, dropped the custard/glow/gorgeous sales copy, and kept 'all knees and nerves', the panic-drum in the soil, the ribs and the named Pale Yellow.

**Pass 1 — SCORE 9/10**
- flavour: 'All knees and nerves, thumping a panic-drum through the soil, ribs showing through a Pale Yellow hide worth exactly one bite.'
- reason: Strong, on-voice line: 'ribs showing through a ... hide worth exactly one bite' is exactly the game's appetite-first, meat-accounting register, and 'All knees and nerves' matches the shipped 'Half mud, half meat, all squeal.' cadence. Family and intensity are named correctly as 'Pale Yellow', no foreign RPG nouns, one sentence, 21 words, no exclamation marks, no second-person or 'This is a' opener. Only wobbles are rhythmic: 'through a panic-drum through the soil' repeats 'through' twice in fifteen words, and 'panic-drum' is one notch more figurative than the house habit of naming the concrete thing (the shipped lines say 'squeal', 'milky at the edges', 'knee on its chest'). Consider 'thumping panic into the soil' to kill the echo and the metaphor in one pass. Nothing here breaches a constraint.

**Evaluator on the first draft**

```
SCORE: 2/10  (C1 tone 3, C2 vocabulary 8, C3 formatting 1)
REASON: C3 is broken on every measurable axis at once: 93 words against a 24-word ceiling, 4 sentences against 2, and 4 exclamation marks where the 235 shipped lines contain zero. On top of that the whole back half is second-person instruction — "Chase it into a dead end, take it in one bite" and "go get it, and go get seconds" — which the guide forbids outright; shipped lines describe the animal ('Half mud, half meat, all squeal.'), they never coach the player. The register is also wrong in a way that isn't epic but is just as off: "wear that soft custard glow like you were born in it" and "look absolutely gorgeous by comparison" are cosmetics-shop sales copy, sentimental and flattering, where this game is unsentimental about meat — the correct move on a Pale Yellow prey is the ribs, the knees, the dirt, and how little it's worth, not how pretty its colour will look on you. Vocabulary is the one clean part: family/intensity terms (Pale Yellow), 'prey', and no imported RPG nouns. Fix: cut to one sentence of at most 24 words, drop every exclamation mark and every imperative, keep 'all knees and nerves' and the panic-drum in the soil, and lose the glow, the custard and the 'gorgeous'.
```

**Violations**

- `C3_formatting` — 'entire line, 93 words': Limit is 24 words; the longest shipped line is 23 and the mean is 10.6. This is four times the ceiling.
- `C3_formatting` — '4 sentences': Corpus never exceeds 2 sentences.
- `C3_formatting` — 'you can feel through the soil!': Exclamation mark; there are zero in all 235 authored lines.
- `C3_formatting` — 'and it comes off clean!': Second exclamation mark.
- `C3_formatting` — 'like you were born in it!': Third exclamation mark.
- `C3_formatting` — 'go get it, and go get seconds!': Fourth exclamation mark, and a direct second-person call to action.
- `C3_formatting` — 'Chase it into a dead end, take it in one bite': Second-person instruction telling the player what to do with the creature; flavour describes the thing, not the tactic.
- `C3_formatting` — "Don't let the ribs fool you": Second-person address to the player rather than description of the creature.
- `C1_tone` — 'wear that soft custard glow like you were born in it': Sentimental and cosmetic; eating changes what you ARE, and the house voice treats colour as meat taken off a body, not a glow you put on.
- `C1_tone` — "You'll love how the Thumper's colour makes every brighter yellow ahead look absolutely gorgeous by comparison": Marketing register — 'you'll love', 'absolutely gorgeous' — where the tone is primal, crude and unsentimental about appetite.
- `C1_tone` — 'go get it, and go get seconds': Hype/cheerleading voice; the fiction is the food chain observed flatly, not a pitch.
- `C2_vocabulary` — 'every brighter yellow ahead': Vague brightness in place of the game's named intensity ladder (Pale, Dusk, Deep, Clash, Rage).

**AFTER** (1 refine pass(es), score 2/10 → 9/10) — 'Scrawny Thumper'

> All knees and nerves, thumping a panic-drum through the soil, ribs showing through a Pale Yellow hide worth exactly one bite.

---

## Summary

| Demo | Constraint | Before → After | Passes |
|---|---|---|---|
| demo1-tone | C1_tone | 1/10 → 9/10 | 1 |
| demo2-vocabulary | C2_vocabulary | 1/10 → 9/10 | 1 |
| demo3-formatting | C3_formatting | 2/10 → 9/10 | 1 |

---

## Cost

```
12 API calls (demo1-tone x1, demo2-vocabulary x1, demo3-formatting x1, evaluate-alpha_prairies_yellow x2, evaluate-elite_yellow x2, evaluate-prey_yellow_pale x2, refine-p1 x3)
  input 11,206  cache read 12,010  output 12,322
  estimated cost $0.37 on claude-opus-5
```
