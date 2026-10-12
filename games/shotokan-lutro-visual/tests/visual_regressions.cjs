// Capture real keyboard jumps beside a standing opponent of the same body.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..');
(async()=>{const browser=await chromium.launch({executablePath:process.env.DOJO_CHROMIUM||(process.platform==='win32'?'C:/Program Files/Google/Chrome/Application/chrome.exe':'/usr/bin/chromium'),headless:true});try{
 const page=await browser.newPage({offline:true}),errors=[],requests=[],checks=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 await require('./offline_page.cjs')(page);
 await page.waitForFunction(()=>document.body.dataset.ready==='true');await page.locator('#mode').selectOption('versus');
 const step=async()=>page.evaluate(()=>{dojoHost.update();dojoHost.render()});
 for(const body of ['adult','teen','child']){
  for(const port of [1,2]){
   await page.locator(`#p${port}-body`).selectOption(body);await page.waitForFunction(id=>!document.getElementById(id).disabled,`p${port}-body`);
   await page.locator(`#p${port}-belt`).selectOption(port===1?'amarela':'branca');await page.waitForFunction(id=>!document.getElementById(id).disabled,`p${port}-belt`);
  }
  await page.evaluate(()=>{dojoHost.clear();run('Scene.reset()');dojoHost.render()});
  const seen=new Set();await page.keyboard.down('ArrowUp');
  for(let n=0;n<45;n++){
   await step();const state=(await page.evaluate(()=>run('local p=Scene.players[1];return p.pose.."|"..p.height'))).split('|').map(Number);
   if(!seen.has(state[0])&&[61,62,63,64].includes(state[0])){
    const data=await page.evaluate(()=>document.getElementById('game').toDataURL());
    fs.writeFileSync(path.join(root,`docs/jump-${body}-${state[0]}.png`),Buffer.from(data.split(',')[1],'base64'));seen.add(state[0]);
   }
  }
  await page.keyboard.up('ArrowUp');assert.deepEqual([...seen].sort(),[61,62,63,64]);
  assert.equal(Number(await page.evaluate(()=>run('return Scene.players[1].height'))),0);
  checks.push(`${body}: actual keyboard takeoff, ascent, descent and landing; standing opponent and colored belt captured`);
 }
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
 fs.writeFileSync(path.join(root,'docs/visual-regression-results.json'),JSON.stringify({checks,errors,requests},null,2)+'\n');console.log(checks.join('\n'));
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
