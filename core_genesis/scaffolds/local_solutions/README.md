# CORE Local Solutions — First Brick

A working, isolated Python standard-library prototype built inside CORE HQ. The original CORE repository was inspected read-only and was not modified.

Run from this directory:

    python3 app.py --port 8091

Open http://127.0.0.1:8091. Submit a local problem, open its card, propose a solution and inspect **PENDING HUMAN REVIEW**. A person can explicitly approve or reject a local proposal. No real-world action is authorized, even after local approval.

Run actual tests (including real HTTP startup, problem → solution → read-back, validation and cross-origin rejection):

    python3 -I verify.py

`build-report.json` captures the Operations test process, real stdout/stderr, exit code, source hashes and acceptance results. `spec.json` contains real Nemotron-selected product choices, including introduction, location requirement and enforced text limits. Source code comes from a predefined, audited scaffold; this is bounded configuration-driven implementation, not unrestricted autonomous code generation. `research-brief.json` traces the design to the actual inspected CORE commit.

Records persist in local `data/records.json`. No database or external service is required. Do not enter sensitive personal data. There is no authenticated identity, moderation, encryption at rest, production hosting or production authorization system. Optional HTTPS evidence links are stored, never fetched. User text renders with `textContent`, never HTML.

Public hosting provides a separately labeled browser-only preview with local browser storage; it does not run Python or fresh inference. Download the source archive to run the fully tested Python application. Synthetic reviewer feedback is not evidence of actual user satisfaction.
