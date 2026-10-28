'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const E = require('../engine.js');

// Run the app's real shortcut handlers with controlled UI/storage boundaries.
const source = fs.readFileSync(path.join(__dirname, '../app.js'), 'utf8');
const start = source.indexOf('function commit(next)');
const end = source.indexOf('function updateHeader()', start);
const currentMonth = source.match(/^function goToCurrentMonth\(\).*$/m)?.[0];
assert.ok(start >= 0 && end > start && currentMonth, 'Shortcut handlers must exist');
const handlers = source.slice(start, end) + '\n' + currentMonth;
const copy = value => JSON.parse(JSON.stringify(value));
let count = 0;
function check(name, fn) { fn(); count++; console.log('PASS ' + name); }
function line(id, extra = {}) {
  return {id, type:'expense', label:'Entry ' + id, note:'Reference', category:'housing',
    member:'member1', amount:360, funding:'cash', frequency:'monthly', month:'',
    essential:true, subscription:false, active:true, ...extra};
}
function budget() {
  const p = E.blank('2026-09');
  p.lines = ['a','b','c'].map(id => line(id));
  p.transactions = [
    {...line('x'), date:'2026-08-15'},
    {...line('y'), date:'2026-09-20'},
    {...line('z'), date:'2026-09-22'}
  ];
  p.closedMonths = ['2026-07','2026-08','2026-09'];
  return E.validate(p);
}
function app(initial = budget()) {
  const elements = new Map(), calls = {save:0, render:0, dialogs:[], toasts:[], focused:null};
  const element = id => {
    if (!elements.has(id)) elements.set(id, {hidden:true, textContent:'', attributes:{},
      setAttribute(name, value) { this.attributes[name] = value; },
      focus() { calls.focused = id; }});
    return elements.get(id);
  };
  const context = vm.createContext({
    E:{...E, monthNow:() => '2026-10'}, state:E.validate(initial), lastDeleted:null,
    tab:'plan', visibleRecords:true, t:(_el,en) => en, $:element,
    save:() => { calls.save++; },
    render:() => { calls.render++; context.updateUndoNotice(); },
    toast:message => calls.toasts.push(message),
    lineDialog:(...args) => calls.dialogs.push(copy(args)),
    $$:selector => {
      if (selector === '[data-tab]') return ['plan','actual','overview'].map(tab => ({
        dataset:{tab}, focus() { calls.focused = 'tab:' + tab; }}));
      if (!context.visibleRecords) return [];
      const key = selector === '[data-edit]' ? 'lines' : 'transactions';
      return context.state[key].map(record => ({getAttribute:() => record.id,
        focus() { calls.focused = key + ':' + record.id; }}));
    }
  });
  vm.runInContext(handlers, context);
  return {context, calls, element, snapshot:() => copy(context.state)};
}

for (const frequency of E.FREQ) {
  check('Actual draft uses the per-period amount for ' + frequency, () => {
    const p = budget();
    p.lines[0] = line('a', {frequency, type:frequency === 'salary14' ? 'income' : 'expense',
      month:frequency === 'once' ? '2026-12' : '', active:false});
    const h = app(p), before = h.snapshot();
    h.context.recordActualFromPlan('a');
    const [actual, existing, seed, sourceFrequency] = h.calls.dialogs[0];
    assert.equal(actual, true);
    assert.equal(existing, null);
    assert.equal(sourceFrequency, frequency);
    assert.equal(seed.amount, 360);
    assert.deepEqual(seed, {type:p.lines[0].type, label:'Entry a', note:'Reference',
      category:'housing', member:'member1', funding:'cash', amount:360});
    assert.equal(Object.hasOwn(seed, 'id'), false, 'The form must generate a fresh ID');
    assert.equal(Object.hasOwn(seed, 'date'), false, 'The form must choose its normal local date');
    assert.deepEqual(h.snapshot(), before, 'Opening a draft cannot record a payment');
    assert.equal(h.calls.save, 0);
  });
}
check('Actual draft preserves every financial type and its funding', () => {
  for (const type of E.TYPES) {
    const p = budget(), funding = type === 'income' ? 'mixed' : type === 'expense' ? 'benefit' : 'cash';
    p.lines[0] = line('a', {type, funding, note:'Keep me', category:'Custom category'});
    const h = app(p);
    h.context.recordActualFromPlan('a');
    const seed = h.calls.dialogs[0][2];
    assert.equal(seed.type, type);
    assert.equal(seed.funding, funding);
    assert.equal(seed.note, 'Keep me');
    assert.equal(seed.category, 'Custom category');
  }
});
check('Unknown plan source is a no-op', () => {
  const h = app(), before = h.snapshot();
  h.context.recordActualFromPlan('unknown');
  assert.equal(h.calls.dialogs.length, 0);
  assert.deepEqual(h.snapshot(), before);
});

for (const id of ['a','b','c']) {
  check('Undo restores exact plan data and position for ' + id, () => {
    const h = app(), before = h.snapshot();
    h.context.deleteEntry(false, id);
    assert.equal(h.context.state.lines.length, 2);
    assert.equal(h.context.state.lines.some(row => row.id === id), false);
    assert.equal(h.element('undoNotice').hidden, false);
    assert.equal(h.element('undoMessage').textContent, 'Deleted: Entry ' + id);
    assert.deepEqual(copy(h.context.state.closedMonths), before.closedMonths);
    h.context.undoLastDelete();
    assert.deepEqual(h.snapshot(), before);
    assert.equal(h.context.lastDeleted, null);
    assert.equal(h.element('undoNotice').hidden, true);
    assert.equal(h.calls.focused, 'lines:' + id);
  });
}
check('Actual undo restores only its completion flag and original position', () => {
  const h = app(), before = h.snapshot();
  h.context.deleteEntry(true, 'y');
  assert.deepEqual(copy(h.context.state.closedMonths), ['2026-07','2026-08']);
  assert.deepEqual(copy(h.context.state.transactions.map(row => row.id)), ['x','z']);
  h.context.state.month = '2026-12'; // Navigation does not edit the records.
  h.context.undoLastDelete();
  assert.deepEqual(copy(h.context.state.transactions), before.transactions);
  assert.deepEqual(new Set(h.context.state.closedMonths), new Set(before.closedMonths));
  assert.equal(h.context.state.month, '2026-12');
  assert.deepEqual(copy(h.context.state.lines), before.lines);
});
check('Undo does not mark an originally incomplete month complete', () => {
  const p = budget(); p.closedMonths = ['2026-07','2026-08'];
  const h = app(p);
  h.context.deleteEntry(true, 'y');
  h.context.undoLastDelete();
  assert.deepEqual(copy(h.context.state.closedMonths), p.closedMonths);
});
check('Only the most recent deletion is restored and only once', () => {
  const h = app();
  h.context.deleteEntry(false, 'a');
  h.context.deleteEntry(false, 'b');
  h.context.undoLastDelete();
  assert.deepEqual(copy(h.context.state.lines.map(row => row.id)), ['b','c']);
  const before = h.snapshot(), saves = h.calls.save;
  h.context.undoLastDelete();
  assert.deepEqual(h.snapshot(), before);
  assert.equal(h.calls.save, saves);
});
check('Unknown deletion keeps the pending undo', () => {
  const h = app(); h.context.deleteEntry(false, 'b');
  const pending = copy(h.context.lastDeleted), before = h.snapshot();
  h.context.deleteEntry(true, 'unknown');
  assert.deepEqual(copy(h.context.lastDeleted), pending);
  assert.deepEqual(h.snapshot(), before);
});
check('The next valid data commit clears undo', () => {
  const h = app(); h.context.deleteEntry(false, 'b');
  const next = h.snapshot(); next.lines[0].amount = 425;
  h.context.commit(next);
  assert.equal(h.context.lastDeleted, null);
  assert.equal(h.element('undoNotice').hidden, true);
  h.context.undoLastDelete();
  assert.equal(h.context.state.lines.length, 2);
  assert.equal(h.context.state.lines[0].amount, 425);
});
check('An invalid attempted data commit preserves undo and data', () => {
  const h = app(); h.context.deleteEntry(false, 'b');
  const before = h.snapshot(), pending = copy(h.context.lastDeleted), next = h.snapshot();
  next.lines[0].amount = -1;
  assert.throws(() => h.context.commit(next));
  assert.deepEqual(h.snapshot(), before);
  assert.deepEqual(copy(h.context.lastDeleted), pending);
  h.context.undoLastDelete();
  assert.equal(h.context.state.lines[1].id, 'b');
});
check('Undo moves focus to the current tab when the restored row is hidden', () => {
  const h = app(); h.context.deleteEntry(false, 'b');
  h.context.visibleRecords = false; h.context.tab = 'actual';
  h.context.undoLastDelete();
  assert.equal(h.calls.focused, 'tab:actual');
});
check('Current month navigation preserves records, completion, and pending undo', () => {
  const h = app(); h.context.deleteEntry(true, 'y');
  const before = h.snapshot(), pending = copy(h.context.lastDeleted);
  h.context.goToCurrentMonth();
  const expected = {...before, month:'2026-10'};
  assert.deepEqual(h.snapshot(), expected);
  assert.deepEqual(copy(h.context.lastDeleted), pending);
  assert.equal(h.element('undoNotice').hidden, false);
  h.context.undoLastDelete();
  assert.equal(h.context.state.month, '2026-10');
  assert.equal(h.context.state.transactions.length, 3);
});
check('Current month navigation is a no-op when already selected', () => {
  const p = budget(); p.month = '2026-10';
  const h = app(p), before = h.snapshot();
  h.context.goToCurrentMonth();
  assert.deepEqual(h.snapshot(), before);
  assert.equal(h.calls.save, 0);
  assert.equal(h.calls.render, 0);
});
console.log(`\n${count} shortcut regression checks passed.`);
