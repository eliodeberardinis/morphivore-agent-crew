# Emblem GER pipeline

**Started** 2026-08-30 18:07:54

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


- **25** passed on the first evaluation
- **0** failed, then were repaired by the Refiner
- **0** escalated to the developer

The generator's first output passed every check.

---

## Set-level checks

All set-level checks pass: 25 emblems, one per Alpha, ids and names unique.

Wrote `output/emblems.json` (25 emblems).
Deployed to `Assets/StreamingAssets/emblems.json` — the §3.3 content contract is now complete.

---

## Cost

```
26 API calls (generate x1, verify-emblem_beach_bonelord x1, verify-emblem_beach_deadeye x1, verify-emblem_beach_greytyrant x1, verify-emblem_beach_nightthroat x1, verify-emblem_beach_quickfang x1, verify-emblem_mountains_bonelord x1, verify-emblem_mountains_deadeye x1, verify-emblem_mountains_greytyrant x1, verify-emblem_mountains_nightthroat x1, verify-emblem_mountains_quickfang x1, verify-emblem_prairies_bonelord x1, verify-emblem_prairies_deadeye x1, verify-emblem_prairies_greytyrant x1, verify-emblem_prairies_nightthroat x1, verify-emblem_prairies_quickfang x1, verify-emblem_volcanic_bonelord x1, verify-emblem_volcanic_deadeye x1, verify-emblem_volcanic_greytyrant x1, verify-emblem_volcanic_nightthroat x1, verify-emblem_volcanic_quickfang x1, verify-emblem_wetlands_bonelord x1, verify-emblem_wetlands_deadeye x1, verify-emblem_wetlands_greytyrant x1, verify-emblem_wetlands_nightthroat x1, verify-emblem_wetlands_quickfang x1)
  input 6,719  cache read 22,464  output 18,573
  estimated cost $0.52 on claude-opus-5
```
