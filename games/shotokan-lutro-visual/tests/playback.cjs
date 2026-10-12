const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
  const page=await browser.newPage({offline:true});
  await require('./offline_page.cjs')(page,false);
  await page.waitForFunction(()=>document.body.dataset.ready==='true');
  await page.waitForFunction(()=>!dojoHost.introActive());
  await page.locator('#study > summary').click();
  const value=()=>page.evaluate(()=>speed);
  assert.equal(await value(),.5);
  for(const expected of [.25,1,.5]){await page.locator('#slow').click();assert.equal(await value(),expected)}
  // Exercise the real animation loop, rather than just checking the button state.
  await page.evaluate(()=>{window.playbackTicks=0;const update=dojoHost.update;dojoHost.update=()=>{window.playbackTicks++;return update()}});
  const count=async(rate)=>{
   await page.evaluate(rate=>{setSpeed(rate);window.playbackTicks=0},rate);
   await page.waitForTimeout(1200);
   return page.evaluate(()=>window.playbackTicks);
  };
  const half=await count(.5),normal=await count(1);
  assert(half>=20&&normal>half*1.5&&normal<half*2.5,{half,normal});
  for(const selector of ['#lesson','#demo','#practice','#play']){
   await page.evaluate(()=>setSpeed(1));await page.locator(selector).click();assert.equal(await value(),.5);
  }
  console.log(JSON.stringify({half,normal,checks:'Default half speed; 0.5/0.25/1 controls; real playback cadence; lesson/demo/practice/fight reset'},null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
