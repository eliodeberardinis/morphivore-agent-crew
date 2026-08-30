"""
The Generator
=============

Authors one emblem per Alpha, in a single pass over the whole roster so the 25
names read as a set rather than 25 unrelated inventions.

It is *told* the rule. That is deliberate and it is what a real pipeline does —
you do not withhold the spec from the author to make the reviewer look good.
The interesting question is not whether a generator can be told a rule, but
whether it holds the line across 25 records when every instinct it has about
the word "emblem" points the other way. The Evaluator exists to answer that.

Speed over polish here: broken output is expected, and catching it is the
loop's job.
"""

from __future__ import annotations

import contract
from common import call_json

_SCHEMA = {
    "type": "object",
    "properties": {
        "emblems": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "alpha_id": {"type": "string"},
                    "biome": {"type": "string"},
                    "opens_biome": {"type": ["string", "null"]},
                    "name": {"type": "string"},
                    "flavor": {"type": "string"},
                },
                "required": ["id", "alpha_id", "biome", "opens_biome",
                             "name", "flavor"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["emblems"],
    "additionalProperties": False,
}

_SYSTEM = """\
You are the Content & Tone agent for MORPHIVORE, a game where you eat creatures \
to take their colour. You are writing the game's emblems.

An emblem is what you cut off an Alpha after you knock it down and eat it. One \
per Alpha. It is proof you beat something that was, until a minute ago, the \
biggest thing in the biome.

{rule}

Voice: primal, crude, comedic, concrete. Short. The existing content sounds \
like "Hops like it just sat on a hornet's nest" and "All knuckles and no neck, \
it complains right up until it doesn't." Match that register — physical, \
unsentimental, faintly disgusting, occasionally funny. No high fantasy, no \
ceremony, no "ancient artifact" register.

Each emblem's name should be a thing you could hold, taken off that specific \
Alpha, in that specific biome. The flavour is one sentence: what it is, how it \
was taken, or what it says about the animal it came off. Not what it does for \
you — it does nothing for you.

`id` is emblem_<biome>_<family>. `biome` is the Alpha's biome. `opens_biome` is \
the biome after it, or null for the last one."""


def generate() -> list[dict]:
    """One emblem per Alpha, authored in a single pass."""
    w = contract.world()
    roster = "\n".join(
        f"- {aid}  |  {a['name']}  |  {a['family']} Alpha of "
        f"{w['biome_names'][a['biome']]}  |  biome={a['biome']}  "
        f"opens_biome={a['opens_biome']}\n"
        f"    that Alpha's flavour: {a['flavor']}"
        for aid, a in w["alphas"].items()
    )

    result = call_json(
        stage="generate",
        system=_SYSTEM.format(rule=contract.rule_brief()),
        user=(f"Write one emblem for each of these {len(w['alphas'])} Alphas. "
              f"Use the given biome and opens_biome values exactly.\n\n{roster}"),
        schema=_SCHEMA,
        max_tokens=16000,
        effort="medium",   # speed over polish; the loop is the quality gate
    )
    return result["emblems"]
