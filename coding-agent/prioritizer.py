"""
Stage 4 — prioritize
====================

Decide what to build first, and be able to show why.

The ranking is **arithmetic, not opinion**. Asking a model "what is most
important?" produces a fluent answer with nothing underneath it, and no way for
the developer to disagree with a specific term. So the order comes from a
formula over facts the earlier stages established:

    score = (1 + blocking_degree) x severity_weight / effort

- `blocking_degree` is the transitive count of requirements that cannot be
  built until this one exists, taken from the dependency graph in stage 1. It
  is counted, not estimated.
- `severity_weight` ranks the verdicts by the shape of the work they imply.
  CONTRADICTED outranks ABSENT because contradicted code must be removed as
  well as replaced, and everything built on top of it inherits the problem.
  UNCONSUMED sits just below: the expensive half is already paid for and
  sitting on disk unread.
- `effort` divides, so cheap high-leverage work rises. Stage 3 is explicitly
  asked to notice when a job is smaller than it looks.

The model's job here is narrow and comes *after* the sort: explain the ranking,
name what the top item blocks, and say whether the leader is genuinely one unit
of work or several. It never reorders the list. If a reader disagrees with the
outcome they can point at the term that produced it, which is the entire reason
for doing it this way.
"""

from __future__ import annotations

from pathlib import Path

from blackboard import BB
from common import call_json, write_json

FORMULA = "score = (1 + blocking_degree) x severity_weight / effort"

# Contradicted work must be undone before it can be redone, and anything built
# on it inherits the defect -- so it outranks work that is merely missing.
SEVERITY = {
    "CONTRADICTED": 3.0,
    "UNCONSUMED": 2.5,
    "ABSENT": 2.0,
    "PARTIAL": 1.0,
    "PRESENT": 0.0,
}
EFFORT = {"small": 1.0, "medium": 2.0, "large": 3.0}

_SCHEMA = {
    "type": "object",
    "properties": {
        "chosen_id": {"type": "string"},
        "one_unit_of_work": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Ids that must ship together with the chosen item.",
        },
        "why_first": {"type": "string"},
        "why_not_runners_up": {"type": "string"},
        "what_it_unblocks": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "disagrees_with_ranking": {"type": "boolean"},
        "disagreement": {"type": "string"},
    },
    "required": ["chosen_id", "one_unit_of_work", "why_first",
                 "why_not_runners_up", "what_it_unblocks", "risks",
                 "disagrees_with_ranking", "disagreement"],
    "additionalProperties": False,
}

_SYSTEM = f"""\
You are the technical lead choosing the next chunk of work.

A ranking has already been computed for you by this formula:

    {FORMULA}

You are NOT being asked to re-rank. The order is arithmetic over facts \
gathered from the codebase, and it stands. Your job is to explain it and to \
answer one question the formula cannot: is the top-ranked item a single \
shippable unit, or does shipping it alone leave the project in a worse state \
than before?

That second question matters. Removing a mechanism the design contradicts can \
strip out the only working version of that system, and if its replacement is a \
separate item further down the list, the two have to land together or the game \
is left with neither. When that is the case, list every id that must ship \
alongside the leader in `one_unit_of_work` (include the leader itself).

If you think the ranking is wrong, say so plainly in `disagreement` and set \
`disagrees_with_ranking`. Disagreeing is recorded, not suppressed — but it \
does not change the order, and the developer decides."""


def _transitive_blocking(findings: list[dict]) -> dict[str, int]:
    """How many requirements transitively wait on each one."""
    dependents: dict[str, list[str]] = {f["id"]: [] for f in findings}
    for f in findings:
        for dep in f["depends_on"]:
            if dep in dependents:
                dependents[dep].append(f["id"])

    def reach(start: str) -> int:
        seen: set[str] = set()
        stack = list(dependents[start])
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            stack.extend(dependents.get(node, []))
        return len(seen)

    return {f["id"]: reach(f["id"]) for f in findings}


def run(run_dir: Path, findings: list[dict]) -> dict:
    BB.stage(4, "Prioritize")

    blocking = _transitive_blocking(findings)
    scored = []
    for f in findings:
        severity = SEVERITY[f["verdict"]]
        effort = EFFORT[f["effort"]]
        scored.append({
            **f,
            "blocking_degree": blocking[f["id"]],
            "severity_weight": severity,
            "effort": effort,
            "effort_label": f["effort"],
            "score": (1 + blocking[f["id"]]) * severity / effort,
        })

    done = [s for s in scored if s["verdict"] == "PRESENT"]
    ranked = sorted((s for s in scored if s["verdict"] != "PRESENT"),
                    key=lambda s: -s["score"])

    BB.note(f"{len(done)} requirement(s) already satisfied and excluded from "
            f"the ranking; {len(ranked)} open.")
    BB.record_scores(ranked, FORMULA)

    top = ranked[:8]
    listing = "\n\n".join(
        f"{i}. **{r['name']}** (id `{r['id']}`, GDD {r['gdd_section']}) — "
        f"score {r['score']:.1f}\n"
        f"   - verdict {r['verdict']} ({r['confidence']} confidence), "
        f"blocks {r['blocking_degree']}, effort {r['effort_label']}\n"
        f"   - {r['reasoning']}\n"
        f"   - requires removing existing code: "
        f"{'yes' if r['must_be_removed'] else 'no'}"
        for i, r in enumerate(top, 1)
    )

    decision = call_json(
        stage="prioritize",
        system=_SYSTEM,
        user=f"# Ranked open gaps\n\n{listing}",
        schema=_SCHEMA,
        effort="high",
    )

    chosen = next((r for r in ranked if r["id"] == decision["chosen_id"]), ranked[0])
    decision["chosen_id"] = chosen["id"]

    BB.record_reasoning(
        f'Chosen: {chosen["name"]} (§{chosen["gdd_section"]}, score {chosen["score"]:.1f})',
        decision["why_first"],
    )
    if decision["one_unit_of_work"]:
        names = [next((r["name"] for r in ranked if r["id"] == i), i)
                 for i in decision["one_unit_of_work"]]
        BB.note("Must ship together: " + " + ".join(f"**{n}**" for n in names))
    BB.record_reasoning("Why not the runners-up", decision["why_not_runners_up"])
    if decision["what_it_unblocks"]:
        BB.record_reasoning("What this unblocks",
                            "\n".join(f"- {x}" for x in decision["what_it_unblocks"]))
    if decision["risks"]:
        BB.record_reasoning("Risks going in",
                            "\n".join(f"- {x}" for x in decision["risks"]))
    if decision["disagrees_with_ranking"]:
        BB.record_reasoning("⚠ The agent disagrees with its own ranking",
                            decision["disagreement"])

    payload = {"formula": FORMULA, "ranked": ranked, "satisfied": done,
               "decision": decision}
    write_json(run_dir / "priorities.json", payload)
    return payload
