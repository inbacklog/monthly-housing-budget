'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const E = require('../engine.js');

// Execute the real startup code, before any rendering, with a controlled store.
const source = fs.readFileSync(path.join(__dirname, '../app.js'), 'utf8');
const boundary = source.indexOf('const t=');
assert.ok(boundary > 0, 'Startup boundary must exist');
const startup = source.slice(0, boundary) + '\nreturn {state,lang,theme,rowColors,storageOK};})()';
const KEY = 'homeflow:budget:v1', PREF = 'homeflow:prefs:v1';
const budget = E.demo('2026-10');
budget.closedMonths = ['2026-09'];
let count = 0;
function check(name, fn) { fn(); count++; console.log('PASS ' + name); }
function load(prefs, saved = JSON.stringify(budget), failedKey = null) {
  const store = {[PREF]: prefs, [KEY]: saved};
  const result = vm.runInNewContext(startup, {
    window: {BudgetEngine: E}, document: {},
    localStorage: {getItem(key) { if (key === failedKey) throw Error('Storage unavailable'); return store[key] ?? null; }}
  });
  return JSON.parse(JSON.stringify(result));
}

for (const prefs of ['{broken', 'null', '[]', 'false', '17']) {
  check('Invalid preference value preserves the saved budget: ' + prefs, () => {
    const result = load(prefs);
    assert.deepEqual(result.state, E.validate(budget));
    assert.equal(result.storageOK, true);
    assert.equal(result.lang, 'el');
    assert.equal(result.theme, 'light');
    assert.equal(result.rowColors, 'soft');
  });
}
check('Preference read failure does not prevent budget restore', () => {
  assert.deepEqual(load(null, JSON.stringify(budget), PREF).state, E.validate(budget));
});
check('Valid preferences and budget are both restored', () => {
  const result = load(JSON.stringify({lang:'en',theme:'dark',rowColors:'off'}));
  assert.deepEqual(result.state, E.validate(budget));
  assert.equal(result.lang, 'en');
  assert.equal(result.theme, 'dark');
  assert.equal(result.rowColors, 'off');
});
check('Malformed budget still reports a storage problem', () => {
  const result = load('{broken', '{bad budget');
  assert.equal(result.storageOK, false);
  assert.deepEqual(result.state.lines, []);
});
check('Unavailable budget storage still reports a storage problem', () => {
  assert.equal(load(null, null, KEY).storageOK, false);
});
check('A first visit starts with an empty budget', () => {
  const result = load(null, null);
  assert.equal(result.storageOK, true);
  assert.deepEqual(result.state.lines, []);
});
console.log(`\n${count} startup regression checks passed.`);
