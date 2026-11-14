/* Rondas repetidas, ablación del diagnóstico y brecha de verificación (datos agregados de BENCH2026). */
(function () {
  'use strict';
  var D = window.BENCH2026;
  if (!D || !D.rounds) return;
  function $(id) { return document.getElementById(id); }
  function el(tag, attrs, kids) {
    var e = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'text') e.textContent = attrs[k]; else if (k === 'class') e.className = attrs[k]; else e.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return e;
  }
  function table(head, rows, cls) {
    return el('div', { class: 'table-wrap' }, [el('table', { class: cls || '' }, [
      el('thead', {}, [el('tr', {}, head.map(function (h) { return el('th', { class: h.cls || '', text: h.t }); }))]), el('tbody', {}, rows)])]);
  }
  var M = D.models;
  function label(id) { return M.filter(function (m) { return m.id === id; })[0].label; }
  function f1(x) { return x == null ? '—' : (Math.round(x * 10) / 10).toString().replace('.', ','); }
  function sgn(x) { return (x > 0 ? '+' : x < 0 ? '−' : '') + Math.abs(Math.round(x * 10) / 10).toString().replace('.', ','); }

  /* 1. Rondas */
  if ($('r-rounds')) {
    var rows = M.map(function (m) {
      var r = D.rounds[m.id], a = r.det.A, s = r.samp.A, sc = D.stability[m.id].sampling_consistency.A, c = r.samp.C;
      return el('tr', {}, [
        el('td', {}, [el('strong', { text: m.label })]),
        el('td', { class: 'num', text: a.per_round.join(' · ') }),
        el('td', { class: 'num', text: s.per_round.join(' · ') }),
        el('td', { class: 'num', text: f1(s.mean) + ' ± ' + f1(s.sd) }),
        el('td', { class: 'num', text: c.per_round.join(' · ') }),
        el('td', { class: 'num', text: sc.always + ' / ' + sc.sometimes + ' / ' + sc.never })
      ]);
    });
    $('r-rounds').appendChild(table([{ t: 'Modelo' }, { t: 'Resolución, 3 rondas con temperatura 0', cls: 'num' }, { t: 'Resolución, 3 rondas con muestreo', cls: 'num' },
      { t: 'Media ± sd (muestreo)', cls: 'num' }, { t: 'Pistas con fuga, muestreo', cls: 'num' }, { t: 'Ítems: siempre / a veces / nunca', cls: 'num' }], rows));
  }
  if ($('r-stability')) {
    var rows2 = M.map(function (m) {
      var s = D.stability[m.id];
      var b = D.rounds[m.id].samp.B;
      return el('tr', {}, [el('td', { text: m.label }), el('td', { class: 'num', text: s.identical_text + ' de ' + s.n }), el('td', { class: 'num', text: b.per_round.join(' · ') })]);
    });
    $('r-stability').appendChild(table([{ t: 'Modelo' }, { t: 'Respuestas idénticas en las 3 rondas con temperatura 0', cls: 'num' }, { t: 'Veredictos acertados, 3 rondas con muestreo', cls: 'num' }], rows2));
  }

  /* 2. Comparaciones */
  if ($('r-compare')) {
    var pairs = [['qwen3-1.7b-q4_K_M', 'qwen3-0.6b-q4_K_M'], ['qwen3-0.6b-q4_K_M', 'qwen3-0.6b-q8_0'], ['qwen3-0.6b-q4_K_M', 'qwen3-0.6b-fp16'], ['qwen3-0.6b-q8_0', 'qwen3-0.6b-fp16'],
      ['phi4-mini-3.8b-q4_K_M', 'smollm3-3b-q4_K_M'], ['phi4-mini-3.8b-q4_K_M', 'qwen3-1.7b-q4_K_M'], ['smollm3-3b-q4_K_M', 'qwen3-1.7b-q4_K_M']];
    function cell(group, code, a, b) {
      var c = D.comparisons[group + '|' + code + '|' + a + ' - ' + b];
      if (!c) return el('td', { class: 'c none', text: '—' });
      var t = sgn(c.diff_items_of_60) + (c.clear_by_plan_rule ? ' ✔' : '');
      var e = el('td', { class: 'c ' + (c.clear_by_plan_rule ? 'hi' : 'none'), text: t });
      e.title = 'IC 95 % de la tasa: ' + f1(100 * c.ci95[0]) + ' % a ' + f1(100 * c.ci95[1]) + ' %';
      return e;
    }
    var rows3 = pairs.map(function (p) {
      return el('tr', {}, [el('td', { text: label(p[0]) + ' frente a ' + label(p[1]) }), cell('det', 'A', p[0], p[1]), cell('samp', 'A', p[0], p[1]), cell('det', 'B', p[0], p[1]), cell('samp', 'B', p[0], p[1])]);
    });
    $('r-compare').appendChild(table([{ t: 'Comparación' }, { t: 'Resolución (temp. 0)', cls: 'c' }, { t: 'Resolución (muestreo)', cls: 'c' }, { t: 'Veredicto (temp. 0)', cls: 'c' }, { t: 'Veredicto (muestreo)', cls: 'c' }], rows3, 'hm'));
  }

  /* 3. Ablación */
  if ($('r-ablation')) {
    var rows4 = M.map(function (m) {
      var a = D.ablation[m.id];
      function c(v, cls) { var x = a[v]; var s = x.errors_caught + '/' + x.n_err; var e = el('td', { class: 'num ' + (cls || ''), text: s });
        if (x.format_errors > 2) e.title = x.format_errors + ' errores de formato'; return e; }
      return el('tr', {}, [el('td', { text: m.label }), c('baseline'), c('solve_first'), c('given_answer'),
        el('td', { class: 'num small', text: a.baseline.controls_accepted + ' · ' + a.solve_first.controls_accepted + ' · ' + a.given_answer.controls_accepted }),
        el('td', { class: 'num small', text: a.given_answer.verdict_and_category + '/51' })]);
    });
    $('r-ablation').appendChild(table([{ t: 'Modelo' }, { t: 'Línea base', cls: 'num' }, { t: 'Resolver primero', cls: 'num' }, { t: 'Con la respuesta dada', cls: 'num' },
      { t: 'Controles aceptados de 9 (base · resolver · dada)', cls: 'num' }, { t: 'Veredicto + categoría (dada)', cls: 'num' }], rows4));
  }

  /* 4. Brecha de verificación */
  if ($('r-gap')) {
    var rows5 = M.map(function (m) {
      var d = D.diag.by_model[m.id], g = d.error_items_with_family_solved_in_A;
      var fe = d.caught_when_false_equation_written, nf = d.caught_when_no_false_equation;
      return el('tr', {}, [el('td', { text: m.label }), el('td', { class: 'num', text: d.errors_caught.k + ' de ' + d.errors_caught.n }),
        el('td', { class: 'num', text: g.k + ' de ' + g.n }), el('td', { class: 'num', text: fe.k + '/' + fe.n + ' · ' + nf.k + '/' + nf.n })]);
    });
    $('r-gap').appendChild(table([{ t: 'Modelo' }, { t: 'Errores detectados (primera pasada)', cls: 'num' }, { t: 'Aceptó el error aunque resolvió el problema', cls: 'num' },
      { t: 'Detectados: con igualdad falsa escrita · sin ella', cls: 'num' }], rows5));
  }
  if ($('r-subtypes')) {
    var st = D.diag.by_subtype;
    var names = {
      tens_written_in_hundreds: 'Leer un número: decenas puestas en las centenas', wrong_number_of_zeros_removed: 'Dividir entre 100 o 1 000: quitar un cero de menos',
      hundreds_written_as_tens: 'Descomponer: una centena escrita como decena', digit_given_instead_of_value: 'Valor posicional: dar la cifra en vez de su valor',
      carry_not_added: 'Suma: no sumar la llevada', neutral_element_given_as_one: 'Elemento neutro de la suma dado como 1', table_recall_one_group_off: 'Tabla de multiplicar: un grupo de menos',
      remainder_not_smaller_than_divisor: 'División: residuo mayor que el divisor', last_step_omitted: 'Problema de varios pasos: omitir el último', smaller_minus_larger_digit: 'Resta: restar el dígito menor del mayor',
      denominators_added: 'Fracciones: sumar también los denominadores', wrong_number_of_zeros: 'Multiplicar por 10, 100 o 1 000: ceros de menos', added_instead_of_multiplied: 'Multiplicación hecha como suma',
      fraction_type_swapped: 'Fracción propia o impropia al revés', blank_filled_with_total: 'Propiedad conmutativa: poner el total', tens_units_swapped: 'Ordinal con decenas y unidades cambiadas',
      step_size_changed: 'Conteo por intervalos: paso cambiado', comparison_symbol_reversed: 'Comparar fracciones: símbolo al revés', multiplied_instead_of_divided: 'División hecha como multiplicación',
      added_instead_of_subtracted: 'Resta de fracciones hecha como suma', symbol_reversed_naturals: 'Comparar números: símbolo al revés'
    };
    var host = $('r-subtypes');
    Object.keys(st).forEach(function (k) {
      var v = st[k];
      var bar = el('div', { class: 'bar', role: 'img', 'aria-label': names[k] || k });
      var s = el('span', { class: 's-ok', text: v.k > 0 ? String(v.k) : '' });
      s.style.width = (100 * v.rate) + '%';
      bar.appendChild(s);
      host.appendChild(el('div', { class: 'bar-row' }, [el('div', { class: 'lab', text: (names[k] || k) + ' (' + v.k + ' de ' + v.n + ')' }), bar]));
    });
  }
})();
