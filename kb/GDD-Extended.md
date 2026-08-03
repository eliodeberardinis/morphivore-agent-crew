# MORPHIVORE
### Game Design Document — Final

**Author:** Elio De Berardinis
**Course:** Agentic AI Game Development — Assignment #02
**Version:** 1.0 (Final) · 19 July 2026
**Supersedes:** v0.1 (Draft), submitted 19 July 2026 — preserved unedited as `gdd-first-draft.md`

> **How this version was produced.** The draft was put through a six-agent adversarial design
> review: six specialist reviewers in isolated contexts (systems designer, narrative critic,
> player psychologist, feasibility lead, adversarial QA, production/business analyst), then a
> cross-examination round where they argued with each other, then a moderated synthesis.
> The board returned **33 findings, 13 of them blocking, and 5 disagreements it could not settle.**
>
> **§5 — Revision Log** is the account of what changed, which finding drove each change, and —
> just as importantly — which recommendations were **declined** and why. Readers comparing
> against v0.1 should start there.

---

## 1. Executive Summary

**Morphivore** is a single-player, top-down 3D **action roguelite** where you play a small cube-beast that survives by eating other beasts — and becoming them. Everything you eat rewrites your body: the colour of the meat you swallow decides what kind of predator you turn into, and the traits you absorb decide where in the world you can physically survive.

A run is a push through procedurally generated biomes. Eating is everything: it is how you mutate, how you heal, and how you earn the traits you need to reach terrain that would otherwise kill you — fins to cross water, claws to climb, a coat to survive the cold. Each colour you turn into is a trade rather than an upgrade — a Yellow Brawler carries a long health bar and moves like a boulder, a Red Leaper is the fastest thing alive and dies to two mistakes — and the meat that *changes* you is not the meat that *heals* you, so a wounded predator has to stop hunting and go find food. Eat enough, and widely enough, and the biome's **Alpha** — the champion of whatever colour you preyed on most, **your equal in rank** — comes out of its lair to hunt you: a mirror-match for the territory, because it only has room for one apex. Beat it and you breed: you choose one offspring from a litter, it has a limb more than you did, and a bigger body means far more shapes you can become. Conquer all five territories, grow to six limbs, and — if your bloodline has explored enough of the world's forms — the **Apex** itself answers, the last thing above you. Die and you lose all of it; every run starts again as a one-limb cube.

The fantasy is *becoming the food chain*, not climbing it. You do not find a sword in a chest. You see a creature that can do something you cannot, and you eat it.

### The world: an eating ladder, all the way up

There is no kingdom to save here — but there is a world to explore in depth and breadth, to master, and eventually to rule. The world of Morphivore is **one ecosystem, five territories deep**, and its only law is the one the theme promises: eat what you can, avoid what you can't, and become the thing everything else avoids. The territories run from the soft margins, where weak Pale meat grazes in the open, to the heart of the wild, where the strongest creatures den and the meat runs Rage. The darkening under your feet (§2.4b, §2.7) is not a plot — it is ecology: **the strongest things hold the richest ground.** At the top of each territory sits an Alpha. At the top of all of them sits nothing, yet.

The fiction *is* the food chain — everything on screen is eating, fleeing, or deciding which — and the tone (§3, Content & Tone Agent) carries the rest. **You are the hungriest thing in the story**, and the whole of your motivation fits in one sentence: you are trying to sit on top.

*(This is also where Morphivore parts company with Cubivore, whose eating ladder is wrapped in a world-restoration plot — reclaim the wildness, re-green the land. Morphivore refuses the wrapper. You are not saving anything.)*

### What you are: a bloodline, not a creature

**A run is one bloodline, and you are the whole of it.** You begin as a single one-limb cube. When you beat an Alpha and breed, you do not level up — your creature produces a litter and **you continue as the offspring you choose.** The parent's story ends there; yours continues in the child, one limb larger. By the final biome you are steering the great-great-great-grandchild of the animal you started as, and everything that animal earned — its traits, its emblems, the panels bolted to its limbs — was **bred true and passed down** (§2.6a).

This is the premise the rest of the document rests on, so it is stated first:

- **Death is the line ending, not a character dying.** When Health hits zero the bloodline stops. That is why permadeath bites: you are not losing a body, you are losing five generations of inheritance in one mistake. A creature that dies childless takes everything with it.
- **Breeding is the only way rank grows**, because rank is generational. Eating changes what you *are*; only a generation changes how *big* you are.
- **The Bestiary is the one thing that outlives the line.** It is the fossil record — the accumulated evidence of every form any of your bloodlines has ever taken, across every run. Lines end; the record does not.

**And the record is the real goal.** A single run asks "can this bloodline reach the final Alpha?" The *game* asks something larger: **which combination of colour, intensity and rank produces a creature that can conquer this world?** There are many answers, and finding them means running the evolutionary tree — breeding one line down a Yellow-Rage path, losing it in the Mountains, starting again and taking the same body somewhere else entirely. The Bestiary is the map of that tree, and filling it in is the thing you are actually doing across a hundred runs.

| | |
|---|---|
| **Genre** | Top-down action roguelite — permadeath, procedural runs |
| **Inspiration** | *Cubivore: Survival of the Fittest* (GameCube, 2002) for mutation; *The Binding of Isaac* for run structure |
| **Platform** | PC (Unity 6, URP). Keyboard + mouse and gamepad |
| **Players** | Single-player |
| **Session length** | ~35–45 minutes per run (five biomes) |
| **You are** | A **bloodline**, not a creature. Each Alpha you beat produces a litter; you continue as the offspring you choose, one limb larger, inheriting everything the parent earned |
| **Rank** | Limbs (1 → 6). Gained only by breeding a new generation — never by eating |
| **Win / end states** | **Conquest** (per run): beat all five biome Alphas and breed to six limbs — you have ruled the five territories. **True ending:** in the rank-6 Ascension, beat the **Apex**, which wakes only once your Bestiary holds **≥100 of 150 forms across all runs** (§2.5). No single bloodline reaches the top the first time |
| **Loss condition** | Your **Health** reaches zero. **The line ends** — the run is over and the next begins with a new one-limb cube |
| **Persistence** | The **Bestiary** — the fossil record. Every distinct form any of your bloodlines has ever taken, across all runs, plus every emblem ever claimed. Lines end; the record does not |

---

## 2. Game Mechanics

### 2.1 What the player does, second to second

You steer with **WASD** or the **left stick**; your beast faces the direction it moves. Combat is a deliberate three-beat rhythm, not a mash:

1. **Lock on.** Hold **right-click** / **left trigger** to lock the nearest creature inside your facing cone. A red ring snaps over it and stays on it while you circle. Your lock range grows as you evolve — a scrawny forager must get close; a big evolved sniper can tag prey from across the clearing.
2. **Pounce.** **Left-click** / **A** to launch at the locked creature. There is no charge meter: the decision is *when* to leap, not how long to hold. A pounce on a standing creature drains its **Health** and **bounces you back off it** — bodies are solid, so you feel the impact.
3. **Knock down, then eat.** When a creature's Health hits zero it does not die. It collapses **dizzy** — squashed flat, spinning slowly, harmless. Pounce it *again* while it's down and you **eat** it: it is dragged into your mouth, shrinking and spinning, and absorbed. Leave it too long and it gets back up at half health.

**Space** / **right trigger** dashes; **Q** / **B** poops out your oldest colour (§2.4a). You cannot walk through creatures or obstacles — you bump, slide, and get shoved.

*(Full control map — keyboard-and-mouse and gamepad in parallel — is in §4.1. Both are first-class; the game reads whichever you touch.)*

### 2.2 Being hunted (the same rules apply to you)

Creatures of your size or larger hunt you exactly the way you hunt them. They lock on, wind up, and pounce.

- When something locks you, a **pulsing orange halo** appears over your beast. That is your warning.
- **Smaller attackers must stand still to wind up** — a readable, punishable telegraph.
- **Bigger attackers keep closing while locked** — far harder to escape.
- The attacker commits its pounce direction at the end of the wind-up, so **moving or pouncing away makes it whiff**. Run far enough and the lock breaks. Hit it during the wind-up and its attack is cancelled outright.
- Any creature you have damaged shows a floating health bar, so you always know what is nearly down.

Smaller creatures flee from you instead, panicking in zig-zags when you lock them.

### 2.3 Health — the bar you chose, and how you refill it

You have **one** meter: **Health**. At zero you die and the run ends permanently.

**How long the bar is, is a consequence of what you became.** Health isn't a counter that creeps up as you eat — it is a property of your current **form**. Limb count sets how much animal you are; **colour decides how that is spent**. A Yellow Brawler carries a long bar and moves like a boulder. A Red Leaper's bar is short and it dies to a couple of mistakes — that is the price of being the fastest thing in the biome. Mutating into a new form re-cuts the bar on the spot, and you can watch it happen — but **the re-cut preserves your wound, not your number**. You keep the same *fraction* of the new bar you had of the old: at 40% health, turning Yellow gives you a longer bar that is still 40% full. Mutation never heals a point and never costs one — the wound stays the same size on screen; only the animal around it changes. (The draft left this unstated, and it produced a visible lie: a wounded player mutating into Yellow watched their bar grow while being told hunting does not heal. The fraction rule closes it — the bar's *length* is what you became; its *fill* is only ever grazers.)

So the bar is not a reward for eating. It is how you *read* the trade you made (see §2.4).

**Grazers refill it.** Grazers are harmless herbivores scattered thinly across every biome. They carry **no colour**, never fight back, and bolt the instant you lock them. Chase one down, eat it, and you recover a real chunk of **current** Health.

**Grazers are limbless, and they are white** — the same white as a bare limb (§2.4a) and a newborn cube: the game's one universal negative: *nothing here to take*. A grazer carries nothing you can become — no colour, no family, just meat. That is the fictional reason the mechanical split works: eating one heals you but cannot change you, because there is nothing in it to take. The player reads them at a glance, from any distance: in a game where limbs hold colour and colour is identity, a creature with no limbs has nowhere to put a colour. It is visibly, instantly a non-participant in the food chain — which is exactly why eating one cannot change you. "A meal that means nothing" becomes a stated property of the world rather than an unexplained exception to the game's one universal rule. The alternative — giving grazers a "worthless" colour — was rejected precisely because colour is the grammar every other system is written in, and spending it on the word *except* would teach the player that colour doesn't reliably mean anything.

**Every class can catch one.** A form's **dash speed = its Speed stat × its family Dash multiplier** (§2.4), so the slowest dash in the game belongs to the 1-limb Yellow Brawler: 12 × 0.8 = **9.6**. Grazer flee speed is pinned in `creatures.json` **below that** — so even the slowest hunter, at full dash, runs one down. No form is ever locked out of healing. A Red Leaper runs a grazer down casually; a Yellow Brawler has to spend its dash and commit. Every class has a route, and the *cost* of that route is what prices the healing detour. Without this rule, a player could be mutated into a body that structurally cannot heal, in a permadeath game, by a system they did not fully steer.

**Hunting does not heal you.** Eating coloured prey drives mutation, Alpha progress and litter width — but it does nothing for your wounds. That split is the point: because the two things you eat serve different needs, **being hurt becomes a problem you have to go and solve** rather than a side effect the next kill quietly repairs. A wounded predator has to break off, find something that doesn't want to be caught, and spend time on it — while whatever mauled it is still out there.

**And the two meals look different going down.** Eating is the game's most repeated act, so the two things it can mean have two visual languages. Coloured prey streams its colour **into a limb** — you watch the unit arrive in the buffer, and the health bar does not move. A grazer dissolves **into the body** — the bar visibly refills, and no limb changes. The player's eye learns where each kind of meal goes on the first grazer they ever catch, without a word of tutorial — the only kind of teaching §4.9's start-cold commitment permits. (Two distinct absorb effects, owned by the Creature Art & VFX Agent, §3.)

The sharpest version of that decision shows up constantly: you've knocked down the red you need, you're two hits from dead, and a grazer is bolting the other way. The red gets back up in five seconds. Choose.

**Grazers do not count toward the Alpha's eat-count.** That gate counts **coloured prey only**, so healing can never be mistaken for progress and the gate can't be padded with easy food.

*(A hunger/starvation clock was considered and cut: eating already drives mutations, Alpha progress and litter width, so a punitive fourth incentive to eat would have been redundant and one more system to tune.)*

### 2.4 Mutation — you are what you eat

Every coloured creature belongs to one of **five families**, and every family is a **playstyle**. Colour does not make you stronger — it decides *what you are strong at*, and what you gave up for it. The multipliers below are each family's **full — Rage — expression**; lower intensities express a fraction of the same trade:

| Family | Class | Health | Speed | Damage | Reach | Dash | The trade |
|---|---|---|---|---|---|---|---|
| Yellow | **Brawler** | **1.5** | 0.85 | **1.5** | 0.9 | 0.8 | Longest bar, hardest hits — and the slowest thing in the biome |
| Red | **Leaper** | 0.8 | **1.3** | 0.7 | 1.0 | **1.6** | Fastest, best dash, weakest bite. Dies to two mistakes |
| Blue | **Sniper** | 0.9 | 1.0 | 1.0 | **1.7** | 1.0 | Locks and pounces from outside everyone else's reach — but fragile up close |
| Purple | **Stalker** | 0.9 | 1.15 | 0.95 | 1.2 | 1.2 | Quick and slippery, no standout strength. Hit-and-run |
| Grey | **Apex** | 1.3 | 1.2 | 1.3 | 1.15 | 1.3 | Strong at everything — and its meat runs rarest |

*(The draft had six colours. **White is no longer a family** — it is the game's empty state: a bare limb, a newborn, a grazer. **Green is cut**; its job — "the starting body, adequate at everything" — passes to the blank hatchling below. The apex family is **Grey**, as in the original Cubivore.)*

**Intensity scales the trade.** A form expresses a fraction of its family's distance from 1.0 on every axis: **Pale 25% · Dusk 50% · Deep 75% · Clash ~90% plus a minor second-tone gift · Rage 100%.** A Pale Brawler is recognisably Yellow; a Rage Brawler *is* Yellow, with everything that costs. (Clash's second-tone gift is specified per form in `forms.json` — a Clash Brawler whose second tone is Red keeps a sliver of the Leaper's dash.)

**And the blank is form zero.** The hatchling is a **white cube with one bare limb** — no family, multiplier 1.0 on every axis: adequate at everything, good at nothing, and not in the Bestiary's 150. Your first meal is your first identity.

Because **Health is one of those columns**, your bar length visibly announces the trade you took. Turning Yellow makes you tanky *and sluggish* in the same instant; turning Red makes you lethal to catch *and easy to kill*. There is no strictly-best colour, which is what makes being forced into one by what was available to eat interesting rather than annoying.

**How the numbers combine: limbs set the baseline, colour multiplies it.**

| Limbs | Health | Damage | Speed | Reach |
|---|---|---|---|---|
| 1 | 100 | 40 | 12 | 16 |
| 2 | 150 | 55 | 13 | 19 |
| 3 | 200 | 70 | 14 | 22 |
| 4 | 250 | 85 | 15 | 25 |
| 5 | 300 | 100 | 16 | 28 |
| 6 | 350 | 115 | 17 | 31 |

Health climbs steepest, so gaining a limb is felt first and most as **durability** — a bigger animal is a harder animal to kill. Speed climbs gently, so a six-limb beast is never sluggish, but never as quick as a small specialist either.

*Worked example.* From the same two-limb litter: a **Rage Leaper** ends up with 150 × 0.8 = **120 Health** and 13 × 1.3 = **16.9 speed**. A **Rage Brawler** gets 150 × 1.5 = **225 Health** but only 13 × 0.85 = **11.1 speed**. Same rank, nearly double the bar, about a third slower. A **Pale Brawler** at the same rank has taken only a quarter of that trade — 150 × 1.125 ≈ **169 Health**, 13 × 0.96 ≈ **12.5 speed** — Yellow, but not yet committed to it.

Rank dominates *within* a colour — a two-limb Yellow always out-tanks a one-limb Yellow — but **across** colours a specialised small beast can still beat a fragile big one on a single axis. That is deliberate. It keeps colour meaningful at every rank instead of letting progression erase it.

### 2.4a The colour buffer — the rule you execute every ten seconds

Your body has a fixed number of **limbs**, and **each limb holds one colour**. Together they are your **colour buffer**: the raw material of mutation, and the thing you are actually managing all run.

The buffer runs on three rules, and they are the whole of it:

1. **Eating fills a white limb first** — a bare limb takes the new colour before anything else is touched. If no limb is white, the meal **evicts your oldest colour**: the buffer is strictly **FIFO**, first in, first out. You are, literally, what you *recently* ate.
2. **Q / B poops.** Your creature squats, strains, and **poops its oldest colour out** — a small dropping left on the ground behind it — and the limb that held it turns **white**: bare, uncoloured, open. White is the game's one universal negative — an emptied limb, a newborn, a grazer — and it always means the same thing: *nothing here to take.*
3. **The two together are the steering tool.** Poop until the limb you want is bare, then hunt the colour you want into it. Steering costs time and meals — it is never free — but it is never hidden either.

**The next slot to be overwritten is always highlighted on your own body** — the limb pulses before you eat, so you can never lose a colour you didn't know you were spending. The mechanism is fully transparent. What is *not* under your control is the menu: §2.7's per-run palette roll decides what is actually alive near you, so your three-meal plan collides with what the biome will give you. **The forcing comes from the world, not from hidden rules** — which is what makes "the story of what you were forced to become" a story rather than noise.

### 2.4b Forms — the 150, and the meat that makes them

Here is the distinction the design turns on, because it is the one thing most easily confused:

- Your **buffer state** is which colour units sit in which limbs right now. It is combinatorial, volatile, and changes with every meal.
- A **form** is a named, statted, silhouetted creature in the Bestiary. There are exactly **150** of these, and every one is hand-authored.

**Meat carries intensity.** A creature is not just a colour — it is a **tier** of that colour, and its meat carries the tier into your limb:

| Tier | Where it lives | Expresses |
|---|---|---|
| **Pale** | Wanders everywhere, every biome — the common meat of the world | 25% of the family trade |
| **Dusk** | Debuts in Prairies **pockets**; wanders freely from the Wetlands on | 50% |
| **Deep** | Debuts in Wetlands **pockets**; wanders from the Mountains on | 75% |
| **Clash** | **Elites, trait minibosses and Alphas only** — two-toned meat, never wandering | ~90%, plus a minor second-tone gift |
| **Rage** | Debuts in Mountains **pockets**; wanders the deep ends of Beach and Volcanic | 100% — the pure expression |

**What you raid today wanders tomorrow.** Each tier debuts guarded, one biome before it roams free — so the world darkens under you as you go, exactly as the original Cubivore's meat darkens by stage.

**A form is a family × an intensity × your rank: 5 × 5 × 6 = 150. Exactly.** Every rank holds the full 25-form ladder — no truncated rows, no special cases. That count satisfies all three legs of the review board's trilemma at once: small enough to author, large enough to gate, regular enough to read as a grid.

**Every buffer state resolves to exactly one form.** No recipes to memorise, no invalid states:

- **Family** = the colour holding the most limbs. Ties break toward the **most recently eaten** — except at birth, where there is no eating history: a **newborn** breaks ties by a fixed family precedence (Yellow → Red → Blue → Purple → Grey), so every litter-mate the screen shows you already resolves to a definite form. (A born-Blue/Grey/Purple triple, for instance, reads as its Blue form until your first meal shifts the count.)
- **Intensity** = the **lowest tier among your family-colour units**, stepped down one rung for every limb *not* carrying the family (off-colour or white), floored at Pale.
- **The dilution ladder is the four wild tiers** — Pale, Dusk, Deep, Rage. **Clash sits beside Rage, not below it**: a parallel summit, reached only by holding Clash units, never by mixing wild meat. Diluted, both summits slide to **Deep** — two peaks, one slope down. (Without this rule, "one rung down from Rage" would land on a mixture tier that mixing is not allowed to produce.) A buffer whose family units mix Clash *and* Rage resolves to **Clash** — holding any Clash unit puts you on the Clash summit; it is the rarer, elite-only tier, so it wins the tie.
- **All limbs white** = the blank (form zero).

You mutate the instant the resolution changes. The rule is one sentence long and it teaches the whole endgame by itself: **your weakest meat sets your intensity**, so climbing to Rage means pooping out every weak unit and replacing it with strong ones — full-body commitment, earned meal by meal. *Worked micro-example:* rank 3 holding Rage Yellow / Rage Yellow / Dusk Red → Yellow dominates, stepped down once by the Red limb → a **Deep Brawler**. Poop the Red (limb goes white — still stepped down: Deep), hunt one more Rage Yellow into it → **Rage Brawler**.

**Why six limbs: the body is a cube.** The creature is built from a central cube with **six faces to grow from**, and a form is assembled by attaching and combining limb-segments across those faces — up to six — into an authored body plan. Rank caps at six because that is the room a cube gives you. *How* a form arranges its segments is part of its authored identity — several can chain together into a low sprawling brawler, spring back into a coiled leaper, or stretch long into a sniper — so silhouette reads family, segment count reads rank, and colour saturation reads tier: **150 distinguishable bodies from one procedural system**, no hand-modelling. The exact attach-and-combine rules are the Creature Art & VFX Agent's to author (§3); the design fixes only the count and the read. (Traits render on the cube's own surface, §2.6a, and are never crowded out by the limbs.)

**The tier ceiling is typical, not absolute.** The per-run roll (§2.7) can spawn an **over-tier pocket** — a Rage hollow in the Prairies, rare and viciously guarded. That is both a jackpot for the line that finds it and the reason every rung of every rank's ladder is reachable across enough runs.

**Why intensity exists at all.** Without it, a form would be nothing but "rank + colour" — and rank only ever goes up, so becoming would collapse into climbing with a paint job. Intensity is **orthogonal to rank**: a 2-limb Rage Brawler and a 5-limb Pale Brawler are both Yellow, both legitimate, and play nothing alike. That is the axis on which the game's central fantasy actually lives.

**Every distinct form you reach is logged in the Bestiary** — and forms are what summon Alphas and widen litters, so "eat widely" and "make progress" are the same instruction.

### 2.5 Rank — the Alpha challenge and breeding

Eating changes *what* you are. It never changes *how big* you are. Limbs — the game's real measure of rank — are earned by beating an Alpha and breeding.

You begin every run as a **blank white one-limb cube** — form zero: no family, no entry in the record, nothing yet. Your first meal is your first identity.

**The lair.** Every biome contains one **Alpha lair** — a landmark you can see from the moment you arrive: scorched ground, scattered bones, a den. It sits empty and quiet. You know from the first minute that something lives there, and roughly where.

**The two gates.** The Alpha only stirs once you have been both *varied* and *busy* in that biome:

| Biome | Player rank there | Reachable forms there | Distinct forms required | Slack | Coloured prey eaten |
|---|---|---|---|---|---|
| Prairies | 1 limb | 15 *(Pale, Dusk + Clash elites)* | 3 | 5.0× | 15 |
| Wetlands | 2 limbs | 20 *(+ Deep)* | 5 | 4.0× | 20 |
| Mountains | 3 limbs | 25 *(+ Rage — the full ladder)* | 7 | 3.6× | 25 |
| Beach | 4 limbs | 25 | 9 | 2.8× | 30 |
| Volcanic | 5 limbs | 25 | 11 | 2.3× | 35 |
| *— then —* | | | | | |
| **The Ascension** | **6 limbs** | 25 *(the rank-6 row)* | *the Apex is record-gated* | — | *see below* |

The five rows are the five **biomes**, where you play at ranks 1–5. **Rank six is not a biome** — it is the finale: beat the Volcanic Alpha, breed to six limbs, and enter the **Ascension** to play the six-limb creature; the Apex itself wakes once your record runs deep enough. That is why the table stops at five limbs; the sixth is on the other side of the last biome (full detail under *The Ascension*, below).

**Slack** is simply *reachable forms ÷ forms required* — how much bigger the pool is than the gate. A slack of 5.0× means the gate asks for one-fifth of what's available (easy, tutorial-safe); 2.3× means it asks for close to half (a real filter). The band tightens biome by biome on purpose. It exists to prove on paper that no gate is ever impossible (slack must stay well above 1.0×) or trivially incidental (it must stay well above the eat-count's own coverage).

Both gates must be met. Forms alone would let a careful player summon the Alpha after three surgical meals; a raw eat-count alone would just be a grind timer. Together they mean: *hunt a range of things, and hunt a lot of them.*

**Every gate sits between 2.3× and 5.0× inside the pool reachable in its biome, tightening monotonically** — loosest in the tutorial biome, tightest at the end; always reachable, never reachable by accident. Those figures are the **full-palette typical**; because the per-run roll need not field all five families (§2.7), the `min_distinct_colours` generator invariant (§3.3) is set to keep the worst-case roll's slack from ever dropping below **~1.5×**, so the gate is safe on paper in every legal world, not just the average one. The reachable pool is set by the biome's meat-tier ceiling (§2.4b, §2.7): no gate can drift into being impossible (as the draft's Volcanic gate did, demanding 7 forms from a pool of 6) or into being satisfied incidentally by the eat-count gate.

At one limb the gate is trivially readable — "3 distinct forms" means **eat three different colours**. As ranks and tiers grow, the *same* rule gets deeper on its own: the same three colours now come Pale, Dusk or Clash, and steering the buffer (§2.4a) becomes how you reach them. The player is never taught a second rule.

**The ten numbers in this table are the QA & Balance Agent's explicit tuning targets, measured against the 35–45 minute run** (§1, §4.10) — the single run-length figure used everywhere in this document.

**The eleventh number — the record gate on the Apex.** Conquering the five territories and breeding to six limbs wins the *run* and opens the Ascension (§2.5, below) — but it does not, by itself, end the game. What ≥100/150 forms gates is not the domain but the **Apex fight**: the final boss stays **dormant** in the Ascension domain until your Bestiary, counted across every run, crosses 100 of 150. This is *Cubivore*'s own final gate (≥100 mutations of 150 to face the Killer Cubivore), and it makes §1's meta-goal mechanical: a run asks whether this line can *Conquer*; the record asks whether your bloodlines have explored enough to be allowed to *rule*. Two consequences, both deliberate:

- **No first line rules the world.** At ~three meals per new form, 100 is more than double a single run's 125 coloured kills — so the Apex is not "play one run perfectly," it is *the top is earned across a lineage.* Ranks 1–5 hold 125 forms, so ≥100 is reachable well before the top row, and the Apex can wake **mid-ascension** the instant you cross it.
- **A line short of the record still Conquers — and still ascends.** It wins its five territories, plays the rank-6 domain, hunts the top row, and banks every form it finds for the next line. The count sits on the Bestiary header and run-start screen from minute one; the Apex is never a surprise wall.

**The target is a 35–45 minute run.** The five eat-counts (125 coloured kills across the run) and the five form gates are tuned toward that target — corrected down from the draft's 200-kill floor, which fit neither the old nor the new run-length figure. We do **not** budget the run second by second here: the exact pacing is a **tuning problem, settled against the run event log** (§4.10), not something the design pins to an accounting of every action. The number to hit is the run length; the levers are the ten gate numbers; the instrument is the log.

**The one pacing invariant the design does fix is the pounce count**, because it is a *feel* guarantee, not a stopwatch one. The review showed the draft's difficulty curve pointed backwards: base health climbs +50 per rank against damage's +15, so if prey scaled flatly with the player, kills would get *slower* as the run went on. The intensity system is the counterweight:

| Biome | You (typical) | Wandering prey (typical mix) | Pounces to knock down |
|---|---|---|---|
| Prairies | rank 1, Pale | rank 1, Pale | **3** |
| Wetlands | rank 2, Dusk | rank 1, Pale–Dusk | **2–3** |
| Mountains | rank 3, Deep | rank 2, Dusk | **2–3** |
| Beach | rank 4, Rage | rank 3, Dusk–Deep | **2–3** |
| Volcanic | rank 5, Rage | rank 4, Deep–Rage | **2–3** |

Your tier climbs one step ahead of the ambient mix (you raid pockets; the wanderers don't), and intensity multiplies your damage faster than it bulks most prey. Worked end-point under the stat model (§2.4): a rank-5 Rage Brawler hits for 100 × 1.5 = 150; a rank-4 Deep Red wanderer carries 250 × (1 + 0.75×(0.8−1)) = **212.5 Health** (two pounces), a rank-4 Deep Yellow 250 × 1.375 = **343.75** (three).

**The 2–3 band is a target-selection guarantee, not a universal one — and the difference is the skill.** It holds *whenever you pick an appropriate meal*: any hunter drops soft and mid families (Red, Blue, Purple prey) in 2–3, and the tank families (Yellow, Grey) drop in 2–3 *for a damage-forward hunter* (Yellow, Grey, Blue). What breaks the band is a **low-damage hunter attacking a tank** — a Rage Leaper (0.7 damage) against a Deep Yellow is a 4–5 pounce slog, by the same arithmetic. That is not a bug; it is the game saying *pick a different animal.* A fragile fast build is not supposed to trade blows with the tankiest thing in the biome — it is supposed to run down the soft, fast prey it out-classes. So the honest statement, which the event log checks per family: **2–3 pounces against the prey each family is built to hunt; more if you pick a fight your form is wrong for.** Two guarantees still fall out universally: no one-shot threshold is ever crossed (your damage < every prey bar at every rank, so the knockdown-then-eat beat survives to the last biome), and what *escalates* across the run is the chase, not the sponge (§2.7).

**And the counter now has a reason.** The two gates are not abstractions — together they are **the profile of a rising predator**: distinct forms is how many shapes you have hunted in, prey eaten is how much of the territory's chain you have eaten through. An apex does not stir for a scavenger picking at the margins. **It comes when a rival has grown into its equal — because a territory has room for exactly one apex, and you have just become the other one.** The mechanical trigger and the creature's motive are the same fact, which is what the draft's counter-wakes-a-predator design was missing.

**Who comes for you.** You don't choose. The Alpha that answers is the **champion of the colour you ate most** in that biome: prey on reds all through the Wetlands and the Red Alpha is what comes for you. It stands at **your own rank — a true mirror-match** — but it always fights at **Clash** intensity, the two-toned elite tier no wandering meat carries (§2.4b), so it hits harder and reads differently than anything you have hunted to get here. You beat your equal, and *then* the emblem lets you breed up: the rank you gain is the reward for the win, not a handicap you fought under. (The draft made every Alpha one limb bigger than the player, which inflated its stats, forced a special anti-kite speed rule, and created a first-biome one-shot edge; a same-rank Clash Alpha is tough on intensity, not on size, and none of those problems arise.)

**You cannot outrun it.** An Alpha's speed does **not** inherit its colour's multiplier — every Alpha moves at a flat rate slightly above the fastest player form at that rank. Without this, a fast-colour player facing a slow-colour Alpha could jog away from the encounter indefinitely. Running buys you distance and time. It never buys you escape.

**The warning.** At **90% of both gates** the lair begins to visibly stir — the den lights, the ground trembles, an audio cue rises. The last meal before the threshold is therefore a *felt* decision rather than an ambush. When both gates fall there is a short **grace period** while the Alpha emerges, and only then does it begin hunting.

**It comes to you.** The lair erupts and the Alpha **hunts you across the biome**. You are not summoned to a boss room — you are found.

**What happens to everything else — and this is the clock.** When the Alpha wakes, the biome empties: prey and grazers alike **bolt for the edges and are gone**, scattering away from the apex exactly as living things flee a predator. The healing supply leaves with them. This is why the **warning matters** (above): the lair stirs at 90% of both gates, so you always get to choose your last few meals *before* you commit — top up your Health, set your buffer, then trip the gate on your terms. You are never ambushed into the fight at low Health; you walk into it having decided to.

Once the hunt is on, **there is no topping up.** A stray grazer may still be caught at the fringes, but the field you fed on all biome is gone, and it does not come back while the Alpha lives. **That is the price on delay** — the longer you circle, the emptier the ground and the thinner your margin — and it is diegetic rather than a tuning knob: a world under an apex goes quiet. You can still keep eating what coloured prey remains to widen your litter, but you do it on a dwindling table.

This is what makes "push your luck or go and meet it" a real decision in every biome: prepare and commit, or scavenge the emptying ground for one more form and risk fighting hungry.

**The emblem.** Knock the Alpha down, eat it, and you take its **emblem**, which does two jobs:

1. it **opens the way** into the next biome, and
2. it **enables breeding**.

The emblem is a **trophy taken off the body of a defeated rival** — it grants no power of its own. Powers come from decorated panels (§2.8), which is where the run's build layer lives. This matters thematically: an emblem that opened a door *and* granted a permanent ability was a boss key by another name, in a game whose opening line refuses to put a sword in a chest. As a trophy that triggers breeding, it is also the only fictionally coherent reason swallowing a rival's remains would cause your creature to reproduce — you are taking the rival's reproductive material, not collecting a magic key.

**Breeding — the generation step.** Holding the emblem, your creature mates, and you are shown a **litter** of possible offspring, each with **one more limb than its parent**. You pick one and **continue as it**; the parent's part in the story is over.

Everything the parent earned is **bred true**: traits, emblems and panels all pass down intact (§2.6a). This is heredity as the bloodline's whole point — a generation is not a reset, it is the accumulated inheritance of every ancestor in the run, one limb larger each time. It is also why losing the line hurts: five generations of inheritance end with it.

The litter's size is set by **how many distinct forms you reached this biome, beyond that biome's gate minimum**:

> litter size = 2 + (distinct forms this biome − the biome's form gate), capped at 5

So clearing the gate exactly gets you two offspring; **three forms past it caps the litter at five.** This is a single, stated definition — the draft defined the litter counter three different ways across §2.5, §2.9 and §2.10 (twice as "mutations achieved," once as "forms"), which meant the reward could be farmed by oscillating two colours without ever satisfying the gate. Tying it to distinct forms *above the gate* also fixes the redundancy: the gate no longer pins the reward high, because the reward only starts counting where the gate stops.

**What actually differs between offspring: the limbs.** Every offspring in the litter has the same rank — one more limb than you — and every one inherits all your traits, emblems and panels (§2.6a). What varies is **which colours their limbs are born loaded with.**

That is a real decision, and it is the only one on the screen. Because every buffer state resolves to a form (§2.4b), your starting buffer decides which forms you are *near* — and newborn meat is always **Pale**, because a body has to eat its way to intensity:

> *This one is born Pale Yellow / Pale Yellow / Pale Red — a Pale Brawler from its first breath, two strong meals from Dusk. That one is born Pale Blue / Pale Grey / Pale Purple — nothing in particular yet, and able to become anything. The third is born all Pale Red — a committed little Leaper that will have to poop its way out of the family if you regret it.*

So the litter screen asks: **do you want to be born committed, or born flexible?** A monochrome litter-mate hands you an intensity immediately and costs you manoeuvring room; a mixed one is nothing in particular but can become anything. The choice is legible against the recipe table the player already knows, and it is made once per biome, at the moment the run's next chapter starts.

In the draft this screen was a menu of near-identical options — the run's single largest progression beat, delivered as a cosmetic choice. It now decides the shape of the biome you are about to play.

- **You do not choose a mate.** The litter is a product of what you became, not who you found.
- **You pick one offspring and continue as it — that form is yours for free.**
- **The ones you didn't pick are not wasted.** They are revealed in the Bestiary as known forms at your new rank: shapes you now know exist and can eat your way into later in the run.
- Limbs cap at **six**.

Every rank holds the same 25-form ladder (§2.4b), so gaining a limb does not widen the *pool* — it opens a **new** column of 25 forms to discover, deepens every buffer (more limbs means finer control over which tier and family you resolve to), and raises the ceiling of what you can become. What it does *not* do is make wide litters easier: because the form gate climbs (3→5→7→9→11) against a flat 25-form pool, the headroom that feeds litter width actually tightens with rank — a deliberate late-game squeeze, not a contradiction.

This is the run's long arc: **eat widely → mutate often → grow into the Alpha's equal and beat it → take its emblem → breed a limb larger → open a new rank of forms to eat your way through → and, once the record is deep enough, ascend to the Apex.**

### The Ascension — where rank six is played

Beating the Volcanic Alpha and breeding to **six limbs** is a **Conquest** — the run's win, all five territories ruled — and it opens the **Ascension**: the six-limb creature is playable at last, in the Apex's domain, a final stretch of the world where the 25 top-row forms (which exist *only* here) can be eaten into. **This domain is always open to a six-limb bloodline** — it is where you go to hunt the rarest forms in the game and drive your record higher. There is always something to *do* at the summit.

- **The Apex** is the world's ultimate: a **rank-6 Clash** creature, your final mirror, one rank above every biome Alpha because there was nothing above them to draw from. It sits **dormant** in the Ascension domain — like the biome lairs before it — and **wakes only when your Bestiary crosses ≥100 of 150 forms** across all runs. That can happen *mid-hunt*, the instant you eat your hundredth form and it stirs. **Beating it is the game won** — the true ending, above the run-level Conquest.
- **A line short of the record still Conquers, and still ascends.** It plays the rank-6 domain, hunts the top row until it dies or you choose to stop, and banks every rank-6 form it finds for the next line. No dead end at rank six: you either wake the Apex or you leave the world a deeper record than you found it.
- **Rank six is real content, not a victory screen.** All 25 top forms are obtainable on any ascension, which makes 150 an honest denominator (§2.9a).

*(This restructures the draft, in which the fifth Alpha granted a sixth limb and ended the run — leaving rank six, 25 authored forms, permanently unplayable. Decoupling the domain from the record and gating only the Apex fight is where the numbers close: 150 authored, 150 reachable.)*

### 2.6 Traits and terrain gates

Four creatures in the world carry a **trait** in their meat, and eating them is the only way to get it. Each is a **miniboss** — a territorial elite holding a defended pocket, several times tougher than ordinary prey, which fights back with the full lock → wind-up → pounce cycle and does not flee:

| Trait | Carrier | Grants | Renders as |
|---|---|---|---|
| **Fins** | The pond-dweller, in deep marsh hollows | Enter water without drowning | Gill slits cut into the main face |
| **Claws** | The crag-holder, on rocky outcrops | Climb high ground | Hooked ridges along the face edge |
| **Coat** | The shaggy grazer-hunter, in the Mountains **foothills** | Survive freezing peaks | A matted shell over the face |
| **Heat** | The vent-dweller, at volcanic seams | Cross lava fields | A scorched, glowing seam across the face |

Taking a trait is a set-piece fight, not a pickup — usually one you start while the pocket's other occupants converge on you. Four traits means four such fights per run.

Traits are the game's keys, and they are always visible as terrain you can *see* but not yet enter. You are never told to find an item; you are shown a pond, and you go looking for something that swims.

### 2.6a Where traits live, and what survives what

**Traits are body, not limbs.** A trait renders on your creature's **main cubic face** — the head-and-torso block that everything else attaches to. Fins are gill slits cut into the face; Claws are hooked ridges; Coat is a matted shell; Heat is a scorched, glowing seam. They are permanent parts of the animal, and **you can read a creature's traversal ability off its body at a glance** — yours and everyone else's.

This is the load-bearing decision, and it resolves the collision the draft created. Limbs hold colour and drive mutation; the main face holds traits and drives traversal. **The two systems never compete for the same real estate.** If traits had occupied limb slots, a Volcanic beast would have spent four of its five slots on traversal keys, leaving one slot to generate the eleven distinct forms that biome's gate demands — which is impossible.

**Once acquired, a trait is fixed.** Nothing in the run removes it. Not mutation, not breeding, not death of the parent body. So the four questions the draft left open have one answer each:

| | **On mutation** (buffer matches a new recipe) | **On breeding** (you continue as an offspring) |
|---|---|---|
| **Limb colours** | Rewritten — this *is* the mutation | Set to the offspring's own starting buffer (§2.5) |
| **Traits** | **Survive** — they are on the face, not the limbs | **Inherited in full.** Every offspring carries every trait you hold |
| **Emblems** | Survive | Carry forward |
| **Decorated panels** | Survive | Carry forward |

The silent soft-lock the draft produced — earn Fins in the Wetlands, beat the Alpha, breed, and walk into a Beach that needs Fins you no longer have — **cannot occur.** There is no path through the rules that separates a creature from a trait it earned.

**So where is the tension, if a trait can never be lost?** In taking it in the first place, and in losing all of them at once.

**Trait carriers are minibosses.** The creature whose meat carries Fins is not an ordinary pond-dweller — it is a **territorial elite**, substantially tougher than anything else in the biome, holding its range in a defended pocket (§2.7). It has a real health pool, it fights back with the full lock → wind-up → pounce cycle, and it does not flee. Taking a trait means committing to a fight you can lose, usually while its neighbours converge on you. The four traits are therefore four set-piece encounters per run, not four pickups.

**And permadeath re-prices them every run.** You hold all four for the length of a run and lose all four the moment you die. The traversal layer is not a one-time checklist that goes inert once ticked — it is a **per-run checklist in a game whose runs are 35–45 minutes**, and every new run starts you back at a shoreline you cannot cross. That is where the ongoing tension lives, and it costs no extra rules.

**Trait reachability is a generator invariant, not a QA problem** (§3.3): the world generator must guarantee that every gate in a biome has a reachable carrier, and that any trait a later biome requires is obtainable. A seeded generator reproduces an unwinnable run for debugging; it does not prevent one.

**Implementation note.** Because `Creature.BuildVisuals()` regenerates the body from primitives on every mutation (§4.3), trait geometry on the main face must be **re-applied after each rebuild** rather than attached once. Trait state lives on the creature, not on the mesh.

### 2.7 Biomes — escalating traversal complexity

Each biome is procedurally generated and holds one **Alpha lair**. The five run from the ecosystem's soft margins to its heart (§1): the strongest things hold the richest ground, which is why the meat darkens as you go.

1. **Prairies** — open grassland, **no gates**. Every area is reachable from the start. This is where the player learns to lock, pounce, knock down and eat.
2. **Wetlands** — broken up by ponds and channels. Requires **Fins** to reach roughly half the map.
3. **Mountains** — requires **Claws** to climb the peaks *and* a **Coat** to survive the cold at altitude. The first biome that demands two traits at once.
4. **Beach** — tidal flats, sea channels and cliffs. Combines **Fins** and **Claws**, and introduces the last new trait, **Heat**, at the volcanic vents along the shore.
5. **Volcanic** — the final biome. Lava fields, sheer rock and flooded caves demand **Fins**, **Claws**, **Coat** and **Heat** together. Nothing new is taught here; everything you have learned is required at once.

The design rule, stated accurately: **each biome introduces one new trait, except Mountains, which introduces two at once and is deliberately the difficulty step-up of the run.** The count is 0 → 1 → 2 → 1 → 0: Prairies teaches with no locks at all, Mountains is the spike, and the last two biomes stop introducing traits and start **combining** them. (The draft claimed a smooth "one more lock each time" ramp that its own table contradicted. The table was right and the sentence was wrong; Mountains is a better game for being the spike, so the sentence is corrected rather than the table.)

**Coat is not behind the cold.** Coat-carrying creatures live in the Mountains **foothills**, below the altitude where cold becomes lethal — so the trait that survives the peaks is always obtainable without first surviving the peaks. Circular gates of this kind are a generator invariant (§3.3), not a thing left to level design.

Five biomes means five Alphas, which is what carries you from one limb to the full **six**.

**Common food everywhere, strength out in the perils — and the land darkens as you go.** Ordinary creatures wander the whole biome at random, so you can always find something to hunt — you are never stranded, and the eat-count ticks along wherever you happen to be. But the wandering mix is not uniform, on two axes:

- **Across biomes**, each tier debuts in defended pockets one biome before it wanders free (§2.4b): the Dusk you raided a marsh hollow for in the Prairies roams openly in the Wetlands, while Deep now hides in the hollows. Every biome's ambient meat is a step darker than the last.
- **Within a biome**, the mix shifts upward with distance from where you entered. The land near the entrance grazes soft and Pale; the deep end runs strong — and **the Alpha lair sits at the strong end**, so walking toward the thing that will eventually hunt you is also walking toward the meat you need. Later parts of the same biome are simply more dangerous ground.

The top tier of each biome still clusters in **defended pockets** — a marsh hollow thick with Dusk, a rocky outcrop where Deep reds den, a treeline thicket hiding Rage. **Clash meat never wanders at all**: it is carried only by elites, trait minibosses and Alphas, two-toned on the bone.

**Stronger meat runs harder, it does not just sit tanky.** Because intensity scales a family's *trade* rather than inflating every stat, a Rage Red wanderer is far faster and bitier than a Pale one — and slightly squishier. Only the tank families (Yellow, Grey) get meaningfully more durable with tier. So the world's escalation arrives as **harder chases and more dangerous mistakes**, not as damage sponges — and the deep-end wanderers of the last biomes, expressing real speed and real teeth, are what keeps being-hunted alive to the end of the run.

**And those pockets bite back.** A strong-meat pocket is never just further away — it is defended. Expect **packs that aggro together and swarm you**, a **territorial elite** holding its range, or terrain that demands a trait you haven't earned yet. Taking the Deep purple you need usually means surviving being surrounded, and knowing when to cut and run on low Health.

So exploration is a gamble rather than a shopping trip: eat commons to stay fed and keep the count moving, then push out into a defended pocket for the colour you actually need, survive the horde, and come back a different animal. This is also what turns the Alpha's form gate into an **exploration** gate — you cannot reach four distinct forms standing in one safe clearing, because the safe clearing only grows common meat.

And because **the colour you eat most decides which Alpha comes for you**, committing to an emblem means committing to repeatedly raiding the pockets where that family's strong meat lives.

**Variety across runs.** Layout is procedurally generated, but the bigger lever is that **each biome's creature palette is rolled per run**. One run the Prairies are thick with reds and yellows; the next they're mostly blues and purples. The roll can also spawn an **over-tier pocket** — a Rage hollow in the Prairies, rare and viciously guarded — a jackpot for this line, and the reason every rung of every rank's ladder is reachable across enough runs. That single roll cascades through the whole run: it changes which forms you can reach early, which colour you end up eating most, therefore **which Alpha comes for you**, therefore which emblem and power you carry into the next biome. The first biome is deliberately the most variable, so no two runs open the same way.

### 2.8 Decorated panels — the run's build layer

Elite creatures drop **decorated meat panels** that visibly attach to your body — you can see how much you've eaten by looking at yourself. Each grants a power: a longer lock range, a stronger dash, a tougher guard, brief camouflage. **Panels are the run's only power source** (the emblem is a trophy and a breeding trigger, §2.5), and they make two players' beasts look and play differently by the end of a run.

The draft left panels as an orphan — no owner, no data file, no slot rule, no persistence rule, and no mention in its own summary of the loop. They are promoted here rather than cut, because they are **the only reward in the design operating on a short interval.** Emblems and limbs both arrive roughly once per eight minutes, behind the hardest fight in the biome. Panels arrive frequently, ungated, from ordinary elite kills — and in a game with no inventory screen, a panel bolting visibly onto your body is how a player reads their own progress at all. Cutting them would have left a 40-minute permadeath run with no fine-grained feedback loop whatsoever.

Now specified:

| | |
|---|---|
| **Capacity** | **Grows with the body — not a fixed cap.** A bigger creature has more room to bolt panels onto: capacity rises as you breed up through the biomes, so a one-limb hatchling carries few and a six-limb ascended creature carries many. You are never arbitrarily blocked from the powers you need to push through an area; you earn the room for them by growing into it |
| **Where they attach** | **Anywhere across the cube's faces**, wherever the authored body plan leaves room (§2.4b) — never crowding the main-face traits (§2.6a), which always keep their place |
| **Choosing** | When you're at capacity and take another, you pick which to shed, both powers shown — a real build decision, not a hard wall |
| **Stacking** | Two panels granting the same power **do not stack**; the game refuses the pickup and says why |
| **Persistence** | Survive mutation; carry forward through breeding (§2.6a) |
| **Data** | `panels.json` — power, magnitude, which elites drop it, attach rules |
| **Owner** | Gameplay Engineer (power logic + capacity curve) + Creature Art & VFX Agent (attachment visuals) |
| **Source** | Elite creatures only. Never grazers, never ordinary prey, never the four trait minibosses |

**The body reads as two registers.** Traits sit on the main cubic face and say what you *are* — where you can go, permanently. Panels bolt across the rest of the body and say what you're *carrying* — what you can do right now, this run, until you swap it. A player can read both off a silhouette without opening a menu, which is the whole reason the game has no inventory screen. And because panel room grows with the creature, an ascended six-limb beast is visibly *studded* with earned powers — the silhouette itself is the record of how far this line has come.

### 2.9 The Bestiary

The Bestiary is where the meta lives, and it is a single screen: **a grid of every beast that exists.**

**Rows are limb count (1–6). Columns are family (5).** That is 30 cells — but a cell is not one form, it is a **family at a rank**, and it opens into that family's **intensity ladder** (Pale → Dusk → Deep → Clash → Rage). So the grid is 30 cells over **150 forms**, three axes rendered as two.

This nesting is what makes the screen work at both scales. At a glance the top level does the design's job for free, exactly as intended: an empty *column* is a colour you keep failing to hunt, an empty *bottom half* means you have never bred past three limbs. Open a cell and there is real depth underneath — the Rage form of a family you have only ever dabbled in is a specific, nameable thing you have not yet become.

Forms you have eaten your way into show in full colour with their name; forms you have never reached show as a **dark silhouette** — so the player can see the shape of what they haven't become yet, and roughly what it would take. A cell whose ladder is partially filled shows as partially filled at the top level.

**It also records emblems.** Every emblem any of your bloodlines has ever taken off an Alpha is kept here permanently, as a trophy shelf beside the form grid. A line that died in the Mountains still leaves behind the two emblems it won — which is the clearest statement of what the Bestiary is for: **the line ends, the record does not.**

### 2.9a The record's milestones — what discovery unlocks

The record is a number the player watches from run one, and it pays out on a stated ladder. Every unlock is deliberately **data-cheap** — a start-state change, a constant, a skin — so the ladder costs the schedule nothing:

| Forms discovered | Unlock |
|---|---|
| **5** | **Hatch-choice** — begin a run as any *discovered* Pale form instead of the blank cube |
| **15** | **Inherited instinct** — begin each run already holding one trait you have earned before |
| **35** | Hatch-choice extends to **Dusk** forms |
| **60** | **Litter floor +1** — no litter of yours is ever smaller than three again |
| **100** | **The Apex wakes** — the dormant final boss (§2.5) will now answer any bloodline that ascends. The game becomes winnable |
| **135** | **Ancient skin** — a completionist cosmetic (§4.9). It needs nearly all of ranks 1–5 *and* ten of the 25 rank-six forms, so only a bloodline that has ascended many times approaches it. Meant to be monstrous |
| **150** | **The Whole Beast** — every form of every family, intensity and rank discovered. The Bestiary is complete; unlocks the **Genesis skin** — the newborn cube's white, now worn as mastery rather than emptiness — and marks the save 100% |

The first rung sits at **5 forms — inside what a losing first run banks before ever meeting an Alpha** (the Prairies pool alone holds 15): *you lost, and you are permanently further along, from the very first death.* The **150 denominator is honest** — ranks 1–5 supply 125 forms and any ascension makes the 25 rank-six forms obtainable — so every cell is reachable. All seven thresholds are QA tuning targets, tuned off the run event log (§4.10).

- **Opened from the pause menu** during a run (Esc / Start → *Bestiary*), and from the **main menu**, because discovery is permanent and survives death.
- The header shows **total discovered / total possible** and the next milestone unlock.
- During a run, forms discovered **this run** are highlighted, along with progress toward the current biome's **Alpha threshold** — so the player always knows how close they are to summoning the Alpha.
- **Offspring you didn't pick** appear here as *known but unachieved* — outlined rather than filled. Breeding therefore doesn't just grow you, it hands you a shortlist of concrete targets to hunt for.
- Selecting a cell shows that form's name, its stats, and which biome you first ate your way into it.

The grid does the design's job for free: an empty bottom half is a visible reminder that you have never bred past three limbs, and an empty column is a colour you keep failing to hunt.

### 2.10 The loop, in one paragraph

Enter a biome as something small. Hunt coloured prey to fill your limbs — the buffer runs FIFO, so every meal spends your oldest colour, and the moment the buffer resolves differently you mutate into a new form: a family, an intensity, a different trade of health for speed for reach. Run down grazers to patch yourself back up, poop out a colour you don't want — the limb goes white, ready for the one you do — and hunt specifically for the trait that opens the part of the map you can't reach. Eat varied enough and often enough and the lair begins to stir — then erupts: the champion of whatever colour you preyed on most comes out hunting you, **your equal in rank but fighting at Clash intensity**, and it cannot be outrun. the biome empties — prey and grazers bolt for the edges — so you heal and set your buffer *before* you trip the gate, then fight on what you brought. Keep eating to widen your litter, or go and meet it. Beat it, eat it, take its **emblem** — the trophy that opens the way on and lets you breed. Then breed: the litter screen shows you each offspring's traits and panels, you keep one, and the rest become marked targets in the Bestiary. Walk into the next biome a limb heavier, with more shapes available to you and harder terrain in the way. Conquer all five and breed to six limbs — a **Conquest** — and the **Ascension** opens: play the six-limb creature at last and hunt the top row. When your record runs deep enough the **Apex** wakes, and beating it is the game won. Die at any point and **the line ends** — five generations of inheritance gone in one mistake. What survives is the record: every form that bloodline reached and every emblem it took, added permanently to the Bestiary, so the next line starts from a one-limb cube but you start from knowing more.

### 2.11 Where AI sits in the finished game

Nothing described above is driven by a language model while you play. Creature behaviour is a hand-written finite-state machine, biome layouts come from a **seeded procedural generator**, Alpha challenges are threshold checks, and litters are rolled from a weighted table. All deterministic, all offline, all instant.

What is AI-built is the **code underneath**. The systems that spawn creatures, roll a biome's palette, place defended pockets, fire the Alpha challenge and run the breeding step were designed and implemented by the agent team in §3. So "AI-generated events" in this project means *events whose systems were authored by agents* — not events invented by a model mid-run.

Three consequences the player actually feels: **no network dependency** (the game runs fully offline), **no inference latency** (an Alpha triggers on the frame its threshold is met), and **reproducibility** (two players on the same seed get the same biome, which is what makes balance testing possible at all).

---

## 3. AI Architecture — the agent team that builds the game

**Framing:** the multi-agent system is the **development studio, not the product**. Morphivore ships with **no LLM at runtime** — in-game creature AI is a traditional finite-state machine (wander / flee / hunt) plus a scripted lock → wind-up → pounce attack cycle. **Runtime token cost is zero.** The agents below are Claude Code agents that write and test the game.

Each agent owns files and has a definition of done tied to something the player can see.

1. **Director** — reviews every other agent's work against this GDD and owns the shared data contracts (`GameConfig`, creature/trait definitions). *Gameplay effect:* "form," "colour" and "trait" mean the same thing in combat code, world generation, and the Bestiary screen.

2. **Gameplay Engineer** — writes the player: movement, lock-on, pounce, knockdown, the eat-and-absorb sequence, the prey/grazer split (prey mutates you, only grazers heal you), the per-colour stat profiles that set your bar length, mutation rules, breeding and the win/loss check. *Gameplay effect:* everything the player physically does is this agent's code.

3. **Creature AI Engineer** — writes the traditional enemy AI: the flee/hunt state machine, the symmetric lock → wind-up → pounce attack, stagger and knockdown reactions, **pack aggro so defended pockets swarm as a group**, and territorial elites that hold a range. *Gameplay effect:* the orange halo warning, the punishable wind-up, prey that panics and runs — and the moment four creatures turn on you at once in a marsh hollow.

4. **World Generation Engineer** — writes the procedural biome generator: terrain layout, pond/peak/lava placement, the trait gates, the **common-creature spread and the defended rare-colour pockets**, the per-run palette roll, and the Alpha lair. *Gameplay effect:* a different Wetlands every run where food is everywhere but the purple you need is in a hollow with four things guarding it.

5. **UI Engineer** — builds the HUD (Health bar, the two Alpha gate counters, lock reticle, threat halo, enemy health bars), the Bestiary grid, the litter-select screen, and run-start/death screens. *Gameplay effect:* the player can always read how hurt they are, what's hunting them, and how close the Alpha is to waking.

6. **Creature Art & VFX Agent** — generates the creatures themselves in code: limb morphology, colour, decorated panels, and the feedback effects for pounce impact, knockdown and absorption — including the **two absorb languages** (§2.3): colour streaming into a limb for prey, body-dissolve with a refilling bar for grazers. Creatures must be procedural because they physically change shape at runtime, so no authored model would work. *Gameplay effect:* you can tell what a creature is, what it can do, and whether it's winding up to attack you, just by looking at it.

7. **Asset Integration Agent** — imports and wires up the third-party environment art: terrain, biome props, water, skyboxes and audio, from a short list of licence-cleared free sources the developer picks. It handles URP material conversion, prefab setup, colliders and the credits file. It does **not** choose packs — licence and taste calls stay with the human. *Gameplay effect:* the Wetlands look and sound like wetlands instead of blue boxes.

8. **QA & Balance Agent** — runs repeatable play tests and tunes creature stats, Alpha thresholds, litter sizes and trait drop rates against two targets: a full five-biome run lands in **35–45 minutes**, and each biome's Alpha threshold is reachable without grinding but not hit by accident. **It owns the run event log** (§4.10) and reads it rather than relying on impressions. *Gameplay effect:* the run length the design promises is the run length the player gets.

9. **Content & Tone Agent** — authors the **150 form names** (§2.4b) and the creature roster, and owns the game's voice. Its register brief is now set: **primal, crude, comedic** — the Cubivore tone, for a game in which you steer your own identity by pooping. *Why this agent exists:* Morphivore has no dialogue, no narrator, no item text and no lore. Form names are the only place the game can be grim, or funny, or clinical — they are the entire authorial voice, and the player reads them comparatively, side by side, on the Bestiary screen. The draft left this unowned while declaring the form table "hundreds" of entries; three reviewers independently found the same hole from three lenses (production cost, schedule, and tone). *Gameplay effect:* the player can tell what kind of game this is from the name of the thing they just turned into. **Scheduled in week 0**, before any other agent, because every downstream agent — Creature Art & VFX especially — is executing against a tone decision that has to exist first.

### 3.1 Agent interfaces

What each agent is given, what it hands back, where that lands, how often it runs, and what happens when it gets it wrong.

| Agent | Input received | Output produced | Where it lands | Frequency | On failure |
|---|---|---|---|---|---|
| **Director** | This GDD, open design questions, other agents' diffs | Revised GDD sections; data-contract definitions | `docs/`, `GameConfig.cs` | Start of each session, and on any contract change | Contradiction is escalated to the developer; no code ships against an unratified contract |
| **Gameplay Engineer** | GDD §2, current `PlayerController.cs` / `Creature.cs` | Complete C# source files | `Assets/Scripts/Game/` via the MCP bridge | Most sessions | Compile error caught by log grep; agent reads the error and re-writes; `git` revert after two failures |
| **Creature AI Engineer** | GDD §2.2, §2.7, current `EnemyAI.cs` | Complete C# source files | `Assets/Scripts/Game/EnemyAI.cs` | Weekly | As above |
| **World Generation Engineer** | GDD §2.6–2.7, biome/palette tables | C# generator **+ `biomes.json` / `creatures.json` content data** | `Assets/Scripts/Game/`, `Assets/Data/` | Weekly | Generator is **seeded**, so a bad layout is reproduced from its seed and fixed rather than guessed at. Malformed JSON falls back to built-in defaults |
| **UI Engineer** | GDD §2.9 and the HUD spec | C# Canvas-construction code | `GameManager.cs` UI methods | Weekly | As Gameplay Engineer |
| **Creature Art & VFX** | Form / limb / colour spec | Procedural mesh + material code | `Creature.BuildVisuals()` | Periodic | As Gameplay Engineer |
| **Asset Integration** | Developer-selected, licence-cleared packs | Imported prefabs, URP materials, `CREDITS.md` | `Assets/Art/` | Occasional | Import is rejected outright if the licence is unverified |
| **QA & Balance** | **Run event logs**, target metrics | Tuning values, bug reports | **Content JSON** (`Assets/Data/`) — no recompile needed | End of most sessions | Values outside target are reverted to the last known-good set |
| **Content & Tone** | Form table shape (§2.4b), tone brief | 150 authored form names, creature roster names | `forms.json`, `creatures.json` | **Week 0**, then occasional | Names failing the tone brief are rewritten, not shipped and patched |

### 3.2 The AI development pipeline

The complete path from a design sentence to something the player can see:

> **Design intent** (a line in this GDD) → **developer instruction + repo context** → **agent** → **C# source written through the Unity MCP bridge** → **asset refresh** → **domain reload (8–13 s)** → **compile verified** by grepping `Editor.log` for `error CS` → **Play mode entered**, log checked for exceptions → **developer plays the change** → **player-visible result**

- **What activates an agent:** a developer instruction in a Claude Code session. Agents never self-trigger and never run while the game is being played.
- **Which model:** Claude via Claude Code — the larger model for design and hard debugging, the faster model for bulk implementation (§4.4).
- **How output is validated:** three gates, in order — it must compile, it must enter Play mode without exceptions, and it must survive a human play test. Only the third gate can judge whether something is *fun*, which is why it is never delegated. **Content-data changes skip the first two gates entirely** — JSON is schema-checked on load, so a balance pass goes straight to play testing without a recompile.
- **If it fails:** compile and runtime errors are fed straight back to the agent, which re-writes. Two failed attempts trigger a `git` revert and developer escalation. Because the whole scene is built procedurally at runtime, a revert is always a clean code revert — there is no corrupted scene file to untangle.

### 3.3 Engine integration — the Unity MCP bridge

AI output becomes running gameplay through a **custom Unity Editor plugin** (`MCPBridge.cs` / `MCPBridgeWindow.cs`) that listens on a local socket and exposes the editor to agents.

| | |
|---|---|
| **Activation event** | An agent issues a bridge command (`write_file`, `refresh_assets`, `play`, `get_components`) |
| **Request component** | `MCPBridge.cs`, a Unity Editor plugin — local only, no external network |
| **Data exchanged** | C# source text, scene-hierarchy queries, play-mode commands |
| **Authorised write surface** | `Assets/Scripts/` and `docs/` only. Agents never hand-edit scene or asset binaries |
| **Validation** | Asset refresh → `Editor.log` grepped for `error CS` → Play mode entered → log checked for exceptions |
| **Player-visible feedback** | The developer observes the change in Play mode; nothing surfaces to an end player |
| **Timeout / retry** | The bridge is unreachable for **8–13 s** during domain reload; agents wait and re-ping rather than treating silence as failure |
| **Logging** | `~/Library/Logs/Unity/Editor.log` is the source of truth — the bridge's own log command is unreliable and is not trusted |

Because the scene is constructed procedurally at runtime (§4.1), agents only ever write plain text files. There are no binary scene merges, which is what makes multiple agents touching the project safe.

**Content data: JSON, not code.**

Procedural generation does not remove the need for content — it *consumes* it. A seed and a ruleset produce layout variety, but something still has to define what a Wetlands **is**. That definition lives in JSON rather than in C#:

| File | Defines |
|---|---|
| `biomes.json` | Terrain parameters, which traits gate the biome, creature-palette weights, **minimum distinct colours in a roll**, **standing population and respawn rate**, pocket count, Alpha roster, and the two Alpha gate thresholds |
| `creatures.json` | Colour family, **meat tier**, base stats, role (grazer / prey / elite / Alpha), **rank (limb count)**, **grazer flee speed**, which biomes it lives in, and which trait its meat carries |
| `forms.json` | The **150 forms** (§2.4b) — for each: family, intensity, rank, its authored name, its socket layout, and its stat profile (generated from the intensity-scaling rule in §2.4, then hand-tuned) |
| `panels.json` | Each panel's power and magnitude, which elites drop it, and its visual attachment point |
| `emblems.json` | Which Alpha drops each emblem and which biome it opens (emblems no longer grant powers — see §2.5) |

**Ambient creature rank is now stated data, not an omission.** Ordinary prey are pinned at the player's current rank minus one (**floored at rank 1** — so in the Prairies, where the player is rank 1, prey are also rank 1, not a nonexistent rank 0); elites at the player's rank; **Alphas at the player's rank** (a same-rank mirror-match, §2.5), always at Clash intensity. The Apex is rank 6, Clash. The draft never stated any of this, which left time-to-kill undefined and made the difficulty curve unarguable in either direction.

**Generator invariants — checked at generation time, not at play time.** The draft's schema checks were all referential-integrity checks on static data (does this creature name a biome that exists), while every failure mode that can actually make a run unwinnable is a *reachability property of a rolled world*. The generator must now guarantee, and refuse the seed if it cannot:

1. Every trait gate in a biome has a **reachable carrier** for its trait, outside the terrain that trait unlocks.
2. Every biome's rolled palette contains **enough distinct families to keep the form gate honestly slack, not merely satisfiable.** The `min_distinct_colours` field in `biomes.json` is set so the reachable pool stays at least ~1.5× the gate: **4 families** in Prairies/Wetlands/Mountains, **5 (all)** in Beach and Volcanic. Bare satisfiability is not enough — a 3-family Volcanic roll would technically clear the 11-form gate (3 families × 5 tiers = 15) but collapse the advertised slack from 2.3× to 1.36×, so it is refused. The §2.5 slack band (2.3×–5.0×) is valid *because* of this invariant, not despite the per-run roll.
3. Every biome's standing population plus respawn can **supply that biome's coloured-prey count** with margin.
4. The rolled palette's plausible most-eaten colour is **present in that biome's Alpha roster**.
5. A trait required by a **later** biome remains obtainable given the player's expected trait set on entry (§2.6a).

A seeded generator reproduces an unwinnable run exactly, which is a debugging affordance — it gets a tester to the bug after a player has already lost a run to it. These five checks are what *prevent* it. They are owned by the World Generation Engineer and ratified by the Director.

**Why JSON and not hardcoded C#:** every tuning change in code costs a recompile — the 8–13 second domain reload that is this project's single biggest constraint (§4.2). Balance tuning is also the **most-repeated task in the project**. Putting content in JSON read at runtime lets the QA agent retune Alpha thresholds, spawn weights and creature stats **without a recompile at all**, which attacks the constraint exactly where it costs the most. It is also the format agents write most reliably through the bridge, and it diffs cleanly in `git`, so a balance change is reviewable like any other.

**Validation and fallback.** Each file is checked against a schema on load: required fields present, stat values within sane ranges, every creature referencing a biome that exists, every biome fielding at least one Alpha. A malformed or missing file **logs a specific error and falls back to built-in defaults** rather than starting a broken run — a bad data edit costs a warning in the console, never a corrupted save or an unwinnable biome.

**Ownership:** the World Generation Engineer authors biome and creature data; the Director owns the schema and ratifies changes to it. A dedicated content agent is deliberately *not* created yet — it would only earn its place if the form table and creature rosters outgrow those two.

### 3.4 Prompt constraints

Rules every agent is briefed with, so output is consistent and reviewable:

- **Identity and ownership.** Each agent is given its owned directory, the GDD sections it implements, and the data contracts it may not change unilaterally.
- **Allowed inputs.** The GDD, its own source files, and compile/runtime logs. Never binary assets or unrelated systems.
- **Required output format.** Complete C# files rather than fragments, matching the existing naming and comment density of the file being edited.
- **Prohibited.** Changing a shared data contract without Director ratification; adding any runtime network or model call; using `OnGUI` (the project is Canvas/uGUI throughout); importing third-party art without a verified licence.
- **Validation rules.** A change is not "done" until it compiles clean, enters Play mode without exceptions, and has been described honestly to the developer — including what was *not* verified.
- **Recovery.** On invalid output, the agent reads the actual error and re-writes. After two failures it stops, reverts via `git`, and escalates rather than accumulating broken edits.

---

## 4. Technical Strategy

### 4.1 Stack

Unity 6 (URP), C#, single scene constructed procedurally at runtime. The project is driven by Claude Code through a **Unity MCP bridge** (a custom editor plugin) that lets agents read/write scripts, inspect the scene hierarchy, enter and exit Play mode, and trigger asset refreshes.

**Controls — keyboard-and-mouse and gamepad in parallel, both first-class.** The game reads whichever the player last touched; nothing is exclusive to one.

| Verb | Keyboard + mouse | Gamepad |
|---|---|---|
| Move / face | WASD | Left stick |
| Lock on (hold) | Right mouse | Left trigger |
| Pounce | Left mouse | A |
| Dash | Space | Right trigger |
| Poop oldest colour (§2.4a) | Q | B |
| Pause / Bestiary | Esc | Start |

Built on Unity's Input System with an action map, so rebinding and additional pads come for free. The prototype already runs both paths (§4.9).

### 4.2 Named constraint: the Unity domain-reload loop

**This is the single biggest limit on agent throughput, and it is measured, not hypothetical.**

Every C# edit requires an asset refresh, which triggers a Unity **domain reload**. During reload the MCP bridge goes unreachable for **roughly 8–13 seconds**, and the editor's log tool is unreliable — compile errors have to be grepped directly out of `~/Library/Logs/Unity/Editor.log`.

The practical effect: an agent cannot hot-iterate. Every change costs a verify cycle of *edit → refresh → wait → grep for `error CS` → enter Play mode → check for exceptions*, which caps useful iterations at a handful per minute and makes long chains of small speculative edits very expensive.

**Mitigations built into the workflow:**
- **Batch edits.** Agents make all related changes across files, then refresh **once**.
- **Keep tuning in data.** Biome, creature, form and emblem definitions live in **JSON read at runtime** (§3.3), not in C#. The most-repeated task in the project — balance tuning — therefore costs **zero recompiles**, which is the single largest saving available against this constraint.
- **Verify by log, not by eye.** Compile status is confirmed by grepping the editor log; runtime health by entering Play mode and checking for exceptions. Feel and fun are confirmed by the human, who is the only one who can actually play it.

### 4.3 Second constraint: no artist — a split art pipeline

There is no artist on this project, so art is split by whether the thing **changes shape at runtime**.

**Creatures are procedural, by necessity and by choice.** A beast gains limbs when it breeds, changes colour when it mutates, and gets panels bolted to it when it eats an elite. No authored, rigged model survives that, so creatures are generated in code from primitives. This is also on-theme: the game's whole visual identity is cube-beasts made of cube limbs, so the constraint and the art direction point the same way — matte, papercraft-like creatures read by **silhouette and colour**, not texture.

**The world is not procedural art.** Terrain, props, water, skyboxes and audio come from **human-curated, licence-cleared free asset packs** (e.g. CC0 sources such as Kenney and Quaternius). This is what makes Prairies, Wetlands and Mountains feel like different places rather than differently tinted boxes.

**Why curated and not scraped.** An automated asset-scraping agent was considered and rejected: licence compliance is a human liability call, an agent cannot reliably judge whether two packs look like the same game, and mismatched packs are the fastest route to an asset-flip look. The developer selects packs and owns the licence decision; the Asset Integration Agent does the mechanical import, material conversion and prefab wiring, and maintains attribution in `CREDITS.md`.

### 4.4 API constraints — and the one that actually binds

**The real limit is a subscription, not a token meter.** Development runs on a **Claude Pro** plan through Claude Code, which is metered as **usage windows** — a short rolling window plus a weekly cap — rather than as a pool of tokens. The token budget in 4.5 is therefore a *planning estimate of work volume*, not a quota that can be spent down. The binding constraint is **how many hours of agent work exist in a week**, and it is the single biggest limit on this project's pace.

Three consequences shape how the agents are actually run:

- **Model tiering.** The larger model is reserved for design, architecture and debugging genuinely hard problems; the faster model does the bulk of implementation work. Model choice moves the weekly ceiling more than any other decision, so it is a scheduling decision, not a preference.
- **Batching is mandatory, and doubles as a cost control.** The Unity domain-reload constraint (4.2) already forces agents to group edits and refresh once. That same discipline is what keeps a week's allowance from being burned on dozens of one-line iterations.
- **Tuning must never cost a code cycle.** Balance values live in **runtime-loaded JSON** (§3.3), so the QA agent can retune Alpha thresholds, litter sizes and creature stats without a recompile — the most-repeated task in the project is deliberately the cheapest one.

Also relevant:

- **Context limits.** Gameplay scripts are kept small and single-responsibility so an agent can read a whole file rather than a fragment. Large binary assets are never fed to agents.
- **No runtime API calls.** The shipped game makes zero model calls: no inference cost, no latency risk, no network dependency in play. All model usage is development-time.

**Planning assumption:** a realistic week is a handful of substantial agent sessions, not continuous development. The five-biome scope above is sized on the expectation that the generator is written once and the remaining biomes are configuration — work that survives an interrupted week far better than five bespoke levels would.

### 4.5 Operational limits

The full checklist, including the limits that are **not applicable** under a development-time AI architecture — stated rather than omitted, so the reasoning is visible.

| Limit | This project |
|---|---|
| **Engine / platform** | Unity 6 (URP); PC (Windows and macOS) |
| **Model & provider** | Anthropic Claude via Claude Code — larger model for design and hard debugging, faster model for bulk implementation |
| **Context window** | Bounded per session. Managed by keeping gameplay scripts small and single-responsibility so an agent reads a *whole* file, never a fragment |
| **Input / output token limits** | Per-response output caps favour complete-file writes over long prose; oversized files are split by responsibility rather than truncated |
| **Processing latency (development)** | Dominated by Unity's **8–13 s domain reload**, not by model response time |
| **Latency target (runtime)** | **Frame budget only — 60 fps.** No inference in the loop, so an Alpha fires on the frame its threshold is met |
| **API rate limits** | Subscription usage windows (§4.4) — the binding development constraint |
| **Network requirements** | **Development:** required. **Shipped game:** none — fully offline |
| **Memory / storage** | Target < 2 GB RAM, < 500 MB install. Creatures are primitives and biomes are regenerated from a seed rather than stored, so world data costs kilobytes; the budget goes almost entirely on imported environment art |
| **JSON / structured formats** | **Content data is JSON** (biomes, creature species, the form table, emblems), authored by agents and read at runtime. Validated against a schema on load, falling back to built-in defaults on a malformed file. Agent *code* output remains C#, validated by the compiler. **No model output is parsed at runtime** |
| **Content safety** | No model-generated or user-generated text ever reaches a player — all in-game text is authored. There is nothing to moderate at runtime |
| **Retry / timeout rules** | Bridge unreachable for 8–13 s during reload → agents wait and re-ping rather than treating silence as failure. Two failed attempts → `git` revert and escalate |
| **Offline / fallback behaviour** | The shipped build has no online dependency at all, so there is no degraded mode to design |
| **Max simultaneous agents** | **One.** A single Unity Editor instance owns the project, and concurrent writers would race on domain reloads and asset refreshes. Parallelism happens *across* sessions, never inside one — this is a hard architectural limit, not a preference |
| **Development time / scope** | ~85–125 agent-hours across ~14 weeks (§4.8), scoped in §4.9 |

### 4.6 Token budget

Estimated for the full 14-week build (input + output combined, with headroom). As noted in 4.4, this is a **planning estimate of work volume** — the Pro subscription is metered in usage windows, not tokens, so these figures size the *effort* per agent rather than a spendable quota.

| Agent | Main deliverables | Est. tokens |
|---|---|---|
| Director | GDD upkeep, data contracts, reviews | 4 M |
| Gameplay Engineer | Movement, lock/pounce/knockdown/eat, mutation, win-loss | 12 M |
| Creature AI Engineer | FSM, symmetric attack cycle, reactions, species behaviour | 8 M |
| World Generation Engineer | Biome generation, trait gates, population tables, arenas | 10 M |
| UI Engineer | HUD, Bestiary grid, litter-select and death screens | 6 M |
| Creature Art & VFX Agent | Limb morphology, panels, impact/absorb effects | 6 M |
| Asset Integration Agent | Importing/wiring curated environment packs, credits | 4 M |
| QA & Balance Agent | Play tests, tuning, regressions | 6 M |
| Contingency (~20%) | Rework, integration, balance passes | 11 M |
| **Total** | | **~67 M tokens** |

### 4.7 Cost projection

**Development cost is a flat subscription, not metered usage.** Claude Pro is billed monthly (~$20/month at time of writing — to be confirmed against current pricing), so the build's total AI cost is:

| | |
|---|---|
| Development cost | ~$20/month × ~4 months = **~$80 total** |
| Maximum acceptable monthly AI expense | **The subscription price.** There is no metered usage, so no variable cost can exceed it |
| Runtime cost | **None** — the shipped build contains no model calls, no API keys and no network layer |

All model usage is development-time, so AI cost is fixed by the calendar rather than by how many people play: there is no per-session or per-player inference to project.

*If the project were ever migrated to metered API billing* (for example to add a runtime feature later), the ~67 M-token estimate in §4.6 would need pricing against the chosen model's published rates **at that time**; no current figure is quoted here because it would be stale by implementation.

### 4.8 Weekly capacity — what the subscription actually buys

Because the plan is metered in usage windows rather than tokens (4.4), the honest unit of planning is **agent-hours per week**. These are the working assumptions behind the schedule below; they are to be measured against real usage in the first fortnight and revised rather than trusted.

| | Assumption |
|---|---|
| Working sessions per week | 3 |
| Length of a session | 2–3 hours |
| **Active agent time per week** | **6–9 hours** |
| Model split | ~80% fast model for implementation, ~20% large model for design, architecture and hard debugging |
| Build window | 14 weeks |
| **Total agent time** | **~85–125 hours** |

*Sanity check:* ~67 M tokens (4.6) spread over ~100 hours is roughly 650–700 K tokens per working hour, which is the right order of magnitude for agentic coding with repeated file reads. The two estimates were made independently and agree — which is the main reason to trust either.

**What that buys, by phase:**

| Weeks | Focus | State at the end |
|---|---|---|
| **0** | **Data contracts + tone.** The persistence matrix (§2.6a), the form model (§2.4b), the Bestiary save format, and the 150 authored form names | Every downstream agent codes against a ratified contract instead of inventing one |
| 1–2 | FIFO colour buffer, recipe matching, mutation, **the event log** | You can eat your way through forms at one and two limbs, and every run produces data |
| 3–4 | Biome generator + **the five generator invariants**, Prairies, colour niches and defended pockets | A procedural first biome that plays differently every run and cannot roll unwinnable |
| 5–6 | Alpha lair, two-gate trigger, warning state, emblem, breeding and the litter screen | The biome → Alpha → breed → next-biome loop closes end to end |
| 7–8 | Traits, terrain gates, Wetlands, trait inheritance on the litter screen | Fins gate real water; two biomes chain; the persistence matrix is exercised |
| 9–10 | Bestiary grid + nested intensity ladders, run-start/death screens, Mountains | Meta-progression persists across runs; three biomes playable |
| 11–12 | Beach and Volcanic as configuration, limbs 5–6, **the Ascension (rank-6 finale + Apex boss)**, **art integration pass** | Full five-biome run to six limbs, then the rank-6 Ascension; the win condition is reachable; biomes look like places |
| 13–14 | Balance, QA passes, polish | Runs land in 35–45 minutes, read off the log; thresholds tuned via four coefficients |

**Two changes to the ordering, both driven by the review.** Week 0 exists because the review found four separate systems silently inventing their own answer to "what is a form, and what persists" — under a one-agent-at-a-time architecture there is no concurrent reviewer to catch the divergence, so the contract has to precede the code. And **the Alpha/breeding loop now closes in weeks 5–6, before traits are built in 7–8** — the draft had it backwards, building the riskiest untested layer before the core loop it decorates was proven end to end.

**Art integration is now on the schedule.** The draft had no week for importing, converting and wiring five biomes' worth of environment art, while simultaneously resting its regression-safety story on there being no binary assets. It is placed in 11–12 rather than earlier so the generator's art dependency graph is known before art lands in it.

### The cut ladder — two axes, not one

The draft had one cut line: drop Beach and Volcanic, ship at three biomes and four limbs. That line is real and it is well designed — but the review showed it is aimed at the wrong part of the schedule. **Every blocking finding the board raised came from systems that survive that cut**, and the cut only recovers weeks 11–12, while the work those findings created lands in weeks 0–8. A content cut cannot pay for a systems overrun.

So there are now two, in order:

| Order | Cut | Recovers | The game becomes |
|---|---|---|---|
| **1** | **The Ascension (rank-6 finale + Apex).** If the rank-6 stage proves too costly, cut it: the fifth Alpha then ends the run on the final breed, as the draft had it | A rank-6 arena, one boss, and 25 forms of authored content; the record gate re-derives to ~85 of 125, the top milestone drops to ≤125, and the win is beating the Volcanic Alpha | A complete five-biome, six-limb conquest — losing only the rank-6 victory lap and an honest 150 denominator (it becomes 125) |
| **2** | **Traits and terrain gates.** The only major system with zero prototype support, and the one whose failure mode is an unwinnable run rather than a shorter one | Weeks 7–8 entirely | Five biomes, complete and winnable, losing an exploration texture |
| **3** | **Beach and Volcanic.** The original cut line | Weeks 11–12 | Three biomes, four limbs — a smaller game, not a broken one |

**Rank 6 is cut from the *content* budget but kept in the *fiction*.** The final breed still happens: you beat the last Alpha, choose a six-limb offspring, and take an emblem that opens nothing because there is nowhere further to go. That is the only ending image this design has, and it is a good one — you become the apex of a food chain and the world has no more of itself to give you. The ladder has a top, and it is you — an emblem that opens nothing, because nothing is left above you. The win screen shows that six-limb form entering the Bestiary: the shape that sat on top. What is cut is authoring a full 25-form intensity ladder for a rank the player occupies for one screen.

### 4.9 Scope — the first publishable build

**The target is a finished game in 14 weeks, not a demo.** Version 1.0 is a build a player can download, start cold, learn without a tutorial, win or lose, and want to replay. Every system listed below exists to serve that single run; anything that does not is deferred rather than half-built.

**In v1.0:** all **five biomes** (Prairies, Wetlands, Mountains, Beach, Volcanic) with per-run palette rolls and defended rare-colour pockets, the full combat verb (lock → pounce → knockdown → eat), the prey/grazer split for healing, pack aggro and territorial elites, colour mutation across the **full one-to-six limb range**, the Alpha lair + two-gate trigger + emblem + breeding/litter step, the Bestiary grid and its persistent unlocks, the four traits and their gates, and the win/loss + permadeath loop.

**Why five biomes fits in 14 weeks rather than costing five times the work:** biome generation is **one system driven by data**. The generator, the trait gates, the niche/pocket placement, the Alpha lair and the palette roll are all built once. Each additional biome is then a **configuration file** — a terrain type, a creature palette, which traits it demands, which Alphas it can field — not new code. The same holds for limbs five and six: the mutation system is combinatorial, so supporting six limbs is the same code as supporting two with a larger form table behind it. The marginal cost of the last two biomes is **content and balance**, which is precisely the work that runs cheapest (§3.3 — content lives in JSON and needs no recompile).

**Deferred past v1.0:** multiplayer, authored and rigged 3D creature art with animation, original composed audio, and any biome beyond the five above. These are candidates for a post-launch update, not cut features — nothing in the v1.0 architecture forecloses them.

**Stretch goal — emblem skins.** Emblems collected in the Bestiary (§2.9) unlock **cosmetic skins for the main cubic body**: a different surface treatment on the head-and-torso block, earned by having claimed that Alpha's emblem at some point across any run. This is deliberately filed as a stretch goal rather than a v1.0 feature, for three reasons that make it a good one:

- **It is cheap in exactly the way the rest of the art is not.** Creatures are cube primitives, so a skin is a material swap on one mesh — and licence-cleared cubic/low-poly texture sets are plentiful in the asset store, which is the same sourcing model §4.3 already uses for environments.
- **It cannot break anything.** Skins are cosmetic only, touch no stat, no recipe and no gate, and render on the main face where traits already live (§2.6a) — so they need a layering rule with trait geometry and nothing else.
- **It pays the meta-layer a visible reward.** A player whose line died in the Mountains still banks the emblems it won, and those emblems visibly change what the *next* bloodline looks like. That converts a lost run into something the player can see on the creature in front of them.

If the schedule holds, this is the first thing added after v1.0. If it does not, nothing in v1.0 depends on it.

**The cut ladder** is in §4.8: rank-6 content first, then traits and gates, then Beach and Volcanic. The game remains complete and winnable at every rung.

### 4.9a Who this is for — and what "publishable" means here

The draft claimed a "finished game a player can download… and want to replay" while costing only its AI spend. It named two inspirations that pull in opposite market directions — *Cubivore*, a 2002 cult obscurity with essentially no living audience to inherit, and *The Binding of Isaac*, the largest and most crowded roguelite audience there is — and never said which one it was addressed to. That ambiguity is load-bearing, because it decides what "learn without a tutorial" is allowed to mean.

**Stated plainly: the target is the first releasable version of the capstone game** — a genuine attempt at a small, shippable game rather than a tech demo. There is no commercial target, no launch date, and no revenue expectation at this stage. What "publishable v1.0" means here is a build that a stranger can download, start cold, and finish or lose without the developer sitting next to them — that is the bar, and it is a design bar rather than a market one.

**The audience it is designed for is the Cubivore-descended player**, not the Isaac-descended one: someone for whom working out the mutation grammar unaided *is* the game. That choice has a consequence this document now honours — opacity is permitted in the *menu* (what the world will let you eat) but **not in the mechanism**. The buffer is FIFO, the next slot is highlighted, the recipes are legible, and the Bestiary shows you what exists. The draft failed this test in the opposite direction: its mechanism was undefined and its constraints were arbitrary, which is the worst of both audiences.

**Non-AI costs, stated rather than omitted:** Steam Direct (~$100) if it is ever published, storefront capsule art, and audio beyond free packs. Storefront art is the one asset class that can be neither a CC0 environment pack nor a procedural cube primitive, and there is no artist on this project — so if publication ever happens, that is a commissioned cost, not a scheduled one. It is named here because the review correctly noted that a document this careful about naming its constraints should not have a blank where its non-AI budget goes.

**Already prototyped and playable today:** lock-on, pounce, knockdown, the eat-and-absorb animation, colour-driven class stats, symmetric enemy hunting with the threat halo, solid-body collisions, and the HUD. The remaining work is the limb/colour mutation system, the breeding step, procedural biome generation, traits and gates, and the Bestiary.

### 4.10 Testing strategy

Every change passes three gates, in increasing order of cost:

1. **It compiles.** Asset refresh, then `~/Library/Logs/Unity/Editor.log` grepped for `error CS`. Automatic, seconds.
2. **It runs.** Play mode entered, log checked for exceptions. Automatic, seconds.
3. **It plays right.** The developer plays it. Only this gate can judge whether something is *fun*, which is why it is never delegated to an agent — and why agent reports are required to state explicitly what was *not* verified.

### The fourth gate: the run event log

The draft gave the QA & Balance Agent a job — time full runs, tune ten thresholds against a 35–45 minute target — and no instrument to do it with. The three gates above end at "the developer plays it," which means **one data point costs 40 minutes out of a 6–9 hour week**, and it is collected by the one person least able to judge it: the developer, who knows every threshold and plays the efficient line by reflex.

Two changes fix this without building a second product:

**1. Every run writes an event log to disk.** Timestamped kills (with colour, rank and time-to-kill), mutations, gate trips, biome entry and exit, damage taken, grazers eaten, and death cause. It costs a few hours to build, needs no bot and no headless mode, and converts every playtest the developer was going to do anyway from *one impression* into *one dataset*. It also settles empirically the questions this document leaves to tuning — real time-to-kill, whether the run lands in 35–45 minutes, and whether the mid-run stretch is momentum or grind.

**2. The tuning surface is cut until it fits manual measurement.** Ten independent gate thresholds validated at 40 minutes a run is unaffordable at any staffing level this project has. The thresholds are therefore generated by **two linear formulas, two coefficients each** — `forms_required = f0 + f_step×(biome−1)` (with f0 = 3, f_step = 2 → 3, 5, 7, 9, 11) and `prey_required = p0 + p_step×(biome−1)` (with p0 = 15, p_step = 5 → 15, 20, 25, 30, 35) — so the developer tunes four numbers, not ten, and the table in §2.5 is reproduced exactly. (An earlier draft of this section tied the form gate to `round(a × reachable_pool)`; that cannot work, because Beach and Volcanic share a pool of 25 but need gates of 9 and 11, and one coefficient times one pool is one number. The gate is linear in biome depth, not in pool size.)

A scripted bot player was explicitly considered and **rejected**: it would need to execute the full combat verb, navigate procedural terrain, satisfy trait gates and beat an Alpha — a working AI player for a game whose combat verb is still being finished. That is a second product built against an unstable spec, inside a budget that cannot afford the first one.

Beyond per-change gates:

- **Balance testing** is the QA agent's standing job: full runs timed against the 35–45 minute target, read off the event log, with each biome's Alpha thresholds checked to be reachable without grinding.
- **Generator invariants** are checked at world-generation time (§3.3) — five reachability properties that must hold before a seed is playable.
- **Seeded reproducibility.** The generator is seeded, so a bad layout is reproduced exactly rather than hunted for. This is a *debugging* affordance and is no longer relied on to prevent unwinnable runs; the invariants do that.
- **Regression safety, honestly stated.** Because gameplay code builds the scene procedurally, a `git` revert of `Assets/Scripts/` restores a working build — **as long as no authored art is involved.** Once imported prefabs, terrain, materials and audio land in `Assets/Art/`, that property no longer holds on its own: a code revert can restore a generator pointing at a renamed prefab path, producing a build that compiles, enters Play mode, and spawns nothing. All three gates above pass on that build. **Art imports are therefore committed as their own atomic commits, and the generator references art through a single indirection table** (`art-manifest.json`) so a broken reference fails loudly at load rather than silently at spawn.

---

## 5. Revision Log — what the review found, and what changed

### 5.1 How the document was tested

The draft was put through a **six-agent adversarial design review**. Six specialist reviewers each read the full GDD in an isolated context, with no access to each other's work: a systems designer, a narrative critic, a player psychologist, a technical feasibility lead, an adversarial QA reviewer, and a production/business analyst. Each was instructed that "looks good" was a failed review, and that every finding had to trace to something the document says or conspicuously omits.

They were then **re-spawned with all six reviews** and required to cross-examine: name conflicts with colleagues and argue their side, find issues visible only by combining two lenses, and revise their own calls. Pure agreement was defined as a failed round. Finally a moderator read all six files and produced a ranked synthesis.

**Result: 33 findings, 13 blocking, 5 disagreements the board could not settle.**

Two properties of that process did work no single reviewer could have done:

- **Independent convergence is a confidence signal.** Six isolated reviewers found the form-space contradiction; four independently found the missing persistence rules. Because they could not see each other, agreement means the defect is legible from any angle — not that one reviewer was persuasive.
- **The cross-examination round produced a finding that existed in no individual review.** The player psychologist read §2.5's phrase *"the ambient creatures scatter"* as removing the healing supply and derived an unrecoverable ambush. Adversarial QA read the same phrase as leaving grazers available and derived an infinite kite — "trigger the Alpha, then never fight it." Both readings were supported by the text and mutually exclusive. **One unstated word decided whether the game's climactic encounter was unlosable or unwinnable, and neither reviewer could see it alone.**

### 5.2 The finding that reframed everything else

The sharpest observation was not about a defect. It was about the fixes:

> *"The document's fixes conflict with each other more than its findings do."* — player psychologist, Round 2

Three concrete cases: resolving the form space downward for cost destroys the retention layer; adding pressure to the Alpha to kill the kiting exploit converts a survivable ambush into a run-ender; giving grazers a colour to fix their thematic hollowness breaks the colour=class rule the whole game is taught on. Each fix is correct in isolation and damaging in combination — and a solo developer running one agent at a time will apply them one at a time.

That changed how this revision was made. Every change below was checked against the others rather than applied section by section, and the three couplings above were each decided as a **pair**, not as two independent fixes.

### 5.3 Substantive changes

| # | Change | Section | Driven by |
|---|---|---|---|
| 1 | **The form space is re-specified.** Forms are now `family × intensity × rank` — **150 authored forms**, resolved deterministically from a FIFO colour buffer. Buffer state (combinatorial) and form (authored) are now distinct objects | §2.4a, §2.4b | Top issue #1 — all six reviewers |
| 2 | **The slot-fill rule is written down.** FIFO, next slot highlighted on the creature, deliberate eject on Q/B | §2.4a | Top issue #5 — 4 reviewers |
| 3 | **Traits move to the main cubic face**, are fixed once acquired, and are inherited in full. The soft-lock becomes structurally impossible | §2.6a | Top issue #2 — 6 reviewers |
| 3b | **Trait carriers become minibosses**, and permadeath re-prices the traversal layer every run — answering the "one-time checklist" horn | §2.6, §2.6a | Systems Designer F2 |
| 3c | **The litter screen decides your starting buffer** — offspring vary by which colours their limbs are born loaded with | §2.5 | Systems Designer F5 |
| 4 | **The Alpha-wake clock: the biome empties.** Prey and grazers both flee when the Alpha wakes; the 90%-of-gates warning is the window to heal and set your buffer *before* committing, so the fight is prepared-for, never an ambush, and the emptying ground is the price on delay | §2.3, §2.5 | Top issue #3 — the Round 2 collision |
| 5 | **Grazer speed is pinned below the slowest class's dash**, so no form is locked out of healing | §2.3 | player psychologist F4 |
| 6 | **The Alpha cannot be outrun** — its speed does not inherit its colour multiplier | §2.5 | adversarial QA F3 + systems designer's Round 2 derivation |
| 7 | **A pre-trigger warning state** at 90% of both gates, plus a grace period | §2.5 | player psychologist F5 — shipped *with* #4 as a pair, never alone |
| 8 | **The gate table is re-derived** against the real pool: every gate sits 2.3×–5.0× inside it, tightening monotonically | §2.5 | systems designer F1 |
| 9 | **Eat counts cut 200 → 125**, tuned toward the 35–45 min target and validated against the event log rather than an on-paper per-action time budget (that budget table was cut as over-accounting) | §2.5, §4.10 | systems designer F4, business analyst F2b |
| 10 | **The emblem loses its power grant**; panels become the sole build layer | §2.5, §2.8 | narrative critic's third option, against business analyst F3 |
| 11 | **Panels promoted, not cut** — capacity grows with the body (no fixed cap), attach across the cube, no stacking, `panels.json`, named owners | §2.8 | player psychologist's short-interval-reward objection |
| 12 | **Litter width gets one definition**: `2 + (forms this biome − gate)`, capped 5 | §2.5 | systems designer F5, adversarial QA's farming case |
| 13 | **The Bestiary is re-specified** as 30 cells nesting 150 forms via intensity ladders | §2.9 | feasibility lead F3, player psychologist F3 |
| 14 | **A run event log** on every run — the fourth validation gate | §4.10 | Top issue #4 — feasibility lead F1 |
| 15 | **The tuning surface is cut** from ten free thresholds to two coefficients | §4.10 | business analyst's counter-proposal to the bot harness |
| 16 | **Five generator invariants** checked at generation time | §3.3 | adversarial QA F4, business analyst F5 |
| 17 | **Ambient creature rank is stated** (prey = rank−1, elites = rank, Alpha = rank+1) | §3.3 | systems designer F3's "load-bearing unknown" |
| 18 | **A Content & Tone Agent** is added and scheduled in **week 0** | §3 | narrative critic F5, business analyst F1, feasibility lead F3 |
| 19 | **Week 0 added** for data contracts; **loop closes before traits** (5–6 / 7–8 swapped) | §4.8 | feasibility lead's discovery-ordering argument, business analyst F5 |
| 20 | **Art integration is scheduled**, and the regression-safety claim is corrected and bounded | §4.8, §4.10 | feasibility lead F4 |
| 21 | **The cut ladder gets a systems axis** — rank 6, then traits, then biomes | §4.8 | business analyst's Round 2 structural finding |
| 22 | **An audience is named**, and non-AI costs stated | §4.9a | business analyst F4 — the only finding no other reviewer touched |
| 23 | **Coat moved to the foothills**, resolving a possible circular gate | §2.7 | systems designer F2 |
| 24 | **The escalation rule is corrected** to match its own table (0→1→2→1→0) | §2.7 | systems designer F2 |
| 25 | **Run length unified at 35–45 minutes**; "six numbers" corrected to ten | §2.5 | 5 of 6 reviewers |
| 26 | **Intensity moved into the meat.** Wild meat comes in tiers (Pale → Rage) escalating one per biome; Clash is elite/Alpha meat. Corrects this revision's own first attempt, whose count-based intensity truncated low ranks to 138 — the space is now **exactly 150 = 5 × 5 × 6**, Cubivore's own arithmetic | §2.4b, §2.7 | Refinement of Top issue #1 |
| 27 | **Roster 6 → 5 families.** White becomes the empty state — bare limb, hatchling, grazer; Green's "starting body" job passes to the blank hatchling; the apex family is **Grey** | §2.4 | Enables #26 and #28 |
| 28 | **The poop.** Q/B poops the oldest colour out; the limb turns white; eating fills white limbs first. Intentional, legible buffer steering — and the game's tone brief (primal, crude, comedic) in one mechanic | §2.4a, §3 | player psychologist F1; narrative critic F5's missing tone |
| 29 | **Six limbs because six faces.** The body is a cube; each limb claims a face; the rank cap is geometry. A form's claimed sockets are its authored silhouette | §2.4b | feasibility lead's silhouette objection |
| 30 | **The record gate and the milestone ladder.** The Apex answers only ≥100/150 forms across all runs — Cubivore's own final gate — and seven quantified milestones run from 5 forms (inside a losing first run) to 150 (full completion) | §2.5, §2.9a | player psychologist F3 (BLOCKING) |
| 31 | **The re-cut rule.** Mutation preserves your health *fraction*, never the number — the wound stays the same size on screen. Plus **two absorb languages**: prey streams colour into a limb (bar unmoved); grazers dissolve into the body (bar refills) | §2.3, §3 | player psychologist F2 (BLOCKING) |
| 32 | **The difficulty curve is derived, not asserted.** Ambient tiers escalate across biomes and toward each biome's deep end (Cubivore's darkening stages); the player's tier climbs a step ahead via pockets; pounces-to-knockdown holds at **2–3 by construction**, no one-shot threshold is crossed, and escalation arrives as harder chases, not sponges | §2.4b, §2.5, §2.7 | systems designer F3 (MAJOR) |
| 33 | **The premise: an eating ladder, and nothing else.** No lore, no kingdom to save — the fiction *is* the food chain. Biomes run from the soft margins to the heart where the strongest den; grazers carry nothing to take; the Alpha attacks because **a rival is getting big enough to matter**, so the trigger and the motive are the same fact. Deliberately refuses Cubivore's world-restoration wrapper. (A dying-world premise was drafted during revision and cut by the designer as unneeded cosmology) | §1, §2.3, §2.5, §2.7, §4.8 | narrative critic F3 + F5 (MAJOR) |
| 34 | **The numbers were re-stress-tested — and did not all pass.** A fresh, isolated systems-designer reviewer (same method that broke the draft) recomputed the entire numeric spine and returned 2 BLOCKING, 5 MAJOR, 5 MINOR. Every one is resolved in rows 35–37 below. The dilution ladder's "two summits" clarification (Clash beside Rage) and the linear tier percentages / lowest-link rule survived the pass intact | §2.4b, §5.4 | Numeric-spine review |
| 35 | **Rank six is now played — the Ascension.** The draft (and this revision, until now) let the fifth Alpha grant a sixth limb *and* end the run, so 25 authored rank-6 forms were permanently unreachable (a hard Bestiary ceiling of 130/150). Now: **Alphas are same-rank mirror-matches at Clash intensity**, beating the Volcanic Alpha + breeding to six is a **Conquest** that always opens the rank-6 **Ascension** (all 25 top forms huntable); the **Apex** sits dormant there and wakes at ≥100/150 forms as the true ending | §1, §2.5, §2.9a, §4.8 | numeric-spine B1 (BLOCKING); user direction |
| 36 | **The tuning formula is fixed.** `round(a × pool)` could not produce gates 9 and 11 from a shared pool of 25; the gate is now linear in biome depth (`f0 + f_step×(biome−1)`), four coefficients total, reproducing the table exactly | §4.10 | numeric-spine B2 (BLOCKING) |
| 37 | **The Alpha-wake clock reworked to fleeing, not freezing.** Prey and grazers both flee when the Alpha wakes; the 90% warning is the heal-and-prepare window, so the fight is committed-to rather than ambushed, and the emptying ground is the price on delay | §2.5 | designer revision of change #4 |
| 38 | **Panels uncapped.** The flat 3-slot limit becomes a capacity that grows with the body as you breed up; panels attach across the cube's faces; an ascended beast is visibly studded with earned powers | §2.8 | designer note |
| 39 | **Gamepad is first-class.** Every verb is bound on both keyboard-and-mouse and gamepad, stated at §2.1 and §4.1 | §2.1, §4.1 | designer note |
| 40 | **Body construction made vague-by-design.** The cube's six faces cap rank at six, but *how* up-to-six limb-segments attach and combine into a silhouette is handed to the Creature Art & VFX Agent; the design fixes only the count and the read | §2.4b | designer note |
| 37 | **Arithmetic and edge-case corrections.** TTK worked example recomputed (212.5 / 343.75, not 233 / 336); the "2–3 pounces" claim re-scoped to *appropriate targets* (a low-damage hunter vs a tank is a deliberate 4–5 slog); stale combinatorial prose replaced (rank opens a new 25-form column, it does not widen the pool); newborn family tie-break defined (fixed precedence); grazer dash baseline made computable (Speed × dash-mult = 9.6); prey rank floored at 1; palette invariant set to keep slack ≥1.5×; litter "+4" → "+3"; revision-log slack figure corrected to 2.3×–5.0× | §2.3, §2.4b, §2.5, §3.3 | numeric-spine M1–M5, m1–m4 |

### 5.4 Where the fix came from outside the review

The board diagnosed the form-space contradiction precisely and could not agree on a repair — three reviewers pushed for the cheap branch (36 cells) and two argued it would delete the game's meta-progression and falsify its thesis. The systems designer noted a band nobody had explored: *"a colour-pair or dominant-plus-accent model gives ~15–30 per rank… but the document has not gone looking for it."*

**That band is how the original *Cubivore* solved it in 2002.** Its 150 forms are 5 families × 5 intensities × 6 limb counts, with forms matched by recipe from a FIFO colour buffer — meaning the buffer stays combinatorial and expressive while the named form set stays small, authored, and legible. The third axis is what the draft was missing.

This is worth stating plainly as a limitation of the method: **six agents with only the GDD in front of them could not reach the answer, because the answer was in a reference document they were not given.** They were right that the contradiction was blocking, right that both proposed branches were damaging, and right about *why* each was damaging — which is exactly what made the reference solution recognisable when it was checked. The review did not produce the fix. It made the fix findable.

### 5.5 Recommendations declined, and why

Recording these matters as much as the accepted ones — a review is not a checklist, and several correct diagnoses had prescriptions that would have cost more than the defect.

| Declined | Argued by | Why |
|---|---|---|
| **Cut decorated panels** | business analyst (hardened to "cut" in Round 2), adversarial QA | player psychologist's counter held: panels are the *only* short-interval reward in a 40-minute run. Cut the emblem's power instead — which also fixes the "sword in a chest" theme problem the narrative critic raised |
| **Give grazers a colour** | narrative critic F4 | player psychologist's objection held: colour is the game's grammar, and spending it on the word *except* teaches that colour doesn't reliably mean anything. Limbless silhouettes solve the same problem outside the colour system |
| **Build a scripted bot / headless harness** | feasibility lead F1 | business analyst was right that it is a second product built against an unfinished combat spec. The event log gets most of the value for a few hours of work |
| **Procedural form-name generation** | business analyst F1 (option a) | narrative critic was right that it violates §4.5's authored-text promise and strips the game's only voice. At 150 forms the authoring cost is affordable, which is what makes declining this possible |
| **Resolve the form space downward to 36** | feasibility lead, business analyst, systems designer's arithmetic | Cheapest, and it would have made §1's thesis definitionally false while leaving ~30 reachable Bestiary cells. Rejected in favour of the three-axis model, which satisfies all three legs of the trilemma |
| **A second Bestiary currency** | player psychologist F3 | business analyst was right that it patches a cliff whose depth was determined by the unresolved form-space question. With 150 forms, a milestone ladder and the record gate (§2.9a), the cliff is closed; re-measure before adding a system |
| **Losable rank** | narrative critic F2 | feasibility lead was right that it breaks the rank-indexed Bestiary, the save format and the Alpha ladder. The theme is carried by the intensity axis instead, which is orthogonal to rank and already free |
| **Restore the hunger clock** | business analyst | The right instinct — check whether the design already had the system — but the emptying-biome clock prices time diegetically, without a second resource bar the player has to watch |

### 5.6 What remains unresolved

Stated rather than hidden, because the board did not settle them and neither does this revision:

- **Whether 150 forms is the right size.** It satisfies every constraint the review identified, but no one has played it. The event log (§4.10) is what will answer this, and the form model is deliberately data-driven so the answer is a `forms.json` change rather than a re-architecture.
- **Whether the Pro plan's weekly cap supports the schedule.** The feasibility lead's strongest unanswered point: §4.4 names the usage window as the binding constraint and then never tests the plan's own ~675K tokens/hour requirement against it. Week 0 and weeks 1–2 will measure it, and the cut ladder (§4.8) is what absorbs the answer.
- **Whether "no tutorial" survives contact with a real player.** The audience is now named (§4.9a), which makes the claim falsifiable. It has not been falsified yet.

