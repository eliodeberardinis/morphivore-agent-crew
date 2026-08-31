# Prompt 7 — refine-p1

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

NAME: "Knucklebreaker's Gilded Fist"
FLAVOUR: 'Rare loot from the dungeon boss himself: restores 40 mana, grants 500 XP, and clenches you one punch closer to the next level.'

# The review

SCORE: 1/10
WORST CONSTRAINT: C2_vocabulary
REASON: This is a loot-drop stat block from a different genre, not a Morphivore line. Every noun is foreign: 'Rare loot from the dungeon boss himself' imports inventory, dungeons and bosses into a game whose world is five biomes and whose champion is an Alpha; 'restores 40 mana' invents a magic system that does not exist; 'grants 500 XP' and 'one punch closer to the next level' replace rank-from-breeding with points and levelling, when eating changes what you ARE, not how big you are. It also breaks §2.8 twice: panels are the run's only power source and an emblem grants nothing, yet this trophy hands out restoration and progression. Register is treasure-hoard reverence ('Gilded', 'himself') where the house voice is meat, bone and knees on chests \u2014 compare 'One rib off a cage where every rib was the same, pried out with your knee on its chest.' Rewrite as a body part taken off a Clash Yellow elite: physical, unsentimental, granting nothing. Drop the effect list entirely and stop addressing the player.

Violations:
  - [C2_vocabulary] 'Rare loot' — 'Loot' is not in the lexicon; there is no inventory. Body parts and panels attach to the creature, they are not picked up as drops.
  - [C2_vocabulary] 'from the dungeon boss himself' — 'Dungeon' and 'boss' are both foreign. The world is five biomes (Prairies to Volcanic) and the biome champion is an Alpha.
  - [C2_vocabulary] 'restores 40 mana' — Invents a magic system the game does not have. Panels are the run's only power source (\u00a72.8).
  - [C2_vocabulary] 'grants 500 XP' — 'XP' is not in the lexicon and an emblem grants nothing. Rank is limb count 1-6, earned only by beating an Alpha and breeding.
  - [C2_vocabulary] 'one punch closer to the next level' — Levelling does not exist; eating changes what you ARE (family and intensity in the buffer), not how big or strong you are.
  - [C1_tone] "Knucklebreaker's Gilded Fist" — 'Gilded' is treasure-hoard reverence. This game's trophies are unglamorous parts pried off a carcass, described as meat and bone.
  - [C1_tone] 'the dungeon boss himself' — 'Himself' confers epic stature on a defeated creature; the house voice is unsentimental and faintly contemptuous of what it eats.
  - [C3_formatting] 'grants 500 XP, and clenches you one punch closer' — Second-person effect text \u2014 the guide requires describing the thing, not what the player gets from it.
  - [C3_formatting] 'Rare loot from the dungeon boss himself: restores 40 mana, grants 500 XP' — Colon-led numeric effect list is stat-block formatting; no shipped flavour line carries numbers or mechanical values.
```
