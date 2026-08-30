# Emblem GER pipeline

**Started** 2026-08-30 18:17:21

---

## The rule (retrieved from the GDD, not hardcoded)

- "a trophy off a defeated rival, granting no power of its own (powers come from panels)"
- "Which Alpha drops each emblem and which biome it opens (no powers)"
- "Panels are the run's only power source"

Retrieved from sections: 2.5, 2.5, What the agent stress-test flagged

---

## Generate

Generated **25 emblems** in one pass.
Raw output (pre-evaluation) saved to `generated-raw.json`.

---

## Evaluate → Refine


- **0** passed on the first evaluation
- **25** failed, then were repaired by the Refiner
- **0** escalated to the developer

**Caught on the generator's first output:**

| `format.id_matches_alpha` | deterministic | 25 |

**emblem_prairies_bonelord** — fixed in 1 pass(es)
- was: "The big fist-bone off its shoulder, still grass-stained from where it stood its ground and then didn't."
- failed: `format.id_matches_alpha`
- now: "The big fist-bone off its shoulder, still grass-stained from where it stood its ground and then didn't."

**emblem_prairies_quickfang** — fixed in 1 pass(es)
- was: 'A back leg that kept kicking dirt for a minute after the rest of it stopped caring.'
- failed: `format.id_matches_alpha`
- now: 'A back leg that kept kicking dirt for a minute after the rest of it stopped caring.'

**emblem_prairies_deadeye** — fixed in 1 pass(es)
- was: "Thumbed out at arm's length, which is closer than it ever wanted anything to be."
- failed: `format.id_matches_alpha`
- now: "Thumbed out at arm's length, which is closer than it ever wanted anything to be."

**emblem_prairies_nightthroat** — fixed in 1 pass(es)
- was: 'Snapped off at the gum and still beading, so hold it by the fat end.'
- failed: `format.id_matches_alpha`
- now: 'Snapped off at the gum and still beading, so hold it by the fat end.'

**emblem_prairies_greytyrant** — fixed in 1 pass(es)
- was: 'Same slab of bone left and right, which is exactly why it took so long to find the seam.'
- failed: `format.id_matches_alpha`
- now: 'Same slab of bone left and right, which is exactly why it took so long to find the seam.'

**emblem_wetlands_bonelord** — fixed in 1 pass(es)
- was: 'Knuckle bone with marsh mud rammed into every crack, because it went down face first.'
- failed: `format.id_matches_alpha`
- now: 'Knuckle bone with marsh mud rammed into every crack, because it went down face first.'

**emblem_wetlands_quickfang** — fixed in 1 pass(es)
- was: 'Webbed and torn, from something that ran across water right up until the water ran out.'
- failed: `format.id_matches_alpha`
- now: 'Webbed and torn, from something that ran across water right up until the water ran out.'

**emblem_wetlands_deadeye** — fixed in 1 pass(es)
- was: 'Peeled off the socket in one piece, sliced up from a lifetime of squinting through sharp grass.'
- failed: `format.id_matches_alpha`
- now: 'Peeled off the socket in one piece, sliced up from a lifetime of squinting through sharp grass.'

**emblem_wetlands_nightthroat** — fixed in 1 pass(es)
- was: 'The venom sac out of its neck, three fat leeches still hanging off it and unbothered.'
- failed: `format.id_matches_alpha`
- now: 'The venom sac out of its neck, three fat leeches still hanging off it and unbothered.'

**emblem_wetlands_greytyrant** — fixed in 1 pass(es)
- was: "Armour off its back, so evenly built you can't tell which half you tore first."
- failed: `format.id_matches_alpha`
- now: "Armour off its back, so evenly built you can't tell which half you tore first."

**emblem_mountains_bonelord** — fixed in 1 pass(es)
- was: 'Bone worn flat as scree from punching rock, and it never learned the rock was winning.'
- failed: `format.id_matches_alpha`
- now: 'Bone worn flat as scree from punching rock, and it never learned the rock was winning.'

**emblem_mountains_quickfang** — fixed in 1 pass(es)
- was: "Four toes' worth of hooks, all filed down to nubs by a lot of very fast bad decisions."
- failed: `format.id_matches_alpha`
- now: "Four toes' worth of hooks, all filed down to nubs by a lot of very fast bad decisions."

**emblem_mountains_deadeye** — fixed in 1 pass(es)
- was: 'The bony shelf it sighted from, cracked off with the dust of its last perch still on it.'
- failed: `format.id_matches_alpha`
- now: 'The bony shelf it sighted from, cracked off with the dust of its last perch still on it.'

**emblem_mountains_nightthroat** — fixed in 1 pass(es)
- was: 'Long, grey and forked, pulled out of a throat that got used to swallowing in the dark.'
- failed: `format.id_matches_alpha`
- now: 'Long, grey and forked, pulled out of a throat that got used to swallowing in the dark.'

**emblem_mountains_greytyrant** — fixed in 1 pass(es)
- was: "Both horns and the skull between them, matched so well you'd swear it was made to annoy you."
- failed: `format.id_matches_alpha`
- now: "Both horns and the skull between them, matched so well you'd swear it was made to annoy you."

**emblem_beach_bonelord** — fixed in 1 pass(es)
- was: 'Crusted white with shells, off an arm that spent years hitting surf and losing.'
- failed: `format.id_matches_alpha`
- now: 'Crusted white with shells, off an arm that spent years hitting surf and losing.'

**emblem_beach_quickfang** — fixed in 1 pass(es)
- was: 'Rubbed raw and smooth by wet sand, torn free while the rest of it was still sprinting.'
- failed: `format.id_matches_alpha`
- now: 'Rubbed raw and smooth by wet sand, torn free while the rest of it was still sprinting.'

**emblem_beach_deadeye** — fixed in 1 pass(es)
- was: 'The good eye gone milky at the edges, because staring down a bright shore costs you something.'
- failed: `format.id_matches_alpha`
- now: 'The good eye gone milky at the edges, because staring down a bright shore costs you something.'

**emblem_beach_nightthroat** — fixed in 1 pass(es)
- was: 'Hollow, curved, and stinking of low tide; the bite mark it left is still in your shoulder.'
- failed: `format.id_matches_alpha`
- now: 'Hollow, curved, and stinking of low tide; the bite mark it left is still in your shoulder.'

**emblem_beach_greytyrant** — fixed in 1 pass(es)
- was: 'One rib off a cage where every rib was the same, pried out with your knee on its chest.'
- failed: `format.id_matches_alpha`
- now: 'One rib off a cage where every rib was the same, pried out with your knee on its chest.'

**emblem_volcanic_bonelord** — fixed in 1 pass(es)
- was: 'Knuckle bone cooked grey through, from a thing that kept swinging in air too hot to breathe.'
- failed: `format.id_matches_alpha`
- now: 'Knuckle bone cooked grey through, from a thing that kept swinging in air too hot to breathe.'

**emblem_volcanic_quickfang** — fixed in 1 pass(es)
- was: 'Pulled hot out of the back leg, still smelling like the crust it ran across barefoot.'
- failed: `format.id_matches_alpha`
- now: 'Pulled hot out of the back leg, still smelling like the crust it ran across barefoot.'

**emblem_volcanic_deadeye** — fixed in 1 pass(es)
- was: 'Popped, cured and shrunk hard by the vents; it never once saw you get close.'
- failed: `format.id_matches_alpha`
- now: 'Popped, cured and shrunk hard by the vents; it never once saw you get close.'

**emblem_volcanic_nightthroat** — fixed in 1 pass(es)
- was: 'Cut out whole and still warm, from the last mouth on this rock that bit before it looked.'
- failed: `format.id_matches_alpha`
- now: 'Cut out whole and still warm, from the last mouth on this rock that bit before it looked.'

**emblem_volcanic_greytyrant** — fixed in 1 pass(es)
- was: 'The top of its head, thick and dull and identical all the way round, and you finally stopped looking for the soft bit.'
- failed: `format.id_matches_alpha`
- now: 'The top of its head, thick and dull and identical all the way round, and you finally stopped looking for the soft bit.'

---

## Set-level checks

All set-level checks pass: 25 emblems, one per Alpha, ids and names unique.

Wrote `output/emblems.json` (25 emblems).
Deployed to `Assets/StreamingAssets/emblems.json` — the §3.3 content contract is now complete.

---

## Cost

```
76 API calls (generate x1, refine-emblem_beach_bonelord-p1 x1, refine-emblem_beach_deadeye-p1 x1, refine-emblem_beach_greytyrant-p1 x1, refine-emblem_beach_nightthroat-p1 x1, refine-emblem_beach_quickfang-p1 x1, refine-emblem_mountains_bonelord-p1 x1, refine-emblem_mountains_deadeye-p1 x1, refine-emblem_mountains_greytyrant-p1 x1, refine-emblem_mountains_nightthroat-p1 x1, refine-emblem_mountains_quickfang-p1 x1, refine-emblem_prairies_bonelord-p1 x1, refine-emblem_prairies_deadeye-p1 x1, refine-emblem_prairies_greytyrant-p1 x1, refine-emblem_prairies_nightthroat-p1 x1, refine-emblem_prairies_quickfang-p1 x1, refine-emblem_volcanic_bonelord-p1 x1, refine-emblem_volcanic_deadeye-p1 x1, refine-emblem_volcanic_greytyrant-p1 x1, refine-emblem_volcanic_nightthroat-p1 x1, refine-emblem_volcanic_quickfang-p1 x1, refine-emblem_wetlands_bonelord-p1 x1, refine-emblem_wetlands_deadeye-p1 x1, refine-emblem_wetlands_greytyrant-p1 x1, refine-emblem_wetlands_nightthroat-p1 x1, refine-emblem_wetlands_quickfang-p1 x1, verify-emblem_beach_blue x1, verify-emblem_beach_bonelord x1, verify-emblem_beach_deadeye x1, verify-emblem_beach_grey x1, verify-emblem_beach_greytyrant x1, verify-emblem_beach_nightthroat x1, verify-emblem_beach_purple x1, verify-emblem_beach_quickfang x1, verify-emblem_beach_red x1, verify-emblem_beach_yellow x1, verify-emblem_mountains_blue x1, verify-emblem_mountains_bonelord x1, verify-emblem_mountains_deadeye x1, verify-emblem_mountains_grey x1, verify-emblem_mountains_greytyrant x1, verify-emblem_mountains_nightthroat x1, verify-emblem_mountains_purple x1, verify-emblem_mountains_quickfang x1, verify-emblem_mountains_red x1, verify-emblem_mountains_yellow x1, verify-emblem_prairies_blue x1, verify-emblem_prairies_bonelord x1, verify-emblem_prairies_deadeye x1, verify-emblem_prairies_grey x1, verify-emblem_prairies_greytyrant x1, verify-emblem_prairies_nightthroat x1, verify-emblem_prairies_purple x1, verify-emblem_prairies_quickfang x1, verify-emblem_prairies_red x1, verify-emblem_prairies_yellow x1, verify-emblem_volcanic_blue x1, verify-emblem_volcanic_bonelord x1, verify-emblem_volcanic_deadeye x1, verify-emblem_volcanic_grey x1, verify-emblem_volcanic_greytyrant x1, verify-emblem_volcanic_nightthroat x1, verify-emblem_volcanic_purple x1, verify-emblem_volcanic_quickfang x1, verify-emblem_volcanic_red x1, verify-emblem_volcanic_yellow x1, verify-emblem_wetlands_blue x1, verify-emblem_wetlands_bonelord x1, verify-emblem_wetlands_deadeye x1, verify-emblem_wetlands_grey x1, verify-emblem_wetlands_greytyrant x1, verify-emblem_wetlands_nightthroat x1, verify-emblem_wetlands_purple x1, verify-emblem_wetlands_quickfang x1, verify-emblem_wetlands_red x1, verify-emblem_wetlands_yellow x1)
  input 34,918  cache read 46,800  output 34,808
  estimated cost $1.07 on claude-opus-5
```
