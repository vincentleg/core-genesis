// Real browser scenarios against the CORE GENESIS site (local build or public URL). Deterministic, no model calls.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const BASE=process.argv[2]||'http://127.0.0.1:8090/',MANUAL=BASE+'?autoplay=0',OUT=path.resolve(__dirname,'../public/testing');
(async()=>{
 let browser;
 try{browser=await chromium.launch({channel:'chrome',headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});}catch{browser=await chromium.launch({headless:true});}
 const results=[];let autoplayDuration=null;
 async function scenario(id,role,viewport,fn,url=MANUAL){
  const page=await browser.newPage({viewport}),errors=[],failed=[],steps=[],inference=[];
  page.on('request',r=>{if(/\/api\/|crusoe|inference|nemotron/i.test(r.url()))inference.push(r.url());});
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('pageerror',e=>errors.push(String(e)));
  page.on('response',r=>{if(r.status()>=400)failed.push(r.status()+' '+r.url());});
  const step=async(task,check)=>{try{await check();steps.push({task,passed:true});}catch(e){steps.push({task,passed:false,error:String(e).slice(0,200)});throw e;}};
  const started=Date.now();let failure=null;
  try{await page.goto(url,{waitUntil:'load'});await fn(page,step);}catch(e){failure=String(e).slice(0,240);}
  await page.screenshot({path:path.join(OUT,'genesis-'+id+'.png')});
  results.push({id,role,viewport,inference_requests:inference,passed:!failure&&errors.length===0&&failed.length===0&&inference.length===0,steps,console_errors:errors,failed_requests:failed,failure,latency_ms:Date.now()-started,screenshot:'genesis-'+id+'.png'});
  await page.close();
 }
 const visible=(page,sel)=>page.locator(sel).first().waitFor({state:'visible',timeout:8000});
 await scenario('hero','First-visit comprehension tester',{width:1440,height:900},async(page,step)=>{
  await step('hero headline and CORE/GENESIS distinction visible',async()=>{await visible(page,'.hero h1');const text=await page.locator('.hero').innerText();if(!/BUILDS CORE/i.test(text)||!/GENESIS/.test(text)||!/CORE/.test(text))throw new Error('hero copy missing');});
  await step('WATCH GENESIS RUN primary action visible',()=>visible(page,'#run-genesis'));
  await step('eight named AI employees rendered on campus',async()=>{await page.waitForFunction(()=>document.querySelectorAll('.crew-tag').length===8,null,{timeout:10000});});
 });
 await scenario('replay','One-click replay tester',{width:1440,height:900},async(page,step)=>{
  await step('manual start shows VERIFIED MISSION REPLAY headline',async()=>{await page.click('#run-genesis');await visible(page,'#run-hl .run-badge');if(!/VERIFIED MISSION REPLAY/.test(await page.locator('#run-hl').innerText()))throw new Error('label');});
  await step('evidence details open with recorded mission contract',async()=>{await page.click('#run-hl [data-run=details]');await visible(page,'.run-card .run-tag');if(!/MISSION CONTRACT/.test(await page.locator('.run-card').innerText()))throw new Error('contract');});
  await step('pause and resume control',async()=>{await page.click('[data-run=toggle]');if(!/Play/.test(await page.locator('[data-run=toggle]').innerText()))throw new Error('not paused');await page.click('[data-run=toggle]');if(!/Pause/.test(await page.locator('[data-run=toggle]').innerText()))throw new Error('not resumed');});
  for(let act=2;act<=6;act++)await step('skip to act '+act,async()=>{await page.click('[data-run=next]');await page.waitForFunction(n=>document.querySelector('#run-hl')?.innerText.includes('ACT '+n+'/7'),act,{timeout:5000});});
  await step('final screen shows three outcomes and READY FOR CEO REVIEW',async()=>{await page.click('[data-run=next]');await visible(page,'#run-final .ceo-review');const text=await page.locator('#run-final').innerText();if(!/READY FOR CEO REVIEW/.test(text)||(await page.locator('#run-final .outcome').count())!==3||!(await page.locator('#run-final .pipeline-state').count()))throw new Error('final');});
  await step('restart control returns to act 1',async()=>{await page.click('#run-final [data-run=restart]');await page.waitForFunction(()=>document.querySelector('#run-hl')?.innerText.includes('ACT 1/7'),null,{timeout:5000});for(let k=0;k<6;k++)await page.click('[data-run=next]');await visible(page,'#run-final .ceo-review');});
  await step('deliverable links resolve',async()=>{for(const href of await page.locator('#run-final a.deliverable, #run-final a.outcome').evaluateAll(a=>a.map(x=>x.href).filter(h=>h.startsWith(location.origin)))){const r=await page.request.get(href);if(!r.ok())throw new Error(href+' '+r.status());}});
 });
 await scenario('lab','Evidence-seeking judge',{width:1280,height:860},async(page,step)=>{
  await step('testing lab opens with real counts',async()=>{await page.click('#open-lab');await visible(page,'#evidence-content .lab-campaign');if(!/target synthetic evaluations actually completed/.test(await page.locator('#evidence-content').innerText()))throw new Error('counts');});
  await step('browser screenshots load',async()=>{await page.waitForFunction(()=>[...document.querySelectorAll('#evidence-content img')].every(i=>i.complete&&i.naturalWidth>0),null,{timeout:8000});});
  await step('pipeline modal opens',async()=>{await page.click('#close-evidence');await page.click('#open-pipeline');await visible(page,'#evidence-content .pipeline');});
 });
 await scenario('mobile','Small-screen visitor',{width:390,height:844},async(page,step)=>{
  await step('hero readable on phone without horizontal scroll',async()=>{await visible(page,'#run-genesis');const w=await page.evaluate(()=>document.documentElement.scrollWidth);if(w>392)throw new Error('scrollWidth '+w);});
  await step('agent profile opens from name tag',async()=>{await page.click('#explore-company');await page.waitForTimeout(600);await page.locator('.crew-tag[data-crew=Nova]').click({force:true});await visible(page,'#context-content h2');if(!/Nova/.test(await page.locator('#context-content h2').innerText()))throw new Error('agent');});
 });
 await scenario('autoplay','Fresh visitor (no click)',{width:1440,height:900},async(page,step)=>{
  await step('replay starts automatically without a click',async()=>{await page.waitForFunction(()=>document.body.dataset.replay==='running',null,{timeout:20000});});
  await step('complete sequence finishes in 45-60 seconds',async()=>{await page.waitForFunction(()=>document.body.dataset.replay==='finished',null,{timeout:90000});autoplayDuration=await page.evaluate(()=>window.GENESIS_RUN.duration_s);if(!(autoplayDuration>=45&&autoplayDuration<=60))throw new Error('duration '+autoplayDuration);});
  await step('no automatic restart after finishing',async()=>{await page.waitForTimeout(3000);if(await page.evaluate(()=>document.body.dataset.replay)!=='finished')throw new Error('restarted');});
 },BASE);
 await browser.close();
 const report={target:BASE,mode:'ACTUAL BROWSER EXECUTION (Playwright Chrome); deterministic scenarios, not human users',finished_at:new Date().toISOString(),passed:results.filter(r=>r.passed).length,total:results.length,autoplay_duration_s:autoplayDuration,public_inference_requests:results.flatMap(r=>r.inference_requests).length,results};
 fs.writeFileSync(path.join(OUT,'genesis-browser-report.json'),JSON.stringify(report,null,1));
 console.log(JSON.stringify({passed:report.passed,total:report.total,duration:report.autoplay_duration_s,inference:report.public_inference_requests,results:results.map(r=>({id:r.id,passed:r.passed,failure:r.failure,errors:r.console_errors.slice(0,3),failed:r.failed_requests.slice(0,3)}))},null,1));
})();
