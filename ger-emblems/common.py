"""
Shared plumbing for the emblem GER pipeline
===========================================

Paths, the model client, cost accounting, and the run log. Follows the same
conventions as the Assignment #5 coding agent: structured output through
`output_config.format` so no stage ever parses model prose, and every call
priced so the run can say what it cost.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))  # agent-crew/, where rag.py lives

CREW_DIR = _HERE.parent
REPO_ROOT = CREW_DIR.parent
RUNS_DIR = _HERE / "runs"

GDD_PATH = REPO_ROOT / "docs" / "0.1-GDDs" / "gdd-condensed-2026-07-22.md"
CONTENT_DIR = REPO_ROOT / "Assets" / "StreamingAssets"
CREATURES_PATH = CONTENT_DIR / "creatures.json"
BIOMES_PATH = CONTENT_DIR / "biomes.json"

MODEL = os.environ.get("MORPHIVORE_GER_MODEL", "claude-opus-5")

_PRICE_IN = 5.00   # Claude Opus 5, $ per million tokens
_PRICE_OUT = 25.00


def _load_env() -> None:
    env = CREW_DIR / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


_load_env()


@dataclass
class Usage:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write: int = 0
    cache_read: int = 0
    per_stage: dict[str, int] = field(default_factory=dict)

    def record(self, stage: str, usage) -> None:
        self.calls += 1
        self.input_tokens += usage.input_tokens
        self.output_tokens += usage.output_tokens
        self.cache_write += getattr(usage, "cache_creation_input_tokens", 0) or 0
        self.cache_read += getattr(usage, "cache_read_input_tokens", 0) or 0
        self.per_stage[stage] = self.per_stage.get(stage, 0) + 1

    @property
    def dollars(self) -> float:
        return (
            self.input_tokens * _PRICE_IN
            + self.cache_write * _PRICE_IN * 1.25
            + self.cache_read * _PRICE_IN * 0.1
            + self.output_tokens * _PRICE_OUT
        ) / 1_000_000

    def summary(self) -> str:
        stages = ", ".join(f"{k} x{v}" for k, v in sorted(self.per_stage.items()))
        return (f"{self.calls} API calls ({stages})\n"
                f"  input {self.input_tokens:,}  cache read {self.cache_read:,}  "
                f"output {self.output_tokens:,}\n"
                f"  estimated cost ${self.dollars:.2f} on {MODEL}")


USAGE = Usage()

_client = None


def client():
    global _client
    if _client is None:
        import anthropic
        # An identity-linked API key must say which workspace it is acting in;
        # a classic key ignores the header. Set ANTHROPIC_WORKSPACE_ID in .env
        # if the API answers "anthropic-workspace-id is required".
        workspace = os.environ.get("ANTHROPIC_WORKSPACE_ID", "").strip()
        headers = {"anthropic-workspace-id": workspace} if workspace else None
        _client = anthropic.Anthropic(default_headers=headers)
    return _client


def call_json(*, stage: str, system: str, user: str, schema: dict,
              max_tokens: int = 16000, effort: str = "high",
              cache_system: bool = False) -> dict:
    """One schema-valid JSON object. No prose parsing anywhere in this pipeline."""
    block = {"type": "text", "text": system}
    if cache_system:
        block["cache_control"] = {"type": "ephemeral"}

    LOG.prompt(stage, system, user)

    response = client().messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=[block],
        messages=[{"role": "user", "content": user}],
        # `output_config` postdates this venv's pinned anthropic; passed through
        # extra_body rather than upgrading a dependency the #3/#4 crews share.
        extra_body={"output_config": {
            "effort": effort,
            "format": {"type": "json_schema", "schema": schema},
        }},
    )
    USAGE.record(stage, response.usage)
    if response.stop_reason == "refusal":
        raise RuntimeError(f"{stage}: the model declined this request")
    return json.loads(next(b.text for b in response.content if b.type == "text"))


class RunLog:
    """The readable trace of one GER run, written as it happens."""

    def __init__(self) -> None:
        self.dir: Path | None = None
        self.path: Path | None = None
        self._n = 0

    def open(self, run_dir: Path, title: str) -> None:
        self.dir = run_dir
        (run_dir / "prompts").mkdir(parents=True, exist_ok=True)
        self.path = run_dir / "ger-log.md"
        self.path.write_text(
            f"# {title}\n\n**Started** "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"[log] {self.path}")

    def write(self, text: str, echo: bool = True) -> None:
        if self.path:
            with self.path.open("a") as fh:
                fh.write(text + "\n")
        if echo:
            print(text.replace("**", ""))

    def stage(self, title: str) -> None:
        self.write(f"\n---\n\n## {title}\n")

    def prompt(self, stage: str, system: str, user: str) -> None:
        if self.dir is None:
            return
        self._n += 1
        (self.dir / "prompts" / f"{self._n:02d}-{stage}.md").write_text(
            f"# Prompt {self._n} — {stage}\n\n## System\n\n```\n{system}\n```\n\n"
            f"## User\n\n```\n{user}\n```\n")


LOG = RunLog()


def write_json(path: Path, payload) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return path
