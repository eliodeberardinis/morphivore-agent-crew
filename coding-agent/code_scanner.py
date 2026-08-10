"""
Stage 2 — scan the codebase
===========================

Deterministic. No model call: this stage answers "what is actually in the
project", and that is a question with a correct answer, so Python answers it.

What it produces is the *evidence* the gap detector reasons over:

  * every C# type and its members, so a requirement can be checked against
    real symbol names rather than the model's memory of the codebase;
  * the string literals in each file, because this project encodes identity as
    strings (`"YELLOW"`, `"WHITE"`) and "which families exist" is answerable
    only by looking at them;
  * a **reference graph over the data contract files** -- which scripts read
    `creatures.json`, `forms.json`, and so on.

That last one earns its place. The naive check is "does forms.json exist?",
which returns yes and hides the actual defect: 150 authored, ratified forms
that nothing loads. Presence is not consumption, and asking the question that
way is what turns a silent gap into a visible one.

The C# parse is regex-based and shallow by design -- it recovers declarations,
not semantics, and assigns each member to the most recently declared type. It
is a good index and a bad compiler, and the gap detector is told so.
"""

from __future__ import annotations

import re
from pathlib import Path

from blackboard import BB
from common import CONTENT_DIR, SCRIPTS_DIR, write_json

_TYPE_RE = re.compile(
    r"^\s*(?:(?:public|internal|private|protected|static|sealed|abstract|partial|readonly)\s+)*"
    r"(class|struct|enum|interface)\s+(\w+)"
)
_METHOD_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|static|virtual|override|async|sealed|new)\s+)+"
    r"[\w<>\[\],\.\?]+\s+(\w+)\s*\("
)
_FIELD_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|static|readonly|const)\s+)+"
    r"[\w<>\[\],\.\?]+\s+(\w+)\s*(?:=|;|\{\s*get)"
)
_STRING_RE = re.compile(r'"([^"\\\n]{2,40})"')
_JSON_RE = re.compile(r'"([\w\-]+\.json)"')

# Literals that are noise rather than vocabulary.
_BORING = re.compile(r"^[\s/\.\-_]*$|^(?:https?:|assets/|/)", re.I)

# Control-flow keywords that the method regex would otherwise read as calls.
_KEYWORDS = {"if", "for", "while", "switch", "foreach", "return", "using",
             "lock", "catch", "fixed", "get", "set"}


def _parse_cs(path: Path) -> dict:
    text = path.read_text(errors="replace")
    lines = text.splitlines()

    # Brace-depth tracking, because this codebase nests types (GameConfig holds
    # Colors, Ecology, Boss; EnemyAI holds its own State/Attack enums). Without
    # it, members land on whichever type was declared most recently rather than
    # the one that encloses them.
    types: list[dict] = []
    stack: list[dict] = []
    depth = 0

    for line in lines:
        m = _TYPE_RE.match(line)
        if m:
            entry = {"kind": m.group(1), "name": m.group(2), "members": []}
            types.append(entry)
            stack.append({"type": entry, "open_depth": depth, "entered": False})
        else:
            member = _METHOD_RE.match(line) or _FIELD_RE.match(line)
            if stack and member and member.group(1) not in _KEYWORDS:
                bucket = stack[-1]["type"]["members"]
                if member.group(1) not in bucket:
                    bucket.append(member.group(1))

        depth += line.count("{") - line.count("}")
        for frame in stack:
            if depth > frame["open_depth"]:
                frame["entered"] = True
        while stack and stack[-1]["entered"] and depth <= stack[-1]["open_depth"]:
            stack.pop()

    literals: list[str] = []
    for s in _STRING_RE.findall(text):
        if not _BORING.match(s) and s not in literals:
            literals.append(s)

    return {
        "path": str(path.relative_to(SCRIPTS_DIR.parent.parent)),
        "lines": len(lines),
        "types": types,
        "string_literals": literals[:60],
        "json_refs": sorted(set(_JSON_RE.findall(text))),
    }


def scan() -> dict:
    """Index Assets/Scripts and the data contract, and link the two."""
    files = [_parse_cs(p) for p in sorted(SCRIPTS_DIR.rglob("*.cs"))]

    content_files = []
    for data in sorted(CONTENT_DIR.glob("*.json")):
        readers = [f["path"] for f in files if data.name in f["json_refs"]]
        content_files.append({
            "name": data.name,
            "size_bytes": data.stat().st_size,
            # The distinction that matters: shipped, versus actually loaded.
            "read_by": readers,
        })

    return {"files": files, "content_files": content_files}


def run(run_dir: Path) -> dict:
    BB.stage(2, "Scan the codebase")
    inventory = scan()
    BB.record_codebase_state(inventory)
    write_json(run_dir / "inventory.json", inventory)
    return inventory


def render_for_prompt(inventory: dict) -> str:
    """Flatten the inventory into the evidence block the judge reads.

    Kept compact and stable: it is the cached prefix for every per-requirement
    call in stage 3, so its bytes must not vary between those calls.
    """
    out = ["# Codebase inventory", "",
           "Regex-derived index of Assets/Scripts. Declarations only -- it "
           "recovers names, not semantics, and members are attributed to the "
           "most recent enclosing type. Treat absence as weak evidence and "
           "presence as strong evidence.", ""]

    for f in inventory["files"]:
        out.append(f"## {f['path']}  ({f['lines']} lines)")
        for t in f["types"]:
            members = ", ".join(t["members"]) or "(none parsed)"
            out.append(f"- `{t['kind']} {t['name']}` — {members}")
        if f["string_literals"]:
            out.append("- string literals: "
                       + ", ".join(f'"{s}"' for s in f["string_literals"]))
        out.append("")

    out += ["## Data contract files (Assets/StreamingAssets)", ""]
    for c in inventory["content_files"]:
        readers = ", ".join(c["read_by"]) if c["read_by"] else "**NOTHING READS THIS FILE**"
        out.append(f"- `{c['name']}` ({c['size_bytes']:,} bytes) — read by: {readers}")

    return "\n".join(out)


if __name__ == "__main__":  # quick check without spending a token
    inv = scan()
    print(render_for_prompt(inv))
