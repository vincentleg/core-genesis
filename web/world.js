import {createCampus,DEPARTMENTS} from './campus.js';
import {planProcurement} from './economy.js';
import {mountCompany} from './company-ui.js';
const $=id=>document.getElementById(id);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pretty=value=>esc(JSON.stringify(value,null,2));
let record=null,verified=null,continuation=null,frames=[],cursor=-1,playing=false,timer=null,currentEvent=null,currentNode=null;
let campus=null,capabilities={live:false},selectedDepartment=null,live=false,livePoll=null,lastLiveEvent=0,seenLive=new Set();
let companyControl=null;
let procurement=planProcurement(),procurementHistory=[],mission=null;
try{mission=JSON.parse(localStorage.getItem('genesis-mission')||'null');}catch{}
try{
 const saved=JSON.parse(localStorage.getItem('genesis-procurement')||'null');
 if(saved){procurement=planProcurement(saved.inputs);procurement.priority=saved.inputs.priority;procurementHistory=Array.isArray(saved.history)?saved.history.slice(-50):[];}
}catch{}
function saveProcurement(){
 procurementHistory=procurementHistory.slice(-50);
 try{localStorage.setItem('genesis-procurement',JSON.stringify({inputs:{budget:procurement.budget_constraints.scenario_budget_usd,priority:procurement.priority||'cost'},history:procurementHistory}));}catch{}
}
const roles={Architect:'hq',Executor:'engineering',Observer:'research',Scientist:'evolution','Observer + Scientist':'evolution',Gate:'evolution',Verifier:'operations',System:'hq'};
const responsibilities={
 hq:['Define measurable incident-response objectives','Assign a bounded mission to departments','Coordinate evaluation and report evidence','Escalate consequential actions to humans'],
 engineering:['Compile allowlisted repair procedures','Enforce worker field ownership','Execute deterministic sandbox tests','Report actual patches and assertions'],
 research:['Analyze internal development evidence','Compare competing hypotheses','Trace findings to actual executions','External research integration is not connected'],
 operations:['Diagnose three incident families','Execute configured evidence-gathering tools','Verify service restoration in memory','No production systems are connected'],
 economy:['Compute budget-constrained recommendations','Compare explicitly labeled planning scenarios','Record decision criteria and risk','Require human review; execute no purchases'],
 evolution:['Generate competing structured team mutations','Test on fresh independent validation cases','Reject regressions and unproven changes','Persist verified procedures and memory'],
 core:['Connect to the long-term CORE vision','Explore human–AI collective intelligence','Represent future departments and projects','Gateway only; CORE World is not implemented here']
};
function getNode(id,source=record){return source?.nodes?.find(n=>n.id===id);}
function metrics(){return record?.sealed_comparison;}
function context(markup){$('context-content').innerHTML=markup;$('context').classList.remove('hidden');$('welcome').classList.add('exploring');}
function title(department){
 const d=DEPARTMENTS.find(item=>item.id===department),future=department==='core',prototype=department==='economy';
 return '<span class="context-icon" style="color:'+d.color+'">'+d.icon+'</span><span class="capability '+(future?'future':prototype?'prototype':'')+'">'+d.status+'</span><h2>'+d.name+'</h2><p>'+d.description+'</p>';
}
function showDepartment(id){
 selectedDepartment=id;campus?.selectDepartment(id);
 document.querySelectorAll('[data-dock]').forEach(b=>b.classList.toggle('active',b.dataset.dock===id));
 if(id==='hq')return showHQ();
 if(['growth','product'].includes(id)||companyControl?.state.mission.id&&['research','engineering','operations'].includes(id))return companyControl.department(id);
 if(id==='economy')return showEconomy();
 if(id==='evolution')return showEvolution();
 let markup=title(id);
 if(id==='core')markup+='<h3>Creation Of Reborn Earth</h3><p>A participatory civilization where artificial and human intelligence collaborate to understand problems, develop solutions and coordinate meaningful progress.</p><p>CORE GENESIS is the autonomous organization supporting this mission. This campus is its first operational demonstration, not the complete civilization.</p>';
 markup+='<h3>'+(id==='core'?'The future connection':'Genuine capabilities')+'</h3><ul class="responsibilities">'+responsibilities[id].map(t=>'<li>'+esc(t)+'</li>').join('')+'</ul>';
 if(id==='operations'&&metrics()){
  const m=metrics();markup+='<div class="evidence-chip"><b>'+m.baseline.passed+'/'+m.baseline.total+' → '+m.active.passed+'/'+m.active.total+'</b>Same sealed incidents, initial and retained team.<br>Experiment '+esc(record.id)+'</div><button class="primary" data-action="story">Follow the incident mission <span>↗</span></button>';
 }
 if(id==='research')markup+='<p class="callout">Natural-language explanations are model hypotheses. Only executable rules and measured outcomes are independently verified.</p>';
 if(id==='engineering')markup+='<p class="fine">The interpreter uses a bounded JSON rule language. It does not execute generated shell commands, source code, or repairs to production services.</p>';
 if(id==='core')markup+='<div class="mission-step"><b>01</b><div>CORE CIVILIZATION<small>Specialized intelligence collaborating on real problems.</small></div></div><div class="mission-step"><b>02</b><div>CORE WORLD & COLLECTIVE INTELLIGENCE<small>Human exploration, participation and contribution.</small></div></div><div class="mission-step"><b>03</b><div>CORE INTELLIGENCE & BUSINESS<small>Evidence, simulation and useful practical services.</small></div></div><div class="mission-step"><b>04</b><div>CORE GOVERNANCE<small>Transparency, rights, privacy and human authority.</small></div></div>';
 context(markup);
}
function showHQ(){
 if(companyControl)return companyControl.office();
 let markup=title('hq')+'<p>Create a scoped company mission. HQ builds a transparent coordination plan locally; live Nemotron reasoning starts only through a separate explicit action.</p><label for="mission-objective">What should the company accomplish?</label><textarea id="mission-objective" maxlength="600">Improve incident response while preserving service contracts and unrelated configuration.</textarea><button class="primary" data-action="create-mission">Create company mission <span>↗</span></button>';
 if(mission)markup+=renderMission();
 else markup+='<h3>Today’s operational scope</h3><p>Software incident diagnosis and configuration remediation, measured on deterministic development, regression and unseen validation tasks.</p><button class="secondary" data-action="story">Inspect the genuine incident mission ↗</button>';
 markup+='<h3>Meet the coordinating team</h3>'+['Architect','Executor','Observer','Scientist'].map(role=>'<button class="secondary" data-agent="'+role+'">◈ '+role+' <span>↗</span></button>').join('')+'<p class="fine">No unrestricted task execution. Agents propose and test; humans retain authority over real-world actions.</p>';
 context(markup);
 if(mission)$('mission-objective').value=mission.objective;
}
function renderMission(){
 return '<h3>Mission '+esc(mission.id)+'</h3><span class="capability prototype">DETERMINISTIC COORDINATION PLAN</span>'+mission.assignments.map((step,i)=>'<div class="mission-step"><b>0'+(i+1)+'</b><div>'+esc(step.action)+'<small>'+esc(step.department)+' · '+esc(step.status)+'</small></div></div>').join('')+'<p class="callout">Success: pass all six sealed contracts; lose no previously passing case; reduce executed work only after full correctness.</p>'+(capabilities.live?'<button class="primary" data-action="live">Start bounded live mission <span>↗</span></button><p class="fine">Real Crusoe inference · $2 project cap · up to 12 physical attempts in two cycles · one concurrent request. This explicit button spends existing credits.</p>':'<button class="secondary" data-action="story">Watch a genuine completed mission ↗</button><p class="fine">Public world: verified replay only. Run python3 -m core_genesis.server locally to start budget-controlled live reasoning.</p>')+'<div id="mission-error" class="fine"></div>';
}
function createMission(){
 const objective=$('mission-objective').value.trim();if(objective.length<12){$('mission-objective').focus();return;}
 mission={id:'M-'+Date.now().toString(36).toUpperCase(),objective,created_at:new Date().toISOString(),mode:'deterministic_coordination_plan',status:'planned',human_authority:'Required for consequential actions',
  success_criteria:[{metric:'sealed_pass_count',target:6},{metric:'regressions',target:0},{metric:'work_units',policy:'Reduce only after full correctness'}],
  assignments:[{department:'Genesis HQ',action:'Define measurable service-restoration criteria',status:'plan created'},
   {department:'Operations',action:'Attempt bounded incident diagnosis',status:'awaiting execution'},
   {department:'Research',action:'Analyze development-only failure evidence',status:'awaiting execution'},
   {department:'Evolution Lab',action:'Propose, compete and independently test team mutations',status:'awaiting execution'},
   {department:'Engineering',action:'Verify the retained generation on sealed cases',status:'awaiting execution'}]};
 try{localStorage.setItem('genesis-mission',JSON.stringify(mission));}catch{}
 showHQ();
}
function showEconomy(){
 const rec=procurement.recommended_action;
 let markup=title('economy')+'<p>Plan an additional five million tokens of inference. Change the scenario budget or priority to recompute an accountable recommendation.</p><label for="scenario-budget">Scenario budget: $<span id="scenario-budget-value">'+procurement.budget_constraints.scenario_budget_usd.toFixed(2)+'</span></label><input type="range" id="scenario-budget" min="0" max="2" step=".05" value="'+procurement.budget_constraints.scenario_budget_usd+'"><label for="procurement-priority">Decision priority</label><select id="procurement-priority"><option value="cost">Lowest feasible cost</option><option value="reliability">Scenario reliability</option><option value="latency">Scenario response speed</option></select><div id="procurement-result"></div>';
 context(markup);$('procurement-priority').value=procurement.priority||'cost';renderProcurement();
}
function renderProcurement(){
 const rec=procurement.recommended_action;
 $('procurement-result').innerHTML='<div class="decision"><strong>'+esc(rec.name)+'</strong><p>'+esc(rec.reason)+'</p><b>$'+rec.estimated_cost_usd.toFixed(2)+' estimated scenario cost</b><small>HUMAN REVIEW REQUIRED · NO TRANSACTION CAPABILITY</small></div><h3>Alternatives actually computed</h3>'+procurement.alternatives.map(a=>'<div class="history-row"><b>'+esc(a.name)+'</b><br>$'+a.estimated_cost_usd.toFixed(2)+' · '+(a.feasible?'feasible':esc(a.rejection))+'<br><small>'+esc(a.price_basis)+'</small></div>').join('')+'<p class="source-note">Shared-pool unit prices: Crusoe snapshot, 17 October 2026. <a href="https://www.crusoe.ai/cloud/pricing" target="_blank" rel="noreferrer">Source ↗</a><br>All capacity, latency and reliability values are scenario fixtures. Other alternatives use synthetic prices. This is not a live market comparison.</p><button class="secondary" data-action="review-procurement">Record a human-review request</button><button class="secondary" data-action="procurement-evidence">Inspect complete decision object ↗</button><p class="fine">Scenario changes do not change the real $2 inference cap or spend credits. '+procurementHistory.length+' local decision-history entries.</p>';
}
function recomputeProcurement(){
 const budget=Number($('scenario-budget').value),priority=$('procurement-priority').value;
 procurement=planProcurement({budget,priority});procurement.priority=priority;
 procurementHistory.push({time:new Date().toISOString(),action:'recomputed',scenario_budget_usd:budget,priority,recommendation:procurement.recommended_action.alternative_id});
 saveProcurement();$('scenario-budget-value').textContent=budget.toFixed(2);renderProcurement();
}
function showEvolution(){
 const m=metrics();
 let markup=title('evolution')+'<p>The organization changes how it works. Nemotron proposes competing team configurations; independent tests decide which version survives.</p>';
 if(m)markup+='<div class="evidence-chip"><b>'+m.baseline.passed+'/'+m.baseline.total+' → '+m.active.passed+'/'+m.active.total+'</b>Sealed cases in this experiment. '+record.decisions.filter(d=>d.action==='promote').length+' verified promotions; '+record.decisions.filter(d=>d.action==='rollback').length+' rollback.</div>';
 else if(record)markup+='<p class="callout">Sealed evaluation has not completed. No sealed score is inferred.</p>';
 markup+='<button class="primary" data-action="story">Watch verified evolution <span>↗</span></button><h3>What actually changes</h3><p>Instructions, worker specialization, tool access, execution order, review policy, evidence caching and development-verified procedural memory.</p><p class="callout">The campus’s worker pavilions and workflow connections update only when a recorded promotion makes that configuration active.</p><h3>Accepted ancestry</h3>';
 const sources=[record,continuation];
 for(const source of sources)for(const decision of source?.decisions||[]){
  markup+='<button class="secondary" data-decision="'+esc(source.id)+':'+esc(decision.generation)+'">'+(decision.action==='promote'?'✧ PROMOTED':'↶ REJECTED')+' · '+esc(decision.candidate_id||'invalid proposal')+'<br><small>'+esc(decision.kind.replaceAll('_',' '))+'</small></button>';
 }
 if(verified)markup+='<h3>Latest independently verified team</h3><p><b>'+verified.sealed_comparison.active.passed+'/'+verified.sealed_comparison.active.total+' on a new sealed shard.</b> Its restored starting team also passed 6/6; the later candidates were rejected for failing to improve executed work.</p><button class="secondary" data-action="latest">Inspect latest continuation evidence ↗</button>';
 markup+='<p class="fine">All source experiments remain available. Different sealed shards are not treated as identical-task comparisons.</p>';context(markup);
 if(companyControl?.state.mission.evolution)$('context-content').insertAdjacentHTML('beforeend','<button class="secondary" data-company="evolution">Real CORE mission · verified workflow improvement ↗</button>');
}
function showAgent(actor){
 const latest=actor.lastAction;
 if(actor.company||latest?.company){
  const missionState=companyControl?.state.mission;
  return context('<span class="context-icon">◈</span><span class="capability">'+(missionState.status==='running'?'LIVE COMPANY ACTIVITY':'RECORDED COMPANY ACTIVITY')+'</span><h2>'+esc(actor.role)+'</h2><p>'+esc(actor.role.startsWith('Synthetic')?'Synthetic persona, not a real user. Its feedback is a model hypothesis.':'A named department actor driven by actual mission events.')+'</p><h3>Mission</h3><p>'+esc(missionState.objective||'No mission')+'</p><h3>Current state</h3><p>'+esc(missionState.departments?.[actor.home]?.state||'idle')+' · Configuration V'+esc(missionState.configuration?.version||0)+'</p><h3>Last recorded activity</h3><p>'+esc(latest?.message||'No event dispatched')+'</p><button class="secondary" data-company="audit">Inspect actual handoffs and audit ↗</button>');
 }
 context('<span class="context-icon" style="color:#6ea698">◈</span><span class="capability">'+(actor.worker?'CONFIGURED WORKER':'LOGICAL AGENT ROLE')+'</span><h2>'+esc(actor.role)+'</h2><p>'+(actor.worker?esc(actor.specialty)+' specialist. '+esc(actor.instructions):'A real logical role in the bounded agent organization. Movement follows recorded workflow events; idle bobbing is decorative.')+'</p><h3>Current mission</h3><p>'+esc(live?mission?.objective:record?.objective||'Evidence not loaded')+'</p><h3>Latest recorded action</h3><p>'+esc(latest&&typeof latest==='object'?latest.message:latest||'No event dispatched to this agent in the current playback.')+'</p>'+(actor.tools?'<h3>Actual granted tools</h3><p>'+actor.tools.map(esc).join(' · ')+'</p>':'')+'<button class="secondary" data-action="event-evidence">Inspect available evidence ↗</button>');
}
function evidence(title,markup){$('evidence-title').textContent=title;$('evidence-content').innerHTML=markup;$('evidence-modal').showModal();}
function sourceLink(source){
 const files={'20261017-123548-c377d6':'story','20261017-123736-61ea83':'continuation','20261017-124001-ae2c9e':'verified'};
 const href=files[source.id]?'./evidence/'+files[source.id]+'.json':capabilities.live?'/api/experiments/'+encodeURIComponent(source.id):null;
 return href?'<a class="text-button" href="'+esc(href)+'" target="_blank" rel="noreferrer">Open original execution record ↗</a>':'';
}
function showEvidence(source=record){
 if(!source)return;
 const sealed=source.sealed_comparison;
 evidence('Genuine experiment · '+source.id,'<p>This is captured execution, not a new API request. Crusoe-hosted NVIDIA Nemotron generated the strategies; local deterministic checks authorized promotion and rollback.</p><div class="metric-row"><div><b>'+(source.inference_calls||0)+'</b><span>PHYSICAL MODEL ATTEMPTS</span></div><div><b>'+(source.total_tokens||0).toLocaleString()+'</b><span>REPORTED TOKENS</span></div><div><b>$'+Number(source.cost_usd||0).toFixed(6)+'</b><span>ESTIMATED USAGE + FAILURE RESERVES</span></div></div>'+(sealed?'<p>Same sealed cases: <b>'+sealed.baseline.passed+'/'+sealed.baseline.total+' → '+sealed.active.passed+'/'+sealed.active.total+'</b>. Sealed results are never used for subsequent mutation in this experiment.</p>':'<p class="rejected">No sealed outcome is available in this record. Existing promotions remain independently replayable.</p>')+(source.decisions||[]).map(d=>'<div class="evidence-event '+(d.action==='promote'?'verified':'rejected')+'"><b>'+esc(d.action.toUpperCase())+' · '+esc(d.candidate_id)+'</b><small>Parent '+esc(d.parent_id)+' · mutation round '+d.generation+'</small>'+esc(d.reason)+'</div>').join('')+'<h3>Reproduce without inference</h3><pre>python3 scripts/verify_evidence.py experiments/'+source.id+'.json</pre>'+sourceLink(source));
}
function showDecision(identity){
 const [id,generation]=identity.split(':'),source=[record,continuation,verified].find(s=>s?.id===id),d=source?.decisions.find(item=>item.generation===Number(generation));if(!d)return;
 const node=getNode(d.candidate_id,source);
 evidence(d.action.toUpperCase()+' · '+d.candidate_id,'<p>'+esc(d.reason)+'</p><h3>Actual mutation and its measured gate</h3><pre>'+pretty({decision:d,changes:node?.changes,team:node?.team})+'</pre>'+sourceLink(source));
}
function eventEvidence(){
 if(!currentEvent)return showEvidence();
 evidence(currentEvent.role+' · recorded action','<p>Exact event from '+esc(record.id)+'. Replay timing is compressed. No synthetic communication or model output is added.</p><pre>'+pretty(currentEvent)+'</pre>'+(currentNode?'<h3>Actual active configuration</h3><pre>'+pretty(currentNode.team)+'</pre>':''));
}
function buildFrames(source){
 // Select authentic milestones in original order; never synthesize events.
 const chosen=[];let firstFailure=false,firstPass=false,seenExecution=new Set();
 for(const event of source.events){
  const message=event.message;
  let include=event.role==='Architect'&&message==='Objective and measurable criteria defined'
   ||event.role==='Observer'
   ||event.role==='Scientist'&&message.startsWith('Candidate registered')
   ||event.role==='Gate';
  if(event.role==='Executor'&&message.startsWith('Executing')&&!seenExecution.has(event.node_id)){seenExecution.add(event.node_id);include=true;}
  if(event.role==='Verifier'&&message==='FAIL'&&!firstFailure){firstFailure=true;include=true;}
  if(event.role==='Verifier'&&message==='PASS'&&!firstPass){firstPass=true;include=true;}
  if(include)chosen.push(event);
 }
 return chosen;
}
function organization(node,promoted=false){
 if(!node)return;currentNode=node;campus?.configure(node.team,node.id,promoted);
 if(promoted){campus?.selectDepartment('evolution');$('generation-name').closest('.generation-bubble').classList.add('verified-generation');setTimeout(()=>$('generation-name').closest('.generation-bubble').classList.remove('verified-generation'),3000);}
 $('generation-name').textContent='Generation '+node.generation;
 $('generation-detail').textContent=node.team.agents.length+' configured worker'+(node.team.agents.length===1?'':'s')+' · '+[...new Set(node.team.agents.flatMap(a=>a.tools))].length+' evidence tools';
}
function dispatch(event){
 currentEvent=event;const dept=roles[event.role]||'hq';campus?.showEvent(event,dept);
 if(event.role==='Gate'&&event.message.startsWith('PROMOTE'))organization(getNode(event.node_id),true);
 $('playback-title').textContent=event.message;
 $('playback-detail').textContent=event.role+' · '+(event.node_id||'company mission')+' · '+(live?'actual local execution':'recorded event; timing compressed');
 const gate=event.role==='Gate'?(record.decisions||[]).find(d=>d.candidate_id===event.node_id&&d.generation===event.generation):null;
 const comparison=gate?.comparison?.held_out;
 $('event-bubble').classList.remove('hidden');$('event-bubble').innerHTML='<span>'+esc(event.role.toUpperCase())+' · '+(live?'LIVE':'RECORDED')+'</span><p>'+esc(event.message.slice(0,220))+'</p>'+(comparison?'<small>Fresh validation '+comparison.parent.passed+'/'+comparison.parent.total+' → '+comparison.candidate.passed+'/'+comparison.candidate.total+' · '+esc(gate.kind.replaceAll('_',' '))+'</small>':'');
 $('progress').style.width=((cursor+1)/Math.max(1,frames.length)*100)+'%';$('step-count').textContent=(cursor+1)+' / '+frames.length;
 if(event.role==='Observer'||event.role==='Gate')$('welcome').classList.add('exploring');
}
function advance(){
 if(cursor>=frames.length-1){pause();$('playback-title').textContent='Experiment complete. The independently verified team remains active.';$('playback-detail').textContent=record.sealed_comparison?'Sealed outcome '+record.sealed_comparison.active.passed+'/'+record.sealed_comparison.active.total+' · rejected branches stay in the evidence history.':'Inference stopped safely; no sealed outcome is claimed.';return;}
 cursor++;dispatch(frames[cursor]);
}
function pause(){playing=false;clearInterval(timer);$('play').textContent='▶';$('play').setAttribute('aria-label','Play recorded experiment');}
function play(){
 if(live)return;if(!record)return;
 if(cursor>=frames.length-1){cursor=-1;organization(getNode('g0'));}
 if(playing)return pause();
 playing=true;$('play').textContent='Ⅱ';$('play').setAttribute('aria-label','Pause recorded experiment');advance();timer=setInterval(advance,4200);
}
function startStory(){
 if(live)return;pause();cursor=-1;organization(getNode('g0'));$('context').classList.add('hidden');$('welcome').classList.add('exploring');play();
}
async function startLive(){
 if(!capabilities.live||live||!mission)return;
 pause();const button=$('context-content').querySelector('[data-action="live"]');if(button)button.disabled=true;
 try{
  const response=await fetch('/api/evolve',{method:'POST',headers:{'Content-Type':'application/json','X-Genesis-Action':'evolve'},body:JSON.stringify({objective:mission.objective,generations:3})});
  const value=await response.json();if(!response.ok)throw Error(value.error||'Live request rejected');
  live=true;currentNode=null;lastLiveEvent=0;seenLive.clear();$('mode-label').textContent='LIVE · EXPLICIT ACTION';$('playback-type').textContent='ACTUAL LOCAL ENGINE · CRUSOE / NEMOTRON';$('context').classList.add('hidden');$('play').disabled=true;
  livePoll=setInterval(pollLive,1200);await pollLive();
 }catch(error){if($('mission-error'))$('mission-error').textContent=error.message;if(button)button.disabled=false;}
}
async function pollLive(){
 try{
  const next=await(await fetch('/api/state')).json();record=next;
  for(const event of next.events.slice(lastLiveEvent)){
   if(event.role==='Architect'||event.role==='Observer'||event.role==='Gate'||event.role==='Scientist'||event.role==='Executor'&&event.message!=='Inference completed')dispatch(event);
  }
  lastLiveEvent=next.events.length;
  if(mission){
   if(next.objective_analysis)mission.assignments[0].status='criteria defined by Architect';
   if(next.runs?.some(r=>r.node_id==='g0'))mission.assignments[1].status='baseline incident attempts recorded';
   if(next.events.some(e=>e.role==='Observer'))mission.assignments[2].status='development analysis recorded';
   if(next.decisions.length)mission.assignments[3].status=next.decisions.filter(d=>d.action==='promote').length+' promotions; '+next.decisions.filter(d=>d.action==='rollback').length+' rollbacks recorded';
   if(next.sealed_comparison)mission.assignments[4].status=next.sealed_comparison.active.passed+'/'+next.sealed_comparison.active.total+' sealed contracts passed';
   else if(next.status!=='running')mission.assignments[4].status='no sealed outcome; inference stopped';
  }
  if(!currentNode&&getNode('g0'))organization(getNode('g0'));
  if(next.active_node_id&&getNode(next.active_node_id))organization(getNode(next.active_node_id));
  $('step-count').textContent=next.inference_calls+' API';
  if(next.status!=='running'){
   clearInterval(livePoll);live=false;$('play').disabled=false;$('mode-label').textContent='RECORDED · LIVE RUN ENDED';frames=buildFrames(record);cursor=frames.length-1;
   $('playback-title').textContent=next.status==='complete'?'Live mission complete; independent evidence saved.':'Live mission stopped safely.';
   $('playback-detail').textContent=next.error_detail||next.inference_stop_reason||'Actual measured outcomes are available in evidence.';
   mission.status=next.status;mission.experiment_id=next.id;try{localStorage.setItem('genesis-mission',JSON.stringify(mission));}catch{}
  }
 }catch(error){$('playback-detail').textContent='Local engine unavailable; no additional inference requested.';}
}
function ready(){$('loading').classList.add('hidden');}
campus=createCampus($('world'),{onDepartment:showDepartment,onAgent:showAgent,onReady:ready,onError:()=>{$('loading').innerHTML='<h2>WebGL is unavailable.</h2><p>The company remains accessible through the department buttons.</p><button id="fallback-enter" class="primary">Explore company evidence</button>';setTimeout(()=>{$('fallback-enter').onclick=ready;},0);}});
companyControl=mountCompany({campus:()=>campus,openContext:context,showEvidence:evidence,escape:esc,capabilities:()=>capabilities});
const dock=$('department-dock');dock.innerHTML=DEPARTMENTS.map(d=>'<button data-dock="'+d.id+'" style="--color:'+d.color+'"><span class="dock-icon">'+d.icon+'</span>'+d.short+'</button>').join('');
document.addEventListener('click',event=>{
 const dept=event.target.closest('[data-dock]');if(dept)showDepartment(dept.dataset.dock);
 const agent=event.target.closest('[data-agent]');if(agent&&campus?.actors.get(agent.dataset.agent))showAgent(campus.actors.get(agent.dataset.agent));
 const decision=event.target.closest('[data-decision]');if(decision)showDecision(decision.dataset.decision);
 const action=event.target.closest('[data-action]')?.dataset.action;
 if(action==='story')startStory();if(action==='create-mission')createMission();if(action==='live')startLive();
 if(action==='event-evidence')eventEvidence();if(action==='latest')showEvidence(verified);
 if(action==='procurement-evidence')evidence('Computed procurement decision','<p>Deterministic scenario. No external research, API call or purchase was made.</p><pre>'+pretty({...procurement,decision_history:[...procurement.decision_history,...procurementHistory]})+'</pre>');
 if(action==='review-procurement'){procurementHistory.push({time:new Date().toISOString(),action:'human_review_requested',detail:'Recorded locally only; no message sent and no transaction authorized.'});procurement.status='human_review_requested';saveProcurement();renderProcurement();}
});
document.addEventListener('input',event=>{if(event.target.id==='scenario-budget')recomputeProcurement();});
document.addEventListener('change',event=>{if(event.target.id==='procurement-priority')recomputeProcurement();});
$('play').onclick=play;$('next').onclick=()=>{pause();advance();};$('watch').onclick=()=>showDepartment('hq');
$('evidence-button').onclick=()=>showEvidence();$('close-evidence').onclick=()=>$('evidence-modal').close();
$('close-context').onclick=()=>{$('context').classList.add('hidden');};
$('home').onclick=()=>{campus?.reset();$('context').classList.add('hidden');$('welcome').classList.remove('exploring');};
$('vision').onclick=()=>showDepartment('core');
$('zoom-in').onclick=()=>campus?.zoomBy(.15);$('zoom-out').onclick=()=>campus?.zoomBy(-.15);$('reset-view').onclick=()=>campus?.reset();
addEventListener('keydown',event=>{if(event.key==='Escape')$('context').classList.add('hidden');});
Promise.all([fetch('./evidence/story.json').then(r=>r.json()),fetch('./evidence/verified.json').then(r=>r.json()),fetch('./evidence/continuation.json').then(r=>r.json()),fetch('./capabilities.json').then(r=>r.json())]).then(([story,last,previous,caps])=>{
 record=story;verified=last;continuation=previous;capabilities=caps;frames=buildFrames(record);organization(getNode('g0'));
 if(caps.company)companyControl.refresh();
 $('playback-detail').textContent=record.id+' · '+frames.length+' authentic milestones · zero new inference';
 $('step-count').textContent='0 / '+frames.length;
 window.genesis={get record(){return record;},get node(){return currentNode;},get frames(){return frames;},get procurement(){return procurement;},get mission(){return mission;},get campus(){return campus;},company:companyControl};
}).catch(error=>{$('playback-detail').textContent='Evidence could not load. No results are inferred.';console.error('Evidence load failed',error);});
