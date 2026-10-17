import * as T from './vendor/three.module.js';

export const DEPARTMENTS=[
 {id:'hq',name:'Genesis HQ',short:'HQ',icon:'✳',color:'#2caaa0',x:0,z:0,status:'FUNCTIONAL · SCOPED',role:'Architect',description:'The coordination heart of a growing AI organization.'},
 {id:'engineering',name:'Engineering',short:'Engineering',icon:'⌘',color:'#e89276',x:-9,z:0,status:'FUNCTIONAL · SANDBOXED',role:'Executor',description:'Bounded repair procedures, reproducible tests, and measurable technical outcomes.'},
 {id:'research',name:'Research',short:'Research',icon:'✧',color:'#a297ce',x:4,z:-9,status:'EXPERIMENTAL · INTERNAL EVIDENCE',role:'Observer',description:'Turning observations into traceable hypotheses and tested knowledge.'},
 {id:'operations',name:'Operations',short:'Operations',icon:'◈',color:'#62a9cb',x:9,z:2,status:'FUNCTIONAL · INCIDENT SIMULATOR',role:'Executor',description:'Diagnose incidents, coordinate response, and verify service contracts.'},
 {id:'economy',name:'Economy',short:'Economy',icon:'◇',color:'#d3b769',x:5,z:10,status:'PROTOTYPE · PLANNING SIMULATION',role:'Economic planner',description:'Accountable resource planning. Recommendations, never autonomous purchases.'},
 {id:'evolution',name:'Evolution Lab',short:'Evolution',icon:'⌬',color:'#9b88c9',x:-5,z:9,status:'FUNCTIONAL · VERSION N+1',role:'Scientist',description:'Where the organization experiments with better versions of itself.'},
 {id:'core',name:'CORE World',short:'CORE World',icon:'◎',color:'#79b78f',x:-7,z:-9,status:'FUTURE VISION',role:'Future connection',description:'A gateway to Creation Of Reborn Earth. A shared future for human and artificial intelligence.'}
];

export function createCampus(container,{onDepartment,onAgent,onReady,onError}={}){
 let renderer;
 try{renderer=new T.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance'});}catch(error){onError?.(error);return null;}
 renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));renderer.setSize(innerWidth,innerHeight);
 renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
 renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;
 container.appendChild(renderer.domElement);
 const scene=new T.Scene();scene.background=new T.Color('#e9f3ef');scene.fog=new T.Fog('#e9f3ef',65,135);
 const camera=new T.OrthographicCamera(-25,25,20,-20,.1,220);
 let azimuth=.76,elevation=.72,zoom=1,targetZoom=1;
 const focus=new T.Vector3(-1,0,0),desiredFocus=focus.clone();
 const ambient=new T.HemisphereLight('#f8ffff','#b3c7a0',2.8);scene.add(ambient);
 const sun=new T.DirectionalLight('#fff1d9',4);sun.position.set(-20,36,16);sun.castShadow=true;
 sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-30,right:30,top:30,bottom:-30,near:.5,far:100});sun.shadow.bias=-.0003;sun.shadow.normalBias=.035;scene.add(sun);
 const fill=new T.DirectionalLight('#b7e8f4',1.2);fill.position.set(20,12,-15);scene.add(fill);
 const materials=new Map();
 function mat(color,options={}){
  const key=color+JSON.stringify(options);
  if(!materials.has(key))materials.set(key,new T.MeshStandardMaterial({color,roughness:.65,metalness:.04,...options}));
  return materials.get(key);
 }
 const pearl=mat('#f9faf2'),cream=mat('#efece1'),glass=mat('#b6ddd8',{roughness:.12,metalness:.2,transparent:true,opacity:.65});
 const gold=mat('#dbc288',{metalness:.55,roughness:.32}),trunk=mat('#b9b19b');
 function mesh(geometry,material,x=0,y=0,z=0,parent=scene){
  const object=new T.Mesh(geometry,material);object.position.set(x,y,z);object.castShadow=true;object.receiveShadow=true;parent.add(object);return object;
 }
 function box(w,h,d,m,x,y,z,p=scene){return mesh(new T.BoxGeometry(w,h,d),m,x,y,z,p);}
 function cylinder(r,h,m,x,y,z,p=scene,top=r){return mesh(new T.CylinderGeometry(top,r,h,48),m,x,y,z,p);}
 function sphere(r,m,x,y,z,p=scene){return mesh(new T.SphereGeometry(r,20,16),m,x,y,z,p);}
 function ring(r,t,m,x,y,z,p=scene){const o=mesh(new T.TorusGeometry(r,t,10,72),m,x,y,z,p);o.rotation.x=Math.PI/2;return o;}
 function line(points,color,opacity=.5,p=scene){
  const o=new T.Line(new T.BufferGeometry().setFromPoints(points),new T.LineBasicMaterial({color,transparent:true,opacity}));p.add(o);return o;
 }
 // Low-poly islands, planted roofs, gardens and light are procedural ambience.
 const water=mesh(new T.PlaneGeometry(280,280),mat('#c5e3dc',{roughness:.35,metalness:.1}),0,-1.05,0);water.rotation.x=-Math.PI/2;water.receiveShadow=true;water.castShadow=false;
 cylinder(20.5,1.1,mat('#d6d9c5'),0,-.45,0,scene,20.2);
 cylinder(20.15,.15,mat('#e9ecd9'),0,.12,0);
 ring(20.2,.08,pearl,0,.19,0);
 const lawn=mat('#b8d3a8'),darkGreen=mat('#78b18a'),brightGreen=mat('#a0c697');
 const islandTop=cylinder(18.9,.035,lawn,0,.22,0);islandTop.castShadow=false;
 cylinder(4.1,.09,mat('#e8eddf'),0,.26,0);
 ring(4.45,.32,mat('#f4f3e7'),0,.28,0);
 // Radial walking avenues with fine turquoise inlays.
 for(const d of DEPARTMENTS.slice(1)){
  const length=Math.hypot(d.x,d.z),mid=new T.Vector3(d.x/2,.3,d.z/2);
  const road=box(1.5,.035,length,mat('#e9efdf'),mid.x,mid.y,mid.z);
  road.rotation.y=Math.atan2(d.x,d.z);
  const trace=box(.045,.04,length,mat('#95cfc1'),mid.x,.33,mid.z);trace.rotation.y=road.rotation.y;
 }
 ring(12.8,.7,mat('#edf0e0'),0,.27,0);
 ring(12.8,.035,mat('#b5d3be'),0,.33,0);
 const buildings=new Map(),hitObjects=[],labels=[];
 function makeLabel(d){
  const button=document.createElement('button');button.className='building-label';button.dataset.department=d.id;button.style.setProperty('--color',d.color);
  button.innerHTML='<i></i>'+d.name+'<small>'+({'hq':'COORDINATE','engineering':'BUILD & VERIFY','research':'INVESTIGATE','operations':'RESTORE','economy':'PLAN RESOURCES','evolution':'EVOLVE & VALIDATE','core':'THE NEXT HORIZON'}[d.id])+'</small>';
  button.addEventListener('pointerdown',event=>event.stopPropagation());button.onclick=()=>onDepartment?.(d.id);
  document.getElementById('labels').appendChild(button);labels.push({element:button,position:new T.Vector3(d.x,0,d.z),height:d.id==='hq'?6:4.1});
 }
 function foundation(d,r=2.8){
  const group=new T.Group();group.position.set(d.x,.32,d.z);scene.add(group);
  cylinder(r,.22,cream,0,.11,0,group);
  ring(r+.18,.07,pearl,0,.1,0,group);
  const accent=mat(d.color);
  cylinder(r-.2,.06,pearl,0,.25,0,group);
  buildings.set(d.id,{group,accent,department:d});makeLabel(d);
  const hit=cylinder(r,5,new T.MeshBasicMaterial({visible:false}),0,2.5,0,group);hit.userData.department=d.id;hitObjects.push(hit);
  return {group,accent};
 }
 for(const d of DEPARTMENTS){
  const {group:g,accent}=foundation(d,d.id==='hq'?3.15:2.55);
  if(d.id==='hq'){
   cylinder(2.1,2.5,pearl,0,1.5,0,g);
   cylinder(2.12,.18,accent,0,1.1,0,g);
   cylinder(1.9,1.9,glass,0,3.55,0,g);
   for(let i=0;i<12;i++){const a=i*Math.PI/6;box(.11,2,.11,pearl,1.92*Math.cos(a),3.55,1.92*Math.sin(a),g);}
   cylinder(2.2,.18,pearl,0,4.6,0,g);
   const dome=mesh(new T.SphereGeometry(1.87,40,20,0,Math.PI*2,0,Math.PI/2),glass,0,4.66,0,g);
   ring(2.52,.075,gold,0,5.2,0,g);
   ring(1.25,.04,accent,0,5.95,0,g);
   sphere(.16,gold,0,6,0,g);
   for(let i=0;i<4;i++){const a=i*Math.PI/2;const wing=box(1.6,1.2,2.4,pearl,Math.cos(a)*2,1,Math.sin(a)*2,g);wing.rotation.y=-a;box(.9,.12,.9,brightGreen,Math.cos(a)*2,1.66,Math.sin(a)*2,g);}
  }else if(d.id==='engineering'){
   box(3.8,1.9,3.1,pearl,0,1.3,0,g);box(4.15,.18,3.4,accent,0,2.35,0,g);
   box(3.85,.1,3,brightGreen,0,2.49,0,g);
   box(3.9,.8,.08,glass,0,1.5,1.57,g);
   for(let i=-1;i<=1;i++)box(.12,1.8,.12,cream,i*1.2,1.3,1.63,g);
   const shed=box(2.2,1.2,1.8,glass,.3,3.1,0,g);
   box(2.5,.12,2.1,pearl,.3,3.75,0,g);
   for(let i=0;i<3;i++){const panel=box(.8,.06,.85,mat('#668f91'),-1+i*.9,2.65,-.9,g);panel.rotation.x=.2;}
  }else if(d.id==='research'){
   for(let i=0;i<3;i++){
    const a=i*Math.PI*2/3,r=1.05,x=Math.cos(a)*r,z=Math.sin(a)*r,h=2.4+i*.45;
    cylinder(.95,h,glass,x,h/2+.4,z,g);cylinder(1.04,.16,pearl,x,h+.5,z,g);
    cylinder(.97,.13,accent,x,1.1,z,g);
    mesh(new T.SphereGeometry(.94,24,12,0,Math.PI*2,0,Math.PI/2),pearl,x,h+.6,z,g);
   }
   ring(2.2,.07,accent,0,3.5,0,g);
  }else if(d.id==='operations'){
   box(3.6,1.1,3.2,pearl,0,.95,0,g);box(3.65,.7,3.23,glass,0,1.75,0,g);box(3.9,.16,3.45,accent,0,2.2,0,g);
   cylinder(1.25,1.6,glass,.1,3,0,g);cylinder(1.5,.18,pearl,.1,3.9,0,g);
   ring(1.65,.065,accent,.1,4.08,0,g);
   box(2,.2,1.8,brightGreen,-.55,2.4,.2,g);
   for(let i=0;i<3;i++)sphere(.07,mat('#c5efbd',{emissive:'#84bc8d',emissiveIntensity:.3}),-.6+i*.5,2.02,1.66,g);
  }else if(d.id==='economy'){
   cylinder(1.8,2.1,pearl,0,1.4,0,g);
   cylinder(1.82,.6,glass,0,1.55,0,g);
   for(let i=0;i<10;i++){const a=i*Math.PI/5;const col=cylinder(.1,2,pearl,Math.cos(a)*1.8,1.45,Math.sin(a)*1.8,g);}
   cylinder(2.15,.2,cream,0,2.55,0,g);cylinder(1.6,.3,accent,0,2.8,0,g);
   ring(1.5,.09,gold,0,3.4,0,g);
   const crystal=mesh(new T.OctahedronGeometry(.6,0),gold,0,3.7,0,g);crystal.userData.decorativeSpin=true;
  }else if(d.id==='evolution'){
   cylinder(1.5,2.5,glass,0,1.7,0,g);
   for(let i=0;i<4;i++){cylinder(2.05-i*.1,.16,pearl,0,.6+i*.85,0,g);ring(2.05-i*.1,.06,i%2?accent:gold,0,.7+i*.85,0,g);}
   for(let i=0;i<20;i++){const a=i*.6,y=.7+i*.13;sphere(.075,i%2?accent:gold,Math.cos(a)*.65,y,Math.sin(a)*.65,g);}
   const roof=cylinder(1.3,.13,accent,0,3.6,0,g);
   ring(2.4,.055,accent,0,4.1,0,g);
  }else{
   cylinder(1.9,.35,pearl,0,.6,0,g);
   const portal=ring(1.7,.15,pearl,0,2.7,0,g);portal.rotation.x=0;portal.rotation.y=.2;
   const glowRing=ring(1.5,.045,accent,0,2.7,0,g);glowRing.rotation.x=0;
   sphere(1.1,mat('#a8d5c2',{transparent:true,opacity:.32,roughness:.2}),0,2.7,0,g);
   for(let i=0;i<3;i++){const orbit=ring(1.12,.018,accent,0,2.7,0,g);orbit.rotation.set(Math.PI/2+i*.6,.3*i,0);}
   for(let i=0;i<9;i++){const a=i*2.4;sphere(.22,brightGreen,Math.cos(a)*.85,2.6+Math.sin(a*.7)*.6,Math.sin(a)*.8,g);}
  }
 }
 // Reproducible planted landscape, not model-generated evidence.
 let seed=7331;const rand=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 const planted=[];
 function tree(x,z,scale=1){planted.push({x,z,scale,dark:rand()>.4});}
 for(let i=0;i<125;i++){
  const a=rand()*Math.PI*2,r=5.3+rand()*13.5,x=Math.cos(a)*r,z=Math.sin(a)*r;
  if(DEPARTMENTS.some(d=>Math.hypot(x-d.x,z-d.z)<3.3))continue;
  if(DEPARTMENTS.slice(1).some(d=>{const dot=(x*d.x+z*d.z)/(d.x*d.x+d.z*d.z);return dot>0&&dot<1&&Math.hypot(x-dot*d.x,z-dot*d.z)<1;}))continue;
  tree(x,z,.65+rand()*.55);
 }
 for(let i=0;i<18;i++){
  const a=i*Math.PI*2/18;tree(Math.cos(a)*18.4,Math.sin(a)*18.4,.6+(i%3)*.15);
  const lamp=cylinder(.035,.85,pearl,Math.cos(a)*13.8,.75,Math.sin(a)*13.8);
  sphere(.09,mat('#f8e9b4',{emissive:'#fff3bb',emissiveIntensity:.2}),Math.cos(a)*13.8,1.23,Math.sin(a)*13.8);
 }
 // Water garden and stepping stones.
 const pond=cylinder(2.2,.035,mat('#8fc9c0',{roughness:.2,metalness:.1}),11,.3,-7);pond.scale.set(1.4,1,.8);
 for(let i=0;i<6;i++)cylinder(.23,.05,cream,9.7+i*.55,.36,-7+Math.sin(i)*.25);
 for(let i=0;i<5;i++)sphere(.22,brightGreen,11+Math.cos(i*1.8)*1.8,.38,-7+Math.sin(i*1.8)*1.1).scale.y=.15;
 for(let i=0;i<4;i++){const g=new T.Group();g.position.set(-12+i*.7,.3,9.5);box(.4,.2,2.2,cream,0,.1,0,g);box(.3,.1,2,brightGreen,0,.25,0,g);scene.add(g);}
 // Small observatory islets and a gently raised footbridge.
 cylinder(3,.7,mat('#d4d9c6'),-21,-.6,-9);cylinder(2.8,.07,lawn,-21,-.18,-9);
 tree(-21,-9,.8);tree(-22,-9.6,.6);
 const bridge=box(5.7,.15,1,cream,-18.3,.15,-8);bridge.rotation.y=-.3;
 // Instanced vegetation keeps the miniature world inexpensive to draw.
 const transform=new T.Object3D();
 const trunks=new T.InstancedMesh(new T.CylinderGeometry(.09,.09,.9,8),trunk,planted.length);
 planted.forEach((p,index)=>{transform.position.set(p.x,.3+.5*p.scale,p.z);transform.scale.setScalar(p.scale);transform.updateMatrix();trunks.setMatrixAt(index,transform.matrix);});
 trunks.castShadow=true;trunks.receiveShadow=true;scene.add(trunks);
 for(const dark of [false,true]){
  const plants=planted.filter(p=>p.dark===dark),leaves=new T.InstancedMesh(new T.SphereGeometry(1,12,10),dark?darkGreen:brightGreen,plants.length*2);
  plants.forEach((p,index)=>{
   transform.position.set(p.x,.3+1.18*p.scale,p.z);transform.scale.set(.55*p.scale,.55*1.35*p.scale,.55*p.scale);transform.updateMatrix();leaves.setMatrixAt(index*2,transform.matrix);
   transform.position.set(p.x+.25*p.scale,.3+1.3*p.scale,p.z+.12*p.scale);transform.scale.setScalar(.39*p.scale);transform.updateMatrix();leaves.setMatrixAt(index*2+1,transform.matrix);
  });leaves.castShadow=true;leaves.receiveShadow=true;scene.add(leaves);
 }
 for(let i=0;i<3;i++){const b=box(1,.06,2.7,mat('#8aaab1'),-14+i*1.1,.39,-3.9);b.rotation.x=.15;}
 const actors=new Map(),actorHits=[],organization=new T.Group(),workflowGroup=new T.Group();scene.add(organization,workflowGroup);
 const roleHomes={Architect:'hq',Executor:'operations',Observer:'research',Scientist:'evolution'};
 function actor(role,department,index=0,worker=false){
  const d=DEPARTMENTS.find(item=>item.id===department),g=new T.Group();
  const shell=mat(worker?'#f7f8e8':'#f8f9f1'),color=mat(d.color,{roughness:.3,metalness:.15});
  sphere(.22,shell,0,.45,0,g).scale.set(1,1.3,1);
  sphere(.17,color,0,.87,0,g);
  const visor=box(.23,.08,.07,mat('#527b7d'),0,.88,.14,g);
  ring(.3,.035,color,0,.18,0,g);
  const x=d.x+2.3+index*.65,z=d.z+1.3;
  g.position.set(x,.33,z);g.userData={role,worker};scene.add(g);
  const hit=sphere(.6,new T.MeshBasicMaterial({visible:false}),0,.65,0,g);hit.userData.actor=role;actorHits.push(hit);
  const entry={group:g,role,worker,home:department,origin:g.position.clone(),destination:g.position.clone(),moving:false,started:0,lastAction:null};
  actors.set(role,entry);return entry;
 }
 Object.entries(roleHomes).forEach(([role,department])=>actor(role,department));
 let workerActors=[],lastTeam='',generationPulse=0,lastSelection=null;
 function clearGroup(group){while(group.children.length){const object=group.children[0];group.remove(object);object.traverse(child=>{child.geometry?.dispose();});}}
 function configure(team,nodeId,promoted=false){
  const hash=JSON.stringify(team);if(hash===lastTeam)return;lastTeam=hash;
  clearGroup(organization);clearGroup(workflowGroup);
  for(const item of workerActors){scene.remove(item.group);actors.delete(item.role);const index=actorHits.findIndex(hit=>hit.userData.actor===item.role);if(index>=0)actorHits.splice(index,1);}
  workerActors=[];
  (team.agents||[]).forEach((agent,index)=>{
   const entry=actor(agent.id,'engineering',index,true);entry.specialty=agent.specialty;entry.tools=agent.tools;entry.instructions=agent.instructions;entry.lastAction='Configured worker in '+nodeId;workerActors.push(entry);
   const x=-5+Math.cos(index*1.7)*3.1,z=9+Math.sin(index*1.7)*3.1;
   cylinder(.42,.18,pearl,x,.44,z,organization);ring(.43,.04,mat('#b7a2d4'),x,.57,z,organization);
   sphere(.2,mat(DEPARTMENTS.find(d=>d.id==='engineering').color),x,.85,z,organization);
  });
  const tools=[...new Set((team.agents||[]).flatMap(a=>a.tools))];
  const destinations={read_logs:'operations',inspect_config:'engineering',inspect_contract:'research',recall_memory:'research'};
  tools.forEach((tool,index)=>{
   const to=DEPARTMENTS.find(d=>d.id===destinations[tool]),from=DEPARTMENTS.find(d=>d.id==='evolution');
   if(!to)return;
   const curve=new T.QuadraticBezierCurve3(new T.Vector3(from.x,.5,from.z),new T.Vector3((from.x+to.x)/2,3+index*.3,(from.z+to.z)/2),new T.Vector3(to.x,.5,to.z));
   line(curve.getPoints(40),promoted?'#d6ac4e':'#8bbdb0',.55,workflowGroup);
   cylinder(.16,.3,mat('#e1c885'),to.x+2.1+index*.35,.55,to.z-1.8,organization);
  });
  const actionDept={...destinations,apply_rules:'engineering',review:'evolution',commit:'hq'};
  const workflow=(team.workflow||[]).map(step=>actionDept[step.action]).filter(Boolean);
  for(let i=1;i<workflow.length;i++){
   const a=DEPARTMENTS.find(d=>d.id===workflow[i-1]),b=DEPARTMENTS.find(d=>d.id===workflow[i]);
   if(a.id===b.id)continue;
   line([new T.Vector3(a.x,.4,a.z),new T.Vector3(b.x,.4,b.z)],'#9ea5c7',.6,workflowGroup);
  }
  if(promoted){generationPulse=performance.now();const lab=buildings.get('evolution');lab.group.scale.setScalar(1.04);}
 }
 let messenger=null,activeDepartment=null;
 const messageOrb=sphere(.13,mat('#e9b56d',{emissive:'#e9b56d',emissiveIntensity:.5}),0,-10,0);
 const promoRing=ring(3.3,.075,gold,0,-10,0);promoRing.visible=false;
 function showEvent(event,department){
  activeDepartment=department;
  const now=performance.now(),target=DEPARTMENTS.find(d=>d.id===department)||DEPARTMENTS[0];
  const roles=[...actors.keys()].filter(role=>!actors.get(role).worker&&event.role?.includes(role));
  for(const role of roles){
   const a=actors.get(role);a.origin.copy(a.group.position);a.destination.set(target.x+2.4,.33,target.z+1.4);a.started=now;a.moving=true;a.lastAction=event;
  }
  const origin=roles.length?actors.get(roles[0]).origin:new T.Vector3(0,.33,0);
  messenger={from:origin.clone(),to:new T.Vector3(target.x,1,target.z),started:now};
  if(event.role==='Gate'&&event.message.startsWith('PROMOTE')){generationPulse=now;promoRing.position.set(target.x,.6,target.z);promoRing.visible=true;}
 }
 function selectDepartment(id){
  lastSelection=id;labels.forEach(item=>item.element.classList.toggle('active',item.element.dataset.department===id));
  const d=DEPARTMENTS.find(item=>item.id===id);if(d){desiredFocus.set(d.x*.3,0,d.z*.3);targetZoom=1.12;}
 }
 const raycaster=new T.Raycaster(),pointer=new T.Vector2();let down=null,drag=false;
 renderer.domElement.addEventListener('pointerdown',event=>{down={x:event.clientX,y:event.clientY,a:azimuth,e:elevation};drag=false;renderer.domElement.setPointerCapture(event.pointerId);});
 renderer.domElement.addEventListener('pointermove',event=>{
  if(!down)return;const dx=event.clientX-down.x,dy=event.clientY-down.y;if(Math.hypot(dx,dy)>5)drag=true;
  if(drag){azimuth=down.a-dx*.004;elevation=T.MathUtils.clamp(down.e+dy*.003,.4,1.1);}
 });
 renderer.domElement.addEventListener('pointerup',event=>{
  if(!drag){
   pointer.set(event.clientX/innerWidth*2-1,-event.clientY/innerHeight*2+1);raycaster.setFromCamera(pointer,camera);
   const hits=raycaster.intersectObjects([...actorHits,...hitObjects],false);
   if(hits.length){const data=hits[0].object.userData;if(data.actor)onAgent?.(actors.get(data.actor));else if(data.department)onDepartment?.(data.department);}
  }down=null;
 });
 renderer.domElement.addEventListener('wheel',event=>{event.preventDefault();targetZoom=T.MathUtils.clamp(targetZoom-event.deltaY*.0008,.65,1.8);},{passive:false});
 function resize(){renderer.setSize(innerWidth,innerHeight);const aspect=innerWidth/innerHeight,frustum=innerWidth<750?(aspect<.8?44:25):20;camera.left=-frustum*aspect;camera.right=frustum*aspect;camera.top=frustum;camera.bottom=-frustum;camera.updateProjectionMatrix();}
 addEventListener('resize',resize);resize();
 let stopped=false,lastFrame=0,frameCount=0,active=true;document.addEventListener('visibilitychange',()=>{active=!document.hidden;});
 function frame(now){
  if(stopped)return;requestAnimationFrame(frame);
  if(!active||now-lastFrame<1000/40)return;lastFrame=now;
  const time=now*.001;zoom=T.MathUtils.lerp(zoom,targetZoom,.08);focus.lerp(desiredFocus,.05);
  // Camera offset preserves room for the short introduction on wide screens.
  camera.position.set(focus.x+Math.sin(azimuth)*48*Math.cos(elevation),35*Math.sin(elevation)+12,focus.z+Math.cos(azimuth)*48*Math.cos(elevation));
  camera.lookAt(focus.x+(innerWidth>1100?-3.8:0),.6,focus.z);camera.zoom=zoom;camera.updateProjectionMatrix();
  for(const a of actors.values()){
   if(a.moving){const t=Math.min(1,(now-a.started)/2200),smooth=t*t*(3-2*t);a.group.position.lerpVectors(a.origin,a.destination,smooth);a.group.rotation.y=Math.atan2(a.destination.x-a.origin.x,a.destination.z-a.origin.z);if(t>=1)a.moving=false;}
   const head=a.group.children[1];head.position.y=.87+Math.sin(time*1.8+a.group.position.x)*.028; // decorative idle bob, explicitly labeled.
  }
  const crystal=buildings.get('economy').group.children.find(o=>o.userData.decorativeSpin);if(crystal)crystal.rotation.y=time*.2;
  if(messenger){const t=(now-messenger.started)/2400;if(t<1){messageOrb.position.lerpVectors(messenger.from,messenger.to,t);messageOrb.position.y=1+Math.sin(t*Math.PI)*2;}else{messageOrb.position.y=-10;messenger=null;}}
  if(generationPulse){const age=(now-generationPulse)/2000;buildings.get('evolution').group.scale.setScalar(1+Math.max(0,1-age)*.04);if(promoRing.visible){promoRing.scale.setScalar(1+age*2);promoRing.material=mat('#dbc288',{transparent:true,opacity:Math.max(0,1-age),metalness:.3});if(age>1)promoRing.visible=false;}}
  for(const label of labels){
   const projected=label.position.clone();projected.y=label.height;projected.project(camera);
   label.element.style.left=((projected.x+1)/2*innerWidth)+'px';label.element.style.top=((-projected.y+1)/2*innerHeight)+'px';
   label.element.style.display=projected.z>1?'none':'';
   label.element.style.opacity=lastSelection&&lastSelection!==label.element.dataset.department?'.7':'1';
  }
  renderer.render(scene,camera);if(++frameCount===2)onReady?.();
 }
 requestAnimationFrame(frame);
 return {configure,showEvent,selectDepartment,actors,renderer,zoomBy:delta=>{targetZoom=T.MathUtils.clamp(targetZoom+delta,.65,1.8);},reset:()=>{azimuth=.76;elevation=.72;targetZoom=1;desiredFocus.set(-1,0,0);lastSelection=null;labels.forEach(l=>l.element.classList.remove('active'));},destroy:()=>{stopped=true;renderer.dispose();}};
}
