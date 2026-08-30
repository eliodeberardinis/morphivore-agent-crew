"""
Morphivore — emblem GER pipeline
================================

Generate → Evaluate → Refine, with a circuit breaker, for the one file in the
game's §3.3 content contract that was never written: `emblems.json`.

    python forge.py                 # run the loop, write output/emblems.json
    python forge.py --deploy        # ...and copy it into Assets/StreamingAssets
    python forge.py --adversarial   # prove the Evaluator fires (see README)

The loop, per emblem:

    generate ──▶ evaluate ──▶ pass? ──▶ accept
                    ▲           │
                    │           ▼ fail
                 refine ◀── circuit breaker (accept / refine / escalate)

Generation is one pass over the whole roster so the 25 read as a set.
Everything after that is per-record: each emblem is evaluated, refined and
judged on its own, because a failure in one is not a reason to re-author the
other twenty-four.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import circuit_breaker
import contract
import evaluator
import generator
import refiner
from circuit_breaker import History
from common import LOG, RUNS_DIR, USAGE, CONTENT_DIR, write_json

OUT_DIR = Path(__file__).resolve().parent / "output"


def _evaluate(record: dict, alpha: dict) -> list:
    """Both layers. Code first — it is free, and it catches the crude failures
    before a model is asked to think about them."""
    failures = evaluator.check_record(record)
    # Only ask the verifier once the record is structurally sane; judging the
    # meaning of a record with a missing flavour field is wasted money.
    if not any(f.check.startswith(("schema.", "text.empty")) for f in failures):
        failures += evaluator.verify(record, alpha)
    return failures


def process(record: dict) -> dict:
    """Run one emblem through the loop until it is accepted or escalated."""
    alphas = contract.world()["alphas"]
    alpha = alphas.get(record.get("alpha_id")) or {
        # Named so an escalation says which Alpha was missing rather than "?".
        "name": f"(no such Alpha: {record.get('alpha_id')!r})",
        "family": "?", "biome": "?", "flavor": "",
        "drops_emblem": False, "emblem_grants_power": False,
        "opens_biome": None,
    }
    history = History(str(record.get("id", "unknown")))
    passes = 0
    note = ""

    while True:
        failures = _evaluate(record, alpha)
        verdict = circuit_breaker.assess(history, failures, passes)
        history.attempts.append({"pass": passes, "record": dict(record),
                                 "failures": failures, "note": note})

        if verdict.action != "refine":
            return {"record": record, "history": history, "verdict": verdict,
                    "accepted": verdict.action == "accept",
                    "passes": passes, "alpha": alpha}

        passes += 1
        patched = refiner.refine(record, failures, passes)
        note = patched.pop("_note", "")
        record = patched


def run(deploy: bool, adversarial: bool) -> int:
    run_dir = RUNS_DIR / datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    LOG.open(run_dir, "Emblem GER pipeline"
             + (" — ADVERSARIAL PROBE" if adversarial else ""))

    # -- the rule being enforced, quoted so the log proves what it was -------- #
    LOG.stage("The rule (retrieved from the GDD, not hardcoded)")
    r = contract.rule()
    for q in r["verbatim"]:
        LOG.write(f'- "{q}"')
    LOG.write(f"\nRetrieved from sections: "
              f"{', '.join(p['section'] for p in r['passages'])}")
    if not r["found_all"]:
        LOG.write("\n**WARNING** — a rule quote was not found verbatim in the "
                  "GDD. The design may have changed; check before trusting "
                  "this run.")

    # -- generate ------------------------------------------------------------ #
    LOG.stage("Generate")
    if adversarial:
        import adversarial as adv
        records = adv.generate()
        LOG.write(f"Adversarial probe: {len(records)} emblems written to "
                  f"*violate* the rule, to prove the Evaluator fires.")
    else:
        records = generator.generate()
        LOG.write(f"Generated **{len(records)} emblems** in one pass.")
    write_json(run_dir / "generated-raw.json", {"emblems": records})
    LOG.write(f"Raw output (pre-evaluation) saved to `generated-raw.json`.")

    # -- evaluate + refine, per record --------------------------------------- #
    LOG.stage("Evaluate → Refine")
    if not records:
        LOG.write("Generator returned nothing; aborting.")
        return 1

    # First record alone so the verifier's cached rule prefix is written once,
    # then the rest fan out against it.
    results = [process(records[0])]
    if len(records) > 1:
        with ThreadPoolExecutor(max_workers=5) as pool:
            results += list(pool.map(process, records[1:]))

    clean_first_pass = [r for r in results
                        if r["passes"] == 0 and r["accepted"]]
    repaired = [r for r in results if r["passes"] > 0 and r["accepted"]]
    escalated = [r for r in results if not r["accepted"]]

    LOG.write(f"\n- **{len(clean_first_pass)}** passed on the first evaluation")
    LOG.write(f"- **{len(repaired)}** failed, then were repaired by the Refiner")
    LOG.write(f"- **{len(escalated)}** escalated to the developer")

    # What the Evaluator actually caught -- the point of the whole exercise.
    caught: dict[str, int] = {}
    for res in results:
        for f in res["history"].attempts[0]["failures"]:
            caught[f.check] = caught.get(f.check, 0) + 1
    if caught:
        LOG.write("\n**Caught on the generator's first output:**\n")
        for check, n in sorted(caught.items(), key=lambda kv: -kv[1]):
            layer = next(f.layer for res in results
                         for f in res["history"].attempts[0]["failures"]
                         if f.check == check)
            LOG.write(f"| `{check}` | {layer} | {n} |")
    else:
        LOG.write("\nThe generator's first output passed every check.")

    for res in repaired:
        first = res["history"].attempts[0]
        LOG.write(f"\n**{res['history'].emblem_id}** — fixed in "
                  f"{res['passes']} pass(es)", echo=False)
        LOG.write(f"- was: {first['record'].get('flavor')!r}", echo=False)
        LOG.write(f"- failed: "
                  f"{', '.join('`'+f.check+'`' for f in first['failures'])}",
                  echo=False)
        LOG.write(f"- now: {res['record'].get('flavor')!r}", echo=False)

    # -- set-level ----------------------------------------------------------- #
    LOG.stage("Set-level checks")
    accepted = [res["record"] for res in results if res["accepted"]]
    set_failures = evaluator.check_set(accepted)
    if set_failures:
        for f in set_failures:
            LOG.write(f"- **{f.check}** — {f.message}")
    else:
        LOG.write(f"All set-level checks pass: {len(accepted)} emblems, "
                  f"one per Alpha, ids and names unique.")

    # -- escalations --------------------------------------------------------- #
    if escalated:
        LOG.stage("Escalated to the developer")
        report = ["# Escalations", "",
                  "The loop could not satisfy these without help.", ""]
        for res in escalated:
            report.append(circuit_breaker.problem_statement(
                res["history"], res["verdict"], res["alpha"]))
            report.append("")
            LOG.write(f"- `{res['history'].emblem_id}` — {res['verdict'].trip}: "
                      f"{res['verdict'].reason[:120]}")
        (run_dir / "escalations.md").write_text("\n".join(report))
        LOG.write(f"\nFull problem statements: `escalations.md`")

    # -- output -------------------------------------------------------------- #
    payload = {
        "generated_by": "Morphivore emblem GER pipeline (Assignment #6)",
        "rule_enforced": r["verbatim"][0] if r["verbatim"] else "",
        "count": len(accepted),
        "emblems": sorted(accepted, key=lambda e: str(e.get("id"))),
    }
    write_json(run_dir / "emblems.json", payload)
    if not adversarial and not escalated and not set_failures:
        write_json(OUT_DIR / "emblems.json", payload)
        LOG.write(f"\nWrote `output/emblems.json` ({len(accepted)} emblems).")
        if deploy:
            shutil.copyfile(OUT_DIR / "emblems.json",
                            CONTENT_DIR / "emblems.json")
            LOG.write(f"Deployed to `Assets/StreamingAssets/emblems.json` — the "
                      f"§3.3 content contract is now complete.")
    elif escalated or set_failures:
        LOG.write("\nHeld back from output/: the run did not close cleanly. "
                  "Resolve the escalations first.")

    LOG.stage("Cost")
    LOG.write("```\n" + USAGE.summary() + "\n```")
    print(f"\nRun artifacts: {run_dir}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deploy", action="store_true",
                    help="copy a clean result into Assets/StreamingAssets/")
    ap.add_argument("--adversarial", action="store_true",
                    help="generate deliberately rule-breaking emblems to prove "
                         "the Evaluator catches them; never deploys")
    return run(**vars(ap.parse_args()))


if __name__ == "__main__":
    sys.exit(main())
