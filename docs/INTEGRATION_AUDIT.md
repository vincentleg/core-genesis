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
