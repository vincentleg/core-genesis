# Prepared 30-session CORE campaign — not executed

The [plan](../testing/core-v92-30-campaign.json) has **30 unique journey variants, zero actual sessions, zero humans, and execution disabled**. It targets read-only CORE V9.2 commit `da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5`, not public production. No ten-session pilot was repeated.

| Journey | Three distinct variants |
| --- | --- |
| First-time exploration | What works today; navigate Create; navigate My CORE |
| Earth exploration | Actual zoom in; zoom out; switch real/CORE layers |
| Location/problem discovery | Mission findings; place search; keyboard no-3D entry to a recorded mission |
| Agent dialogue | Consult roster agent; inspect engine exchanges and dates; causal uncertainty question |
| Contribution | Consented observation; research-question type; empty-form validation |
| My CORE | Empty/local status; contribution recovery after navigation/reload; follow mission and recover it |
| French/English | Heading round trip; French conversation; persist language across navigation/reload |
| Keyboard | Skip link focus; Tab/Space contribution submission; keyboard language selection |
| Error handling | Unsupported evidence question; invalid pseudonym; locked private-vault feedback |
| Investor impression | Actual Progress metrics; manifesto navigation; current scope versus My CORE impact |

Each case defines a persona, objective, initial route, concrete browser success criteria, timeout and a single-session invocation. These are real Playwright controls/assertions, not generated opinions. Local Qwen can parameterize the predefined browser tools; this is bounded control, not unrestricted autonomous browsing. AI UX notes are heuristics requiring human validation. Returning JSON or matching a quote is not evidence of accurate human comprehension.

The existing runner/orchestration, immutable Git server, local inference adapter, isolated contexts, private evidence and budget cleanup are reused. New `--suite journey --scenario <id> --variant <id>` execution is restricted to **one session**. It rejects unknown cases and multi-session invocations before CORE inspection or browser launch. No 30-session executor exists; the plan cannot silently execute. The old ten-session runner cap remains.

## Limits and evidence

Prepared limits: one browser session at a time; 180 seconds per session with 12 seconds reserved for evidence; 60 minutes for the future whole campaign. Two inference stages, each with at most two attempts, 90 seconds per stage, 60/25-second attempt limits clamped to remaining work time. Ollama loopback only, existing `qwen3:8b`, no downloads, no paid provider, cost ceiling $0. Context/output caps and returned/unknown token usage are in the plan. Hardware/electricity cost is unmeasured.

Every future capture must retain exact CORE commit and requested ref, HQ code/catalog hashes, actual actions/assertions, page/console/HTTP/request failures, screenshots or explicit capture failures, trace or finalization failure, model input/output/partial streams, separate planning/browser/evaluation results, runtime, reported usage, unknown usage and checksums. Raw observations stay in ignored `company/`; source-free summaries can be committed. Synthetic fixtures stay in fresh local contexts. Public-map GETs require the explicit narrow `public-assets` option; other requests, WebSockets and server mutations remain blocked.

SIGTERM handling and watchdog recovery are reused for single sessions. `core_genesis.browser_campaign.pending_sessions` provides bookkeeping for a future scheduler: stop after the original deadline and never replay completed, failed or interrupted IDs. It validates IDs/commit and rejects duplicate records. This helper cannot launch anything. The future scheduler still needs implementation and verification of the global 60-minute cap, durable checkpoint integrity, all evidence gates and stop/resume orchestration. Those are explicit execution blockers, not completed capabilities.

## What has actually been checked

Targeted checks outside the campaign passed: `bilingual:roundtrip` (3 actions, 8.926s), `my-core:contribution` (7 actions, 18.741s), `keyboard:skip` (2 actions, 8.458s). They used real browsers with zero inference and are **not campaign sessions**. Their captures are listed in [verification evidence](evidence/earth-and-journeys-summary.json). Other new variants are implemented but unvalidated, and none of these journey variants has a completed AI campaign run.

The single requested AI Earth verification failed at an obscured zoom button. Earth initialized and imagery loaded, but the catalog intercepted the click. The corrected mission selector was never reached. The future sequencing fix has no AI validation. See [Earth outcome](CORE_HQ_EARTH_AND_JOURNEYS.md). This blocks a claim that the prepared campaign is ready to launch, and scaling to 50–100 remains unjustified.

Preparation is repeatable without network or inference:

```sh
python3 scripts/prepare_core_campaign.py --commit da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5
```

This writes a plan only. No campaign execution is authorized by this document.
