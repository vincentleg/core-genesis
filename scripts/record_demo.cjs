// Records the one-minute demo video from the live site using Playwright's built-in recorder.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const URL=process.argv[2]||'https://core-genesis-living.vercel.app/',OUT=path.resolve(__dirname,'../video');
(async()=>{
 fs.mkdirSync(OUT,{recursive:true});
 let browser;try{browser=await chromium.launch({channel:'chrome',headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});}catch{browser=await chromium.launch({headless:true});}
 const context=await browser.newContext({viewport:{width:1280,height:720},recordVideo:{dir:OUT,size:{width:1280,height:720}}});
 const page=await context.newPage();await page.goto(URL,{waitUntil:'load'});await page.waitForTimeout(3000);
 await page.click('#run-genesis');await page.waitForTimeout(400);await page.click('[data-run=speed]');
 await page.waitForSelector('#run-final:not(.hidden)',{timeout:120000});await page.waitForTimeout(4000);
 const video=page.video();await context.close();await browser.close();
 fs.renameSync(await video.path(),path.join(OUT,'genesis-demo.webm'));console.log('saved video/genesis-demo.webm');
})();
