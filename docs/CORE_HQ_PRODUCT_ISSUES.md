# CORE V9.2 — evidence-backed development issues

CORE was not changed. These findings target immutable development commit `da51a1b9b3e5af0e8921fa3a9b9f5c9df68109b5`; they are not claims about public production.

## HQ-CORE-001 — mission controls depend on map readiness in the offline test environment

Status: reproducible environment-dependent failure; production impact unverified. Priority: investigate before expanding browser testing.

Actual trigger: open CORE Earth with external map/data services blocked, then open Problems & missions. The local problem registry and three San Francisco GeoJSON datasets return HTTP 200 with the exact CORE commit header, but the mission catalog does not become available. Explicitly waiting 25 seconds for CORE's own `civReady` state also fails. Default-motion and reduced-motion attempts both failed; no functions or data were replaced.

Evidence (all local, retained with screenshots, trace and capture checksums):

- `company/core-browser/20261018T020240Z-8137b3/session-01/report.json`: actual Problems & missions click; catalog not visible.
- `company/core-browser/20261018T020403Z-c32cb3/session-01/report.json`: readiness wait timed out.
- `company/core-browser/20261018T020513Z-99bde4/session-01/report.json`: same wait failure using default motion and blocked-request settings matching the earlier browser harness.

Source evidence supports a startup dependency: `src/earth/app.mjs` invokes `startCivilisation()` in the map's `load` handler; mission UI depends on `S.civ`. This is a plausible cause, not a complete root-cause diagnosis. Earlier navigation testing succeeded under its recorded timing; that historical success is retained and does not erase the newly observed failures.

Recommended CORE-team investigation: start the committed-data mission registry independently of external map availability; provide a truthful loading/unavailable state for mission controls; verify that the advertised no-3D path can operate when tiles are unavailable. Test normal, slow and blocked tile services, with keyboard and reduced motion. Do not treat online tile rendering as verified by these offline captures. No CORE fix has been implemented or verified here.

Further explicit checks: `20261018T020707Z-9be69f` tested CORE's built-in `quality=low` option and still timed out. Its read-only runtime diagnostic records `mapLoaded: true`, `styleLoaded: true`, `ready: false`, with no fatal message. A subsequent visible Zoom in control attempt did not find an actionable control and is recorded as a harness interaction failure, not a separate confirmed CORE defect. No further Earth retries are planned in this phase.

The direct conversation-room URL is independent of Earth map initialization. `company/core-browser/20261018T021120Z-7c5ee8` passed all nine critical browser actions there: dated sources loaded, a real agent was consulted, evidence dialogue and an unsupported-question refusal worked, and a synthetic consented mission contribution persisted only in its isolated browser. This success does not repair or validate the Earth entry path.

The earlier direct-room attempt `20261018T021013Z-7667ca` read a staged conversation before its final answer had appeared. The harness now waits for the rendered conversation to settle. That assertion failure is not classified as a CORE hallucination or unsupported-answer defect.
