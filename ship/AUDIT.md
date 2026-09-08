# Morphivore — pipeline audit and cost analysis

Five agent pipelines built the content, the code and the last mile of a Unity game.
Everything below is measured from the runs that shipped, not estimated.

## What the pipeline is

| # | Pipeline | Pattern | Output, and where it lands in the game |
|---|---|---|---|
| 3 | Bestiary crew | CrewAI, 4 agents | `forms.json` — 150 forms; every mutation the player resolves to |
| 4 | World content | RAG + 8-way parallel + severity-thresholded critic | `creatures.json`, `biomes.json`, `panels.json` — 60 creatures, 5 biomes |
| 5 | Coding agent | Goal-oriented: scope → inventory → gap → prioritise → build | Wrote `ColourBuffer.cs` and the identity model into the game |
| 6 | Emblem GER | Generate → Evaluate → Refine + circuit breaker | `emblems.json` — 25 emblems, the last file in the §3.3 contract |
| 7 | Style guide | GER scoring 1–10 against the game's voice | Found drift in all three shipped corpora |
| — | `ship.py` | Deterministic, no model | Agent output → deployed content → headless WebGL build |

The engine integration is the point: no file above is a report. `ContentDatabase` loads all
five at boot, and a bad file is a warning plus a fallback, never a crash.

## What it cost

Claude Opus 5 throughout, at $5/M input and $25/M output; cache writes 1.25×, reads 0.1×.

| Pipeline | Input | Cache read | Output | Cost |
|---|---:|---:|---:|---:|
| #5 coding agent — analysis | 81,988 | 269,544 | 100,251 | $3.09 |
| **#5 coding agent — build loop** | **2,883,319** | **0** | **111,060** | **$17.19** |
| #6 emblem GER (3 runs) | 49,991 | 79,560 | 61,890 | $1.86 |
| #7 style guide (5 runs) | 511,815 | 1,149,101 | 636,092 | $19.03 |
| **Total measured** | **3,527,113** | **1,498,205** | **909,293** | **$41.17** |

**The most expensive step is the #5 build loop: $17.19, 42% of all spend.** The cause is
visible in its own row — **2,883,319 input tokens with zero cache reads.** The loop re-sent
the scoped GDD, the code inventory and the accumulated diff on every iteration, uncached.
The analysis phase of the *same* pipeline, which did cache, cost $3.09 for comparable work.

Caching saved **$6.74** across the runs that used it — 1,498,205 cache-read tokens billed at
10% instead of 100%. Applying it to the build loop would plausibly have removed most of a
$17 line item, making it the single highest-leverage change available.

## The honest gaps

**Assignments #3 and #4 have no cost instrumentation at all.** Token accounting lives in
`common.py`, which #5, #6 and #7 share and the two CrewAI pipelines predate. So the $41.17
above covers three of five pipelines, and the two that authored the *majority of the shipped
content* — 150 forms, 60 creatures, 5 biomes, 15 panels — can only be guessed at. That is
the finding I would act on first: **instrument before optimising**, because the pipelines I
can measure are not necessarily the ones worth tuning.

**Estimation was unreliable where measurement was absent.** #7 was quoted at $7–9 and cost
$19.03. The error was structural, not arithmetic: the estimate priced one evaluation per
record and ignored that a failing record triggers a rewrite *and* a re-score, so cost scales
with the failure rate — which is exactly the thing a style audit cannot know in advance.

**Four runtime bugs survived every pipeline and were caught only by running the thing.**
None was an agent error. All four were integration assumptions no pipeline was asked to
check — a generated-content pipeline validates its *data*, and nothing was validating the
*engine's behaviour* on that data.

| Defect | Why nothing caught it |
|---|---|
| The Alpha could not be damaged | A tier rule in the combat code contradicted the GDD the content was authored from. The data was right; the code disagreed with it. |
| A third of the terrain never drew | Flat shading emitted 83,544 vertices past Unity's 65,535 16-bit index ceiling. Fails **silently** — no exception, no console error. |
| Terrain generation used OS threads | WebGL has none. The editor has them, so the editor could never show it. |
| Every creature rendered magenta | `CreatePrimitive` inherits a Built-in-pipeline material the editor tolerates and a URP **build** strips. |

**The last three share a property worth naming: the editor cannot show them.** They are
visible only in a player build, which is the actual deliverable and the last artefact anyone
looks at. Two of the three fail with no error at all — the terrain simply stops being drawn
and the ground stays solid underfoot, which reads as a level-design mistake rather than a
renderer one. This is the strongest argument in this audit for build-time smoke tests: the
gap is not between "content is correct" and "content is wrong", it is between "runs in the
editor" and "runs where the player is".

## What I would change architecturally

1. **Cache the build loop's context.** One `cache_control` marker on the static prefix —
   scoped GDD plus code inventory — addresses 42% of total spend.
2. **Put cost accounting in the shared layer, not per-pipeline.** `common.py` was written
   for #5 and adopted by #6 and #7; #3 and #4 never got it. Accounting should have been a
   property of the client, so every pipeline gets it by existing.
3. **Add a smoke-test stage to `ship.py`.** It verifies the content in the build is the
   content the agents produced, by hash. It does not verify the build *runs*. Every defect
   in the table above is cheaply assertable — terrain vertex count under 65,535, no material
   left on the default shader, the Alpha's health reachable by the player's damage at that
   rank, `System.Threading` absent from shipping assemblies — and three of the four are
   static checks that need no runtime at all. This is the single change that would have
   saved the most time on this assignment, by a wide margin.
4. **Keep the deterministic last mile deterministic.** `ship.py` uses no model, and that is
   deliberate: reproducibility is worth more than flexibility at the point where content
   becomes a build. Nothing in the shipped game calls a model at runtime — creature AI is a
   hand-written state machine and biomes come from a seeded generator, so runtime token cost
   is **zero** and the same seed always produces the same world.

## Provenance

Every deployed file is hashed into `build-provenance.json`, which ships inside the build and
names the pipeline that authored each one. The claim "this content came out of the pipeline"
is therefore checkable by a stranger rather than asserted here.
