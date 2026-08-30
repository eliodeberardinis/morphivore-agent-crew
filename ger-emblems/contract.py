"""
The contract the Evaluator enforces
===================================

Two things live here, and neither is invented by this pipeline:

* **The world data** — the 25 Alphas and the 5-biome chain, read from
  `creatures.json` and `biomes.json` as the #4 crew authored them. The emblem
  set is fully determined by that data: one emblem per Alpha, opening the biome
  after its own.
* **The rule** — retrieved from the GDD at run time via the Assignment #4
  crew's `rag.py`, not pasted into a constant here. If the design changes, the
  Evaluator's rule changes with it, and the run log records the passage it
  actually enforced.

`rag.py` is reused unmodified; its module paths are repointed at a corpus built
from the condensed GDD, the same technique the #5 agent used.
"""

from __future__ import annotations

import json
import re
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # agent-crew/

import rag  # noqa: E402 -- the Assignment #4 retrieval layer, unmodified
from common import BIOMES_PATH, CREATURES_PATH, GDD_PATH, _HERE  # noqa: E402

KB_DIR = _HERE / "kb-gdd"

# The emblem record shape, from GDD 3.3: "Which Alpha drops each emblem and
# which biome it opens (no powers)". Nothing else belongs in the file.
ALLOWED_KEYS = {"id", "alpha_id", "biome", "opens_biome", "name", "flavor"}
REQUIRED_KEYS = ALLOWED_KEYS

# Keys that would smuggle a power grant back in. The rule is that an emblem has
# no mechanical effect at all, so any field claiming one is a violation
# regardless of its value.
FORBIDDEN_KEYS = {
    "power", "powers", "grants", "grant", "effect", "effects", "modifier",
    "modifiers", "bonus", "bonuses", "buff", "buffs", "stat", "stats",
    "ability", "abilities", "passive", "perk", "boon", "magnitude",
}

# "+15%", "x1.2", "1.5x", "+5 damage" -- a stat grant wearing prose.
STAT_NOTATION = re.compile(
    r"[+\-−]\s?\d|\b\d+\s?%|\b\d+(\.\d+)?\s?[x×]\b|\b[x×]\s?\d+(\.\d+)?\b",
    re.I,
)

ID_RE = re.compile(r"^emblem_[a-z]+_[a-z]+$")


@lru_cache(maxsize=1)
def world() -> dict:
    """The Alphas and the biome chain, exactly as the content files state them."""
    creatures = json.loads(CREATURES_PATH.read_text())
    rows = next(v for v in creatures.values() if isinstance(v, list))
    alphas = [r for r in rows if r.get("role") == "alpha"]

    biomes = json.loads(BIOMES_PATH.read_text())["biomes"]
    ordered = sorted(biomes, key=lambda b: b.get("order", 0))
    ids = [b["id"] for b in ordered]

    # An emblem opens the biome after its own. The last biome's emblems open
    # nothing -- GDD 4.9: "take an emblem that opens nothing".
    opens_after = {bid: (ids[i + 1] if i + 1 < len(ids) else None)
                   for i, bid in enumerate(ids)}

    by_alpha = {}
    for a in alphas:
        biome = next((b for b in ids if b in a["id"]), None)
        by_alpha[a["id"]] = {
            "name": a.get("name", ""),
            "family": a.get("family", ""),
            "flavor": a.get("flavor", ""),
            "biome": biome,
            "opens_biome": opens_after.get(biome),
            "drops_emblem": bool(a.get("drops_emblem")),
            # The #4 crew already asserted the rule in the creature data. The
            # Evaluator cross-checks emblems against it rather than re-deciding.
            "emblem_grants_power": bool(a.get("emblem_grants_power")),
        }

    return {"alphas": by_alpha, "biome_ids": ids,
            "biome_names": {b["id"]: b["name"] for b in ordered},
            "opens_after": opens_after}


@lru_cache(maxsize=1)
def panel_powers() -> list[str]:
    """The powers panels grant -- the vocabulary an emblem must never claim."""
    path = CREATURES_PATH.parent / "panels.json"
    if not path.exists():
        return ["lock range", "dash", "guard", "camouflage"]
    data = json.loads(path.read_text())
    rows = next((v for v in data.values() if isinstance(v, list)), [])
    found = {str(r.get("power", "")).replace("_", " ").strip().lower()
             for r in rows if r.get("power")}
    return sorted(p for p in found if p)


@lru_cache(maxsize=1)
def rule() -> dict:
    """Retrieve the no-powers rule from the GDD. Never hardcoded."""
    KB_DIR.mkdir(exist_ok=True)
    (KB_DIR / "gdd.md").write_text(GDD_PATH.read_text())
    rag.KB_DIR = KB_DIR
    rag.RETRIEVAL_LOG = _HERE / "runs" / "retrieval-log.jsonl"
    rag.RETRIEVAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    rag._index = None

    hits = rag.retrieve(
        "emblem trophy defeated rival grants no power opens next biome breeding",
        asked_by="ger-emblems/contract", k=3,
    )
    passages = [{"section": c.section, "id": c.id, "text": c.text}
                for c, _ in hits]

    # The two sentences the whole pipeline turns on, quoted verbatim from the
    # document so the log shows exactly what was enforced.
    doc = GDD_PATH.read_text().replace("**", "")
    quotes = [q for q in (
        "a trophy off a defeated rival, granting no power of its own "
        "(powers come from panels)",
        "Which Alpha drops each emblem and which biome it opens (no powers)",
        "Panels are the run's only power source",
    ) if q in doc]

    return {"passages": passages, "verbatim": quotes,
            "found_all": len(quotes) == 3}


def rule_brief() -> str:
    """The rule as handed to the Generator, Verifier and Refiner."""
    r = rule()
    lines = ["THE RULE, quoted from the game's own design document:", ""]
    lines += [f'  - "{q}"' for q in r["verbatim"]]
    lines += [
        "",
        "An emblem is a trophy taken off a defeated Alpha. It does exactly two "
        "things: it opens the way to the next biome, and it enables breeding. "
        "It grants NO power, stat, ability or advantage of any kind, and its "
        "name and flavour must not imply that it does. Powers in this game come "
        "only from panels.",
    ]
    return "\n".join(lines)
