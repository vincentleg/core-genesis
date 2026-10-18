import {mountTesting} from './testing-ui.js';
/** Real mission control; public hosting only replays genuine recorded work. */
export function mountCompany({campus,openContext,showEvidence,escape:esc,capabilities}){
 const $=id=>document.getElementById(id);
 let state={mission:{status:'idle',events:[],departments:{}},governance:{paused:false,audit:[],decisions:[]}},mode='recorded',timer=null,eventIndex=0,activeView=null,playTimer=null;
 const FLAGSHIP='Analyze the actual local CORE V9.2 source at v9.2/earth-first. Review browser evidence, identify problems and propose improvements for human approval. Keep CORE read-only.';
 const testingControl=mountTesting({capabilities,showEvidence,escape:esc,campus});
 const title='<span class="eyebrow">HUMAN CEO · BOUNDED AGENT AUTHORITY</span><h2>CEO Office</h2>';
 function badge(value){return '<span class="capability">'+esc(value.replaceAll('_',' ').toUpperCase())+'</span>';}
 async function request(path,data,action){
  const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Genesis-Action':action},body:JSON.stringify(data)});
  const body=await response.json();if(!response.ok)throw Error(body.error||'Action rejected');return body;
 }
 function missionDetails(){
  const mission=state.mission,artifacts=mission.artifacts||{};
  let html='<div class="company-state">'+badge(mode==='live'?'LIVE LOCAL EXECUTION':'VERIFIED EXECUTION REPLAY')+' '+badge(mission.status)+'</div>';
  html+='<p id="company-live-progress" class="fine">'+esc(mission.events?.at(-1)?.message||'No current activity')+'</p>';
  if(!mission.id)return html+'<p>No real repository mission has been recorded yet. No result is inferred.</p>';
  html+='<p class="mission-objective">'+esc(mission.objective)+'</p><p class="fine">Mission '+esc(mission.id)+'<br>CORE commit '+esc(mission.snapshot?.commit||'Retrieval pending')+'<br>Read-only GitHub evidence; no CORE changes or test execution.</p>';
  const usage=mission.usage;
  html+='<div class="company-resource">'+(usage?'<b>'+usage.physical_requests+' actual attempts</b><span>'+Number(usage.reported_tokens||0).toLocaleString()+' reported tokens · ~$'+Number(usage.cost_estimate_usd||0).toFixed(6)+' estimated incl. failed-request reserves</span>':'<b>Budgeted execution</b><span>Up to 11 planned calls including citation correction, 12 physical attempts maximum, single concurrency. Project cap $2.</span>')+'</div>';
  html+='<div class="mission-actions"><button class="secondary" data-company="sources">Inspect actual CORE source evidence ↗</button><button class="secondary" data-company="deliverable">Engineering deliverable ↗</button><button class="secondary" data-company="panel">Synthetic research ('+(mission.panel||[]).length+'/5) ↗</button><button class="secondary" data-company="growth">Growth approval queue ↗</button><button class="secondary" data-company="evolution">Workflow evolution evidence ↗</button><button class="secondary" data-company="audit">Handoffs & audit trail ↗</button></div>';
  if(mission.error_detail)html+='<p class="callout">'+esc(mission.error_detail)+'</p>';
  html+='<h3>Department operations</h3>';
  const departments=['hq','research','engineering','product','operations','growth','evolution'];
  for(const id of departments){
   const department=mission.departments?.[id];
   html+='<button class="department-state secondary" data-company-department="'+id+'"><b>'+esc(department?.agent||id)+'</b><span>'+esc(department?.state||'idle')+'</span><small>'+esc(department?.last_activity||'No assigned activity in this mission')+'</small></button>';
  }
  return html;
 }
 function office(){
  activeView='office';
  const mission=state.mission;
  if(mission.configuration){
   const policy=mission.evolution?.active_policy||mission.configuration.policy,version=mission.evolution?.resulting_version??mission.configuration.version;
   campus()?.applyPolicy(policy,version);
   $('generation-name').textContent='Mission policy V'+version;
   $('generation-detail').textContent=['known_sources','line_bounds','exact_quotes'].filter(key=>policy[key]).length+'/3 preflight checks enabled · final validation always strict';
  }
  let html=title+'<p>The founder sets objectives and retains consequential authority. Current work inspects local CORE V9.2 and records real browser evidence. Legacy mission artifacts below are historical. <a href="./hq.html">Open current CORE HQ status ↗</a></p>';
  html+='<p class="fine">Strategic priorities: useful CORE development, traceable evidence, independent evaluation and human authority. '+state.governance.decisions.filter(d=>d.status==='pending_ceo_review').length+' decisions awaiting CEO review.</p>';
  if(state.budget)html+='<div class="company-resource"><b>$'+Number(state.budget.committed_estimate_and_reserves_usd||0).toFixed(4)+' committed / $2 cap</b><span>$'+Number(state.budget.remaining_usd||0).toFixed(4)+' remaining · usage estimates plus conservative reserves</span></div>';
  if(capabilities().company){
   html+='<label for="company-objective">Assign a real CORE mission</label><textarea id="company-objective" maxlength="600">'+esc(FLAGSHIP)+'</textarea><button class="primary" data-company="start" '+(!capabilities().paid_inference_enabled||state.governance.paused||state.mission.status==='running'?'disabled':'')+'>LAUNCH MISSION <span>↗</span></button><p class="fine">Legacy remote-model workflow: disabled until paid inference approval; local CORE source sharing remains separately blocked. Use the CORE HQ product lab for zero-cost local browser sessions.</p><button class="emergency" data-company="'+(state.governance.paused?'resume':'pause')+'">'+(state.governance.paused?'Resume authority · do not restart work':'Emergency pause · company-wide')+'</button><p class="fine">Pause blocks new inference and retrieval. An in-flight request may finish. Resume never automatically restarts a mission.</p>';
  }else{
   html+='<p class="callout">Public experience: genuine recorded company work. New inference and CEO authority controls remain local; no public paid endpoint.</p><button class="primary" data-company="replay">Replay actual department handoffs <span>↗</span></button>';
  }
  html+='<div id="company-error" class="fine"></div>'+resultCard()+missionDetails();
  openContext(html);
 }
 function prototype(){return state.mission.artifacts?.prototype;}
 function previewUrl(){return capabilities().company?prototype().preview_url:'./artifacts/core-local-solutions/index.html';}
 function artifactUrl(name){return capabilities().company?'/artifact/'+state.mission.id+'/'+name:'./artifacts/core-local-solutions/source/'+name+'.txt';}
 function resultCard(){
  const p=prototype();if(!p)return '';
  const outcome=p.test_report.outcome;
  return '<section class="artifact-result"><span class="eyebrow">'+(p.test_report.passed?'HISTORICAL LOCAL SOLUTIONS PROTOTYPE':'PROTOTYPE NEEDS REVIEW')+'</span><h3>CORE Local Solutions</h3><p>'+outcome.tests_run+' actual tests · '+outcome.failures+' failures · '+outcome.errors+' errors<br>Isolated application. '+esc((state.governance.decisions.find(d=>d.type==='artifact_review'&&d.mission_id===state.mission.id)?.status||'pending_ceo_review').replaceAll('_',' '))+'</p><a class="primary artifact-open" href="'+esc(previewUrl())+'" target="_blank" rel="noopener">OPEN PROTOTYPE ↗</a><button class="secondary" data-company="result">Review delivered capability ↗</button></section>';
 }
 function result(){
  const p=prototype();if(!p)return;
  const m=state.mission,o=p.test_report.outcome;
  let html='<p><b>Requested:</b> '+esc(m.objective)+'</p><p><b>Built:</b> a working problem → proposed solution → local human-review application, using an audited scaffold and real Nemotron-selected specification.</p><div class="metric-row"><div><b>'+o.tests_run+'</b><span>ACTUAL TESTS</span></div><div><b>'+o.failures+'</b><span>FAILURES</span></div><div><b>'+Math.round((m.finished_at-m.created_at)||0)+'s</b><span>EXECUTION TIME</span></div></div>'+resultCard();
  html+='<div class="mission-actions"><button class="secondary" data-company="artifact-source">INSPECT SOURCE ↗</button><button class="secondary" data-company="test-results">VIEW TEST RESULTS ↗</button><button class="secondary" data-company="integration">REVIEW FOR CORE ↗</button><button class="secondary" data-company="improve">REQUEST IMPROVEMENT ↗</button><button class="secondary" data-company="evolution">WORKFLOW EVOLUTION ↗</button></div>';
  html+='<p>'+Object.keys(p.files).length+' source/configuration files · '+(m.usage?.physical_requests||0)+' requests · '+(m.usage?.reported_tokens||0)+' tokens · ~$'+Number(m.usage?.cost_estimate_usd||0).toFixed(6)+' estimated.</p><p class="callout">No production integration, authenticated identity or real-world authorization. Synthetic reviews are not customer validation. Public preview uses browser-only storage; local mode runs the tested Python backend.</p>';
  const decision=state.governance.decisions.find(d=>d.mission_id===m.id&&d.type==='artifact_review');
  if(decision){html+='<p>'+badge(decision.status)+'</p>';if(capabilities().company&&decision.status==='pending_ceo_review')html+='<button class="primary" data-company="approve" data-artifact="true" data-decision-id="'+esc(decision.id)+'">CEO: accept for local review</button><button class="secondary" data-company="reject" data-artifact="true" data-decision-id="'+esc(decision.id)+'">Request revision</button>';}
  showEvidence('CORE HQ delivered · CORE Local Solutions',html);
 }
 function artifactSource(){const p=prototype();if(!p)return;showEvidence('Generated source · immutable mission artifact','<p>'+esc(p.implementation)+'</p><p>Version '+esc(state.mission.id)+' · original CORE unchanged.</p>'+Object.entries(p.files).map(([name,hash])=>'<div class="evidence-event"><a target="_blank" rel="noopener" href="'+esc(artifactUrl(name))+'">'+esc(name)+' ↗</a><small>SHA-256 '+esc(hash)+'</small></div>').join('')+(!capabilities().company?'<a class="primary artifact-open" href="./artifacts/core-local-solutions/source.zip">Download runnable source archive ↧</a>':''));}
 function testResults(){const p=prototype();if(!p)return;showEvidence('Operations · actual process output','<p>'+esc(p.test_report.scope)+'</p><p>Exit code '+p.test_report.exit_code+' · '+p.test_report.outcome.tests_run+' tests run</p><pre>'+esc(p.test_report.stderr)+'</pre><pre>'+esc(JSON.stringify(p.test_report.outcome,null,2))+'</pre><a target="_blank" rel="noopener" href="'+esc(artifactUrl('build-report.json'))+'">Machine-readable report ↗</a>');}
 function integration(){const p=prototype();if(!p)return;showEvidence('Review for CORE · proposal only','<p>No CORE changes, deployment or real-world execution is authorized by this prototype.</p><ol>'+p.integration_plan.map(v=>'<li>'+esc(v)+'</li>').join('')+'</ol><p>CEO approval and maintainer review are required before any separate integration task. The existing CORE project is pre-existing external work.</p>');}
 function showDeliverable(){
  const mission=state.mission,report=mission.artifacts?.engineering,snapshot=mission.snapshot;
  if(!report)return showEvidence('Deliverable not available','<p>The Engineering stage has not produced a result. No completion is inferred.</p>');
  let html='<p><b>'+esc(report.summary)+'</b></p><p class="callout">Model-authored proposals for maintainer review. Citation checks prove the quoted text exists; they do not establish that a feature is missing or that these are the best priorities. Existing implementations may fall outside the eight inspected excerpts.</p><p>CORE '+esc(snapshot.commit)+' · '+esc(mission.verification?.note)+'</p>';
  report.priorities.forEach((p,index)=>{
   const verified=mission.verification?.priorities?.[index]?.passed;
   html+='<section class="deliverable-priority"><span class="'+(verified?'verified':'rejected')+'">'+(verified?'CITATIONS VERIFIED':'EVIDENCE REVIEW REQUIRED')+'</span><h3>'+(index+1)+'. '+esc(p.title)+'</h3><p>'+esc(p.finding)+'</p><ul>'+p.actions.map(action=>'<li>'+esc(action)+'</li>').join('')+'</ul><p><b>Verification plan:</b> '+p.verification.map(esc).join('; ')+'<br><b>Uncertainty:</b> '+esc(p.uncertainty)+'</p>';
   for(const ref of p.citations){
    const source=snapshot.sources.find(s=>s.id===ref.source_id);
    html+='<div class="source-citation">'+(source?'<a href="'+esc(source.url)+'#L'+Number(ref.line_start)+'-L'+Number(ref.line_end)+'" target="_blank" rel="noreferrer">'+esc(source.path)+' · lines '+ref.line_start+'–'+ref.line_end+' ↗</a>':'Unknown source')+'<blockquote>'+esc(ref.quote)+'</blockquote></div>';
   }
   html+='</section>';
  });
  html+='<h3>Scope and uncertainty</h3><ul>'+snapshot.limitations.map(text=>'<li>'+esc(text)+'</li>').join('')+'</ul>';
  if(capabilities().company)html+='<a class="text-button" href="/api/company/mission/'+esc(mission.id)+'.md" target="_blank" rel="noreferrer">Download actionable Markdown report ↗</a>';
  showEvidence('CORE · evidence-backed engineering priorities',html);
 }
 function sources(){
  const snapshot=state.mission.snapshot;
  if(!snapshot)return showEvidence('CORE connection','<p>No public repository snapshot has been retrieved in this mission.</p>');
  showEvidence('Actual CORE source · read-only snapshot','<p>Commit '+esc(snapshot.commit)+' · '+snapshot.file_count+' files in the retrieved public tree; '+snapshot.sources.length+' bounded excerpts inspected. No checkout, execution, deployment or CORE write occurred.</p>'+snapshot.sources.map(s=>'<div class="evidence-event"><a href="'+esc(s.url)+'" target="_blank" rel="noreferrer"><b>'+esc(s.path)+' ↗</b></a><small>'+esc(s.id)+' · lines '+s.line_start+'–'+s.line_end+' of '+s.full_line_count+' · '+(s.truncated?'excerpt only':'complete bounded file')+'</small><pre>'+esc(s.text)+'</pre></div>').join('')+'<h3>Retrieval evidence</h3><pre>'+esc(JSON.stringify(snapshot.requests,null,2))+'</pre>');
 }
 function panel(){
  const mission=state.mission;
  let html='<p>Five independent Nemotron calls, each with a distinct synthetic perspective and no access to other persona responses. These are NOT actual beta users or evidence of real-world product success.</p>';
  for(const review of mission.panel||[])html+='<div class="evidence-event"><b>'+esc(review.persona.name)+'</b><small>SYNTHETIC · independent call · priority '+esc(review.response.priority)+' · '+esc(review.response.position)+'</small><p>'+esc(review.response.concern)+'</p><p><b>Recommendation:</b> '+esc(review.response.recommendation)+'<br><b>Verify:</b> '+esc(review.response.verification_needed)+'</p></div>';
  html+='<h3>Agreement and disagreement</h3><pre>'+esc(JSON.stringify(mission.panel_summary||{completed:0},null,2))+'</pre><p>Five-person execution is implemented. Scaling to 100 requires separate bounded batches and explicit budget authorization; no 100-person research result is claimed.</p>';
  showEvidence('Product Research · synthetic panel',html);
 }
 function growth(){
  const draft=state.mission.artifacts?.growth;
  if(!draft)return showEvidence('Growth Director','<p>No Growth draft has been completed for this mission. No official accounts are connected. No audience metrics exist.</p>');
  let html='<p>'+esc(draft.strategy)+'</p><p class="callout">Draft proposals only. No personal accounts, no LinkedIn, no publishing API connected. Approval records authorize manual export only; nothing is posted automatically.</p>';
  for(const post of draft.posts)html+='<div class="evidence-event"><b>'+esc(post.platform)+' · CEO REVIEW</b><p>'+esc(post.text)+'</p><small>Grounded in priority '+post.priority_ids.map(esc).join(', ')+'<br>Visual brief: '+esc(post.visual_brief)+'</small></div>';
  const decisions=state.governance.decisions.filter(d=>d.mission_id===state.mission.id);
  for(const decision of decisions){
   html+='<p>'+badge(decision.status)+'</p>';
   if(capabilities().company&&decision.status==='pending_ceo_review')html+='<button class="primary" data-company="approve" data-decision-id="'+esc(decision.id)+'">CEO: approve for manual export</button><button class="secondary" data-company="reject" data-decision-id="'+esc(decision.id)+'">Reject draft</button>';
  }
  html+='<p>Account setup remains a CEO-authorized manual process using official developer portals and organization-owned accounts. Platform verification, CAPTCHA and credential setup are not automated. Impressions, engagement and follower counts: unavailable.</p>';
  showEvidence('Growth · official-channel approval queue',html);
 }
 function evolution(){
  const value=state.mission.evolution;
  if(!value)return showEvidence('Evolution Lab','<p>No mission-specific mutation evaluation completed. Existing incident evolution remains available from the campus Evolution Lab.</p>');
  let html='<p>'+esc(value.scope)+'</p><div class="metric-row"><div><b>V'+state.mission.configuration.version+'</b><span>BASELINE PREFLIGHT CONFIGURATION</span></div><div><b>'+esc(value.action.toUpperCase())+'</b><span>INDEPENDENT EVIDENCE GATE</span></div><div><b>V'+value.resulting_version+'</b><span>RESULTING CONFIGURATION</span></div></div><p>'+esc(value.reason)+'</p>';
  const scores=value.comparison;
  html+='<p>Development accuracy: '+scores.development.parent.passed+'/'+scores.development.parent.total+' → '+scores.development.candidate.passed+'/'+scores.development.candidate.total+'<br>Independent held-out accuracy: '+scores.heldout.parent.passed+'/'+scores.heldout.parent.total+' → '+scores.heldout.candidate.passed+'/'+scores.heldout.candidate.total+'</p>';
  html+='<p>These are explicitly labeled deterministic citation-error fixtures, not fabricated mission results. The Scientist received development cases only. The existing independent promotion gate checks success gains and regressions. Mandatory final citation validation always stays strict.</p><pre>'+esc(JSON.stringify(value,null,2))+'</pre>';
  showEvidence('Evolution · real-work preflight improvement',html);
 }
 function audit(){
  showEvidence('Company audit · actual handoffs','<p>Each entry records a real assignment and its observed result or failure. No automatic external communications, purchases, account changes or CORE writes are implemented.</p>'+state.mission.handoffs.map(h=>'<div class="evidence-event"><b>'+esc(h.source_agent)+' → '+esc(h.destination_agent)+'</b><small>'+new Date(h.timestamp*1000).toLocaleString()+' · '+esc(h.status)+'</small><p>'+esc(h.task)+'</p><pre>'+esc(JSON.stringify({evidence:h.evidence,result:h.result},null,2))+'</pre></div>').join('')+'<h3>CEO decision audit</h3><pre>'+esc(JSON.stringify(state.governance.audit,null,2))+'</pre>');
 }
 function department(id){
  activeView=id;const status=state.mission.departments?.[id],names={research:'Research',engineering:'Engineering',product:'Product Testing',growth:'Growth & PR',operations:'Operations',evolution:'Evolution Lab'};
  let html='<span class="eyebrow">REAL COMPANY OPERATIONS</span><h2>'+names[id]+'</h2>'+badge(status?.state||'idle')+'<p>'+esc(status?.last_activity||'No active assignment. Idle ambience is decorative, not work.')+'</p><p class="fine">Agent '+esc(status?.agent||'unassigned')+' · configuration V'+(state.mission.configuration?.version||0)+'<br>Mission '+esc(state.mission.id||'none')+'</p>';
  if(id==='research')html+='<button class="primary" data-company="sources">Inspect actual CORE source ↗</button>';
  if(id==='research'||id==='engineering')html+='<button class="secondary" data-company="deliverable">Inspect CORE deliverable ↗</button>';
  if(id==='product')html+='<button class="primary" data-company="testing">Open Product Testing Lab ↗</button><button class="secondary" data-company="panel">Inspect five-person synthetic panel ↗</button>';
  if(id==='growth')html+='<button class="primary" data-company="growth">Review official-channel drafts ↗</button>';
  if(id==='operations')html+='<button class="primary" data-company="audit">Inspect actual handoffs ↗</button>';
  if(id==='evolution')html+='<button class="primary" data-company="evolution">Inspect mission policy evolution ↗</button>';
  html+='<h3>Assigned work</h3>'+state.mission.handoffs.filter(h=>h.destination_agent.toLowerCase().includes(id==='product'?'synthetic':id==='evolution'?'scientist':id)).map(h=>'<div class="mission-step"><b>↗</b><div>'+esc(h.task)+'<small>'+esc(h.status)+'</small></div></div>').join('')+'<button class="secondary" data-company="office">Open CEO Office ↗</button>';
  openContext(html);
 }
 function animate(event){
  campus()?.ensureAgent(event.agent,event.department);
  campus()?.showEvent({role:event.agent,message:event.message,time:event.time,company:true},event.department);
  if(event.type==='research.started'||event.type==='engineering.started'||event.type==='operations.testing'||event.type==='mission.awaiting_approval')campus()?.selectDepartment(event.department);
  if(event.execution_kind==='independent_gate'&&state.mission.evolution){
   const evolution=state.mission.evolution;
   campus()?.applyPolicy(evolution.active_policy,evolution.resulting_version,evolution.action==='promote');
   $('generation-name').textContent='Mission policy V'+evolution.resulting_version;
   $('generation-detail').textContent=evolution.action.toUpperCase()+' · independent citation-preflight validation';
  }
  $('mode-label').textContent=mode==='live'?'LIVE LOCAL EXECUTION':'VERIFIED EXECUTION REPLAY';
  $('playback-type').textContent=mode==='live'?'REAL CORE MISSION · CRUSOE / NEMOTRON':'GENUINE CORE MISSION · REPLAY';
  $('playback-title').textContent=event.agent+': '+event.message;
  $('playback-detail').textContent=(mode==='live'?'Actual activity':'Recorded activity; timing compressed')+' · '+state.mission.id;
  $('event-bubble').classList.remove('hidden');$('event-bubble').innerHTML='<span>'+esc(event.agent.toUpperCase())+' · '+(mode==='live'?'LIVE':'RECORDED')+'</span><p>'+esc(event.message.slice(0,210))+'</p>';
 }
 async function refresh(){
  if(!capabilities().company)return;
  const response=await fetch('/api/company');state=await response.json();
  state.budget=await(await fetch('/api/budget')).json();
  if(mode==='live'){
   for(const event of state.mission.events.slice(eventIndex))animate(event);
   eventIndex=state.mission.events.length;
   if($('company-live-progress'))$('company-live-progress').textContent=state.mission.events.at(-1)?.message||'Awaiting first activity';
   if(state.mission.status!=='running'){clearInterval(timer);timer=null;office();}
  }
 }
 async function action(name,target){
  try{
   if(name==='testing')testingControl.open();if(name==='office')office();if(name==='result')result();if(name==='artifact-source')artifactSource();if(name==='test-results')testResults();if(name==='integration')integration();if(name==='improve'){if($('evidence-modal').open)$('evidence-modal').close();office();$('company-objective').value=FLAGSHIP+' Improvement objective: improve clarity and usability while retaining all required workflows.';$('company-objective').focus();}
   if(name==='deliverable')showDeliverable();if(name==='sources')sources();if(name==='panel')panel();if(name==='growth')growth();if(name==='evolution')evolution();if(name==='audit')audit();
   if(name==='replay'){
    clearInterval(playTimer);mode='recorded';let index=0;$('context').classList.add('hidden');
    if(state.mission.configuration){campus()?.applyPolicy(state.mission.configuration.policy,state.mission.configuration.version);$('generation-name').textContent='Mission policy V'+state.mission.configuration.version;}
    const events=state.mission.events.filter(e=>e.message!=='Nemotron reasoning started'&&(e.message!=='Nemotron result recorded'||e.agent.startsWith('Synthetic ')));
    if(!events.length)return;
    animate(events[index++]);playTimer=setInterval(()=>{if(index>=events.length){clearInterval(playTimer);return;}animate(events[index++]);},3000);
   }
   if(name==='start'){
    target.disabled=true;
    await request('/api/company/mission',{objective:$('company-objective').value},'mission');
    mode='live';eventIndex=0;await refresh();office();timer=setInterval(()=>refresh().catch(error=>{$('playback-detail').textContent=error.message;}),1200);
   }
   if(['pause','resume','approve','reject'].includes(name)){
    await request('/api/company/control',{action:name,decision_id:target.dataset.decisionId},'ceo');await refresh();
    if(name==='approve'||name==='reject'){if($('evidence-modal').open)$('evidence-modal').close();if(target.dataset.artifact)result();else growth();}else office();
   }
  }catch(error){if($('company-error'))$('company-error').textContent=error.message;target.disabled=false;}
 }
 document.addEventListener('click',event=>{
  const target=event.target.closest('[data-company]');if(target)action(target.dataset.company,target);
  const departmentButton=event.target.closest('[data-company-department]');if(departmentButton)department(departmentButton.dataset.companyDepartment);
 });
 async function loadRecorded(){
  try{state=await(await fetch('./evidence/company-mission.json')).json();}catch{}
 }
 loadRecorded();
 return {office,department,refresh,get state(){return state;}};
}
