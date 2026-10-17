# CORE GENESIS — EVOLUTION ZERO

**The AI Team That Rewrites How It Thinks.**

A bounded research platform for the Recursive Agents Hackathon's **Version N+1** track. NVIDIA Nemotron, hosted by Crusoe Managed Inference, designs competing agent teams and compiles their repair procedures. A separate deterministic evaluator decides which team survives.

V2 evolves executable team structure: worker specialization, tool permissions, coordination, review policy, instructions and verified procedural memory. It runs up to **three evolutionary rounds with two competing mutations per round**, preserving real ancestry and every rejected candidate. The original working Crusoe integration and V0 evidence remain in the repository.

## Run locally

Python 3.9+. Zero third-party runtime dependencies.

    git clone https://github.com/vincentleg/core-genesis.git
    cd core-genesis
    cp .env.example .env
    # Set CRUSOE_API_KEY in .env using existing credits.
    python3 -m core_genesis.server --fresh

Open **http://127.0.0.1:8080**. Recorded evidence is the default. Enter an incident-remediation objective, choose one to three rounds, and explicitly start LIVE EVOLUTION to authorize inference.

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

Architect, Executor, Observer and Scientist are logical stages using the real pinned model. Observer and Scientist share one request to conserve credits. Nemotron compiles procedures once; the local runtime then executes them against every benchmark instance. Local tool calls and deterministic verification are explicitly distinguished from remote model activity in the Arena. The fixed controller can review and commit but cannot acquire tools or write repairs.

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

The current network-disabled suite contains **46 passing tests**. Chrome checks cover graph/inspector interaction, real tool traces, captured reasoning, mobile layout and zero inference from read-only activity.

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
