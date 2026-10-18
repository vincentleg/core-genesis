/** Short read-only diagnostic. No inference, source patches, fake tiles or pilot sessions. */
const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const {allowedMapAsset,publicHeaders}=require('./core_map_network.cjs');
const c=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),u=new URL(c.base);
if(u.protocol!=='http:'||u.hostname!=='127.0.0.1'||c.suite!=='earth-diagnostic'||!path.resolve(c.output).startsWith(path.resolve(__dirname,'../company/core-browser')+path.sep))throw Error('Local diagnostic only');
const out=c.output,record={kind:'read_only_earth_diagnostic',commit:c.commit,model_calls:0,cost_usd:0,external_requests:c.external_network,stages:[],events:[],requests:[],page_errors:[],console_errors:[]};
const save=()=>fs.writeFileSync(path.join(out,'diagnostic.json'),JSON.stringify(record,null,2));
(async()=>{let browser,context;const started=Date.now();try{
 browser=await chromium.launch({channel:'chrome',headless:true,handleSIGTERM:false,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 context=await browser.newContext({viewport:{width:1440,height:1000},serviceWorkers:'block'});await context.tracing.start({screenshots:true,snapshots:true,sources:false});
 await context.route('**/*',route=>{const q=route.request(),url=new URL(q.url());if(url.origin===c.base&&q.method()==='GET')return route.continue();if(c.external_network==='public-assets'&&q.method()==='GET'&&allowedMapAsset(q.url())){record.requests.push({url:q.url(),allowed:true});return route.continue({headers:publicHeaders(q)});}record.requests.push({url:q.url(),blocked:true});return route.abort('blockedbyclient');});
 await context.routeWebSocket('**/*',ws=>ws.close());
 const page=await context.newPage();record.request_failures=[];page.on('requestfailed',q=>record.request_failures.push({url:q.url(),error:q.failure()?.errorText}));record.data_responses=[];record.map_responses=[];page.on('response',r=>{if(new URL(r.url()).origin===c.base&&new URL(r.url()).pathname.startsWith('/data/'))record.data_responses.push({path:new URL(r.url()).pathname,status:r.status(),commit:r.headers()['x-core-commit']});if(allowedMapAsset(r.url()))record.map_responses.push({url:r.url(),status:r.status()});});page.setDefaultTimeout(c.verify_earth_mission?6500:2500);page.on('pageerror',e=>record.page_errors.push(e.message));page.on('console',m=>{if(m.type()==='error')record.console_errors.push(m.text())});
 await page.addInitScript(()=>{globalThis.__hqEvents=[];const observer=setInterval(()=>{const m=globalThis.CORE_EARTH?.state?.map;if(!m)return;clearInterval(observer);for(const kind of ['load','idle','render','error'])m.on(kind,e=>{if(kind==='render'&&globalThis.__hqEvents.filter(x=>x.kind==='render').length>=3)return;globalThis.__hqEvents.push({kind,at:performance.now(),message:e.error?.message});});},25);setTimeout(()=>clearInterval(observer),25000);});
 const response=await page.goto(c.base+'/world.html?quality=low',{waitUntil:'networkidle',timeout:12000});if(response.headers()['x-core-commit']!==c.commit)throw Error('Commit mismatch');
 async function state(name){const value=await page.evaluate(()=>{const s=globalThis.CORE_EARTH?.state,m=s?.map;return {ready:s?.ready,civReady:s?.civReady||false,quality:s?.quality,mapLoaded:m?.loaded(),mapLoadEventSent:m?._loaded,styleLoaded:m?.isStyleLoaded(),visibility:document.visibilityState,webgl:!!m?.getCanvas()?.getContext('webgl2'),sources:m?.style?.sourceCaches?Object.fromEntries(Object.entries(m.style.sourceCaches).map(([k,v])=>[k,{loaded:v.loaded(),type:v.getSource()?.type}])):null,buttons:[...document.querySelectorAll('button')].filter(b=>b.className.includes('maplibre')).map(b=>({class:b.className,label:b.getAttribute('aria-label'),title:b.title})),events:globalThis.__hqEvents};});record.stages.push({name,elapsed_ms:Date.now()-started,...value});save();}
 await page.waitForTimeout(4000);await state('before_any_explicit_screenshot');
 await page.screenshot({path:path.join(out,'before.png'),animations:'disabled',timeout:3000}).catch(e=>record.screenshot_error=e.message);await state('after_animation_disabled_screenshot');
 await page.mouse.move(1200,450);await page.mouse.wheel(0,-120);record.events.push({action:'Actual mouse wheel on visible map',at:new Date().toISOString()});
 await page.waitForTimeout(4000);await state('after_actual_wheel');
 const plus=page.locator('.maplibregl-ctrl-zoom-in');if(await plus.count()&&!c.verify_earth_mission){
  try{await plus.click({timeout:2000});record.events.push({action:'Actual map Zoom in button',passed:true});}catch(e){record.events.push({action:'Actual map Zoom in button',passed:false,error:e.message});}
 }
 await page.waitForTimeout(3000);await state('after_actual_zoom_control');
 if(c.verify_earth_mission){
  record.mission_regression={kind:'scripted_read_only_not_AI',actions:[],passed:false};
  const act=async(name,work)=>{const a={name,started_at:new Date().toISOString()};record.mission_regression.actions.push(a);save();try{await work();a.passed=true;}catch(e){a.passed=false;a.error=e.message;throw e;}finally{save();}};
  await act('Enter actual initialized Earth',async()=>{await page.waitForFunction(()=>globalThis.CORE_EARTH?.state.civReady===true,null,{timeout:10000});await page.locator('#ea-start').click();});
  await act('Open actual mission catalog',async()=>{await page.locator('#ea-problems-btn').click();await page.locator('#ea-panel-body button[data-mission]').first().waitFor();});
  await page.screenshot({path:path.join(out,'catalog.png'),animations:'disabled',timeout:5000}).catch(e=>record.catalog_screenshot_error=e.message);
  await act('Select previously observed housing mission using the first visible matching control',async()=>{const buttons=page.locator('#ea-panel-body button[data-mission="mission.sf.housing-resilience"]:visible');record.mission_regression.matching_controls=await buttons.count();if(!record.mission_regression.matching_controls)throw Error('Observed mission absent');await buttons.first().click();await page.locator('#ea-panel-body .cv-findings').waitFor();});
  await act('Verify actual dated findings, citation links and committed data responses',async()=>{const panel=page.locator('#ea-panel-body'),findings=panel.locator('.cv-findings');record.mission_regression.findings=await findings.innerText();record.mission_regression.links=await findings.locator('a').evaluateAll(es=>es.map(e=>({text:e.innerText,href:e.href})));if(record.mission_regression.findings.length<100||!record.mission_regression.links.length||record.data_responses.filter(d=>d.status===200&&d.commit===c.commit).length<5)throw Error('Findings or source provenance missing');});
  record.mission_regression.passed=true;await state('after_actual_mission_open');
 }
 await page.screenshot({path:path.join(out,'after.png'),animations:'disabled',timeout:3000}).catch(()=>{});
 }catch(e){record.failure=e.message;}
 finally{if(context)await context.tracing.stop({path:path.join(out,'diagnostic-trace.zip')}).catch(e=>record.trace_error=e.message);if(browser)await browser.close();record.runtime_ms=Date.now()-started;save();console.log(JSON.stringify({diagnostic:out,states:record.stages.map(s=>({name:s.name,ready:s.ready,civReady:s.civReady,mapLoaded:s.mapLoaded,mapLoadEventSent:s.mapLoadEventSent})),failure:record.failure,mission_regression:record.mission_regression?.passed}));if(record.failure)process.exitCode=1;}
})();
