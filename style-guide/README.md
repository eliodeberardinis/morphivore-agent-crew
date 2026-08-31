# Morphivore — Style Guide Agent

**Assignment #7.** A Generator → Evaluator → Refiner loop that enforces
**Morphivore's** own voice on real content for the game. The Evaluator scores 1–10
and explains itself; the Refiner acts on that reason; the loop runs unattended.

```bash
cd agent-crew/style-guide
python loop.py --demo    # the three before/after demonstrations
python loop.py --check   # generate on-brand content and score it (control)
python loop.py --gate ../ger-emblems/output/emblems.json   # score a real content file
```

## Pipeline connection

> This Style Guide Agent runs immediately after the Generator in my Assignment #6 emblem
> pipeline (`agent-crew/ger-emblems/forge.py`), scoring every generated emblem name and
> flavour line against Morphivore's voice and refining anything below 9/10 before the
> rule Evaluator checks it for power grants.

That is not a plan. Running it over the 25 emblems that pipeline had already shipped
into the game caught two live defects — see [Enforcement on shipped content](#enforcement-on-real-shipped-content).

---

## The style guide

Three constraint types. Two are quoted out of the GDD; the third is **measured** from the
235 flavour lines already in the game. Every quote is verified present in the document at
run time, and the run warns if one has stopped matching.

### C1 — Tone: primal, crude, comedic

> **GDD §3.1** — "owns the voice: **primal, crude, comedic** (the Cubivore tone). With no
> dialogue, narrator, item text or lore, form names are the *entire* authorial voice."

> **GDD §1** — "Morphivore refuses Cubivore's world-restoration wrapper; you are not
> saving anything, you are trying to sit on top."

Physical, concrete, unsentimental, faintly disgusting, occasionally funny. Not reverent,
mystical, ceremonial or sentimental. There is no kingdom to save and no plot to resolve.

That first quote is why this game needs the agent more than most: there is no dialogue or
lore carrying the tone, so a flavour line drifting into high fantasy **is** the damage.
Nothing else is holding the register up.

### C2 — Vocabulary and lore: this game's nouns, and claims that hold

Required: family (Yellow / Red / Blue / Purple / Grey), intensity (Pale → Dusk → Deep →
Clash → Rage), rank as limb count 1–6, form, panel, emblem, Alpha, grazer, prey, elite,
Bestiary, the Blank, buffer, meat.

Forbidden — each with what this game says instead:

| Foreign word | Why it is wrong here |
|---|---|
| mana, magic, spell, rune | no magic system exists |
| XP, level up | rank comes from breeding, not points |
| loot, inventory | there is no inventory; panels attach to the body |
| quest, dungeon | there are no quests; there is an eating ladder |
| artifact, relic | an emblem is a trophy, not an artifact |
| **boss** | **the biome champion is an Alpha** |
| prophecy, chosen one, ancient evil | there is no destiny and no plot |

Plus lore that must hold: **GDD §2.8** — *"Panels are the run's only power source"*, so an
emblem grants nothing.

### C3 — Formatting and length: measured, not invented

Taken from the **235** flavour lines already shipped — 60 creatures, 150 forms, 25 emblems:

| Rule | Where the number comes from |
|---|---|
| ≤ 24 words | longest shipped line is 23; mean is 11.7 |
| ≤ 2 sentences | no shipped line exceeds 2 |
| **0 exclamation marks** | there are **zero** in all 235 lines |
| No second-person instruction, no "This is a…" openers | shipped lines describe the thing, not what to do with it |

A length limit I invented would be my taste. One derived from the corpus is the game's own
house style, and it moves when the game does.

### C4 — Naming convention: names are not flavour lines

Added **because the agent argued me into it** — see
[what the gate found](#3-forms-150--the-agent-found-a-gap-in-my-guide). Every content
class in the game has its own naming shape, and all six are 100% internally consistent in
the shipped content:

| Class | n | Convention | Example |
|---|---|---|---|
| grazer | 5 | one word | `Puffgrub` |
| prey | 20 | exactly two words | `Scrawny Thumper` |
| elite | 5 | begins `The` | `The Knucklebreaker` |
| trait_miniboss | 4 | begins `The` | `The Mudking` |
| **alpha** | **25** | **`<Epithet> of the <Place>`** | `Bonelord of the Trampled Fields` |
| form | 150 | 2–6 words, never `of the` | `Sniffling Gut-Puncher` |

C1's tone rules govern the **flavour line**. A name that keeps its class convention is
correct even when that convention reads as a title.

---

## The loop

| Agent | File | What it does |
|---|---|---|
| **Generator** | [`generator.py`](generator.py) | Writes a name and flavour line for a real subject from `creatures.json`. In demo mode it gets a deliberately off-brand brief **and no style guide at all**. |
| **Evaluator** | [`evaluator.py`](evaluator.py) | Grades each constraint 1–10, returns an overall **SCORE + REASON**, and lists every violation with the offending phrase. |
| **Refiner** | [`refiner.py`](refiner.py) | Rewrites from that reason, keeping whatever already worked. |
| Loop | [`loop.py`](loop.py) | Runs it to 9/10 or the 3-pass limit, unattended. |

**The score is the weighted worst case, not an average.** A line that nails the tone and
invents a magic system is not a 7 — in this game a single foreign noun is the whole
failure, because there is no plot to absorb it.

**Objective checks run in code first.** Word count, sentence count, exclamation marks and
the foreign-lexicon scan are deterministic, and their results are handed to the Evaluator
as established fact. The model is never asked to count words or spot "mana"; it is asked
to judge register, which is the part code cannot do.

**Scoring exists for the Refiner's benefit.** "Fail" gives it nothing to aim at, so it
would re-roll the whole line and lose what was already right. A score plus a named phrase
gives it a target — and prevents the regression the Assignment #6 circuit breaker had to
catch after the fact.

---

## Before / after — three violation classes

All three use real subjects from `creatures.json`. The Generator was given the off-brand
brief and **no style guide**, so everything the Evaluator caught, it caught on its own.

### 1 · Tone (C1) — 1/10 → 9/10

*Subject: Bonelord of the Trampled Fields (Clash Yellow Alpha). Brief: "reverent high
fantasy… ancient artifact of untold power, wreathed in destiny."*

**BEFORE** — *The Aureate Horn of the Bonelord*
> Hewn from the last king of the herd, whose hooves wrote thunder across the grasslands
> and whose bones the prairie still bows toward. Lift it, and the trampled fields remember
> their sovereign; the yellow of high summer rises in you like a war-hymn, and the earth
> itself consents to your passage.

```
SCORE: 1/10  (C1 tone 1, C2 vocabulary 2, C3 formatting 1)
REASON: Every constraint is breached at once, and the piece reads as a high-fantasy
relic blurb rather than a Morphivore emblem line. Tone: 'whose bones the prairie still
bows toward', 'the trampled fields remember their sovereign' and 'like a war-hymn' are
reverence, royalty and hymn-register; this game's emblems are body parts you pried off
a corpse...
```

**AFTER** — *The Cracked Yellow Horn* — **9/10**
> Twisted off the herd's Alpha while it was still warm, yellow gone brown at the base, and
> it still stinks of the animal.

### 2 · Vocabulary and lore (C2) — 1/10 → 9/10

*Subject: The Knucklebreaker (Clash Yellow elite). Brief: "classic RPG item description…
mana, XP, rare loot from a dungeon boss, level up."*

**BEFORE** — *Knucklebreaker's Gilded Fist*
> Rare loot from the dungeon boss himself: restores 40 mana, grants 500 XP, and clenches
> you one punch closer to the next level.

```
SCORE: 1/10  (C1 tone 2, C2 vocabulary 1, C3 formatting 4)
REASON: This is a loot-drop stat block from a different genre, not a Morphivore line.
Every noun is foreign: 'Rare loot from the dungeon boss himself' imports inventory,
dungeons and bosses into a game whose world is five biomes and whose champion is an
Alpha; 'restores 40 mana' invents a magic system that does not exist; 'grants 500 XP'
and 'one punch closer to the next level' replace rank-from-breeding...
```

**AFTER** — *Knucklebreaker's Fist* — **9/10**
> Four knuckles fused hard as gravel, still cocked to swing. The arm behind them is meat
> in your gut and buys you nothing.

*(Note the last clause — the Refiner reached for the panels-only rule on its own.)*

### 3 · Formatting and length (C3) — 2/10 → 9/10

*Subject: Scrawny Thumper (Pale Yellow prey). Brief: "enthusiastic, at least four
sentences, exclamation marks, tell the player what to do."*

**BEFORE** — *Scrawny Thumper*
> A jittery little scrap of pale yellow, all knees and nerves, thumping out a panic-drum
> you can feel through the soil! Don't let the ribs fool you — that faded straw hide is the
> purest Pale Yellow you'll find this early, and it comes off clean! Chase it into a dead
> end, take it in one bite, and wear that soft custard glow like you were born in it! You'll
> love how the Thumper's colour makes every brighter yellow ahead look absolutely gorgeous
> by comparison — go get it, and go get seconds!

```
SCORE: 2/10  (C1 tone 3, C2 vocabulary 8, C3 formatting 1)
REASON: C3 is broken on every measurable axis at once: 93 words against a 24-word
ceiling, 4 sentences against 2, and 4 exclamation marks where the 235 shipped lines
contain zero. On top of that the whole back half is second-person instruction — "Chase
it into a dead end, take it in one bite" and "go get it, and go get seconds" — which the
guide forbids outright...
```

**AFTER** — *Scrawny Thumper* — **9/10**
> All knees and nerves, thumping a panic-drum through the soil, ribs showing through a Pale
> Yellow hide worth exactly one bite.

Note the C2 score of 8 here: the vocabulary was mostly fine, and only formatting and tone
sank it. A binary verdict would have thrown that information away.

---

## Enforcement on real shipped content

The demos prove the loop works on content built to fail. The harder question is whether it
finds anything in content that already passed review — so I ran it over all three of the
game's shipped text corpora, written by three different pipelines across three months.

| Corpus | Author | Mean first score | Refined |
|---|---|---|---|
| `emblems.json` (25) | Assignment #6, with a voice brief | **8.70** | 2 |
| `creatures.json` (60) | Assignment #4 crew | **7.63** | 38 |
| `forms.json` (150) | Assignment #3 crew | **6.64** | 124 |

**The trend is the finding.** The further content sits from the guide — in time, and in
whether its author ever had a voice brief — the lower it scores. Emblems were written last
month against an explicit brief; forms were written in July, before any of this existed.
That is the agent detecting authorial drift across the project's own history.

### 1 · Emblems (25) — two real catches, both deployed

| Emblem | Score | What the agent caught |
|---|---|---|
| `emblem_mountains_grey` | **3/10** | Named *"Twin-Horn **Boss**"*. This game's biome champions are **Alphas**; "boss" is vocabulary from a different genre. |
| `emblem_prairies_purple` | **6/10** | *"so hold it by the fat end"* — second-person instruction, which C3 forbids. |

```
"Twin-Horn Boss"  →  "Twin-Horn Emblem"
  Both horns and the skull between them, matched so well you'd swear it was made to annoy you.
  →  ...matched so evenly you spent a while deciding which one to twist off first.

"Drip Fang"  (name kept)
  Snapped off at the gum and still beading, so hold it by the fat end.
  →  Snapped off at the gum and still beading, the fat end slick where a thumb dug in.
```

Neither was findable by the #6 pipeline, which only ever asked whether an emblem granted a
power. Both were live in the game. The repaired file still passes #6's rule Evaluator —
0 failures, all set-level checks green — and is now deployed, so the two pipelines compose
rather than fight.

### 2 · Creatures (60) — one real cluster, in nine records

Nine Blue-family records — five Alphas and four prey — all carry the same line:

> One good eye and a better **trigger**; useless the second you're inside its arms.

A trigger is a firearm. This game's only tools are teeth, limbs and appetite, and the
word had been shipped in nine places since the #4 crew wrote it. It is the same class of
error as `boss`: a noun that quietly imports a different genre. Not deployed — a
nine-record targeted fix is a separate, deliberate job.

### 3 · Forms (150) — the agent found a gap in my guide

The first creatures run flagged **all 25 Alpha names** as high-fantasy title cards and
wanted `Bonelord of the Shattered Crags` rewritten to `Gristle Knuckle`. Eleven of its 38
refinements changed only the name.

**It was right about the rule and wrong about the scope.** Alpha names follow a deliberate
convention my guide had never mentioned, because the guide made no distinction between a
flavour line and a name. That is the Assignment #4 lesson again: a finding that keeps
coming back is usually a bug report about your contract, not about the content. So C4
exists, measured from the corpus the same way C3 was.

Re-checking the ten worst-affected records with C4 in place:

- **All 8 Alpha names accepted at 9/10** — the false-positive class is gone.
- **Both `"a better trigger"` records still caught** — the true-positive class survived.

Removing noise without removing signal is the only outcome that shows a tuning change was
correct rather than merely quieter.

With C4 in place, the forms run then found something different: **96 of 124 refinements
were C1 tone**, and the pattern is anachronistic modern humour.

> *"Casts a shadow that files its own taxes."*
> *"Throws hands first, asks questions never."*
> *"Breaks the sound barrier and several local noise ordinances."*

Tax filings, internet idiom, municipal noise ordinances — in an ecosystem with no
municipalities. Against a brief asking for *primal, crude, comedic*, the agent reads these
as importing a modern frame, and it is a coherent, systematic reading across 150 lines.

**Not deployed, and not close.** 121 flavour rewrites is a wholesale replacement of the
game's largest text corpus on an agent's reading of one adjective. Whether that humour is
drift or charm is a designer's decision. The pattern is worth knowing; the fix is not the
agent's to make.

## Honest notes

- **The guide is stricter than the corpus that produced it.** 83% of forms and 63% of
  creatures fall below 9/10, including lines a human wrote and shipped. C4 removed one
  cause of that; the tone gap is the rest, and I have not established whether the guide is
  over-reading "comedic" or the content genuinely drifted. One corpus cannot settle it.
- **"Boss" is a defensible false positive.** A horn *boss* is a real anatomical term for
  the fused base, and the line may have meant it that way. In a game that calls its
  champions Alphas the word still reads as RPG furniture, so I kept the flag — but the
  agent cannot tell those senses apart, and I would not want it to decide that alone.
- **9/10 is the ceiling in practice.** Almost nothing scored 10 in any run, including
  human-written shipped lines. Either the Evaluator reserves 10, or the bar is set above
  the corpus.
- **Every demo cleared in one pass.** Three are available and the third has never been
  needed, so the escalation path is untested on this content.
- **Only 2 of 164 flagged records were deployed.** The gate writes a copy, never in place,
  and deployment is a separate human decision. An agent that scores content is useful; an
  agent that rewrites 121 lines of shipped text unsupervised is a liability.
- **Cost: $19.03 total** — $0.37 demos, $0.76 emblems, $4.34 creatures, $0.51 re-check,
  $13.05 forms. I had estimated $7–9 for the last two: wrong, because I priced evaluations
  and 83% of forms triggered a refine-and-rescore cycle on top.
