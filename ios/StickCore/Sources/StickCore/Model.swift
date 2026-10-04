import Foundation

public enum Severity: String {
    case ok, moderate, critical
}

public struct Margins: Equatable {
    public var top: Double
    public var right: Double
    public var bottom: Double
    public var left: Double
}

/// Alles, was die Web-App aus den Einstellungen ableitet (Hauptkomponente, Z. 1019–1160).
public struct StickResult {
    public let settings: StickSettings

    // Format / Fläche
    public let formatW: Double
    public let formatH: Double
    public let margins: Margins
    public let usableW: Double
    public let usableH: Double
    public let cx: Double
    public let cy: Double
    public let Rmax: Double
    public let Rmin: Double
    public let formatOk: Bool
    public let R: Double

    // Sternschicht-Optionen
    public let teilerOptionen: [Int]
    public let effTeiler1: Int
    public let effTeiler2: Int
    public let sternPunkte1: Int
    public let sternPunkte2: Int
    public let kMax1: Int
    public let kMax2: Int
    public let k1Eff: Int
    public let k2Eff: Int
    public let sternEbeneEff1: Int
    public let sternEbeneEff2: Int
    public let branchLevels: [Int]
    public let skip1ExaktMoeglich: Bool
    public let skip1LeMoeglich: Bool
    public let skip2ExaktMoeglich: Bool
    public let skip2LeMoeglich: Bool
    public let skip1CapLvl: Int
    public let skip2CapLvl: Int
    public let unterdrueckteEbenen: Set<Int>

    // Graph / Stichfolge
    public let graph: StickGraph
    public let segments: [StitchSegment]
    public let stitchCount: Int
    public let jumpCount: Int
    public let frontLength: Double
    public let jumpLength: Double

    // Abstände / Warnungen
    public let severity: [String: Severity]
    public let hasCritical: Bool
    public let hasModerate: Bool
    public let warnungen: [String]

    public var maxStep: Int { segments.count }
    /// Fadenlänge inkl. 15 % Zuschlag, in cm
    public var fadenCm: Double { ((frontLength + jumpLength) * Stick.fadenZuschlag) / 10 }
    public var flat: FlatSheet { computeFlatSheet(w: formatW, h: formatH, falzposition: settings.falzposition) }
    public var pageFit: PageFit { pageFitFor(flat) }
}

public enum StickModel {
    public static func compute(_ s: StickSettings) -> StickResult {
        let size: (w: Double, h: Double)
        if s.formatPreset == .custom {
            size = (s.customW, s.customH)
        } else {
            size = s.formatPreset.size ?? (105, 148)
        }
        var m = Margins(top: Stick.randMin, right: Stick.randMin, bottom: Stick.randMin, left: Stick.randMin)
        if s.falzposition == .links { m.left = Stick.falzMin }
        if s.falzposition == .oben { m.top = Stick.falzMin }

        let usableW = max(1, size.w - m.left - m.right)
        let usableH = max(1, size.h - m.top - m.bottom)
        let cx = m.left + usableW / 2
        let cy = m.top + usableH / 2
        let Rmax = min(usableW, usableH) / 2

        let n = s.n
        let ebenen = s.ebenen
        let teilerOptionen = divisorsOf(n)
        let effTeiler1 = teilerOptionen.contains(s.sternTeiler) ? s.sternTeiler : 1
        let sternPunkte1 = n / effTeiler1
        let kMax1 = max(1, Int((Double(sternPunkte1) / 2).rounded(.down)) - (s.astschicht ? 1 : 0))
        let effTeiler2 = teilerOptionen.contains(s.sternTeiler2) ? s.sternTeiler2 : 1
        let sternPunkte2 = n / effTeiler2
        let kMax2 = max(1, Int((Double(sternPunkte2) / 2).rounded(.down)) - (s.astschicht ? 1 : 0))

        let branchLevels = astBranchLevels(ebenen)
        let sternEbeneEff1 = min(s.sternEbene, ebenen)
        let sternEbeneEff2 = min(s.sternEbene2, ebenen)
        let ausblendungBasis = s.astschicht && s.astAktiv && !branchLevels.isEmpty
        let skip1Exakt = ausblendungBasis && s.sternschicht && branchLevels.contains(sternEbeneEff1)
        let skip1Le = ausblendungBasis && s.sternschicht && sternEbeneEff1 >= 2
        let skip2Exakt = ausblendungBasis && s.sternschicht && s.sternschicht2 && branchLevels.contains(sternEbeneEff2)
        let skip2Le = ausblendungBasis && s.sternschicht && s.sternschicht2 && sternEbeneEff2 >= 2

        // Die beiden Sternschicht-Optionen wirken additiv.
        var unterdrueckt = Set<Int>()
        if ausblendungBasis {
            if s.sternschicht {
                if s.astAusblendung1 == .exakt && branchLevels.contains(sternEbeneEff1) { unterdrueckt.insert(sternEbeneEff1) }
                if s.astAusblendung1 == .kleinerGleich { for L in branchLevels where L <= sternEbeneEff1 { unterdrueckt.insert(L) } }
            }
            if s.sternschicht && s.sternschicht2 {
                if s.astAusblendung2 == .exakt && branchLevels.contains(sternEbeneEff2) { unterdrueckt.insert(sternEbeneEff2) }
                if s.astAusblendung2 == .kleinerGleich { for L in branchLevels where L <= sternEbeneEff2 { unterdrueckt.insert(L) } }
            }
        }

        var Rmin = 12.0
        Rmin = max(Rmin, (Stick.mindestabstand * Double(n)) / (2 * Double.pi))
        if s.astschicht { Rmin = max(Rmin, Stick.mindestabstand * Double(ebenen)) }
        let formatOk = Rmin <= Rmax
        let R = formatOk ? Rmin + s.zoom * (Rmax - Rmin) : Rmax

        let k1Eff = min(s.k1, kMax1)
        let k2Eff = min(s.k2, kMax2)
        let graph = buildGraph(GraphParams(
            n: n, R: R, cx: cx, cy: cy, astschicht: s.astschicht, ebenen: ebenen, astAktiv: s.astAktiv,
            astWinkel: s.astWinkel, astLaenge: s.astLaenge, astWachstum: s.astWachstum,
            fraktalTiefe: s.fraktalTiefe, fraktalSkalierung: s.fraktalSkalierung,
            sternschicht: s.sternschicht, sternEbene: sternEbeneEff1, sternTeiler: effTeiler1, k1: k1Eff,
            sternschicht2: s.sternschicht2, sternEbene2: sternEbeneEff2, sternTeiler2: effTeiler2,
            sternVersatz2: s.sternVersatz2, k2: k2Eff, unterdrueckteEbenen: unterdrueckt
        ))
        let segments = buildStitchSequence(graph.edges)
        var frontLength = 0.0
        var jumpLength = 0.0
        var stitchCount = 0
        for seg in segments {
            let d = dist(graph.point(seg.a), graph.point(seg.b))
            if seg.isJump { jumpLength += d } else { frontLength += d; stitchCount += 1 }
        }

        // Abstands-Klassifizierung je Punkt
        let (severity, hasCritical, hasModerate) = classify(graph)

        var warnungen: [String] = []
        if !s.astschicht && !s.sternschicht { warnungen.append("Aktiviere mindestens eine Musterschicht (Astschicht oder Sternschicht).") }
        if !formatOk { warnungen.append("Bei dieser Achsen-/Ebenenzahl passt kein gültiger Mindestabstand auf diese Karte.") }
        if stitchCount > Stick.stichLimit {
            warnungen.append("\(stitchCount) Stiche — mehr als das Richtmaß von \(Stick.stichLimit). Für eine handhabbare Karte Kreispunkte oder Ebenen reduzieren.")
        }
        let minAbst = String(format: "%.1f", Stick.mindestabstand)
        if hasCritical {
            warnungen.append("Manche Löcher liegen unter dem Mindestabstand (\(minAbst) mm) — Stiche werden nicht angezeigt, bis der Zoom verkleinert wird.")
        } else if hasModerate {
            warnungen.append("Manche Löcher liegen nur knapp über dem Mindestabstand (\(minAbst) mm) — betroffene Punkte sind markiert.")
        }

        return StickResult(
            settings: s, formatW: size.w, formatH: size.h, margins: m, usableW: usableW, usableH: usableH,
            cx: cx, cy: cy, Rmax: Rmax, Rmin: Rmin, formatOk: formatOk, R: R,
            teilerOptionen: teilerOptionen, effTeiler1: effTeiler1, effTeiler2: effTeiler2,
            sternPunkte1: sternPunkte1, sternPunkte2: sternPunkte2, kMax1: kMax1, kMax2: kMax2,
            k1Eff: k1Eff, k2Eff: k2Eff, sternEbeneEff1: sternEbeneEff1, sternEbeneEff2: sternEbeneEff2,
            branchLevels: branchLevels, skip1ExaktMoeglich: skip1Exakt, skip1LeMoeglich: skip1Le,
            skip2ExaktMoeglich: skip2Exakt, skip2LeMoeglich: skip2Le,
            skip1CapLvl: min(sternEbeneEff1, ebenen - 1), skip2CapLvl: min(sternEbeneEff2, ebenen - 1),
            unterdrueckteEbenen: unterdrueckt, graph: graph, segments: segments,
            stitchCount: stitchCount, jumpCount: segments.count - stitchCount,
            frontLength: frontLength, jumpLength: jumpLength,
            severity: severity, hasCritical: hasCritical, hasModerate: hasModerate, warnungen: warnungen
        )
    }

    /// Abstands-Klassifizierung: ok / moderat (< 1,5 × Mindestabstand) / kritisch (< Mindestabstand).
    static func classify(_ graph: StickGraph) -> ([String: Severity], Bool, Bool) {
        let ids = graph.nodeIDs
        let xs = ids.map { graph.point($0).x }
        let ys = ids.map { graph.point($0).y }
        var sev: [String: Severity] = [:]
        var critical = false
        var moderate = false
        for i in 0..<ids.count {
            var nearest = Double.infinity
            for j in 0..<ids.count where j != i {
                let d = hypot(xs[i] - xs[j], ys[i] - ys[j])
                if d < nearest { nearest = d }
            }
            var s = Severity.ok
            if nearest < Stick.mindestabstand { s = .critical; critical = true }
            else if nearest < Stick.mindestabstand * Stick.moderatFaktor { s = .moderate; moderate = true }
            sev[ids[i]] = s
        }
        return (sev, critical, moderate)
    }
}
