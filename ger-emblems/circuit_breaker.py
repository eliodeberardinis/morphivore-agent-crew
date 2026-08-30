"""
The Circuit Breaker
===================

Decides when the loop has stopped making progress and hands the problem back to
a human with enough context to act on.

A pass limit alone is a weak breaker: it waits for three failed attempts even
when the first two prove the loop cannot win. So this one trips on four
signals, three of which fire early:

* **exhausted** — three refine passes used, still failing. The plain limit.
* **oscillating** — a failure signature repeats after being cleared. The
  Refiner is cycling between two states, and a fourth pass would be a fifth.
* **regressing** — a check that previously passed now fails. Fixing A broke B,
  which means the record is being re-authored rather than patched, and more
  passes make it worse.
* **unfixable** — the failure is not in the content at all. If
  `creatures.json` ever asserts `emblem_grants_power: true`, no edit to an
  emblem can satisfy the GDD, because the *data contract* contradicts the
  design. No number of passes fixes that, and a Refiner told to try would
  quietly invent something to paper over it.

That last one is the Assignment #4 lesson made mechanical: a finding that keeps
coming back is usually a bug report about your contract, not about the content
in front of you. There, I spent several judging rounds re-authoring panels
before accepting that my own `PANEL_POWERS` list was wrong. This breaker is
built to notice that class of problem in one pass instead of four.

The escalation is a problem statement, not a stack trace: what was asked, what
each pass produced, which check failed each time, and the most likely cause.
"""

from __future__ import annotations

from dataclasses import dataclass, field

MAX_PASSES = 3

# Checks no content edit can clear, because the fault is upstream of the record.
UNFIXABLE = {"contract.data_contradicts_gdd"}


@dataclass
class History:
    """What happened to one emblem across the loop."""
    emblem_id: str
    attempts: list[dict] = field(default_factory=list)   # {pass, record, failures, note}

    def signatures(self) -> list[frozenset]:
        return [frozenset(f.check for f in a["failures"]) for a in self.attempts]


@dataclass
class Verdict:
    action: str        # "accept" | "refine" | "escalate"
    reason: str = ""
    trip: str = ""     # which signal tripped


def assess(history: History, failures: list, passes_used: int) -> Verdict:
    """Continue, accept, or stop and escalate."""
    if not failures:
        return Verdict("accept")

    unfixable = [f for f in failures if f.check in UNFIXABLE]
    if unfixable:
        return Verdict("escalate", unfixable[0].message, "unfixable")

    signatures = history.signatures()
    current = frozenset(f.check for f in failures)

    # Regression: something that passed at some point is failing again.
    previously_absent = [c for c in current
                         if signatures and all(c not in s for s in signatures)]
    if len(signatures) >= 1 and previously_absent and passes_used >= 1:
        return Verdict(
            "escalate",
            f"Refining introduced {previously_absent} — checks that were "
            f"passing before this pass. The record is being re-authored rather "
            f"than patched, so further passes are likely to keep trading one "
            f"failure for another.",
            "regressing")

    # Oscillation: this exact failure set has been seen before.
    if current in signatures:
        return Verdict(
            "escalate",
            f"Failure set {sorted(current)} has already been seen in this "
            f"record's history — the loop is cycling, not converging.",
            "oscillating")

    if passes_used >= MAX_PASSES:
        return Verdict(
            "escalate",
            f"{MAX_PASSES} refine passes used and {sorted(current)} still "
            f"failing.",
            "exhausted")

    return Verdict("refine")


def problem_statement(history: History, verdict: Verdict, alpha: dict) -> str:
    """What a human needs in order to decide the next move."""
    lines = [
        f"### `{history.emblem_id}` — escalated ({verdict.trip})", "",
        f"**Alpha:** {alpha['name']} ({alpha['family']}, {alpha['biome']})",
        f"**Why the loop stopped:** {verdict.reason}", "",
        "**What each pass produced:**", "",
    ]
    for a in history.attempts:
        checks = ", ".join(f"`{f.check}`" for f in a["failures"]) or "clean"
        lines.append(f"- **Pass {a['pass']}** — name {a['record'].get('name')!r}, "
                     f"flavour {a['record'].get('flavor')!r}")
        if a.get("note"):
            lines.append(f"  - refiner said: {a['note']}")
        lines.append(f"  - failed: {checks}")

    persistent = set.intersection(*[set(s) for s in history.signatures()]) \
        if history.signatures() else set()
    if persistent:
        lines += ["", f"**Failed in every pass:** "
                      f"{', '.join(f'`{c}`' for c in sorted(persistent))} — "
                      f"a check this record has never once satisfied is more "
                      f"likely a problem with the brief than with the wording."]

    lines += ["", "**Decide:** accept as-is, hand-write this one, loosen the "
                  "check if it is wrong, or fix the contract it is enforcing."]
    return "\n".join(lines)
