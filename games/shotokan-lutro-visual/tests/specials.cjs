const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'dist/deshi-dojo-visual.html'),'utf8');
(async()=>{let browser;try{
 browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({offline:true}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(require('url').pathToFileURL(path.join(root,'dist/deshi-dojo-visual.html')).href+'?capture=1',{timeout:90000});await page.waitForFunction(()=>document.body.dataset.ready==='true');
 await page.evaluate(()=>run(`local M=require('motion')
 local function check(seq,name,face,config)
  local s=M.new(config);for _,d in ipairs(seq) do local c={};if d==2 or d==1 or d==3 then c.down=true end;if d==4 or d==1 then c[face==1 and 'left' or 'right']=true end;if d==6 or d==3 then c[face==1 and 'right' or 'left']=true end;for n=1,2 do M.update(s,c,face) end end
  assert(M.matches(s,name),name..' facing '..face);s.consumed=s.tick;assert(not M.matches(s,name),'consumed reuse')
 end
 for _,face in ipairs({1,-1}) do for name,pattern in pairs(M.patterns) do check(pattern,name,face) end end
 check({2,6},'qcf',1,{four_way=true});check({4,2,6},'hcf',1,{four_way=true});check({6,2,6},'z',-1,{four_way=true})
 for _,seq in ipairs({{6},{2,6},{2,3},{4,6},{6,4,6},{2,4,6}}) do local s=M.new();for _,d in ipairs(seq) do s.history[#s.history+1]={direction=d,tick=#s.history*2+1};s.tick=#s.history*2 end;assert(not M.matches(s,'qcf'),'incomplete') end
 local s=M.new();s.history={{direction=2,tick=1},{direction=3,tick=3},{direction=6,tick=5}};s.tick=30;assert(not M.matches(s,'qcf'),'stale')
 `));
 const step=async n=>page.evaluate(n=>{for(let i=0;i<n;i++)dojoHost.update();dojoHost.render()},n);
 const lua=async s=>page.evaluate(s=>run(s),s);
 const status=async()=>page.evaluate(()=>run('function dojoSpecialStatus() local a,b=Scene.players[1],Scene.players[2];return (a.special and a.special.id or "-").."|"..(b.special and b.special.id or "-").."|"..a.energy.."|"..b.energy.."|"..a.combatState.."|"..b.combatState end')||window.fengari.load('return dojoSpecialStatus()')());
 const reset=async(side=1,reverse=false,x=140)=>{await page.evaluate(({reverse,x})=>{dojoHost.clear();run(`Scene.demo=false;Scene.practice=false;Scene.configure('versus','easy');Scene.players[1].x=${reverse?x+88:x};Scene.players[2].x=${reverse?x:x+88};Scene.left=${reverse?2:1}`)},{reverse,x});await step(2)};
 const maps={1:{down:'ArrowDown',forward:'ArrowRight',back:'ArrowLeft',kick:'a',guard:'x',punch:'z'},2:{down:'k',forward:'j',back:'l',kick:'h',guard:'g',punch:'f'}};
 const motion=async(side,reverse,name,button)=>{let m={...maps[side]};if(reverse)[m.forward,m.back]=[m.back,m.forward];const patterns={qcf:[[m.down],[m.down,m.forward],[m.forward]],qcb:[[m.down],[m.down,m.back],[m.back]],hcf:[[m.back],[m.back,m.down],[m.down],[m.down,m.forward],[m.forward]],hcb:[[m.forward],[m.forward,m.down],[m.down],[m.down,m.back],[m.back]],z:[[m.forward],[m.down],[m.down,m.forward]]};let held=[];for(const keys of patterns[name]){for(const k of held)if(!keys.includes(k))await page.keyboard.up(k);for(const k of keys)if(!held.includes(k))await page.keyboard.down(k);held=keys;await step(2)}await page.keyboard.down(m[button]);await step(2);await page.keyboard.up(m[button]);for(const k of held)await page.keyboard.up(k);await step(1)};
 for(const side of [1,2])for(const reverse of [false,true]){
  await reset(side,reverse);await motion(side,reverse,'qcf','kick');await lua(`assert(Scene.players[${side}].special.id=='ashi_barai')`);await step(75);
  await lua(`local t=Scene.players[${3-side}];assert(t.energy==96,tostring(t.energy)..' state '..t.combatState);assert(t.combatState=='down',t.combatState..' age '..tostring(t.knockdown and t.knockdown.age));assert(Scene.players[${side}].special==nil,'attacker recovering')`);
  const m=maps[side];await page.keyboard.down(m.down);await page.keyboard.down(m.guard);await step(2);await page.keyboard.up(m.guard);await page.keyboard.up(m.down);
  await lua(`assert(Scene.players[${side}].special.id=='ashi_finish');assert(Scene.players[${3-side}].combatState=='receiving_finish')`);
  // Fallen player cannot counter, and holding finish never repeats its damage.
  await page.keyboard.down(maps[3-side].punch);await page.keyboard.down(maps[3-side].kick);await step(60);
  await lua(`assert(Scene.players[${3-side}].energy==84);assert(Scene.players[${side}].energy==100);assert(Scene.players[${3-side}].knockdown)`);
  await page.keyboard.up(maps[3-side].punch);await page.keyboard.up(maps[3-side].kick);await step(70);
  await lua('assert(not Scene.players[1].knockdown and not Scene.players[2].knockdown);assert(Scene.players[1].x<Scene.players[2].x or Scene.left==2)');
 }
 await reset();await page.keyboard.down('k');await page.keyboard.down('g');await step(8);await motion(1,false,'qcf','kick');await step(50);await lua('assert(Scene.players[2].energy==100 and not Scene.players[2].knockdown);assert(Scene.players[2].blocks==1)');await page.keyboard.up('k');await page.keyboard.up('g');
 await reset();await motion(1,false,'qcf','kick');await step(140);await lua('assert(Scene.players[2].energy==96 and not Scene.players[2].knockdown)');await page.keyboard.down('ArrowDown');await page.keyboard.down('x');await step(2);await lua("assert(Scene.players[1].action.id=='gedan')");await page.keyboard.up('ArrowDown');await page.keyboard.up('x');
 await reset(1,false,64);await lua('Scene.players[2].x=280');await motion(1,false,'qcf','kick');await step(100);await lua('assert(Scene.players[2].energy==100 and not Scene.players[2].knockdown)');
 for(const [name,button,id] of [['hcf','kick','ura_mawashi'],['hcb','kick','ushiro'],['z','punch','renzoku'],['z','kick','nidan'],['qcb','guard','tai_sabaki']]){await reset();await motion(1,false,name,button);await lua(`assert(Scene.players[1].special and Scene.players[1].special.id=='${id}')`);await step(130);await lua('assert(not Scene.players[1].special and Scene.players[1].height==0)')}
 await reset();await motion(1,false,'qcf','kick');await motion(2,false,'z','kick');await step(40);await lua("assert(not Scene.players[2].knockdown,'Sweep must not knock down airborne Nidan')");
 for(const side of [1,2])for(const reverse of [false,true])for(const x of [64,232]){
  await reset(side,reverse,x);await motion(side,reverse,'qcf','kick');await step(75);
  await page.keyboard.down(maps[side].down);await page.keyboard.down(maps[side].guard);await step(2);await page.keyboard.up(maps[side].guard);await page.keyboard.up(maps[side].down);
  await lua(`assert(Scene.players[${side}].special.id=='ashi_finish')`);await step(35);
  await lua("assert(math.abs(Scene.players[1].x-Scene.players[2].x)>=require('techniques').special_rules.ground_push_distance-.001)");await step(105);
  await lua(`assert(Scene.players[${3-side}].energy==84 and not Scene.players[${3-side}].knockdown);assert(math.abs(Scene.players[1].x-Scene.players[2].x)>=87.999)`);
 }
 await reset();await motion(1,false,'qcf','kick');await step(75);await page.keyboard.down('ArrowLeft');await step(19);await page.keyboard.up('ArrowLeft');await page.keyboard.down('ArrowDown');await page.keyboard.down('x');await step(2);await lua("assert(not Scene.players[1].special and Scene.players[1].action.id=='gedan');assert(Scene.players[2].energy==96)");await page.keyboard.up('ArrowDown');await page.keyboard.up('x');await step(80);
 await reset();await lua('Scene.players[2].energy=16');await motion(1,false,'qcf','kick');await step(75);await page.keyboard.down('ArrowDown');await page.keyboard.down('x');await step(2);await page.keyboard.up('ArrowDown');await page.keyboard.up('x');await step(50);await lua('assert(Scene.result==1 and Scene.players[2].energy==0)');await step(110);await lua('assert(Scene.round==2 and not Scene.players[2].knockdown and Scene.players[2].energy==100)');
 await reset();await page.evaluate(()=>{dojoHost.clear();run("Scene.configure('cpu','hard');Scene.practice=true;Scene.specialCPU={};Scene.onContact=function(e) Scene.specialCPU[e.technique]=(Scene.specialCPU[e.technique] or 0)+1 end")});await step(7000);await lua("assert(Scene.specialCPU.ashi_barai and Scene.specialCPU.ashi_finish,'CPU sweep/finish through normal input');assert(Scene.players[1].energy==100 and Scene.players[2].energy==100,'practice energy regression')");
 assert.deepEqual(errors,[]);
 const result={artifact_sha256:require('crypto').createHash('sha256').update(html).digest('hex'),checks:['All five motions; mirrored facing; incomplete/stale rejection; optional four-way tolerance','Priority over normal actions and deliberate second guard command','P1 and P2 finish from both sides; no fallen counterattack; one finish per knockdown','Low block, miss, expiry and out-of-range gedan fallback','Eight wall/facing/player finish cases and restored standing barrier','All other specials activate and recover','Round KO/reset and practice energy','CPU performs sweep and finish through ordinary input over 7000 ticks'],errors};
 const dest=path.join(__dirname,'../docs/specials-results.json');fs.writeFileSync(dest+'.tmp',JSON.stringify(result,null,2)+'\n');fs.renameSync(dest+'.tmp',dest);
 console.log('PASS: motions, both players/facings, deliberate finish, no counter/repeat, block, expiry, miss, all specials');
}finally{if(browser)await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});

