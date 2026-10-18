# STOPPED — resumption snapshot (2026-10-18 UTC / October 17 Pacific)

Work was stopped at the founder's usage-limit request. **Do not launch testing, inference or campaigns until work is explicitly resumed.** No testing or development was started during shutdown. Process inspection found no active HQ browser/campaign/inference jobs; the selected-session scheduler journal is finished, with zero running sessions.

## Branch, commits and boundaries

- Repository: `/Users/vincentgppm/core-genesis` (CORE HQ), branch `feat/core-hq-real-core-testing`.
- Previous committed checkpoint: `91e1cbb`. The shutdown preservation commit is **HEAD**; obtain its exact SHA with `git rev-parse HEAD`. Its SHA is also supplied in the final shutdown response. This file and the unfinished implementation are included together in that commit.
- CORE is a separate, **read-only** repository: `/Users/vincentgppm/core`, inspected development branch `v9.2/earth-first`, exact tested commit `da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5`. HQ has made no CORE changes. Never substitute main or silently test another commit.
- The public CORE website still serves an older version per the founder; production SHA is unverified. Local V9.2 has not been deployed. Local tests are not production verification.
- This snapshot supersedes the current-status statements in older sections below and in the Earth/journeys, campaign and backlog documents. Historical results remain unchanged.

## Completed since 91e1cbb

**Real AI Earth session PASSED:** `company/core-browser/20261018T054429Z-792b60/`.
Local Qwen3:8b selected `zoom_in` and `mission.sf.mobility` from actual observed controls. Earth initialized, real imagery loaded, an unforced real pointer click changed zoom **15.4 → 16.4**, and the selected mission opened with actual findings. Six of six browser actions passed; AI evaluation passed separately. Six PNGs, trace, action logs, model records, provenance and checksums are retained. Runtime 105.661s; two returned local calls, 3,833 prompt + 302 output tokens; $0 paid APIs. The selected mission had one matching control: the older two-match duplicate case remains verified by a separate scripted regression, not by this AI session.

**HQ Earth repair:** added `scripts/core_earth_actions.cjs`; wait for CORE/city readiness and camera settling, close the actual blocking catalog, observe enabled visible hit-testable zoom controls, validate the model's canonical action, perform a real click, verify zoom change, reopen catalog and select the exact mission. No CORE patch, forced click or substitute globe. The preserved failed session `20261018T052643Z-af7767` was an HQ overlay/action sequencing defect, not evidence of broken CORE zoom. Initialization/imagery had succeeded in that failed attempt.

**Three selected, genuinely AI-driven journeys PASSED**, through the new scheduler:

| Selected case | Browser capture | Verified interaction | Actions | PNGs |
|---|---|---|---|---|
| campaign-10, agent-dialogue:consult | 20261018T055033Z-148397 | Actual Qwen question, agent consultation, dialogue and unsupported-question boundary | 4/4 | 4 |
| campaign-17, my-core:contribution | 20261018T055208Z-72aad0 | Consented labelled synthetic local contribution, reload/isolation, My CORE item persistence | 7/7 | 6 |
| campaign-01, first-look:status | 20261018T055324Z-ca1e22 | Qwen chose observed status control, clicked real disclosure and verified rendered content | 2/2 | 2 |

Scheduler journal: `company/core-campaigns/20261018T055033Z-cb2e5a/`. **Finished: 3 selected, 3 completed, 0 failed/incomplete/running/unstarted.** Six returned calls, 9,841 prompt + 1,159 output tokens; about 229.4 seconds initial execution. Individual parent runtimes 94.833/75.750/58.837s, below the 180s cap; total cap 540s. A completed-journal resume launched zero new sessions and retained the original selection/deadline. Do not use its later journal update timestamp as execution runtime. Executed scheduler source copies and their manifest were retained inside the private journal before later safeguards were added.

**Combined new evidence: four AI sessions passed, 19/19 browser actions, 18 screenshots, four traces, eight returned local inference calls, 13,674 prompt + 1,461 output tokens, no unknown usage, $0 paid API cost, zero human participants.** One contribution screenshot timed out and remains an explicit capture error; trace and other screenshots were retained. No page exceptions; optional local backend-state 404s remain logged. No prior ten-session pilot was rerun; only these three selected campaign definitions were executed, and the remaining 27 definitions were not executed.

**Scheduler implemented, bounded validation only:** `core_genesis/campaign_scheduler.py` and `scripts/run_core_campaign.py`. Default is inspection-only. Execution requires explicit selected IDs, invocation limit and verified same-commit AI Earth gate. Sequential children, fixed session/total budgets, cleanup reserve, unique capture IDs, immutable selection/deadline policy, atomic checkpoints, lock/owner checks, no replay of attempted IDs, signal forwarding, recoverable partial records, browser/evaluation status separation, provenance/hash checks, token accounting and zero-paid-cost policy are implemented. Interrupted usage stays unknown. Resume cannot reset original budgets or selection. The thirty-case JSON is a definition, not a live result ledger; default execution remains disabled.

Additional saved changes: bounded viewport/run-ID inputs, a four-call inference cap checked before dispatch, AI-selected onboarding controls, screenshot deadline adjustment, driver signal forwarding, and targeted scheduler/Earth/inference/process fixture tests. Existing infrastructure and historical evidence were retained.

## Historical pilots — keep these counts separate

| Metric | Original pilot | Second pilot |
|---|---|---|
| Root | 20261018T021206Z-d6b035; continuation 20261018T021740Z-1e1b47 | 20261018T024131Z-fd4185 |
| Attempts | 10 unique | 10 finalized |
| Browser-task completions | 9; 1 interrupted before task | 9; 1 Earth mission-selector failure |
| End-to-end passes | 6; 3 later evaluations timed out | 9 |
| Local inference | 19 attempted / 16 returned; 3 unknown-usage calls | 19/19 returned; no unknown usage |
| Returned prompt/output tokens | 29,211 / 2,276 | 32,488 / 2,621 |
| Screenshots / traces | 41 / 9; interrupted trace missing | 44 / 10 |
| Runtime | 688.609s wall including continuation | 508.516s runner; ~518.593s wall |
| Paid APIs / human participants | $0 / 0 | $0 / 0 |

Sources: `docs/evidence/product-pilot-summary.json`, `docs/CORE_HQ_TESTING_REPORT.md`, `docs/evidence/second-pilot-summary.json`, `docs/CORE_HQ_SECOND_PILOT.md`. Original reports/artifacts must not be rewritten to improve historical counts. Earlier controlled-timeout smoke and scripted browser checks are separate evidence, not additional pilot participants.

## Unfinished work and limitations

1. **Documentation consolidation unfinished:** `CORE_HQ_EARTH_AND_JOURNEYS.md`, `CORE_HQ_30_SESSION_CAMPAIGN.md`, `CORE_HQ_IMPROVEMENT_BACKLOG.md` and `testing/core-improvement-backlog.json` still contain pre-repair status (Earth blocked/scheduler missing). Update them from the actual captures above on resumption; add a small source-free current summary if useful. This handoff is the current authority. No new report/backlog claims were fabricated during shutdown.
2. **Final verification pending:** earlier targeted scheduler tests (10), driver-signal subprocess fixture (1), recovery tests (2), and Node Earth/inference tests (10 combined) passed at their respective revisions. Latest plan-definition/test-expectation edits and final resume guard have not been rerun as one final suite. No further tests were run during shutdown. Do not claim a fresh full suite passed. CORE's own unit suite was not run.
3. Normal three-session scheduler execution and completed no-op resume are browser-backed. Real-browser forced interruption/mid-session resumption are **not** yet verified end to end; process/recovery fixtures are separate. Later guard changes were not part of the saved launch-version normal run. Most thirty-case variants remain unvalidated. Do not claim readiness for 30 or 50–100 sessions.
4. One new screenshot capture timed out despite retained trace/other PNGs. Trace finalization on hard process termination remains a risk. Token usage for interrupted local calls can remain unknown; electricity/hardware cost is unmeasured.
5. UX evaluations are heuristic and can contradict their own quotations. They do not measure human comprehension; actual human participants remain zero. CORE's observed dialogue behavior is its real deterministic engine, distinct from Qwen browser-controller inference.

## Issue classification and reliable globe conditions

- **HQ defects:** catalog overlay previously intercepted selected zoom; fixed and now AI verified. Corrected exact mission selector opened the selected mission in the new run; the duplicate-control two-match regression remains separately scripted. Capture timeout and semantic evaluation noise remain limitations.
- **CORE/environment-dependent behavior:** blocked external map resources can leave Earth mission readiness false even after style/map load. Low-quality mode did not establish reliable offline initialization. This is a conditional product limitation requiring CORE-team investigation; do not claim a new confirmed general online globe failure or modify CORE.
- **Environment/network:** real imagery needs reachable allowed public map/style/terrain/NASA imagery resources via `--map-network public-assets`; external access is blocked by default. Existing allowlist strips private request headers. Start from the exact local commit, wait for CORE ready/civReady and city camera settling, verify actual successful imagery responses, then interact through unoccluded UI. Optional `/.core-local/civ/state.json` 404 is expected with the static local server; transient map connection resets have occurred historically. Online success is conditional on resource availability, not a guarantee of reliable offline globe testing.
- **UX hypotheses:** first-impression and comprehension criticisms need actual human validation; do not promote them to confirmed product defects or human testing metrics. No new confirmed CORE defect was established by the four passing sessions.

## Next steps, in priority order — after explicit resumption

1. Read this snapshot and inspect the existing four captures/journal; do not rerun either pilot or the now-passing Earth session merely to rediscover results. Consolidate the current report/backlog statuses from retained evidence, preserving the historical files/counts.
2. Finish only the short final syntax/unit verification of saved changes; clearly record the latest revisions tested. Review remaining scheduler interruption/recovery edges; if further actual browser validation is necessary, use a separately authorized small targeted run, not a large campaign.
3. Human review of evidence, still-unvalidated variants, capture reliability and scheduler readiness before authorizing any broader campaign. Thirty-case execution and 50–100-session scaling remain unauthorized/unjustified at shutdown.

## Resume commands

Start with inspection only (no browser, model call or test):

```sh
cd /Users/vincentgppm/core-genesis
git switch feat/core-hq-real-core-testing
git status --short --branch
git log -1 --format='%H %s'
cat docs/CORE_HQ_HANDOFF.md
```

After the founder explicitly resumes work, these are the relevant short verification commands (not executed at shutdown):

```sh
node --check scripts/core_product_browser.cjs
node --check scripts/core_journeys.cjs
node --test tests/earth_actions.test.cjs tests/core_journeys.test.cjs tests/local_inference.test.cjs tests/core_map_network.test.cjs
PYTHONPYCACHEPREFIX="$PWD/.cache/pycache" python3 -m unittest discover -s tests -p 'test_*campaign*.py'
PYTHONPYCACHEPREFIX="$PWD/.cache/pycache" python3 -m unittest discover -s tests -p 'test_product_gates.py'
PYTHONPYCACHEPREFIX="$PWD/.cache/pycache" python3 -m unittest discover -s tests -p 'test_runner_recovery.py'
PYTHONPYCACHEPREFIX="$PWD/.cache/pycache" python3 -m unittest discover -s tests -p 'test_driver_signal.py'
python3 scripts/run_core_campaign.py
```

The last command is **inspection-only**, not execution. Do not add `--execute` without authorization. Existing finished selected-case journal needs no resume: its three selected cases are terminal and its original deadline is expired; it cannot become a new campaign or gain 27 additional cases.

## Preservation and approvals

All valid partial implementation/tests/plan and this handoff are saved locally in the shutdown commit. Raw private screenshots, traces, prompts and manifests remain intact under ignored `company/core-browser/` and `company/core-campaigns/`; they are intentionally not committed, published or copied into public assets. Keep this workspace or separately arrange an authorized private backup: a Git checkout alone will not restore ignored evidence. Historical hackathon records are untouched. Temporary files, credentials and large raw artifacts are excluded from the commit.

Constraints persist: HQ-only edits; CORE read-only; local Qwen3/Ollama only; no paid APIs, external AI disclosure, recruitment, fake human counts or public synthetic contributions; no push/deploy/merge or external resource renames. Public map-asset access is distinct from permission to disclose private source/user data. Existing local-model availability is required; do not download/pay for models automatically. Future external services, source/user-data sharing, paid costs, human panels, push/deploy or large campaigns require explicit approval. **After saving this snapshot, STOP.**

---

## Historical handoff (retained; current-status claims superseded above)

# CORE HQ implementation handoff

Latest follow-up after `c5c815b`: **one AI Earth attempt failed in HQ** because the open catalog intercepted the AI-selected zoom. Initialization and actual imagery succeeded; corrected selector verification was not reached. No AI rerun or pilot repetition occurred. Three independent scripted checks passed (French/English, My CORE persistence, keyboard skip). Thirty distinct journey variants are defined and a 30-session campaign is prepared with execution disabled and zero actual sessions. See [current results](CORE_HQ_EARTH_AND_JOURNEYS.md), [prepared campaign](CORE_HQ_30_SESSION_CAMPAIGN.md), and [prioritized backlog](CORE_HQ_IMPROVEMENT_BACKLOG.md). Earlier results below remain historical.

Latest execution: the combined local-Qwen3/browser smoke passed, including controlled timeout recovery. The second pilot `20261018T024131Z-fd4185` finalized all ten AI-directed attempts: nine browser/evaluation passes, one Earth selector failure, zero incomplete or unstarted personas. All 19 calls returned, reporting 32,488 prompt + 2,621 output tokens; $0 paid APIs, zero humans. Runner time 508.516s; wall estimate including inspection 518.6s, below the 900-second pilot cap. All ten sessions were below 180 seconds. See [second-pilot comparison](CORE_HQ_SECOND_PILOT.md) and its source-free evidence manifest. Earlier checkpoint descriptions below remain historical.

Phase 1 is committed locally as `5dc8a4e` on `feat/core-hq-real-core-testing`. The completed product pilot infrastructure and reports are preserved in local checkpoint `0d27d7d` (clean tree confirmed immediately after that commit). Verified baseline: 10 attempts, 9 completed, 1 incomplete, 6 end-to-end passes; 41 screenshots and 9 traces. The reliability follow-up is documented separately below. No push, deployment, paid API request, CORE write, recruitment or public contribution occurred.

Implemented: current CORE HQ branding and metadata; status page; local full-file Git inspection with explicit ref selection; privacy and paid-inference gates; immutable local CORE browser server; Playwright scripted baseline and genuine local-Ollama decision adapter; isolated serial pilot harness; evidence-linked review records; consent-aware human-export ingestion; resource migration plan. Existing orchestration, Nemotron client, budget ledger, replay and historical prototype builder are retained. The default legacy remote mission now reads local CORE and stops before transmitting private source.

CORE: clean `v9.2/earth-first` at `da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5`, 568 tracked paths, 190 full eligible sources. Production's exact commit remains unverified; per founder it serves older CORE, not local V9.2.

Successful actual AI evidence: `company/core-browser/20261018T015606Z-a96878/summary.json`, `session-01/report.json`, `session-01/decision-*.json`, six PNGs, `session-01/trace.zip`, `provenance.json` and `checksums.json`. Source bodies stay in ignored `company/core-inspection.json`. Failed attempts remain alongside the success. Evidence is private and local; it is not included in Git or public assets. `public/hq-status.json` is a small allowlisted projection without source bodies, screenshots, traces, model prompts or participant rows.

Successful session: 6/6 actions, 5 local qwen3:8b calls, 8,397 prompt + 119 output tokens, ~89 s, $0 paid API cost. It verified four UI milestones (Earth exploration, CORE World selection, problems panel, contribution UI). Zero page exceptions; blocked external map requests and one optional local backend-state 404 remain recorded. No dialogue, submission, live location data or human comprehension validation.

Validation: the 73-test Python suite had 72 passes and one socket-bind sandbox failure; the affected three-test artifact file passed with localhost permission. The added publication privacy check brings the new HQ test file to 8 passing tests. Five existing JavaScript tests passed. Six HQ browser smoke checks passed, including cost-gate HTTP rejection. Syntax checks and `git diff --check` passed. These are HQ checks; the CORE application unit-test suite was not run or claimed.

Historical mission/evidence/experiment/artifact records were not changed. The original README is preserved byte-for-byte in `docs/hackathon/README.md` (SHA-256 `b8a1e385e517fb01d68c1e9e0f6f361065c908578d9f48b177fe7c88b891a369`). Current source/client branding changed; historical recorded JSON and videos retain original names.

Preservation checkpoint: original browser capture checksums verified; a source-free capture manifest is retained at docs/evidence/initial-browser-session.json. Completed infrastructure is preserved in the single requested local commit `5dc8a4e`; no push or deployment.

Expanded work is complete for this phase. The direct-room critical preflight `20261018T021120Z-7c5ee8` passed nine real browser actions: source-backed dated data delivery, agent consultation, cited dialogue, unsupported-question refusal, consent rejection, synthetic local mission-queue contribution, reload persistence and independent-context isolation. This is not a vault test or a public contribution. CORE's conversation engine is deterministic; browser-controller inference is a separate local qwen3:8b model.

Ten-persona pilot: root `20261018T021206Z-d6b035`, continuation `20261018T021740Z-1e1b47`. Exactly ten unique persona/browser attempts; no reruns. Nine executed AI task sessions completed their assigned product checks. Six also completed rendered-interface comprehension evaluation. Three evaluations hit the initial 40-second model timeout. The environmental-researcher attempt was interrupted after planning and before its task; aggregate reporting conservatively counts it incomplete. Original reports and their status strings remain unchanged. The aggregate explains this stricter classification rather than silently rewriting evidence.

Pilot result: 9 completed, 1 incomplete, 6 end-to-end passes. Wall time 688.6 seconds (~11.48 minutes) including the continuation pause; longest session 77.2 seconds. All recorded sessions were below 3 minutes, and the continuation retained the original 30-minute deadline. Local inference: 19 attempted / 16 returned calls; 29,211 reported prompt + 2,276 reported output tokens. Three interrupted calls have unknown token usage. Paid API cost $0; hardware/electricity unmeasured. Actual human participants: 0.

After the pilot, Playwright automatic SIGTERM shutdown was disabled so the HQ controller can own graceful evidence cleanup; that signal-handling adjustment has syntax validation but no additional browser run. The interrupted fourth trace remains missing and was not recreated.

The controller was corrected in HQ: wait for staged dialogue to settle; allow up to 90 seconds for local evaluation within each 180-second session; observe focused actual UI instead of an overlong snapshot; reserve time for trace cleanup; permit continuation only for unrun contiguous persona IDs under the original deadline. Product task failures are separate from controller/evaluation failures. Pilot objectives varied across the ten named personas, but the explicit direct room covered one San Francisco housing/resilience mission. Model-generated questions and fixture text were executed through actual controls; browser steps inside each selected tool are deterministic.

CORE issue HQ-CORE-001: Earth mission initialization failed repeatedly with external maps blocked, including CORE's built-in low-quality option. A diagnostic captured `mapLoaded: true`, `styleLoaded: true`, `ready: false`. No functions were forced, sources patched or data mocked. The room entry is explicit and separate, not a silent fallback or proof Earth works. Production impact remains unverified. See docs/CORE_HQ_PRODUCT_ISSUES.md.

AI UX interpretations were noisy. One claimed missing source dates while quoting a retrieval date. All raw model outputs are retained as unverified hypotheses; quote presence alone does not verify the complaint. Six comprehension evaluations returned; 2/6 visibility answers explicitly mentioned browser/local/nonpublication scope (text-presence proxy only, not human accuracy).

New essential validation: product-room browser preflight 9/9; pilot raw browser actions retained for all attempts; four pilot safety tests passed (entry-specific preflight gate, ten-session cap, production rejection, original resume deadline cannot reset). Changed Python/JavaScript syntax and diff checks passed. The prior phase's eight HQ and broader tests are recorded above; they were not repeatedly rerun. CORE's unit suite was not executed.

[Investor report](CORE_HQ_TESTING_REPORT.md) gives actual scope, failures, recommendations and the conclusion: not ready for 100+ sessions. Source-free per-persona metrics and capture hashes: docs/evidence/product-pilot-summary.json. Full private aggregate: company/core-pilots/20261018T021206Z-d6b035/aggregate.json. Retained pilot evidence: 41 screenshots and nine finalized traces. All nine completed task sessions have a trace; the interrupted fourth attempt has screenshots/action logs but trace finalization failed when the browser closed. Two initial screenshots also timed out and remain recorded as capture errors. Returned model records are retained. Original successful navigation evidence and all hackathon records remain intact.

Next: human review of this diff and CORE issue evidence. Request a CORE-team investigation of map-independent mission startup; do not write CORE from HQ. Improve semantic UX review and broaden missions/task coverage before scaling. No extra sessions, source-sharing approval, paid service connection or recruitment was performed.

No new service/key/payment approval is needed for the local path already verified. Future paid inference, private-data disclosure, cloud browsers, panel recruitment, external resource renames, push or deployment require separate explicit approval. The existing Crusoe key is not used by this local browser adapter.


## Focused reliability follow-up

See [reliability results and exact environment conditions](CORE_HQ_RELIABILITY.md). The original pilot totals above remain unchanged. Three failed evaluations followed successful browser assertions; their old artifacts cannot establish the inference bottleneck. Streaming now saves partial output/timing/unknown usage, retries at most once within existing deadlines, and reports browser/evaluator results separately. Graceful watchdog shutdown recovers existing partial reports without overwriting a finalized summary.

A 22.474-second real offline Earth probe recovered application readiness after an actual wheel gesture, with map load observed; imagery remained unavailable. This narrows HQ-CORE-001 without fixing CORE or validating the complete Earth journey. One scripted room regression passed 9/9 actions; one local inference transport fixture passed (200 reported tokens, $0). Eight inference tests, four safety-gate tests and two recovery tests passed. Neither check adds AI pilot participants. The combined revised AI controller still needs one short end-to-end smoke before a second room pilot; no full ten-session rerun occurred. Reliable globe rendering and 100+ scaling remain unverified. Historical evidence is retained.


## Combined smoke and second pilot follow-up

Smoke `20261018T023931Z-2d06fc` passed five real browser actions and a separately reported evaluation; its first evaluation was deliberately timed out after two characters of real output, saved privately, then recovered on the single retry. Usage of that interrupted call is unknown; smoke usage is separate from the pilot. The second pilot retained 44 PNGs, ten finalized traces and 44/45 successful browser actions. One initial screenshot timed out. Thirteen HTTP/console entries were the optional local-state 404, with zero page exceptions. Coverage: nine dated-data checks, four dialogue checks, three isolated consented contributions, one successful Earth-to-catalog navigation followed by a failed mission click. Nine actual rendered-interface evaluations returned, but their semantic quality is unvalidated and several complaints contradict their own quotes.

Earth resources were explicitly enabled through a narrow public-asset GET allowlist; no private source, credentials or user data went to external AI providers. The first online probe rendered textured Earth, despite two recorded connection resets. All four public-assets browser captures initialized CORE. The pilot Earth click failed because two controls had the same mission ID. HQ now selects the first visible exact matching control. Separate scripted regression `20261018T025047Z-f20e8d` hit a 2.5-second transition timeout; final check `20261018T025157Z-905732`, using the main harness’s 6.5-second limit, passed four real actions and opened actual mission findings/citations. Neither probe counts as an AI session or repairs CORE. The revised AI Earth path was not rerun.

New pilots require a verified successful same-commit/model smoke capture; optional network access stays blocked by default. The historical first-pilot generator refuses to replace its report with a later pilot. `compare_core_pilots.py` creates a separate report and verifies old/new capture hashes. Focused validation: ten Node tests, five Python safety-gate tests and two recovery tests passed, plus syntax/diff checks. No full CORE test suite ran. No 50–100-session campaign is justified yet: retest the corrected AI Earth path, broaden missions, improve semantic evaluation and check rendering/capture consistency first. No CORE writes, push or deployment occurred.

Current validation: 23 targeted unit tests passed, alongside the three recorded scripted browser checks. One Qwen3 call in the failed Earth attempt reported 1,396 prompt + 125 output tokens; $0 paid API cost. The prepared campaign has no execution path/scheduler and remains blocked pending the corrected AI Earth verification and validation of remaining journey variants.
