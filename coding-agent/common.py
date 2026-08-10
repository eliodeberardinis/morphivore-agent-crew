"""
Shared plumbing for the goal-oriented coding agent
==================================================

Paths, the model client, and cost accounting. Everything here is deliberately
small: the interesting logic lives in the five stage modules, and a reviewer
should be able to read this file once and then forget it.

Two conventions the whole agent follows:

  * **The LLM judges; Python counts.** Every stage that produces structured
    data asks for it through `output_config.format`, so the model returns
    schema-valid JSON and no stage ever regex-scrapes prose. Anything that can
    be computed -- reference graphs, blocking degree, ranking -- is computed
    here in Python, not asked for.
  * **Every API call is priced.** `USAGE` accumulates tokens across the run and
    `USAGE.summary()` renders what the run cost. An agent that writes code on
    your behalf should be able to tell you what it spent doing it.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

# The crew's rag.py lives one level up and is reused verbatim for GDD retrieval.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from blackboard import BB  # noqa: E402 -- needs the path insert above

# --------------------------------------------------------------------------- #
#  Paths                                                                       #
# --------------------------------------------------------------------------- #

CREW_DIR = _HERE.parent                  # agent-crew/
REPO_ROOT = CREW_DIR.parent              # the Unity project
RUNS_DIR = _HERE / "runs"

# The *condensed* GDD is canonical for this project -- the extended one is a
# 21k-word reference. Scoping the agent to the canonical document is the first
# of two narrowing steps (the second is the section filter in gdd_reader).
GDD_PATH = REPO_ROOT / "docs" / "0.1-GDDs" / "gdd-condensed-2026-07-22.md"

# The build brief for stage 5. Held out of stages 1-4 on purpose: it contains a
# human gap analysis, and an agent that reads it is doing comprehension rather
# than detection. See README, "Why the plan is held out".
BUILD_PLAN_PATH = REPO_ROOT / "docs" / "4-Build-Plan" / "build-plan.md"

SCRIPTS_DIR = REPO_ROOT / "Assets" / "Scripts"
CONTENT_DIR = REPO_ROOT / "Assets" / "StreamingAssets"

# --------------------------------------------------------------------------- #
#  Model                                                                       #
# --------------------------------------------------------------------------- #

# The CrewAI crews route through LiteLLM and use an "anthropic/" prefix. This
# agent calls the Anthropic SDK directly, so it takes the bare model id and its
# own env var rather than reusing MORPHIVORE_CREW_MODEL.
MODEL = os.environ.get("MORPHIVORE_CODER_MODEL", "claude-opus-5")

# Claude Opus 5, $ per million tokens. Cache writes cost 1.25x base, reads 0.1x.
_PRICE_IN = 5.00
_PRICE_OUT = 25.00


def _load_env() -> None:
    """Read agent-crew/.env without requiring python-dotenv."""
    env = CREW_DIR / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_env()


@dataclass
class Usage:
    """Running token and cost total for one agent run."""

    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0
    per_stage: dict[str, int] = field(default_factory=dict)

    def record(self, stage: str, usage) -> None:
        self.calls += 1
        self.input_tokens += usage.input_tokens
        self.output_tokens += usage.output_tokens
        self.cache_write_tokens += getattr(usage, "cache_creation_input_tokens", 0) or 0
        self.cache_read_tokens += getattr(usage, "cache_read_input_tokens", 0) or 0
        self.per_stage[stage] = self.per_stage.get(stage, 0) + 1

    @property
    def dollars(self) -> float:
        return (
            self.input_tokens * _PRICE_IN
            + self.cache_write_tokens * _PRICE_IN * 1.25
            + self.cache_read_tokens * _PRICE_IN * 0.1
            + self.output_tokens * _PRICE_OUT
        ) / 1_000_000

    def summary(self) -> str:
        stages = ", ".join(f"{k} x{v}" for k, v in self.per_stage.items())
        return (
            f"{self.calls} API calls ({stages})\n"
            f"  input {self.input_tokens:,}  "
            f"cache write {self.cache_write_tokens:,}  "
            f"cache read {self.cache_read_tokens:,}  "
            f"output {self.output_tokens:,}\n"
            f"  estimated cost ${self.dollars:.2f} on {MODEL}"
        )


USAGE = Usage()

_client = None


def client():
    global _client
    if _client is None:
        import anthropic

        _client = anthropic.Anthropic()
    return _client


def call_json(
    *,
    stage: str,
    system: str,
    user: str,
    schema: dict,
    max_tokens: int = 16000,
    effort: str = "high",
    cache_system: bool = False,
) -> dict:
    """Ask for one schema-valid JSON object.

    `output_config.format` constrains the response to the schema, so callers
    get a dict and never a parse failure. `cache_system` marks the system block
    cacheable -- worth it when the same large prefix (the codebase inventory)
    is reused across many per-requirement calls.
    """
    system_block = {"type": "text", "text": system}
    if cache_system:
        system_block["cache_control"] = {"type": "ephemeral"}

    # Recorded before the call, so a crashed run still shows what was asked.
    BB.record_prompt(stage, system, user)

    # `output_config` is newer than the pinned SDK's typed parameters. It is
    # passed through `extra_body` rather than upgrading `anthropic`, because
    # this venv is shared with the Assignment #3/#4 crews and CrewAI pins
    # against that version -- a graded pipeline is not worth breaking for a
    # keyword argument.
    response = client().messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=[system_block],
        messages=[{"role": "user", "content": user}],
        extra_body={
            "output_config": {
                "effort": effort,
                "format": {"type": "json_schema", "schema": schema},
            }
        },
    )
    USAGE.record(stage, response.usage)

    if response.stop_reason == "refusal":
        raise RuntimeError(f"{stage}: the model declined this request")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def write_json(path: Path, payload) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return path
