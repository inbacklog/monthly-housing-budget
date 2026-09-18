/* Homeflow: pure, deterministic budget calculations. No IO or remote services. */
(function(root,factory){'use strict';const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.BudgetEngine=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const CATEGORIES=[
 ['housing','Σπίτι','Housing'],['food','Τρόφιμα & φαγητό','Food'],['transportation','Μετακινήσεις','Transportation'],
 ['children','Παιδιά','Children'],['entertainment','Ψυχαγωγία','Entertainment'],['gifts','Δώρα & προσφορές','Gifts and charity'],
 ['insurance','Ασφάλιση','Insurance'],['loans','Δάνεια & κάρτες','Loans'],['personal','Προσωπική φροντίδα','Personal care'],
 ['pets','Κατοικίδια','Pets'],['savings','Αποταμίευση','Savings'],['subscriptions','Συνδρομές','Subscriptions'],
 ['taxes','Φόροι','Taxes'],['income','Εισοδήματα','Income'],['health','Υγεία','Health'],['travel','Ταξίδια','Travel'],['other','Άλλα','Other']
];
const TYPES=['income','expense','saving','investment'],FREQ=['monthly','yearly','quarterly','weekly','salary14','once'];
const MAX_ITEMS=10000,MAX_AMOUNT=1e9;
function clone(x){return JSON.parse(JSON.stringify(x));}
function id(){return 'i'+Date.now().toString(36)+Math.random().toString(36).slice(2,10);}
function monthNow(){const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0');}
function isMonth(s){return typeof s==='string'&&/^\d{4}-(0[1-9]|1[0-2])$/.test(s)&&Number(s.slice(0,4))>=1900&&Number(s.slice(0,4))<=2199;}
function isDate(s){if(typeof s!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(s)||!isMonth(s.slice(0,7)))return false;const d=new Date(s+'T12:00:00Z');return Number.isFinite(d.valueOf())&&d.toISOString().slice(0,10)===s;}
function addMonth(s,n){const [y,m]=s.split('-').map(Number);const d=new Date(Date.UTC(y,m-1+n,1));return d.toISOString().slice(0,7);}
function blank(month=monthNow()){return {version:1,title:'',month,members:[{id:'member1',name:'',role:'adult'}],lines:[],transactions:[],closedMonths:[],settings:{openingCash:0,emergencyFund:0,emergencyMonths:3,extraSaving:0,investPercent:0,annualIncomeGrowth:0,annualExpenseGrowth:0,horizon:12}};}
function text(x,max=100){if(typeof x!=='string'||x.length>max)throw Error('Invalid text / μη έγκυρο κείμενο');return x;}
function num(x,min=0,max=MAX_AMOUNT){if(typeof x!=='number'||!Number.isFinite(x)||x<min||x>max)throw Error('Invalid amount / μη έγκυρο ποσό');return x;}
function bool(x){if(typeof x!=='boolean')throw Error('Invalid boolean');return x;}
function validate(input){
 if(!input||typeof input!=='object'||Array.isArray(input)||input.version!==1)throw Error('Not a Homeflow v1 file / μη συμβατό αρχείο');
 const p=blank();p.title=text(input.title??'');if(!isMonth(input.month))throw Error('Invalid month / μη έγκυρος μήνας');p.month=input.month;
 if(!Array.isArray(input.members)||!input.members.length||input.members.length>1000)throw Error('Household requires 1–1000 members');
 p.members=input.members.map(m=>({id:text(m.id,80),name:text(m.name??'',80),role:['adult','child','other'].includes(m.role)?m.role:'other'}));
 const ids=new Set(p.members.map(m=>m.id));if(ids.size!==p.members.length||ids.has(''))throw Error('Duplicate / missing member IDs');
 for(const arr of ['lines','transactions']){
  if(!Array.isArray(input[arr])||input[arr].length>MAX_ITEMS)throw Error('Too many records (max 10,000 per list)');
  const seen=new Set();p[arr]=input[arr].map(l=>{
   const o={id:text(l.id,80),type:text(l.type,20),label:text(l.label,160),category:text(l.category,80),member:text(l.member||'',80),amount:num(l.amount),funding:l.funding||'cash'};
   if(!o.id||seen.has(o.id))throw Error('Duplicate / missing record IDs');seen.add(o.id);
   if(!TYPES.includes(o.type)||!o.label.trim()||!o.category.trim()||(o.member&&!ids.has(o.member)))throw Error('Invalid record type, label, category or member');
   if(!['cash','benefit','mixed'].includes(o.funding)||((o.type==='saving'||o.type==='investment')&&o.funding!=='cash')||(o.type!=='income'&&o.funding==='mixed'))throw Error('Invalid funding / μη έγκυρη πηγή');
   if(arr==='lines'){
    o.frequency=l.frequency;if(!FREQ.includes(o.frequency)||o.frequency==='salary14'&&o.type!=='income')throw Error('Invalid frequency');
    o.month=l.month||'';if(o.frequency==='once'&&!isMonth(o.month))throw Error('One-off entry needs a month');
    o.essential=bool(l.essential??false);o.subscription=bool(l.subscription??false);o.active=bool(l.active??true);
    if(o.subscription&&o.type!=='expense')throw Error('Subscription must be an expense');
   }else{if(!isDate(l.date))throw Error('Invalid transaction date / μη έγκυρη ημερομηνία');o.date=l.date;}
   return o;
  });
 }
 p.closedMonths=Array.isArray(input.closedMonths)?[...new Set(input.closedMonths.filter(isMonth))]:[];
 if(p.closedMonths.length>3600)throw Error('Too many months');
 const s=input.settings||{};for(const k of ['openingCash','emergencyFund','extraSaving'])p.settings[k]=num(s[k]??0);
 p.settings.emergencyMonths=num(s.emergencyMonths??3,0,36);p.settings.investPercent=num(s.investPercent??0,0,100);
 for(const k of ['annualIncomeGrowth','annualExpenseGrowth'])p.settings[k]=num(s[k]??0,-50,50);
 p.settings.horizon=num(s.horizon??12,1,120);if(!Number.isInteger(p.settings.horizon))throw Error('Horizon needs whole months');
 return p;
}
function equivalent(l,month){if(!l.active)return 0;const factors={monthly:1,yearly:1/12,quarterly:1/3,weekly:52/12,salary14:14/12};return l.frequency==='once'?(l.month===month?l.amount:0):l.amount*factors[l.frequency];}
function summarize(records,value){
 const s={income:0,expenses:0,saving:0,investment:0,benefitIncome:0,benefitExpenses:0,mixedIncome:0,essential:0,discretionary:0,subscriptions:0,categories:Object.create(null),members:Object.create(null)};
 for(const l of records){const a=value(l);if(!a)continue;
  if(l.funding==='mixed'){s.mixedIncome+=a;continue;}
  if(l.funding==='benefit'){if(l.type==='income')s.benefitIncome+=a;else s.benefitExpenses+=a;continue;}
  if(l.type==='income')s.income+=a;if(l.type==='saving')s.saving+=a;if(l.type==='investment')s.investment+=a;
  if(l.type==='expense'){s.expenses+=a;s.categories[l.category]=(s.categories[l.category]||0)+a;if(l.essential)s.essential+=a;else s.discretionary+=a;if(l.subscription)s.subscriptions+=a;}
  const member=l.member||'shared';if(!s.members[member])s.members[member]={income:0,expenses:0};if(l.type==='income')s.members[member].income+=a;else if(l.type==='expense')s.members[member].expenses+=a;
 }
 s.afterLiving=s.income-s.expenses;s.unassigned=s.afterLiving-s.saving-s.investment;s.benefitBalance=s.benefitIncome-s.benefitExpenses;
 return s;
}
function allocation(s,settings){const extraSaving=Math.min(Math.max(0,s.unassigned),settings.extraSaving);const available=Math.max(0,s.unassigned-extraSaving);const extraInvestment=available*settings.investPercent/100;return {extraSaving,available,extraInvestment,remaining:s.unassigned-extraSaving-extraInvestment,investment:s.investment+extraInvestment,feasible:s.unassigned>=0,requestedSaving:settings.extraSaving};}
function budget(p,month=p.month){const s=summarize(p.lines,l=>equivalent(l,month));return {...s,allocation:allocation(s,p.settings)};}
function actual(p,month=p.month){const tx=p.transactions.filter(l=>l.date.slice(0,7)===month),s=summarize(tx,l=>l.amount);return {...s,count:tx.length,closed:p.closedMonths.includes(month),hasIncome:tx.some(l=>l.type==='income'&&l.funding==='cash'),hasExpense:tx.some(l=>l.type==='expense'&&l.funding==='cash')};}
function forecast(p,options={}){
 const settings={...p.settings,...options};let cash=settings.openingCash,saved=0,invested=0;const rows=[];
 for(let i=0;i<settings.horizon;i++){
  const month=addMonth(p.month,i),s=summarize(p.lines,l=>{let a=equivalent(l,month);if(l.frequency!=='once'&&(l.type==='income'||l.type==='expense'))a*=Math.pow(1+settings[l.type==='income'?'annualIncomeGrowth':'annualExpenseGrowth']/100,i/12);if(l.type==='expense'&&l.funding==='cash'&&!l.essential)a*=1-(options.flexCut||0)/100;if(l.type==='income'&&l.funding==='cash')a*=1-(options.incomeCut||0)/100;return a;});
  const alloc=allocation(s,settings);cash+=alloc.remaining;saved+=s.saving+alloc.extraSaving;invested+=alloc.investment;
  rows.push({month,income:s.income,expenses:s.expenses,savings:s.saving+alloc.extraSaving,investment:alloc.investment,remaining:alloc.remaining,cash,totalSaved:saved,totalInvested:invested,unfunded:Math.max(0,-s.unassigned)});
 }
 return rows;
}
// RFC-4180 style CSV parser: quotes, escaped quotes, BOM, comma/semicolon delimiter.
function parseCSV(input){if(typeof input!=='string'||input.length>2e6)throw Error('CSV is too large (2 MB text limit)');const str=input.replace(/^\uFEFF/,'');const head=str.split(/\r?\n/,1)[0];const delimiter=head.includes(';')?';':',';const rows=[];let row=[],cell='',quoted=false;
 for(let i=0;i<str.length;i++){const ch=str[i];if(ch==='"'){if(quoted&&str[i+1]==='"'){cell+='"';i++;}else quoted=!quoted;}else if(ch===delimiter&&!quoted){row.push(cell);cell='';}else if((ch==='\n'||ch==='\r')&&!quoted){if(ch==='\r'&&str[i+1]==='\n')i++;row.push(cell);if(row.some(v=>v.trim()))rows.push(row);row=[];cell='';}else cell+=ch;}
 if(quoted)throw Error('CSV: unclosed quote');row.push(cell);if(row.some(v=>v.trim()))rows.push(row);if(rows.length>MAX_ITEMS+1)throw Error('Too many CSV rows');return rows;
}
const CSV_COLS=['kind','date','type','description','category','amount','frequency','member','essential','subscription','funding'];
function importCSV(input,base){const rows=parseCSV(input);if(!rows.length)throw Error('Empty CSV');const headers=rows.shift().map(x=>x.trim().toLowerCase());if(headers.length!==CSV_COLS.length||!CSV_COLS.every((h,i)=>headers[i]===h))throw Error('Use the Homeflow CSV template headers / χρησιμοποίησε το πρότυπο');
 const p=clone(base),incoming={lines:[],transactions:[]};let newMembers=0;
 const yes=x=>{const v=x.trim().toLowerCase();if(!['true','false','1','0',''].includes(v))throw Error('Boolean must be true or false');return v==='true'||v==='1';};
 rows.forEach((r,i)=>{try{
  if(r.length!==headers.length)throw Error('Wrong column count');const d=Object.fromEntries(headers.map((h,j)=>[h,r[j].trim()]));
  if(!['plan','actual'].includes(d.kind))throw Error('kind must be plan or actual');
  if(!/^(?:\d+(?:[.,]\d{1,2})?)$/.test(d.amount))throw Error('amount must be nonnegative, no thousands separator, up to 2 decimals');
  let member='';if(d.member){let m=p.members.find(m=>m.name===d.member);if(!m){m={id:id(),name:d.member,role:'other'};p.members.push(m);newMembers++;}member=m.id;}
  const item={id:id(),type:d.type,label:d.description,category:d.category,amount:Number(d.amount.replace(',','.')),member,funding:d.funding||'cash'};
  if(d.kind==='plan'){Object.assign(item,{frequency:d.frequency||'monthly',month:d.date,essential:yes(d.essential),subscription:yes(d.subscription),active:true});incoming.lines.push(item);}else{item.date=d.date;incoming.transactions.push(item);}
 }catch(e){throw Error('CSV row '+(i+2)+': '+e.message);}});
 p.lines.push(...incoming.lines);p.transactions.push(...incoming.transactions);const valid=validate(p);return {state:valid,lines:incoming.lines.length,transactions:incoming.transactions.length,newMembers};
}
function csvEscape(v){let s=String(v??'');if(/^[\s]*[=+\-@]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';}
function exportCSV(p){const rows=[CSV_COLS];for(const kind of ['plan','actual'])for(const l of p[kind==='plan'?'lines':'transactions'].filter(l=>kind==='actual'||l.active))rows.push([kind,kind==='plan'?(l.month||''):l.date,l.type,l.label,l.category,l.amount,kind==='plan'?l.frequency:'',l.member?(p.members.find(m=>m.id===l.member)?.name||'Member '+(p.members.findIndex(m=>m.id===l.member)+1)):'',l.essential||false,l.subscription||false,l.funding]);return '\uFEFF'+rows.map(r=>r.map(csvEscape).join(',')).join('\r\n');}
function anonymize(p,withActual=false){const c=clone(p);c.title='';c.members=c.members.map((m,i)=>({...m,name:'Member '+(i+1)}));c.lines=c.lines.map((l,i)=>({...l,label:l.category+' '+(i+1)}));c.transactions=withActual?c.transactions.map((l,i)=>({...l,label:l.category+' '+(i+1)})):[];if(!withActual)c.closedMonths=[];return c;}
function demo(month=monthNow()){
 const p=blank(month);p.title='';p.members=[{id:'member1',name:'',role:'adult'},{id:'member2',name:'',role:'adult'}];
 const defs=[['income','Μισθός / Salary','income',1800,'monthly','member1',false],['income','Μισθός / Salary','income',1200,'monthly','member2',false],['expense','Ενοίκιο / Rent','housing',700,'monthly','',true],['expense','Ρεύμα / Electricity','housing',85,'monthly','',true],['expense','Internet','housing',25,'monthly','',true],['expense','Σούπερ μάρκετ / Groceries','food',360,'monthly','',true],['expense','Μετακινήσεις / Transport','transportation',160,'monthly','',true],['expense','Ασφάλιση / Insurance','insurance',360,'yearly','',true],['expense','Έξοδοι / Going out','entertainment',140,'monthly','',false],['expense','Streaming','subscriptions',12,'monthly','',false],['expense','Υγεία / Health','health',60,'monthly','',true],['expense','Δώρα / Gifts','gifts',30,'monthly','',false],['saving','Αποταμίευση / Savings','savings',250,'monthly','',false],['investment','Επένδυση / Investment','savings',150,'monthly','',false]];
 p.lines=defs.map((a,i)=>({id:'demo'+i,type:a[0],label:a[1],category:a[2],amount:a[3],frequency:a[4],member:a[5],essential:a[6],subscription:a[2]==='subscriptions',active:true,funding:'cash',month:''}));p.settings.openingCash=1500;p.settings.emergencyFund=1000;return p;
}

/** Reorder visible array slots without changing records or hidden entries. Zero-based target. */
function reorder(items,visible,source,position){
 if(!Array.isArray(items)||!Array.isArray(visible))throw new TypeError('Lists required');
 const itemIds=items.map(x=>x.id),set=new Set(visible);
 if(set.size!==visible.length||new Set(itemIds).size!==items.length||visible.some(id=>!itemIds.includes(id))||!set.has(source))throw new RangeError('Invalid reorder IDs');
 if(!Number.isInteger(position)||position<0||position>=visible.length)throw new RangeError('Invalid reorder position');
 const ids=visible.filter(id=>id!==source);ids.splice(position,0,source);
 const byId=new Map(items.map(x=>[x.id,x]));let at=0;
 return items.map(x=>set.has(x.id)?byId.get(ids[at++]):x);
}

return Object.freeze({reorder,CATEGORIES,TYPES,FREQ,CSV_COLS,MAX_ITEMS,MAX_AMOUNT,blank,demo,clone,id,monthNow,isMonth,isDate,addMonth,validate,equivalent,budget,actual,allocation,forecast,parseCSV,importCSV,exportCSV,anonymize,csvEscape});
});
