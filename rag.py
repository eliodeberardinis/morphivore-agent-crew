"""
Morphivore -- the shared lore database (RAG layer)
==================================================

One knowledge base, read by every agent in every crew: the game's own GDD.

Assignment #3's crew was game-anchored by *transcription* -- the GDD's facts were
copied by hand into constants in `tools.py`. This module replaces that with
*retrieval*: agents ask the document a question and author from what comes back,
so a design change in the GDD reaches the agents without anyone re-typing it.

Three parts:

  * `build_kb()`   -- assembles `kb/` from the game's docs (the "folder the agent
                      can read"), including a voice digest of the 150 forms the
                      #3 crew already authored.
  * `retrieve()`   -- hybrid search over section-level chunks: BM25 (always
                      available) fused with vector embeddings (when the ONNX
                      model is reachable), so retrieval degrades instead of
                      failing.
  * `gdd_search`   -- the CrewAI tool wrapper. Every agent gets this one tool,
                      which is what makes the knowledge base *shared* rather
                      than per-agent.

Every retrieval is appended to `output/retrieval-log.jsonl` -- query, backend,
and the chunks that came back with their scores. That log is the audit trail:
it is what lets a reader put a query, the chunk it pulled, and the content it
produced side by side.
"""

import hashlib
import json
import re
import shutil
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------- #
#  Paths                                                                       #
# --------------------------------------------------------------------------- #

_HERE = Path(__file__).parent
KB_DIR = _HERE / "kb"
OUT_DIR = _HERE / "output"
CACHE_DIR = OUT_DIR / ".cache"
RETRIEVAL_LOG = OUT_DIR / "retrieval-log.jsonl"

# The GDD lives in the game repo; kb/ holds the copy the crew actually reads, so
# the pipeline stays runnable after it is extracted from this repository.
GDD_SOURCE = _HERE.parent / "docs" / "0.1-GDDs" / "GDD-Extended.md"
FORMS_SOURCE = OUT_DIR / "forms.json"

TOP_K = 4               # chunks returned per query
_RRF_K = 60             # reciprocal-rank-fusion damping constant
_MAX_CHUNK_WORDS = 260  # long GDD sections are windowed to keep retrieval sharp
# Overlap is deliberately large. Tuned up from 40 after a test query for grazer
# behaviour split the GDD's flee-speed derivation ("12 x 0.8 = 9.6. Grazer flee
# speed is pinned below that") across two windows, returning the rule without its
# number. A hard invariant has to survive windowing intact to be retrievable.
_CHUNK_OVERLAP_WORDS = 90

_log_lock = threading.Lock()  # the #4 crew retrieves from parallel tracks


# --------------------------------------------------------------------------- #
#  Knowledge base assembly                                                     #
# --------------------------------------------------------------------------- #

def _forms_voice_digest(forms_path: Path) -> str:
    """Render forms.json into a prose voice sample.

    The 150 authored names are the game's entire authorial voice (GDD 3.1,
    Content & Tone Agent). New content has to sound like it came from the same
    hand, so the names and flavour lines belong in the knowledge base -- not
    just the GDD prose that describes the tone in the abstract.
    """
    data = json.loads(forms_path.read_text())
    forms = data.get("forms", [])
    if not forms:
        return ""

    lines = [
        "# Authored voice reference — the 150 Bestiary form names",
        "",
        "Authored by the Assignment #3 crew from the same GDD. This is the game's",
        "established register: primal, crude, comedic. New content must sit beside",
        "these without sounding like it came from a different game.",
        "",
    ]
    by_strain: dict[tuple[str, str], list[str]] = {}
    flavours: dict[tuple[str, str], str] = {}
    for f in forms:
        key = (f["family"], f["intensity"])
        by_strain.setdefault(key, []).append(f["name"])
        flavours.setdefault(key, f.get("flavor", ""))

    for (family, intensity), names in by_strain.items():
        lines.append(f"### {family} {intensity} — {len(names)} ranks")
        lines.append(f"Flavour: {flavours[(family, intensity)]}")
        lines.append("Names, rank 1 to 6: " + "; ".join(names))
        lines.append("")
    return "\n".join(lines)


def build_kb() -> str:
    """Populate `kb/` from the game's documents. Idempotent.

    Slide-1 pattern: put the game docs in a folder the agent can read. If the
    source documents are absent (e.g. this crew has been extracted from the game
    repo) an already-populated kb/ is left alone.
    """
    KB_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)
    report = []

    if GDD_SOURCE.exists():
        dest = KB_DIR / GDD_SOURCE.name
        shutil.copyfile(GDD_SOURCE, dest)
        report.append(f"{dest.name} ({len(dest.read_text().splitlines())} lines)")

    if FORMS_SOURCE.exists():
        digest = _forms_voice_digest(FORMS_SOURCE)
        if digest:
            dest = KB_DIR / "forms-voice-reference.md"
            dest.write_text(digest)
            report.append(dest.name)

    present = sorted(p.name for p in KB_DIR.glob("*.md"))
    if not present:
        raise FileNotFoundError(
            f"Knowledge base is empty and no source documents found at {GDD_SOURCE}. "
            "The crew cannot run game-anchored without its GDD."
        )
    return "KB: " + ", ".join(report or present)


# --------------------------------------------------------------------------- #
#  Chunking -- the GDD's own headings are the natural boundaries               #
# --------------------------------------------------------------------------- #

@dataclass
class Chunk:
    id: str        # e.g. "GDD-Extended §2.4a [1/2]"
    source: str
    section: str   # "2.4a", or the heading text when the GDD gives no number
    heading: str
    text: str


_HEADING_RE = re.compile(r"^(#{2,4})\s+(.*)$")
_SECTION_NO_RE = re.compile(r"^(\d+(?:\.\d+)?[a-z]?)\.?\s+(.*)$")


def _window(words: list[str]) -> list[list[str]]:
    """Split an over-long section into overlapping windows."""
    if len(words) <= _MAX_CHUNK_WORDS:
        return [words]
    step = _MAX_CHUNK_WORDS - _CHUNK_OVERLAP_WORDS
    return [words[i : i + _MAX_CHUNK_WORDS] for i in range(0, len(words), step)]


def _chunk_document(path: Path) -> list[Chunk]:
    """Split one markdown document into section-level chunks.

    The GDD is written with '## 2. Game Mechanics' / '### 2.4a The colour buffer'
    headings, so its own structure gives semantically clean boundaries -- and a
    citable section number to show alongside any generated content.
    """
    chunks: list[Chunk] = []
    heading, section, body = path.stem, "preamble", []

    def flush() -> None:
        text = "\n".join(body).strip()
        if not text:
            return
        windows = _window(text.split())
        for i, w in enumerate(windows, 1):
            suffix = f" [{i}/{len(windows)}]" if len(windows) > 1 else ""
            chunks.append(
                Chunk(
                    id=f"{path.stem} §{section}{suffix}",
                    source=path.name,
                    section=section,
                    heading=heading,
                    # The heading rides along so the embedding sees what the
                    # passage is *about*, not just its body text.
                    text=f"{heading}\n\n{' '.join(w)}",
                )
            )

    for line in path.read_text().splitlines():
        m = _HEADING_RE.match(line)
        if m:
            flush()
            body = []
            heading = m.group(2).strip()
            num = _SECTION_NO_RE.match(heading)
            section = num.group(1) if num else heading[:40]
        else:
            body.append(line)
    flush()
    return chunks


def load_chunks() -> list[Chunk]:
    """Chunk every document in the knowledge base."""
    docs = sorted(KB_DIR.glob("*.md"))
    if not docs:
        build_kb()
        docs = sorted(KB_DIR.glob("*.md"))
    return [c for d in docs for c in _chunk_document(d)]


# --------------------------------------------------------------------------- #
#  Retrieval -- BM25 always, embeddings when available, fused                  #
# --------------------------------------------------------------------------- #

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class _Index:
    """Hybrid index. Built once, reused by every agent and every track."""

    def __init__(self) -> None:
        self.chunks = load_chunks()
        self.backends: list[str] = []

        from rank_bm25 import BM25Okapi  # hard dependency: the guaranteed floor

        self._bm25 = BM25Okapi([_tokenize(c.text) for c in self.chunks])
        self.backends.append("bm25")

        self._embeddings = None
        self._embed_query = None
        self._try_embeddings()

    # -- vector half -------------------------------------------------------- #

    def _corpus_fingerprint(self) -> str:
        h = hashlib.sha256()
        for c in self.chunks:
            h.update(c.text.encode())
        return h.hexdigest()[:16]

    def _try_embeddings(self) -> None:
        """Attach the vector half if chromadb's ONNX model is reachable.

        Chroma ships with CrewAI, so this costs no new dependency. If the model
        cannot be fetched (offline, first run, sandbox), retrieval quietly
        continues on BM25 alone rather than taking the pipeline down.
        """
        try:
            import numpy as np
            from chromadb.utils import embedding_functions

            ef = embedding_functions.DefaultEmbeddingFunction()
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache = CACHE_DIR / f"embeddings-{self._corpus_fingerprint()}.npy"

            if cache.exists():
                mat = np.load(cache)
            else:
                mat = np.asarray(ef([c.text for c in self.chunks]), dtype="float32")
                np.save(cache, mat)

            norms = np.linalg.norm(mat, axis=1, keepdims=True)
            self._embeddings = mat / np.clip(norms, 1e-9, None)
            self._embed_query = lambda q: np.asarray(ef([q])[0], dtype="float32")
            self._np = np
            self.backends.append("embeddings")
        except Exception as exc:  # noqa: BLE001 -- degrade, never fail
            self._embeddings = None
            self.embedding_error = str(exc)[:200]

    # -- fusion ------------------------------------------------------------- #

    def search(self, query: str, k: int = TOP_K) -> tuple[list[tuple[Chunk, float]], list[str]]:
        """Reciprocal-rank fusion of the lexical and vector rankings.

        RRF is used rather than a weighted score blend because BM25 scores and
        cosine similarities are not on a comparable scale; ranks are.
        """
        rankings: list[list[int]] = []

        bm25_scores = self._bm25.get_scores(_tokenize(query))
        rankings.append(sorted(range(len(self.chunks)), key=lambda i: -bm25_scores[i]))

        if self._embeddings is not None:
            qv = self._embed_query(query)
            qv = qv / max(float(self._np.linalg.norm(qv)), 1e-9)
            sims = self._embeddings @ qv
            rankings.append(sorted(range(len(self.chunks)), key=lambda i: -float(sims[i])))

        fused: dict[int, float] = {}
        for ranking in rankings:
            for rank, idx in enumerate(ranking, 1):
                fused[idx] = fused.get(idx, 0.0) + 1.0 / (_RRF_K + rank)

        top = sorted(fused.items(), key=lambda kv: -kv[1])[:k]
        return [(self.chunks[i], round(s, 6)) for i, s in top], self.backends


_index: _Index | None = None
_index_lock = threading.Lock()


def get_index() -> _Index:
    global _index
    with _index_lock:
        if _index is None:
            _index = _Index()
    return _index


def _log(query: str, asked_by: str, hits: list[tuple[Chunk, float]], backends: list[str]) -> None:
    """Append the retrieval to the audit trail."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "asked_by": asked_by or "unattributed",
        "query": query,
        "backends": backends,
        "hits": [
            {"chunk_id": c.id, "source": c.source, "section": c.section,
             "score": s, "text": c.text}
            for c, s in hits
        ],
    }
    OUT_DIR.mkdir(exist_ok=True)
    with _log_lock:
        with RETRIEVAL_LOG.open("a") as fh:
            fh.write(json.dumps(record) + "\n")


def retrieve(query: str, asked_by: str = "", k: int = TOP_K) -> list[tuple[Chunk, float]]:
    """Search the knowledge base and record the retrieval. Library entry point."""
    hits, backends = get_index().search(query, k)
    _log(query, asked_by, hits, backends)
    return hits


# --------------------------------------------------------------------------- #
#  The CrewAI tool -- every agent in every crew gets exactly this one          #
# --------------------------------------------------------------------------- #

def _format(hits: list[tuple[Chunk, float]]) -> str:
    if not hits:
        return "No passages found. Try different wording, or fewer/plainer terms."
    out = []
    for c, score in hits:
        out.append(f"--- {c.id} (relevance {score:.4f}) ---\n{c.text}")
    return "\n\n".join(out)


def search_gdd(query: str, asked_by: str = "") -> str:
    """Plain-python form of the tool, so critics can retrieve without an agent."""
    return _format(retrieve(query, asked_by=asked_by))


try:
    from crewai.tools import tool

    @tool("gdd_search")
    def gdd_search(query: str, asked_by: str = "") -> str:
        """Search MORPHIVORE's own design documents and return the most relevant
        passages, each labelled with its GDD section number.

        This is the single source of truth for the whole crew. Before you author
        ANY content -- a creature, a panel, a biome, a name -- search here first
        and write from what comes back. Never write from general game-design
        knowledge or from memory of other games: if it is not in the retrieved
        passages, it is not true of this game.

        Args:
            query: what you need to know, in plain words
                   (e.g. "what colour and stats do grazers have").
            asked_by: your agent role, recorded in the retrieval audit log.
        """
        return search_gdd(query, asked_by=asked_by)

except ImportError:  # pragma: no cover -- module stays usable without CrewAI
    gdd_search = None  # type: ignore[assignment]


# --------------------------------------------------------------------------- #
#  CLI -- inspect the knowledge base without running a crew                    #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import sys

    print(build_kb())
    idx = get_index()
    print(f"Chunks: {len(idx.chunks)} | backends: {', '.join(idx.backends)}")
    if idx._embeddings is None and hasattr(idx, "embedding_error"):
        print(f"(embeddings unavailable, BM25 only: {idx.embedding_error})")

    query = " ".join(sys.argv[1:]).strip()
    if query:
        print(f"\nQuery: {query}\n")
        print(_format(retrieve(query, asked_by="cli")))
