// Renderer parity for native snapshots, including negative coordinates and airtime.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const folder=process.argv[2],root=path.resolve(__dirname,'..');
(async()=>{let browser;try{
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']});
 const context=await browser.newContext({offline:true}),page=await context.newPage(),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 await page.goto('about:blank?capture=1');await page.setContent(fs.readFileSync(path.join(root,'dist/deshi-dojo-visual.html'),'utf8'));
 await page.waitForFunction(()=>document.body.dataset.ready==='true');
 for(const c of JSON.parse(fs.readFileSync(path.join(folder,'cases.json'),'utf8'))){
  const url=await page.evaluate(code=>{dojoHost.clear();run('Scene.reset();'+code);dojoHost.render();return document.getElementById('game').toDataURL()},c.code);
  fs.writeFileSync(path.join(folder,c.name+'-browser.png'),Buffer.from(url.split(',')[1],'base64'));
 }
 if(errors.length||requests.length)throw Error(JSON.stringify({errors,requests}));
 }catch(e){console.error(e);process.exitCode=1}finally{if(browser)await browser.close()}})();
