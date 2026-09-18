'use strict';
const assert=require('node:assert/strict'),E=require('../engine.js');
let n=0;function test(name,fn){fn();n++;console.log('PASS '+name);}
const rows=[{id:'a',amount:11},{id:'b',amount:23},{id:'c',amount:37},{id:'d',amount:41}];
const ids=x=>x.map(r=>r.id);
test('Move first to last',()=>assert.deepEqual(ids(E.reorder(rows,ids(rows),'a',3)),['b','c','d','a']));
test('Move last to first',()=>assert.deepEqual(ids(E.reorder(rows,ids(rows),'d',0)),['d','a','b','c']));
test('Move to middle',()=>assert.deepEqual(ids(E.reorder(rows,ids(rows),'a',2)),['b','c','a','d']));
test('Hidden entries keep their original slots',()=>assert.deepEqual(ids(E.reorder(rows,['a','c'],'c',0)),['c','b','a','d']));
test('Input array and records are unchanged',()=>{const before=JSON.stringify(rows);E.reorder(rows,ids(rows),'a',3);assert.equal(JSON.stringify(rows),before);});
test('Identity and amounts are preserved',()=>{const r=E.reorder(rows,ids(rows),'c',0);r.forEach(x=>assert.strictEqual(x,rows.find(y=>y.id===x.id)));assert.equal(r.reduce((s,x)=>s+x.amount,0),112);});
test('Same position is a no-op',()=>assert.deepEqual(E.reorder(rows,ids(rows),'b',1),rows));
test('Single visible row is a no-op',()=>assert.deepEqual(E.reorder(rows,['b'],'b',0),rows));
test('Out-of-range positions reject',()=>{for(const p of [-1,4,0.5,NaN])assert.throws(()=>E.reorder(rows,ids(rows),'a',p));});
test('Invalid identifiers reject',()=>{assert.throws(()=>E.reorder(rows,['a','a'],'a',0));assert.throws(()=>E.reorder(rows,['x'],'x',0));assert.throws(()=>E.reorder(rows,['b'],'a',0));});
test('Order survives v1 schema and anonymized sharing',()=>{let p=E.demo('2026-09');const last=p.lines.at(-1).id;p.lines=E.reorder(p.lines,ids(p.lines),last,0);const v=E.validate(JSON.parse(JSON.stringify(p)));assert.equal(v.lines[0].id,last);const anon=E.anonymize(v,false,false);assert.deepEqual(anon.lines.map(r=>r.amount),v.lines.map(r=>r.amount));});
test('Budget and forecast totals are invariant',()=>{const p=E.demo('2026-09'),b=E.budget(p),f=E.forecast(p);const q=E.clone(p);q.lines=E.reorder(q.lines,ids(q.lines),q.lines.at(-1).id,0);const qb=E.budget(q);for(const k of ['income','expenses','saving','investment','unassigned'])assert.ok(Math.abs(b[k]-qb[k])<1e-8);assert.deepEqual(E.forecast(q),f);});
console.log(`\n${n} ordering test groups passed.`);
