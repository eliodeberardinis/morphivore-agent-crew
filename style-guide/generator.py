"""
The Generator
=============

Writes one piece of real Morphivore content — a creature or emblem flavour
line — for a named subject drawn from the game's own content files.

It has two modes, and the second is the interesting one.

`style_aware=True` is production: the generator gets the style guide, as it
would in the real pipeline.

`style_aware=False` takes an **off-brand brief** instead — a deliberately wrong
instruction, like "write it as reverent high fantasy". This is how the
demonstrations are produced. The point is not that a model can be told to write
badly; it is that the resulting text is real content for a real subject in this
game, off-brand in one specific, nameable way, so the Evaluator has something
genuine to catch and the Refiner something genuine to repair.
"""

from __future__ import annotations

import json

import style_guide
from common import CONTENT_DIR, call_json

_SCHEMA = {
    "type": "object",
    "properties": {"name": {"type": "string"}, "flavor": {"type": "string"}},
    "required": ["name", "flavor"],
    "additionalProperties": False,
}

_BASE = """\
You write flavour text for MORPHIVORE, a game where you eat creatures to take
their colour. A flavour line is one short line shown with a creature or a
trophy — what it is, or what it says about the animal it came off."""


def subjects() -> list[dict]:
    """Real subjects from the game's own content, not invented ones."""
    creatures = json.loads((CONTENT_DIR / "creatures.json").read_text())
    rows = next(v for v in creatures.values() if isinstance(v, list))
    alphas = [r for r in rows if r.get("role") == "alpha"]
    elites = [r for r in rows if r.get("role") == "elite"]
    prey = [r for r in rows if r.get("role") == "prey"]
    picks = (alphas[:1] + elites[:1] + prey[:1]) or rows[:3]
    return [{"id": r["id"], "name": r.get("name", ""),
             "family": r.get("family", ""), "role": r.get("role", ""),
             "tier": r.get("tier", "")} for r in picks]


def generate(subject: dict, *, style_aware: bool = True,
             off_brand_brief: str = "", label: str = "gen") -> dict:
    """One flavour line. With the guide, or with a deliberately wrong brief."""
    if style_aware:
        system = f"{_BASE}\n\n{style_guide.brief()}"
        instruction = "Write it in the house style."
    else:
        # No style guide at all — only the wrong instruction. Anything the
        # Evaluator catches here it catches on its own terms.
        system = _BASE
        instruction = off_brand_brief

    return call_json(
        stage=label,
        system=system,
        user=(f"Subject: {subject['name']} — a {subject.get('tier','')} "
              f"{subject.get('family','')} {subject.get('role','')} "
              f"(id {subject['id']}).\n\n{instruction}\n\n"
              f"Return a name and a flavour line."),
        schema=_SCHEMA,
        effort="medium",
    )
