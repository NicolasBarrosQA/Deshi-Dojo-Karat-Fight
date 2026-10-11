// Uses the available development browser only; the delivered game has no dependencies.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'dist/deshi-dojo-arcade.html'),'utf8');
(async()=>{let browser;try{
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'],timeout:10000});
 const context=await browser.newContext({offline:true,viewport:{width:1100,height:1000}});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('about:blank?selftest=1');
 await page.setContent(html,{waitUntil:'domcontentloaded',timeout:10000});
 const status=await page.locator('#status').innerText();console.log(status);
 if(await page.locator('body').getAttribute('data-test')!=='passed')throw Error(status);
 await page.screenshot({path:path.join(root,'docs/browser-contact.png')});
 await page.goto('about:blank?capture=1');await page.setContent(html,{waitUntil:'domcontentloaded'});
 const canvas=await page.evaluate(()=>document.getElementById('game').toDataURL());
 fs.writeFileSync(path.join(root,'docs/browser-title-native-resolution.png'),Buffer.from(canvas.split(',')[1],'base64'));
 await page.goto('about:blank');await page.setContent(html,{waitUntil:'domcontentloaded'});
 await page.locator('#play').click();await page.keyboard.press('z',{delay:100});await page.keyboard.press('f',{delay:100});await page.waitForTimeout(40);
 await page.waitForFunction(()=>{const s=dojoHost.snapshot().split('|');return s[0]==='fight'&&s[6]==='0'},{timeout:3000});
 let before=(await page.evaluate(()=>dojoHost.snapshot())).split('|');if(before[0]!=='fight')throw Error('Keyboard confirmation failed');
 await page.keyboard.down('ArrowRight');await page.keyboard.down('j');await page.waitForTimeout(220);await page.keyboard.up('ArrowRight');await page.keyboard.up('j');
 let after=(await page.evaluate(()=>dojoHost.snapshot())).split('|');
 if(!(+after[1]>+before[1]&&+after[2]<+before[2]))throw Error('Independent movement failed');
 await page.locator('#diagnostic').click();await page.waitForTimeout(40);if((await page.evaluate(()=>dojoHost.snapshot())).split('|')[0]!=='diagnostic')throw Error('Diagnostic menu failed');
 // User gesture unlocks WebAudio; actual command emits and plays an original envelope.
 const audio=await page.evaluate(()=>dojoHost.audioStatus());if(audio.state!=='running'||audio.played<1)throw Error('WebAudio did not run');
 await page.locator('#audio').click();if(!(await page.evaluate(()=>dojoHost.audioStatus())).muted)throw Error('Mute failed');
 await page.locator('#audio').click();
 // Freeze the RAF only in the existing capture test mode, then drive actual keyboard inputs.
 await page.goto('about:blank?capture=1');await page.setContent(html,{waitUntil:'domcontentloaded'});
 for(const side of [0,1])for(const [index,key] of ['z','x','a','s'].entries()){
  const actual=side===0?key:['f','g','r','t'][index];
  await page.evaluate(()=>fengari.load('G.startFight();G.intro=0;G.p[1].x=100;G.p[2].x=140')());
  if(index<2)await page.evaluate(()=>fengari.load('G.p[2].x=132')());
  await page.keyboard.down(actual);await page.evaluate(()=>dojoHost.update());await page.keyboard.up(actual);
  const ticks=[9,7,13,16][index];await page.evaluate(n=>{for(let i=0;i<n;i++)dojoHost.update()},ticks);
  const result=(await page.evaluate(()=>dojoHost.snapshot())).split('|');
  if(+result[3+side]!==([1,1,2,2][index]))throw Error('Technique/port failed '+side+'/'+index+' '+result);
 }
 await page.locator('#title').click();await page.waitForTimeout(40);if((await page.evaluate(()=>dojoHost.snapshot())).split('|')[0]!=='title')throw Error('Title menu failed');
 if(errors.length)throw Error(errors.join('\n'));
 console.log('PASS browser offline: raster art, selection, 2-player keyboard, all four techniques on both ports, collision/scoring, audio/mute, menus and no JS/Lua errors');
 }catch(e){console.error(e.message);process.exitCode=1}finally{if(browser)await browser.close()}})();
