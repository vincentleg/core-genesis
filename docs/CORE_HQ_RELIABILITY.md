# CORE HQ focused reliability follow-up

This is the checkpoint at `8f8527b`, before the combined smoke and second pilot. Those pending checks have since run; see [actual later results](CORE_HQ_SECOND_PILOT.md). Historical validation limits below describe that checkpoint.

The ten-attempt pilot is preserved by local commit `0d27d7d`. This pass did not rerun it or modify CORE. Target remains `v9.2/earth-first`, commit `da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5`. Public production is a separate, older version with unverified SHA.

## Three evaluation timeouts

The first three personas completed the recorded location/dialogue/contribution browser assertions before their 40-second evaluation calls timed out. They are **browser-task passes with model-evaluation failures**, not three demonstrated product failures. Their total runtimes were 77.240, 73.708 and 75.993 seconds. Initial rendered observations were 8,091 characters. Old nonstream requests saved only successful results: failed calls have no partial output, inference timings or token counts. The exact cause (queue/load, prompt processing, decoding or connection delay) cannot be reconstructed.

The continuation shortened observations and raised the cap to 90 seconds; all six evaluations returned. Both variables changed, so neither improvement alone is proven causal. New measurements make a subsequent diagnosis possible; no historical missing usage was invented.

## Implemented handling

- Local Ollama streaming only; each attempt saves its input, partial output, status, elapsed time, first chunk/content timing, returned token counts and Ollama load/prompt/decode timings in ignored private evidence.
- At most two attempts per planning/evaluation stage: 60 seconds then 25 seconds, clamped to a 90-second stage limit and remaining session work time. Retry needs at least eight seconds left. Timeouts, transient transport/HTTP failures and malformed structured output can retry; permanent HTTP errors, cancellation and exhausted budgets cannot. No browser action or contribution is retried by this mechanism.
- Reports persist separate planning/browser/evaluation stages. A failed evaluation retains successful browser tasks, identifies the failure stage, and reports unknown usage separately. JSON reports/attempt records use atomic replacement.
- SIGTERM cancels inference, lets HQ finalize traces, and stops new sessions. Python reserves eight seconds inside its watchdog budget for graceful termination and final kill. A finalized summary is retained; otherwise saved session reports are recovered, including partial stages. Unreadable records are identified rather than silently counted as successful.
- The 180-second session and 30-minute pilot limits remain. Retries consume those budgets; they never extend them. Existing evidence is untouched.

## Offline Earth diagnosis and test conditions

Read-only capture `company/core-browser/20261018T023154Z-43eb7d` used real headless Chrome, SwiftShader WebGL2, 1440×1000 viewport, CORE's built-in `world.html?quality=low`, an immutable loopback Git-blob server, and all external requests blocked. No injected startup call, replaced data, fake tile or source modification was used. Observer listeners only recorded map events.

Before any explicit screenshot, `map.loaded()` and style readiness were true, while CORE `ready` and `civReady` were false and no map `load` event had been observed. Disabling screenshot animations did not immediately recover readiness. After a real wheel gesture at (1200,450), deltaY −120, the observer saw `load` and both CORE flags became true. This is a single observed recovery, not proof that the wheel is the sole cause or that it always works. Source inspection locates mission startup inside CORE's map `load` handler; the renderer/scheduling cause needs CORE-team investigation.

The subsequent real Zoom in button click timed out because the control was hidden behind the landing state. That is a harness interaction failure, not an additional product defect. The harness now uses the observed wheel gesture before waiting for CORE readiness; it does not force a hidden click or alter application state. The full Earth-to-mission product journey has **not** passed this revised harness yet.

For a comparable **offline initialization** test, retain the pinned commit, entry URL, browser/GPU flags, viewport, isolated context, local dataset commit headers, external-request blocking, real gesture, and observed `ready` + `civReady` checks. Never use `map.loaded()` alone as application readiness. Capture blocked requests, page/console errors, screenshots and trace. The diagnostic completed in 22.474 seconds with zero model calls. The after screenshot shows an untextured blue globe: recovered mission initialization is not successful imagery rendering.

**Reliable textured globe testing is not established in this offline setup.** Actual style/vector tiles (`tiles.openfreemap.org`), NASA GIBS imagery (`gibs.earthdata.nasa.gov`), and terrain dependencies when selected (`s3.amazonaws.com` in the source) require working network access, browser CORS/resource delivery and WebGL. Under this task's no-external-disclosure constraint they stay blocked. An explicitly authorized network environment or a separately verified faithful offline asset setup is needed to test those resources; neither was enabled. No paid service or key is required by the current local path. Record successful actual responses, usable rendered geography, application readiness and mission interactions before calling an online globe test reliable. Do not claim imagery passed because the readiness flags did.

## Targeted validation and next pilot

- Eight streaming/retry unit tests passed with explicitly injected transport fixtures; these are not CORE sessions.
- Four pilot safety-gate tests and two watchdog/recovery tests passed.
- One real local Ollama transport smoke passed in 7.208 seconds, 123 prompt + 77 output tokens, $0 paid API charges. Its input was explicitly fixture UI text, not a browser observation; zero browser sessions are credited. Private capture: `reliability-inference-smoke-1792290867204`.
- One actual direct-room product regression passed all nine actions, separate browser-pass reporting and finalized trace in 18.733 seconds process runtime; no inference. Capture: `20261018T023512Z-53d7d1`. This is a scripted preflight, not a new AI-pilot participant/session.
- Syntax and whitespace checks passed. Original pilot and historical evidence hashes remain unchanged. No full pilot or CORE unit suite ran.

A second bounded **direct-room** ten-session pilot is prepared, subject to one short end-to-end AI browser smoke of the revised combined controller on the same pinned target. Streaming was verified with real local inference and browser tools independently; their revised combination and real timeout recovery under model load remain unverified. Do that single gate before the second pilot, retain the three-minute/30-minute caps, and report browser and evaluator outcomes separately. Do not start a globe-inclusive pilot until its complete entry journey passes and the required rendering environment is established. The system is not ready for 100+ sessions. Human participants remain zero.

Source-free diagnostic/checksum references: [reliability evidence](evidence/reliability-summary.json). Existing screenshots, traces and model records remain private and local.
