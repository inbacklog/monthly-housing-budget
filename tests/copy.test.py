"""v1.2.1 bilingual user-copy regression checks.
Uses the actual standalone builder with inline assets and an in-memory Storage
adapter. It does not test hosted deployment or real-device persistence.
"""
from pathlib import Path
import importlib.util
import re
from playwright.sync_api import sync_playwright

BASE=Path(__file__).resolve().parents[1]
OUT=BASE.parent/'qa_output'
OUT.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('build_offline',BASE/'tools/build_offline.py')
builder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
html=builder.build()
forbidden=[
    'Κανένα προσωπικό ποσό δεν είναι προεπιλεγμένο',
    'There are no personal amounts pre-filled',
    'Δεν υποθέτουμε δύο μισθούς',
    'We do not assume two incomes',
    'Δεν χρησιμοποιούμε στοιχεία χαρτοφυλακίου',
    'No unprovided portfolio details are assumed',
    'Τα δημόσια αρχεία δεν περιέχουν προσωπικό προϋπολογισμό',
    'Public files do not contain a personal household budget',
    'Δεν βάζουμε ποσό για εσένα',
    'We never fill a price for you',
    'No preset prices',
    'Χωρίς έτοιμα ποσά',
    'Τεχνική απομόνωση',
    'Technical isolation',
    'public repo',
    'GenAI app',
    'Share it only after publishing',
    'Στείλε τον μόνο αφού δημοσιευτεί',
    'ούτε προσωπικά δεδομένα',
    'or personal data',
]
checks=[]
def check(label,condition):
    assert condition,label
    checks.append(label)
    print('PASS '+label,flush=True)
def clean_visible(page):
    visible=page.locator('body').inner_text()
    return not any(s.casefold() in visible.casefold() for s in forbidden)

check('Removed development-context wording is absent from all runtime source',
      not any(x.casefold() in html.casefold() for x in forbidden))
check('Storage key remains compatible with v1.1.0',"KEY='homeflow:budget:v1'" in html)
check('Release and cache identify v1.2.1','v1.2.1 · inbacklog' in html and 'homeflow-static-v1.2.1' in (BASE/'sw.js').read_text())
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},locale='el-GR')
    page.set_default_timeout(5000)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.evaluate("""()=>{const data={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>data[k]??null,setItem:(k,v)=>data[k]=String(v),removeItem:k=>delete data[k]}});} """)
    page.set_content(html,wait_until='load')
    check('Greek welcome gives a clear next action','Φτιάξε τον μηνιαίο προϋπολογισμό σου.' in page.locator('#view').inner_text())
    check('Greek welcome contains the new short description','Πρόσθεσε τα έσοδα και τα έξοδά σου ή δοκίμασε ένα παράδειγμα για να ξεκινήσεις.' in page.locator('#view').inner_text())
    page.screenshot(path=str(OUT/'Homeflow_v1.2.1_Welcome_Desktop.png'),full_page=False)
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(OUT/'Homeflow_v1.2.1_Welcome_Mobile.png'),full_page=False)
    for language in ['el','en']:
        if page.locator('html').get_attribute('lang')!=language:page.locator('#langBtn').click()
        for tab in ['overview','plan','actual','future','guide']:
            page.locator(f'[data-tab="{tab}"]').click()
            check(f'{language} / {tab}: visible copy has no development-context messages',clean_visible(page))
            check(f'{language} / {tab}: mobile layout fits',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        page.locator('#privacyBtn').click()
        check(f'{language}: privacy dialog is free of project comparisons and implementation jargon',clean_visible(page))
        privacy=page.locator('#dialogBody').inner_text()
        check(f'{language}: privacy still explains sharing and unencrypted storage',
              ('δεν είναι κρυπτογραφημένος' in privacy and 'δεν είναι κρυπτογραφημένα' in privacy) if language=='el' else ('not encrypted' in privacy and 'cannot be revoked' in privacy))
        page.locator('#closeDialog').click()
        page.locator('#demoBtn').click()
        copy=page.locator('#dialogBody').inner_text()
        check(f'{language}: example warns before replacing budget AND transactions',
              ('αντικαταστήσει' in copy and 'κινήσεις' in copy) if language=='el' else ('replace' in copy and 'transactions' in copy))
        page.locator('#confirmAction').click()
        check(f'{language}: example has a simple sample-data label',page.locator('#message').inner_text()==('Ενδεικτικά δεδομένα' if language=='el' else 'Sample data'))
        page.locator('#shareBtn').click()
        check(f'{language}: sharing still requires explicit consent',page.locator('#makeLink').is_disabled())
        page.locator('#shareConsent').check();page.locator('#makeLink').click();page.wait_for_selector('#shareURL')
        check(f'{language}: generated link retains same destination',page.locator('#shareURL').input_value().startswith('https://inbacklog.github.io/monthly-housing-budget/#plan='))
        check(f'{language}: share dialog no longer tells visitors to deploy the app',clean_visible(page))
        page.locator('#closeDialog').click()
        page.locator('#filesBtn').click()
        check(f'{language}: import-format guidance remains available','CSV UTF-8' in page.locator('#dialogBody').inner_text())
        page.locator('#closeDialog').click()
    check('No uncaught exceptions in copy/navigation tests',errors==[])
    browser.close()
print(f'\n{len(checks)} copy checks passed.')
(OUT/'copy_v111.log').write_text('\n'.join('PASS '+c for c in checks)+f'\n{len(checks)} copy checks passed.\n',encoding='utf-8')
