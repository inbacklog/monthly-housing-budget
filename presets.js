/* Homeflow v1.1: expense names, not financial recommendations or preset prices.
 * Kept separate from user data. No amounts, member names or provider accounts.
 * Pure helpers also run under Node for regression tests.
 */
(function(root,factory){'use strict';const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.HomeflowPresets=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const raw=[
 ['rent','housing','Ενοίκιο','Rent',true,['ενοικιο','rent','Ενοίκιο ή στεγαστικό','Rent or mortgage']],
 ['mortgage','housing','Στεγαστικό δάνειο','Mortgage payment',true,['στεγαστικο']],
 ['electricity','housing','Ρεύμα','Electricity',true,['δεη','power','ilektriko','reuma']],
 ['water','housing','Ύδρευση / νερό','Water bill',true,['νερο','water','eydap','ευδαπ','ydreysi']],
 ['building','housing','Κοινόχρηστα','Building fees',true,['Building maintenance','koinoxrista']],
 ['heating','housing','Θέρμανση / αέριο','Heating / gas',true,['Θέρμανση','Heating','πετρελαιο','gas']],
 ['internet','housing','Internet & σταθερό','Internet & landline',true,['Internet','Internet & τηλέφωνο','Internet & phone','wifi']],
 ['mobile','housing','Κινητό τηλέφωνο','Mobile phone',true,['κινητο','mobile','phone','kinito']],
 ['repairs','housing','Επισκευές σπιτιού','Home repairs',true,['συντηρηση','repair']],
 ['cleaning','housing','Καθαρισμός σπιτιού','House cleaning',false,['καθαριοτητα','cleaner']],
 ['furniture','housing','Έπιπλα & συσκευές','Furniture & appliances',false,['επιπλα','appliances']],
 ['groceries','food','Supermarket','Groceries',true,['super market','σουπερμαρκετ','σουπερ μαρκετ','Σούπερ μάρκετ','ψωνια','tropima']],
 ['bakery','food','Φούρνος & λαϊκή','Bakery & market',true,['φουρνος','λαϊκη','market']],
 ['coffee','food','Καφές & snack','Coffee & snacks',false,['καφες','coffee','kafes']],
 ['takeaway','food','Delivery / έτοιμο φαγητό','Takeaway / delivery',false,['Delivery & καφές','Takeaway & coffee','delivery','efood']],
 ['dining','food','Εστιατόρια','Dining out',false,['φαγητο εξω','restaurant']],
 ['fuel','transportation','Καύσιμα','Fuel',true,['βενζινη','πετρελαιο κινησης','Καύσιμα / μεταφορές','Fuel / transport','kausima']],
 ['transit','transportation','ΜΜΜ / εισιτήρια','Public transport',true,['εισιτηρια','λεωφορειο','μετρο','transport']],
 ['taxi','transportation','Ταξί','Taxi',false,['ταξι','taxi']],
 ['parking','transportation','Parking & διόδια','Parking & tolls',false,['parking','διοδια']],
 ['car-service','transportation','Service / ΚΤΕΟ','Car service / inspection',true,['Συντήρηση οχήματος','Vehicle maintenance','kteo','service']],
 ['car-insurance','transportation','Ασφάλεια οχήματος','Vehicle insurance',true,['ασφαλεια αυτοκινητου']],
 ['car-payment','transportation','Δόση οχήματος','Vehicle payment',true,['leasing','δοση αυτοκινητου']],
 ['car-tax','taxes','Τέλη κυκλοφορίας','Vehicle tax',true,['τελη','road tax']],
 ['childcare','children','Παιδικός σταθμός / φύλαξη','Childcare',true,['Παιδική φροντίδα','βρεφικος']],
 ['school','children','Σχολείο / δίδακτρα','School fees',true,['Σχολείο & δραστηριότητες','School & activities','σχολειο']],
 ['tutoring','children','Φροντιστήριο / μαθήματα','Tutoring / lessons',true,['φροντιστηριο','mathimata']],
 ['kids-activities','children','Δραστηριότητες παιδιών','Children’s activities',false,['δραστηριοτητες','sports']],
 ['baby','children','Βρεφικά είδη / πάνες','Baby supplies / nappies',true,['πανες','γαλα μωρου']],
 ['kids-clothing','children','Παιδικά ρούχα / σχολικά','Children’s clothes / supplies',true,['σχολικα','school supplies']],
 ['doctor','health','Γιατροί & εξετάσεις','Doctors & tests',true,['Ιατρικά έξοδα','Medical expenses','υγεια','health','γιατρος']],
 ['pharmacy','health','Φαρμακείο','Pharmacy',true,['φαρμακα','farmakeio']],
 ['dentist','health','Οδοντίατρος','Dentist',true,['δοντια']],
 ['therapy','health','Θεραπείες / φυσιοθεραπεία','Therapy / physio',true,['φυσικοθεραπεια','θεραπεια']],
 ['home-insurance','insurance','Ασφάλιση κατοικίας','Home insurance',true,['Ασφάλιση κατοικίας / ζωής','Home / life insurance']],
 ['life-health-insurance','insurance','Ασφάλιση ζωής / υγείας','Life / health insurance',true,['ασφαλεια υγειας']],
 ['loan','loans','Δόση δανείου','Loan payment',true,['δανειο','loan']],
 ['credit-card','loans','Αποπληρωμή κάρτας','Credit card repayment',true,['πιστωτικη','credit card']],
 ['clothing','personal','Ρούχα & παπούτσια','Clothes & shoes',false,['Ρούχα & φροντίδα','Clothing & care','ρουχα']],
 ['haircut','personal','Κομμωτήριο','Haircut',false,['κουρειο','hairdresser']],
 ['care','personal','Καλλυντικά / περιποίηση','Personal care',false,['καλλυντικα','φροντιδα']],
 ['pet-food','pets','Τροφή κατοικιδίου','Pet food',true,['Τροφή & κτηνίατρος','Pet food & vet']],
 ['vet','pets','Κτηνίατρος','Vet',true,['κτηνιατρος']],
 ['pet-care','pets','Φροντίδα κατοικιδίου','Pet care',false,['grooming','pet sitting']],
 ['streaming','subscriptions','Streaming / TV','Streaming / TV',false,['Streaming / εφαρμογές','Streaming / apps','netflix','disney','streaming'],true],
 ['music','subscriptions','Μουσική / Spotify','Music / Spotify',false,['μουσικη','spotify'],true],
 ['apps','subscriptions','Εφαρμογές / software','Apps / software',false,['chatgpt','λογισμικο','apps'],true],
 ['cloud','subscriptions','Cloud / αποθήκευση','Cloud storage',false,['icloud','google drive','cloud'],true],
 ['gym','subscriptions','Γυμναστήριο','Gym membership',false,['gym','γυμναστηριο'],true],
 ['other-subscription','subscriptions','Άλλη συνδρομή','Other subscription',false,['συνδρομη','subscription'],true],
 ['going-out','entertainment','Έξοδοι / σινεμά','Going out / cinema',false,['Έξοδοι','Going out','Ψυχαγωγία','Entertainment']],
 ['hobbies','entertainment','Hobby / αθλητισμός','Hobbies / sports',false,['hobby','χόμπι','athlitismos']],
 ['gifts','gifts','Δώρα','Gifts',false,['Δώρα & δωρεές','Gifts & charity','dora']],
 ['charity','gifts','Δωρεές / προσφορές','Charity / donations',false,['δωρεες','charity']],
 ['property-tax','taxes','ΕΝΦΙΑ / ακίνητα','Property tax',true,['ενφια','enfia']],
 ['income-tax','taxes','Φόρος εισοδήματος','Income tax',true,['φορος','tax']],
 ['other-tax','taxes','Άλλοι φόροι / τέλη','Other taxes / fees',true,['Φόροι & τέλη','Taxes & fees']],
 ['holidays','travel','Διακοπές / ταξίδια','Holidays / travel',false,['διακοπες','travel']],
 ['accommodation','travel','Διαμονή / ξενοδοχείο','Accommodation',false,['ξενοδοχειο','hotel']],
 ['travel-tickets','travel','Πτήσεις / πλοία','Flights / ferries',false,['αεροπορικα','ακτοπλοικα']],
 ['other-expense','other','Άλλο έξοδο','Other expense',false,['απροβλεπτα','other']],
 ['salary','income','Μισθός','Salary',false,['μισθος','pay'],false,'income'],
 ['bonus','income','Bonus / πρόσθετη αμοιβή','Bonus / extra pay',false,['bonus','δωρο μισθου'],false,'income'],
 ['pension','income','Σύνταξη','Pension',false,['συνταξη'],false,'income'],
 ['rental-income','income','Έσοδα από ενοίκια','Rental income',false,['ενοικια'],false,'income'],
 ['freelance','income','Ελεύθερο επάγγελμα','Freelance income',false,['freelance'],false,'income'],
 ['other-income','income','Άλλο καθαρό έσοδο','Other take-home income',false,[],false,'income'],
 ['reserve','savings','Απόθεμα ασφαλείας','Emergency reserve',false,[],false,'saving'],
 ['savings-goal','savings','Αποταμίευση στόχου','Goal savings',false,[],false,'saving'],
 ['investment','savings','Επενδυτική καταβολή','Investment contribution',false,[],false,'investment']
];
const items=Object.freeze(raw.map(a=>Object.freeze({id:a[0],category:a[1],el:a[2],en:a[3],essential:a[4],aliases:Object.freeze(a[5]||[]),subscription:!!a[6],type:a[7]||'expense'})));
const popular=Object.freeze(['groceries','rent','electricity','water','internet','fuel','pharmacy','streaming']);
const fold=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/ς/g,'σ').trim();
const exact=s=>fold(s).replace(/[^a-z0-9\u03b1-\u03c9]/g,'');
const name=(p,lang)=>p[lang==='en'?'en':'el'];
const get=id=>items.find(p=>p.id===id);
function search(query='',category='',type='expense'){
 const terms=fold(query).split(/\s+/).filter(Boolean);
 return items.filter(p=>p.type===type&&(!category||p.category===category)&&terms.every(term=>fold([p.el,p.en,p.category,...p.aliases].join(' ')).includes(term)));
}
function match(line){return items.find(p=>p.type===line.type&&p.category===line.category&&[p.el,p.en,p.el+' / '+p.en,...p.aliases,...p.aliases.map(a=>a+' / '+p.en),...p.aliases.map(a=>p.el+' / '+a)].some(n=>exact(n)===exact(line.label)));}
function key(line){return match(line)?.id||exact(line.label);}
function seed(p,lang){return {type:p.type,label:name(p,lang),category:p.category,essential:p.essential,subscription:p.subscription};}
function readAmount(input){const s=String(input).trim();if(!s)return null;if(!/^\d+(?:[.,]\d{1,2})?$/.test(s))throw Error('Βάλε θετικό ποσό ή 0, έως δύο δεκαδικά, χωρίς χιλιάδες (π.χ. 1234,50). / Use 0 or a positive amount, up to 2 decimals, without thousands separators (e.g. 1234.50).');const n=Number(s.replace(',','.'));if(!Number.isFinite(n)||n>1e9)throw Error('Μέγιστο ποσό: 1.000.000.000 €. / Maximum amount: €1,000,000,000.');return n;}
function estimateRows(state,lang){
 const seen=new Set(),rows=[];
 for(const l of state.lines.filter(l=>l.type==='expense')){const preset=match(l);if(preset)seen.add(preset.id);rows.push({key:'existing:'+l.id,existingId:l.id,category:l.category,label:l.label,amount:l.amount,frequency:l.frequency,line:l,preset});}
 for(const p of items.filter(p=>p.type==='expense'&&!seen.has(p.id)))rows.push({key:'new:'+p.id,existingId:null,category:p.category,label:name(p,lang),amount:null,frequency:'monthly',preset:p});
 return rows;
}
/* Atomic change plan: untouched / empty fields do not mutate stored data.
 * Existing IDs, members, funding, flags, one-off dates and paused state survive.
 */
function buildEstimate(E,state,rows,drafts,lang){
 const next=E.clone(state);let added=0,updated=0;
 for(const row of rows){const d=drafts[row.key];if(!d)continue;
  const unchangedAmount=row.existingId&&String(d.amount).trim()===String(row.amount);const n=unchangedAmount?row.amount:readAmount(d.amount);if(n===null)continue;
  if(!['monthly','yearly','quarterly','weekly','once'].includes(d.frequency))throw Error('Invalid frequency');
  if(row.existingId){const l=next.lines.find(l=>l.id===row.existingId);if(!l)throw Error('Entry no longer exists. Reopen the editor.');if(l.amount!==n||l.frequency!==d.frequency){l.amount=n;l.frequency=d.frequency;if(l.frequency==='once'&&!E.isMonth(l.month))l.month=next.month;updated++;}}
  else if(n>0){const p=row.preset;if(d.frequency==='once')throw Error('Use the detailed form for one-off entries.');if(next.lines.some(l=>l.type==='expense'&&match(l)?.id===p.id))throw Error('Το έξοδο υπάρχει ήδη. Κλείσε και άνοιξε ξανά το γρήγορο πλάνο. / This expense already exists. Reopen quick setup.');next.lines.push({id:E.id(),...seed(p,lang),amount:n,frequency:d.frequency,member:'',active:true,funding:'cash',month:''});added++;}
 }
 return {state:E.validate(next),added,updated};
}
return Object.freeze({items,popular,fold,exact,get,name,search,match,key,seed,readAmount,estimateRows,buildEstimate});
});
