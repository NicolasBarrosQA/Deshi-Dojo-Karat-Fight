// Use UI choices and real keyboard events for all CPU levels, menu and human2.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'dist/deshi-dojo-visual.html'),'utf8');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});try{
 const page=await browser.newPage({offline:true,viewport:{width:1200,height:1080}}),errors=[],requests=[],checks=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 await page.goto('about:blank?capture=1');await page.setContent(html,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>document.body.dataset.ready==='true');
 const step=async n=>page.evaluate(n=>{for(let i=0;i<n;i++)dojoHost.update();dojoHost.render()},n);
 const state=async()=> (await page.evaluate(()=>dojoHost.snapshot())).split('|').map(Number);
 const match=async()=> (await page.evaluate(()=>dojoHost.matchInfo())).split('|');
 const press=async(key,n=2)=>{await page.keyboard.down(key);await step(n);await page.keyboard.up(key);await step(2)};
 assert.deepEqual((await match()).slice(0,2),['cpu','easy']);assert.equal(await page.locator('#difficulty').inputValue(),'easy');
 assert(!(await page.locator('.pad[data-port="2"]').isVisible()));assert((await page.locator('#cpu-belt').textContent()).includes('vermelha'));
 await step(400);assert((await state())[7+1]>0,'Default CPU must approach and hit without any P2 input');
 checks.push('Default solo/easy/red profile attacks autonomously; CPU labels visible, P2 keyboard instructions hidden');
 for(const [level,belt] of [['easy','vermelha'],['medium','laranja'],['hard','preta']]){
  await page.locator('#difficulty').selectOption(level);assert.deepEqual((await match()).slice(0,2),['cpu',level]);
  assert((await page.locator('#cpu-belt').textContent()).includes(belt));await step(2);
  const before=(await state())[1];await page.keyboard.down('ArrowRight');await step(12);await page.keyboard.up('ArrowRight');assert((await state())[1]>before);
  await press('z');await step(12);assert((await state())[21]>0);await step(120);assert((await state())[2]<280);
 }
 checks.push('Three difficulty choices reset into the matching colored rank; P1 still moves and attacks');
 // Preserve selected profile across training, lessons, reset, rounds and rematch.
 await page.locator('#practice').click();await step(900);let s=await state();assert.equal(s[25],100);assert.equal(s[26],100);assert.equal(s[27],3600);assert.equal((await match())[1],'hard');
 await page.locator('#study summary').click();await page.locator('#technique').selectOption('mawashi');await page.locator('#lesson').click();await step(42);
 assert.equal((await match())[3],'1');assert(await page.locator('.pad[data-port="2"]').isVisible());
 await page.locator('#play').click();assert.deepEqual((await match()).slice(0,2),['cpu','hard']);await step(80);assert.equal((await match())[3],'0');
 await press('Enter');assert.equal((await state())[25],100);assert.deepEqual((await match()).slice(0,2),['cpu','hard']);
 checks.push('Selected hard profile persists through infinite training, isolated lesson, return to fight and Enter rematch');
 // Open the same native controller menu using Select via F2; no mouse needed.
 await press('F2');assert.equal((await match())[2],'1');let timer=(await state())[27];await page.keyboard.down('ArrowDown');await step(20);await page.keyboard.up('ArrowDown');assert.equal((await state())[27],timer);
 await press('z');assert.equal((await match())[0],'versus');assert(await page.locator('.pad[data-port="2"]').isVisible());assert(!(await page.locator('#cpu-belt').isVisible()));assert(await page.locator('#difficulty').isDisabled());
 let before=(await state())[2];await page.keyboard.down('j');await step(12);await page.keyboard.up('j');assert((await state())[2]<before);assert.equal((await state())[22],0);
 await press('F2');await press('ArrowDown');await press('a');assert.deepEqual((await match()).slice(0,2),['cpu','easy']);
 checks.push('F2/controller menu freezes fight, held direction changes once, punch chooses 2P, P2 restored; kick chooses solo again');
 await page.locator('#mode').selectOption('versus');assert.equal((await match())[0],'versus');await page.locator('#mode').selectOption('cpu');assert.equal((await match())[0],'cpu');
 await page.locator('#difficulty').selectOption('hard');await step(150);await page.screenshot({path:path.join(root,'docs/cpu-notebook.png'),fullPage:true});
 checks.push('Mouse mode switch preserves two-player option; hard CPU HUD screenshot');
 // The exact user exploit: establish first-hit initiative at distance88, then
 // press/release only punch through real DOM keyboard bindings for a whole match.
 for(const level of ['easy','medium','hard']){
  await page.locator('#difficulty').selectOption(level);await page.locator('#play').click();
  await page.evaluate(()=>run('Scene.players[1].x=140;Scene.players[2].x=228;'));
  let winner=0,received=0,previous=0;
  for(let cycle=0;cycle<750;cycle++){
   await page.keyboard.down('z');await step(2);await page.keyboard.up('z');await step(2);
   const s=await state();received+=Math.max(0,s[6]-previous);previous=s[6];winner=s[31];if(winner)break;
  }
  assert(winner,'Punch-only match should finish');if(level!=='easy')assert(received>0,'CPU must be able to answer pressure');
  if(level==='hard')assert.equal(winner,2,'Fast punch-only exploit must be punished by hard CPU');
 }
 checks.push('Punch-only complete matches through keyboard at all three levels: medium/hard answer; hard wins with same energy/damage rules');
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
 const result={passed:checks.length,checks,artifact_sha256:crypto.createHash('sha256').update(html).digest('hex'),errors,external_requests:requests,scope:'Offline Chromium real UI/keyboard; physical controls/Pi and player-rated difficulty pending'};
 fs.writeFileSync(path.join(root,'docs/cpu-browser-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
 }finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
