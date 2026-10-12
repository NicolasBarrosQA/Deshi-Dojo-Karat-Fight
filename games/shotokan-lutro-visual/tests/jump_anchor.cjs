// Real DOM jumps plus actual historical draw coordinates on both ports/facings.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),out=path.join(root,'docs/avatar-set-v3');
const base=JSON.parse(fs.readFileSync(path.join(root,'assets/character-assets.json'))),masks=JSON.parse(fs.readFileSync(path.join(root,'assets/character-masks.json')));
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const page=await browser.newPage({offline:true}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await require('./offline_page.cjs')(page);await page.waitForFunction(()=>document.body.dataset.ready==='true');const checks=[];
 for(const body of Object.keys(base))for(const port of [1,2])for(const horizontal of [false,true]){
  await page.selectOption('#p1-body',body);await page.selectOption('#p2-body',body);
  await page.evaluate(port=>{dojoHost.clear();run(`Scene.demo=false;Scene.practice=false;Scene.configure('versus','easy',true);Scene.players[1].x=90;Scene.players[2].x=310
   local C=require('characters');local p=Scene.players[${port}];local part=C.data.bodies[p.character.body].parts.body.default
   local g=lutro.graphics;Scene.anchorSavedDraw=g.draw;g.draw=function(image,quad,x,y)
    local side=p.face==1 and 'right' or 'left';if image==C.cache[part[side]] then Scene.anchorDrawX=x end
    Scene.anchorSavedDraw(image,quad,x,y) end`);},port);
  const up=port===1?'ArrowUp':'i',forward=port===1?'ArrowRight':'j';if(horizontal)await page.keyboard.down(forward);await page.keyboard.down(up);
  const trace=await page.evaluate(port=>{const a=[];for(let i=0;i<45;i++){dojoHost.update();dojoHost.render();a.push(run(`local p=Scene.players[${port}];return p.x..'|'..p.pose..'|'..p.face..'|'..p.height..'|'..p.jumpVX..'|'..tostring(Scene.anchorDrawX)`))}run('lutro.graphics.draw=Scene.anchorSavedDraw');return a;},port);
  await page.keyboard.up(up);if(horizontal)await page.keyboard.up(forward);
  const rows=trace.map(s=>s.split('|').map(Number));let transitions=0;
  for(let i=1;i<rows.length;i++)if(rows[i-1][1]===62&&rows[i][1]===63){
   const head=r=>{const pose=r[1],f=base[body].parts.body.default.frames[pose-1],a=base[body].jump_anchor,c=(pose===62?a.rise_anchor_x:a.descent_anchor_x)-f.x;return r[5]+(r[2]===1?c:f.w-c)};
   const before=rows[i-1],after=rows[i],physics=after[0]-before[0];
   assert(Math.abs(physics-(horizontal?after[4]:0))<.001,`${body} P${port} physical teleport`);
   const renderedPhysics=Math.floor(after[0]-112)-Math.floor(before[0]-112);
   assert(Math.abs(head(after)-head(before)-renderedPhysics)<=.501,`${body} P${port} drawn jump ${JSON.stringify({before,after,headBefore:head(before),headAfter:head(after),renderedPhysics})}`);transitions++;
  }
  assert.equal(transitions,1);assert.equal(rows.at(-1)[3],0);
  checks.push({body,port,horizontal,transition_count:transitions});
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'jump-anchor-tests.json'),JSON.stringify({passed:checks.length,checks,errors,actual_draw_coordinates:true,artifact_sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'dist/deshi-dojo-visual.html'))).digest('hex')},null,2)+'\n');
 console.log('PASS 24 real vertical/forward jumps: six bodies, both ports, continuous physics and drawn upper-body anchor');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
