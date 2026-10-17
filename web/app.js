const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let state = {}, archived = false, records = [], mode = 'recorded', budget = null;
const cases = [
 ['dev-timeout','Gateway drops valid requests','development'],['dev-pool','Database queue saturation','development'],['dev-route','Health checks fail after migration','development'],
 ['eval-timeout','Report service intermittent 504s','held_out'],['eval-pool','Worker connection starvation','held_out'],['eval-route','Deployment never becomes ready','held_out']
];
const percent = runs => runs.length ? Math.round(runs.filter(r => r.passed).length / runs.length * 100) + '%' : '—';
function render(s) {
 state = s; records = s.runs || []; const strategies = s.strategies || [], events = s.events || [];
 const decision = (s.decisions || []).at(-1), selected = decision?.version ?? events.filter(e => e.message.includes('Development winner')).at(-1)?.version;
 const baselineVersion = s.baseline_version ?? 0;
 const baseline = records.filter(r => r.version === baselineVersion), candidate = records.filter(r => r.version === selected);
 const running = s.status === 'running';
 document.body.classList.toggle('running', running);
 $('status').textContent = archived ? 'ARCHIVED EXPERIMENT' : ({idle:'AWAITING EXPERIMENT',running:'EVOLUTION IN PROGRESS',complete:'EXPERIMENT COMPLETE',error:'EXPERIMENT STOPPED',interrupted:'EXPERIMENT INTERRUPTED'}[s.status] || s.status);
 $('evolve').disabled = running; $('evolve').innerHTML = running ? 'Evolution in progress <span>◌</span>' : 'Run evolution <span>↗</span>';
 $('generation').innerHTML = String(s.current_generation || 0).padStart(2,'0') + '<span>/ GEN</span>';
 $('core-version').textContent = 'GEN ' + String(s.current_generation || 0).padStart(2,'0');
 $('strategy-name').textContent = s.active_strategy?.name || strategies[0]?.name || 'Log-first triage';
 $('baseline').textContent = percent(baseline); $('candidate').textContent = percent(candidate);
 $('delta').textContent = candidate.length ? `${candidate.filter(r=>r.passed).length}/${candidate.length} verified · ${candidate.filter(r=>r.split==='held_out').length}/3 held-out run` : 'Awaiting verified results';
 const inference = events.filter(e=>e.usage), tokens = inference.reduce((n,e)=>n+(e.usage.total_tokens||0),0), latency = inference.reduce((n,e)=>n+(e.latency_s||0),0);
 $('tokens').textContent = tokens ? tokens.toLocaleString() : '—';
 $('latency').textContent = inference.length ? `${latency.toFixed(1)}s inference · ${inference.length} calls · cost unpriced` : 'Cost unavailable · pricing not configured';
 $('event-count').textContent = events.length + ' EVENTS';
 const feed = $('activity-feed'), atBottom = feed.scrollHeight - feed.scrollTop - feed.clientHeight < 60;
 if (events.length) feed.innerHTML = events.map(e=>`<div class="event ${e.message==='FAIL'?'failure':''} ${e.role==='Gate'?'gate':''}"><time>${new Date(e.time*1000).toLocaleTimeString([], {hour12:false,hour:'2-digit',minute:'2-digit',second:'2-digit'})}</time><div><div class="event-text"><b>${esc(e.role)}</b>${esc(e.message)}</div>${e.case_id || e.latency_s || e.analysis ? `<div class="event-detail">${esc(e.case_id || '')}${e.latency_s ? ` ${e.latency_s}s · ${e.usage?.total_tokens || 0} tokens` : ''}${e.analysis ? esc(e.analysis.weakness || e.analysis.hypothesis || '') : ''}</div>`:''}</div></div>`).join('');
 else feed.innerHTML = '<div class="empty"><span>⌁</span><b>No inference activity in this mode.</b><p>Choose Live evolution to explicitly start real reasoning.</p></div>';
 if (atBottom) feed.scrollTop = feed.scrollHeight;
 $('feed-status').textContent = running ? 'Listening for agent activity' : events.length ? `${s.id} · ${s.status}` : 'Waiting for real execution records';
 document.querySelectorAll('.agent').forEach(el=>el.classList.remove('working'));
 if(running) { const role=events.at(-1)?.role?.toLowerCase(); if(['architect','executor','observer','scientist'].includes(role)) document.querySelector('.'+role)?.classList.add('working'); }
 $('strategy-cards').innerHTML = strategies.map(st=>{const runs=records.filter(r=>r.version===st.version),dev=runs.filter(r=>r.split==='development');return `<article class="strategy ${s.current_generation===st.version?'selected':''}"><div class="strategy-top"><span>GEN ${String(st.version).padStart(2,'0')}</span><span>${s.current_generation===st.version?'● ACTIVE':selected===st.version?(decision?.action==='rollback'?'ROLLED BACK':'GATE CANDIDATE'):st.version===baselineVersion?'BASELINE':selected!==undefined?'NOT SELECTED':'CHALLENGER'}</span></div><h3>${esc(st.name)}</h3><p>${esc(st.instructions)}</p><div class="chips">${st.tools.map(t=>`<span class="chip">${esc(t)}</span>`).join('')}</div><div class="strategy-bottom"><span>DEV ${percent(dev)}</span><span>${runs.length} CASES · ${runs.reduce((n,r)=>n+r.attempts.length,0)} ATTEMPTS</span></div></article>`}).join('') + (strategies.length<3 ? Array.from({length:3-strategies.length},(_,i)=>`<article class="strategy placeholder"><div class="strategy-top">CANDIDATE ${i+1}</div><h3>Waiting for a mutation</h3><p>The Scientist proposes competing strategies from observed development failures.</p></article>`).join('') : '');
 $('matrix-head').innerHTML = `<tr><th>INCIDENT / TEST SUITE</th>${strategies.map(st=>`<th>GEN ${String(st.version).padStart(2,'0')}</th>`).join('')}</tr>`;
 $('matrix-body').innerHTML = cases.map(([id,title,split])=>`<tr><td>${esc(title)}<small><span class="split-tag ${split==='held_out'?'held':''}">${split==='held_out'?'◇ HELD-OUT':'○ DEVELOPMENT'}</span> / ${id}</small></td>${strategies.map(st=>{let index=records.findIndex(r=>r.case_id===id && r.version===st.version),r=records[index];return `<td>${r?`<button class="result ${r.passed?'':'fail'}" data-record="${index}">${r.passed?'✓ PASS':'× FAIL'} ↗</button>`:'<span class="not-run">—</span>'}</td>`}).join('')}</tr>`).join('');
 if(decision) $('decision').innerHTML = `<div class="decision-icon ${decision.action==='promote'?'decision-good':'decision-bad'}">${decision.action==='promote'?'↗':'↶'}</div><h3 class="${decision.action==='promote'?'decision-good':'decision-bad'}">Generation ${decision.version} ${decision.action==='promote'?'promoted.':'rolled back.'}</h3><p>${esc(decision.reason)}<br>Baseline remains available in the saved experiment record.</p>`;
 else $('decision').innerHTML = `<div class="decision-icon">⇄</div><h3>${s.status==='error'?'Experiment stopped safely.':'Improvement must be earned.'}</h3><p>${s.status==='error'?esc(s.error)+'. No promotion was made.':'Strict gains on both suites. Zero case regressions.<br>Incomplete evidence blocks promotion.'}</p>`;
 $('download').href=s.id?'/api/experiments/'+encodeURIComponent(s.id):'/api/state';
 if (s.cost_usd !== undefined && s.cost_usd !== null && s.budget_policy) $('latency').textContent = `${latency.toFixed(1)}s · ${s.inference_calls ?? inference.length} requests · ~$${Number(s.cost_usd).toFixed(5)} estimated`;
 applyMode();
}
function applyMode(){
 const running = state.status === 'running';
 $('mode-banner').className = 'mode-banner '+mode;
 if(mode==='recorded'){
  $('mode-banner').innerHTML = '<b>RECORDED EVIDENCE / REPLAY</b><span>Genuine prior execution · zero new API calls.'+(state.id && !state.budget_policy?' Historical record predates the six-request policy.':'')+'</span>';
  $('status').textContent='RECORDED EVIDENCE'; $('evolve').disabled=false; $('evolve').innerHTML='Open latest evidence <span>↗</span>';
  $('action-note').textContent='Read-only replay · no new inference';
 } else if(mode==='local'){
  $('mode-banner').innerHTML='<b>LOCAL TEST</b><span>Network disabled · deterministic unit checks · zero external API calls. No simulated benchmark metrics.</span>';
  $('evolve').innerHTML=running?'Running local checks <span>◌</span>':'Run local checks <span>↗</span>'; $('evolve').disabled=running;
  $('action-note').textContent='Fixed local test suite · network is blocked';
 } else {
  $('mode-banner').innerHTML='<b>LIVE EVOLUTION</b><span>Actual Crusoe / NVIDIA Nemotron reasoning · six physical requests maximum · one cycle per click · $2 project cap.</span>';
  $('evolve').innerHTML=running?'Evolution in progress <span>◌</span>':'Start live evolution <span>↗</span>';
  $('evolve').disabled=running || !budget || budget.status!=='ready';
  $('action-note').textContent=budget?.status==='ready'?'Explicit action spends existing credits · no background inference':(budget?.reason || 'Live locked until verified pricing and budget are available');
 }
}
function renderLocal(report){
 render({status:report.status,events:[],runs:[],strategies:[],current_generation:0});
 $('status').textContent=report.status==='running'?'LOCAL CHECKS RUNNING':report.status==='idle'?'LOCAL TEST READY':report.passed?'LOCAL CHECKS PASSED':'LOCAL CHECKS FAILED';
 $('decision').innerHTML=`<div class="decision-icon ${report.passed?'decision-good':''}">${report.passed?'✓':'⌁'}</div><h3>${report.test_count ? esc(report.test_count)+' deterministic checks' : 'Local verification'}</h3><p>External API calls: 0. Network disabled.<br>${esc(report.note || 'Run the verifier, budget, isolation and lifecycle checks.')}</p>`;
 $('activity-feed').innerHTML=report.output?`<pre>${esc(report.output)}</pre>`:'<div class="empty"><span>⌁</span><b>Local tests are ready.</b><p>These checks never call external APIs.</p></div>';
 $('baseline').textContent='—';$('candidate').textContent='—';$('tokens').textContent='0';$('latency').textContent='0 external API calls · $0';
}
async function poll(){ if(archived)return; try{const response=await fetch(mode==='local'?'/api/local-test':mode==='recorded'?'/api/recorded':'/api/state');if(!response.ok)throw Error('State unavailable');const data=await response.json();if(mode==='local')renderLocal(data);else render(data);}catch(e){$('action-error').textContent='Cannot reach local engine. Start python3 -m core_genesis.server.';} }
async function refreshBudget(){try{const response=await fetch('/api/budget');budget=await response.json();$('budget-strip').textContent=budget.status==='locked'?'LIVE LOCKED · '+budget.reason:`PROJECT CAP $${Number(budget.cap_usd).toFixed(2)} · COMMITTED ESTIMATE + RESERVES $${Number(budget.committed_estimate_and_reserves_usd).toFixed(5)} · REMAINING $${Number(budget.remaining_usd).toFixed(5)} · includes historical uncertainty allowances`;applyMode();}catch(e){budget={status:'locked',reason:'Budget ledger unavailable'};applyMode();}}
async function history(){try{const response=await fetch('/api/history');const list=await response.json();$('history-list').innerHTML=list.length?`<button class="history-item" data-live="true"><span>↗ LIVE WORKSPACE</span><span>OPEN</span></button>`+list.map(x=>`<button class="history-item" data-history="${esc(x.id)}"><span>${esc(x.id)}</span><span>VIEW ↗</span></button>`).join(''):'<div class="empty" style="height:180px"><p>Completed experiments and their evidence<br>will appear here.</p></div>';}catch(e){} }
document.addEventListener('click',async event=>{const item=event.target.closest('[data-record], [data-history], [data-live]');if(!item)return;if(item.dataset.record!==undefined){const record=records[Number(item.dataset.record)];const requestIds=record.attempts.map(a=>a.request_id).filter(Boolean);const requests=(state.events||[]).filter(e=>requestIds.includes(e.request_id));$('evidence-json').textContent=JSON.stringify(requests.length?{...record,shared_request_metrics:requests}:record,null,2);$('evidence-modal').showModal();}if(item.dataset.history){const response=await fetch('/api/experiments/'+encodeURIComponent(item.dataset.history));if(response.ok){mode='recorded';$('mode').value=mode;archived=true;render(await response.json());}}if(item.dataset.live){archived=false;poll();}});
$('close-modal').addEventListener('click',()=>$('evidence-modal').close());
$('mode').addEventListener('change',()=>{mode=$('mode').value;archived=false;$('action-error').textContent='';poll();refreshBudget();});
$('evolve').addEventListener('click',async()=>{try{$('evolve').disabled=true;if(mode==='recorded'){archived=false;await poll();return;}const action=mode==='local'?'local-test':'evolve';const response=await fetch('/api/'+action,{method:'POST',headers:{'X-Genesis-Action':action}});if(!response.ok)throw Error((await response.json()).error);archived=false;await poll();await history();await refreshBudget();}catch(e){$('action-error').textContent=e.message;applyMode();}});
poll();history();refreshBudget();setInterval(poll,1500);setInterval(history,15000);setInterval(refreshBudget,15000);
