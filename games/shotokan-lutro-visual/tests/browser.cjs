// Offline keyboard/gamepad controls and actual fight loop; no action injection.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'dist/deshi-dojo-visual.html'),'utf8');
const docs=path.resolve(root,process.env.DOJO_TEST_OUTPUT||'docs');fs.mkdirSync(docs,{recursive:true});
(async()=>{let browser;try{
 browser=await chromium.launch({executablePath:process.env.DOJO_CHROMIUM||(process.platform==='win32'?'C:/Program Files/Google/Chrome/Application/chrome.exe':'/usr/bin/chromium'),headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']});
 const context=await browser.newContext({offline:true,viewport:{width:1200,height:1000}}),page=await context.newPage(),errors=[],requests=[],checks=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 await require('./offline_page.cjs')(page);await page.waitForFunction(()=>document.body.dataset.ready==='true');
 const step=async n=>page.evaluate(n=>{for(let i=0;i<n;i++)dojoHost.update();dojoHost.render()},n);
 const state=async()=> (await page.evaluate(()=>dojoHost.snapshot())).split('|').map(Number);
 const reset=async(near=false,reverse=false)=>{await page.evaluate(({near,reverse})=>{dojoHost.clear();run('Scene.demo=false;Scene.practice=false;Scene.configure(\"versus\",\"easy\",true);'+(near?'Scene.players[1].x=140;Scene.players[2].x=228;':'')+(reverse?'local x=Scene.players[1].x;Scene.players[1].x=Scene.players[2].x;Scene.players[2].x=x;Scene.left=2;':''))},{near,reverse});await step(2)};
 const press=async(key,n=2)=>{await page.keyboard.down(key);await step(n);await page.keyboard.up(key)};
 const invariant=(s,reverse=false)=>{assert(s[1]>=64&&s[2]<=320&&Math.abs(s[2]-s[1])>=87.999,String(s));assert.equal(s[2]>s[1],!reverse)};
 assert.equal(await page.locator('#study').getAttribute('open'),null);
 assert(await page.locator('#practice').isVisible());assert((await page.locator('.quick').textContent()).includes('soco'));
 checks.push('Fight/three-action controls first; detailed lessons collapsed by default');
 let data=await page.evaluate(()=>document.getElementById('game').toDataURL());fs.writeFileSync(path.join(docs,'scene-browser.png'),Buffer.from(data.split(',')[1],'base64'));
 for(const reverse of [false,true]){
  await reset(false,reverse);const inward=reverse?['ArrowLeft','l']:['ArrowRight','j'];
  const before=await state();for(const key of inward)await page.keyboard.down(key);
  await step(15);let s=await state();assert(s[1]!==before[1]&&s[2]!==before[2]);
  for(let n=0;n<140;n++){await step(1);invariant(await state(),reverse)}
  for(const key of inward)await page.keyboard.up(key);
 }
 checks.push('Both keyboard ports move independently; 280 per-frame barrier/order checks from both sides');
 for(const [direction,key,first,last] of [['ArrowUp','x',13,15],['ArrowDown','x',16,18],['ArrowRight','x',19,21],['ArrowLeft','x',22,24],['i','g',13,15],['k','g',16,18],['j','g',19,21],['l','g',22,24]]){
  await reset();const side=key==='x'?0:1;await page.keyboard.down(direction);await page.keyboard.down(key);await step(2);
  assert.equal((await state())[3+side],first);await step(10);assert.equal((await state())[3+side],last);
  await page.keyboard.up(direction);await page.keyboard.up(key);
 }
 checks.push('Four directional uke on both players; commands relative to opponent');
 for(const [key,side,first] of [['z',0,45],['f',1,45],['a',0,25],['h',1,25]]){
  await reset(true);await page.keyboard.down(key);await step(2);assert.equal((await state())[3+side],first);
  assert(await page.locator(`.pad[data-port="${side+1}"] [data-key="${first===45?1:9}"]`).evaluate(e=>e.classList.contains('pressed')));
  await step(70);const s=await state();assert.equal(s[7+side],1);assert.equal(s[21+side],1);
  await page.keyboard.up(key);
 }
 checks.push('Punch/kick both ports: immediate startup, button indicators, single contact when held');
 await reset(true);await page.keyboard.down('g');await page.keyboard.down('i');await step(8);
 await page.keyboard.down('ArrowUp');await press('z');await page.keyboard.up('ArrowUp');await step(28);
 assert.equal((await state())[5],0);assert.equal((await state())[12],1);
 await page.keyboard.up('i');await page.keyboard.up('g');
 await reset(true);await page.keyboard.down('g');await page.keyboard.down('i');await step(8);await press('a');await step(28);
 assert.equal((await state())[5],1);assert.equal((await state())[12],0);await page.keyboard.up('g');await page.keyboard.up('i');
 checks.push('High coverage stops high punch; leaves middle kick vulnerable');
 for(const side of [0,1])for(const reverse of [false,true]){
  await reset(true,reverse);const punch=side?'f':'z',kick=side?'h':'a';
  await press(punch);await step(1);await press(punch);
  for(let n=0;(await state())[21+side]<2;n++){assert(n<25,'Second punch lost');await step(1)}
  await step(1);await page.keyboard.down(kick);await step(2);
  let best=0;for(let n=0;n<32;n++){await step(1);const s=await state();invariant(s,reverse);best=Math.max(best,s[32+side])}
  let s=await state();assert.equal(s[21+side],3);assert.equal(s[7+side],3);assert.equal(best,3);assert.equal(s[26-side],70);
  await step(35);assert.equal((await state())[21+side],3);await page.keyboard.up(kick);
 }
 checks.push('Soco > soco > chute through real keyboard: both ports/facings, early buffer, three actual hits and no held repeat');
 for(const side of [0,1])for(const reverse of [false,true]){
  const punch=side?'f':'z',guard=side?'g':'x',high=side?'i':'ArrowUp';
  await reset(false,reverse);await press(punch);await step(1);await press(punch);
  await page.keyboard.down(guard);await page.keyboard.down(high);await step(35);
  let s=await state();assert.equal(s[21+side],1,'New defense must replace stale buffered punch');assert.equal(s[3+side],15);
  assert((await page.evaluate(()=>dojoHost.view())).includes('GUARDA ALTA'));
  await page.keyboard.up(guard);await page.keyboard.up(high);
  await reset(false,reverse);
  const face=(side===0)!==reverse?1:-1;
  await page.evaluate(({side,face})=>run(`Scene.players[${side+1}].x=${face===1?64:320};Scene.players[${2-side}].x=${face===1?152:232};`),{side,face});
  const foe=side?'z':'f';
  for(let n=0;n<110;n++){
   if(n%2===0)await page.keyboard.down(foe);else await page.keyboard.up(foe);
   if(n===6)await page.keyboard.down(punch);if(n===8){await page.keyboard.up(punch);await page.keyboard.down(guard)}
   await step(1);
  }
  s=await state();assert.equal(s[21+side],0);assert(s[11+side]>0);assert.equal(s[25+side],78);
  await page.keyboard.up(guard);await page.keyboard.up(foe);
 }
 checks.push('Fresh guard clears queued punches during preparation/stun on both keyboards/facings; visible coverage and fourth punch blocked at either wall');
 for(const [up,punch,kick,side] of [['ArrowUp','z','a',0],['i','f','h',1]]){
  await reset();await page.keyboard.down(up);await step(12);assert((await state())[15+side]>20);
  await press(punch);await step(1);await press(kick);await step(65);const s=await state();
  assert.equal(s[15+side],0);assert.equal(s[17+side],0);assert.equal(s[23+side],1);assert.equal(s[21+side],1);
  await page.keyboard.up(up);
 }
 checks.push('Jump, airborne punch, one attack per jump and safe landing on both keyboards');
 for(const [dir,key,first] of [['ArrowLeft','z',6],['ArrowRight','z',6],['ArrowDown','z',89],['ArrowUp','z',41],['ArrowRight','a',33],['ArrowDown','a',29]]){
  await reset();await page.keyboard.down(dir);await page.keyboard.down(key);await step(2);assert.equal((await state())[3],first);
  assert.equal((await state())[23],0);await page.keyboard.up(dir);await page.keyboard.up(key);
 }
 checks.push('Ground reverse/advance/low/high punches and circular/low kicks use the revised commands');
 await page.locator('#practice').click();await press('z');await step(28);let s=await state();assert.equal(s[25],100);assert.equal(s[26],100);assert.equal(s[27],3600);
 await page.locator('#play').click();await step(8);assert.equal((await state())[27],3600);await step(420);assert((await state())[27]<3600);assert.equal((await state())[10],0);
 await page.locator('#study summary').click();await page.locator('#technique').selectOption('mawashi');await page.locator('#lesson').click();await step(35);
 assert.equal((await state())[10],1);assert((await page.locator('#tech-foundation').textContent()).includes('quadril'));
 await page.locator('#pause').click();let tick=(await state())[0];await page.locator('#step').click();assert.equal((await state())[0],tick+1);
 await page.locator('#slow').click();await page.locator('#boxes').click();await page.locator('#play').click();assert.equal((await state())[10],0);
 checks.push('Fight vs infinite practice; optional lessons/explanation, slow, pause, single-frame/debug and return to fight');
 await reset(true);await press('z');await step(15);await press('Enter');assert((await state())[0]<=1);assert.equal((await state())[25],100);
 await reset();await page.keyboard.down('ArrowRight');await step(4);await page.evaluate(()=>window.dispatchEvent(new Event('blur')));const blurX=(await state())[1];await step(6);assert.equal((await state())[1],blurX);await page.keyboard.up('ArrowRight');
 checks.push('Enter restarts; focus loss releases cached keyboard inputs');
 // Mock standard Gamepad API with real binding/polling: hardware wiring remains untested.
 await reset();await page.evaluate(()=>{window.testPads=[0,1].map(()=>({axes:[0,0],buttons:Array.from({length:16},()=>({pressed:false}))}));Object.defineProperty(navigator,'getGamepads',{configurable:true,value:()=>window.testPads});testPads[0].axes[0]=1;testPads[1].axes[0]=-1;pollGamepads()});
 let beforePad=await state();await step(12);s=await state();assert(s[1]>beforePad[1]&&s[2]<beforePad[2]);
 await page.evaluate(()=>{for(const p of testPads){p.axes[0]=0;p.buttons[0].pressed=true}pollGamepads()});await step(2);s=await state();assert.equal(s[3],45);assert.equal(s[4],45);
 await page.evaluate(()=>{for(const p of testPads)p.buttons[0].pressed=false;pollGamepads()});
 checks.push('Standard gamepad API mapping mock: two pads, analog movement, both punch buttons (physical pads pending)');
 // Actual RAF response and Escape pause, outside the capture/manual-step loop.
 await require('./offline_page.cjs')(page,false);await page.waitForFunction(()=>document.body.dataset.ready==='true');
 await page.locator('#mode').selectOption('versus');await page.locator('#play').click();await page.waitForFunction(()=>!dojoHost.introActive());let before=await state();await page.keyboard.down('ArrowRight');await page.keyboard.down('j');await page.waitForTimeout(220);
 await page.keyboard.up('ArrowRight');await page.keyboard.up('j');let after=await state();assert(after[1]>before[1]&&after[2]<before[2]);
 await page.keyboard.press('Escape');tick=(await state())[0];await page.waitForTimeout(80);assert.equal((await state())[0],tick);await page.keyboard.press('Escape');await page.waitForTimeout(80);assert((await state())[0]>tick);
 checks.push('Actual RAF movement with keyboard; Escape pauses/resumes');await page.screenshot({path:path.join(docs,'notebook.png'),fullPage:true});
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
 const result={passed:checks.length,checks,artifact_sha256:require('crypto').createHash('sha256').update(html).digest('hex'),external_requests:requests,errors,platform:process.platform+' offline Chromium/Chrome; gamepad API mocked, physical pads/Pi/GPIO pending'};
 fs.writeFileSync(path.join(docs,'browser-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
 }catch(e){console.error(e);process.exitCode=1}finally{if(browser)await browser.close()}})();
