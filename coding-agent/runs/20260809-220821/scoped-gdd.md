## 1. Executive Summary

**Morphivore** is a single-player, top-down 3D **action roguelite** where you play a small cube-beast that survives by eating other beasts — and becoming them. Everything you eat rewrites your body: the colour of the meat you swallow decides what kind of predator you turn into, and the traits you absorb decide where in the world you can physically survive.

A run is a push through procedurally generated biomes. Eating is everything: how you mutate, how you heal, and how you earn the traits you need to reach terrain that would otherwise kill you — fins to cross water, claws to climb, a coat for the cold. Each colour is a **trade, not an upgrade** (a Yellow Brawler carries a long bar and moves like a boulder; a Red Leaper is the fastest thing alive and dies to two mistakes), and the meat that *changes* you is not the meat that *heals* you. Eat enough, and widely enough, and the biome's **Alpha** — the champion of whatever colour you preyed on most, **your equal in rank** — comes to hunt you. Beat it and you breed, continuing as one offspring from a litter, a limb larger. Conquer all five territories, grow to six limbs, and — if your bloodline has explored enough of the world's forms — the **Apex** answers. Die and you lose all of it; every run starts again as a one-limb cube.

The fantasy is *becoming the food chain*, not climbing it. You do not find a sword in a chest — you see a creature that can do something you cannot, and you eat it.

### The world: an eating ladder, all the way up

There is no kingdom to save, but there is a world to rule: **one ecosystem, five territories deep,** running from soft margins where weak Pale meat grazes in the open to the heart of the wild where the meat runs Rage — **the strongest things hold the richest ground.** (Morphivore refuses Cubivore's world-restoration wrapper; you are not saving anything, you are trying to sit on top.)

### What you are: a bloodline, not a creature

**A run is one bloodline, and you are the whole of it.** You begin as a one-limb cube; when you beat an Alpha and breed, you do not level up — **you continue as the offspring you choose,** one limb larger, and everything the parent earned (traits, emblems, panels) is **bred true.** When Health hits zero **the line ends.** Eating changes what you *are*; **only breeding changes how big you are.** The **Bestiary** outlives the line — the fossil record of every form any bloodline has ever taken, across every run — and it is the real goal: which combination of colour, intensity and rank can conquer this world.

| | |
|---|---|
| **Genre** | Top-down action roguelite — permadeath, procedural runs |
| **Inspiration** | *Cubivore: Survival of the Fittest* (GameCube, 2002) for mutation; *The Binding of Isaac* for run structure |
| **Platform** | PC (Unity 6, URP). Keyboard + mouse and gamepad, both first-class |
| **Players / session** | Single-player · ~35–45 minutes per run (five biomes) |
| **Rank** | Limbs (1 → 6). Gained only by breeding a new generation — never by eating |
| **Win / end** | **Conquest** (per run): beat all five biome Alphas and breed to six limbs. **True ending:** in the rank-6 Ascension, beat the **Apex**, which wakes only once your Bestiary holds **≥100 of 150 forms across all runs** |
| **Loss** | **Health** reaches zero. The line ends; the next run begins with a new one-limb cube |
| **Persistence** | The **Bestiary** — every distinct form any bloodline has ever taken, across all runs, plus every emblem claimed |

---

## 2. Game Mechanics

### 2.1 What the player does, second to second

You steer with **WASD** or the **left stick**; your beast faces the direction it moves. Combat is a three-beat rhythm:

1. **Lock on.** Hold **right-click** / **left trigger** to lock the nearest creature in your facing cone (a red ring snaps over it); lock range grows as you evolve.
2. **Pounce.** **Left-click** / **A** launches at it — no charge meter, just *when* to leap. Pouncing a standing creature drains its **Health** and **bounces you back** (bodies are solid).
3. **Knock down, then eat.** At zero Health a creature collapses **dizzy** (squashed, spinning) rather than dying. Pounce it *again* while down to **eat** it; leave it too long and it rises at half health.

**Space** / **right trigger** dashes; **Q** / **B** poops your oldest colour (§2.4a). You cannot walk through creatures or obstacles. (Full control map, §4.1.)

### 2.2 Being hunted (the same rules apply to you)

Creatures your size or larger hunt you the same way. When something locks you a **pulsing orange halo** warns you: **smaller attackers stand still to wind up** (a punishable telegraph), **bigger ones keep closing while locked.** The pounce direction commits at the end of the wind-up, so moving away, pouncing away, or hitting them during it defeats it; running far breaks the lock. Smaller creatures flee, and damaged creatures show a floating health bar.

### 2.3 Health — the bar you chose, and how you refill it

You have **one** meter: **Health**; at zero you die and the run ends permanently. Health is a property of your current **form:** limbs set how much animal you are, colour how it is spent. Mutating re-cuts the bar and **preserves your wound, not your number** (you keep the same *fraction*); it never heals or costs a point.

**Grazers refill it.** Harmless, **no-colour, limbless white** herbivores scattered thinly across every biome; they never fight and bolt the instant you lock them. Eat one to recover a chunk of **current** Health — a grazer heals but cannot change you (nothing to take). Grazer flee speed is pinned in `creatures.json` **below every form's dash speed** (Speed × family Dash multiplier), so no form is ever locked out of healing.

**Hunting does not heal you.** Coloured prey drives mutation, Alpha progress and litter width, nothing for your wounds; the two meals even look different (prey **streams into a limb,** a grazer **dissolves into the body**). **Grazers don't count toward the Alpha's eat-count.**

### 2.4 Mutation — you are what you eat

Every coloured creature belongs to one of **five families**, each a **playstyle**. Colour does not make you stronger — it decides *what you are strong at* and what you gave up. The multipliers below are each family's **full (Rage) expression;** lower intensities express a fraction of the same trade:

| Family | Class | Health | Speed | Damage | Reach | Dash | The trade |
|---|---|---|---|---|---|---|---|
| Yellow | **Brawler** | **1.5** | 0.85 | **1.5** | 0.9 | 0.8 | Longest bar, hardest hits, slowest |
| Red | **Leaper** | 0.8 | **1.3** | 0.7 | 1.0 | **1.6** | Fastest, best dash, weakest bite |
| Blue | **Sniper** | 0.9 | 1.0 | 1.0 | **1.7** | 1.0 | Strikes from range; fragile close |
| Purple | **Stalker** | 0.9 | 1.15 | 0.95 | 1.2 | 1.2 | Quick, slippery; hit-and-run |
| Grey | **Apex** | 1.3 | 1.2 | 1.3 | 1.15 | 1.3 | Strong at everything; rarest meat |

**Intensity scales the trade.** A form expresses a fraction of its family's distance from 1.0 on every axis: **Pale 25% · Dusk 50% · Deep 75% · Clash ~90% plus a minor second-tone gift · Rage 100%.** (The Clash gift is specified per form in `forms.json`.)

**The blank is form zero:** the hatchling is a **white cube with one bare limb,** multiplier 1.0 on every axis — not in the 150. **White is the empty state,** and your first meal is your first identity. Because Health is one of those columns, there is no strictly-best colour.

**Limbs set the baseline, colour multiplies it.**

| Limbs | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Health | 100 | 150 | 200 | 250 | 300 | 350 |
| Damage | 40 | 55 | 70 | 85 | 100 | 115 |
| Speed | 12 | 13 | 14 | 15 | 16 | 17 |
| Reach | 16 | 19 | 22 | 25 | 28 | 31 |

Health climbs steepest (a new limb reads first as **durability**), speed gently — so rank dominates *within* a colour, but **across** colours a specialised small beast can still beat a fragile big one on one axis.

### 2.4a The colour buffer — the rule you execute every ten seconds

Each of your **limbs holds one colour;** together they are your **colour buffer,** managed all run on three rules:

1. **Eating fills a white limb first;** if none is white, the meal **evicts your oldest colour** — the buffer is strictly **FIFO**.
2. **Q / B poops the oldest colour out** and that limb turns **white.**
3. **Together they steer:** poop until the limb you want is bare, then hunt the colour you want into it — costing time and meals, never hidden rules.

**The next slot to be overwritten always pulses on your body,** so you never lose a colour unknowingly. What you don't control is the menu: §2.7's per-run palette roll decides what is alive near you — **the forcing comes from the world, not hidden rules.**

### 2.4b Forms — the 150, and the meat that makes them

Your **buffer state** (colours in limbs) is volatile; a **form** is a named, statted creature in the Bestiary — exactly **150,** hand-authored. **Meat carries intensity:** a creature is a **tier** of a colour, and its meat carries that tier into your limb:

| Tier | Where it lives | Expresses |
|---|---|---|
| **Pale** | Wanders everywhere, every biome | 25% |
| **Dusk** | Debuts in Prairies **pockets**; wanders from the Wetlands on | 50% |
| **Deep** | Debuts in Wetlands **pockets**; wanders from the Mountains on | 75% |
| **Clash** | **Elites, trait minibosses and Alphas only** — two-toned, never wandering | ~90% + second-tone gift |
| **Rage** | Debuts in Mountains **pockets**; wanders deep ends of Beach and Volcanic | 100% |

Each tier debuts guarded, one biome before it roams free, so the world darkens as you go. **A form is a family × an intensity × your rank: 5 × 5 × 6 = 150** (exactly Cubivore's). **Every buffer state resolves to exactly one form** — no recipes, no invalid states:

- **Family** = the colour holding the most limbs; ties break toward the **most recently eaten** (at birth, a fixed precedence Yellow → Red → Blue → Purple → Grey, so every litter-mate resolves to a definite form).
- **Intensity** = the **lowest tier among your family-colour units, stepped down one rung for every limb *not* carrying the family** (the "lowest-link" rule), floored at Pale.
- **The dilution ladder is the four wild tiers** (Pale, Dusk, Deep, Rage); **Clash sits beside Rage,** a parallel summit reached only by holding Clash units; diluting either slides it to **Deep.** Holding any Clash unit wins the tie for Clash.
- **All limbs white** = the blank (form zero).

You mutate the instant the resolution changes. **Your weakest meat sets your intensity,** so climbing to Rage means pooping out every weak unit for a strong one — full-body commitment, meal by meal.

**Why six limbs:** the body is a **cube with six faces to grow from,** so a form spans up to six limb-segments in an authored body plan — **the socket layout is the authored silhouette,** and 150 distinguishable bodies come from one procedural system (silhouette reads family, segment count rank, saturation tier). Traits render on the cube's own face (§2.6a). The per-run roll (§2.7) can spawn an **over-tier pocket** (a Rage hollow in the Prairies), so every rung is reachable across enough runs. **Intensity is orthogonal to rank** — a 2-limb Rage Brawler and a 5-limb Pale Brawler are both Yellow but play nothing alike.

### 2.5 Rank — the Alpha challenge and breeding

Eating changes *what* you are, never *how big.* You begin every run as a **blank white one-limb cube.** Every biome contains one **Alpha lair** — a landmark you see on arrival — sitting empty until you have been both *varied* and *busy* in that biome:

| Biome | Rank | Reachable forms | Distinct required | Slack | Prey eaten |
|---|---|---|---|---|---|
| Prairies | 1 | 15 *(Pale, Dusk + Clash elites)* | 3 | 5.0× | 15 |
| Wetlands | 2 | 20 *(+ Deep)* | 5 | 4.0× | 20 |
| Mountains | 3 | 25 *(+ Rage — full ladder)* | 7 | 3.6× | 25 |
| Beach | 4 | 25 | 9 | 2.8× | 30 |
| Volcanic | 5 | 25 | 11 | 2.3× | 35 |
| **Ascension** | **6** | 25 *(rank-6 row)* | *Apex is record-gated* | — | *see below* |

Ranks 1–5 are the five **biomes;** **rank six is not a biome** but the finale. **Slack** (*reachable ÷ required*) tightens biome by biome; because the roll need not field all five families, the `min_distinct_colours` invariant (§3.3) keeps worst-case slack above **~1.5×. Both gates must be met** — forms alone reward surgical meals, an eat-count alone is a grind timer. The ten numbers are **QA tuning targets.**

**The eleventh number — the record gate.** Breeding to six limbs wins the *run* (a **Conquest**); the **Apex fight** beyond it is gated on **≥100/150 forms across all runs** (Cubivore's final gate), and since ranks 1–5 hold 125 forms, ≥100 is reachable before the top row. A knockdown takes **2–3 pounces** against appropriate targets, more if mismatched; **no one-shot is ever crossed** (your damage < every prey bar at every rank).

**Who comes for you.** The Alpha is the **champion of the colour you ate most,** at **your own rank — a mirror-match** — always at **Clash** intensity, and **you cannot outrun it** (its speed ignores the colour multiplier, running flat just above the fastest player form at that rank). At **90% of both gates** the lair stirs; when the Alpha wakes the biome **empties** (prey and grazers bolt with the healing supply), so pick your last meals *before* committing — there is **no topping up** while it **hunts you across the biome.**

**The emblem.** Knock the Alpha down and eat it for its **emblem:** it **opens the way** to the next biome and **enables breeding** — a **trophy off a defeated rival,** granting no power of its own (powers come from panels).

**Breeding.** You pick from a **litter,** each offspring **one limb larger;** you **continue as it,** and everything the parent earned is **bred true** (§2.6a):

> litter size = 2 + (distinct forms this biome − the biome's form gate), capped at 5

So a bare clear gets two offspring, three past it caps at five. Offspring share the rank and inherit all traits, emblems and panels; what varies is **which colours their limbs are born loaded with** (newborn meat is always **Pale**) — **committed** (monochrome, an intensity in hand) or **flexible** (mixed). **The ones you didn't pick** appear in the Bestiary as known targets. Limbs cap at **six.** Each new limb opens a **new** 25-form column; because the gate climbs (3→5→7→9→11) against a flat 25-form pool, litter-width headroom tightens with rank.

### The Ascension — where rank six is played

Breeding to **six limbs** is a **Conquest** — the run's win — and opens the **Ascension:** the six-limb creature is playable at last, in the Apex's domain, the only place the **25 rank-6 forms** exist. **This domain is always open** to a six-limb bloodline (NOT record-gated); it is where you hunt the rarest forms. **The Apex** — a **rank-6 Clash** creature, your final mirror — sits **dormant** there and **wakes only at ≥100/150 forms** across all runs; beating it is the **true ending** above the Conquest. A line short of the record still Conquers and ascends, banking its top-row forms for the next line. **150 authored, 150 reachable.**

### 2.6 Traits and terrain gates

Four creatures carry a **trait** in their meat; eating them is the only way to get it. Each is a **miniboss** — a territorial elite, several times tougher than ordinary prey, that fights back and doesn't flee:

| Trait | Carrier | Grants | Renders as |
|---|---|---|---|
| **Fins** | Pond-dweller, in deep marsh hollows | Enter water without drowning | Gill slits in the main face |
| **Claws** | Crag-holder, on rocky outcrops | Climb high ground | Hooked ridges along the face edge |
| **Coat** | Shaggy grazer-hunter, in the Mountains **foothills** | Survive freezing peaks | A matted shell over the face |
| **Heat** | Vent-dweller, at volcanic seams | Cross lava fields | A scorched, glowing seam across the face |

Taking a trait is a set-piece fight, usually while the pocket's other occupants converge — four such fights per run. Traits are the game's keys, always visible as terrain you can *see* but not yet enter.

### 2.6a Where traits live, and what survives what

**Traits are body, not limbs:** a trait renders on the **main cubic face,** so limbs stay free for colour while the face drives traversal. **Once acquired, a trait is fixed** — nothing in the run removes it (not mutation, breeding, or the parent's death).

| | **On mutation** | **On breeding** |
|---|---|---|
| **Limb colours** | Rewritten — this *is* the mutation | Set to the offspring's own starting buffer (§2.5) |
| **Traits** | **Survive** (on the face, not the limbs) | **Inherited in full** — every offspring carries every trait you hold |
| **Emblems / panels** | Survive | Carry forward |

So the soft-lock — breed and lose a trait a later biome needs — **cannot occur;** the risk is instead losing a trait fight, or **losing all four at once** on death. **Trait reachability is a generator invariant** (§3.3).

### 2.7 Biomes — escalating traversal complexity

Each biome is procedurally generated and holds one **Alpha lair.** The five run from the ecosystem's soft margins to its heart:

1. **Prairies** — open grassland, **no gates;** where you learn the loop.
2. **Wetlands** — ponds and channels; **Fins** reach roughly half the map.
3. **Mountains** — **Claws** for the peaks *and* a **Coat** for the cold: the first two-trait biome, the difficulty step-up.
4. **Beach** — tidal flats and cliffs; combines **Fins** and **Claws,** and introduces the last trait, **Heat,** at the volcanic vents.
5. **Volcanic** — the finale; lava, sheer rock and flooded caves demand **Fins, Claws, Coat** and **Heat** at once.

The trait-introduction count is **0 → 1 → 2 → 1 → 0.** **Coat carriers live in the Mountains foothills,** below lethal cold, so the trait that survives the peaks is obtainable without first surviving them (a generator invariant, §3.3).

**Common food everywhere, strength out in the perils.** Ordinary creatures wander so you can always find a meal, but the mix darkens with distance from your entrance, and **the Alpha lair sits at the strong end.** Top-tier meat clusters in **defended pockets** (Clash never wanders) that **bite back** with swarming packs and elites, turning the form gate into an **exploration** gate. And **each biome's palette is rolled per run,** so which forms you reach, which colour you eat most, and which Alpha comes all cascade from that roll.

### 2.8 Decorated panels — the run's build layer

**Elite creatures only** drop **decorated meat panels** that bolt onto your body, each granting a power (longer lock range, stronger dash, tougher guard, brief camouflage). **Panels are the run's only power source** (the emblem is a trophy and breeding trigger); an ascended beast visibly *studded* with earned powers is how progress reads in a game with no inventory screen (`panels.json`). **Capacity grows with the body;** panels **attach anywhere across the cube's faces** (not crowding main-face traits), at capacity you shed one, the **same power does not stack,** and they **survive mutation and breeding.** So traits say what you *are* (permanently), panels what you're *carrying* this run.

### 2.9 The Bestiary

The Bestiary is where the meta lives, a single screen: **rows are limb count (1–6), columns are family (5).** A cell is a family at a rank that opens into that family's **intensity ladder** (Pale → Dusk → Deep → Clash → Rage), so 30 cells hold **150 forms** — three axes rendered as two. Reached forms show in full colour with their name; unreached ones as a **dark silhouette.** It also keeps every **emblem** any bloodline ever took, permanently — **the line ends, the record does not.**

Opened from the pause and main menus (discovery survives death); the header shows **discovered / total** and the next milestone. In-run, forms found this run are highlighted with **Alpha-threshold** progress, and **offspring you didn't pick** appear outlined as *known but unachieved.*

### 2.9a The record's milestones — what discovery unlocks

The record pays out on a ladder of deliberately **data-cheap** unlocks:

| Forms | Unlock |
|---|---|
| **5** | **Hatch-choice** — start a run as any *discovered* Pale form, not the blank cube |
| **15** | **Inherited instinct** — begin each run already holding one trait you have earned |
| **35** | Hatch-choice extends to **Dusk** forms |
| **60** | **Litter floor +1** — no litter is ever smaller than three again |
| **100** | **The Apex wakes** — the dormant final boss answers any ascending bloodline; the game becomes winnable |
| **135** | **Ancient skin** — completionist cosmetic (nearly all of ranks 1–5 plus ten rank-six forms) |
| **150** | **The Whole Beast** — every form discovered; unlocks the **Genesis skin** (the newborn's white) and marks the save 100% |

The first rung sits at **5 forms — inside what a losing first run banks before meeting an Alpha** — so even a first death leaves you further along; all thresholds are QA tuning targets.

---

### 3.3 Engine integration — the Unity MCP bridge

AI output becomes running gameplay through a **custom Unity Editor plugin** (`MCPBridge.cs` / `MCPBridgeWindow.cs`) on a local socket — no external network — exposing commands (`write_file`, `refresh_assets`, `play`, `get_components`). Agents write only to `Assets/Scripts/` and `docs/`, never binaries; validation is an asset refresh, then `~/Library/Logs/Unity/Editor.log` grepped for `error CS` (the source of truth — the bridge's own log is unreliable), then Play mode. The bridge is unreachable for **8–13 s** during domain reload, so agents wait and re-ping. Because the scene is built procedurally at runtime, agents only ever write plain text — no binary scene merges — which makes concurrent work safe.

**Content data: JSON, not code.** Procedural generation *consumes* content, and that lives in JSON:

| File | Defines |
|---|---|
| `biomes.json` | Terrain, gating traits, palette weights, **minimum distinct colours in a roll,** population/respawn, pocket count, Alpha roster, the two gate thresholds |
| `creatures.json` | Colour family, **meat tier,** base stats, role (grazer/prey/elite/Alpha), **rank,** **grazer flee speed,** home biomes, which trait its meat carries |
| `forms.json` | The **150 forms** — family, intensity, rank, authored name, socket layout, stat profile (from the intensity-scaling rule, hand-tuned) |
| `panels.json` | Each panel's power/magnitude, which elites drop it, its attachment point |
| `emblems.json` | Which Alpha drops each emblem and which biome it opens (no powers) |

**Ambient rank is stated data:** prey at the player's rank minus one (**floored at 1**), elites at the player's rank, **Alphas at the player's rank** (same-rank mirror-match) always at Clash; the Apex is rank 6, Clash.

**Generator invariants — checked at generation time.** The generator must guarantee, and refuse the seed if it cannot:

1. Every trait gate in a biome has a **reachable carrier** for its trait, outside the terrain that trait unlocks.
2. Every biome's rolled palette contains **enough distinct families to keep the form gate honestly slack.** `min_distinct_colours` keeps the reachable pool at least ~1.5× the gate: **4 families** in Prairies/Wetlands/Mountains, **5 (all)** in Beach and Volcanic. A 3-family Volcanic roll would clear the 11-form gate (3 × 5 = 15) but collapse slack from 2.3× to 1.36×, so it is refused.
3. Every biome's standing population plus respawn can **supply that biome's coloured-prey count** with margin.
4. The rolled palette's plausible most-eaten colour is **present in that biome's Alpha roster.**
5. A trait required by a **later** biome remains obtainable given the player's expected trait set on entry.

A seeded generator only *reproduces* an unwinnable run for debugging; these five checks *prevent* one. Owned by the World Generation Engineer, ratified by the Director.

**Why JSON, not hardcoded C#:** every code change costs the 8–13 s domain reload (§4.2), and balance tuning is the most-repeated task — runtime JSON lets the QA agent retune without a recompile. Each file is schema-checked on load; a malformed or missing file **logs a specific error and falls back to built-in defaults** rather than starting broken.
