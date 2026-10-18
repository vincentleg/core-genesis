/** Product testing keeps actual browsers separate from synthetic opinions. */
export function mountTesting({capabilities,showEvidence,escape:esc,campus}){
 let state={browser:{status:'idle'},audience:{status:'idle',reviews:[],batches:[]}},timer=null,active=false,seen=new Set();
 const $=id=>document.getElementById(id);
 async function refresh(){
  const path=capabilities().company?'/api/company/testing':'./evidence/product-testing.json';
  try{const response=await fetch(path);if(response.ok)state=await response.json();}catch{}
  return state;
 }
 const shot=(phase,name)=>capabilities().company?'/testing-evidence/'+state.browser.id+'/'+phase+'/'+name:'./testing/'+phase+'-'+name;
 function render(){
  const b=state.browser,a=state.audience,reviews=a.reviews||[],latest=b.after||b.reproduced||b.before;
  let html='<p><a href="./hq.html">Current CORE HQ product testing status ↗</a></p><p><b>Historical hackathon lab:</b> the browser results below target the separate Local Solutions prototype; synthetic campaigns do not browse CORE V9.2.</p><p>Two separate evidence systems: actual browser execution and model-generated synthetic opinions. Neither is presented as real customer validation.</p>';
  html+='<h3>A · Actual browser testers</h3><p><b>'+esc(b.status.toUpperCase())+'</b> · '+(latest?latest.successes+'/'+latest.completed+' completed cases passed':'No browser completion inferred')+' · zero model requests</p>';
  if(capabilities().company)html+='<button class="primary" data-testing="browser" '+(b.status==='running'||a.status==='running'?'disabled':'')+'>Run three actual local browser testers ↗</button>';
  if(latest){const phase=b.after?'after':b.reproduced?'reproduce':'before';for(const agent of latest.agents||[])html+='<div class="evidence-event"><b>'+esc(agent.role)+' · '+(agent.passed?'PASS':'FAIL')+'</b><small>'+agent.viewport.width+' × '+agent.viewport.height+' · '+agent.latency_ms+'ms · '+agent.browser_errors.length+' browser errors</small><a href="'+esc(shot(phase,agent.screenshot))+'" target="_blank" rel="noopener"><img class="testing-shot" src="'+esc(shot(phase,agent.screenshot))+'" alt="Actual '+esc(agent.role)+' screenshot"></a><ul>'+agent.steps.map(s=>'<li>'+esc(s.task)+' · '+(s.passed?'pass':'fail')+'</li>').join('')+'</ul>'+(agent.failure?'<pre>'+esc(JSON.stringify(agent.failure,null,2))+'</pre>':'')+'</div>';html+='<p><b>Repair:</b> '+esc(b.repair||'No repair result claimed')+'</p><pre>'+esc(JSON.stringify({before:b.before?.successes,after:b.after?.successes??null,regression_before:b.regression_before?.outcome,regression_after:b.regression_after?.outcome,handoffs:b.handoffs,evolution:b.evolution_evidence},null,2))+'</pre>';}
  if(b.error)html+='<p class="callout">'+esc(b.error)+'</p>';
  html+='<h3>B · Independent synthetic audience</h3><p><b>'+reviews.length+' / '+(a.target||100)+'</b> synthetic perspectives completed. Actual customers: 0.</p><p>Up to 100 perspectives are supported across explicit batches of at most five independent calls. Context is frozen per campaign; personas never receive other responses.</p>';
  if(capabilities().company){html+='<button class="secondary" data-testing="campaign" '+(a.status==='running'?'disabled':'')+'>Create a 100-perspective campaign · zero model calls</button>';if(a.id&&reviews.length<a.target)html+='<button class="primary" data-testing="batch" '+(a.status==='running'||b.status==='running'?'disabled':'')+'>Run next '+Math.min(5,a.target-reviews.length)+' synthetic calls · uses existing credits ↗</button>';}
  if(a.id)html+='<p>'+esc(a.limitations)+'</p><pre>'+esc(JSON.stringify(a.analysis||{},null,2))+'</pre>';
  for(const review of reviews)html+='<div class="evidence-event"><b>'+esc(review.persona.role)+' · SYNTHETIC</b><small>'+esc(review.persona.context)+' · '+esc(review.response.category)+' · '+esc(review.response.position)+'</small><p>'+esc(review.response.concern)+'</p><p><b>Recommendation:</b> '+esc(review.response.recommendation)+'<br><b>Uncertainty:</b> '+esc(review.response.uncertainty)+'</p></div>';
  const batches=a.batches||[];if(batches.length)html+='<h3>Actual batch accounting</h3>'+batches.map(batch=>'<p>'+esc(batch.run_id)+' · '+esc(batch.status)+' · '+(batch.usage?.physical_requests||0)+' attempts · '+(batch.usage?.reported_tokens||0)+' reported tokens · ~$'+Number(batch.usage?.cost_estimate_usd||0).toFixed(6)+'</p>').join('');
  html+='<p class="callout">Browser pass counts measure the implemented tasks only. Synthetic opinions are hypotheses. Organizational changes still require the separate development, held-out and regression gate.</p><p id="testing-error"></p>';
  if($('evidence-modal').open&&active){$('evidence-title').textContent='Product Testing · real browsers & synthetic audience';$('evidence-content').innerHTML=html;}else showEvidence('Product Testing · real browsers & synthetic audience',html);
 }
 async function open(){active=true;await refresh();render();}
 async function tick(){await refresh();for(const event of state.browser.events||[]){const key=event.timestamp+event.type;if(seen.has(key))continue;seen.add(key);campus()?.ensureAgent('Product Testing Lead','product');campus()?.showEvent({role:'Product Testing Lead',message:event.type+': '+event.status,company:true},'product');}if(active&&$('evidence-modal').open)render();if(state.browser.status!=='running'&&state.audience.status!=='running'){clearInterval(timer);timer=null;}}
 document.addEventListener('click',async event=>{
  const target=event.target.closest('[data-testing]');if(!target)return;
  try{target.disabled=true;const action=target.dataset.testing,path=action==='campaign'?'audience':action;const r=await fetch('/api/company/testing/'+path,{method:'POST',headers:{'Content-Type':'application/json','X-Genesis-Action':'testing'},body:JSON.stringify(action==='campaign'?{target:100}:{})});const body=await r.json();if(!r.ok)throw Error(body.error||'Testing action failed');await refresh();render();if(action!=='campaign'){clearInterval(timer);timer=setInterval(()=>tick().catch(()=>{}),1000);}}catch(error){if($('testing-error'))$('testing-error').textContent=error.message;target.disabled=false;}
 });
 return {open,refresh};
}
