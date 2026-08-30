# Morphivore — Emblem GER Pipeline

**Assignment #6.** A Generate → Evaluate → Refine loop with a circuit breaker, for
**Morphivore**, my capstone game — a creature-eating game where identity is the colours
you have eaten.

It writes `emblems.json`: the one file in my GDD's §3.3 content contract that had never
been written, by hand or by my earlier crews.

```bash
cd agent-crew/ger-emblems
python forge.py                 # run the loop
python forge.py --deploy        # ...and copy a clean result into the game
python forge.py --adversarial   # prove the Evaluator fires
```

---

## Pre-Build Declaration

> **1. What content does my game generate manually, inconsistently, or not at all?**
>
> Emblems. `emblems.json` is the one file in my GDD's §3.3 content contract that has
> never been written — not by hand, not by my Assignment #3 or #4 crews. Twenty-five:
> one per Alpha, five biomes × five family champions.
>
> **2. What specific rule from my GDD must every piece satisfy?**
>
> §2.5: an emblem is *"a trophy off a defeated rival, granting no power of its own
> (powers come from panels)."* The §3.3 contract row for `emblems.json` ends
> *"(no powers)."* An emblem may only open the next biome and enable breeding.
>
> **3. What does a failure look like, concretely?**
>
> An emblem granting an ability or stat — "+15% dash", "aura of dread." It breaks §2.8 —
> panels are the run's only power source — and compounds: emblems are permanent and bred
> true, while panels are shed at capacity. My revision log records removing exactly this.
> A generator reaches for it anyway, because everywhere else "emblem" means relic.

---

## What it generates

Twenty-five emblems, one per Alpha. Each record is exactly what §3.3 specifies and
nothing more — which Alpha dropped it, which biome it opens, a name and a flavour line:

```json
{
  "id": "emblem_beach_purple",
  "alpha_id": "alpha_beach_purple",
  "biome": "beach",
  "opens_biome": "volcanic",
  "name": "Tidepool Fang",
  "flavor": "Hollow, curved, and stinking of low tide; the bite mark it left is still in your shoulder."
}
```

There is deliberately **no field for an effect, stat or magnitude** — not in the JSON, and
not in the C# type that loads it. Content that tried to grant a power would have nowhere
to put it. The rule is enforced by the shape of the data as well as by the Evaluator.

## The rule the Evaluator enforces

Not a generic validity check, and not a constant I typed into the source.
[`contract.py`](contract.py) **retrieves it from the GDD at run time** — reusing the
Assignment #4 crew's `rag.py` unmodified, repointed at the condensed GDD — and every run
logs the passages it actually enforced:

```
- "a trophy off a defeated rival, granting no power of its own (powers come from panels)"
- "Which Alpha drops each emblem and which biome it opens (no powers)"
- "Panels are the run's only power source"

Retrieved from sections: 2.5, 2.5, What the agent stress-test flagged
```

The third hit is the revision-log entry recording that emblems *used* to grant power and
that I removed it — so the rule is identifiable in three separate places in the document.
If a quote ever stops matching the GDD verbatim, the run warns before trusting itself.

## The loop

```
generate ──▶ evaluate ──▶ pass? ──▶ accept
                ▲            │
                │            ▼ fail
             refine ◀── circuit breaker  ──▶ escalate
```

| Component | File | What it does |
|---|---|---|
| **Generator** | [`generator.py`](generator.py) | Authors 25 emblems in one pass over the Alpha roster, in the voice the #3 crew established. Told the rule — as any real pipeline would be. |
| **Evaluator** | [`evaluator.py`](evaluator.py) | Two layers: deterministic checks, then a verifier agent. |
| **Refiner** | [`refiner.py`](refiner.py) | Gets *one* failing check plus the rule, patches only the named field. Three passes, each told what the last one failed to fix. |
| **Circuit Breaker** | [`circuit_breaker.py`](circuit_breaker.py) | Stops the loop and escalates with a problem statement. |
| Loop + CLI | [`forge.py`](forge.py) | Runs it, writes the log, deploys a clean result. |

### Why the Evaluator has two layers

**Code owns structure.** Whether a `power` field exists, whether `alpha_id` names a real
Alpha, whether `opens_biome` follows the Prairies→Wetlands→Mountains→Beach→Volcanic
chain. Objective, repeatable, free.

**The model owns meaning.** *"Wearing it, you feel faster"* has no forbidden field, no
number and no panel vocabulary. It passes every deterministic check and still breaks the
rule, because it *implies* a power.

The split comes from a specific failure in Assignment #4: a keyword check flagged
*"…at its edge rather than the open water"* as a violation, because negation is invisible
to substring matching. Deterministic checks over prose are brittle in exactly one
direction — they see strings, not claims. So strings go to code and claims go to the
verifier.

### The Circuit Breaker trips on four signals, three of them early

A pass limit alone is weak: it waits for three failures even when the first two prove the
loop cannot win.

- **exhausted** — 3 passes used, still failing.
- **regressing** — a check that was passing now fails. The Refiner is re-authoring rather
  than patching, and more passes will keep trading one failure for another.
- **oscillating** — a failure set repeats. The loop is cycling, not converging.
- **unfixable** — the fault is upstream of the record. If `creatures.json` ever asserted
  `emblem_grants_power: true`, no edit to an emblem could satisfy the GDD, because the
  *data contract* would contradict the design.

That last one is the Assignment #4 lesson made mechanical: a finding that keeps coming
back is usually a bug report about your contract, not about the content in front of you.

---

## Did it catch something I would have missed?

**Yes — but not where I expected, and the honest answer is more interesting than the one
I was hoping for.**

### The first run caught nothing

25 emblems, **25 passed on the first evaluation**, 0 refined, 0 escalated, $0.52. Told the
rule clearly, the generator held the line across all 25 records — no power fields, no stat
notation, no implied grants. All 25 verifier calls ran and passed it.

A pipeline whose Evaluator never rejects anything is indistinguishable from a pipeline
with no Evaluator, so this run proved nothing on its own.

### What it did catch was a defect in my own Evaluator

Reading the clean output, the ids were `emblem_beach_bonelord` — the Alpha's **name** —
where the brief I had written specifies `emblem_<biome>_<family>`, i.e.
`emblem_beach_grey`. My `format.id` check was a loose regex (`emblem_[a-z]+_[a-z]+`) that
accepted either.

**The Evaluator was documenting a convention it did not enforce**, which is worse than no
check at all, because it reads as coverage. I added `format.id_matches_alpha`, which
derives the expected id from the Alpha's own family rather than pattern-matching a shape.

On the re-run: **0 passed first evaluation, 25 repaired by the Refiner, 0 escalated**,
$1.07. And it is reproducible — the generator used the Alpha's name in the id on both
runs, ignoring an explicit formatting instruction both times. That is a real failure mode
I would not have found by reading 25 records and nodding at the prose, because the prose
was fine.

### And the adversarial probes proved the loop works

`--adversarial` runs six hand-written violations, one per check, through the same loop.
They are hand-written on purpose: asking a model to "write some bad emblems" tests whether
that model follows instructions, not whether my checks work.

Every check fired. `rule.implies_power` fired **three** times — caught only by the
verifier layer. The Refiner made minimal, targeted fixes:

| Was | Became |
|---|---|
| *"Snapped clean off. Worth +15% dash to anyone who straps it on."* | *"Snapped clean off. Its legs were still kicking when it came loose."* |
| *"Pop it out and your lock range doubles."* | *"Popped out while the other eye was still looking for you."* |
| *"Wear it and you will never tire again."* | *"Chewed through from the inside. Still stinks of the throat it came off."* |

On the two probes whose fault was a **field** rather than the prose — a `grants` key, and
a wrong `opens_biome` — the flavour came back byte-identical. It patched the field and
left the writing alone.

And the Circuit Breaker tripped, correctly, at **pass 1**:

> `emblem_prairies_green` — escalated (**regressing**). Refining introduced
> `voice.not_a_trophy` — a check that was passing before this pass.
>
> Pass 1 — refiner said: *"Pointed alpha_id at the actual prairies Alpha
> (`alpha_prairies`)"* — which does not exist either.
>
> **Failed in every pass:** `world.alpha_exists` — a check this record has never once
> satisfied is more likely a problem with the brief than with the wording.

Asked to fix an emblem for an Alpha that does not exist, the Refiner invented a different
nonexistent Alpha and broke the voice on the way. The breaker caught the regression and
stopped, instead of spending two more passes on an unwinnable record.

---

## It runs in the game

`emblems.json` deploys to `Assets/StreamingAssets/` and is **read at boot**:

```
[Content] loaded 60 creatures, 5 biomes, 150 forms, 25 emblems from StreamingAssets.
```

Compiles clean, no exceptions in Play mode. [`EmblemTable.cs`](https://github.com/eliodeberardinis/morphivore-agent-crew/blob/main/Assets/Scripts/Content/EmblemTable.cs)
and a `ContentDatabase.EmblemFor(alphaId)` lookup were added so the file is actually
consumed — shipping authored content that nothing loads is precisely the defect my
Assignment #5 agent caught in `forms.json`, and it would have been a poor joke to repeat
it in the same project two assignments later.

Full use of emblems — the Alpha drop and the breeding trigger — belongs to the
Alpha/breeding chunk, which is the next piece of work on the build plan.

## Honest notes

- **The generator complied on content, not on format.** Given a clearly stated rule it
  never once tried to grant a power in 50 generated records across two runs. My
  declaration predicted it would "reach for it anyway"; on this evidence, prediction
  wrong. Where it *did* drift was an id convention it was told just as plainly — which is
  a useful reminder that the failure mode you brace for is not always the one you get.
- **The verifier layer is unproven on organic output.** It fired three times on planted
  violations and zero times on 50 real records. It may be genuinely idle here, or it may
  be lenient; one clean corpus cannot distinguish those.
- **Six probes are not a test suite.** They cover each check once, in isolation.
- **Cost:** $0.52 clean run, $1.07 with 25 repairs, $0.27 adversarial. Cheap because the
  rule prefix is cached across all 25 verifier calls.
