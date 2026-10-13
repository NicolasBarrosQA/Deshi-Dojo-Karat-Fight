const {chromium}=require('playwright'),assert=require('assert/strict'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),out=path.join(root,'docs/hair-rebuild-v2'),url=process.env.DOJO_EDITOR_URL,cases=JSON.parse(process.env.DOJO_HAIR_CASES);
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1400,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(url+'/editor');await page.waitForFunction(()=>document.body.dataset.ready==='true');
  const catalog=await page.evaluate(()=>fetch('/api/characters').then(r=>r.json()).then(r=>r.catalog));
  assert.deepEqual(catalog.hair_styles.map(e=>e.id),['default','masculino_curto','feminino_chanel']);assert.deepEqual(catalog.beard_styles.map(e=>e.id),['default']);
  const previews=[];
  for(const body of catalog.bodies){
   await page.selectOption('#body',body);
   for(const [hair,color] of [['masculino_curto','preto'],['feminino_chanel','branco']]){
    await page.selectOption('#hair',hair);await page.selectOption('#hair_color',color);
    await page.waitForFunction(({body,hair,color})=>window.editorVisual?.body===body&&window.editorVisual.hair===hair&&window.editorVisual.appearance.hair_color===color,{body,hair,color},{timeout:90000});
    for(const pose of [1,15,59,62,63,85]){await page.fill('#pose',String(pose));await page.locator('#pose').dispatchEvent('input');await page.selectOption('#facing','left');await page.selectOption('#facing','right')}
    previews.push({body,hair,color});
   }
  }
  await page.evaluate(()=>{document.getElementById('hair-custom').value='#663399';document.getElementById('hair-custom').dispatchEvent(new Event('input',{bubbles:true}))});
  await page.waitForFunction(()=>window.editorVisual?.appearance.hair_color==='#663399',{},{timeout:90000});
  await page.screenshot({path:path.join(out,'editor-native-cuts.png'),fullPage:true});
  const game=await browser.newPage({offline:true});game.on('pageerror',e=>errors.push(String(e)));
  await require('./offline_page.cjs')(game,true,process.env.DOJO_EDITOR_DIST);await game.waitForFunction(()=>document.body.dataset.ready==='true');
  const lua=s=>game.evaluate(s=>run(s),s),step=n=>game.evaluate(n=>{for(let i=0;i<n;i++)dojoHost.update();dojoHost.render()},n);
  for(let i=0;i<cases.length;i+=2){
   await game.evaluate(({a,b})=>{dojoHost.clear();run(`Scene.configure('versus','easy',true);Scene.student(1,'${a}');Scene.student(2,'${b}')`)},{a:cases[i],b:cases[i+1]});await game.evaluate(()=>Promise.all([...assetLoads.values()]));await step(420);
   await lua('assert(Scene.players[1].energy==100 and Scene.players[2].energy==100)');
   // Draw every special pose through the real game in both ports.
   for(const group of ['ashi_barai','ashi_finish','knockdown','ura_mawashi','ushiro','tai_sabaki','renzoku','nidan','ceremony','hand_touch'])
    for(let frame=1;frame<=9;frame++)await lua(`Scene.players[1].specialPose={group='${group}',frame=${frame}};Scene.players[2].specialPose={group='${group}',frame=${frame}};lutro.draw()`);
   await lua('Scene.players[1].specialPose=nil;Scene.players[2].specialPose=nil');
   const dir=path.join(root,'.runtime/native-hair-captures',catalog.bodies[i/2]);fs.mkdirSync(dir,{recursive:true});
   for(let tick=0;tick<=240;tick+=4){
    if(tick===8){await game.keyboard.down('ArrowUp');await game.keyboard.down('i')}
    if(tick===12){await game.keyboard.up('ArrowUp');await game.keyboard.up('i')}
    if(tick===64)await lua("assert(require('specials').start(Scene.players[1],'nidan'));assert(require('specials').start(Scene.players[2],'nidan'))");
    if(tick===164)await lua("assert(require('specials').start(Scene.players[1],'ushiro'));assert(require('specials').start(Scene.players[2],'ushiro'))");
    if(tick)await step(4);else await game.evaluate(()=>dojoHost.render());
    const png=await game.locator('#game').evaluate(c=>c.toDataURL('image/png').split(',')[1]);fs.writeFileSync(path.join(dir,String(tick).padStart(4,'0')+'.png'),Buffer.from(png,'base64'));
   }
   await lua('assert(Scene.players[1].height==0 and Scene.players[2].height==0)');
  }
  const native=[];
  for(const styleIndex of [0,1]) native.push(await lua(`local C=require('characters');local g=lutro.graphics;local saved=g.newImage;local selected={C.selected[1],C.selected[2]};local overrides=C.overrides
   g.newImage=function(path)return {path=path} end;lutro.browser=false;C.cache={};C.retained={};C.retainedBytes=0
   local ids={${cases.filter((_,i)=>i%2===styleIndex).map(id=>"'"+id+"'").join(',')}};C.selected={ids[1],ids[1]};C.overrides={}
   for _,id in ipairs(ids) do C.student(1,id) end
   assert(C.retainedBytes<C.nativeBudget);local bytes=C.retainedBytes
   for _,id in ipairs(ids) do C.student(1,id) end;assert(C.retainedBytes==bytes)
   C.selected=selected;C.overrides=overrides;C.cache={};C.retained={};C.retainedBytes=0;lutro.browser=true;g.newImage=saved;C.prepare();return bytes`));
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'native-runtime-tests.json'),JSON.stringify({previews,custom_color:true,offline:true,six_bases_both_cuts:true,all_special_frames_both_ports:true,real_jump_nidan_ushiro:true,native_retained_basic_bytes:native,physical_Pi_executed:false,errors},null,2)+'\n');
  console.log('PASS 12 editor previews; custom color; six offline pairs; both ports/all special frames; real jumps/nidan/ushiro; native basic bytes per six-character roster='+native);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
