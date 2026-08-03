"""
Place ratified content into the Unity project.

This is the step that makes "the engine consumes it" a fact rather than a
description. Assignment #3 emitted `forms.json` + `FormTable.cs` and documented
where they would go; nothing was ever placed. This script does the placing, for
that file and the three new ones:

    output/*.json        ->  Assets/StreamingAssets/     (read at boot)
    output/*Table*.cs    ->  Assets/Scripts/Content/     (typed loaders)

It refuses to deploy content the critics have not ratified -- `lore_verified`
must be true on every JSON file -- so an unreviewed draft can never reach the
game. Run it after `crew_world.py` reports a ratified run, then refresh assets
through the Unity MCP bridge and grep Editor.log for `error CS` (GDD 3.2).

    python deploy_to_unity.py            # deploy
    python deploy_to_unity.py --check    # report only, write nothing
"""

import json
import os
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).parent
OUT_DIR = _HERE / "output"

# This crew lives inside the Morphivore Unity project, so the game is the parent
# directory. When the crew is cloned on its own, point MORPHIVORE_UNITY_ROOT at
# a checkout of the game instead.
UNITY_ROOT = Path(os.getenv("MORPHIVORE_UNITY_ROOT", _HERE.parent))
STREAMING = UNITY_ROOT / "Assets" / "StreamingAssets"
SCRIPTS = UNITY_ROOT / "Assets" / "Scripts" / "Content"

# forms.json is #3's deliverable, carried along so the whole content contract
# lands in one place. It has no lore_verified flag, so it is exempt.
JSON_FILES = ["creatures.json", "panels.json", "biomes.json", "forms.json"]
CS_FILES = ["WorldTables.cs", "FormTable.cs"]
NEEDS_RATIFICATION = {"creatures.json", "panels.json", "biomes.json"}


def check() -> tuple[list[str], list[str]]:
    ready, problems = [], []
    for name in JSON_FILES:
        path = OUT_DIR / name
        if not path.exists():
            problems.append(f"{name}: missing -- run the crew first")
            continue
        if name in NEEDS_RATIFICATION:
            data = json.loads(path.read_text())
            if not data.get("lore_verified"):
                problems.append(
                    f"{name}: lore_verified is false -- the critics have not ratified it"
                )
                continue
        ready.append(name)
    for name in CS_FILES:
        if (OUT_DIR / name).exists():
            ready.append(name)
        else:
            problems.append(f"{name}: missing")
    return ready, problems


def deploy() -> str:
    ready, problems = check()
    if problems:
        return "REFUSED:\n- " + "\n- ".join(problems)

    if not (UNITY_ROOT / "Assets").is_dir():
        return (
            f"REFUSED: {UNITY_ROOT} does not look like a Unity project (no Assets/).\n"
            "Set MORPHIVORE_UNITY_ROOT to a checkout of the Morphivore game."
        )

    STREAMING.mkdir(parents=True, exist_ok=True)
    SCRIPTS.mkdir(parents=True, exist_ok=True)

    placed = []
    for name in JSON_FILES:
        shutil.copyfile(OUT_DIR / name, STREAMING / name)
        placed.append(f"Assets/StreamingAssets/{name}")
    for name in CS_FILES:
        shutil.copyfile(OUT_DIR / name, SCRIPTS / name)
        placed.append(f"Assets/Scripts/Content/{name}")

    return "Placed:\n- " + "\n- ".join(placed) + (
        "\n\nNext: refresh assets through the Unity MCP bridge, wait for the "
        "domain reload (8-13 s), then grep ~/Library/Logs/Unity/Editor.log for "
        "'error CS'."
    )


if __name__ == "__main__":
    if "--check" in sys.argv:
        ready, problems = check()
        print("Ready: " + (", ".join(ready) or "nothing"))
        if problems:
            print("Blocked:\n- " + "\n- ".join(problems))
        sys.exit(1 if problems else 0)
    print(deploy())
