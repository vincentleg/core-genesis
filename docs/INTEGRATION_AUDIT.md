# Department integration review — October 17, 2026

These repositories were inspected as references. None was blindly cloned, installed, executed or connected to credentials. This is a bounded source review, not a security certification.

| Repository | License / maintenance evidence | Requirements and risks | Decision |
| --- | --- | --- | --- |
| [Pendpost](https://github.com/pendpost/pendpost) | MIT. [Package](https://github.com/pendpost/pendpost/blob/develop/package.json) declares v2.7.0 and Node 20+. [Security policy](https://github.com/pendpost/pendpost/blob/develop/SECURITY.md) describes an early, part-time project with fixes on the latest release line. | Broad scheduler, subprocess publishing engines and OAuth/token handling. Its documented approval, origin checks and Meta circuit breaker are useful patterns; connecting it expands authority considerably. Official platform apps and credentials remain necessary. | No runtime dependency. Native draft-only queue and CEO review implemented. No accounts, publisher or personal credentials connected; LinkedIn explicitly excluded. Future adapter requires a separate audit and CEO authorization. |
| [Tunnel](https://github.com/krish1905/tunnel) | README states proprietary software, all rights reserved. Public source availability does not grant reuse rights. | Full market-research application; copying is inappropriate without a suitable license. | No code reused or dependency installed. |
| [OpenPersonaSimulation](https://github.com/npmiaman/OpenPersonaSimulation) | Repository exposes MIT licensing and a substantial commit history; maintenance quality is not inferred from commit count. | Python package and broader simulation/studio stack. README quickstart requires an OpenAI key, outside this project's pinned Crusoe-only spending scope. | No dependency. Native, independent Nemotron persona contexts are smaller and use the existing budget manager. |
| [crewai-focus-group](https://github.com/MxMnr/crewai-focus-group) | README identifies MIT licensing. Long-term maintenance and security posture not independently established. | CrewAI orchestration would duplicate the existing controller and introduce a separate dependency/model configuration surface. | No dependency; role separation implemented directly. |
| [your-ai-focus-group](https://github.com/itsrouk/your-ai-focus-group) | MIT. README documents a lightweight Next.js application. | Node 18+, Gemini key and a separate frontend/runtime. Synthetic Likert scores must not become real-user validation claims. | No dependency. Five real independent synthetic calls, structured criticism and explicit disagreement replace unsupported success metrics. |

Only general workflow ideas informed the independent implementation. No third-party source is copied. Consequently no upstream runtime integration is claimed.

## Implemented boundaries

- Five synthetic perspectives run as five separate real Nemotron calls. They do not see each other's responses.
- Synthetic criticism is labeled as hypothesis; it is not beta-user feedback, market validation or a promotion criterion.
- Growth drafts are based on cited proposals, not fictional shipped developments.
- CEO review records approval for manual export only. No publishing capability exists.
- Official account creation is a manual, CEO-authorized setup process. No CAPTCHA, verification or access restriction is bypassed.
- No impressions, follower counts or engagement metrics are displayed without source data.
- The 100-person panel is an explicit future batch plan, not an implemented or measured research result.
- External provider availability and configuration requirements were reviewed from documentation; installed or operational third-party integrations are not implied.

## Product Testing update — actual local browser execution

Rechecked Tunnel and OpenPersonaSimulation from their public README/license pages. Tunnel still states proprietary/all rights reserved: no source reuse. OpenPersona remains MIT and explicitly distinguishes synthetic reactions from real market behavior; its broader simulation stack is unnecessary for this bounded pipeline.

[Stagehand](https://github.com/browserbase/stagehand) is MIT and documents local browser support. Its README demonstrates model-directed browser operations with separate model credentials. Direct Crusoe/Nemotron compatibility was not verified, so no Stagehand integration is claimed. Installing it would duplicate existing browser tooling and add an unneeded model adapter.

Decision: use the already-working local **Playwright** package and Chrome. The optional development dependency is pinned in package-lock.json. Three deterministic browser testing actors run actual sessions against the generated Python application; their scripted actions are not represented as LLM reasoning. They capture screenshots, browser errors, actual task completion and reproducible failures. There is no Browserbase cloud account, remote browser service or extra model cost.

Synthetic research now supports 5–100 perspectives per campaign, frozen artifact context, five calls per explicit batch, single concurrency and the existing global budget. A 100-target campaign is not a claim that 100 evaluations ran; the UI reports actual completed reviews and per-batch usage. No automatic batch continuation occurs.

The bounded repair controller reproduces a browser failure, permits one restoration of audited scaffold files and reruns the identical cases plus real regression tests. It cannot autonomously invent or execute code to repair arbitrary bugs. Unresolved failures remain visible. Browser outcomes are queued as workflow evidence for Evolution Lab; they do not bypass independent promotion gates.
