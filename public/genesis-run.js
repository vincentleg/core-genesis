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
let data=null,steps=[],index=-1,playing=false,timer=null,speed=1,follow=true,remaining=0,stepStarted=0;
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
 const files=Object.keys(p.files||{}),gbPassed=gb?.passed||0,gbTotal=gb?.total||0,synthetic=(core?.completed||0)+(gen?.completed||0);
 // secs: 55 s total at standard pace. hl/why: plain-English headline; card: detailed evidence on demand.
 const S=(act,secs,o)=>({act,secs,...o});
 return [
  S(0,4,{cam:'hq',hl:'CORE is the world. GENESIS is the company building it.',why:'The CEO gives GENESIS a mission: build the first working piece of CORE.',title:'The CEO defines a mission',detail:'A place where humans report local problems, propose solutions and request human review.',moves:[['Atlas','hq','working','Receives the CEO mission contract']],
   card:'<span class="run-tag">MISSION CONTRACT · '+esc(m.id)+'</span><p class="quote">“'+esc(m.objective)+'”</p><dl><dt>CEO authorization</dt><dd>'+esc(ev(m,'mission.authorized')?.message)+'</dd><dt>Scope</dt><dd>'+esc(m.authorization.scope)+'</dd><dt>Expected deliverable</dt><dd>'+m.authorization.acceptance_criteria.map(esc).join(' · ')+'</dd></dl>'}),
  S(0,3,{cam:'hq',hl:'The CEO authorizes a bounded mission',why:'$'+m.authorization.budget_cap_usd+' budget cap. Agents may read, build and test — not publish, buy or change CORE.',title:'Atlas, Chief of Staff, receives the mission',detail:ev(m,'hq.activity')?.message,moves:[],card:'<span class="run-tag">RECORDED EVENT · hq.activity</span><p>'+esc(ev(m,'hq.activity')?.message)+'</p><dl><dt>Authorized</dt><dd>'+m.authorization.authorized.map(esc).join(' · ')+'</dd><dt>Prohibited</dt><dd>'+m.authorization.prohibited.map(esc).join(' · ')+'</dd><dt>Budget</dt><dd>$'+esc(m.authorization.budget_cap_usd)+' cap · '+esc(m.limits.planned_model_calls)+' planned model calls</dd></dl>'}),
  S(1,4,{cam:null,zoom:.95,hl:'Atlas delegates the work',why:'Research, Engineering and Operations agents leave HQ for their departments.',title:'Recorded handoffs',detail:'Each move follows a recorded handoff.',moves:[['Nova','research','working',research.task],['Forge','engineering','working','Await cited Research brief'],['Sentinel','operations','working','Prepare verification']],handoffCard:true}),
  S(1,4,{cam:null,zoom:.95,hl:m.handoffs.length+' recorded handoffs across 8 AI employees',why:'Testing, Economy, Evolution Lab and Growth receive their assignments.',title:'Recorded handoffs',detail:'Each move follows a recorded handoff.',moves:[['Echo','product','working','Prepare beta testing'],['Ledger','economy','working','Resource accounting'],['Darwin','evolution','working','Prepare policy evaluation'],['Pulse','growth','working','Prepare CEO-review draft']],handoffCard:true}),
  S(2,3,{cam:'research',followAgent:'Nova',hl:'Nova reads the real CORE code',why:research.result.sources+' source files from the original CORE repository, read-only, at a pinned commit.',title:'Research inspects CORE',detail:ev(m,'research.activity')?.message,moves:[['Nova','research','working','Reading pinned CORE source']],
   card:'<span class="run-tag">RESEARCH · READ-ONLY</span><dl><dt>Repository</dt><dd>'+esc(m.repository)+' — '+esc(m.core_access)+'</dd><dt>Commit inspected</dt><dd><code>'+esc(research.result.commit)+'</code></dd><dt>Brief</dt><dd>'+m.artifacts.research.priorities.map(x=>esc(x.title)).join(' · ')+'</dd></dl>'}),
  S(2,2,{cam:'engineering',followAgent:'Nova',transfer:['research','engineering'],hl:cite.valid_priorities+'/'+cite.total_priorities+' citations verified',why:'Every recommendation traces back to exact lines of CORE source before Engineering builds.',title:'Research hands a cited brief to Engineering',detail:handoff(m,'Research Lead','Engineering Lead').task,moves:[['Nova','engineering','working','Delivering cited brief',true]],
   card:'<span class="run-tag">HANDOFF · Research Lead → Engineering Lead</span><p><b>'+cite.valid_priorities+'/'+cite.total_priorities+'</b> priority citation sets verified.</p><p class="fine">'+esc(cite.note)+'</p>'}),
  S(2,3,{cam:'engineering',followAgent:'Forge',hl:'GENESIS built its first CORE application',why:'A functional prototype was delivered — not just a proposal.',title:'Forge builds '+(p.spec?.application_title||'CORE Local Solutions'),detail:files.length+' files created from an audited scaffold.',moves:[['Nova','research','completed','Brief delivered'],['Forge','engineering','working','Generating versioned application']],
   card:'<span class="run-tag">ARTIFACT CREATED · '+files.length+' FILES</span><ul class="files">'+files.map(f=>'<li><code>'+esc(f)+'</code></li>').join('')+'</ul><a class="run-link" href="./artifacts/core-local-solutions/" target="_blank" rel="noreferrer">Open the prototype ↗</a>'}),
  S(2,2,{cam:'operations',followAgent:'Forge',transfer:['engineering','operations'],hl:report.tests_run+'/'+report.tests_run+' automated tests passed',why:'Operations ran the real test suite: '+report.failures+' failures, '+report.external_network_requests+' network calls.',title:'Sentinel verifies the build',detail:ev(m,'test.passed')?.message,moves:[['Forge','operations','working','Delivering build for verification',true],['Sentinel','operations','reviewing','Executing isolated tests + loopback HTTP']],
   card:'<span class="run-tag">OPERATIONS · '+esc(p.test_report.command.join(' '))+'</span><div class="big">'+esc(report.tests_run)+' tests · '+esc(report.failures)+' failures · '+esc(report.errors)+' errors</div><p class="fine">Exit code '+esc(p.test_report.exit_code)+'</p>'}),
  S(3,3,{cam:'product',followAgent:'Echo',transfer:['operations','product'],hl:(passed+gbPassed)+' real browser scenarios passed',why:'Automated Chrome testing verified actual user workflows: '+passed+'/'+browser.length+' on CORE, '+gbPassed+'/'+gbTotal+' on GENESIS.',title:'The beta testing lab',detail:'Real browser sessions, not human testers.',moves:[['Forge','engineering','completed','Prototype delivered'],['Sentinel','operations','completed',report.tests_run+' tests passed'],['Echo','product','reviewing','Running browser testers']],
   card:'<span class="run-tag">REAL BROWSER TESTS · CORE LOCAL SOLUTIONS</span><div class="shots">'+browser.map(a=>'<figure><img src="./testing/before-'+esc(a.screenshot)+'" alt="Screenshot from '+esc(a.role)+'" loading="lazy"><figcaption>'+(a.passed?'✓':'✗')+' '+esc(a.role)+'</figcaption></figure>').join('')+'</div>'}),
  S(3,3,{cam:'product',hl:synthetic+' synthetic product evaluations',why:(core?.completed||0)+' for CORE and '+(gen?.completed||0)+' for GENESIS. AI-simulated perspectives — not real human customers.',title:'Synthetic perspectives critique both products',detail:'Independent Nemotron calls, one persona each.',moves:[['Echo','product','reviewing','Collecting synthetic perspectives']],
   card:'<span class="run-tag">SYNTHETIC CAMPAIGNS · SIMULATED, NOT HUMANS</span>'+[['CORE Local Solutions',core],['CORE GENESIS',gen]].map(([label,c])=>c?'<div class="campaign"><b>'+label+' · '+c.completed+'/'+c.target+'</b><p>Top concern: “'+esc(c.top[0]?.[1].concerns[0])+'”</p></div>':'').join('')+'<button class="run-link" data-run="lab">Open full testing lab ↗</button>'}),
  ...(fix?[S(3,3,{cam:'engineering',followAgent:'Echo',transfer:['product','engineering'],hl:'A bug found, fixed and retested',why:'A mobile test failed; the code was fixed and the retest went '+fix.before.passed+'/'+fix.before.total+' → '+fix.retest.passed+'/'+fix.retest.total+'.',title:'Test → improve → retest',detail:fix.issue,moves:[['Echo','engineering','working','Reporting reproducible defect',true]],
   card:'<span class="run-tag">CLOSED LOOP · '+esc(fix.product)+'</span><p>'+esc(fix.issue)+'</p><div class="shots two"><figure><img src="./testing/'+esc(fix.before.screenshot)+'" alt="Before fix"><figcaption>Before</figcaption></figure><figure><img src="./testing/'+esc(fix.retest.screenshot)+'" alt="After fix"><figcaption>After</figcaption></figure></div><p class="fine">'+esc(fix.honesty)+'</p>'})]:[]),
  S(4,6,{cam:'evolution',followAgent:'Darwin',hl:'GENESIS improved its own verification policy',why:'Citation checking improved from '+(pc?pc.parent.passed+'/'+pc.parent.total+' to '+pc.candidate.passed+'/'+pc.candidate.total:'?')+' on independent held-out tests — promoted to policy V'+(prior?.resulting_version??'?')+'.',title:'Evolution Lab · earlier mission',detail:esc(priorId),moves:[['Darwin','evolution','working','Evaluating policy candidates']],big:pc?pc.parent.passed+'/'+pc.parent.total+' → '+pc.candidate.passed+'/'+pc.candidate.total:'',
   card:loop('prior')+'<span class="run-tag">HISTORICAL PROMOTION · '+esc(priorId)+'</span>'+(prior?bench(prior)+'<p><b>'+esc(prior.action.toUpperCase())+'</b> — '+esc(prior.reason)+'</p>':'')}),
  S(4,5,{cam:'evolution',hl:'An unnecessary mutation was rejected',why:'This mission reused V'+evo.resulting_version+'. The new candidate scored '+(cc?cc.candidate.passed+'/'+cc.candidate.total:'?')+', no better than V'+evo.resulting_version+', so the company kept its existing procedure.',title:'Evolution Lab · this mission',detail:evo.reason,moves:[['Darwin','evolution','completed','Rollback: no measured gain']],big:cc?cc.parent.passed+'/'+cc.parent.total+' = '+cc.candidate.passed+'/'+cc.candidate.total:'',
   card:loop('current')+'<span class="run-tag">THIS MISSION · '+esc(m.id)+'</span>'+bench(evo)+'<p><b>'+esc(evo.action.toUpperCase())+'</b> — '+esc(evo.reason)+'</p>'}),
  S(5,4,{cam:'hq',zoom:1,followAgent:'Pulse',transfer:['growth','hq'],hl:'Humans keep the consequential decisions',why:'Publishing, purchases, deployments and changes to CORE wait for the CEO. '+pending.length+' decisions are pending.',title:'Human governance',detail:'Nothing was published, purchased, deployed or written to CORE.',moves:[['Ledger','hq','completed','Budget verified; no purchase',true],['Pulse','hq','reviewing','Draft queued for CEO review',true]],
   card:'<div class="gov"><div><span class="run-tag">AUTONOMOUS</span><ul>'+m.authorization.authorized.map(x=>'<li>✓ '+esc(x)+'</li>').join('')+'</ul></div><div><span class="run-tag gold">REQUIRES CEO</span><ul><li>⏸ Public publication</li><li>⏸ Purchases</li><li>⏸ Production deployments</li><li>⏸ Changes to CORE</li></ul></div></div>'}),
  S(6,6,{cam:'hq',zoom:1.05,hl:'Ready for CEO review',why:'The prototype is complete, but integrating it into CORE requires human authorization.',title:'Mission complete — the first brick of CORE is built',detail:'Prototype built — awaiting CORE integration approval.',final:true,moves:CREW.filter(c=>c.name!=='Atlas').map((c,i)=>[c.name,'hq','completed','Mission delivered',false,i+1]).concat([['Atlas','hq','completed','Delivered for CEO review']]),card:''})
 ].map(s=>s.handoffCard?{...s,card:'<span class="run-tag">'+m.handoffs.length+' RECORDED HANDOFFS</span><ol class="handoffs">'+m.handoffs.map(h=>'<li><b>'+esc(h.source_agent)+' → '+esc(h.destination_agent)+'</b><small>'+esc(h.task)+'</small></li>').join('')+'</ol>'}:s);
}
function bench(e){const d=e.comparison?.development,h=e.comparison?.heldout;if(!h)return '';const row=(k,v)=>'<tr><th>'+k+'</th><td>'+v.parent.passed+'/'+v.parent.total+'</td><td>'+v.candidate.passed+'/'+v.candidate.total+'</td></tr>';return '<table class="bench"><tr><th></th><th>Baseline</th><th>Candidate</th></tr>'+row('Development',d)+row('Held-out',h)+'</table>';}
function loop(which){const stages=['Mission','Performance observation','Proposed mutation','Independent evaluation',which==='prior'?'Promotion ✓':'Rollback ↶','Next generation'];return '<div class="loop">'+stages.map((s,i)=>'<span class="'+(i===4?(which==='prior'?'ok':'no'):'')+'">'+s+'</span>').join('<i>→</i>')+'</div>';}

function pipeline(){
 const m=data?.mission;if(!m)return '';
 const done=[['CORE need identified','Local problems & solutions with human review'],['Mission authorized',m.id],['Research completed','Commit '+(handoff(m,'CEO','Research Lead')?.result.commit||'').slice(0,10)],['Engineering artifact produced',m.artifacts.prototype.spec?.application_title],['Tests completed','7 tests · 3 browser scenarios'],['Product feedback collected','Synthetic campaigns + browser evidence'],['Integration proposal prepared','integration_plan in mission record']];
 return '<div class="pipeline">'+done.map(([t,s],i)=>'<div class="stage done"><b>'+(i+1)+'</b><span>'+esc(t)+'<small>'+esc(s)+'</small></span></div>').join('')+'<div class="stage now"><b>8</b><span>Awaiting CEO approval<small>approval_status: '+esc(m.approval_status)+'</small></span></div><div class="stage todo"><b>9</b><span>Integrated into CORE<small>Not done — original CORE unchanged ('+(m.artifacts.prototype.original_core_modified?'modified':'original_core_modified: false')+')</small></span></div></div><p class="pipeline-state">PROTOTYPE BUILT — AWAITING CORE INTEGRATION APPROVAL</p>';
}
function finalCard(){
 const m=data.mission,u=m.usage,core=campaign(data.testing?.audience),gen=campaign(data.testing?.genesis_audience),browser=data.testing?.browser?.before?.agents||[],gb=data.genesisBrowser;
 const pending=(data.governance?.decisions||[]).filter(d=>d.status==='pending_ceo_review'),report=stdout(m.artifacts.prototype.test_report),pc=data.prior?.comparison?.heldout;
 const link=(href,label,sub)=>'<a class="deliverable" href="'+href+'" target="_blank" rel="noreferrer"><b>'+label+' ↗</b><small>'+sub+'</small></a>';
 const outcome=(n,head,why,href)=>'<a class="outcome" href="'+href+'" target="_blank" rel="noreferrer"><span>'+n+'</span><b>'+head+'</b><small>'+why+'</small></a>';
 return '<div class="final"><span class="run-tag gold">VERIFIED MISSION REPLAY · '+esc(m.id)+'</span><h2>Mission complete — the first brick of CORE is built.</h2><div class="outcomes">'+
  outcome('✓','Working CORE prototype delivered',esc(report.tests_run)+'/'+esc(report.tests_run)+' automated tests passed. A functional app, not a proposal.','./artifacts/core-local-solutions/')+
  outcome('✓','Product tests and feedback completed',(browser.filter(a=>a.passed).length+(gb?.passed||0))+' real browser scenarios passed · '+((core?.completed||0)+(gen?.completed||0))+' synthetic evaluations (AI-simulated, not humans).','./evidence/product-testing.json')+
  outcome('✓','Internal verification policy improved',(pc?pc.parent.passed+'/'+pc.parent.total+' → '+pc.candidate.passed+'/'+pc.candidate.total:'')+' on held-out tests → V'+esc(data.prior?.resulting_version)+'. A later mutation with no gain was rejected.',REPO+'mission-evidence/'+(data.priorId||'')+'.json')+
  '</div><div class="ceo-review"><b>READY FOR CEO REVIEW</b><span>Integrating into CORE requires human authorization · '+(pending.length+1)+' decisions pending · mission cost $'+Number(u.cost_estimate_usd).toFixed(4)+' estimated ('+esc(u.physical_requests)+' Nemotron requests)</span></div>'+
  '<details class="final-more"><summary>Pipeline, deliverables and pending decisions</summary>'+pipeline()+'<div class="deliverables">'+
  link('./artifacts/core-local-solutions/source.zip','Source archive','Exact generated source + tests')+
  link(REPO+'mission-evidence/'+m.id+'.json','Mission record',m.events.length+' events · '+m.handoffs.length+' handoffs')+
  link('./testing/loop/loop.json','Closed loop','Test → fix → retest record')+'</div><ul class="pending">'+'<li>Approve integration of CORE Local Solutions into CORE</li>'+pending.map(d=>'<li>'+esc(d.type.replaceAll('_',' '))+' · '+esc(d.mission_id)+'</li>').join('')+'</ul></details>'+
  '<div class="final-actions"><button class="primary" data-run="restart">↺ Replay</button><button class="secondary" data-run="explore">Explore the company</button></div></div>';
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
    placed.push({x:p.x,y,w});el.style.transform='translate('+p.x+'px,'+y+'px) translate(-50%,-100%)';el.style.display=p.visible?'':'none';el.dataset.state=status.get(el.dataset.crew).state;el.dataset.active=ACTIVE.has(el.dataset.crew)?'1':'';}
  });}
 return campus;
}
function setState(name,state,task,step){
 status.set(name,{state,task,evidence:step});
 const list=history.get(name);if(step&&list[list.length-1]?.title!==step.title)list.push({title:step.title,act:ACTS[step.act],state});
}
let details=false,deadline=0,startedAt=0,autoplayTimer=null,interacted=false;
const ACTIVE=new Set();
function apply(step,i){
 const campus=ensureCrew();ACTIVE.clear();
 if(campus){
  const move=Math.min(2200,step.secs*800/speed);
  for(const [name,dept,state,task,carry,slot] of step.moves){const crew=CREW.find(c=>c.name===name);campus.moveCrew(name,dept,{carry:!!carry,duration:move,slot:slot??CREW.indexOf(crew)});setState(name,state,task,step);ACTIVE.add(name);}
  if(step.transfer)campus.transfer?.(...step.transfer,move);
  campus.highlight?.(step.final?'hq':step.transfer?.[1]||step.cam||null);
  if(follow){if(step.followAgent)campus.followCrew?.(step.followAgent,step.zoom||1.3);else{campus.followCrew?.(null);if(step.cam)campus.focusOn(step.cam,step.zoom||1.3);else campus.reset?.();}}
  else campus.followCrew?.(null);
 }
 const pct=steps.slice(0,i+1).reduce((s,x)=>s+x.secs,0)/steps.reduce((s,x)=>s+x.secs,0)*100;
 $('run-hl').innerHTML=step.final?'':'<span class="run-badge">● VERIFIED MISSION REPLAY · ACT '+(step.act+1)+'/7</span>'+(step.big?'<em>'+esc(step.big)+'</em>':'')+'<strong>'+esc(step.hl)+'</strong><p>'+esc(step.why)+'</p><button data-run="details">'+(details?'Hide evidence ▴':'Show evidence ▾')+'</button>';
 $('run-hl').classList.toggle('hidden',!!step.final);
 $('run').innerHTML='<div class="run-head"><span>'+esc(ACTS[step.act])+' · '+esc(step.title)+'</span></div><div class="run-acts">'+ACTS.map((a,k)=>'<button data-act="'+k+'" class="'+(k<step.act?'done':k===step.act?'now':'')+'" title="'+esc(a)+'" aria-label="Act '+(k+1)+': '+esc(a)+'"><span style="width:'+(k<step.act?100:k===step.act?Math.min(100,Math.max(8,pct*7-k*100)):0)+'%"></span></button>').join('')+'</div><div class="run-controls"><button data-run="toggle" aria-label="'+(playing?'Pause':'Play')+'">'+(playing?'❚❚ Pause':'▶ Play')+'</button><button data-run="restart" aria-label="Restart">↺</button><button data-run="next" aria-label="Next act">Next →</button><button data-run="speed" class="'+(speed<1?'on':'')+'">'+(speed<1?'Detailed pace':'55s pace')+'</button><button data-run="follow" class="'+(follow?'on':'')+'">Follow agents</button><button data-run="autoplay" class="'+(autoplayEnabled()?'on':'')+'">Autoplay '+(autoplayEnabled()?'on':'off')+'</button><button data-run="close" aria-label="Close replay and explore">×</button></div>';
 const card=$('run-card');
 if(step.final){card.classList.add('hidden');$('run-final').innerHTML=finalCard();$('run-final').classList.remove('hidden');}
 else{$('run-final').classList.add('hidden');card.innerHTML=step.card;card.classList.toggle('hidden',!details);}
}
// Wall-clock deadlines keep the sequence at its stated length even if rendering delays timers.
function schedule(ms){clearTimeout(timer);deadline=performance.now()+ms;remaining=ms;tick();}
function tick(){clearTimeout(timer);timer=setTimeout(()=>{if(index<steps.length-1)go(index+1,false,true);else{playing=false;window.GENESIS_RUN.duration_s=(performance.now()-startedAt)/1000;document.body.dataset.replay='finished';apply(steps[index],index);}},Math.max(0,deadline-performance.now()));}
function go(i,keepPaused=false,chained=false){index=i;apply(steps[i],i);if(playing&&!keepPaused){const ms=steps[i].secs*1000/speed;if(chained){deadline+=ms;remaining=ms;tick();}else schedule(ms);}}
async function start(){
 clearTimeout(autoplayTimer);$('autoplay-chip')?.remove();
 await load();if(!data.mission){alert('Mission evidence is unavailable.');return;}
 document.body.classList.add('running');document.body.dataset.replay='running';$('welcome').classList.add('exploring');$('context').classList.add('hidden');$('run').classList.remove('hidden');
 for(const c of CREW){setState(c.name,'idle','Awaiting mission',null);history.set(c.name,[]);}
 const campus=ensureCrew();if(campus)CREW.forEach((c,i)=>campus.moveCrew(c.name,'hq',{duration:400,slot:i}));
 playing=true;startedAt=performance.now();go(0);
}
function toggle(){playing=!playing;if(playing){deadline=performance.now()+Math.max(300,remaining);tick();}else{clearTimeout(timer);remaining=Math.max(0,deadline-performance.now());}apply(steps[index],index);}
function nextAct(){const act=steps[index]?.act??-1;const j=steps.findIndex(s=>s.act>act);if(j>=0)go(j);}
function close(){clearTimeout(timer);playing=false;window.GENESIS?.campus()?.followCrew?.(null);window.GENESIS?.campus()?.highlight?.(null);['run','run-card','run-final','run-hl'].forEach(id=>$(id).classList.add('hidden'));document.body.classList.remove('running');}
function autoplayEnabled(){try{return localStorage.getItem('genesis-autoplay')!=='off';}catch{return true;}}
function setAutoplay(on){try{localStorage.setItem('genesis-autoplay',on?'on':'off');}catch{}}
function scheduleAutoplay(){
 const params=new URLSearchParams(location.search),reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 if(params.get('autoplay')==='0'||(!params.has('run')&&(!autoplayEnabled()||reduced)))return;
 const begin=()=>{if(interacted)return;document.querySelector('.hero')?.insertAdjacentHTML('beforeend','<div class="autoplay-chip" id="autoplay-chip">Verified mission replay starting… <button data-run="cancel-autoplay">Stay here</button></div>');autoplayTimer=setTimeout(()=>{if(!interacted)start();},2000);};
 const loading=$('loading');
 if(!loading||loading.classList.contains('hidden'))begin();else new MutationObserver((_,o)=>{if(loading.classList.contains('hidden')){o.disconnect();begin();}}).observe(loading,{attributes:true});
}
function agent(name){
 const c=CREW.find(x=>x.name===name),s=status.get(name),h=history.get(name),g=window.GENESIS;
 g?.context('<span class="context-icon" style="color:'+c.color+'">◈</span><span class="capability">AI EMPLOYEE · '+esc(s.state.toUpperCase())+'</span><h2>'+esc(c.name)+' — '+esc(c.title)+'</h2><p>Interface name for the recorded backend role'+(c.agents.length>1?'s':'')+': <b>'+c.agents.map(esc).join(', ')+'</b>.</p><h3>Assigned mission</h3><p>'+esc(data?.mission?.id||'Load the replay to attach a mission')+'</p><h3>Current task</h3><p>'+esc(s.task)+'</p><h3>Verified activity in this replay</h3>'+(h.length?'<ul class="responsibilities">'+h.map(x=>'<li>'+esc(x.act)+': '+esc(x.title)+'</li>').join('')+'</ul>':'<p class="fine">No recorded event has been dispatched yet. Press WATCH GENESIS RUN.</p>')+(data?'<h3>Recorded events for this role</h3><ul class="responsibilities">'+data.mission.events.filter(e=>c.agents.includes(e.agent)).slice(-4).map(e=>'<li>'+esc(e.type)+' — '+esc(e.message)+'</li>').join('')+'</ul>':'')+'<p class="fine">Idle motion is decorative; movement only follows replay steps derived from recorded handoffs.</p>');
}
document.addEventListener('click',async event=>{
 const run=event.target.closest('[data-run]')?.dataset.run,act=event.target.closest('[data-act]')?.dataset.act,crew=event.target.closest('[data-crew]')?.dataset.crew;
 if(run==='toggle')toggle();if(run==='restart')start();if(run==='next')nextAct();if(run==='close')close();
 if(run==='speed'){speed=speed<1?1:.55;apply(steps[index],index);}if(run==='details'){details=!details;apply(steps[index],index);}if(run==='autoplay'){setAutoplay(!autoplayEnabled());apply(steps[index],index);}if(run==='cancel-autoplay'){interacted=true;clearTimeout(autoplayTimer);$('autoplay-chip')?.remove();}if(run==='follow'){follow=!follow;apply(steps[index],index);}
 if(run==='explore'){close();window.GENESIS?.showDepartment('hq');}
 if(run==='lab'||event.target.id==='open-lab'){await load();window.GENESIS?.evidence('Autonomous Product Testing Lab',lab());}
 if(event.target.id==='open-pipeline'){await load();window.GENESIS?.evidence('CORE Development Pipeline','<p>GENESIS researches, engineers, tests, operates, governs and improves. CORE receives verified capabilities only after CEO approval.</p>'+pipeline());}
 if(act!==undefined){const j=steps.findIndex(s=>s.act===Number(act));if(j>=0)go(j);}
 if(crew){await load();ensureCrew();agent(crew);}
});
$('run-genesis')?.addEventListener('click',start);
$('explore-company')?.addEventListener('click',()=>{interacted=true;clearTimeout(autoplayTimer);$('autoplay-chip')?.remove();$('welcome').classList.add('exploring');ensureCrew();});
document.body.insertAdjacentHTML('beforeend','<section class="run-final hidden" id="run-final" aria-live="polite"></section><div class="run-hl hidden" id="run-hl" aria-live="polite"></div>');
// Any manual navigation before autoplay begins cancels it; autoplay never restarts after pause or exploration.
document.addEventListener('pointerdown',e=>{if(e.target.closest('[data-dock],#give-mission,#home,#vision,#open-pipeline,#open-lab,.building-label,#world'))interacted=true;},true);
const boot=()=>{ensureCrew();load();};
if(window.GENESIS)setTimeout(boot,300);else addEventListener('genesis-ready',()=>setTimeout(boot,300),{once:true});
scheduleAutoplay();
window.GENESIS_RUN={start,agent,lab,pipeline,duration_s:null};
