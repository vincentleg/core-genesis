# CORE product and HQ testing improvement backlog

Pinned CORE V9.2: `da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5`. CORE remains read-only. Human participants: **0**.

One conditional local CORE failure; no general or production defect is established. Harness failures, environment limits and subjective UX hypotheses are separate.

| Priority | ID | Category | Finding |
| --- | --- | --- | --- |
| P1 | CORE-001 | core_product_defect | Mission bootstrap stalls in recorded blocked-map conditions |
| P1 | HQ-001 | hq_harness_defect | AI-selected Earth zoom was blocked by the catalog panel |
| P2 | HQ-002 | hq_harness_defect | Duplicate mission cards violated a unique-selector assumption |
| P1 | HQ-003 | hq_harness_defect | Quote-anchored AI criticism is not a valid usability verdict |
| P2 | HQ-004 | hq_harness_defect | Short screenshot deadlines lose action screenshots under rendering load |
| P2 | ENV-001 | environment_network_limitation | Public map resource resets and missing optional local-state service |
| P2 | UX-001 | subjective_ux_hypothesis | Contribution council sharing versus browser-local privacy may need clearer emphasis |
| P3 | UX-002 | subjective_ux_hypothesis | Large planetary aspiration may overshadow the narrow working demonstration |

## CORE-001 — Mission bootstrap stalls in recorded blocked-map conditions

**Severity:** P1. **Status:** confirmed_conditional_local_failure. **Confidence:** observed_failure: high; proposed_root_cause: medium; production_impact: unknown.

**Reproduce:** 1. Serve pinned CORE Git blobs on loopback; fresh context, Chrome/SwiftShader, 1440×1000. 2. Block external map resources and load world.html?quality=low. 3. Wait 25 seconds for CORE civReady without a camera gesture; inspect actual mission controls and state.

**Impact:** In those local offline runs, real committed records return 200 but mission readiness stays false. A later wheel gesture recovered it once. Public-assets runs initialized; production impact is unknown.

**Suggested fix:** CORE team: make local-data mission initialization idempotent and independent of tile availability; show truthful loading/failure states. Verify offline, slow-network and normal public-assets paths on a new commit.

**Scope:** Only the retained blocked-resource local setup. Map-dependent source control flow supports a diagnosis, not proof of a renderer root cause or universal failure.

**Evidence:** `company/core-browser/20261018T020403Z-c32cb3/session-01/report.json`, `company/core-browser/20261018T020707Z-9be69f/session-01/report.json`, `company/core-browser/20261018T023154Z-43eb7d/diagnostic.json`, `CORE src/earth/app.mjs: map load handler starts civilisation`.

## HQ-001 — AI-selected Earth zoom was blocked by the catalog panel

**Severity:** P1. **Status:** confirmed_harness_failure_future_fix_unverified. **Confidence:** attribution: high; post_fix_AI_validation: not_performed.

**Reproduce:** 1. Use retained Earth-agent capture and the pre-fix action sequence. 2. Enter Earth, open catalog, obtain Qwen plan zoom_in, then click the visible zoom control without closing the catalog.

**Impact:** The only requested AI Earth verification failed. The corrected mission selector was never reached, and evaluation was not started.

**Suggested fix:** HQ now closes the actual catalog before zoom and reopens it for mission selection; future journey Earth flow also waits for the startup camera transition. Requires a separately authorized combined AI retest; no rerun was performed here.

**Scope:** Trace explicitly reports ea-panel intercepting pointer events. No hidden/forced click or CORE mutation is an acceptable test substitute.

**Evidence:** `company/core-browser/20261018T052643Z-af7767/session-01/report.json`, `company/core-browser/20261018T052643Z-af7767/session-01/agent-plan.json`, `company/core-browser/20261018T052643Z-af7767/session-01/trace.zip`.

## HQ-002 — Duplicate mission cards violated a unique-selector assumption

**Severity:** P2. **Status:** fixed_scripted_only. **Confidence:** attribution: high; scripted_fix: high; AI_fix: unverified.

**Reproduce:** 1. In second pilot session 4 open Problems & missions. 2. Use the old unique selector for mission.sf.housing-resilience; two visible buttons match.

**Impact:** One second-pilot attempt failed despite successful Earth initialization.

**Suggested fix:** Keep first-visible exact-ID selection and record match count. Scripted four-action regression passed; corrected AI selector verification remains incomplete because HQ-001 failed earlier.

**Scope:** Duplicate cards are observed UI structure, not evidence that CORE mission opening is defective.

**Evidence:** `company/core-browser/20261018T024131Z-fd4185/session-04/report.json`, `company/core-browser/20261018T025157Z-905732/diagnostic.json`.

## HQ-003 — Quote-anchored AI criticism is not a valid usability verdict

**Severity:** P1. **Status:** confirmed_evaluation_quality_limitation. **Confidence:** contradiction_observed: high; human_usability_inference: unsupported.

**Reproduce:** 1. Read second-pilot urban-planner and student evaluation outputs. 2. Compare claims with their own evidence quotes and the rendered dossier.

**Impact:** Investors or product teams could prioritize false defects or mistake model output for human comprehension.

**Suggested fix:** Retain raw outputs as subjective hypotheses requiring human validation. Add explicit task assertions and reviewed semantic rubrics; never report a returned evaluation as accurate human comprehension.

**Scope:** One output alleges missing dates while quoting 2016–2025; another labels evidence-bounded refusal a high-severity issue. These do not establish CORE defects.

**Evidence:** `company/core-browser/20261018T024131Z-fd4185/session-06/rendered-evaluation.json`, `company/core-browser/20261018T024131Z-fd4185/session-05/rendered-evaluation.json`, `docs/CORE_HQ_SECOND_PILOT.md`.

## HQ-004 — Short screenshot deadlines lose action screenshots under rendering load

**Severity:** P2. **Status:** confirmed_capture_failure. **Confidence:** observed_failure: high; proposed_timeout_tuning: unvalidated.

**Reproduce:** 1. Inspect first screenshot errors in both pilots. 2. In the latest Earth run inspect actions 2/3 screenshot timeouts at 2500 ms.

**Impact:** Latest Earth run retained one PNG and a trace, with two failed screenshot captures. Absence must not be mistaken for a clean visual result.

**Suggested fix:** Use remaining-budget-aware capture deadlines and an explicitly logged screenshot-only retry or trace-frame fallback, without repeating browser tasks or rewriting failed evidence.

**Scope:** Trace capture survived; this is evidence quality, not a proven CORE functional defect.

**Evidence:** `company/core-browser/20261018T052643Z-af7767/session-01/report.json`, `docs/evidence/product-pilot-summary.json`, `docs/evidence/second-pilot-summary.json`.

## ENV-001 — Public map resource resets and missing optional local-state service

**Severity:** P2. **Status:** observed_environment_limit. **Confidence:** logs: high; upstream_failure_cause: unknown.

**Reproduce:** 1. Run immutable loopback server with named public map assets enabled. 2. Inspect request/console logs; the static server cannot serve /.core-local/civ/state.json.

**Impact:** Two connection resets occurred in the public-assets probe; second pilot logged 13 optional-state 404s including reloads. These add noise and can delay captures.

**Suggested fix:** Record real delivery/error events and renderer/browser settings. Classify the known optional endpoint separately; investigate repeatable missing required assets rather than counting every 404 as a CORE bug.

**Scope:** No production backend was tested. Successful imagery delivery and these network failures coexist.

**Evidence:** `company/core-browser/20261018T024005Z-d0b6ce/diagnostic.json`, `docs/CORE_HQ_SECOND_PILOT.md`.

## UX-001 — Contribution council sharing versus browser-local privacy may need clearer emphasis

**Severity:** P2. **Status:** requires_human_validation. **Confidence:** copy_and_local_persistence: high; UX_effect: low.

**Reproduce:** 1. Open the actual mission contribution form and read its consent/vault copy. 2. Compare first-visitor evaluation output with the actual scope and My CORE contribution disclosure.

**Impact:** Potential confusion about local queue, encrypted vault and actual publication; no recruited user has demonstrated that confusion.

**Suggested fix:** Consider a concise browser-only/no-publication label next to each action and follow-up acknowledgement. Validate wording with real consented humans before claiming improved comprehension.

**Scope:** Synthetic browser fixtures are not human participants. Encrypted-vault storage was not tested by mission-queue checks.

**Evidence:** `company/core-browser/20261018T024131Z-fd4185/session-01/rendered-evaluation.json`, `company/core-browser/20261018T024131Z-fd4185/session-02/report.json`, `company/core-browser/20261018T053229Z-a71e90/session-01/report.json`.

## UX-002 — Large planetary aspiration may overshadow the narrow working demonstration

**Severity:** P3. **Status:** requires_human_validation. **Confidence:** rendered_copy: high; UX_effect: low.

**Reproduce:** 1. Open the real Earth landing screenshot and What works today disclosure. 2. Navigate to actual dated mission evidence or Progress to compare scope.

**Impact:** A first-time visitor may overestimate geographic coverage or verified impact; this is a hypothesis, not a measured human error rate.

**Suggested fix:** Consider moving the current San Francisco scope and working-evidence entry nearer the main CTA while retaining truthful long-term aspiration. Test with humans.

**Scope:** CORE already discloses one street and no verified impact. The backlog does not claim those disclaimers are absent.

**Evidence:** `company/core-browser/20261018T052643Z-af7767/session-01/01.png`, `company/core-browser/20261018T024131Z-fd4185/session-01/first-impression.json`.

Changes to CORE are recommendations only. A new exact-commit verification and human approval are required before any CORE fix or deployment. Returned model evaluations are not human research or verified product defects. The machine-readable backlog is [core-improvement-backlog.json](../testing/core-improvement-backlog.json).
