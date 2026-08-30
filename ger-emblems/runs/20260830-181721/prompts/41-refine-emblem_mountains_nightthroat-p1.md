# Prompt 41 — refine-emblem_mountains_nightthroat-p1

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

name: 'Crevice Tongue'
flavor: 'Long, grey and forked, pulled out of a throat that got used to swallowing in the dark.'
id: 'emblem_mountains_nightthroat'  alpha_id: 'alpha_mountains_purple'
biome: 'mountains'  opens_biome: 'beach'

# What review found

- [format.id_matches_alpha] field `id` (deterministic check): id is 'emblem_mountains_nightthroat' but must be 'emblem_mountains_purple' — emblem_<biome>_<family>, using the Alpha's colour family (Purple), not its name.
```
