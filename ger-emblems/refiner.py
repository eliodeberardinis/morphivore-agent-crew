"""
The Refiner
===========

Receives one emblem, the specific checks it failed, and the rule — and returns
the same emblem with those failures fixed. Not a rewrite.

The discipline matters more than it looks. A refiner that re-authors the record
"while it's in there" will fix the flagged problem and silently introduce a new
one somewhere the Evaluator already passed, and the loop starts chasing its own
tail. So: change only the named fields, keep everything else byte-identical,
and make the smallest edit that clears the check.

Three passes, and they are not the same prompt three times — each one is told
what the previous attempt failed to fix, so a stuck record gets progressively
tighter instruction rather than three identical rolls of the dice.
"""

from __future__ import annotations

import contract
from common import call_json

_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "alpha_id": {"type": "string"},
        "biome": {"type": "string"},
        "opens_biome": {"type": ["string", "null"]},
        "name": {"type": "string"},
        "flavor": {"type": "string"},
        "what_i_changed": {"type": "string"},
    },
    "required": ["id", "alpha_id", "biome", "opens_biome", "name", "flavor",
                 "what_i_changed"],
    "additionalProperties": False,
}

_PASS_GUIDANCE = {
    1: "Make the smallest edit that clears the failure. Prefer deleting the "
       "offending clause over rewriting the sentence.",
    2: "The previous edit did not clear it. Do not try a synonym — the problem "
       "is what the line CLAIMS, not the words it uses. Cut the claim out "
       "entirely and say what the emblem physically is instead.",
    3: "Final attempt. Rewrite the flavour from scratch as a plain physical "
       "description of the object and how it was taken off the Alpha. Make no "
       "reference to the player, to carrying or wearing it, or to any effect "
       "of any kind.",
}

_SYSTEM = """\
You are fixing one generated emblem for MORPHIVORE that failed review.

{rule}

Rules of this job:
- Change ONLY the fields named in the failures. Every other field must come \
back exactly as given.
- Do not rewrite what already passes. You are patching, not re-authoring.
- Keep the voice: primal, crude, comedic, concrete. Short.
- An emblem may be frightening, disgusting, or notorious. It may change how the \
world regards the player. It may never change what the player can do.

{guidance}

Report what you changed in `what_i_changed`, in one line."""


def refine(record: dict, failures: list, attempt: int) -> dict:
    """Patch one record against its specific failures."""
    listing = "\n".join(
        f"- [{f.check}] field `{f.field}` ({f.layer} check): {f.message}"
        for f in failures
    )
    result = call_json(
        stage=f"refine-{record.get('id', 'unknown')}-p{attempt}",
        system=_SYSTEM.format(rule=contract.rule_brief(),
                              guidance=_PASS_GUIDANCE.get(attempt,
                                                          _PASS_GUIDANCE[3])),
        user=(f"# The emblem as it stands\n\n"
              f"name: {record.get('name')!r}\n"
              f"flavor: {record.get('flavor')!r}\n"
              f"id: {record.get('id')!r}  alpha_id: {record.get('alpha_id')!r}\n"
              f"biome: {record.get('biome')!r}  "
              f"opens_biome: {record.get('opens_biome')!r}\n\n"
              f"# What review found\n\n{listing}"),
        schema=_SCHEMA,
        max_tokens=2000,
    )
    note = result.pop("what_i_changed", "")
    result["_note"] = note
    return result
