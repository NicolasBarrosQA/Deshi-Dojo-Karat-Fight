const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'dist/deshi-dojo-arcade.html'),'utf8');
(async()=>{let browser;try{
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']});
 const context=await browser.newContext({offline:true});const page=await context.newPage();
 await page.goto('about:blank?capture=1');await page.setContent(html);
 const result=await page.evaluate(()=>{
  fengari.load('G.startFight();G.intro=0')();const times=[];
  for(let n=0;n<1200;n++){
   if(n%150===0)fengari.load('G.startFight();G.intro=0')();
   const start=performance.now();dojoHost.update();times.push(performance.now()-start);
  }
  times.sort((a,b)=>a-b);
  return {frames:times.length,mean_ms:times.reduce((a,b)=>a+b,0)/times.length,p95_ms:times[Math.floor(times.length*.95)],p99_ms:times[Math.floor(times.length*.99)],max_ms:times.at(-1),over_16_67_ms:times.filter(t=>t>1000/60).length};
 });
 // Real RAF and keyboard startup, with wall-time and logical ticks measured independently.
 await page.goto('about:blank');await page.setContent(html);await page.locator('#play').click();
 await page.keyboard.press('z',{delay:120});await page.keyboard.press('f',{delay:120});
 await page.waitForFunction(()=>{const s=dojoHost.snapshot().split('|');return s[0]==='fight'&&s[6]==='0'});
 const cadence=await page.evaluate(()=>new Promise(resolve=>{
  const start=performance.now(),frame=+dojoHost.snapshot().split('|')[9];let callbacks=0;
  const sample=()=>{callbacks++;if(performance.now()-start>=2000)resolve({wall_ms:performance.now()-start,logical_ticks:+dojoHost.snapshot().split('|')[9]-frame,raf_callbacks:callbacks});else requestAnimationFrame(sample)};requestAnimationFrame(sample);
 }));
 const output={platform:'Chromium headless offline, Linux cloud; not ARM, desktop-only',update:result,cadence};
 fs.writeFileSync(path.join(root,'docs/browser-performance-results.json'),JSON.stringify(output,null,2)+'\n');console.log(JSON.stringify(output,null,2));
 }catch(e){console.error(e);process.exitCode=1}finally{if(browser)await browser.close()}})();
