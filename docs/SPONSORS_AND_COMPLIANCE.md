# Sponsor and compliance evidence

Verified October 17, 2026. This is a technical evidence checklist, not a claim that organizers have approved eligibility or submission.

## Genuine integrations

- **Crusoe Managed Inference:** actual reasoning backend. The original dependency-free `core_genesis/crusoe.py` remains unchanged. Production inference entry points use `RequestBudget`; the original smoke script now uses the same wrapper.
- **NVIDIA Nemotron:** actual model `nvidia/Nemotron-3.5-Lightning-30B-A3B` served by Crusoe. Model identifiers, HTTP status, real token usage, latency and estimated costs are recorded. Architect, Executor, Observer and Scientist all use real reasoning; Observer and Scientist share a cost-saving request under the current policy.
- **You.com:** not integrated. No You.com key is present. The public event page does not provide a verified event-specific API-credit procedure; unrelated historic credit promotions are not assumed to apply. No retrieved evidence is invented.
- **OpenShell / NemoClaw:** investigated, not integrated. [Official OpenShell setup](https://docs.nvidia.com/openshell/latest/get-started/quickstart) introduces a gateway and sandbox runtime. Current repairs are allowlisted in-memory JSON configuration changes, so adding executable-agent infrastructure provides little value for this slice. No infrastructure was installed for a sponsor claim.
- **Switchyard:** not integrated. A single pinned model makes routing unnecessary and simplifies verified pricing and accounting.

## Sources and verified limits

- [Official event listing](https://events.cerebralvalley.ai/e/crusoe-recursive-agents-hackathon): October 17, San Francisco, in person, approved attendees, teams up to four, hosted by Cerebral Valley and Crusoe. The page describes persistent agent teams and Crusoe-hosted open models including Nemotron.
- [Official Crusoe pricing](https://www.crusoe.ai/cloud/pricing): Serverless Inference → Nemotron 3.5 Lightning. Input $0.05/1M tokens, output $0.20/1M, cached $0.03/1M. Estimates conservatively ignore cached discounts.
- [Crusoe model documentation](https://docs.crusoecloud.com/serverless-inference/index.html) and [NVIDIA model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16): confirm the Lightning family and up-to-1M context. Unknown historical requests reserve the full 1,048,576-token context plus bounded output, not guessed actual usage.

The public event listing does **not** publish the detailed Version N+1 track, source-code timing requirements, video specifications or submission portal. These constraints come from the project owner's instructions and are followed here; organizer verification remains outstanding until their detailed rules are available. The owner's 5 PM Pacific deadline is the working deadline.

## Implementation checklist

- Target: Version N+1, per owner-provided track instructions.
- All newly implemented engine, benchmark, Arena, budgeting and evidence tooling were developed October 17, 2026 in this repository.
- The Crusoe client and smoke integration already present at handover were reused and disclosed. No code or functionality from the separate CORE project was imported or modified.
- MIT license retained. Repository https://github.com/vincentleg/core-genesis was confirmed PUBLIC through GitHub's API before the source push.
- Deterministic tests verify repairs and the promotion/rollback gate; separate held-out fixtures are excluded from mutation prompts.
- Live request limit, persistent $2 estimated cap, retry accounting, one concurrent request, fixed token bounds, and fail-closed pricing are implemented and covered by network-disabled tests.
- Local Test and Recorded Evidence make zero new external API calls. Browser read/poll/refresh does not trigger inference.
- Current production runs use at most six physical requests. Earlier higher-request evidence is kept transparently as historical, never presented as satisfying the newer request policy.
- No purchases, paid hosting, automatic top-ups, generated shell execution or production repairs.
- Credentials are never sent to the browser, model prompts, screenshots or videos. A source/artifact secret scan must pass before Git push.

## Submission artifacts

- Current-policy evidence: `experiments/20261017-114030-02b57b.json`, six requests, 7,061 reported tokens, estimated $0.0005665, verified promotion.
- Actual 60-second screen recording: `docs/demo.webm`, 1440×900, silent.
- Source/artifact scan against the configured Crusoe secret passed before publication.

## Submission items requiring final verification

Organizer-specific track/rules confirmation, participant approval/team eligibility, and actual submission upload. Do not claim organizer approval or completed submission without portal confirmation. The owner has been asked for the detailed rules/credit instructions; the public event listing does not supply them.
