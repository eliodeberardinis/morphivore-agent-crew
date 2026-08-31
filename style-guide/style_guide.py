"""
Morphivore's style guide
========================

Three constraint types, none of them invented here.

Two are quoted out of the GDD; the third is *measured* from the 235 flavour
lines already shipped in the game — 60 creatures, 150 forms, 25 emblems. A
length rule I made up would be my taste. A length rule derived from the corpus
is the game's own house style, and it moves if the game does.

    C1  TONE         primal, crude, comedic — GDD §3.1, §1
    C2  VOCABULARY   the game's own nouns, and lore that holds — GDD §2.4-2.8
    C3  FORMATTING   measured from the corpus that already exists

Why this game needs it more than most: the GDD states that with "no dialogue,
narrator, item text or lore, form names are the *entire* authorial voice." There
is no plot to carry tone here. If a flavour line drifts into high fantasy, the
drift *is* the damage — there is nothing else holding the register up.
"""

from __future__ import annotations

import json
import re
import statistics as st
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import rag  # noqa: E402 -- the Assignment #4 retrieval layer, unmodified
from common import CONTENT_DIR, GDD_PATH, _HERE  # noqa: E402

KB_DIR = _HERE / "kb-gdd"

# Quoted verbatim from the condensed GDD. Checked at run time; if the design
# moves, the guide says so rather than enforcing a rule the game abandoned.
ANCHORS = {
    "voice": ("§3.1", "owns the voice: primal, crude, comedic (the Cubivore "
                      "tone). With no dialogue, narrator, item text or lore, "
                      "form names are the *entire* authorial voice."),
    "premise": ("§1", "There is no kingdom to save, but there is a world to "
                      "rule"),
    "no_restoration": ("§1", "Morphivore refuses Cubivore's world-restoration "
                             "wrapper; you are not saving anything, you are "
                             "trying to sit on top."),
    "panels_only": ("§2.8", "Panels are the run's only power source"),
}

# ── C2, the game's own lexicon ────────────────────────────────────────────── #

FAMILIES = ["Yellow", "Red", "Blue", "Purple", "Grey"]
INTENSITIES = ["Pale", "Dusk", "Deep", "Clash", "Rage"]
BIOMES = ["Prairies", "Wetlands", "Mountains", "Beach", "Volcanic"]
GAME_NOUNS = ["family", "intensity", "rank", "limb", "form", "panel", "emblem",
              "Alpha", "grazer", "prey", "elite", "Bestiary", "the Blank",
              "buffer", "meat"]

# Generic RPG vocabulary this game does not have. Each entry is a word the
# design deliberately does not use, with what the game says instead.
FOREIGN_LEXICON = {
    "mana": "no magic system exists", "magic": "no magic system exists",
    "spell": "no magic system exists", "enchant": "no magic system exists",
    "rune": "no magic system exists",
    "xp": "rank comes from breeding, not points",
    "experience point": "rank comes from breeding, not points",
    "level up": "you do not level up; you breed to a larger rank",
    "levelling": "you do not level up; you breed to a larger rank",
    "loot": "there is no inventory; panels attach to the body",
    "inventory": "there is no inventory screen",
    "quest": "there are no quests; there is an eating ladder",
    "artifact": "an emblem is a trophy, not an artifact",
    "relic": "an emblem is a trophy, not a relic",
    "potion": "healing comes from eating grazers",
    "dungeon": "the world is five biomes, not dungeons",
    "boss": "the biome champion is an Alpha",
    "chosen one": "there is no destiny; you are one bloodline of many",
    "prophecy": "there is no destiny; you are one bloodline of many",
    "ancient evil": "there is no plot to resolve",
    "save the world": "you are not saving anything, you are trying to sit on top",
}

# Lore claims that are simply false about this game.
LORE_TRAPS = {
    "emblem grants a power": "emblems are trophies; panels are the only power "
                             "source (§2.8)",
    "evolve by eating": "eating changes what you are; only breeding changes "
                        "how big you are (§1)",
    "levels or tiers of identity": "identity is family + intensity + rank",
}

_SENTENCE_END = re.compile(r"[.!?]+")


@lru_cache(maxsize=1)
def corpus() -> dict:
    """Measure the house style from the lines already in the game."""
    lines: dict[str, list[str]] = {}

    creatures = json.loads((CONTENT_DIR / "creatures.json").read_text())
    rows = next(v for v in creatures.values() if isinstance(v, list))
    lines["creatures"] = [r["flavor"] for r in rows if r.get("flavor")]

    forms = json.loads((CONTENT_DIR / "forms.json").read_text())["forms"]
    lines["forms"] = [f["flavor"] for f in forms if f.get("flavor")]

    path = CONTENT_DIR / "emblems.json"
    if path.exists():
        lines["emblems"] = [e["flavor"]
                            for e in json.loads(path.read_text())["emblems"]
                            if e.get("flavor")]

    every = [x for xs in lines.values() for x in xs]
    words = [len(x.split()) for x in every]
    sentences = [len([s for s in _SENTENCE_END.split(x) if s.strip()])
                 for x in every]

    return {
        "n": len(every),
        "sources": {k: len(v) for k, v in lines.items()},
        "words_mean": round(st.mean(words), 1),
        "words_max": max(words),
        "sentences_max": max(sentences),
        "exclamations": sum(x.count("!") for x in every),
        "samples": (lines["creatures"][:3] + lines.get("emblems", [])[:2]),
    }


@lru_cache(maxsize=1)
def name_conventions() -> dict:
    """Naming conventions per content class, measured from the corpus.

    Added after the first gate run over `creatures.json`, where the agent
    flagged all 25 Alpha names as "high-fantasy title cards" and wanted
    "Bonelord of the Shattered Crags" rewritten to "Gristle Knuckle". It was
    right about the tone rule and wrong about the scope: Alpha names follow a
    deliberate convention that the flavour-line voice does not govern, and the
    guide had never said so. Every class below is 100% internally consistent in
    the shipped content, so these are the game's rules, not mine.
    """
    creatures = json.loads((CONTENT_DIR / "creatures.json").read_text())
    rows = next(v for v in creatures.values() if isinstance(v, list))

    by_role: dict[str, list[str]] = {}
    for r in rows:
        by_role.setdefault(r.get("role", "?"), []).append(r.get("name", ""))

    out = {}
    for role, names in by_role.items():
        words = [len(n.split()) for n in names]
        out[role] = {
            "n": len(names),
            "words": (min(words), max(words)),
            "of_the": all(" of the " in n for n in names),
            "the_prefix": all(n.startswith("The ") for n in names),
            "examples": names[:2],
        }

    forms = json.loads((CONTENT_DIR / "forms.json").read_text())["forms"]
    fnames = [f["name"] for f in forms]
    fwords = [len(n.split()) for n in fnames]
    out["form"] = {"n": len(fnames), "words": (min(fwords), max(fwords)),
                   "of_the": False, "the_prefix": False,
                   "examples": fnames[:2]}
    return out


def describe_name_rule(role: str) -> str:
    """The naming convention for one class, in words."""
    conv = name_conventions().get(role)
    if not conv:
        return ("No fixed naming convention for this class; judge the name by "
                "tone and vocabulary only.")
    lo, hi = conv["words"]
    length = f"{lo} words" if lo == hi else f"{lo}-{hi} words"
    shape = ""
    if conv["of_the"]:
        shape = (" and every one follows '<Epithet> of the <Place>' — this is "
                 "the established convention for this class and is CORRECT, "
                 "not a high-fantasy violation")
    elif conv["the_prefix"]:
        shape = " and every one begins 'The '"
    return (f"{role}: all {conv['n']} shipped names are {length}{shape}. "
            f"e.g. {', '.join(repr(e) for e in conv['examples'])}")


def check_name(name: str, role: str) -> list[str]:
    """The objectively checkable half of C4."""
    conv = name_conventions().get(role)
    if not conv or not name:
        return []
    out = []
    lo, hi = conv["words"]
    w = len(name.split())
    if not (lo <= w <= hi):
        out.append(f"name is {w} words; every shipped {role} name is "
                   f"{lo}-{hi}")
    if conv["of_the"] and " of the " not in name:
        out.append(f"all {conv['n']} shipped {role} names use "
                   f"'<Epithet> of the <Place>'; this one does not")
    if conv["the_prefix"] and not name.startswith("The "):
        out.append(f"all {conv['n']} shipped {role} names begin 'The '")
    return out


def measured_limits() -> dict:
    """C3's numbers, taken from the corpus with a little headroom."""
    c = corpus()
    return {
        "max_words": c["words_max"] + 1,      # 23 observed -> 24
        "max_sentences": c["sentences_max"],  # 2
        "max_exclamations": 0,                # 0 in all 235 lines
    }


def check_formatting(text: str) -> list[str]:
    """The objectively checkable half of C3. No model needed."""
    lim = measured_limits()
    out = []
    words = len(text.split())
    if words > lim["max_words"]:
        out.append(f"{words} words; the corpus tops out at "
                   f"{corpus()['words_max']} (limit {lim['max_words']})")
    sentences = len([s for s in _SENTENCE_END.split(text) if s.strip()])
    if sentences > lim["max_sentences"]:
        out.append(f"{sentences} sentences; the corpus never exceeds "
                   f"{lim['max_sentences']}")
    if text.count("!") > lim["max_exclamations"]:
        out.append(f"{text.count('!')} exclamation mark(s); there are zero in "
                   f"all {corpus()['n']} authored lines")
    return out


def find_foreign_words(text: str) -> list[tuple[str, str]]:
    """The objectively checkable half of C2."""
    low = text.lower()
    return [(w, why) for w, why in FOREIGN_LEXICON.items() if w in low]


@lru_cache(maxsize=1)
def verify_anchors() -> dict:
    """Confirm every quoted rule is still in the GDD, and index it for retrieval."""
    KB_DIR.mkdir(exist_ok=True)
    (KB_DIR / "gdd.md").write_text(GDD_PATH.read_text())
    rag.KB_DIR = KB_DIR
    rag.RETRIEVAL_LOG = _HERE / "runs" / "retrieval-log.jsonl"
    rag.RETRIEVAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    rag._index = None

    doc = GDD_PATH.read_text().replace("**", "").replace("*", "")
    present = {k: (q.replace("*", "") in doc) for k, (_, q) in ANCHORS.items()}

    hits = rag.retrieve("voice tone primal crude comedic form names authorial",
                        asked_by="style-guide", k=2)
    return {"present": present, "all_found": all(present.values()),
            "retrieved_sections": [c.section for c, _ in hits]}


def brief(role: str = "") -> str:
    """The style guide as handed to the Generator, Evaluator and Refiner.

    `role` selects the naming convention for the class being judged, so the
    guide governs a flavour line and a name by their own separate rules.
    """
    c, lim = corpus(), measured_limits()
    samples = "\n".join(f'    - "{s}"' for s in c["samples"])
    foreign = ", ".join(sorted(FOREIGN_LEXICON)[:14])

    return f"""\
MORPHIVORE — STYLE GUIDE

The game: you are a cube-creature in a five-biome ecosystem. You eat creatures
to take their colour. Identity is a FIFO colour buffer — one slot per limb,
each holding a family ({', '.join(FAMILIES)}) at an intensity
({' < '.join(INTENSITIES)}) — resolving to one of 150 forms. Rank is limb count
1-6 and comes only from beating an Alpha and breeding. Biomes run
{' -> '.join(BIOMES)}.

This guide is not a general quality standard. It is three constraints taken
from this game's own design document and its own shipped text.

C1 — TONE: primal, crude, comedic.
    GDD {ANCHORS['voice'][0]}: "{ANCHORS['voice'][1]}"
    Physical, concrete, unsentimental, faintly disgusting, occasionally funny.
    Describe meat, bone, dirt, appetite and violence plainly.
    NOT: reverent or epic register, mysticism, awe, destiny, prophecy,
    ceremony, sentimentality, or abstraction.
    GDD {ANCHORS['premise'][0]}: "{ANCHORS['no_restoration'][1]}"
    There is no kingdom to save and no plot to resolve. The fiction is the food
    chain and nothing else.

C2 — VOCABULARY AND LORE: this game's nouns, and claims that hold.
    Use: {', '.join(GAME_NOUNS)}.
    Families are {', '.join(FAMILIES)}. Intensities are {', '.join(INTENSITIES)}.
    Never use generic RPG vocabulary this game does not have — {foreign}, and
    the like. Rank comes from breeding, not from points or levels. Eating
    changes what you ARE, not how big you are.
    Lore that must hold: {ANCHORS['panels_only'][0]} — "{ANCHORS['panels_only'][1]}";
    an emblem is a trophy and grants nothing.

C3 — FORMATTING AND LENGTH: measured from the {c['n']} flavour lines already in
the game ({', '.join(f'{k} {v}' for k, v in c['sources'].items())}).
    At most {lim['max_words']} words (the longest shipped line is
    {c['words_max']}; the mean is {c['words_mean']}).
    At most {lim['max_sentences']} sentence(s).
    ZERO exclamation marks — there are {c['exclamations']} in all {c['n']}
    authored lines.
    No second-person instructions ("Use this to...") and no "This is a..."
    openers. Describe the thing, not what the player should do with it.

C4 — NAMING CONVENTION: names are not flavour lines, and each class has its
own shape, measured from the shipped content.
    {describe_name_rule(role) if role else
     'No class given; judge the name on tone and vocabulary only.'}
    C1's tone rules govern the FLAVOUR line. A name that follows its class
    convention is correct even when that convention reads as a title — do not
    flag an established naming pattern as high fantasy.

The house voice, from lines already shipped:
{samples}"""
