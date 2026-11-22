/* Elementos compartidos: tema claro/oscuro, índice lateral, enlaces a secciones, paginación y botón para volver arriba. */
(function () {
  'use strict';
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function el(tag, props, kids) {
    var n = document.createElement(tag);
    Object.keys(props || {}).forEach(function (k) { if (k === 'text') n.textContent = props[k]; else if (k === 'class') n.className = props[k]; else n.setAttribute(k, props[k]); });
    (kids || []).forEach(function (c) { n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  /* Tema */
  var btn = $('.theme-toggle');
  function effective() {
    var t = document.documentElement.getAttribute('data-theme');
    if (t) return t;
    return window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function label() { if (btn) btn.textContent = effective() === 'dark' ? '☀ Claro' : '☾ Oscuro'; }
  if (btn) {
    label();
    btn.addEventListener('click', function () {
      var next = effective() === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next); store('theme', next); label();
    });
  }

  var main = $('main');
  if (!main) return;

  /* Identificadores y enlaces a cada sección */
  function slug(t) {
    return t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 48) || 'seccion';
  }
  var used = {};
  $$('[id]', main).forEach(function (n) { used[n.id] = true; });
  var heads = $$('h2', main).filter(function (h) { return !h.closest('.tldr') && !h.closest('.test'); });
  heads.forEach(function (h) {
    if (!h.id) { var s = slug(h.textContent), i = 2, base = s; while (used[s]) { s = base + '-' + i++; } h.id = s; used[s] = true; }
    var a = el('a', { class: 'anchor', href: '#' + h.id, 'aria-label': 'Enlace a esta sección', text: '#' }); h.appendChild(a);
  });

  /* Índice lateral */
  if (heads.length >= 4) {
    var toc = el('aside', { class: 'toc', 'aria-label': 'En esta página' }, [el('strong', { text: 'En esta página' })]);
    var links = heads.map(function (h) {
      var t = h.textContent.replace(/#$/, '');
      var a = el('a', { href: '#' + h.id, text: t }); toc.appendChild(a); return a;
    });
    main.classList.add('has-toc'); main.insertBefore(toc, main.firstChild);
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) { links.forEach(function (l) { l.classList.toggle('on', l.getAttribute('href') === '#' + e.target.id); }); }
        });
      }, { rootMargin: '-130px 0px -65% 0px' });
      heads.forEach(function (h) { io.observe(h); });
    }
  }

  /* Paginación: un recorrido sugerido por las páginas principales */
  var ORDER = [
    ['index.html', 'Inicio'], ['benchmark.html', 'Qué es el benchmark 2026'], ['resultados-2026.html', 'Resultados 2026'],
    ['rondas-2026.html', 'Rondas y ablación'], ['pruebas.html', 'Pruebas del laboratorio 2024'], ['dataset.html', 'Dataset 2024'],
    ['rubrica.html', 'Rúbrica'], ['metodologia.html', 'Metodología'], ['fuentes.html', 'Fuentes'],
    ['hoja-de-ruta.html', 'Hoja de ruta'], ['glosario.html', 'Glosario']
  ];
  var here = location.pathname.split('/').pop() || 'index.html';
  var ix = -1; ORDER.forEach(function (o, i) { if (o[0] === here) ix = i; });
  if (ix >= 0 && here !== 'index.html') {
    var pager = el('nav', { class: 'pager', 'aria-label': 'Seguir leyendo' });
    if (ix > 0) pager.appendChild(el('a', { class: 'prev', href: ORDER[ix - 1][0] }, [el('small', { text: '← Anterior' }), ORDER[ix - 1][1]]));
    if (ix < ORDER.length - 1) pager.appendChild(el('a', { class: 'next', href: ORDER[ix + 1][0] }, [el('small', { text: 'Siguiente →' }), ORDER[ix + 1][1]]));
    main.appendChild(pager);
  }

  /* Volver arriba */
  var up = el('button', { class: 'totop', type: 'button', 'aria-label': 'Volver arriba', text: '↑' });
  up.addEventListener('click', function () { window.scrollTo({ top: 0 }); });
  document.body.appendChild(up);
  window.addEventListener('scroll', function () { up.classList.toggle('show', window.scrollY > 700); }, { passive: true });
})();
