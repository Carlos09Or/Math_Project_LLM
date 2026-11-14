/* Página de la rúbrica: se dibuja desde window.PROJECT_RUBRIC (dataset/rubric/rubric_v0.1.json). Texto siempre con textContent. */
(function () {
  'use strict';
  var R = window.PROJECT_RUBRIC;
  if (!R || !document.getElementById('rb-criteria')) return;

  function el(tag, props, children) {
    var n = document.createElement(tag);
    if (props) Object.keys(props).forEach(function (k) {
      if (k === 'class') n.className = props[k]; else if (k === 'text') n.textContent = props[k]; else n.setAttribute(k, props[k]);
    });
    (children || []).forEach(function (c) { n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }
  function $(id) { return document.getElementById(id); }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); }
  function badge(text, kind) { return el('span', { class: 'badge b-' + kind, text: text }); }

  var TASK = { solve: 'Resolver', diagnose: 'Diagnosticar', hint: 'Pista', todas: 'Todas las tareas' };
  var APPLIES = { todos: 'todos los ítems', con_error: 'ítems con error', control: 'controles (el estudiante acierta)' };
  var LVKIND = { 0: 'bad', 1: 'warn', 2: 'ok' };
  var LVNAME = { 0: 'Nivel 0', 1: 'Nivel 1', 2: 'Nivel 2' };

  // Tarjetas de cifras
  var real = R.anchors.filter(function (a) { return a.provenance === 'real'; }).length;
  [[R.criteria.length, 'criterios'], [R.anchors.length, 'ejemplos ancla'], [real + ' / ' + (R.anchors.length - real), 'reales / sintéticos'], ['0–2', 'escala, más es mejor']].forEach(function (k) {
    $('rb-kpis').appendChild(el('div', { class: 'card' }, [el('div', { class: 'stat', text: String(k[0]) }), el('div', { class: 'stat-label', text: k[1] })]));
  });

  // Qué criterios se puntúan en cada tipo de respuesta (derivado de los datos)
  function forGroup(task, sub) {
    return R.criteria.filter(function (c) {
      if (c.task !== 'todas' && c.task !== task) return false;
      if (task === 'diagnose' && sub === 'con_error' && c.applies_to === 'control') return false;
      if (task === 'diagnose' && sub === 'control' && c.applies_to === 'con_error') return false;
      return true;
    }).map(function (c) { return c.id; });
  }
  var tb = $('rb-tasks').appendChild(el('tbody'));
  [['Resolver', 'solve', ''], ['Diagnosticar · el estudiante se equivocó', 'diagnose', 'con_error'], ['Diagnosticar · control (el estudiante acierta)', 'diagnose', 'control'], ['Pista', 'hint', '']].forEach(function (g) {
    var ids = forGroup(g[1], g[2]);
    tb.appendChild(el('tr', null, [el('td', { text: g[0] }), el('td', null, ids.map(function (i) { return el('code', { text: i + ' ' }); })), el('td', { text: String(ids.length) })]));
  });

  // Criterios con descriptores y anclas
  var F = '';
  var sel = $('rb-filter');
  [['', 'Todos los criterios'], ['solve', 'Resolver'], ['diagnose', 'Diagnosticar'], ['hint', 'Pista']].forEach(function (o) { sel.appendChild(el('option', { value: o[0], text: o[1] })); });
  sel.addEventListener('change', function () { F = sel.value; render(); });

  function render() {
    var box = $('rb-criteria'); clear(box);
    R.criteria.filter(function (c) { return !F || c.task === F || c.task === 'todas'; }).forEach(function (c) {
      var head = el('div', { class: 't-head' }, [el('span', { class: 't-id', text: c.id }), badge(TASK[c.task], 'info'), badge(APPLIES[c.applies_to], 'pend')]);
      var levels = el('div', { class: 'levels' });
      ['2', '1', '0'].forEach(function (lv) {
        levels.appendChild(el('div', { class: 'lv lv' + lv }, [el('strong', { text: LVNAME[lv] }), el('p', { text: c.levels[lv] })]));
      });
      var card = el('article', { class: 'test info', id: 'crit-' + c.id }, [head, el('h3', { text: c.name }), el('p', { class: 'q', text: c.question }), levels]);
      if (c.automated) card.appendChild(el('p', { class: 'count', text: 'Lo automático: ' + c.automated }));
      if (c.notes) card.appendChild(el('p', { class: 'count', text: 'Nota: ' + c.notes }));
      var anchors = R.anchors.filter(function (a) { return a.criterion === c.id; }).sort(function (a, b) { return b.level - a.level; });
      var det = el('details', null, [el('summary', { text: 'Ver los ' + anchors.length + ' ejemplos ancla' })]);
      anchors.forEach(function (a) {
        var meta = el('div', { class: 'meta' }, [el('code', { text: a.id }), badge('nivel ' + a.level, LVKIND[a.level]), a.provenance === 'real' ? badge('respuesta real del modelo (dev)', 'info') : badge('sintético, escrito a mano', 'warn')]);
        var dl = el('dl');
        dl.appendChild(el('dt', { text: 'Problema' })); dl.appendChild(el('dd', { text: a.problem }));
        if (a.student_answer) { dl.appendChild(el('dt', { text: 'Estudiante' })); dl.appendChild(el('dd', { text: a.student_answer })); }
        if (a.gold_error_observable) { dl.appendChild(el('dt', { text: 'Error observable' })); dl.appendChild(el('dd', { text: a.gold_error_observable })); }
        det.appendChild(el('div', { class: 'item' }, [meta, dl, el('pre', { class: 'resp', text: a.response }), el('p', { class: 'count', text: 'Por qué: ' + a.rationale })]));
      });
      card.appendChild(det);
      box.appendChild(card);
    });
  }
  render();
})();
