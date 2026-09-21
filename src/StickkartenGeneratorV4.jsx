import React, { useState, useMemo, useEffect, useCallback } from "react";
import { Play, Pause, RotateCcw, Download, AlertTriangle, Settings, X, Printer, FileDown } from "lucide-react";

/* ---------------------------------------------------------------------- */
/* Feste Randbedingungen                                                  */
/* ---------------------------------------------------------------------- */

const FADEN_STRAENGE = 3;
const FADEN_DURCHMESSER = FADEN_STRAENGE * 0.17; // mm
const LOCH_DURCHMESSER = Math.min(1.5, Math.max(0.5, FADEN_DURCHMESSER * 1.8)); // mm
const MINDESTABSTAND = Math.max(2, LOCH_DURCHMESSER * 3.5); // mm
const RAND_MIN = 14; // mm
const FALZ_MIN = 18; // mm
const STICH_LIMIT = 300;
const MODERAT_FAKTOR = 1.5; // 100–150 % des Mindestabstands = mäßig eng; darunter = zu gering

const FORMATE = {
  "a6-hoch": { label: "A6 Hochformat, 105 × 148 mm (A5 gefaltet)", w: 105, h: 148 },
  "a6-quer": { label: "A6 Querformat, 148 × 105 mm (A5 gefaltet)", w: 148, h: 105 },
  custom: { label: "Eigenes Format", w: null, h: null },
};
const KARTONFARBEN = {
  tanne: { label: "Tannengrün", hex: "#153a2c", aktivVS: "#ffd966", aktivRS: "#7fd8ff" },
  mitternacht: { label: "Mitternachtsblau", hex: "#10203a", aktivVS: "#ffcf5c", aktivRS: "#8fe6c8" },
  bordeaux: { label: "Bordeaux", hex: "#481621", aktivVS: "#ffd97a", aktivRS: "#7fe0e0" },
  elfenbein: { label: "Elfenbein", hex: "#efe6d6", aktivVS: "#a8650a", aktivRS: "#1f4e8c" },
};
const FADENFARBEN = {
  gold: { label: "Gold", primary: "#e8c987" },
  silber: { label: "Silber", primary: "#d9e2e7" },
  weiss: { label: "Weiß", primary: "#ffffff" },
  blau: { label: "Mitternachtsblau", primary: "#3a5a8c" },
};
const WARN_FARBE = "#e8a23d"; // mäßig eng
const GEFAHR_FARBE = "#e0503f"; // zu gering

/* ---------------------------------------------------------------------- */
/* Geometrie                                                              */
/* ---------------------------------------------------------------------- */

function polar(cx, cy, angleDeg, r) {
  const rad = (angleDeg * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}
function dist(p1, p2) {
  return Math.hypot(p1.x - p2.x, p1.y - p2.y);
}
function divisorsOf(n) {
  const ds = [];
  for (let d = 1; d <= n; d++) if (n % d === 0 && n / d >= 2) ds.push(d);
  return ds;
}
/* Ebenen, auf denen Seitenäste überhaupt existieren können (siehe buildGraph:
   Astwurzeln entstehen für L = 1..ebenen-1, Seitenäste erst ab L>=2) — leer,
   wenn ebenen<3. Wird gebraucht, um die "Seitenäste beim Sternlevel weglassen"-
   Option nur dann anzuzeigen, wenn sie tatsächlich etwas bewirken würde. */
function astBranchLevels(ebenen) {
  const levels = [];
  for (let L = 2; L <= ebenen - 1; L++) levels.push(L);
  return levels;
}

/* ---------------------------------------------------------------------- */
/* Punktkreis-Modell                                                      */
/* ---------------------------------------------------------------------- */

function addFraktalZweige(parentId, parentPos, approachAngle, length, depth, maxDepth, branchAngle, scale, nodes, addEdge) {
  if (depth > maxDepth || length < 0.6) return;
  for (const side of [-1, 1]) {
    const childAngle = approachAngle + side * branchAngle;
    const p = polar(parentPos.x, parentPos.y, childAngle, length);
    const id = `${parentId}f${depth}${side < 0 ? "n" : "p"}`;
    nodes.set(id, p);
    addEdge(parentId, id);
    addFraktalZweige(id, p, childAngle, length * scale, depth + 1, maxDepth, branchAngle, scale, nodes, addEdge);
  }
}

/* Eine Sternschicht: eigene Ebene, eigene Strahlenzahl (Teiler von n), eigener
   Rotationsversatz, eigene Schrittweite — vollständig unabhängig von anderen Schichten. */
function addSternLayer({ n, ringIds, ebenen, astschicht, sternEbene, sternTeiler, versatz, k, seen, addEdge }) {
  const level = astschicht ? Math.min(Math.max(1, sternEbene), ebenen) : null;
  const pointIdAt = (i) => (level === null || level === ebenen ? ringIds[i] : `A${i}L${level}`);
  let teiler = Math.max(1, Math.min(sternTeiler, n));
  while (teiler > 1 && n % teiler !== 0) teiler--;
  const m = n / teiler;
  const offset = ((versatz % teiler) + teiler) % teiler;
  if (k < 1 || k > m - 1) return;
  for (let j = 0; j < m; j++) {
    const jj = (j + k) % m;
    const a = pointIdAt((j * teiler + offset) % n);
    const b = pointIdAt((jj * teiler + offset) % n);
    const key = a < b ? `${a}|${b}` : `${b}|${a}`;
    if (!seen.has(key)) {
      seen.add(key);
      addEdge(a, b);
    }
  }
}

function buildGraph({
  n,
  R,
  cx,
  cy,
  astschicht,
  ebenen,
  astAktiv,
  astWinkel,
  astLaenge,
  astWachstum,
  fraktalTiefe,
  fraktalSkalierung,
  sternschicht,
  sternEbene,
  sternTeiler,
  k1,
  sternschicht2,
  sternEbene2,
  sternTeiler2,
  sternVersatz2,
  k2,
  unterdrueckteEbenen, // Set<number> — Ebenen, deren Seitenäste (samt Fraktal-Spitzen) weggelassen werden (siehe Sternschicht-Option)
}) {
  const skipLevels = unterdrueckteEbenen || new Set();
  const nodes = new Map();
  const edges = [];
  let counter = 0;
  const addEdge = (a, b) => edges.push({ id: `e${counter++}`, a, b, len: dist(nodes.get(a), nodes.get(b)) });

  const ringIds = [];
  for (let i = 0; i < n; i++) {
    const angle = -90 + i * (360 / n);
    const id = `R${i}`;
    nodes.set(id, polar(cx, cy, angle, R));
    ringIds.push(id);
  }

  if (astschicht) {
    nodes.set("C", { x: cx, y: cy });
    const armStep = R / ebenen;
    // Für jeden Arm exakt dieselbe Reihenfolge: Stamm nach außen, an jeder
    // Verzweigung erst der linke, dann der rechte Zweig samt Fraktal-Spitzen,
    // bevor es am Stamm weitergeht — identisch für alle n Arme.
    for (let i = 0; i < n; i++) {
      const angle = -90 + i * (360 / n);
      let prevId = "C";
      for (let L = 1; L < ebenen; L++) {
        const r = L * armStep;
        const id = `A${i}L${L}`;
        nodes.set(id, polar(cx, cy, angle, r));
        addEdge(prevId, id);
        const root = nodes.get(id);
        prevId = id;
        if (astAktiv && L >= 2 && !skipLevels.has(L)) {
          for (const side of [-1, 1]) {
            const bAngle = angle + side * astWinkel;
            const branchLen = armStep * astLaenge * (1 + astWachstum * (L - 1));
            const bid = `A${i}L${L}b${side}`;
            // Astspitze relativ zur Astwurzel (nicht zum Kartenzentrum) —
            // dadurch sind Astlänge und Astwinkel vollständig entkoppelt.
            const bp = polar(root.x, root.y, bAngle, branchLen);
            nodes.set(bid, bp);
            addEdge(id, bid);
            if (fraktalTiefe > 0) {
              addFraktalZweige(bid, bp, bAngle, branchLen * fraktalSkalierung, 1, fraktalTiefe, astWinkel, fraktalSkalierung, nodes, addEdge);
            }
          }
        }
      }
      addEdge(prevId, ringIds[i]);
      if (fraktalTiefe > 0) {
        addFraktalZweige(ringIds[i], nodes.get(ringIds[i]), angle, armStep * astLaenge * (1 + astWachstum * (ebenen - 1)), 1, fraktalTiefe, astWinkel, fraktalSkalierung, nodes, addEdge);
      }
    }
  }

  // Kantenzähler je Phase — für die Arbeitsanweisung (Teil "Astschicht"/"Sternschicht(en)"),
  // damit deren jeweilige Kanten aus dem gemeinsamen `edges`-Array isoliert werden können,
  // ohne die Grafikerzeugung (nodes/edges) selbst zu verändern.
  const astCount = edges.length;
  let star1Count = 0;
  let star2Count = 0;

  if (sternschicht) {
    const seen = new Set();
    const beforeStar1 = edges.length;
    addSternLayer({ n, ringIds, ebenen, astschicht, sternEbene, sternTeiler, versatz: 0, k: k1, seen, addEdge });
    star1Count = edges.length - beforeStar1;
    if (sternschicht2) {
      const beforeStar2 = edges.length;
      addSternLayer({ n, ringIds, ebenen, astschicht, sternEbene: sternEbene2, sternTeiler: sternTeiler2, versatz: sternVersatz2, k: k2, seen, addEdge });
      star2Count = edges.length - beforeStar2;
    }
  }

  return { nodes, edges, astCount, star1Count, star2Count };
}

/* ---------------------------------------------------------------------- */
/* Stichweg: Kanten in ihrer strukturellen Erzeugungsreihenfolge (Ast für  */
/* Ast, Sehne für Sehne) statt nach Distanz sortiert. Jede Kante genau     */
/* einmal, immer ein echter Sprung zwischen zwei Stichen.                 */
/* ---------------------------------------------------------------------- */

function buildStitchSequence(edges) {
  const segments = [];
  let currentPos = null;
  for (const edge of edges) {
    let near = edge.a;
    let far = edge.b;
    if (near === currentPos) {
      near = edge.b;
      far = edge.a;
    }
    if (currentPos !== null) segments.push({ a: currentPos, b: near, type: "jump" });
    segments.push({ a: near, b: far, type: "stitch" });
    currentPos = far;
  }
  return segments;
}

/* ---------------------------------------------------------------------- */
/* Anleitung — Layout-Hilfsfunktionen (reine Geometrie, kein DOM-Zugriff;  */
/* das Rendering erfolgt unten als JSX innerhalb der Anleitung-Komponente).*/
/* ---------------------------------------------------------------------- */

function rotatePt(p, c, deg) {
  const rad = (deg * Math.PI) / 180;
  const dx = p.x - c.x, dy = p.y - c.y;
  return { x: c.x + dx * Math.cos(rad) - dy * Math.sin(rad), y: c.y + dx * Math.sin(rad) + dy * Math.cos(rad) };
}
function xformPt(p, scale, cx, cy, offX, offY) {
  return { x: offX + (p.x - cx) * scale, y: offY + (p.y - cy) * scale };
}
function bowedPt(a, b, bend) {
  const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
  const dx = b.x - a.x, dy = b.y - a.y, len = Math.hypot(dx, dy) || 1;
  const nx = -dy / len, ny = dx / len;
  return { x: mx + nx * bend, y: my + ny * bend };
}
/* Bogenhöhe proportional zur (Bildschirm-)Länge des Segments, statt fest — sonst
   wirken kurze Sehnen (z.B. beim Stern) überproportional stark gekrümmt. */
function autoBendPt(a, b, factor, minB, maxB) {
  return Math.max(minB, Math.min(maxB, dist(a, b) * factor));
}
/* Tatsächlicher Kurvenmittelpunkt (t=0.5) einer quadratischen Bézier — nicht der
   Kontrollpunkt selbst (der liegt doppelt so weit von der Sehne weg). */
function curveMidpointPt(a, b, bend) {
  const c = bowedPt(a, b, bend);
  return { x: 0.25 * a.x + 0.5 * c.x + 0.25 * b.x, y: 0.25 * a.y + 0.5 * c.y + 0.25 * b.y };
}
/* Passt Skalierung UND Zeichenfläche automatisch an die tatsächliche Ausdehnung
   der Punkte an — nutzt immer den verfügbaren Platz (bis maxW×maxH), unabhängig
   davon, wie viele Ebenen/Äste/Zweige eine Konfiguration erzeugt. Kein
   Kollisions-Check auf Pfad-Ebene (aufwendig, fehleranfällig) — stattdessen:
   maximal ausnutzen, Schrift-/Badge-Größen bleiben fest, bei sehr komplexen
   Mustern wird es eng (bewusste, einfache Entscheidung statt Overengineering). */
function autoFitPts(points, maxW, maxH, margin) {
  const xs = points.map((p) => p.x), ys = points.map((p) => p.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
  const bboxW = Math.max(maxX - minX, 1e-6), bboxH = Math.max(maxY - minY, 1e-6);
  const scale = Math.min((maxW - 2 * margin) / bboxW, (maxH - 2 * margin) / bboxH);
  const width = Math.round(bboxW * scale + 2 * margin), height = Math.round(bboxH * scale + 2 * margin);
  return { scale, offX: margin - minX * scale, offY: margin - minY * scale, width, height };
}
function badgeR(text) {
  return 9 + Math.max(0, String(text).length - 1) * 3;
}
/* Erst feststellen, welche Kreise (Art + Anzahl an Ziffern) an einer Stelle
   zusammentreffen, dann den Bogen jedes RS-Pfeils so weit vergrößern, bis sein
   Nummern-Kreis den Mindestabstand (+1px) zu allen bereits platzierten Kreisen
   einhält — VS-Badges (feste Position) zählen dabei als bereits belegt. */
function resolveRsBendsPts(vsBadges, rsGroups, factor, minB, maxB, step) {
  const placed = vsBadges.map((v) => ({ pos: v.pos, r: v.r }));
  return rsGroups.map((g) => {
    const r = badgeR(g.nums.join(","));
    let bend = autoBendPt(g.seg.a, g.seg.b, factor, minB, maxB);
    let pos = curveMidpointPt(g.seg.a, g.seg.b, bend);
    let tries = 0;
    while (tries < 25 && bend < maxB * 2 && placed.some((o) => dist(pos, o.pos) < r + o.r + 1)) {
      bend += step;
      pos = curveMidpointPt(g.seg.a, g.seg.b, bend);
      tries++;
    }
    placed.push({ pos, r });
    return Object.assign({}, g, { bend, pos, r });
  });
}
/* Logische Beschriftungsposition je Loch: aus allen tatsächlich gezeichneten
   Verbindungen dieses Punkts die größte freie Winkellücke suchen und das
   Kürzel dort platzieren — so weicht es den Pfeilen aus, statt immer an
   derselben festen Seite zu kleben. */
function buildAdjacencyPts(pairs) {
  const adj = new Map();
  pairs.forEach(([a, b]) => {
    if (!adj.has(a)) adj.set(a, []);
    if (!adj.has(b)) adj.set(b, []);
    adj.get(a).push(b);
    adj.get(b).push(a);
  });
  return adj;
}
function labelAnglePt(nodeId, disp, adj) {
  const p = disp[nodeId];
  const neighbors = adj.get(nodeId) || [];
  const angles = neighbors.map((nb) => Math.atan2(disp[nb].y - p.y, disp[nb].x - p.x)).sort((x, y) => x - y);
  if (!angles.length) return -Math.PI / 2;
  let bestStart = angles[0], bestSize = -1;
  for (let i = 0; i < angles.length; i++) {
    const a1 = angles[i];
    const a2 = i + 1 < angles.length ? angles[i + 1] : angles[0] + 2 * Math.PI;
    const gap = a2 - a1;
    if (gap > bestSize) {
      bestSize = gap;
      bestStart = a1;
    }
  }
  return bestStart + bestSize / 2;
}
function placeLabelCoords(p, angle, distFromHole) {
  const lx = p.x + Math.cos(angle) * distFromHole, ly = p.y + Math.sin(angle) * distFromHole;
  let anchor = "middle", dx = 0, dy = 3.5;
  if (Math.cos(angle) > 0.35) { anchor = "start"; dx = 2; }
  else if (Math.cos(angle) < -0.35) { anchor = "end"; dx = -2; }
  if (Math.sin(angle) < -0.35) dy = 0;
  else if (Math.sin(angle) > 0.35) dy = 8;
  return { x: lx + dx, y: ly + dy, anchor };
}
/* RS-Bögen mit identischem Start/Ziel zusammenfassen und alle Schrittnummern gemeinsam anzeigen. */
function groupRsByPairPts(steps) {
  const groups = new Map();
  steps.forEach((step, i) => {
    if (!step.rs) return;
    const key = step.rs.a + "|" + step.rs.b;
    if (!groups.has(key)) groups.set(key, { seg: step.rs, nums: [] });
    groups.get(key).nums.push(i + 1);
  });
  return [...groups.values()];
}
/* Fasst je einen VS-Stich mit dem unmittelbar folgenden RS-Sprung zu "einem
   Schritt" zusammen (echte Abfolge der App: auf jeden Stich folgt sofort ein
   Sprung). `transitionSeg`: beim letzten Schritt einer Schicht optional der
   Sprung zum nächsten Teilelement (z.B. zum nächsten Ast). */
function groupSteps(segs, transitionSeg) {
  const steps = [];
  segs.forEach((s, i) => {
    if (s.type !== "stitch") return;
    const next = segs[i + 1];
    steps.push({ vs: s, rs: next && next.type === "jump" ? next : null });
  });
  if (transitionSeg && steps.length) {
    steps[steps.length - 1].rs = transitionSeg;
    steps[steps.length - 1].rsIsTransition = true;
  }
  return steps;
}
function fadenCmFor(segs, nodes) {
  const sum = segs.reduce((s, seg) => s + dist(nodes.get(seg.a), nodes.get(seg.b)), 0);
  return (sum * 1.15) / 10;
}
/* Generische Kurzbeschriftung für Astschicht-Knoten — funktioniert unabhängig
   von Ebenenzahl und Fraktaltiefe: Zentrum, Ebene L, Seitenast L links/rechts,
   Fraktal-Spitzen (rekursiv aus der Eltern-Beschriftung abgeleitet), Kreispunkt. */
function astNodeLabel(id) {
  if (id === "C") return "Z";
  if (/^R\d+$/.test(id)) return "K";
  let m = id.match(/^A\d+L(\d+)$/);
  if (m) return `E${m[1]}`;
  m = id.match(/^A\d+L(\d+)b(-?1)$/);
  if (m) return `E${m[1]}${m[2] === "-1" ? "L" : "R"}`;
  m = id.match(/^(.+)f(\d+)(n|p)$/);
  if (m) return `${astNodeLabel(m[1])}.${m[2]}${m[3] === "n" ? "a" : "b"}`;
  return id;
}

/* Baut ein einzelnes Schritt-Diagramm (VS-Pfeile, gruppierte RS-Bögen,
   Zahlen-Badges kollisionsfrei, Lochpunkte mit ausweichender Beschriftung) als
   Array von JSX-Elementen — von Astschicht- und Sternschicht-Anleitung gleichermaßen genutzt. */
function buildStepDiagram({
  keyPrefix,
  points, // { id: {x,y} } Weltkoordinaten
  ids, // anzuzeigende Lochpunkte (bestimmt auch die Passgenauigkeit/Bounding-Box)
  steps, // [{ vs:{a,b}, rs:{a,b}|null }]
  labelOf,
  backgroundEdges, // optional [{a,b}] — blass hinterlegtes Gesamtmuster
  backgroundColor,
  rotateAroundId,
  rotateDeg,
  maxW,
  maxH,
  margin,
  holeR,
  holeFill,
  holeStroke,
  labelFill,
  labelSize,
  bend,
  vsColor,
  rsColor,
}) {
  const allIds = Object.keys(points);
  const rotated = {};
  if (rotateAroundId && rotateDeg) {
    const center = points[rotateAroundId];
    allIds.forEach((id) => { rotated[id] = rotatePt(points[id], center, rotateDeg); });
  } else {
    allIds.forEach((id) => { rotated[id] = points[id]; });
  }
  const fit = autoFitPts(ids.map((id) => rotated[id]), maxW, maxH, margin);
  const disp = {};
  allIds.forEach((id) => { disp[id] = xformPt(rotated[id], fit.scale, 0, 0, fit.offX, fit.offY); });

  const TRIM = holeR + 2;
  const vsMarker = `${keyPrefix}-vs`, rsMarker = `${keyPrefix}-rs`;
  const elements = [];

  elements.push(
    <defs key="defs">
      <marker id={vsMarker} viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4.6" markerHeight="4.6" orient="auto-start-reverse">
        <path d="M0,0L10,5L0,10z" fill={vsColor} />
      </marker>
      <marker id={rsMarker} viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M0,0L10,5L0,10z" fill={rsColor} />
      </marker>
    </defs>
  );

  if (backgroundEdges) {
    backgroundEdges.forEach((e, i) => {
      elements.push(
        <line key={`bg-${i}`} x1={disp[e.a].x} y1={disp[e.a].y} x2={disp[e.b].x} y2={disp[e.b].y} stroke={backgroundColor} strokeWidth={1.6} opacity={0.22} />
      );
    });
  }

  // Vorab: Positionen/Radien der VS-Zahlenkreise (feste Position) + kollisionsfrei
  // aufgeweitete Bögen für die RS-Gruppen.
  const vsBadges = steps.map((step, i) => ({
    pos: { x: (disp[step.vs.a].x + disp[step.vs.b].x) / 2, y: (disp[step.vs.a].y + disp[step.vs.b].y) / 2 },
    r: badgeR(String(i + 1)),
  }));
  const rsGroupsWorld = groupRsByPairPts(steps).map((g) => Object.assign({}, g, { seg: { a: disp[g.seg.a], b: disp[g.seg.b] } }));
  const rsResolved = resolveRsBendsPts(vsBadges, rsGroupsWorld, bend.factor, bend.minB, bend.maxB, bend.step);

  // 1) Pfeile
  steps.forEach((step, i) => {
    const a = disp[step.vs.a], b = disp[step.vs.b];
    const dx = b.x - a.x, dy = b.y - a.y, len = Math.hypot(dx, dy) || 1, ux = dx / len, uy = dy / len;
    elements.push(
      <line key={`vs-${i}`} x1={a.x + ux * TRIM} y1={a.y + uy * TRIM} x2={b.x - ux * TRIM} y2={b.y - uy * TRIM} stroke={vsColor} strokeWidth={1.8} markerEnd={`url(#${vsMarker})`} />
    );
  });
  rsResolved.forEach((g, i) => {
    const c = bowedPt(g.seg.a, g.seg.b, g.bend);
    const along = (p, toward, trim) => {
      const dx = toward.x - p.x, dy = toward.y - p.y, len = Math.hypot(dx, dy) || 1;
      return { x: p.x + (dx / len) * trim, y: p.y + (dy / len) * trim };
    };
    const a2 = along(g.seg.a, c, TRIM), b2 = along(g.seg.b, c, TRIM);
    elements.push(
      <path key={`rs-${i}`} d={`M ${a2.x} ${a2.y} Q ${c.x} ${c.y} ${b2.x} ${b2.y}`} fill="none" stroke={rsColor} strokeWidth={1.8} strokeDasharray="0.1,5" strokeLinecap="round" markerEnd={`url(#${rsMarker})`} />
    );
  });

  // 2) Lochpunkte + Kürzel (Kürzel weicht der größten freien Winkellücke aus)
  const adjPairs = steps.flatMap((s) => (s.rs ? [[s.vs.a, s.vs.b], [s.rs.a, s.rs.b]] : [[s.vs.a, s.vs.b]]));
  if (backgroundEdges) backgroundEdges.forEach((e) => adjPairs.push([e.a, e.b]));
  const adj = buildAdjacencyPts(adjPairs);
  ids.forEach((id) => {
    const p = disp[id];
    elements.push(
      <circle key={`hole-${id}`} cx={p.x} cy={p.y} r={holeR} fill={holeFill} {...(holeStroke ? { stroke: holeStroke, strokeWidth: 1.4 } : {})} />
    );
    const angle = labelAnglePt(id, disp, adj);
    const { x, y, anchor } = placeLabelCoords(p, angle, holeR + 11);
    elements.push(
      <text key={`lbl-${id}`} x={x} y={y} fontFamily="system-ui,sans-serif" fontSize={labelSize || 10.5} fill={labelFill || "#26241f"} textAnchor={anchor} fontWeight="bold">
        {labelOf(id)}
      </text>
    );
  });

  // 3) Schritt-Nummern zuoberst
  steps.forEach((step, i) => {
    const p = vsBadges[i].pos;
    elements.push(<circle key={`vsnum-${i}`} cx={p.x} cy={p.y} r={vsBadges[i].r} fill="#ffffff" stroke={vsColor} strokeWidth={2} />);
    elements.push(
      <text key={`vsnumtxt-${i}`} x={p.x} y={p.y + 3.5} fontFamily="system-ui,sans-serif" fontSize={10.5} fill={vsColor} fontWeight="bold" textAnchor="middle">
        {i + 1}
      </text>
    );
  });
  rsResolved.forEach((g, i) => {
    elements.push(<circle key={`rsnum-${i}`} cx={g.pos.x} cy={g.pos.y} r={g.r} fill="#ffffff" stroke={rsColor} strokeWidth={2} />);
    elements.push(
      <text key={`rsnumtxt-${i}`} x={g.pos.x} y={g.pos.y + 3.5} fontFamily="system-ui,sans-serif" fontSize={10.5} fill={rsColor} fontWeight="bold" textAnchor="middle">
        {g.nums.join(",")}
      </text>
    );
  });

  return { width: fit.width, height: fit.height, elements };
}

/* ---------------------------------------------------------------------- */
/* Anleitung — druckbare Arbeitsanweisung aus den aktuellen App-Werten     */
/* (keine Vorlagen-/Beispieldaten mehr — echte Ebenen, echte Stichfolge). */
/* ---------------------------------------------------------------------- */

/* Maße des flachen, ungefalteten Zuschnitts, aus dem die (gefaltete) Karte
   entsteht — plus Versatz des vorderen (bestickten) Panels innerhalb dieses
   Zuschnitts. `format` ist im ganzen Generator die Größe der GEFALTETEN Karte
   (eine Hälfte); beim Falz an der Seite/oben liegt der Falz an genau der Kante
   dieses Panels, die auch die größere Mindestrandbreite (FALZ_MIN) trägt —
   der Zuschnitt ist daher in dieser Richtung doppelt so groß, und das Panel
   sitzt auf der von der Zuschnittmitte (Falzlinie) abgewandten Hälfte. */
function computeFlatSheet(format, falzposition) {
  if (falzposition === "links") return { w: format.w * 2, h: format.h, offX: format.w, offY: 0, foldAxis: "v", foldPos: format.w };
  if (falzposition === "oben") return { w: format.w, h: format.h * 2, offX: 0, offY: format.h, foldAxis: "h", foldPos: format.h };
  return { w: format.w, h: format.h, offX: 0, offY: 0, foldAxis: null, foldPos: null };
}
/* Passende A4-Seitenausrichtung (Hoch-/Querformat) für den Zuschnitt bestimmen —
   maßstabsgetreuer 1:1-Druck (für ein tatsächlich anstechbares Lochmuster
   entscheidend) hat Vorrang; passt keine Ausrichtung bei 100 %, wird die mit
   der geringsten nötigen Verkleinerung gewählt und das als Hinweis markiert. */
function pageFitFor(flat) {
  const PAGE_MARGIN_MM = 10;
  const options = [
    { orientation: "hoch", pageW: 210, pageH: 297 },
    { orientation: "quer", pageW: 297, pageH: 210 },
  ].map((o) => {
    const availW = o.pageW - 2 * PAGE_MARGIN_MM, availH = o.pageH - 2 * PAGE_MARGIN_MM;
    const scale = Math.min(1, availW / flat.w, availH / flat.h);
    return { ...o, availW, availH, scale, fits: scale >= 0.999 };
  });
  const [hoch, quer] = options;
  if (hoch.fits && quer.fits) return flat.w >= flat.h ? quer : hoch;
  if (hoch.fits) return hoch;
  if (quer.fits) return quer;
  return hoch.scale >= quer.scale ? hoch : quer;
}

const ANLEITUNG_FARBEN = {
  flocke: "#5b3a70", flockeTint: "#f1eaf5",
  stern1: "#c98a2b", stern1Tint: "#faf0df",
  stern2: "#2f8f8f", stern2Tint: "#e6f4f4",
  vs: "#2f7a4d", rs: "#b23b3b", ink: "#26241f", sub: "#6b6558", line: "#c9c0ac", paper: "#faf6ee",
};

function Anleitung({ config, nodes, edges, astCount, star1Count, star2Count, onClose }) {
  const {
    n, ebenen, astschicht, astAktiv, sternschicht, sternEbene, effTeiler1, k1,
    sternschicht2, sternEbene2, effTeiler2, sternVersatz2, k2, format, falzposition, zoom,
  } = config;

  // Läuft diese Komponente eingebettet (z.B. in einer Artifact-/Vorschau-Sandbox),
  // sind sowohl window.print() als auch ein via window.open() neu geöffneter Tab
  // aus Sicherheitsgründen blockiert — ohne sichtbare Fehlermeldung, es passiert
  // schlicht nichts (bestätigt auf Win10/Chrome und iPad/Safari). Der einzige
  // Weg, der aus einer solchen Sandbox zuverlässig herausreicht, ist ein echter
  // Dateidownload über einen Blob + unsichtbaren <a download>-Klick — exakt die
  // Technik, die "SVG exportieren" bereits nutzt. Der Download liefert die
  // Anleitung als eigenständige HTML-Datei (Stylesheet inkl. @page/@media
  // print-Regeln ist eingebettet); die Datei wird außerhalb der Sandbox in
  // einem normalen Browser-Tab geöffnet, wo Drucken/"Als PDF speichern" ganz
  // regulär funktioniert.
  function buildStandaloneHtml(docTitle) {
    const sheetEl = document.querySelector(".anleitung-root .sheet");
    if (!sheetEl) return null;
    return `<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><title>${docTitle}</title><style>${anleitungCss}</style></head><body><div class="anleitung-overlay"><div class="anleitung-root">${sheetEl.outerHTML}</div></div></body></html>`;
  }
  const handleDownloadHtml = () => {
    const html = buildStandaloneHtml("Stickkarten-Anleitung");
    if (!html) return;
    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "stickkarten-anleitung.html";
    a.click();
    URL.revokeObjectURL(url);
  };
  // Best-effort-Direktdruck — funktioniert, sofern diese Seite NICHT in einer
  // Sandbox/einem eingebetteten Frame läuft (z.B. selbst gehostet). In einer
  // Artifact-Vorschau bewusst nur als sekundäre Option, falls es doch geht.
  const handleDirectPrint = () => { try { window.print(); } catch (e) { /* siehe Download-Button oben */ } };

  // Echter Ein-Klick-PDF-Download ohne Druckdialog. Zwei Techniken kombiniert,
  // damit weder mitten im Inhalt geschnitten wird noch die 1:1-Maßhaltigkeit
  // verloren geht (beides trat mit einer reinen Ganzseiten-Rasterung auf):
  // - Teil 1–4 (Text/Diagramme, nicht maßstabskritisch): jeder Abschnitt wird
  //   EINZELN gerastert (html2canvas) und als eigenes Bild platziert — ein
  //   Seitenumbruch passiert nur ZWISCHEN Abschnitten, nie innerhalb eines
  //   Diagramms/einer Tabelle.
  // - Lochmuster-Seite (muss exakt 1:1 in mm stimmen, sonst passen die Löcher
  //   beim Anstechen nicht): wird als echtes Vektor-SVG in die PDF übernommen
  //   (svg2pdf), nicht gerastert/reskaliert — die physische Größe bleibt exakt
  //   erhalten, identisch zur bereits vorhandenen "Tatsächliche Größe"-Druckseite.
  const [pdfExporting, setPdfExporting] = useState(false);
  const handleDirectPdfDownload = async () => {
    const sheetEl = document.querySelector(".anleitung-root .sheet");
    if (!sheetEl || pdfExporting) return;
    setPdfExporting(true);
    try {
      const [{ jsPDF }, { default: html2canvas }, { svg2pdf }] = await Promise.all([
        import("jspdf"),
        import("html2canvas"),
        import("svg2pdf.js"),
      ]);
      const doc = new jsPDF({ unit: "mm", format: "a4", orientation: "portrait" });
      const pageW = doc.internal.pageSize.getWidth();
      const pageH = doc.internal.pageSize.getHeight();
      const margin = 12;
      const contentW = pageW - margin * 2;
      let y = margin;

      const blocks = [sheetEl.querySelector(".pdf-header"), ...sheetEl.querySelectorAll(".teil:not(.lochmuster-teil)")].filter(Boolean);
      for (const el of blocks) {
        const canvas = await html2canvas(el, { scale: 2, backgroundColor: "#ffffff", useCORS: true });
        const imgW = contentW;
        const imgH = (canvas.height / canvas.width) * imgW;
        if (y > margin && y + imgH > pageH - margin) {
          doc.addPage();
          y = margin;
        }
        doc.addImage(canvas.toDataURL("image/jpeg", 0.95), "JPEG", margin, y, imgW, imgH);
        y += imgH + 6;
      }

      const svgEl = sheetEl.querySelector(".lochmuster-svg");
      if (svgEl) {
        doc.addPage("a4", pageFit.orientation === "quer" ? "landscape" : "portrait");
        const pW = doc.internal.pageSize.getWidth();
        const pH = doc.internal.pageSize.getHeight();
        const drawW = flat.w * pageFit.scale;
        const drawH = flat.h * pageFit.scale;
        await svg2pdf(svgEl, doc, { x: (pW - drawW) / 2, y: (pH - drawH) / 2, width: drawW, height: drawH });
        doc.setFontSize(8);
        doc.setTextColor(107, 101, 88);
        // "≈" fehlt in der WinAnsi-Kodierung der jsPDF-Standardschrift und würde
        // sonst als kaputtes Glyph erscheinen.
        doc.text(kennwerte.replace(/≈/g, "ca. "), margin, pH - 6, { maxWidth: pW - margin * 2 });
      }

      doc.save("stickkarten-anleitung.pdf");
    } finally {
      setPdfExporting(false);
    }
  };

  const astEdges = astschicht ? edges.slice(0, astCount) : [];
  const star1Edges = sternschicht ? edges.slice(astCount, astCount + star1Count) : [];
  const star2Edges = sternschicht2 ? edges.slice(astCount + star1Count, astCount + star1Count + star2Count) : [];

  // ---- Teil 2: repräsentativer Arm (Arm 1 von n) ----
  let armSection = null;
  if (astschicht && n > 0 && astCount > 0) {
    const armEdgeCount = astCount / n;
    const arm0Edges = astEdges.slice(0, armEdgeCount);
    // Volle Stichfolge über ALLE Astschicht-Kanten (wie im echten Generator) —
    // daraus Arm 1 herausschneiden. Jede Kante erzeugt genau 1 Stich-Segment
    // plus (außer der allerersten Kante) 1 vorangehenden Sprung, also erzeugen
    // die ersten `armEdgeCount` Kanten exakt die ersten (2*armEdgeCount-1)
    // Segmente; das direkt folgende Segment ist der reale Übergangssprung in
    // den nächsten Arm (falls es einen gibt) — kein Nachbau von Hand nötig.
    const fullAstSegs = buildStitchSequence(astEdges);
    const armSegCount = 2 * armEdgeCount - 1;
    const armSegs = fullAstSegs.slice(0, armSegCount);
    const transitionSeg = n > 1 ? fullAstSegs[armSegCount] || null : null;
    const armSteps = groupSteps(armSegs, transitionSeg);
    const armIds = [...new Set(arm0Edges.flatMap((e) => [e.a, e.b]))];
    const armPoints = {};
    armIds.forEach((id) => { armPoints[id] = nodes.get(id); });
    const diagram = buildStepDiagram({
      keyPrefix: "arm",
      points: armPoints,
      ids: armIds,
      steps: armSteps,
      labelOf: astNodeLabel,
      rotateAroundId: "C" in armPoints ? "C" : armIds[0],
      rotateDeg: 90,
      // maxW = tatsächlich nutzbare Breite im Dokument (Blattbreite 960px, abzüglich
      // Blatt- und Kartenpolster) — maxH bewusst großzügig: bei stark verzweigten
      // Ästen (viele Ebenen/Seitenäste) ist die Punktwolke nach der Rotation oft
      // näherungsweise quadratisch bis breit; ein knapper Höhen-Deckel (früher 320)
      // hätte dann VOR der Breite gegriffen und die Grafik unnötig verkleinert,
      // statt die volle Dokumentbreite auszunutzen.
      maxW: 856, maxH: 900, margin: 42,
      holeR: 5, holeFill: ANLEITUNG_FARBEN.paper, holeStroke: ANLEITUNG_FARBEN.ink,
      bend: { factor: 0.3, minB: 16, maxB: 30, step: 2 },
      vsColor: ANLEITUNG_FARBEN.vs, rsColor: ANLEITUNG_FARBEN.rs,
    });
    const fadenFlocke = fadenCmFor(astEdges.length ? buildStitchSequence(astEdges) : [], nodes);
    armSection = { armSteps, diagram, fadenFlocke, armEdgeCount };
  }

  // ---- Sternschicht(en): erste 2–3 Schritte grafisch, vollständige Tabelle ----
  function buildSternSection(keyPrefix, starEdges, level, teiler, k, farbe, farbeTint) {
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
      keyPrefix,
      points,
      ids,
      steps: shown,
      labelOf,
      backgroundEdges: starEdges,
      backgroundColor: farbe,
      maxW: 420, maxH: 420, margin: 40,
      holeR: 4, holeFill: ANLEITUNG_FARBEN.ink,
      labelFill: ANLEITUNG_FARBEN.sub, labelSize: 11,
      bend: { factor: 0.3, minB: 18, maxB: 38, step: 3 },
      vsColor: ANLEITUNG_FARBEN.vs, rsColor: ANLEITUNG_FARBEN.rs,
    });
    const fadenLaenge = fadenCmFor(starSegs, nodes);
    return { starSteps, diagram, fadenLaenge, ids, labelOf, level, teiler, k, farbe, farbeTint };
  }
  const stern1Section = sternschicht ? buildSternSection("s1", star1Edges, sternEbene, effTeiler1, k1, ANLEITUNG_FARBEN.stern1, ANLEITUNG_FARBEN.stern1Tint) : null;
  const stern2Section = sternschicht2 ? buildSternSection("s2", star2Edges, sternEbene2, effTeiler2, k2, ANLEITUNG_FARBEN.stern2, ANLEITUNG_FARBEN.stern2Tint) : null;

  const kennwerte = `Kartenformat ${format.w} × ${format.h} mm · Kreispunkte ${n}` + (astschicht ? ` · Ebenen ${ebenen}` : "") + ` · Mindestabstand ≈ ${MINDESTABSTAND.toFixed(1)} mm · Lochdurchmesser ≈ ${LOCH_DURCHMESSER.toFixed(2)} mm.`;

  // ---- Letzte Seite: Lochmuster (1:1, zum tatsächlichen Anstechen) ----
  const flat = computeFlatSheet(format, falzposition);
  const pageFit = pageFitFor(flat);
  const lochMargins = { top: RAND_MIN, right: RAND_MIN, bottom: RAND_MIN, left: RAND_MIN };
  if (falzposition === "links") lochMargins.left = FALZ_MIN;
  if (falzposition === "oben") lochMargins.top = FALZ_MIN;
  const lochUsableW = format.w - lochMargins.left - lochMargins.right;
  const lochUsableH = format.h - lochMargins.top - lochMargins.bottom;
  const alleLochPunkte = [...nodes.entries()];

  return (
    <div className="anleitung-root" style={anleitungStyles.overlay}>
      <style>{anleitungCss}</style>
      <div className="anleitung-toolbar no-print">
        <span>Druckbare Arbeitsanweisung</span>
        <div>
          <button className="btn" onClick={handleDirectPdfDownload} disabled={pdfExporting} title="Erzeugt direkt eine PDF-Datei und lädt sie herunter — ohne Druckdialog-Umweg">
            <FileDown size={14} style={{ marginRight: 6 }} /> {pdfExporting ? "PDF wird erstellt …" : "PDF herunterladen"}
          </button>
          <button className="btn btn-secondary" onClick={handleDownloadHtml} title="Lädt die Anleitung als eigenständige HTML-Datei herunter — darin (außerhalb dieser Vorschau) funktionieren Drucken und „Als PDF speichern“ normal">
            <Download size={14} style={{ marginRight: 6 }} /> Anleitung herunterladen
          </button>
          <button className="btn btn-secondary" onClick={handleDirectPrint} title="Direkter Druckversuch — funktioniert nur außerhalb einer eingebetteten Vorschau/Sandbox; hier ggf. ohne Wirkung, dann bitte den Download-Button nutzen">
            <Printer size={14} style={{ marginRight: 6 }} /> Direkt drucken (falls möglich)
          </button>
          <button className="btn btn-secondary" onClick={onClose}>
            <X size={14} style={{ marginRight: 6 }} /> Schließen
          </button>
        </div>
      </div>
      <div className="sheet">
        <div className="pdf-header">
          <h1>Stickkarten-Anleitung</h1>
          <p className="subtitle">Arbeitsanweisung auf Basis der aktuellen Einstellungen ({FORMATE[Object.keys(FORMATE).find((k) => FORMATE[k].w === format.w && FORMATE[k].h === format.h) || "custom"]?.label || `${format.w} × ${format.h} mm`}, Falz {falzposition}, Zoom {(zoom * 100).toFixed(0)} %).</p>
          <div className="legend">
            <span><span className="swatch" style={{ background: ANLEITUNG_FARBEN.vs }} />VS — sichtbarer Stich, Vorderseite (gerader Pfeil)</span>
            <span><span className="swatch" style={{ background: ANLEITUNG_FARBEN.rs }} />RS — verdeckter Sprung, Rückseite (gebogener Pfeil)</span>
            <span>Auf jeden Stich folgt unmittelbar ein Sprung — nur der letzte Schritt einer Schicht nicht.</span>
          </div>
        </div>

        {/* TEIL 1 */}
        <div className="teil">
          <div className="teil-label">Teil 1</div>
          <h2>Ebenen</h2>
          <p className="caption">
            {astschicht ? "Astschicht aktiv" : "Astschicht deaktiviert"}
            {sternschicht ? " · Sternschicht 1 aktiv" : " · Sternschicht 1 deaktiviert"}
            {sternschicht2 ? " · Sternschicht 2 aktiv" : " · Sternschicht 2 deaktiviert"}.
          </p>
          <LayerOverview nodes={nodes} astEdges={astEdges} star1Edges={star1Edges} star2Edges={star2Edges} astschicht={astschicht} sternschicht={sternschicht} sternschicht2={sternschicht2} />
        </div>

        {/* TEIL 2: Astschicht */}
        {astschicht && armSection && (
          <div className="teil">
            <div className="teil-label">Teil 2</div>
            <h2><span className="dotTag" style={{ background: ANLEITUNG_FARBEN.flocke }} />Flocke (Astschicht)</h2>
            <p className="caption">
              Punkt-Kürzel: Z = Zentrum · E1–E{ebenen - 1} = Ebene 1–{ebenen - 1}
              {astAktiv ? " · E{L}L/E{L}R = Seitenast links/rechts (ggf. mit Fraktal-Unterspitzen E{L}L.1a usw.)" : ""} · K = Kreispunkt.
              Ablauf für Ast 1 von {n} — für die übrigen {n - 1} Äste identisch wiederholen, jeweils um {(360 / n).toFixed(1)}° weitergedreht.
            </p>
            <div className="diagrams">
              <div className="card" style={{ background: ANLEITUNG_FARBEN.flockeTint }}>
                <svg width={armSection.diagram.width} height={armSection.diagram.height} viewBox={`0 0 ${armSection.diagram.width} ${armSection.diagram.height}`}>
                  {armSection.diagram.elements}
                </svg>
              </div>
            </div>
            <table className="stitchtable">
              <thead><tr><th>Schritt</th><th>VS</th><th>RS</th></tr></thead>
              <tbody>
                {armSection.armSteps.map((step, i) => (
                  <tr key={i}>
                    <td className="step">{i + 1}</td>
                    <td className="vs">{astNodeLabel(step.vs.a)} → {astNodeLabel(step.vs.b)}</td>
                    <td className="rs">{step.rs ? `${astNodeLabel(step.rs.a)} → ${astNodeLabel(step.rs.b)}${step.rsIsTransition ? ` (Start Ast 2 von ${n})` : ""}` : "–"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="fadenBox" style={{ background: ANLEITUNG_FARBEN.flockeTint, color: ANLEITUNG_FARBEN.flocke }}>
              Fadenlänge Flocke (alle {n} Äste, +15 %): ≈ {armSection.fadenFlocke.toFixed(0)} cm
            </div>
          </div>
        )}

        {/* TEIL 3+: Sternschicht(en) */}
        {[stern1Section && { section: stern1Section, titel: "Stern 1", nr: astschicht ? 3 : 2 }, stern2Section && { section: stern2Section, titel: "Stern 2", nr: astschicht ? 4 : 3 }]
          .filter(Boolean)
          .map(({ section, titel, nr }) => (
            <div className="teil" key={titel}>
              <div className="teil-label">Teil {nr}</div>
              <h2><span className="dotTag" style={{ background: section.farbe }} />{titel}</h2>
              <p className="caption">
                Verbindet {section.ids.length} Punkte{astschicht ? ` auf Ebene ${section.level}` : ""}
                {section.teiler > 1 ? ` (jeder ${section.teiler}. Kreispunkt)` : ""}, Schrittweite {section.k}. Blasses Muster im
                Hintergrund = vollständiger Stern; nur die ersten {Math.min(3, section.starSteps.length)} Schritte sind grafisch
                dargestellt (Rest wiederholt das Prinzip).
              </p>
              <div className="diagrams">
                <div className="card" style={{ background: section.farbeTint }}>
                  <svg width={section.diagram.width} height={section.diagram.height} viewBox={`0 0 ${section.diagram.width} ${section.diagram.height}`}>
                    {section.diagram.elements}
                  </svg>
                </div>
              </div>
              <table className="stitchtable">
                <thead><tr><th>Schritt</th><th>VS</th><th>RS</th></tr></thead>
                <tbody>
                  {section.starSteps.map((step, i) => (
                    <tr key={i}>
                      <td className="step">{i + 1}</td>
                      <td className="vs">{section.labelOf(step.vs.a)} → {section.labelOf(step.vs.b)}</td>
                      <td className="rs">{step.rs ? `${section.labelOf(step.rs.a)} → ${section.labelOf(step.rs.b)}` : "– (letzter Schritt dieser Schicht)"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="fadenBox" style={{ background: section.farbeTint, color: section.farbe }}>
                Fadenlänge {titel} (+15 %): ≈ {section.fadenLaenge.toFixed(0)} cm
              </div>
            </div>
          ))}

        {!sternschicht2 && (
          <div className="teil">
            <div className="teil-label">Teil {astschicht ? 4 : 3}</div>
            <h2><span className="dotTag" style={{ background: ANLEITUNG_FARBEN.stern2 }} />Stern 2</h2>
            <div className="noteBox">Deaktiviert (zweite Sternschicht ist in den aktuellen Einstellungen nicht aktiv) — keine Daten, kein Fadenbedarf.</div>
          </div>
        )}

        {/* Letzte Seite: eigenes, echtes A4-Blatt mit dem Zuschnitt maßstabsgetreu
            zentriert darin — zum Ausdrucken und tatsächlichen Anstechen der
            Löcher (kein Illustrationsmaßstab wie bei den Diagrammen oben). */}
        <div className={`teil lochmuster-teil lochmuster-${pageFit.orientation}`}>
          <div className="teil-label">Letzte Seite</div>
          <h2>Lochmuster (1:1)</h2>
          <p className="caption">
            Maßstabsgetreuer Zuschnitt {flat.w} × {flat.h} mm{flat.foldAxis ? `, gefaltet ${falzposition === "links" ? "links" : "oben"} (gestrichelte Falzlinie)` : " (ungefaltet)"} —
            das vordere, bestickte Panel ist gerahmt dargestellt; alle {alleLochPunkte.length} Löcher sind in tatsächlicher Größe (Ø {LOCH_DURCHMESSER.toFixed(2)} mm) eingezeichnet.
            {pageFit.fits
              ? " Beim Drucken unbedingt „Tatsächliche Größe“ bzw. 100 % wählen, nicht „An Seite anpassen“ — sonst stimmen die Lochpositionen nicht mehr."
              : ` Dieser Zuschnitt ist größer als eine A4-Seite — die Darstellung ist hier auf ${(pageFit.scale * 100).toFixed(0)} % verkleinert und daher NICHT zum direkten Anstechen geeignet (zum Übertragen entsprechend vergrößert nachdrucken oder auf mehrere Blätter aufteilen).`}
          </p>
          <div className="lochmuster-wrap">
            <svg
              className="lochmuster-svg"
              width={`${flat.w}mm`}
              height={`${flat.h}mm`}
              viewBox={`0 0 ${flat.w} ${flat.h}`}
              style={{ maxWidth: "none" }}
            >
              <rect x={0} y={0} width={flat.w} height={flat.h} fill="none" stroke={ANLEITUNG_FARBEN.ink} strokeWidth={0.3} />
              {flat.foldAxis === "v" && <line x1={flat.foldPos} y1={0} x2={flat.foldPos} y2={flat.h} stroke={ANLEITUNG_FARBEN.ink} strokeWidth={0.25} strokeDasharray="3,2" />}
              {flat.foldAxis === "h" && <line x1={0} y1={flat.foldPos} x2={flat.w} y2={flat.foldPos} stroke={ANLEITUNG_FARBEN.ink} strokeWidth={0.25} strokeDasharray="3,2" />}
              <rect x={flat.offX} y={flat.offY} width={format.w} height={format.h} fill="none" stroke={ANLEITUNG_FARBEN.ink} strokeWidth={0.25} />
              <rect
                x={flat.offX + lochMargins.left}
                y={flat.offY + lochMargins.top}
                width={lochUsableW}
                height={lochUsableH}
                fill="none"
                stroke={ANLEITUNG_FARBEN.ink}
                strokeOpacity={0.35}
                strokeWidth={0.2}
                strokeDasharray="1.5,1.5"
              />
              {alleLochPunkte.map(([id, p]) => (
                <circle key={id} cx={flat.offX + p.x} cy={flat.offY + p.y} r={LOCH_DURCHMESSER / 2} fill="rgba(0,0,0,0.6)" />
              ))}
            </svg>
          </div>
        </div>

        <footer>{kennwerte}</footer>
      </div>
    </div>
  );
}

function LayerOverview({ nodes, astEdges, star1Edges, star2Edges, astschicht, sternschicht, sternschicht2 }) {
  const allPts = [...nodes.values()];
  if (!allPts.length) return null;
  const xs = allPts.map((p) => p.x), ys = allPts.map((p) => p.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
  const bboxW = Math.max(maxX - minX, 1e-6), bboxH = Math.max(maxY - minY, 1e-6);
  const iconScale = 76 / Math.max(bboxW, bboxH);
  const offX = 50 - ((minX + maxX) / 2) * iconScale;
  const offY = 50 - ((minY + maxY) / 2) * iconScale;
  const xf = (p) => xformPt(p, iconScale, 0, 0, offX, offY);
  const drawAst = (color, w) => astEdges.map((e, i) => {
    const a = xf(nodes.get(e.a)), b = xf(nodes.get(e.b));
    return <line key={`a${i}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={color} strokeWidth={w} />;
  });
  const drawStar = (edgesArr, color, w) => edgesArr.map((e, i) => {
    const a = xf(nodes.get(e.a)), b = xf(nodes.get(e.b));
    return <line key={`s${i}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={color} strokeWidth={w} opacity={0.9} />;
  });
  const Card = ({ title, children, inactive }) => (
    <div className="layerCard">
      <div className="card" style={{ width: 130, height: 130, display: "flex", alignItems: "center", justifyContent: "center", position: "relative", background: "#fff" }}>
        <svg width={100} height={100} viewBox="0 0 100 100">{children}</svg>
        {inactive && <div className="inactiveTag">deaktiviert</div>}
      </div>
      <div className="card-title">{title}</div>
    </div>
  );
  return (
    <div className="layerRow">
      <Card title="Flocke" inactive={!astschicht}>{astschicht && drawAst(ANLEITUNG_FARBEN.flocke, 1.8)}</Card>
      <Card title="Stern 1" inactive={!sternschicht}>{sternschicht && drawStar(star1Edges, ANLEITUNG_FARBEN.stern1, 1.6)}</Card>
      <Card title="Stern 2" inactive={!sternschicht2}>{sternschicht2 && drawStar(star2Edges, ANLEITUNG_FARBEN.stern2, 1.6)}</Card>
      <div className="plus">=</div>
      <Card title="Gesamtbild">
        {astschicht && drawAst(ANLEITUNG_FARBEN.flocke, 1.6)}
        {sternschicht && drawStar(star1Edges, ANLEITUNG_FARBEN.stern1, 1.4)}
        {sternschicht2 && drawStar(star2Edges, ANLEITUNG_FARBEN.stern2, 1.4)}
      </Card>
    </div>
  );
}

const anleitungCss = `
  .anleitung-toolbar{ position:sticky; top:0; z-index:5; display:flex; align-items:center; justify-content:space-between;
    background:#132437; color:#eef3f7; padding:8px 16px; font-family:system-ui,sans-serif; font-size:13px; }
  .anleitung-toolbar .btn{ background:#d9b86a; border:none; color:#10203a; border-radius:6px; padding:6px 12px; font-size:12.5px;
    font-weight:600; display:inline-flex; align-items:center; cursor:pointer; margin-left:8px; }
  .anleitung-toolbar .btn-secondary{ background:#2c4460; color:#eef3f7; }
  .sheet{ max-width:960px; margin:0 auto; background:#faf6ee; border:1px solid #c9c0ac; border-radius:4px; padding:36px 40px 48px;
    box-shadow:0 2px 18px rgba(0,0,0,0.12); color:#26241f; font-family:Georgia,'Iowan Old Style','Palatino Linotype',serif; }
  .sheet h1{ font-size:22px; margin:0 0 4px; letter-spacing:0.3px; }
  .sheet .subtitle{ font-size:12.5px; color:#6b6558; margin:0 0 8px; font-family:system-ui,sans-serif; line-height:1.55; }
  .sheet .legend{ display:flex; gap:18px; flex-wrap:wrap; font-family:system-ui,sans-serif; font-size:11.5px; color:#26241f;
    margin:0 0 28px; padding:10px 14px; background:#f1ead9; border-radius:8px; }
  .sheet .legend span{ display:inline-flex; align-items:center; gap:6px; }
  .sheet .swatch{ width:20px; height:3px; border-radius:2px; display:inline-block; }
  .sheet .teil{ margin-top:34px; padding-top:20px; border-top:1px solid #c9c0ac; }
  .sheet .teil:first-of-type{ margin-top:0; padding-top:0; border-top:none; }
  .sheet .teil-label{ font-size:10.5px; letter-spacing:1.5px; text-transform:uppercase; color:#6b6558; font-family:system-ui,sans-serif; font-weight:600; margin-bottom:4px; }
  .sheet h2{ font-size:18px; margin:0 0 6px; display:flex; align-items:center; gap:8px; }
  .sheet .dotTag{ width:11px; height:11px; border-radius:50%; display:inline-block; }
  .sheet .caption{ font-size:12px; color:#6b6558; font-family:system-ui,sans-serif; line-height:1.5; margin:0 0 10px; }
  .sheet .diagrams{ display:flex; gap:18px; flex-wrap:wrap; align-items:flex-start; }
  .sheet .card{ border:1px solid #c9c0ac; border-radius:8px; padding:12px; flex:0 0 auto; }
  .sheet .card-title{ font-size:11px; font-family:system-ui,sans-serif; color:#6b6558; text-align:center; margin:8px 0 0; text-transform:uppercase; letter-spacing:0.5px; }
  .sheet svg{ display:block; max-width:100%; height:auto; }
  .sheet .layerRow{ display:flex; gap:16px; flex-wrap:wrap; align-items:center; }
  .sheet .layerCard{ width:130px; text-align:center; }
  .sheet .plus{ font-size:20px; color:#6b6558; font-family:system-ui,sans-serif; }
  .sheet .inactiveTag{ position:absolute; bottom:6px; left:0; right:0; font-size:9px; letter-spacing:0.4px; color:#6b6558; font-family:system-ui,sans-serif; }
  .sheet table.stitchtable{ border-collapse:collapse; width:100%; margin:8px 0 4px; font-family:system-ui,sans-serif; font-size:12.5px; }
  .sheet table.stitchtable th{ text-align:left; font-size:10.5px; text-transform:uppercase; letter-spacing:0.6px; color:#6b6558; border-bottom:2px solid #c9c0ac; padding:6px 10px; }
  .sheet table.stitchtable td{ padding:7px 10px; border-bottom:1px solid #c9c0ac; vertical-align:top; }
  .sheet table.stitchtable td.step{ color:#26241f; font-weight:700; width:34px; }
  .sheet table.stitchtable td.vs{ color:#2f7a4d; font-weight:600; }
  .sheet table.stitchtable td.rs{ color:#b23b3b; font-weight:600; }
  .sheet .fadenBox{ margin-top:12px; font-family:system-ui,sans-serif; font-size:13px; padding:8px 12px; border-radius:6px; display:inline-block; }
  .sheet .noteBox{ border:1px dashed #c9c0ac; border-radius:8px; padding:12px 14px; font-family:system-ui,sans-serif; font-size:12px; color:#6b6558; }
  .sheet footer{ margin-top:36px; padding-top:14px; border-top:1px dashed #c9c0ac; font-size:11.5px; color:#6b6558; font-family:system-ui,sans-serif; line-height:1.6; }
  .lochmuster-wrap{ overflow-x:auto; padding:4px 0 8px; }
  .lochmuster-svg{ display:block; margin:0 auto; }

  @page{ size:A4; margin:14mm; }
  /* Eigenes Seitenprofil fürs Lochmuster: knapperer Rand und ggf. Querformat,
     damit der 1:1-Zuschnitt (oft breiter als eine normale Textseite) noch
     unskaliert auf ein A4-Blatt passt. Named-page-Zuordnung ist eine
     CSS-Paged-Media-Funktion mit bislang uneinheitlicher Browser-Unterstützung
     (in Chrome/Edge beim Drucken bzw. „Als PDF speichern“ zuverlässig; andere
     Engines ignorieren sie und fallen auf das @page-Standardprofil oben
     zurück — die Darstellung bleibt dann korrekt, ggf. nur mit dem normalen
     14-mm-Rand statt 10 mm). */
  @page lochmuster-hoch{ size:A4 portrait; margin:10mm; }
  @page lochmuster-quer{ size:A4 landscape; margin:10mm; }
  .lochmuster-teil{ break-before:page; }
  .lochmuster-hoch{ page:lochmuster-hoch; }
  .lochmuster-quer{ page:lochmuster-quer; }
  @media print{
    .no-print{ display:none !important; }
    body *{ visibility:hidden; }
    .anleitung-overlay, .anleitung-overlay *{ visibility:visible; }
    .anleitung-overlay{ position:static; left:auto; top:auto; background:#fff; }
    /* Der Wurzel-Container ist fürs Bildschirm-Overlay fixiert/auf Viewport-Höhe
       begrenzt (position:fixed + overflow:auto) — beim Druck muss er sich auf
       die tatsächliche (ggf. mehrseitige) Dokumenthöhe ausdehnen können, sonst
       würde nur der sichtbare Bildschirmausschnitt gedruckt. Inline-Styles
       überschreiben wir daher mit !important. */
    .anleitung-root{ position:static !important; inset:auto !important; overflow:visible !important; height:auto !important; background:#fff !important; }
    .sheet{ box-shadow:none; border:none; max-width:100%; padding:0; }
    .sheet h2{ break-after:avoid-page; }
    .sheet .layerRow, .sheet .diagrams, .sheet .card, .sheet .fadenBox, .sheet .noteBox, .sheet .legend{ break-inside:avoid-page; }
    /* Tabellen dürfen über mehrere Seiten laufen (können bei vielen Stichen lang
       werden) — nur einzelne Zeilen bleiben zusammen, und die Kopfzeile
       wiederholt sich automatisch auf jeder Folgeseite. */
    .sheet table.stitchtable{ break-inside:auto; }
    .sheet table.stitchtable thead{ display:table-header-group; }
    .sheet table.stitchtable tr{ break-inside:avoid; }
  }
`;

const anleitungStyles = {
  overlay: { position: "fixed", inset: 0, zIndex: 50, background: "#e8e2d4", overflowY: "auto", fontFamily: "system-ui,sans-serif" },
};

/* ---------------------------------------------------------------------- */
/* Hauptkomponente                                                        */
/* ---------------------------------------------------------------------- */

export default function StickkartenGeneratorV4() {
  const [formatPreset, setFormatPreset] = useState("a6-hoch");
  const [customW, setCustomW] = useState(105);
  const [customH, setCustomH] = useState(148);
  const [falzposition, setFalzposition] = useState("links");

  const [n, setN] = useState(8);
  const [zoom, setZoom] = useState(1);

  const [astschicht, setAstschicht] = useState(true);
  const [ebenen, setEbenen] = useState(4);
  const [astAktiv, setAstAktiv] = useState(true);
  const [astWinkel, setAstWinkel] = useState(55);
  const [astLaenge, setAstLaenge] = useState(0.7);
  const [astWachstum, setAstWachstum] = useState(0.3);
  const [fraktalTiefe, setFraktalTiefe] = useState(0);
  const [fraktalSkalierung, setFraktalSkalierung] = useState(0.5);

  const [sternschicht, setSternschicht] = useState(true);
  const [sternEbene, setSternEbene] = useState(2);
  const [sternTeiler, setSternTeiler] = useState(1);
  const [k1, setK1] = useState(3);
  const [sternschicht2, setSternschicht2] = useState(false);
  const [sternEbene2, setSternEbene2] = useState(4);
  const [sternTeiler2, setSternTeiler2] = useState(1);
  const [sternVersatz2, setSternVersatz2] = useState(0);
  const [k2, setK2] = useState(1);
  // Seitenäste beim Sternlevel weglassen — je Sternschicht: "keine" (Standard),
  // "exakt" (nur die Äste genau auf dem Sternlevel) oder "kleinerGleich" (alle
  // Äste von Ebene 2 bis einschließlich des Sternlevels).
  const [astAusblendung1, setAstAusblendung1] = useState("keine");
  const [astAusblendung2, setAstAusblendung2] = useState("keine");

  const [kartonfarbe, setKartonfarbe] = useState("tanne");
  const [fadenfarbe, setFadenfarbe] = useState("gold");
  const [zeigeVorschau, setZeigeVorschau] = useState(true);
  const [zeigeSpruenge, setZeigeSpruenge] = useState(true);
  const [zeigeEinstellungen, setZeigeEinstellungen] = useState(false);
  const [zeigeAnleitung, setZeigeAnleitung] = useState(false);

  const [currentStep, setCurrentStep] = useState(0);
  const [playing, setPlaying] = useState(false);

  const format = formatPreset === "custom" ? { w: customW, h: customH } : FORMATE[formatPreset];
  const margins = useMemo(() => {
    const m = { top: RAND_MIN, right: RAND_MIN, bottom: RAND_MIN, left: RAND_MIN };
    if (falzposition === "links") m.left = FALZ_MIN;
    if (falzposition === "oben") m.top = FALZ_MIN;
    return m;
  }, [falzposition]);

  const usableW = Math.max(1, format.w - margins.left - margins.right);
  const usableH = Math.max(1, format.h - margins.top - margins.bottom);
  const cx = margins.left + usableW / 2;
  const cy = margins.top + usableH / 2;
  const Rmax = Math.min(usableW, usableH) / 2;

  const teilerOptionen = useMemo(() => divisorsOf(n), [n]);
  const effTeiler1 = teilerOptionen.includes(sternTeiler) ? sternTeiler : 1;
  const sternPunkte1 = n / effTeiler1;
  const kMax1 = Math.max(1, Math.floor(sternPunkte1 / 2) - (astschicht ? 1 : 0));
  const effTeiler2 = teilerOptionen.includes(sternTeiler2) ? sternTeiler2 : 1;
  const sternPunkte2 = n / effTeiler2;
  const kMax2 = Math.max(1, Math.floor(sternPunkte2 / 2) - (astschicht ? 1 : 0));

  // Anwendbarkeit der "Seitenäste weglassen"-Option je Sternschicht — nur
  // anzeigen/anwenden, wenn sie bei den aktuellen Einstellungen (Ebenen,
  // Seitenäste an, Sternlevel) tatsächlich etwas bewirkt.
  const branchLevels = useMemo(() => astBranchLevels(ebenen), [ebenen]);
  const sternEbeneEff1 = Math.min(sternEbene, ebenen);
  const sternEbeneEff2 = Math.min(sternEbene2, ebenen);
  const ausblendungBasis = astschicht && astAktiv && branchLevels.length > 0;
  const skip1ExaktMoeglich = ausblendungBasis && sternschicht && branchLevels.includes(sternEbeneEff1);
  const skip1LeMoeglich = ausblendungBasis && sternschicht && sternEbeneEff1 >= 2;
  const skip1CapLvl = Math.min(sternEbeneEff1, ebenen - 1);
  const skip2ExaktMoeglich = ausblendungBasis && sternschicht && sternschicht2 && branchLevels.includes(sternEbeneEff2);
  const skip2LeMoeglich = ausblendungBasis && sternschicht && sternschicht2 && sternEbeneEff2 >= 2;
  const skip2CapLvl = Math.min(sternEbeneEff2, ebenen - 1);

  // Die beiden Sternschicht-Optionen wirken additiv: jede Ebene, die von
  // mindestens einer der beiden aktiven Optionen betroffen ist, verliert ihre
  // Seitenäste (samt Fraktal-Spitzen).
  const unterdrueckteEbenen = useMemo(() => {
    const set = new Set();
    if (!ausblendungBasis) return set;
    if (sternschicht) {
      if (astAusblendung1 === "exakt" && branchLevels.includes(sternEbeneEff1)) set.add(sternEbeneEff1);
      if (astAusblendung1 === "kleinerGleich") branchLevels.forEach((L) => { if (L <= sternEbeneEff1) set.add(L); });
    }
    if (sternschicht && sternschicht2) {
      if (astAusblendung2 === "exakt" && branchLevels.includes(sternEbeneEff2)) set.add(sternEbeneEff2);
      if (astAusblendung2 === "kleinerGleich") branchLevels.forEach((L) => { if (L <= sternEbeneEff2) set.add(L); });
    }
    return set;
  }, [ausblendungBasis, branchLevels, sternschicht, sternschicht2, astAusblendung1, astAusblendung2, sternEbeneEff1, sternEbeneEff2]);

  const Rmin = useMemo(() => {
    let r = 12;
    r = Math.max(r, (MINDESTABSTAND * n) / (2 * Math.PI));
    if (astschicht) r = Math.max(r, MINDESTABSTAND * ebenen);
    return r;
  }, [n, astschicht, ebenen]);
  const formatOk = Rmin <= Rmax;
  const R = formatOk ? Rmin + zoom * (Rmax - Rmin) : Rmax;

  const { nodes, edges, segments, astCount, star1Count, star2Count } = useMemo(() => {
    const { nodes, edges, astCount, star1Count, star2Count } = buildGraph({
      n,
      R,
      cx,
      cy,
      astschicht,
      ebenen,
      astAktiv,
      astWinkel,
      astLaenge,
      astWachstum,
      fraktalTiefe,
      fraktalSkalierung,
      sternschicht,
      sternEbene: Math.min(sternEbene, ebenen),
      sternTeiler: effTeiler1,
      k1: Math.min(k1, kMax1),
      sternschicht2,
      sternEbene2: Math.min(sternEbene2, ebenen),
      sternTeiler2: effTeiler2,
      sternVersatz2,
      k2: Math.min(k2, kMax2),
      unterdrueckteEbenen,
    });
    const segments = buildStitchSequence(edges);
    return { nodes, edges, segments, astCount, star1Count, star2Count };
  }, [n, R, cx, cy, astschicht, ebenen, astAktiv, astWinkel, astLaenge, astWachstum, fraktalTiefe, fraktalSkalierung, sternschicht, sternEbene, effTeiler1, k1, kMax1, sternschicht2, sternEbene2, effTeiler2, sternVersatz2, k2, kMax2, unterdrueckteEbenen]);

  const stitchSegments = segments.filter((s) => s.type === "stitch");
  const jumpSegments = segments.filter((s) => s.type === "jump");
  const frontLength = stitchSegments.reduce((sum, s) => sum + dist(nodes.get(s.a), nodes.get(s.b)), 0);
  const jumpLength = jumpSegments.reduce((sum, s) => sum + dist(nodes.get(s.a), nodes.get(s.b)), 0);
  const maxStep = segments.length;

  useEffect(() => {
    setCurrentStep(maxStep);
    setPlaying(false);
  }, [nodes, edges]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!playing) return;
    if (currentStep >= maxStep) {
      setPlaying(false);
      return;
    }
    const t = setTimeout(() => setCurrentStep((s) => Math.min(maxStep, s + 1)), 45);
    return () => clearTimeout(t);
  }, [playing, currentStep, maxStep]);

  /* ---------------- Abstands-Klassifizierung je Punkt ---------------- */

  const { pointSeverity, hasCritical, hasModerate } = useMemo(() => {
    const sev = new Map();
    const pts = [...nodes.entries()];
    for (let i = 0; i < pts.length; i++) {
      let nearest = Infinity;
      for (let j = 0; j < pts.length; j++) {
        if (i === j) continue;
        const d = dist(pts[i][1], pts[j][1]);
        if (d < nearest) nearest = d;
      }
      let s = "ok";
      if (nearest < MINDESTABSTAND) s = "critical";
      else if (nearest < MINDESTABSTAND * MODERAT_FAKTOR) s = "moderate";
      sev.set(pts[i][0], s);
    }
    const vals = [...sev.values()];
    return { pointSeverity: sev, hasCritical: vals.includes("critical"), hasModerate: vals.includes("moderate") };
  }, [nodes]);

  const warnungen = [];
  if (!astschicht && !sternschicht) warnungen.push("Aktiviere mindestens eine Musterschicht (Astschicht oder Sternschicht).");
  if (!formatOk) warnungen.push("Bei dieser Achsen-/Ebenenzahl passt kein gültiger Mindestabstand auf diese Karte.");
  if (stitchSegments.length > STICH_LIMIT) warnungen.push(`${stitchSegments.length} Stiche — mehr als das Richtmaß von ${STICH_LIMIT}. Für eine handhabbare Karte Kreispunkte oder Ebenen reduzieren.`);
  if (hasCritical) warnungen.push(`Manche Löcher liegen unter dem Mindestabstand (${MINDESTABSTAND.toFixed(1)} mm) — Stiche werden nicht angezeigt, bis der Zoom verkleinert wird.`);
  else if (hasModerate) warnungen.push(`Manche Löcher liegen nur knapp über dem Mindestabstand (${MINDESTABSTAND.toFixed(1)} mm) — betroffene Punkte sind markiert.`);

  const cardHex = KARTONFARBEN[kartonfarbe].hex;
  const threadPrimary = FADENFARBEN[fadenfarbe].primary;

  const exportSVG = useCallback(() => {
    const lines = stitchSegments
      .map((s) => {
        const a = nodes.get(s.a);
        const b = nodes.get(s.b);
        return `<line x1="${a.x.toFixed(2)}" y1="${a.y.toFixed(2)}" x2="${b.x.toFixed(2)}" y2="${b.y.toFixed(2)}" stroke="${threadPrimary}" stroke-width="0.35" stroke-linecap="round" />`;
      })
      .join("\n");
    const holes = Array.from(nodes.values())
      .map((p) => `<circle cx="${p.x.toFixed(2)}" cy="${p.y.toFixed(2)}" r="${(LOCH_DURCHMESSER / 2).toFixed(2)}" fill="rgba(0,0,0,0.4)" />`)
      .join("\n");
    const foldLine =
      falzposition === "links"
        ? `<line x1="0.5" y1="0" x2="0.5" y2="${format.h}" stroke="#000" stroke-opacity="0.35" stroke-width="0.3" stroke-dasharray="2,1.5"/>`
        : falzposition === "oben"
        ? `<line x1="0" y1="0.5" x2="${format.w}" y2="0.5" stroke="#000" stroke-opacity="0.35" stroke-width="0.3" stroke-dasharray="2,1.5"/>`
        : "";
    const svgString = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${format.w}mm" height="${format.h}mm" viewBox="0 0 ${format.w} ${format.h}">
  <rect x="0" y="0" width="${format.w}" height="${format.h}" fill="${cardHex}" />
  ${foldLine}
  ${lines}
  ${holes}
</svg>`;
    const blob = new Blob([svgString], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "stickvorlage.svg";
    a.click();
    URL.revokeObjectURL(url);
  }, [stitchSegments, nodes, cardHex, threadPrimary, falzposition, format]);

  return (
    <div style={styles.outer}>
      <style>{cssReset}</style>
      <div style={styles.frame}>
        <header style={styles.header}>
          <h1 style={styles.h1}>Stickkarten-Generator</h1>
          <div style={{ display: "flex", gap: 6 }}>
            <button style={styles.gearBtn} onClick={() => setZeigeAnleitung(true)} title="Druckbare Anleitung">
              <Printer size={16} />
            </button>
            <button style={styles.gearBtn} onClick={() => setZeigeEinstellungen((v) => !v)}>
              <Settings size={16} />
            </button>
          </div>
        </header>

        {zeigeEinstellungen && (
          <div style={styles.settingsOverlay}>
            <div style={styles.settingsPanel}>
              <div style={styles.settingsPanelHead}>
                <span style={styles.sectionTitle}>Einstellungen</span>
                <button style={styles.closeBtn} onClick={() => setZeigeEinstellungen(false)}>
                  <X size={14} />
                </button>
              </div>
              <Field label="Kartenformat">
                <select style={styles.select} value={formatPreset} onChange={(e) => setFormatPreset(e.target.value)}>
                  {Object.entries(FORMATE).map(([k, v]) => (
                    <option key={k} value={k}>{v.label}</option>
                  ))}
                </select>
              </Field>
              {formatPreset === "custom" && (
                <Row>
                  <Field label="Breite (mm)"><input type="number" style={styles.input} value={customW} onChange={(e) => setCustomW(Number(e.target.value))} /></Field>
                  <Field label="Höhe (mm)"><input type="number" style={styles.input} value={customH} onChange={(e) => setCustomH(Number(e.target.value))} /></Field>
                </Row>
              )}
              <Field label="Falzposition">
                <select style={styles.select} value={falzposition} onChange={(e) => setFalzposition(e.target.value)}>
                  <option value="links">Links</option>
                  <option value="oben">Oben</option>
                  <option value="keine">Keine (Einzelkarte)</option>
                </select>
              </Field>
              <Slider label={`Zoom: ${(zoom * 100).toFixed(0)} %`} min={0} max={1} step={0.02} value={zoom} onChange={setZoom} />
              <p style={styles.hint}>
                Radius {R.toFixed(0)} mm · Faden {FADEN_STRAENGE}-strängig · Karton 250 g/m² · Rand min. {RAND_MIN} mm, Falz min. {FALZ_MIN} mm · Mindestabstand {MINDESTABSTAND.toFixed(1)} mm.
              </p>

              <div style={{ marginTop: 10, borderTop: "1px solid #223751", paddingTop: 8 }}>
                <span style={styles.sectionTitle}>Darstellung</span>
                <Row>
                  <Field label="Kartonfarbe">
                    <select style={styles.select} value={kartonfarbe} onChange={(e) => setKartonfarbe(e.target.value)}>
                      {Object.entries(KARTONFARBEN).map(([k, v]) => (<option key={k} value={k}>{v.label}</option>))}
                    </select>
                  </Field>
                  <Field label="Fadenfarbe">
                    <select style={styles.select} value={fadenfarbe} onChange={(e) => setFadenfarbe(e.target.value)}>
                      {Object.entries(FADENFARBEN).map(([k, v]) => (<option key={k} value={k}>{v.label}</option>))}
                    </select>
                  </Field>
                </Row>
                <div style={styles.checkboxRow}>
                  <input type="checkbox" id="vorschau" checked={zeigeVorschau} onChange={(e) => setZeigeVorschau(e.target.checked)} />
                  <label htmlFor="vorschau" style={{ marginLeft: 6 }}>Restmuster als Vorschau</label>
                </div>
                <div style={styles.checkboxRow}>
                  <input type="checkbox" id="spruenge" checked={zeigeSpruenge} onChange={(e) => setZeigeSpruenge(e.target.checked)} />
                  <label htmlFor="spruenge" style={{ marginLeft: 6 }}>Rückseiten-Sprünge anzeigen</label>
                </div>
              </div>
            </div>
          </div>
        )}

        <div style={styles.layout}>
          {/* ---------------- Sidebar (breiter, gruppierte Regler) ---------------- */}
          <aside style={styles.sidebar}>
            <Section title="Grundform">
              <Slider label={`Kreispunkte: ${n}`} min={3} max={16} value={n} onChange={setN} />
            </Section>

            <Section title="Astschicht (Baum)">
              <Row>
                <div style={styles.checkboxRow}>
                  <input type="checkbox" id="astschicht" checked={astschicht} onChange={(e) => setAstschicht(e.target.checked)} />
                  <label htmlFor="astschicht" style={{ marginLeft: 6 }}>aktiv</label>
                </div>
                {astschicht && (
                  <div style={styles.checkboxRow}>
                    <input type="checkbox" id="astAktiv" checked={astAktiv} onChange={(e) => setAstAktiv(e.target.checked)} />
                    <label htmlFor="astAktiv" style={{ marginLeft: 6 }}>Seitenäste</label>
                  </div>
                )}
              </Row>
              {astschicht && (
                <>
                  <Row cols={astAktiv ? 4 : 1}>
                    <Slider label={`Ebenen: ${ebenen}`} min={1} max={6} value={ebenen} onChange={setEbenen} />
                    {astAktiv && <Slider label={`Astwinkel: ${astWinkel}°`} min={3} max={55} value={astWinkel} onChange={setAstWinkel} />}
                    {astAktiv && <Slider label={`Astlänge: ${(astLaenge * 100).toFixed(0)} %`} min={0.2} max={2} step={0.05} value={astLaenge} onChange={setAstLaenge} />}
                    {astAktiv && <Slider label={`Wachstum n. außen: ${(astWachstum * 100).toFixed(0)} %`} min={0} max={1.5} step={0.05} value={astWachstum} onChange={setAstWachstum} />}
                  </Row>
                </>
              )}
            </Section>

            <Section title="Sternschicht — Schicht 1">
              <div style={styles.checkboxRow}>
                <input type="checkbox" id="sternschicht" checked={sternschicht} onChange={(e) => setSternschicht(e.target.checked)} />
                <label htmlFor="sternschicht" style={{ marginLeft: 6 }}>aktiv</label>
              </div>
              {sternschicht && (
                <>
                  <Row cols={3}>
                    {astschicht && <Slider label={`Sternebene: ${Math.min(sternEbene, ebenen)} (${ebenen}=Ring)`} min={1} max={ebenen} value={Math.min(sternEbene, ebenen)} onChange={setSternEbene} />}
                    <Field label={`Sternstrahlen: ${sternPunkte1}`}>
                      <select style={styles.select} value={effTeiler1} onChange={(e) => setSternTeiler(Number(e.target.value))}>
                        {teilerOptionen.map((t) => (<option key={t} value={t}>{n / t} Strahlen{t === 1 ? " (alle)" : ` (jeder ${t}.)`}</option>))}
                      </select>
                    </Field>
                    {kMax1 > 1 ? (
                      <Slider label={`Schrittweite: ${Math.min(k1, kMax1)}`} min={1} max={kMax1} value={Math.min(k1, kMax1)} onChange={setK1} />
                    ) : (
                      <Field label="Schrittweite">
                        <p style={styles.hint}>nur 1 Verbindungsart möglich (zu wenige Sternstrahlen)</p>
                      </Field>
                    )}
                  </Row>
                  {(skip1ExaktMoeglich || skip1LeMoeglich) && (
                    <Field label="Seitenäste bei diesem Sternlevel">
                      {/* key erzwingt einen Neuaufbau, sobald sich die betroffene Ebene ändert —
                          manche Browser aktualisieren sonst den sichtbaren Text der aktuell
                          ausgewählten <option> im geschlossenen Dropdown nicht zuverlässig
                          (rein visuell; die Auswertung selbst war stets korrekt). Zusätzlich
                          bleiben die Options-Texte bewusst generisch statt die Ebenenzahl zu
                          nennen — die konkrete Ebene steht stattdessen im Hinweistext darunter. */}
                      <select key={`sk1-${sternEbeneEff1}`} style={styles.select} value={astAusblendung1} onChange={(e) => setAstAusblendung1(e.target.value)}>
                        <option value="keine">Alle behalten</option>
                        {skip1ExaktMoeglich && <option value="exakt">Nur auf Sternlevel weglassen</option>}
                        {skip1LeMoeglich && <option value="kleinerGleich">Sternlevel und darunter weglassen</option>}
                      </select>
                      <p style={styles.hint}>
                        {astAusblendung1 === "exakt" && skip1ExaktMoeglich && `Betrifft Ebene ${sternEbeneEff1}.`}
                        {astAusblendung1 === "kleinerGleich" && skip1LeMoeglich && `Betrifft Ebene 2–${skip1CapLvl}.`}
                        {astAusblendung1 === "keine" && "Keine Ebene betroffen."}
                      </p>
                    </Field>
                  )}
                  <div style={styles.checkboxRow}>
                    <input type="checkbox" id="sternschicht2" checked={sternschicht2} onChange={(e) => setSternschicht2(e.target.checked)} />
                    <label htmlFor="sternschicht2" style={{ marginLeft: 6 }}>zweite, unabhängige Schicht</label>
                  </div>
                </>
              )}
            </Section>

            {sternschicht && sternschicht2 && (
              <Section title="Sternschicht — Schicht 2">
                <Row cols={3}>
                  {astschicht && <Slider label={`Sternebene 2: ${Math.min(sternEbene2, ebenen)}`} min={1} max={ebenen} value={Math.min(sternEbene2, ebenen)} onChange={setSternEbene2} />}
                  <Field label={`Sternstrahlen 2: ${sternPunkte2}`}>
                    <select style={styles.select} value={effTeiler2} onChange={(e) => setSternTeiler2(Number(e.target.value))}>
                      {teilerOptionen.map((t) => (<option key={t} value={t}>{n / t} Strahlen{t === 1 ? " (alle)" : ` (jeder ${t}.)`}</option>))}
                    </select>
                  </Field>
                  {kMax2 > 1 ? (
                    <Slider label={`Schrittweite 2: ${Math.min(k2, kMax2)}`} min={1} max={kMax2} value={Math.min(k2, kMax2)} onChange={setK2} />
                  ) : (
                    <Field label="Schrittweite 2">
                      <p style={styles.hint}>nur 1 Verbindungsart (Versatz bleibt trotzdem wirksam)</p>
                    </Field>
                  )}
                </Row>
                {effTeiler2 > 1 && (
                  <Slider label={`Rotationsversatz: ${sternVersatz2} (von ${effTeiler2})`} min={0} max={effTeiler2 - 1} value={sternVersatz2} onChange={setSternVersatz2} />
                )}
                {(skip2ExaktMoeglich || skip2LeMoeglich) && (
                  <Field label="Seitenäste bei diesem Sternlevel">
                    <select key={`sk2-${sternEbeneEff2}`} style={styles.select} value={astAusblendung2} onChange={(e) => setAstAusblendung2(e.target.value)}>
                      <option value="keine">Alle behalten</option>
                      {skip2ExaktMoeglich && <option value="exakt">Nur auf Sternlevel weglassen</option>}
                      {skip2LeMoeglich && <option value="kleinerGleich">Sternlevel und darunter weglassen</option>}
                    </select>
                    <p style={styles.hint}>
                      {astAusblendung2 === "exakt" && skip2ExaktMoeglich && `Betrifft Ebene ${sternEbeneEff2}.`}
                      {astAusblendung2 === "kleinerGleich" && skip2LeMoeglich && `Betrifft Ebene 2–${skip2CapLvl}.`}
                      {astAusblendung2 === "keine" && "Keine Ebene betroffen."}
                    </p>
                  </Field>
                )}
              </Section>
            )}
          </aside>

          {/* ---------------- Vorschau ---------------- */}
          <main style={styles.main}>
            <div style={styles.cardFrame}>
              <svg viewBox={`0 0 ${format.w} ${format.h}`} style={{ height: "100%", maxHeight: "100%", width: "auto", maxWidth: "100%", display: "block", margin: "0 auto" }}>
                <rect x={0} y={0} width={format.w} height={format.h} fill={cardHex} />
                <defs>
                  <marker id="pfeilVS" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="1.8" markerHeight="1.8" markerUnits="userSpaceOnUse" orient="auto-start-reverse">
                    <path d="M0,0L10,5L0,10z" fill={KARTONFARBEN[kartonfarbe].aktivVS} />
                  </marker>
                  <marker id="pfeilRS" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="1.8" markerHeight="1.8" markerUnits="userSpaceOnUse" orient="auto-start-reverse">
                    <path d="M0,0L10,5L0,10z" fill={KARTONFARBEN[kartonfarbe].aktivRS} />
                  </marker>
                </defs>
                {falzposition === "links" && <line x1={0.4} y1={0} x2={0.4} y2={format.h} stroke="#000" strokeOpacity={0.35} strokeWidth={0.3} strokeDasharray="2,1.5" />}
                {falzposition === "oben" && <line x1={0} y1={0.4} x2={format.w} y2={0.4} stroke="#000" strokeOpacity={0.35} strokeWidth={0.3} strokeDasharray="2,1.5" />}
                <rect x={margins.left} y={margins.top} width={usableW} height={usableH} fill="none" stroke="#000" strokeOpacity={0.15} strokeWidth={0.25} strokeDasharray="1.5,1.5" />

                {!hasCritical &&
                  zeigeVorschau &&
                  segments
                    .filter((s, i) => i >= currentStep && s.type === "stitch")
                    .map((s, i) => {
                      const p1 = nodes.get(s.a);
                      const p2 = nodes.get(s.b);
                      return <line key={`prev-${i}`} x1={p1.x} y1={p1.y} x2={p2.x} y2={p2.y} stroke="#ffffff" strokeOpacity={0.14} strokeWidth={0.25} />;
                    })}

                {!hasCritical &&
                  segments.map((s, i) => {
                    if (i >= currentStep) return null;
                    const p1 = nodes.get(s.a);
                    const p2 = nodes.get(s.b);
                    const active = i === currentStep - 1;
                    if (s.type === "jump") {
                      if (!zeigeSpruenge && !active) return null;
                      return (
                        <line
                          key={i}
                          x1={p1.x} y1={p1.y} x2={p2.x} y2={p2.y}
                          stroke={active ? KARTONFARBEN[kartonfarbe].aktivRS : "#ffffff"}
                          strokeOpacity={active ? 1 : 0.3}
                          strokeWidth={active ? 0.45 : 0.18}
                          strokeDasharray={active ? undefined : "0.6,0.8"}
                          markerEnd={active ? "url(#pfeilRS)" : undefined}
                        />
                      );
                    }
                    return (
                      <line
                        key={i}
                        x1={p1.x} y1={p1.y} x2={p2.x} y2={p2.y}
                        stroke={active ? KARTONFARBEN[kartonfarbe].aktivVS : threadPrimary}
                        strokeWidth={active ? 0.55 : 0.4}
                        strokeLinecap="round"
                        markerEnd={active ? "url(#pfeilVS)" : undefined}
                      />
                    );
                  })}

                {Array.from(nodes.entries()).map(([id, p], i) => {
                  const sev = pointSeverity.get(id);
                  const fill = sev === "critical" ? GEFAHR_FARBE : sev === "moderate" ? WARN_FARBE : "rgba(0,0,0,0.4)";
                  const r = sev === "ok" ? LOCH_DURCHMESSER / 2 : LOCH_DURCHMESSER / 2 + 0.25;
                  return <circle key={i} cx={p.x} cy={p.y} r={r} fill={fill} />;
                })}


              </svg>
            </div>

            <div style={styles.playback}>
              <button style={styles.iconBtn} onClick={() => setPlaying((p) => !p)} disabled={hasCritical}>
                {playing ? <Pause size={16} /> : <Play size={16} />}
              </button>
              <button style={styles.iconBtn} onClick={() => { setCurrentStep(0); setPlaying(false); }} disabled={hasCritical}>
                <RotateCcw size={16} />
              </button>
              <input type="range" min={0} max={maxStep} value={currentStep} onChange={(e) => { setCurrentStep(Number(e.target.value)); setPlaying(false); }} style={{ flex: 1 }} disabled={hasCritical} />
              <span style={styles.stepLabel}>{currentStep} / {maxStep}</span>
              <button style={styles.exportBtn} onClick={exportSVG} disabled={hasCritical}>
                <Download size={14} style={{ marginRight: 6 }} />
                SVG exportieren
              </button>
            </div>

            <div style={{ ...styles.warnBox, ...(warnungen.length === 0 ? styles.warnBoxEmpty : hasCritical ? styles.warnBoxGefahr : null) }}>
              {warnungen.map((w, i) => (
                <div key={i} style={{ ...styles.warnLine, color: hasCritical ? GEFAHR_FARBE : styles.warnLine.color }}>
                  <AlertTriangle size={13} style={{ marginRight: 6, flexShrink: 0, marginTop: 1 }} />
                  <span>{w}</span>
                </div>
              ))}
            </div>

            <div style={styles.statsGrid}>
              <Stat label="Punkte" value={nodes.size} />
              <Stat label="Stiche" value={stitchSegments.length} />
              <Stat label="Fadenlänge (+15%)" value={`${(((frontLength + jumpLength) * 1.15) / 10).toFixed(1)} cm`} />
            </div>

            <p style={styles.legend}>
              <span style={{ color: threadPrimary }}>━</span> Vorderseite (1×) &nbsp;·&nbsp;
              <span style={{ color: "#ffffff", opacity: 0.6 }}>┅</span> Rückseiten-Sprung &nbsp;·&nbsp;
              <span style={{ color: KARTONFARBEN[kartonfarbe].aktivVS }}>➤</span> aktiver VS-Schritt &nbsp;·&nbsp;
              <span style={{ color: KARTONFARBEN[kartonfarbe].aktivRS }}>➤</span> aktiver RS-Sprung &nbsp;·&nbsp;
              <span style={{ color: WARN_FARBE }}>●</span> Abstand knapp &nbsp;·&nbsp;
              <span style={{ color: GEFAHR_FARBE }}>●</span> Abstand zu gering
            </p>
          </main>
        </div>
      </div>

      {zeigeAnleitung && (
        <div className="anleitung-overlay">
          <Anleitung
            config={{ n, ebenen, astschicht, astAktiv, sternschicht, sternEbene: Math.min(sternEbene, ebenen), effTeiler1, k1: Math.min(k1, kMax1), sternschicht2, sternEbene2: Math.min(sternEbene2, ebenen), effTeiler2, sternVersatz2, k2: Math.min(k2, kMax2), format, falzposition, zoom }}
            nodes={nodes}
            edges={edges}
            astCount={astCount}
            star1Count={star1Count}
            star2Count={star2Count}
            onClose={() => setZeigeAnleitung(false)}
          />
        </div>
      )}
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/* UI-Bausteine                                                           */
/* ---------------------------------------------------------------------- */

function Section({ title, children }) {
  return (
    <div style={styles.section}>
      <h2 style={styles.sectionTitle}>{title}</h2>
      {children}
    </div>
  );
}
function Row({ children, cols }) {
  return <div style={{ ...styles.row, gridTemplateColumns: `repeat(${cols || React.Children.count(children)}, 1fr)` }}>{children}</div>;
}
function Field({ label, children }) {
  return (
    <div style={styles.field}>
      <label style={styles.label}>{label}</label>
      {children}
    </div>
  );
}
function Slider({ label, min, max, step = 1, value, onChange }) {
  return (
    <div style={styles.field}>
      <label style={styles.label}>{label}</label>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} style={{ width: "100%" }} />
    </div>
  );
}
function Stat({ label, value }) {
  return (
    <div style={styles.stat}>
      <div style={styles.statValue}>{value}</div>
      <div style={styles.statLabel}>{label}</div>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/* Styles                                                                 */
/* ---------------------------------------------------------------------- */

const cssReset = `
  * { box-sizing: border-box; }
  input[type="range"] { accent-color: #d9b86a; }
  input[type="range"]:disabled { opacity: 0.4; }
`;

const styles = {
  outer: { minHeight: "100vh", background: "#0a141f", color: "#eef3f7", fontFamily: "'Iowan Old Style', 'Palatino Linotype', Georgia, serif", display: "flex", alignItems: "center", justifyContent: "center", padding: 14 },
  frame: { position: "relative", width: "100%", maxWidth: 1320, aspectRatio: "16 / 9", maxHeight: "94vh", background: "#0e1b2b", border: "1px solid #223751", borderRadius: 12, display: "flex", flexDirection: "column", overflow: "hidden", padding: "10px 16px 12px" },
  header: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8, flexShrink: 0 },
  h1: { fontSize: 17, fontWeight: 600, margin: 0, letterSpacing: 0.2 },
  gearBtn: { background: "#1c3350", border: "1px solid #2c4460", color: "#c3d2e0", borderRadius: 6, width: 28, height: 28, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer" },
  settingsOverlay: { position: "absolute", top: 44, right: 16, zIndex: 20 },
  settingsPanel: { width: 300, maxHeight: "80%", overflowY: "auto", background: "#132437", border: "1px solid #2c4460", borderRadius: 10, padding: "12px 14px", boxShadow: "0 8px 24px rgba(0,0,0,0.45)", fontFamily: "system-ui, -apple-system, sans-serif" },
  settingsPanelHead: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 },
  closeBtn: { background: "transparent", border: "none", color: "#8fa3b8", cursor: "pointer", display: "flex" },
  layout: { flex: 1, minHeight: 0, display: "grid", gridTemplateColumns: "440px 1fr", gap: 14 },
  sidebar: { background: "#132437", borderRadius: 10, padding: "10px 14px", border: "1px solid #223751", fontFamily: "system-ui, -apple-system, sans-serif", overflowY: "auto", minHeight: 0 },
  section: { marginBottom: 10 },
  sectionTitle: { fontSize: 10.5, textTransform: "uppercase", letterSpacing: 1, color: "#7d93a8", margin: "0 0 6px", borderBottom: "1px solid #223751", paddingBottom: 4, display: "block" },
  row: { display: "grid", gap: 10, marginBottom: 2, alignItems: "end" },
  field: { marginBottom: 8 },
  label: { display: "block", fontSize: 11.5, color: "#c3d2e0", marginBottom: 3 },
  select: { width: "100%", background: "#0e1b2b", color: "#eef3f7", border: "1px solid #2c4460", borderRadius: 6, padding: "5px 7px", fontSize: 12.5 },
  input: { width: "100%", background: "#0e1b2b", color: "#eef3f7", border: "1px solid #2c4460", borderRadius: 6, padding: "5px 7px", fontSize: 12.5 },
  checkboxRow: { display: "flex", alignItems: "center", fontSize: 12, color: "#c3d2e0", marginBottom: 8 },
  hint: { fontSize: 10.5, color: "#7d93a8", lineHeight: 1.4, marginTop: 4 },
  main: { minWidth: 0, minHeight: 0, display: "flex", flexDirection: "column" },
  cardFrame: { flex: 1, minHeight: 0, background: "#132437", border: "1px solid #223751", borderRadius: 10, padding: 10, display: "flex", alignItems: "center", justifyContent: "center" },
  playback: { display: "flex", alignItems: "center", gap: 8, marginTop: 8, flexShrink: 0, fontFamily: "system-ui, -apple-system, sans-serif" },
  iconBtn: { background: "#1c3350", border: "1px solid #2c4460", color: "#eef3f7", borderRadius: 6, width: 28, height: 28, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer" },
  exportBtn: { background: "#d9b86a", border: "none", color: "#10203a", borderRadius: 6, padding: "5px 10px", fontSize: 11.5, fontWeight: 600, display: "flex", alignItems: "center", cursor: "pointer", whiteSpace: "nowrap" },
  stepLabel: { fontSize: 11, color: "#7d93a8", minWidth: 55, textAlign: "right", fontFamily: "system-ui, -apple-system, sans-serif" },
  warnBox: { marginTop: 8, height: 44, overflowY: "auto", background: "#3a2416", border: "1px solid #6b4726", borderRadius: 8, padding: "5px 10px", flexShrink: 0, fontFamily: "system-ui, -apple-system, sans-serif", transition: "opacity 0.15s" },
  warnBoxEmpty: { background: "transparent", border: "1px solid transparent" },
  warnBoxGefahr: { background: "#3a1c18", border: "1px solid #6b2e26" },
  warnLine: { display: "flex", alignItems: "flex-start", fontSize: 11, color: "#f0c896", marginBottom: 2 },
  statsGrid: { marginTop: 8, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8, flexShrink: 0, fontFamily: "system-ui, -apple-system, sans-serif" },
  stat: { background: "#132437", border: "1px solid #223751", borderRadius: 8, padding: "6px 6px", textAlign: "center" },
  statValue: { fontSize: 13, fontWeight: 600, color: "#eef3f7" },
  statLabel: { fontSize: 9.5, color: "#7d93a8", marginTop: 1 },
  legend: { marginTop: 6, fontSize: 11, color: "#8fa3b8", flexShrink: 0, fontFamily: "system-ui, -apple-system, sans-serif" },
};
