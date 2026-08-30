# Prompt 1 — generate

## System

```
You are the Content & Tone agent for MORPHIVORE, a game where you eat creatures to take their colour. You are writing the game's emblems.

An emblem is what you cut off an Alpha after you knock it down and eat it. One per Alpha. It is proof you beat something that was, until a minute ago, the biggest thing in the biome.

THE RULE, quoted from the game's own design document:

  - "a trophy off a defeated rival, granting no power of its own (powers come from panels)"
  - "Which Alpha drops each emblem and which biome it opens (no powers)"
  - "Panels are the run's only power source"

An emblem is a trophy taken off a defeated Alpha. It does exactly two things: it opens the way to the next biome, and it enables breeding. It grants NO power, stat, ability or advantage of any kind, and its name and flavour must not imply that it does. Powers in this game come only from panels.

Voice: primal, crude, comedic, concrete. Short. The existing content sounds like "Hops like it just sat on a hornet's nest" and "All knuckles and no neck, it complains right up until it doesn't." Match that register — physical, unsentimental, faintly disgusting, occasionally funny. No high fantasy, no ceremony, no "ancient artifact" register.

Each emblem's name should be a thing you could hold, taken off that specific Alpha, in that specific biome. The flavour is one sentence: what it is, how it was taken, or what it says about the animal it came off. Not what it does for you — it does nothing for you.

`id` is emblem_<biome>_<family>. `biome` is the Alpha's biome. `opens_biome` is the biome after it, or null for the last one.
```

## User

```
Write one emblem for each of these 25 Alphas. Use the given biome and opens_biome values exactly.

- alpha_prairies_yellow  |  Bonelord of the Trampled Fields  |  Yellow Alpha of Prairies  |  biome=prairies  opens_biome=wetlands
    that Alpha's flavour: All knuckles and no neck, it complains right up until it doesn't.
- alpha_prairies_red  |  Quickfang of the Trampled Fields  |  Red Alpha of Prairies  |  biome=prairies  opens_biome=wetlands
    that Alpha's flavour: Twitchy legs, empty head, gone before you blink twice.
- alpha_prairies_blue  |  Deadeye of the Trampled Fields  |  Blue Alpha of Prairies  |  biome=prairies  opens_biome=wetlands
    that Alpha's flavour: One good eye and a better trigger; useless the second you're inside its arms.
- alpha_prairies_purple  |  Nightthroat of the Trampled Fields  |  Purple Alpha of Prairies  |  biome=prairies  opens_biome=wetlands
    that Alpha's flavour: Slinks in, bites once, forgets to leave a body.
- alpha_prairies_grey  |  Greytyrant of the Trampled Fields  |  Grey Alpha of Prairies  |  biome=prairies  opens_biome=wetlands
    that Alpha's flavour: Doesn't have a weak side, and hates that you keep looking for one.
- alpha_wetlands_yellow  |  Bonelord of the Rotting Marsh  |  Yellow Alpha of Wetlands  |  biome=wetlands  opens_biome=mountains
    that Alpha's flavour: All knuckles and no neck, it complains right up until it doesn't.
- alpha_wetlands_red  |  Quickfang of the Rotting Marsh  |  Red Alpha of Wetlands  |  biome=wetlands  opens_biome=mountains
    that Alpha's flavour: Twitchy legs, empty head, gone before you blink twice.
- alpha_wetlands_blue  |  Deadeye of the Rotting Marsh  |  Blue Alpha of Wetlands  |  biome=wetlands  opens_biome=mountains
    that Alpha's flavour: One good eye and a better trigger; useless the second you're inside its arms.
- alpha_wetlands_purple  |  Nightthroat of the Rotting Marsh  |  Purple Alpha of Wetlands  |  biome=wetlands  opens_biome=mountains
    that Alpha's flavour: Slinks in, bites once, forgets to leave a body.
- alpha_wetlands_grey  |  Greytyrant of the Rotting Marsh  |  Grey Alpha of Wetlands  |  biome=wetlands  opens_biome=mountains
    that Alpha's flavour: Doesn't have a weak side, and hates that you keep looking for one.
- alpha_mountains_yellow  |  Bonelord of the Shattered Crags  |  Yellow Alpha of Mountains  |  biome=mountains  opens_biome=beach
    that Alpha's flavour: All knuckles and no neck, it complains right up until it doesn't.
- alpha_mountains_red  |  Quickfang of the Shattered Crags  |  Red Alpha of Mountains  |  biome=mountains  opens_biome=beach
    that Alpha's flavour: Twitchy legs, empty head, gone before you blink twice.
- alpha_mountains_blue  |  Deadeye of the Shattered Crags  |  Blue Alpha of Mountains  |  biome=mountains  opens_biome=beach
    that Alpha's flavour: One good eye and a better trigger; useless the second you're inside its arms.
- alpha_mountains_purple  |  Nightthroat of the Shattered Crags  |  Purple Alpha of Mountains  |  biome=mountains  opens_biome=beach
    that Alpha's flavour: Slinks in, bites once, forgets to leave a body.
- alpha_mountains_grey  |  Greytyrant of the Shattered Crags  |  Grey Alpha of Mountains  |  biome=mountains  opens_biome=beach
    that Alpha's flavour: Doesn't have a weak side, and hates that you keep looking for one.
- alpha_beach_yellow  |  Bonelord of the Scalded Shore  |  Yellow Alpha of Beach  |  biome=beach  opens_biome=volcanic
    that Alpha's flavour: All knuckles and no neck, it complains right up until it doesn't.
- alpha_beach_red  |  Quickfang of the Scalded Shore  |  Red Alpha of Beach  |  biome=beach  opens_biome=volcanic
    that Alpha's flavour: Twitchy legs, empty head, gone before you blink twice.
- alpha_beach_blue  |  Deadeye of the Scalded Shore  |  Blue Alpha of Beach  |  biome=beach  opens_biome=volcanic
    that Alpha's flavour: One good eye and a better trigger; useless the second you're inside its arms.
- alpha_beach_purple  |  Nightthroat of the Scalded Shore  |  Purple Alpha of Beach  |  biome=beach  opens_biome=volcanic
    that Alpha's flavour: Slinks in, bites once, forgets to leave a body.
- alpha_beach_grey  |  Greytyrant of the Scalded Shore  |  Grey Alpha of Beach  |  biome=beach  opens_biome=volcanic
    that Alpha's flavour: Doesn't have a weak side, and hates that you keep looking for one.
- alpha_volcanic_yellow  |  Bonelord of the Molten Maw  |  Yellow Alpha of Volcanic  |  biome=volcanic  opens_biome=None
    that Alpha's flavour: All knuckles and no neck, it complains right up until it doesn't.
- alpha_volcanic_red  |  Quickfang of the Molten Maw  |  Red Alpha of Volcanic  |  biome=volcanic  opens_biome=None
    that Alpha's flavour: Twitchy legs, empty head, gone before you blink twice.
- alpha_volcanic_blue  |  Deadeye of the Molten Maw  |  Blue Alpha of Volcanic  |  biome=volcanic  opens_biome=None
    that Alpha's flavour: One good eye and a better trigger; useless the second you're inside its arms.
- alpha_volcanic_purple  |  Nightthroat of the Molten Maw  |  Purple Alpha of Volcanic  |  biome=volcanic  opens_biome=None
    that Alpha's flavour: Slinks in, bites once, forgets to leave a body.
- alpha_volcanic_grey  |  Greytyrant of the Molten Maw  |  Grey Alpha of Volcanic  |  biome=volcanic  opens_biome=None
    that Alpha's flavour: Doesn't have a weak side, and hates that you keep looking for one.
```
