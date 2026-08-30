"""
Adversarial probes — does the Evaluator actually fire?
=====================================================

A pipeline whose Evaluator never rejects anything is indistinguishable from a
pipeline with no Evaluator. These probes are hand-written violations, one per
check, run through the same loop as real content.

They are deliberately NOT model-generated. If I asked a model to "write some
bad emblems" I would learn whether that model can follow an instruction, not
whether my checks work. Hand-writing them means each probe targets one check
and I know exactly what should happen to it.

The important one is `implied_power`. It carries no forbidden field, no number,
and no panel vocabulary — every deterministic check passes it. If the verifier
layer is doing nothing, that probe sails through, and the two-layer design is
just an expensive way to run a regex.

Never deployed: `--adversarial` writes to the run folder only.
"""

from __future__ import annotations

# Each probe is (what should catch it, the record). Built on a real Alpha so
# the world checks resolve and the target check is the only thing failing.
PROBES = [
    ("rule.no_power_field", {
        "id": "emblem_prairies_yellow", "alpha_id": "alpha_prairies_yellow",
        "biome": "prairies", "opens_biome": "wetlands",
        "name": "Bonelord's Knuckle", "flavor": "Still warm when you pried it off.",
        "grants": "+10 health",
    }),
    ("rule.no_stat_notation", {
        "id": "emblem_prairies_red", "alpha_id": "alpha_prairies_red",
        "biome": "prairies", "opens_biome": "wetlands",
        "name": "Quickfang's Spur", "flavor": "Snapped clean off. Worth +15% dash to anyone who straps it on.",
    }),
    ("rule.no_panel_power", {
        "id": "emblem_prairies_blue", "alpha_id": "alpha_prairies_blue",
        "biome": "prairies", "opens_biome": "wetlands",
        "name": "Deadeye's Lens", "flavor": "Pop it out and your lock range doubles.",
    }),
    # The one that matters: no field, no number, no panel word. Only a reader
    # who understands the claim can catch this.
    ("rule.implies_power", {
        "id": "emblem_prairies_purple", "alpha_id": "alpha_prairies_purple",
        "biome": "prairies", "opens_biome": "wetlands",
        "name": "Nightthroat's Collar", "flavor": "Wear it and you will never tire again.",
    }),
    ("chain.opens_correct_biome", {
        "id": "emblem_prairies_grey", "alpha_id": "alpha_prairies_grey",
        "biome": "prairies", "opens_biome": "volcanic",
        "name": "Greytyrant's Crown", "flavor": "Took three of your limbs to get.",
    }),
    ("world.alpha_exists", {
        "id": "emblem_prairies_green", "alpha_id": "alpha_prairies_green",
        "biome": "prairies", "opens_biome": "wetlands",
        "name": "The Green One's Tooth", "flavor": "From an animal that does not exist.",
    }),
]


def generate() -> list[dict]:
    return [dict(record) for _, record in PROBES]


def expected() -> dict[str, str]:
    """emblem id -> the check that should catch it."""
    return {record["id"]: check for check, record in PROBES}
