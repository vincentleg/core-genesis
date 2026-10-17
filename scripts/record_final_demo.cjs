// Deterministic capture of the final demo from the live site. Fixed viewport and scale; no mouse movement.
// Titles and subtitles are drawn as an in-page overlay layer during capture only (the site itself is unchanged).
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const URL=(process.argv[2]||'https://core-genesis-living.vercel.app/')+'?autoplay=0',OUT=path.resolve(__dirname,'../video/capture');
const F=1.08,HERO=3.0,TOTAL=54.0; // capture runs F× longer than the final video; ffmpeg retimes it
const timeline=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../video/vo/timeline.json'))).cues;
(async()=>{
 fs.rmSync(OUT,{recursive:true,force:true});fs.mkdirSync(OUT,{recursive:true});
 const browser=await chromium.launch({channel:'chrome',headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const context=await browser.newContext({viewport:{width:1280,height:720},deviceScaleFactor:1,recordVideo:{dir:OUT,size:{width:1280,height:720}}});
 const page=await context.newPage();const recStart=Date.now();let mark=null;
 await page.exposeFunction('__mark',()=>{mark=Date.now();});
 await page.goto(URL,{waitUntil:'load'});
 await page.waitForFunction(()=>document.getElementById('loading')?.classList.contains('hidden')&&window.GENESIS_RUN,null,{timeout:30000});
 await page.waitForTimeout(2500); // let the scene, shadows and agent tags settle before t0
 await page.evaluate(({F,HERO,cues})=>{
  const css=`#run,.world-corner,.generation-bubble,footer,.department-dock,.playback{display:none!important}
  .vx{position:fixed;z-index:50;pointer-events:none;font-family:"Avenir Next","Segoe UI",system-ui,sans-serif;transition:opacity .35s ease,transform .35s ease;opacity:0}
  .vx.on{opacity:1}
  #vx-chapter{left:36px;top:96px;font-size:13px;font-weight:700;letter-spacing:2.4px;color:#22302c;background:#fbfaf7ee;border-radius:6px;padding:7px 12px;box-shadow:0 6px 18px #22302c22}
  #vx-sub{left:50%;bottom:26px;transform:translateX(-50%);width:max-content;max-width:1100px;text-align:center;font-size:27px;line-height:1.3;font-weight:600;color:#fff;background:#141b19d9;border-radius:8px;padding:8px 18px;text-shadow:0 1px 2px #000}
  .vx-call{right:30px;top:300px;width:400px;background:#fbfaf7f5;border-radius:14px;padding:18px 22px;box-shadow:0 18px 44px #22302c33;color:#1b2724;transform:translateY(8px)}
  .vx-call.on{transform:none}
  .vx-call b{display:block;font-size:24px;line-height:1.15;letter-spacing:-.3px;text-transform:uppercase}
  .vx-call small{display:block;margin-top:8px;font-size:14px;line-height:1.35;color:#3c4842}
  .vx-call .row{display:none;margin-top:10px;font-size:20px;font-weight:700;color:#2f6559}.vx-call .row.on{display:block}
  #vx-title{left:50%;top:50%;transform:translate(-2%,-50%);width:560px;background:#fbfaf7f2;border-radius:16px;padding:26px 30px;box-shadow:0 24px 60px #22302c3a;color:#1b2724}
  #vx-title h1{margin:0;font-size:56px;letter-spacing:-1.5px;line-height:1}#vx-title h2{margin:8px 0 18px;font-size:22px;font-weight:600;color:#2f6559}
  #vx-title p{margin:6px 0;font-size:17px}#vx-title p b{display:inline-block;width:92px;letter-spacing:2px;color:#2f6559}#vx-title p+p b{color:#a8874a}
  #vx-bench{right:30px;top:280px;width:440px;background:#fbfaf7f7;border-radius:14px;padding:18px 22px;box-shadow:0 18px 44px #22302c33;color:#1b2724}
  #vx-bench .k{font-size:12px;letter-spacing:2px;font-weight:700;color:#5d6560}
  .bar{display:grid;grid-template-columns:150px 1fr 48px;gap:10px;align-items:center;margin-top:12px;font-size:15px;font-weight:600}
  .bar i{display:block;height:18px;border-radius:9px;background:#dcd8cf;overflow:hidden}.bar i span{display:block;height:100%;width:0;border-radius:9px;transition:width 1.4s cubic-bezier(.2,.7,.2,1)}
  .bar b{font-size:22px}
  .verdict{display:none;margin-top:12px;font-size:19px;font-weight:800;letter-spacing:.5px}.verdict.on{display:block}
  #vx-end{inset:0;display:grid;place-items:center;background:radial-gradient(ellipse at 50% 48%,#fbfaf7f0 0%,#fbfaf7c8 38%,#fbfaf700 75%);}
  #crew-tags,#labels{transition:opacity .5s}
  #vx-end>div{text-align:center;margin-bottom:120px}#vx-end h1{margin:0;font-size:64px;letter-spacing:-1.5px;color:#1b2724}#vx-end h2{margin:4px 0 18px;font-size:20px;letter-spacing:4px;color:#2f6559}
  #vx-end .chips span{display:inline-block;margin:0 6px;padding:8px 14px;border-radius:20px;background:#2f6559;color:#fff;font-size:15px;font-weight:700;letter-spacing:1px}
  #vx-end .url{margin-top:16px;font-size:24px;font-weight:700;color:#1b2724}#vx-end .credit{margin-top:10px;font-size:12px;letter-spacing:1.5px;color:#5d6560}`;
  document.head.insertAdjacentHTML('beforeend','<style>'+css+'</style>');
  document.body.insertAdjacentHTML('beforeend',`<div class="vx" id="vx-chapter"></div>
  <div class="vx" id="vx-title"><h1>CORE GENESIS</h1><h2>The AI Company Building CORE</h2><p><b>CORE</b>the civilization we're building</p><p><b>GENESIS</b>the AI company building it</p></div>
  <div class="vx vx-call" id="vx-c1"><b>One mission.<br>Specialized AI teams.</b><small>8 AI employees · 8 recorded handoffs</small></div>
  <div class="vx vx-call" id="vx-c2"><b>Working software delivered</b><small>CORE Local Solutions — report a local problem, propose a solution, request human review.</small><div class="row" id="vx-c2r">✓ 7/7 application tests</div></div>
  <div class="vx vx-call" id="vx-c3"><b>200 synthetic product evaluations</b><small>100 CORE + 100 GENESIS · AI-simulated perspectives, not human users</small><div class="row" id="vx-c3r">✓ 8/8 browser scenarios passed</div></div>
  <div class="vx" id="vx-bench"><div class="k">CITATION-CHECKING POLICY · INDEPENDENT HELD-OUT TESTS</div>
   <div class="bar">Baseline<i><span id="vx-b1" style="background:#9a8f7e"></span></i><b>4/6</b></div>
   <div class="bar">Improved policy<i><span id="vx-b2" style="background:#2f6559"></span></i><b>6/6</b></div>
   <div class="verdict" id="vx-v1" style="color:#2f6559">✓ PROMOTE V1</div><div class="verdict" id="vx-v2" style="color:#9a5b3c">✕ REJECT NO-GAIN MUTATION <small style="font-weight:600">(later candidate 6/6 = 6/6)</small></div></div>
  <div class="vx vx-call" id="vx-c5"><b>Autonomous execution.<br>Human authorization.</b><small>Prototype built — awaiting CORE integration approval. The original CORE repository is unchanged.</small></div>
  <div class="vx" id="vx-end"><div><h1>CORE GENESIS</h1><h2>THE LIVING AI COMPANY</h2><div class="chips"><span>REAL SOFTWARE</span><span>VERIFIED TESTS</span><span>MEASURABLE SELF-IMPROVEMENT</span></div><div class="url">core-genesis-living.vercel.app</div><div class="credit">CRUSOE MANAGED INFERENCE × NVIDIA NEMOTRON</div></div></div>
  <div class="vx" id="vx-sub"></div>`);
  const $=id=>document.getElementById(id);
  const chapters=[[0,'01 · THE VISION'],[6,'02 · THE MISSION'],[16.6,'03 · REAL SOFTWARE'],[25.9,'04 · BETA TESTING LAB'],[34.3,'05 · RECURSIVE IMPROVEMENT'],[44.4,'06 · HUMAN GOVERNANCE'],[49.2,'07 · THE REVEAL']];
  const spans=[['vx-title',0,2.75],['vx-c1',6.2,16.4],['vx-c2',16.8,25.7],['vx-c3',26.1,34.1],['vx-bench',34.5,44.2],['vx-c5',44.6,49.0],['vx-end',50.6,99]];
  const once={};const t0=performance.now();let started=false;window.__mark();
  (function loop(){
   const t=(performance.now()-t0)/1000/F; // output-video seconds
   if(!started&&t>=HERO/F){started=true;document.getElementById('run-genesis').click();}
   let ch='';for(const [s,l] of chapters)if(t>=s)ch=l;$('vx-chapter').textContent=ch;$('vx-chapter').classList.toggle('on',t<50.6);
   for(const [id,a,b] of spans)$(id).classList.toggle('on',t>=a&&t<b);
   $('vx-c2r').classList.toggle('on',t>=20.5);$('vx-c3r').classList.toggle('on',t>=29.6);
   if(t>=35.2)$('vx-b1').style.width='66.7%';if(t>=36.6)$('vx-b2').style.width='100%';
   $('vx-v1').classList.toggle('on',t>=38.6);$('vx-v2').classList.toggle('on',t>=40.4);
   if(t>=50.6&&!once.end){once.end=true;document.querySelector('[data-run=close]')?.click();document.getElementById('crew-tags').style.opacity='0';document.getElementById('labels').style.opacity='0';window.GENESIS.campus().reset();}
   const cue=cues.find(c=>t>=c.start&&t<c.end);$('vx-sub').textContent=cue?cue.text:'';$('vx-sub').classList.toggle('on',!!cue);
   requestAnimationFrame(loop);
  })();
 },{F,HERO,cues:timeline});
 await page.waitForTimeout((TOTAL*F+0.6)*1000);
 const video=page.video();await context.close();await browser.close();
 const file=await video.path();fs.renameSync(file,path.join(OUT,'capture.webm'));
 fs.writeFileSync(path.join(OUT,'capture.json'),JSON.stringify({offset_s:(mark-recStart)/1000,factor:F,total_s:TOTAL}));
 console.log('capture offset',(mark-recStart)/1000);
})();
