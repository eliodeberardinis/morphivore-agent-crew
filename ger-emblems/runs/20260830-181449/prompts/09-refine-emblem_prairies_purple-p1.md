# Prompt 9 — refine-emblem_prairies_purple-p1

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

name: "Nightthroat's Collar"
flavor: 'Wear it and you will never tire again.'
id: 'emblem_prairies_purple'  alpha_id: 'alpha_prairies_purple'
biome: 'prairies'  opens_biome: 'wetlands'

# What review found

- [rule.implies_power] field `flavor` (verifier check): Implies a power without naming one: 'Wear it and you will never tire again.'. The line makes a direct promise about what the wearer's body can do \u2014 unlimited stamina. It is the textbook case from the design document ("Those who carry it do not tire"), just phrased in second person and with 'never...again' making it permanent. No number and no stat word, but the implication is unambiguous: the emblem is being sold as a power source, and panels are the run's only power source. An emblem may change how the world regards you, never what you can do.
- [voice.not_a_trophy] field `flavor` (verifier check): Does not read as a trophy taken off a defeated rival. Reads as a shop blurb for a magic item, not a trophy pried off a corpse. Nothing in it points back to Nightthroat, the prairie, or the kill \u2014 the collar could have come from anywhere. The Alpha's own flavour is excellent and concrete ('bites once, forgets to leave a body'); the emblem should feed off that. Something about the collar being chewed through from the inside, or the buckle being on the wrong side, or it still smelling of a throat \u2014 the object and its taking, no promises to the wearer.
```
