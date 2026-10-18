# CORE HQ — second bounded AI browser pilot

Exact CORE development target: `v9.2/earth-first` at `da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5`. Local immutable Git-blob server; CORE remained read-only. Public production was not tested. HQ starting commit: `8f8527b` plus the smoke/pilot configuration changes in this change set.

## Gate and recovery evidence

Combined smoke `20261018T023931Z-2d06fc` passed 5 actual browser actions and a separately recorded AI evaluation in 62.667s. Local qwen3:8b selected a real task and question. The saved interrupted prefix is only two characters; this validates persistence/retry, not recovery of a useful complete assessment. The controlled timeout interrupted the first evaluation only after real streamed content arrived; its partial prefix is retained with unknown token usage. The single retry completed. No browser action or contribution was replayed by this retry. Smoke counts are separate from both ten-persona pilots.

Public-assets Earth diagnostic `20261018T024005Z-d0b6ce`: 32.910s, zero inference; readiness was true before any explicit screenshot or wheel gesture. Actual OpenFreeMap TileJSON and NASA imagery returned HTTP 200. The retained after screenshot shows textured Earth. Two connection resets and an optional local-state 404 were also logged; initial screenshot capture timed out, while the after screenshot and trace were retained. The hidden landing-state Zoom in control still failed its click; it is not counted as successful navigation. This probe establishes one observed online initialization, not general reliability.

## Measured comparison

| Metric | Original pilot | Second pilot |
| --- | --- | --- |
| Browser attempts | 10 | 10 |
| Finalized AI-directed attempts (may fail) | 9 | 10 |
| Browser task passes | 9 | 9 |
| Completed evaluations | 6 | 9 |
| End-to-end passes | 6 | 9 |
| Incomplete attempts | 1 | 0 |
| Unstarted personas | 0 | 0 |
| Wall runtime (seconds) | 688.61 | 518.59 |
| Returned/attempted model calls | 16/19 | 19/19 |
| Reported prompt/output tokens | 29211/2276 | 32488/2621 |
| Unknown-usage model attempts | 3 | 0 |
| Saved screenshots | 41 | 44 |
| Finalized traces | 9 | 10 |
| Paid API cost (USD) | 0 | 0 |
| Actual human participants | 0 | 0 |

Second pilot budget: 891.1s total (requested 900s); finalization is not task success; maximum 180s per session. Returned tokens exclude interrupted-call usage. Paid APIs cost $0; hardware/electricity are unmeasured. Original evidence hashes verified unchanged. The wall estimate includes inspection and uses capture timestamps/file completion time (about one-second precision); runner time is 508.516s. Neither pilot runtime includes this operation’s separate smoke, diagnostics or reporting.

## Actual persona/task outcomes

| Persona | Entry | Browser tasks passed | Evaluation | End-to-end | Seconds |
| --- | --- | --- | --- | --- | --- |
| First-time visitor | room | location, dialogue | passed | pass | 31.38 |
| Nontechnical user | room | location, contribution | passed | pass | 55.72 |
| Scientific researcher | room | location, dialogue | passed | pass | 54.60 |
| Environmental researcher | earth | earth_navigation | not_started | fail | 32.88 |
| Student | room | location, dialogue | passed | pass | 55.81 |
| Urban planner | room | location | passed | pass | 56.47 |
| Skeptical investor | room | location, dialogue | passed | pass | 58.88 |
| Accessibility-focused user | room | location, contribution | passed | pass | 52.49 |
| Community contributor | room | location, contribution | passed | pass | 53.63 |
| Technical power user | room | location | passed | pass | 55.55 |

## Separate scripted Earth follow-up

- `20261018T025047Z-f20e8d`: failed, 1/2 actions, 26.371s, zero inference. locator.click: Timeout 2500ms exceeded.
- `20261018T025157Z-905732`: passed, 4/4 actions, 35.188s, zero inference. Observed 2 visible controls for the same mission; the first matching control opened actual dated findings and citation links.

After the pilot, HQ was changed to select the first visible control with the exact AI-selected mission ID. The first scripted regression hit its 2.5-second transition click limit; one final retry used the main harness’s existing 6.5-second action limit. These are new zero-inference diagnostic captures, not replacements or additional AI pilot sessions. The successful scripted path verifies the selector fix and actual Earth-to-mission flow, but the revised combined AI Earth path has not been rerun. All four public-assets browser captures reached application readiness; they sample one machine/renderer, not general reliability.

Actual browser actions: 44/45 passed. Captured page exceptions: 0; console errors: 13; HTTP errors: 13; screenshot failures: 1. All 13 HTTP/console errors were the optional `/.core-local/civ/state.json` 404, including reloads; they are an immutable-server environment limitation. One initial screenshot timed out; remaining captures and all ten traces were retained. Logs remain separate from confirmed product defects.

## Failures, interpretation and scale decision

- Session 4 (earth), stage `browser`: `locator.click: Error: strict mode violation: locator('#ea-panel-body button[data-mission="mission.sf.housing-resilience"]') resolved to 2 elements:`. See private `session-04/report.json` and trace. Successful earlier assertions are retained; no fallback or task rerun occurred.

This is a changed-condition comparison, not a controlled causal experiment: HQ inference/reporting changed and the second pilot permits named public map assets. Cache warm-up/load and the original continuation pause were not controlled, so runtime differences are not a causal speedup estimate. Nine personas use the same explicit San Francisco housing/resilience room; one follows Earth and selects from its observed mission catalog. Personae vary task instructions, not human participants. Browser tools use deterministic steps selected and parameterized by local AI; CORE answers use its own cited deterministic engine. Source dates, analytical correctness and live upstream freshness were not independently validated. AI UX complaints remain hypotheses, even when a quote matches; one alleges missing dates while its quote explicitly gives 2016–2025, and another labels evidence-bounded refusal a high-severity issue. An accessibility complaint claims a button lacks a label while quoting its accessible name. These are evaluator-quality problems, not established CORE defects; no model opinion is a confirmed CORE defect. First-time comprehension is model interpretation of the actual rendered interface, not human comprehension accuracy.

**Scaling to 50–100 sessions is not justified yet.** Broaden missions and assertion coverage, verify the complete Earth journey repeatedly under recorded conditions, and review failure attribution and evidence capture before spending that runtime. A single second pilot does not demonstrate general usability, accessibility conformance or production readiness. No paid inference, private source upload, CORE modification, production contribution, push or deployment occurred.

Private captures: `company/core-browser/20261018T024131Z-fd4185`, `company/core-browser/20261018T023931Z-2d06fc`, `company/core-browser/20261018T024005Z-d0b6ce`. Source-free metrics and manifest digests: [second-pilot-summary.json](evidence/second-pilot-summary.json). Raw inputs/output/screenshots/traces stay in ignored local evidence. Historical [first-pilot report](CORE_HQ_TESTING_REPORT.md) is retained separately.
