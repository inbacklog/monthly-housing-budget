"""Scenario/onboarding UI integration tests. Local content with in-memory localStorage.
Browser navigation to loopback is blocked in this runner; no live deployment or real
browser storage/service-worker lifecycle is claimed by these tests.
"""
import base64,json,os,re
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
OUT=Path(os.getenv('QA_OUTPUT','/tmp/homeflow-scenarios-qa'));OUT.mkdir(parents=True,exist_ok=True)
passed=[];failures=[];errors=[]
def document(seed=None):
 h=(BASE/'index.html').read_text().replace('<link rel="stylesheet" href="styles.css">','<style>'+(BASE/'styles.css').read_text()+'</style>')
 h=re.sub(r'<script defer src="[^"]+"></script>','',h);h=re.sub(r'<link rel="manifest"[^>]*>','',h)
 for name in ['icon.svg','icon-192.png','buymeacoffee-qr.png','wallet-of-satoshi-qr.png']:
  mime='image/svg+xml' if name.endswith('.svg') else 'image/png'
  h=h.replace('assets/'+name,'data:'+mime+';base64,'+base64.b64encode((BASE/'assets'/name).read_bytes()).decode())
 scripts='\n'.join((BASE/n).read_text() for n in ['budget-engine.js','data.js','xlsx-reader.js','io.js','scenarios.js','app.js'])
 seedjs=json.dumps(list((seed or {}).items())).replace('<','\\u003c')
 mock="window.HOMEFLOW_OFFLINE=true;window.__ls=new Map("+seedjs+");Object.defineProperty(window,'localStorage',{value:{getItem:k=>__ls.get(k)||null,setItem:(k,v)=>__ls.set(k,String(v)),removeItem:k=>__ls.delete(k)}});"
 return h.replace('</body>','<script>'+mock+'\n'+scripts+'</script></body>')
def check(name,ok):
 (passed if ok else failures).append(name);print('PASS' if ok else 'FAIL',name)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
 def page(seed=None,width=1440):
  p=browser.new_page(viewport={'width':width,'height':1000});p.set_default_timeout(6000);p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(document(seed));p.wait_for_timeout(100);return p
 p=page()
 def wait():p.wait_for_timeout(100)
 def act(a,**kw):p.locator(f'[data-action="{a}"]').first.click(**kw);wait()
 def nav(v):p.locator(f'.nav-button[data-view="{v}"]').click();wait()
 def sub():p.locator('#dialogBody button[type=submit]').click();wait()
 def ws():return p.evaluate("JSON.parse(localStorage.getItem('homeflow:workspace:v1'))")
 def active():
  w=ws();return next(s for s in w['scenarios'] if s['id']==w['activeId'])['state']
 def duplicate(name):
  act('scenarioAdd');p.locator('[name=scenarioName]').fill(name);sub()
 check('Guide opens before showing a public financial plan',p.locator('.start-wrap').is_visible())
 check('Guide has three pathways',p.locator('.start-card').count()==3)
 p.screenshot(path=str(OUT/'Homeflow_Start_Desktop_v1.2.png'),full_page=True)
 act('startPlan');check('Initial guide amounts are empty',[p.locator(f'#startPlanForm [name={n}]').input_value() for n in ['income','housing','living']]==['','',''])
 p.locator('[name=income]').fill('2700');p.locator('[name=housing]').fill('725');p.locator('[name=living]').fill('');p.locator('[name=members]').fill('2');p.locator('#startPlanForm button[type=submit]').click();wait()
 check('Review step does not silently save',ws() is None)
 act('startApply');check('Guide saves only explicitly supplied amounts',[r['amount'] for r in active()['plan']]==[2700,725,None]);check('Guide household does not multiply expenses',active()['plan'][1]['amount']==725 and len(active()['household']['members'])==2)
 check('Guide aggregate is visibly marked for review',active()['plan'][2]['review'])
 # New fictional demo, consent required with existing data.
 nav('files');act('demo');sub();check('Demo replacement keeps one active scenario',len(ws()['scenarios'])==1)
 nav('compare');check('Comparison includes base plan',p.locator('[data-scenario-card]').count()==1)
 base_id=ws()['activeId'];base_plan=active()
 duplicate('Different home');copy_id=ws()['activeId']
 check('Duplicate is independently editable',copy_id!=base_id and len(ws()['scenarios'])==2)
 check('Actuals omitted in new scenario by default',active()['actual']==[] and ws()['scenarios'][0]['state']['actual'])
 p.locator(f'[data-action=scenarioEdit][data-id="{copy_id}"]').click();wait();p.locator('[data-amount="example-2"]').fill('995');wait()
 check('Editing copied housing leaves original unchanged',ws()['scenarios'][0]['state']['plan'][2]['amount']==720 and active()['plan'][2]['amount']==995)
 nav('compare');check('Two lines drawn for two scenarios',p.locator('#comparisonChart path[data-series]').count()==2)
 check('Monthly delta uses common source values','-275' in p.locator(f'[data-scenario-card="{copy_id}"] .scenario-delta').inner_text())
 duplicate('Income change');third_id=ws()['activeId'];check('Exactly three cards and lines displayed',p.locator('[data-scenario-card]').count()==3 and p.locator('#comparisonChart path[data-series]').count()==3)
 check('Fourth scenario creation disabled',p.locator('[data-action=scenarioAdd]').evaluate_all('(xs)=>xs.every(x=>x.disabled)'))
 third=p.locator(f'[data-scenario-card="{third_id}"]');third.locator('summary').click();third.locator('[data-scenario-setting=scenarioIncome]').fill('-15');third.locator('[data-scenario-setting=scenarioIncome]').press('Tab');wait()
 check('Quick shock changes only selected scenario',ws()['scenarios'][2]['state']['settings']['scenarioIncome']==-15 and ws()['scenarios'][0]['state']['settings']['scenarioIncome']==0)
 p.locator('#compareMonths').fill('24');p.locator('#compareMonths').press('Tab');wait();check('One horizon applied to whole comparison',ws()['comparison']['months']==24)
 # Baseline change not an active-scenario swap.
 p.locator(f'[data-action=scenarioReference][data-id="{copy_id}"]').click();wait();check('Reference independent of active scenario',ws()['referenceId']==copy_id and ws()['activeId']==third_id)
 p.locator(f'[data-action=scenarioRename][data-id="{copy_id}"]').click();wait();p.locator('[name=scenarioName]').fill('Home <img src=x onerror=alert(1)>');sub()
 check('Scenario names escaped as text',p.locator('#content img').count()==0 and '<img src=x' in p.locator('#content').inner_text())
 # Revert to friendly example label for screenshot.
 p.locator(f'[data-action=scenarioRename][data-id="{copy_id}"]').click();wait();p.locator('[name=scenarioName]').fill('Άλλο σπίτι');sub()
 p.locator(f'[data-action=scenarioRename][data-id="{third_id}"]').click();wait();p.locator('[name=scenarioName]').fill('Αλλαγή εισοδήματος');sub()
 nav('compare');p.evaluate("document.getElementById('toast').hidden=true")
 p.screenshot(path=str(OUT/'Homeflow_Scenarios_Desktop_v1.2.png'),full_page=True)
 # Whole workspace backups include all scenarios.
 with p.expect_download() as dl:act('backup') if p.locator('[data-action=backup]').count() else (nav('files'),act('backup'))
 path=dl.value.path();backup=json.loads(Path(path).read_text());check('Full backup includes three scenarios and reference',backup['schema']=='homeflow-workspace' and len(backup['scenarios'])==3 and backup['referenceId']==copy_id)
 # Compare CSV carries scope and all rows.
 nav('compare')
 with p.expect_download() as dl:act('exportCompare')
 csv=Path(dl.value.path()).read_text(encoding='utf-8-sig');check('CSV export carries three alternatives and all months',len(csv.splitlines())==78 and ws()['comparison']['month'] in csv)
 # URL does not disclose actuals or scenario names by default.
 act('shareCompare');check('Comparison sharing defaults to all scenarios',p.locator('[name=shareScope]').input_value()=='all')
 check('Actuals excluded and names stripped by default',not p.locator('[name=includeActual]').is_checked() and p.locator('[name=stripNames]').is_checked())
 p.locator('[name=ack]').check();sub();p.wait_for_selector('#shareOutput');link=p.locator('#shareOutput').input_value();payload=link.split('#',1)[1]
 decoded=p.evaluate('(v)=>HomeIO.shareDecode(v)',payload)
 check('Sharing keeps all three but removes private descriptions',len(decoded['scenarios'])==3 and all(s['state']['actual']==[] for s in decoded['scenarios']) and [s['name'] for s in decoded['scenarios']]==['Scenario 1','Scenario 2','Scenario 3'])
 check('Link length guard gives practical link',len(link)<=8000)
 p.locator('#dialogClose').click();before=p.evaluate("localStorage.getItem('homeflow:workspace:v1')");p.evaluate('(h)=>location.hash=h',payload);p.wait_for_timeout(300)
 check('Shared comparison opens as a temporary copy',p.locator('#sharedBanner').is_visible() and p.locator('[data-scenario-card]').count()==3)
 act('scenarioEdit');p.locator('[data-amount]').first.fill('3456');wait();check('Editing shared workspace leaves local workspace intact',p.evaluate("localStorage.getItem('homeflow:workspace:v1')")==before)
 act('discardShared');check('Return restores whole local workspace',p.locator('#sharedBanner').is_hidden() and p.evaluate("localStorage.getItem('homeflow:workspace:v1')")==before)
 # Invalid edits cannot be silently applied on scenario switch.
 nav('budget');p.locator('[data-amount]').first.fill('-1');wait();p.locator(f'[data-action=scenarioSwitch][data-id="{base_id}"]').click();wait();check('Invalid current input blocks scenario switch',ws()['activeId']==third_id);p.locator('[data-amount]').first.fill(str(active()['plan'][0]['amount']));wait()
 # Refresh/migration is simulated by loading a new document with the stored payload.
 p.close();p=page({'homeflow:workspace:v1':before});nav('compare');check('Reinitializing from serialized workspace retains all scenarios',len(ws()['scenarios'])==3 if ws() else p.locator('[data-scenario-card]').count()==3)
 # Seed has key so ws exists from seeding.
 check('Reference survives serialization',ws()['referenceId']==copy_id)
 # Restore full workspace requires an explicit checkbox.
 nav('files');act('import');p.locator('#importFile').set_input_files({'name':'budget.json','mimeType':'application/json','buffer':json.dumps(backup).encode()});wait();check('Workspace import has replace-all confirmation',p.locator('[name=confirm]').count()==1 and 'σεναρίων' in p.locator('#dialogTitle').inner_text());sub();check('Cannot restore without confirmation',p.locator('#modalError').is_visible());p.locator('[name=confirm]').check();sub();check('Confirmed restore keeps three scenarios',len(ws()['scenarios'])==3)
 # Layout: all 3 cards same row on wide desktop; readable stack on phones.
 for width in [320,390,768,1024,1440]:
  p.set_viewport_size({'width':width,'height':900});nav('compare');check(f'Comparison no page overflow at {width}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
  if width==1440:
   ys=[b['y'] for b in [p.locator('[data-scenario-card]').nth(i).bounding_box() for i in range(3)]];check('Three scenarios side by side on desktop',max(ys)-min(ys)<3)
  if width in [320,390]:
   check(f'All three visible in compact comparison at {width}px',p.locator('#scenarioSnapshot').is_visible() and p.locator('#scenarioSnapshot [data-snapshot-id]').count()==3 and p.locator('#scenarioSnapshot').bounding_box()['width']<=width)
  if width==390:
   p.evaluate("document.getElementById('toast').hidden=true");p.screenshot(path=str(OUT/'Homeflow_Scenarios_Mobile_v1.2.png'),full_page=True)
  p.locator('#themeBtn').click();wait();check(f'Dark compare renders at {width}px',p.locator('#comparisonChart').count()==1);p.locator('#themeBtn').click();wait()
 # Active deletion changes active/reference deterministically.
 nav('compare');p.locator(f'[data-action=scenarioDelete][data-id="{copy_id}"]').click();wait();sub();check('Deletion removes only requested scenario',len(ws()['scenarios'])==2 and not any(s['id']==copy_id for s in ws()['scenarios']));check('Deleting reference chooses existing survivor',ws()['referenceId'] in [s['id'] for s in ws()['scenarios']])
 # Local-storage failure reports save failure; in-memory result still exports.
 p.evaluate("()=>{localStorage.setItem=()=>{throw new Error('quota')};}");act('scenarioAdd');p.locator('[name=scenarioName]').fill('Unsaved copy');sub();check('Storage failure displays a visible warning',p.locator('#statusBanner').is_visible());check('In-memory failed-save scenario remains visible',p.locator('[data-scenario-card]').count()==3)
 # Existing v1 plan migrates in memory without destroying its old storage key.
 p.close();p=page({'homeflow:state:v1':json.dumps(base_plan)});nav('compare');check('Legacy plan migrates as one scenario',p.locator('[data-scenario-card]').count()==1);check('Legacy storage preserved until explicit wipe',json.loads(p.evaluate("localStorage.getItem('homeflow:state:v1')"))==base_plan)
 # Block unexpected values before parser/projection.
 p.locator('#compareMonths').fill('121');p.locator('#compareMonths').press('Tab');wait();check('Horizon beyond 120 months is rejected',p.locator('#compareMonths').get_attribute('aria-invalid')=='true')
 p.close();p=page({'homeflow:workspace:v1':'{not-json'});nav('budget');act('addPlan');p.locator('[name=name]').fill('Safe local edit');p.locator('[name=amount]').fill('1');sub();check('Corrupted stored workspace not silently overwritten',p.evaluate("localStorage.getItem('homeflow:workspace:v1')")=='{not-json')
 p.close();p=page(width=390);p.screenshot(path=str(OUT/'Homeflow_Start_Mobile_v1.2.png'),full_page=True)
 check('No JavaScript runtime errors',not errors)
 report={'passed':len(passed),'failed':len(failures),'failures':failures,'page_errors':errors,'scope':'Local set_content with simulated storage; no deployed origin or real device.'};(OUT/'scenarios_browser_results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));browser.close()
 if failures or errors:raise SystemExit(1)
