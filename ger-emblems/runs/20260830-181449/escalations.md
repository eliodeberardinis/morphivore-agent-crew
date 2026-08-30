# Escalations

The loop could not satisfy these without help.

### `emblem_prairies_green` — escalated (regressing)

**Alpha:** ? (?, ?)
**Why the loop stopped:** Refining introduced ['voice.not_a_trophy'] — checks that were passing before this pass. The record is being re-authored rather than patched, so further passes are likely to keep trading one failure for another.

**What each pass produced:**

- **Pass 0** — name "The Green One's Tooth", flavour 'From an animal that does not exist.'
  - failed: `world.alpha_exists`
- **Pass 1** — name "The Green One's Tooth", flavour 'From an animal that does not exist.'
  - refiner said: Pointed alpha_id at the actual prairies Alpha ('alpha_prairies') instead of the nonexistent 'alpha_prairies_green'.
  - failed: `world.alpha_exists`, `voice.not_a_trophy`

**Failed in every pass:** `world.alpha_exists` — a check this record has never once satisfied is more likely a problem with the brief than with the wording.

**Decide:** accept as-is, hand-write this one, loosen the check if it is wrong, or fix the contract it is enforcing.
