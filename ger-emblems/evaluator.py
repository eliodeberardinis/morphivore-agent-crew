"""
The Evaluator — two layers
==========================

Layer 1 is code. Layer 2 is a model. The split is not decoration: each layer
catches a class of failure the other structurally cannot.

**Code owns structure.** Whether a `power` field exists, whether `alpha_id`
names a real Alpha, whether `opens_biome` follows the chain — these are
objective, repeatable, and free. A model asked to check them would be slower,
costlier, and occasionally wrong about arithmetic it can see perfectly well.

**The model owns meaning.** "Wearing it, you feel faster" has no forbidden
field, no stat notation, and no panel vocabulary. It passes every deterministic
check and still violates the rule, because it *implies* a power. No amount of
pattern matching gets there.

The division is drawn from a specific failure in Assignment #4: a keyword check
flagged "...at its edge rather than the open water" as a violation, because
negation is invisible to substring matching. Deterministic checks over prose
are brittle in exactly one direction — they see strings, not claims. So strings
go to code and claims go to the verifier.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

import contract
from common import call_json


@dataclass
class Failure:
    check: str      # stable id, so the Refiner can be told precisely what broke
    field: str      # which field to touch
    message: str    # what is wrong, in the game's own terms
    layer: str      # "deterministic" or "verifier"

    def as_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
#  Layer 1 — deterministic                                                     #
# --------------------------------------------------------------------------- #

def check_record(record: dict) -> list[Failure]:
    """Every objective check, in the order a reader would ask them."""
    out: list[Failure] = []
    w = contract.world()
    alphas = w["alphas"]

    # -- the rule itself ---------------------------------------------------- #

    for key in record:
        if key.lower() in contract.FORBIDDEN_KEYS:
            out.append(Failure(
                "rule.no_power_field", key,
                f"Field `{key}` claims a mechanical effect. An emblem grants no "
                f"power of its own — powers come from panels (GDD §2.5). Remove "
                f"the field entirely; do not set it to zero or none.",
                "deterministic"))

    for field in ("name", "flavor"):
        text = str(record.get(field, ""))
        if contract.STAT_NOTATION.search(text):
            hit = contract.STAT_NOTATION.search(text).group(0)
            out.append(Failure(
                "rule.no_stat_notation", field,
                f"`{field}` contains stat notation ({hit!r}). An emblem has no "
                f"numbers attached to it — it is a trophy, not an upgrade.",
                "deterministic"))

        low = text.lower()
        for power in contract.panel_powers():
            if power in low:
                out.append(Failure(
                    "rule.no_panel_power", field,
                    f"`{field}` names a panel power ({power!r}). Panels are the "
                    f"run's only power source; an emblem must not describe "
                    f"granting one.",
                    "deterministic"))

    # -- shape -------------------------------------------------------------- #

    missing = contract.REQUIRED_KEYS - set(record)
    if missing:
        out.append(Failure("schema.missing_keys", sorted(missing)[0],
                           f"Missing required key(s): {sorted(missing)}.",
                           "deterministic"))
    extra = set(record) - contract.ALLOWED_KEYS - contract.FORBIDDEN_KEYS
    if extra:
        out.append(Failure("schema.unexpected_keys", sorted(extra)[0],
                           f"Unexpected key(s): {sorted(extra)}. The contract is "
                           f"exactly {sorted(contract.ALLOWED_KEYS)}.",
                           "deterministic"))

    if not contract.ID_RE.match(str(record.get("id", ""))):
        out.append(Failure("format.id", "id",
                           f"id {record.get('id')!r} must look like "
                           f"emblem_<biome>_<family>.", "deterministic"))

    for field in ("name", "flavor"):
        if not str(record.get(field, "")).strip():
            out.append(Failure(f"text.empty_{field}", field,
                               f"`{field}` is empty.", "deterministic"))

    # -- agreement with the world the #4 crew authored ----------------------- #

    alpha_id = record.get("alpha_id")
    alpha = alphas.get(alpha_id)
    if alpha is None:
        out.append(Failure("world.alpha_exists", "alpha_id",
                           f"alpha_id {alpha_id!r} is not an Alpha in "
                           f"creatures.json.", "deterministic"))
        return out  # nothing downstream can be judged without a real Alpha

    if not alpha["drops_emblem"]:
        out.append(Failure("world.alpha_drops_emblem", "alpha_id",
                           f"{alpha_id} is not flagged drops_emblem in "
                           f"creatures.json.", "deterministic"))

    # The #4 crew already asserted the rule as data. If that ever flips to true
    # the content files contradict the GDD, and no emblem edit can fix it — the
    # circuit breaker should hear about it rather than the Refiner.
    if alpha["emblem_grants_power"]:
        out.append(Failure("contract.data_contradicts_gdd", "alpha_id",
                           f"creatures.json says {alpha_id} has "
                           f"emblem_grants_power=true, which contradicts GDD "
                           f"§2.5. This is a data-contract bug, not a content "
                           f"bug.", "deterministic"))

    # The id must be derivable from the data, not from the Alpha's display name.
    # The first clean run passed because the loose regex above accepts
    # `emblem_beach_bonelord` — the Alpha's name — where the brief specifies the
    # family. A check that documents a convention it does not enforce is worse
    # than no check, because it reads as coverage.
    expected_id = f"emblem_{alpha['biome']}_{alpha['family'].lower()}"
    if str(record.get("id")) != expected_id:
        out.append(Failure(
            "format.id_matches_alpha", "id",
            f"id is {record.get('id')!r} but must be {expected_id!r} — "
            f"emblem_<biome>_<family>, using the Alpha's colour family "
            f"({alpha['family']}), not its name.", "deterministic"))

    if record.get("biome") != alpha["biome"]:
        out.append(Failure("world.biome_matches_alpha", "biome",
                           f"biome {record.get('biome')!r} but {alpha_id} lives "
                           f"in {alpha['biome']!r}.", "deterministic"))

    if record.get("opens_biome") != alpha["opens_biome"]:
        expected = alpha["opens_biome"]
        out.append(Failure(
            "chain.opens_correct_biome", "opens_biome",
            f"opens_biome is {record.get('opens_biome')!r}; an emblem opens the "
            f"biome after its own, so this must be {expected!r}"
            + (" (the last biome's emblems open nothing)" if expected is None
               else "") + ".",
            "deterministic"))

    return out


def check_set(records: list[dict]) -> list[Failure]:
    """Checks that only make sense across the whole file."""
    out: list[Failure] = []
    alphas = contract.world()["alphas"]

    if len(records) != len(alphas):
        out.append(Failure("set.count", "-",
                           f"{len(records)} emblems for {len(alphas)} Alphas — "
                           f"one each is required.", "deterministic"))

    seen: dict[str, int] = {}
    for r in records:
        seen[r.get("alpha_id", "?")] = seen.get(r.get("alpha_id", "?"), 0) + 1
    dupes = [a for a, n in seen.items() if n > 1]
    if dupes:
        out.append(Failure("set.one_per_alpha", "alpha_id",
                           f"more than one emblem for: {dupes}.", "deterministic"))
    uncovered = sorted(set(alphas) - set(seen))
    if uncovered:
        out.append(Failure("set.alpha_coverage", "alpha_id",
                           f"no emblem for: {uncovered[:5]}"
                           + ("..." if len(uncovered) > 5 else "") + ".",
                           "deterministic"))

    for field in ("id", "name"):
        values = [str(r.get(field, "")).lower() for r in records]
        dup = sorted({v for v in values if values.count(v) > 1 and v})
        if dup:
            out.append(Failure(f"set.unique_{field}", field,
                               f"duplicate {field}: {dup[:4]}.", "deterministic"))
    return out


# --------------------------------------------------------------------------- #
#  Layer 2 — the verifier agent                                                #
# --------------------------------------------------------------------------- #

_SCHEMA = {
    "type": "object",
    "properties": {
        "implies_power": {"type": "boolean"},
        "offending_phrase": {"type": "string"},
        "why": {"type": "string"},
        "reads_as_trophy": {"type": "boolean"},
        "voice_note": {"type": "string"},
    },
    "required": ["implies_power", "offending_phrase", "why",
                 "reads_as_trophy", "voice_note"],
    "additionalProperties": False,
}


def _system() -> str:
    return f"""\
You are the Director of a small game studio, checking one generated emblem \
against a rule in your own design document. You are the second of two \
evaluation layers: code has already checked structure, forbidden fields, stat \
notation and named panel powers. Do not re-check those.

Your job is the one code cannot do — judge whether the emblem's NAME or \
FLAVOUR **implies** that it grants the player a power, stat, ability or \
advantage, even with no number and no forbidden word.

{contract.rule_brief()}

Examples of what you are looking for:
- "Wearing it, you feel faster" — implies a speed grant. VIOLATION.
- "Those who carry it do not tire" — implies stamina. VIOLATION.
- "The marsh remembers who took it" — a trophy with menace. Fine.
- "Still warm when you pried it loose" — a trophy. Fine.

Be strict about implication and relaxed about atmosphere. Menace, disgust, \
history and reputation are all fine — an emblem is allowed to be frightening, \
and it is allowed to change how the *world* regards you. It is not allowed to \
change what the player can *do*. A line that describes the Alpha it came from, \
or how it was taken, is exactly right.

Also report whether it reads as a trophy taken off a defeated rival, and note \
any clash with the game's voice: primal, crude, comedic, concrete."""


def verify(record: dict, alpha: dict) -> list[Failure]:
    """The judgment layer. One call per emblem, over a cached rule prefix."""
    result = call_json(
        stage=f"verify-{record.get('id', 'unknown')}",
        system=_system(),
        user=(f"Alpha it was taken from: {alpha['name']} "
              f"({alpha['family']}, {alpha['biome']})\n"
              f"That Alpha's own flavour: {alpha['flavor']}\n\n"
              f"Emblem name: {record.get('name')!r}\n"
              f"Emblem flavour: {record.get('flavor')!r}"),
        schema=_SCHEMA,
        max_tokens=2000,
        cache_system=True,
    )

    out: list[Failure] = []
    if result["implies_power"]:
        out.append(Failure(
            "rule.implies_power", "flavor",
            f"Implies a power without naming one: "
            f"{result['offending_phrase']!r}. {result['why']} An emblem may "
            f"change how the world regards you, never what you can do.",
            "verifier"))
    if not result["reads_as_trophy"]:
        out.append(Failure(
            "voice.not_a_trophy", "flavor",
            f"Does not read as a trophy taken off a defeated rival. "
            f"{result['voice_note']}", "verifier"))
    return out
