# Single AI Earth verification and broader journeys

CORE development target: `v9.2/earth-first`, exact commit `da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5`. CORE HQ started at `c5c815b`; new Earth instrumentation was added locally. CORE remained read-only. Public production was not tested.

## Actual Earth outcome: failed harness interaction

Exactly **one** real local-Qwen3/browser session ran: `20261018T052643Z-af7767`. No pilot was repeated and this session was not rerun after failure.

| Requirement | Observed outcome |
| --- | --- |
| Earth initializes | Passed: `ready: true`, `civReady: true`; entered Earth and opened actual mission catalog |
| Real imagery | Passed: 38 NASA imagery and 25 OpenFreeMap responses returned HTTP 200; `imageryLoaded: true`; retained PNG shows textured Earth |
| AI direction | One actual local Qwen3 call returned `zoom_in` and selected `mission.sf.mobility` from the observed catalog |
| Successful AI globe interaction | **Not achieved**: visible zoom button click was intercepted by the catalog panel |
| Corrected mission selector | **Not reached**; remains unverified by a combined AI session |
| AI evaluation | Not started after the browser failure |
| Evidence | One PNG, finalized trace, action/assertion/error logs, actual plan and usage, CORE provenance and SHA-256 capture manifest |

Process runtime: 49.038 seconds. Actual browser actions: 2/3 passed. Reported local inference: 1/1 calls, 1,396 prompt + 125 output tokens. Paid API cost $0; hardware/electricity unmeasured. Two action screenshots timed out at 2.5 seconds and remain recorded as capture failures. No page exceptions occurred. The trace and the initial screenshot were retained.

The trace explicitly reports `<aside id="ea-panel"> intercepts pointer events`. HQ opened Problems & missions before planning, then attempted zoom without closing that catalog. This is a **CORE HQ sequencing defect**, not evidence of a CORE zoom-control defect. No forced hidden click, mock, injected camera mutation or CORE repair was used. The AI-selected question/fixture text was not executed after the failure and is not accepted as product evidence.

The future Earth-agent sequence now closes the actual panel before zoom, checks a genuine camera change, and reopens the catalog for exact-ID first-visible mission selection. Broader Earth journeys wait for the startup camera transition as well. **These future fixes have no additional AI validation in this operation.** The prior scripted selector regression remains historical supporting evidence; it does not turn this failed run into a pass.

Harness source hashes were not captured before this Earth run. New future capture configs now hash the HQ runner/helper/catalog files and record browser/Node versions in reports; this does not backfill missing historical metadata.

## Broader browser scenarios

[Journey definitions](../testing/core-v92-journeys.json) and `scripts/core_journeys.cjs` implement ten families and thirty explicit variants: first visit, Earth, location/problem discovery, dialogue, contribution, My CORE, French/English, keyboard, errors, investor impression. They operate actual links, forms, language controls, map controls and rendered data, with concrete browser assertions. Existing dialogue, contribution, evidence, cost, local-inference and cleanup infrastructure is reused. These are bounded tools, not an unrestricted autonomous browser agent.

Three short **scripted** checks ran outside the campaign, with zero inference:

| Check | Capture | Browser actions | Runtime |
| --- | --- | --- | --- |
| English → French → English My CORE headings | `20261018T053115Z-a9b6c8` | 3/3 | 8.926s |
| Consented local contribution → My CORE → reload | `20261018T053229Z-a71e90` | 7/7 | 18.741s |
| Tab/Enter skip link → main-content focus | `20261018T053231Z-ecfe2a` | 2/2 | 8.458s |

Those captures preserve the old generic runner's inherited `assigned_task` label; the explicit `scenario`, task IDs and actual actions establish the journey tested. Future metadata uses the scenario ID as the assigned task and scenario-specific limitations. Original records are not rewritten. The other variants are implemented but unvalidated, and no thirty-session AI campaign has executed. Keyboard focus checks are not a full accessibility conformance audit; French navigation is not professional translation review. My CORE mission-queue persistence is not a vault encryption test. Model UX output cannot reliably represent human comprehension; every UX interpretation requires human validation. Actual human participants: **0**.

A single case can be selected explicitly with `--suite journey --scenario <id> --variant <id> --sessions 1`; unknown cases and multi-case execution are rejected. The prepared campaign remains disabled. Its global scheduler, durable checkpoint orchestration and campaign-wide enforcement still need implementation/verification before execution. See [campaign plan](CORE_HQ_30_SESSION_CAMPAIGN.md).

## Evidence and recommendations

Source-free records and capture-manifest hashes: [earth-and-journeys-summary.json](evidence/earth-and-journeys-summary.json). Raw images, traces, model text and source inspection remain private under ignored `company/`. Both completed pilots were verified against their existing manifests without altering results or evidence.

The [prioritized backlog](CORE_HQ_IMPROVEMENT_BACKLOG.md) distinguishes one conditional local CORE startup failure, confirmed HQ defects, environment/network limitations and subjective UX hypotheses. Top next steps: separately verify the corrected AI Earth path when authorized, improve capture reliability and semantic review, then validate distinct journeys individually before any campaign. Scaling to 50–100 sessions remains unjustified. No CORE writes, paid API calls, push or deployment occurred.

Validation: 23 short targeted unit tests passed (12 Node; 6 CLI safety gates, 3 campaign preparation/recovery and 2 watchdog tests in Python), plus changed-code syntax and whitespace checks. These fixtures are not browser sessions. The CORE application unit suite was not run. No full pilot or campaign executed.
