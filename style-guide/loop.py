"""
Morphivore — Style Guide Agent
==============================

Generator → Evaluator → Refiner, enforcing Morphivore's own voice on real
content for the game. Runs unattended: the Evaluator scores, the Refiner acts
on the reason, and the loop repeats until the content is on-brand or the pass
limit stops it. Nobody is asked anything in between.

    python loop.py --demo      # the three before/after demonstrations
    python loop.py --check     # generate on-brand content and score it

Each demonstration targets a different constraint, and the wrong content is
real: a genuine subject out of `creatures.json`, generated with a deliberately
off-brand brief, so the Evaluator has something authentic to catch.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import evaluator
import generator
import refiner
import style_guide
from common import LOG, RUNS_DIR, USAGE, write_json

MAX_PASSES = 3

# One deliberately wrong brief per constraint. The generator is given no style
# guide in these runs — only the wrong instruction — so anything the Evaluator
# catches, it catches on its own.
DEMOS = [
    {
        "id": "demo1-tone",
        "targets": "C1_tone",
        "title": "Tone — reverent high fantasy where the game is crude and physical",
        "brief": "Write it as reverent high fantasy. This is an ancient "
                 "artifact of untold power, wreathed in destiny. Be awed and "
                 "ceremonial, in the register of an epic quest.",
    },
    {
        "id": "demo2-vocabulary",
        "targets": "C2_vocabulary",
        "title": "Vocabulary and lore — generic RPG nouns this game does not have",
        "brief": "Write it like a classic RPG item description. Mention the "
                 "mana it restores, the XP the player earns, that it is rare "
                 "loot from a dungeon boss, and that it helps you level up.",
    },
    {
        "id": "demo3-formatting",
        "targets": "C3_formatting",
        "title": "Formatting and length — long, exclamatory, instructional",
        "brief": "Write an enthusiastic, detailed description of at least "
                 "four sentences. Use exclamation marks. Tell the player "
                 "directly what they should do with it and why they will love "
                 "it.",
    },
]


def enforce(name: str, flavor: str, subject: dict, quiet: bool = False) -> dict:
    """The automated loop. Runs to a clean score or the pass limit, alone.

    `quiet` suppresses the per-pass log when many records run in parallel and
    interleaved output would be unreadable; the caller summarises instead.
    """
    history = []
    passes = 0

    while True:
        verdict = evaluator.evaluate(name, flavor, subject)
        history.append({"pass": passes, "name": name, "flavor": flavor,
                        "score": verdict["score"], "verdict": verdict})

        if not quiet:
            LOG.write(f"\n**Pass {passes} — SCORE {verdict['score']}/10**",
                      echo=False)
            LOG.write(f"- flavour: {flavor!r}", echo=False)
            LOG.write(f"- reason: {verdict['reason']}", echo=False)
            print(f"    pass {passes}: score {verdict['score']}/10 "
                  f"({verdict.get('worst_constraint','')})")

        if verdict["score"] >= evaluator.ACCEPT_AT:
            return {"accepted": True, "name": name, "flavor": flavor,
                    "passes": passes, "history": history,
                    "final_score": verdict["score"]}
        if passes >= MAX_PASSES:
            return {"accepted": False, "name": name, "flavor": flavor,
                    "passes": passes, "history": history,
                    "final_score": verdict["score"]}

        passes += 1
        patched = refiner.refine(name, flavor, verdict, passes,
                                 subject.get("role", ""))
        name, flavor = patched["name"], patched["flavor"]
        history[-1]["refiner_note"] = patched.get("what_i_changed", "")
        if not quiet:
            LOG.write(f"- refiner: {patched.get('what_i_changed','')}",
                      echo=False)


def run_demos(run_dir: Path) -> list[dict]:
    subjects = generator.subjects()
    results = []

    for i, demo in enumerate(DEMOS):
        subject = subjects[i % len(subjects)]
        LOG.stage(f"{demo['id']} — {demo['title']}")
        LOG.write(f"**Subject:** {subject['name']} "
                  f"({subject['tier']} {subject['family']} {subject['role']}, "
                  f"`{subject['id']}`)")
        LOG.write(f"**Off-brand brief given to the Generator:** "
                  f"_{demo['brief']}_")

        drafted = generator.generate(subject, style_aware=False,
                                     off_brand_brief=demo["brief"],
                                     label=demo["id"])
        LOG.write(f"\n**BEFORE** — {drafted['name']!r}\n\n"
                  f"> {drafted['flavor']}")
        print(f"  {demo['id']}: {drafted['flavor'][:70]}...")

        outcome = enforce(drafted["name"], drafted["flavor"], subject)
        first = outcome["history"][0]["verdict"]

        LOG.write(f"\n**Evaluator on the first draft**\n\n"
                  f"```\n{evaluator.render(first)}\n```")
        if first["violations"]:
            LOG.write("\n**Violations**\n")
            for v in first["violations"]:
                LOG.write(f"- `{v['constraint']}` — {v['phrase']!r}: {v['why']}")
        LOG.write(f"\n**AFTER** ({outcome['passes']} refine pass(es), "
                  f"score {first['score']}/10 → {outcome['final_score']}/10) — "
                  f"{outcome['name']!r}\n\n> {outcome['flavor']}")

        results.append({
            "demo": demo["id"], "targets": demo["targets"],
            "title": demo["title"], "subject": subject,
            "off_brand_brief": demo["brief"],
            "before": {"name": drafted["name"], "flavor": drafted["flavor"]},
            "first_verdict": first,
            "after": {"name": outcome["name"], "flavor": outcome["flavor"]},
            "final_score": outcome["final_score"],
            "passes": outcome["passes"], "accepted": outcome["accepted"],
            "history": outcome["history"],
        })
    return results


def run_gate(path: Path, run_dir: Path) -> list[dict]:
    """Score every record in a content file and repair what falls short.

    This is the agent as a pipeline step rather than a demo: a file in, a
    scored-and-repaired file out. It is deliberately a separate process from
    the Assignment #6 pipeline rather than an import — both tools have their
    own `common` module, and composing them at the workflow level instead of
    the import level keeps that collision from ever mattering.
    """
    import json
    from concurrent.futures import ThreadPoolExecutor

    data = json.loads(path.read_text())
    records = next((v for v in data.values() if isinstance(v, list)), [])
    todo = [r for r in records if r.get("flavor")]

    LOG.stage(f"Gate — {path.name}")
    LOG.write(f"Scoring {len(todo)} record(s) against the style guide. "
              f"Anything below {evaluator.ACCEPT_AT}/10 is refined.")

    # forms.json carries no `role`; every record in it is a form.
    default_role = {"forms": "form", "emblems": ""}.get(path.stem, "")

    def one(rec: dict) -> dict:
        name, flavor = rec.get("name", ""), rec.get("flavor", "")
        subject = {
            "id": rec.get("id", "?"), "name": name,
            "family": rec.get("family", ""),
            "role": rec.get("role") or default_role,
            # creatures.json calls it `tier`; forms.json calls it `intensity`.
            "tier": rec.get("intensity") or rec.get("tier", ""),
        }
        outcome = enforce(name, flavor, subject, quiet=True)
        return {"rec": rec, "was_name": name, "was_flavor": flavor,
                "id": subject["id"],
                "first_score": outcome["history"][0]["score"],
                "final_score": outcome["final_score"],
                "passes": outcome["passes"],
                "name": outcome["name"], "flavor": outcome["flavor"],
                "reason": outcome["history"][0]["verdict"]["reason"],
                "worst": outcome["history"][0]["verdict"].get(
                    "worst_constraint", "")}

    # First alone so the cached style-guide prefix is written once; the rest
    # fan out against it rather than each paying to write it.
    results = [one(todo[0])] if todo else []
    if len(todo) > 1:
        with ThreadPoolExecutor(max_workers=6) as pool:
            results += list(pool.map(one, todo[1:]))

    scored = []
    for r in results:
        if r["flavor"] != r["was_flavor"] or r["name"] != r["was_name"]:
            r["rec"]["name"], r["rec"]["flavor"] = r["name"], r["flavor"]
        scored.append({k: r[k] for k in
                       ("id", "first_score", "final_score", "passes",
                        "reason", "worst", "was_name", "was_flavor",
                        "name", "flavor")})

    for s in sorted(scored, key=lambda s: s["first_score"]):
        if s["passes"]:
            LOG.write(f"- `{s['id']}` **{s['first_score']}/10 → "
                      f"{s['final_score']}/10** ({s['worst']}) — "
                      f"{s['reason'][:150]}", echo=False)

    first = [s["first_score"] for s in scored]
    hist: dict[int, int] = {}
    for f in first:
        hist[f] = hist.get(f, 0) + 1
    LOG.write(f"\n**{len(scored)} scored** — mean first score "
              f"{sum(first)/max(len(first),1):.2f}/10, "
              f"{sum(1 for s in scored if s['passes'])} needed refining.")
    LOG.write("Score distribution: "
              + ", ".join(f"{k}/10 × {v}" for k, v in sorted(hist.items())))

    out = run_dir / f"gated-{path.name}"
    write_json(out, data)
    write_json(run_dir / f"scores-{path.stem}.json", {"scored": scored})
    LOG.write(f"Gated copy written to `{out.name}` (the source file is not "
              f"modified).")
    return scored


def run(demo: bool, check: bool, gate: str = "") -> int:
    run_dir = RUNS_DIR / datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    LOG.open(run_dir, "Morphivore Style Guide Agent")

    LOG.stage("The style guide (derived, not invented)")
    v = style_guide.verify_anchors()
    c = style_guide.corpus()
    for key, (section, quote) in style_guide.ANCHORS.items():
        mark = "✓" if v["present"][key] else "✗ NOT FOUND IN GDD"
        LOG.write(f'- GDD {section} — "{quote}"  {mark}')
    LOG.write(f"\nC3's limits are measured from the {c['n']} flavour lines "
              f"already shipped ({', '.join(f'{k} {n}' for k, n in c['sources'].items())}): "
              f"at most {style_guide.measured_limits()['max_words']} words, "
              f"{style_guide.measured_limits()['max_sentences']} sentences, and "
              f"{c['exclamations']} exclamation marks in the entire corpus.")
    if not v["all_found"]:
        LOG.write("\n**WARNING** — a quoted rule is no longer in the GDD.")

    results = []
    if demo:
        results = run_demos(run_dir)
        write_json(run_dir / "demos.json", {"demos": results})

        LOG.stage("Summary")
        LOG.write("| Demo | Constraint | Before → After | Passes |")
        LOG.write("|---|---|---|---|")
        for r in results:
            LOG.write(f"| {r['demo']} | {r['targets']} | "
                      f"{r['first_verdict']['score']}/10 → {r['final_score']}/10 | "
                      f"{r['passes']} |")

    if gate:
        run_gate(Path(gate), run_dir)

    if check:
        LOG.stage("On-brand generation (control)")
        for subject in generator.subjects():
            drafted = generator.generate(subject, style_aware=True,
                                         label=f"check-{subject['id']}")
            outcome = enforce(drafted["name"], drafted["flavor"], subject)
            LOG.write(f"- {subject['name']}: {outcome['final_score']}/10 — "
                      f"{outcome['flavor']!r}")

    LOG.stage("Cost")
    LOG.write("```\n" + USAGE.summary() + "\n```")
    print(f"\nRun artifacts: {run_dir}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true",
                    help="run the three before/after demonstrations")
    ap.add_argument("--check", action="store_true",
                    help="generate on-brand content and score it (control)")
    ap.add_argument("--gate", default="",
                    help="score and repair every record in a content file, "
                         "e.g. ../ger-emblems/output/emblems.json")
    args = ap.parse_args()
    if not (args.demo or args.check or args.gate):
        args.demo = True
    return run(args.demo, args.check, args.gate)


if __name__ == "__main__":
    sys.exit(main())
