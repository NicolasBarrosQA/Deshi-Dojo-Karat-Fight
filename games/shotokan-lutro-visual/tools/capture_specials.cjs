// Captures actual rendered game frames driven by DOM keyboard; never injects actions.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'dist/deshi-dojo-visual.html'),'utf8'),out=path.join(root,'docs/special-captures');fs.mkdirSync(out,{recursive:true});
(async()=>{let browser;try{
 browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const context=await browser.newContext({offline:true}),page=await context.newPage();await page.goto(require('url').pathToFileURL(path.join(root,'dist/deshi-dojo-visual.html')).href+'?capture=1',{timeout:90000});await page.waitForFunction(()=>document.body.dataset.ready==='true');
 let frame=0,dir,trace=[],held=new Set();const results={html_sha256:crypto.createHash('sha256').update(html).digest('hex'),capture:'Actual offline HTML/Lua combat; DOM keys; manual 60 Hz ticks; every second rendered tick; playback 0.5x',sequences:{}};
 const step=async n=>{for(let j=0;j<n;j++){
  const data=await page.evaluate(capture=>{dojoHost.update();if(capture){dojoHost.render();return {png:document.getElementById('game').toDataURL(),state:dojoHost.specialState()+'|pose='+run('return Scene.players[1].pose')}}},frame%2===0);
  if(data){fs.writeFileSync(path.join(dir,String(frame).padStart(4,'0')+'.png'),Buffer.from(data.png.split(',')[1],'base64'));trace.push({frame,keys:[...held],state:data.state.split('|')})}frame++;
 }};
 const keys=async next=>{for(const k of held)if(!next.includes(k))await page.keyboard.up(k);for(const k of next)if(!held.has(k))await page.keyboard.down(k);held=new Set(next)};
 const motion=async(name,button)=>{const parts={qcf:[['ArrowDown'],['ArrowDown','ArrowRight'],['ArrowRight']],qcb:[['ArrowDown'],['ArrowDown','ArrowLeft'],['ArrowLeft']],hcf:[['ArrowLeft'],['ArrowLeft','ArrowDown'],['ArrowDown'],['ArrowDown','ArrowRight'],['ArrowRight']],hcb:[['ArrowRight'],['ArrowRight','ArrowDown'],['ArrowDown'],['ArrowDown','ArrowLeft'],['ArrowLeft']],z:[['ArrowRight'],['ArrowDown'],['ArrowDown','ArrowRight']]};for(const c of parts[name]){await keys(c);await step(2)}await keys([...parts[name].at(-1),button]);await step(2);await keys([]);await step(1)};
 for(const [id,name,button] of [['ashi-sequence','qcf','a'],['ura_mawashi','hcf','a'],['ushiro','hcb','a'],['tai_sabaki','qcb','x'],['renzoku','z','z'],['nidan','z','a']]){
  dir=path.join(out,id);fs.mkdirSync(dir,{recursive:true});frame=0;trace=[];await keys([]);
  await page.evaluate(()=>{dojoHost.clear();run("Scene.practice=false;Scene.configure('versus','easy',true);Scene.captureContacts={};Scene.onContact=function(e) Scene.captureContacts[#Scene.captureContacts+1]=e.technique..':'..e.player..':'..e.damage..':'..tostring(e.blocked)..':'..Scene.tick end")});
  await step(8);await keys(['ArrowRight']);await step(47);await keys([]);await step(8);await motion(name,button);
  if(id==='ashi-sequence'){
   for(let j=0;j<120;j++){const s=(await page.evaluate(()=>dojoHost.specialState())).split('|');if(s[11]==='down'&&s[3]==='-'&&Number(s[7])===0)break;await step(1);assert(j<119,'No finish opportunity')}
   await keys(['ArrowDown','x']);await step(2);await keys([]);await step(140);
   await page.evaluate(()=>run("assert(Scene.players[2].energy==84 and not Scene.players[2].knockdown and Scene.players[1].energy==100,'Complete deliberate finish failed')"));
  }else if(id==='tai_sabaki'){
   await step(3);await keys(['f']);await step(2);await keys([]);await step(18);await keys(['z']);await step(2);await keys([]);await step(90);
  }else await step(110);
  const contacts=await page.evaluate(()=>run("return table.concat(Scene.captureContacts,'|')"));results.sequences[id]={frames:trace.length,contacts,end:await page.evaluate(()=>dojoHost.specialState())};
  fs.writeFileSync(path.join(dir,'trace.json'),JSON.stringify(trace,null,2));
 }
 if(process.env.DOJO_CAPTURE_SCALE)for(const body of ['adult','teen','child','adult_female','teen_female','child_female']){
  const id='scale-'+body;dir=path.join(out,id);fs.mkdirSync(dir,{recursive:true});frame=0;trace=[];await keys([]);
  const student='demo-'+body.replace('_female','-female');await page.selectOption('#p1-student',student);
  await page.waitForFunction(body=>run('return Scene.players[1].character.body')===body,body);
  await page.evaluate(()=>{dojoHost.clear();run("Scene.demo=false;Scene.practice=false;Scene.configure('versus','easy',true);Scene.players[1].x=100;Scene.players[2].x=310")});
  await step(12);await keys(['z']);await step(2);await keys([]);await step(42);
  await keys(['a']);await step(2);await keys([]);await step(48);
  await keys(['ArrowUp']);await step(12);
  await page.evaluate(()=>run("assert(Scene.players[1].air and Scene.players[1].height>20)"));
  await keys([]);await step(36);
  await page.evaluate(()=>run("assert(not Scene.players[1].air)"));
  await keys(['ArrowUp']);await step(12);
  await keys(['z']);await step(2);await keys([]);await step(60);
  await page.evaluate(()=>run("assert(not Scene.players[1].air and not Scene.players[1].action)"));
  results.sequences[id]={body,frames:trace.length,end:await page.evaluate(()=>dojoHost.specialState()),commands:['punch','kick','plain jump with descent and landing','second jump with air punch','landing']};
  fs.writeFileSync(path.join(dir,'trace.json'),JSON.stringify(trace,null,2));
 }
 fs.writeFileSync(path.join(out,'capture-results.json'),JSON.stringify(results,null,2));console.log(results);
}finally{if(browser)await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
