// Six neutral bodies, both ports, real DOM sweep/finish inputs, offline.
const {chromium}=require('playwright'),assert=require('assert/strict'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),out=path.join(root,'docs/avatar-set-v3');
const bodies=['adult','teen','child','adult_female','teen_female','child_female'];
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const page=await browser.newPage({offline:true,viewport:{width:1280,height:950}}),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 await require('./offline_page.cjs')(page);await page.waitForFunction(()=>document.body.dataset.ready==='true');
 const lua=s=>page.evaluate(s=>run(s),s),traces={};let capture=null,index=0;
 const step=async n=>{
  if(!capture)return page.evaluate(n=>{for(let i=0;i<n;i++)dojoHost.update();dojoHost.render()},n);
  const images=await page.evaluate(n=>{const a=[];for(let i=0;i<n;i++){dojoHost.update();if(++window.neutralCaptureTick%2===0){dojoHost.render();a.push({png:document.getElementById('game').toDataURL('image/png').split(',')[1],state:dojoHost.specialState()})}}dojoHost.render();return a},n);
  const dir=path.join(root,'.runtime/neutral-captures',capture);fs.mkdirSync(dir,{recursive:true});
  for(const im of images){const file=String(index++).padStart(4,'0')+'.png';fs.writeFileSync(path.join(dir,file),Buffer.from(im.png,'base64'));traces[capture].push({file,state:im.state});}
 };
 const select=async(port,body)=>{await page.selectOption('#p'+port+'-body',body);await page.waitForFunction(p=>!document.getElementById('p'+p+'-body').disabled,port)};
 assert((await page.locator('#p1-student option').count())>=6);
 assert.equal(await page.locator('#p1-student option[value^="pilot-"]').count(),0);
 await page.selectOption('#mode','versus');
 for(const port of [1,2])for(const body of bodies){
  await select(1,body);await select(2,body);await lua('Scene.reset(true)');await step(2);
  await lua(`local C=require('characters');local p=Scene.players[${port}]
   assert(p.character.body=='${body}' and (not p.character.identity or p.character.identity=='default') and not p.character.visual)
   for i=1,92 do p.pose=i;lutro.draw() end
   for group,a in pairs(C.data.specials['${body}']) do for i=1,9 do p.specialPose={group=group,frame=i};lutro.draw() end end
   p.specialPose=nil;p.pose=1`);
  await lua("Scene.demo=false;Scene.practice=false;Scene.configure('versus','easy',true);Scene.players[1].x=150;Scene.players[2].x=280");
  if(process.env.DOJO_NEUTRAL_GIFS){capture=body+'-p'+port;index=0;traces[capture]=[];await page.evaluate(()=>window.neutralCaptureTick=0)}
  await step(2);
  const forward=port===1?'ArrowRight':'j',down=port===1?'ArrowDown':'k',kick=port===1?'a':'h',guard=port===1?'x':'g';
  await page.keyboard.down(forward);await step(20);await page.keyboard.up(forward);await step(2);
  await page.keyboard.down(down);await step(2);await page.keyboard.down(forward);await step(2);await page.keyboard.up(down);await step(2);
  await page.keyboard.down(kick);await step(2);await page.keyboard.up(kick);await page.keyboard.up(forward);
  await lua(`assert(Scene.players[${port}].special and Scene.players[${port}].special.id=='ashi_barai')`);
  await step(75);const target=3-port;
  await lua(`assert(Scene.players[${target}].knockdown and Scene.players[${target}].energy==96)`);
  await page.keyboard.down(down);await page.keyboard.down(guard);await step(2);await page.keyboard.up(down);await page.keyboard.up(guard);
  await step(35);await lua(`assert(Scene.players[${target}].energy==84)`);
  if(port===1)await page.screenshot({path:path.join(out,body+'-finish.png')});
  await step(95);await lua(`assert(Scene.players[${target}].energy==84 and not Scene.players[${target}].knockdown);assert(Scene.players[${port}].energy==100);assert(math.abs(Scene.players[1].x-Scene.players[2].x)>=87.999)`);
  capture=null;
 }
 const memory=await lua(`local C=require('characters');local g=lutro.graphics;local saved=g.newImage;local defs={C.definition(1),C.definition(2)};local max=0
  g.newImage=function(path)return {path=path}end;lutro.browser=false
  for _,body in ipairs({'adult','teen','child','adult_female','teen_female','child_female'})do
   C.cache={};C.retained={};C.retainedBytes=0;C.overrides={};C.select(1,{body=body,belt='branca'});C.select(2,{body=body,belt='branca'})
   for _,a in pairs(C.data.specials[body])do C.prepareAnimation({character=C.definition(1),face=1},a)end
   assert(C.retainedBytes<C.nativeBudget);max=math.max(max,C.retainedBytes)
  end
  C.overrides=defs;C.cache={};C.retained={};C.retainedBytes=0;lutro.browser=true;g.newImage=saved;C.prepare();return max`);
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
 const sha=crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'dist/deshi-dojo-visual.html'))).digest('hex');
 if(process.env.DOJO_NEUTRAL_GIFS)fs.writeFileSync(path.join(out,'capture-traces.json'),JSON.stringify({artifact_sha256:sha,capture:'Actual offline HTML game canvas; directional/kick/guard DOM inputs; every two 60 Hz ticks',frames:traces},null,2)+'\n');
 fs.writeFileSync(path.join(out,'browser-tests.json'),JSON.stringify({bodies:6,ports:2,rendered_basic_poses:1104,rendered_special_poses:864,real_sweep_finish_recovery_sequences:12,native_pair_simulated_max_bytes:memory,native_device_tested:false,errors,requests,artifact_sha256:sha},null,2)+'\n');
 console.log('PASS six neutral bodies, all poses on both ports, 12 real sweep/finish/recovery sequences, offline and pair budget:',memory);
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
