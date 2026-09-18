from pathlib import Path
import importlib.util
from playwright.sync_api import sync_playwright

BASE=Path(__file__).resolve().parents[1]
OUT=BASE.parent/'qa_output';OUT.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('build_offline',BASE/'tools/build_offline.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);html=b.build()
checks=[]
def check(label,cond):
    assert cond,label;checks.append(label);print('PASS '+label,flush=True)

with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},locale='el-GR')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.evaluate("""()=>{const data={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>data[k]??null,setItem:(k,v)=>data[k]=String(v),removeItem:k=>delete data[k]}});}""")
    page.set_content(html,wait_until='load')
    # Demo supplies enough rows to exercise missing-item suggestions.
    page.locator('#demoBtn').click();page.locator('#confirmAction').click()
    check('Household button has dedicated emphasis class',page.locator('#householdBtn').get_attribute('class').find('household-btn')>=0)
    check('Household button is visible and contains people icon','👥' in page.locator('#householdBtn').inner_text())

    page.locator('[data-tab="plan"]').click()
    check('Notes column is visible','Σημείωση' in page.locator('thead').inner_text())
    first_note=page.locator('[data-note]').first
    first_note.fill('Δοκιμαστική σημείωση');first_note.blur()
    saved=page.evaluate("JSON.parse(localStorage.getItem('homeflow:budget:v1')).lines[0].note")
    check('Inline note saves to existing v1 local data',saved=='Δοκιμαστική σημείωση')

    page.locator('#entryAddBtn').click()
    check('Entry form includes optional note field',page.locator('#entryNote').count()==1)
    quick_title=page.locator('#entryQuickTitle').inner_text()
    check('New expense form explicitly suggests missing budget items','δεν υπάρχουν ακόμα' in quick_title)
    quick_text=page.locator('#entryQuickChips').inner_text()
    check('Existing groceries are not suggested again','Supermarket' not in quick_text)
    check('At least one unused common expense is suggested',len(quick_text.strip())>0)
    page.locator('#closeDialog').click()

    # Settings / 7% investment return.
    page.locator('[data-tab="future"]').click()
    page.locator('[data-action="settings"]').first.click()
    check('Investment return defaults to 7%',page.locator('#investmentReturn').input_value()=='7')
    check('Existing invested balance can be entered',page.locator('#investmentStart').count()==1)
    page.locator('#investmentStart').fill('10000')
    page.locator('#investmentReturn').fill('9')
    page.locator('#horizon').fill('24')
    page.locator('#settingsForm button[type="submit"]').click()
    check('Future view shows chosen investment assumption','9%' in page.locator('#view').inner_text())
    check('Investment projection card is visible','Προβολή επενδύσεων' in page.locator('#view').inner_text())
    check('Projection shows modelled gain/loss','Υποθετικό κέρδος / ζημιά' in page.locator('#view').inner_text())
    link=page.locator('a[href*="wealth-goal-planner"]').get_attribute('href')
    check('Wealth Goal link carries starting balance and return','start=10000.00' in link and 'returnRate=9.00' in link)
    # Screenshot future desktop
    page.screenshot(path=str(OUT/'Homeflow_v1.4_Future_Desktop.png'),full_page=False)

    # Mobile plan / notes / household button.
    page.set_viewport_size({'width':390,'height':844})
    page.locator('[data-tab="plan"]').click()
    check('Plan remains within mobile viewport',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
    page.screenshot(path=str(OUT/'Homeflow_v1.4_Plan_Mobile.png'),full_page=False)
    check('No uncaught errors in v1.4 flows',errors==[])
    browser.close()

print(f'\n{len(checks)} v1.4 UI checks passed.')
