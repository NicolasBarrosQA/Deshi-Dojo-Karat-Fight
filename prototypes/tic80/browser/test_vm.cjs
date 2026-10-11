const fs=require('fs'),vm=require('vm');
const path=require('path');
const html=fs.readFileSync(path.join(__dirname,'deshi-dojo-jogar.html'),'utf8');
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const context={console,HTMLDocument:function(){},URLSearchParams,Set,Uint8Array,Uint32Array,ArrayBuffer,TextEncoder,TextDecoder,location:{search:'?selftest=1'},performance:{now:()=>0}};
const canvas={getContext:()=>({fillRect(){},fillText(){}}),focus(){}};
const status={};context.document={body:{dataset:{}},readyState:'complete',getElementById:(id)=>id==='game'?canvas:id==='status'?status:{},querySelectorAll:()=>[],addEventListener(){}};
context.addEventListener=()=>{};context.window=context;context.globalThis=context;vm.createContext(context);
try{for(const script of scripts)vm.runInContext(script,context);console.log(status.textContent);if(context.document.body.dataset.test!=='passed')process.exitCode=1}catch(e){console.error(e.message);process.exitCode=1}
