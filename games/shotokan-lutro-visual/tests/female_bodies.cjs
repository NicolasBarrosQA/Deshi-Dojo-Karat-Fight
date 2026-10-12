const {chromium}=require('playwright'),assert=require('assert/strict'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..'),out=path.join(root,'docs/female-bodies');
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
const page=await browser.newPage({offline:true,viewport:{width:1280,height:900}}),errors=[],requests=[];
page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
await require('./offline_page.cjs')(page);await page.waitForFunction(()=>document.body.dataset.ready==='true');
let capture=null,index=0;const frames={};
const lua=s=>page.evaluate(s=>run(s),s),step=async n=>{
 if(!capture)return page.evaluate(n=>{for(let i=0;i<n;i++)dojoHost.update();dojoHost.render()},n);
 const snapshots=await page.evaluate(n=>{const a=[];for(let i=0;i<n;i++){dojoHost.update();if(++window.femaleCaptureTick%2===0){dojoHost.render();a.push({png:document.querySelector('canvas').toDataURL('image/png').split(',')[1],state:dojoHost.specialState()})}}dojoHost.render();return a},n);
 const dir=path.join(root,'.runtime/female-captures',capture);fs.mkdirSync(dir,{recursive:true});
 for(const f of snapshots){const file=String(index++).padStart(4,'0')+'.png';fs.writeFileSync(path.join(dir,file),Buffer.from(f.png,'base64'));frames[capture].push({file,state:f.state});}
};
const select=async(port,body)=>{await page.locator('#p'+port+'-body').selectOption(body);await page.waitForFunction(port=>!document.getElementById('p'+port+'-body').disabled,port);};
await page.locator('#mode').selectOption('versus');
for(const age of ['adult','teen','child']){
 const body=age+'_female';await select(1,body);await select(2,body);await lua('Scene.reset(true)');await step(2);
 await lua("for p=1,2 do for n=1,92 do Scene.players[p].pose=n;lutro.draw() end;Scene.players[p].pose=1 end");
 await lua(`local C=require('characters');local p=Scene.players[1]
 for group,a in pairs(C.data.specials['${body}']) do for n=1,9 do p.specialPose={group=group,frame=n};lutro.draw() end end;p.specialPose=nil`);
 for(const belt of ['branca','amarela','vermelha','laranja','verde','roxa','marrom','preta']){await page.locator('#p1-belt').selectOption(belt);await page.waitForFunction(()=>!document.getElementById('p1-belt').disabled);}
 await lua('Scene.reset(true)');await step(2);await page.screenshot({path:path.join(out,body+'-game.png')});
 await page.keyboard.down('ArrowUp');await step(5);await page.keyboard.up('ArrowUp');await lua('assert(Scene.players[1].air)');await step(90);await lua('assert(not Scene.players[1].air)');
 await lua("Scene.demo=false;Scene.practice=false;Scene.configure('versus','easy',true);Scene.players[1].x=150;Scene.players[2].x=280");
 if(process.env.DOJO_FEMALE_GIFS){capture=body;index=0;frames[body]=[];await page.evaluate(()=>window.femaleCaptureTick=0);}
 await step(2);await page.keyboard.down('ArrowRight');await step(20);await page.keyboard.up('ArrowRight');await step(2);
 await page.keyboard.down('ArrowDown');await step(2);await page.keyboard.down('ArrowRight');await step(2);await page.keyboard.up('ArrowDown');await step(2);await page.keyboard.down('a');await step(2);await page.keyboard.up('a');await page.keyboard.up('ArrowRight');
 await lua("assert(Scene.players[1].special and Scene.players[1].special.id=='ashi_barai','Motion did not trigger sweep')");await step(75);
 await lua("assert(Scene.players[2].knockdown and Scene.players[2].energy==96,'Sweep energy '..Scene.players[2].energy..' / '..Scene.players[2].combatState)");
 await page.keyboard.down('ArrowDown');await page.keyboard.down('x');await step(2);await page.keyboard.up('ArrowDown');await page.keyboard.up('x');await step(35);await lua('assert(Scene.players[2].energy==84)');await page.screenshot({path:path.join(out,body+'-finish.png')});await step(95);
 await lua('assert(Scene.players[2].energy==84 and not Scene.players[2].knockdown);assert(math.abs(Scene.players[1].x-Scene.players[2].x)>=87.999)');
 capture=null;
}
const memory=await lua(`local C=require('characters');local g=lutro.graphics;local saved=g.newImage;local defs={C.definition(1),C.definition(2)};local max=0
 g.newImage=function(path) return {path=path} end;lutro.browser=false
 for _,body in ipairs({'adult_female','teen_female','child_female'}) do
 C.cache={};C.retained={};C.retainedBytes=0;C.overrides={};C.select(1,{body=body,belt='preta'});C.select(2,{body=body,belt='preta'})
 for group,a in pairs(C.data.specials[body]) do C.prepareAnimation({character=C.definition(1),face=1},a) end
 assert(C.retainedBytes<C.nativeBudget);max=math.max(max,C.retainedBytes)
 end
 C.overrides=defs;C.cache={};C.retained={};C.retainedBytes=0;lutro.browser=true;g.newImage=saved;C.prepare();return max`);
assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
if(process.env.DOJO_FEMALE_GIFS)fs.writeFileSync(path.join(out,'capture-traces.json'),JSON.stringify({artifact_sha256:require('crypto').createHash('sha256').update(fs.readFileSync(path.join(root,'dist/deshi-dojo-visual.html'))).digest('hex'),capture:'Actual offline game canvas, DOM directional/kick/guard inputs, every 2 ticks',frames},null,2)+'\n');
fs.writeFileSync(path.join(out,'browser-tests.json'),JSON.stringify({bodies:3,base_poses:276,special_poses:216,belts:24,real_input_sweep_and_deliberate_finish:3,native_pair_simulated_max_bytes:memory,native_core_executed:false,errors,requests},null,2)+'\n');console.log('Female bases: all poses, belts, jump, actual sweep/finish/recovery, offline and native pair budget passed',memory);
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
