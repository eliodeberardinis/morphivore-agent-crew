"""
Targeted repair: re-author only the creature track against recorded findings.

The full loop in crew_world.py re-runs whichever tracks the critics' findings
route to. This script does the same thing for the creature track alone, reading
the findings already on disk -- useful when the panel and biome tracks have
already been repaired and re-running them would just re-pay for work that is
done. Run `crew_world.py --from-drafts` afterwards to assemble and re-judge.
"""

import asyncio
import json

from crew_world import behaviour_crew, names_crew
import tools_world as tw


async def main() -> None:
    findings: list[str] = []
    for name in ("director-verdict.json", "qa-verdict.json"):
        path = tw.VERDICT_DIR / name
        if path.exists():
            findings += json.loads(path.read_text()).get("reason", [])
    if not findings:
        raise SystemExit("No recorded findings -- nothing to repair.")

    # Only the creature-track findings; panels and biomes are repaired already.
    creature_findings = [
        f for f in findings
        if not f.lower().startswith(("panel_", "biomes/"))
    ]

    feedback = (
        "\n\nREPAIR ROUND -- the Director rejected the previous draft. Fix every "
        "violation below and re-save your scheme. Change nothing that was not "
        "flagged; keep every name and line that was not criticised exactly as it "
        "was.\n- " + "\n- ".join(creature_findings)
    )

    print(f"Repairing the creature track against {len(creature_findings)} finding(s)\n")
    await asyncio.gather(
        names_crew(feedback).kickoff_async(),
        behaviour_crew(feedback).kickoff_async(),
    )
    print("\nCreature track re-authored. Now run: python crew_world.py --from-drafts")


if __name__ == "__main__":
    asyncio.run(main())
