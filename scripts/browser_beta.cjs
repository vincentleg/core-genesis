/** Fixed, local-only browser testing actors. No LLM calls or generated actions. */
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),http=require('http'),net=require('net'),{spawn}=require('child_process');
const directory=path.resolve(process.argv[2]||''),output=path.resolve(process.argv[3]||''),python=process.argv[4]||'python3';
if(!directory.includes(path.join('artifacts','core-local-solutions','runs'))||!output.includes(path.join('company','testing')))throw Error('Only generated CORE artifact and local testing directories are allowed');
const actors=[{id:'resident',role:'Resident journey tester',viewport:{width:1440,height:1000}},{id:'mobile',role:'Small-screen contributor tester',viewport:{width:390,height:844}},{id:'safety',role:'Input and authorization tester',viewport:{width:1280,height:900}}];
(async()=>{
 fs.mkdirSync(output,{recursive:true});
 const probe=net.createServer();await new Promise(resolve=>probe.listen(0,'127.0.0.1',resolve));const port=probe.address().port;await new Promise(resolve=>probe.close(resolve));
 const child=spawn(python,[path.join(directory,'app.py'),'--port',String(port)],{cwd:directory,stdio:['ignore','pipe','pipe']});let startup='';child.stdout.on('data',d=>startup+=d);child.stderr.on('data',d=>startup+=d);child.on('error',e=>startup+=e.message);
 const base='http://127.0.0.1:'+port;let browser;
 try{
  let ready=false;for(let i=0;i<50;i++){try{await new Promise((resolve,reject)=>http.get(base+'/api/state',r=>{r.resume();r.statusCode===200?resolve():reject(Error('Not ready'))}).on('error',reject));ready=true;break;}catch{}await new Promise(resolve=>setTimeout(resolve,100));}if(!ready)throw Error('Generated app did not start: '+startup);
  try{browser=await chromium.launch({channel:'chrome',headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});}catch{browser=await chromium.launch({headless:true});}
  const results=[];
  for(const actor of actors){
   const context=await browser.newContext({viewport:actor.viewport}),page=await context.newPage(),errors=[],consoleErrors=[],blocked=[],steps=[];let failure=null;const started=Date.now();
   await context.route('**/*',route=>{const url=new URL(route.request().url());if(url.origin===base)return route.continue();blocked.push(url.origin);return route.abort();});
   page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});page.setDefaultTimeout(10000);
   try{
    await page.goto(base);await page.waitForFunction(()=>document.querySelector('#intro').textContent.length>0);steps.push({task:'application started in actual Chrome context',passed:true});
    if(actor.id==='safety'){
     if(await page.locator('#problem-form').evaluate(e=>e.checkValidity()))throw Error('Empty problem form unexpectedly valid');
     const rejected=await page.request.post(base+'/api/problems',{headers:{'X-Local-Solutions':'explicit-action'},data:{title:'Invalid evidence test',description:'An observation that is deliberately paired with unsafe evidence.',location:'Test plaza',evidence:'javascript:alert(1)'}});if(rejected.status()!==400)throw Error('Unsafe evidence was not rejected');steps.push({task:'empty input and unsafe evidence rejected',passed:true});
    }
    const title='BETA TEST '+actor.id+' '+Date.now();
    await page.locator('#problem-form [name="title"]').fill(title);await page.locator('#problem-form [name="description"]').fill('Synthetic browser-test fixture: residents report a difficult crossing near their local library.');await page.locator('#problem-form [name="location"]').fill('Synthetic test plaza');
    if(actor.id==='mobile'){await page.locator('#problem-form [name="title"]').focus();await page.keyboard.press('Tab');if(!await page.locator('#problem-form [name="description"]').evaluate(e=>e===document.activeElement))throw Error('Keyboard field sequence failed');}
    await page.locator('#problem-form button').click();const card=page.locator('.problem').filter({hasText:title});await card.waitFor();steps.push({task:'created local problem using actual form',passed:true});
    await card.locator('textarea').fill('Synthetic browser-test proposal: convene a resident review of safe, accessible crossing options.');await card.locator('form button').click();await card.getByText('PENDING HUMAN REVIEW',{exact:true}).waitFor();steps.push({task:'linked solution appears pending human review',passed:true});
    const state=await(await page.request.get(base+'/api/state')).json(),p=state.problems.find(p=>p.title===title),solution=state.solutions.find(s=>s.problem_id===p.id);if(!solution||solution.authorized_for_real_world!==false||solution.status!=='pending_human_review')throw Error('Human authority invariant failed');
    if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2))throw Error('Horizontal overflow at tested viewport');
    steps.push({task:'persisted data, readable viewport and no real-world authorization verified',passed:true});
    if(errors.length||blocked.length)throw Error('Browser error or disallowed network attempt');
   }catch(error){failure={message:error.message,stack:error.stack};steps.push({task:'execution failure',passed:false,error:error.message});}
   await page.screenshot({path:path.join(output,actor.id+'.png'),fullPage:true}).catch(()=>{});
   results.push({...actor,started_at:started/1000,latency_ms:Date.now()-started,passed:!failure,steps,browser_errors:errors,console_errors:consoleErrors,blocked_external_requests:blocked,screenshot:actor.id+'.png',failure,execution:'Real local Chrome browser context; deterministic tester, no synthetic customer opinion or model-directed browsing'});
   await context.close();
  }
  const report={mode:'ACTUAL LOCAL BROWSER EXECUTION',started_application:base,application_startup:startup,agents:results,passed:results.every(r=>r.passed),completed:results.length,successes:results.filter(r=>r.passed).length,new_model_requests:0,fixtures:'All created records are explicitly labeled synthetic browser-test fixtures, not community submissions.'};
  fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));process.exitCode=report.passed?0:1;
 }finally{if(browser)await browser.close();child.kill('SIGTERM');}
})().catch(error=>{fs.mkdirSync(output,{recursive:true});fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({passed:false,error:error.message,completed:0,agents:[],new_model_requests:0}));console.error(error.message);process.exit(1)});
