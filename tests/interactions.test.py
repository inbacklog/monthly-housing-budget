"""v1.2 regression: mouse + emulated touch sorting, keyboard, tap alternative,
quick add and type-first forms. Inline local assets and a Storage adapter are
used because hosted browser navigation is restricted in this environment.
This is NOT a real-phone or live GitHub Pages installation test.
"""
from pathlib import Path
import re,json,base64,mimetypes
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1];OUT=BASE.parent/'qa_output';OUT.mkdir(exist_ok=True)
def html():
 s=(BASE/'index.html').read_text().replace('<link rel="stylesheet" href="styles.css">','<style>'+(BASE/'styles.css').read_text()+'</style>').replace('<link rel="manifest" href="manifest.webmanifest">','')
 for f in ['engine.js','presets.js','app.js']:s=s.replace(f'<script src="{f}" defer></script>','')
 for a in ['assets/icon.svg','assets/icon-192.png','assets/buymeacoffee-qr.png','assets/wallet-of-satoshi-qr.png']:
  s=s.replace(a,'data:'+mimetypes.guess_type(a)[0]+';base64,'+base64.b64encode((BASE/a).read_bytes()).decode())
 app=(BASE/'app.js').read_text().replace('render();checkShared();','window._qa={get:()=>BudgetEngine.clone(state),set:p=>commit(p),encodeShare,decodeShare};render();checkShared();')
 return s.replace('</body>','<script>window.HOMEFLOW_OFFLINE=true;</script>'+''.join('<script>'+text+'</script>' for text in [(BASE/'engine.js').read_text(),(BASE/'presets.js').read_text(),app])+'</body>')
checks=[]
def check(name,result):
 assert result,name
 checks.append(name);print('PASS '+name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000},locale='el-GR');page.set_default_timeout(4000);errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const data={'another-app:key':'keep'};window._store=data;Object.defineProperty(window,'localStorage',{value:{getItem:k=>data[k]??null,setItem:(k,v)=>data[k]=String(v),removeItem:k=>delete data[k]}});} """)
 page.set_content(html(),wait_until='load')
 get=lambda:page.evaluate('_qa.get()')
 def close():
  if page.locator('#dialog').is_visible():page.locator('#closeDialog').click()
 def tab(t):page.locator(f'[data-tab="{t}"]').click()
 def demo():
  close();page.evaluate("_qa.set(BudgetEngine.demo('2026-09'))");tab('plan');page.locator('#toast').evaluate('(e)=>e.hidden=true')
 def ids(list='lines'):return [x['id'] for x in get()[list]]
 def handles():return page.locator('.row-handle')
 def grip(id):return page.locator(f'[data-row-handle="{id}"]')
 def table_top():page.locator('#budgetTable').evaluate('(t)=>{t.closest(".table-wrap").scrollTop=0;t.closest(".table-wrap").scrollIntoView({block:"center",behavior:"instant"});}')
 def mouse_move(from_index,to_index):
  table_top();src=handles().nth(from_index);dst=handles().nth(to_index);a=src.bounding_box();b=dst.bounding_box()
  page.mouse.move(a['x']+a['width']/2,a['y']+a['height']/2);page.mouse.down()
  page.mouse.move(b['x']+b['width']/2,b['y']+b['height']*(.8 if from_index<to_index else .2),steps=12);page.wait_for_timeout(50);page.mouse.up();page.wait_for_timeout(420)
 demo();before=get();mouse_move(0,3)
 check('Mouse drag moves a budget row to the chosen position',ids()==['demo1','demo2','demo3','demo0']+[f'demo{i}' for i in range(4,14)])
 check('Mouse reorder changes no amounts, labels or flags',sorted(get()['lines'],key=lambda r:r['id'])==sorted(before['lines'],key=lambda r:r['id']))
 check('Custom order is written to browser storage',json.loads(page.evaluate("localStorage.getItem('homeflow:budget:v1')"))['lines']==get()['lines'])
 check('Drag does not accidentally open a dialog',not page.locator('#dialog').is_visible())
 page.locator('.toast-undo').click();check('Undo restores order without deleting entries',ids()==[f'demo{i}' for i in range(14)])
 grip('demo0').focus();grip('demo0').press('ArrowDown')
 check('Keyboard ArrowDown moves only that row',ids()[:3]==['demo1','demo0','demo2'])
 check('Keyboard focus follows the moved handle',page.evaluate('document.activeElement.dataset.rowHandle')=='demo0')
 grip('demo0').press('End');check('Keyboard End moves the row to the bottom',ids()[-1]=='demo0')
 grip('demo0').press('Home');check('Keyboard Home moves the row to the top',ids()[0]=='demo0')
 grip('demo2').click();check('A tap opens a non-drag position picker',page.locator('#moveRowForm').is_visible())
 page.locator('#moveLast').click();page.locator('#moveRowForm button[type="submit"]').click();check('Tap alternative moves row to chosen final position',ids()[-1]=='demo2')
 # Filtered order must keep hidden slots fixed.
 demo();before=ids();page.locator('#categoryFilter').select_option('housing')
 shown=[h.get_attribute('data-row-handle') for h in handles().all()];grip(shown[0]).press('End');after=ids()
 check('Filtering reorders visible slots only',all(before[i]==after[i] for i in range(len(before)) if before[i] not in shown) and [x for x in after if x in shown]==shown[1:]+shown[:1])
 check('Filtering warning explains scope','ορατών γραμμών' in page.locator('#planOrderHint').inner_text())
 page.locator('#categoryFilter').select_option('');old=get();table_top();a=grip('demo0').bounding_box();b=grip('demo4').bounding_box()
 page.mouse.move(a['x']+20,a['y']+20);page.mouse.down();page.mouse.move(b['x']+20,b['y']+20,steps=8);page.keyboard.press('Escape');page.mouse.up()
 check('Escape cancels drag without mutation',get()==old)
 page.wait_for_timeout(420);table_top();a=handles().first.bounding_box();b=handles().nth(3).bounding_box();old=get()
 page.mouse.move(a['x']+20,a['y']+20);page.mouse.down();page.mouse.move(b['x']+20,b['y']+20,steps=8);page.mouse.move(2,2);page.mouse.up()
 check('Dropping outside the table cancels the move',get()==old)
 page.wait_for_timeout(420)
 # Order survives a fresh render of the actual app, using persisted JSON.
 order=ids();page.set_content(html(),wait_until='load');tab('plan')
 check('Saved order survives reloading the app in the storage adapter',ids()==order)
 # Optional actual data with a deliberately different date order.
 page.evaluate("""()=>{const p=BudgetEngine.blank('2026-09');p.transactions=[{id:'outside',type:'expense',label:'Other month',category:'food',member:'',amount:9,funding:'cash',date:'2026-08-15'},...['01','03','02'].map((d,i)=>({id:'t'+i,type:'expense',label:'Receipt '+i,category:'food',member:'',amount:i+10,funding:'cash',date:'2026-09-'+d}))];p.closedMonths=['2026-09'];_qa.set(p)}""");tab('actual')
 check('Existing actuals retain date-descending default order',[h.get_attribute('data-row-handle') for h in handles().all()]==['t1','t2','t0'])
 before=get();grip('t1').press('End')
 check('Actual records support custom row order',[h.get_attribute('data-row-handle') for h in handles().all()]==['t2','t0','t1'])
 check('Actual sorting never changes dates, values or closed-month flags',sorted(before['transactions'],key=lambda r:r['id'])==sorted(get()['transactions'],key=lambda r:r['id']) and get()['closedMonths']==before['closedMonths'])
 check('Other months stay in place',ids('transactions')[0]=='outside')
 check('Actual month manual order survives schema',get()['actualManualMonths']==['2026-09'])
 page.set_content(html(),wait_until='load');tab('actual');check('Actual manual order survives app reload',[h.get_attribute('data-row-handle') for h in handles().all()]==['t2','t0','t1'])
 page.locator('[data-action="date-order"]').click();check('Date-sort reset is explicit and works',[h.get_attribute('data-row-handle') for h in handles().all()]==['t1','t2','t0'] and get()['actualManualMonths']==[])
 # Contextual + in Budget and Actuals.
 page.locator('#quickAddBtn').click();check('Floating plus opens compact nonmodal menu',page.locator('#quickAddMenu').is_visible() and not page.locator('#dialog').is_visible() and page.locator('#quickAddMenu').bounding_box()['width']<320)
 check('Plus on Actuals selects actual context','πραγματική' in page.locator('#quickAddTitle').inner_text())
 page.locator('[data-add-type="income"]').click();check('Quick income opens Actuals with income selected',page.locator('[data-entry-type="income"]').get_attribute('aria-pressed')=='true' and page.locator('#entryDate').count()==1)
 check('Amount is visible before suggestions',page.locator('#entryAmount').bounding_box()['y']<page.locator('#entrySuggestions').bounding_box()['y'])
 check('Type choice is above suggestions',page.locator('.entry-type-first').bounding_box()['y']<page.locator('#entrySuggestions').bounding_box()['y'])
 check('Income shows income suggestions, not utility expenses',page.locator('[data-entry-preset="salary"]').count()>0 and page.locator('[data-entry-preset="electricity"]').count()==0)
 check('No amount is prefilled by quick add',page.locator('#entryAmount').input_value()=='')
 page.locator('#entryAmount').fill('141,25');page.locator('#entryDate').fill('2026-09-18');page.locator('[data-entry-preset="salary"]').first.click()
 page.locator('[data-entry-type="expense"]').click();check('Changing to expense shows matching suggestions',page.locator('[data-entry-preset="electricity"]').count()>0 and page.locator('[data-entry-preset="salary"]').count()==0)
 check('Changing type preserves amount and date',page.locator('#entryAmount').input_value()=='141,25' and page.locator('#entryDate').input_value()=='2026-09-18')
 check('Type change clears unrelated suggested category',page.locator('#entryCategory').input_value()=='housing')
 page.locator('[data-entry-type="income"]').click();check('Switching back restores the draft description',page.locator('#entryLabel').input_value() in ['Μισθός','Salary'])
 page.locator('#saveEntry').click();check('Quick income saves one real income, not an expense',get()['transactions'][-1]['type']=='income' and get()['transactions'][-1]['amount']==141.25)
 tab('plan');page.locator('#quickAddBtn').click();check('Quick-add uses Budget automatically without a second context choice',page.locator('#quickAddMenu').is_visible() and 'πλάνο' in page.locator('#quickAddTitle').inner_text() and page.locator('[data-add-context]').count()==0)
 page.keyboard.press('Escape');check('Quick-add menu closes with Escape and restores focus',not page.locator('#quickAddMenu').is_visible() and page.evaluate('document.activeElement.id')=='quickAddBtn')
 page.locator('#quickAddBtn').click();page.locator('#coffeeBtn').click();check('Support and add menu never overlap',not page.locator('#quickAddMenu').is_visible() and page.locator('#supportCard').is_visible());page.keyboard.press('Escape')
 # Existing preset flow and custom categories unchanged.
 demo();page.locator('#quickAddBtn').click();page.locator('[data-add-type="expense"]').click();page.locator('#entryLabel').fill('Own custom item');page.locator('#entryCategory').select_option('pets');page.locator('#entryAmount').fill('12,34');page.locator('#saveEntry').click()
 check('Custom descriptions remain free within defined categories',get()['lines'][-1]['label']=='Own custom item' and get()['lines'][-1]['category']=='pets')
 entry=get()['lines'][-1]['id'];page.locator(f'[data-amount="{entry}"]').fill('25,45');page.locator(f'[data-amount="{entry}"]').dispatch_event('change')
 check('Inline list amounts accept decimal comma too',get()['lines'][-1]['amount']==25.45)
 # Shared token preserves the current custom order.
 token=page.evaluate('_qa.encodeShare(_qa.get())');decoded=page.evaluate('t=>_qa.decodeShare(t)',token)
 check('Shared editable snapshot retains list order',[l['id'] for l in decoded['lines']]==ids())
 check('JSON roundtrip retains all financial records',page.evaluate('JSON.stringify(BudgetEngine.validate(_qa.get()))===JSON.stringify(_qa.get())'))
 check('Other applications storage is unchanged',page.evaluate("localStorage.getItem('another-app:key')")=='keep')
 # Verify desktop / mobile geometry without altering the site content.
 for width in [320,390,768,1440]:
  close();page.set_viewport_size({'width':width,'height':900});tab('plan')
  check(f'No page overflow at {width}px',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
  plus=page.locator('#quickAddBtn').bounding_box();coffee=page.locator('#coffeeBtn').bounding_box()
  check(f'Floating plus and coffee do not overlap at {width}px',plus['x']+plus['width']+5<=coffee['x'])
  page.locator('#quickAddBtn').click();box=page.locator('#quickAddMenu').bounding_box()
  check(f'Add menu remains within screen at {width}px',box['x']>=0 and box['x']+box['width']<=width+1 and box['y']>=0)
  page.locator('[data-add-type="income"]').click()
  check(f'Type-first form fits at {width}px',page.locator('.entry-type-first').is_visible() and page.evaluate('document.querySelector("#dialog").scrollWidth<=document.querySelector("#dialog").clientWidth+1'))
  close()
 # Mouse autoscroll of a long table.
 page.set_viewport_size({'width':1440,'height':1000})
 page.evaluate("""()=>{const p=BudgetEngine.blank('2026-09');p.lines=Array.from({length:50},(_,i)=>({id:'r'+i,type:'expense',label:'Entry '+i,category:'food',amount:1,frequency:'monthly',essential:false,subscription:false,active:true,funding:'cash',member:'',month:''}));_qa.set(p)}""");tab('plan');table_top()
 a=grip('r0').bounding_box();wrap=page.locator('#budgetTable').locator('..').bounding_box();x=a['x']+20;y=min(930,wrap['y']+wrap['height']-15)
 page.mouse.move(x,a['y']+20);page.mouse.down();page.mouse.move(x,y,steps=14);page.wait_for_timeout(950)
 check('Dragging near table edge auto-scrolls long lists',page.locator('#budgetTable').evaluate('t=>t.parentElement.scrollTop')>0)
 page.mouse.up();page.wait_for_timeout(430)
 check('Auto-scroll can move a row beyond the initial viewport',ids().index('r0')>7)
 check('No runtime exceptions in desktop interactions',errors==[])
 # Capture final visuals from synthetic data, never the user workbook.
 demo();page.locator('#budgetTable').evaluate('t=>t.parentElement.scrollIntoView({block:"center",behavior:"instant"})');page.screenshot(path=str(OUT/'Homeflow_v1.2_Plan_Desktop.png'))
 page.locator('#quickAddBtn').click();page.screenshot(path=str(OUT/'Homeflow_v1.2_AddMenu_Desktop.png'));page.keyboard.press('Escape')
 page.set_viewport_size({'width':390,'height':844});tab('plan');page.locator('#quickAddBtn').click();page.locator('[data-add-type="income"]').click();page.screenshot(path=str(OUT/'Homeflow_v1.2_Income_Mobile.png'));close()
 page.locator('#quickAddBtn').click();page.locator('[data-add-type="expense"]').click();page.screenshot(path=str(OUT/'Homeflow_v1.2_Expense_Mobile.png'));close()
 page.locator('#themeBtn').click();page.locator('#quickAddBtn').click();page.screenshot(path=str(OUT/'Homeflow_v1.2_AddMenu_Dark_Mobile.png'));page.keyboard.press('Escape')
 page.locator('#langBtn').click();page.locator('#quickAddBtn').click();page.locator('[data-add-type="income"]').click()
 check('English type-first controls are translated',page.locator('[data-entry-type="income"]').inner_text().strip().endswith('Income') and page.locator('#entryContext').inner_text()=='Budget plan · Income');close()
 # Emulated touch uses real Chromium Input.dispatchTouchEvent -> PointerEvents.
 touch=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='el-GR');terr=[];touch.on('pageerror',lambda e:terr.append(str(e)))
 touch.evaluate("""()=>{const d={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>d[k]??null,setItem:(k,v)=>d[k]=String(v),removeItem:k=>delete d[k]}})}""")
 touch.set_content(html(),wait_until='load');touch.evaluate("_qa.set(BudgetEngine.demo('2026-09'))");touch.locator('[data-tab="plan"]').click()
 touch.locator('#budgetTable').evaluate('t=>{t.parentElement.scrollTop=0;t.parentElement.scrollIntoView({block:"start",behavior:"instant"})}')
 aa=touch.locator('.row-handle').nth(0).bounding_box();bb=touch.locator('.row-handle').nth(3).bounding_box();cdp=touch.context.new_cdp_session(touch)
 x=aa['x']+aa['width']/2;sy=aa['y']+aa['height']/2;ey=bb['y']+bb['height']*.8
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':sy}]})
 for k in range(1,12):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':sy+(ey-sy)*k/11}]});touch.wait_for_timeout(12)
 cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});touch.wait_for_timeout(420)
 check('Emulated touchscreen drag moves row correctly',touch.evaluate('_qa.get().lines.map(r=>r.id).slice(0,4)')==['demo1','demo2','demo3','demo0'])
 check('Touch dragging uses only the grip, not normal row scrolling',touch.locator('.row-handle').first.evaluate('el=>getComputedStyle(el).touchAction')=='none' and touch.locator('#budgetTable tbody tr').first.evaluate('el=>getComputedStyle(el).touchAction')=='auto')
 touch.locator('.row-handle').first.tap();check('Touch tap opens alternative position picker',touch.locator('#moveRowForm').is_visible());touch.locator('#closeDialog').tap()
 touch.locator('#budgetTable').evaluate('t=>{t.parentElement.scrollTop=0;t.parentElement.scrollIntoView({block:"start",behavior:"instant"})}')
 before_touch=touch.evaluate('_qa.get()');aa=touch.locator('.row-handle').nth(0).bounding_box();bb=touch.locator('.row-handle').nth(2).bounding_box()
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':aa['x']+22,'y':aa['y']+22}]})
 cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':bb['x']+22,'y':bb['y']+22}]})
 cdp.send('Input.dispatchTouchEvent',{'type':'touchCancel','touchPoints':[]});touch.wait_for_timeout(100)
 check('Interrupted touch drag leaves records unchanged',touch.evaluate('_qa.get()')==before_touch and touch.locator('.row-drag-ghost').count()==0)
 check('Emulated touch has no uncaught errors',terr==[])
 browser.close()
(OUT/'interactions-results.txt').write_text('\n'.join('PASS '+s for s in checks)+f'\n{len(checks)} passed\n')
print(f'\n{len(checks)} interaction checks passed.')
