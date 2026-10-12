const {chromium}=require('playwright'),assert=require('assert/strict'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),out=path.join(root,'docs/hair'),url=process.env.DOJO_EDITOR_URL,cases=JSON.parse(process.env.DOJO_HAIR_CASES);
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1400,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(url+'/editor');await page.waitForFunction(()=>document.body.dataset.ready==='true');
  const catalog=await page.evaluate(()=>fetch('/api/characters').then(r=>r.json()).then(r=>r.catalog));
  assert.equal(await page.locator('#hair-cards button').count(),catalog.hair_styles.length);assert.equal(await page.locator('#hair-colors button').count(),14);
  await page.selectOption('#hair-category','masculino');assert.equal(await page.locator('#hair-cards button').count(),1+catalog.hair_styles.filter(e=>e.category==='masculino').length);
  await page.selectOption('#hair-category','feminino');assert.equal(await page.locator('#hair-cards button').count(),1+catalog.hair_styles.filter(e=>e.category==='feminino').length);
  await page.fill('#hair-search','trança');assert(await page.locator('#hair-cards button').count()>1);await page.fill('#hair-search','');await page.selectOption('#hair-category','todos');
  const previews=[];
  for(const body of ['adult','teen','child','adult_female','teen_female','child_female']){
   await page.selectOption('#body',body);
   for(const [hair,color] of [['curto_classico','branco'],['medio_ondulado','preto'],['crespo_curto','ruivo']]){
    await page.locator(`[data-hair="${hair}"]`).click();await page.selectOption('#hair_color',color);
    await page.waitForFunction(({body,hair,color})=>window.editorVisual?.body===body&&window.editorVisual.hair===hair&&window.editorVisual.appearance.hair_color===color,{body,hair,color},{timeout:90000});
    for(const pose of [1,9,15,59,62,63,85]){await page.fill('#pose',String(pose));await page.locator('#pose').dispatchEvent('input');await page.selectOption('#facing','left');await page.selectOption('#facing','right')}
    previews.push({body,hair,color});
   }
  }
  await page.selectOption('#roster',cases[3]);
  await page.evaluate(()=>{document.getElementById('hair-custom').value='#663399';document.getElementById('hair-custom').dispatchEvent(new Event('input',{bubbles:true}))});
  await page.waitForFunction(()=>window.editorVisual?.appearance.hair_color==='#663399',{},{timeout:90000});
  for(const entry of catalog.beard_styles.filter(e=>e.id!=='default')){
   await page.selectOption('#beard',entry.id);await page.selectOption('#beard_color','branco');
   await page.waitForFunction(id=>window.editorVisual?.beard===id&&window.editorVisual.appearance.beard_color==='branco',entry.id,{timeout:90000});
   for(const pose of [1,15,59,62,85]){await page.fill('#pose',String(pose));await page.locator('#pose').dispatchEvent('input');await page.selectOption('#facing','left');await page.selectOption('#facing','right')}
  }
  const lastBeard=catalog.beard_styles.at(-1).id;
  await page.evaluate(()=>{document.getElementById('beard-custom').value='#934521';document.getElementById('beard-custom').dispatchEvent(new Event('input',{bubbles:true}))});
  await page.waitForFunction(()=>window.editorVisual?.appearance.beard_color==='#934521',{},{timeout:90000});
  await page.click('#save');await page.waitForFunction(()=>document.getElementById('status').textContent.startsWith('Salvo e exportado:'),{},{timeout:90000});
  await page.reload();await page.waitForFunction(()=>document.body.dataset.ready==='true');await page.selectOption('#roster',cases[3]);
  await page.waitForFunction(()=>window.editorVisual?.appearance.hair_color==='#663399',{},{timeout:90000});
  assert.equal(await page.inputValue('#hair-custom'),'#663399');assert.equal(await page.inputValue('#hair'),'curto_classico');
  assert.equal(await page.inputValue('#beard'),lastBeard);assert.equal(await page.inputValue('#beard-custom'),'#934521');
  await page.screenshot({path:path.join(out,'editor.png'),fullPage:true});
  const game=await browser.newPage({offline:true});game.on('pageerror',e=>errors.push(String(e)));
  await require('./offline_page.cjs')(game,true,process.env.DOJO_EDITOR_DIST);await game.waitForFunction(()=>document.body.dataset.ready==='true');
  const lua=s=>game.evaluate(s=>run(s),s),step=n=>game.evaluate(n=>{for(let i=0;i<n;i++)dojoHost.update();dojoHost.render()},n);
  for(let i=0;i<cases.length;i++){
   await lua(`Scene.configure('versus','easy');Scene.student(1,'${cases[i]}');Scene.student(2,'${cases[(i+1)%cases.length]}')`);
   await game.evaluate(()=>Promise.all([...assetLoads.values()]));await step(210);
   await lua('assert(Scene.intro.touchGap<=1);assert(Scene.players[1].energy==100 and Scene.players[2].energy==100)');await step(210);
   await game.keyboard.down('ArrowUp');await step(40);await game.keyboard.up('ArrowUp');
   await lua('assert(Scene.players[1].jumps==1 and Scene.players[1].height==0)');
   await lua("assert(require('specials').start(Scene.players[1],'nidan'))");await step(100);
   for(const group of ['ashi_barai','ashi_finish','knockdown','ura_mawashi','ushiro','tai_sabaki','renzoku','nidan','ceremony','hand_touch']){
    for(let frame=1;frame<=9;frame++)await lua(`Scene.players[1].specialPose={group='${group}',frame=${frame}};Scene.players[2].specialPose={group='${group}',frame=${frame}};lutro.draw()`);
   }
   await lua('Scene.players[1].specialPose=nil;Scene.players[2].specialPose=nil');
  }
  const native=await lua(`local C=require('characters');local g=lutro.graphics;local saved=g.newImage;local selected={C.selected[1],C.selected[2]};local overrides=C.overrides
   g.newImage=function(path)return {path=path} end;lutro.browser=false;C.cache={};C.retained={};C.retainedBytes=0
   for _,id in ipairs(C.data.student_order) do C.student(1,id) end
   assert(C.retainedBytes<C.nativeBudget);local bytes=C.retainedBytes
   C.selected=selected;C.overrides=overrides;C.cache={};C.retained={};C.retainedBytes=0;lutro.browser=true;g.newImage=saved;C.prepare();return bytes`);
  const captures=[];
  for(const [one,two,name] of [[0,3,'adult'],[1,4,'teen'],[2,5,'child']]){
   await game.evaluate(({one,two,cases})=>{dojoHost.clear();run(`Scene.configure('versus','easy',true);Scene.student(1,'${cases[one]}');Scene.student(2,'${cases[two]}')`)},{one,two,cases});
   await game.evaluate(()=>Promise.all([...assetLoads.values()]));const dir=path.join(root,'.runtime/hair-captures',name);fs.mkdirSync(dir,{recursive:true});
   for(let tick=0;tick<=354;tick+=3){
    if(tick===12){await game.keyboard.down('x');await game.keyboard.down('ArrowUp');await game.keyboard.down('g');await game.keyboard.down('i')}
    if(tick===42){for(const key of ['ArrowUp','x','i','g'])await game.keyboard.up(key)}
    if(tick===60)await game.keyboard.down('ArrowUp');if(tick===63)await game.keyboard.up('ArrowUp');
    if(tick===114)await lua("assert(require('specials').start(Scene.players[1],'nidan'))");
    if(tick===234)await lua("assert(require('specials').start(Scene.players[1],'ushiro'))");
    if(tick)await step(3);else await game.evaluate(()=>dojoHost.render());
    const frame=await game.locator('#game').evaluate(canvas=>canvas.toDataURL('image/png').split(',')[1]);fs.writeFileSync(path.join(dir,String(tick).padStart(4,'0')+'.png'),Buffer.from(frame,'base64'));
   }captures.push(name);
  }
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'editor-tests.json'),JSON.stringify({previews,custom_color_persisted:true,offline:true,all_special_frames_both_ports:true,native_retained_basic_bytes:native,captures,errors},null,2)+'\n');
  console.log('PASS 18 real editor previews, custom color save/reopen, six offline bodies, every special frame in both ports, jump, nidan, greeting and native budget='+native);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
