// Read-only live editor review; all persistent save/export tests use a fixture.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),out=path.join(root,'docs/skin-personalization');fs.mkdirSync(out,{recursive:true});
(async()=>{const rosterPath=path.join(root,'assets/characters.json'),before=crypto.createHash('sha256').update(fs.readFileSync(rosterPath)).digest('hex');const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const page=await browser.newPage({viewport:{width:1400,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://localhost:8769/editor');await page.waitForFunction(()=>document.body.dataset.ready==='true');
 assert.equal(await page.locator('#skin-cards button').count(),12);assert.equal(await page.locator('#skin option').count(),12);
 await page.check('#compare-original');const checked=[];
 for(const body of ['adult','teen','child','adult_female','teen_female','child_female']){
  await page.selectOption('#body',body);await page.locator('[data-skin="retinta"]').click();
  await page.waitForFunction(body=>window.editorVisual?.body===body&&window.editorVisual.appearance.skin==='retinta'&&originalVisual?.body===body,body,{timeout:90000});
  assert.equal(await page.locator('[data-skin="retinta"]').getAttribute('aria-pressed'),'true');
  for(const pose of [1,27,63]){await page.fill('#pose',String(pose));await page.locator('#pose').dispatchEvent('input');const different=await page.evaluate(()=>document.getElementById('preview').toDataURL()!==document.getElementById('original-preview').toDataURL());assert(different);}
  await page.selectOption('#facing','left');await page.selectOption('#facing','right');checked.push(body);
 }
 await page.selectOption('#roster','demo-adult-female');await page.locator('[data-skin="castanha"]').click();await page.fill('#pose','1');await page.locator('#pose').dispatchEvent('input');
 await page.waitForFunction(()=>window.editorVisual?.body==='adult_female'&&window.editorVisual.appearance.skin==='castanha'&&originalVisual?.body==='adult_female',{},{timeout:90000});
 await page.screenshot({path:path.join(out,'editor.png'),fullPage:true});
 const snapshot=await page.evaluate(()=>current());await page.locator('#clone').click();const clone=await page.evaluate(()=>current());assert.notEqual(clone.id,snapshot.id);assert.equal(clone.body,snapshot.body);assert.equal(clone.appearance.skin,snapshot.appearance.skin);assert.equal(await page.evaluate(()=>editing),null);
 await page.locator('[data-skin="retinta"]').click();assert((await page.inputValue('#nickname')).includes('Retinta'));
 const game=await browser.newPage();await game.goto('http://localhost:8769/',{waitUntil:'domcontentloaded',timeout:90000});await game.waitForFunction(()=>document.body.dataset.ready==='true',{},{timeout:90000});
 assert.equal(await game.locator('#p1-body').isVisible(),false);assert.equal(await game.locator('a[href="/editor"]').count(),0);assert(await game.locator('#p1-student').isVisible());assert(await game.locator('#p1-belt').isVisible());
 const after=crypto.createHash('sha256').update(fs.readFileSync(rosterPath)).digest('hex');assert.equal(before,after);assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(out,'editor-tests.json'),JSON.stringify({tones:12,bodies:checked,comparison:true,poses:[1,27,63],roster_unchanged:true,production_body_controls_hidden:true,errors},null,2)+'\n');console.log('PASS 12 swatches, six bodies, baked comparisons, poses/mirrors, production UI and unchanged live roster');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
