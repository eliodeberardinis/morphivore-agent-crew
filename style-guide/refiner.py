"""
The Refiner
===========

Takes the content and the Evaluator's REASON, and rewrites it to score 10.

It is given the reason, the per-violation list and the worst constraint — not
just "this failed". That is the whole argument for scoring over pass/fail: the
Refiner is aimed at a named phrase and told what the game does instead, so it
can repair the line rather than replace it.

One rule it is held to: keep whatever already worked. A refiner that re-rolls
the whole line will fix the flagged problem and quietly lose the one good image
in it — and on the next pass the Evaluator marks down something that was fine
before. That is the regression the Assignment #6 circuit breaker exists to
catch, and it is cheaper to prevent here than to detect there.
"""

from __future__ import annotations

import style_guide
from common import call_json

_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "flavor": {"type": "string"},
        "what_i_changed": {"type": "string"},
    },
    "required": ["name", "flavor", "what_i_changed"],
    "additionalProperties": False,
}

_PASS_GUIDANCE = {
    1: "Make the smallest change that clears the violations. Keep any phrase "
       "that already sounds like this game.",
    2: "The previous rewrite did not clear it. Stop reaching for a better "
       "adjective — the problem is the register and the nouns, not the "
       "polish. Describe the physical thing plainly: what it is, what it "
       "smells like, how it came off the animal.",
    3: "Final attempt. Write one short concrete sentence about a body part and "
       "nothing else. No adjectives of grandeur, no reference to the player, "
       "no effect of any kind.",
}

_SYSTEM = """\
You are rewriting one piece of MORPHIVORE content that failed style review.

{guide}

{guidance}

Rules of this job:
- Fix exactly what the review names. Keep everything that already worked —
  if one image in the line is right, it survives the rewrite.
- Rewrite so it would score 10/10 against the guide above.
- Return the name too; change it only if the review flagged it.

Report what you changed in `what_i_changed`, in one line."""


def refine(name: str, flavor: str, verdict: dict, attempt: int,
           role: str = "") -> dict:
    """Rewrite from the Evaluator's reason."""
    violations = "\n".join(
        f"  - [{v['constraint']}] {v['phrase']!r} — {v['why']}"
        for v in verdict.get("violations", [])
    ) or "  - (see the reason below)"

    return call_json(
        stage=f"refine-p{attempt}",
        system=_SYSTEM.format(guide=style_guide.brief(role),
                              guidance=_PASS_GUIDANCE.get(attempt,
                                                          _PASS_GUIDANCE[3])),
        user=(f"# The content as it stands\n\n"
              f"NAME: {name!r}\nFLAVOUR: {flavor!r}\n\n"
              f"# The review\n\n"
              f"SCORE: {verdict['score']}/10\n"
              f"WORST CONSTRAINT: {verdict.get('worst_constraint','')}\n"
              f"REASON: {verdict['reason']}\n\n"
              f"Violations:\n{violations}"),
        schema=_SCHEMA,
    )
