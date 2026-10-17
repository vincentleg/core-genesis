/** Deterministic planning simulation. Never connects to payment or provider APIs. */
export function planProcurement({budget=1,demand=5,priority='cost'}={}){
 if(!Number.isFinite(budget)||budget<0||budget>100||!Number.isFinite(demand)||demand<=0||demand>100)throw Error('Planning inputs out of bounds');
 if(!['cost','reliability','latency'].includes(priority))throw Error('Unknown decision priority');
 const need={description:'Plan additional inference capacity for the company research workload.',million_tokens:demand,input_share:.8,output_share:.2};
 const catalog=[
  {id:'shared',name:'Shared Nemotron inference',input:.05,output:.20,fixed:0,capacity:8,reliability:92,latency:72,
   price_basis:'Published Crusoe unit-price snapshot, verified 2026-10-17; not a live quote.',source:'https://www.crusoe.ai/cloud/pricing',assumptions:'Capacity, reliability and latency are planning fixtures, not provider guarantees.'},
  {id:'burst',name:'Redundant burst pool · scenario',input:.09,output:.30,fixed:.25,capacity:12,reliability:99,latency:95,
   price_basis:'Synthetic comparison fixture. Not a purchasable offer.',source:'Local deterministic scenario catalog v1',assumptions:'All prices and service attributes are fictional planning inputs.'},
  {id:'batch',name:'Off-peak batch pool · scenario',input:.025,output:.10,fixed:0,capacity:4,reliability:80,latency:35,
   price_basis:'Synthetic comparison fixture. Not a purchasable offer.',source:'Local deterministic scenario catalog v1',assumptions:'All prices and service attributes are fictional planning inputs.'}
 ];
 const alternatives=catalog.map(option=>{
  const cost=Math.round((demand*(need.input_share*option.input+need.output_share*option.output)+option.fixed)*10000)/10000;
  const feasible=cost<=budget&&option.capacity>=demand;
  const score=priority==='cost'?-cost:priority==='reliability'?option.reliability:option.latency;
  return {...option,estimated_cost_usd:cost,feasible,score,rejection:cost>budget?'Exceeds scenario budget':option.capacity<demand?'Insufficient scenario capacity':null};
 });
 const winner=alternatives.filter(a=>a.feasible).sort((a,b)=>b.score-a.score||a.estimated_cost_usd-b.estimated_cost_usd||a.id.localeCompare(b.id))[0];
 return {version:'procurement-simulation-v1',mode:'DETERMINISTIC PLANNING SIMULATION',business_need:need,alternatives,
  evidence_sources:[...new Set(catalog.map(a=>a.source))],budget_constraints:{scenario_budget_usd:budget,real_project_inference_cap_usd:2,changes_real_budget:false},
  decision_criteria:['Meet workload capacity','Remain within scenario budget','Optimize '+priority,'Require human review before any consequential action'],
  risk_assessment:['Published unit prices can expire; reverify before a real decision.','Capacity and service-quality inputs are scenarios, not measured provider guarantees.','Existing credit balance is unknown; no new commitment is authorized.'],
  recommended_action:winner?{alternative_id:winner.id,name:winner.name,estimated_cost_usd:winner.estimated_cost_usd,reason:'Meets the scenario capacity and budget constraints; best feasible '+priority+' score.'}:{alternative_id:null,name:'Defer procurement',estimated_cost_usd:0,reason:'No alternative satisfies both the scenario budget and workload capacity.'},
  human_approval_required:true,execution_enabled:false,status:'proposal_only',decision_history:[{action:'computed',detail:'Deterministic alternatives evaluated; no transaction executed.'}]};
}
