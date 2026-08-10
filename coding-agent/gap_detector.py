"""
Stage 3 — detect gaps
=====================

For each requirement, decide what the codebase actually does about it.

The verdict is five-valued, and the extra three values are the whole point. A
two-valued present/absent detector is wrong about this project in both of the
ways that matter:

  * **CONTRADICTED** — the codebase implements the requirement as a *different
    mechanism*. `Creature.tier` is a progression system, so "is there
    progression?" answers yes; but it is 0-4 earned by eating, where the design
    calls for limb count 1-6 earned by breeding. That is not a partial
    implementation, it is a different game, and code built on it has to come
    out before the real thing goes in. Absent work is additive; contradicted
    work is additive plus subtractive, and it compounds while it sits there.
  * **UNCONSUMED** — the data exists and nothing loads it. Stage 2 establishes
    this deterministically via the reference graph, so the judge is told the
    fact rather than asked to guess it.
  * **PARTIAL** — present for some cases, absent for others.

The codebase inventory rides in the *system* block, identical on every call, so
it is written to the prompt cache once and read back at a tenth of the price
for every requirement after the first. That is why the first judgement is made
alone before the rest fan out: parallel calls with a cold cache would each pay
to write it.
"""

from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import code_scanner
import gdd_rag
from blackboard import BB
from common import call_json, write_json

VERDICTS = ["PRESENT", "PARTIAL", "ABSENT", "CONTRADICTED", "UNCONSUMED"]

_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": VERDICTS},
        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
        "evidence": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Concrete symbols or files from the inventory.",
        },
        "reasoning": {"type": "string"},
        "what_exists_instead": {"type": "string"},
        "must_be_removed": {"type": "boolean"},
        "effort": {"type": "string", "enum": ["small", "medium", "large"]},
        "effort_reason": {"type": "string"},
    },
    "required": ["verdict", "confidence", "evidence", "reasoning",
                 "what_exists_instead", "must_be_removed", "effort",
                 "effort_reason"],
    "additionalProperties": False,
}

_SYSTEM_HEAD = """\
You are a senior engineer auditing a Unity C# codebase against its own design \
document. You are given an index of the codebase and one design requirement. \
Decide what the code currently does about that requirement.

Choose exactly one verdict:

- PRESENT: implemented as the design describes.
- PARTIAL: implemented for some cases but not others, or missing a stated rule.
- ABSENT: nothing in the codebase addresses it.
- CONTRADICTED: the codebase implements this area of the design, but by a \
DIFFERENT MECHANISM than the one specified. Use this when code exists and \
would have to be changed or removed, not merely added to. This is the most \
consequential verdict and the easiest to miss: a system that superficially \
matches the requirement's topic but works on different rules is contradicted, \
not present.
- UNCONSUMED: the data or asset the requirement needs exists in the project, \
but no code reads it. The inventory marks these explicitly.

Judge only from the inventory you are given. It is a regex-derived index of \
declarations: type and member names are reliable, semantics are not. Cite \
concrete symbols in `evidence`. If the inventory is genuinely insufficient to \
decide, say so in `reasoning` and set confidence low — do not invent a symbol \
you cannot see.

`must_be_removed` is true when existing code must be deleted or rewritten, not \
merely extended.

`effort` estimates the work to close the gap, and `effort_reason` must justify \
it from the inventory. Look for work that is smaller than it appears: values \
already present under the wrong name, data already parsed but discarded, a \
table that is already correct and only mislabelled. Say so when you find it.

# Codebase inventory

"""


def _judge(requirement: dict, system: str) -> dict:
    # Verbatim design text for this one requirement. Stage 1's summary says
    # "stats scale with rank"; the retrieved passage says 100 -> 350. Only the
    # second lets the judge check `GameConfig.Tiers` against anything.
    passages = gdd_rag.search(
        f"{requirement['name']}. {requirement['statement']}",
        asked_by=f"gap-detector/{requirement['id']}",
        k=3,
    )
    user = (
        f"# Requirement: {requirement['name']}  (GDD {requirement['gdd_section']})\n\n"
        f"**What the design requires**\n{requirement['statement']}\n\n"
        f"**How you could tell it works in-game**\n{requirement['observable_behaviour']}\n\n"
        f"**Data it implies**\n{requirement['data_contract'] or '(none)'}\n\n"
        f"**Worked example from the document**\n{requirement['acceptance_test'] or '(none given)'}\n\n"
        f"## Verbatim design passages\n\n"
        f"Retrieved from the design document for this requirement. These are "
        f"authoritative — where they carry exact numbers, tables, or formulas, "
        f"check the code against those, not against the summary above.\n\n"
        f"{passages}\n"
    )
    verdict = call_json(
        stage=f"gap-{requirement['id']}",
        system=system,
        user=user,
        schema=_SCHEMA,
        effort="high",
        max_tokens=4000,
        cache_system=True,
    )
    return {**requirement, **verdict}


def _load_completed(reuse: Path | None) -> dict[str, dict]:
    """Judgements already paid for in an earlier run."""
    if reuse is None:
        return {}
    path = reuse / "gap-findings.jsonl"
    if not path.exists():
        return {}
    done = {}
    for line in path.read_text().splitlines():
        if line.strip():
            record = json.loads(line)
            done[record["id"]] = record
    return done


def run(run_dir: Path, requirements: list[dict], inventory: dict,
        reuse: Path | None = None) -> list[dict]:
    BB.stage(3, "Detect gaps")

    system = _SYSTEM_HEAD + code_scanner.render_for_prompt(inventory)
    completed = _load_completed(reuse)
    todo = [r for r in requirements if r["id"] not in completed]

    if completed:
        BB.note(f"Reusing {len(completed)} judgement(s) from an earlier run; "
                f"{len(todo)} still to judge.")
    BB.note(
        f"Judging {len(todo)} requirements against the inventory "
        f"(~{len(system) // 4:,} token cached prefix per call)."
    )

    # Each verdict is appended the moment it lands, so an interrupted run --
    # a rate limit, an exhausted balance, a dropped connection -- keeps
    # everything it already paid for and resumes from there.
    ledger = run_dir / "gap-findings.jsonl"
    ledger_lock = threading.Lock()
    errors: list[str] = []

    def judge_and_record(requirement: dict) -> dict | None:
        try:
            finding = _judge(requirement, system)
        except Exception as exc:
            with ledger_lock:
                errors.append(f'{requirement["id"]}: {type(exc).__name__}: {exc}')
            return None
        with ledger_lock, ledger.open("a") as fh:
            fh.write(json.dumps(finding) + "\n")
        return finding

    findings = list(completed.values())
    if todo:
        # First call alone so it writes the prompt cache; the rest read it.
        # Firing all of them at once would have every worker pay the write.
        first = judge_and_record(todo[0])
        if first:
            findings.append(first)
        if len(todo) > 1:
            with ThreadPoolExecutor(max_workers=5) as pool:
                findings += [f for f in pool.map(judge_and_record, todo[1:]) if f]

    if errors:
        BB.note(f"⚠ {len(errors)} judgement(s) failed: {errors[0]}")
        BB.detail("Failed: " + "; ".join(errors[:10]))
        # A ranking computed over a hole is worse than no ranking, because it
        # looks complete. Refuse rather than quietly under-report.
        if len(errors) > len(requirements) * 0.1:
            raise RuntimeError(
                f"{len(errors)} of {len(requirements)} judgements failed — "
                f"refusing to rank a partial picture. Completed verdicts are "
                f"saved in {ledger}; rerun with --resume {run_dir.name} to "
                f"continue without repaying for them.\nFirst error: {errors[0]}"
            )

    findings.sort(key=lambda f: [r["id"] for r in requirements].index(f["id"]))

    by_verdict: dict[str, int] = {}
    for f in findings:
        by_verdict[f["verdict"]] = by_verdict.get(f["verdict"], 0) + 1
    BB.note("Verdicts: " + ", ".join(f"**{v}** {n}" for v, n in
                                     sorted(by_verdict.items(), key=lambda kv: -kv[1])))

    BB.table(
        ["§", "Requirement", "Verdict", "Confidence", "Removal?", "Effort", "Evidence"],
        [[f["gdd_section"], f["name"], f["verdict"], f["confidence"],
          "yes" if f["must_be_removed"] else "no", f["effort"],
          ", ".join(f"`{e}`" for e in f["evidence"][:3]) or "—"]
         for f in findings],
    )

    # The two verdicts a naive detector gets wrong are worth spelling out.
    for f in findings:
        if f["verdict"] in ("CONTRADICTED", "UNCONSUMED"):
            BB.record_reasoning(
                f'{f["verdict"]} — {f["name"]} (§{f["gdd_section"]})',
                f'{f["reasoning"]}\n\n'
                + (f'_Exists instead:_ {f["what_exists_instead"]}\n'
                   if f["what_exists_instead"] else "")
                + f'_Effort:_ {f["effort"]} — {f["effort_reason"]}',
            )

    write_json(run_dir / "gap-report.json", {"findings": findings})
    return findings
