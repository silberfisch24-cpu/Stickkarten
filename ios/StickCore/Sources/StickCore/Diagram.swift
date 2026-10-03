import Foundation

// Port von `buildStepDiagram` samt Layout-Hilfsfunktionen (Web-App Z. 228–504).
// Ergebnis ist eine geordnete Liste von Zeichen-Primitiven in einem „CSS-Pixel“-Koordinatensystem
// (y nach unten); Renderer (PDF, SwiftUI) zeichnen sie in dieser Reihenfolge.

public enum DiagramRole {
    case background, vs, rs, hole, label, vsBadge, rsBadge
}

public enum TextAnchor: String {
    case start, middle, end
}

public enum DiagramElement {
    case line(x1: Double, y1: Double, x2: Double, y2: Double, role: DiagramRole)
    /// Quadratische Bézierkurve (RS-Bogen) mit Pfeilspitze am Ende
    case curve(x1: Double, y1: Double, cx: Double, cy: Double, x2: Double, y2: Double, role: DiagramRole)
    case circle(cx: Double, cy: Double, r: Double, role: DiagramRole)
    case text(x: Double, y: Double, text: String, anchor: TextAnchor, role: DiagramRole)
}

public struct StepDiagram {
    public var width: Double
    public var height: Double
    public var elements: [DiagramElement]
    public var holeR: Double
    public var labelSize: Double
    public var badgeFontSize: Double
    /// Lochpunkte als Ring (Arm-Diagramm) statt gefüllt (Stern-Diagramme)
    public var holeOutlined: Bool
}

public struct DiagramParams {
    public var keyPrefix = ""
    public var points: [String: Point] = [:]
    public var ids: [String] = []
    public var steps: [StitchStep] = []
    public var labelOf: (String) -> String = { $0 }
    public var backgroundEdges: [(String, String)]? = nil
    public var rotateAroundId: String? = nil
    public var rotateDeg: Double = 0
    public var maxW: Double = 0
    public var maxH: Double = 0
    public var margin: Double = 0
    public var holeR: Double = 5
    public var labelSize: Double? = nil
    public var holeOutlined = false
    public var bendFactor: Double = 0.3
    public var bendMin: Double = 16
    public var bendMax: Double = 30
    public var bendStep: Double = 2
    public init() {}
}

// MARK: Hilfsfunktionen

func rotatePt(_ p: Point, _ c: Point, _ deg: Double) -> Point {
    let rad = (deg * Double.pi) / 180
    let dx = p.x - c.x, dy = p.y - c.y
    return Point(x: c.x + dx * cos(rad) - dy * sin(rad), y: c.y + dx * sin(rad) + dy * cos(rad))
}

func xformPt(_ p: Point, _ scale: Double, _ cx: Double, _ cy: Double, _ offX: Double, _ offY: Double) -> Point {
    Point(x: offX + (p.x - cx) * scale, y: offY + (p.y - cy) * scale)
}

func bowedPt(_ a: Point, _ b: Point, _ bend: Double) -> Point {
    let mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2
    let dx = b.x - a.x, dy = b.y - a.y
    var len = hypot(dx, dy)
    if len == 0 { len = 1 }
    let nx = -dy / len, ny = dx / len
    return Point(x: mx + nx * bend, y: my + ny * bend)
}

func autoBendPt(_ a: Point, _ b: Point, _ factor: Double, _ minB: Double, _ maxB: Double) -> Double {
    max(minB, min(maxB, dist(a, b) * factor))
}

/// Tatsächlicher Kurvenmittelpunkt (t = 0,5) einer quadratischen Bézier.
func curveMidpointPt(_ a: Point, _ b: Point, _ bend: Double) -> Point {
    let c = bowedPt(a, b, bend)
    return Point(x: 0.25 * a.x + 0.5 * c.x + 0.25 * b.x, y: 0.25 * a.y + 0.5 * c.y + 0.25 * b.y)
}

struct AutoFit {
    var scale: Double
    var offX: Double
    var offY: Double
    var width: Double
    var height: Double
}

func autoFitPts(_ points: [Point], _ maxW: Double, _ maxH: Double, _ margin: Double) -> AutoFit {
    let xs = points.map { $0.x }, ys = points.map { $0.y }
    let minX = xs.min() ?? 0, maxX = xs.max() ?? 0, minY = ys.min() ?? 0, maxY = ys.max() ?? 0
    let bboxW = max(maxX - minX, 1e-6), bboxH = max(maxY - minY, 1e-6)
    let scale = min((maxW - 2 * margin) / bboxW, (maxH - 2 * margin) / bboxH)
    let width = jsRound(bboxW * scale + 2 * margin), height = jsRound(bboxH * scale + 2 * margin)
    return AutoFit(scale: scale, offX: margin - minX * scale, offY: margin - minY * scale, width: width, height: height)
}

func badgeR(_ text: String) -> Double {
    9 + Double(max(0, text.count - 1)) * 3
}

struct RsGroup {
    var a: Point
    var b: Point
    var nums: [Int]
    var bend: Double = 0
    var pos: Point = Point(x: 0, y: 0)
    var r: Double = 0
}

/// Kreise (Art + Anzahl Ziffern) erfassen, dann den Bogen jedes RS-Pfeils so weit vergrößern,
/// bis sein Nummernkreis den Mindestabstand (+1) zu allen bereits platzierten Kreisen einhält.
func resolveRsBendsPts(
    vsBadges: [(pos: Point, r: Double)], groups: [RsGroup], factor: Double, minB: Double, maxB: Double, step: Double
) -> [RsGroup] {
    var placed: [(pos: Point, r: Double)] = vsBadges.map { ($0.pos, $0.r) }
    var out: [RsGroup] = []
    for g0 in groups {
        var g = g0
        let r = badgeR(g.nums.map(String.init).joined(separator: ","))
        var bend = autoBendPt(g.a, g.b, factor, minB, maxB)
        var pos = curveMidpointPt(g.a, g.b, bend)
        var tries = 0
        while tries < 25 && bend < maxB * 2 && placed.contains(where: { dist(pos, $0.pos) < r + $0.r + 1 }) {
            bend += step
            pos = curveMidpointPt(g.a, g.b, bend)
            tries += 1
        }
        placed.append((pos, r))
        g.bend = bend
        g.pos = pos
        g.r = r
        out.append(g)
    }
    return out
}

func buildAdjacencyPts(_ pairs: [(String, String)]) -> [String: [String]] {
    var adj: [String: [String]] = [:]
    for (a, b) in pairs {
        adj[a, default: []].append(b)
        adj[b, default: []].append(a)
    }
    return adj
}

/// Logische Beschriftungsposition je Loch: größte freie Winkellücke zwischen den Verbindungen.
func labelAnglePt(_ nodeId: String, _ disp: [String: Point], _ adj: [String: [String]]) -> Double {
    guard let p = disp[nodeId] else { return -Double.pi / 2 }
    let neighbors = adj[nodeId] ?? []
    let angles = neighbors.compactMap { nb -> Double? in
        guard let q = disp[nb] else { return nil }
        return atan2(q.y - p.y, q.x - p.x)
    }.sorted()
    if angles.isEmpty { return -Double.pi / 2 }
    var bestStart = angles[0]
    var bestSize = -1.0
    for i in 0..<angles.count {
        let a1 = angles[i]
        let a2 = i + 1 < angles.count ? angles[i + 1] : angles[0] + 2 * Double.pi
        let gap = a2 - a1
        if gap > bestSize {
            bestSize = gap
            bestStart = a1
        }
    }
    return bestStart + bestSize / 2
}

func placeLabelCoords(_ p: Point, _ angle: Double, _ distFromHole: Double) -> (x: Double, y: Double, anchor: TextAnchor) {
    let lx = p.x + cos(angle) * distFromHole, ly = p.y + sin(angle) * distFromHole
    var anchor = TextAnchor.middle
    var dx = 0.0, dy = 3.5
    if cos(angle) > 0.35 { anchor = .start; dx = 2 }
    else if cos(angle) < -0.35 { anchor = .end; dx = -2 }
    if sin(angle) < -0.35 { dy = 0 }
    else if sin(angle) > 0.35 { dy = 8 }
    return (lx + dx, ly + dy, anchor)
}

// MARK: buildStepDiagram

public func buildStepDiagram(_ p: DiagramParams) -> StepDiagram {
    let allIds = Array(p.points.keys)
    var rotated: [String: Point] = [:]
    if let rid = p.rotateAroundId, p.rotateDeg != 0, let center = p.points[rid] {
        for id in allIds { rotated[id] = rotatePt(p.points[id]!, center, p.rotateDeg) }
    } else {
        for id in allIds { rotated[id] = p.points[id]! }
    }
    let fit = autoFitPts(p.ids.compactMap { rotated[$0] }, p.maxW, p.maxH, p.margin)
    var disp: [String: Point] = [:]
    for id in allIds { disp[id] = xformPt(rotated[id]!, fit.scale, 0, 0, fit.offX, fit.offY) }
    func d(_ id: String) -> Point { disp[id] ?? Point(x: 0, y: 0) }

    let TRIM = p.holeR + 2
    var elements: [DiagramElement] = []

    if let bg = p.backgroundEdges {
        for (a, b) in bg {
            elements.append(.line(x1: d(a).x, y1: d(a).y, x2: d(b).x, y2: d(b).y, role: .background))
        }
    }

    // Positionen/Radien der VS-Zahlenkreise (feste Position) + kollisionsfrei aufgeweitete RS-Bögen.
    let vsBadges: [(pos: Point, r: Double)] = p.steps.enumerated().map { i, step in
        let a = d(step.vs.a), b = d(step.vs.b)
        return (Point(x: (a.x + b.x) / 2, y: (a.y + b.y) / 2), badgeR(String(i + 1)))
    }
    // RS-Bögen mit identischem Start/Ziel zusammenfassen (Einfügereihenfolge)
    var groupOrder: [String] = []
    var groupMap: [String: (a: String, b: String, nums: [Int])] = [:]
    for (i, step) in p.steps.enumerated() {
        guard let rs = step.rs else { continue }
        let key = rs.a + "|" + rs.b
        if groupMap[key] == nil {
            groupMap[key] = (rs.a, rs.b, [])
            groupOrder.append(key)
        }
        groupMap[key]!.nums.append(i + 1)
    }
    let rsGroupsWorld: [RsGroup] = groupOrder.map { key in
        let g = groupMap[key]!
        return RsGroup(a: d(g.a), b: d(g.b), nums: g.nums)
    }
    let rsResolved = resolveRsBendsPts(
        vsBadges: vsBadges, groups: rsGroupsWorld, factor: p.bendFactor, minB: p.bendMin, maxB: p.bendMax, step: p.bendStep
    )

    // 1) Pfeile
    for step in p.steps {
        let a = d(step.vs.a), b = d(step.vs.b)
        let dx = b.x - a.x, dy = b.y - a.y
        var len = hypot(dx, dy)
        if len == 0 { len = 1 }
        let ux = dx / len, uy = dy / len
        elements.append(.line(x1: a.x + ux * TRIM, y1: a.y + uy * TRIM, x2: b.x - ux * TRIM, y2: b.y - uy * TRIM, role: .vs))
    }
    for g in rsResolved {
        let c = bowedPt(g.a, g.b, g.bend)
        func along(_ q: Point, _ toward: Point, _ trim: Double) -> Point {
            let dx = toward.x - q.x, dy = toward.y - q.y
            var len = hypot(dx, dy)
            if len == 0 { len = 1 }
            return Point(x: q.x + (dx / len) * trim, y: q.y + (dy / len) * trim)
        }
        let a2 = along(g.a, c, TRIM), b2 = along(g.b, c, TRIM)
        elements.append(.curve(x1: a2.x, y1: a2.y, cx: c.x, cy: c.y, x2: b2.x, y2: b2.y, role: .rs))
    }

    // 2) Lochpunkte + Kürzel
    var adjPairs: [(String, String)] = []
    for s in p.steps {
        adjPairs.append((s.vs.a, s.vs.b))
        if let rs = s.rs { adjPairs.append((rs.a, rs.b)) }
    }
    if let bg = p.backgroundEdges { adjPairs.append(contentsOf: bg) }
    let adj = buildAdjacencyPts(adjPairs)
    for id in p.ids {
        let pt = d(id)
        elements.append(.circle(cx: pt.x, cy: pt.y, r: p.holeR, role: .hole))
        let angle = labelAnglePt(id, disp, adj)
        let lc = placeLabelCoords(pt, angle, p.holeR + 11)
        elements.append(.text(x: lc.x, y: lc.y, text: p.labelOf(id), anchor: lc.anchor, role: .label))
    }

    // 3) Schritt-Nummern zuoberst
    for (i, _) in p.steps.enumerated() {
        let pos = vsBadges[i].pos
        elements.append(.circle(cx: pos.x, cy: pos.y, r: vsBadges[i].r, role: .vsBadge))
        elements.append(.text(x: pos.x, y: pos.y + 3.5, text: String(i + 1), anchor: .middle, role: .vsBadge))
    }
    for g in rsResolved {
        elements.append(.circle(cx: g.pos.x, cy: g.pos.y, r: g.r, role: .rsBadge))
        elements.append(.text(x: g.pos.x, y: g.pos.y + 3.5, text: g.nums.map(String.init).joined(separator: ","), anchor: .middle, role: .rsBadge))
    }

    return StepDiagram(
        width: fit.width, height: fit.height, elements: elements,
        holeR: p.holeR, labelSize: p.labelSize ?? 10.5, badgeFontSize: 10.5, holeOutlined: p.holeOutlined
    )
}
