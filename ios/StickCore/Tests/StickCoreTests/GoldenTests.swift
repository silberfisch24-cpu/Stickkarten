import XCTest
import Foundation
@testable import StickCore

final class GoldenTests: XCTestCase {
    let tol = 1e-9

    func testGrid() throws { try runFile("grid") }
    func testFraktal() throws { try runFile("fraktal") }
    func testAusblendung() throws { try runFile("ausblendung") }
    func testRandom() throws { try runFile("random") }

    func testConstantsMatchReference() throws {
        struct Meta: Decodable {
            var FADEN_DURCHMESSER, LOCH_DURCHMESSER, MINDESTABSTAND, RAND_MIN, FALZ_MIN, STICH_LIMIT, MODERAT_FAKTOR: Double
            var FORMATE: [String: Fmt]
            struct Fmt: Decodable { var w: Double?; var h: Double? }
        }
        let m: Meta = try loadGolden("meta")
        XCTAssertEqual(Stick.fadenDurchmesser, m.FADEN_DURCHMESSER, accuracy: 1e-12)
        XCTAssertEqual(Stick.lochDurchmesser, m.LOCH_DURCHMESSER, accuracy: 1e-12)
        XCTAssertEqual(Stick.mindestabstand, m.MINDESTABSTAND, accuracy: 1e-12)
        XCTAssertEqual(Stick.randMin, m.RAND_MIN)
        XCTAssertEqual(Stick.falzMin, m.FALZ_MIN)
        XCTAssertEqual(Double(Stick.stichLimit), m.STICH_LIMIT)
        XCTAssertEqual(Stick.moderatFaktor, m.MODERAT_FAKTOR)
        XCTAssertEqual(FormatPreset.a6Hoch.size?.w, m.FORMATE["a6-hoch"]?.w)
        XCTAssertEqual(FormatPreset.a6Hoch.size?.h, m.FORMATE["a6-hoch"]?.h)
        XCTAssertEqual(FormatPreset.a6Quer.size?.w, m.FORMATE["a6-quer"]?.w)
        XCTAssertEqual(FormatPreset.a6Quer.size?.h, m.FORMATE["a6-quer"]?.h)
    }

    func testLayoutTables() throws {
        let rows: [GLayout] = try loadGolden("layout")
        let c = Checker()
        for row in rows {
            c.context = "\(row.w)x\(row.h) \(row.falz)"
            let flat = computeFlatSheet(w: row.w, h: row.h, falzposition: Falzposition(rawValue: row.falz)!)
            compare(flat: flat, row.flat, c)
            compare(pageFit: pageFitFor(flat), row.pageFit, c)
        }
        c.finish("layout")
    }

    // MARK: -

    private func runFile(_ name: String) throws {
        let records: [GRecord] = try loadGolden(name)
        XCTAssertFalse(records.isEmpty)
        let c = Checker()
        for rec in records {
            c.context = rec.name
            check(rec, c)
        }
        c.finish(name)
    }

    private func check(_ rec: GRecord, _ c: Checker) {
        let r = StickModel.compute(rec.settings)
        let d = rec.derived

        // abgeleitete Werte
        c.close(r.formatW, d.formatW, tol, "formatW"); c.close(r.formatH, d.formatH, tol, "formatH")
        c.close(r.margins.top, d.margins.top, tol, "margin.top"); c.close(r.margins.left, d.margins.left, tol, "margin.left")
        c.close(r.margins.right, d.margins.right, tol, "margin.right"); c.close(r.margins.bottom, d.margins.bottom, tol, "margin.bottom")
        c.close(r.usableW, d.usableW, tol, "usableW"); c.close(r.usableH, d.usableH, tol, "usableH")
        c.close(r.cx, d.cx, tol, "cx"); c.close(r.cy, d.cy, tol, "cy")
        c.close(r.Rmax, d.Rmax, tol, "Rmax"); c.close(r.Rmin, d.Rmin, tol, "Rmin"); c.close(r.R, d.R, tol, "R")
        c.expect(r.formatOk == d.formatOk, "formatOk")
        c.expect(r.effTeiler1 == d.effTeiler1 && r.effTeiler2 == d.effTeiler2, "effTeiler")
        c.expect(r.kMax1 == d.kMax1 && r.kMax2 == d.kMax2, "kMax")
        c.expect(r.k1Eff == d.k1Eff && r.k2Eff == d.k2Eff, "kEff")
        c.expect(r.sternEbeneEff1 == d.sternEbeneEff1 && r.sternEbeneEff2 == d.sternEbeneEff2, "sternEbeneEff")
        c.expect(r.unterdrueckteEbenen.sorted() == d.unterdrueckteEbenen, "unterdrueckteEbenen \(r.unterdrueckteEbenen.sorted()) ≠ \(d.unterdrueckteEbenen)")

        // Knoten (Reihenfolge + Position)
        let g = r.graph
        c.expect(g.nodeIDs == rec.nodes.ids, "Knoten-IDs/Reihenfolge: \(g.nodeIDs.count) vs \(rec.nodes.ids.count)")
        if g.nodeIDs == rec.nodes.ids {
            for (i, id) in g.nodeIDs.enumerated() {
                let p = g.point(id)
                c.close(p.x, rec.nodes.x[i], tol, "Knoten \(id).x")
                c.close(p.y, rec.nodes.y[i], tol, "Knoten \(id).y")
            }
        }

        // Kanten (Reihenfolge entscheidend)
        c.expect(g.edges.count == rec.edges.a.count, "Kantenzahl \(g.edges.count) vs \(rec.edges.a.count)")
        if g.edges.count == rec.edges.a.count {
            for (i, e) in g.edges.enumerated() {
                c.expect(e.a == rec.edges.a[i] && e.b == rec.edges.b[i] && e.id == rec.edges.id[i],
                         "Kante \(i): \(e.a)-\(e.b) ≠ \(rec.edges.a[i])-\(rec.edges.b[i])")
                c.close(e.len, rec.edges.len[i], tol, "Kante \(i).len")
            }
        }
        c.expect(g.astCount == rec.counts.ast && g.star1Count == rec.counts.star1 && g.star2Count == rec.counts.star2, "Phasenzähler")

        // Stichfolge
        let sg = rec.segments
        c.expect(r.segments.count == sg.a.count, "Segmentzahl \(r.segments.count) vs \(sg.a.count)")
        if r.segments.count == sg.a.count {
            for (i, s) in r.segments.enumerated() {
                c.expect(s.a == sg.a[i] && s.b == sg.b[i] && s.isJump == (sg.jump[i] == 1), "Segment \(i)")
            }
        }

        // Statistik
        c.expect(r.stitchCount == rec.stats.stitchCount && r.jumpCount == rec.stats.jumpCount && r.maxStep == rec.stats.maxStep, "Stichzahlen")
        c.close(r.frontLength, rec.stats.frontLength, 1e-8, "frontLength")
        c.close(r.jumpLength, rec.stats.jumpLength, 1e-8, "jumpLength")
        c.close(r.fadenCm, rec.stats.fadenCm, 1e-8, "fadenCm")

        // Abstands-Klassifizierung + Warnungen
        let sev = g.nodeIDs.map { id -> Character in
            switch r.severity[id] ?? .ok {
            case .ok: return "o"
            case .moderate: return "m"
            case .critical: return "c"
            }
        }
        // Liegt der nächste Nachbar exakt auf einer Schwelle (z. B. Zoom 0 => Astabstand == Mindestabstand),
        // entscheidet das letzte Bit von hypot() — JS und Swift dürfen dort verschieden runden.
        let ids = g.nodeIDs
        for (i, ch) in String(sev).enumerated() where i < rec.severity.count {
            let refCh = Array(rec.severity)[i]
            if ch == refCh { continue }
            var nearest = Double.infinity
            for j in 0..<ids.count where j != i { nearest = min(nearest, dist(g.point(ids[i]), g.point(ids[j]))) }
            let onThreshold = abs(nearest - Stick.mindestabstand) < 1e-9 || abs(nearest - Stick.mindestabstand * Stick.moderatFaktor) < 1e-9
            c.expect(onThreshold, "Severity Knoten \(ids[i]): \(ch) ≠ \(refCh), Nachbarabstand \(nearest)")
        }
        c.expect(String(sev).count == rec.severity.count, "Severity-Länge")
        c.expect(r.hasCritical == rec.hasCritical && r.hasModerate == rec.hasModerate, "hasCritical/hasModerate")
        c.expect(r.warnungen == rec.warnungen, "Warnungen \(r.warnungen) ≠ \(rec.warnungen)")

        compare(flat: r.flat, rec.flat, c)
        compare(pageFit: r.pageFit, rec.pageFit, c)

        if let an = rec.anleitung { checkAnleitung(r, an, c) }
    }

    private func compare(flat: FlatSheet, _ g: GFlat, _ c: Checker) {
        c.close(flat.w, g.w, tol, "flat.w"); c.close(flat.h, g.h, tol, "flat.h")
        c.close(flat.offX, g.offX, tol, "flat.offX"); c.close(flat.offY, g.offY, tol, "flat.offY")
        c.expect(flat.foldAxis?.rawValue == g.foldAxis, "foldAxis")
        c.expect(flat.foldPos == g.foldPos, "foldPos")
    }

    private func compare(pageFit: PageFit, _ g: GPageFit, _ c: Checker) {
        c.expect(pageFit.orientation.rawValue == g.orientation, "pageFit.orientation \(pageFit.orientation) ≠ \(g.orientation)")
        c.close(pageFit.pageW, g.pageW, tol, "pageW"); c.close(pageFit.pageH, g.pageH, tol, "pageH")
        c.close(pageFit.availW, g.availW, tol, "availW"); c.close(pageFit.availH, g.availH, tol, "availH")
        c.close(pageFit.scale, g.scale, tol, "scale")
        c.expect(pageFit.fits == g.fits, "fits")
    }

    private func checkAnleitung(_ r: StickResult, _ an: GAnleitung, _ c: Checker) {
        let content = buildAnleitung(r)
        c.expect((content.arm != nil) == (an.arm != nil), "Arm-Abschnitt vorhanden")
        if let a = content.arm, let g = an.arm {
            c.expect(a.armEdgeCount == g.armEdgeCount, "armEdgeCount")
            compare(steps: a.steps, g.steps, c, "arm")
            c.expect(a.ids == g.labels.map { $0[0] }, "arm ids")
            c.expect(a.ids.map(astNodeLabel) == g.labels.map { $0[1] }, "arm Labels")
            c.close(a.fadenCm, g.fadenCm, 1e-8, "arm fadenCm")
            compare(diagram: a.diagram, width: g.width, height: g.height, g.elements, c, "arm")
        }
        for (name, mine, ref) in [("stern1", content.stern1, an.stern1), ("stern2", content.stern2, an.stern2)] {
            c.expect((mine != nil) == (ref != nil), "\(name) vorhanden")
            if let s = mine, let g = ref {
                c.expect(s.ids == g.ids, "\(name) ids")
                c.expect(s.ids.map(s.labelOf) == g.labels, "\(name) Labels")
                compare(steps: s.steps, g.steps, c, name)
                c.close(s.fadenCm, g.fadenCm, 1e-8, "\(name) fadenCm")
                compare(diagram: s.diagram, width: g.width, height: g.height, g.elements, c, name)
            }
        }
    }

    private func compare(steps: [StitchStep], _ g: [GStep], _ c: Checker, _ what: String) {
        c.expect(steps.count == g.count, "\(what) Schrittzahl \(steps.count) vs \(g.count)")
        if steps.count != g.count { return }
        for (i, s) in steps.enumerated() {
            c.expect([s.vs.a, s.vs.b] == g[i].vs, "\(what) Schritt \(i + 1) VS")
            let rs: [String]? = s.rs.map { [$0.a, $0.b] }
            c.expect(rs == g[i].rs, "\(what) Schritt \(i + 1) RS")
            c.expect(s.rsIsTransition == g[i].rsIsTransition, "\(what) Schritt \(i + 1) Übergang")
        }
    }

    private func compare(diagram: StepDiagram, width: Double, height: Double, _ g: [GElement], _ c: Checker, _ what: String) {
        c.close(diagram.width, width, 0, "\(what) Diagrammbreite")
        c.close(diagram.height, height, 0, "\(what) Diagrammhöhe")
        c.expect(diagram.elements.count == g.count, "\(what) Elementzahl \(diagram.elements.count) vs \(g.count)")
        if diagram.elements.count != g.count { return }
        for (i, el) in diagram.elements.enumerated() {
            let kind: String
            var v: [Double]
            var text: String? = nil
            switch el {
            case let .line(x1, y1, x2, y2, _): kind = "line"; v = [x1, y1, x2, y2]
            case let .curve(x1, y1, cx, cy, x2, y2, _): kind = "path"; v = [x1, y1, cx, cy, x2, y2]
            case let .circle(cx, cy, rr, _): kind = "circle"; v = [cx, cy, rr]
            case let .text(x, y, t, _, _): kind = "text"; v = [x, y]; text = t
            }
            c.expect(kind == g[i].k, "\(what) Element \(i): \(kind) ≠ \(g[i].k)")
            if kind != g[i].k || v.count != g[i].v.count { continue }
            // Linien (VS/Hintergrund) und Lochkreise (r < 6) sind reine Fit-Geometrie => streng.
            // RS-Bögen, Zahlenkreise und Beschriftungen hängen von Kollisions-/Winkel-Entscheidungen
            // ab, die in symmetrischen Mustern auf exakten Gleichständen beruhen (letztes Bit von
            // hypot/atan2 in V8 vs. libm) => nur grobe Plausibilität (< 60 px).
            let strict = kind == "line" || (kind == "circle" && g[i].v[2] < 6)
            for (j, val) in v.enumerated() { c.close(val, g[i].v[j], strict ? 1e-6 : 60, "\(what) Element \(i) (\(kind)) Wert \(j)") }
            if case let .text(_, _, _, anchor, _) = el { c.expect(anchor.rawValue == g[i].anchor, "\(what) Element \(i) Anker") }
            if let t = text { c.expect(t == g[i].s, "\(what) Element \(i) Text '\(t)' ≠ '\(g[i].s ?? "nil")'") }
        }
    }
}
