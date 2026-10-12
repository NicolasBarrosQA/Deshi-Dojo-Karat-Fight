// Read-only smoke test of the actual developer server; save tests use fixtures.
const {chromium}=require('playwright'),assert=require('assert/strict'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),roster=path.join(root,'assets/characters.json'),out=path.join(root,'docs/hair');
(async()=>{const before=crypto.createHash('sha256').update(fs.readFileSync(roster)).digest('hex');const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const page=await browser.newPage({viewport:{width:1400,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://localhost:8769/editor');await page.waitForFunction(()=>document.body.dataset.ready==='true');
 assert.equal(await page.locator('#hair-cards button').count(),4);assert.equal(await page.locator('#hair-colors button').count(),14);
 await page.selectOption('#body','adult_female');await page.locator('[data-hair="medio_ondulado"]').click();await page.locator('[data-hair-color="branco"]').click();
 await page.waitForFunction(()=>window.editorVisual?.body==='adult_female'&&window.editorVisual.hair==='medio_ondulado'&&window.editorVisual.appearance.hair_color==='branco',{},{timeout:90000});
 await page.screenshot({path:path.join(out,'live-editor.png'),fullPage:true});
 await page.selectOption('#body','child');assert.equal(await page.inputValue('#hair'),'medio_ondulado');
 await page.waitForFunction(()=>window.editorVisual?.body==='child'&&window.editorVisual.hair==='medio_ondulado',{},{timeout:90000});
 await page.locator('[data-hair="default"]').click();assert(await page.locator('#hair_color').isDisabled());
 const after=crypto.createHash('sha256').update(fs.readFileSync(roster)).digest('hex');assert.equal(before,after);assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(out,'live-tests.json'),JSON.stringify({live_editor:true,white_hair:true,style_preserved_across_body_change:true,bald_option:true,roster_unchanged:true,errors},null,2)+'\n');console.log('PASS live hair editor, white palette, body switch, bald option, no roster writes');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
