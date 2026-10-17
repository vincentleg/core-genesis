// Real browser scenarios against the CORE GENESIS site (local build or public URL). Deterministic, no model calls.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const BASE=process.argv[2]||'http://127.0.0.1:8090/',OUT=path.resolve(__dirname,'../public/testing');
(async()=>{
 let browser;
 try{browser=await chromium.launch({channel:'chrome',headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});}catch{browser=await chromium.launch({headless:true});}
 const results=[];
 async function scenario(id,role,viewport,fn){
  const page=await browser.newPage({viewport}),errors=[],failed=[],steps=[];
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('pageerror',e=>errors.push(String(e)));
  page.on('response',r=>{if(r.status()>=400)failed.push(r.status()+' '+r.url());});
  const step=async(task,check)=>{try{await check();steps.push({task,passed:true});}catch(e){steps.push({task,passed:false,error:String(e).slice(0,200)});throw e;}};
  const started=Date.now();let failure=null;
  try{await page.goto(BASE,{waitUntil:'load'});await fn(page,step);}catch(e){failure=String(e).slice(0,240);}
  await page.screenshot({path:path.join(OUT,'genesis-'+id+'.png')});
  results.push({id,role,viewport,passed:!failure&&errors.length===0&&failed.length===0,steps,console_errors:errors,failed_requests:failed,failure,latency_ms:Date.now()-started,screenshot:'genesis-'+id+'.png'});
  await page.close();
 }
 const visible=(page,sel)=>page.locator(sel).first().waitFor({state:'visible',timeout:8000});
 await scenario('hero','First-visit comprehension tester',{width:1440,height:900},async(page,step)=>{
  await step('hero headline and CORE/GENESIS distinction visible',async()=>{await visible(page,'.hero h1');const text=await page.locator('.hero').innerText();if(!/BUILDS CORE/i.test(text)||!/GENESIS/.test(text)||!/CORE/.test(text))throw new Error('hero copy missing');});
  await step('WATCH GENESIS RUN primary action visible',()=>visible(page,'#run-genesis'));
  await step('eight named AI employees rendered on campus',async()=>{await page.waitForFunction(()=>document.querySelectorAll('.crew-tag').length===8,null,{timeout:10000});});
 });
 await scenario('replay','One-click replay tester',{width:1440,height:900},async(page,step)=>{
  await step('replay starts labeled VERIFIED MISSION REPLAY',async()=>{await page.click('#run-genesis');await visible(page,'.run-badge');if(!/VERIFIED MISSION REPLAY/.test(await page.locator('.run-badge').innerText()))throw new Error('label');});
  await step('act 1 shows recorded mission contract',async()=>{await visible(page,'.run-card .run-tag');if(!/MISSION CONTRACT/.test(await page.locator('.run-card').innerText()))throw new Error('contract');});
  for(let act=2;act<=7;act++)await step('skip to act '+act,async()=>{await page.click('[data-run=next]');await page.waitForFunction(n=>document.querySelector('.run-head')?.innerText.includes('ACT '+n+' / 7'),act,{timeout:5000});});
  await step('final delivery shows pipeline awaiting CEO integration approval',async()=>{await visible(page,'#run-final .pipeline-state');if(!/AWAITING CORE INTEGRATION APPROVAL/.test(await page.locator('#run-final').innerText()))throw new Error('pipeline');});
  await step('deliverable links resolve',async()=>{for(const href of await page.locator('#run-final a.deliverable').evaluateAll(a=>a.map(x=>x.href).filter(h=>h.startsWith(location.origin)))){const r=await page.request.get(href);if(!r.ok())throw new Error(href+' '+r.status());}});
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
 await browser.close();
 const report={target:BASE,mode:'ACTUAL BROWSER EXECUTION (Playwright Chrome); deterministic scenarios, not human users',finished_at:new Date().toISOString(),passed:results.filter(r=>r.passed).length,total:results.length,results};
 fs.writeFileSync(path.join(OUT,'genesis-browser-report.json'),JSON.stringify(report,null,1));
 console.log(JSON.stringify({passed:report.passed,total:report.total,results:results.map(r=>({id:r.id,passed:r.passed,failure:r.failure,errors:r.console_errors.slice(0,3),failed:r.failed_requests.slice(0,3)}))},null,1));
})();
