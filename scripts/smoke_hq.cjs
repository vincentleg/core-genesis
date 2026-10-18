/** Short local HQ branding/status regression. No historical evidence overwritten. */
const {spawn}=require('child_process'),{chromium}=require('playwright'),fs=require('fs');
(async()=>{
 const base='http://127.0.0.1:8098',child=spawn('python3',['-m','core_genesis.server','--port','8098'],{stdio:'ignore'});let browser;
 try{
  let ready=false;for(let i=0;i<60;i++){try{if((await fetch(base+'/hq-status.json')).ok){ready=true;break;}}catch{}await new Promise(r=>setTimeout(r,100));}if(!ready)throw Error('HQ server not ready');
  browser=await chromium.launch({channel:'chrome',headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const context=await browser.newContext(),page=await context.newPage(),errors=[];
  await context.route('**/*',route=>new URL(route.request().url()).origin===base?route.continue():route.abort());
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/?autoplay=0');await page.locator('#welcome').waitFor();
  if(!(await page.locator('.brand').innerText()).includes('HQ'))throw Error('HQ brand missing');
  await page.getByRole('link',{name:'CORE HQ status'}).click();await page.getByText('Recorded execution evidence',{exact:false}).waitFor();
  if(!(await page.locator('#source').innerText()).includes('da51a1b9'))throw Error('Verified CORE provenance missing');
  if(await page.locator('#sessions tr').count()<2)throw Error('Recorded sessions missing');
  const rejected=await fetch(base+'/api/company/mission',{method:'POST',headers:{'Content-Type':'application/json','X-Genesis-Action':'mission'},body:JSON.stringify({objective:'Analyze the actual local CORE project'})});
  if(rejected.status!==403)throw Error('Paid mission endpoint was not blocked');
  if(errors.length)throw Error(errors.join('\n'));
  fs.mkdirSync('company/hq-smoke',{recursive:true});await page.screenshot({path:'company/hq-smoke/status.png',fullPage:true});
  fs.writeFileSync('company/hq-smoke/report.json',JSON.stringify({passed:true,checks:['HQ visible branding','navigation to status page','actual source SHA','recorded session table','zero page errors','paid mission endpoint blocked before execution'],model_calls:0},null,2));
  console.log('HQ smoke: 6 checks passed; zero model calls');
 }finally{if(browser)await browser.close();child.kill('SIGTERM');}
})().catch(e=>{console.error(e.message);process.exitCode=1});
