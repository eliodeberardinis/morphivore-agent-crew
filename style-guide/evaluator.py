"""
The Evaluator — SCORE and REASON, never pass/fail
=================================================

Grades one piece of content 1–10 against Morphivore's three constraints and
explains itself. A binary verdict would be useless to the Refiner: "fail" gives
it nothing to aim at, and it would rewrite the whole line and lose what was
already right. A score plus a reason naming the offending phrase gives it a
target.

The score is not a vibe. Each constraint is graded separately and the overall
score is the **weighted worst case**, not an average: a line that nails the
tone and invents a magic system is not a 7. Content can be off-brand in one
dimension and that alone should sink it, because in this game a single foreign
noun is the whole failure — there is no plot to absorb it.

Objective findings go in first. `style_guide.check_formatting` and
`find_foreign_words` run in code before the model is asked anything, and their
results are handed over as established fact. The model is not asked to count
words or spot "mana"; it is asked to judge register, which is the part code
cannot do.
"""

from __future__ import annotations

import style_guide
from common import call_json

ACCEPT_AT = 9   # the loop stops here

_SCHEMA = {
    "type": "object",
    "properties": {
        # No `minimum`/`maximum` here: structured outputs reject numeric
        # constraints. The 1-10 range is stated in the prompt and clamped below.
        "score": {"type": "integer"},
        "reason": {"type": "string"},
        "constraints": {
            "type": "object",
            "properties": {
                "C1_tone": {
                    "type": "object",
                    "properties": {"score": {"type": "integer"},
                                   "note": {"type": "string"}},
                    "required": ["score", "note"], "additionalProperties": False},
                "C2_vocabulary": {
                    "type": "object",
                    "properties": {"score": {"type": "integer"},
                                   "note": {"type": "string"}},
                    "required": ["score", "note"], "additionalProperties": False},
                "C3_formatting": {
                    "type": "object",
                    "properties": {"score": {"type": "integer"},
                                   "note": {"type": "string"}},
                    "required": ["score", "note"], "additionalProperties": False},
                "C4_naming": {
                    "type": "object",
                    "properties": {"score": {"type": "integer"},
                                   "note": {"type": "string"}},
                    "required": ["score", "note"], "additionalProperties": False},
            },
            "required": ["C1_tone", "C2_vocabulary", "C3_formatting",
                         "C4_naming"],
            "additionalProperties": False,
        },
        "violations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "constraint": {"type": "string"},
                    "phrase": {"type": "string"},
                    "why": {"type": "string"},
                },
                "required": ["constraint", "phrase", "why"],
                "additionalProperties": False,
            },
        },
        "worst_constraint": {"type": "string"},
    },
    "required": ["score", "reason", "constraints", "violations",
                 "worst_constraint"],
    "additionalProperties": False,
}


def _system(role: str = "") -> str:
    return f"""\
You are the Content & Tone director for MORPHIVORE, reviewing one piece of
generated content against your own style guide.

{style_guide.brief(role)}

Grade it 1-10 on each of the four constraints, then give ONE overall score.
Judge the FLAVOUR line under C1-C3 and the NAME under C4 — a name that keeps
its class convention is correct even if that convention reads as a title.

The overall score is the WEIGHTED WORST CASE, not an average. A line that nails
the tone and invents a magic system is not a 7 — the foreign vocabulary alone
sinks it, because in this game there is no dialogue or lore to absorb a wrong
noun. Take the lowest constraint score and adjust by at most one point for how
the other two read.

Scoring guide:
  10  Indistinguishable from the lines already shipped.
  8-9 On-brand; at most a small wobble in rhythm or word choice.
  5-7 Recognisably this game, but one constraint is clearly breached.
  2-4 Off-brand: wrong register, or vocabulary from a different genre.
  1   Could be from any game. Nothing identifies it as Morphivore.

Name the worst constraint by id (C1_tone, C2_vocabulary, C3_formatting or
C4_naming).

`reason` must be specific and actionable — name the offending phrase and say
what the game does instead. "The tone is wrong" is useless to whoever fixes it;
"'ancient artifact of untold power' is high-fantasy reverence, and this game's
trophies are body parts you pried off something" is not.

List every violation separately with the exact phrase. Name the worst
constraint by id (C1_tone, C2_vocabulary or C3_formatting)."""


def evaluate(name: str, flavor: str, subject: dict) -> dict:
    """Score one piece of content, with the objective checks folded in."""
    role = subject.get("role", "")
    fmt = style_guide.check_formatting(flavor)
    foreign = style_guide.find_foreign_words(f"{name} {flavor}")
    naming = style_guide.check_name(name, role)

    established = []
    if fmt:
        established += [f"C3 formatting (measured): {f}" for f in fmt]
    if foreign:
        established += [f"C2 vocabulary: the word {w!r} is not in this game's "
                        f"lexicon — {why}" for w, why in foreign]
    if naming:
        established += [f"C4 naming (measured): {n}" for n in naming]
    established_block = ("\n".join(f"  - {e}" for e in established)
                         if established
                         else "  - none; the objective checks all pass")

    result = call_json(
        stage=f"evaluate-{subject.get('id', 'x')}",
        system=_system(role),
        user=(f"Subject: {subject.get('name','')} — a {subject.get('tier','')} "
              f"{subject.get('family','')} {subject.get('role','')}\n\n"
              f"NAME: {name!r}\n"
              f"FLAVOUR: {flavor!r}\n\n"
              f"Objective checks already run in code (treat as established "
              f"fact, do not re-derive):\n{established_block}\n\n"
              f"Grade it."),
        schema=_SCHEMA,
        cache_system=True,
    )

    # The schema cannot bound the range, so bound it here.
    result["score"] = max(1, min(10, int(result["score"])))
    for c in result["constraints"].values():
        c["score"] = max(1, min(10, int(c["score"])))

    result["objective_findings"] = established
    return result


def render(result: dict) -> str:
    """The Evaluator's verdict in the format the assignment asks for."""
    c = result["constraints"]
    return (f"SCORE: {result['score']}/10  "
            f"(C1 tone {c['C1_tone']['score']}, "
            f"C2 vocabulary {c['C2_vocabulary']['score']}, "
            f"C3 formatting {c['C3_formatting']['score']}, "
            f"C4 naming {c['C4_naming']['score']})\n"
            f"REASON: {result['reason']}")
