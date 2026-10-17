# One-minute live demo

The produced artifact is [demo.webm](demo.webm): 60.000 seconds, 1440×900, captured from the actual browser interaction with experiment [`20261017-114030-02b57b`](../experiments/20261017-114030-02b57b.json). It shows mode distinctions, local checks, explicit live start, real agent activity, candidate comparison, evidence and promotion. It has no audio; the narration below is available for a voiced take.

Start with the existing credits and a fresh baseline:

```sh
python3 -m core_genesis.server --fresh
```

Open http://127.0.0.1:8080. The default is **Recorded Evidence** (zero API calls). Select **Live Evolution**, then click **Start live evolution** while recording. One cycle uses at most six physical requests, including retries. Saved runs are clearly labeled replay.

- **0–10s:** “CORE GENESIS evolves an AI team's strategy. Local tests and genuine recorded evidence cost zero API calls. Live mode is explicit and budgeted.” Show the mode selector.
- **10–25s:** “The Executor attempts repairs. Deterministic tests expose failures. The Observer sees development evidence; the Scientist proposes two competing workflow mutations.” Point to live activity and tool chips.
- **25–40s:** “Both candidates face development incidents. Only the development winner reaches the held-out suite. The Scientist never sees held-out results.” Show the matrix.
- **40–50s:** “Promotion requires strict improvement on both suites, without a single regression. If this run fails, it rolls back. The result is computed, not voted on.” Show the actual decision.
- **50–60s:** Click a result cell. “Here is the exact patch, behavioral assertions, token usage and latency. Export the evidence and replay the checks without an LLM.”

Latency and outcomes vary. Narrate actual results only. A rejection validly demonstrates the gate. If inference takes longer than the recording window, finish the run and record another take using another **live** run.

Reference experiment `20261017-111232-160e6d` is a real historical run: 0/6 baseline, 2/6 candidate, promotion, 18 calls, 8,905 tokens. It predates the six-request policy and does not substitute for a new live run.

## Submission

- Source: https://github.com/vincentleg/core-genesis
- Track: Version N+1
- Name: CORE GENESIS — EVOLUTION ZERO
- Tagline: The AI Team That Rewrites How It Thinks.
- Include source, reproduction commands, and the one-minute recording.
- Describe the six-case simulator honestly; it demonstrates workflow evolution, not general real-world incident repair.
