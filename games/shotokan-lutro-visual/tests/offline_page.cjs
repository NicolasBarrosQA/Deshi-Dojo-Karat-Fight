// Load the shipped standalone file directly. Large HTML must not be copied
// through Playwright's setContent/IPC JSON buffer (it can crash the renderer).
const path=require('path'),{pathToFileURL}=require('url');
module.exports=(page,manual=true,file=path.resolve(__dirname,'../dist/deshi-dojo-visual.html'))=>
 page.goto(pathToFileURL(file).href+(manual?'?capture=1':''),{waitUntil:'domcontentloaded',timeout:90000});
