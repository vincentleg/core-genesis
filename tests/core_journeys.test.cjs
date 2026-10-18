// Catalog and triage invariants only; not CORE browser evidence.
const {test}=require('node:test'),assert=require('node:assert/strict');
const {catalog,journey}=require('../scripts/core_journeys.cjs');
const {classifyFailure}=require('../scripts/core_failure_classification.cjs');
test('unknown variants fail closed; exactly thirty explicit browser journeys',()=>{assert.equal(catalog.length,30);assert.equal(new Set(catalog.map(v=>v.id)).size,30);assert.throws(()=>journey('my-core','unknown'));assert.equal(journey('bilingual','roundtrip').entry,'room');});
test('triage never automatically confirms CORE or human UX defects',()=>{assert.equal(classifyFailure('browser','panel intercepts pointer events'),'hq_harness_defect');assert.equal(classifyFailure('browser','strict mode violation'),'hq_harness_defect');assert.equal(classifyFailure('evaluation','TimeoutError'),'model_evaluation_failure');assert.equal(classifyFailure('browser','ERR_CONNECTION_RESET'),'environment_network_limitation');assert.equal(classifyFailure('browser','Timeout 6500ms exceeded'),'needs_triage');assert.equal(classifyFailure('browser','new unknown error'),'needs_triage');});
