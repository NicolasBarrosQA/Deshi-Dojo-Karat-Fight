// Reproduce native controller workload in offline Fengari; exact deterministic state.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert/strict');
const data=JSON.parse(fs.readFileSync(process.argv[2])),root=path.resolve(__dirname,'..');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});try{
 const page=await browser.newPage({offline:true}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('about:blank?capture=1');await page.setContent(fs.readFileSync(path.join(root,'dist/deshi-dojo-visual.html'),'utf8'));await page.waitForFunction(()=>document.body.dataset.ready==='true');
 for(const replay of data.replays){
  const actual=await page.evaluate(replay=>{
   dojoHost.clear();run(replay.initial);const output=[];
   for(const keys of replay.keys){
    for(let p=1;p<=2;p++)for(let k=1;k<=14;k++)dojoHost.press(p,k,false);
    for(const [port,button] of keys)dojoHost.press(port+1,button+1,true);
    dojoHost.update();
    output.push(run(`local a,b=Scene.players[1],Scene.players[2];local s=Scene.cpu;local bits=0
     for i,k in ipairs({'up','down','left','right','b','y','a'}) do if b.inputs[k] then bits=bits+2^(i-1) end end
     local t={Scene.tick,math.floor(a.x*16),math.floor(b.x*16),a.energy,b.energy,a.executed,b.executed,a.contacts,b.contacts,a.blocks,b.blocks,a.chain,b.chain,a.jumps,b.jumps,Scene.wins[1],Scene.wins[2],Scene.matchWinner or 0,Scene.menu and 1 or 0,Scene.menuChoice or 0,s.clock,s.pulses,s.decisions,s.rng%65536,math.floor(s.rng/65536),bits,Scene.testProof or 0,Scene.round,Scene.timer,b.maxChain,math.floor(b.height*16)}
     for i,v in ipairs(t) do t[i]=math.floor(v) end;return table.concat(t,'|')`).split('|').map(Number));
   }return output;
  },replay);
  for(let n=0;n<actual.length;n++)assert.deepEqual(actual[n],replay.frames[n],`${replay.level}, tick${n+1}`);
 }
 assert.deepEqual(errors,[]);console.log('PASS 1080 native/Fengari CPU ticks');
 }finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
