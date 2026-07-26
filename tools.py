"""
Deterministic tools for the Morphivore form-authoring crew.

The LLM agents author the *creative / structural* layers (names, flavour, art
specs) at the 25-identity level (5 families x 5 intensities) plus per-family
rank ladders.  These tools own everything that must be exact and reproducible:
the 150-cell grid, the stat maths (GDD 2.4), deterministic expansion to 150
records, assembly of forms.json, the C# loader, and contract validation.

Nothing here calls an LLM -- that is the whole point: the numbers are arithmetic,
not generation.
"""

import json
import re
from pathlib import Path

from crewai.tools import tool

# --------------------------------------------------------------------------- #
#  Data contract -- lifted verbatim from GDD 2.4 / 3.3                          #
# --------------------------------------------------------------------------- #

FAMILIES = ["Yellow", "Red", "Blue", "Purple", "Grey"]
FAMILY_CLASS = {
    "Yellow": "Brawler",
    "Red": "Leaper",
    "Blue": "Sniper",
    "Purple": "Stalker",
    "Grey": "Apex",
}
FAMILY_HEX = {
    "Yellow": "#F2C10E",
    "Red": "#E23A2E",
    "Blue": "#2E6FE2",
    "Purple": "#8A2EE2",
    "Grey": "#8C8C8C",
}

INTENSITIES = ["Pale", "Dusk", "Deep", "Clash", "Rage"]
INTENSITY_FRACTION = {"Pale": 0.25, "Dusk": 0.50, "Deep": 0.75, "Clash": 0.90, "Rage": 1.00}
INTENSITY_PCT = {k: int(v * 100) for k, v in INTENSITY_FRACTION.items()}

RANKS = [1, 2, 3, 4, 5, 6]

# Family multipliers -- axis order: [health, speed, damage, reach, dash]
# (each family's FULL Rage expression; lower intensities express a fraction).
FAMILY_MULT = {
    "Yellow": [1.5, 0.85, 1.5, 0.9, 0.8],
    "Red":    [0.8, 1.30, 0.7, 1.0, 1.6],
    "Blue":   [0.9, 1.00, 1.0, 1.7, 1.0],
    "Purple": [0.9, 1.15, 0.95, 1.2, 1.2],
    "Grey":   [1.3, 1.20, 1.3, 1.15, 1.3],
}

# Rank baselines, indexed by rank-1 (limbs 1..6). GDD 2.4 "limbs set the baseline".
BASELINE = {
    "health": [100, 150, 200, 250, 300, 350],
    "damage": [40, 55, 70, 85, 100, 115],
    "speed":  [12, 13, 14, 15, 16, 17],
    "reach":  [16, 19, 22, 25, 28, 31],
}

# A cube has six faces -- the socket layout is the authored silhouette (GDD 2.4b).
FACE_ORDER = ["+Y", "+X", "-X", "+Z", "-Z", "-Y"]

_HERE = Path(__file__).parent
OUT_DIR = _HERE / "output"
OUT_DIR.mkdir(exist_ok=True)
NAMES_FILE = OUT_DIR / "names.json"
ART_FILE = OUT_DIR / "art.json"
FORMS_FILE = OUT_DIR / "forms.json"
CSHARP_FILE = OUT_DIR / "FormTable.cs"


# --------------------------------------------------------------------------- #
#  Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _parse_json(raw: str):
    """Lenient JSON parse: strips ```json fences and leading/trailing prose."""
    if not isinstance(raw, str):
        return raw
    s = raw.strip()
    s = re.sub(r"^```(?:json)?", "", s).strip()
    s = re.sub(r"```$", "", s).strip()
    # Grab the outermost {...} if there is surrounding prose.
    first, last = s.find("{"), s.rfind("}")
    if first != -1 and last != -1:
        s = s[first : last + 1]
    return json.loads(s)


def compute_stats(family: str, intensity: str, rank: int) -> dict:
    """GDD 2.4 stat maths. Pure function, no LLM.

    effective_mult = 1 + (family_mult - 1) * intensity_fraction
    stat           = rank_baseline * effective_mult
    dash           = speed * effective_dash_mult   (grazer-floor rule)
    """
    frac = INTENSITY_FRACTION[intensity]
    m = FAMILY_MULT[family]  # [health, speed, damage, reach, dash]
    eff = lambda i: 1.0 + (m[i] - 1.0) * frac
    speed = round(BASELINE["speed"][rank - 1] * eff(1), 2)
    return {
        "health": round(BASELINE["health"][rank - 1] * eff(0)),
        "damage": round(BASELINE["damage"][rank - 1] * eff(2)),
        "speed": speed,
        "reach": round(BASELINE["reach"][rank - 1] * eff(3), 2),
        "dash": round(speed * eff(4), 2),
    }


# --------------------------------------------------------------------------- #
#  Tool 1 -- the 150-cell grid (Content & Tone Agent uses this to iterate)     #
# --------------------------------------------------------------------------- #

@tool("get_form_grid")
def get_form_grid() -> str:
    """Return the authoritative Morphivore form space as JSON: the 5 families
    (with their playstyle class), the 5 intensity tiers (with their percentages),
    and the 6 ranks. 5 x 5 x 6 = 150 forms. Call this first so you author every
    family and intensity and miss none."""
    return json.dumps(
        {
            "families": [{"family": f, "class": FAMILY_CLASS[f], "hex": FAMILY_HEX[f]} for f in FAMILIES],
            "intensities": [{"intensity": i, "pct": INTENSITY_PCT[i]} for i in INTENSITIES],
            "ranks": RANKS,
            "total_forms": len(FAMILIES) * len(INTENSITIES) * len(RANKS),
        },
        indent=2,
    )


# --------------------------------------------------------------------------- #
#  Tool 2 -- Content & Tone Agent saves its naming scheme                      #
# --------------------------------------------------------------------------- #

@tool("save_naming_scheme")
def save_naming_scheme(scheme_json: str) -> str:
    """Persist the naming scheme authored by the Content & Tone Agent.

    Expects a JSON object keyed by family (Yellow, Red, Blue, Purple, Grey).
    Each family value MUST contain:
      - "rank_epithets": array of EXACTLY 6 escalating epithets (rank 1 -> 6),
      - "strains": object keyed by the 5 intensities (Pale, Dusk, Deep, Clash,
        Rage); each intensity value is {"strain": <word>, "flavor": <one line>}.
    Voice: primal, crude, comedic (the Cubivore tone). The final form name is
    built deterministically as "<strain> <rank_epithet>".
    Returns a validation summary; fix and re-call if it reports errors.
    """
    try:
        scheme = _parse_json(scheme_json)
    except Exception as e:  # noqa: BLE001
        return f"ERROR: could not parse JSON ({e}). Re-send a single JSON object."

    errors = []
    for fam in FAMILIES:
        node = scheme.get(fam)
        if not isinstance(node, dict):
            errors.append(f"missing family '{fam}'")
            continue
        eps = node.get("rank_epithets")
        if not isinstance(eps, list) or len(eps) != 6:
            errors.append(f"{fam}.rank_epithets must have exactly 6 entries")
        strains = node.get("strains", {})
        for inten in INTENSITIES:
            s = strains.get(inten) if isinstance(strains, dict) else None
            if not isinstance(s, dict) or not s.get("strain") or not s.get("flavor"):
                errors.append(f"{fam}.strains.{inten} needs 'strain' and 'flavor'")
    if errors:
        return "VALIDATION FAILED:\n- " + "\n- ".join(errors)

    NAMES_FILE.write_text(json.dumps(scheme, indent=2))
    return f"OK: naming scheme for {len(FAMILIES)} families saved to {NAMES_FILE.name}."


# --------------------------------------------------------------------------- #
#  Tool 3 -- Creature Art & VFX Agent saves its art scheme                     #
# --------------------------------------------------------------------------- #

@tool("save_art_scheme")
def save_art_scheme(scheme_json: str) -> str:
    """Persist the art / VFX scheme authored by the Creature Art & VFX Agent.

    Expects a JSON object keyed by family. Each family value MUST contain:
      - "silhouette": a one-line family-level shape descriptor,
      - "strains": object keyed by the 5 intensities; each value is
        {"surface": <look of the skin/coat>, "vfx": <the absorb/feedback cue>}.
    Colour hue and saturation are set deterministically from family + intensity;
    do not invent hex values. Returns a validation summary.
    """
    try:
        scheme = _parse_json(scheme_json)
    except Exception as e:  # noqa: BLE001
        return f"ERROR: could not parse JSON ({e}). Re-send a single JSON object."

    errors = []
    for fam in FAMILIES:
        node = scheme.get(fam)
        if not isinstance(node, dict):
            errors.append(f"missing family '{fam}'")
            continue
        if not node.get("silhouette"):
            errors.append(f"{fam}.silhouette is required")
        strains = node.get("strains", {})
        for inten in INTENSITIES:
            s = strains.get(inten) if isinstance(strains, dict) else None
            if not isinstance(s, dict) or not s.get("surface") or not s.get("vfx"):
                errors.append(f"{fam}.strains.{inten} needs 'surface' and 'vfx'")
    if errors:
        return "VALIDATION FAILED:\n- " + "\n- ".join(errors)

    ART_FILE.write_text(json.dumps(scheme, indent=2))
    return f"OK: art scheme for {len(FAMILIES)} families saved to {ART_FILE.name}."


# --------------------------------------------------------------------------- #
#  Tool 4 -- Gameplay Engineer assembles the 150 forms + C# loader             #
# --------------------------------------------------------------------------- #

def _emit_csharp() -> None:
    CSHARP_FILE.write_text(
        """// AUTO-GENERATED by the Morphivore agent crew. Do not edit by hand.
// Loads output/forms.json (the 150 authored Bestiary forms) into typed structs.
using System;
using UnityEngine;

namespace Morphivore.Content
{
    [Serializable]
    public class StatBlock
    {
        public float health;
        public float damage;
        public float speed;
        public float reach;
        public float dash;
    }

    [Serializable]
    public class FormDef
    {
        public string id;
        public string family;
        public string @class;      // serialises as "class"
        public string intensity;
        public int intensity_pct;
        public int rank;
        public string name;
        public string flavor;
        public string base_hex;
        public float saturation;
        public string silhouette;
        public string surface;
        public string vfx;
        public string[] socket_layout;
        public StatBlock stats;
    }

    [Serializable]
    public class FormTable
    {
        public string generated_by;
        public int count;
        public FormDef[] forms;

        /// <summary>Parse the crew's forms.json (root object with a "forms" array).</summary>
        public static FormTable Load(string json) => JsonUtility.FromJson<FormTable>(json);
    }
}
"""
    )


@tool("assemble_forms")
def assemble_forms() -> str:
    """Expand the saved naming + art schemes into the full 150-form forms.json,
    computing every stat block deterministically (GDD 2.4), and emit the C#
    FormTable loader. Reads output/names.json and output/art.json from disk;
    writes output/forms.json and output/FormTable.cs. Returns a summary. Call
    this after both schemes have been saved."""
    if not NAMES_FILE.exists():
        return "ERROR: names.json missing -- the Content & Tone Agent must save its scheme first."
    if not ART_FILE.exists():
        return "ERROR: art.json missing -- the Creature Art & VFX Agent must save its scheme first."

    names = json.loads(NAMES_FILE.read_text())
    art = json.loads(ART_FILE.read_text())

    forms = []
    for fam in FAMILIES:
        epithets = names[fam]["rank_epithets"]
        for inten in INTENSITIES:
            strain = names[fam]["strains"][inten]
            art_strain = art[fam]["strains"][inten]
            for rank in RANKS:
                forms.append(
                    {
                        "id": f"{fam.lower()}_{inten.lower()}_r{rank}",
                        "family": fam,
                        "class": FAMILY_CLASS[fam],
                        "intensity": inten,
                        "intensity_pct": INTENSITY_PCT[inten],
                        "rank": rank,
                        "name": f"{strain['strain']} {epithets[rank - 1]}".strip(),
                        "flavor": strain["flavor"],
                        "base_hex": FAMILY_HEX[fam],
                        "saturation": INTENSITY_FRACTION[inten],
                        "silhouette": art[fam]["silhouette"],
                        "surface": art_strain["surface"],
                        "vfx": art_strain["vfx"],
                        "socket_layout": FACE_ORDER[:rank],
                        "stats": compute_stats(fam, inten, rank),
                    }
                )

    payload = {"generated_by": "morphivore-agent-crew", "count": len(forms), "forms": forms}
    FORMS_FILE.write_text(json.dumps(payload, indent=2))
    _emit_csharp()
    return (
        f"OK: wrote {len(forms)} forms to {FORMS_FILE.name} and the C# loader to "
        f"{CSHARP_FILE.name}. Example -- {forms[0]['name']} ({forms[0]['id']}): {forms[0]['stats']}"
    )


# --------------------------------------------------------------------------- #
#  Tool 5 -- Director validates forms.json against the data contract           #
# --------------------------------------------------------------------------- #

@tool("validate_forms")
def validate_forms() -> str:
    """Validate output/forms.json against the Morphivore data contract:
    exactly 150 forms, all 30 (family x rank) cells x 5 intensities present,
    unique names, required schema fields, correct intensity percentages, and
    stat sanity (positive stats, health rising with rank within a colour). This
    is the Director's ratification gate. Returns PASS with a summary or FAIL
    with the list of violations."""
    if not FORMS_FILE.exists():
        return "FAIL: forms.json does not exist -- assemble_forms must run first."

    data = json.loads(FORMS_FILE.read_text())
    forms = data.get("forms", [])
    problems = []

    if len(forms) != 150:
        problems.append(f"expected 150 forms, found {len(forms)}")

    seen = set()
    names = set()
    required = {"id", "family", "class", "intensity", "intensity_pct", "rank", "name", "stats"}
    health_by_cell = {}
    for f in forms:
        missing = required - f.keys()
        if missing:
            problems.append(f"{f.get('id', '?')}: missing fields {sorted(missing)}")
            continue
        key = (f["family"], f["intensity"], f["rank"])
        if key in seen:
            problems.append(f"duplicate cell {key}")
        seen.add(key)
        if f["name"] in names:
            problems.append(f"duplicate name '{f['name']}'")
        names.add(f["name"])
        if f["intensity_pct"] != INTENSITY_PCT.get(f["intensity"]):
            problems.append(f"{f['id']}: intensity_pct {f['intensity_pct']} != {INTENSITY_PCT.get(f['intensity'])}")
        st = f["stats"]
        if any(st.get(k, 0) <= 0 for k in ("health", "damage", "speed", "reach", "dash")):
            problems.append(f"{f['id']}: non-positive stat {st}")
        health_by_cell.setdefault((f["family"], f["intensity"]), {})[f["rank"]] = st["health"]

    # every (family, intensity, rank) cell present exactly once
    for fam in FAMILIES:
        for inten in INTENSITIES:
            for rank in RANKS:
                if (fam, inten, rank) not in seen:
                    problems.append(f"missing cell ({fam}, {inten}, {rank})")

    # health must rise with rank within a colour+intensity
    for cell, ranks in health_by_cell.items():
        ordered = [ranks[r] for r in sorted(ranks)]
        if any(b <= a for a, b in zip(ordered, ordered[1:])):
            problems.append(f"health not monotonic by rank for {cell}: {ordered}")

    if problems:
        head = problems[:25]
        more = f"\n... and {len(problems) - 25} more" if len(problems) > 25 else ""
        return "FAIL -- contract violations:\n- " + "\n- ".join(head) + more

    return (
        "PASS -- 150 forms, all 30 cells x 5 intensities present, names unique, "
        "stats positive and monotonic by rank. forms.json ratified for the game."
    )
