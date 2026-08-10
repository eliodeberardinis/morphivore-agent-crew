"""
Stage 1 — read the GDD
======================

Turns design prose into a list of checkable requirements.

**Scoping is deliberate, and happens twice.** The agent is not handed the whole
design corpus:

  1. It reads the *condensed* GDD (7.4k words), which is this project's
     canonical document, not the 21k-word extended reference.
  2. Within that, it reads only the sections that describe **the game** --
     §1-§2 plus §3.3's data contract. §3 is the development team's roster, §4
     is the production plan and cut ladder, §5 is the revision log. None of
     those describe a feature, and feeding them to a feature-gap detector
     produces noise dressed up as findings.

The excluded sections are named in the blackboard rather than silently
dropped, because "what the agent was allowed to see" is part of what a reader
needs in order to trust the ranking that comes out the other end.

`--scope` narrows further to named sections, which is how the targeted build
run is pointed at the identity sections alone.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import gdd_rag
from blackboard import BB
from common import GDD_PATH, call_json, write_json

# Sections that describe the game rather than the making of it.
_DESIGN_TOPLEVEL = {"1", "2"}
_DESIGN_EXTRA_PREFIXES = ("3.3",)  # the §3.3 data contract defines the JSON files

_H2 = re.compile(r"^##\s+(?:(\d+)\.\s*)?(.+)$")
_H3 = re.compile(r"^###\s+(?:(\d+(?:\.\d+)?[a-z]?)\s+)?(.+)$")

_SCHEMA = {
    "type": "object",
    "properties": {
        "requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "gdd_section": {"type": "string"},
                    "statement": {"type": "string"},
                    "observable_behaviour": {"type": "string"},
                    "data_contract": {"type": "string"},
                    "depends_on": {"type": "array", "items": {"type": "string"}},
                    "acceptance_test": {"type": "string"},
                },
                "required": ["id", "name", "gdd_section", "statement",
                             "observable_behaviour", "data_contract",
                             "depends_on", "acceptance_test"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["requirements"],
    "additionalProperties": False,
}

_SYSTEM = """\
You are the Director of a small game studio, reading your own design document \
and turning it into a list of requirements an engineer could check off against \
a codebase.

A requirement is one mechanic, system, or data structure the game must have. \
Split at the level a developer would build at: "the colour buffer" is one \
requirement, "the game has mechanics" is not, and "the buffer holds a family \
and an intensity per limb" is a detail of the first, not a separate entry.

For each one record:
- observable_behaviour: how someone playing the game could tell it works. This \
is what makes the requirement checkable, so it must describe something visible \
or measurable, not a restatement of the design intent.
- data_contract: any JSON file, table, or persisted structure the requirement \
implies. Empty string if none.
- depends_on: ids of other requirements that must exist first. Only reference \
ids you are also emitting. Be accurate and be sparing: this field determines \
build order downstream, so a dependency you invent reorders real work.
- acceptance_test: if the document gives a worked example with concrete values, \
capture it verbatim enough to run. Empty string if it gives none.

Derive everything from the passages given. Do not import mechanics from other \
games you know, and do not infer requirements the text does not state."""


def _filter_sections(text: str, scope: list[str] | None) -> tuple[str, list[str], list[str]]:
    """Keep the design sections; report what was kept and what was dropped."""
    kept_lines: list[str] = []
    kept: list[str] = []
    dropped: list[str] = []
    top, sub, include = None, None, False

    def label(num: str | None, title: str) -> str:
        return f"§{num} {title}" if num else title

    for line in text.splitlines():
        h2, h3 = _H2.match(line), _H3.match(line)
        if h2:
            top, sub = h2.group(1), None
            include = top in _DESIGN_TOPLEVEL
            (kept if include else dropped).append(label(top, h2.group(2)))
        elif h3:
            sub = h3.group(1)
            if sub and sub.startswith(_DESIGN_EXTRA_PREFIXES):
                include = True
            elif sub:
                include = (sub.split(".")[0] in _DESIGN_TOPLEVEL)
            else:
                include = top in _DESIGN_TOPLEVEL
            if include and scope:
                include = any(sub and sub.startswith(s) for s in scope)
            (kept if include else dropped).append(label(sub, h3.group(2)))
        if include:
            kept_lines.append(line)

    return "\n".join(kept_lines), kept, dropped


def run(run_dir: Path, scope: list[str] | None = None,
        reuse: Path | None = None) -> list[dict]:
    BB.stage(1, "Read the GDD")

    text = GDD_PATH.read_text()
    scoped, kept, dropped = _filter_sections(text, scope)

    BB.note(
        f"Source: `{GDD_PATH.name}` ({len(text.split()):,} words). "
        f"After the design-section filter: **{len(scoped.split()):,} words**, "
        f"{len(kept)} sections in, {len(dropped)} out."
    )
    BB.detail("Sections read: " + ", ".join(f"`{s}`" for s in kept))
    BB.detail(
        "Sections withheld (they describe making the game, not the game): "
        + ", ".join(f"`{s}`" for s in dropped)
    )
    if scope:
        BB.note(f"Scope override active: {', '.join(scope)}")

    # Index the scoped text so later stages can pull verbatim passages -- the
    # exact tables and formulas that a distilled requirement loses.
    (run_dir / "scoped-gdd.md").write_text(scoped)
    index = gdd_rag.build_index(scoped, run_dir)
    BB.note(
        f"Indexed the scoped GDD for retrieval: {index['chunks']} chunks, "
        f"backends {', '.join(index['backends'])}."
    )

    # Extraction is deterministic in effect from one run to the next over an
    # unchanged document, so a resumed run reuses it rather than paying again.
    cached = (reuse / "requirements.json") if reuse else None
    if cached and cached.exists():
        requirements = json.loads(cached.read_text())["requirements"]
        BB.note(f"Reused {len(requirements)} requirements from `{reuse.name}` "
                f"— no extraction call made.")
    else:
        result = call_json(
            stage="gdd-read",
            system=_SYSTEM,
            user=f"# Design document (scoped)\n\n{scoped}",
            schema=_SCHEMA,
            effort="high",
        )
        requirements = result["requirements"]

    # Drop dependency edges pointing at ids that were never emitted. The graph
    # feeds the priority score, so a dangling edge would silently distort the
    # ranking; better to prune it here than to trust it downstream.
    ids = {r["id"] for r in requirements}
    pruned = 0
    for r in requirements:
        clean = [d for d in r["depends_on"] if d in ids and d != r["id"]]
        pruned += len(r["depends_on"]) - len(clean)
        r["depends_on"] = clean
    if pruned:
        BB.detail(f"Pruned {pruned} dependency edge(s) referencing unknown ids.")

    BB.note(f"Extracted **{len(requirements)} requirements**.")
    BB.table(
        ["§", "Requirement", "Depends on", "Has acceptance test"],
        [[r["gdd_section"], r["name"], ", ".join(r["depends_on"]) or "—",
          "yes" if r["acceptance_test"] else "no"] for r in requirements],
    )
    write_json(run_dir / "requirements.json", {"requirements": requirements})
    return requirements
