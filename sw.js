/* Only Homeflow assets: never delete other apps' caches on this origin. */
const CACHE='homeflow-static-v1.1.1',PREFIX='homeflow-static-';
const FILES=['./','./index.html','./styles.css','./engine.js','./app.js','./presets.js','./manifest.webmanifest','./assets/icon.svg','./assets/icon-192.png','./assets/icon-512.png','./assets/buymeacoffee-qr.png','./assets/wallet-of-satoshi-qr.png','./templates/Household_Budget_Import_Template.xlsx'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith(PREFIX)&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{const u=new URL(event.request.url),base=new URL(self.registration.scope);if(event.request.method!=='GET'||u.origin!==base.origin||!u.pathname.startsWith(base.pathname))return;
 const rel=u.pathname.slice(base.pathname.length);if(!FILES.some(f=>f.slice(2)===rel))return;
 const key=new URL(rel||'./',base).href;
 event.respondWith(fetch(event.request).then(response=>{if(response.ok){const copy=response.clone();event.waitUntil(caches.open(CACHE).then(c=>c.put(key,copy)));}return response;}).catch(()=>caches.open(CACHE).then(c=>c.match(key))));
});
