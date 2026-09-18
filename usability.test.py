"""v1.1 guided-entry/batch regression checks (Chromium, inline local assets).
Navigation is restricted in the authoring environment. Storage here is an
in-memory adapter, NOT evidence of real-device persistence or installation.
Run: python tests/usability.test.py
"""
from pathlib import Path
import re, json, base64, mimetypes
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1];OUT=BASE.parent/'qa_output';OUT.mkdir(exist_ok=True)

def source_html():
    html=(BASE/'index.html').read_text()
    html=html.replace('<link rel="stylesheet" href="styles.css">','<style>'+(BASE/'styles.css').read_text()+'</style>')
    html=html.replace('<link rel="manifest" href="manifest.webmanifest">','')
    for f in ['engine.js','presets.js','app.js']:
        html=html.replace(f'<script src="{f}" defer></script>','')
    for asset in ['assets/icon.svg','assets/icon-192.png','assets/buymeacoffee-qr.png','assets/wallet-of-satoshi-qr.png']:
        html=html.replace(asset,'data:'+mimetypes.guess_type(asset)[0]+';base64,'+base64.b64encode((BASE/asset).read_bytes()).decode())
    app=(BASE/'app.js').read_text().replace('render();checkShared();','window._qa={encodeShare,decodeShare,getState:()=>JSON.parse(JSON.stringify(state)),setState:p=>commit(p)};render();checkShared();')
    return html.replace('</body>','<script>window.HOMEFLOW_OFFLINE=true;</script>'+''.join('<script>'+s+'</script>' for s in [(BASE/'engine.js').read_text(),(BASE/'presets.js').read_text(),app])+'</body>')

checks=[]
def check(label,test):
    if not test: raise AssertionError(label)
    checks.append(label);print('PASS '+label,flush=True)

with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1080},locale='el-GR')
    page.set_default_timeout(4500)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.evaluate("""()=>{const data={'unrelated-app:state':'keep'};window._store=data;Object.defineProperty(window,'localStorage',{value:{getItem:k=>data[k]??null,setItem:(k,v)=>data[k]=String(v),removeItem:k=>delete data[k]}});} """)
    page.set_content(source_html(),wait_until='load')
    state=lambda:page.evaluate('_qa.getState()')
    def tab(name):page.locator(f'[data-tab="{name}"]').click()
    def close():
        if page.locator('#dialog').is_visible():page.locator('#closeDialog').click()
    def blank():
        close();page.evaluate("_qa.setState(BudgetEngine.blank('2026-09'))");tab('plan')
    def save():page.locator('#saveEntry').click()
    def shortcut(id,actual=False):page.locator(f'[data-quick-preset="{id}"][data-actual="{int(actual)}"]').click()
    def batch_row(label):return page.locator('[data-quick-row]').filter(has=page.locator('label',has_text=re.compile('^'+re.escape(label)+'$')))

    tab('plan')
    check('Eight visible expense shortcuts on empty budget',page.locator('[data-quick-preset]').count()==8)
    shortcut('groceries')
    check('Groceries shortcut selects description and food category',page.locator('#entryLabel').input_value()=='Supermarket' and page.locator('#entryCategory').input_value()=='food')
    check('No price is inserted by a shortcut',page.locator('#entryAmount').input_value()=='')
    save();check('Empty amount never creates a financial record',state()['lines']==[] and bool(page.locator('#formError').inner_text()))
    page.locator('#entryAmount').fill('1234,50');page.locator('#entryFrequency').select_option('yearly');page.locator('#entryMember').select_option('member1')
    page.locator('#entrySuggestions > summary').click();page.locator('[data-entry-preset="rent"]').first.click()
    check('Changing suggestions retains amount, frequency and person',page.locator('#entryAmount').input_value()=='1234,50' and page.locator('#entryFrequency').input_value()=='yearly' and page.locator('#entryMember').input_value()=='member1')
    save();check('Greek decimal comma stores exact numeric value',state()['lines'][0]['amount']==1234.5)
    check('Annual selected frequency not reset by shortcut',state()['lines'][0]['frequency']=='yearly')
    shortcut('rent');page.locator('#entryMember').select_option('member1');page.locator('#entryAmount').fill('1350')
    check('Possible duplicate budget entry is signalled',page.locator('#duplicateWarning').is_visible())
    before=state();save();check('Duplicate not committed without explicit acknowledgement',state()==before)
    page.locator('#allowDuplicate').check();save();check('Intentional separate entry may be explicitly saved',len(state()['lines'])==2)

    blank();page.locator('[data-action="add-plan"]').first.click()
    page.locator('#entryType').select_option('income');page.locator('[data-entry-preset="salary"]').first.click()
    page.locator('#entryAmount').fill('1700');save()
    check('Income also has shortcuts and correct type',state()['lines'][0]['type']=='income' and state()['lines'][0]['category']=='income')
    page.locator('[data-action="library"]').click();page.locator('#librarySearch').fill('ΝΕΡΟ')
    check('Full picker searches Greek without accents',page.locator('[data-library-preset="water"]').count()==1)
    page.locator('[data-library-preset="water"]').click();page.locator('#entryAmount').fill('18,75')
    page.locator('button[name="saveNext"]').click()
    check('Save and next commits once, keeping a fresh blank draft',len(state()['lines'])==2 and page.locator('#entryAmount').input_value()=='' and page.locator('#entryLabel').input_value()=='')
    page.locator('[data-entry-preset="electricity"]').first.click();page.locator('#entryAmount').fill('82');save()
    check('Second quick entry keeps independent amount',state()['lines'][-1]['amount']==82 and len(state()['lines'])==3)
    page.locator('[data-action="add-plan"]').first.click();page.locator('#entryAll summary').click();page.locator('#entrySuggestSearch').fill('Netflix');page.locator('#entrySuggestSearch').press('Enter')
    check('Search Enter does not submit a draft',len(state()['lines'])==3 and page.locator('#dialog').is_visible())
    page.locator('[data-entry-preset="streaming"]').last.click();page.locator('#entryAmount').fill('9.99');save()
    check('Subscription shortcut marks subscription flag',state()['lines'][-1]['subscription'] is True)
    check('Category totals display computed entries',page.locator('[data-category-filter="housing"]').count()==1)
    page.locator('[data-category-filter="housing"]').click()
    check('Tapping category filters budget without changing values',page.locator('#categoryFilter').input_value()=='housing' and len(state()['lines'])==4)
    page.locator('#categoryFilter').select_option('')
    tab('actual');shortcut('groceries',True)
    check('Actual shortcuts default to a real transaction, not budget',page.locator('#entryDate').count()==1 and page.locator('#entryFrequency').count()==0)
    page.locator('#entryDate').fill('2026-09-08');page.locator('#entryAmount').fill('27,35')
    page.locator('#entrySuggestions > summary').click();page.locator('#entryAll summary').click();page.locator('#entrySuggestSearch').fill('φαρμακ');page.locator('#entryLibrary [data-entry-preset="pharmacy"]').click()
    check('Actual suggestion switch preserves date and amount',page.locator('#entryDate').input_value()=='2026-09-08' and page.locator('#entryAmount').input_value()=='27,35')
    save();check('Actual shortcut does not mutate the budget',len(state()['lines'])==4 and len(state()['transactions'])==1)
    page.locator('[data-action="library-actual"]').click();page.locator('#librarySearch').fill('water');page.locator('[data-library-preset="water"]').click()
    check('All-expenses picker retains actual context',page.locator('#entryDate').count()==1);close()
    page.locator('#closedMonth').check();page.locator('[data-edit-actual]').click();page.locator('#entryDate').fill('2026-10-09');save()
    check('Moving an actual payment reopens both affected months','2026-09' not in state()['closedMonths'] and '2026-10' not in state()['closedMonths'])

    blank();page.locator('[data-action="quick-budget"]').first.click()
    check('Quick monthly setup contains only blank suggested prices',all(x.input_value()=='' for x in page.locator('[data-quick-amount]').all()))
    before=state();page.locator('#quickSearch').fill('Supermarket');batch_row('Supermarket').locator('input').fill('320,50')
    page.locator('#quickSearch').fill('');batch_row('Ενοίκιο').locator('input').fill('700')
    batch_row('Ύδρευση / νερό').locator('input').fill('120');batch_row('Ύδρευση / νερό').locator('select').select_option('yearly')
    check('Quick summary converts annual amounts to monthly','1.030,5' in page.locator('#quickTotal').inner_text())
    check('Previewing several estimates does not write to storage',state()==before)
    page.locator('#quickSearch').fill('Supermarket')
    check('Filtering retains values on hidden draft rows',batch_row('Ύδρευση / νερό').locator('input').input_value()=='120')
    page.locator('#quickApply').click()
    check('Batch save requires a review and acknowledgement',page.locator('#quickConfirm').is_visible() and page.locator('#quickApply').is_disabled() and state()==before)
    page.locator('#quickConsent').check();page.locator('#quickApply').click()
    check('Only three filled rows are added',len(state()['lines'])==3)
    check('Budget total equals sum of monthly equivalents',abs(page.evaluate('BudgetEngine.budget(_qa.getState()).expenses')-1030.5)<1e-9)
    initial_ids=[x['id'] for x in state()['lines']]
    page.locator('[data-action="quick-budget"]').first.click()
    check('Existing groceries appear once, not as duplicate new suggestion',page.locator('[data-quick-row]').filter(has=page.locator('label',has_text=re.compile('^Supermarket$'))).count()==1)
    page.locator('#quickCategory').select_option('food');batch_row('Supermarket').locator('input').fill('350');page.locator('#quickApply').click();page.locator('#quickConsent').check();page.locator('#quickApply').click()
    check('Quick editing keeps existing IDs and record count',[x['id'] for x in state()['lines']]==initial_ids)
    check('Updated category sums recalculate live',page.evaluate('BudgetEngine.budget(_qa.getState()).categories.food')==350)
    page.locator('[data-action="quick-budget"]').first.click();batch_row('Ενοίκιο').locator('input').fill('900');close()
    check('Cancelling a batch draft leaves saved amounts untouched',next(l for l in state()['lines'] if l['label']=='Ενοίκιο')['amount']==700)
    page.locator('[data-action="quick-budget"]').first.click();batch_row('Ενοίκιο').locator('input').fill('-10');page.locator('#quickApply').click()
    check('Invalid batch input is rejected atomically',next(l for l in state()['lines'] if l['label']=='Ενοίκιο')['amount']==700 and bool(page.locator('#formError').inner_text()));close()

    # Preserve stored v1 data under the same key, including custom entries & real months.
    snapshot=state();page.set_content(source_html(),wait_until='load')
    check('Reloading the UI reads the previous v1 JSON unchanged',state()==snapshot)
    check('Unrelated app storage is untouched',page.evaluate("localStorage.getItem('unrelated-app:state')")=='keep')
    tab('plan');page.locator('#langBtn').click();shortcut('electricity')
    check('English suggestions and form are translated',page.locator('#entryLabel').input_value()=='Electricity' and page.locator('#saveEntry').inner_text()=='Save entry');close()
    page.locator('#langBtn').click()
    # Responsive checks include entry forms and the new wide batch editor.
    for width,height in [(320,740),(390,844),(768,1024),(1440,1000)]:
        page.set_viewport_size({'width':width,'height':height});tab('plan')
        check(f'Plan and shortcuts fit {width}px',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        shortcut('groceries')
        check(f'Entry suggestions fit {width}px dialog',page.locator('#dialog').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'))
        close();page.locator('[data-action="quick-budget"]').first.click()
        check(f'Batch editor fits {width}px dialog',page.locator('#dialog').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'))
        if width==390:
            page.locator('#quickFilled').check();page.screenshot(path=str(OUT/'Homeflow_QuickSetup_Mobile_v1.1.0.png'))
        close();tab('actual');check(f'Actual shortcuts fit {width}px',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
    # Preview uses empty amounts (no private financial data in public assets).
    blank();page.set_viewport_size({'width':1440,'height':1100});page.evaluate('window.scrollTo(0,300)');page.locator('#toast').evaluate('(e)=>e.hidden=true')
    page.screenshot(path=str(OUT/'Homeflow_Plan_Desktop_v1.1.0.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':900});page.evaluate('window.scrollTo(0,270)')
    page.screenshot(path=str(OUT/'Homeflow_Shortcuts_Mobile_v1.1.0.png'))
    shortcut('groceries');page.screenshot(path=str(OUT/'Homeflow_AddExpense_Mobile_v1.1.0.png'));close()
    page.locator('#themeBtn').click();shortcut('groceries');check('Dark theme applies to new controls',page.locator('html').get_attribute('data-theme')=='dark');page.screenshot(path=str(OUT/'Homeflow_Expense_Dark_v1.1.0.png'));close()
    page.locator('#coffeeBtn').click();box=page.locator('#supportCard').bounding_box();check('Support remains compact and nonmodal',box['height']<900*.75 and not page.locator('#dialog').is_visible());page.screenshot(path=str(OUT/'Homeflow_Support_v1.1.0.png'))
    check('No uncaught script errors in all new flows',errors==[])
    browser.close()

print('\n'+str(len(checks))+' usability checks passed.')
(OUT/'usability-results.txt').write_text('\n'.join('PASS '+c for c in checks)+'\n'+str(len(checks))+' passed\n')
