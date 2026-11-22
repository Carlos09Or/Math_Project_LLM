/* Portada: barras comparativas de las siete configuraciones, calculadas desde window.BENCH2026 (datos agregados). */
(function () {
  'use strict';
  var D = window.BENCH2026, box = document.getElementById('home-bars');
  if (!D || !box) return;
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; }
  function out(t, id, key) { return ((D.tasks[t].outcomes[id] || {})[key]) || 0; }
  var groups = [
    { title: 'Resolución: aciertos de 60 (más es mejor)', val: function (m) { return out('A', m.id, 'correct'); }, max: 60, cls: '' },
    { title: 'Diagnóstico: veredicto acertado de 60 (más es mejor)', val: function (m) { return D.verdict[m.id].err_said_incorrect + D.verdict[m.id].ctrl_said_correct; }, max: 60, cls: '' },
    { title: 'Pistas que revelan la respuesta: de 60 (menos es mejor)', val: function (m) { return out('C', m.id, 'leak'); }, max: 60, cls: 'leak' }
  ];
  var wrap = el('div', 'grid');
  groups.forEach(function (g) {
    var card = el('div', 'hbars'); card.appendChild(el('h3', '', g.title));
    D.models.forEach(function (m) {
      var v = g.val(m), row = el('div', 'row'), track = el('div', 'track'), fill = el('div', 'fill ' + g.cls);
      fill.style.width = Math.round(100 * v / g.max) + '%'; track.appendChild(fill);
      row.appendChild(el('span', 'lab', m.label)); row.appendChild(track); row.appendChild(el('span', 'v', String(v)));
      card.appendChild(row);
    });
    wrap.appendChild(card);
  });
  wrap.style.gridTemplateColumns = 'repeat(auto-fit, minmax(340px, 1fr))';
  box.appendChild(wrap);
})();
