"""Homeflow v1.3 row-colour UI regression checks."""
from pathlib import Path
import importlib.util
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1];OUT=BASE.parent/'qa_output';OUT.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('offline_builder',BASE/'tools/build_offline.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
HTML=m.build().replace('render();checkShared();','window._qa={getState:()=>JSON.parse(JSON.stringify(state)),setState:p=>commit(p)};render();checkShared();')
checks=[]
def check(name,ok):
    assert ok,name
    checks.append(name);print('PASS '+name,flush=True)
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1280,'height':900},locale='el-GR',reduced_motion='reduce');page.set_default_timeout(4000)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.evaluate("""()=>{const d={};window._store=d;Object.defineProperty(window,'localStorage',{value:{getItem:k=>d[k]??null,setItem:(k,v)=>d[k]=String(v),removeItem:k=>delete d[k]}})}""")
    page.set_content(HTML,wait_until='load')
    page.locator('#demoBtn').click();page.locator('#confirmAction').click();page.locator('[data-tab="plan"]').click()
    check('Default list colouring is soft',page.locator('#rowColorMode').input_value()=='soft' and page.locator('html').get_attribute('data-row-colors')=='soft')
    check('All four financial types retain textual labels',all(x in page.locator('#view').inner_text() for x in ['Έσοδο','Έξοδο','Αποταμίευση','Επένδυση']))
    check('Rows expose type classes',page.locator('tr.type-income').count()>0 and page.locator('tr.type-expense').count()>0 and page.locator('tr.type-saving').count()>0 and page.locator('tr.type-investment').count()>0)
    income_bg=page.locator('tr.type-income').first.locator('td').nth(1).evaluate('(e)=>getComputedStyle(e).backgroundColor')
    expense_bg=page.locator('tr.type-expense').first.locator('td').nth(1).evaluate('(e)=>getComputedStyle(e).backgroundColor')
    check('Income and expense use different soft tints',income_bg!=expense_bg)
    page.locator('#rowColorMode').select_option('scaled')
    check('Amount-aware mode is explicit and persisted',page.locator('html').get_attribute('data-row-colors')=='scaled' and 'rowColors' in page.evaluate("localStorage.getItem('homeflow:prefs:v1')"))
    # Rent is 700 monthly; streaming is 12 monthly, both expense type.
    rent=page.locator('tr.type-expense').filter(has_text='Ενοίκιο').first
    stream=page.locator('tr.type-expense').filter(has_text='Streaming').first
    rent_alpha=float(rent.evaluate("e=>getComputedStyle(e).getPropertyValue('--row-alpha')"))
    stream_alpha=float(stream.evaluate("e=>getComputedStyle(e).getPropertyValue('--row-alpha')"))
    check('Higher same-type amount receives stronger tint',rent_alpha>stream_alpha)
    check('Scaled explanation states same-type comparison','μέσο όρο του ίδιου τύπου' in page.locator('.row-color-note').inner_text())
    # Switching off leaves text/type metadata while removing row tint.
    page.locator('#rowColorMode').select_option('off')
    check('No-colour mode remains available',page.locator('html').get_attribute('data-row-colors')=='off')
    check('Text type labels remain when colour is off','Έξοδο' in page.locator('tr.type-expense').first.inner_text())
    # Preference survives full UI reload through localStorage adapter.
    page.set_content(HTML,wait_until='load');page.locator('[data-tab="plan"]').click()
    check('Colour preference survives UI reload',page.locator('#rowColorMode').input_value()=='off')
    page.locator('#rowColorMode').select_option('scaled');page.locator('#themeBtn').click()
    check('Dark theme and scaled colours coexist',page.locator('html').get_attribute('data-theme')=='dark' and page.locator('html').get_attribute('data-row-colors')=='scaled')
    page.set_viewport_size({'width':390,'height':844});page.locator('[data-tab="plan"]').click()
    check('Colour controls fit mobile width',page.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth+1'))
    page.screenshot(path=str(OUT/'Homeflow_v1.3_Colours_Mobile.png'),full_page=False)
    page.set_viewport_size({'width':1440,'height':950});page.screenshot(path=str(OUT/'Homeflow_v1.3_Colours_Desktop.png'),full_page=False)
    check('No uncaught script errors',not errors)
    browser.close()
print(f'\n{len(checks)} colour UI checks passed.')
