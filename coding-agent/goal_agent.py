"""
Morphivore — goal-oriented coding agent
=======================================

Reads the game's design document, scans the game's codebase, works out what the
design asks for that the code does not do, decides what to build first, and
builds it.

    python goal_agent.py --discover                 # stages 1-4, no code written
    python goal_agent.py --build                    # stages 1-5
    python goal_agent.py --build --goal colour-buffer --brief-plan
    python goal_agent.py --discover --scope 2.3,2.4,2.5

Five stages, each in its own module:

    1  gdd_reader     design prose      -> requirements.json
    2  code_scanner   Assets/Scripts    -> inventory.json      (no model call)
    3  gap_detector   the two, compared -> gap-report.json
    4  prioritizer    ranked by formula -> priorities.json
    5  builder        the chosen chunk  -> C# in the project

Everything the run decides is written to `runs/<timestamp>/blackboard.md` as it
happens, and the cross-session memory in `AGENT_STATE.md` is updated at the
end. The blackboard is not a log; it is how the developer stays in control of
an agent writing into their repository.

**Discovery runs blind on purpose.** Stages 1-4 never see
`docs/4-Build-Plan/build-plan.md`, which contains a human gap analysis and
priority order for this same codebase. An agent handed that document is doing
reading comprehension, not detection. It is passed as a build brief in stage 5
only, under `--brief-plan`, once the target has been chosen independently.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import builder
import code_scanner
import gap_detector
import gdd_reader
import prioritizer
from blackboard import BB
from common import BUILD_PLAN_PATH, RUNS_DIR, USAGE


def _plan_excerpt(ids: list[str]) -> str:
    """Pull the named chunk sections out of the build plan, e.g. A1 and A2.

    Stage 5 only. This is a build brief — implementation detail for work
    already chosen — not an input to the choosing.
    """
    if not BUILD_PLAN_PATH.exists():
        return ""
    text = BUILD_PLAN_PATH.read_text()
    wanted = [i.strip().upper() for i in ids]
    out: list[str] = []
    keep = False
    for line in text.splitlines():
        heading = re.match(r"^###\s+([A-E]\d[a-z]?)\s*·", line)
        if heading:
            keep = heading.group(1).upper() in wanted
        elif line.startswith("## ") or line.startswith("---"):
            keep = False
        if keep:
            out.append(line)
    return "\n".join(out).strip()


def _compose_brief(priorities: dict, run_dir: Path, plan_chunks: list[str],
                   memory: str) -> str:
    """Assemble everything the builder needs, and nothing it does not."""
    decision = priorities["decision"]
    ranked = {r["id"]: r for r in priorities["ranked"]}
    unit_ids = decision["one_unit_of_work"] or [decision["chosen_id"]]
    unit = [ranked[i] for i in unit_ids if i in ranked]

    parts = ["# Build brief", "",
             "Implement the following chunk. It was selected by this agent's "
             "own gap analysis of the codebase against the design document.", ""]

    for r in unit:
        parts += [
            f"## {r['name']}  (GDD §{r['gdd_section']})", "",
            f"**The design requires:** {r['statement']}", "",
            f"**Working means:** {r['observable_behaviour']}", "",
            f"**Current state of the code:** {r['verdict']} — {r['reasoning']}",
        ]
        if r["what_exists_instead"]:
            parts += ["", f"**What exists instead:** {r['what_exists_instead']}"]
        if r["must_be_removed"]:
            parts += ["", "**This requires removing or rewriting existing code, "
                          "not only adding to it.**"]
        if r["acceptance_test"]:
            parts += ["", f"**Acceptance test from the design document:** "
                          f"{r['acceptance_test']}"]
        if r["data_contract"]:
            parts += ["", f"**Data it must read:** {r['data_contract']}"]
        parts.append("")

    if len(unit) > 1:
        parts += [
            "## These ship together", "",
            decision["why_first"], "",
            "Do not land one without the other — " + decision["why_not_runners_up"],
            "",
        ]

    plan = _plan_excerpt(plan_chunks) if plan_chunks else ""
    if plan:
        parts += ["## Implementation notes from the project's build plan", "",
                  "The developer's own notes on this chunk. Where these and the "
                  "design document disagree, the design document wins.", "",
                  plan, ""]

    if memory and "_Nothing yet._" not in memory.split("## BUILT")[-1][:40]:
        parts += ["## What earlier runs of this agent did", "", memory, ""]

    parts += [
        "## Codebase index", "",
        "Declarations only — read any file before you change it.", "",
        (run_dir / "inventory-digest.md").read_text(),
    ]
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--discover", action="store_true",
                      help="stages 1-4 only: find and rank gaps, write no code")
    mode.add_argument("--build", action="store_true",
                      help="stages 1-5: also implement the top-ranked chunk")
    ap.add_argument("--scope", default="",
                    help="comma-separated GDD sections to restrict to, e.g. 2.3,2.4,2.5")
    ap.add_argument("--goal", default="",
                    help="comma-separated requirement ids to build, unioned with "
                         "the unit the agent chose for itself; the blind ranking "
                         "is still computed and recorded either way")
    ap.add_argument("--brief-plan", default="",
                    help="build-plan chunk ids to include as implementation "
                         "notes in stage 5, e.g. A1,A2")
    ap.add_argument("--resume", default="",
                    help="reuse the requirements and completed judgements from "
                         "an earlier run folder (name under runs/), so an "
                         "interrupted run is not paid for twice")
    ap.add_argument("--yes", action="store_true",
                    help="skip the cost confirmation prompt")
    args = ap.parse_args()

    reuse = (RUNS_DIR / args.resume) if args.resume else None
    if reuse and not reuse.exists():
        ap.error(f"no such run to resume: {reuse}")

    scope = [s.strip() for s in args.scope.split(",") if s.strip()]
    plan_chunks = [s.strip() for s in args.brief_plan.split(",") if s.strip()]

    if not args.yes:
        print("This run calls Claude Opus 5. Discovery is roughly $1-3; a build "
              "run adds several dollars more.")
        if input("Continue? [y/N] ").strip().lower() not in ("y", "yes"):
            return 1

    run_dir = RUNS_DIR / datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    BB.open(run_dir,
            goal=args.goal or "highest-scoring gap (agent's choice)",
            mode="build" if args.build else "discover")
    memory = BB.load_state()

    # Stage 2 first in execution order: it is free, and stage 1's extraction is
    # the only thing that has to happen before the judging.
    inventory = code_scanner.run(run_dir)
    (run_dir / "inventory-digest.md").write_text(
        code_scanner.render_for_prompt(inventory))

    requirements = gdd_reader.run(run_dir, scope or None, reuse)
    findings = gap_detector.run(run_dir, requirements, inventory, reuse)
    priorities = prioritizer.run(run_dir, findings)

    decision = priorities["decision"]
    if args.goal:
        ranked = {r["id"]: r for r in priorities["ranked"]}
        wanted = [g.strip() for g in args.goal.split(",") if g.strip()]
        unknown = [g for g in wanted if g not in ranked]
        known = [g for g in wanted if g in ranked]
        if unknown:
            BB.note(f"⚠ Ignoring `{', '.join(unknown)}` — not open gaps.")
        if known:
            # Union, not replacement: the agent's own judgement about what
            # cannot ship alone is the expensive part of this run, and an
            # override that discards it would reintroduce the exact hazard
            # the agent just warned about.
            added = [g for g in known if g not in decision["one_unit_of_work"]]
            decision["one_unit_of_work"] = (
                decision["one_unit_of_work"] + added
                if decision["one_unit_of_work"] else known
            )
            decision["chosen_id"] = known[0]
            BB.note(
                f"⚠ Developer override — the chunk is widened to "
                f"{', '.join(decision['one_unit_of_work'])}"
                + (f" (added {', '.join(added)})" if added else "")
                + ". The blind ranking above stands exactly as recorded."
            )

    built: list[str] = []
    failed: list[str] = []
    if args.build:
        brief = _compose_brief(priorities, run_dir, plan_chunks, memory)
        (run_dir / "build-brief.md").write_text(brief)
        result = builder.run(run_dir, brief)
        built = [f"{f['action']} `{f['path']}` — {f['why']}" for f in result["files"]]
        if not result["files"]:
            failed.append("Build stage wrote no files.")

    top = priorities["ranked"][:5]
    BB.update_state(
        built=built,
        decisions=[decision["why_first"][:300]] if args.build else [],
        next_up=[f"{r['name']} (§{r['gdd_section']}, {r['verdict']}, "
                 f"score {r['score']:.1f})" for r in top],
        failed=failed,
    )
    BB.close(USAGE.summary())
    print(f"\nRun artifacts: {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
