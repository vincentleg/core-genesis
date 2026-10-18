# CORE HQ — product testing report

CORE: `v9.2/earth-first` at `da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5`. CORE HQ pilot preservation commit: `0d27d7d` (foundation `5dc8a4e`). No CORE changes, push, deployment, external disclosure or paid APIs.

## Actual scope and results

Real Chrome tested the existing direct conversation room for the San Francisco housing/resilience mission. Local qwen3:8b selected a browser task and supplied the question or synthetic contribution text; Playwright operated actual controls. This is a bounded tool controller. CORE’s own conversation answers came from its deterministic cited engine, not an autonomous language model.

**10 persona/browser attempts: 9 completed, 1 incomplete. 9 executed sessions passed their assigned product checks; 6 also completed the comprehension evaluation.** Three early evaluations timed out. The environmental-researcher attempt was interrupted after planning, before its selected task; it was not rerun. The six remaining personas continued in a second preserved capture under the original deadline.

| AI persona | Verified product checks | Evaluation / completion |
| --- | --- | --- |
| First-time visitor | location, dialogue | completed checks; evaluation timeout |
| Nontechnical user | location, contribution | completed checks; evaluation timeout |
| Scientific researcher | location, dialogue | completed checks; evaluation timeout |
| Environmental researcher | none executed | incomplete; interrupted before task |
| Student | location, dialogue | completed; evaluation returned |
| Urban planner | location | completed; evaluation returned |
| Skeptical investor | location, dialogue | completed; evaluation returned |
| Accessibility-focused user | location, contribution | completed; evaluation returned |
| Community contributor | location, contribution | completed; evaluation returned |
| Technical power user | location | completed; evaluation returned |

Verified interactions: dated committed datasets delivered and displayed; four agent consultations with question/answer and unsupported-question refusal checks; three consented synthetic mission contributions with consent rejection, reload persistence and independent-context isolation. Contributions remained in disposable local browser storage. The encrypted vault, live upstream freshness and analytical calculations were not independently validated.

**Runtime:** 11.48 minutes wall time, including the continuation pause, within the original 30-minute budget. Longest session: 77.2s, below 180s. **Inference:** 16/19 calls returned; 29,211 prompt + 2,276 output tokens reported. Usage for three interrupted evaluation calls is unknown. **Paid API cost: $0**; hardware/electricity unmeasured.

## Failures and reproducible findings

- **Earth startup has an offline initialization defect.** Local records returned 200, while a diagnostic showed map/style loaded but CORE readiness false. Waiting and CORE’s low-quality option did not recover it in the original captures. A subsequent focused diagnostic recovered application readiness after a real wheel gesture; imagery stayed unavailable, and the complete Earth journey remains unverified. The direct-room success does not validate the Earth journey. See [CORE issue HQ-CORE-001](CORE_HQ_PRODUCT_ISSUES.md) for captures and reproduction; production impact is unverified.
- **Controller evaluation needed correction.** Three model evaluations exceeded forty-second caps after their browser tasks passed; the old records cannot isolate inference load, processing or decode delays. The remaining personas used shorter observed context and up to ninety seconds within their session budgets. A premature staged-dialogue assertion was fixed in HQ and then passed. CORE was never patched.
- **AI comprehension remains noisy.** Six evaluations returned; 2/6 contribution-visibility answers explicitly mentioned browser/local/nonpublication scope. This is a text-presence check, not human comprehension accuracy. At least one claimed missing source dates while quoting a retrieval date. Such complaints are retained as hypotheses, not confirmed CORE defects.
- Optional local backend-state requests returned 404 and remain in the logs. External map requests were blocked. Online map rendering, production behavior, live CORE model wording and real-world impact were not tested.

## Recommendations and scale decision

CORE team: investigate map-independent mission initialization and truthful loading/unavailable controls. Retest the Earth entry on an exact new commit after any approved fix. HQ: improve semantic review of UX claims and broaden task/mission coverage before scaling.

**Not ready for 100+ sessions.** The bounded local pipeline works, but Earth entry, evaluation reliability and coverage of only one mission remain material limits. **Actual human participants: 0.** AI personas and model interpretations are separate from human beta testing.

## Evidence

Preservation review verified every file against the recorded pilot capture hashes, and checked the archived hackathon README hash. No historical capture was rewritten.

Private aggregate: `company/core-pilots/20261018T021206Z-d6b035/aggregate.json`. Immutable captures: `company/core-browser/20261018T021740Z-1e1b47`, `company/core-browser/20261018T021206Z-d6b035`. Retained: 41 screenshots and 9 finalized traces. All nine completed task sessions have traces. The interrupted fourth attempt lacks a finalized trace, and two initial screenshots timed out; these capture failures remain in the logs. Returned decisions and capture hashes are retained.

Reproduce critical interactions: `python3 scripts/test_core.py --suite product --entry room --ref da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5`. The [handoff](CORE_HQ_HANDOFF.md) records gates, limitations and Git state. Report generation runs no additional browser sessions.


## Reliability follow-up (separate from pilot metrics)

[Focused results](CORE_HQ_RELIABILITY.md): streaming inference preserves partial results and timing; one bounded retry consumes the existing deadline; reports separate browser-task success from evaluation failure; watchdog cleanup retains finalized or recoverable evidence. Eight inference tests, four safety tests and two recovery tests passed. A real 22.474-second offline Earth diagnostic observed recovery after a wheel gesture (untextured globe), and a scripted room regression passed nine actions in 18.733 seconds. One local inference transport fixture passed in 7.208 seconds, reporting 123 input + 77 output tokens. These checks cost $0 in paid APIs and add **zero AI pilot sessions and zero human participants**. Original pilot counts are unchanged.

A second direct-room pilot is prepared pending one short combined AI/browser smoke of the revised controller. Globe-inclusive testing needs a verified entry journey and authorized usable map resources; 100+ scaling remains premature. CORE was read-only throughout. No full pilot rerun, push or deployment occurred.
