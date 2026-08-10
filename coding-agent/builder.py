"""
Stage 5 — generate the code
===========================

A tool-use loop over the real repository. Four tools, hand-rolled against the
Anthropic SDK rather than delegated to a framework, because a reviewer grading
"can I follow what this agent does?" should be able to read the loop.

    read_file     look at existing code before changing it
    list_files    find things by glob
    search_gdd    pull the verbatim spec for a rule being implemented
    write_file    write C# into the project

Three properties worth knowing about `write_file`:

* **It logs before it writes.** The blackboard entry is committed to disk
  first, so a run that dies mid-write still shows what the agent intended.
* **It is fenced.** Only `.cs` files under `Assets/Scripts/` are writable, and
  the resolved path must stay inside the repo. An agent editing its own source,
  the GDD, or `~/.ssh` is not a hypothetical worth leaving open.
* **It snapshots.** Every generated file is copied verbatim into the run folder
  before the developer touches it. That snapshot is what makes "here is what I
  changed before accepting it" a diff rather than a recollection.

`write_file` also brace-balances what it wrote and hands the result back to the
model. It is not a compiler — it catches the failure that actually happens,
which is a long file truncated mid-method — and the model gets to fix it inside
the same loop. Real verification is a Unity domain reload, which happens in the
editor afterwards, with a human watching.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import gdd_rag
from blackboard import BB
from common import MODEL, REPO_ROOT, SCRIPTS_DIR, USAGE, client, write_json

MAX_ITERATIONS = 40

TOOLS = [
    {
        "name": "read_file",
        "description": (
            "Read a file from the project. Use this before changing any file: "
            "the inventory you were given lists declarations only, so it tells "
            "you a member exists but not what it does."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string",
                         "description": "Repo-relative, e.g. Assets/Scripts/Game/GameConfig.cs"}
            },
            "required": ["path"],
        },
    },
    {
        "name": "list_files",
        "description": "List project files matching a glob, e.g. 'Assets/Scripts/**/*.cs'.",
        "input_schema": {
            "type": "object",
            "properties": {"pattern": {"type": "string"}},
            "required": ["pattern"],
        },
    },
    {
        "name": "search_gdd",
        "description": (
            "Search the design document for the exact wording of a rule. Call "
            "this whenever you need a specific number, table, formula, or "
            "worked example — implement from the retrieved text, not from your "
            "summary of it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "write_file",
        "description": (
            "Write a C# file into the project, creating or replacing it. Path "
            "must be under Assets/Scripts/ and end in .cs. Always send the "
            "complete file contents, never a fragment or a diff. Returns a "
            "brace-balance check on what you wrote."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "contents": {"type": "string"},
                "why": {"type": "string",
                        "description": "One sentence: what this file does and why it changed."},
            },
            "required": ["path", "contents", "why"],
        },
    },
]

SYSTEM = """\
You are the Gameplay Engineer on a small Unity game, implementing one chunk of \
work against the game's own design document.

The design document is authoritative. Where it gives a number, a table, or a \
worked example, implement that exactly — call search_gdd rather than working \
from your memory of the brief.

Match the project as you find it. Read the files you are about to change, and \
follow their existing conventions: the naming, the comment density and voice, \
the way state is held, the way visuals are rebuilt. Code that is locally \
idiomatic and slightly imperfect is worth more here than code that is correct \
in the abstract and reads like it came from somewhere else.

Constraints specific to this codebase:
- Unity 6 with URP. UI is Canvas/uGUI; never add OnGUI or GUI.* code.
- Creature.BuildVisuals() destroys all children, so anything parented to a \
creature is rebuilt with it. Per-creature UI that must survive is a separate \
non-child object.
- Difficulty dials live in GameConfig.Ecology and are applied where authored \
stats are stamped. Never hardcode per-creature values into code.
- Generated content files carry an AUTO-GENERATED header. Do not hand-edit them.

Deliver what the brief asks for, at the scope it intends. Make routine \
judgment calls yourself. Do not add features, refactor neighbouring code, or \
introduce abstractions the chunk does not need; do not add error handling for \
states that cannot occur. If you think the brief is wrong, say so in one \
sentence and implement it anyway — the developer decides.

Leave no placeholders behind: no TODO stubs for behaviour the brief asked for, \
no hardcoded sample values standing in for real data, no debug constants. \
Finish the whole chunk. When you are done, stop and summarise what you changed \
and what you could not verify."""


def _safe_path(rel: str) -> Path:
    """Resolve a model-supplied path and refuse anything outside the repo."""
    path = (REPO_ROOT / rel).resolve()
    if not path.is_relative_to(REPO_ROOT.resolve()):
        raise ValueError(f"path escapes the project: {rel}")
    return path


def _brace_balance(text: str) -> str:
    """Cheap truncation detector: the failure mode long generations actually hit."""
    pairs = {"{": "}", "(": ")", "[": "]"}
    counts = {c: text.count(c) - text.count(pairs[c]) for c in pairs}
    bad = {c: n for c, n in counts.items() if n != 0}
    if bad:
        return ("WARNING — unbalanced delimiters, the file is probably "
                f"truncated: {bad}. Rewrite it complete.")
    return "OK — delimiters balanced."


class Builder:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.snapshots = run_dir / "generated"
        self.snapshots.mkdir(parents=True, exist_ok=True)
        self.written: list[dict] = []

    def dispatch(self, name: str, args: dict) -> str:
        try:
            result = getattr(self, f"_tool_{name}")(**args)
        except Exception as exc:  # hand the failure back; the model can recover
            result = f"ERROR: {exc}"
        BB.record_tool_call(name, args, result)
        return result

    # -- tools -------------------------------------------------------------- #

    def _tool_read_file(self, path: str) -> str:
        target = _safe_path(path)
        if not target.exists():
            return f"ERROR: no such file: {path}"
        return target.read_text(errors="replace")

    def _tool_list_files(self, pattern: str) -> str:
        hits = sorted(str(p.relative_to(REPO_ROOT))
                      for p in REPO_ROOT.glob(pattern) if p.is_file())
        return "\n".join(hits[:200]) or "(no matches)"

    def _tool_search_gdd(self, query: str) -> str:
        return gdd_rag.search(query, asked_by="builder", k=3)

    def _tool_write_file(self, path: str, contents: str, why: str) -> str:
        target = _safe_path(path)
        if target.suffix != ".cs":
            return f"ERROR: refused, not a C# file: {path}"
        if not target.is_relative_to(SCRIPTS_DIR.resolve()):
            return f"ERROR: refused, outside Assets/Scripts/: {path}"

        action = "Modified" if target.exists() else "Created"
        # Blackboard first: if this run dies here, the record still shows the
        # code that was about to land in the project.
        BB.record_generated(path, action, contents, why)

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents)

        # Verbatim snapshot, before any human edit. This is the "before" side
        # of the README's what-I-changed diff.
        shutil.copyfile(target, self.snapshots / target.name)
        self.written.append({"path": path, "action": action, "why": why})

        return f"{action} {path} ({len(contents.splitlines())} lines). {_brace_balance(contents)}"

    # -- the loop ----------------------------------------------------------- #

    def run(self, brief: str) -> dict:
        BB.record_prompt("build", SYSTEM, brief)
        messages: list[dict] = [{"role": "user", "content": brief}]
        summary = ""

        for turn in range(1, MAX_ITERATIONS + 1):
            with client().messages.stream(
                model=MODEL,
                max_tokens=32000,
                system=SYSTEM,
                tools=TOOLS,
                messages=messages,
                extra_body={
                    # xhigh is the documented sweet spot for coding and agentic
                    # work; see the note in common.call_json on extra_body.
                    "output_config": {"effort": "xhigh"},
                    # Cache the whole prefix each turn. The conversation only
                    # grows -- every file read stays in it -- so without this
                    # a 19-turn build re-sends and re-pays for the entire
                    # transcript on every turn. Measured at 2.88M input tokens
                    # and $17 before this line existed.
                    "cache_control": {"type": "ephemeral"},
                },
            ) as stream:
                response = stream.get_final_message()
            USAGE.record("build", response.usage)

            if response.stop_reason == "refusal":
                BB.note("The model declined to continue.")
                break

            messages.append({"role": "assistant", "content": response.content})
            calls = [b for b in response.content if b.type == "tool_use"]
            said = " ".join(b.text for b in response.content if b.type == "text").strip()

            if not calls:
                summary = said
                BB.note(f"Finished after {turn} turn(s).")
                break

            if said:
                BB.detail(f"> {said[:400]}")
            messages.append({
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": c.id,
                     "content": self.dispatch(c.name, c.input)}
                    for c in calls
                ],
            })
        else:
            BB.note(f"Stopped at the {MAX_ITERATIONS}-turn cap without finishing.")

        return {"files": self.written, "summary": summary}


def run(run_dir: Path, brief: str) -> dict:
    BB.stage(5, "Generate code")
    result = Builder(run_dir).run(brief)

    BB.note(f"Wrote **{len(result['files'])} file(s)**.")
    if result["summary"]:
        BB.record_reasoning("The agent's own account of what it built",
                            result["summary"])
    write_json(run_dir / "build-result.json", result)
    return result
