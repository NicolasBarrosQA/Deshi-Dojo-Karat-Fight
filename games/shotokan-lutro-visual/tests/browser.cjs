// Offline browser runs the same Lua; use real keyboard events and inspect pixels.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'dist/deshi-dojo-visual.html'),'utf8');
(async()=>{let browser;try{
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']});
 const context=await browser.newContext({offline:true,viewport:{width:1200,height:1300}}),page=await context.newPage(),errors=[],requests=[],checks=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 await page.goto('about:blank?capture=1');await page.setContent(html,{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>document.body.dataset.ready==='true');
 const step=async n=>page.evaluate(n=>{for(let i=0;i<n;i++)dojoHost.update();dojoHost.render()},n);
 const state=async()=> (await page.evaluate(()=>dojoHost.snapshot())).split('|').map(Number);
 const reset=async near=>{await page.evaluate(near=>{dojoHost.clear();run('Scene.reset();Scene.demo=false'+(near?';Scene.players[1].x=150;Scene.players[2].x=217':''))},near);await step(2)};
 let data=await page.evaluate(()=>document.getElementById('game').toDataURL());
 fs.writeFileSync(path.join(root,'docs/scene-browser.png'),Buffer.from(data.split(',')[1],'base64'));
 let before=await state();await page.keyboard.down('ArrowRight');await page.keyboard.down('j');await step(20);
 await page.keyboard.up('ArrowRight');await page.keyboard.up('j');let after=await state();
 if(!(after[1]>before[1]&&after[2]<before[2]))throw Error('Both ports failed movement');
 checks.push('Both players move with real keyboard events');
 const cases=[['ArrowUp','x',13,15],['ArrowDown','x',16,18],['ArrowRight','x',19,21],['ArrowLeft','x',22,24],['i','g',13,15],['k','g',16,18],['j','g',19,21],['l','g',22,24]];
 for(let n=0;n<cases.length;n++){
  await reset(false);const [direction,key,first,last]=cases[n],side=n<4?0:1;
  await page.keyboard.down(direction);await page.keyboard.down(key);await step(2);
  if((await state())[3+side]!==first)throw Error('Wrong defence preparation '+cases[n]);
  await step(12);if((await state())[3+side]!==last)throw Error('Wrong defence completion '+cases[n]);
  await page.keyboard.up(direction);await page.keyboard.up(key);await step(10);
 }
 checks.push('Four directional blocks on both players, forward/back relative to opponent');
 for(const [key,side,first] of [['z',0,6],['f',1,6],['a',0,25],['h',1,25]]){
  await reset(true);await page.keyboard.down(key);await step(2);
  if((await state())[3+side]!==first)throw Error('Wrong punch/kick '+key);
  await step(65);const s=await state();
  if(s[5+side]!==1||s[7+side]!==1)throw Error('Contact or held-key repeat failed '+s);
  await page.keyboard.up(key);await step(2);
 }
 checks.push('Punch and kick on both ports: contact and no repeat on held button');
 await reset(true);await page.keyboard.down('g');await page.keyboard.down('i');await step(20);
 await page.keyboard.down('ArrowUp');await page.keyboard.down('z');await step(2);
 await page.keyboard.up('z');await page.keyboard.up('ArrowUp');await step(40);
 let s=await state();if(s[5]!==0||s[12]!==1)throw Error('Age failed high coverage: '+s);
 await page.keyboard.up('i');await page.keyboard.up('g');
 checks.push('Age-uke stops high punch');
 await reset(true);await page.keyboard.down('g');await page.keyboard.down('i');await step(20);
 await page.keyboard.down('a');await step(2);await page.keyboard.up('a');await step(50);
 s=await state();if(s[5]!==1||s[12]!==0)throw Error('High block incorrectly stopped mid kick: '+s);
 await page.keyboard.up('i');await page.keyboard.up('g');checks.push('High block leaves middle kick exposed');
 await page.locator('#technique').selectOption('mawashi');await page.locator('#lesson').click();await step(35);
 if((await state())[10]!==1)throw Error('Lesson failed');
 if(!(await page.locator('#tech-foundation').textContent()).includes('quadril'))throw Error('Technique explanation missing');
 await page.locator('#pause').click();let tick=(await state())[0];await page.locator('#step').click();if((await state())[0]!==tick+1)throw Error('Single frame failed');
 await page.locator('#slow').click();await page.locator('#boxes').click();await page.locator('#play').click();
 if((await state())[10]!==0)throw Error('Play did not leave lesson');await page.locator('#reset').click();
 checks.push('Technique selection/explanation, slow mode, pause, single frame, play/reset/debug');
 // Actual RAF, not just manually stepped capture mode.
 await page.goto('about:blank');await page.setContent(html,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>document.body.dataset.ready==='true');
 await page.locator('#play').click();before=await state();await page.keyboard.down('ArrowRight');await page.keyboard.down('j');await page.waitForTimeout(240);
 await page.keyboard.up('ArrowRight');await page.keyboard.up('j');after=await state();
 if(!(after[1]>before[1]&&after[2]<before[2]))throw Error('Live RAF keyboard failed');
 checks.push('Live RAF keyboard control');await page.screenshot({path:path.join(root,'docs/notebook.png'),fullPage:true});
 if(errors.length||requests.length)throw Error(JSON.stringify({errors,requests}));
 const result={passed:checks.length,checks,external_requests:requests,errors,platform:'Chromium offline/Linux x86-64; not Pi/GPIO'};
 fs.writeFileSync(path.join(root,'docs/browser-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
 }catch(e){console.error(e);process.exitCode=1}finally{if(browser)await browser.close()}})();
