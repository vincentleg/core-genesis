# CORE HQ

CORE HQ (CORE Headquarters), formerly CORE GENESIS, is the AI-native company behind **CORE — Creation Of Reborn Earth**.

CORE HQ currently has **read-only** access to CORE. It can inspect commit-pinned source, run real local browsers, retain evidence, and prepare proposals for human review. It cannot change CORE, merge, push, or deploy.

## Inspect the real product

```sh
python3 scripts/inspect_core.py
python3 scripts/inspect_core.py --repo ~/core --ref v9.2/earth-first
# --ref also accepts an existing branch or commit. Missing refs fail; never fall back to main.
```

Default: `~/core`, branch `v9.2/earth-first`. Full eligible source files are read from immutable Git objects, with a complete tracked-file inventory, source hashes, selection limits, architecture groups and checkout status. Private source bodies stay in ignored `company/` storage. This is source inspection, **not a test run**.

The founder reports that local V9.2 has not been deployed. **https://creationofrebornearth.com serves an older CORE version.** Production's exact commit is unverified. Local development and production are separate targets.

## Real local browser testing

The existing pinned Playwright installation is reused. Chrome or an installed Playwright Chromium browser is required. No automatic installs, model downloads, cloud browsers, paid requests, or recruitment.

```sh
# Deterministic browser baseline, not an AI agent:
python3 scripts/test_core.py
# Probe localhost only, without running inference:
python3 scripts/test_core.py --check-models
# Genuine model-directed actions using an already installed local Ollama model:
python3 scripts/test_core.py --mode local-agent --model qwen3:8b
```

The harness serves **real CORE files from the requested commit** over loopback, with a commit header. It never checks out or writes to `~/core`. Each fresh browser context records actions, screenshots, a Playwright trace, errors, pages, timing, completion counts and inference usage. External browser network and server mutations are blocked. Map tiles and live APIs therefore have offline limitations. No claim of full product validation follows from a passing navigation check.

```sh
# Only after a successful single session in the same mode, commit and model:
python3 scripts/test_core.py --mode local-agent --model qwen3:8b --sessions 10 --execute-pilot
# Evidence-linked review proposals; no CORE changes:
python3 scripts/review_core_session.py company/core-browser/<run>/session-01
# Review a trace locally:
npx --no-install playwright show-trace company/core-browser/<run>/session-01/trace.zip
```

A pilot stops on the first failed session. Each session is bounded to 12 model calls and 12 decisions; the process has a runtime limit. Cost ceiling: **$0 paid inference**. Ten sessions are prepared; hundreds are not authorized. See [browser design, limitations and research](docs/CORE_HQ_TESTING.md).

## Human testing

Human participants are separate from AI agents and scripted browser contexts. Map a consented platform export to [the template](docs/templates/human-study.json), then validate it locally:

```sh
python3 scripts/ingest_human_testing.py study.json --output company/human-testing/study-001.json
```

Actual participant rows, tasks, completion rates, feedback, issues, participation evidence and consent evidence are required. Structural validation cannot establish the authenticity of external records; human review is required. No participants have been recruited or inferred.

## CORE HQ website and retained infrastructure

```sh
python3 -m core_genesis.server
# Or serve existing static assets (zero inference):
python3 -m http.server 8090 --bind 127.0.0.1 --directory public
```

The Python package, existing API headers, filenames, repository and domain identifiers remain compatible. Current branding is CORE HQ. The campus replay is explicitly historical hackathon evidence, including the separate Local Solutions prototype and synthetic audience campaigns. These are not CORE V9.2 browser validation. The new CORE HQ status page is `public/hq.html`.

The existing Crusoe/NVIDIA Nemotron client, request ledger, agent orchestration, replay, evaluation and budget infrastructure remain. Paid inference is **disabled by default**, even if a key exists. A future approved inference run would require `CORE_HQ_ALLOW_PAID_INFERENCE=approved` and still use the existing request budget. Local CORE source transmission to that workflow is separately blocked; enabling paid inference does not authorize private source sharing.

The old prototype builder remains available for historical compatibility; it is not the current CORE improvement workflow. Default company retrieval now selects local CORE; its external-model reasoning step rejects local source rather than transmitting it.

## Historical evidence and resource migration

[Original hackathon README](docs/hackathon/README.md), `mission-evidence/`, `experiments/`, artifact runs, videos and recorded JSON evidence are retained. Other pre-HQ documents under `docs/` describe the hackathon implementation and its historical limitations. Existing static evidence was not rebuilt or rewritten during the rename.

[External migration plan](docs/CORE_HQ_MIGRATION.md): local directory, GitHub repository, Vercel project and production domain remain unchanged. No push or deployment is authorized.
