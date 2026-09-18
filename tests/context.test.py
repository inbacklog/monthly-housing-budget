"""v1.2.1: contextual actions, supplied support images, dialog lifecycle.
Loads the real self-contained app with an in-memory Storage adapter. No live
hosting, native OS clipboard, payment or physical device is exercised.
"""
from pathlib import Path
import importlib.util,hashlib,json
from playwright.sync_api import sync_playwright,expect
BASE=Path(__file__).resolve().parents[1]
OUT=BASE.parent/'qa_output';OUT.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('builder',BASE/'tools/build_offline.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
html=builder.build();checks=[]
def check(label,ok):
 assert ok,label
 checks.append(label);print('PASS '+label,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844},locale='el-GR');page.set_default_timeout(5000)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const data={'another-app:key':'keep'};window._store=data;Object.defineProperty(window,'localStorage',{value:{getItem:k=>data[k]??null,setItem:(k,v)=>data[k]=String(v),removeItem:k=>delete data[k]}})}""")
 page.set_content(html,wait_until='load')
 add=page.locator('#quickAddBtn');coffee=page.locator('#coffeeBtn');dialog=page.locator('#dialog')
 def tab(name):page.locator('[data-tab="'+name+'"]').click()
 def close():
  if dialog.is_visible():page.locator('#closeDialog').click()
 def hidden_actions():return not add.is_visible() and not coffee.is_visible()
 def data():return json.loads(page.evaluate("localStorage.getItem('homeflow:budget:v1')"))
 check('Add button starts hidden in the HTML (no pre-init flash)','id="quickAddBtn" hidden' in html)
 check('Welcome has no floating entry button',not add.is_visible())
 for lang in ['el','en']:
  if page.locator('html').get_attribute('lang')!=lang:page.locator('#langBtn').click()
  for screen in ['overview','plan','actual','future','guide']:
   tab(screen)
   check(lang+'/'+screen+': contextual visibility',add.is_visible()==(screen in ['plan','actual']))
   check(lang+'/'+screen+': no stale entry menu',not page.locator('#quickAddMenu').is_visible())
   if screen not in ['plan','actual']:
    page.locator('#quickAddBtn').evaluate('(e)=>e.click()')
    check(lang+'/'+screen+': hidden button cannot open menu programmatically',not page.locator('#quickAddMenu').is_visible())
  tab('plan');add.click()
  check(lang+': budget menu identifies its destination',page.locator('#quickAddTitle').inner_text()==('Προσθήκη στο πλάνο' if lang=='el' else 'Add to your budget'))
  check(lang+': no redundant Budget/Actuals chooser',page.locator('[data-add-context]').count()==0)
  page.locator('[data-add-type="expense"]').click()
  check(lang+': both floating controls hidden while entering an expense',hidden_actions())
  check(lang+': correct expense type is selected',page.locator('[data-entry-type="expense"]').get_attribute('aria-pressed')=='true')
  page.keyboard.press('Escape');expect(dialog).not_to_be_visible();expect(add).to_be_visible()
  check(lang+': native Escape restores only appropriate controls',add.is_visible() and coffee.is_visible())
  for button in ['householdBtn','filesBtn','shareBtn']:
   page.locator('#'+button).click()
   check(lang+'/'+button+': no plus or coffee over dialog',hidden_actions())
   close();expect(add).to_be_visible()
  tab('guide');page.locator('#privacyBtn').click();check(lang+': no floating controls over guide privacy dialog',hidden_actions());close()
  check(lang+': closing a guide dialog does not reveal the plus',not add.is_visible() and coffee.is_visible())
  tab('actual');add.click()
  check(lang+': actual menu identifies its destination',page.locator('#quickAddTitle').inner_text()==('Νέα πραγματική κίνηση' if lang=='el' else 'New actual transaction'))
  page.locator('[data-add-type="income"]').click()
  check(lang+': actual income form includes date and starts without an amount',page.locator('#entryDate').count()==1 and page.locator('#entryAmount').input_value()=='')
  close();add.click();tab('future')
  check(lang+': changing tabs closes menu and hides add',not add.is_visible() and not page.locator('#quickAddMenu').is_visible())
  tab('plan');add.click();coffee.click()
  check(lang+': support excludes entry controls and add menu',not add.is_visible() and not page.locator('#quickAddMenu').is_visible() and not dialog.is_visible())
  expect(page.locator('.support-card img').first).to_be_visible()
  check(lang+': supplied full-size QR assets decode as image files',page.evaluate('Array.from(document.querySelectorAll(".support-card img")).map(i=>[i.naturalWidth,i.naturalHeight])')==[[2048,2048],[280,278]])
  check(lang+': support panel is nonmodal and compact',page.locator('#supportCard').bounding_box()['height']<=844*.73 and not dialog.is_visible())
  page.keyboard.press('Escape');expect(add).to_be_visible()
  check(lang+': support close restores contextual add',add.is_visible() and page.evaluate('document.activeElement.id')=='coffeeBtn')
  coffee.click();tab('guide');check(lang+': support is dismissed on navigation',not page.locator('#supportCard').is_visible() and not add.is_visible())
 # Exercise real UI saves and persistence serialization with synthetic test data only.
 if page.locator('html').get_attribute('lang')!='el':page.locator('#langBtn').click()
 tab('plan');add.click();page.locator('[data-add-type="income"]').click()
 page.locator('#entryLabel').fill('Test income');page.locator('#entryAmount').fill('1234,56');page.locator('#saveEntry').click()
 check('Budget + saves only one budget entry',len(data()['lines'])==1 and len(data()['transactions'])==0 and data()['lines'][0]['amount']==1234.56)
 tab('actual');add.click();page.locator('[data-add-type="expense"]').click();page.locator('#entryLabel').fill('Test receipt');page.locator('#entryAmount').fill('19,99');page.locator('#saveEntry').click()
 check('Actual + saves only one actual expense',len(data()['lines'])==1 and len(data()['transactions'])==1 and data()['transactions'][0]['amount']==19.99)
 saved=data();page.set_content(html,wait_until='load');tab('plan')
 check('Saved data round-trips without reset',data()==saved and page.locator('#budgetTable tbody tr').count()==1)
 check('Other apps storage untouched',page.evaluate("localStorage.getItem('another-app:key')")=='keep')
 for width in [320,390,768,1440]:
  height=844 if width<768 else 1000
  page.set_viewport_size({'width':width,'height':height});tab('plan')
  a=add.bounding_box();b=coffee.bounding_box()
  check(str(width)+': add and coffee stay separate',a['x']+a['width']<=b['x']-3)
  check(str(width)+': both controls fit viewport',a['x']>=0 and b['x']+b['width']<=width)
  check(str(width)+': no page horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
  coffee.click();box=page.locator('#supportCard').bounding_box()
  check(str(width)+': support panel stays inside viewport',box['x']>=0 and box['y']>=0 and box['x']+box['width']<=width and box['height']<=height*.73)
  page.keyboard.press('Escape')
 # Actual screenshots of final UI, not mockups. Demo is expressly synthetic.
 page.locator('#demoBtn').click();page.locator('#confirmAction').click();tab('plan')
 page.set_viewport_size({'width':1440,'height':1000});page.evaluate('window.scrollTo(0,0)')
 page.screenshot(path=str(OUT/'Homeflow_v1.2.1_Plan_Desktop.png'))
 page.set_viewport_size({'width':390,'height':844});tab('plan');add.click();page.locator('[data-add-type="income"]').click()
 page.screenshot(path=str(OUT/'Homeflow_v1.2.1_Form_Mobile.png'));close()
 coffee.click();page.screenshot(path=str(OUT/'Homeflow_v1.2.1_Support_Mobile.png'));page.keyboard.press('Escape')
 tab('guide');page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(OUT/'Homeflow_v1.2.1_Guide_Mobile.png'))
 page.locator('#themeBtn').click();tab('plan');coffee.click()
 check('Dark support uses supplied QR without filters',page.locator('.support-card img').first.evaluate('i=>getComputedStyle(i).filter')=='none')
 page.screenshot(path=str(OUT/'Homeflow_v1.2.1_Support_Dark_Mobile.png'))
 check('No uncaught JavaScript exceptions',errors==[])
 browser.close()
(OUT/'context.log').write_text('\n'.join('PASS '+s for s in checks)+f'\n{len(checks)} contextual-UI checks passed.\n')
print(f'\n{len(checks)} contextual-UI checks passed.')
