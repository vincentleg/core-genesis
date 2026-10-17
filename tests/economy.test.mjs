import test from 'node:test';
import assert from 'node:assert/strict';
import {planProcurement} from '../web/economy.js';

test('unit-price calculation selects the cheapest feasible scenario',()=>{
 const decision=planProcurement({budget:1});
 assert.equal(decision.recommended_action.alternative_id,'shared');
 assert.equal(decision.recommended_action.estimated_cost_usd,.4);
 assert.equal(decision.alternatives.find(a=>a.id==='batch').rejection,'Insufficient scenario capacity');
});
test('budget changes defer a recommendation without granting spending authority',()=>{
 const decision=planProcurement({budget:.1});
 assert.equal(decision.recommended_action.alternative_id,null);
 assert.equal(decision.recommended_action.name,'Defer procurement');
 assert.equal(decision.execution_enabled,false);
 assert.equal(decision.human_approval_required,true);
 assert.equal(decision.budget_constraints.changes_real_budget,false);
});
test('priority changes choose a different feasible alternative',()=>{
 assert.equal(planProcurement({budget:1,priority:'reliability'}).recommended_action.alternative_id,'burst');
 assert.equal(planProcurement({budget:.5,priority:'reliability'}).recommended_action.alternative_id,'shared');
 assert.equal(planProcurement({budget:1,priority:'latency'}).recommended_action.alternative_id,'burst');
});
test('reduced demand makes the explicitly synthetic batch scenario feasible',()=>{
 const decision=planProcurement({budget:1,demand:3});
 assert.equal(decision.recommended_action.alternative_id,'batch');
 assert.equal(decision.recommended_action.estimated_cost_usd,.12);
 assert.match(decision.alternatives.find(a=>a.id==='batch').price_basis,/Synthetic/);
});
test('invalid financial inputs fail closed',()=>{
 for(const args of [{budget:-1},{budget:NaN},{budget:Infinity},{budget:101},{demand:0},{demand:101},{priority:'buy-now'}])assert.throws(()=>planProcurement(args));
});
