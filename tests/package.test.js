/* Static integrity + isolated service-worker policy tests (not a browser lifecycle test). */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const base=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(base,f),'utf8');
let passed=0;const failures=[];async function test(n,f){try{await f();passed++;console.log('PASS',n);}catch(e){failures.push(n+': '+e.message);console.error('FAIL',n,e.message);}}
(async()=>{
const html=read('index.html'),js=read('app.js'),manifest=JSON.parse(read('manifest.webmanifest'));
await test('All local entry-point scripts are present and syntactically valid',()=>{for(const f of [...html.matchAll(/<script defer src="([^"]+)"/g)].map(m=>m[1])){new vm.Script(read(f));assert.ok(!f.startsWith('http'));}});
await test('No third-party runtime script or style CDN',()=>{assert.ok(!/<(?:script|link)[^>]*(?:src|href)=["']https?:/i.test(html));});
await test('All statically referenced local images and styles exist',()=>{for(const [,f] of html.matchAll(/(?:src|href)="((?:assets\/|styles\.css)[^"]*)"/g))assert.ok(fs.existsSync(path.join(base,f)),f);});
await test('Manifest starts and remains in this project directory',()=>{assert.equal(manifest.scope,'./');assert.equal(manifest.start_url,'./');assert.equal(manifest.id,'./');});
await test('No Jekyll build is required',()=>assert.ok(fs.existsSync(path.join(base,'.nojekyll'))));
await test('Public template files exist and XLSX is a ZIP',()=>{const f=fs.readFileSync(path.join(base,'templates/Homeflow_Template.xlsx'));assert.equal(f.subarray(0,2).toString(),'PK');assert.ok(read('templates/Homeflow_Template.csv').includes('record_type'));});
await test('App data keys isolated to Homeflow namespace',()=>{assert.ok(js.includes("homeflow:state:v1"));assert.ok(js.includes("homeflow:prefs:v1"));assert.ok(!js.includes('localStorage.clear('));});
await test('Support links use expected explicit destinations',()=>{assert.ok(html.includes('https://buymeacoffee.com/inbacklog'));assert.ok(html.includes('lightning:doableshrimp862@walletofsatoshi.com'));});
await test('External new-tab links set noopener noreferrer',()=>{for(const [tag] of html.matchAll(/<a\b[^>]*target="_blank"[^>]*>/g))assert.ok(tag.includes('noopener noreferrer'));});
await test('Only blank template XLSX included',()=>{const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(d,e.name)):[path.relative(base,path.join(d,e.name))]);assert.deepEqual(walk(base).filter(f=>f.endsWith('.xlsx')),['templates/Homeflow_Template.xlsx']);});
const listeners={},store=new Map(),deleted=[],precached=[];let offline=false,claims=0;
const cache={addAll:async a=>{precached.push(...a);for(const p of a)store.set(p,'CACHED');},match:async r=>store.get(typeof r==='string'?r:r.url),put:async(r,v)=>store.set(typeof r==='string'?r:r.url,v)};
const own='homeflow-/monthly-housing-budget/-v1.2.0';const context={URL,self:{registration:{scope:'https://example.test/monthly-housing-budget/'},addEventListener:(t,f)=>listeners[t]=f,skipWaiting:async()=>{},clients:{claim:async()=>claims++}},caches:{open:async()=>cache,keys:async()=>[own,'homeflow-/monthly-housing-budget/-v0','wealth-goal-planner-cache','homeflow-/another-app/-v1'],delete:async k=>{deleted.push(k);return true;}},fetch:async()=>{if(offline)throw Error('offline');return{ok:true,clone:()=>({body:'FRESH'})};}};
vm.runInNewContext(read('sw.js'),context);
async function lifecycle(type){let promise;listeners[type]({waitUntil:p=>promise=p});await promise;}
await test('SW installation references only real files in this package',async()=>{await lifecycle('install');for(const f of precached)assert.ok(f==='./'||fs.existsSync(path.join(base,f)),f);});
await test('SW precaches both QR codes and templates',()=>{assert.ok(precached.includes('assets/wallet-of-satoshi-qr.png'));assert.ok(precached.includes('templates/Homeflow_Template.xlsx'));});
await test('Activation purges only this project old cache',async()=>{await lifecycle('activate');assert.deepEqual(deleted,['homeflow-/monthly-housing-budget/-v0']);assert.equal(claims,1);});
function request(url,mode='cors',method='GET'){let promise;listeners.fetch({request:{url,mode,method},respondWith:p=>promise=p});return promise;}
await test('SW ignores external domains',()=>{assert.equal(request('https://other.test/data'),undefined);});
await test('SW ignores another app on same origin',()=>{assert.equal(request('https://example.test/wealth-goal-planner/index.html'),undefined);});
await test('SW ignores non-GET requests',()=>{assert.equal(request('https://example.test/monthly-housing-budget/file','cors','POST'),undefined);});
await test('Navigation awaits a refreshed offline document copy',async()=>{await request('https://example.test/monthly-housing-budget/','navigate');assert.deepEqual(store.get('index.html'),{body:'FRESH'});});
await test('Offline navigation uses cached app document',async()=>{offline=true;assert.deepEqual(await request('https://example.test/monthly-housing-budget/','navigate'),{body:'FRESH'});});
await test('Cached assets remain available during simulated offline',async()=>{store.set('https://example.test/monthly-housing-budget/app.js','JS');assert.equal(await request('https://example.test/monthly-housing-budget/app.js'),'JS');});
console.log(JSON.stringify({passed,failed:failures.length,failures},null,2));if(failures.length)process.exitCode=1;
})();
