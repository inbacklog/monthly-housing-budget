from pathlib import Path
import importlib.util
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_offline',BASE/'tools/build_offline.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);html=b.build()
checks=[]
def check(label,cond):
    assert cond,label;checks.append(label);print('PASS '+label,flush=True)
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},locale='el-GR')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html,wait_until='load')
    page.locator('#demoBtn').click();page.locator('#confirmAction').click()
    page.locator('[data-tab="future"]').click()
    page.locator('[data-action="settings"]').first.click()
    check('Default horizon is 10 years',page.locator('#horizonYears').input_value()=='10')
    check('Quick horizon presets are present',page.locator('[data-horizon-years]').count()==4)
    page.locator('[data-horizon-years="20"]').click()
    check('20-year preset updates input',page.locator('#horizonYears').input_value()=='20')
    page.locator('#settingsForm button[type="submit"]').click()
    txt=page.locator('#view').inner_text()
    check('Future summary uses years','20 χρόνια' in txt)
    check('Long horizon uses annual snapshots','Έτος με το έτος' in txt)
    check('Combined financial-position metric is shown','Cash + απόθεμα + επενδύσεις' in txt)
    rows=page.locator('#view table tbody tr').count()
    check('20-year screen does not show 240 monthly rows',rows<=21)
    page.locator('[data-action="settings"]').first.click();page.locator('#horizonYears').fill('50');page.locator('#settingsForm button[type="submit"]').click()
    check('50-year horizon is accepted','50 χρόνια' in page.locator('#view').inner_text())
    check('No uncaught v1.5 errors',errors==[])
    browser.close()
print(f'\n{len(checks)} v1.5 UI checks passed.')
