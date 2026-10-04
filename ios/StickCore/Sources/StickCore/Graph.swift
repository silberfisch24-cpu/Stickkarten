import Foundation

public struct StickEdge: Equatable {
    public let id: String
    public let a: String
    public let b: String
    public let len: Double
}

/// Knoten in Einfügereihenfolge (wie `Map` in JS) + Kanten in Erzeugungsreihenfolge.
/// Die Kantenreihenfolge ist fachlich entscheidend (sie ist die Stichfolge).
public struct StickGraph {
    public private(set) var nodeIDs: [String] = []
    public private(set) var nodes: [String: Point] = [:]
    public internal(set) var edges: [StickEdge] = []
    public internal(set) var astCount = 0
    public internal(set) var star1Count = 0
    public internal(set) var star2Count = 0

    public func point(_ id: String) -> Point { nodes[id] ?? Point(x: 0, y: 0) }

    /// Alle Knoten (id, Position) in Einfügereihenfolge.
    public var entries: [(id: String, point: Point)] {
        nodeIDs.map { ($0, nodes[$0]!) }
    }

    mutating func setNode(_ id: String, _ p: Point) {
        if nodes[id] == nil { nodeIDs.append(id) }
        nodes[id] = p
    }

    mutating func addEdge(_ a: String, _ b: String) {
        let e = StickEdge(id: "e\(edges.count)", a: a, b: b, len: dist(point(a), point(b)))
        edges.append(e)
    }
}

public struct GraphParams {
    public var n: Int
    public var R: Double
    public var cx: Double
    public var cy: Double
    public var astschicht: Bool
    public var ebenen: Int
    public var astAktiv: Bool
    public var astWinkel: Double
    public var astLaenge: Double
    public var astWachstum: Double
    public var fraktalTiefe: Int
    public var fraktalSkalierung: Double
    public var sternschicht: Bool
    public var sternEbene: Int
    public var sternTeiler: Int
    public var k1: Int
    public var sternschicht2: Bool
    public var sternEbene2: Int
    public var sternTeiler2: Int
    public var sternVersatz2: Int
    public var k2: Int
    /// Ebenen, deren Seitenäste (samt Fraktal-Spitzen) weggelassen werden.
    public var unterdrueckteEbenen: Set<Int>
}

private func addFraktalZweige(
    graph: inout StickGraph, parentId: String, parentPos: Point, approachAngle: Double, length: Double,
    depth: Int, maxDepth: Int, branchAngle: Double, scale: Double
) {
    if depth > maxDepth || length < 0.6 { return }
    for side in [-1, 1] {
        let childAngle = approachAngle + Double(side) * branchAngle
        let p = polar(parentPos.x, parentPos.y, childAngle, length)
        let id = "\(parentId)f\(depth)\(side < 0 ? "n" : "p")"
        graph.setNode(id, p)
        graph.addEdge(parentId, id)
        addFraktalZweige(
            graph: &graph, parentId: id, parentPos: p, approachAngle: childAngle, length: length * scale,
            depth: depth + 1, maxDepth: maxDepth, branchAngle: branchAngle, scale: scale
        )
    }
}

/// Eine Sternschicht: eigene Ebene, eigene Strahlenzahl (Teiler von n), eigener
/// Rotationsversatz, eigene Schrittweite — unabhängig von anderen Schichten.
private func addSternLayer(
    graph: inout StickGraph, n: Int, ringIds: [String], ebenen: Int, astschicht: Bool, sternEbene: Int,
    sternTeiler: Int, versatz: Int, k: Int, seen: inout Set<String>
) {
    let level: Int? = astschicht ? min(max(1, sternEbene), ebenen) : nil
    func pointIdAt(_ i: Int) -> String {
        if level == nil || level == ebenen { return ringIds[i] }
        return "A\(i)L\(level!)"
    }
    var teiler = max(1, min(sternTeiler, n))
    while teiler > 1 && n % teiler != 0 { teiler -= 1 }
    let m = n / teiler
    let offset = ((versatz % teiler) + teiler) % teiler
    if k < 1 || k > m - 1 { return }
    for j in 0..<m {
        let jj = (j + k) % m
        let a = pointIdAt((j * teiler + offset) % n)
        let b = pointIdAt((jj * teiler + offset) % n)
        let key = a < b ? "\(a)|\(b)" : "\(b)|\(a)"
        if !seen.contains(key) {
            seen.insert(key)
            graph.addEdge(a, b)
        }
    }
}

public func buildGraph(_ p: GraphParams) -> StickGraph {
    var g = StickGraph()
    let n = p.n
    let ebenen = p.ebenen

    var ringIds: [String] = []
    for i in 0..<max(0, n) {
        let angle = -90 + Double(i) * (360 / Double(n))
        let id = "R\(i)"
        g.setNode(id, polar(p.cx, p.cy, angle, p.R))
        ringIds.append(id)
    }

    if p.astschicht {
        g.setNode("C", Point(x: p.cx, y: p.cy))
        let armStep = p.R / Double(ebenen)
        // Für jeden Arm exakt dieselbe Reihenfolge: Stamm nach außen, an jeder
        // Verzweigung erst der linke, dann der rechte Zweig samt Fraktal-Spitzen,
        // bevor es am Stamm weitergeht.
        for i in 0..<max(0, n) {
            let angle = -90 + Double(i) * (360 / Double(n))
            var prevId = "C"
            var L = 1
            while L < ebenen {
                let r = Double(L) * armStep
                let id = "A\(i)L\(L)"
                g.setNode(id, polar(p.cx, p.cy, angle, r))
                g.addEdge(prevId, id)
                let root = g.point(id)
                prevId = id
                if p.astAktiv && L >= 2 && !p.unterdrueckteEbenen.contains(L) {
                    for side in [-1, 1] {
                        let bAngle = angle + Double(side) * p.astWinkel
                        let branchLen = armStep * p.astLaenge * (1 + p.astWachstum * Double(L - 1))
                        let bid = "A\(i)L\(L)b\(side)"
                        // Astspitze relativ zur Astwurzel (nicht zum Kartenzentrum).
                        let bp = polar(root.x, root.y, bAngle, branchLen)
                        g.setNode(bid, bp)
                        g.addEdge(id, bid)
                        if p.fraktalTiefe > 0 {
                            addFraktalZweige(
                                graph: &g, parentId: bid, parentPos: bp, approachAngle: bAngle,
                                length: branchLen * p.fraktalSkalierung, depth: 1, maxDepth: p.fraktalTiefe,
                                branchAngle: p.astWinkel, scale: p.fraktalSkalierung
                            )
                        }
                    }
                }
                L += 1
            }
            g.addEdge(prevId, ringIds[i])
            if p.fraktalTiefe > 0 {
                addFraktalZweige(
                    graph: &g, parentId: ringIds[i], parentPos: g.point(ringIds[i]), approachAngle: angle,
                    length: armStep * p.astLaenge * (1 + p.astWachstum * Double(ebenen - 1)), depth: 1,
                    maxDepth: p.fraktalTiefe, branchAngle: p.astWinkel, scale: p.fraktalSkalierung
                )
            }
        }
    }

    g.astCount = g.edges.count
    g.star1Count = 0
    g.star2Count = 0

    if p.sternschicht {
        var seen = Set<String>()
        let before1 = g.edges.count
        addSternLayer(
            graph: &g, n: n, ringIds: ringIds, ebenen: ebenen, astschicht: p.astschicht, sternEbene: p.sternEbene,
            sternTeiler: p.sternTeiler, versatz: 0, k: p.k1, seen: &seen
        )
        g.star1Count = g.edges.count - before1
        if p.sternschicht2 {
            let before2 = g.edges.count
            addSternLayer(
                graph: &g, n: n, ringIds: ringIds, ebenen: ebenen, astschicht: p.astschicht, sternEbene: p.sternEbene2,
                sternTeiler: p.sternTeiler2, versatz: p.sternVersatz2, k: p.k2, seen: &seen
            )
            g.star2Count = g.edges.count - before2
        }
    }
    return g
}

// MARK: - Stichweg

public struct StitchSegment: Equatable {
    public let a: String
    public let b: String
    public let isJump: Bool
}

/// Kanten in ihrer strukturellen Erzeugungsreihenfolge (Ast für Ast, Sehne für Sehne).
/// Jede Kante genau einmal, immer ein echter Sprung zwischen zwei Stichen.
public func buildStitchSequence(_ edges: [StickEdge]) -> [StitchSegment] {
    var segments: [StitchSegment] = []
    var currentPos: String? = nil
    for edge in edges {
        var near = edge.a
        var far = edge.b
        if near == currentPos {
            near = edge.b
            far = edge.a
        }
        if let cp = currentPos { segments.append(StitchSegment(a: cp, b: near, isJump: true)) }
        segments.append(StitchSegment(a: near, b: far, isJump: false))
        currentPos = far
    }
    return segments
}
