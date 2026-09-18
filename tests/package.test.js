'use strict';
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),vm=require('node:vm');const base=path.resolve(__dirname,'..');let count=0;const read=f=>fs.readFileSync(path.join(base,f),'utf8');
function check(name,fn){fn();count++;console.log('PASS '+name);}
check('HTML uses local scripts and styles',()=>{const s=read('index.html');assert.ok(s.includes('src="engine.js" defer'));assert.ok(s.includes('src="app.js" defer'));assert.ok(!/<script[^>]+src="https?:/i.test(s));});
check('All static HTML assets exist',()=>{for(const m of read('index.html').matchAll(/(?:src|href)="((?:assets\/|templates\/)[^"]+)"/g))assert.ok(fs.existsSync(path.join(base,m[1])),m[1]);});
check('Manifest is scoped to project directory',()=>{const m=JSON.parse(read('manifest.webmanifest'));assert.equal(m.start_url,'./');assert.equal(m.scope,'./');assert.equal(m.id,'./');});
check('Manifest icons exist',()=>{for(const i of JSON.parse(read('manifest.webmanifest')).icons)assert.ok(fs.existsSync(path.join(base,i.src)));});
check('Empty CSV and Excel templates are included',()=>{for(const f of ['homeflow-plan-template.csv','homeflow-actual-template.csv','Household_Budget_Import_Template.xlsx'])assert.ok(fs.existsSync(path.join(base,'templates',f)));});
check('CSV templates parse using real engine',()=>{const E=require('../engine.js');for(const f of ['homeflow-plan-template.csv','homeflow-actual-template.csv'])assert.doesNotThrow(()=>E.importCSV(read('templates/'+f),E.blank()));});
check('Private personal workbook is not packaged',()=>{const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(f=>f.isDirectory()?walk(path.join(d,f.name)):[path.join(d,f.name)]);const xlsx=walk(base).filter(f=>f.endsWith('.xlsx'));assert.equal(xlsx.length,1);assert.ok(xlsx[0].endsWith('Household_Budget_Import_Template.xlsx'));});
check('Service worker cache uses unique prefix',()=>{const s=read('sw.js');assert.ok(s.includes("PREFIX='homeflow-static-'"));assert.ok(s.includes('k.startsWith(PREFIX)&&k!==CACHE'));});
check('Service worker refuses other app paths and origins',()=>{const handlers={};vm.runInNewContext(read('sw.js'),{self:{addEventListener:(k,f)=>handlers[k]=f,registration:{scope:'https://example.test/monthly-housing-budget/'}},URL});for(const url of ['https://example.test/wealth-goal-planner/','https://other.test/monthly-housing-budget/']){let touched=false;handlers.fetch({request:{url,method:'GET'},respondWith:()=>touched=true});assert.equal(touched,false);}});
check('App does not clear other applications storage',()=>{const s=read('app.js');assert.ok(!s.includes('localStorage.clear('));assert.ok(s.includes("KEY='homeflow:budget:v1'"));});
check('Consent and no live-sync disclosure are included',()=>{const s=read('app.js');assert.ok(s.includes('shareConsent'));assert.ok(s.includes('there is no live synchronization'));assert.ok(s.includes('link is not encrypted'));});
check('Standalone generator defers execution until body exists',()=>{const s=read('index.html');assert.ok(s.includes('<div id="dialogBody"'));assert.ok(s.includes('src="app.js" defer'));});
console.log(`\n${count} package checks passed.`);
