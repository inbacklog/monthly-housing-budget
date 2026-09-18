'use strict';
const assert=require('node:assert/strict'),E=require('../engine.js'),P=require('../presets.js');let count=0;
function test(name,fn){fn();count++;console.log('PASS '+name);}
function line(o={}){return {id:'l1',type:'expense',category:'food',label:'Supermarket',amount:300,frequency:'monthly',member:'',funding:'cash',essential:true,subscription:false,active:true,month:'',...o};}
function fixture(){const s=E.blank('2026-09');s.lines=[line(),line({id:'salary',type:'income',label:'Salary',category:'income',amount:2000}),line({id:'sav',type:'saving',label:'Saving',category:'savings',amount:120}),line({id:'inv',type:'investment',label:'Investment',category:'savings',amount:50})];s.transactions=[{id:'t1',type:'expense',label:'Receipt',category:'food',member:'',funding:'cash',amount:12.34,date:'2026-09-01'}];s.closedMonths=['2026-09'];return E.validate(s);}
function apply(s,drafts){const rows=P.estimateRows(s,'el');return P.buildEstimate(E,s,rows,drafts,'el');}
test('Catalogue contains no preset prices or household data',()=>{assert.ok(P.items.length>60);for(const p of P.items){assert.ok(!('amount' in p));assert.ok(!('member' in p));assert.ok(E.CATEGORIES.some(c=>c[0]===p.category));assert.ok(E.TYPES.includes(p.type));}});
test('Preset IDs are unique',()=>assert.equal(new Set(P.items.map(p=>p.id)).size,P.items.length));
test('Common eight shortcuts all resolve',()=>P.popular.forEach(id=>assert.equal(P.get(id).type,'expense')));
test('Greek searches ignore accents and case',()=>assert.ok(P.search('ΡΕΥΜΑ').some(p=>p.id==='electricity')));
test('Water alias resolves in Greek and English',()=>{assert.ok(P.search('νερο').some(p=>p.id==='water'));assert.ok(P.search('water').some(p=>p.id==='water'));});
test('Provider aliases are search terms, not cost assumptions',()=>assert.equal(P.search('Netflix')[0].id,'streaming'));
test('Category filter and type filters apply together',()=>{assert.ok(P.search('','housing').every(p=>p.category==='housing'));assert.ok(P.search('','','income').every(p=>p.type==='income'));});
test('Blank search returns full expense catalogue',()=>assert.equal(P.search().length,P.items.filter(p=>p.type==='expense').length));
test('Arbitrary new labels remain unclassified until user chooses',()=>assert.equal(P.match(line({label:'Unrelated item'})),undefined));
test('Original bilingual grocery label is recognized',()=>assert.equal(P.match(line({label:'Σούπερ μάρκετ / Groceries'})).id,'groceries'));
test('Original bilingual rent is recognized',()=>assert.equal(P.match(line({category:'housing',label:'Ενοίκιο / Rent'})).id,'rent'));
test('Legacy water label remains recognized',()=>assert.equal(P.match(line({category:'housing',label:'Νερό'})).id,'water'));
test('Commas and decimal points parse identically',()=>{assert.equal(P.readAmount('1234,50'),1234.5);assert.equal(P.readAmount('1234.50'),1234.5);});
test('Blank and explicit zero are distinct',()=>{assert.equal(P.readAmount(' '),null);assert.equal(P.readAmount('0'),0);});
test('Invalid signs, grouping, exponent, precision and limits reject',()=>{for(const s of ['-2','1.000,50','1,234.50','1e6','NaN','123.456','1000000001'])assert.throws(()=>P.readAmount(s),s);});
test('New drafts remain zero-price-free until entered',()=>{const s=E.blank('2026-09'),r=P.estimateRows(s,'el');assert.ok(r.every(x=>x.amount===null));assert.deepEqual(apply(s,{}).state,s);});
test('New positive rows add atomically without mutating input',()=>{const s=fixture(),before=E.clone(s),r=apply(s,{'new:water':{amount:'120',frequency:'yearly'},'new:rent':{amount:'700',frequency:'monthly'}});assert.deepEqual(s,before);assert.equal(r.added,2);assert.equal(r.updated,0);assert.equal(E.budget(r.state).expenses,1010);});
test('New blank and zero rows are not persisted',()=>{const s=fixture(),r=apply(s,{'new:water':{amount:'',frequency:'yearly'},'new:rent':{amount:'0',frequency:'monthly'}});assert.deepEqual(r.state,s);});
test('Recognized existing rows suppress duplicate blank presets',()=>{const r=P.estimateRows(fixture(),'el');assert.ok(!r.some(x=>x.key==='new:groceries'));assert.ok(r.some(x=>x.key==='existing:l1'));});
test('Existing amount edit retains ID and does not add a row',()=>{const s=fixture(),r=apply(s,{'existing:l1':{amount:'325,50',frequency:'monthly'}});assert.equal(r.updated,1);assert.equal(r.added,0);assert.equal(r.state.lines.length,s.lines.length);assert.equal(r.state.lines[0].amount,325.5);});
test('Existing zero is a deliberate update, blank is no change',()=>{const s=fixture();assert.equal(apply(s,{'existing:l1':{amount:'0',frequency:'monthly'}}).state.lines[0].amount,0);assert.deepEqual(apply(s,{'existing:l1':{amount:'',frequency:'monthly'}}).state,s);});
test('Income, savings, investment, actuals and closed-month flags survive',()=>{const s=fixture(),r=apply(s,{'new:water':{amount:'20',frequency:'monthly'}});assert.deepEqual(r.state.lines.slice(0,4),s.lines);assert.deepEqual(r.state.transactions,s.transactions);assert.deepEqual(r.state.closedMonths,s.closedMonths);assert.deepEqual(r.state.settings,s.settings);});
test('Paused, assigned and benefit-funded rows retain flags',()=>{const s=fixture();s.lines[0]={...s.lines[0],member:'member1',active:false,funding:'benefit',subscription:true};const r=apply(s,{'existing:l1':{amount:'250',frequency:'yearly'}}).state.lines[0];for(const k of ['id','member','active','funding','subscription','essential'])assert.equal(r[k],s.lines[0][k]);});
test('One-off month is retained on updates',()=>{const s=fixture();s.lines[0].frequency='once';s.lines[0].month='2026-12';assert.equal(apply(s,{'existing:l1':{amount:'550',frequency:'once'}}).state.lines[0].month,'2026-12');});
test('Invalid batch is not partially committed',()=>{const s=fixture(),before=E.clone(s);assert.throws(()=>apply(s,{'new:rent':{amount:'700',frequency:'monthly'},'new:water':{amount:'bad',frequency:'monthly'}}));assert.deepEqual(s,before);});
test('Foreign and removed row identifiers cannot overwrite a record',()=>{const s=fixture(),rows=P.estimateRows(s,'el');s.lines.shift();assert.throws(()=>P.buildEstimate(E,s,rows,{'existing:l1':{amount:'20',frequency:'monthly'}},'el'));});
test('Custom categories are preserved in quick view',()=>{const s=fixture();s.lines[0].category='My custom';assert.equal(P.estimateRows(s,'en')[0].category,'My custom');});
test('Same template across people keeps separate existing rows',()=>{const s=fixture();s.lines.push(line({id:'l2',member:'member1',amount:75}));const rows=P.estimateRows(s,'el');assert.equal(rows.filter(r=>r.preset?.id==='groceries').length,2);assert.equal(apply(s,{'existing:l1':{amount:'400',frequency:'monthly'}}).state.lines.find(x=>x.id==='l2').amount,75);});
test('Untouched higher precision values from old JSON are preserved',()=>{const s=fixture();s.lines[0].amount=10.12345;assert.deepEqual(apply(s,{'existing:l1':{amount:'10.12345',frequency:'monthly'}}).state,s);});
test('Updated states round-trip through existing schema and CSV',()=>{const r=apply(fixture(),{'new:water':{amount:'24,65',frequency:'monthly'}});assert.deepEqual(E.validate(r.state),r.state);assert.equal(E.importCSV(E.exportCSV(r.state),E.blank()).state.lines.at(-1).amount,24.65);});
console.log('\n'+count+' preset/batch test groups passed.');
