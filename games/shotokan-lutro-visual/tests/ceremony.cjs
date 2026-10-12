// Real shipped offline Lua runtime: introduction locks, round transitions and stance.
const {chromium}=require('playwright'),assert=require('assert/strict'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),out=path.join(root,'docs/ceremony');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
  const page=await browser.newPage({offline:true,viewport:{width:1080,height:900}}),errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await require('./offline_page.cjs')(page);await page.waitForFunction(()=>document.body.dataset.ready==='true');
  const lua=s=>page.evaluate(s=>run(s),s);
  const step=n=>page.evaluate(n=>{for(let i=0;i<n;i++)dojoHost.update();dojoHost.render()},n);
  for(const body of ['adult','teen','child','adult_female','teen_female','child_female']){
   await page.evaluate(body=>{dojoHost.clear();run(`Scene.demo=false;Scene.practice=false;Scene.configure('versus','easy');Scene.character(1,{body='${body}'});Scene.character(2,{body='${body}'})`)},body);
   await page.evaluate(()=>Promise.all([...assetLoads.values()]));
   await page.keyboard.down('z');await page.keyboard.down('a');await page.keyboard.down('ArrowUp');
   await step(100);
   await lua("assert(Scene.intro.age==100);assert(Scene.players[1].ceremonyPose.frame==3);assert(Scene.timer==require('techniques').arcade.round_ticks);for _,p in ipairs(Scene.players) do assert(p.energy==100 and p.executed==0 and p.jumps==0 and not p.action and not p.special and #p.motion.history==0) end");
   await step(80);await lua("assert(Scene.players[1].ceremonyPose.frame==6 and Scene.players[2].phase=='YOI')");
   await step(119);await lua('assert(Scene.intro.age==299)');
   await step(1);await lua("assert(not Scene.intro);assert(Scene.message=='HAJIME!');assert(Scene.players[1].pose==1 and not Scene.players[1].ceremonyPose)");
   await step(2);await lua('assert(Scene.players[1].executed==0 and Scene.players[1].jumps==0)');
   await page.keyboard.up('z');await page.keyboard.up('a');await page.keyboard.up('ArrowUp');await step(1);
   await page.keyboard.down('ArrowDown');await step(2);
   await lua("assert(Scene.players[1].phase=='KIBA-DACHI');assert(Scene.players[1].ceremonyPose.frame==9 and not Scene.players[1].action and not Scene.players[1].special)");
   await page.keyboard.down('z');await step(2);
   await lua("assert(Scene.players[1].action.id=='gyaku_low' and not Scene.players[1].ceremonyPose,'low punch stays an attack')");
   await page.keyboard.up('z');await page.keyboard.up('ArrowDown');
  }
  await page.evaluate(()=>{dojoHost.clear();run("Scene.configure('cpu','hard')")});await step(299);
  await lua('assert(Scene.intro and Scene.players[2].executed==0 and Scene.players[2].x==280 and Scene.timer==require("techniques").arcade.round_ticks)');
  await step(2);await lua('assert(not Scene.intro)');
  await lua('Scene.result=1;Scene.roundWait=1');await step(1);
  await lua('assert(Scene.round==2 and Scene.intro.age==0)');
  await lua('Scene.practice=true');await step(1);await lua('assert(not Scene.intro)');
  await lua('Scene.practice=false;Scene.reset()');await step(30);
  await page.keyboard.down('F2');await step(2);await page.keyboard.up('F2');await step(1);
  await lua('assert(Scene.menu);Scene.pausedIntroAge=Scene.intro.age');await step(90);await lua('assert(Scene.intro.age==Scene.pausedIntroAge)');
  await page.keyboard.down('x');await step(2);await page.keyboard.up('x');await step(2);await lua('assert(not Scene.menu and Scene.intro.age>Scene.pausedIntroAge)');
  // Capture real runtime frames: all six bodies in both ports, five-second greeting and kiba.
  const traces=[];
  for(const [left,right,name] of [['adult','adult_female','adults'],['teen','teen_female','teens'],['child','child_female','children']]){
   const dir=path.join(root,'.runtime/ceremony',name);fs.mkdirSync(dir,{recursive:true});
   await page.evaluate(({left,right})=>{dojoHost.clear();run(`Scene.configure('versus','easy');Scene.student(1,'demo-${left.replace('_','-')}');Scene.student(2,'demo-${right.replace('_','-')}');Scene.character(1,{belt='preta'});Scene.character(2,{belt='roxa'})`)},{left,right});
   await page.evaluate(()=>Promise.all([...assetLoads.values()]));
   const trace=[];
   for(let tick=0;tick<=348;tick+=3){
    if(tick===312){await page.keyboard.down('ArrowDown');await page.keyboard.down('k')}
    if(tick)await step(3);else await page.evaluate(()=>dojoHost.render());
    trace.push(await page.evaluate(()=>({state:dojoHost.snapshot(),intro:dojoHost.introActive()})));
    const frame=await page.locator('#game').evaluate(canvas=>canvas.toDataURL('image/png').split(',')[1]);
    fs.writeFileSync(path.join(dir,String(tick).padStart(4,'0')+'.png'),Buffer.from(frame,'base64'));
   }
   await page.keyboard.up('ArrowDown');await page.keyboard.up('k');
   fs.writeFileSync(path.join(out,name+'-trace.json'),JSON.stringify(trace,null,2));traces.push(name);
  }
  assert.deepEqual(errors,[]);
  const live=await browser.newPage({offline:true});await require('./offline_page.cjs')(live,false);
  await live.waitForFunction(()=>document.body.dataset.ready==='true');
  await live.evaluate(()=>{setSpeed(.25);run("Scene.practice=false;Scene.configure('versus','easy')");window.introStart=performance.now()});
  await live.waitForFunction(()=>!dojoHost.introActive(),{},{timeout:7000});
  const realSeconds=await live.evaluate(()=>(performance.now()-window.introStart)/1000);
  assert(realSeconds>=4.7&&realSeconds<6.5,'Five real seconds at quarter speed: '+realSeconds);
  await live.close();
  const nativeBytes=await lua(`local C=require('characters');local saved=lutro.graphics.newImage
   local selected,overrides=C.selected,C.overrides;local calls=0
   lutro.graphics.newImage=function(path) calls=calls+1;return {path=path} end
   lutro.browser=false;C.cache={};C.retained={};C.retainedBytes=0
   for pass=1,2 do
    for _,id in ipairs(C.data.student_order) do
     C.student(1,id);local d=C.definition(1);local a=d.visual and C.data.special_profiles[d.visual] or C.data.specials[d.body]
     C.prepareAnimation({character=d},a.ceremony)
    end
    if pass==1 then Scene.ceremonyLoads=calls else assert(calls==Scene.ceremonyLoads,'Repeated native allocation') end
   end
   assert(C.retainedBytes<C.nativeBudget);local bytes=C.retainedBytes
   C.selected=selected;C.overrides=overrides;C.cache={};C.retained={};C.retainedBytes=0
   lutro.browser=true;lutro.graphics.newImage=saved;C.prepare();return bytes`);
  const result={six_bodies_both_ports:true,intro_ticks:300,real_seconds_at_quarter_speed:realSeconds,native_retained_bytes_with_intro:nativeBytes,native_reselection_no_extra_allocations:true,locked_damage_timer_cpu_inputs:true,held_attack_does_not_leak:true,next_round_and_menu:true,kiba_separate_from_low_punch:true,offline:true,captures:traces};
  fs.writeFileSync(path.join(out,'tests.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
