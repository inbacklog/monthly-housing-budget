"""Local content-rendering integration tests. Requires Playwright + Chromium.
Uses page.set_content and a deliberately mocked localStorage, NOT a deployed origin.
No real wallet, network deployment, browser-origin persistence or SW lifecycle tested.
Run: python tests/browser.test.py  (CHROMIUM_PATH and QA_OUTPUT can be overridden.)
"""
import base64,json,os,re
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('QA_OUTPUT','/tmp/homeflow-qa'));OUT.mkdir(parents=True,exist_ok=True)
passed=[];failures=[];errors=[]

def document():
    h=(BASE/'index.html').read_text()
    h=h.replace('<link rel="stylesheet" href="styles.css">','<style>'+(BASE/'styles.css').read_text()+'</style>')
    h=re.sub(r'<script defer src="[^"]+"></script>','',h)
    h=re.sub(r'<link rel="manifest"[^>]*>','',h)
    for name in ['icon.svg','icon-192.png','buymeacoffee-qr.png','wallet-of-satoshi-qr.png']:
        mime='image/svg+xml' if name.endswith('.svg') else 'image/png'
        h=h.replace('assets/'+name,'data:'+mime+';base64,'+base64.b64encode((BASE/'assets'/name).read_bytes()).decode())
    scripts='\n'.join((BASE/n).read_text() for n in ['budget-engine.js','data.js','xlsx-reader.js','io.js','scenarios.js','app.js'])
    mock="""window.HOMEFLOW_OFFLINE=true;window.__ls=new Map();Object.defineProperty(window,'localStorage',{value:{getItem:k=>__ls.get(k)||null,setItem:(k,v)=>__ls.set(k,String(v)),removeItem:k=>__ls.delete(k),clear:()=>__ls.clear()}});"""
    return h.replace('</body>','<script>'+mock+'\n'+scripts+'</script></body>')

def check(name, condition):
    if condition:passed.append(name);print('PASS',name)
    else:failures.append(name);print('FAIL',name)

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    page.set_default_timeout(6000)
    page.on('pageerror',lambda e:errors.append(str(e)))
    def wait():page.wait_for_timeout(120)
    def action(name):page.locator(f'[data-action="{name}"]').first.click();wait()
    def nav(v):page.locator(f'.nav-button[data-view="{v}"]').click();wait()
    def state():return page.evaluate("(()=>{const w=JSON.parse(localStorage.getItem('homeflow:workspace:v1'));return w.scenarios.find(s=>s.id===w.activeId).state})()")
    def submit():page.locator('#dialogBody form button[type=submit]').click();wait()
    def close():
        if page.locator('#dialog').is_visible():page.locator('#dialogClose').click();wait()
    def fill(n,v):page.locator(f'#dialogBody [name="{n}"]').fill(str(v))
    def select(n,v):page.locator(f'#dialogBody [name="{n}"]').select_option(v)
    def newapp():page.set_content(document(),wait_until='load');wait()
    def load_demo():action('demo');close()
    newapp()
    check('Blank public start does not reveal any example balances',page.locator('.start-wrap').is_visible() and page.locator('#demoBanner').is_hidden())
    check('No external runtime scripts',page.locator('script[src]').count()==0)
    action('demo')
    check('Fictional example is prominently identified',page.locator('#demoBanner').is_visible())
    check('Demo financial cards reconcile to the engine',page.locator('.kpi-value').all_inner_texts()==['3.700\xa0€','2.395\xa0€','250\xa0€','150\xa0€'])
    for v in ['budget','actual','subscriptions','goals','projection','household','files','overview']:
        nav(v);check('Navigation renders '+v,page.locator('h1').count()==1 and len(page.locator('h1').inner_text())>5)
    page.locator('#enBtn').click();wait();check('English interface toggle',page.locator('html').get_attribute('lang')=='en' and 'More clarity' in page.locator('h1').inner_text())
    nav('budget');action('addPlan');fill('name','Custom expense <img src=x onerror=alert(1)>');fill('amount','123.45');select('category','Other');submit()
    check('Any custom amount accepted, not constrained to presets',state()['plan'][-1]['amount']==123.45)
    check('User descriptions are escaped rather than injected as HTML',page.locator('#content img').count()==0 and '<img src=x' in page.locator('body').inner_text())
    new_id=state()['plan'][-1]['id'];page.locator(f'[data-amount="{new_id}"]').fill('19.99');wait();check('Inline arbitrary amount saves immediately',state()['plan'][-1]['amount']==19.99)
    page.locator(f'[data-amount="{new_id}"]').fill('-1');wait();check('Negative planned amount rejected without corrupting state',state()['plan'][-1]['amount']==19.99 and page.locator(f'[data-amount="{new_id}"]').get_attribute('aria-invalid')=='true')
    page.locator(f'[data-amount="{new_id}"]').fill('');wait();check('Empty planned amount remains unknown',state()['plan'][-1]['amount'] is None)
    page.locator(f'[data-amount="{new_id}"]').fill('0');wait();check('Explicit zero is retained',state()['plan'][-1]['amount']==0)
    page.locator(f'[data-action="deletePlan"][data-id="{new_id}"]').click();wait();submit();check('Plan removal confirmed explicitly',not any(p['id']==new_id for p in state()['plan']))
    action('undo');check('Undo restores the deleted entry',any(p['id']==new_id for p in state()['plan']))
    nav('household');action('addMember');fill('name','New dependent');select('role','dependent');page.locator('[name=contributor]').uncheck();submit()
    check('Household supports another non-contributing dependant',len(state()['household']['members'])==4 and state()['household']['members'][-1]['contributor']==False)
    page.locator('#splitRule').select_option('equal');wait();check('Equal sharing rule saved',state()['household']['split']=='equal')
    nav('actual');check('Example actuals remain partial until explicitly completed',page.locator('#closeMonth').is_checked()==False)
    page.locator('#closeMonth').check();wait();check('Actual month can be explicitly marked complete',state()['month'] in state()['closedMonths'])
    action('quickActual');fill('name','Actual purchase');fill('amount','17.25');select('category','Food');submit()
    check('Actual entry appended with exact custom amount',state()['actual'][-1]['amount']==17.25)
    check('Changing actuals reopens the completed month',state()['month'] not in state()['closedMonths'])
    aid=state()['actual'][-1]['id'];page.locator(f'[data-action=deleteActual][data-id="{aid}"]').click();wait();check('Actual deletion preserves the plan',len(state()['plan'])==21 and not any(a['id']==aid for a in state()['actual']))
    nav('subscriptions');before=state()['plan'];sub=next(p for p in before if p['subscription']);page.locator(f'[data-action=pausePlan][data-id="{sub["id"]}"]').click();wait();check('Pause subscription updates the same row without duplication',len(state()['plan'])==len(before) and not next(p for p in state()['plan'] if p['id']==sub['id'])['active'])
    nav('goals');n=len(state()['plan']);action('addGoal');fill('name','Generic goal');fill('target',2400);fill('saved',200);fill('contribution',75);submit()
    check('Goal creates exactly one savings allocation',len(state()['plan'])==n+1 and state()['goals'][-1]['entryId']==state()['plan'][-1]['id'] and state()['plan'][-1]['amount']==75)
    nav('projection');page.locator('#setting-scenarioIncome').fill('-20');wait();check('What-if updates without changing salary rows',state()['settings']['scenarioIncome']==-20 and state()['plan'][0]['amount']==2100)
    page.locator('#setting-projectionMonths').fill('24');wait();check('Projection horizon changes table length',page.locator('#forecastResults tbody tr').count()==24)
    nav('files');action('import');page.locator('#importFile').set_input_files(str(BASE/'templates/Homeflow_Template.xlsx'));page.wait_for_timeout(800)
    check('Generated XLSX template reads in native browser parser','Errors found.' not in page.locator('#dialogBody').inner_text() and page.locator('#dialogBody form button[type=submit]').is_enabled())
    submit();check('Template imports unknown amounts rather than inventing costs',any(p['amount'] is None for p in state()['plan']))
    action('import');page.locator('#importFile').set_input_files({'name':'bad.csv','mimeType':'text/csv','buffer':b'record_type;kind;description;category;amount;frequency\nplan;expense;Test;Food;-2;monthly'});wait();check('Invalid import blocks apply with row errors',page.locator('#dialogBody form button[type=submit]').is_disabled());close()
    # Generic clean reset for share and screenshots.
    action('demo');submit();nav('overview')
    action('share');check('Actual transactions excluded by default',not page.locator('#shareForm [name=includeActual]').is_checked())
    check('Names/descriptions removed by default',page.locator('#shareForm [name=stripNames]').is_checked())
    submit();check('Explicit privacy acknowledgement required',page.locator('#modalError').is_visible())
    page.locator('#shareForm [name=ack]').check();submit();page.wait_for_timeout(300)
    url=page.locator('#shareOutput').input_value();check('Share link targets the correct app and URL fragment',url.startswith('https://inbacklog.github.io/monthly-housing-budget/#h1'))
    data=page.evaluate('(s)=>HomeIO.shareDecode(s)',url.split('#',1)[1]);check('Shared payload independently decodes with no actuals/names',data['actual']==[] and data['household']['members'][0]['name']=='Person 1')
    close()
    # Hash opening on the existing about:blank document exercises copy logic without network.
    old_store=page.evaluate("localStorage.getItem('homeflow:workspace:v1')")
    page.evaluate('(v)=>location.hash=v',url.split('#',1)[1]);page.wait_for_timeout(400)
    check('Shared budget opens as a separate temporary copy',page.locator('#sharedBanner').is_visible())
    nav('budget');first_id=page.locator('[data-amount]').first.get_attribute('data-amount');page.locator('[data-amount]').first.fill('3456');wait()
    check('Editing shared copy leaves original saved data unchanged',page.evaluate("localStorage.getItem('homeflow:workspace:v1')")==old_store)
    action('discardShared');check('Discarding shared copy restores local state',page.locator('#sharedBanner').is_hidden())
    # Coffee is a popover, not the global dialog.
    page.locator('#coffeeBtn').click();wait();check('Coffee uses compact non-modal support panel',page.locator('#supportCard').is_visible() and not page.locator('#dialog').is_visible())
    check('Both verified destinations exposed',page.locator('#supportCard a[href="https://buymeacoffee.com/inbacklog"]').count()>=1 and page.locator('#supportCard a[href="lightning:doableshrimp862@walletofsatoshi.com"]').count()==1)
    check('Both QR images load locally',page.locator('#supportCard img').evaluate_all('(a)=>a.length===2&&a.every(x=>x.complete&&x.naturalWidth>0)'))
    page.keyboard.press('Escape');check('Escape closes support popover',page.locator('#supportCard').is_hidden())
    page.locator('#coffeeBtn').click();page.locator('#supportClose').click();check('Explicit close closes popover',page.locator('#supportCard').is_hidden())
    nav('overview');page.locator('#elBtn').click();wait();page.locator('#themeBtn').click();wait();check('Dark theme toggle',page.locator('html').get_attribute('data-theme')=='dark')
    page.locator('#themeBtn').click();wait();page.evaluate("document.getElementById('toast').hidden=true")
    page.screenshot(path=str(OUT/'Homeflow_Desktop_Preview.png'),full_page=True)
    for width in [320,360,390,768,1440]:
        page.set_viewport_size({'width':width,'height':844});wait()
        for v in ['overview','budget','actual','subscriptions','goals','projection','household','files']:
            nav(v)
            check(f'No page overflow {width}px / {v}',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        nav('overview')
        if width==390:
            page.evaluate("document.getElementById('toast').hidden=true")
            page.screenshot(path=str(OUT/'Homeflow_Mobile_Preview.png'),full_page=True)
            page.locator('#coffeeBtn').click();wait();box=page.locator('#supportCard').bounding_box()
            check('Mobile popover stays compact and in viewport',box['width']<=340 and box['height']<=844*.76 and box['x']>=0 and box['y']>=0)
            page.screenshot(path=str(OUT/'Homeflow_Mobile_Support.png'),full_page=False)
            page.locator('#supportClose').click()
    check('No uncaught JavaScript errors',not errors)
    report={'passed':len(passed),'failed':len(failures),'failures':failures,'page_errors':errors,'scope':'Content rendering with in-memory mocked storage; no real origin/SW tests.'}
    (OUT/'browser_results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print(json.dumps(report,indent=2,ensure_ascii=False))
    browser.close()
    if failures or errors:raise SystemExit(1)
