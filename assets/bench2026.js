/* Renderiza las tablas y barras del benchmark 2026 desde window.BENCH2026 (datos agregados). */
(function () {
  'use strict';
  var D = window.BENCH2026;
  function $(id) { return document.getElementById(id); }
  function el(tag, attrs, kids) {
    var e = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'text') e.textContent = attrs[k]; else if (k === 'class') e.className = attrs[k]; else e.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return e;
  }
  function wilson(k, n) {
    if (!n) return null;
    var z = 1.96, p = k / n, d = 1 + z * z / n, c = (p + z * z / (2 * n)) / d;
    var h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d;
    return [Math.max(0, c - h), Math.min(1, c + h)];
  }
  function pct(x) { return Math.round(100 * x) + ' %'; }
  function fmt(n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' '); }
  if (!D) { return; }
  var M = D.models;
  function label(id) { return M.filter(function (m) { return m.id === id; })[0].label; }
  function out(t, id, key) { return (D.tasks[t].outcomes[id] || {})[key] || 0; }
  function table(head, rows, cls) {
    var thead = el('thead', {}, [el('tr', {}, head.map(function (h) {
      return el('th', { class: h.cls || '', text: h.t });
    }))]);
    var tbody = el('tbody', {}, rows);
    return el('div', { class: 'table-wrap' }, [el('table', { class: cls || '' }, [thead, tbody])]);
  }
  function bestSet(values, higher) {
    var b = higher ? Math.max.apply(null, values) : Math.min.apply(null, values);
    return values.map(function (v) { return v === b; });
  }

  /* KPIs */
  if ($('b-kpis')) {
    var stats = [[D.n_items, 'ítems del benchmark'], [D.n_families, 'problemas base (familias)'], [M.length, 'configuraciones evaluadas'], [M.reduce(function (a, m) { return a + m.n_ok; }, 0), 'respuestas registradas']];
    stats.forEach(function (s) {
      $('b-kpis').appendChild(el('div', { class: 'card' }, [el('div', { class: 'stat', text: String(s[0]) }), el('div', { class: 'stat-label', text: s[1] })]));
    });
  }

  /* Tabla resumen */
  if ($('b-summary')) {
    var a = M.map(function (m) { return out('A', m.id, 'correct'); });
    var bv = M.map(function (m) { return D.verdict[m.id].err_said_incorrect + D.verdict[m.id].ctrl_said_correct; });
    var cl = M.map(function (m) { return out('C', m.id, 'leak'); });
    var ba = bestSet(a, true), bb = bestSet(bv, true), bc = bestSet(cl, false);
    var rows = M.map(function (m, i) {
      var ci = wilson(a[i], 60);
      return el('tr', {}, [
        el('td', {}, [el('strong', { text: m.label })]),
        el('td', { class: 'num', text: m.params }),
        el('td', { class: 'num' + (ba[i] ? ' best' : ''), text: a[i] + '/60' }),
        el('td', { class: 'num small', text: pct(ci[0]) + '–' + pct(ci[1]) }),
        el('td', { class: 'num' + (bb[i] ? ' best' : ''), text: bv[i] + '/60' }),
        el('td', { class: 'num', text: D.verdict[m.id].err_verdict_and_category + '/51' }),
        el('td', { class: 'num' + (bc[i] ? ' best' : ''), text: cl[i] + '/60' }),
        el('td', { class: 'num', text: fmt(m.tok_s) }),
        el('td', { class: 'num', text: fmt(m.wall_ms) }),
        el('td', { class: 'num', text: fmt(m.vram_mb) })
      ]);
    });
    $('b-summary').appendChild(table([
      { t: 'Modelo' }, { t: 'Parám. (Ollama)', cls: 'num' }, { t: 'Resolución', cls: 'num' }, { t: 'IC 95 %', cls: 'num' }, { t: 'Veredicto', cls: 'num' },
      { t: 'Veredicto + categoría', cls: 'num' }, { t: 'Pistas con fuga', cls: 'num' }, { t: 'tok/s', cls: 'num' }, { t: 'ms', cls: 'num' }, { t: 'MB vídeo', cls: 'num' }
    ], rows));
  }

  /* Barras apiladas por tarea */
  function legend(defs) {
    return el('div', { class: 'legend' }, defs.map(function (d) { var i = el('i'); i.style.background = d[2]; return el('span', {}, [i, d[1]]); }));
  }
  var COL = { ok: 'var(--ok)', bad: 'var(--bad)', warn: '#b8860b', mute: 'var(--pend)' };
  function stacked(id, task, defs) {
    var host = $(id); if (!host) return;
    host.appendChild(legend(defs.map(function (d) { return [d[0], d[1], COL[d[2]]]; })));
    M.forEach(function (m) {
      var total = defs.reduce(function (s, d) { return s + out(task, m.id, d[0]); }, 0) || 1;
      var bar = el('div', { class: 'bar', role: 'img', 'aria-label': m.label });
      defs.forEach(function (d) {
        var c = out(task, m.id, d[0]);
        if (!c) return;
        var s = el('span', { class: 's-' + d[2], text: c > 2 ? String(c) : '' });
        s.style.width = (100 * c / total) + '%';
        s.title = d[1] + ': ' + c;
        bar.appendChild(s);
      });
      host.appendChild(el('div', { class: 'bar-row' }, [el('div', { class: 'lab', text: m.label }), bar]));
    });
  }
  stacked('b-stack-A', 'A', [['correct', 'Correcta', 'ok'], ['incorrect', 'Incorrecta', 'bad'], ['format_error', 'Error de formato', 'warn'], ['needs_manual_review', 'Revisión manual', 'mute']]);
  stacked('b-stack-B', 'B', [['correct', 'Veredicto y categoría acertados', 'ok'], ['verdict_only', 'Solo el veredicto', 'warn'], ['incorrect', 'Veredicto equivocado', 'bad']]);
  stacked('b-stack-C', 'C', [['no_leak', 'Sin fuga', 'ok'], ['possible_leak', 'Posible fuga', 'warn'], ['leak', 'Revela la respuesta', 'bad']]);

  /* Dificultad (resolución) */
  if ($('b-diff')) {
    var levels = [['basica', 'Básica'], ['intermedia', 'Intermedia'], ['avanzada', 'Avanzada']];
    var rows2 = M.map(function (m) {
      return el('tr', {}, [el('td', { text: m.label })].concat(levels.map(function (l) {
        var c = D.difficulty[m.id][l[0]] || [0, 0];
        var r = c[1] ? c[0] / c[1] : 0;
        return el('td', { class: 'c ' + (r >= 0.8 ? 'hi' : r >= 0.5 ? 'mid' : 'lo'), text: c[0] + '/' + c[1] });
      })));
    });
    $('b-diff').appendChild(table([{ t: 'Modelo' }].concat(levels.map(function (l) { return { t: l[1], cls: 'c' }; })), rows2, 'hm'));
  }

  /* Mapa de calor por competencia */
  function heat(id, task, leak) {
    var host = $(id); if (!host) return;
    var rows = D.skills.filter(function (s) { return Object.keys(s[task]).length; }).map(function (s) {
      return el('tr', {}, [el('td', { text: s.name })].concat(M.map(function (m) {
        var c = s[task][m.id];
        if (!c) return el('td', { class: 'c none', text: '—' });
        var r = c[0] / c[1];
        return el('td', { class: 'c ' + (r >= 0.75 ? 'hi' : r >= 0.4 ? 'mid' : 'lo'), text: c[0] + '/' + c[1] });
      })));
    });
    host.appendChild(table([{ t: 'Competencia' }].concat(M.map(function (m) { return { t: m.label.replace(' Q4_K_M', '\nQ4').replace('Qwen3-0.6B ', '0.6B '), cls: 'c' }; })), rows, 'hm' + (leak ? ' leak' : '')));
  }
  heat('b-heat-A', 'A', false);
  heat('b-heat-B', 'B', false);
  heat('b-heat-C', 'C', true);

  /* Diagnóstico: veredictos */
  if ($('b-verdict')) {
    var rows3 = M.map(function (m) {
      var v = D.verdict[m.id];
      return el('tr', {}, [
        el('td', { text: m.label }),
        el('td', { class: 'num', text: v.err_said_incorrect + ' de ' + v.err_n }),
        el('td', { class: 'num', text: v.err_said_correct + ' de ' + v.err_n }),
        el('td', { class: 'num', text: v.ctrl_said_correct + ' de ' + v.ctrl_n }),
        el('td', { class: 'num', text: v.err_verdict_and_category + ' de ' + v.err_n })
      ]);
    });
    $('b-verdict').appendChild(table([{ t: 'Modelo' }, { t: 'Error: dijo «incorrecto»', cls: 'num' }, { t: 'Error: dijo «correcto»', cls: 'num' },
      { t: 'Control: dijo «correcto»', cls: 'num' }, { t: 'Error: veredicto y categoría', cls: 'num' }], rows3));
  }

  /* Costo */
  if ($('b-cost')) {
    var rows4 = M.map(function (m) {
      return el('tr', {}, [
        el('td', { text: m.label }), el('td', { class: 'num', text: m.quant }), el('td', { class: 'num', text: fmt(m.vram_mb) }),
        el('td', { class: 'num', text: fmt(m.tok_s) }), el('td', { class: 'num', text: fmt(m.wall_ms) }), el('td', { class: 'num', text: fmt(m.ttft_ms) }),
        el('td', { class: 'num', text: fmt(m.eval_tokens) }), el('td', {}, [el('code', { text: m.digest })])
      ]);
    });
    $('b-cost').appendChild(table([{ t: 'Modelo' }, { t: 'Cuant.', cls: 'num' }, { t: 'MB de vídeo', cls: 'num' }, { t: 'tok/s', cls: 'num' }, { t: 'Latencia ms', cls: 'num' },
      { t: '1.er token ms', cls: 'num' }, { t: 'Tokens generados', cls: 'num' }, { t: 'Digest' }], rows4));
  }

  /* Cobertura (página del benchmark) */
  if ($('b-coverage')) {
    var rows5 = D.coverage.map(function (c) {
      return el('tr', {}, [el('td', { text: c.name }), el('td', {}, [el('code', { text: c.skill })]), el('td', { class: 'num', text: c.n }), el('td', { class: 'num', text: c.A }),
        el('td', { class: 'num', text: c.B }), el('td', { class: 'num', text: c.C }), el('td', { class: 'num', text: c.families }), el('td', { class: 'num', text: c.controls }),
        el('td', { class: 'num', text: c.zero })]);
    });
    $('b-coverage').appendChild(table([{ t: 'Competencia' }, { t: 'Id' }, { t: 'Ítems', cls: 'num' }, { t: 'A', cls: 'num' }, { t: 'B', cls: 'num' }, { t: 'C', cls: 'num' },
      { t: 'Familias', cls: 'num' }, { t: 'Controles', cls: 'num' }, { t: 'Con cero', cls: 'num' }], rows5));
  }
  if ($('b-validation')) {
    var v = D.validation;
    $('b-validation').textContent = 'Validador: ' + v.result + ' · ' + v.errors + ' errores · ' + v.warnings + ' advertencias · ' + D.n_items + ' ítems · ' + D.n_families + ' familias · '
      + D.controls + ' controles de trabajo correcto · ' + D.zero_items + ' ítems que involucran el cero · mayor peso de una competencia: ' + (100 * D.max_skill_share).toFixed(1).replace('.', ',') + ' %.';
  }
})();
