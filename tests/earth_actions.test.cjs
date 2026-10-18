const {test}=require('node:test'),assert=require('node:assert/strict');
const {validateAction}=require('../scripts/core_earth_actions.cjs');
test('only canonical observed Earth controls can execute',()=>{const observed=[{name:'zoom_in'}];assert.equal(validateAction('zoom_in',observed),'.maplibregl-ctrl-zoom-in:visible');assert.throws(()=>validateAction('zoom_out',observed),/unavailable/);assert.throws(()=>validateAction('ZOOM_IN',observed),/unavailable/);assert.throws(()=>validateAction('delete_storage',observed),/unavailable/);});
