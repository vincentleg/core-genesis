# CORE GENESIS — THE COMPANY THAT BUILDS CORE

**CORE is the world we're building. GENESIS is the AI company building it — and learning to run itself better.**

**▶ Watch GENESIS run (one click, verified mission replay): https://core-genesis-living.vercel.app** (append `?run` to autoplay)

**One-minute demo video (68 s, recorded from the live site with `scripts/record_demo.cjs`):** https://core-genesis-living.vercel.app/genesis-demo.webm · also in this repo at [`video/genesis-demo.webm`](video/genesis-demo.webm)

## Final hackathon sprint (Version N+1 track) — what is real

| Claim | Evidence |
|---|---|
| **WATCH GENESIS RUN** — seven-act replay (mission → delegation → build → beta lab → evolution → governance → delivery), ~100 s or 60 s mode, play/pause, restart, skip act, camera follow. Every caption and number is read from recorded evidence; zero inference on the public site. | `web/genesis-run.js`, `public/evidence/*.json` |
| Eight named AI employees (Atlas, Nova, Forge, Sentinel, Echo, Ledger, Pulse, Darwin) are interface names mapped to the recorded backend roles; they move between departments only on replay steps derived from recorded handoffs. Click one for its role, task and recorded events. | `CREW` in `web/genesis-run.js` |
| Mission `mission-20261017-145411-2e83ef`: Research read CORE commit `c016d73` (8 excerpts), 3/3 citation sets verified, CORE Local Solutions prototype built, **7 tests / 0 failures**, 10 Nemotron requests, ~$0.0022. | `mission-evidence/` |
| **Campaign A (CORE Local Solutions): 100/100 synthetic perspectives** (5 from the original mission panel + 95 run in this sprint), 100 distinct outputs, 20 bounded batches. | `public/evidence/product-testing.json` → `audience` |
| **Campaign B (CORE GENESIS): 100/100 synthetic perspectives**, 100 distinct outputs, 20 bounded batches. Each reads a structured description of the site (it does not browse). | `product-testing.json` → `genesis_audience`, `scripts/run_campaigns.py` |
| Real browser tests: CORE Local Solutions **3/3** (earlier run); CORE GENESIS website **4/4** (hero, full replay + deliverable links, testing lab + pipeline, mobile agent profile). | `public/testing/`, `scripts/browser_genesis.cjs` |
| **Closed loop**: GENESIS mobile scenario failed (agent tags overlapped; wrong profile opened) → code fixed → retest **3/4 → 4/4**. Fixed by the Claude Code engineering session, not by a GENESIS runtime agent. | `public/testing/loop/loop.json` |
| **Evolution**: earlier mission `b15161` promoted citation-preflight V1 (**4/6 → 6/6 held-out**). Mission `2e83ef` reused V1; its new candidates scored 6/6 vs 6/6 → **rolled back, no gain**. | `public/evidence/prior-evolution.json`, `company-mission.json` |
| CORE pipeline ends at **PROTOTYPE BUILT — AWAITING CORE INTEGRATION APPROVAL**. The original CORE repo is unmodified. | Topbar → CORE pipeline |

Synthetic perspectives are simulated by one model (NVIDIA Nemotron on Crusoe) in independent contexts — **not real users**. The campaigns cost ~$0.015 estimated, under the project's $2 hard cap.

Reproduce: `python3 scripts/run_campaigns.py` (needs a local `CRUSOE_API_KEY`), `python3 scripts/build_world.py`, `python3 -m http.server 8090 --directory public`, `node scripts/browser_genesis.cjs`.

---

**The AI company that builds itself, runs itself, and gets better.**

The autonomous organization behind **CORE — Creation Of Reborn Earth**.

**Explore the public 3D world: https://core-genesis-living.vercel.app**

A procedural architectural campus is the control surface for a bounded AI organization. The human founder assigns a CORE repository-analysis mission from the CEO Office. Research reads real, commit-pinned public code; Engineering prepares cited priorities; five independent synthetic personas critique the proposal; Growth prepares private drafts for CEO review. A separate reproducible evidence gate evaluates changes to the workflow. The public site is a static, zero-inference replay hosted on the verified Vercel **Hobby** plan. Live reasoning stays local behind the existing budget manager.

This is a bounded operational prototype. The long-term CORE civilization, immersive Earth, collective intelligence, enterprise ecosystem and governance systems are a vision; they are not claimed as implemented here. The independent CORE project and website are untouched.

| Department | Implemented scope |
| --- | --- |
| CEO Office | Real mission assignment, department state, pending decisions, budget visibility, audit and company-wide emergency pause |
| Engineering | Real Nemotron engineering priorities and Markdown deliverable with exact source citations; bounded evidence correction; existing deterministic incident-repair compiler |
| Research | Read-only public GitHub metadata, compact branch head, tree and eight bounded safe file excerpts from `vincentleg/core`; pinned sources and explicit uncertainties |
| Operations | Recorded interdepartmental handoffs, strict source/line/quote verification and existing three-family incident diagnosis |
| Product Testing | Three actual local browser testers with screenshots and errors; separate synthetic audience campaigns up to 100 through explicit five-call batches |
| Growth & PR | Truthful X, Instagram and GitHub draft queue; CEO review for manual export only; no publisher, accounts or audience metrics; LinkedIn excluded |
| Economy | Computed budget/priority simulation, alternatives, sourced price snapshot plus clearly synthetic scenarios, risk and local human-review history; no transaction capability |
| Evolution Lab | Real Nemotron team mutations, fresh validation, regression gates, memory, ancestry, promotion and rollback |
| CORE World | Clearly labeled future gateway explaining the broader CORE mission |

The 3D scene uses locally vendored MIT-licensed Three.js and procedural assets. Agent travel follows actual workflow events; idle bobbing, gardens and architectural motion are decorative ambience. Organization changes follow real promotion records: actual worker composition, tool grants and workflow connections. Replay timing is compressed and explicitly labeled.

Run the world and live engine locally using the instructions below. The prior technical Arena remains available at **http://127.0.0.1:8080/arena**.

Build the strictly static public experience without making any API requests:

    python3 scripts/build_world.py
    python3 -m http.server 8090 --bind 127.0.0.1 --directory public
    node --test tests/economy.test.mjs

Static output contains only explicit client assets and genuine evidence. It includes no Python execution endpoint, API credential, payment integration or deployment of the original CORE website.

A bounded research platform for the Recursive Agents Hackathon's **Version N+1** track. NVIDIA Nemotron, hosted by Crusoe Managed Inference, designs competing agent teams and compiles their repair procedures. A separate deterministic evaluator decides which team survives.

V2 evolves executable team structure: worker specialization, tool permissions, coordination, review policy, instructions and verified procedural memory. It runs up to **three evolutionary rounds with two competing mutations per round**, preserving real ancestry and every rejected candidate. The original working Crusoe integration and V0 evidence remain in the repository.

## Run locally

Python 3.9+. Zero third-party runtime dependencies.

    git clone https://github.com/vincentleg/core-genesis.git
    cd core-genesis
    cp .env.example .env
    # Set CRUSOE_API_KEY in .env using existing credits.
    python3 -m core_genesis.server --fresh

Open **http://127.0.0.1:8080** for the living company. Recorded evidence is the default. Open the CEO Office to explicitly assign a real CORE analysis mission. This uses 9 planned reasoning calls, at most one evidence-correction call, and a hard ceiling of 12 physical attempts including retries. The technical Arena at **/arena** retains the three-mode controls and one-to-three-round selection.

| Mode | Behavior | New external API calls |
| --- | --- | --- |
| LOCAL TEST | Network-disabled deterministic tests of runtime, gates, isolation and budget | 0 |
| RECORDED EVIDENCE | Clearly labeled playback of genuine saved execution records | 0 |
| LIVE EVOLUTION | Real Nemotron reasoning through the centralized Crusoe request budget | Maximum 12 physical attempts across two six-attempt cycles |

Page loads, refresh, polling, archive selection and evidence inspection never call a model. No video is being produced for V2; the existing video and screenshot document the earlier V0 only.

Headless execution:

    python3 scripts/run_evolution.py --fresh --generations 3
    python3 scripts/run_evolution.py --fresh --generations 3 --seed 1729 --objective "Restore service contracts while preserving unrelated settings"
    # Continue the most recent completed verified team and its earned memory:
    python3 scripts/run_evolution.py --generations 3

The optional seed reproduces benchmark instances, not stochastic provider output. Omitting --fresh restores the last completed experiment's active team, including when later candidates were rolled back.


## Working software delivery — First Brick

Give GENESIS the preloaded mission from the campus CEO Office. The supported build scope is deliberately specific: **CORE Local Solutions**, an isolated app where a person submits a local problem and a linked proposed solution, initially pending human review. Unsupported arbitrary development, external actions and CORE modifications are rejected or outside the explicit mission contract.

A genuine completed mission, [`mission-20261017-145411-2e83ef`](mission-evidence/mission-20261017-145411-2e83ef.json), produced the [versioned runnable artifact](artifacts/core-local-solutions/runs/mission-20261017-145411-2e83ef). Research inspected actual immutable CORE source. Engineering used real Nemotron reasoning to select a safe specification; a predefined audited scaffold supplied the executable implementation. **This is configuration-driven generation, not unrestricted autonomous coding.** Operations ran a guarded fixed test process with **seven actual passing tests**, including HTTP startup, problem creation, solution submission, pending review, persistence, input validation and authority checks. A previous failed citation mission is preserved rather than rewritten.

    python3 artifacts/core-local-solutions/app.py --port 8091
    python3 -I artifacts/core-local-solutions/verify.py

Open http://127.0.0.1:8091. The app is also reachable through the company mission's **OPEN PROTOTYPE** action. No new server deployment is needed. Source, build report and proposed integration plan are inspectable. Local review cannot authorize real-world action or change CORE.

The mission used **10 requests, 33,199 reported tokens and $0.00218915 estimated usage**. Active V1 citation preflight ran on its real Research brief. A further mutation produced **no independent gain and was rolled back**; no promotion was forced. The earlier 4/6→6/6 held-out citation-fixture improvement remains separately inspectable.

Product Testing then ran **three actual Chrome contexts**, covering desktop, small-screen/keyboard and unsafe-input/authority cases: **3/3 passed**, with real screenshots, zero JavaScript errors and zero extra model requests. A fresh seven-test regression run passed. No repair was needed; the bounded controller can reproduce failures and attempt one audited-scaffold restoration, then rerun the same browsers and regressions. It cannot repair arbitrary new code.

For browser tooling only:

    npm ci --ignore-scripts
    # Chrome is used when installed; otherwise: npx playwright install chromium

Synthetic audience campaigns support **up to 100**, at most **five independent calls per explicit batch**. The captured campaign has **5/100 completed**, not 100. Its first actual batch used five requests, 8,025 tokens and $0.000489 estimated usage. No automatic continuation, fake customers or invented engagement metrics exist.

The public site provides **VERIFIED EXECUTION REPLAY**, actual source downloads and a separately labeled **browser-only artifact preview** using local browser storage. Python and live inference stay local. The original CORE project is never modified, executed or deployed.

    python3 scripts/verify_mission.py mission-evidence/mission-20261017-145411-2e83ef.json
    python3 scripts/verify_testing.py public/evidence/product-testing.json

See [three-minute demo instructions](docs/FIRST_BRICK_DEMO.md). No new video was produced.

## Earlier company workflow — preserved evidence

Captured mission [`mission-20261017-142256-b15161`](mission-evidence/mission-20261017-142256-b15161.json) analyzed public CORE commit `c016d732faaef495c7facce29b7595e3be2a6f19`. Research and Engineering produced three proposed priorities with **3/3 citation sets verified**. Five synthetic personas evaluated the proposal in separate real model calls. Growth prepared a private approval queue. Nothing was posted, purchased, executed in CORE or written to CORE.

The Scientist proposed two citation-preflight policies. The selected candidate improved deterministic verification accuracy **4/6 → 6/6** on development and independently generated held-out fixtures, without regression; policy V1 was promoted and persists for future Research→Engineering handoffs. This proves better citation preflight on that bounded evaluator, **not** better real-world business outcomes or objectively superior product priorities. Mandatory final verification was strict throughout.

The complete run used **9 physical requests, 15,791 reported tokens and $0.0012187 estimated token cost**. Browser testing exercised actual mission assignment, source-backed deliverable, five-person panel, draft approval boundaries and independent evolution evidence. Earlier partial and failed records were retained locally; unapproved social draft text is withheld from public evidence.

**Important limitation:** exact quotations establish provenance, not semantic correctness. The model made absence claims that require maintainer review against files outside the eight excerpts. The UI labels recommendations as hypotheses; the next-run context now prioritizes implementation/test paths rather than historical data files. No unexecuted test or proposed capability is presented as completed work.

Reproduce the archived evidence checks with **zero external requests**:

    python3 scripts/verify_mission.py mission-evidence/mission-20261017-142256-b15161.json

Private mission records and pending communications are stored under gitignored `company/`. Curated public exports retain real Research, Engineering, persona, usage and mutation evidence while withholding Growth text. See [integration audit](docs/INTEGRATION_AUDIT.md) for the five requested upstream reviews. None is installed or claimed as an operational integration.

## What actually evolves

| Component | Operational effect |
| --- | --- |
| Instructions | Included in Nemotron's actual procedure-compilation context |
| Worker composition | General or latency/capacity/routing specialists with enforced field ownership |
| Tool permissions | Determine which configuration, contract, logs and memory the runtime can retrieve |
| Workflow | Shared evidence, specialist pipelines or memory-first coordination expand into explicit ordered steps |
| Verification policy | Schema, protected-field or contract review before commit; independent final checks are mandatory |
| Evidence cache | Skips repeated retrievals and records actual cache hits |
| Memory | Reference-based rules earned only from passing development executions, with source cases and lineage |
| Procedure source | Compile a new procedure or reuse a genuinely verified three-family memory bank without another compiler request |

Generated procedures are a tiny declarative language: copy, increment or decrement an allowlisted evidence reference into an owned configuration field. Only the initial control may make literal guesses. There is no eval, generated Python, shell, arbitrary file access or production remediation.

Remembered executable rules are development-verified; the accompanying natural-language rationale remains a model hypothesis and is labeled accordingly. The Observer also receives development-only scores, work counts and failures from prior competing designs, so it can avoid repeating inefficient approaches without seeing their held-out results or gate decisions.

Architect, Executor, Observer and Scientist are logical stages using the original pinned Lightning model. New company missions use the verified same-price `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` endpoint; original Crusoe client defaults and experiment identities are preserved. Observer and Scientist share one request to conserve credits. Nemotron compiles procedures once; the local runtime then executes them against every benchmark instance. Local tool calls and deterministic verification are explicitly distinguished from remote model activity in the Arena. The fixed controller can review and commit but cannot acquire tools or write repairs.

## Evolution and independent evaluation

1. Architect interprets the objective and assembles a log-only experimental control team.
2. Executor compiles a bounded procedure; the runtime measures its development failures.
3. Observer analyzes development evidence. Scientist proposes two complete team designs.
4. Executor compiles both proposals in one request, unless verified memory permits compiler-free reuse.
5. Both candidates run on development cases. Selection uses successes, then fewer measured work units, then proposal order.
6. The selected candidate and its parent run on identical fresh validation cases and fixed regression cases.
7. A deterministic gate promotes or rolls back. Earned development memory follows verified ancestry.
8. Repeat for up to three rounds. A separate sealed shard compares the original and final team after mutation decisions are finished.

Each full three-round experiment contains **36 distinct incident instances**: six development, six fixed regression, three fresh six-case validation shards and six sealed cases. Repeated executions of the same instance across teams are separately recorded.

Mutators receive development fixtures, development traces and development-verified lessons only. Fresh validation and sealed instances are never serialized into mutation/compiler prompts. Every real inference record includes its input context, output, model identifier, usage and request metadata for inspection.

Promotion requires strict success-count gains on **both development and fresh validation**, complete identical coverage, and no previously passing case lost in development, validation or regression. Once both teams are fully correct, a candidate can instead win by reducing actual work on both development and validation without regressions. Work units count tool invocations, rule evaluations and apply/review/commit dispatches; they are an interpreter-work proxy, not a claim about billed dollars or statistically significant wall-clock speed.

Invalid designs, unauthorized writes, missing evidence and malformed programs are rejected. A valid sibling can still compete. If both proposals fail validation, the generation rolls back without paying for a compiler call. Three rounds do not imply three promotions.

The benchmark covers latency/retry contracts, database connection capacity and readiness route/listener alignment. Numeric limits and paths vary by instance. This is a narrow in-memory configuration-repair simulator, not a production operator or proof of general software engineering ability. The source is public; held-out isolation concerns prompts and evaluation order, not permanent secrecy. The intentionally restricted control makes its evidence-gathering weakness visible.

## Evolution Arena

The native dark blue/violet interface displays real candidate nodes and parent edges, current activity, per-node mutation diffs, exact teams/workflows, earned memory, tool traces, test assertions and promotion reasons. Generation Battles compare only identical cases actually executed by both selected teams. Invalid candidates display their rejection reason rather than fabricated scores.

All scores, timing, usage and costs derive from execution records. Historical playback is labeled. Failed and rolled-back experiments are retained alongside successful ones; future runs can produce different outcomes.

## Verify without inference

Latest verified V2 milestone: [20261017-123548-c377d6](experiments/20261017-123548-c377d6.json).

| Round | Development, parent → candidate | Fresh validation, parent → candidate | Decision |
| --- | --- | --- | --- |
| G1 | 0/6 → 4/6 | 0/6 → 4/6 | Promote |
| G2 | 4/6 → 5/6 | 4/6 → 5/6 | Promote |
| G3 | 5/6 → 6/6 | 6/6 → 6/6 | Roll back: no strict independent gain |

Final sealed comparison: **0/6 → 4/6**, retaining G2. Seven genuine candidate/control nodes, 132 executions and all three decisions reproduce independently. Nine physical attempts (one retry), 19,924 reported tokens and **$0.0022272 estimated usage plus failed-attempt reserve**. Two development-verified memory lessons were earned. Capacity repair remains a measurable weakness; G3's stronger development result did not bypass the gate.

Subsequent genuine continuation [20261017-123736-61ea83](experiments/20261017-123736-61ea83.json) repaired capacity and earned two additional promotions: **5/6 → 6/6** on development and fresh validation, then **38 → 36 interpreter work units** at unchanged 6/6. Its third proposal was truncated; that original stopped record is preserved without retroactively adding sealed results.

[20261017-124001-ae2c9e](experiments/20261017-124001-ae2c9e.json) independently replayed and restored that verified team, completed three more competitive rounds, and passed **6/6 on a new sealed shard**. The starting team also passed 6/6: this is continued correctness, not a fabricated additional gain. Memory-reuse competitors executed genuine recalled rules and avoided compiler requests, but failed to improve measured work and were rejected. This run used six physical requests, 16,816 reported tokens and an estimated **$0.0012155**. Its 132 executions and three decisions replay independently.

The Arena connects the four accepted mutations across these actual histories, with direct links to their source experiments. Each experiment still shows all competing branches and rejected proposals. Scores from different sealed shards are never treated as identical-task comparisons.

The current network-disabled suite contains **66 passing Python tests**, alongside **five passing deterministic procurement tests**. Chrome checks cover graph/inspector interaction, real tool traces, captured reasoning, 3D department interactions, mission creation, procurement recomputation, recorded organizational transformations, mobile layout and zero inference from read-only activity.

The new Living Company HQ also triggered genuine live experiment [20261017-133419-f6762d](experiments/20261017-133419-f6762d.json): two promotions improved development and fresh validation **0/6 → 4/6 → 6/6**, with no regressions. Crusoe HTTP 429 stopped the third round after the bounded retry. The original record contains **no sealed outcome** and is retained as such. Ten physical attempts, 14,168 reported tokens and $0.00480235 estimated usage plus retained failed-attempt reserves. Independent replay reproduced its 84 executions and two decisions.

Subsequent resilience handling is unit-tested: after a later provider HTTP failure, inference stops and the verified parent completes local sealed evaluation. No additional provider call was made merely to demonstrate this failure path.

    python3 -m unittest discover -s tests -v
    python3 -m core_genesis.local_test
    node --check web/arena.js
    python3 scripts/verify_evidence.py experiments/EXPERIMENT_ID.json

V2 replay regenerates the seeded suite and reexecutes every recorded program, tool trace, work counter, development selection and promotion/rollback gate. Evaluator source hashes must match the producing revision; check out that experiment's commit for older histories. Replay does not repeat inference, authenticate provider provenance or reproduce historical wall-clock latency. Records are ordinary auditable JSON, not tamper-proof storage.

The preserved V0 experiment [20261017-114030-02b57b](experiments/20261017-114030-02b57b.json) achieved 0/6 → 2/6 in six physical requests, 7,061 reported tokens and an estimated $0.0005665. Its fixed six-case protocol differs from V2 and must not be presented as V2's sealed evaluation. New V2 experiments, including unsuccessful runs, live in experiments/.

## Hard budget and safety

- Persistent **$2 project-wide estimated cap** using existing Crusoe credits only. No purchases, top-ups or paid deployments.
- Maximum **six physical attempts per cycle, two cycles per explicit run, one concurrent request and one automatic transient retry**. Retries count and retain reservations after partial failures.
- A typical three-round run plans eight model requests; real verified memory can reduce this. Exhaustion stops the run safely.
- Pinned model: nvidia/Nemotron-3.5-Lightning-30B-A3B. Original core_genesis/crusoe.py is preserved.
- Architect output maximum 350 tokens; other reasoning maximum 1,800. Input messages plus output schema must fit 24KB; conservative token framing is reserved before HTTP.
- Provider-constrained JSON plus independent runtime validation. Empty or invalid output stops safely; no hidden paid correction loop.
- Malformed later-generation JSON records a rollback, stops further inference and finishes local sealed evaluation of the verified parent. Previously earned promotions in an interrupted run can be restored only after independent gate replay succeeds.
- Decimal accounting, cross-process locks and atomic persistent reservations. Reported usage settles estimated costs; missing usage, timeouts and failures retain full reserves.
- Official [Crusoe pricing](https://www.crusoe.ai/cloud/pricing) verified October 17: $0.05/million input and $0.20/million output tokens; cached discounts ignored. Prices expire after 24 hours. Unknown, invalid or expired pricing fails closed.
- Legacy uncertain usage and possible old hidden retries have explicit conservative allowances in the same ledger. Do not delete budget/ledger.json to reset spending.
- One bounded retry waits for provider cooldown up to ten seconds; a longer or unrecognized cooldown stops the run. No automatic background restart.
- Existing credentials remain in gitignored .env/environment and never enter prompts or browser state. The server exposes explicit assets and evidence only.
- Loopback server; mutation endpoints require local Host, same Origin and explicit action headers.
- In-memory deterministic repairs only. No untrusted generated commands, unrestricted self-modification or changes to the separate original CORE project.

Crusoe and NVIDIA Nemotron are genuine operational integrations. You.com access has not been supplied; no retrieved evidence is invented. OpenShell/NemoClaw and Switchyard are not claimed or installed as decorative dependencies.

## Code map

| Path | Purpose |
| --- | --- |
| core_genesis/crusoe.py | Preserved working Crusoe client |
| core_genesis/evolution.py | V2 orchestration, lineage, candidate compilation and memory |
| core_genesis/team.py | Bounded executable team interpreter and objective gate |
| core_genesis/assembly.py, schemas.py | Typed team operators and provider JSON grammars |
| core_genesis/suites.py, benchmark.py | Fresh reproducible shards and deterministic assertions |
| core_genesis/replay.py | Independent V2 evidence replay |
| core_genesis/engine.py | Preserved V0 protocol and shared persistence utilities |
| core_genesis/budget.py, pricing.json, budget/ledger.json | Centralized budget, verified prices and persistent consumption |
| core_genesis/server.py, web/arena.* | Local API and interactive Evolution Arena |
| experiments/, tests/ | Genuine execution evidence and isolated automated checks |

MIT licensed. Developed October 17, 2026 for the Recursive Agents Hackathon organized by Cerebral Valley × Crusoe, with NVIDIA and You.com. Public repository and local application exist; no public deployment is claimed.
