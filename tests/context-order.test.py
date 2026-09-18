"""Homeflow 1.2: scoped add control, type-first form, mouse/touch/keyboard ordering.
Chromium with actual pointer events and inline app; in-memory storage for repeatability.
Does not assert native phone/PWA installation or production deployment.
"""
from pathlib import Path
import importlib.util,json
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1];OUT=BASE.parent/'qa_output';OUT.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('offline_builder',BASE/'tools/build_offline.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
HTML=m.build().replace('render();checkShared();','window._qa={getState:()=>JSON.parse(JSON.stringify(state)),setState:p=>commit(p),encodeShare,decodeShare};render();checkShared();')
checks=[]
def check(name,ok):
 assert ok,name
 checks.append(name);print('PASS '+name,flush=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000},locale='el-GR',reduced_motion='reduce');page.set_default_timeout(4000)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.evaluate("""()=>{const d={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>d[k]??null,setItem:(k,v)=>d[k]=String(v),removeItem:k=>delete d[k]}});} """)
 page.set_content(HTML,wait_until='load')
 get=lambda:page.evaluate('_qa.getState()')
 def tab(n):page.locator(f'[data-tab="{n}"]').click()
 def close():
  if page.locator('#dialog').is_visible():page.locator('#closeDialog').click()
 def ids(kind='lines'):return [r['id'] for r in get()[kind]]
 def demo():page.evaluate("_qa.setState(BudgetEngine.demo('2026-09'))");tab('plan')
 for name in ['overview','future','guide']:
  tab(name);check(name+': no registration control or floating add widget',page.locator('#entryAddBtn').count()==0 and page.locator('#addFab').count()==0)
 for name in ['plan','actual']:
  tab(name);check(name+': exactly one main add control',page.locator('#entryAddBtn').count()==1 and page.locator('[data-action="add-'+name+'"]').count()==1)
  page.locator('#entryAddBtn').click()
  check(name+': first form field is income/expense type',page.locator('#entryForm input,#entryForm select').first.get_attribute('id')=='entryType')
  check(name+': type and amount precede suggestions',page.locator('#entryType').bounding_box()['y']<page.locator('#entrySuggestions').bounding_box()['y'])
  page.locator('#entryType').select_option('income')
  check(name+': income selection offers salary, not groceries',page.locator('#entryQuickChips [data-entry-preset="salary"]').count()==1 and page.locator('#entryQuickChips [data-entry-preset="groceries"]').count()==0 and page.locator('#entryCategory').input_value()=='income')
  page.locator('#entryAmount').fill('456,78');page.locator('#entryLabel').fill('A custom description')
  page.locator('#entryType').select_option('expense')
  check(name+': type change preserves entered amount and description',page.locator('#entryAmount').input_value()=='456,78' and page.locator('#entryLabel').input_value()=='A custom description')
  check(name+': form context is correct',page.locator('#entryDate').count()==(name=='actual') and page.locator('#entryFrequency').count()==(name=='plan'))
  close()
 demo();orig=get();before=ids();h=page.locator('[data-grip]').first;h.focus();page.keyboard.press('End')
 check('Keyboard End moves row to last position',ids()==before[1:]+before[:1])
 page.keyboard.press('Home');check('Keyboard Home restores first position',ids()==before)
 page.keyboard.press('ArrowDown');check('Keyboard arrow moves by one',ids()==[before[1],before[0]]+before[2:])
 check('Reordering preserves all records and amounts',sorted(get()['lines'],key=lambda x:x['id'])==sorted(orig['lines'],key=lambda x:x['id']))
 check('Reordering persists the v1 array order',json.loads(page.evaluate("localStorage.getItem('homeflow:budget:v1')"))['lines']==get()['lines'])
 page.locator('[data-grip]').first.click();page.locator('#rowPosition').fill('5');page.locator('#positionForm button[type="submit"]').click()
 check('Tap handle and choose numeric position works',ids()[4]==before[1])
 # One hidden-slot example through a real category filter.
 demo();unfiltered=ids();page.locator('#categoryFilter').select_option('housing');visible=page.locator('[data-grip]').evaluate_all('(els)=>els.map(e=>e.dataset.grip)')
 page.locator('[data-grip]').first.focus();page.keyboard.press('End');new=ids();positions=[unfiltered.index(x) for x in visible]
 check('Filter reorder changes only visible positions',all(new[i]==unfiltered[i] for i in range(len(new)) if i not in positions) and [new[i] for i in positions]==visible[1:]+visible[:1])
 # Real mouse capture path.
 demo();before=ids();wrap=page.locator('.reorder-wrap');wrap.evaluate('(e)=>e.scrollTop=0');page.locator('.reorder-wrap').evaluate('(e)=>window.scrollTo({top:window.scrollY+e.getBoundingClientRect().top-180,behavior:"instant"})');page.wait_for_timeout(80)
 def mouse_move_first_to_third():
  h=page.locator('[data-grip]').first.bounding_box();dest=page.locator('tr[data-row-id]').nth(2).bounding_box();x=h['x']+h['width']/2;y=h['y']+h['height']/2
  page.mouse.move(x,y);page.mouse.down();page.mouse.move(x,dest['y']+dest['height']*.75,steps=8);page.mouse.up();page.wait_for_timeout(80)
 mouse_move_first_to_third();check('Mouse drag places first row after third',ids()==before[1:3]+before[:1]+before[3:])
 # Escape cancels an active drag.
 h=page.locator('[data-grip]').first.bounding_box();dest=page.locator('tr[data-row-id]').nth(2).bounding_box();before=ids()
 page.mouse.move(h['x']+15,h['y']+20);page.mouse.down();page.mouse.move(h['x']+15,dest['y']+25,steps=5);page.keyboard.press('Escape');page.mouse.up()
 check('Escape cancels drag without any mutation',ids()==before and page.locator('.row-drag-ghost').count()==0)
 # Order survives a complete UI reload with the same storage adapter.
 snapshot=get();page.set_content(HTML,wait_until='load');check('Order and data survive UI reload',get()==snapshot)
 # Actuals: reorder only the selected month, leave all dates/closed flags intact.
 page.evaluate("""()=>{const p=BudgetEngine.blank('2026-09');p.transactions=[['t1','2026-09-01'],['t2','2026-08-01'],['t3','2026-09-02'],['t4','2026-09-03']].map(([id,date],i)=>({id,date,type:'expense',label:'Receipt '+i,category:'food',member:'',amount:i+1,funding:'cash'}));p.closedMonths=['2026-09'];_qa.setState(p)}""")
 tab('actual');before=get();page.locator('[data-grip]').first.focus();page.keyboard.press('End')
 check('Actual ordering does not move other months',ids('transactions')==['t3','t2','t4','t1'])
 check('Actual dates, amounts and completion flags remain unchanged',sorted(get()['transactions'],key=lambda x:x['id'])==sorted(before['transactions'],key=lambda x:x['id']) and get()['closedMonths']==before['closedMonths'])
 # Touch events via Chromium DevTools: browser PointerEvent path, no mock drag APIs.
 demo();page.set_viewport_size({'width':390,'height':844});page.locator('.reorder-wrap').evaluate('(e)=>{e.scrollTop=0;e.scrollLeft=0}');page.locator('.reorder-wrap').evaluate('(e)=>window.scrollTo({top:window.scrollY+e.getBoundingClientRect().top-180,behavior:"instant"})');page.wait_for_timeout(80);before=ids()
 h=page.locator('[data-grip]').first.bounding_box();dest=page.locator('tr[data-row-id]').nth(2).bounding_box();x=h['x']+h['width']/2;y=h['y']+h['height']/2;end=dest['y']+dest['height']*.8
 cdp=page.context.new_cdp_session(page)
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
 for i in range(1,9):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':y+(end-y)*i/8}]})
 cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});page.wait_for_timeout(80)
 check('Touch drag reorders using the handle',ids()==before[1:3]+before[:1]+before[3:])
 check('Handle does not replace ordinary table swiping',page.locator('[data-grip]').first.evaluate('(e)=>getComputedStyle(e).touchAction')=='none' and page.locator('.reorder-wrap').evaluate('(e)=>getComputedStyle(e).touchAction')!='none')
 # Confirm the one contextual button remains available while its card scrolls.
 check('List toolbar is sticky, not a global overlay',page.locator('.entry-toolbar').evaluate('(e)=>getComputedStyle(e).position')=='sticky' and page.locator('#entryAddBtn').bounding_box()['y']>=0)
 for w in [320,390,768,1440]:
  page.set_viewport_size({'width':w,'height':900});tab('plan')
  check(f'Plan fits {w}px and add button is usable',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1') and page.locator('#entryAddBtn').bounding_box()['height']>=44)
  page.locator('#entryAddBtn').click()
  check(f'Type-first form fits {w}px',page.locator('#dialog').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1') and page.locator('#entryType').bounding_box()['y']>=0)
  close()
 demo();page.set_viewport_size({'width':1440,'height':1000});page.locator('#entryAddBtn').scroll_into_view_if_needed();page.locator('#toast').evaluate('(e)=>e.hidden=true');page.screenshot(path=str(OUT/'Homeflow_v1.2_Plan_Desktop.png'),full_page=False)
 page.set_viewport_size({'width':390,'height':844});tab('plan');page.locator('#entryAddBtn').click();page.locator('#entryType').select_option('income');page.locator('#dialog').evaluate('(e)=>e.scrollTop=0');page.screenshot(path=str(OUT/'Homeflow_v1.2_Income_Mobile.png'));close()
 page.locator('#themeBtn').click();page.locator('#entryAddBtn').scroll_into_view_if_needed();page.screenshot(path=str(OUT/'Homeflow_v1.2_Plan_Dark_Mobile.png'))
 check('No uncaught script errors',errors==[])
 browser.close()
print(f'\n{len(checks)} scoped-entry and ordering UI checks passed.',flush=True)
(OUT/'context-order-results.txt').write_text('\n'.join('PASS '+s for s in checks)+f'\n{len(checks)} passed\n')
