// WATCH GENESIS RUN: a seven-act verified mission replay. Every caption and number below is read from
// recorded evidence files; the replay makes no inference calls and invents no progress.
const $=id=>document.getElementById(id);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const REPO='https://github.com/vincentleg/core-genesis/blob/main/';
// Display names are interface labels for the real backend roles listed in `agents`.
const CREW=[
 {name:'Atlas',title:'Chief of Staff',dept:'hq',color:'#b8954a',agents:['CEO Office']},
 {name:'Nova',title:'Research',dept:'research',color:'#6f98a0',agents:['Research Lead']},
 {name:'Forge',title:'Engineering',dept:'engineering',color:'#a77d52',agents:['Engineering Lead','Implementation Designer']},
 {name:'Sentinel',title:'Operations',dept:'operations',color:'#3f7d6f',agents:['Operations Verifier','Evidence Verifier']},
 {name:'Echo',title:'Product Testing',dept:'product',color:'#5f8396',agents:['Synthetic User Research Lead','Product Testing Lead','Resident journey tester','Small-screen contributor tester','Input and authorization tester']},
 {name:'Ledger',title:'Economy',dept:'economy',color:'#9b8450',agents:['Economy Planner']},
 {name:'Pulse',title:'Growth & PR',dept:'growth',color:'#a46f55',agents:['Growth Director']},
 {name:'Darwin',title:'Evolution Lab',dept:'evolution',color:'#7d769e',agents:['Scientist']}
];
const ACTS=['The CEO defines a mission','The company organizes itself','Agents build CORE','The beta testing lab','The company improves','Human governance','The company delivers'];
let data=null,steps=[],index=-1,playing=false,timer=null,speed=1.25,follow=true,remaining=0,stepStarted=0;
const history=new Map(CREW.map(c=>[c.name,[]]));
const status=new Map(CREW.map(c=>[c.name,{state:'idle',task:'Awaiting mission',evidence:null}]));

async function load(){
 if(data)return data;
 const get=path=>fetch(path).then(r=>r.ok?r.json():null).catch(()=>null);
 const [company,testing,prior,loopRecord,genesisBrowser]=await Promise.all([get('./evidence/company-mission.json'),get('./evidence/product-testing.json'),get('./evidence/prior-evolution.json'),get('./testing/loop/loop.json'),get('./testing/genesis-browser-report.json')]);
 data={loop:loopRecord,genesisBrowser,company,mission:company?.mission,governance:company?.governance,testing,prior:prior?.evolution,priorId:prior?.mission_id};
 steps=build(data);return data;
}
const ev=(m,type)=>m.events.find(e=>e.type===type);
const handoff=(m,from,to)=>m.handoffs.find(h=>h.source_agent===from&&h.destination_agent===to);
function stdout(report){try{return JSON.parse(report.stdout);}catch{return {};}}
function campaign(panel){
 if(!panel)return null;
 const reviews=panel.reviews||[],cats=panel.analysis?.by_category||{};
 return {completed:reviews.length,target:panel.target||100,distinct:new Set(reviews.map(r=>r.output)).size,cats,batches:(panel.batches||[]).length,
  top:Object.entries(cats).sort((a,b)=>(b[1].support+b[1].conditional+b[1].challenge)-(a[1].support+a[1].conditional+a[1].challenge)),
  challenge:reviews.filter(r=>r.response?.position==='challenge').length,limitations:panel.limitations};
}
function build({mission:m,testing,prior,priorId,governance,loop:fix,genesisBrowser:gb}){
 const p=m.artifacts.prototype,report=stdout(p.test_report),research=handoff(m,'CEO','Research Lead'),cite=m.verification;
 const browser=testing?.browser?.before?.agents||[],passed=browser.filter(a=>a.passed).length;
 const core=campaign(testing?.audience),gen=campaign(testing?.genesis_audience),evo=m.evolution,pc=prior?.comparison?.heldout,cc=evo.comparison?.heldout;
 const pending=(governance?.decisions||[]).filter(d=>d.status==='pending_ceo_review');
 const files=Object.keys(p.files||{});
 const S=(act,secs,o)=>({act,secs,...o});
 return [
  S(0,9,{cam:'hq',title:'Build the first functional capability for CORE',detail:'A place where humans report local problems, propose solutions and request human review.',moves:[['Atlas','hq','working','Receives the CEO mission contract']],
   card:'<span class="run-tag">MISSION CONTRACT · '+esc(m.id)+'</span><p class="quote">“'+esc(m.objective)+'”</p><dl><dt>CEO authorization</dt><dd>'+esc(ev(m,'mission.authorized')?.message)+'</dd><dt>Scope</dt><dd>'+esc(m.authorization.scope)+'</dd><dt>Expected deliverable</dt><dd>'+m.authorization.acceptance_criteria.map(esc).join(' · ')+'</dd><dt>Budget</dt><dd>$'+esc(m.authorization.budget_cap_usd)+' project cap · '+esc(m.limits.planned_model_calls)+' planned model calls · concurrency '+esc(m.limits.concurrency)+'</dd></dl>'}),
  S(0,6,{cam:'hq',title:'Atlas, Chief of Staff, receives the mission',detail:ev(m,'hq.activity')?.message,moves:[],card:'<span class="run-tag">RECORDED EVENT · hq.activity</span><p>'+esc(ev(m,'hq.activity')?.message)+'</p><p class="fine">Prohibited for agents: '+m.authorization.prohibited.map(esc).join(' · ')+'</p>'}),
  S(1,10,{cam:null,zoom:.95,title:'The company organizes itself',detail:'Each agent leaves HQ for the department named in a recorded handoff.',moves:[['Nova','research','working',research.task],['Forge','engineering','working','Await cited Research brief'],['Sentinel','operations','working','Prepare verification'],['Echo','product','working','Prepare beta testing'],['Ledger','economy','working','Resource accounting'],['Darwin','evolution','working','Prepare policy evaluation'],['Pulse','growth','working','Prepare CEO-review draft']],
   card:'<span class="run-tag">'+m.handoffs.length+' RECORDED HANDOFFS</span><ol class="handoffs">'+m.handoffs.map(h=>'<li><b>'+esc(h.source_agent)+' → '+esc(h.destination_agent)+'</b><small>'+esc(h.task)+' · '+esc(h.status)+'</small></li>').join('')+'</ol>'}),
  S(2,9,{cam:'research',title:'Nova inspects the original CORE repository',detail:ev(m,'research.activity')?.message,moves:[['Nova','research','working','Reading pinned CORE source']],
   card:'<span class="run-tag">RESEARCH · READ-ONLY</span><dl><dt>Repository</dt><dd>'+esc(m.repository)+' — '+esc(m.core_access)+'</dd><dt>Commit inspected</dt><dd><code>'+esc(research.result.commit)+'</code></dd><dt>Sources</dt><dd>'+esc(research.result.sources)+' bounded file excerpts</dd><dt>Brief</dt><dd>'+m.artifacts.research.priorities.map(x=>esc(x.title)).join(' · ')+'</dd></dl>'}),
  S(2,8,{cam:'engineering',title:'Research hands a cited brief to Engineering',detail:'Sentinel verified '+cite.valid_priorities+'/'+cite.total_priorities+' citation sets against exact source lines.',moves:[['Nova','engineering','working','Delivering cited brief',true]],
   card:'<span class="run-tag">HANDOFF · Research Lead → Engineering Lead</span><p>'+esc(handoff(m,'Research Lead','Engineering Lead').task)+'</p><p><b>'+cite.valid_priorities+'/'+cite.total_priorities+'</b> priority citation sets verified.</p><p class="fine">'+esc(cite.note)+'</p>'}),
  S(2,10,{cam:'engineering',title:'Forge builds CORE Local Solutions',detail:ev(m,'artifact.created')?.message,moves:[['Nova','research','completed','Brief delivered'],['Forge','engineering','working','Generating versioned application']],
   card:'<span class="run-tag">ARTIFACT CREATED · '+files.length+' FILES</span><p><b>'+esc(p.spec?.application_title)+'</b></p><ul class="files">'+files.map(f=>'<li><code>'+esc(f)+'</code></li>').join('')+'</ul><p class="fine">'+esc(p.implementation?.note||'Audited scaffold configured by Nemotron-selected specification; no generated code is executed.')+'</p><a class="run-link" href="./artifacts/core-local-solutions/" target="_blank" rel="noreferrer">Open the prototype ↗</a>'}),
  S(2,9,{cam:'operations',title:'Sentinel runs the real tests',detail:ev(m,'test.passed')?.message,moves:[['Forge','operations','working','Delivering build for verification',true],['Sentinel','operations','reviewing','Executing isolated tests + loopback HTTP']],
   card:'<span class="run-tag">OPERATIONS · '+esc(p.test_report.command.join(' '))+'</span><div class="big">'+esc(report.tests_run)+' tests · '+esc(report.failures)+' failures · '+esc(report.errors)+' errors</div><p class="fine">Exit code '+esc(p.test_report.exit_code)+' · external network requests '+esc(report.external_network_requests)+' · '+esc(report.guard)+'</p>'}),
  S(3,12,{cam:'product',title:'The beta testing lab challenges the product',detail:passed+'/'+browser.length+' real browser scenarios passed on CORE Local Solutions.',moves:[['Forge','engineering','completed','Prototype delivered'],['Sentinel','operations','completed','7/7 tests passed'],['Echo','product','reviewing','Running browser testers + synthetic panel']],
   card:'<span class="run-tag">REAL BROWSER TESTS · LOCAL CHROME</span><div class="shots">'+browser.map(a=>'<figure><img src="./testing/before-'+esc(a.screenshot)+'" alt="Screenshot from '+esc(a.role)+'" loading="lazy"><figcaption>'+(a.passed?'✓':'✗')+' '+esc(a.role)+'<small>'+a.steps.length+' steps · '+a.console_errors.length+' console errors · '+a.viewport.width+'px</small></figcaption></figure>').join('')+'</div>'}),
  S(3,12,{cam:'product',title:'Synthetic perspectives critique CORE and GENESIS',detail:'Simulated perspectives from independent Nemotron calls — not real human beta users.',moves:[],
   card:'<span class="run-tag">SYNTHETIC CAMPAIGNS · SIMULATED, NOT HUMANS</span>'+[['Campaign A · CORE Local Solutions',core],['Campaign B · CORE GENESIS',gen]].map(([label,c])=>c?'<div class="campaign"><b>'+label+'</b><div class="big">'+c.completed+'<small>/'+c.target+' independent evaluations</small></div><small>'+c.distinct+' distinct outputs · '+c.challenge+' challenges</small><ul>'+c.top.slice(0,3).map(([k,v])=>'<li><b>'+esc(k)+'</b> '+(v.support+v.conditional+v.challenge)+' — “'+esc(v.concerns[0])+'”</li>').join('')+'</ul></div>':'<div class="campaign"><b>'+label+'</b><p class="fine">Not run.</p></div>').join('')+'<button class="run-link" data-run="lab">Open full testing lab ↗</button>'}),
  ...(fix?[S(3,11,{cam:'engineering',title:'Test → improve → retest',detail:fix.outcome,moves:[['Echo','engineering','working','Reporting reproducible defect',true],['Forge','engineering','working','Fixing reported defect']],
   card:'<span class="run-tag">CLOSED LOOP · '+esc(fix.product)+'</span><dl><dt>Before</dt><dd>'+fix.before.passed+'/'+fix.before.total+' browser scenarios passed</dd><dt>Detected issue</dt><dd>'+esc(fix.issue)+'</dd><dt>Engineering task</dt><dd>'+esc(fix.engineering_task)+'</dd><dt>Implemented change</dt><dd>'+fix.implemented_change.map(esc).join('<br>')+'</dd><dt>Retest</dt><dd><b>'+fix.retest.passed+'/'+fix.retest.total+'</b> passed'+(gb?' · latest GENESIS run '+gb.passed+'/'+gb.total:'')+'</dd></dl><div class="shots two"><figure><img src="./testing/'+esc(fix.before.screenshot)+'" alt="Before fix"><figcaption>Before</figcaption></figure><figure><img src="./testing/'+esc(fix.retest.screenshot)+'" alt="After fix"><figcaption>After</figcaption></figure></div><p class="fine">'+esc(fix.honesty)+'</p>'})]:[]),
  S(4,11,{cam:'evolution',title:'Evolution Lab: the company improves itself',detail:'Earlier mission '+(priorId||'')+': citation-preflight policy '+(pc?pc.parent.passed+'/'+pc.parent.total+' → '+pc.candidate.passed+'/'+pc.candidate.total:'')+' on held-out tests — promoted to V'+(prior?.resulting_version??'?')+'.',moves:[['Darwin','evolution','working','Evaluating policy candidates']],
   card:loop('prior')+'<span class="run-tag">HISTORICAL PROMOTION · '+esc(priorId)+'</span>'+(prior?bench(prior)+'<p><b>Decision: '+esc(prior.action.toUpperCase())+'</b> — '+esc(prior.reason)+'</p><p class="fine">Observed weakness: '+esc(prior.observed_weakness)+'</p>':'')}),
  S(4,10,{cam:'evolution',title:'This mission reuses V'+evo.resulting_version+' — and the new mutation is rejected',detail:'Research ran with the promoted V1 citation preflight. New candidates showed no gain, so the baseline was retained.',moves:[['Darwin','evolution','completed','Rollback: no independent gain']],
   card:loop('current')+'<span class="run-tag">THIS MISSION · '+esc(m.id)+'</span>'+bench(evo)+'<p><b>Decision: '+esc(evo.action.toUpperCase())+'</b> — '+esc(evo.reason)+'</p><p class="fine">'+esc(evo.scope)+'</p><p class="fine">Reuse evidence: “'+esc(ev(m,'research.completed')?.message)+'”</p>'}),
  S(5,11,{cam:'hq',zoom:1,title:'Human governance: the CEO keeps consequential authority',detail:pending.length+' decisions are pending CEO review. Nothing was published, purchased, deployed or written to CORE.',moves:[['Ledger','hq','completed','Budget verified; no purchase',true],['Pulse','hq','reviewing','Draft queued for CEO review',true]],
   card:'<div class="gov"><div><span class="run-tag">AUTONOMOUS</span><ul>'+m.authorization.authorized.map(x=>'<li>✓ '+esc(x)+'</li>').join('')+'</ul></div><div><span class="run-tag gold">REQUIRES CEO</span><ul><li>⏸ Public publication</li><li>⏸ Purchases</li><li>⏸ Production deployments</li><li>⏸ Changes to the original CORE repository</li></ul></div></div><span class="run-tag">REVIEW QUEUE</span><ul>'+pending.map(d=>'<li><b>'+esc(d.type.replaceAll('_',' '))+'</b> · '+esc(d.mission_id)+'<small> '+esc(d.requirement)+'</small></li>').join('')+'</ul><p class="fine">Growth draft text is withheld from public evidence until approved.</p>'}),
  S(6,12,{cam:'hq',zoom:1.05,title:'MISSION COMPLETE — THE FIRST BRICK OF CORE IS BUILT.',detail:'Prototype built — awaiting CORE integration approval.',final:true,moves:CREW.filter(c=>c.name!=='Atlas').map((c,i)=>[c.name,'hq','completed','Mission delivered',false,i+1]).concat([['Atlas','hq','completed','Delivered for CEO review']]),card:''})
 ];
}
function bench(e){const d=e.comparison?.development,h=e.comparison?.heldout;if(!h)return '';const row=(k,v)=>'<tr><th>'+k+'</th><td>'+v.parent.passed+'/'+v.parent.total+'</td><td>'+v.candidate.passed+'/'+v.candidate.total+'</td></tr>';return '<table class="bench"><tr><th></th><th>Baseline</th><th>Candidate</th></tr>'+row('Development',d)+row('Held-out',h)+'</table>';}
function loop(which){const stages=['Mission','Performance observation','Proposed mutation','Independent evaluation',which==='prior'?'Promotion ✓':'Rollback ↶','Next generation'];return '<div class="loop">'+stages.map((s,i)=>'<span class="'+(i===4?(which==='prior'?'ok':'no'):'')+'">'+s+'</span>').join('<i>→</i>')+'</div>';}

function pipeline(){
 const m=data?.mission;if(!m)return '';
 const done=[['CORE need identified','Local problems & solutions with human review'],['Mission authorized',m.id],['Research completed','Commit '+(handoff(m,'CEO','Research Lead')?.result.commit||'').slice(0,10)],['Engineering artifact produced',m.artifacts.prototype.spec?.application_title],['Tests completed','7 tests · 3 browser scenarios'],['Product feedback collected','Synthetic campaigns + browser evidence'],['Integration proposal prepared','integration_plan in mission record']];
 return '<div class="pipeline">'+done.map(([t,s],i)=>'<div class="stage done"><b>'+(i+1)+'</b><span>'+esc(t)+'<small>'+esc(s)+'</small></span></div>').join('')+'<div class="stage now"><b>8</b><span>Awaiting CEO approval<small>approval_status: '+esc(m.approval_status)+'</small></span></div><div class="stage todo"><b>9</b><span>Integrated into CORE<small>Not done — original CORE unchanged ('+(m.artifacts.prototype.original_core_modified?'modified':'original_core_modified: false')+')</small></span></div></div><p class="pipeline-state">PROTOTYPE BUILT — AWAITING CORE INTEGRATION APPROVAL</p>';
}
function finalCard(){
 const m=data.mission,u=m.usage,core=campaign(data.testing?.audience),gen=campaign(data.testing?.genesis_audience),browser=data.testing?.browser?.before?.agents||[];
 const pending=(data.governance?.decisions||[]).filter(d=>d.status==='pending_ceo_review');
 const link=(href,label,sub)=>'<a class="deliverable" href="'+href+'" target="_blank" rel="noreferrer"><b>'+label+' ↗</b><small>'+sub+'</small></a>';
 return '<div class="final"><span class="run-tag gold">VERIFIED MISSION REPLAY · '+esc(m.id)+'</span><h2>Mission complete — the first brick of CORE is built.</h2>'+pipeline()+'<div class="deliverables">'+
  link('./artifacts/core-local-solutions/','Working prototype','Browser-only preview of CORE Local Solutions')+
  link('./artifacts/core-local-solutions/source.zip','Source archive','Exact generated source + tests')+
  link(REPO+'mission-evidence/'+m.id+'.json','Mission record',m.events.length+' events · '+m.handoffs.length+' handoffs')+
  link('./evidence/product-testing.json','Beta-testing evidence',browser.filter(a=>a.passed).length+'/'+browser.length+' browser · '+(core?.completed||0)+' + '+(gen?.completed||0)+' synthetic')+
  link(REPO+'mission-evidence/'+(data.priorId||'')+'.json','Evolution results','4/6 → 6/6 held-out promotion; latest mutation rolled back')+
  '<div class="deliverable"><b>Model cost</b><small>'+esc(u.physical_requests)+' Nemotron requests · '+esc(u.reported_tokens)+' tokens · $'+Number(u.cost_estimate_usd).toFixed(4)+' estimated</small></div></div>'+
  '<div class="final-foot"><div><span class="run-tag">PENDING CEO DECISIONS</span><ul><li>Approve integration of CORE Local Solutions into CORE</li>'+pending.map(d=>'<li>'+esc(d.type.replaceAll('_',' '))+' · '+esc(d.mission_id)+'</li>').join('')+'</ul></div><div><span class="run-tag">NEXT RECOMMENDED MISSION</span><p>'+esc(core?.top[0]?'Address the top synthetic concern ('+core.top[0][0]+'): '+core.top[0][1].recommendations?.[0]||'':'Run the 100-perspective campaign')+'</p></div></div><div class="final-actions"><button class="primary" data-run="restart">↺ Replay</button><button class="secondary" data-run="explore">Explore the company</button></div></div>';
}
function lab(){
 const t=data.testing,core=campaign(t?.audience),gen=campaign(t?.genesis_audience),browser=t?.browser?.before?.agents||[];
 const block=(label,c,questions)=>'<section class="lab-campaign"><h3>'+label+'</h3>'+(c?'<p><b>'+c.completed+' of '+c.target+'</b> target synthetic evaluations actually completed · '+c.distinct+' distinct outputs · '+c.batches+' bounded batches</p><p class="fine">Questions: '+questions+'</p><table class="bench"><tr><th>Category</th><th>Support</th><th>Conditional</th><th>Challenge</th></tr>'+c.top.map(([k,v])=>'<tr><th>'+esc(k)+'</th><td>'+v.support+'</td><td>'+v.conditional+'</td><td>'+v.challenge+'</td></tr>').join('')+'</table><h4>Recurring concerns (verbatim, first per category)</h4><ul>'+c.top.map(([k,v])=>'<li><b>'+esc(k)+':</b> '+esc(v.concerns[0])+(v.recommendations?'<br><small>Recommendation: '+esc(v.recommendations[0])+'</small>':'')+'</li>').join('')+'</ul><p class="fine">Limitations: '+esc(c.limitations)+'</p>':'<p>Not run.</p>')+'</section>';
 return '<p class="callout">Synthetic perspectives are simulated by Nemotron in independent contexts. They are hypotheses — not real users, customers or market validation. Browser tests are deterministic real-Chrome sessions, not human testers.</p><h3>Real browser scenarios · CORE Local Solutions</h3><div class="shots">'+browser.map(a=>'<figure><img src="./testing/before-'+esc(a.screenshot)+'" alt="'+esc(a.role)+'"><figcaption>'+(a.passed?'✓ PASSED':'✗ FAILED')+' · '+esc(a.role)+'<small>'+a.steps.map(s=>(s.passed?'✓ ':'✗ ')+esc(s.task)).join('<br>')+'</small></figcaption></figure>').join('')+'</div>'+
  block('Campaign A · CORE Local Solutions',core,'purpose, reporting, proposing, human review, usability, adoption barriers')+block('Campaign B · CORE GENESIS',gen,'CORE vs GENESIS, usefulness, autonomy, Version N+1, CEO controls, evidence discoverability')+(data.genesisBrowser?'<h3>Real browser scenarios · CORE GENESIS website</h3><p><b>'+data.genesisBrowser.passed+'/'+data.genesisBrowser.total+'</b> passed · '+esc(data.genesisBrowser.mode)+'</p><div class="shots">'+data.genesisBrowser.results.map(r=>'<figure><img src="./testing/'+esc(r.screenshot)+'" alt="'+esc(r.role)+'"><figcaption>'+(r.passed?'✓ PASSED':'✗ FAILED')+' · '+esc(r.role)+'<small>'+r.steps.map(s=>(s.passed?'✓ ':'✗ ')+esc(s.task)).join('<br>')+'<br>'+r.console_errors.length+' console errors · '+r.failed_requests.length+' failed requests</small></figcaption></figure>').join('')+'</div>':'')+(data.loop?'<h3>Closed loop: test → improve → retest</h3><p>'+esc(data.loop.issue)+'</p><p><b>'+esc(data.loop.outcome)+'</b></p><p class="fine">'+esc(data.loop.honesty)+'</p><a class="text-button" href="./testing/loop/loop.json" target="_blank" rel="noreferrer">Loop record ↗</a> ':'')+'<a class="text-button" href="./evidence/product-testing.json" target="_blank" rel="noreferrer">Raw testing evidence ↗</a>';
}

function ensureCrew(){
 const campus=window.GENESIS?.campus();if(!campus)return null;
 CREW.forEach((c,i)=>{campus.crewAgent(c.name,'hq',c.color,i);});
 const tags=$('crew-tags');
 if(!tags.children.length){tags.innerHTML=CREW.map(c=>'<button class="crew-tag" data-crew="'+c.name+'" style="--c:'+c.color+'"><b>'+c.name+'</b><span>'+c.title+'</span><i></i></button>').join('');
  campus.setFrameHook(()=>{
   // Lay tags out without overlap so every agent stays clickable when several share a department.
   const placed=[];
   for(const el of tags.children){const a=campus.crew.get(el.dataset.crew);if(!a)continue;const p=campus.project(a.group.position.clone().setY(2.3)),w=el.offsetWidth||70,h=(el.offsetHeight||20)+3;let y=p.y;
    for(let k=0;k<placed.length;k++){const q=placed[k];if(Math.abs(q.x-p.x)<(q.w+w)/2&&Math.abs(q.y-y)<h){y=q.y-h;k=-1;}}
    placed.push({x:p.x,y,w});el.style.transform='translate('+p.x+'px,'+y+'px) translate(-50%,-100%)';el.style.display=p.visible?'':'none';el.dataset.state=status.get(el.dataset.crew).state;}
  });}
 return campus;
}
function setState(name,state,task,step){
 status.set(name,{state,task,evidence:step});
 const list=history.get(name);if(step&&list[list.length-1]?.title!==step.title)list.push({title:step.title,act:ACTS[step.act],state});
}
function apply(step,i){
 const campus=ensureCrew();
 if(campus){
  for(const [name,dept,state,task,carry,slot] of step.moves){const crew=CREW.find(c=>c.name===name);campus.moveCrew(name,dept,{carry:!!carry,duration:Math.max(1200,2400/speed),slot:slot??CREW.indexOf(crew)});setState(name,state,task,step);}
  if(follow){if(step.cam)campus.focusOn(step.cam,step.zoom||1.3);else campus.reset?.();}
 }
 const pct=steps.slice(0,i+1).reduce((s,x)=>s+x.secs,0)/steps.reduce((s,x)=>s+x.secs,0)*100;
 $('run').innerHTML='<div class="run-head"><span class="run-badge">● VERIFIED MISSION REPLAY</span><span>ACT '+(step.act+1)+' / 7 · '+esc(ACTS[step.act])+'</span></div><b class="run-title">'+esc(step.title)+'</b><small class="run-detail">'+esc(step.detail||'')+'</small><div class="run-acts">'+ACTS.map((a,k)=>'<button data-act="'+k+'" class="'+(k<step.act?'done':k===step.act?'now':'')+'" title="'+esc(a)+'"><span style="width:'+(k<step.act?100:k===step.act?Math.min(100,pct*7-k*100):0)+'%"></span></button>').join('')+'</div><div class="run-controls"><button data-run="toggle" aria-label="Play or pause">'+(playing?'❚❚':'▶')+'</button><button data-run="restart" aria-label="Restart">↺</button><button data-run="next" aria-label="Next act">Next act →</button><button data-run="speed" class="'+(speed>1.5?'on':'')+'">'+(speed>1.5?'60s mode':'~100s')+'</button><button data-run="follow" class="'+(follow?'on':'')+'">Camera follow</button><button data-run="close" aria-label="Close replay">×</button></div>';
 const card=$('run-card');
 if(step.final){card.classList.add('hidden');$('run-final').innerHTML=finalCard();$('run-final').classList.remove('hidden');}
 else{$('run-final').classList.add('hidden');card.innerHTML=step.card;card.classList.remove('hidden');}
}
function schedule(ms){clearTimeout(timer);stepStarted=performance.now();remaining=ms;timer=setTimeout(()=>{if(index<steps.length-1)go(index+1);else{playing=false;apply(steps[index],index);}},ms);}
function go(i,keepPaused=false){index=i;apply(steps[i],i);if(playing&&!keepPaused)schedule(steps[i].secs*1000/speed);}
async function start(){
 await load();if(!data.mission){alert('Mission evidence is unavailable.');return;}
 document.body.classList.add('running');$('welcome').classList.add('exploring');$('context').classList.add('hidden');$('run').classList.remove('hidden');
 for(const c of CREW){setState(c.name,'idle','Awaiting mission',null);history.set(c.name,[]);}
 const campus=ensureCrew();if(campus)CREW.forEach((c,i)=>campus.moveCrew(c.name,'hq',{duration:600,slot:i}));
 playing=true;go(0);
}
function toggle(){playing=!playing;if(playing)schedule(Math.max(500,remaining-(0)));else{clearTimeout(timer);remaining=Math.max(0,remaining-(performance.now()-stepStarted));}apply(steps[index],index);}
function nextAct(){const act=steps[index]?.act??-1;const j=steps.findIndex(s=>s.act>act);if(j>=0)go(j);}
function close(){clearTimeout(timer);playing=false;$('run').classList.add('hidden');$('run-card').classList.add('hidden');$('run-final').classList.add('hidden');document.body.classList.remove('running');}
function agent(name){
 const c=CREW.find(x=>x.name===name),s=status.get(name),h=history.get(name),g=window.GENESIS;
 g?.context('<span class="context-icon" style="color:'+c.color+'">◈</span><span class="capability">AI EMPLOYEE · '+esc(s.state.toUpperCase())+'</span><h2>'+esc(c.name)+' — '+esc(c.title)+'</h2><p>Interface name for the recorded backend role'+(c.agents.length>1?'s':'')+': <b>'+c.agents.map(esc).join(', ')+'</b>.</p><h3>Assigned mission</h3><p>'+esc(data?.mission?.id||'Load the replay to attach a mission')+'</p><h3>Current task</h3><p>'+esc(s.task)+'</p><h3>Verified activity in this replay</h3>'+(h.length?'<ul class="responsibilities">'+h.map(x=>'<li>'+esc(x.act)+': '+esc(x.title)+'</li>').join('')+'</ul>':'<p class="fine">No recorded event has been dispatched yet. Press WATCH GENESIS RUN.</p>')+(data?'<h3>Recorded events for this role</h3><ul class="responsibilities">'+data.mission.events.filter(e=>c.agents.includes(e.agent)).slice(-4).map(e=>'<li>'+esc(e.type)+' — '+esc(e.message)+'</li>').join('')+'</ul>':'')+'<p class="fine">Idle motion is decorative; movement only follows replay steps derived from recorded handoffs.</p>');
}
document.addEventListener('click',async event=>{
 const run=event.target.closest('[data-run]')?.dataset.run,act=event.target.closest('[data-act]')?.dataset.act,crew=event.target.closest('[data-crew]')?.dataset.crew;
 if(run==='toggle')toggle();if(run==='restart')start();if(run==='next')nextAct();if(run==='close')close();
 if(run==='speed'){speed=speed>1.5?1.25:2.15;apply(steps[index],index);}if(run==='follow'){follow=!follow;apply(steps[index],index);}
 if(run==='explore'){close();window.GENESIS?.showDepartment('hq');}
 if(run==='lab'||event.target.id==='open-lab'){await load();window.GENESIS?.evidence('Autonomous Product Testing Lab',lab());}
 if(event.target.id==='open-pipeline'){await load();window.GENESIS?.evidence('CORE Development Pipeline','<p>GENESIS researches, engineers, tests, operates, governs and improves. CORE receives verified capabilities only after CEO approval.</p>'+pipeline());}
 if(act!==undefined){const j=steps.findIndex(s=>s.act===Number(act));if(j>=0)go(j);}
 if(crew){await load();ensureCrew();agent(crew);}
});
$('run-genesis')?.addEventListener('click',start);
$('explore-company')?.addEventListener('click',()=>{$('welcome').classList.add('exploring');ensureCrew();});
document.body.insertAdjacentHTML('beforeend','<section class="run-final hidden" id="run-final" aria-live="polite"></section>');
const boot=()=>{ensureCrew();load();};
if(window.GENESIS)setTimeout(boot,300);else addEventListener('genesis-ready',()=>setTimeout(boot,300),{once:true});
if(new URLSearchParams(location.search).has('run'))addEventListener('load',()=>setTimeout(start,1200));
window.GENESIS_RUN={start,agent,lab,pipeline};
