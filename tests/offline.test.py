"""Smoke-check the actual self-contained HTML (no test-instrumented UI).
Navigation is restricted here; set_content loads the saved HTML itself.
Storage-denied operation is exercised. This is not a PWA installation test.
"""
from pathlib import Path
import sys,base64,re
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
path=Path(sys.argv[1]) if len(sys.argv)>1 else BASE.parent/'Homeflow_Offline_v1.1.1.html'
html=path.read_text(encoding='utf-8');count=0

def check(label,result):
    global count
    assert result,label
    count+=1;print('PASS '+label)

check('Offline file contains no external scripts',not re.search(r'<script[^>]+src=',html))
check('Offline file contains no stylesheet requests','rel="stylesheet"' not in html)
check('No development instrumentation in final file','window._qa' not in html)
check('Full Excel template embedded', 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,' in html)
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844});errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html,wait_until='load')
    check('Actual standalone renders without a build or backend',page.locator('#view').inner_text()!='')
    check('Storage-denied warning is visible',page.locator('#message').is_visible())
    page.locator('[data-tab="plan"]').click()
    check('New catalogue available in offline copy',page.locator('[data-quick-preset]').count()==8)
    page.locator('[data-quick-preset="groceries"]').click();page.locator('#entryAmount').fill('23,45');page.locator('#saveEntry').click()
    check('Offline arithmetic accepts comma amounts',page.locator('[data-amount]').input_value()=='23.45')
    page.locator('[data-action="quick-budget"]').first.click()
    check('Offline batch editor works',page.locator('#quickBudgetForm').is_visible());page.locator('#closeDialog').click()
    page.locator('#filesBtn').click()
    href=page.locator('a[download="Household_Budget_Import_Template.xlsx"]').get_attribute('href')
    check('Embedded Excel download is byte-exact',base64.b64decode(href.split(',',1)[1])==(BASE/'templates/Household_Budget_Import_Template.xlsx').read_bytes());page.locator('#closeDialog').click()
    page.locator('#coffeeBtn').click()
    check('Both QR images load in standalone without a remote asset',page.evaluate('Array.from(document.querySelectorAll(".support-card img")).every(i=>i.complete&&i.naturalWidth>0)'))
    check('Standalone UI has no uncaught errors',errors==[])
    browser.close()
print('\n'+str(count)+' standalone smoke checks passed.')
