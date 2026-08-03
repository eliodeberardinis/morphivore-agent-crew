"""
Morphivore -- the world data contract
=====================================

The deterministic half of the Assignment #4 pipeline, in the same spirit as
`tools.py`: nothing here calls an LLM. It publishes the *shape* of the world --
which creatures exist, which biomes exist, how many panels, what rank and tier
each cell carries -- so the three content tracks can author into one shared
namespace **concurrently** instead of waiting on each other.

That is what makes the parallel fan-out honest. `biomes.json` has to name Alpha
rosters and `panels.json` has to name the elites that drop each panel, so if IDs
were invented by whichever agent got there first, the tracks would be forced into
a chain. Fixing the IDs up front removes the dependency, exactly as
`get_form_grid` fixed the 150 cells before any form was named.

Every constant is traceable to a GDD section, cited inline. The QA & Balance
critic re-derives the numbers from these facts rather than trusting them.
"""

import json

from crewai.tools import tool

from tools import FAMILIES, FAMILY_CLASS, INTENSITIES

# --------------------------------------------------------------------------- #
#  Tiers -- where each meat tier lives (GDD 2.4b)                              #
# --------------------------------------------------------------------------- #

# Clash is deliberately absent from every wander list: it is carried only by
# elites, trait minibosses and Alphas, and "never wanders at all" (GDD 2.7).
WILD_TIERS = ["Pale", "Dusk", "Deep", "Rage"]
ELITE_ONLY_TIER = "Clash"

# --------------------------------------------------------------------------- #
#  Biomes (GDD 2.5 gate table, 2.7 traversal, 3.3 generator invariants)        #
# --------------------------------------------------------------------------- #

BIOMES = [
    {
        "id": "prairies",
        "name": "Prairies",
        "order": 1,
        "player_rank": 1,
        "gates_requiring_traits": [],          # GDD 2.7: no gates at all
        "traits_introduced": [],
        "wandering_tiers": ["Pale"],           # GDD 2.4b: Pale wanders everywhere
        "pocket_tiers": ["Dusk"],              # Dusk debuts in Prairies pockets
        "distinct_forms_required": 3,
        "coloured_prey_required": 15,
        "min_distinct_colours": 4,             # GDD 3.3 invariant 2
    },
    {
        "id": "wetlands",
        "name": "Wetlands",
        "order": 2,
        "player_rank": 2,
        "gates_requiring_traits": ["Fins"],
        "traits_introduced": ["Fins"],
        "wandering_tiers": ["Pale", "Dusk"],
        "pocket_tiers": ["Deep"],
        "distinct_forms_required": 5,
        "coloured_prey_required": 20,
        "min_distinct_colours": 4,
    },
    {
        "id": "mountains",
        "name": "Mountains",
        "order": 3,
        "player_rank": 3,
        "gates_requiring_traits": ["Claws", "Coat"],
        "traits_introduced": ["Claws", "Coat"],   # the deliberate difficulty spike
        "wandering_tiers": ["Pale", "Dusk", "Deep"],
        "pocket_tiers": ["Rage"],
        "distinct_forms_required": 7,
        "coloured_prey_required": 25,
        "min_distinct_colours": 4,
    },
    {
        "id": "beach",
        "name": "Beach",
        "order": 4,
        "player_rank": 4,
        "gates_requiring_traits": ["Fins", "Claws"],
        "traits_introduced": ["Heat"],
        "wandering_tiers": ["Pale", "Dusk", "Deep", "Rage"],
        "pocket_tiers": ["Rage"],
        "distinct_forms_required": 9,
        "coloured_prey_required": 30,
        "min_distinct_colours": 5,             # all five families
    },
    {
        "id": "volcanic",
        "name": "Volcanic",
        "order": 5,
        "player_rank": 5,
        "gates_requiring_traits": ["Fins", "Claws", "Coat", "Heat"],
        "traits_introduced": [],
        "wandering_tiers": ["Pale", "Dusk", "Deep", "Rage"],
        "pocket_tiers": ["Rage"],
        "distinct_forms_required": 11,
        "coloured_prey_required": 35,
        "min_distinct_colours": 5,
    },
]

BIOME_IDS = [b["id"] for b in BIOMES]

# --------------------------------------------------------------------------- #
#  Traits (GDD 2.6 / 2.6a)                                                     #
# --------------------------------------------------------------------------- #

# `home_biome` is where the carrier lives; `opens` is the terrain it unlocks.
# Coat's carrier sits in the Mountains FOOTHILLS, below the altitude where cold
# is lethal -- the trait that survives the peaks must be obtainable without first
# surviving the peaks (GDD 2.7, generator invariant 1).
TRAITS = [
    {"trait": "Fins",  "home_biome": "wetlands",  "habitat": "deep marsh hollows",
     "opens": "water", "renders_as": "gill slits cut into the main face"},
    {"trait": "Claws", "home_biome": "mountains", "habitat": "rocky outcrops",
     "opens": "high ground", "renders_as": "hooked ridges along the face edge"},
    {"trait": "Coat",  "home_biome": "mountains", "habitat": "the foothills, below the lethal cold line",
     "opens": "freezing peaks", "renders_as": "a matted shell over the face"},
    {"trait": "Heat",  "home_biome": "beach",     "habitat": "volcanic vents along the shore",
     "opens": "lava fields", "renders_as": "a scorched, glowing seam across the face"},
]

# --------------------------------------------------------------------------- #
#  Hard invariants -- quoted to the agents, re-checked by the critics          #
# --------------------------------------------------------------------------- #

# The slowest dash in the game: a 1-limb Yellow Brawler, 12 x 0.8 (GDD 2.3).
# Grazer flee speed is pinned below this so no form is ever locked out of healing.
SLOWEST_DASH = 9.6

INVARIANTS = [
    "The five colour families are Yellow, Red, Blue, Purple and Grey. Green was CUT "
    "and White is NOT a family -- white is the game's empty state (a bare limb, a "
    "newborn, a grazer). Never author a Green or White family creature. (GDD 2.4)",

    "Grazers carry NO colour, are LIMBLESS, are WHITE, never fight back, and flee "
    f"below {SLOWEST_DASH} speed so even the slowest hunter can catch one. They heal "
    "the player but cannot mutate them, and they do NOT count toward the Alpha's "
    "eat-count. (GDD 2.3)",

    "Clash meat NEVER wanders. It is carried only by elites, trait minibosses and "
    "Alphas. A wandering or ordinary-prey creature can never be Clash. (GDD 2.4b, 2.7)",

    "Emblems grant NO power of their own. An emblem is a trophy taken off a defeated "
    "rival that opens the way onward and enables breeding. Powers come only from "
    "decorated panels. (GDD 2.5)",

    "Panels drop from ELITE creatures only -- never from grazers, never from ordinary "
    "prey, and never from the four trait minibosses. Two panels granting the same "
    "power do not stack. (GDD 2.8)",

    "An Alpha stands at the PLAYER'S OWN RANK -- a true mirror-match -- and always "
    "fights at Clash intensity. Its speed does NOT inherit its colour's multiplier; "
    "it is flat, slightly above the fastest player form at that rank, so it can never "
    "be outrun. (GDD 2.5)",

    "Ordinary prey are pinned at the player's rank minus one, floored at rank 1. "
    "Elites sit at the player's rank. (GDD 3.3)",

    "Traits render on the creature's MAIN CUBIC FACE, never on limbs -- limbs hold "
    "colour. Once acquired a trait is never lost within a run. (GDD 2.6a)",

    "The game has no dialogue, no narrator, no item text and no lore. Do not write "
    "backstory, prophecy, factions, gods or ancient civilisations. The fiction IS the "
    "food chain. (GDD 1, 3.1)",

    "The voice is primal, crude and comedic -- never epic-fantasy, never solemn. "
    "(GDD 3.1, Content & Tone Agent)",
]

# --------------------------------------------------------------------------- #
#  Derived roster skeleton                                                     #
# --------------------------------------------------------------------------- #

def prey_cells() -> list[dict]:
    """The wild prey grid: 5 families x 4 wild tiers = 20 authored identities.

    Deliberately mirrors `get_form_grid`'s 25-identity level -- agents author
    identities, tools expand them across biomes and ranks.
    """
    cells = []
    for family in FAMILIES:
        for tier in WILD_TIERS:
            biomes = [
                b["id"] for b in BIOMES
                if tier in b["wandering_tiers"] or tier in b["pocket_tiers"]
            ]
            cells.append({
                "id": f"prey_{family.lower()}_{tier.lower()}",
                "family": family,
                "class": FAMILY_CLASS[family],
                "tier": tier,
                "role": "prey",
                "biomes": biomes,
                "pocket_only_in": [b["id"] for b in BIOMES if tier in b["pocket_tiers"]],
            })
    return cells


def grazer_cells() -> list[dict]:
    """One grazer per biome. White, limbless, colourless by contract."""
    return [
        {
            "id": f"grazer_{b['id']}",
            "family": None,
            "tier": None,
            "role": "grazer",
            "biomes": [b["id"]],
            "max_flee_speed": SLOWEST_DASH,
        }
        for b in BIOMES
    ]


def elite_cells() -> list[dict]:
    """One Clash elite per family. The only panel source in the game."""
    return [
        {
            "id": f"elite_{family.lower()}",
            "family": family,
            "class": FAMILY_CLASS[family],
            "tier": ELITE_ONLY_TIER,
            "role": "elite",
            "biomes": BIOME_IDS,
            "drops_panels": True,
        }
        for family in FAMILIES
    ]


def miniboss_cells() -> list[dict]:
    """The four trait carriers. Exactly four -- one per trait, no more."""
    return [
        {
            "id": f"miniboss_{t['trait'].lower()}",
            "role": "trait_miniboss",
            "tier": ELITE_ONLY_TIER,
            "trait": t["trait"],
            "biomes": [t["home_biome"]],
            "habitat": t["habitat"],
            "opens": t["opens"],
            "drops_panels": False,
        }
        for t in TRAITS
    ]


def alpha_cells() -> list[dict]:
    """5 biomes x 5 family champions = 25 Alphas, plus the rank-6 Apex.

    Every family appears in every biome's roster because the Alpha that answers
    is the champion of whichever colour the player ate most, and that is not
    known until the run is played (GDD 2.5, generator invariant 4).
    """
    cells = [
        {
            "id": f"alpha_{b['id']}_{family.lower()}",
            "role": "alpha",
            "family": family,
            "class": FAMILY_CLASS[family],
            "tier": ELITE_ONLY_TIER,          # Alphas always fight at Clash
            "rank": b["player_rank"],         # mirror-match, never a rank above
            "biomes": [b["id"]],
        }
        for b in BIOMES
        for family in FAMILIES
    ]
    cells.append({
        "id": "apex",
        "role": "apex",
        "family": "Grey",
        "class": FAMILY_CLASS["Grey"],
        "tier": ELITE_ONLY_TIER,
        "rank": 6,
        "biomes": ["ascension"],
        "record_gate": "wakes only at >=100 of 150 Bestiary forms",
    })
    return cells


def world_contract() -> dict:
    """The whole skeleton, as one object. Pure function, no LLM, no I/O."""
    grazers, prey = grazer_cells(), prey_cells()
    elites, minibosses, alphas = elite_cells(), miniboss_cells(), alpha_cells()
    return {
        "families": [{"family": f, "class": FAMILY_CLASS[f]} for f in FAMILIES],
        "intensities": INTENSITIES,
        "wild_tiers": WILD_TIERS,
        "elite_only_tier": ELITE_ONLY_TIER,
        "biomes": BIOMES,
        "traits": TRAITS,
        "invariants": INVARIANTS,
        "roster": {
            "grazers": grazers,
            "prey": prey,
            "elites": elites,
            "trait_minibosses": minibosses,
            "alphas": alphas,
        },
        "counts": {
            "grazers": len(grazers),
            "prey": len(prey),
            "elites": len(elites),
            "trait_minibosses": len(minibosses),
            "alphas": len(alphas),
            "total_creatures": len(grazers) + len(prey) + len(elites)
                               + len(minibosses) + len(alphas),
            "biomes": len(BIOMES),
        },
    }


# --------------------------------------------------------------------------- #
#  The tool                                                                    #
# --------------------------------------------------------------------------- #

@tool("get_world_contract")
def get_world_contract() -> str:
    """Return MORPHIVORE's authoritative world skeleton as JSON: every biome,
    every creature slot (with its fixed id, role, family, tier and biomes), the
    four traits, and the hard invariants no generated content may break.

    Call this FIRST. The ids here are fixed -- author content for these slots and
    reference these ids. Never invent a creature id, a biome id or a trait: if a
    slot is not in this contract, it does not exist in the game.
    """
    return json.dumps(world_contract(), indent=2)
