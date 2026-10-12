const {chromium}=require('playwright'),assert=require('assert/strict'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
const page=await browser.newPage({viewport:{width:1280,height:1200}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
await page.goto((process.env.DOJO_EDITOR_URL||'http://localhost:8769')+'/editor');await page.waitForFunction(()=>document.body.dataset.ready==='true');
for(const age of ['adult','teen','child']){
 const body=age+'_female';await page.selectOption('#roster','demo-'+age+'-female');await page.waitForFunction(body=>window.editorVisual?.body===body,body,{timeout:90000});
 assert.equal(await page.inputValue('#body'),body);assert.equal(await page.evaluate(()=>current().body),body);
 const text=await page.locator('#body option:checked').textContent();assert(text.includes('feminino'));
 await page.fill('#pose','67');await page.locator('#pose').dispatchEvent('input');await page.screenshot({path:path.join(root,'docs/female-bodies',body+'-editor.png'),fullPage:true});
}
assert.deepEqual(errors,[]);fs.writeFileSync(path.join(root,'docs/female-bodies/editor-tests.json'),JSON.stringify({female_models:3,compiled_preview_and_exported_body:3,errors},null,2)+'\n');console.log('Creator: all 3 female models, compiled previews and exported configs passed');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
