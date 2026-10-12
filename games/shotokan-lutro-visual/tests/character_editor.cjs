const {chromium}=require('playwright'),assert=require('assert/strict'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),url=process.env.DOJO_EDITOR_URL;
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:1050}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(url+'/editor');await page.waitForFunction(()=>document.body.dataset.ready==='true');
  await page.locator('#new').click();await page.locator('#id').fill('editor-qa');await page.locator('#name').fill('EDITOR QA');
  await page.locator('#body').selectOption('child');await page.locator('#skin').selectOption('clara');await page.locator('#hair_color').selectOption('loiro');await page.locator('#belt').selectOption('roxa');await page.locator('#height').selectOption('0.94');await page.locator('#build').selectOption('forte');
  await page.locator('#save').click();await page.waitForFunction(()=>document.getElementById('status').textContent.startsWith('Salvo e exportado:'),{},{timeout:90000});
  assert.equal(await page.locator('#roster').inputValue(),'editor-qa');
  await page.locator('#technique').selectOption('gyaku');await page.locator('#animate').click();await page.waitForTimeout(400);
  assert.notEqual(await page.locator('#pose').inputValue(),'1');await page.locator('#stop').click();
  await page.locator('#pose').fill('63');await page.locator('#pose').dispatchEvent('input');
  await page.screenshot({path:path.join(root,'docs/character-editor.png'),fullPage:true});
  const downloadReady=page.waitForEvent('download');await page.locator('#export').click();
  const download=await downloadReady;assert.equal(download.suggestedFilename(),'deshi-dojo-visual.lutro');
  await page.reload();await page.waitForFunction(()=>document.body.dataset.ready==='true');await page.locator('#roster').selectOption('editor-qa');await page.waitForFunction(()=>document.getElementById('name').value==='EDITOR QA');
  assert.equal(await page.locator('#skin').inputValue(),'clara');assert.equal(await page.locator('#belt').inputValue(),'roxa');
  const game=await browser.newPage({viewport:{width:1200,height:1100}});game.on('pageerror',e=>errors.push(String(e)));
  await game.goto(url+'/?capture=1&student=editor-qa');await game.waitForFunction(()=>document.body.dataset.ready==='true');
  assert.equal(await game.locator('#p1-student').inputValue(),'editor-qa');
  await game.locator('#mode').selectOption('versus');
  await game.locator('#p1-student').selectOption('editor-qa');await game.waitForFunction(()=>!document.getElementById('p1-student').disabled);
  await game.locator('#p2-student').selectOption('demo-adult');await game.waitForFunction(()=>!document.getElementById('p2-student').disabled);
  const step=async n=>game.evaluate(n=>{for(let i=0;i<n;i++)dojoHost.update();dojoHost.render()},n);
  const selected=await game.evaluate(()=>run('local a,b=Scene.players[1].character,Scene.players[2].character;return a.id.."|"..a.body.."|"..a.belt.."|"..b.id'));
  assert.equal(selected,'editor-qa|child|roxa|demo-adult');
  await game.evaluate(()=>run('Scene.players[1].x=140;Scene.players[2].x=228'));
  await game.keyboard.down('z');await step(3);await game.keyboard.up('z');await step(25);
  assert(Number(await game.evaluate(()=>run('return Scene.players[1].contacts')))>0);
  await game.evaluate(()=>{run('for n=1,92 do Scene.players[1].pose=n;lutro.draw() end;Scene.players[1].pose=39');dojoHost.render()});
  await game.locator('#game').screenshot({path:path.join(root,'docs/character-creator-combat.png')});
  await game.locator('#mode').selectOption('cpu');await game.locator('#difficulty').selectOption('hard');await game.locator('#p2-student').selectOption('demo-teen');await game.waitForFunction(()=>!document.getElementById('p2-student').disabled);await step(160);
  assert.equal(await game.locator('#difficulty').inputValue(),'hard');assert.equal(await game.evaluate(()=>run('return Scene.players[2].character.id')),'demo-teen');
  assert(Number(await game.evaluate(()=>run('return Scene.players[2].executed')))>0);
  const cache=await game.evaluate(()=>run(`local C=require('characters');local expected={}
   local function part(p)for _,side in ipairs({'right','left'})do expected[p[side]]=p.decoded_bytes/2 end end
   for port=1,2 do local d=C.definition(port);local b=C.data.bodies[d.body];local p=d.visual and C.data.visual_profiles[d.visual]
    if p then part(p.parts.body);part(p.parts.belt[d.belt]);expected[p.portrait]=p.portrait_bytes or 5120
    else for _,layer in ipairs({'body','belt','face','hair','foreground'})do local v=layer=='belt' and d.belt or layer=='face' and d.face or layer=='hair' and d.hair or 'default';part(b.parts[layer][v])end end
    for _,a in pairs(d.visual and C.data.special_profiles[d.visual] or C.data.specials[d.body])do part(a.body);part(a.belts[d.belt])end
   end
   local n=0;local bytes=0;for name in pairs(C.cache)do assert(expected[name],'Unselected image retained: '..name);n=n+1;bytes=bytes+expected[name]end
   local count=0;for name in pairs(expected)do assert(C.cache[name],'Missing selected image: '..name);count=count+1 end
   assert(n==count and bytes<C.nativeBudget);return n`));
  const retained=await game.evaluate(()=>run(`
   local C=require('characters');local g=lutro.graphics;local saved=g.newImage;local loads=0
   local selected={C.selected[1],C.selected[2]};local overrides=C.overrides
   g.newImage=function(path) loads=loads+1 return {path=path} end
   lutro.browser=false C.cache={} C.retained={} C.retainedBytes=0
   for pass=1,2 do
    for _,id in ipairs(C.data.student_order) do C.student(1,id) end
    if pass==1 then Scene.appearanceLoads=loads else assert(loads==Scene.appearanceLoads) end
   end
   assert(C.retainedBytes<C.nativeBudget);local bytes=C.retainedBytes
   C.selected=selected C.overrides=overrides C.cache={} C.retained={} C.retainedBytes=0
   lutro.browser=true g.newImage=saved C.prepare();return bytes
  `));
  assert(Number(retained)<128*1048576,'Retained character images exceed the native 128 MiB budget: '+retained);
  await game.keyboard.down('F2');await step(2);await game.keyboard.up('F2');await step(2);
  for(let i=0;i<4;i++){await game.keyboard.down('ArrowDown');await step(2);await game.keyboard.up('ArrowDown');await step(2)}
  assert.equal(Number(await game.evaluate(()=>run('return Scene.menuChoice'))),7);
  await game.keyboard.down('z');await step(2);await game.keyboard.up('z');await step(2);
  assert.equal(await game.evaluate(()=>run('return Scene.players[1].character.id')),'demo-adult');
  await game.locator('#game').screenshot({path:path.join(root,'docs/character-selection-menu.png')});
  const offline=await browser.newPage({offline:true});await require('./offline_page.cjs')(offline,true,process.env.DOJO_EDITOR_DIST);await offline.waitForFunction(()=>document.body.dataset.ready==='true');
  assert.equal(await offline.locator('#p1-student option[value="editor-qa"]').count(),1);
  assert.deepEqual(errors,[]);console.log('PASS editor UI persistence, all 92 customized poses, child/adult keyboard contact, independent CPU, F2 roster, selective cache='+cache+', retained appearance bytes='+retained+', offline roster');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
