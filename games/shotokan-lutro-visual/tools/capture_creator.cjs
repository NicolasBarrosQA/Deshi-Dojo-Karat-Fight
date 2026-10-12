// Capture the actual saved demo roster and editor, without changing any data.
const {chromium}=require('playwright'),path=require('path');
const root=path.resolve(__dirname,'..'),url=process.env.DOJO_EDITOR_URL||'http://localhost:8765';
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const editor=await browser.newPage({viewport:{width:1280,height:1100}});
 await editor.goto(url+'/editor');await editor.waitForFunction(()=>document.body.dataset.ready==='true');
 await editor.locator('#roster').selectOption('demo-child');
 await editor.waitForFunction(()=>document.getElementById('status').textContent.startsWith('Prévia pronta')&&window.editorVisual?.body==='child');
 await editor.screenshot({path:path.join(root,'docs/character-editor-demo.png'),fullPage:true});
 const game=await browser.newPage({viewport:{width:1200,height:1100}});
 await game.goto(url+'/?capture=1');await game.waitForFunction(()=>document.body.dataset.ready==='true');await game.locator('#mode').selectOption('versus');
 for(const [a,b] of [['adult','teen'],['teen','child'],['child','adult']]){
  for(const [port,body] of [[1,a],[2,b]]){await game.locator(`#p${port}-student`).selectOption('demo-'+body);await game.waitForFunction(p=>!document.getElementById(`p${p}-student`).disabled,port)}
  await game.evaluate(()=>{dojoHost.clear();run('Scene.reset();Scene.players[1].x=140;Scene.players[2].x=228');dojoHost.render()});
  await game.keyboard.down('z');await game.evaluate(()=>{for(let i=0;i<7;i++)dojoHost.update();dojoHost.render()});await game.keyboard.up('z');
  await game.locator('#game').screenshot({path:path.join(root,`docs/demo-combat-${a}-${b}.png`)});
 }
 await game.screenshot({path:path.join(root,'docs/character-roster-demo.png'),fullPage:true});console.log('Captured real editor and adult/teen/child demo combats');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
