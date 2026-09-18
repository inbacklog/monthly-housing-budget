/* Homeflow scenario workspace. Independent documents, max 3, explicit common comparison scope.
 * No snapshots are embedded in public code. This module performs no storage/network writes.
 */
(function (root) {
  'use strict';
  const E = root.BudgetEngine, IO = root.HomeIO, D = root.HomeData;
  const MAX = 3;
  function check(ok, message) { if (!ok) throw new Error(message); }
  function clean(w) {
    check(w && w.schema === 'homeflow-workspace' && w.version === 1, 'Invalid scenario workspace.');
    check(Array.isArray(w.scenarios) && w.scenarios.length >= 1 && w.scenarios.length <= MAX, 'Use 1–3 scenarios.');
    const ids = new Set();
    const scenarios = w.scenarios.map(s => {
      check(s && typeof s.id === 'string' && /^[a-zA-Z0-9_-]{1,80}$/.test(s.id) && !ids.has(s.id), 'Invalid scenario ID.');
      ids.add(s.id);
      check(typeof s.name === 'string' && s.name.trim() && s.name.length <= 60, 'Use a scenario name of 1–60 characters.');
      return {id:s.id, name:s.name.trim(), state:IO.clean(s.state)};
    });
    check(ids.has(w.activeId) && ids.has(w.referenceId), 'Invalid active/reference scenario.');
    check(E.validMonth(w.comparison?.month), 'Invalid comparison month.');
    check(Number.isInteger(w.comparison.months) && w.comparison.months >= 1 && w.comparison.months <= 120, 'Use a comparison horizon of 1–120 months.');
    return {schema:'homeflow-workspace',version:1,activeId:w.activeId,referenceId:w.referenceId,
      comparison:{month:w.comparison.month,months:w.comparison.months},scenarios};
  }
  function create(state, name='Scenario 1') {
    const s = IO.clean(state), id = D.uid();
    return clean({schema:'homeflow-workspace',version:1,activeId:id,referenceId:id,
      comparison:{month:s.month,months:s.settings.projectionMonths},scenarios:[{id,name,state:s}]});
  }
  function active(w) { return w.scenarios.find(s=>s.id===w.activeId); }
  function sync(w, state) { const c=clean(w); active(c).state=IO.clean(state); return c; }
  function fork(w, name, includeActual=false) {
    const c=clean(w); check(c.scenarios.length<MAX,'Έως 3 σενάρια / Maximum 3 scenarios.');
    const source=active(c), s=IO.clean(source.state), id=D.uid();
    if(!includeActual){s.actual=[];s.closedMonths=[];}
    c.scenarios.push({id,name,state:s});c.activeId=id;return clean(c);
  }
  function remove(w,id) {
    const c=clean(w);check(c.scenarios.length>1,'Keep at least one scenario.');check(c.scenarios.some(s=>s.id===id),'Unknown scenario.');
    c.scenarios=c.scenarios.filter(s=>s.id!==id);if(c.activeId===id)c.activeId=c.scenarios[0].id;if(c.referenceId===id)c.referenceId=c.scenarios[0].id;return clean(c);
  }
  function strip(w, options={}) {
    const c=clean(w);c.scenarios=c.scenarios.map((s,i)=>({...s,name:options.names===false?s.name:'Scenario '+(i+1),state:IO.strip(s.state,options)}));return clean(c);
  }
  function compare(w) {
    const c=clean(w), {month,months}=c.comparison;
    const results=c.scenarios.map(s=>{
      const doc=IO.clean(s.state);doc.month=month;const p=E.totalPlan(doc), settings=doc.settings;
      const projection=E.project(doc,{months,incomeChange:settings.scenarioIncome,flexChange:settings.scenarioFlexible,extraExpense:settings.scenarioExtra});
      const first=projection.rows[0];
      // Empty or all-paused plans are not labelled as complete financial plans.
      const empty=!doc.plan.some(p=>p.active && p.amount!==null);
      const incomplete=empty||projection.incomplete;
      return {id:s.id,name:s.name,doc,plan:p,projection,first,empty,incomplete,
        average:projection.cumulative/months,capacity:incomplete?null:Math.max(0,first.free),
        delta:null};
    });
    const reference=results.find(s=>s.id===c.referenceId);
    for(const s of results) if(!s.incomplete&&!reference.incomplete)
      s.delta={monthly:s.first.free-reference.first.free,cumulative:s.projection.cumulative-reference.projection.cumulative};
    return {month,months,referenceId:c.referenceId,results};
  }
  root.HomeScenarios=Object.freeze({MAX,clean,create,active,sync,fork,remove,strip,compare});
})(globalThis);
