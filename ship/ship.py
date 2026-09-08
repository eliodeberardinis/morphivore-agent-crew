"""
Morphivore — the last mile
==========================

One command from agent output to a playable build.

    python ship.py                # deploy content, then build WebGL
    python ship.py --deploy-only  # stop after deployment
    python ship.py --build-only   # rebuild without redeploying
    python ship.py --check        # report what would happen, write nothing

Before this existed, the gap between "the agents produced content" and "someone
can play it" was four manual acts: copy five JSON files into the Unity project
by hand, open the editor, click through the build dialog, and upload the folder.
Three of those four are now this script. The fourth — publishing — is documented
at the end of a run and in the README, and is the one step a human still does.

What it actually guarantees is narrower and more useful than "it automates the
build": it guarantees the content in the build is *the content the agents
produced*. Every deployed file is hashed and recorded in `build-provenance.json`,
which ships inside the build and is displayed in-game, so the claim "this text
came out of the pipeline" is checkable by a stranger rather than asserted here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CREW = HERE.parent
REPO = CREW.parent
STREAMING = REPO / "Assets" / "StreamingAssets"
BUILD_DIR = REPO / "Builds" / "WebGL"
UNITY = Path("/Applications/Unity/Hub/Editor/6000.4.6f1/Unity.app/Contents/MacOS/Unity")

# Which pipeline authored each content file. The game reads all five at boot.
SOURCES = {
    "forms.json":     (CREW / "output" / "forms.json",
                       "Assignment #3 — Bestiary form crew (CrewAI, 4 agents)"),
    "creatures.json": (CREW / "output" / "creatures.json",
                       "Assignment #4 — RAG content pipeline (8 parallel crews)"),
    "biomes.json":    (CREW / "output" / "biomes.json",
                       "Assignment #4 — RAG content pipeline"),
    "panels.json":    (CREW / "output" / "panels.json",
                       "Assignment #4 — RAG content pipeline"),
    "emblems.json":   (CREW / "ger-emblems" / "output" / "emblems.json",
                       "Assignment #6 — emblem GER pipeline, "
                       "style-checked by #7"),
}

# Hand-authored, not generated: it maps biomes to imported art packs, which is
# an art decision. Recorded as such rather than quietly counted as agent output.
HAND_AUTHORED = {"art-manifest.json": "hand-authored (art pack mapping)"}


def _records(path: Path) -> int:
    """How many records a content file holds, whatever it calls its list."""
    try:
        data = json.loads(path.read_text())
    except Exception:
        return -1
    if isinstance(data, list):
        return len(data)
    for value in data.values():
        if isinstance(value, list):
            return len(value)
    return -1


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def deploy(check: bool) -> dict:
    """Copy every generated content file into the Unity project, and record
    exactly what was copied."""
    print("\n=== 1. Deploy content ===")
    entries, missing = [], []

    for name, (src, origin) in SOURCES.items():
        dst = STREAMING / name
        if not src.exists():
            missing.append(name)
            print(f"  MISSING  {name}  (expected at {src.relative_to(REPO)})")
            continue

        n = _records(src)
        same = dst.exists() and _sha(dst) == _sha(src)
        verb = "unchanged" if same else ("would copy" if check else "copied")
        if not check and not same:
            shutil.copyfile(src, dst)

        entries.append({
            "file": name, "records": n, "origin": origin,
            "sha256_16": _sha(src), "bytes": src.stat().st_size,
            "source": str(src.relative_to(REPO)),
        })
        print(f"  {verb:<10} {name:<16} {n:>4} records   {origin}")

    for name, note in HAND_AUTHORED.items():
        if (STREAMING / name).exists():
            print(f"  {'in place':<10} {name:<16} {'—':>4}           {note}")

    if missing:
        print(f"\n  {len(missing)} file(s) missing — run the owning pipeline first.")

    provenance = {
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "content": entries,
        "hand_authored": HAND_AUTHORED,
        "note": "Written by agent-crew/ship/ship.py. Every file listed here was "
                "produced by the pipeline named in `origin` and copied into the "
                "build unmodified; the hash is of the file as deployed.",
    }
    if not check:
        (STREAMING / "build-provenance.json").write_text(
            json.dumps(provenance, indent=2) + "\n")
        print(f"\n  wrote build-provenance.json "
              f"({sum(e['records'] for e in entries if e['records'] > 0)} "
              f"records across {len(entries)} files)")
    return provenance


def build(check: bool) -> bool:
    """Drive Unity headlessly to a WebGL build."""
    print("\n=== 2. Build WebGL ===")
    if not UNITY.exists():
        print(f"  Unity not found at {UNITY}")
        return False
    if check:
        print(f"  would build -> {BUILD_DIR.relative_to(REPO)}")
        return True

    log = REPO / "Logs" / "webgl-build.log"
    log.parent.mkdir(exist_ok=True)
    cmd = [
        str(UNITY), "-quit", "-batchmode", "-nographics",
        "-projectPath", str(REPO),
        "-executeMethod", "Morphivore.Editor.BuildScript.BuildWebGL",
        "-buildOutput", str(BUILD_DIR),
        "-logFile", str(log),
    ]
    print(f"  {' '.join(cmd[:6])} ...")
    print(f"  log: {log.relative_to(REPO)}  (first build re-imports for WebGL "
          f"and can take several minutes)")

    started = time.time()
    result = subprocess.run(cmd)
    elapsed = time.time() - started

    if result.returncode != 0:
        print(f"  BUILD FAILED after {elapsed:.0f}s (exit {result.returncode})")
        if log.exists():
            errors = [l for l in log.read_text(errors="replace").splitlines()
                      if "error CS" in l or "[Build]" in l]
            for line in errors[-15:]:
                print(f"    {line}")
        return False

    index = BUILD_DIR / "index.html"
    size = sum(f.stat().st_size for f in BUILD_DIR.rglob("*") if f.is_file())
    print(f"  BUILD OK in {elapsed:.0f}s — {size / (1024*1024):.1f} MB")
    print(f"  {index.relative_to(REPO)}")
    return index.exists()


def publish_instructions() -> None:
    """The one step a human still does."""
    print("\n=== 3. Publish (manual) ===")
    print(f"""\
  The build is a plain folder of static files; it needs a host that serves them.

  itch.io, via butler:
      butler push {BUILD_DIR.relative_to(REPO)} <user>/morphivore:html5
  then on the project page set Kind = HTML, tick "This file will be played in
  the browser", and set the viewport to 1280x720.

  Or by hand: zip the *contents* of {BUILD_DIR.name}/ (index.html at the top
  level, not the folder itself) and upload it as an HTML project.

  This build has compression disabled, so it needs no special server headers.""")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deploy-only", action="store_true")
    ap.add_argument("--build-only", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="report what would happen; write nothing")
    args = ap.parse_args()

    print("Morphivore — agent output to playable build")
    print("=" * 52)

    if not args.build_only:
        deploy(args.check)
    if args.deploy_only:
        return 0

    ok = build(args.check)
    if ok and not args.check:
        publish_instructions()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
