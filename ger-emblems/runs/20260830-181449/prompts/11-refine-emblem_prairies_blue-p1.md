# Prompt 11 — refine-emblem_prairies_blue-p1

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

name: "Deadeye's Lens"
flavor: 'Pop it out and your lock range doubles.'
id: 'emblem_prairies_blue'  alpha_id: 'alpha_prairies_blue'
biome: 'prairies'  opens_biome: 'wetlands'

# What review found

- [rule.no_panel_power] field `flavor` (deterministic check): `flavor` names a panel power ('lock range'). Panels are the run's only power source; an emblem must not describe granting one.
- [rule.implies_power] field `flavor` (verifier check): Implies a power without naming one: 'Pop it out and your lock range doubles.'. This is the most direct kind of violation the rule exists to catch: the flavour states outright that carrying/using the emblem improves a player capability — targeting or lock-on range — and even quantifies the improvement. Emblems open a biome and enable breeding; panels are the run's only power source. A doubled lock range is a panel effect wearing an emblem's name. The fix is trivial: keep the pried-out eye, drop the benefit. Something like 'One good eye, pried out while the other was still looking' keeps the gore, the origin and the menace and grants nothing. An emblem may change how the world regards you, never what you can do.
- [voice.not_a_trophy] field `flavor` (verifier check): Does not read as a trophy taken off a defeated rival. 'Pop it out' is nicely crude and concrete and the eye-as-lens image sits well against Deadeye's own flavour, so the name is on-voice. But 'your lock range doubles' is UI jargon — 'lock range' is a stat readout, not something a prairie brawler would say, and it drags the line out of the primal register into a tooltip. Even after the power is stripped, prefer body language over system language.
```
