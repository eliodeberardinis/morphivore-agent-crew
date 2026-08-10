"""
The blackboard -- how a human stays in control of an agent writing their code
=============================================================================

Every decision this agent makes is written to disk as markdown, as it happens.
Not a debug log: the blackboard is the mechanism by which the developer can
answer "did it do what I intended?" without reading the diff and guessing.

Three things it records, matching the three questions worth asking:

  * **What it scored** -- every gap the agent found, its utility score, and the
    arithmetic behind that score. If you disagree with the ranking you can see
    exactly which term produced it.
  * **What it issued** -- the full text of every prompt sent to the model, with
    the context that was passed. Written to `prompts/` so a reviewer can read
    what the agent actually asked, not a paraphrase of it.
  * **What it generated** -- the code, logged *before* it is written into the
    project. `record_generated()` is called ahead of the file write on purpose:
    if the run dies mid-write, the blackboard still shows what was intended.

Everything flushes on write, so `tail -f` on the blackboard shows the run
progressing live.

Separately, `AGENT_STATE.md` is the agent's memory across sessions -- BUILT,
DECISIONS, NEXT, FAILED. Plain markdown, no database: the developer can read
it, correct it, and hand it back to the next run, which picks up from there.
"""

from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
STATE_PATH = _HERE / "AGENT_STATE.md"

_STATE_TEMPLATE = """# Morphivore coding agent — state

Markdown is the agent's memory. Read it, edit it, hand it to the next run.
Anything you change here is what the next session believes.

## BUILT
_Nothing yet._

## DECISIONS
_Nothing yet._

## NEXT
_Nothing yet._

## FAILED
_Nothing yet._
"""


class Blackboard:
    """A live markdown record of one agent run."""

    def __init__(self) -> None:
        self.run_dir: Path | None = None
        self.path: Path | None = None
        self.prompt_dir: Path | None = None
        self._prompt_n = 0
        self.scores: list[dict] = []
        self.generated: list[dict] = []
        # Stage 3 judges requirements in parallel; without this, two threads
        # interleave mid-line and the record becomes unreadable.
        self._lock = threading.Lock()

    # -- lifecycle ---------------------------------------------------------- #

    def open(self, run_dir: Path, *, goal: str, mode: str) -> None:
        self.run_dir = run_dir
        self.prompt_dir = run_dir / "prompts"
        self.prompt_dir.mkdir(parents=True, exist_ok=True)
        self.path = run_dir / "blackboard.md"
        started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.path.write_text(
            f"# Blackboard — {run_dir.name}\n\n"
            f"**Started** {started}  \n"
            f"**Mode** {mode}  \n"
            f"**Goal** {goal}\n"
        )
        print(f"[blackboard] {self.path}")

    # -- primitives --------------------------------------------------------- #

    def _append(self, text: str) -> None:
        if self.path is None:  # allow stage modules to be imported standalone
            return
        with self._lock, self.path.open("a") as fh:
            fh.write(text)

    def stage(self, number: int, title: str) -> None:
        self._append(f"\n\n---\n\n## Stage {number} — {title}\n")
        print(f"\n=== Stage {number}: {title} ===")

    def note(self, text: str) -> None:
        self._append(f"\n{text}\n")
        print(f"  {text}")

    def detail(self, text: str) -> None:
        """A line for the record but too fine-grained for the terminal."""
        self._append(f"\n{text}\n")

    def table(self, headers: list[str], rows: list[list[str]]) -> None:
        if not rows:
            return
        out = ["", "| " + " | ".join(headers) + " |",
               "|" + "|".join(["---"] * len(headers)) + "|"]
        out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
        self._append("\n".join(out) + "\n")

    def code(self, language: str, body: str) -> None:
        self._append(f"\n```{language}\n{body}\n```\n")

    # -- the three things worth recording ----------------------------------- #

    def record_codebase_state(self, inventory: dict) -> None:
        """What the agent read from the project before deciding anything."""
        files = inventory.get("files", [])
        contracts = inventory.get("content_files", [])
        self.note(
            f"Read **{len(files)} C# files** "
            f"({sum(f['lines'] for f in files):,} lines, "
            f"{sum(len(f['types']) for f in files)} types) and "
            f"**{len(contracts)} data contract files**."
        )
        self.table(
            ["File", "Lines", "Types", "Members"],
            [[f["path"], f["lines"], ", ".join(t["name"] for t in f["types"]) or "—",
              sum(len(t["members"]) for t in f["types"])] for f in files],
        )
        unread = [c["name"] for c in contracts if not c["read_by"]]
        if unread:
            self.note(
                "Data files present but **read by no script**: "
                + ", ".join(f"`{n}`" for n in unread)
                + " — authored content the game never loads."
            )

    def record_prompt(self, stage: str, system: str, user: str) -> Path:
        """The exact prompt issued, written in full to prompts/."""
        with self._lock:
            self._prompt_n += 1
            n = self._prompt_n
        path = self.prompt_dir / f"{n:02d}-{stage}.md"
        path.write_text(
            f"# Prompt {n} — {stage}\n\n"
            f"## System\n\n```\n{system}\n```\n\n"
            f"## User\n\n```\n{user}\n```\n"
        )
        return path

    def record_scores(self, ranked: list[dict], formula: str) -> None:
        """Every gap, its utility score, and the arithmetic behind it."""
        self.scores = ranked
        self.note(f"Utility score: `{formula}`")
        self.table(
            ["#", "Requirement", "§", "Verdict", "Blocks", "Severity",
             "Effort", "Score"],
            [[i, r["name"], r["gdd_section"], r["verdict"], r["blocking_degree"],
              f'{r["severity_weight"]:.1f}', f'{r["effort"]:.1f}',
              f'{r["score"]:.1f}']
             for i, r in enumerate(ranked, 1)],
        )

    def record_reasoning(self, title: str, text: str) -> None:
        self._append(f"\n**{title}**\n\n{text}\n")

    def record_generated(self, path: str, action: str, body: str, why: str) -> None:
        """Log generated code BEFORE it is written into the project."""
        self.generated.append({"path": path, "action": action, "why": why})
        self._append(
            f"\n### {action}: `{path}`\n\n_{why}_\n\n"
            f"<details><summary>{len(body.splitlines())} lines</summary>\n\n"
            f"```csharp\n{body}\n```\n\n</details>\n"
        )
        print(f"  [{action}] {path} ({len(body.splitlines())} lines)")

    def record_tool_call(self, name: str, args: dict, result: str) -> None:
        summary = ", ".join(f"{k}={v!r}"[:70] for k, v in args.items())
        first = result.splitlines()[0][:100] if result else ""
        self._append(f"\n- `{name}({summary})` → {first}\n")
        print(f"  · {name}({summary})")

    def close(self, usage_summary: str) -> None:
        self._append(f"\n\n---\n\n## Run cost\n\n```\n{usage_summary}\n```\n")
        print(f"\n{usage_summary}")

    # -- persistent memory -------------------------------------------------- #

    @staticmethod
    def load_state() -> str:
        if not STATE_PATH.exists():
            STATE_PATH.write_text(_STATE_TEMPLATE)
        return STATE_PATH.read_text()

    @staticmethod
    def update_state(*, built: list[str], decisions: list[str],
                     next_up: list[str], failed: list[str]) -> None:
        """Append this run's outcome to the agent's cross-session memory.

        Appends rather than rewrites: the developer's own edits to this file
        are instructions to the next run, and an agent that overwrites them
        has quietly ignored its operator.
        """
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        text = Blackboard.load_state()

        def add(section: str, lines: list[str]) -> None:
            nonlocal text
            if not lines:
                return
            block = "\n".join(f"- {stamp} — {line}" for line in lines)
            marker = f"## {section}\n"
            head, _, tail = text.partition(marker)
            tail = tail.replace("_Nothing yet._\n", "", 1)
            text = f"{head}{marker}{block}\n{tail}"

        add("FAILED", failed)
        add("NEXT", next_up)
        add("DECISIONS", decisions)
        add("BUILT", built)
        STATE_PATH.write_text(text)
        print(f"[state] updated {STATE_PATH.name}")


BB = Blackboard()
