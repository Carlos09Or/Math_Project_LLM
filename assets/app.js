/* Sitio del proyecto. Todo el texto de los datos se inserta con textContent (nunca como HTML). */
(function () {
  'use strict';

  function el(tag, props, children) {
    var n = document.createElement(tag);
    if (props) Object.keys(props).forEach(function (k) {
      if (k === 'class') n.className = props[k];
      else if (k === 'text') n.textContent = props[k];
      else n.setAttribute(k, props[k]);
    });
    (children || []).forEach(function (c) { n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }
  function badge(text, kind) { return el('span', { class: 'badge b-' + kind, text: text }); }
  function $(id) { return document.getElementById(id); }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); }

  var TASK = { solve: 'resolver', diagnose: 'diagnosticar', hint: 'pista' };
  var COMP = { 'A3-SUB-24': 'Sustracción', 'A3-MUL-24': 'Multiplicación', 'A3-DIV-24': 'División con residuo' };

  // La navegación (sección y página actual) ya viene marcada en el HTML de cada página.

  // ---------- Portada: cifras calculadas desde los datos
  if ($('home-stats') && window.PROJECT_ITEMS && window.PROJECT_RUNS) {
    var items = window.PROJECT_ITEMS.items, runs = window.PROJECT_RUNS.runs;
    var bases = {}; items.forEach(function (i) { bases[i.problem_base_id] = i; });
    var controls = Object.keys(bases).filter(function (b) {
      return items.some(function (i) { return i.problem_base_id === b && i.task === 'diagnose' && i.student_answer_is_correct; });
    }).length;
    var reviewed = items.filter(function (i) { return i.reviewer_status !== 'unreviewed'; }).length;
    var stats = [
      [items.length, 'ítems en el borrador del dataset'],
      [Object.keys(bases).length, 'problemas base originales'],
      [controls, 'controles con respuesta correcta'],
      [reviewed, 'ítems revisados por docentes'],
      [runs.length, 'corridas de la prueba de humo']
    ];
    stats.forEach(function (s) {
      $('home-stats').appendChild(el('div', { class: 'card' }, [el('div', { class: 'stat', text: String(s[0]) }), el('div', { class: 'stat-label', text: s[1] })]));
    });
  }

  // ---------- Explorador del dataset
  if ($('explorer') && window.PROJECT_ITEMS) {
    var all = window.PROJECT_ITEMS.items;
    var f = { comp: '', task: '', split: '', kind: '', q: '' };
    function opt(sel, value, label) { sel.appendChild(el('option', { value: value, text: label })); }
    function select(id, entries, key) {
      var s = $(id); entries.forEach(function (e) { opt(s, e[0], e[1]); });
      s.addEventListener('change', function () { f[key] = s.value; render(); });
    }
    select('f-comp', [['', 'Todas'], ['A3-SUB-24', COMP['A3-SUB-24']], ['A3-MUL-24', COMP['A3-MUL-24']], ['A3-DIV-24', COMP['A3-DIV-24']]], 'comp');
    select('f-task', [['', 'Todas'], ['solve', 'Resolver'], ['diagnose', 'Diagnosticar'], ['hint', 'Pista']], 'task');
    select('f-split', [['', 'Todas'], ['dev', 'dev (ajuste de prompts)'], ['pilot', 'pilot (evaluación)']], 'split');
    select('f-kind', [['', 'Todos'], ['err', 'Respuesta con error'], ['ok', 'Control: respuesta correcta']], 'kind');
    $('f-q').addEventListener('input', function (e) { f.q = e.target.value.toLowerCase(); render(); });

    function render() {
      var list = all.filter(function (i) {
        if (f.comp && i.competency_id !== f.comp) return false;
        if (f.task && i.task !== f.task) return false;
        if (f.split && i.split !== f.split) return false;
        if (f.kind === 'err' && i.student_answer_is_correct !== false) return false;
        if (f.kind === 'ok' && i.student_answer_is_correct !== true) return false;
        if (f.q && (i.problem_text + ' ' + i.item_id).toLowerCase().indexOf(f.q) < 0) return false;
        return true;
      });
      $('f-count').textContent = list.length + ' de ' + all.length + ' ítems';
      var box = $('explorer'); clear(box);
      list.slice(0, 60).forEach(function (i) {
        var meta = el('div', { class: 'meta' }, [
          el('code', { text: i.item_id }), badge(COMP[i.competency_id], 'info'), badge(TASK[i.task], 'pend'),
          badge('dificultad ' + i.difficulty, 'pend'), badge(i.split, 'pend')]);
        if (i.student_answer_is_correct === true) meta.appendChild(badge('control: sin error', 'ok'));
        if (i.student_answer_is_correct === false) meta.appendChild(badge('con error', 'warn'));
        var dl = el('dl');
        function row(k, v) { if (v === null || v === undefined || v === '') return; dl.appendChild(el('dt', { text: k })); dl.appendChild(el('dd', { text: String(v) })); }
        row('Respuesta del estudiante', i.student_answer);
        row('Respuesta correcta', i.gold_answer);
        row('Error observable', i.gold_error_observable);
        row('Tipo de error (hipótesis)', i.gold_error_type);
        row('Cómo se generó el error', i.error_generator);
        row('Currículo (M-2024, págs.)', i.curriculum_page);
        row('Revisión', i.reviewer_status === 'unreviewed' ? 'sin revisión docente' : i.reviewer_status);
        box.appendChild(el('article', { class: 'item' }, [meta, el('p', { text: i.problem_text }), dl]));
      });
      if (list.length > 60) box.appendChild(el('p', { class: 'count', text: 'Se muestran los primeros 60. Usa los filtros para acotar.' }));
    }
    render();
  }

  // ---------- Resultados del piloto técnico
  if ($('runs-table') && window.PROJECT_RUNS) {
    var D = window.PROJECT_RUNS, R = D.runs;
    function med(a) { var s = a.slice().sort(function (x, y) { return x - y; }); var m = Math.floor(s.length / 2); return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; }
    var head = ['Corrida', 'Inicio (UTC)', 'Ítems', 'Errores', 'Truncadas', 'Modo', 'Sin red', 'Primer ítem (s)', 'Mediana del resto (s)', 'Archivo (SHA-256, 16)'];
    var tb = el('table', null, [el('thead', null, [el('tr', null, head.map(function (h) { return el('th', { text: h }); }))])]);
    var body = el('tbody');
    R.forEach(function (r) {
      var w = r.results.map(function (x) { return x.wall_s; });
      var rest = w.slice(1);
      body.appendChild(el('tr', null, [
        el('td', { class: 'mono', text: r.run_id }), el('td', { text: r.started_utc.slice(0, 19).replace('T', ' ') }),
        el('td', { text: String(r.items) }), el('td', { text: String(r.counts.errors) }), el('td', { text: String(r.counts.truncated) }),
        el('td', { text: r.offload_first === 'gpu_only' ? 'GPU pura' : String(r.offload_first) }),
        el('td', null, [r.offline_verified ? badge('sí (verificado)', 'ok') : badge('no: con red', 'pend')]),
        el('td', { text: w[0].toFixed(2) }), el('td', { text: rest.length ? med(rest).toFixed(2) : '—' }),
        el('td', { class: 'mono', text: r.sha256_16 })]));
    });
    tb.appendChild(body); $('runs-table').appendChild(tb);

    // Rejilla de coincidencia con la corrida sin red
    var ref = R.filter(function (r) { return r.offline_verified; })[0] || R[R.length - 1];
    var ids = ref.results.map(function (x) { return x.id; });
    var heat = $('heat');
    heat.style.gridTemplateColumns = 'minmax(110px,max-content) repeat(' + R.length + ', minmax(70px,1fr))';
    heat.appendChild(el('div', { class: 'head', text: 'Ítem' }));
    R.forEach(function (r) { heat.appendChild(el('div', { class: 'head', text: r.run_id + (r.run_id === ref.run_id ? ' (ref.)' : '') })); });
    ids.forEach(function (id) {
      heat.appendChild(el('div', { class: 'mono', text: id }));
      var refResp = ref.results.filter(function (x) { return x.id === id; })[0].response;
      R.forEach(function (r) {
        var m = r.results.filter(function (x) { return x.id === id; })[0];
        if (!m) heat.appendChild(el('div', { class: 'cell head', text: '—' }));
        else heat.appendChild(el('div', { class: 'cell ' + (m.response === refResp ? 'same' : 'diff'), text: m.response === refResp ? 'igual' : 'distinta' }));
      });
    });

    // Respuestas del modelo (texto plano)
    var sel = $('run-select');
    R.forEach(function (r, i) { sel.appendChild(el('option', { value: String(i), text: r.run_id + ' · ' + r.items + ' ítems' + (r.offline_verified ? ' · sin red' : ' · con red') })); });
    sel.value = String(R.indexOf(ref));
    function showRun() {
      var r = R[Number(sel.value)], box = $('responses'); clear(box);
      r.results.forEach(function (x) {
        var tags = [badge(TASK[x.task], 'pend'), badge(x.wall_s.toFixed(2) + ' s', 'pend'), badge(x.eval_count + ' tokens', 'pend')];
        if (x.truncated) tags.push(badge('truncada', 'bad'));
        if (x.has_reasoning || x.think_tag_in_response) tags.push(badge('con razonamiento', 'warn'));
        if (x.hint_contains_gold === true) tags.push(badge('la pista contiene el resultado', 'bad'));
        if (x.latex) tags.push(badge('formato LaTeX', 'warn'));
        var dl = el('dl'); dl.appendChild(el('dt', { text: 'Correcta' })); dl.appendChild(el('dd', { text: x.gold_answer }));
        if (x.student_answer) { dl.appendChild(el('dt', { text: 'Estudiante' })); dl.appendChild(el('dd', { text: x.student_answer })); }
        box.appendChild(el('article', { class: 'item' }, [el('div', { class: 'meta' }, [el('code', { text: x.id })].concat(tags)), dl, el('pre', { class: 'resp', text: x.response })]));
      });
    }
    sel.addEventListener('change', showRun); showRun();

    // Evidencia de red
    var ne = $('net-evidence');
    D.network_evidence.forEach(function (n) {
      ne.appendChild(el('li', null, [
        el('code', { text: n.file }), ' — Wi-Fi: ' + n.wifi_before.join(', ') + ' → ' + n.wifi_after.join(', ') +
        '; conexión a 1.1.1.1:443 y 8.8.8.8:53 antes: ' + n.probe_before.map(function (b) { return b ? 'sí' : 'no'; }).join(' / ') +
        ', después: ' + n.probe_after.map(function (b) { return b ? 'sí' : 'no'; }).join(' / ') + '. Código de salida del runner: ' + n.runner_exit_code + '.']));
    });
  }
})();
