"""Chromium tests with inline local assets.
The execution environment blocks browser navigation, so HTML is loaded with
set_content. Persistence tests use an in-memory Storage adapter. This does NOT
claim an end-to-end hosted/service-worker installation test.
Run: python tests/browser.test.py
"""
from pathlib import Path
import sys, re, json, base64, mimetypes
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
OUT=BASE.parent/'qa_output'
OUT.mkdir(exist_ok=True)

def source_html():
    html=(BASE/'index.html').read_text()
    html=html.replace('<link rel="stylesheet" href="styles.css">','<style>'+(BASE/'styles.css').read_text()+'</style>')
    html=html.replace('<link rel="manifest" href="manifest.webmanifest">','')
    html=html.replace('<script src="engine.js" defer></script>','').replace('<script src="app.js" defer></script>','').replace('<script src="presets.js" defer></script>','')
    for asset in ['assets/icon.svg','assets/icon-192.png','assets/buymeacoffee-qr.png','assets/wallet-of-satoshi-qr.png']:
        html=html.replace(asset,'data:'+mimetypes.guess_type(asset)[0]+';base64,'+base64.b64encode((BASE/asset).read_bytes()).decode())
    js=(BASE/'app.js').read_text()
    # Test instrumentation only; never written to distribution source.
    js=js.replace('render();checkShared();','window._qa={encodeShare,decodeShare,getState:()=>JSON.parse(JSON.stringify(state)),setState:p=>commit(p)};render();checkShared();')
    return html.replace('</body>','<script>window.HOMEFLOW_OFFLINE=true;</script><script>'+(BASE/'engine.js').read_text()+'</script><script>'+(BASE/'presets.js').read_text()+'</script><script>'+js+'</script></body>')

checks=[]
def check(name,condition):
    if not condition:raise AssertionError(name)
    checks.append(name);print('PASS '+name)

with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},locale='el-GR')
    page.set_default_timeout(4000)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.evaluate("""()=>{const data={'other-app:data':'untouched'};window._storage=data;Object.defineProperty(window,'localStorage',{value:{getItem:k=>data[k]??null,setItem:(k,v)=>data[k]=String(v),removeItem:k=>delete data[k],clear:()=>{for(const k in data)delete data[k]}}});}""")
    page.set_content(source_html(),wait_until='load')
    get=lambda:page.evaluate('window._qa.getState()')
    def close():
        if page.locator('#dialog').is_visible():page.locator('#closeDialog').click()
    def tab(name):page.locator(f'[data-tab="{name}"]').click()
    def submit():page.locator('#saveEntry').click()
    check('Initial public app starts empty',get()['lines']==[] and len(get()['members'])==1)
    check('No private personal defaults in page',get()['title']=='' and get()['settings']['investPercent']==0 and get()['settings']['openingCash']==0)
    page.locator('#demoBtn').click();page.locator('#confirmAction').click()
    check('Demo is explicitly labelled',page.locator('#message').is_visible())
    check('Demo calculates 998 EUR remainder',page.locator('.big-value').inner_text().replace('\xa0','')=='998€')
    check('Persistence adapter received valid JSON',json.loads(page.evaluate("localStorage.getItem('homeflow:budget:v1')"))['version']==1)
    page.locator('#langBtn').click();check('English renders across tabs',page.locator('[data-tab="actual"]').inner_text()=='Actuals')
    page.locator('#themeBtn').click();check('Dark mode toggles',page.locator('html').get_attribute('data-theme')=='dark')
    page.locator('#themeBtn').click();page.locator('#langBtn').click()
    page.locator('#householdBtn').click()
    page.locator('[data-member-name="0"]').fill('Person X')
    for _ in range(4):page.locator('#addMember').click()
    page.locator('#houseForm button[type="submit"]').click()
    check('Multiple household members can be added',len(get()['members'])==6)
    check('Adding members preserves income',page.evaluate('BudgetEngine.budget(_qa.getState()).income')==3000)
    page.locator('#householdBtn').click();page.locator('[data-remove-member="0"]').click();page.locator('#houseForm button[type="submit"]').click()
    check('Removing member preserves financial rows',len(get()['lines'])==14 and page.evaluate('BudgetEngine.budget(_qa.getState()).income')==3000)
    tab('plan');page.locator('[data-action="add-plan"]').first.click()
    page.locator('#entryType').select_option('income',force=True);page.locator('#entryLabel').fill('Custom income');page.locator('#entryAmount').fill('1234.56');page.locator('#entryCategory').select_option('income');submit()
    check('Arbitrary income amount accepted',get()['lines'][-1]['amount']==1234.56)
    page.locator('[data-action="add-plan"]').first.click();page.locator('#entryLabel').fill('<img src=x onerror=alert(1)>');page.locator('#entryAmount').fill('42.75');page.locator('#entryCategory').select_option('__new');page.locator('#customCategory').fill('Custom category');submit()
    check('Custom category works',get()['lines'][-1]['category']=='Custom category')
    check('User HTML is rendered as text, never executed',page.locator('.table-wrap img').count()==0 and '<img' in page.locator('#view').inner_text())
    rowid=get()['lines'][-1]['id'];page.locator(f'[data-amount="{rowid}"]').fill('57.25');page.locator(f'[data-amount="{rowid}"]').dispatch_event('change')
    check('Inline amount edits recalculate',get()['lines'][-1]['amount']==57.25)
    page.locator(f'[data-toggle="{rowid}"]').click();check('Pause does not delete entry',get()['lines'][-1]['active']==False)
    page.locator(f'[data-toggle="{rowid}"]').click()
    page.locator('#filter').select_option('subscriptions');check('Subscription filter shows subset',page.locator('tbody tr').count()==1)
    page.locator('#filter').select_option('all');page.locator('#search').fill('Custom income');check('Search narrows entries',page.locator('tbody tr').count()==1)
    tab('actual');page.locator('[data-action="add-actual"]').first.click()
    page.locator('#entryLabel').fill('Groceries receipt');page.locator('#entryAmount').fill('27.50');page.locator('#entryCategory').select_option('food');page.locator('#entryDate').fill('2026-09-08');submit()
    check('Actual transaction recorded without changing budget',len(get()['transactions'])==1 and len(get()['lines'])==16)
    check('New actual month stays incomplete',not get()['closedMonths'])
    check('No-income warning exists for expense-only actuals','Δεν έχεις καταχωρίσει έσοδα' in page.locator('#view').inner_text())
    # Last cell per category remains unknown until marked complete.
    check('Partial actuals do not claim savings',all(x.inner_text()=='—' for x in page.locator('#view > section').nth(1).locator('tbody tr td:last-child').all()))
    page.locator('#closedMonth').check();check('Complete month can be marked',get()['month'] in get()['closedMonths'])
    page.locator('[data-edit-actual]').click();page.locator('#entryAmount').fill('29.50');submit()
    check('Editing actuals invalidates complete-month flag',get()['month'] not in get()['closedMonths'])
    page.locator('#nextMonth').click();check('Month selector isolates actuals',not page.locator('[data-edit-actual]').count());page.locator('#prevMonth').click()
    tab('future');page.locator('[data-action="settings"]').first.click();page.locator('#extraSaving').fill('100');page.locator('#investPercent').fill('50');page.locator('#horizon').fill('24');page.locator('#settingsForm button[type="submit"]').click()
    check('Projection horizon updates',page.locator('table tbody tr').count()==24)
    check('Investment link transfers no private initial portfolio', 'start=0' in page.locator('a[href*="wealth-goal-planner/#"]').get_attribute('href'))
    page.locator('#coffeeBtn').click();check('Support is a small non-modal panel',page.locator('#supportCard').is_visible() and not page.locator('#dialog').is_visible() and page.locator('#supportCard').bounding_box()['width']<=331)
    check('Both support QR images load',page.evaluate('Array.from(document.querySelectorAll(".support-card img")).every(i=>i.complete&&i.naturalWidth>0)'))
    check('Lightning address is correct',page.locator('a[href^="lightning:"]').get_attribute('href')=='lightning:doableshrimp862@walletofsatoshi.com')
    page.keyboard.press('Escape');check('Support closes with Escape',not page.locator('#supportCard').is_visible())
    page.locator('#shareBtn').click();check('Sharing requires consent',page.locator('#makeLink').is_disabled())
    check('Names and actuals are excluded by default',not page.locator('#shareNames').is_checked() and not page.locator('#shareActuals').is_checked())
    page.locator('#shareConsent').check();page.locator('#makeLink').click();page.wait_for_selector('#shareURL')
    url=page.locator('#shareURL').input_value();token=url.split('#plan=')[1]
    decoded=page.evaluate('(token)=>_qa.decodeShare(token)',token)
    check('Share link roundtrips amounts exactly',decoded['lines'][0]['amount']==get()['lines'][0]['amount'])
    check('Shared link removes names and receipts',decoded['transactions']==[] and decoded['members'][0]['name'].startswith('Member ') and 'Groceries receipt' not in json.dumps(decoded))
    check('Shared URL uses the requested GitHub Pages destination',url.startswith('https://inbacklog.github.io/monthly-housing-budget/#plan='))
    close();page.locator('#filesBtn').click()
    bad='kind,date\nwrong,data\n'
    before=get();page.locator('#importFile').set_input_files({'name':'bad.csv','mimeType':'text/csv','buffer':bad.encode()})
    check('Bad CSV shows useful error and does not mutate data',bool(page.locator('#fileError').inner_text()) and get()==before)
    good='kind,date,type,description,category,amount,frequency,member,essential,subscription,funding\nplan,,expense,CSV subscription,subscriptions,8.75,monthly,,false,true,cash\n'
    page.locator('#importFile').set_input_files({'name':'valid.csv','mimeType':'text/csv','buffer':good.encode()});page.wait_for_selector('#confirmImport')
    check('CSV import requires preview confirmation',page.locator('#applyImport').is_disabled())
    page.locator('#confirmImport').check();page.locator('#applyImport').click();check('CSV import appends only after confirmation',len(get()['lines'])==len(before['lines'])+1)
    page.locator('#filesBtn').click();page.locator('#importFile').set_input_files({'name':'valid.csv','mimeType':'text/csv','buffer':good.encode()});page.wait_for_selector('#confirmImport');check('Repeated CSV triggers duplicate warning','μοιάζουν διπλές' in page.locator('#importPreview').inner_text());close()
    page.locator('#filesBtn').click();clean=page.evaluate("BudgetEngine.blank('2026-04')");page.locator('#importFile').set_input_files({'name':'clean.json','mimeType':'application/json','buffer':json.dumps(clean).encode()});page.wait_for_selector('#confirmImport');page.locator('#confirmImport').check();page.locator('#applyImport').click();check('JSON replacement retains exact selected month',get()['month']=='2026-04' and not get()['lines'])
    check('Other apps storage untouched',page.evaluate("localStorage.getItem('other-app:data')")=='untouched')
    # Restore a synthetic demo for final responsive screenshots.
    page.evaluate("_qa.setState(BudgetEngine.demo('2026-09'))");tab('overview');page.locator('#message').evaluate('(e)=>e.hidden=true');page.locator('#toast').evaluate('(e)=>e.hidden=true')
    for width in [320,390,768,1440]:
        page.set_viewport_size({'width':width,'height':900})
        for which in ['overview','plan','actual','future','guide']:
            tab(which);page.wait_for_timeout(140)
            check(f'No page overflow at {width}px / {which}',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        if width==390:
            tab('overview');page.screenshot(path=str(OUT/'Homeflow_Mobile_Preview.png'),full_page=True)
            page.locator('#coffeeBtn').click();bb=page.locator('#supportCard').bounding_box();check('Mobile support leaves page visible',bb['height']<900*.75 and bb['y']>0);page.screenshot(path=str(OUT/'Homeflow_Support_Preview.png'),full_page=False);page.keyboard.press('Escape')
    tab('overview');page.screenshot(path=str(OUT/'Homeflow_Desktop_Preview.png'),full_page=True)
    tab('future');page.screenshot(path=str(OUT/'Homeflow_Projection_Preview.png'),full_page=True)
    page.locator('#themeBtn').click();page.screenshot(path=str(OUT/'Homeflow_Dark_Preview.png'),full_page=True)
    check('No uncaught JavaScript errors',errors==[])
    browser.close()
print(f'\n{len(checks)} browser checks passed. Navigation restricted; tests used inline HTML and a Storage adapter.')
(OUT/'homeflow_browser_results.txt').write_text('\n'.join('PASS '+s for s in checks)+'\n'+str(len(checks))+' passed\n',encoding='utf-8')
