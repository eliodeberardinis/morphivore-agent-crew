"""
Morphivore -- World-Content Crew (Assignment #4)
================================================

Builds on the Assignment #3 form-authoring crew (`crew.py`) rather than
replacing it. Three things are added on top of that crew's shape:

  1. RAG.  Every agent gets ONE shared tool, `gdd_search`, over the game's own
     GDD (see rag.py). #3 was game-anchored by transcription -- its facts were
     copied by hand into constants. Here the agents ask the document.
  2. Parallel execution.  The three content tracks fan out concurrently, and
     within the panel track each elite family fans out again, generating ten
     candidates and keeping three.
  3. A critic that sends work back.  #3's Director validated a schema; here a
     deterministic QA & Balance pass and an LLM Director lore/tone pass both
     have to return {"status": "pass"} before anything is ratified, and a
     failure feeds a bounded repair round.

Pipeline
--------

                        get_world_contract  (deterministic ids)
                                   |
      +------------+---------------+-----------+-------------------+
      |            |                           |                   |
  names       behaviour                   biomes            panels x5 families
 (Content    (Creature AI              (World Gen        (Gameplay Engineer,
  & Tone)     Engineer)                 Engineer)         10 candidates each)
      +------------+---------------+-----------+-------------------+
                                   |  assemble_world (deterministic)
                                   |
                    QA & Balance  -> arithmetic critic
                                   |
                    Director       -> lore / tone critic
                                   |
              fail -> repair round (archived)   /   pass -> lore_verified
"""

import asyncio
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from crewai import LLM, Agent, Crew, Process, Task

import tools_world as tw
from rag import build_kb, gdd_search, get_index
from tools import FAMILIES
from world_contract import get_world_contract

load_dotenv()

# CrewAI routes models through LiteLLM, so Claude is addressed as "anthropic/<id>".
# Opus does the judging (the two critics); Sonnet does the bulk authoring.
CRITIC_MODEL = os.getenv("MORPHIVORE_CRITIC_MODEL", "anthropic/claude-opus-5")
AUTHOR_MODEL = os.getenv("MORPHIVORE_AUTHOR_MODEL", "anthropic/claude-sonnet-5")

# No temperature/top_p: the Claude 5 family rejects sampling params.
#
# The critics get a far larger max_tokens than the authors, and that is not
# cosmetic. On Claude Opus 5 adaptive thinking is ON BY DEFAULT and max_tokens
# caps thinking PLUS response text together. The Director reads all 60
# creatures, 15 panels and 5 biomes before ruling, so at 8192 it spent the
# whole budget reasoning and returned an empty message ("Invalid response from
# LLM call - None or empty"). The authors write far less per call and are fine.
# Sonnet 5 runs adaptive thinking by default too, so the authors hit the same
# wall once a repair round appends the critics' findings to their context.
critic_llm = LLM(model=CRITIC_MODEL, max_tokens=32000)
author_llm = LLM(model=AUTHOR_MODEL, max_tokens=24000)

# One repair round. The critic will always find *something* on a fresh pass over
# 80 records, so the bar is "no blocking findings", not "no findings" -- chasing
# a spotless verdict never terminates.
MAX_REPAIR_ROUNDS = 1

TONE = (
    "The voice is primal, crude, and comedic. Morphivore has no dialogue, no "
    "narrator, no item text and no lore -- names and flavour lines are the ENTIRE "
    "authorial voice. Never write backstory, prophecy, factions, gods or ancient "
    "civilisations: the fiction IS the food chain."
)

RAG_RULE = (
    "Before you author anything, call `gdd_search` with plain-language questions "
    "and write from the passages it returns. If a fact is not in a retrieved "
    "passage, it is not true of this game -- do not fill gaps from other games "
    "you know. Call `get_world_contract` first for the fixed ids and the hard "
    "invariants you may not break."
)


def _agent(role: str, goal: str, backstory: str, tools: list, llm=author_llm) -> Agent:
    return Agent(
        role=role, goal=goal, backstory=backstory, tools=tools,
        llm=llm, verbose=True, allow_delegation=False,
    )


# --------------------------------------------------------------------------- #
#  Agents -- every role is chartered in the game's own GDD 3.1                 #
#                                                                              #
#  These are FACTORIES, not singletons, and that is load-bearing: a CrewAI     #
#  Agent owns a stateful executor, so reusing one instance across concurrently  #
#  running crews raises "Executor is already running." The panel track fans out #
#  five Gameplay Engineers at once, so each crew must build its own.           #
# --------------------------------------------------------------------------- #

def content_agent() -> Agent:
    return _agent(
    "Content & Tone Agent",
    "Name every creature in the wild roster in the game's own voice.",
    "You own the game's authorial voice and named the 150 Bestiary forms. Now you "
    "name the world the player eats: grazers, prey, elites, the four trait "
    "minibosses, the Alphas and the Apex. " + TONE,
    [gdd_search, get_world_contract, tw.save_world_names],
)


def creature_ai_agent() -> Agent:
    return _agent(
    "Creature AI Engineer",
    "Author the observable behaviour of every creature role.",
    "You write the traditional enemy AI: flee/hunt state machines, the symmetric "
    "lock -> wind-up -> pounce cycle, pack aggro so defended pockets swarm, and "
    "territorial elites that hold a range. You describe what a player SEES, never "
    "stats -- the numbers are computed from the GDD's own model.",
    [gdd_search, get_world_contract, tw.save_world_behaviour],
)


def gameplay_agent() -> Agent:
    return _agent(
    "Gameplay Engineer",
    "Author candidate decorated panels for one elite family.",
    "You own the run's only power source. Panels bolt visibly onto the creature's "
    "body and each grants exactly one power from a closed vocabulary. You generate "
    "ten candidates so a selection pass can keep the best three. " + TONE,
    [gdd_search, get_world_contract, tw.save_panel_candidates],
)


def worldgen_agent() -> Agent:
    return _agent(
    "World Generation Engineer",
    "Author the five biomes: terrain, pockets, palettes and populations.",
    "You own the procedural biome generator and its content data. You decide what "
    "a Wetlands IS -- what the generator lays down, where the defended pockets sit, "
    "which families the per-run palette can roll, and how much prey stands and "
    "respawns. Gate thresholds and traits are fixed by the contract; you never "
    "invent them.",
    [gdd_search, get_world_contract, tw.save_biome_draft],
)


def qa_agent() -> Agent:
    return _agent(
    "QA & Balance Agent",
    "Prove or disprove every numeric invariant in the generated content.",
    "You own tuning values in content JSON and you read instruments rather than "
    "impressions. Your audit re-derives each expected number from the GDD's own "
    "stat model, so a violation you report is arithmetic, not opinion.",
    [tw.qa_balance_check],
    llm=critic_llm,
)


def director_agent() -> Agent:
    return _agent(
    "Director",
    "Ratify the generated content against the GDD's fiction and voice.",
    "You review every other agent's work against this GDD and own the shared data "
    "contract. You do not rewrite content -- you judge it. You are the only check "
    "that can catch a creature belonging to a family that was cut, meat that is "
    "not allowed to wander, a reward that was demoted to a trophy, or a name that "
    "has drifted out of the game's register into someone else's game.",
    [gdd_search, tw.load_generated, tw.record_lore_verdict],
    llm=critic_llm,
)


# --------------------------------------------------------------------------- #
#  Track builders -- one small Crew each, so they can run concurrently         #
# --------------------------------------------------------------------------- #

def _solo(agent: Agent, description: str, expected: str) -> Crew:
    return Crew(agents=[agent], tasks=[Task(description=description, expected_output=expected,
                                            agent=agent)],
                process=Process.sequential, verbose=True)


def names_crew(feedback: str = "") -> Crew:
    return _solo(
        content_agent(),
        RAG_RULE + "\n\n"
        "Author the naming scheme for the ENTIRE wild roster and save it with "
        "`save_world_names`. Search the GDD for at least: what grazers are and "
        "what colour they carry; what the five colour families are and which were "
        "cut; what the four traits are and which creature carries each; and what "
        "an Alpha is. Names compose deterministically, so author the PARTS:\n"
        "  - one stem + flavour per colour family (prey), and one darkening "
        "prefix per wild tier -- together these make 20 prey names;\n"
        "  - one grazer per biome; one elite per family; one miniboss per trait;\n"
        "  - one Alpha title per family and one epithet per biome -- together "
        "these make the 25 Alpha names; plus the Apex.\n"
        + TONE + "\n" + feedback,
        "Confirmation that save_world_names returned OK.",
    )


def behaviour_crew(feedback: str = "") -> Crew:
    return _solo(
        creature_ai_agent(),
        RAG_RULE + "\n\n"
        "Author the behaviour scheme for every creature role and save it with "
        "`save_world_behaviour`. Search the GDD for: how creatures hunt the player "
        "(lock -> wind-up -> pounce), how smaller and bigger attackers differ, how "
        "prey and grazers react to being locked, what a defended pocket does, and "
        "how an Alpha emerges and hunts. Cover prey per family, grazers, elites per "
        "family, the four trait minibosses (which never flee) and Alphas per family. "
        "Describe only what the player can observe -- no numbers.\n" + feedback,
        "Confirmation that save_world_behaviour returned OK.",
    )


def panel_crew(family: str, feedback: str = "") -> Crew:
    return _solo(
        gameplay_agent(),
        RAG_RULE + "\n\n"
        f"Author TEN candidate decorated panels dropped by the {family} elite, and "
        f"save them with `save_panel_candidates` (family = \"{family}\"). Search the "
        "GDD for what decorated panels are, which creatures drop them, what powers "
        "they grant, where they attach, and the rule about two panels granting the "
        "same power. Ten candidates are authored on purpose: a later selection step "
        "keeps the best three, so give the set real variety across the power "
        f"vocabulary rather than ten versions of one idea. Fit the {family} family's "
        "character. Never attach a panel to the main cubic face.\n"
        + TONE + "\n" + feedback,
        f"Confirmation that save_panel_candidates returned OK for {family}.",
    )


def biome_crew(feedback: str = "") -> Crew:
    return _solo(
        worldgen_agent(),
        RAG_RULE + "\n\n"
        "Author all five biomes and save them with `save_biome_draft`. Search the "
        "GDD for: what each biome is and which traits gate it; how the ambient meat "
        "mix shifts with distance from the entrance; what a defended pocket contains "
        "and what guards it; where the Alpha lair sits; and how many distinct "
        "families a legal per-run palette roll must field. For each biome give the "
        "terrain, the entrance, the deep end, the lair, 2-4 pockets, per-family "
        "palette weights, the standing coloured-prey population and the respawn "
        "rate. Population must comfortably supply that biome's coloured-prey gate "
        "over an eight-minute stay. Do not invent gate numbers or traits.\n" + feedback,
        "Confirmation that save_biome_draft returned OK for all five biomes.",
    )


def director_crew() -> Crew:
    return _solo(
        director_agent(),
        "Ratify the generated world content against the GDD's fiction and voice.\n\n"
        "Call `load_generated` for \"creatures\", then \"panels\", then \"biomes\". "
        "For each, use `gdd_search` to check the claims you are unsure of, then "
        "judge ONLY the authored text -- names, flavour, behaviour, descriptions. "
        "Numbers are the QA agent's job.\n\n"
        "Look hard for these, which are the breaks this game is most prone to:\n"
        "  - a creature belonging to a colour family that does not exist;\n"
        "  - meat at a tier that is not allowed to wander;\n"
        "  - a grazer written as if it carried a colour or fought back;\n"
        "  - an emblem or trophy described as granting a power;\n"
        "  - a trait described as living on a limb rather than the main face;\n"
        "  - a trait carrier placed behind the terrain its own trait unlocks;\n"
        "  - invented lore: factions, gods, prophecy, ancient civilisations, a "
        "world to save;\n"
        "  - tone drift out of primal/crude/comedic into epic fantasy or solemn "
        "high style.\n\n"
        "Then call `record_lore_verdict` exactly once, passing EVERY finding you "
        "have with a severity and -- for blocking findings -- an exact fix:\n"
        '  {"findings": [{"severity": "blocking"|"nit", "id": "...", "detail": "...",\n'
        '                 "fix": {"file": "creatures"|"panels"|"biomes",\n'
        '                         "path": "flavor" | "behaviour.opening" | "attach" | ...,\n'
        '                         "old": "<current text, copied EXACTLY>",\n'
        '                         "new": "<corrected text, ready to ship>"}}]}\n\n'
        "`id` must be the record's OWN id exactly as `load_generated` shows it "
        '-- "prairies", "panel_red_bite", "alpha_beach_grey". Do NOT prefix it '
        'with the file ("biomes/prairies" is wrong); the file goes in `fix.file`.\n\n'
        "The `fix` is not advice -- it is applied verbatim to the file, with no "
        "agent re-writing anything. So copy `old` character-for-character from "
        "what `load_generated` showed you (a mismatch is refused rather than "
        "guessed at), and write `new` as the complete finished value. Supply a "
        "fix for EVERY blocking finding that is wrong text in one field. Omit it "
        "only when no single field edit can solve the problem, and say so in "
        "`detail`.\n\n"
        "Severity is the judgement that matters here. Mark a finding **blocking** "
        "only when the content CONTRADICTS a stated rule in the GDD -- an invented "
        "family or tier, meat that may not wander, a grazer with colour or fight in "
        "it, an emblem granting power, a trait or panel on the wrong real estate, a "
        "carrier behind its own gate, or invented lore. Mark it a **nit** when it is "
        "a preference rather than a contradiction: wording you would tighten, a flat "
        "line, mild repetition.\n\n"
        "Do not soften a real contradiction into a nit to help the content pass, and "
        "do not inflate a wording preference into a blocker. Report everything you "
        "find -- nits are recorded and shipped, blockers are sent back for repair. "
        "Each `detail` must name the id, quote the offending text, cite the GDD "
        "section, and state the correction.",
        "The recorded verdict with its blocking and nit counts.",
    )


# --------------------------------------------------------------------------- #
#  Orchestration                                                               #
# --------------------------------------------------------------------------- #

def _archive(round_no: int, label: str) -> Path:
    """Keep every rejected draft and verdict -- this archive is the evidence
    that the critic caught something and that it was corrected."""
    dest = tw.VERDICT_DIR / f"round-{round_no}-{label}"
    dest.mkdir(parents=True, exist_ok=True)
    for f in (tw.CREATURES_FILE, tw.PANELS_FILE, tw.BIOMES_FILE,
              tw.VERDICT_DIR / "qa-verdict.json",
              tw.VERDICT_DIR / "director-verdict.json"):
        if f.exists():
            shutil.copyfile(f, dest / f.name)
    return dest


def _route(reasons: list[str]) -> set[str]:
    """Decide which authoring tracks a set of violations sends work back to."""
    tracks: set[str] = set()
    for r in (x.lower() for x in reasons):
        if any(k in r for k in ("panel", "power", "stack", "attach")):
            tracks.add("panels")
        if any(k in r for k in ("biome", "palette", "slack", "population", "pocket",
                                "lair", "terrain")):
            tracks.add("biomes")
        if any(k in r for k in ("grazer", "prey", "alpha", "elite", "miniboss",
                                "creature", "apex", "name", "tone", "flavour",
                                "flavor", "family", "clash", "emblem", "trait")):
            tracks.add("creatures")
    return tracks or {"creatures", "panels", "biomes"}


async def _run_authoring(tracks: set[str], feedback: str = "") -> None:
    """Fan out the authoring work. This is where the parallelism lives."""
    jobs: list[tuple[str, Crew]] = []
    if "creatures" in tracks:
        jobs.append(("names", names_crew(feedback)))
        jobs.append(("behaviour", behaviour_crew(feedback)))
    if "biomes" in tracks:
        jobs.append(("biomes", biome_crew(feedback)))
    if "panels" in tracks:
        jobs += [(f"panels:{f}", panel_crew(f, feedback)) for f in FAMILIES]

    print(f"\n>>> fanning out {len(jobs)} concurrent crews: "
          f"{', '.join(n for n, _ in jobs)}\n")
    started = time.perf_counter()
    await asyncio.gather(*(c.kickoff_async() for _, c in jobs))
    print(f"\n>>> {len(jobs)} crews finished in {time.perf_counter() - started:.1f}s "
          f"(wall clock, concurrent)\n")


def _feedback_block(qa: dict, lore: dict) -> str:
    lines = list(qa.get("reason", [])) + list(lore.get("reason", []))
    if not lines:
        return ""
    return (
        "\n\nREPAIR ROUND -- the critics rejected the previous draft. Fix every "
        "violation below and re-save your scheme. Do not change anything they did "
        "not flag.\n- " + "\n- ".join(lines)
    )


async def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    print(build_kb())
    idx = get_index()
    print(f"Knowledge base: {len(idx.chunks)} chunks | retrieval: {', '.join(idx.backends)}")
    print(f"Critics: {CRITIC_MODEL} | Authoring: {AUTHOR_MODEL}\n")

    tracks = {"creatures", "panels", "biomes"}
    feedback = ""
    qa: dict = {}
    lore: dict = {}

    # --from-drafts re-uses authoring already on disk and restarts at assembly.
    # Useful when iterating on the critics without re-paying for the fan-out.
    resume = "--from-drafts" in sys.argv and all(
        f.exists() for f in (tw.NAMES_FILE, tw.BEHAVIOUR_FILE,
                             tw.PANEL_DRAFTS_FILE, tw.BIOME_DRAFT_FILE)
    )

    # When every blocking finding carries a fix, the next round patches the
    # assembled files in place and only re-judges. Re-authoring (and therefore
    # re-assembling) happens only for findings no single edit can solve --
    # assemble_world regenerates from the drafts, so running it after a patch
    # would silently throw the patch away.
    needs_authoring = True

    for rnd in range(MAX_REPAIR_ROUNDS + 1):
        if resume and rnd == 0:
            print(">>> --from-drafts: reusing the authoring already on disk\n")
            print(tw.assemble_world.run())
        elif needs_authoring:
            await _run_authoring(tracks, feedback)
            print(tw.assemble_world.run())
            # Assembly rebuilds ALL THREE files from the drafts, so it wipes
            # patches applied to tracks that were not re-authored. Replay them;
            # drop the ledger entries for tracks that were regenerated, since
            # those records no longer exist in the form the patch described.
            regenerated = {"creatures" if t == "creatures" else t for t in tracks}
            replayed = tw.replay_patches(skip_files=regenerated)
            if replayed:
                print(f">>> replayed {len(replayed)} earlier patch(es) "
                      f"onto the rebuilt files")
        else:
            print(">>> patched in place -- re-judging without re-authoring\n")

        qa = tw.run_qa_check()
        (tw.VERDICT_DIR / "qa-verdict.json").write_text(json.dumps(qa, indent=2))
        print(f"\nQA & Balance: {qa['status'].upper()}")
        for r in qa.get("reason", []):
            print(f"  - {r}")

        # kickoff_async, not kickoff: main() runs inside an event loop, and
        # CrewAI refuses a synchronous kickoff from within one.
        await director_crew().kickoff_async()
        lore_path = tw.VERDICT_DIR / "director-verdict.json"
        lore = json.loads(lore_path.read_text()) if lore_path.exists() else {
            "status": "fail", "reason": ["Director did not record a verdict"]
        }
        print(f"\nDirector (lore/tone): {lore['status'].upper()} "
              f"({lore.get('blocking_count', len(lore.get('reason', [])))} blocking, "
              f"{lore.get('nit_count', 0)} nit)")
        for f in lore.get("findings", []):
            print(f"  [{f['severity']:>8}] {f.get('id', '?')}: {f['detail'][:150]}")

        if qa["status"] == "pass" and lore["status"] == "pass":
            print("\n" + tw.stamp_lore_verified())
            _archive(rnd, "accepted")
            break

        dest = _archive(rnd, "rejected")
        print(f"\nRejected draft archived to {dest}")
        if rnd == MAX_REPAIR_ROUNDS:
            print("Repair budget exhausted -- content is NOT ratified.")
            break

        # Deterministic repair first: apply every fix the critic supplied.
        applied, unpatched = tw.apply_fixes(lore.get("findings", []))
        print(f"\nRepair round {rnd + 1}: patched {len(applied)} finding(s) in place")
        for f in applied:
            print(f"  ~ {f.get('id')}.{f['fix']['path']}")
            print(f"      - {f['fix']['old'][:110]}")
            print(f"      + {f['fix']['new'][:110]}")
        for f in unpatched:
            print(f"  ! {f.get('id')}: {f['skip_reason']}")

        # Re-author only what no single edit could fix.
        if unpatched or qa["status"] != "pass":
            needs_authoring = True
            feedback = _feedback_block(qa, {"reason": [f["detail"] for f in unpatched]})
            tracks = _route(qa.get("reason", []) + [f["detail"] for f in unpatched])
            print(f"  -> re-authoring {sorted(tracks)} for the rest")
        else:
            needs_authoring = False
            feedback = ""
            print("  -> everything was patchable; re-judging the patched files")

    summary = {
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "qa": qa, "director": lore,
        "ratified": qa.get("status") == "pass" and lore.get("status") == "pass",
    }
    (tw.OUT_DIR / "run-summary.json").write_text(json.dumps(summary, indent=2))

    print("\n" + "=" * 70)
    print("Deliverables: output/creatures.json, output/panels.json, "
          "output/biomes.json, output/WorldTables.cs")
    print("Evidence:     output/retrieval-log.jsonl, output/critic-log/")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
