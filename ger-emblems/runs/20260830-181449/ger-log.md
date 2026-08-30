# Emblem GER pipeline — ADVERSARIAL PROBE

**Started** 2026-08-30 18:14:49

---

## The rule (retrieved from the GDD, not hardcoded)

- "a trophy off a defeated rival, granting no power of its own (powers come from panels)"
- "Which Alpha drops each emblem and which biome it opens (no powers)"
- "Panels are the run's only power source"

Retrieved from sections: 2.5, 2.5, What the agent stress-test flagged

---

## Generate

Adversarial probe: 6 emblems written to *violate* the rule, to prove the Evaluator fires.
Raw output (pre-evaluation) saved to `generated-raw.json`.

---

## Evaluate → Refine


- **0** passed on the first evaluation
- **5** failed, then were repaired by the Refiner
- **1** escalated to the developer

**Caught on the generator's first output:**

| `rule.implies_power` | verifier | 3 |
| `voice.not_a_trophy` | verifier | 3 |
| `rule.no_power_field` | deterministic | 1 |
| `rule.no_stat_notation` | deterministic | 1 |
| `rule.no_panel_power` | deterministic | 1 |
| `chain.opens_correct_biome` | deterministic | 1 |
| `world.alpha_exists` | deterministic | 1 |

**emblem_prairies_yellow** — fixed in 1 pass(es)
- was: 'Still warm when you pried it off.'
- failed: `rule.no_power_field`
- now: 'Still warm when you pried it off.'

**emblem_prairies_red** — fixed in 1 pass(es)
- was: 'Snapped clean off. Worth +15% dash to anyone who straps it on.'
- failed: `rule.no_stat_notation`, `rule.implies_power`, `voice.not_a_trophy`
- now: 'Snapped clean off. Its legs were still kicking when it came loose.'

**emblem_prairies_blue** — fixed in 1 pass(es)
- was: 'Pop it out and your lock range doubles.'
- failed: `rule.no_panel_power`, `rule.implies_power`, `voice.not_a_trophy`
- now: 'Popped out while the other eye was still looking for you.'

**emblem_prairies_purple** — fixed in 1 pass(es)
- was: 'Wear it and you will never tire again.'
- failed: `rule.implies_power`, `voice.not_a_trophy`
- now: 'Chewed through from the inside. Still stinks of the throat it came off.'

**emblem_prairies_grey** — fixed in 1 pass(es)
- was: 'Took three of your limbs to get.'
- failed: `chain.opens_correct_biome`
- now: 'Took three of your limbs to get.'

---

## Set-level checks

- **set.count** — 5 emblems for 25 Alphas — one each is required.
- **set.alpha_coverage** — no emblem for: ['alpha_beach_blue', 'alpha_beach_grey', 'alpha_beach_purple', 'alpha_beach_red', 'alpha_beach_yellow']....

---

## Escalated to the developer

- `emblem_prairies_green` — regressing: Refining introduced ['voice.not_a_trophy'] — checks that were passing before this pass. The record is being re-authored 

Full problem statements: `escalations.md`

Held back from output/: the run did not close cleanly. Resolve the escalations first.

---

## Cost

```
18 API calls (refine-emblem_prairies_blue-p1 x1, refine-emblem_prairies_green-p1 x1, refine-emblem_prairies_grey-p1 x1, refine-emblem_prairies_purple-p1 x1, refine-emblem_prairies_red-p1 x1, refine-emblem_prairies_yellow-p1 x1, verify-emblem_prairies_blue x2, verify-emblem_prairies_green x2, verify-emblem_prairies_grey x2, verify-emblem_prairies_purple x2, verify-emblem_prairies_red x2, verify-emblem_prairies_yellow x2)
  input 8,354  cache read 10,296  output 8,509
  estimated cost $0.27 on claude-opus-5
```
