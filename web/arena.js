const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const json = value => esc(JSON.stringify(value, null, 2) ?? '');
const pct = metrics => metrics && metrics.total ? Math.round(metrics.passed / metrics.total * 100) + '%' : '—';
const fraction = metrics => metrics && metrics.total ? metrics.passed + '/' + metrics.total : '—';
const money = value => Number(value || 0).toFixed(5);
let state = {}, budget = null, mode = 'recorded', archived = false, selection = null;
let inspectorTab = 'changes', feedFilter = 'all', requestEpoch = 0, battleAuto = true, previousRun = null, localReport = null;
let recordIndex = new Map();

function html(id, markup) {
  if ($(id).innerHTML !== markup) $(id).innerHTML = markup;
}
function empty(title, detail) {
  return '<div class="empty-state"><span>⌬</span><h3>' + esc(title) + '</h3><p>' + esc(detail) + '</p></div>';
}
function nodes() { return state.nodes || []; }
function selectedNode() { return nodes().find(n => n.id === selection); }
function latestRecords(nodeId, suite) {
  const map = new Map();
  for (const record of state.runs || []) {
    if (record.node_id === nodeId && (!suite || record.suite === suite)) map.set(record.suite + ':' + record.case_id, record);
  }
  return [...map.values()];
}
function metrics(records) {
  return {passed:records.filter(r => r.passed).length, total:records.length,
    work_units:records.reduce((n,r) => n + (r.metrics?.work_units || 0),0),
    tool_calls:records.reduce((n,r) => n + (r.metrics?.tool_calls || 0),0)};
}
function updateControls() {
  const running = mode === 'local' ? localReport?.status === 'running' : state.status === 'running';
  const live = mode === 'live';
  $('run-action').disabled = running || live && (!budget || budget.status !== 'ready');
  $('objective').disabled = running;
  $('rounds').disabled = running;
  $('run-action').innerHTML = (running ? (mode === 'local' ? 'Running local checks' : 'Evolution in progress') : mode === 'local' ? 'Run local verification' : live ? 'Start live evolution' : 'Load recorded evidence') + '<span>' + (running ? '◌' : '↗') + '</span>';
  $('mode-description').textContent = mode === 'local' ? 'Deterministic local checks. Network is disabled. No model calls or synthetic benchmark results.' : live ? 'Actual Nemotron reasoning. Programs execute in a bounded local runtime. Only this button starts inference.' : 'Genuine saved execution. Read-only replay; zero new external API requests.';
  $('mode-badge').textContent = mode === 'local' ? 'LOCAL TEST · ZERO API' : live ? 'LIVE · EXPLICIT ACTION' : 'RECORDED EVIDENCE · REPLAY';
  $('mode-badge').classList.toggle('live', live);
  $('request-plan').textContent = live ? (2 + Number($('rounds').value) * 2) + ' planned model calls · ≤12 physical attempts across 2 cycles' : 'Zero external requests · read-only or local computation';
  if (live && budget?.status !== 'ready') $('request-plan').textContent = 'LIVE LOCKED · ' + (budget?.reason || 'Verified pricing and budget unavailable');
}
function render(s) {
  state = s; localReport = null;
  if (state.id !== previousRun) { selection = null; battleAuto = true; previousRun = state.id; }
  recordIndex = new Map((s.runs || []).map((r,i) => [r.id || 'legacy-' + i, r]));
  const running = s.status === 'running';
  $('status-light').classList.toggle('running', running && mode === 'live');
  $('run-status').textContent = mode === 'recorded' ? 'RECORDED EVIDENCE' : ({running:'EXPERIMENT IN PROGRESS',complete:'EXPERIMENT COMPLETE',error:'STOPPED SAFELY',interrupted:'INTERRUPTED',idle:'READY FOR AN OBJECTIVE'}[s.status] || 'READY');
  $('run-id').textContent = s.id || 'NO RUN SELECTED';
  $('objective-display').textContent = s.objective || 'V0 historical experiment. Its genuine results are preserved; no V2 lineage or sealed challenge is inferred.';
  const sealed = s.sealed_comparison;
  const lastDecision = (s.decisions || []).at(-1);
  $('stat-generation').textContent = s.engine_version === 2 ? String(s.current_generation ?? 0).padStart(2,'0') : '—';
  $('stat-team').textContent = s.active_strategy?.name || nodes()[0]?.team.name || 'No verified V2 team';
  $('stat-score').textContent = pct(sealed?.active);
  $('stat-score-detail').textContent = sealed ? fraction(sealed.active) + ' · initial control ' + fraction(sealed.baseline) : 'Sealed cases open after final mutation';
  $('stat-candidates').textContent = nodes().length ? String(nodes().length - 1).padStart(2,'0') : '—';
  $('stat-candidate-detail').textContent = nodes().length ? (s.rounds || []).length + '/' + s.requested_generations + ' rounds evaluated · 2 siblings per round' : 'No candidate lineage in this artifact';
  const inferredCalls = (s.events || []).filter(e => e.usage).length;
  $('stat-requests').textContent = s.inference_calls ?? (inferredCalls || '—');
  const tokenCount = s.total_tokens ?? (s.events || []).reduce((n,e) => n + (e.usage?.total_tokens || 0),0);
  $('stat-cost').textContent = tokenCount.toLocaleString() + ' reported tokens' + (s.cost_usd != null ? ' · ~$' + money(s.cost_usd) + ' est.' : ' · unpriced historical run');
  const outcome = s.status === 'error' ? ['SAFE STOP',s.error_detail || s.error] : running ? ['RESEARCH IN PROGRESS','Testing the next procedure'] : sealed ? ['SEALED OBJECTIVE',s.objective_achieved ? 'All challenge incidents restored' : 'Weaknesses remain measurable'] : ['HISTORICAL EVIDENCE','V0 execution record'];
  html('experiment-outcome','<span>' + esc(outcome[0]) + '</span><b>' + esc(outcome[1]) + '</b>');
  if (!selection || !nodes().some(n => n.id === selection)) selection = s.active_node_id || nodes()[0]?.id || null;
  renderGraph(); renderActivity(); renderInspector(); renderBattle(); renderMemory(); renderCriteria();
  $('download').href = s.id ? '/api/experiments/' + encodeURIComponent(s.id) : '/api/state';
  updateControls();
}

function renderGraph() {
  const list = nodes(), svg = $('evolution-graph');
  $('graph-empty').classList.toggle('hidden', list.length > 0);
  if (!list.length) {
    svg.innerHTML = ''; $('round-timeline').innerHTML = '';
    $('graph-caption').textContent = 'V0 results are genuine; a branching lineage was not recorded.';
    return;
  }
  const positions = new Map(list.map(n => [n.id,{x:32+n.generation*260,y:n.generation===0?116:n.id.endsWith('a')?52:180}]));
  svg.setAttribute('viewBox','0 0 1040 306');
  let markup = '<defs><filter id="node-glow"><feGaussianBlur stdDeviation="5"/></filter></defs>';
  for (let g=0;g<=3;g++) markup += '<text class="graph-generation" x="' + (136+g*260) + '" y="22" text-anchor="middle">GENERATION ' + g + '</text>';
  for (const node of list) {
    if (!node.parent_id) continue;
    const from = positions.get(node.parent_id), to = positions.get(node.id);
    if (!from || !to) continue;
    const x=from.x+208,y=from.y+43,tx=to.x,ty=to.y+43;
    markup += '<path class="graph-edge ' + (node.status==='promoted'?'promoted':'') + '" d="M' + x + ',' + y + ' C' + (x+29) + ',' + y + ' ' + (tx-29) + ',' + ty + ' ' + tx + ',' + ty + '"/>';
  }
  for (const node of list) {
    const p=positions.get(node.id), dev=node.metrics.development;
    const validation=node.metrics['validation-g'+node.generation];
    const name=node.team.name.length>26?node.team.name.slice(0,25)+'…':node.team.name;
    const status=node.id===state.active_node_id?'ACTIVE / '+node.status.replaceAll('_',' '):node.status.replaceAll('_',' ');
    markup += '<g class="graph-node ' + esc(node.status) + (node.id===selection?' selected':'') + '" data-node="' + esc(node.id) + '" role="button" tabindex="0" aria-label="Inspect ' + esc(node.id+' '+node.team.name) + '" transform="translate(' + p.x + ',' + p.y + ')">';
    markup += '<rect class="main-node" x="0" y="0" width="208" height="86" rx="6"/>';
    markup += '<text class="node-id" x="13" y="20">' + esc(node.id.toUpperCase()) + '<tspan x="195" text-anchor="end">' + node.team.agents.length + (node.team.agents.length===1?' WORKER':' WORKERS') + '</tspan></text>';
    markup += '<text class="node-name" x="13" y="41">' + esc(name) + '</text>';
    markup += '<text class="node-score" x="13" y="60">DEV ' + fraction(dev) + ' · VAL ' + fraction(validation) + '</text>';
    markup += '<text class="node-status" x="13" y="75">' + esc(status.toUpperCase()) + '</text></g>';
  }
  if (svg.innerHTML !== markup) svg.innerHTML=markup;
  $('graph-caption').textContent = list.length + ' actual configurations · parent edges reflect accepted lineage · click to inspect';
  html('round-timeline',(state.decisions || []).map(d => '<button class="round-item ' + (d.action==='rollback'?'rollback':'') + '" data-node="' + esc(d.candidate_id) + '"><span>ROUND ' + d.generation + '</span><b>' + esc(d.action.toUpperCase()) + ' ' + esc(d.candidate_id) + '</b><span>' + esc(d.kind.replaceAll('_',' ')) + '</span></button>').join('') || '<div class="round-item">The first independent gate has not completed.</div>');
}

function renderActivity() {
  const events=state.events || [];
  $('event-count').textContent=events.length+' EVENTS';
  const pending=new Set();
  for(const event of events) {
    if(event.message==='Reasoning started') pending.add(event.role);
    if(event.message==='Inference completed') pending.delete(event.role);
  }
  const icons={Architect:'◇',Executor:'ϟ',Observer:'◎',Scientist:'⌬'};
  html('role-strip',Object.entries(icons).map(([role,icon])=>'<div class="role '+(state.status==='running'&&[...pending].some(p=>p.includes(role))?'working':'')+'"><span>'+icon+'</span>'+role+'</div>').join(''));
  const visible=events.filter(e=>feedFilter==='all'||feedFilter==='remote'&&(e.execution_kind==='remote_model'||e.usage)||feedFilter==='gate'&&e.role==='Gate').slice(-100);
  const feed=$('activity-feed'), stick=feed.scrollHeight-feed.scrollTop-feed.clientHeight<65;
  const markup=visible.map(e=>{
    const kind=e.execution_kind==='remote_model'?'NEMOTRON API':e.execution_kind==='local_team_runtime'?'LOCAL TEAM RUNTIME':e.role==='Verifier'?'DETERMINISTIC CHECK':'CONTROLLER';
    const detail=[e.node_id,e.case_id,e.suite,e.usage?e.usage.total_tokens+' tokens':null,e.latency_s?e.latency_s+'s':null,e.tool_calls!=null?e.tool_calls+' tool calls':null].filter(Boolean).join(' · ');
    return '<div class="activity-entry '+(e.role==='Gate'?'gate':'')+' '+(e.message==='FAIL'?'failure':'')+'"><time>'+new Date(e.time*1000).toLocaleTimeString([],{hour12:false})+'</time><div><b>'+esc(e.role)+'</b><span class="event-kind">'+kind+'</span><p>'+esc(e.message)+'</p>'+(detail?'<small>'+esc(detail)+'</small>':'')+'</div></div>';
  }).join('');
  html('activity-feed',markup || empty('No inference activity in this view.','Local execution and remote reasoning will be labeled separately.'));
  if(stick)feed.scrollTop=feed.scrollHeight;
  $('activity-note').textContent=state.status==='running'?'Reading actual engine events · no simulated activity':'Complete tool/agent traces are attached to every incident result.';
}

function renderInspector() {
  const node=selectedNode();
  $('inspector-node').textContent=node?node.id.toUpperCase():'NO LINEAGE NODE';
  if(!node) {
    html('inspector-summary','<h3>Inspect a real candidate.</h3><p>V2 records expose team changes, procedure, workflow and the evidence behind every decision.</p>');
    html('inspector-content',state.engine_version===2?empty('Select a candidate.','The first node appears when the Architect registers its control team.'):renderLegacy());
    return;
  }
  const decision=node.decision;
  html('inspector-summary','<h3>'+esc(node.team.name)+'</h3><p>'+esc(node.reason)+'</p>'+(node.invalid_reason?'<p class="fail">Rejected before execution: '+esc(node.invalid_reason)+'</p>':'')+'<div class="node-meta">PARENT '+esc(node.parent_id||'NONE / CONTROL')+' · '+esc(node.status.replaceAll('_',' ').toUpperCase())+(decision?' · '+esc(decision.kind.replaceAll('_',' ').toUpperCase()):'')+'</div>');
  let content='';
  if(inspectorTab==='changes') {
    if(!node.changes.length) content=empty('Initial control configuration.','The control is measured before any competing team is promoted.');
    else content=node.changes.map(change=>'<details class="change" data-field="'+esc(change.field)+'"><summary>'+esc(change.label)+'<small>'+esc(change.field)+'</small></summary><div class="diff-grid"><div><label>PARENT</label><pre>'+json(change.before)+'</pre></div><div><label>CANDIDATE</label><pre>'+json(change.after)+'</pre></div></div></details>').join('');
    if(decision)content+='<p class="program-note">'+esc(decision.reason)+'</p>';
  } else if(inspectorTab==='team') {
    if(node.design)content+='<p class="program-note">Scientist-selected operator: <b>'+esc(node.design.coordination)+'</b> · Procedure source: '+esc(node.design.procedure_source)+'. The framework expands this into the explicit capability-checked workflow below.</p>';
    content+=node.team.agents.map(agent=>'<div class="team-member"><span class="member-icon">'+({general:'◇',latency:'ϟ',capacity:'▦',routing:'⌘',verifier:'◎'}[agent.specialty]||'◇')+'</span><div><h4>'+esc(agent.id)+' / '+esc(agent.specialty)+'</h4><p>'+esc(agent.instructions)+'</p><div class="chip-row">'+agent.tools.map(tool=>'<span class="chip">'+esc(tool)+'</span>').join('')+'</div></div></div>').join('');
    if(node.team.workflow.some(step=>step.agent==='controller'))content+='<div class="team-member"><span class="member-icon">◎</span><div><h4>controller / fixed verifier</h4><p>Reviews and commits transactions. Cannot retrieve evidence, own repair fields, or disable independent evaluation.</p><span class="chip">IMMUTABLE SAFETY BOUNDARY</span></div></div>';
    content+='<div class="workflow-label">ACTUAL EXECUTION ORDER</div><div class="workflow-list">'+node.team.workflow.map((step,i)=>'<span class="workflow-step"><b>'+String(i+1).padStart(2,'0')+'</b>'+esc(step.agent)+' → '+esc(step.action)+'</span>').join('')+'</div>';
    if(node.configuration_normalizations?.length)content+='<p class="program-note" style="margin-top:15px">'+node.configuration_normalizations.map(esc).join('<br>')+'</p>';
    content+='<p class="program-note" style="margin-top:15px">Review: '+esc(node.team.review_policy)+' · Memory: '+esc(node.team.memory_policy)+' · Evidence cache: '+(node.team.cache_evidence?'enabled':'disabled')+'. Specialized agents can write only their owned fields.</p>';
  } else if(inspectorTab==='program') {
    content='<p class="program-note">'+(node.procedure_origin==='development_verified_memory'?'This procedure recalls development-verified reference rules. No new compiler inference was issued.':'A model-generated declarative procedure, executed locally.')+' References read only retrieved evidence. No generated code, shell, imports or network operations.</p><pre class="code">'+json(node.team.program)+'</pre>';
    if(node.team.memory_policy==='inherit_verified')content+='<div class="workflow-label">AVAILABLE VERIFIED RULE MEMORY</div><pre class="code">'+json(node.memory_snapshot)+'</pre>';
    content+='<p class="program-note">Compiler request: '+esc(node.compilation_request_id||'None; verified procedure or memory reused')+'</p>';
  } else {
    const results=latestRecords(node.id);
    content='<p class="program-note">Latest execution per identical fixture. Click for the actual tool trace, patch, work accounting and behavioral checks.</p><div class="case-list">'+results.map(r=>'<button class="case-row" data-evidence="'+esc(r.id)+'"><span>'+esc(r.case_id)+'<small>'+esc(r.suite)+' · '+r.metrics.tool_calls+' tools · '+r.metrics.work_units+' work units</small></span><span class="'+(r.passed?'pass':'fail')+'">'+(r.passed?'PASS':'FAIL')+' ↗</span></button>').join('')+'</div>';
    if(!results.length)content+=empty('Evaluation has not run.','No score is inferred from the proposed procedure.');
  }
  const opened=new Set([...$('inspector-content').querySelectorAll('details[open]')].map(el=>el.dataset.field));
  html('inspector-content',content);
  $('inspector-content').querySelectorAll('details').forEach(el=>{if(opened.has(el.dataset.field))el.open=true;});
}

function renderLegacy() {
  if(!(state.strategies || []).length)return empty('No V2 experiment yet.','The archive remains read-only; live inference requires explicit action.');
  return '<p class="program-note">Historical V0 evidence. These are strategy versions, not a fabricated evolutionary tree.</p><div class="legacy-grid">'+state.strategies.map(s=>{
    const records=(state.runs||[]).filter(r=>r.version===s.version);
    return '<div class="legacy-card"><span class="mono muted">VERSION '+s.version+'</span><h3>'+esc(s.name)+'</h3><p>'+esc(s.instructions)+'</p><strong>'+records.filter(r=>r.passed).length+'/'+records.length+'</strong></div>';
  }).join('')+'</div>';
}

function renderBattle() {
  const list=nodes(), left=$('battle-left'),right=$('battle-right');
  const oldLeft=left.value,oldRight=right.value;
  const options=list.map(n=>'<option value="'+esc(n.id)+'">'+esc(n.id.toUpperCase()+' / '+n.team.name)+'</option>').join('');
  html('battle-left',options);html('battle-right',options);
  const decision=(state.decisions||[]).at(-1);
  left.value=battleAuto?(decision?.parent_id||list[0]?.id||''):(list.some(n=>n.id===oldLeft)?oldLeft:list[0]?.id||'');
  right.value=battleAuto?(decision?.candidate_id||list.at(-1)?.id||''):(list.some(n=>n.id===oldRight)?oldRight:list.at(-1)?.id||'');
  const l=list.find(n=>n.id===left.value),r=list.find(n=>n.id===right.value);
  if(!l||!r){html('battle-summary',empty('Comparable executions will appear here.','A battle shows only tasks actually evaluated for both candidates.'));$('battle-head').innerHTML='';$('battle-body').innerHTML='';$('battle-reason').textContent='No hypothetical winner is displayed.';return;}
  const a=new Map(latestRecords(l.id).map(x=>[x.suite+':'+x.case_id,x]));
  const b=new Map(latestRecords(r.id).map(x=>[x.suite+':'+x.case_id,x]));
  const common=[...a.keys()].filter(k=>b.has(k));
  const aa=common.map(k=>a.get(k)),bb=common.map(k=>b.get(k)),am=metrics(aa),bm=metrics(bb);
  const side=(node,m)=>'<div class="battle-side"><h3>'+esc(node.id.toUpperCase()+' / '+node.team.name)+'</h3><div class="battle-numbers"><div><strong>'+pct(m)+'</strong><span>'+fraction(m)+' MATCHED CASES</span></div><div><strong>'+m.work_units+'</strong><span>EXECUTED WORK UNITS</span></div><div><strong>'+m.tool_calls+'</strong><span>TOOL CALLS</span></div></div></div>';
  html('battle-summary',side(l,am)+side(r,bm));
  html('battle-head','<tr><th>IDENTICAL INCIDENT / SUITE</th><th>'+esc(l.id.toUpperCase())+'</th><th>'+esc(r.id.toUpperCase())+'</th><th>WORK Δ</th></tr>');
  html('battle-body',common.map(key=>{
    const x=a.get(key),y=b.get(key),delta=y.metrics.work_units-x.metrics.work_units;
    const cell=q=>'<button class="result-button '+(q.passed?'pass':'fail')+'" data-evidence="'+esc(q.id)+'">'+(q.passed?'✓ PASS':'× FAIL')+' ↗</button>';
    return '<tr><td>'+esc(x.title)+'<small>'+esc(x.suite+' / '+x.case_id)+'</small></td><td>'+cell(x)+'</td><td>'+cell(y)+'</td><td class="mono '+(delta<0?'blue':'muted')+'">'+(delta>0?'+':'')+delta+'</td></tr>';
  }).join('')||'<tr><td colspan="4">These nodes do not share an evaluated fixture set yet.</td></tr>');
  const actual=(state.decisions||[]).find(d=>d.parent_id===l.id&&d.candidate_id===r.id);
  $('battle-reason').textContent=actual?actual.action.toUpperCase()+': '+actual.reason:'Exploratory comparison of '+common.length+' identical fixtures. No promotion gate was computed for this exact pair.';
}

function renderMemory() {
  const lessons=state.memory||[];
  $('memory-count').textContent=lessons.length+' VERIFIED LESSONS';
  html('memory-content',lessons.map(m=>'<article class="lesson"><h4>'+esc(m.family)+'<span>DEVELOPMENT VERIFIED</span></h4><p>'+esc(m.principle)+'</p><small>'+m.rules.length+' reusable reference rules · source '+esc(m.source_node_id)+'<br>'+esc(m.source_case_ids.join(', '))+'</small></article>').join('')||empty('No verified reusable lessons yet.','Only rules actually applied in passing development cases can enter memory. Held-out evidence is excluded.'));
}
function renderCriteria() {
  html('criteria-content',(state.criteria||[]).map((c,i)=>'<div class="criterion"><span>'+String(i+1).padStart(2,'0')+'</span><div><h4>'+esc(c.description)+'</h4><p>'+esc(c.metric)+(c.target!==undefined?' · target '+esc(c.target):'')+'</p></div></div>').join('')+(state.suite_manifest?'<div class="criteria-seed">REPRODUCTION SEED '+esc(state.suite_manifest.seed)+'<br>SUITE SHA256 '+esc(state.suite_manifest.sha256)+'<br>Fresh validation per round. Sealed challenge never informs another mutation.</div>':empty('Independent verification stays mandatory.','The Architect may interpret the objective but cannot relax the promotion or safety gate.')));
}
function showEvidence(id) {
  const record=recordIndex.get(id);
  if(!record)return;
  $('evidence-title').textContent=(record.node_id||'V0')+' / '+record.case_id;
  let content='<div class="evidence-facts"><span class="chip '+(record.passed?'pass':'fail')+'">'+(record.passed?'PASS':'FAIL')+'</span><span class="chip">'+esc(record.suite||record.split)+'</span>'+(record.metrics?'<span class="chip">'+record.metrics.tool_calls+' actual tool calls</span><span class="chip">'+record.metrics.work_units+' work units</span><span class="chip">'+record.metrics.latency_s+'s local runtime</span>':'')+'</div>';
  content+='<p class="program-note">'+esc(record.provenance||'Historical actual model repair and deterministic verification.')+'</p>';
  if(record.trace)content+='<div class="workflow-label">EXECUTED AGENT / TOOL TRACE</div>'+record.trace.map(step=>'<div class="trace-step"><strong>'+String(step.step+1).padStart(2,'0')+' · '+esc(step.agent)+' → '+esc(step.action)+'</strong><p>'+esc(step.kind)+' / '+esc(step.status)+(step.detail?' · '+esc(step.detail):'')+'</p><details><summary>Inspect actual evidence and operations</summary><pre class="code">'+json(step)+'</pre></details></div>').join('');
  content+='<div class="workflow-label">COMPLETE RECORD</div><pre class="code">'+json(record)+'</pre>';
  html('evidence-content',content);
  $('evidence-dialog').showModal();
}

function renderLocal(report) {
  localReport=report;
  state={status:report.status,nodes:[],runs:[],events:[]};
  recordIndex.clear();selection=null;
  $('run-status').textContent=report.status==='running'?'LOCAL VERIFICATION RUNNING':report.passed?'LOCAL VERIFICATION PASSED':report.status==='idle'?'LOCAL VERIFICATION READY':'LOCAL VERIFICATION FAILED';
  $('run-id').textContent='NETWORK DISABLED';
  $('objective-display').textContent='Local tests exercise the actual interpreter, budget, lineage, memory, isolation and gate. Unit-test transports never serve as live benchmark evidence.';
  $('stat-generation').textContent='—';$('stat-team').textContent='No live team created';
  $('stat-score').textContent=report.test_count||'—';$('stat-score-detail').textContent='Local unit checks; not benchmark success';
  $('stat-candidates').textContent='—';$('stat-candidate-detail').textContent='No fabricated candidate activity';
  $('stat-requests').textContent='0';$('stat-cost').textContent='$0 · zero external API calls';
  html('experiment-outcome','<span>LOCAL VERIFICATION</span><b>'+esc(report.passed?'All checks passed':report.status)+'</b>');
  renderGraph();renderInspector();renderBattle();renderMemory();renderCriteria();
  html('activity-feed',report.output?'<pre class="local-output">'+esc(report.output)+'</pre>':empty('Ready for deterministic local checks.','Network access is disabled in the test process.'));
  $('event-count').textContent=report.test_count?report.test_count+' TESTS':'0 INFERENCE EVENTS';
  updateControls();
}

async function poll() {
  if(archived)return;
  const epoch=requestEpoch,requestedMode=mode;
  try{
    const response=await fetch(requestedMode==='local'?'/api/local-test':requestedMode==='recorded'?'/api/recorded':'/api/state');
    if(!response.ok)throw Error('Engine state unavailable');
    const value=await response.json();
    if(epoch!==requestEpoch||requestedMode!==mode)return;
    requestedMode==='local'?renderLocal(value):render(value);
  }catch(error){$('action-error').textContent='Local engine unavailable. Start python3 -m core_genesis.server.';}
}
async function refreshBudget() {
  try{
    const response=await fetch('/api/budget');budget=await response.json();
    if(budget.status==='locked'){$('budget-used').textContent='LIVE LOCKED';$('budget-left').textContent='';$('budget-note').textContent=budget.reason;}
    else{
      $('budget-fill').style.width=Math.min(100,Number(budget.committed_estimate_and_reserves_usd)/Number(budget.cap_usd)*100)+'%';
      $('budget-used').textContent='$'+money(budget.committed_estimate_and_reserves_usd)+' committed';
      $('budget-left').textContent='$'+money(budget.remaining_usd)+' left';
      $('budget-note').textContent='Estimated usage + conservative uncertainty reserves. '+budget.physical_requests+' requests recorded since budget policy.';
    }
  }catch(error){budget={status:'locked',reason:'Budget ledger unavailable'};}
  updateControls();
}
async function refreshHistory() {
  try{
    const response=await fetch('/api/history'),list=await response.json(),selected=$('archive').value;
    html('archive','<option value="">Latest completed experiment</option>'+list.map(item=>'<option value="'+esc(item.id)+'">'+esc(item.id)+'</option>').join(''));
    $('archive').value=selected;
  }catch(error){}
}
async function action() {
  $('action-error').textContent='';
  if(mode==='recorded'){archived=false;$('archive').value='';requestEpoch++;await poll();return;}
  try{
    $('run-action').disabled=true;
    const local=mode==='local',actionName=local?'local-test':'evolve';
    const options={method:'POST',headers:{'X-Genesis-Action':actionName,'Content-Type':'application/json'}};
    if(!local)options.body=JSON.stringify({objective:$('objective').value,generations:Number($('rounds').value)});
    const response=await fetch('/api/'+actionName,options);
    if(!response.ok)throw Error((await response.json()).error||'Action rejected');
    archived=false;$('archive').value='';requestEpoch++;await poll();await refreshBudget();await refreshHistory();
  }catch(error){$('action-error').textContent=error.message;updateControls();}
}

document.addEventListener('click',event=>{
  const node=event.target.closest('[data-node]');
  if(node){selection=node.dataset.node;renderGraph();renderInspector();}
  const evidence=event.target.closest('[data-evidence]');
  if(evidence)showEvidence(evidence.dataset.evidence);
  const tab=event.target.closest('[data-inspect]');
  if(tab){inspectorTab=tab.dataset.inspect;document.querySelectorAll('[data-inspect]').forEach(b=>b.classList.toggle('active',b===tab));renderInspector();}
  const feed=event.target.closest('[data-feed]');
  if(feed){feedFilter=feed.dataset.feed;document.querySelectorAll('[data-feed]').forEach(b=>b.classList.toggle('active',b===feed));renderActivity();}
});
$('evolution-graph').addEventListener('keydown',event=>{const node=event.target.closest('[data-node]');if(node&&(event.key==='Enter'||event.key===' ')){event.preventDefault();selection=node.dataset.node;renderGraph();renderInspector();}});
$('mode').addEventListener('change',()=>{mode=$('mode').value;requestEpoch++;archived=false;$('archive').value='';$('action-error').textContent='';poll();refreshBudget();});
$('rounds').addEventListener('change',updateControls);
$('run-action').addEventListener('click',action);
$('close-evidence').addEventListener('click',()=>$('evidence-dialog').close());
$('graph-fit').addEventListener('click',()=>{$('graph-scroll').scrollTo({left:0,behavior:'smooth'});});
for(const id of ['battle-left','battle-right'])$(id).addEventListener('change',()=>{battleAuto=false;renderBattle();});
$('archive').addEventListener('change',async()=>{
  const id=$('archive').value;requestEpoch++;
  if(!id){archived=false;await poll();return;}
  try{
    const response=await fetch('/api/experiments/'+encodeURIComponent(id));if(!response.ok)throw Error('Unknown experiment');
    const record=await response.json();mode='recorded';$('mode').value=mode;archived=true;render(record);
  }catch(error){$('action-error').textContent=error.message;}
});
poll();refreshBudget();refreshHistory();
setInterval(poll,1500);setInterval(refreshBudget,10000);setInterval(refreshHistory,15000);
