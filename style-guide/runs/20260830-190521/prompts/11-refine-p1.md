# Prompt 11 — refine-p1

## System

```
You are rewriting one piece of MORPHIVORE content that failed style review.

MORPHIVORE — STYLE GUIDE

The game: you are a cube-creature in a five-biome ecosystem. You eat creatures
to take their colour. Identity is a FIFO colour buffer — one slot per limb,
each holding a family (Yellow, Red, Blue, Purple, Grey) at an intensity
(Pale < Dusk < Deep < Clash < Rage) — resolving to one of 150 forms. Rank is limb count
1-6 and comes only from beating an Alpha and breeding. Biomes run
Prairies -> Wetlands -> Mountains -> Beach -> Volcanic.

This guide is not a general quality standard. It is three constraints taken
from this game's own design document and its own shipped text.

C1 — TONE: primal, crude, comedic.
    GDD §3.1: "owns the voice: primal, crude, comedic (the Cubivore tone). With no dialogue, narrator, item text or lore, form names are the *entire* authorial voice."
    Physical, concrete, unsentimental, faintly disgusting, occasionally funny.
    Describe meat, bone, dirt, appetite and violence plainly.
    NOT: reverent or epic register, mysticism, awe, destiny, prophecy,
    ceremony, sentimentality, or abstraction.
    GDD §1: "Morphivore refuses Cubivore's world-restoration wrapper; you are not saving anything, you are trying to sit on top."
    There is no kingdom to save and no plot to resolve. The fiction is the food
    chain and nothing else.

C2 — VOCABULARY AND LORE: this game's nouns, and claims that hold.
    Use: family, intensity, rank, limb, form, panel, emblem, Alpha, grazer, prey, elite, Bestiary, the Blank, buffer, meat.
    Families are Yellow, Red, Blue, Purple, Grey. Intensities are Pale, Dusk, Deep, Clash, Rage.
    Never use generic RPG vocabulary this game does not have — ancient evil, artifact, boss, chosen one, dungeon, enchant, experience point, inventory, level up, levelling, loot, magic, mana, potion, and
    the like. Rank comes from breeding, not from points or levels. Eating
    changes what you ARE, not how big you are.
    Lore that must hold: §2.8 — "Panels are the run's only power source";
    an emblem is a trophy and grants nothing.

C3 — FORMATTING AND LENGTH: measured from the 235 flavour lines already in
the game (creatures 60, forms 150, emblems 25).
    At most 24 words (the longest shipped line is
    23; the mean is 10.6).
    At most 2 sentence(s).
    ZERO exclamation marks — there are 0 in all 235
    authored lines.
    No second-person instructions ("Use this to...") and no "This is a..."
    openers. Describe the thing, not what the player should do with it.

The house voice, from lines already shipped:
    - "Rolls through the grass eating grass, offering nothing, fearing everything."
    - "Half mud, half meat, all squeal."
    - "Rolls downhill faster than it ever runs uphill, and it never runs uphill."
    - "The good eye gone milky at the edges, because staring down a bright shore costs you something."
    - "One rib off a cage where every rib was the same, pried out with your knee on its chest."

Make the smallest change that clears the violations. Keep any phrase that already sounds like this game.

Rules of this job:
- Fix exactly what the review names. Keep everything that already worked —
  if one image in the line is right, it survives the rewrite.
- Rewrite so it would score 10/10 against the guide above.
- Return the name too; change it only if the review flagged it.

Report what you changed in `what_i_changed`, in one line.
```

## User

```
# The content as it stands

NAME: 'Scrawny Thumper'
FLAVOUR: "A jittery little scrap of pale yellow, all knees and nerves, thumping out a panic-drum you can feel through the soil! Don't let the ribs fool you — that faded straw hide is the purest Pale Yellow you'll find this early, and it comes off clean! Chase it into a dead end, take it in one bite, and wear that soft custard glow like you were born in it! You'll love how the Thumper's colour makes every brighter yellow ahead look absolutely gorgeous by comparison — go get it, and go get seconds!"

# The review

SCORE: 2/10
WORST CONSTRAINT: C3_formatting
REASON: C3 is broken on every measurable axis at once: 93 words against a 24-word ceiling, 4 sentences against 2, and 4 exclamation marks where the 235 shipped lines contain zero. On top of that the whole back half is second-person instruction — "Chase it into a dead end, take it in one bite" and "go get it, and go get seconds" — which the guide forbids outright; shipped lines describe the animal ('Half mud, half meat, all squeal.'), they never coach the player. The register is also wrong in a way that isn't epic but is just as off: "wear that soft custard glow like you were born in it" and "look absolutely gorgeous by comparison" are cosmetics-shop sales copy, sentimental and flattering, where this game is unsentimental about meat — the correct move on a Pale Yellow prey is the ribs, the knees, the dirt, and how little it's worth, not how pretty its colour will look on you. Vocabulary is the one clean part: family/intensity terms (Pale Yellow), 'prey', and no imported RPG nouns. Fix: cut to one sentence of at most 24 words, drop every exclamation mark and every imperative, keep 'all knees and nerves' and the panic-drum in the soil, and lose the glow, the custard and the 'gorgeous'.

Violations:
  - [C3_formatting] 'entire line, 93 words' — Limit is 24 words; the longest shipped line is 23 and the mean is 10.6. This is four times the ceiling.
  - [C3_formatting] '4 sentences' — Corpus never exceeds 2 sentences.
  - [C3_formatting] 'you can feel through the soil!' — Exclamation mark; there are zero in all 235 authored lines.
  - [C3_formatting] 'and it comes off clean!' — Second exclamation mark.
  - [C3_formatting] 'like you were born in it!' — Third exclamation mark.
  - [C3_formatting] 'go get it, and go get seconds!' — Fourth exclamation mark, and a direct second-person call to action.
  - [C3_formatting] 'Chase it into a dead end, take it in one bite' — Second-person instruction telling the player what to do with the creature; flavour describes the thing, not the tactic.
  - [C3_formatting] "Don't let the ribs fool you" — Second-person address to the player rather than description of the creature.
  - [C1_tone] 'wear that soft custard glow like you were born in it' — Sentimental and cosmetic; eating changes what you ARE, and the house voice treats colour as meat taken off a body, not a glow you put on.
  - [C1_tone] "You'll love how the Thumper's colour makes every brighter yellow ahead look absolutely gorgeous by comparison" — Marketing register — 'you'll love', 'absolutely gorgeous' — where the tone is primal, crude and unsentimental about appetite.
  - [C1_tone] 'go get it, and go get seconds' — Hype/cheerleading voice; the fiction is the food chain observed flatly, not a pitch.
  - [C2_vocabulary] 'every brighter yellow ahead' — Vague brightness in place of the game's named intensity ladder (Pale, Dusk, Deep, Clash, Rage).
```
