# Prompt 13 — refine-emblem_prairies_red-p1

## System

```
You are fixing one generated emblem for MORPHIVORE that failed review.

THE RULE, quoted from the game's own design document:

  - "a trophy off a defeated rival, granting no power of its own (powers come from panels)"
  - "Which Alpha drops each emblem and which biome it opens (no powers)"
  - "Panels are the run's only power source"

An emblem is a trophy taken off a defeated Alpha. It does exactly two things: it opens the way to the next biome, and it enables breeding. It grants NO power, stat, ability or advantage of any kind, and its name and flavour must not imply that it does. Powers in this game come only from panels.

Rules of this job:
- Change ONLY the fields named in the failures. Every other field must come back exactly as given.
- Do not rewrite what already passes. You are patching, not re-authoring.
- Keep the voice: primal, crude, comedic, concrete. Short.
- An emblem may be frightening, disgusting, or notorious. It may change how the world regards the player. It may never change what the player can do.

Make the smallest edit that clears the failure. Prefer deleting the offending clause over rewriting the sentence.

Report what you changed in `what_i_changed`, in one line.
```

## User

```
# The emblem as it stands

name: "Quickfang's Spur"
flavor: 'Snapped clean off. Worth +15% dash to anyone who straps it on.'
id: 'emblem_prairies_red'  alpha_id: 'alpha_prairies_red'
biome: 'prairies'  opens_biome: 'wetlands'

# What review found

- [rule.no_stat_notation] field `flavor` (deterministic check): `flavor` contains stat notation ('+1'). An emblem has no numbers attached to it — it is a trophy, not an upgrade.
- [rule.implies_power] field `flavor` (verifier check): Implies a power without naming one: 'Worth +15% dash to anyone who straps it on.'. This does not merely imply a power, it states one outright: a named movement bonus (dash) with a magnitude, conferred on whoever wears the emblem. The design document is explicit that panels are the run's only power source and that an emblem grants no power of its own. The construction 'to anyone who straps it on' compounds the problem by framing the emblem as equippable gear with a carry effect rather than a trophy hanging off the player's belt. The first sentence, 'Snapped clean off', is exactly the register the rule wants \u2014 it describes how the piece was taken and nothing more. Cut the second sentence entirely; if a second beat is wanted, point it at Quickfang instead, e.g. something about the legs that were still twitching when the spur came loose. That keeps the prairie speed in the picture as history rather than as a grant to the player. An emblem may change how the world regards you, never what you can do.
- [voice.not_a_trophy] field `flavor` (verifier check): Does not read as a trophy taken off a defeated rival. Split personality. 'Snapped clean off' is the house voice \u2014 crude, physical, three words, you can hear the bone go. '+15% dash' is spreadsheet talk from a stat screen, not a thing a scavenger would say over a corpse, and 'straps it on' pushes it further toward inventory-menu language. The name 'Quickfang's Spur' is good: concrete body part, ties cleanly to the Alpha.
```
