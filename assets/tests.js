/* Páginas de pruebas: catálogo, piloto, ajuste de formato y capacidad de la GPU.
   Todo el texto de los datos se inserta con textContent (nunca como HTML). */
(function () {
  'use strict';
  var T = window.PROJECT_TESTS, I = window.PROJECT_ITEMS, R = window.PROJECT_RUNS;
  if (!T) return;

  var SVGNS = 'http://www.w3.org/2000/svg';
  function el(tag, props, children) {
    var n = document.createElement(tag);
    if (props) Object.keys(props).forEach(function (k) {
      if (k === 'class') n.className = props[k]; else if (k === 'text') n.textContent = props[k]; else n.setAttribute(k, props[k]);
    });
    (children || []).forEach(function (c) { n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }
  function svg(tag, attrs, text) {
    var n = document.createElementNS(SVGNS, tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    return n;
  }
  function $(id) { return document.getElementById(id); }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); }
  function badge(text, kind) { return el('span', { class: 'badge b-' + kind, text: text }); }
  function num(x, d) { return x == null ? '—' : x.toFixed(d == null ? 1 : d).replace('.', ','); }
  function pct(x, d) { return x == null ? '—' : num(100 * x, d == null ? 1 : d) + ' %'; }
  function median(a) { var s = a.slice().sort(function (x, y) { return x - y; }), m = Math.floor(s.length / 2); return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; }

  var MODELS = ['q4_K_M', 'q8_0', 'fp16'];
  var SHAPE = { q4_K_M: 'circle', q8_0: 'square', fp16: 'diamond' };
  var TASK = { solve: 'Resolver', diagnose: 'Diagnosticar', hint: 'Pista' };

  function marker(shape, cx, cy, cls) {
    if (shape === 'circle') return svg('circle', { cx: cx, cy: cy, r: 5, class: cls });
    if (shape === 'square') return svg('rect', { x: cx - 4.5, y: cy - 4.5, width: 9, height: 9, class: cls });
    return svg('polygon', { points: [cx, cy - 6, cx + 6, cy, cx, cy + 6, cx - 6, cy].join(' '), class: cls });
  }

  /* ---------- Gráfico de intervalos (una fila por precisión, agrupado por métrica) ---------- */
  function forest(container, groups) {
    var W = 680, L = 110, Rr = 190, rowH = 24, headH = 30, top = 8, y = top;  // Rr reserva una columna fija para las etiquetas
    var h = top + groups.length * (headH + 3 * rowH + 8) + 30;
    var s = svg('svg', { viewBox: '0 0 ' + W + ' ' + h, class: 'chart', role: 'img', 'aria-label': 'Tasas por precisión con intervalos de confianza' });
    function X(p) { return L + (W - L - Rr) * p; }
    groups.forEach(function (g) {
      s.appendChild(svg('text', { x: 4, y: y + 14, class: 'g-title' }, g.title));
      s.appendChild(svg('text', { x: 4, y: y + 27, class: 'g-sub' }, g.sub));
      y += headH;
      [0, 0.25, 0.5, 0.75, 1].forEach(function (p) {
        s.appendChild(svg('line', { x1: X(p), x2: X(p), y1: y - 2, y2: y + 3 * rowH - 2, class: 'grid' }));
      });
      g.rows.forEach(function (r, i) {
        var cy = y + i * rowH + rowH / 2 - 2;
        s.appendChild(svg('text', { x: L - 8, y: cy + 4, class: 'row-label', 'text-anchor': 'end' }, r.model));
        if (r.est == null) return;
        s.appendChild(svg('line', { x1: X(r.lo), x2: X(r.hi), y1: cy, y2: cy, class: 'ci m-' + r.model }));
        s.appendChild(marker(SHAPE[r.model], X(r.est), cy, 'pt m-' + r.model));
        s.appendChild(svg('text', { x: W - 4, y: cy + 4, class: 'val', 'text-anchor': 'end' }, pct(r.est, 0) + '  [' + pct(r.lo, 0).replace(' %', '') + '–' + pct(r.hi, 0) + ']'));
      });
      y += 3 * rowH + 8;
    });
    [0, 25, 50, 75, 100].forEach(function (v) { s.appendChild(svg('text', { x: X(v / 100), y: y + 12, class: 'axis', 'text-anchor': 'middle' }, v + ' %')); });
    container.appendChild(s);
  }

  /* ---------- Barras horizontales simples con umbral opcional ---------- */
  function bar(label, value, opts) {
    opts = opts || {};
    var row = el('div', { class: 'bar-row' });
    row.appendChild(el('div', { class: 'bar-label', text: label }));
    var track = el('div', { class: 'bar-track' });
    var fill = el('div', { class: 'bar-fill' + (opts.kind ? ' ' + opts.kind : '') });
    fill.style.width = Math.max(0, Math.min(100, 100 * value / (opts.max || 1))) + '%';
    track.appendChild(fill);
    if (opts.mark != null) { var m = el('div', { class: 'bar-mark', title: opts.markLabel || '' }); m.style.left = (100 * opts.mark / (opts.max || 1)) + '%'; track.appendChild(m); }
    row.appendChild(track);
    row.appendChild(el('div', { class: 'bar-val', text: opts.text || pct(value) }));
    return row;
  }

  /* =====================================================================
     PÁGINA: Pruebas (catálogo) — cifras clave calculadas desde los datos
     ===================================================================== */
  if ($('cat-pilot')) {
    var P = T.pilot, rep = P.report;
    function g(task, sub, model) { return rep.groups.filter(function (x) { return x.task === task && x.subgroup === sub && x.model === model; })[0]; }
    $('cat-pilot').textContent = 'Resolver: q8_0 y fp16 ' + pct(g('solve', 'todos', 'fp16').rate_strict, 0) + ', q4_K_M ' + pct(g('solve', 'todos', 'q4_K_M').rate_strict, 0) +
      '. Pistas sin fuga del resultado: q4_K_M ' + pct(g('hint', 'todos', 'q4_K_M').rate_strict, 0) + ', fp16 ' + pct(g('hint', 'todos', 'fp16').rate_strict, 0) + '.';
    $('cat-pilot-n').textContent = P.totals.records + ' registros (' + P.totals.measured + ' medidos), ' + P.totals.errors + ' errores';
    var f2 = T.format.rounds[1].decision, f1 = T.format.rounds[0].decision;
    var best1 = Object.keys(f1.variants).map(function (v) { return [v, f1.variants[v].format_rate]; }).sort(function (a, b) { return b[1] - a[1]; })[0];
    $('cat-format1').textContent = 'Ninguna cumplió. La mejor, ' + best1[0] + ', llegó a ' + pct(best1[1]) + ' (umbral 90 %).';
    $('cat-format2').textContent = 'Cumplió ' + f2.chosen + ': ' + pct(f2.variants[f2.chosen].format_rate) + ' global y ' + pct(f2.variants[f2.chosen].format_rate_division) + ' en divisiones.';
    var fp = T.gpu.footprint.filter(function (x) { return x.ok; });
    $('cat-gpu').textContent = fp.length + ' modelos caben completos en GPU; el servidor mantiene como máximo ' + T.gpu.co_load[T.gpu.co_load.length - 1].loaded_now + ' cargados a la vez; en paralelo la velocidad cae entre ' +
      Math.round(100 * Math.min.apply(null, MODELS.map(function (m) { return 1 - T.gpu.concurrency.median_concurrent['qwen3:0.6b-' + m] / T.gpu.concurrency.median_solo['qwen3:0.6b-' + m]; }))) + ' y ' +
      Math.round(100 * Math.max.apply(null, MODELS.map(function (m) { return 1 - T.gpu.concurrency.median_concurrent['qwen3:0.6b-' + m] / T.gpu.concurrency.median_solo['qwen3:0.6b-' + m]; }))) + ' %.';
    if (R) {
      var off = R.runs.filter(function (r) { return r.offline_verified; })[0];
      $('cat-smoke').textContent = R.runs.length + ' corridas; la de ' + off.items + ' ítems sin internet terminó con ' + off.counts.errors + ' errores, en GPU pura.';
    }
  }

  /* =====================================================================
     PÁGINA: Piloto
     ===================================================================== */
  if ($('pilot-kpis')) {
    var P = T.pilot, rep = P.report, kp = $('pilot-kpis');
    [[P.totals.records, 'registros ejecutados'], [P.totals.measured, 'registros medidos (sin calentamiento)'], [P.totals.errors + ' / ' + P.totals.truncated, 'errores / truncadas'],
     [Math.round(P.duration_s / 60 * 10) / 10 + ' min', 'duración total, en secuencia']].forEach(function (k) {
      kp.appendChild(el('div', { class: 'card' }, [el('div', { class: 'stat', text: String(k[0]).replace('.', ',') }), el('div', { class: 'stat-label', text: k[1] })]));
    });
    var groups = rep.groups, defs = [['solve', 'todos', 'Resolver · exactitud', 'Acierta la respuesta final'], ['diagnose', 'con_error', 'Diagnosticar · sensibilidad', 'Detecta el error cuando lo hay (21 problemas)'],
      ['diagnose', 'control', 'Diagnosticar · especificidad', 'No acusa error cuando no lo hay (6 controles)'], ['hint', 'todos', 'Pista · sin fuga', 'La pista NO contiene el resultado']];
    forest($('pilot-forest'), defs.map(function (d) {
      return { title: d[2], sub: d[3], rows: MODELS.map(function (m) {
        var x = groups.filter(function (q) { return q.task === d[0] && q.subgroup === d[1] && q.model === m; })[0];
        return { model: m, est: x && x.rate_strict, lo: x && x.ci95_low, hi: x && x.ci95_high };
      }) };
    }));
    var pb = $('pilot-paired').appendChild(el('tbody'));
    rep.paired.forEach(function (p) {
      var crosses = p.ci95_low <= 0 && p.ci95_high >= 0;
      pb.appendChild(el('tr', null, [el('td', { text: TASK[p.task] + (p.subgroup === 'todos' ? '' : ' (' + (p.subgroup === 'con_error' ? 'con error' : 'control') + ')') }),
        el('td', { text: p.a + ' − ' + p.b }), el('td', { text: (p.diff >= 0 ? '+' : '') + num(100 * p.diff) + ' pts' }),
        el('td', { text: '[' + num(100 * p.ci95_low) + '; ' + num(100 * p.ci95_high) + ']' }),
        el('td', { text: p.a_better + ' / ' + p.b_better + ' / ' + p.ties }), el('td', null, [crosses ? badge('incluye 0', 'pend') : badge('no incluye 0', 'warn')])]));
    });
    var rb = $('pilot-repeat').appendChild(el('tbody'));
    rep.repeatability.forEach(function (r) {
      var tm = rep.timing.filter(function (t) { return t.model === r.model; })[0];
      rb.appendChild(el('tr', null, [el('td', { text: r.model }), el('td', { text: r.identical_response + ' de ' + r.items_multi_rep }), el('td', { text: String(r.score_changes) }),
        el('td', { text: num(tm.median_tokens_per_s, 0) }), el('td', { text: num(tm.median_wall_s, 2) + ' s' })]));
    });
  }

  /* ---------- Explorador de respuestas + herramienta de revisión humana ---------- */
  if ($('rv-list') && I) {
    var items = {}; I.items.forEach(function (i) { items[i.item_id] = i; });
    var recs = T.pilot.records.filter(function (r) { return r.r === 1; });
    var byKey = {}; T.pilot.records.forEach(function (r) { (byKey[r.m + '|' + r.i] = byKey[r.m + '|' + r.i] || []).push(r); });
    var STORE = 'math_project_review_v1', marks = {};
    try { marks = JSON.parse(localStorage.getItem(STORE) || '{}'); } catch (e) { marks = {}; }
    function save() { try { localStorage.setItem(STORE, JSON.stringify(marks)); } catch (e) { $('rv-warn').hidden = false; } }
    var F = { model: '', task: '', sub: '', only: '', q: '', mark: '' }, LIMIT = 30, shown = LIMIT;

    function fill(id, entries, key) {
      var s = $(id); entries.forEach(function (e) { s.appendChild(el('option', { value: e[0], text: e[1] })); });
      s.addEventListener('change', function () { F[key] = s.value; shown = LIMIT; render(); });
    }
    fill('rv-model', [['', 'Todas'], ['q4_K_M', 'q4_K_M'], ['q8_0', 'q8_0'], ['fp16', 'fp16']], 'model');
    fill('rv-task', [['', 'Todas'], ['solve', 'Resolver'], ['diagnose', 'Diagnosticar'], ['hint', 'Pista']], 'task');
    fill('rv-sub', [['', 'Todos'], ['err', 'Con error'], ['ctl', 'Control (respuesta correcta)']], 'sub');
    fill('rv-only', [['', 'Todas las respuestas'], ['fail', 'Donde el corrector marcó fallo o fuga'], ['ok', 'Donde el corrector marcó acierto'], ['diff', 'Donde las precisiones puntúan distinto'], ['unstable', 'Donde las 3 repeticiones no son idénticas']], 'only');
    fill('rv-mark', [['', 'Todas'], ['none', 'Sin revisar'], ['agree', 'De acuerdo'], ['disagree', 'En desacuerdo'], ['doubt', 'Con duda']], 'mark');
    $('rv-q').addEventListener('input', function (e) { F.q = e.target.value.toLowerCase(); shown = LIMIT; render(); });

    function scoreOf(model, item) { var r = recs.filter(function (x) { return x.m === model && x.i === item; })[0]; return r ? r.sc : null; }
    function verdictBadge(r) {
      if (r.sc === 1) return badge(r.t === 'hint' ? 'corrector: sin fuga' : 'corrector: acierto', 'ok');
      if (r.sc === 0) return badge(r.t === 'hint' ? 'corrector: HAY FUGA' : 'corrector: fallo', 'bad');
      return badge('corrector: sin leer', 'warn');
    }
    function passes(r) {
      var it = items[r.i], key = r.m + '|' + r.i, mk = marks[key] && marks[key].v;
      if (F.model && r.m !== F.model) return false;
      if (F.task && r.t !== F.task) return false;
      if (F.sub === 'err' && it.student_answer_is_correct !== false) return false;
      if (F.sub === 'ctl' && it.student_answer_is_correct !== true) return false;
      if (F.only === 'fail' && r.sc !== 0) return false;
      if (F.only === 'ok' && r.sc !== 1) return false;
      if (F.only === 'diff') { var s = MODELS.map(function (m) { return scoreOf(m, r.i); }); if (s.every(function (x) { return x === s[0]; })) return false; }
      if (F.only === 'unstable') { var rs = byKey[key] || []; if (new Set(rs.map(function (x) { return x.re; })).size < 2) return false; }
      if (F.mark === 'none' && mk) return false;
      if (F.mark && F.mark !== 'none' && mk !== F.mark) return false;
      if (F.q && (r.i + ' ' + it.problem_text + ' ' + r.re).toLowerCase().indexOf(F.q) < 0) return false;
      return true;
    }
    function counts() {
      var c = { agree: 0, disagree: 0, doubt: 0 }; Object.keys(marks).forEach(function (k) { if (marks[k].v) c[marks[k].v]++; });
      $('rv-count').textContent = 'Has revisado ' + (c.agree + c.disagree + c.doubt) + ' respuestas: ' + c.agree + ' de acuerdo · ' + c.disagree + ' en desacuerdo · ' + c.doubt + ' con duda.';
    }
    function card(r) {
      var it = items[r.i], key = r.m + '|' + r.i, cur = marks[key] || {}, same = (byKey[key] || []).length > 1 && new Set(byKey[key].map(function (x) { return x.re; })).size === 1;
      var meta = el('div', { class: 'meta' }, [el('code', { text: r.i }), badge(r.m, 'info'), badge(TASK[r.t], 'pend'), verdictBadge(r)]);
      if (it.student_answer_is_correct === true) meta.appendChild(badge('control: el estudiante acierta', 'ok'));
      if (r.fl && r.fl.latex) meta.appendChild(badge('LaTeX', 'warn'));
      meta.appendChild(badge(same ? '3 repeticiones idénticas' : 'repeticiones distintas', same ? 'pend' : 'warn'));
      var dl = el('dl');
      function row(k, v) { if (v == null || v === '') return; dl.appendChild(el('dt', { text: k })); dl.appendChild(el('dd', { text: String(v) })); }
      row('Respuesta del estudiante', it.student_answer); row('Respuesta correcta', it.gold_answer);
      if (r.t === 'solve') row('Lo que leyó el corrector', r.d ? JSON.stringify(r.d).replace(/[{}"]/g, '') + ' (' + r.me + ')' : 'nada');
      if (r.t === 'diagnose') row('Veredicto leído / esperado', r.d ? r.d.verdict + ' / ' + r.d.expected : '—');
      if (r.t === 'hint') row('Cifras del resultado halladas en la pista', r.d && r.d.leaked && r.d.leaked.length ? r.d.leaked.join(', ') : 'ninguna');
      var btns = el('div', { class: 'rv-btns' });
      [['agree', '✓ De acuerdo con el corrector'], ['disagree', '✗ En desacuerdo'], ['doubt', '? Dudo']].forEach(function (b) {
        var bt = el('button', { type: 'button', class: 'rv-btn' + (cur.v === b[0] ? ' on-' + b[0] : ''), text: b[1] });
        bt.addEventListener('click', function () {
          var v = marks[key] && marks[key].v === b[0] ? null : b[0];
          marks[key] = { v: v, n: (marks[key] && marks[key].n) || '', at: new Date().toISOString() }; if (!v && !marks[key].n) delete marks[key]; save(); counts(); render(true);
        });
        btns.appendChild(bt);
      });
      var note = el('textarea', { class: 'rv-note', rows: '2', placeholder: 'Tu nota (qué está mal, qué esperabas…)', 'aria-label': 'Nota de revisión' });
      note.value = cur.n || '';
      note.addEventListener('change', function () { marks[key] = { v: (marks[key] && marks[key].v) || null, n: note.value, at: new Date().toISOString() }; if (!marks[key].v && !note.value) delete marks[key]; save(); counts(); });
      return el('article', { class: 'item' }, [meta, el('p', { class: 'q', text: it.problem_text }), dl, el('pre', { class: 'resp', text: r.re }), btns, note]);
    }
    function render(keep) {
      var list = recs.filter(passes);
      $('rv-shown').textContent = list.length + ' de ' + recs.length + ' respuestas (primera repetición de cada una)';
      var box = $('rv-list'), y = window.scrollY; clear(box);
      list.slice(0, shown).forEach(function (r) { box.appendChild(card(r)); });
      if (list.length > shown) {
        var more = el('button', { type: 'button', class: 'rv-more', text: 'Mostrar 30 más (' + (list.length - shown) + ' restantes)' });
        more.addEventListener('click', function () { shown += LIMIT; render(true); }); box.appendChild(more);
      }
      if (keep) window.scrollTo(0, y);
    }
    function download(name, text, type) {
      var a = el('a', { href: URL.createObjectURL(new Blob([text], { type: type })), download: name }); document.body.appendChild(a); a.click(); document.body.removeChild(a);
    }
    function safeCell(s) { s = String(s == null ? '' : s); if (/^[=+\-@\t\r]/.test(s)) s = "'" + s; return '"' + s.replace(/"/g, '""') + '"'; }
    function rows() {
      return Object.keys(marks).sort().map(function (k) {
        var p = k.split('|'), it = items[p[1]], r = recs.filter(function (x) { return x.m === p[0] && x.i === p[1]; })[0] || {};
        return { modelo: p[0], item: p[1], tarea: it ? it.task : '', corrector: r.sc == null ? 'sin leer' : (r.sc === 1 ? 'acierto/sin fuga' : 'fallo/fuga'), mi_veredicto: marks[k].v || '', nota: marks[k].n || '', fecha: marks[k].at || '' };
      });
    }
    $('rv-csv').addEventListener('click', function () {
      var rs = rows(), cols = ['modelo', 'item', 'tarea', 'corrector', 'mi_veredicto', 'nota', 'fecha'];
      download('mi_revision_piloto.csv', '﻿' + cols.join(',') + '\n' + rs.map(function (r) { return cols.map(function (c) { return safeCell(r[c]); }).join(','); }).join('\n') + '\n', 'text/csv;charset=utf-8');
    });
    $('rv-json').addEventListener('click', function () { download('mi_revision_piloto.json', JSON.stringify({ dataset_sha256_16: I.sha256_16, matriz: T.pilot.matrix.id, marcas: rows() }, null, 2), 'application/json'); });
    $('rv-clear').addEventListener('click', function () {
      if (window.confirm('¿Borrar todas tus marcas y notas de este navegador? Exporta antes si las necesitas.')) { marks = {}; save(); counts(); render(true); }
    });
    counts(); render();
  }

  /* =====================================================================
     PÁGINA: Ajuste de formato
     ===================================================================== */
  if ($('format-rounds')) {
    var host = $('format-rounds');
    T.format.rounds.forEach(function (rd) {
      var d = rd.decision, sec = el('section', { class: 'round', id: 'ronda-' + rd.round });
      sec.appendChild(el('h2', { text: 'Ronda ' + rd.round + ' · ' + (d.chosen ? 'ganó ' + d.chosen : 'ninguna variante cumplió') }));
      sec.appendChild(el('p', { class: 'count', text: 'Sondas: ' + rd.probes_bases + ' problemas de práctica (' + rd.probes_items + ' ítems; solo se usó «resolver»), SHA-256 ' + rd.probes_sha.slice(0, 12) + '… · ' + rd.matrices + ' matrices en secuencia.' }));
      var tb = el('table', null, [el('thead', null, [el('tr', null, ['Variante', 'Formato global (≥ 90 %)', 'En divisiones (≥ 80 %)', 'Sin leer', 'Por precisión (fp16 / q4_K_M / q8_0)', 'Veredicto'].map(function (h) { return el('th', { text: h }); }))])]);
      var body = el('tbody');
      Object.keys(d.variants).forEach(function (v) {
        var x = d.variants[v], ok = x.format_rate >= d.rule.global_min && x.format_rate_division >= d.rule.division_min;
        var pm = x.format_rate_by_model;
        body.appendChild(el('tr', null, [el('td', { class: 'mono', text: v }), el('td', { text: pct(x.format_rate) }), el('td', { text: pct(x.format_rate_division) }), el('td', { text: String(x.unscored) }),
          el('td', { text: Object.keys(pm).map(function (k) { return k.split(':')[1].replace('0.6b-', '') + ' ' + pct(pm[k], 0); }).join(' · ') }),
          el('td', null, [ok ? badge(d.chosen === v ? 'cumple y se congeló' : 'cumple', 'ok') : badge('no cumple', 'bad')])]));
      });
      tb.appendChild(body); sec.appendChild(el('div', { class: 'table-wrap' }, [tb]));
      var bars = el('div', { class: 'bars' });
      bars.appendChild(el('h3', { text: 'Formato leído, global (la línea marca el umbral del 90 %)' }));
      Object.keys(d.variants).forEach(function (v) { bars.appendChild(bar(v, d.variants[v].format_rate, { mark: d.rule.global_min, markLabel: 'umbral 90 %', kind: d.variants[v].format_rate >= d.rule.global_min ? 'ok' : '' })); });
      bars.appendChild(el('h3', { text: 'Formato leído en divisiones (umbral 80 %)' }));
      Object.keys(d.variants).forEach(function (v) { bars.appendChild(bar(v, d.variants[v].format_rate_division, { mark: d.rule.division_min, markLabel: 'umbral 80 %', kind: d.variants[v].format_rate_division >= d.rule.division_min ? 'ok' : '' })); });
      sec.appendChild(bars);
      sec.appendChild(el('p', { text: d.chosen ? 'Decisión: ' + d.reason + '.' : 'Decisión: ' + d.reason + '. No se congeló ninguna variante.' }));
      var det = el('details', null, [el('summary', { text: 'Ver el texto exacto de cada variante (solo cambia la indicación de formato de «resolver»)' })]);
      Object.keys(rd.prompts).forEach(function (v) {
        det.appendChild(el('h3', { text: v })); det.appendChild(el('p', { class: 'count', text: 'Problema de suma/resta/multiplicación:' })); det.appendChild(el('pre', { class: 'resp', text: rd.prompts[v].sub }));
        det.appendChild(el('p', { class: 'count', text: 'Problema de división:' })); det.appendChild(el('pre', { class: 'resp', text: rd.prompts[v].div }));
      });
      sec.appendChild(det);
      var acc = el('p', { class: 'count', text: 'Exactitud aparente (informativa, NO usada para decidir): ' + Object.keys(d.variants).map(function (v) { return v + ' ' + pct(d.variants[v].accuracy_informative, 0); }).join(' · ') });
      sec.appendChild(acc);
      host.appendChild(sec);
    });
    var fz = T.format.frozen, fb = $('frozen-box');
    fb.appendChild(el('p', null, [el('strong', { text: fz.version }), ' · huella SHA-256 de las plantillas y el prompt de sistema: ', el('code', { text: fz.sha256 })]));
    [['Resolver (sumas, restas, multiplicaciones)', fz.texts.solve_sub], ['Resolver (divisiones)', fz.texts.solve_div], ['Diagnosticar (nunca se ajustó)', fz.texts.diagnose], ['Pista (nunca se ajustó)', fz.texts.hint], ['Prompt de sistema', fz.texts.system]].forEach(function (x) {
      fb.appendChild(el('h3', { text: x[0] })); fb.appendChild(el('pre', { class: 'resp', text: x[1] }));
    });
  }

  /* =====================================================================
     PÁGINA: Capacidad de la GPU
     ===================================================================== */
  if ($('gpu-foot')) {
    var G = T.gpu, total = G.meta.gpu.total_mib, base = G.meta.gpu.used_mib;
    $('gpu-meta').textContent = G.meta.gpu.name + ', ' + total + ' MiB, driver ' + G.meta.gpu.driver + ' · Ollama ' + G.meta.ollama_version + ' · medido el ' + G.meta.started_utc.slice(0, 10) + ' (UTC) · el escritorio ya ocupaba ' + base + ' MiB.';
    var foot = G.footprint.filter(function (x) { return x.ok; }).sort(function (a, b) { return a.gpu_delta_mib - b.gpu_delta_mib; }), fbox = $('gpu-foot');
    foot.forEach(function (x) {
      fbox.appendChild(bar(x.model, x.gpu_delta_mib / (total - base), { max: 1, text: x.gpu_delta_mib + ' MiB · ' + (x.size_vram_mib >= 0.99 * x.size_mib ? 'GPU pura' : 'híbrido'), kind: x.size_vram_mib >= 0.99 * x.size_mib ? '' : 'warn' }));
    });
    var cb = $('gpu-coload').appendChild(el('tbody'));
    G.co_load.forEach(function (c, i) {
      cb.appendChild(el('tr', null, [el('td', { text: String(i + 1) }), el('td', { class: 'mono', text: c.loading }), el('td', { text: String(c.loaded_now) }), el('td', { text: c.gpu_used_mib + ' MiB' }),
        el('td', null, [c.loaded_now < i + 1 ? badge('el servidor expulsó un modelo', 'warn') : badge('todos siguen cargados', 'ok')])]));
    });
    var cc = $('gpu-conc'), C = G.concurrency;
    MODELS.forEach(function (m) {
      var key = 'qwen3:0.6b-' + m, solo = C.median_solo[key], conc = C.median_concurrent[key], mx = Math.max.apply(null, MODELS.map(function (q) { return C.median_solo['qwen3:0.6b-' + q]; })) * 1.05;
      cc.appendChild(el('h3', { text: m }));
      cc.appendChild(bar('solo', solo, { max: mx, text: num(solo, 0) + ' tokens/s' }));
      cc.appendChild(bar('3 a la vez', conc, { max: mx, text: num(conc, 0) + ' tokens/s  (−' + Math.round(100 * (1 - conc / solo)) + ' %)', kind: 'warn' }));
    });
  }
})();
