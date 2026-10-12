// Real browser, offline, UI selection, contact events and transition coverage.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..');
(async()=>{const browser=await chromium.launch({executablePath:process.env.DOJO_CHROMIUM||(process.platform==='win32'?'C:/Program Files/Google/Chrome/Application/chrome.exe':'/usr/bin/chromium'),headless:true});try{
 const page=await browser.newPage({offline:true,viewport:{width:1180,height:1100}}),errors=[],requests=[],checks=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 await require('./offline_page.cjs')(page);
 await page.waitForFunction(()=>document.body.dataset.ready==='true').catch(async e=>{console.error(errors,await page.locator('#status').textContent());throw e});
 const step=async n=>page.evaluate(n=>{for(let i=0;i<n;i++)dojoHost.update();dojoHost.render()},n);
 await page.locator('#mode').selectOption('versus');
 for(const body of ['adult','teen','child']){
  await page.locator('#p1-body').selectOption(body);await page.waitForFunction(()=>!document.getElementById('p1-body').disabled);
  await page.evaluate(()=>run('for n=1,92 do Scene.players[1].pose=n;lutro.draw() end'));
  for(const belt of ['branca','amarela','vermelha','laranja','verde','roxa','marrom','preta']){
   await page.locator('#p1-belt').selectOption(belt);await page.waitForFunction(()=>!document.getElementById('p1-belt').disabled);
   assert.equal((await page.evaluate(()=>dojoHost.characterInfo())).split('|')[1],belt);
  }
 }
 await page.locator('#p1-body').selectOption('child');await page.waitForFunction(()=>!document.getElementById('p1-body').disabled);
 await page.locator('#p2-body').selectOption('teen');await page.waitForFunction(()=>!document.getElementById('p2-body').disabled);
 await page.locator('#p1-belt').selectOption('branca');await page.waitForFunction(()=>!document.getElementById('p1-belt').disabled);
 await page.locator('#p2-belt').selectOption('verde');await page.waitForFunction(()=>!document.getElementById('p2-belt').disabled);
 await page.evaluate(()=>run('Scene.reset(true)'));await step(2);
 assert.equal(await page.evaluate(()=>dojoHost.characterInfo()),'child|branca|teen|verde');
 await page.locator('#mode').selectOption('cpu');await page.locator('#difficulty').selectOption('hard');
 assert.equal(await page.evaluate(()=>dojoHost.characterInfo()),'child|branca|teen|verde');
 checks.push('All body/belt selectors, all 92 draw poses, independent CPU difficulty and appearance survives reset');
 await page.locator('#mode').selectOption('versus');
 await page.keyboard.down('ArrowRight');await page.keyboard.down('j');await step(200);
 const values=(await page.evaluate(()=>dojoHost.snapshot())).split('|').map(Number);
 assert(Math.abs(values[2]-values[1])>=87.999);
 await page.keyboard.up('ArrowRight');await page.keyboard.up('j');
 checks.push('Child vs teenager retain shared collision barrier for 200 movement ticks');
 const guardCount=await page.evaluate(()=>run(`
 local s=require('techniques').techniques;local count=0
 for _,side in ipairs({1,2}) do
  local p=Scene.players[side];p.stun=0;p.air=false
  for _,old in ipairs({'kamae','age','gedan','soto','uchi'}) do
   for _,new in ipairs({'kamae','age','gedan','soto','uchi'}) do
    for _,zone in ipairs({'jodan','chudan','gedan'}) do
     local covers=function(id) return id=='kamae' and (zone=='jodan' or zone=='chudan') or s[id].zone==zone end
     p.coverage=old;p.action={id=new,age=s[new].windup}
     local blocked,parry,id=Scene.defended(p,zone)
     assert(blocked==covers(old));assert(not parry);assert(id==(blocked and old or nil))
     p.action.age=s[new].windup+1
     blocked,parry,id=Scene.defended(p,zone)
     assert(blocked==covers(new));assert(id==(blocked and new or nil));assert(parry==(blocked and new~='kamae'))
     count=count+1
    end
   end
  end
 end
 return count
 `));assert.equal(guardCount,150);
 checks.push('150 transition/zone/player cases: old coverage retained, new coverage/parry only after preparation');
 await page.evaluate(()=>{dojoHost.clear();run('Scene.reset(true);Scene.players[1].x=140;Scene.players[2].x=228;')});
 await page.keyboard.down('g');await step(12);await page.keyboard.down('ArrowUp');await page.keyboard.down('z');await step(2);await page.keyboard.up('z');await page.keyboard.up('ArrowUp');await step(35);await page.keyboard.up('g');
 const contact=await page.evaluate(()=>run('local e=Scene.lastContact;assert(e and e.blocked and e.defense=="kamae");assert(Scene.players[2].energy==100);return e.defense'));
 assert.equal(contact,'kamae');checks.push('Real keyboard high punch blocked by neutral guard; no energy loss; event identifies kamae');
 const transitionContacts=await page.evaluate(()=>run(`
 local tech=require('techniques').techniques;local count=0
 for _,targetIndex in ipairs({1,2}) do
  Scene.reset(true);local attackerIndex=3-targetIndex
  local target,attacker=Scene.players[targetIndex],Scene.players[attackerIndex]
  Scene.players[1].x=140;Scene.players[2].x=228
  target.action={id='kamae',age=20};target.coverage=nil
  attacker.action={id='jodan',age=tech.jodan.windup,spent=false,counter=false,link=1,step=0}
  local read=lutro.joystick.isDown
  lutro.joystick.isDown=function(port,key) return port==targetIndex and (key==2 or key==6) end
  Scene.advance();lutro.joystick.isDown=read
  local e=Scene.lastContact
  assert(target.action.id=='gedan' and target.action.age==1)
  assert(e and e.blocked and e.defense=='kamae' and not e.parry)
  assert(target.energy==100);count=count+1
 end
 return count
 `));assert.equal(transitionContacts,2);checks.push('Both facings: actual contact during kamae-to-gedan startup records kamae, blocks high strike, no early parry');
 const nativeCache=await page.evaluate(()=>run(`
 local C=require('characters');local g=lutro.graphics;local saved=g.newImage
 local overrides={C.definition(1),C.definition(2)};local loaded=0
 g.newImage=function(path) loaded=loaded+1 return {path=path} end
 lutro.browser=false;C.cache={};C.retained={};C.retainedBytes=0
 for pass=1,2 do
  for _,body in ipairs(C.data.body_order) do
   for _,belt in ipairs(C.data.belt_order) do C.select(1,{body=body,belt=belt}) end
  end
  if pass==1 then Scene.firstLoads=loaded else assert(loaded==Scene.firstLoads) end
 end
 assert(C.retainedBytes<C.nativeBudget)
 local bytes=C.retainedBytes
 C.overrides=overrides;C.cache={};C.retained={};C.retainedBytes=0;lutro.browser=true;g.newImage=saved;C.prepare()
 return bytes
 `));checks.push('Historical cache logic: revisiting all bases/belts allocates zero extra images; bounded bytes='+nativeCache);
 await page.evaluate(()=>run('Scene.reset(true)'));await step(2);await page.screenshot({path:path.join(root,'docs/personalization-browser.png'),fullPage:true});
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
 const active=await page.evaluate(()=>Object.keys(images).filter(x=>x.startsWith('char-')));
 assert(active.length<=20,active.join(','));checks.push('Offline with zero network requests/errors; at most two selected characters decoded');
 fs.writeFileSync(path.join(root,'docs/personalization-browser-results.json'),JSON.stringify({checks,guard_transition_cases:guardCount,transition_contacts:transitionContacts,native_cache_simulation_bytes:nativeCache,native_core_executed:false,errors,requests,active_assets:active.length},null,2)+'\n');console.log(checks.join('\n'));
 }finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
