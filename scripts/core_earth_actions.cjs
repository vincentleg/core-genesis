/** Observed, canonical Earth actions. Read state; manipulate CORE only through real UI. */
const selectors={zoom_in:'.maplibregl-ctrl-zoom-in:visible',zoom_out:'.maplibregl-ctrl-zoom-out:visible'};
async function prepareEarth(page){
 await page.waitForFunction(()=>{const s=globalThis.CORE_EARTH?.state;return s?.ready&&s.civReady&&s.scale==='city'&&!s.map.isMoving();},null,{timeout:25000});
 if(await page.locator('#ea-panel').isVisible())await page.locator('[data-close="ea-panel"]').click();
 await page.locator('#ea-panel').waitFor({state:'hidden'});
}
async function observeActions(page){
 const actions=[];
 for(const [name,selector] of Object.entries(selectors)){
  const button=page.locator(selector);
  if(await button.count()===1&&await button.isEnabled()&&await button.evaluate(el=>{const b=el.getBoundingClientRect(),hit=document.elementFromPoint(b.x+b.width/2,b.y+b.height/2);return hit===el||el.contains(hit);})){actions.push({name,selector,label:await button.getAttribute('aria-label')});}
 }
 return actions;
}
function validateAction(name,catalog){if(!Object.hasOwn(selectors,name)||!catalog.some(a=>a.name===name))throw Error('AI selected an unavailable Earth action: '+name);return selectors[name];}
async function executeAction(page,name,catalog){
 const selector=validateAction(name,catalog);await prepareEarth(page);
 validateAction(name,await observeActions(page));
 const before=await page.evaluate(()=>globalThis.CORE_EARTH.state.map.getZoom());
 await page.locator(selector).click();
 await page.waitForFunction(({before,name})=>name==='zoom_in'?globalThis.CORE_EARTH.state.map.getZoom()>before+0.1:globalThis.CORE_EARTH.state.map.getZoom()<before-0.1,{before,name});
 await page.waitForFunction(()=>!globalThis.CORE_EARTH.state.map.isMoving());
 return {name,before,after:await page.evaluate(()=>globalThis.CORE_EARTH.state.map.getZoom()),method:'real_pointer_click',forced:false};
}
module.exports={prepareEarth,observeActions,validateAction,executeAction};
