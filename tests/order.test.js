'use strict';
const E=require('../engine.js'),assert=require('node:assert/strict');let n=0;
function test(name,fn){fn();console.log('PASS '+name);n++;}
const rows=[{id:'a',label:'Same',amount:1},{id:'b',label:'Same',amount:2},{id:'c',label:'C',amount:3},{id:'d',label:'D',amount:4},{id:'e',label:'E',amount:5}];
const ids=arr=>arr.map(x=>x.id);
test('First to last preserves all records',()=>{const out=E.reorderVisible(rows,ids(rows),'a',4);assert.deepEqual(ids(out),['b','c','d','e','a']);assert.equal(out.at(-1).amount,1);});
test('Last to first',()=>assert.deepEqual(ids(E.reorderVisible(rows,ids(rows),'e',0)),['e','a','b','c','d']));
test('Move to an exact middle position',()=>assert.deepEqual(ids(E.reorderVisible(rows,ids(rows),'b',3)),['a','c','d','b','e']));
test('Same-position operation leaves content unchanged',()=>assert.deepEqual(E.reorderVisible(rows,ids(rows),'b',1),rows));
test('Filtered moves preserve hidden slots',()=>assert.deepEqual(ids(E.reorderVisible(rows,['a','c','e'],'a',2)),['c','b','e','d','a']));
test('Duplicate descriptions are independent IDs',()=>{const out=E.reorderVisible(rows,ids(rows),'a',1);assert.equal(out[0].amount,2);assert.equal(out[1].amount,1);});
test('Input arrays are never mutated',()=>{const copy=JSON.stringify(rows),visible=ids(rows);E.reorderVisible(rows,visible,'b',0);assert.equal(JSON.stringify(rows),copy);assert.deepEqual(visible,ids(rows));});
test('Unknown row or scope ID is rejected',()=>{assert.throws(()=>E.reorderVisible(rows,ids(rows),'x',0));assert.throws(()=>E.reorderVisible(rows,['a','missing'],'a',0));});
test('Duplicate scope or source ID is rejected',()=>{assert.throws(()=>E.reorderVisible(rows,['a','a'],'a',0));assert.throws(()=>E.reorderVisible([...rows,rows[0]],ids(rows),'a',0));});
test('Invalid destinations rejected without clamping',()=>{for(const to of [-1,5,1.2,NaN,'2'])assert.throws(()=>E.reorderVisible(rows,ids(rows),'a',to));});
test('Old v1 JSON without ordering metadata remains readable',()=>{const p=E.demo('2026-09');delete p.actualManualMonths;assert.deepEqual(E.validate(p).actualManualMonths,[]);});
test('Manual actual order survives validation and JSON',()=>{const p=E.blank('2026-09');p.actualManualMonths=['2026-09'];assert.deepEqual(E.validate(JSON.parse(JSON.stringify(p))).actualManualMonths,['2026-09']);});
test('Invalid/duplicate manual months are filtered',()=>{const p=E.blank();p.actualManualMonths=['bad','2026-09','2026-09'];assert.deepEqual(E.validate(p).actualManualMonths,['2026-09']);});
test('Sharing without actuals removes actual ordering metadata',()=>{const p=E.blank();p.actualManualMonths=['2026-09'];assert.deepEqual(E.anonymize(p,false).actualManualMonths,[]);});
test('Sharing with actuals preserves manual order metadata',()=>{const p=E.blank();p.actualManualMonths=['2026-09'];assert.deepEqual(E.anonymize(p,true).actualManualMonths,['2026-09']);});
test('Budget and forecast calculations unchanged by reordering',()=>{
 const p=E.demo('2026-09'),before=E.budget(p),forecast=E.forecast(p);p.lines=E.reorderVisible(p.lines,ids(p.lines),p.lines[0].id,p.lines.length-1);const after=E.budget(p),f=E.forecast(p);
 for(const k of ['income','expenses','saving','investment','essential','discretionary','subscriptions','unassigned'])assert.ok(Math.abs(before[k]-after[k])<1e-8,k);
 forecast.forEach((r,i)=>assert.ok(Math.abs(r.cash-f[i].cash)<1e-8));
});
test('100 deterministic moves preserve every untouched value',()=>{let current=rows;for(let i=0;i<100;i++){const scope=ids(current).filter((_,j)=>(j+i)%2===0);const before=JSON.stringify(rows);current=E.reorderVisible(current,scope,scope[0],scope.length-1);assert.deepEqual([...current].sort((a,b)=>a.id.localeCompare(b.id)),rows);assert.equal(JSON.stringify(rows),before);}});
console.log(`\n${n} row-order engine checks passed.`);
