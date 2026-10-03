import Foundation

// MARK: - Schritte

/// Ein Schritt der Anleitung: ein VS-Stich plus der unmittelbar folgende RS-Sprung.
public struct StitchStep: Equatable {
    public var vs: StitchSegment
    public var rs: StitchSegment?
    public var rsIsTransition: Bool
}

/// Fasst je einen VS-Stich mit dem unmittelbar folgenden RS-Sprung zu „einem Schritt“ zusammen.
/// `transitionSeg`: beim letzten Schritt einer Schicht optional der Sprung zum nächsten Teilelement.
public func groupSteps(_ segs: [StitchSegment], transitionSeg: StitchSegment?) -> [StitchStep] {
    var steps: [StitchStep] = []
    for (i, s) in segs.enumerated() where !s.isJump {
        let next: StitchSegment? = i + 1 < segs.count ? segs[i + 1] : nil
        steps.append(StitchStep(vs: s, rs: (next?.isJump == true) ? next : nil, rsIsTransition: false))
    }
    if let t = transitionSeg, !steps.isEmpty {
        steps[steps.count - 1].rs = t
        steps[steps.count - 1].rsIsTransition = true
    }
    return steps
}

public func fadenCmFor(_ segs: [StitchSegment], graph: StickGraph) -> Double {
    var sum = 0.0
    for s in segs { sum += dist(graph.point(s.a), graph.point(s.b)) }
    return (sum * Stick.fadenZuschlag) / 10
}

private func isAllDigits(_ s: Substring) -> Bool {
    !s.isEmpty && s.allSatisfy { $0 >= "0" && $0 <= "9" }
}

/// Generische Kurzbeschriftung für Astschicht-Knoten (Z, E<L>, E<L>L/R, Fraktal-Spitzen rekursiv, K).
public func astNodeLabel(_ id: String) -> String {
    if id == "C" { return "Z" }
    if id.hasPrefix("R"), isAllDigits(id.dropFirst()) { return "K" }
    // A<arm>L<level>[b(-1|1)]
    if id.hasPrefix("A") {
        let rest = id.dropFirst()
        if let lIdx = rest.firstIndex(of: "L") {
            let arm = rest[rest.startIndex..<lIdx]
            let tail = rest[rest.index(after: lIdx)...]
            if isAllDigits(arm) {
                if isAllDigits(tail) { return "E\(tail)" }
                if let bIdx = tail.firstIndex(of: "b") {
                    let lvl = tail[tail.startIndex..<bIdx]
                    let side = tail[tail.index(after: bIdx)...]
                    if isAllDigits(lvl), side == "-1" || side == "1" {
                        return "E\(lvl)\(side == "-1" ? "L" : "R")"
                    }
                }
            }
        }
    }
    // <prefix>f<digits>(n|p)
    if let last = id.last, last == "n" || last == "p" {
        let body = id.dropLast()
        var digitsStart = body.endIndex
        while digitsStart > body.startIndex {
            let prev = body.index(before: digitsStart)
            if body[prev] >= "0" && body[prev] <= "9" { digitsStart = prev } else { break }
        }
        if digitsStart < body.endIndex, digitsStart > body.startIndex {
            let fIdx = body.index(before: digitsStart)
            if body[fIdx] == "f", fIdx > body.startIndex {
                let prefix = String(body[body.startIndex..<fIdx])
                let digits = body[digitsStart...]
                return "\(astNodeLabel(prefix)).\(digits)\(last == "n" ? "a" : "b")"
            }
        }
    }
    return id
}

// MARK: - Abschnitte (Arm, Sternschichten)

public struct AnleitungSection {
    public var steps: [StitchStep]
    public var ids: [String]
    public var labelOf: (String) -> String
    public var fadenCm: Double
    public var diagram: StepDiagram
}

public struct ArmSection {
    public var armEdgeCount: Int
    public var steps: [StitchStep]
    public var ids: [String]
    public var fadenCm: Double
    public var diagram: StepDiagram
}

public struct AnleitungContent {
    public var arm: ArmSection?
    public var stern1: AnleitungSection?
    public var stern2: AnleitungSection?
}

public struct DiagramLimits {
    public var armMaxW: Double
    public var armMaxH: Double
    public var sternMax: Double
    /// Web-App: 856 × 900 (Arm) und 420 × 420 (Stern).
    public static let web = DiagramLimits(armMaxW: 856, armMaxH: 900, sternMax: 420)
}

/// Daten der Arbeitsanweisung (Web-App: `Anleitung`-Komponente, Z. 589–667).
public func buildAnleitung(_ r: StickResult, limits: DiagramLimits = .web) -> AnleitungContent {
    let s = r.settings
    let g = r.graph
    let n = s.n
    let edges = g.edges
    let astCount = g.astCount
    let astEdges = s.astschicht ? Array(edges[0..<astCount]) : []
    let star1Edges = s.sternschicht ? Array(edges[astCount..<(astCount + g.star1Count)]) : []
    let star2Edges = s.sternschicht2
        ? Array(edges[(astCount + g.star1Count)..<(astCount + g.star1Count + g.star2Count)]) : []

    var content = AnleitungContent()

    if s.astschicht && n > 0 && astCount > 0 {
        let armEdgeCount = astCount / n
        let arm0Edges = Array(astEdges[0..<armEdgeCount])
        let fullAstSegs = buildStitchSequence(astEdges)
        let armSegCount = 2 * armEdgeCount - 1
        let armSegs = Array(fullAstSegs[0..<armSegCount])
        let transitionSeg: StitchSegment? = n > 1 && armSegCount < fullAstSegs.count ? fullAstSegs[armSegCount] : nil
        let armSteps = groupSteps(armSegs, transitionSeg: transitionSeg)
        let armIds = uniqueIDs(arm0Edges)
        var armPoints: [String: Point] = [:]
        for id in armIds { armPoints[id] = g.point(id) }
        var p = DiagramParams()
        p.keyPrefix = "arm"
        p.points = armPoints
        p.ids = armIds
        p.steps = armSteps
        p.labelOf = astNodeLabel
        p.rotateAroundId = armPoints["C"] != nil ? "C" : armIds.first
        p.rotateDeg = 90
        p.maxW = limits.armMaxW
        p.maxH = limits.armMaxH
        p.margin = 42
        p.holeR = 5
        p.bendFactor = 0.3; p.bendMin = 16; p.bendMax = 30; p.bendStep = 2
        let diagram = buildStepDiagram(p)
        let faden = fadenCmFor(astEdges.isEmpty ? [] : buildStitchSequence(astEdges), graph: g)
        content.arm = ArmSection(armEdgeCount: armEdgeCount, steps: armSteps, ids: armIds, fadenCm: faden, diagram: diagram)
    }

    func sternSection(_ prefix: String, _ starEdges: [StickEdge]) -> AnleitungSection? {
        if starEdges.isEmpty { return nil }
        let starSegs = buildStitchSequence(starEdges)
        let starSteps = groupSteps(starSegs, transitionSeg: nil)
        let ids = uniqueIDs(starEdges)
        var points: [String: Point] = [:]
        for id in ids { points[id] = g.point(id) }
        let astschicht = s.astschicht
        let labelOf: (String) -> String = { id in
            let idx = (ids.firstIndex(of: id) ?? -1)
            let isRing = id.hasPrefix("R") && isAllDigits(id.dropFirst())
            return isRing || !astschicht ? "K\(idx + 1)" : "A\(idx + 1)"
        }
        var p = DiagramParams()
        p.keyPrefix = prefix
        p.points = points
        p.ids = ids
        p.steps = Array(starSteps.prefix(3))
        p.labelOf = labelOf
        p.backgroundEdges = starEdges.map { ($0.a, $0.b) }
        p.maxW = limits.sternMax
        p.maxH = limits.sternMax
        p.margin = 40
        p.holeR = 4
        p.labelSize = 11
        p.bendFactor = 0.3; p.bendMin = 18; p.bendMax = 38; p.bendStep = 3
        let diagram = buildStepDiagram(p)
        return AnleitungSection(steps: starSteps, ids: ids, labelOf: labelOf, fadenCm: fadenCmFor(starSegs, graph: g), diagram: diagram)
    }
    if s.sternschicht { content.stern1 = sternSection("s1", star1Edges) }
    if s.sternschicht2 { content.stern2 = sternSection("s2", star2Edges) }
    return content
}

func uniqueIDs(_ edges: [StickEdge]) -> [String] {
    var seen = Set<String>()
    var out: [String] = []
    for e in edges {
        for id in [e.a, e.b] where !seen.contains(id) {
            seen.insert(id)
            out.append(id)
        }
    }
    return out
}
