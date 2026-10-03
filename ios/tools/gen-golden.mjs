// Erzeugt Golden-Files für die StickCore-Tests direkt aus src/StickkartenGeneratorV4.jsx.
//
// Die JSX wird per esbuild transformiert (JSX -> h()-Aufrufe) und als ES-Modul geladen;
// die Funktionen buildGraph, buildStitchSequence, computeFlatSheet, pageFitFor,
// buildStepDiagram usw. laufen damit unverändert aus der Referenz. Nur die in der
// Komponente `StickkartenGeneratorV4` / `Anleitung` inline berechneten abgeleiteten Werte
// (Rmin, Rmax, kMax, unterdrückte Ebenen, Abstands-Klassifizierung, Arm-/Stern-Abschnitte)
// sind hier 1:1 nachgebaut (Quellzeilen jeweils vermerkt), weil sie nicht exportiert sind.
//
// Aufruf: cd ios/tools && npm install && npm run golden

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import esbuild from "esbuild";

const here = dirname(fileURLToPath(import.meta.url));
const jsxPath = join(here, "../../src/StickkartenGeneratorV4.jsx");
const outDir = join(here, "../StickCore/Tests/StickCoreTests/Golden");
mkdirSync(outDir, { recursive: true });

/* ---------------- Referenz-Modul laden ---------------- */

const src = readFileSync(jsxPath, "utf8");
const { code } = esbuild.transformSync(src, { loader: "jsx", jsxFactory: "h", jsxFragment: "Frag", format: "esm" });
const prelude = `
const h = (tag, props, ...children) => ({ tag, props: props || {}, children: children.flat(Infinity) });
const Frag = "frag";
const React = { Children: { count: () => 0 } };
const useState = () => [], useMemo = () => null, useEffect = () => {}, useCallback = () => null;
const Play = 0, Pause = 0, RotateCcw = 0, Download = 0, AlertTriangle = 0, Settings = 0, X = 0, Printer = 0;
`;
const exportsTail = `
export { FADEN_STRAENGE, FADEN_DURCHMESSER, LOCH_DURCHMESSER, MINDESTABSTAND, RAND_MIN, FALZ_MIN, STICH_LIMIT,
  MODERAT_FAKTOR, FORMATE, polar, dist, divisorsOf, astBranchLevels, buildGraph, buildStitchSequence,
  computeFlatSheet, pageFitFor, buildStepDiagram, groupSteps, fadenCmFor, astNodeLabel, ANLEITUNG_FARBEN };
`;
const body = code.replace(/^import .*$/gm, "").replace("export default function", "function");
const tmpFile = join(here, ".reference-module.mjs");
writeFileSync(tmpFile, prelude + body + exportsTail);
const ref = await import(pathToFileURL(tmpFile).href);
const {
  LOCH_DURCHMESSER, MINDESTABSTAND, RAND_MIN, FALZ_MIN, STICH_LIMIT, MODERAT_FAKTOR, FORMATE,
  dist, divisorsOf, astBranchLevels, buildGraph, buildStitchSequence, computeFlatSheet, pageFitFor,
  buildStepDiagram, groupSteps, fadenCmFor, astNodeLabel, ANLEITUNG_FARBEN,
} = ref;

/* ---------------- Standardwerte = useState-Anfangswerte (JSX Z. 977–1014) ---------------- */

const DEFAULTS = {
  formatPreset: "a6-hoch", customW: 105, customH: 148, falzposition: "links",
  n: 8, zoom: 1,
  astschicht: true, ebenen: 4, astAktiv: true, astWinkel: 55, astLaenge: 0.7, astWachstum: 0.3,
  fraktalTiefe: 0, fraktalSkalierung: 0.5,
  sternschicht: true, sternEbene: 2, sternTeiler: 1, k1: 3,
  sternschicht2: false, sternEbene2: 4, sternTeiler2: 1, sternVersatz2: 0, k2: 1,
  astAusblendung1: "keine", astAusblendung2: "keine",
};

/* ---------------- Abgeleitete Werte (JSX Z. 1019–1150) ---------------- */

function derive(s) {
  const format = s.formatPreset === "custom" ? { w: s.customW, h: s.customH } : FORMATE[s.formatPreset];
  const margins = { top: RAND_MIN, right: RAND_MIN, bottom: RAND_MIN, left: RAND_MIN };
  if (s.falzposition === "links") margins.left = FALZ_MIN;
  if (s.falzposition === "oben") margins.top = FALZ_MIN;
  const usableW = Math.max(1, format.w - margins.left - margins.right);
  const usableH = Math.max(1, format.h - margins.top - margins.bottom);
  const cx = margins.left + usableW / 2;
  const cy = margins.top + usableH / 2;
  const Rmax = Math.min(usableW, usableH) / 2;
  const { n, ebenen, astschicht, astAktiv } = s;

  const teilerOptionen = divisorsOf(n);
  const effTeiler1 = teilerOptionen.includes(s.sternTeiler) ? s.sternTeiler : 1;
  const sternPunkte1 = n / effTeiler1;
  const kMax1 = Math.max(1, Math.floor(sternPunkte1 / 2) - (astschicht ? 1 : 0));
  const effTeiler2 = teilerOptionen.includes(s.sternTeiler2) ? s.sternTeiler2 : 1;
  const sternPunkte2 = n / effTeiler2;
  const kMax2 = Math.max(1, Math.floor(sternPunkte2 / 2) - (astschicht ? 1 : 0));

  const branchLevels = astBranchLevels(ebenen);
  const sternEbeneEff1 = Math.min(s.sternEbene, ebenen);
  const sternEbeneEff2 = Math.min(s.sternEbene2, ebenen);
  const ausblendungBasis = astschicht && astAktiv && branchLevels.length > 0;

  const set = new Set();
  if (ausblendungBasis) {
    if (s.sternschicht) {
      if (s.astAusblendung1 === "exakt" && branchLevels.includes(sternEbeneEff1)) set.add(sternEbeneEff1);
      if (s.astAusblendung1 === "kleinerGleich") branchLevels.forEach((L) => { if (L <= sternEbeneEff1) set.add(L); });
    }
    if (s.sternschicht && s.sternschicht2) {
      if (s.astAusblendung2 === "exakt" && branchLevels.includes(sternEbeneEff2)) set.add(sternEbeneEff2);
      if (s.astAusblendung2 === "kleinerGleich") branchLevels.forEach((L) => { if (L <= sternEbeneEff2) set.add(L); });
    }
  }
  const unterdrueckteEbenen = set;

  let Rmin = 12;
  Rmin = Math.max(Rmin, (MINDESTABSTAND * n) / (2 * Math.PI));
  if (astschicht) Rmin = Math.max(Rmin, MINDESTABSTAND * ebenen);
  const formatOk = Rmin <= Rmax;
  const R = formatOk ? Rmin + s.zoom * (Rmax - Rmin) : Rmax;

  const { nodes, edges, astCount, star1Count, star2Count } = buildGraph({
    n, R, cx, cy, astschicht, ebenen, astAktiv,
    astWinkel: s.astWinkel, astLaenge: s.astLaenge, astWachstum: s.astWachstum,
    fraktalTiefe: s.fraktalTiefe, fraktalSkalierung: s.fraktalSkalierung,
    sternschicht: s.sternschicht, sternEbene: Math.min(s.sternEbene, ebenen), sternTeiler: effTeiler1, k1: Math.min(s.k1, kMax1),
    sternschicht2: s.sternschicht2, sternEbene2: Math.min(s.sternEbene2, ebenen), sternTeiler2: effTeiler2,
    sternVersatz2: s.sternVersatz2, k2: Math.min(s.k2, kMax2),
    unterdrueckteEbenen,
  });
  const segments = buildStitchSequence(edges);
  const stitchSegments = segments.filter((x) => x.type === "stitch");
  const jumpSegments = segments.filter((x) => x.type === "jump");
  const frontLength = stitchSegments.reduce((sum, x) => sum + dist(nodes.get(x.a), nodes.get(x.b)), 0);
  const jumpLength = jumpSegments.reduce((sum, x) => sum + dist(nodes.get(x.a), nodes.get(x.b)), 0);

  const sev = new Map();
  const pts = [...nodes.entries()];
  for (let i = 0; i < pts.length; i++) {
    let nearest = Infinity;
    for (let j = 0; j < pts.length; j++) {
      if (i === j) continue;
      const d = dist(pts[i][1], pts[j][1]);
      if (d < nearest) nearest = d;
    }
    let sv = "ok";
    if (nearest < MINDESTABSTAND) sv = "critical";
    else if (nearest < MINDESTABSTAND * MODERAT_FAKTOR) sv = "moderate";
    sev.set(pts[i][0], sv);
  }
  const vals = [...sev.values()];
  const hasCritical = vals.includes("critical");
  const hasModerate = vals.includes("moderate");

  const warnungen = [];
  if (!astschicht && !s.sternschicht) warnungen.push("Aktiviere mindestens eine Musterschicht (Astschicht oder Sternschicht).");
  if (!formatOk) warnungen.push("Bei dieser Achsen-/Ebenenzahl passt kein gültiger Mindestabstand auf diese Karte.");
  if (stitchSegments.length > STICH_LIMIT) warnungen.push(`${stitchSegments.length} Stiche — mehr als das Richtmaß von ${STICH_LIMIT}. Für eine handhabbare Karte Kreispunkte oder Ebenen reduzieren.`);
  if (hasCritical) warnungen.push(`Manche Löcher liegen unter dem Mindestabstand (${MINDESTABSTAND.toFixed(1)} mm) — Stiche werden nicht angezeigt, bis der Zoom verkleinert wird.`);
  else if (hasModerate) warnungen.push(`Manche Löcher liegen nur knapp über dem Mindestabstand (${MINDESTABSTAND.toFixed(1)} mm) — betroffene Punkte sind markiert.`);

  return {
    format, margins, usableW, usableH, cx, cy, Rmax, Rmin, formatOk, R,
    effTeiler1, effTeiler2, kMax1, kMax2, sternEbeneEff1, sternEbeneEff2,
    k1Eff: Math.min(s.k1, kMax1), k2Eff: Math.min(s.k2, kMax2),
    unterdrueckteEbenen, nodes, edges, astCount, star1Count, star2Count, segments, stitchSegments,
    frontLength, jumpLength, sev, hasCritical, hasModerate, warnungen,
  };
}

/* ---------------- Anleitung-Daten (JSX Z. 551–680) ---------------- */

const r = (x) => x; // Platzhalter: volle Double-Präzision wird beibehalten

function primitives(elements) {
  const out = [];
  for (const el of elements) {
    if (el.tag === "line") {
      const p = el.props;
      out.push({ k: "line", v: [p.x1, p.y1, p.x2, p.y2] });
    } else if (el.tag === "path") {
      const nums = el.props.d.match(/-?\d+(?:\.\d+)?(?:e-?\d+)?/gi).map(Number);
      out.push({ k: "path", v: nums });
    } else if (el.tag === "circle") {
      out.push({ k: "circle", v: [el.props.cx, el.props.cy, el.props.r] });
    } else if (el.tag === "text") {
      out.push({ k: "text", v: [el.props.x, el.props.y], s: String(el.children.join("")), anchor: el.props.textAnchor });
    }
  }
  return out;
}

function stepList(steps) {
  return steps.map((st) => ({
    vs: [st.vs.a, st.vs.b],
    rs: st.rs ? [st.rs.a, st.rs.b] : null,
    rsIsTransition: !!st.rsIsTransition,
  }));
}

function anleitung(s, d) {
  const { nodes, edges, astCount, star1Count, star2Count } = d;
  const { n, ebenen, astschicht } = s;
  const astEdges = astschicht ? edges.slice(0, astCount) : [];
  const star1Edges = s.sternschicht ? edges.slice(astCount, astCount + star1Count) : [];
  const star2Edges = s.sternschicht2 ? edges.slice(astCount + star1Count, astCount + star1Count + star2Count) : [];
  const out = { arm: null, stern1: null, stern2: null };

  if (astschicht && n > 0 && astCount > 0) {
    const armEdgeCount = astCount / n;
    const arm0Edges = astEdges.slice(0, armEdgeCount);
    const fullAstSegs = buildStitchSequence(astEdges);
    const armSegCount = 2 * armEdgeCount - 1;
    const armSegs = fullAstSegs.slice(0, armSegCount);
    const transitionSeg = n > 1 ? fullAstSegs[armSegCount] || null : null;
    const armSteps = groupSteps(armSegs, transitionSeg);
    const armIds = [...new Set(arm0Edges.flatMap((e) => [e.a, e.b]))];
    const armPoints = {};
    armIds.forEach((id) => { armPoints[id] = nodes.get(id); });
    const diagram = buildStepDiagram({
      keyPrefix: "arm", points: armPoints, ids: armIds, steps: armSteps, labelOf: astNodeLabel,
      rotateAroundId: "C" in armPoints ? "C" : armIds[0], rotateDeg: 90,
      maxW: 856, maxH: 900, margin: 42, holeR: 5, holeFill: ANLEITUNG_FARBEN.paper, holeStroke: ANLEITUNG_FARBEN.ink,
      bend: { factor: 0.3, minB: 16, maxB: 30, step: 2 }, vsColor: ANLEITUNG_FARBEN.vs, rsColor: ANLEITUNG_FARBEN.rs,
    });
    const fadenFlocke = fadenCmFor(astEdges.length ? buildStitchSequence(astEdges) : [], nodes);
    out.arm = {
      armEdgeCount, steps: stepList(armSteps), labels: armIds.map((id) => [id, astNodeLabel(id)]),
      fadenCm: fadenFlocke, width: diagram.width, height: diagram.height, elements: primitives(diagram.elements),
    };
  }

  function sternSection(keyPrefix, starEdges, farbe) {
    if (!starEdges.length) return null;
    const starSegs = buildStitchSequence(starEdges);
    const starSteps = groupSteps(starSegs, null);
    const ids = [...new Set(starEdges.flatMap((e) => [e.a, e.b]))];
    const points = {};
    ids.forEach((id) => { points[id] = nodes.get(id); });
    const labelOf = (id) => {
      const idx = ids.indexOf(id);
      const isRing = /^R\d+$/.test(id);
      return isRing || !astschicht ? `K${idx + 1}` : `A${idx + 1}`;
    };
    const shown = starSteps.slice(0, 3);
    const diagram = buildStepDiagram({
      keyPrefix, points, ids, steps: shown, labelOf, backgroundEdges: starEdges, backgroundColor: farbe,
      maxW: 420, maxH: 420, margin: 40, holeR: 4, holeFill: ANLEITUNG_FARBEN.ink,
      labelFill: ANLEITUNG_FARBEN.sub, labelSize: 11,
      bend: { factor: 0.3, minB: 18, maxB: 38, step: 3 }, vsColor: ANLEITUNG_FARBEN.vs, rsColor: ANLEITUNG_FARBEN.rs,
    });
    return {
      ids, labels: ids.map((id) => labelOf(id)), steps: stepList(starSteps), fadenCm: fadenCmFor(starSegs, nodes),
      width: diagram.width, height: diagram.height, elements: primitives(diagram.elements),
    };
  }
  if (s.sternschicht) out.stern1 = sternSection("s1", star1Edges, ANLEITUNG_FARBEN.stern1);
  if (s.sternschicht2) out.stern2 = sternSection("s2", star2Edges, ANLEITUNG_FARBEN.stern2);
  return out;
}

/* ---------------- Datensatz je Konfiguration ---------------- */

function record(name, overrides, { diagrams = false } = {}) {
  const s = { ...DEFAULTS, ...overrides };
  const d = derive(s);
  const nodeIds = [...d.nodes.keys()];
  const flat = computeFlatSheet(d.format, s.falzposition);
  const rec = {
    name,
    settings: s,
    derived: {
      formatW: d.format.w, formatH: d.format.h,
      margins: d.margins, usableW: d.usableW, usableH: d.usableH, cx: d.cx, cy: d.cy,
      Rmax: d.Rmax, Rmin: d.Rmin, formatOk: d.formatOk, R: d.R,
      effTeiler1: d.effTeiler1, effTeiler2: d.effTeiler2, kMax1: d.kMax1, kMax2: d.kMax2,
      sternEbeneEff1: d.sternEbeneEff1, sternEbeneEff2: d.sternEbeneEff2, k1Eff: d.k1Eff, k2Eff: d.k2Eff,
      unterdrueckteEbenen: [...d.unterdrueckteEbenen].sort((a, b) => a - b),
    },
    nodes: { ids: nodeIds, x: nodeIds.map((id) => d.nodes.get(id).x), y: nodeIds.map((id) => d.nodes.get(id).y) },
    edges: { a: d.edges.map((e) => e.a), b: d.edges.map((e) => e.b), len: d.edges.map((e) => e.len), id: d.edges.map((e) => e.id) },
    counts: { ast: d.astCount, star1: d.star1Count, star2: d.star2Count },
    segments: { a: d.segments.map((x) => x.a), b: d.segments.map((x) => x.b), jump: d.segments.map((x) => (x.type === "jump" ? 1 : 0)) },
    stats: {
      stitchCount: d.stitchSegments.length, jumpCount: d.segments.length - d.stitchSegments.length,
      maxStep: d.segments.length, frontLength: d.frontLength, jumpLength: d.jumpLength,
      fadenCm: ((d.frontLength + d.jumpLength) * 1.15) / 10,
    },
    severity: nodeIds.map((id) => ({ ok: "o", moderate: "m", critical: "c" }[d.sev.get(id)])).join(""),
    hasCritical: d.hasCritical, hasModerate: d.hasModerate, warnungen: d.warnungen,
    flat: { w: flat.w, h: flat.h, offX: flat.offX, offY: flat.offY, foldAxis: flat.foldAxis, foldPos: flat.foldPos },
    pageFit: pageFitFor(flat),
  };
  if (diagrams) rec.anleitung = anleitung(s, d);
  return rec;
}

/* ---------------- Konfigurationsmengen ---------------- */

// Deterministischer Zufall (mulberry32), damit die Golden-Files reproduzierbar sind.
function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const grid = [];
for (let n = 3; n <= 16; n++) {
  for (let ebenen = 1; ebenen <= 6; ebenen++) {
    grid.push(record(`grid n=${n} ebenen=${ebenen}`, { n, ebenen }, { diagrams: (n + ebenen) % 3 === 0 }));
  }
}

const fraktal = [];
for (const n of [3, 5, 8, 12, 16]) {
  for (const ebenen of [1, 2, 4, 6]) {
    for (const fraktalTiefe of [0, 1, 2]) {
      for (const astAktiv of [true, false]) {
        fraktal.push(record(`fraktal n=${n} e=${ebenen} t=${fraktalTiefe} ast=${astAktiv}`,
          { n, ebenen, fraktalTiefe, astAktiv, astWinkel: 30 + ((n + ebenen) % 3) * 12, fraktalSkalierung: [0.5, 0.65, 0.4][fraktalTiefe] },
          { diagrams: fraktalTiefe > 0 && (n === 5 || n === 12) && ebenen !== 1 }));
      }
    }
  }
}

const ausblendung = [];
for (const ebenen of [3, 5, 6]) {
  for (const sternEbene of [1, 2, 3, 5, 6]) {
    for (const a1 of ["keine", "exakt", "kleinerGleich"]) {
      for (const a2 of ["keine", "exakt", "kleinerGleich"]) {
        ausblendung.push(record(`ausblendung e=${ebenen} se=${sternEbene} a1=${a1} a2=${a2}`, {
          n: 12, ebenen, sternEbene, sternEbene2: 7 - sternEbene, sternschicht2: true, sternTeiler: 2, sternTeiler2: 3, sternVersatz2: 1,
          k1: 2, k2: 1, astAusblendung1: a1, astAusblendung2: a2, fraktalTiefe: sternEbene % 3,
        }, { diagrams: a1 === "exakt" && a2 === "kleinerGleich" }));
      }
    }
  }
}

const rand = rng(20240607);
const pick = (arr) => arr[Math.floor(rand() * arr.length)];
const between = (lo, hi, step) => lo + Math.floor(rand() * (Math.round((hi - lo) / step) + 1)) * step;
const random = [];
for (let i = 0; i < 260; i++) {
  const n = between(3, 16, 1);
  const preset = pick(["a6-hoch", "a6-quer", "a6-hoch", "custom"]);
  const o = {
    formatPreset: preset,
    customW: between(60, 210, 5), customH: between(60, 297, 5),
    falzposition: pick(["links", "oben", "keine"]),
    n, zoom: pick([0, 0.2, 0.5, 0.8, 1, between(0, 1, 0.02)]),
    astschicht: rand() > 0.12, ebenen: between(1, 6, 1), astAktiv: rand() > 0.3,
    astWinkel: between(3, 55, 1), astLaenge: between(0.2, 2, 0.05), astWachstum: between(0, 1.5, 0.05),
    fraktalTiefe: pick([0, 0, 1, 2]), fraktalSkalierung: pick([0.3, 0.5, 0.7]),
    sternschicht: rand() > 0.15, sternEbene: between(1, 6, 1), sternTeiler: between(1, 8, 1), k1: between(1, 8, 1),
    sternschicht2: rand() > 0.5, sternEbene2: between(1, 6, 1), sternTeiler2: between(1, 8, 1), sternVersatz2: between(0, 5, 1), k2: between(1, 8, 1),
    astAusblendung1: pick(["keine", "exakt", "kleinerGleich"]), astAusblendung2: pick(["keine", "exakt", "kleinerGleich"]),
  };
  random.push(record(`random #${i}`, o, { diagrams: i % 5 === 0 }));
}

/* ---------------- Layout-Tabellen ---------------- */

const layout = [];
for (const [w, h] of [[105, 148], [148, 105], [60, 60], [100, 280], [150, 200], [200, 150], [210, 297], [297, 210], [280, 100], [190, 277], [190.5, 277.5], [250, 120], [120, 250], [400, 300]]) {
  for (const falz of ["links", "oben", "keine"]) {
    const flat = computeFlatSheet({ w, h }, falz);
    layout.push({ w, h, falz, flat: { w: flat.w, h: flat.h, offX: flat.offX, offY: flat.offY, foldAxis: flat.foldAxis, foldPos: flat.foldPos }, pageFit: pageFitFor(flat) });
  }
}

const meta = {
  FADEN_DURCHMESSER: ref.FADEN_DURCHMESSER, LOCH_DURCHMESSER, MINDESTABSTAND, RAND_MIN, FALZ_MIN, STICH_LIMIT, MODERAT_FAKTOR,
  FORMATE: Object.fromEntries(Object.entries(FORMATE).map(([k, v]) => [k, { w: v.w, h: v.h }])),
};

const files = { "grid.json": grid, "fraktal.json": fraktal, "ausblendung.json": ausblendung, "random.json": random, "layout.json": layout, "meta.json": meta };
for (const [name, data] of Object.entries(files)) {
  writeFileSync(join(outDir, name), JSON.stringify(data));
  console.log(name, Array.isArray(data) ? data.length : "obj", (JSON.stringify(data).length / 1024).toFixed(0) + " KiB");
}
