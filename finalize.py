"""
Recover an abandoned run: re-open the best archived draft and finish it.

The repair loop in `crew_world.py` already patches in place -- `apply_fixes`
applies each blocking finding's structured `fix` verbatim, and a track is only
re-authored when no single field edit can solve the problem. This script is not
a different mechanism; it calls the same `apply_fixes`.

What it adds is the ability to pick up a run that stopped part-way -- out of
budget, interrupted, or ended on a round that was worse than an earlier one.
It selects the archived draft with the fewest blocking findings, applies that
round's recorded fixes to it, re-runs the deterministic critic, and stamps
`lore_verified` only if nothing blocking remains. Nits are advisories: recorded,
shipped, never repaired.

    python finalize.py --dry-run
    python finalize.py
"""

import json
import shutil
import sys
from pathlib import Path

import tools_world as tw

# Fixes are no longer transcribed here. The Director emits each blocking finding
# with a structured `fix` (file / path / old / new), and `tools_world.apply_fixes`
# applies it verbatim -- the same mechanism the repair loop now uses in-flight.
# This script only chooses which archived draft to apply them to.


def best_round() -> Path:
    """The archived round with the fewest blocking findings."""
    rounds = []
    for d in sorted(tw.VERDICT_DIR.glob("round-*")):
        verdict = d / "director-verdict.json"
        if not verdict.exists():
            continue
        v = json.loads(verdict.read_text())
        rounds.append((v.get("blocking_count", len(v.get("reason", []))), d, v))
    if not rounds:
        raise SystemExit("No archived rounds found -- run crew_world.py first.")
    rounds.sort(key=lambda r: r[0])
    blocking, path, v = rounds[0]
    print(f"Best archived draft: {path.name} "
          f"({blocking} blocking, {v.get('nit_count', 0)} nits)")
    return path


def apply(dry_run: bool) -> None:
    src = best_round()

    if not dry_run:
        for name in ("creatures.json", "panels.json", "biomes.json"):
            if (src / name).exists():
                shutil.copyfile(src / name, tw.OUT_DIR / name)
        shutil.copyfile(src / "director-verdict.json",
                        tw.VERDICT_DIR / "director-verdict.json")
        print(f"Restored the three content files from {src.name}")

    verdict = json.loads((tw.VERDICT_DIR / "director-verdict.json").read_text())
    findings = verdict.get("findings", [])
    blocking = [f for f in findings if f["severity"] == "blocking"]

    if dry_run:
        print(f"\nWould apply fixes for {sum(1 for f in blocking if f.get('fix'))} "
              f"of {len(blocking)} blocking finding(s):")
        for f in blocking:
            fix = f.get("fix")
            if fix:
                print(f"\n  {f.get('id')}.{fix['path']}")
                print(f"    - {fix['old']}")
                print(f"    + {fix['new']}")
            else:
                print(f"\n  {f.get('id')}: no fix supplied -- needs re-authoring")
        print("\n(dry run -- nothing written)")
        return

    applied, unpatched = tw.apply_fixes(findings)
    print(f"\nApplied {len(applied)} fix(es) in place; {len(unpatched)} unpatched.")
    for f in applied:
        print(f"  ~ {f.get('id')}.{f['fix']['path']}")
        print(f"      - {f['fix']['old'][:110]}")
        print(f"      + {f['fix']['new'][:110]}")
    for f in unpatched:
        print(f"  ! {f.get('id')}: {f['skip_reason']}")

    qa = tw.run_qa_check()
    print(f"\nQA & Balance re-check: {qa['status'].upper()}")
    for r in qa.get("reason", []):
        print(f"  - {r}")

    remaining = unpatched

    if qa["status"] == "pass" and not remaining:
        print("\n" + tw.stamp_lore_verified())
        summary = {
            "ratified": True,
            "basis": f"{src.name} with {len(applied)} critic-supplied fix(es) applied in place",
            "qa": qa["status"],
            "blocking_remaining": 0,
            "nits_shipped_as_advisories": verdict.get("nit_count", 0),
        }
    else:
        print("\nNOT ratified.")
        summary = {"ratified": False, "qa": qa["status"],
                   "blocking_remaining": len(remaining)}

    (tw.OUT_DIR / "run-summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    apply("--dry-run" in sys.argv)
