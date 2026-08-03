"""
Deterministic tools for the Morphivore world-content crew (Assignment #4).

Same division of labour as `tools.py`: the LLM agents author the *creative*
layer at the identity level, and these tools own everything that must be exact --
stat maths, rank rules, expansion to full rosters, cross-file referential
integrity, and the two critics.

Three content files are produced, all named as required-but-missing in GDD 3.3:

  * creatures.json -- the wild roster (grazers, prey, elites, trait minibosses,
                      Alphas, the Apex): what the spawner reads.
  * panels.json    -- decorated panels, the run's only power source (GDD 2.8).
  * biomes.json    -- the five territories: palettes, pockets, populations,
                      and the two Alpha gate thresholds (GDD 2.5, 3.3).

The QA & Balance critic below is deterministic on purpose: every invariant it
checks is arithmetic derived from the GDD, so a violation is *proved* rather
than judged. The Director's lore/tone critic is the LLM half (see crew_world.py).
"""

import json
from pathlib import Path

from crewai.tools import tool

from tools import (
    BASELINE,
    FAMILIES,
    FAMILY_CLASS,
    FAMILY_HEX,
    FAMILY_MULT,
    INTENSITY_FRACTION,
    _parse_json,
    compute_stats,
)
from world_contract import (
    BIOMES,
    ELITE_ONLY_TIER,
    SLOWEST_DASH,
    TRAITS,
    WILD_TIERS,
    alpha_cells,
    elite_cells,
    grazer_cells,
    miniboss_cells,
    prey_cells,
)

_HERE = Path(__file__).parent
OUT_DIR = _HERE / "output"
OUT_DIR.mkdir(exist_ok=True)

NAMES_FILE = OUT_DIR / "world-names.json"
BEHAVIOUR_FILE = OUT_DIR / "world-behaviour.json"
PANEL_DRAFTS_FILE = OUT_DIR / "panel-drafts.json"
BIOME_DRAFT_FILE = OUT_DIR / "biome-draft.json"

CREATURES_FILE = OUT_DIR / "creatures.json"
PANELS_FILE = OUT_DIR / "panels.json"
BIOMES_FILE = OUT_DIR / "biomes.json"
CSHARP_FILE = OUT_DIR / "WorldTables.cs"

VERDICT_DIR = OUT_DIR / "critic-log"
VERDICT_DIR.mkdir(exist_ok=True)
# Durable record of every patch applied, so a later re-assembly can replay them.
PATCH_LEDGER = VERDICT_DIR / "patch-ledger.json"

# --------------------------------------------------------------------------- #
#  Derived constants                                                           #
# --------------------------------------------------------------------------- #

# Panels are the run's only power source, and the vocabulary is EXACTLY the four
# the GDD names -- 2.8: "Each grants a power: a longer lock range, a stronger
# dash, a tougher guard, brief camouflage."
#
# An earlier version of this table added "bite" and "vigour", reasoning that
# Damage and Health were stats a panel could plausibly touch. That was an
# overreach by this contract, not by the agents: they authored faithfully into
# the slots they were given, and the Director then -- correctly, repeatedly --
# rejected the results for granting powers the game does not have. Damage and
# Health belong to family and intensity (2.4); a bolt-on cannot change them.
PANEL_POWERS = {
    "lock_range": "extends the lock-on cone's reach",
    "dash_power": "a stronger dash",
    "guard": "a tougher guard against incoming pounces",
    "camouflage": "brief camouflage, breaking enemy locks",
}

# "Capacity grows with the body" (GDD 2.8) -- the simplest honest curve.
PANEL_CAPACITY_BY_RANK = {r: r for r in range(1, 7)}

# A biome is played for roughly one fifth of a 35-45 minute run (GDD 2.5).
BIOME_MINUTES = 8.0
SUPPLY_MARGIN = 1.3   # population must beat the eat-count by this much
MIN_WORST_ROLL_SLACK = 1.5   # GDD 3.3 invariant 2

# The fastest player form at a rank is Rage Red (speed multiplier 1.3). An Alpha
# is pinned slightly above it and does NOT inherit its own colour's multiplier,
# so it can never be outrun (GDD 2.5).
ALPHA_SPEED_MARGIN = 1.05


def fastest_player_speed(rank: int) -> float:
    """Speed of the fastest form at a rank -- Rage Red, by the 2.4 stat model."""
    return round(BASELINE["speed"][rank - 1] * FAMILY_MULT["Red"][1], 2)


def alpha_speed(rank: int) -> float:
    return round(fastest_player_speed(rank) * ALPHA_SPEED_MARGIN, 2)


def grazer_flee_speed(order: int) -> float:
    """Deterministically below the slowest dash in the game (GDD 2.3).

    Later biomes graze faster -- but every one stays under 9.6, so no form is
    ever locked out of healing.
    """
    return round(8.6 + 0.2 * (order - 1), 2)


def _biome(biome_id: str) -> dict:
    return next(b for b in BIOMES if b["id"] == biome_id)


def _reachable_tiers(biome: dict) -> set:
    return set(biome["wandering_tiers"]) | set(biome["pocket_tiers"]) | {ELITE_ONLY_TIER}


# --------------------------------------------------------------------------- #
#  Tool 1 -- Content & Tone saves the naming scheme                            #
# --------------------------------------------------------------------------- #

@tool("save_world_names")
def save_world_names(scheme_json: str) -> str:
    """Persist the naming scheme for the whole wild roster.

    Expects ONE JSON object with these keys:
      - "prey_family_stems": keyed by the 5 families; each {"stem", "flavor"}.
        The stem is the creature noun (e.g. "Gutbag"), reused across tiers.
      - "tier_prefixes": keyed by Pale, Dusk, Deep, Rage; each a single word
        that darkens the stem (names compose as "<prefix> <stem>").
      - "grazers": keyed by biome id; each {"name", "flavor"}. Grazers are
        white, limbless and colourless -- names must NOT imply a colour family.
      - "elites": keyed by the 5 families; each {"name", "flavor"}.
      - "minibosses": keyed by Fins, Claws, Coat, Heat; each {"name", "flavor"}.
      - "alpha_titles": keyed by the 5 families; a single title word/phrase.
      - "biome_epithets": keyed by biome id; Alpha names compose as
        "<alpha_title> of the <biome_epithet>".
      - "apex": {"name", "flavor"} -- the rank-6 final boss.
    Voice: primal, crude, comedic. No lore, no factions, no gods, no prophecy.
    Returns a validation summary; fix and re-call until it returns OK.
    """
    try:
        scheme = _parse_json(scheme_json)
    except Exception as e:  # noqa: BLE001
        return f"ERROR: could not parse JSON ({e}). Re-send a single JSON object."

    errors: list[str] = []

    def need(section: str, keys, fields):
        node = scheme.get(section)
        if not isinstance(node, dict):
            errors.append(f"missing section '{section}'")
            return
        for k in keys:
            v = node.get(k)
            if fields is None:
                if not isinstance(v, str) or not v.strip():
                    errors.append(f"{section}.{k} must be a non-empty string")
                continue
            if not isinstance(v, dict) or any(not v.get(f) for f in fields):
                errors.append(f"{section}.{k} needs {sorted(fields)}")

    biome_ids = [b["id"] for b in BIOMES]
    trait_names = [t["trait"] for t in TRAITS]

    need("prey_family_stems", FAMILIES, {"stem", "flavor"})
    need("tier_prefixes", WILD_TIERS, None)
    need("grazers", biome_ids, {"name", "flavor"})
    need("elites", FAMILIES, {"name", "flavor"})
    need("minibosses", trait_names, {"name", "flavor"})
    need("alpha_titles", FAMILIES, None)
    need("biome_epithets", biome_ids, None)

    apex = scheme.get("apex")
    if not isinstance(apex, dict) or not apex.get("name") or not apex.get("flavor"):
        errors.append("apex needs 'name' and 'flavor'")

    if errors:
        return "VALIDATION FAILED:\n- " + "\n- ".join(errors)

    NAMES_FILE.write_text(json.dumps(scheme, indent=2))
    return f"OK: world naming scheme saved to {NAMES_FILE.name}."


# --------------------------------------------------------------------------- #
#  Tool 2 -- Creature AI Engineer saves the behaviour scheme                   #
# --------------------------------------------------------------------------- #

@tool("save_world_behaviour")
def save_world_behaviour(scheme_json: str) -> str:
    """Persist the behaviour scheme for the wild roster (the FSM's content layer).

    Expects ONE JSON object with these keys:
      - "prey": keyed by the 5 families; each
        {"idle", "when_locked", "packs": true|false}.
      - "grazers": {"idle", "when_locked"} -- they never fight back and bolt
        the instant they are locked.
      - "elites": keyed by the 5 families; each
        {"territory", "pack_aggro": true|false, "wind_up"}.
      - "minibosses": keyed by Fins, Claws, Coat, Heat; each
        {"arena", "opening", "wind_up"} -- these do NOT flee and do NOT drop panels.
      - "alphas": keyed by the 5 families; each {"emergence", "hunt", "tell"}.
      - "apex": {"emergence", "hunt", "tell"} -- the rank-6 final boss, which is
        NOT a biome Alpha and must not borrow its machinery. It is not summoned
        by the two gates; it lies dormant in the Ascension domain and wakes only
        when the Bestiary record crosses its threshold, possibly mid-hunt. Rank
        six is not a biome, so it does not hunt you "across the biome".
    Describe observable behaviour only -- no stats, no numbers (the tools compute
    those), no lore.
    Returns a validation summary; fix and re-call until it returns OK.
    """
    try:
        scheme = _parse_json(scheme_json)
    except Exception as e:  # noqa: BLE001
        return f"ERROR: could not parse JSON ({e}). Re-send a single JSON object."

    errors: list[str] = []
    trait_names = [t["trait"] for t in TRAITS]

    for section, keys, fields in [
        ("prey", FAMILIES, {"idle", "when_locked"}),
        ("elites", FAMILIES, {"territory", "wind_up"}),
        ("minibosses", trait_names, {"arena", "opening", "wind_up"}),
        ("alphas", FAMILIES, {"emergence", "hunt", "tell"}),
    ]:
        node = scheme.get(section)
        if not isinstance(node, dict):
            errors.append(f"missing section '{section}'")
            continue
        for k in keys:
            v = node.get(k)
            if not isinstance(v, dict) or any(not v.get(f) for f in fields):
                errors.append(f"{section}.{k} needs {sorted(fields)}")

    grazers = scheme.get("grazers")
    if not isinstance(grazers, dict) or not grazers.get("idle") or not grazers.get("when_locked"):
        errors.append("grazers needs 'idle' and 'when_locked'")

    apex = scheme.get("apex")
    if not isinstance(apex, dict) or any(not apex.get(f) for f in ("emergence", "hunt", "tell")):
        errors.append("apex needs 'emergence', 'hunt' and 'tell' -- it is NOT a biome Alpha "
                      "and must not reuse their wording")

    if errors:
        return "VALIDATION FAILED:\n- " + "\n- ".join(errors)

    BEHAVIOUR_FILE.write_text(json.dumps(scheme, indent=2))
    return f"OK: world behaviour scheme saved to {BEHAVIOUR_FILE.name}."


# --------------------------------------------------------------------------- #
#  Tool 3 -- Gameplay Engineer saves panel CANDIDATES (generate 10, keep 3)    #
# --------------------------------------------------------------------------- #

@tool("save_panel_candidates")
def save_panel_candidates(candidates_json: str) -> str:
    """Persist ten candidate panels dropped by ONE elite family.

    Expects ONE JSON object: {"family": "<Yellow|Red|Blue|Purple|Grey>",
    "candidates": [ 10 objects ]}. Each candidate needs:
      - "name": the panel's name (primal, crude, comedic),
      - "power": one of lock_range, dash_power, guard, camouflage, bite, vigour,
      - "magnitude": a number between 1.05 and 1.60 (a multiplier),
      - "flavor": one crude line,
      - "attach": where on the cube's faces it bolts on -- NEVER the main face,
        which belongs to traits.
    Ten are authored; a later selection step keeps the best three. Panels drop
    from ELITES only -- never grazers, ordinary prey, or trait minibosses.
    Returns a validation summary; fix and re-call until it returns OK.
    """
    try:
        payload = _parse_json(candidates_json)
    except Exception as e:  # noqa: BLE001
        return f"ERROR: could not parse JSON ({e}). Re-send a single JSON object."

    family = payload.get("family")
    if family not in FAMILIES:
        return f"ERROR: 'family' must be one of {FAMILIES}, got {family!r}."

    cands = payload.get("candidates")
    if not isinstance(cands, list) or len(cands) != 10:
        return f"ERROR: expected exactly 10 candidates, got {len(cands) if isinstance(cands, list) else 'none'}."

    errors: list[str] = []
    for i, c in enumerate(cands, 1):
        if not isinstance(c, dict):
            errors.append(f"candidate {i} is not an object")
            continue
        for f in ("name", "power", "magnitude", "flavor", "attach"):
            if c.get(f) in (None, ""):
                errors.append(f"candidate {i} missing '{f}'")
        if c.get("power") not in PANEL_POWERS:
            errors.append(f"candidate {i}: power {c.get('power')!r} not in {sorted(PANEL_POWERS)}")
        try:
            m = float(c.get("magnitude", 0))
            if not 1.05 <= m <= 1.60:
                errors.append(f"candidate {i}: magnitude {m} outside 1.05-1.60")
        except (TypeError, ValueError):
            errors.append(f"candidate {i}: magnitude is not a number")

    if errors:
        return "VALIDATION FAILED:\n- " + "\n- ".join(errors[:20])

    drafts = json.loads(PANEL_DRAFTS_FILE.read_text()) if PANEL_DRAFTS_FILE.exists() else {}
    drafts[family] = cands
    PANEL_DRAFTS_FILE.write_text(json.dumps(drafts, indent=2))
    return (
        f"OK: 10 {family} panel candidates saved ({len(drafts)}/{len(FAMILIES)} families done). "
        "The selection step will keep the best 3."
    )


# --------------------------------------------------------------------------- #
#  Tool 4 -- World Generation Engineer saves the biome draft                   #
# --------------------------------------------------------------------------- #

@tool("save_biome_draft")
def save_biome_draft(draft_json: str) -> str:
    """Persist the authored layer of all five biomes.

    Expects ONE JSON object keyed by biome id (prairies, wetlands, mountains,
    beach, volcanic). Each biome needs:
      - "terrain": one line on what the generator lays down,
      - "entrance": what the soft ground near the entrance is like,
      - "deep_end": what the strong ground near the Alpha lair is like,
      - "lair": the visible landmark the Alpha dens in,
      - "pockets": a list of 2-4 defended pocket descriptions,
      - "palette_weights": an object keyed by family (Yellow/Red/Blue/Purple/Grey)
        with numeric spawn weights; entries may be 0, but the number of NON-ZERO
        families must be at least that biome's min_distinct_colours,
      - "standing_population": integer, coloured prey alive at once,
      - "respawn_per_min": number, coloured prey respawning per minute.
    Population must comfortably supply the biome's coloured-prey gate over an
    eight-minute stay. Do NOT invent gate thresholds or traits -- those are fixed
    by the contract. Returns a validation summary; fix and re-call until OK.
    """
    try:
        draft = _parse_json(draft_json)
    except Exception as e:  # noqa: BLE001
        return f"ERROR: could not parse JSON ({e}). Re-send a single JSON object."

    errors: list[str] = []
    for b in BIOMES:
        node = draft.get(b["id"])
        if not isinstance(node, dict):
            errors.append(f"missing biome '{b['id']}'")
            continue
        for f in ("terrain", "entrance", "deep_end", "lair"):
            if not node.get(f):
                errors.append(f"{b['id']}.{f} is required")
        pockets = node.get("pockets")
        if not isinstance(pockets, list) or not 2 <= len(pockets) <= 4:
            errors.append(f"{b['id']}.pockets must be a list of 2-4 entries")
        weights = node.get("palette_weights")
        if not isinstance(weights, dict):
            errors.append(f"{b['id']}.palette_weights must be an object keyed by family")
        else:
            unknown = set(weights) - set(FAMILIES)
            if unknown:
                errors.append(f"{b['id']}.palette_weights has unknown families {sorted(unknown)}")
            nonzero = sum(1 for f in FAMILIES if float(weights.get(f, 0) or 0) > 0)
            if nonzero < b["min_distinct_colours"]:
                errors.append(
                    f"{b['id']}: only {nonzero} families have non-zero weight, "
                    f"min_distinct_colours is {b['min_distinct_colours']}"
                )
        for f in ("standing_population", "respawn_per_min"):
            try:
                float(node.get(f))
            except (TypeError, ValueError):
                errors.append(f"{b['id']}.{f} must be a number")

    if errors:
        return "VALIDATION FAILED:\n- " + "\n- ".join(errors[:20])

    BIOME_DRAFT_FILE.write_text(json.dumps(draft, indent=2))
    return f"OK: biome draft for {len(BIOMES)} biomes saved to {BIOME_DRAFT_FILE.name}."


# --------------------------------------------------------------------------- #
#  Assembly -- deterministic expansion into the three game files               #
# --------------------------------------------------------------------------- #

def _assemble_creatures(names: dict, behaviour: dict) -> list[dict]:
    out: list[dict] = []

    # -- grazers: white, limbless, colourless, sub-9.6 flee speed (GDD 2.3) --
    for cell in grazer_cells():
        biome = _biome(cell["biomes"][0])
        authored = names["grazers"][biome["id"]]
        out.append({
            "id": cell["id"],
            "role": "grazer",
            "name": authored["name"],
            "flavor": authored["flavor"],
            "family": None,
            "tier": None,
            "rank": 0,
            "limbs": 0,
            "base_hex": "#FFFFFF",
            "carries_colour": False,
            "counts_toward_alpha_gate": False,
            "drops_panels": False,
            "heals_player_pct": 0.25,
            "behaviour": behaviour["grazers"],
            "spawns": [{
                "biome": biome["id"],
                "flee_speed": grazer_flee_speed(biome["order"]),
                "stats": {"health": 30, "damage": 0},
            }],
        })

    # -- ordinary prey: rank = player rank - 1, floored at 1 (GDD 3.3) --
    for cell in prey_cells():
        fam, tier = cell["family"], cell["tier"]
        stem = names["prey_family_stems"][fam]
        spawns = []
        for bid in cell["biomes"]:
            b = _biome(bid)
            rank = max(1, b["player_rank"] - 1)
            spawns.append({
                "biome": bid,
                "rank": rank,
                "pocket_only": bid in cell["pocket_only_in"],
                "stats": compute_stats(fam, tier, rank),
            })
        out.append({
            "id": cell["id"],
            "role": "prey",
            "name": f"{names['tier_prefixes'][tier]} {stem['stem']}".strip(),
            "flavor": stem["flavor"],
            "family": fam,
            "class": FAMILY_CLASS[fam],
            "tier": tier,
            "base_hex": FAMILY_HEX[fam],
            "saturation": INTENSITY_FRACTION[tier],
            "carries_colour": True,
            "counts_toward_alpha_gate": True,
            "drops_panels": False,
            "behaviour": behaviour["prey"][fam],
            "spawns": spawns,
        })

    # -- elites: Clash, at the player's rank, the only panel source (GDD 2.8) --
    for cell in elite_cells():
        fam = cell["family"]
        authored = names["elites"][fam]
        out.append({
            "id": cell["id"],
            "role": "elite",
            "name": authored["name"],
            "flavor": authored["flavor"],
            "family": fam,
            "class": FAMILY_CLASS[fam],
            "tier": ELITE_ONLY_TIER,
            "base_hex": FAMILY_HEX[fam],
            "saturation": INTENSITY_FRACTION[ELITE_ONLY_TIER],
            "carries_colour": True,
            "counts_toward_alpha_gate": True,
            "drops_panels": True,
            "behaviour": behaviour["elites"][fam],
            "spawns": [{
                "biome": b["id"],
                "rank": b["player_rank"],
                "pocket_only": True,
                "stats": compute_stats(fam, ELITE_ONLY_TIER, b["player_rank"]),
            } for b in BIOMES],
        })

    # -- the four trait minibosses: never flee, never drop panels (GDD 2.6a) --
    for cell in miniboss_cells():
        trait = cell["trait"]
        authored = names["minibosses"][trait]
        b = _biome(cell["biomes"][0])
        out.append({
            "id": cell["id"],
            "role": "trait_miniboss",
            "name": authored["name"],
            "flavor": authored["flavor"],
            "family": None,
            "tier": ELITE_ONLY_TIER,
            "grants_trait": trait,
            "opens": cell["opens"],
            "habitat": cell["habitat"],
            "carries_colour": False,
            "counts_toward_alpha_gate": False,
            "drops_panels": False,
            "flees": False,
            "behaviour": behaviour["minibosses"][trait],
            "spawns": [{
                "biome": b["id"],
                "rank": b["player_rank"],
                "pocket_only": True,
                # Minibosses are substantially tougher than ordinary prey; the
                # stat block is the Grey Clash profile at the player's rank.
                "stats": compute_stats("Grey", ELITE_ONLY_TIER, b["player_rank"]),
            }],
        })

    # -- Alphas: mirror-match rank, Clash, flat un-outrunnable speed (GDD 2.5) --
    for cell in alpha_cells():
        fam = cell["family"]
        rank = cell["rank"]
        if cell["role"] == "apex":
            authored = names["apex"]
            name = authored["name"]
            flavour = authored["flavor"]
            # The Apex is not a biome Alpha: it has no gates, no lair in a
            # biome, and hunts in the Ascension. Reusing the Grey Alpha's block
            # gave it their machinery, which the Director correctly rejected.
            behave = behaviour.get("apex") or behaviour["alphas"][fam]
        else:
            bid = cell["biomes"][0]
            name = f"{names['alpha_titles'][fam]} of the {names['biome_epithets'][bid]}"
            flavour = names["prey_family_stems"][fam]["flavor"]
            behave = behaviour["alphas"][fam]
        stats = compute_stats(fam, ELITE_ONLY_TIER, rank)
        stats["speed"] = alpha_speed(rank)          # flat: does NOT inherit colour
        stats["dash"] = alpha_speed(rank)
        out.append({
            "id": cell["id"],
            "role": cell["role"],
            "name": name,
            "flavor": flavour,
            "family": fam,
            "class": FAMILY_CLASS[fam],
            "tier": ELITE_ONLY_TIER,
            "rank": rank,
            "base_hex": FAMILY_HEX[fam],
            "saturation": INTENSITY_FRACTION[ELITE_ONLY_TIER],
            "carries_colour": True,
            "drops_panels": False,
            "drops_emblem": cell["role"] == "alpha",
            "emblem_grants_power": False,           # GDD 2.5 -- a trophy, not a key
            "can_be_outrun": False,
            "behaviour": behave,
            "spawns": [{
                "biome": cell["biomes"][0],
                "rank": rank,
                "pocket_only": False,
                "stats": stats,
            }],
        })

    return out


def _select_panels(drafts: dict) -> list[dict]:
    """Generate-10-keep-3: score each family's candidates and keep the best three.

    Scoring is deterministic so the selection is reproducible and explainable:
    a candidate is rewarded for occupying a power slot the family hasn't taken
    yet (variety), and for a magnitude near the middle of the legal band (a
    panel that is neither pointless nor an auto-include).
    """
    kept: list[dict] = []
    for fam in FAMILIES:
        cands = drafts.get(fam, [])
        chosen: list[dict] = []
        used_powers: set[str] = set()
        pool = sorted(
            cands,
            key=lambda c: abs(float(c["magnitude"]) - 1.30),   # nearest the middle first
        )
        for c in pool:
            if len(chosen) == 3:
                break
            if c["power"] in used_powers:
                continue            # no two kept panels share a power (GDD 2.8)
            used_powers.add(c["power"])
            chosen.append(c)
        for i, c in enumerate(chosen, 1):
            kept.append({
                "id": f"panel_{fam.lower()}_{c['power']}",
                "name": c["name"],
                "flavor": c["flavor"],
                "power": c["power"],
                "power_description": PANEL_POWERS[c["power"]],
                "magnitude": round(float(c["magnitude"]), 2),
                "attach": c["attach"],
                "dropped_by": f"elite_{fam.lower()}",
                "source_family": fam,
                "stacks": False,
                "survives_mutation": True,
                "survives_breeding": True,
                "selected_from_candidates": len(cands),
                "selection_rank": i,
            })
    return kept


def _assemble_biomes(draft: dict) -> list[dict]:
    out = []
    for b in BIOMES:
        authored = draft[b["id"]]
        weights = {f: float(authored["palette_weights"].get(f, 0) or 0) for f in FAMILIES}
        total = sum(weights.values()) or 1.0
        tiers = _reachable_tiers(b)
        reachable = len(tiers) * len(FAMILIES)
        out.append({
            "id": b["id"],
            "name": b["name"],
            "order": b["order"],
            "player_rank": b["player_rank"],
            "terrain": authored["terrain"],
            "entrance": authored["entrance"],
            "deep_end": authored["deep_end"],
            "alpha_lair": authored["lair"],
            "pockets": authored["pockets"],
            "gates_requiring_traits": b["gates_requiring_traits"],
            "traits_introduced": b["traits_introduced"],
            "wandering_tiers": b["wandering_tiers"],
            "pocket_tiers": b["pocket_tiers"],
            "palette_weights": {f: round(w / total, 4) for f, w in weights.items()},
            "min_distinct_colours": b["min_distinct_colours"],
            "standing_population": int(authored["standing_population"]),
            "respawn_per_min": float(authored["respawn_per_min"]),
            "alpha_roster": [f"alpha_{b['id']}_{f.lower()}" for f in FAMILIES],
            "gates": {
                "distinct_forms_required": b["distinct_forms_required"],
                "coloured_prey_required": b["coloured_prey_required"],
            },
            "derived": {
                "reachable_forms": reachable,
                "slack": round(reachable / b["distinct_forms_required"], 2),
                "worst_roll_slack": round(
                    len(tiers) * b["min_distinct_colours"] / b["distinct_forms_required"], 2
                ),
            },
        })
    return out


def _emit_csharp() -> None:
    CSHARP_FILE.write_text(
        """// AUTO-GENERATED by the Morphivore world-content crew. Do not edit by hand.
// Loads creatures.json / panels.json / biomes.json into typed structs.
using System;
using UnityEngine;

namespace Morphivore.Content
{
    [Serializable] public class CreatureStats { public float health; public float damage;
        public float speed; public float reach; public float dash; }

    [Serializable] public class SpawnDef { public string biome; public int rank;
        public bool pocket_only; public float flee_speed; public CreatureStats stats; }

    [Serializable] public class CreatureDef
    {
        public string id, role, name, flavor, family, @class, tier, base_hex;
        public string grants_trait, opens, habitat;
        public int rank;
        public bool carries_colour, counts_toward_alpha_gate, drops_panels;
        public bool drops_emblem, emblem_grants_power, can_be_outrun;
        public SpawnDef[] spawns;
    }

    [Serializable] public class PanelDef
    {
        public string id, name, flavor, power, power_description, attach, dropped_by;
        public float magnitude;
        public bool stacks, survives_mutation, survives_breeding;
    }

    [Serializable] public class GateDef { public int distinct_forms_required;
        public int coloured_prey_required; }

    [Serializable] public class BiomeDef
    {
        public string id, name, terrain, entrance, deep_end, alpha_lair;
        public int order, player_rank, min_distinct_colours, standing_population;
        public float respawn_per_min;
        public string[] gates_requiring_traits, traits_introduced;
        public string[] wandering_tiers, pocket_tiers, pockets, alpha_roster;
        public GateDef gates;
    }

    [Serializable] public class CreatureTable { public int count; public bool lore_verified;
        public CreatureDef[] creatures;
        public static CreatureTable Load(string json) => JsonUtility.FromJson<CreatureTable>(json); }

    [Serializable] public class PanelTable { public int count; public bool lore_verified;
        public PanelDef[] panels;
        public static PanelTable Load(string json) => JsonUtility.FromJson<PanelTable>(json); }

    [Serializable] public class BiomeTable { public int count; public bool lore_verified;
        public BiomeDef[] biomes;
        public static BiomeTable Load(string json) => JsonUtility.FromJson<BiomeTable>(json); }
}
"""
    )


@tool("assemble_world")
def assemble_world() -> str:
    """Expand every saved scheme into the three game-ready JSON files and the C#
    loader. Reads the naming, behaviour, panel-candidate and biome drafts from
    disk; computes all stats, ranks, tiers and thresholds deterministically;
    runs generate-10-keep-3 selection on the panels; writes creatures.json,
    panels.json, biomes.json and WorldTables.cs. Call this once every track has
    saved its scheme. Returns a summary."""
    missing = [
        f.name for f in (NAMES_FILE, BEHAVIOUR_FILE, PANEL_DRAFTS_FILE, BIOME_DRAFT_FILE)
        if not f.exists()
    ]
    if missing:
        return f"ERROR: missing upstream files {missing} -- those tracks must save their schemes first."

    names = json.loads(NAMES_FILE.read_text())
    behaviour = json.loads(BEHAVIOUR_FILE.read_text())
    drafts = json.loads(PANEL_DRAFTS_FILE.read_text())
    biome_draft = json.loads(BIOME_DRAFT_FILE.read_text())

    short = [f for f in FAMILIES if len(drafts.get(f, [])) != 10]
    if short:
        return f"ERROR: these families have no complete candidate set: {short}."

    creatures = _assemble_creatures(names, behaviour)
    panels = _select_panels(drafts)
    biomes = _assemble_biomes(biome_draft)

    CREATURES_FILE.write_text(json.dumps(
        {"generated_by": "morphivore-world-crew", "count": len(creatures),
         "lore_verified": False, "creatures": creatures}, indent=2))
    PANELS_FILE.write_text(json.dumps(
        {"generated_by": "morphivore-world-crew", "count": len(panels),
         "lore_verified": False,
         "capacity_by_rank": PANEL_CAPACITY_BY_RANK, "panels": panels}, indent=2))
    BIOMES_FILE.write_text(json.dumps(
        {"generated_by": "morphivore-world-crew", "count": len(biomes),
         "lore_verified": False, "biomes": biomes}, indent=2))
    _emit_csharp()

    return (
        f"OK: wrote {len(creatures)} creatures, {len(panels)} panels "
        f"(kept 3 of 10 per elite family), {len(biomes)} biomes, plus "
        f"{CSHARP_FILE.name}. Example creature -- {creatures[0]['name']} ({creatures[0]['id']})."
    )


# --------------------------------------------------------------------------- #
#  Critic 1 -- QA & Balance: the arithmetic critic                             #
# --------------------------------------------------------------------------- #

def run_qa_check() -> dict:
    """Prove or disprove every numeric invariant. Pure function, no LLM."""
    problems: list[str] = []

    if not (CREATURES_FILE.exists() and PANELS_FILE.exists() and BIOMES_FILE.exists()):
        return {"status": "fail", "reason": ["assemble_world has not produced the three files yet"]}

    creatures = json.loads(CREATURES_FILE.read_text())["creatures"]
    panels = json.loads(PANELS_FILE.read_text())["panels"]
    biomes = json.loads(BIOMES_FILE.read_text())["biomes"]
    by_id = {c["id"]: c for c in creatures}

    # -- grazers ---------------------------------------------------------- #
    for c in (c for c in creatures if c["role"] == "grazer"):
        for s in c["spawns"]:
            if s["flee_speed"] >= SLOWEST_DASH:
                problems.append(
                    f"{c['id']}: flee speed {s['flee_speed']} >= the slowest dash "
                    f"{SLOWEST_DASH}; a 1-limb Yellow Brawler could never catch it (GDD 2.3)"
                )
        if c["family"] is not None or c["carries_colour"]:
            problems.append(f"{c['id']}: grazers carry no colour (GDD 2.3)")
        if c["counts_toward_alpha_gate"]:
            problems.append(f"{c['id']}: grazers must not count toward the Alpha gate (GDD 2.3)")

    # -- Clash never wanders ---------------------------------------------- #
    for c in creatures:
        if c.get("tier") == ELITE_ONLY_TIER and c["role"] == "prey":
            problems.append(f"{c['id']}: Clash meat never wanders as ordinary prey (GDD 2.4b/2.7)")

    # -- rank rules -------------------------------------------------------- #
    for c in creatures:
        for s in c["spawns"]:
            if "rank" not in s:
                continue
            b = _biome(s["biome"]) if s["biome"] != "ascension" else None
            if b is None:
                continue
            if c["role"] == "prey" and s["rank"] != max(1, b["player_rank"] - 1):
                problems.append(
                    f"{c['id']} in {b['id']}: prey rank {s['rank']} should be "
                    f"{max(1, b['player_rank'] - 1)} (player rank minus one, floored at 1)"
                )
            if c["role"] in ("elite", "alpha") and s["rank"] != b["player_rank"]:
                problems.append(
                    f"{c['id']} in {b['id']}: {c['role']} rank {s['rank']} should be "
                    f"{b['player_rank']} (GDD 3.3)"
                )

    # -- Alphas cannot be outrun ------------------------------------------ #
    for c in (c for c in creatures if c["role"] in ("alpha", "apex")):
        rank = c["rank"]
        got = c["spawns"][0]["stats"]["speed"]
        if got <= fastest_player_speed(rank):
            problems.append(
                f"{c['id']}: speed {got} does not exceed the fastest player form at "
                f"rank {rank} ({fastest_player_speed(rank)}) -- it could be outrun (GDD 2.5)"
            )
        if c.get("emblem_grants_power"):
            problems.append(f"{c['id']}: emblems grant no power of their own (GDD 2.5)")

    # -- panels ------------------------------------------------------------ #
    for p in panels:
        src = by_id.get(p["dropped_by"])
        if src is None:
            problems.append(f"{p['id']}: dropped_by references unknown creature {p['dropped_by']}")
        elif src["role"] != "elite":
            problems.append(
                f"{p['id']}: dropped by a {src['role']}; panels come from elites only (GDD 2.8)"
            )
        if p["power"] not in PANEL_POWERS:
            problems.append(f"{p['id']}: unknown power {p['power']!r}")
    for fam in FAMILIES:
        fam_powers = [p["power"] for p in panels if p["source_family"] == fam]
        if len(fam_powers) != len(set(fam_powers)):
            problems.append(f"{fam}: two kept panels share a power; they would not stack (GDD 2.8)")

    # Panels must never mount on the main cubic face -- that is trait real estate
    # (GDD 2.6a), and 2.8 says panels never crowd it. This was an LLM-critic
    # finding on three separate runs; it is a keyword test, so it belongs here
    # where it costs nothing and cannot be missed.
    # Deliberately conservative. A first version flagged any face word and
    # produced false positives on "rear skull plate, behind the main face" --
    # which is correctly OFF the face. A deterministic check that cries wolf is
    # worse than none, so anything carrying an explicit off-face qualifier is
    # left to the Director's judgement.
    FACE_WORDS = ("brow", "cheek", "temple", "jaw", "forehead", "muzzle",
                  "snout", "chin", "eye socket", "main face", "main cubic face")
    OFF_FACE = ("off the main face", "behind the main face", "away from the main face",
                "not the main face", "behind the face", "rear", "back of", "nape",
                "behind the jaw", "below the jaw", "under the jaw")
    for p in panels:
        attach = str(p.get("attach", "")).lower()
        if any(q in attach for q in OFF_FACE):
            continue
        hit = next((w for w in FACE_WORDS if w in attach), None)
        if hit:
            problems.append(
                f"{p['id']}: attach {p['attach']!r} names main-face real estate "
                f"({hit!r}); the main cubic face is reserved for traits (GDD 2.6a, 2.8)"
            )

    # Names must be unique across the whole panel set -- two panels sharing a
    # name breaks the data contract. Also an LLM-critic finding; also arithmetic.
    names = [p["name"] for p in panels]
    for n in {x for x in names if names.count(x) > 1}:
        problems.append(f"duplicate panel name {n!r} -- ids must map to distinct names")

    # NOTE -- deliberately NOT checked here: whether a trait carrier's *prose*
    # places the fight inside the terrain its own trait unlocks (GDD 3.3
    # invariant 1). It was tried and removed. A keyword test flagged
    # "holding the reedy shallows ... rather than the open water" as a circular
    # gate, because the offending phrase is present and the negation is not
    # visible to a substring match. `attach` is a short noun phrase and suits
    # keyword matching; behaviour is prose, where "X rather than Y" is exactly
    # how a corrected line reads. That distinction is the dividing line between
    # the two critics: this one proves arithmetic and matches literals, the
    # Director reads meaning. The structural half of the invariant -- that the
    # carrier's biome is not itself gated by that trait -- is checked above.

    # -- biomes ------------------------------------------------------------ #
    for b in biomes:
        d = b["derived"]
        if d["worst_roll_slack"] < MIN_WORST_ROLL_SLACK:
            problems.append(
                f"{b['id']}: worst-roll slack {d['worst_roll_slack']} < {MIN_WORST_ROLL_SLACK} "
                f"(GDD 3.3 invariant 2)"
            )
        nonzero = sum(1 for w in b["palette_weights"].values() if w > 0)
        if nonzero < b["min_distinct_colours"]:
            problems.append(
                f"{b['id']}: palette fields {nonzero} families, needs {b['min_distinct_colours']}"
            )
        supply = b["standing_population"] + b["respawn_per_min"] * BIOME_MINUTES
        need = b["gates"]["coloured_prey_required"] * SUPPLY_MARGIN
        if supply < need:
            problems.append(
                f"{b['id']}: supply {supply:.0f} coloured prey over {BIOME_MINUTES:.0f} min "
                f"cannot meet the gate of {b['gates']['coloured_prey_required']} with "
                f"{SUPPLY_MARGIN}x margin ({need:.0f}) (GDD 3.3 invariant 3)"
            )
        for aid in b["alpha_roster"]:
            if aid not in by_id:
                problems.append(f"{b['id']}: alpha roster references missing creature {aid}")

    # -- trait reachability (GDD 3.3 invariant 1) -------------------------- #
    carriers = {c["grants_trait"]: c for c in creatures if c["role"] == "trait_miniboss"}
    for t in TRAITS:
        c = carriers.get(t["trait"])
        if c is None:
            problems.append(f"no carrier authored for trait {t['trait']}")
            continue
        home = c["spawns"][0]["biome"]
        if t["opens"] in _biome(home)["gates_requiring_traits"]:
            problems.append(
                f"{c['id']}: carrier sits behind the terrain its own trait unlocks -- circular gate"
            )

    return {"status": "fail", "reason": problems} if problems else {
        "status": "pass",
        "reason": [],
        "checked": [
            "grazer flee speed below the slowest dash",
            "grazers colourless and outside the Alpha gate",
            "Clash never wanders",
            "prey/elite/alpha rank rules",
            "Alphas cannot be outrun; emblems grant no power",
            "panels dropped by elites only, no duplicate power per family",
            "no panel mounted on main-face real estate (trait territory)",
            "panel names unique across the whole set",
            "worst-roll slack, palette breadth, population supply",
            "alpha roster + panel source referential integrity",
            "trait carriers reachable without their own trait",
        ],
    }


@tool("qa_balance_check")
def qa_balance_check() -> str:
    """Run the QA & Balance Agent's arithmetic audit over the three generated
    files. Every check re-derives its expected value from the GDD's own stat
    model rather than trusting what was written, so a violation is proved.
    Returns {"status": "pass"|"fail", "reason": [...]} as JSON."""
    verdict = run_qa_check()
    (VERDICT_DIR / "qa-verdict.json").write_text(json.dumps(verdict, indent=2))
    return json.dumps(verdict, indent=2)


# --------------------------------------------------------------------------- #
#  Critic 2 support -- the Director reads content and records a lore verdict   #
# --------------------------------------------------------------------------- #

@tool("load_generated")
def load_generated(which: str) -> str:
    """Load generated content for review. `which` is one of: "creatures",
    "panels", "biomes". Returns the authored, human-readable fields only (names,
    flavour, behaviour, descriptions) -- the numbers are the QA agent's job, not
    yours. Read this before judging tone or lore."""
    key = (which or "").strip().lower()
    path = {"creatures": CREATURES_FILE, "panels": PANELS_FILE, "biomes": BIOMES_FILE}.get(key)
    if path is None:
        return 'ERROR: `which` must be one of "creatures", "panels", "biomes".'
    if not path.exists():
        return f"ERROR: {path.name} does not exist yet."

    data = json.loads(path.read_text())
    if key == "creatures":
        rows = [{"id": c["id"], "role": c["role"], "name": c["name"],
                 "flavor": c["flavor"], "family": c.get("family"),
                 "tier": c.get("tier"), "behaviour": c.get("behaviour")}
                for c in data["creatures"]]
    elif key == "panels":
        rows = [{"id": p["id"], "name": p["name"], "flavor": p["flavor"],
                 "power": p["power"], "attach": p["attach"],
                 "dropped_by": p["dropped_by"]} for p in data["panels"]]
    else:
        rows = [{"id": b["id"], "terrain": b["terrain"], "entrance": b["entrance"],
                 "deep_end": b["deep_end"], "alpha_lair": b["alpha_lair"],
                 "pockets": b["pockets"]} for b in data["biomes"]]
    return json.dumps(rows, indent=2)


@tool("record_lore_verdict")
def record_lore_verdict(verdict_json: str) -> str:
    """Record the Director's lore-and-tone ratification, with severities.

    Expects ONE JSON object:
      {"findings": [ {"severity": "blocking"|"nit", "id": "...",
                      "detail": "..."} , ... ]}

    Severity is the whole point of this tool -- get it right:
      * "blocking" -- the content CONTRADICTS a stated rule in the GDD. A colour
        family that does not exist; meat at a tier that may not wander; a grazer
        with a colour or a fight in it; an emblem that grants a power; a trait on
        a limb instead of the main face; a panel on the main face; a trait
        carrier behind the terrain its own trait unlocks; an invented tier,
        mechanic or system; invented lore (factions, gods, prophecy, a world to
        save). These make the content wrong, and they must be fixed.
      * "nit" -- a preference, not a contradiction. Wording you would tighten, a
        line that is a little flat, mild repetition, a name you merely like less.
        Nits are recorded and shipped, not repaired.

    `detail` must name the id, quote the offending text, cite the GDD section,
    and state the correction. Report every finding you have -- do NOT suppress
    small ones to make the content pass; that is what "nit" is for. Content is
    ratified when there are ZERO BLOCKING findings; nits do not block.

    EVERY BLOCKING FINDING MUST CARRY A `fix`, whenever the problem is wrong
    TEXT in one field. The fix is applied verbatim and deterministically -- no
    agent re-writes the file -- so it must be exact:

        "fix": {"file":  "creatures" | "panels" | "biomes",
                "path":  "flavor" | "name" | "behaviour.opening" | "attach" | ...,
                "old":   "<the current value, copied EXACTLY, character for character>",
                "new":   "<the corrected value, complete and ready to ship>"}

    `path` may be dotted to reach a nested field (e.g. "behaviour.opening").
    `old` must match what is in the file exactly or the patch is refused --
    copy it from what `load_generated` showed you, do not retype it from memory.
    Omit `fix` only when no single field edit can solve it (the record is
    structurally wrong, or the same error spans many records); say so in
    `detail`, and that track will be re-authored instead.
    """
    try:
        verdict = _parse_json(verdict_json)
    except Exception as e:  # noqa: BLE001
        return f"ERROR: could not parse JSON ({e}). Re-send a single JSON object."

    findings = verdict.get("findings")
    if not isinstance(findings, list):
        return 'ERROR: "findings" must be a list of {severity, id, detail} objects.'

    errors = []
    for i, f in enumerate(findings, 1):
        if not isinstance(f, dict):
            errors.append(f"finding {i} is not an object")
            continue
        if f.get("severity") not in ("blocking", "nit"):
            errors.append(f'finding {i}: severity must be "blocking" or "nit"')
        if not f.get("detail"):
            errors.append(f"finding {i}: 'detail' is required")
        fix = f.get("fix")
        if fix is not None:
            if not isinstance(fix, dict):
                errors.append(f"finding {i}: 'fix' must be an object")
            else:
                if fix.get("file") not in ("creatures", "panels", "biomes"):
                    errors.append(
                        f'finding {i}: fix.file must be "creatures", "panels" or "biomes"'
                    )
                for k in ("path", "old", "new"):
                    if not isinstance(fix.get(k), str) or not fix.get(k):
                        errors.append(f"finding {i}: fix.{k} must be a non-empty string")
                if fix.get("old") == fix.get("new"):
                    errors.append(f"finding {i}: fix.old and fix.new are identical")
    if errors:
        return "VALIDATION FAILED:\n- " + "\n- ".join(errors[:15])

    blocking = [f for f in findings if f["severity"] == "blocking"]
    nits = [f for f in findings if f["severity"] == "nit"]
    patchable = [f for f in blocking if f.get("fix")]

    record = {
        "status": "fail" if blocking else "pass",
        "blocking_count": len(blocking),
        "nit_count": len(nits),
        "patchable_count": len(patchable),
        "findings": findings,
        # Kept for the repair loop, which only ever acts on blocking findings.
        "reason": [f["detail"] for f in blocking],
    }
    (VERDICT_DIR / "director-verdict.json").write_text(json.dumps(record, indent=2))
    return (
        f"OK: recorded {record['status']} -- {len(blocking)} blocking "
        f"({len(patchable)} with an applicable fix), {len(nits)} nit(s). "
        "Content is ratified when blocking is zero; nits ship as recorded advisories."
    )


# --------------------------------------------------------------------------- #
#  Deterministic repair -- apply the critic's fixes in place                   #
# --------------------------------------------------------------------------- #

def _step(cur, key: str):
    """One hop along a path. Numeric keys index lists (e.g. "pockets.0")."""
    if isinstance(cur, list):
        return cur[int(key)] if key.isdigit() and int(key) < len(cur) else None
    if isinstance(cur, dict):
        return cur.get(key)
    return None


def _dig(obj: dict, path: str):
    """Walk a dotted path, returning (container, key) or (None, None).

    Handles list indices as well as object keys -- `biomes` carries a `pockets`
    array, and a live run produced a fix targeting "pockets.0". A dict-only walk
    silently refused it, so the whole track was sent back for re-authoring over
    a single line.
    """
    parts = path.split(".")
    cur = obj
    for p in parts[:-1]:
        cur = _step(cur, p)
        if cur is None:
            return None, None
    last = parts[-1]
    if isinstance(cur, list):
        if last.isdigit() and int(last) < len(cur):
            return cur, int(last)
        return None, None
    if isinstance(cur, dict) and last in cur:
        return cur, last
    return None, None


def apply_fixes(findings: list[dict]) -> tuple[list[dict], list[dict]]:
    """Apply every blocking finding that carries a `fix`, in place.

    This is the repair mechanism. Re-authoring a whole track to correct one
    field is lossy -- it regenerates the records that were already right, and
    on a live run that traded 1 blocking finding for 7. A fix names one object,
    one field, the exact text to replace and the text to replace it with, so the
    edit touches nothing else.

    A fix whose `old` does not match the file is REFUSED rather than forced:
    a mismatch means the critic was describing different content from what is
    on disk, and guessing would corrupt it.

    Returns (applied, unpatched). `unpatched` is what still needs re-authoring.
    """
    files = {"creatures": (CREATURES_FILE, "creatures"),
             "panels": (PANELS_FILE, "panels"),
             "biomes": (BIOMES_FILE, "biomes")}
    cache: dict[str, dict] = {}
    applied, unpatched = [], []

    for f in findings:
        if f.get("severity") != "blocking":
            continue
        fix = f.get("fix")
        if not fix:
            unpatched.append({**f, "skip_reason": "no fix supplied"})
            continue

        path_obj, key = files.get(fix["file"], (None, None))
        if path_obj is None or not path_obj.exists():
            unpatched.append({**f, "skip_reason": f"unknown or missing file {fix['file']}"})
            continue

        if fix["file"] not in cache:
            cache[fix["file"]] = json.loads(path_obj.read_text())
        data = cache[fix["file"]]

        # The critic writes `id` in free text and a live run namespaced it with
        # the file ("biomes/prairies" instead of "prairies"), which refused every
        # otherwise-valid patch. Normalise rather than insist: strip a leading
        # "<file>/" and match case-insensitively on the bare id.
        raw = str(f.get("id", ""))
        candidates = {raw, raw.split("/")[-1]}
        target = next(
            (o for o in data[key]
             if o.get("id") in candidates
             or str(o.get("id", "")).lower() in {c.lower() for c in candidates}),
            None,
        )
        if target is None:
            unpatched.append({**f, "skip_reason": f"no record with id {raw!r}"})
            continue

        container, field = _dig(target, fix["path"])
        if container is None:
            unpatched.append({**f, "skip_reason": f"path {fix['path']!r} not present"})
            continue
        if container[field] != fix["old"]:
            unpatched.append({**f, "skip_reason":
                              f"`old` does not match the file at {fix['path']} -- refusing to guess"})
            continue

        container[field] = fix["new"]
        applied.append(f)

    for name, data in cache.items():
        files[name][0].write_text(json.dumps(data, indent=2))

    log = {"applied": [{"id": f.get("id"), "file": f["fix"]["file"],
                        "path": f["fix"]["path"],
                        "old": f["fix"]["old"], "new": f["fix"]["new"],
                        "detail": f["detail"]} for f in applied],
           "unpatched": [{"id": f.get("id"), "reason": f["skip_reason"],
                          "detail": f["detail"]} for f in unpatched]}
    (VERDICT_DIR / "patches-applied.json").write_text(json.dumps(log, indent=2))

    # Record every applied patch in a durable ledger. `assemble_world` rebuilds
    # ALL THREE files from the authoring drafts, so a later round that re-authors
    # one track would otherwise silently throw away patches applied to the other
    # two -- which is exactly what a live run did, discarding nine good fixes.
    ledger = json.loads(PATCH_LEDGER.read_text()) if PATCH_LEDGER.exists() else []
    for f in applied:
        entry = {"id": f.get("id"), **f["fix"]}
        if entry not in ledger:
            ledger.append(entry)
    PATCH_LEDGER.write_text(json.dumps(ledger, indent=2))

    return applied, unpatched


def replay_patches(skip_files: set[str] | None = None) -> list[dict]:
    """Re-apply the ledger after an assembly, for files that were NOT re-authored.

    A track that was re-authored is regenerated wholesale and will be re-judged,
    so its old patches are moot -- pass it in `skip_files` to drop them. A track
    that was only patched is rebuilt from the SAME drafts, so it comes back with
    the pre-patch text and every ledger entry's `old` still matches.
    """
    if not PATCH_LEDGER.exists():
        return []
    skip_files = skip_files or set()
    ledger = json.loads(PATCH_LEDGER.read_text())
    keep = [e for e in ledger if e["file"] not in skip_files]
    PATCH_LEDGER.write_text(json.dumps(keep, indent=2))
    if not keep:
        return []
    findings = [{"severity": "blocking", "id": e["id"], "detail": "ledger replay",
                 "fix": {k: e[k] for k in ("file", "path", "old", "new")}}
                for e in keep]
    replayed, _ = apply_fixes(findings)
    return replayed


def stamp_lore_verified() -> str:
    """Set lore_verified=true on all three files once both critics pass."""
    touched = []
    for path in (CREATURES_FILE, PANELS_FILE, BIOMES_FILE):
        data = json.loads(path.read_text())
        data["lore_verified"] = True
        path.write_text(json.dumps(data, indent=2))
        touched.append(path.name)
    return "lore_verified=true stamped on " + ", ".join(touched)
