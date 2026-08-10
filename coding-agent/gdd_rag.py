"""
Retrieval over the *scoped* GDD
===============================

Reuses the Assignment #4 crew's `rag.py` — the same hybrid BM25 + embedding
index, the same heading-aware chunking, the same audit log — but points it at a
corpus this agent controls instead of the 21k-word extended GDD it ships with.

Why not just pass the scoped text wholesale to every call? Because a
distillation is lossy in precisely the place a code auditor needs precision.
Stage 1 turns "Health 100 -> 350, Damage 40 -> 115" into "stats scale with
rank", which is true and useless for deciding whether `GameConfig.Tiers` is
right. Retrieval puts the verbatim passage — numbers, formulas, worked
examples — back in front of the judge for the one requirement being judged.

Two deliberate choices:

* **`rag.py` is not edited.** It is shared byte-for-byte with the public crew
  repo, so this module reassigns its module-level paths instead. Repointing is
  reversible and leaves the crews untouched.
* **Retrieved passages go in the USER block, never the system block.** Stage 3
  caches its system prefix across every requirement; varying it per call would
  invalidate that cache on every single request.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))  # agent-crew/, where rag.py lives

import rag  # noqa: E402 -- the Assignment #4 retrieval layer, unmodified

KB_DIR = _HERE / "kb-scoped"


def build_index(scoped_text: str, run_dir: Path) -> dict:
    """Index the scoped GDD and route the audit log into this run's folder."""
    KB_DIR.mkdir(exist_ok=True)
    (KB_DIR / "gdd-scoped.md").write_text(scoped_text)

    # Repoint the shared module at our corpus. `_index` is a process-global
    # cache inside rag.py; clearing it forces a rebuild against the new KB
    # rather than serving chunks from the extended GDD.
    rag.KB_DIR = KB_DIR
    rag.RETRIEVAL_LOG = run_dir / "retrieval-log.jsonl"
    rag._index = None

    index = rag.get_index()
    return {
        "chunks": len(index.chunks),
        "backends": list(index.backends),
        "sections": sorted({c.section for c in index.chunks}),
    }


def search(query: str, *, asked_by: str, k: int = 3) -> str:
    """Return the most relevant scoped-GDD passages, labelled by section."""
    hits = rag.retrieve(query, asked_by=asked_by, k=k)
    if not hits:
        return "(no matching design passages)"
    return "\n\n".join(f"--- {c.id} ---\n{c.text}" for c, _ in hits)
