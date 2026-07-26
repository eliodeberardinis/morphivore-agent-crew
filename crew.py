"""
Morphivore -- Bestiary Form-Authoring Crew
==========================================

A 4-agent CrewAI pipeline that authors the 150 Bestiary forms for MORPHIVORE
(a cube-creature game: eat same-or-lower-tier enemies to mutate, evolve, and
dominate an ecosystem). It emits a
game-ready `output/forms.json` (the file the game loads, GDD 3.3) plus a C#
`FormTable` loader.

Pipeline (sequential):

    Content & Tone  ->  Creature Art & VFX  ->  Gameplay Engineer  ->  Director

Each agent maps 1:1 onto a role defined in the game's GDD (3.1 Agent Interfaces).
Remove any one and the pipeline breaks:

  * Content & Tone     -> the forms have no identity / voice (names, flavour).
  * Creature Art & VFX -> the game cannot render a form (silhouette, colour, VFX).
  * Gameplay Engineer  -> the game cannot instantiate a form (no stat blocks).
  * Director           -> nothing enforces the 150-form data contract.

The creative work is done by the LLM agents at the 25-identity level (5 families
x 5 intensities) plus per-family rank ladders; deterministic tools expand that
to the full 150 records and compute every stat exactly (see tools.py).
"""

import os

from dotenv import load_dotenv
from crewai import LLM, Agent, Crew, Process, Task

from tools import (
    assemble_forms,
    get_form_grid,
    save_art_scheme,
    save_naming_scheme,
    validate_forms,
)

load_dotenv()

# CrewAI routes models through LiteLLM, so Claude is addressed as "anthropic/<id>".
MODEL = os.getenv("MORPHIVORE_CREW_MODEL", "anthropic/claude-opus-5")

# No temperature/top_p: Claude Opus 5 rejects sampling params. Bounded max_tokens
# keeps every agent's output small (25-identity schemes, not 150 records).
llm = LLM(model=MODEL, max_tokens=8192)

TONE = "The voice is primal, crude, and comedic. With no dialogue, narrator, or item text in the game, the form names are the ENTIRE authorial voice."

# --------------------------------------------------------------------------- #
#  Agents (roles from GDD 3.1)                                                 #
# --------------------------------------------------------------------------- #

content_agent = Agent(
    role="Content & Tone Agent",
    goal="Author the naming scheme and voice for all 150 Morphivore forms.",
    backstory=(
        "You own the game's entire authorial voice. " + TONE + " You name creatures "
        "by their colour family (a playstyle) and their intensity tier, and you give "
        "each family a ladder of six escalating epithets so a form's name grows meaner "
        "as it gains limbs."
    ),
    tools=[get_form_grid, save_naming_scheme],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

art_agent = Agent(
    role="Creature Art & VFX Agent",
    goal="Author the silhouette, surface look, and feedback VFX for every form.",
    backstory=(
        "You turn colour families and intensity tiers into things the renderer can build: "
        "a family silhouette (the cube's authored socket shape), a per-strain surface look, "
        "and the absorb/feedback VFX cue. Hue and saturation are fixed from family + "
        "intensity, so you never invent colour values -- you describe surface and motion."
    ),
    tools=[get_form_grid, save_art_scheme],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

gameplay_agent = Agent(
    role="Gameplay Engineer",
    goal="Expand the authored schemes into the full 150-form forms.json with exact stats.",
    backstory=(
        "You turn design into data the game can instantiate. Stats come from the GDD's "
        "intensity-scaling rule, computed deterministically by your tool -- you never do "
        "the arithmetic yourself. You assemble the 150 records and emit the C# loader."
    ),
    tools=[assemble_forms],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

director_agent = Agent(
    role="Director",
    goal="Ratify forms.json against the Morphivore data contract; reject anything off-spec.",
    backstory=(
        "You own the shared data contract so 'form', 'colour', and 'intensity' mean one "
        "thing everywhere. You do not rewrite content -- you validate: exactly 150 forms, "
        "every family x intensity x rank cell present, unique names, correct schema and "
        "percentages, sane stats. If it passes, the file is game-ready."
    ),
    tools=[validate_forms],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# --------------------------------------------------------------------------- #
#  Tasks (sequential; disk-based handoff via output/*.json)                    #
# --------------------------------------------------------------------------- #

content_task = Task(
    description=(
        "Call `get_form_grid` to see the 5 families (with playstyle class), 5 intensity "
        "tiers, and 6 ranks. Then author a naming scheme for EVERY family. For each family "
        "provide:\n"
        "  - rank_epithets: 6 escalating epithets (rank 1 = smallest, rank 6 = apex),\n"
        "  - strains: for each of the 5 intensities, a {strain, flavor} pair.\n"
        + TONE
        + " Keep flavour to one crude, funny line. When done, call `save_naming_scheme` "
        "with the whole scheme as one JSON object. If it reports validation errors, fix "
        "them and call it again until it returns OK."
    ),
    expected_output="Confirmation that save_naming_scheme returned OK for all 5 families.",
    agent=content_agent,
)

art_task = Task(
    description=(
        "Using the same family/intensity grid (call `get_form_grid` if needed), author an "
        "art scheme for EVERY family:\n"
        "  - silhouette: one line describing the family's cube-creature shape,\n"
        "  - strains: for each of the 5 intensities, a {surface, vfx} pair -- 'surface' is "
        "the skin/coat look, 'vfx' is the eat/absorb feedback cue.\n"
        "Do not invent hex colours (hue/saturation are set from family+intensity). When "
        "done, call `save_art_scheme` with the whole scheme as one JSON object; fix and "
        "re-call until it returns OK."
    ),
    expected_output="Confirmation that save_art_scheme returned OK for all 5 families.",
    agent=art_agent,
    context=[content_task],
)

assemble_task = Task(
    description=(
        "Call `assemble_forms`. It reads the saved naming and art schemes, expands them to "
        "all 150 forms (5 families x 5 intensities x 6 ranks), computes every stat block "
        "deterministically from the GDD rule, and writes output/forms.json plus the C# "
        "FormTable loader. Report the summary it returns, including the example form."
    ),
    expected_output="The assemble_forms summary confirming 150 forms and the C# loader were written.",
    agent=gameplay_agent,
    context=[content_task, art_task],
)

validate_task = Task(
    description=(
        "Call `validate_forms` to check output/forms.json against the data contract. Report "
        "the result verbatim. If it returns FAIL, clearly state that the crew's output is "
        "NOT ratified and list the violations; if PASS, state that forms.json is game-ready."
    ),
    expected_output="The validate_forms verdict (PASS or FAIL) and a one-line ratification statement.",
    agent=director_agent,
    context=[assemble_task],
)

crew = Crew(
    agents=[content_agent, art_agent, gameplay_agent, director_agent],
    tasks=[content_task, art_task, assemble_task, validate_task],
    process=Process.sequential,
    verbose=True,
)


if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    print(f"Running the Morphivore form-authoring crew on {MODEL} ...\n")
    result = crew.kickoff()
    print("\n" + "=" * 70)
    print(result)
    print("=" * 70)
    print("Deliverable: output/forms.json (150 forms) + output/FormTable.cs")
