"""
Finalise a run: restore the best draft, apply the Director's prescribed
corrections deterministically, re-check, and ratify.

Why this exists. The repair loop re-authors a whole track from scratch against
the critics' feedback, and on a large corpus that trades known-good content for
new mistakes -- the live run went from 1 blocking finding to 7 that way. When a
finding already carries an exact correction ("Correction: rewrite as ... e.g.
<text>"), applying that text directly is both cheaper and safer than asking an
agent to re-author around it.

So this is the last mile: take the draft with the fewest blocking findings,
apply each recorded correction, re-run the deterministic critic, and stamp
`lore_verified` only if nothing blocking remains. Nits are kept as advisories in
the verdict; they are not repaired and they do not block.

    python finalize.py --dry-run
    python finalize.py
"""

import json
import shutil
import sys
from pathlib import Path

import tools_world as tw

# Corrections transcribed verbatim from the Director's recorded findings.
# Each entry: (file, json-pointer-ish path, expected old text, new text, finding id)
CORRECTIONS = [
    (
        "panels", "panel_red_vigour", "flavor",
        "Squeeze it before you go down. Tastes like copper and a bad decision.",
        "Ripped off something that would not lie down. Bolted on, it keeps you "
        "upright a beat longer than you deserve.",
        "panel_red_vigour: written as an activated one-shot heal, which "
        "contradicts §2.3 (only grazers refill Health), §2.1 (no use-item input "
        "exists) and §2.8 (panels are standing powers, not consumables).",
    ),
]


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

    applied, missed = [], []
    for which, obj_id, field, old, new, finding in CORRECTIONS:
        path = {"creatures": tw.CREATURES_FILE, "panels": tw.PANELS_FILE,
                "biomes": tw.BIOMES_FILE}[which]
        data = json.loads(path.read_text())
        key = {"creatures": "creatures", "panels": "panels", "biomes": "biomes"}[which]
        hit = next((o for o in data[key] if o["id"] == obj_id), None)
        if hit is None or hit.get(field) != old:
            missed.append(f"{obj_id}.{field}: expected text not found (already fixed?)")
            continue
        print(f"\n  {obj_id}.{field}")
        print(f"    before: {old}")
        print(f"    after : {new}")
        print(f"    reason: {finding[:110]}...")
        if not dry_run:
            hit[field] = new
            path.write_text(json.dumps(data, indent=2))
        applied.append(obj_id)

    print(f"\nApplied {len(applied)} correction(s); {len(missed)} skipped.")
    for m in missed:
        print(f"  - {m}")

    if dry_run:
        print("\n(dry run -- nothing written)")
        return

    qa = tw.run_qa_check()
    print(f"\nQA & Balance re-check: {qa['status'].upper()}")
    for r in qa.get("reason", []):
        print(f"  - {r}")

    verdict = json.loads((tw.VERDICT_DIR / "director-verdict.json").read_text())
    remaining = [f for f in verdict.get("findings", [])
                 if f["severity"] == "blocking" and f.get("id") not in applied]

    if qa["status"] == "pass" and not remaining:
        print("\n" + tw.stamp_lore_verified())
        summary = {
            "ratified": True,
            "basis": f"{src.name} with {len(applied)} recorded correction(s) applied",
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
