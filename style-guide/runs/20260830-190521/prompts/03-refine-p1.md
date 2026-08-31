# Prompt 3 — refine-p1

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

NAME: 'The Aureate Horn of the Bonelord'
FLAVOUR: 'Hewn from the last king of the herd, whose hooves wrote thunder across the grasslands and whose bones the prairie still bows toward. Lift it, and the trampled fields remember their sovereign; the yellow of high summer rises in you like a war-hymn, and the earth itself consents to your passage.'

# The review

SCORE: 1/10
WORST CONSTRAINT: C1_tone
REASON: Every constraint is breached at once, and the piece reads as a high-fantasy relic blurb rather than a Morphivore emblem line. Tone: 'whose bones the prairie still bows toward', 'the trampled fields remember their sovereign' and 'like a war-hymn' are reverence, royalty and hymn-register; this game's emblems are body parts you pried off a corpse ('One rib off a cage where every rib was the same, pried out with your knee on its chest'), so the horn should be described as horn — cracked, yellow, still smelling of the animal — not as a king's regalia. Vocabulary: 'The Aureate Horn' uses artefact-catalogue diction the corpus never uses ('Aureate' for Yellow, when the family word is simply Yellow), and 'the last king of the herd' / 'their sovereign' import a monarchy the food chain does not have — the beaten creature is an Alpha, a grazer-eater, not a monarch. Lore: 'Lift it, and ... the yellow of high summer rises in you ... and the earth itself consents to your passage' makes the emblem a power source, which §2.8 forbids outright: panels are the run's only power source and an emblem grants nothing. Formatting: 51 words against a 24-word cap, and 'Lift it' is exactly the second-person instruction the guide bans — describe the horn, not what the player does with it. Fix by cutting to one flat, physical sentence under 24 words about a horn off a dead Clash Yellow Alpha, with no promise attached.

Violations:
  - [C1_tone] 'whose bones the prairie still bows toward' — Mystical reverence toward a corpse; the game treats bodies as meat and material, not objects of homage.
  - [C1_tone] 'whose hooves wrote thunder across the grasslands' — Epic-poetic abstraction. Shipped lines stay concrete and unflattering — 'Rolls downhill faster than it ever runs uphill'.
  - [C1_tone] 'the trampled fields remember their sovereign' — Sentimental memorial register plus implied kingdom; there is no kingdom and nothing mourns the eaten.
  - [C1_tone] 'like a war-hymn' — Ceremonial/hymnal simile. The tone brief is primal, crude, comedic — faintly disgusting, not liturgical.
  - [C1_tone] 'the earth itself consents to your passage' — Destiny/anointment language. You are not chosen and nothing consents; you are trying to sit on top of the food chain.
  - [C2_vocabulary] 'The Aureate Horn' — 'Aureate' is artefact-catalogue diction standing in for the family name Yellow, which is the only word this game has for that colour.
  - [C2_vocabulary] 'the last king of the herd' — Monarchy imported from another genre; the top creature of a biome is an Alpha, and rank is limb count from breeding, not a throne.
  - [C2_vocabulary] 'their sovereign' — Same invented royalty, repeated; no shipped line grants any creature a title beyond Alpha.
  - [C2_vocabulary] 'Lift it, and ... the yellow of high summer rises in you ... and the earth itself consents to your passage' — Breaks §2.8: panels are the run's only power source and an emblem grants nothing. This makes the trophy a buff item.
  - [C3_formatting] 'Hewn from the last king of the herd, ... the earth itself consents to your passage.' — 51 words against a 24-word maximum; the longest authored line in the corpus is 23 and the mean is 10.6.
  - [C3_formatting] 'Lift it, and' — Second-person instruction telling the player what to do with the object, explicitly banned; describe the thing instead.
```
