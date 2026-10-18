# CORE HQ browser testing

Current execution results are in [the product testing report](CORE_HQ_TESTING_REPORT.md). The initial navigation/pilot-preparation sections below describe the earlier baseline; the expanded product coverage section records the subsequent work. The product pilot has executed, with nine completed sessions, one incomplete attempt and six end-to-end passes.

## Framework decision

Selected: the existing **Playwright 1.64.1** browser library (Apache-2.0), with a bounded local-model decision adapter. No new dependency was required. Playwright is a browser automation framework, not an autonomous reasoning model. The adapter requests decisions from a local Ollama model and executes constrained actions; it does not claim to be the upstream Playwright planner/generator/healer agents.

Official sources checked October 17, 2026:

| Option | Compatibility and evidence | Cost and decision |
| --- | --- | --- |
| [Playwright](https://github.com/microsoft/playwright) and its [agent tooling](https://playwright.dev/docs/test-agents) | Already used in HQ; real Chrome, isolated contexts, DOM/accessibility observations, screenshots. [Tracing](https://playwright.dev/docs/api/class-tracing) captures operations/network; our report separately records task assertions. Exact dependency already pinned. | Reuse selected. Browser execution has no API fee. Existing installation works; this is not a comparative stability benchmark. |
| [Browser Use](https://github.com/browser-use/browser-use) | Purpose-built open-source browser agents; Python Agent and local-model support. Would add a second runtime/browser lifecycle alongside existing Playwright recording. | Consider for broader exploration after pilot. Cloud services and remote model defaults require cost/privacy review. Local execution is possible; not installed or claimed tested here. |

This deliberately small integration reuses the existing browser framework instead of adopting a second browser stack before one real session is verified. Model-directed decisions and scripted regression checks remain separate modes and counts.

## Executable limits

`inspect_core.py`: local Git object reads only; fixed default branch; explicit refs; no fetch/checkout or fallback. Full eligible `src/`, `test/`, `schemas/`, entry files and selected architecture documentation, with a 2 MB per-file limit. Source selection and omissions are explicit. Git tree inventory includes files whose bodies were not inspected. Local dirty status is recorded but working-tree edits are excluded.

`test_core.py`: immutable local static server. No production testing mode exists. Server uses only tracked static-file paths at the selected SHA. Every response includes `X-CORE-Commit`. No POST handler, backend startup, source execution, build command or CORE mutation. Repository JavaScript executes only inside the isolated browser.

`core_browser.cjs`: real Chrome/Chromium; isolated, unauthenticated contexts; blocked external requests and non-GET/HEAD requests; no downloads or service workers. Scripted mode verifies bounded visible UI behaviors. Local-agent mode sends the rendered accessibility snapshot and visible controls to **127.0.0.1:11434 only**, never to Crusoe or a cloud provider. Existing Ollama models only; no downloads. Controls are reobserved after each step; generated shell/JavaScript is never executed. Mutation-like controls are rejected. Each model call records observed state, decision, notes and token counts. Model notes remain AI-generated evaluations, not human testimony or proven UX findings.

Actions have an 8-second timeout; local inference has a 35-second timeout; 12 decisions/model calls maximum; no automatic retries; 170-second decision-loop runtime bound plus a 240-second-per-requested-session process watchdog; serial sessions; stop on failure. Pilot requires explicit command flag plus a successful single-session gate for the same mode, model and commit. Screenshots and traces are retained even after failure when capture succeeds; capture failures are recorded.

## Evidence and interpretation

Private `company/core-browser/<run>/` contains provenance, config, session reports, PNG screenshots, trace ZIPs, model decisions, summary and SHA-256 manifest. The first sandbox-denied attempt may contain only provenance; it is not a browser session. A report's `task_completion` counts executed actions, not human task comprehension. `features` refers to verified checks only. Keyboard input establishes that input was sent, not that map coordinates changed unless an assertion verifies movement.

Offline requests to external tiles are expected to be blocked. These are retained as errors/limitations, not silently discarded. Optional missing local backend state can generate a 404; do not classify it as a production regression without reproduction. Live map imagery, real-location data delivery, live CORE AI dialogue and contribution submission require additional task-specific checks. A navigation session cannot establish that all of CORE works.

Workflow: read → browser test → evidence → local review record → proposed investigation → verify a reviewed change → human approval. `review_core_session.py` creates evidence-linked findings from failed actions/page errors and leaves verification unexecuted. It does not edit CORE, resolve causes automatically or label suggestions as verified improvements.

## Ten-session pilot

[Machine-readable preparation](templates/core-pilot.json). Do not run hundreds. First establish one model-directed session. Then use ten independent browser contexts, alternating desktop/mobile, at the same commit. Current pilot varies viewport, not ten independent human personas or ten parallel model agents. A fuller task matrix (location, recorded agent dialogue, contribution, accessibility and first-time comprehension) is future work. Record completion, coverage, errors, timing and local token counts; do not manufacture costs or participant counts. Paid API cost is zero in the current adapter; electricity/hardware costs are not measured.

A remote-model adapter is not implemented. If required later, obtain separate approval for cost ceiling, endpoint and page-data disclosure; route approved Crusoe calls through the existing `RequestBudget`. No API key or remote source transmission is required for the local adapter.

## Human research

`ingest_human_testing.py` accepts mapped platform exports, not provider credentials. Unique pseudonymous participant rows, actual tasks, evidence and documented consent are required for nonempty studies. Completion rates are computed from performed task rows; duplicate participants/tasks and count mismatches fail. Keep unconsented records outside ingestion. Evidence references and consent authenticity require human review. There is no recruitment, platform account connection, payment or assertion of real participants without an import.

## Verified initial execution

Local CORE branch `v9.2/earth-first`, commit `da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5`. Source inventory: 568 tracked files; 190 full eligible file bodies read. CORE remained clean and was not changed.

| Run (private company/core-browser directory) | Actual result |
| --- | --- |
| `20261018T014740Z-cc61a8` | Initial scripted session: 3/6 actions succeeded. Unclosed panel and ambiguous harness selector; retained. |
| `20261018T014921Z-50067f` | Corrected scripted session: 8/8 actions succeeded, zero model calls, ~22.5 s. Keyboard input sent; coordinate movement not asserted. |
| `20261018T014949Z-6b1503` | First local AI attempt hit the 240 s process timeout while reopening a panel. Partial action screenshots/decisions/usage retained; no finalized trace or successful completion claimed. Ten calls attempted; last in-flight call has no reported token usage. |
| `20261018T015442Z-b09b6f` | Local AI attempt ended with an offscreen skip-link failure and repeated-action stop. Two calls; finalized trace retained. |
| `20261018T015606Z-a96878` | Local AI session completed: 6/6 actions, 5 genuine model decisions, 4 UI milestones verified, 6 screenshots, decision logs and 12.9 MB trace. ~88.8 s process runtime (~86.5 s browser session), 8,397 prompt / 119 output tokens, $0 paid API cost. |

The successful AI agent selected controls from rendered accessibility observations. It entered Earth, selected CORE World, opened Problems & missions, closed the panel and opened Contribute. No contribution was submitted. Screenshots were captured immediately after actions, so some frames may precede a panel animation; the trace and visibility assertions also record the DOM state. Future captures disable finite screenshot animations for clarity.

There were zero page JavaScript exceptions in the successful session. External map requests were deliberately blocked. The optional `/.core-local/civ/state.json` request returned 404 because the immutable static runtime does not serve untracked local backend state. This is an environment limitation, not an established production defect. No live agent dialogue or first-time human comprehension was evaluated. Model notes describe actions, not a validated usability study.

A rough linear ten-session estimate from the successful session is ~15 minutes and ~85,160 local model tokens; this excludes startup variation, mobile differences and failed-session overhead. It is not a measured pilot. No paid API charges are expected with the local-only adapter; hardware/electricity costs are unmeasured. That estimate preceded the subsequently completed pilot recorded below.

## Expanded product coverage (explicit entry paths)

`--suite product --entry room` tests the real CORE team conversation page at `dialogue.html#mission=mission.sf.housing-resilience`; it does not pretend the Earth entry succeeded. The first successful product preflight is `20261018T021120Z-7c5ee8`, nine actions, ~18.5 seconds, zero inference. It checks rendered dated San Francisco findings against actual committed data deliveries, a registry-agent consultation, a question/answer exchange, refusal of an unsupported question, consent enforcement, local mission-queue submission, reload persistence and isolation. The contribution is a labelled synthetic fixture inside an unauthenticated disposable local context. It is not public, a real community submission, or an encrypted-vault test.

`--suite pilot --entry room --mode local-agent --model qwen3:8b --sessions 10 --execute-pilot --smoke-run <verified-smoke-id>` requires a successful product preflight for the same commit and entry. Ten distinct named personas vary objectives; the current direct room remains the same housing/resilience mission. The local model reads real rendered accessibility observations, selects a task tool and provides the question/fixture text. Browser actions within that tool are deterministic and recorded. A second local call evaluates what the interface actually displayed; quoted UX concerns are checked against the observation before being labelled grounded hypotheses. No AI interpretation becomes a verified human finding.

The product runner reserves twelve seconds for evidence cleanup within a three-minute session deadline. It aborts model work and closes the page when that deadline approaches, writes partial results, and stops new sessions before the thirty-minute global budget expires. The Python watchdog uses the remaining total budget. Failed tasks do not erase successful actions or stop independent personas; safety/inference infrastructure failures stop execution. Reports distinguish requested, attempted, completed, incomplete and unstarted sessions. Reported token totals exclude unknown usage for interrupted calls.

[CORE issues](CORE_HQ_PRODUCT_ISSUES.md) records the offline Earth startup failure without patching CORE. [Investor report](CORE_HQ_TESTING_REPORT.md) is generated from actual captures.


The first product pilot is complete: root `20261018T021206Z-d6b035`, continuation `20261018T021740Z-1e1b47`. A `--resume <original-run-id>` continuation may execute only remaining contiguous persona IDs, retain the same commit/entry/model and requested count, verify the original config checksum and use the original timestamp-based deadline. Touching a file cannot reset the thirty-minute budget. The completed ten-persona plan rejects any further resume; no persona was rerun.

The original segment used a forty-second inference cap and overlong evaluation context; three evaluations timed out. The remaining six used focused rendered observations and a ninety-second cap within each session deadline. One environmental-researcher attempt was interrupted after planning before its task. The aggregate explicitly marks it incomplete, preserving the original finalized process report unchanged. All nine completed task sessions retained traces. The interrupted trace and two initial screenshots could not be finalized; capture errors are retained. A post-pilot `handleSIGTERM:false` launch setting lets the controller own graceful shutdown in future runs; no extra browser session was run to claim this signal-handling fix verified.


Focused reliability follow-up: [actual diagnostics and limits](CORE_HQ_RELIABILITY.md). `python3 scripts/test_core.py --suite earth-diagnostic --ref <exact-commit>` captures a short read-only Earth initialization probe with zero inference; it never counts as a pilot or product pass. Model attempts now stream to private evidence, retry at most once within the session deadline, and retain partial output and unknown usage. The watchdog reserves graceful cleanup time and preserves finalized summaries or recovers partial session reports. New reports separate browser-task and model-evaluation outcomes. Existing capture records are not migrated or rewritten. No second ten-session pilot has been run.


## Validated combined path and second pilot

One actual smoke passed with `--suite smoke --entry room --mode local-agent --model qwen3:8b --verify-timeout-recovery --time-budget-seconds 180 --ref <exact-commit>`. The fault flag is restricted to smoke: it deliberately aborts the first evaluation after actual streamed output and permits one normal bounded retry. This is not a simulated browser or fake model result. The aborted call’s tokens remain unknown. Fresh pilots require `--smoke-run <id>`; the summary hash, successful browser/evaluation stages, exact CORE commit and model must match.

The second pilot used `--suite pilot --entry mixed --mode local-agent --model qwen3:8b --sessions 10 --execute-pilot --smoke-run 20261018T023931Z-2d06fc --map-network public-assets --time-budget-seconds 900 --ref da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5`. Mixed entry assigns the environmental researcher to Earth and nine other personas to the explicit room; there is no fallback after Earth failure. See [actual outcomes](CORE_HQ_SECOND_PILOT.md): nine end-to-end passes, one preserved selector failure, ten traces, zero evaluation timeouts. The post-pilot selector fix passed a separate scripted Earth regression; the AI Earth attempt was not rerun.

`--map-network public-assets` optionally permits HTTPS GETs only for CORE’s named public OpenFreeMap, NASA GIBS and AWS terrain asset paths, with no query payload, credentials, cookies or referrer. Other requests and WebSockets remain blocked. Default network policy remains blocked. This option permits map retrieval, not external inference, source upload, public contributions or backend writes. `--suite earth-diagnostic --verify-earth-mission --map-network public-assets --time-budget-seconds 60 --ref <exact-commit>` runs a zero-inference read-only globe/catalog/mission check. Action timeout is 6.5 seconds for that check, matching the main harness; its diagnostic results are never AI pilot sessions. Use `compare_core_pilots.py` for later pilot reports; the old report generator protects the original baseline.
