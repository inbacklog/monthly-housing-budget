/* Only this app's URL scope and cache are managed. Never purge another app. */
'use strict';
const PREFIX='homeflow-'+new URL(self.registration.scope).pathname+'-',CACHE=PREFIX+'v1.2.0';
const FILES=['./','index.html','styles.css','budget-engine.js','data.js','xlsx-reader.js','io.js','scenarios.js','app.js','manifest.webmanifest','assets/icon.svg','assets/icon-192.png','assets/icon-512.png','assets/buymeacoffee-qr.png','assets/wallet-of-satoshi-qr.png','templates/Homeflow_Template.xlsx','templates/Homeflow_Template.csv'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith(PREFIX)&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url),scope=new URL(self.registration.scope);if(e.request.method!=='GET'||u.origin!==scope.origin||!u.pathname.startsWith(scope.pathname))return;
 if(e.request.mode==='navigate'){e.respondWith(fetch(e.request).then(async r=>{if(r.ok){const c=await caches.open(CACHE);await c.put('index.html',r.clone()).catch(()=>{});}return r;}).catch(()=>caches.open(CACHE).then(c=>c.match('index.html'))));return;}
 e.respondWith(caches.open(CACHE).then(async c=>{const cached=await c.match(e.request);if(cached)return cached;return fetch(e.request).then(async r=>{if(r.ok)await c.put(e.request,r.clone()).catch(()=>{});return r;});}));
});
