// Read-only smoke test of the actual developer server; save tests use fixtures.
const {chromium}=require('playwright'),assert=require('assert/strict'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),roster=path.join(root,'assets/characters.json'),out=path.join(root,'docs/hair');
(async()=>{const before=crypto.createHash('sha256').update(fs.readFileSync(roster)).digest('hex');const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const page=await browser.newPage({viewport:{width:1400,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://localhost:8769/editor');await page.waitForFunction(()=>document.body.dataset.ready==='true');
 const catalog=await page.evaluate(()=>fetch('/api/characters').then(r=>r.json()).then(r=>r.catalog));assert.equal(await page.locator('#hair-cards button').count(),catalog.hair_styles.length);assert.equal(await page.locator('#hair-colors button').count(),14);
 await page.selectOption('#body','adult_female');await page.locator('[data-hair="medio_ondulado"]').click();await page.locator('[data-hair-color="branco"]').click();
 await page.waitForFunction(()=>window.editorVisual?.body==='adult_female'&&window.editorVisual.hair==='medio_ondulado'&&window.editorVisual.appearance.hair_color==='branco',{},{timeout:90000});
 await page.screenshot({path:path.join(out,'live-editor.png'),fullPage:true});
 await page.selectOption('#body','child');assert.equal(await page.inputValue('#hair'),'medio_ondulado');
 await page.waitForFunction(()=>window.editorVisual?.body==='child'&&window.editorVisual.hair==='medio_ondulado',{},{timeout:90000});
 await page.locator('[data-hair="default"]').click();assert(await page.locator('#hair_color').isDisabled());
  await page.selectOption('#body','adult');await page.locator('[data-hair="curto_classico"]').click();await page.selectOption('#hair_color','grisalho');await page.selectOption('#skin','clara');
  await page.waitForFunction(()=>window.editorVisual?.body==='adult'&&window.editorVisual.hair==='curto_classico'&&window.editorVisual.appearance.hair_color==='grisalho'&&window.editorVisual.appearance.skin==='clara',{},{timeout:90000});
  await page.selectOption('#belt','preta');await page.waitForFunction(()=>images[editorVisual.parts.belt.preta.right],{},{timeout:90000});
  await page.fill('#pose','15');await page.locator('#pose').dispatchEvent('input');await page.locator('#preview').screenshot({path:path.join(out,'reported-pose-corrected.png')});
  assert(await page.evaluate(()=>Object.values(images).every(image=>image.src.includes('?v='+editorVisual.revision))),'Preview images must carry the authored-source revision');
  await page.selectOption('#hair','buzz_uniforme');await page.waitForFunction(()=>editorVisual.hair==='buzz_uniforme',{},{timeout:90000});
  const contact=await page.evaluate(async()=>{
   const student=current(),baseline=await api('/api/preview',{...student,hair:'default',beard:'default'});
   const image=new Image();image.src=baseline.asset_base+baseline.visual.parts.body.right+'.png?v='+baseline.visual.revision;await image.decode();
   function pixels(visual,image){const f=visual.parts.body.frames[14],canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;const c=canvas.getContext('2d');c.drawImage(image,0,0);return [[110,11],[111,11],[113,12]].map(([x,y])=>[...c.getImageData(f.sx+x-f.x,f.sy+y-f.y,1,1).data])}
   return {original:pixels(baseline.visual,image),hair:pixels(editorVisual,images[editorVisual.parts.body.right])};
  });assert.deepEqual(contact.hair,contact.original,'Packed buzz cut must preserve raised fingers');
  await page.selectOption('#body','child_female');await page.selectOption('#hair','bob_cacheado');await page.selectOption('#hair_color','castanho_escuro');
  await page.waitForFunction(()=>editorVisual.body==='child_female'&&editorVisual.hair==='bob_cacheado'&&editorVisual.appearance.hair_color==='castanho_escuro',{},{timeout:90000});await page.fill('#pose','1');await page.locator('#pose').dispatchEvent('input');
  await page.screenshot({path:path.join(root,'docs/hair-catalog/editor-female.png'),fullPage:true});
 const after=crypto.createHash('sha256').update(fs.readFileSync(roster)).digest('hex');assert.equal(before,after);assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(out,'live-tests.json'),JSON.stringify({live_editor:true,white_hair:true,style_preserved_across_body_change:true,bald_option:true,roster_unchanged:true,errors},null,2)+'\n');console.log('PASS live hair editor, white palette, body switch, bald option, no roster writes');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
