// SPDX-License-Identifier: MIT
//
// The engine behind every interactive diagram page in tex/<slug>/html/. A page
// holds only data and calls Diagram.mount(config); everything a reader sees —
// header, link back to the PDF, theme switch, the rotatable canvas, its
// controls, the equation panel and the opening animation — is built here, so
// that every page has the same structure and behaves the same way.
//
// Shared by all topics: a change here is a change to every page at once, so it
// goes on a branch and through a PR, like tex/preamble.tex. The config format
// and the page skeleton are docs/interactive-convention.md; this file is the
// implementation, not the specification.
(() => {
'use strict';

// MathJax is the one thing not served from this repo. Pinned to an exact
// version so a release cannot change the diagrams behind our backs; this is the
// only place that names it.
const MATHJAX_URL = 'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js';
// Where the PDFs live; the header links to <slug>.pdf here, as \Assumes does.
const PDF_URL = 'https://github.com/ys-math/math-study/blob/main/pdf/';
// One theme choice for every diagram: the pages share an origin, so they share it.
const MODE_KEY = 'diagram-mode';

const CAM_D = 1000; // camera distance in sphere radii; this far away the view is effectively orthographic, like the notes
const DEFAULT_KEY = ['composite path', 'arrow it equals'];
const DEFAULT_DEF_KEY = ['structure maps', 'defined here'];

// ---------- vector + quaternion helpers ----------
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const vnorm = a => { const n = Math.hypot(...a) || 1; return a.map(c => c / n); };
const qmul = (a, b) => [
  a[0] * b[0] - a[1] * b[1] - a[2] * b[2] - a[3] * b[3],
  a[0] * b[1] + a[1] * b[0] + a[2] * b[3] - a[3] * b[2],
  a[0] * b[2] - a[1] * b[3] + a[2] * b[0] + a[3] * b[1],
  a[0] * b[3] + a[1] * b[2] - a[2] * b[1] + a[3] * b[0]];
const qnorm = q => { const n = Math.hypot(...q); return q.map(c => c / n); };
const qconj = q => [q[0], -q[1], -q[2], -q[3]];
const qaxis = (ax, ang) => { const s = Math.sin(ang / 2), n = vnorm(ax); return [Math.cos(ang / 2), n[0] * s, n[1] * s, n[2] * s]; };
function qrot(q, v) {
  const [w, x, y, z] = q;
  const tx = 2 * (y * v[2] - z * v[1]), ty = 2 * (z * v[0] - x * v[2]), tz = 2 * (x * v[1] - y * v[0]);
  return [v[0] + w * tx + (y * tz - z * ty), v[1] + w * ty + (z * tx - x * tz), v[2] + w * tz + (x * ty - y * tx)];
}
function qslerp(a, b, t) {
  let d = a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3];
  if (d < 0) { b = b.map(c => -c); d = -d; }
  if (d > 0.9995) return qnorm(a.map((c, i) => c + (b[i] - c) * t));
  const th = Math.acos(d), s = Math.sin(th);
  return a.map((c, i) => c * Math.sin((1 - t) * th) / s + b[i] * Math.sin(t * th) / s);
}
function qfromRows(r1, r2, r3) {
  const [m00, m01, m02] = r1, [m10, m11, m12] = r2, [m20, m21, m22] = r3;
  const tr = m00 + m11 + m22; let w, x, y, z;
  if (tr > 0) { const s = Math.sqrt(tr + 1) * 2; w = s / 4; x = (m21 - m12) / s; y = (m02 - m20) / s; z = (m10 - m01) / s; }
  else if (m00 > m11 && m00 > m22) { const s = Math.sqrt(1 + m00 - m11 - m22) * 2; w = (m21 - m12) / s; x = s / 4; y = (m01 + m10) / s; z = (m02 + m20) / s; }
  else if (m11 > m22) { const s = Math.sqrt(1 + m11 - m00 - m22) * 2; w = (m02 - m20) / s; x = (m01 + m10) / s; y = s / 4; z = (m12 + m21) / s; }
  else { const s = Math.sqrt(1 + m22 - m00 - m11) * 2; w = (m10 - m01) / s; x = (m02 + m20) / s; y = (m12 + m21) / s; z = s / 4; }
  return qnorm([w, x, y, z]);
}
const deg = Math.PI / 180;
// a list of { axis, deg } rotations, composed left to right
const rotation = steps => qnorm(steps.reduce((q, r) => qmul(q, qaxis(r.axis, r.deg * deg)), [1, 0, 0, 0]));

// ---------- DOM ----------
function el(tag, attrs = {}, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') e.className = v;
    else if (k === 'text') e.textContent = v;
    else e.setAttribute(k, v);
  }
  e.append(...kids);
  return e;
}
// text with $...$ pieces: the pieces become MathJax spans (typeset later, TeX source as fallback)
function mathText(str) {
  const frag = document.createDocumentFragment();
  str.split('$').forEach((part, k) => {
    if (!part) return;
    if (k % 2) frag.append(el('span', { class: 'tm', 'data-tex': part, text: part }));
    else frag.append(part);
  });
  return frag;
}
// the topic slug, read off the page's own path: .../<slug>/html/<name>.html
function topicSlug() {
  const parts = location.pathname.split('/');
  const i = parts.lastIndexOf('html');
  return i > 0 ? decodeURIComponent(parts[i - 1]) : null;
}

function buildPage(cfg) {
  const slug = topicSlug();
  const source = el('p', { class: 'source' }, 'From the notes: ');
  if (slug) source.append(el('a', { href: `${PDF_URL}${slug}.pdf`, target: '_blank', rel: 'noopener', text: `${slug}.pdf` }));
  const modes = el('div', { class: 'theme-switch', role: 'group', 'aria-label': 'Colour theme' },
    ...['auto', 'light', 'dark'].map(m => el('button', { type: 'button', class: 'plainbtn', 'data-mode': m, 'aria-pressed': 'false', text: m[0].toUpperCase() + m.slice(1) })));
  const header = el('header', {}, el('h1', { text: cfg.title }), source, modes);

  const canvas = el('canvas', { id: 'view', tabindex: '0', role: 'img',
    'aria-label': `${cfg.description} Drag, or focus and use the arrow keys, to turn it. Press R to reset.` });
  const btn = (id, label, pressed) => el('button', { class: 'plainbtn', id, type: 'button', ...(pressed == null ? {} : { 'aria-pressed': String(pressed) }), text: label });
  const controls = el('div', { class: 'controls' },
    el('p', { class: 'hint', text: 'Drag to turn · double-click to reset' }),
    el('div', { class: 'row' }, btn('btn-reset', 'Reset view'), btn('btn-spin', 'Spin', false), btn('btn-depth', 'Depth shading', true)));
  const square = el('div', { class: 'square', id: 'square' }, canvas, controls);
  const stage = el('section', { class: 'stage', id: 'stage', 'aria-label': '3D diagram' }, square);

  const key = el('div', { class: 'key' },
    el('span', { class: 'k-path' }, el('i'), el('span', { id: 'key-path', text: DEFAULT_KEY[0] })),
    el('span', { class: 'k-direct' }, el('i'), el('span', { id: 'key-direct', text: DEFAULT_KEY[1] })));
  const inner = el('div', { class: 'panel-inner' }, key);
  const tablist = el('div', { class: 'tabs', role: 'tablist', 'aria-label': 'Equation list' });
  const panels = cfg.tabs.map((t, i) => {
    const panel = el('div', { class: t.definitions ? 'groups defs' : 'groups', id: `panel-${i}`, role: 'tabpanel', 'aria-labelledby': `tab-${i}` });
    if (i) panel.hidden = true;
    inner.append(panel);
    tablist.append(el('button', { class: 'plainbtn', type: 'button', role: 'tab', id: `tab-${i}`, 'aria-selected': String(!i), 'aria-controls': `panel-${i}`, text: t.label }));
    return panel;
  });
  const panel = el('aside', { class: 'panel', 'aria-label': 'Equations' }, el('div', { class: 'panel-scroll' }, inner));
  if (cfg.tabs.length > 1) panel.append(tablist);

  document.body.prepend(el('div', { class: 'app' }, header, el('div', { class: 'layout' }, stage, panel)));
  return { canvas, stage, square, panels, tablist, modes };
}

// ---------- mount ----------
function mount(cfg) {
const VERT = {}, NODE_TEX = {}, NODE_PLAIN = {};
for (const [k, o] of Object.entries(cfg.objects)) { VERT[k] = o.at; NODE_TEX[k] = o.tex; NODE_PLAIN[k] = o.plain; }
const EDGES = cfg.arrows.map(a => ({ id: a.id, s: a.from, t: a.to, tex: a.tex, plain: a.plain, straight: !!a.straight, lt: a.labelAt }));

// every highlightable entry, in panel order; a face's index here is its identity
const FACES = [];
cfg.tabs.forEach((t, ti) => {
  for (const g of t.groups || []) for (const f of g.faces) FACES.push({ ...f, tab: ti, group: g });
  for (const d of t.definitions || []) FACES.push({ ...d, tab: ti, def: true, look: d.look || 'none', key: d.key || t.key || DEFAULT_DEF_KEY, plain: d.sym });
});
for (const f of FACES) { f.direct = [].concat(f.direct || []); f.legs = f.legs || []; f.path = f.path || []; }

const dom = buildPage(cfg);

// ---------- geometry samples ----------
const NS = 96;
function along(e, u) {
  const p = VERT[e.s], q = VERT[e.t];
  if (e.straight) return p.map((c, i) => c + (q[i] - c) * u);
  const om = Math.acos(Math.max(-1, Math.min(1, dot(p, q))));
  const a = Math.sin((1 - u) * om) / Math.sin(om), b = Math.sin(u * om) / Math.sin(om);
  return p.map((c, i) => a * c + b * q[i]);
}
for (const e of EDGES) {
  e.pts3 = Array.from({ length: NS + 1 }, (_, i) => along(e, i / NS));
  e.lab3 = along(e, e.lt ?? 0.5);
}

// trim a projected polyline where it enters the source/target boxes
function trimPolyline(P, inS, inT) {
  let i0 = 0; while (i0 < P.length && inS(P[i0])) i0++;
  let i1 = P.length - 1; while (i1 >= 0 && inT(P[i1])) i1--;
  if (i1 - i0 < 2) return null;
  const cut = (a, b, inside) => { // a inside, b outside
    let lo = a, hi = b;
    for (let k = 0; k < 12; k++) {
      const m = { x: (lo.x + hi.x) / 2, y: (lo.y + hi.y) / 2, z: (lo.z + hi.z) / 2 };
      if (inside(m)) lo = m; else hi = m;
    }
    return hi;
  };
  const out = P.slice(i0, i1 + 1);
  if (i0 > 0) out.unshift(cut(P[i0 - 1], P[i0], inS));
  if (i1 < P.length - 1) out.push(cut(P[i1 + 1], P[i1], inT));
  return out;
}

// ---------- state ----------
const HOME = rotation(cfg.home || []);
let q = HOME.slice();
let anim = null, inertia = null, spinning = false, shading = true;
let hoverFace = null, pinnedFace = null;
let need = true;
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');

const canvas = dom.canvas;
const ctx = canvas.getContext('2d');
let W = 600, dpr = 1, S = 200, cx = 300, cy = 300;
const D = CAM_D;

const stage = dom.stage, square = dom.square;
const stacked = matchMedia('(max-width: 900px), (max-height: 560px)');
function resize() {
  // the square is as large as the stage allows; stacked (phones) it follows the width only
  const size = Math.floor(stacked.matches ? Math.min(stage.clientWidth, 640) : Math.min(stage.clientWidth, stage.clientHeight)) || 600;
  if (size === W && dpr === (window.devicePixelRatio || 1)) return;
  W = size; dpr = window.devicePixelRatio || 1;
  square.style.width = canvas.style.width = W + 'px';
  square.style.height = canvas.style.height = W + 'px';
  canvas.width = Math.round(W * dpr); canvas.height = Math.round(W * dpr);
  S = W * (stacked.matches ? 0.38 : 0.42); cx = cy = W / 2; need = true;
}
W = 0;
new ResizeObserver(resize).observe(stage);
stacked.addEventListener('change', resize);

let col = {};
function readColors() {
  const cs = getComputedStyle(document.documentElement);
  const g = n => cs.getPropertyValue(n).trim();
  col = { bg: g('--bg'), ink: g('--ink'), path: g('--path'), direct: g('--direct') };
  need = true;
}
readColors();
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', readColors);
new MutationObserver(readColors).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'data-mode'] });

// Light / Dark / Auto switch (remembered in this browser when storage is available)
const modeBtns = [...dom.modes.querySelectorAll('button')];
function setMode(mode) {
  if (mode === 'light' || mode === 'dark') document.documentElement.setAttribute('data-mode', mode);
  else { mode = 'auto'; document.documentElement.removeAttribute('data-mode'); }
  modeBtns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.mode === mode)));
  try { localStorage.setItem(MODE_KEY, mode); } catch (err) { /* storage unavailable */ }
}
modeBtns.forEach(b => b.addEventListener('click', () => setMode(b.dataset.mode)));
try { setMode(localStorage.getItem(MODE_KEY) || 'auto'); } catch (err) { setMode('auto'); }

// ---------- typeset labels (MathJax SVG -> image -> tinted canvas) ----------
const texCache = new Map();
const RF = 40; // raster pixels per ex
async function texImage(tex) {
  const node = MathJax.tex2svg(tex, { display: false });
  const svg = node.querySelector('svg');
  const wEx = parseFloat(svg.getAttribute('width')), hEx = parseFloat(svg.getAttribute('height'));
  svg.setAttribute('width', (wEx * RF).toFixed(1));
  svg.setAttribute('height', (hEx * RF).toFixed(1));
  svg.removeAttribute('style');
  let s = new XMLSerializer().serializeToString(svg).replace(/currentColor/g, '#000');
  if (!/xmlns="http:\/\/www\.w3\.org\/2000\/svg"/.test(s)) s = s.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
  const img = new Image();
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(s);
  await img.decode();
  const L = { img, wEx, hEx, tints: new Map(), interior: null, interiorTints: new Map() };
  if (tex.includes('pmatrix')) { try { L.interior = matrixInterior(L); } catch (err) { /* fall back to outline only */ } }
  return L;
}
// For a matrix, a mask of the region between its two parentheses, row by row,
// so the background can hug the outside of the brackets and fill everything inside them.
function matrixInterior(L) {
  const w = Math.max(1, Math.round(L.wEx * RF)), h = Math.max(1, Math.round(L.hEx * RF));
  const src = document.createElement('canvas'); src.width = w; src.height = h;
  const sx = src.getContext('2d'); sx.drawImage(L.img, 0, 0, w, h);
  const a = sx.getImageData(0, 0, w, h).data;
  const on = (x, y) => a[(y * w + x) * 4 + 3] > 40;
  const out = document.createElement('canvas'); out.width = w; out.height = h;
  const ox = out.getContext('2d'); ox.fillStyle = '#000';
  for (let y = 0; y < h; y++) {
    let l = 0; while (l < w && !on(l, y)) l++;
    if (l >= w * 0.25) continue;                 // no left bracket on this row
    while (l < w && on(l, y)) l++;               // step over the bracket's stroke
    let r = w - 1; while (r >= 0 && !on(r, y)) r--;
    if (r <= w * 0.75) continue;                 // no right bracket on this row
    while (r >= 0 && on(r, y)) r--;
    if (r > l) ox.fillRect(l, y, r - l + 1, 1);
  }
  return out;
}
function tintedInterior(L, color) {
  let c = L.interiorTints.get(color);
  if (!c) {
    c = document.createElement('canvas'); c.width = L.interior.width; c.height = L.interior.height;
    const x = c.getContext('2d');
    x.drawImage(L.interior, 0, 0);
    x.globalCompositeOperation = 'source-in';
    x.fillStyle = color; x.fillRect(0, 0, c.width, c.height);
    L.interiorTints.set(color, c);
  }
  return c;
}
function tinted(L, color) {
  let c = L.tints.get(color);
  if (!c) {
    c = document.createElement('canvas');
    c.width = Math.max(1, Math.round(L.wEx * RF)); c.height = Math.max(1, Math.round(L.hEx * RF));
    const x = c.getContext('2d');
    x.drawImage(L.img, 0, 0, c.width, c.height);
    x.globalCompositeOperation = 'source-in';
    x.fillStyle = color; x.fillRect(0, 0, c.width, c.height);
    L.tints.set(color, c);
  }
  return c;
}
const LABEL_FONT = '"CM Roman", "Latin Modern Roman", Georgia, serif';
function labelSize(tex, plain, ex) {
  const L = texCache.get(tex);
  if (L) return [L.wEx * ex, L.hEx * ex];
  ctx.font = `italic ${(ex * 2.15).toFixed(1)}px ${LABEL_FONT}`;
  return [ctx.measureText(plain).width, ex * 2.6];
}
function drawLabel(tex, plain, x, y, ex, color, alpha, withBg) {
  const [w, h] = labelSize(tex, plain, ex);
  const L = texCache.get(tex);
  if (withBg && tex.includes('pmatrix') && !(L && L.interior)) {
    // matrix without a usable bracket mask: ordinary rectangular background
    ctx.globalAlpha = 1; ctx.fillStyle = col.bg;
    const p = Math.max(2, ex * 0.35);
    roundRect(x - w / 2 - p, y - h / 2 - p, w + 2 * p, h + 2 * p, 4); ctx.fill();
  } else if (withBg) {
    // background that follows the glyph outlines: the label stamped in the background colour
    // around a small circle, which widens every stroke by r on all sides
    ctx.globalAlpha = 1;
    const r = Math.max(2.2, ex * 0.42), steps = 16;
    if (L) {
      const halo = tinted(L, col.bg);
      for (let k = 0; k < steps; k++) {
        const a = 2 * Math.PI * k / steps;
        ctx.drawImage(halo, x - w / 2 + r * Math.cos(a), y - h / 2 + r * Math.sin(a), w, h);
      }
      ctx.drawImage(halo, x - w / 2, y - h / 2, w, h);
      // matrices: the whole inside of the brackets is filled as well
      if (L.interior) ctx.drawImage(tintedInterior(L, col.bg), x - w / 2, y - h / 2, w, h);
    } else {
      ctx.font = `italic ${(ex * 2.15).toFixed(1)}px ${LABEL_FONT}`;
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.strokeStyle = col.bg; ctx.lineWidth = 2 * r; ctx.lineJoin = 'round';
      ctx.strokeText(plain, x, y);
    }
  }
  ctx.globalAlpha = alpha;
  if (L) ctx.drawImage(tinted(L, color), x - w / 2, y - h / 2, w, h);
  else {
    ctx.fillStyle = color; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.font = `italic ${(ex * 2.15).toFixed(1)}px ${LABEL_FONT}`;
    ctx.fillText(plain, x, y);
  }
  ctx.globalAlpha = 1;
}
// add a polyline to the current path, leaving out the part inside rectangle R = [x0, y0, x1, y1]
function pathOutside(c, R) {
  let pen = false;
  for (let i = 0; i < c.length - 1; i++) {
    const p = c[i], q = c[i + 1];
    const ins = clipInside(p, q, R);
    if (!ins) { if (!pen) { ctx.moveTo(p.x, p.y); pen = true; } ctx.lineTo(q.x, q.y); continue; }
    const [a, b] = ins, at = t => [p.x + (q.x - p.x) * t, p.y + (q.y - p.y) * t];
    if (a > 0) { if (!pen) ctx.moveTo(p.x, p.y); ctx.lineTo(...at(a)); }
    pen = false;
    if (b < 1) { ctx.moveTo(...at(b)); ctx.lineTo(q.x, q.y); pen = true; }
  }
}
// Liang–Barsky: the parameter interval of segment p→q that lies inside R, or null
function clipInside(p, q, R) {
  let t0 = 0, t1 = 1;
  const dx = q.x - p.x, dy = q.y - p.y;
  const P = [-dx, dx, -dy, dy], Q = [p.x - R[0], R[2] - p.x, p.y - R[1], R[3] - p.y];
  for (let i = 0; i < 4; i++) {
    if (P[i] === 0) { if (Q[i] < 0) return null; continue; }
    const t = Q[i] / P[i];
    if (P[i] < 0) { if (t > t1) return null; if (t > t0) t0 = t; }
    else { if (t < t0) return null; if (t < t1) t1 = t; }
  }
  return t0 < t1 ? [t0, t1] : null;
}
function roundRect(x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}

// ---------- render ----------
function proj(v) {
  const p = qrot(q, v), s = D / (D - p[2]);
  return { x: cx + p[0] * S * s, y: cy - p[1] * S * s, z: p[2], s };
}
const depthAlpha = z => shading ? 0.36 + 0.64 * (z + 1) / 2 : 1;

// ---------- opening animation ----------
// The diagram assembles itself: the objects appear, then the arrows draw themselves along their great
// circles in the order the page gives (cfg.intro, or the order of objects and arrows), while the sphere
// swings round into place. A straight arrow is a chord through the middle, and draws a little slower.
const INTRO = (() => {
  const node = {}, edge = {};
  const given = cfg.intro || {};
  let t = 0;
  for (const k in VERT) { node[k] = given.objects?.[k] ?? t; t = node[k] + 90; }
  t += 20;
  for (const e of EDGES) { edge[e.id] = given.arrows?.[e.id] ?? t; t = edge[e.id] + 80; }
  const nodeDur = 450, edgeDur = 600, labelDur = 320, rotDur = 2900;
  const done = Math.max(...EDGES.map(e => edge[e.id] + edgeDur * 0.75 + labelDur), ...Object.values(node).map(s => s + nodeDur));
  return { node, edge, nodeDur, edgeDur, labelDur, rotDur, end: Math.max(rotDur, done) + 100 };
})();
let intro = null;                        // { t0, q0 } while running
let introPending = !reduceMotion.matches; // canvas waits (blank) until the labels are typeset
const clamp01 = u => Math.max(0, Math.min(1, u));
const easeOut = u => 1 - Math.pow(1 - u, 3);
const easeInOut = u => u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
function introT() { return intro ? performance.now() - intro.t0 : Infinity; }
const STRAIGHT = new Set(EDGES.filter(e => e.straight).map(e => e.id));
const nodeIn = (k, T) => easeOut(clamp01((T - INTRO.node[k]) / INTRO.nodeDur));
const edgeIn = (id, T) => easeInOut(clamp01((T - INTRO.edge[id]) / (STRAIGHT.has(id) ? INTRO.edgeDur * 1.15 : INTRO.edgeDur)));
const labelIn = (id, T) => clamp01((T - INTRO.edge[id] - INTRO.edgeDur * 0.75) / INTRO.labelDur);
if (introPending) document.documentElement.classList.add('intro');
function startIntro() {
  if (!introPending) return;
  introPending = false;
  // start a quarter turn away, tipped slightly, and swing into the home view
  intro = { t0: performance.now(), q0: qnorm(qmul(qaxis([1, 0, 0], 0.32), qmul(HOME, qaxis([0, 1, 0], -1.7)))) };
  q = intro.q0.slice();
  const root = document.documentElement;
  root.classList.add('intro-go'); root.classList.remove('intro');
  need = true;
}
function finishIntro() {
  introPending = false;
  if (intro) { intro = null; need = true; }
  document.documentElement.classList.remove('intro', 'intro-go');
}
setTimeout(startIntro, 2500);            // if MathJax is slow or unavailable, start with plain labels
setTimeout(finishIntro, 9000);           // never leave the page half-revealed
// a polyline cut to the first fraction f of its length
function truncate(pts, f) {
  if (f >= 1) return pts;
  const d = [0];
  for (let i = 1; i < pts.length; i++) d.push(d[i - 1] + Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y));
  const target = f * d[d.length - 1];
  let i = 1; while (i < d.length - 1 && d[i] < target) i++;
  const u = (target - d[i - 1]) / ((d[i] - d[i - 1]) || 1), a = pts[i - 1], b = pts[i];
  return pts.slice(0, i).concat([{ x: a.x + (b.x - a.x) * u, y: a.y + (b.y - a.y) * u, z: a.z + (b.z - a.z) * u }]);
}

function render() {
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.globalAlpha = 1; ctx.fillStyle = col.bg; ctx.fillRect(0, 0, W, W);
  ctx.imageSmoothingQuality = 'high';
  if (introPending) return;
  const T = introT();
  const exN = Math.min(9.6, Math.max(7, S * 0.036));
  const exE = Math.min(7.0, Math.max(5.2, S * 0.026));
  const lw = Math.min(1.7, Math.max(1.1, S / 190));
  const face = pinnedFace ?? hoverFace;
  const F = face == null ? null : FACES[face];
  updateKey(F);

  const nodeP = {}, box = {};
  for (const k in VERT) {
    const p = proj(VERT[k]); nodeP[k] = p;
    const [w, h] = labelSize(NODE_TEX[k], NODE_PLAIN[k], exN * p.s);
    box[k] = { x: p.x, y: p.y, hw: w / 2 + 6, hh: h / 2 + 5 };
  }
  const inBox = k => pt => Math.abs(pt.x - box[k].x) < box[k].hw && Math.abs(pt.y - box[k].y) < box[k].hh;
  // no halo is drawn this close to any object, so a halo can never erase an arrow tip arriving there
  const nearNode = pt => {
    for (const k in box) if (Math.abs(pt.x - box[k].x) < box[k].hw + 14 && Math.abs(pt.y - box[k].y) < box[k].hh + 14) return true;
    return false;
  };

  const items = [];
  for (const e of EDGES) {
    let role = 'plain';
    if (F) role = F.path.includes(e.id) ? 'path' : F.direct.includes(e.id) ? 'direct' : F.legs.includes(e.id) ? 'leg' : (F.keep || []).includes(e.id) ? 'plain' : 'dim';
    const grow = edgeIn(e.id, T);
    if (grow <= 0) continue;
    let pts = trimPolyline(e.pts3.map(proj), inBox(e.s), inBox(e.t));
    if (pts && grow < 1) { pts = truncate(pts, grow); if (pts.length < 2) pts = null; }
    const lp = proj(e.lab3);
    const [lw2, lh2] = labelSize(e.tex, e.plain, exE * lp.s);
    const reach = Math.hypot(lw2, lh2) / 2 + 6;
    // the arrow breaks where its own label sits, so the label needs no box behind it
    const ownGap = [lp.x - lw2 / 2 - 3, lp.y - lh2 / 2 - 2, lp.x + lw2 / 2 + 3, lp.y + lh2 / 2 + 2];
    let labZ = lp.z;
    if (pts) {
      for (const p of pts) p.nn = nearNode(p);
      const CH = 8, n = pts.length - 1;
      for (let a = 0; a < n; ) {
        let b = a + CH; if (b >= n - CH / 2) b = n; // no stub chunk at the end
        const chunk = pts.slice(a, b + 1);
        const z = chunk.reduce((s, p) => s + p.z, 0) / chunk.length;
        items.push({ kind: 'seg', z, chunk, role, gap: ownGap });
        if (chunk.some(p => Math.hypot(p.x - lp.x, p.y - lp.y) < reach)) labZ = Math.max(labZ, z);
        a = b;
      }
      // tips sit in depth order; halos never reach them, and any label overlapping a tip is lifted above it below
      const t = pts[n];
      items.push({ kind: 'tip', z: t.z + 0.004, all: pts, role, rect: [t.x - 11, t.y - 11, t.x + 11, t.y + 11] });
    }
    items.push({ kind: 'elab', z: labZ + 0.002, p: lp, e, role, fade: labelIn(e.id, T), rect: [lp.x - lw2 / 2 - 3, lp.y - lh2 / 2 - 3, lp.x + lw2 / 2 + 3, lp.y + lh2 / 2 + 3] });
  }
  for (const k in VERT) {
    const on = !F || F.objects.includes(k);
    const b = box[k];
    items.push({ kind: 'node', z: nodeP[k].z + 0.05, p: nodeP[k], k, on, fade: nodeIn(k, T), rect: [b.x - b.hw + 3, b.y - b.hh + 3, b.x + b.hw - 3, b.y + b.hh - 3] });
  }
  liftLabelsOverTips(items);
  items.sort((a, b) => a.z - b.z);

  for (const it of items) {
    const base = depthAlpha(it.z);
    if (it.kind === 'seg' || it.kind === 'tip') {
      const color = it.role === 'path' ? col.path : it.role === 'direct' ? col.direct : col.ink;
      const alpha = it.role === 'dim' ? base * 0.28 : (it.role === 'plain' ? base : Math.max(base, 0.75));
      const width = (it.role === 'path' || it.role === 'direct' || it.role === 'leg') ? lw * 1.7 : lw;
      ctx.lineWidth = width; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      if (it.kind === 'seg') {
        const c = it.chunk;
        // halo: only along the stretches that stay clear of every object, and not under the arrow's own label
        ctx.globalAlpha = 1; ctx.strokeStyle = col.bg; ctx.lineWidth = width + 6; ctx.lineCap = 'butt';
        ctx.beginPath();
        let run = [];
        for (let i = 0; i <= c.length; i++) {
          if (i === c.length || c[i].nn) { if (run.length > 1) pathOutside(run, it.gap); run = []; }
          else run.push(c[i]);
        }
        ctx.stroke();
        ctx.globalAlpha = alpha; ctx.strokeStyle = color; ctx.lineWidth = width; ctx.lineCap = 'round';
        ctx.beginPath(); pathOutside(c, it.gap); ctx.stroke();
      } else {
        ctx.globalAlpha = alpha; ctx.strokeStyle = color;
        const all = it.all, tip = all[all.length - 1];
        let j = all.length - 2; while (j > 0 && Math.hypot(tip.x - all[j].x, tip.y - all[j].y) < 7) j--;
        const ang = Math.atan2(tip.y - all[j].y, tip.x - all[j].x);
        const h = 4.2 + width * 3;
        ctx.beginPath();
        for (const sd of [-1, 1]) {
          const wx = tip.x - h * Math.cos(ang + sd * 0.62), wy = tip.y - h * Math.sin(ang + sd * 0.62);
          const kx = tip.x - h * 0.5 * Math.cos(ang + sd * 0.2), ky = tip.y - h * 0.5 * Math.sin(ang + sd * 0.2);
          ctx.moveTo(wx, wy); ctx.quadraticCurveTo(kx, ky, tip.x, tip.y);
        }
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    } else if (it.kind === 'elab') {
      const color = it.role === 'path' ? col.path : it.role === 'direct' ? col.direct : col.ink;
      const alpha = it.role === 'dim' ? base * 0.3 : (it.role === 'plain' ? base : 1);
      if (it.fade > 0) drawLabel(it.e.tex, it.e.plain, it.p.x, it.p.y, exE * it.p.s, color, alpha * it.fade, true);
    } else {
      if (it.fade > 0) drawLabel(NODE_TEX[it.k], NODE_PLAIN[it.k], it.p.x, it.p.y, exN * it.p.s * (0.82 + 0.18 * it.fade), col.ink, (it.on ? Math.max(base, 0.55) : base * 0.35) * it.fade, true);
    }
  }
}

// ---------- animation loop ----------
let last = performance.now();
function tick(t) {
  const dt = Math.min(50, t - last); last = t;
  if (intro) {
    const T = introT();
    q = qslerp(intro.q0, HOME, easeOut(clamp01(T / INTRO.rotDur)));
    need = true;
    if (T >= INTRO.end) finishIntro();
  } else if (anim) {
    const u = Math.min(1, (t - anim.t0) / anim.dur);
    const e = u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
    q = qslerp(anim.from, anim.to, e); need = true;
    if (u >= 1) anim = null;
  } else if (inertia) {
    q = qnorm(qmul(qaxis(inertia.axis, inertia.w * dt), q)); need = true;
    inertia.w *= Math.exp(-dt / 380);
    if (Math.abs(inertia.w) < 0.00004) inertia = null;
  } else if (spinning && !drag) {
    q = qnorm(qmul(q, qaxis([0, 1, 0], 0.00035 * dt))); need = true;
  }
  if (need) { render(); need = false; }
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);

function goTo(target) {
  if (intro) finishIntro();
  inertia = null;
  if (reduceMotion.matches) { q = target; need = true; return; }
  anim = { from: q.slice(), to: target, t0: performance.now(), dur: 750 };
}

// ---------- pointer + keyboard ----------
let drag = null;
canvas.addEventListener('pointerdown', ev => {
  finishIntro();
  canvas.setPointerCapture(ev.pointerId); canvas.classList.add('dragging');
  drag = { x: ev.clientX, y: ev.clientY, t: performance.now(), axis: [0, 1, 0], w: 0 };
  anim = null; inertia = null;
});
canvas.addEventListener('pointermove', ev => {
  if (!drag) return;
  const dx = ev.clientX - drag.x, dy = ev.clientY - drag.y;
  const d = Math.hypot(dx, dy); if (d === 0) return;
  const now = performance.now(), ang = d * 0.0085;
  const axis = [dy, dx, 0];
  q = qnorm(qmul(qaxis(axis, ang), q));
  const dtt = Math.max(1, now - drag.t);
  drag = { x: ev.clientX, y: ev.clientY, t: now, axis, w: ang / dtt };
  need = true;
});
function endDrag() {
  if (!drag) return;
  canvas.classList.remove('dragging');
  if (!reduceMotion.matches && performance.now() - drag.t < 80 && drag.w > 0.0003) inertia = { axis: drag.axis, w: Math.min(drag.w, 0.02) };
  drag = null;
}
canvas.addEventListener('pointerup', endDrag);
canvas.addEventListener('pointercancel', endDrag);
canvas.addEventListener('dblclick', () => goTo(HOME));
canvas.addEventListener('keydown', ev => {
  finishIntro();
  const step = 8 * deg; let axis = null, a = 0;
  if (ev.key === 'ArrowLeft') { axis = [0, 1, 0]; a = -step; }
  else if (ev.key === 'ArrowRight') { axis = [0, 1, 0]; a = step; }
  else if (ev.key === 'ArrowUp') { axis = [1, 0, 0]; a = -step; }
  else if (ev.key === 'ArrowDown') { axis = [1, 0, 0]; a = step; }
  else if (ev.key === 'r' || ev.key === 'R') { goTo(HOME); ev.preventDefault(); return; }
  else if (ev.key === 'Escape') { setPinned(null); return; }
  if (axis) { ev.preventDefault(); anim = null; inertia = null; q = qnorm(qmul(qaxis(axis, a), q)); need = true; }
});

// ---------- toolbar ----------
const spinBtn = document.getElementById('btn-spin');
const depthBtn = document.getElementById('btn-depth');
document.getElementById('btn-reset').addEventListener('click', () => goTo(HOME));
spinBtn.addEventListener('click', () => { spinning = !spinning; spinBtn.setAttribute('aria-pressed', String(spinning)); });
depthBtn.addEventListener('click', () => { shading = !shading; depthBtn.setAttribute('aria-pressed', String(shading)); need = true; });

// ---------- equation panel (one tab per cfg.tabs entry) ----------
const faceBtns = [];
function faceButton(f, i) {
  const b = el('button', { type: 'button', class: 'face', id: 'face-' + i, 'aria-pressed': 'false', 'aria-label': f.plain });
  b.append(el('span', { class: 'plain', 'data-tex': f.tex, text: f.plain }));
  b.addEventListener('mouseenter', () => { hoverFace = i; need = true; });
  b.addEventListener('mouseleave', () => { hoverFace = null; need = true; });
  b.addEventListener('focus', () => { hoverFace = i; need = true; });
  b.addEventListener('blur', () => { hoverFace = null; need = true; });
  b.addEventListener('click', () => {
    if (pinnedFace === i) { setPinned(null); return; }
    setPinned(i);
    const view = faceView(f);
    if (view) goTo(view);
  });
  faceBtns[i] = b;
  return b;
}
cfg.tabs.forEach((t, ti) => {
  const panel = dom.panels[ti];
  (t.groups || []).forEach((g, gi) => {
    const h = el('h3', {}, mathText(g.title));
    if (g.note) h.append(el('span', { class: 'k-note' }, mathText(g.note)));
    const list = el('div', { class: 'face-list' });
    FACES.forEach((f, i) => { if (f.group === g) list.append(faceButton(f, i)); });
    const wrap = el('div', { class: 'group' }, h, list);
    wrap.style.animationDelay = `${(1.35 + 0.15 * gi).toFixed(2)}s`; // the groups rise one after another
    panel.append(wrap);
  });
  if (t.definitions) {
    if (t.intro) panel.append(el('p', { class: 'def-intro' }, mathText(t.intro)));
    FACES.forEach((f, i) => {
      if (f.tab !== ti || !f.def) return;
      const b = faceButton(f, i);
      b.classList.add('def'); b.removeAttribute('aria-label');
      b.replaceChildren(
        el('span', { class: 'def-sym' }, el('span', { class: 'tm', 'data-tex': f.sym, text: f.sym })),
        el('span', { class: 'def-text' }, mathText(f.text)));
      panel.append(b);
    });
  }
});
const tabBtns = [...dom.tablist.children];
function showTab(which) {
  dom.panels.forEach((p, i) => { p.hidden = i !== which; tabBtns[i].setAttribute('aria-selected', String(i === which)); });
}
tabBtns.forEach((b, i) => b.addEventListener('click', () => showTab(i)));
// the key names what the two colours mean for whatever is highlighted
let keyState = '';
function updateKey(F) {
  const k = F && F.key ? F.key : (F && cfg.tabs[F.tab].key) || DEFAULT_KEY;
  const st = k.join('|'); if (st === keyState) return; keyState = st;
  document.getElementById('key-path').textContent = k[0];
  document.getElementById('key-direct').textContent = k[1];
}
function setPinned(i) {
  pinnedFace = i;
  faceBtns.forEach((b, j) => b.setAttribute('aria-pressed', String(j === i)));
  need = true;
}
// Where a highlighted face is seen from. `view` is a fixed direction; `look` is
// 'outside' (default: from beyond the centroid of its first three objects, for a face on the sphere),
// 'plane' (square-on to the plane through its first three objects, nudged by `tilt`, for a triangle
// through the middle) or 'none' (leave the view alone).
function faceView(f) {
  if (f.look === 'none') return null;
  const vs = f.objects.map(k => VERT[k]);
  const c = vnorm([0, 1, 2].map(i => vs[0][i] + vs[1][i] + vs[2][i]));
  let fwd;
  if (f.view) fwd = vnorm(f.view);
  else if (f.look === 'plane') {
    let n = vnorm(cross(vs[1].map((x, i) => x - vs[0][i]), vs[2].map((x, i) => x - vs[0][i])));
    if (dot(n, qrot(qconj(q), [0, 0, 1])) < 0) n = n.map(x => -x);
    const tilt = f.tilt || [0, 0, 0];
    fwd = vnorm(n.map((x, i) => x + 0.34 * c[i] + tilt[i]));
  } else fwd = c;
  let up = f.up || [0, 1, 0];
  if (Math.abs(dot(fwd, up)) > 0.9) up = qrot(qconj(q), [0, 1, 0]);
  const r2 = vnorm(up.map((x, i) => x - dot(up, fwd) * fwd[i]));
  const r1 = cross(r2, fwd);
  return qfromRows(r1, r2, fwd);
}

// labels always win over arrowheads: any label whose box meets a tip is drawn after that tip
function liftLabelsOverTips(items) {
  const tips = items.filter(i => i.kind === 'tip');
  const meets = (a, b) => a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3];
  for (const it of items) {
    if (it.kind === 'tip' || !it.rect) continue;
    for (const t of tips) if (meets(it.rect, t.rect) && it.z <= t.z) it.z = t.z + 0.001;
  }
}

// ---------- MathJax ----------
async function onMathReady() {
  try { document.head.appendChild(MathJax.svgStylesheet()); } catch (err) { /* older MathJax */ }
  try {
    const all = new Set([...Object.values(NODE_TEX), ...EDGES.map(e => e.tex)]);
    await Promise.all([...all].map(async t => { texCache.set(t, await texImage(t)); }));
  } catch (err) { texCache.clear(); }
  for (const node of document.querySelectorAll('.face .plain[data-tex], .tm[data-tex]')) {
    try { node.replaceWith(MathJax.tex2svg(node.dataset.tex, { display: false })); } catch (err) { /* keep the plain text */ }
  }
  need = true;
  startIntro();
}
window.MathJax = {
  svg: { fontCache: 'none' },
  options: { enableAssistiveMml: false },
  startup: {
    typeset: false,
    ready() {
      MathJax.startup.defaultReady();
      MathJax.startup.promise.then(onMathReady);
    },
  },
};
document.head.append(el('script', { src: MATHJAX_URL, async: '' }));
}

window.Diagram = { mount };
})();
