import Foundation
import CoreGraphics
import StickCore

private enum Farben {
    static let flocke = hexColor("#5b3a70"), flockeTint = hexColor("#f1eaf5")
    static let stern1 = hexColor("#c98a2b"), stern1Tint = hexColor("#faf0df")
    static let stern2 = hexColor("#2f8f8f"), stern2Tint = hexColor("#e6f4f4")
    static let vs = hexColor("#2f7a4d"), rs = hexColor("#b23b3b")
    static let ink = hexColor("#26241f"), sub = hexColor("#6b6558"), line = hexColor("#c9c0ac")
    static let paper = hexColor("#faf6ee"), legendBg = hexColor("#f1ead9")
}

/// Mehrseitige Arbeitsanweisung (A4 hoch): Ebenen-Übersicht, Astschicht, Sternschichten,
/// Fadenlängen und als letzte Seite das Lochmuster 1:1.
public enum Anleitung {
    public static func pdf(_ r: StickResult) -> Data {
        guard let w = PDFWriter(title: "Stickkarten-Anleitung") else { return Data() }
        let content = buildAnleitung(r, limits: DiagramLimits(armMaxW: 680, armMaxH: 760, sternMax: 420))
        let flow = Flow(w)
        flow.render(r, content)
        Lochmuster.drawPage(w, r)
        return w.finish()
    }
}

private final class Flow {
    let w: PDFWriter
    let pageW = 210 * mm, pageH = 297 * mm, margin = 15 * mm
    var y = 0.0
    var pageNo = 0
    var contentW: Double { pageW - 2 * margin }
    var bottom: Double { pageH - margin - 6 * mm }
    let px = 0.75 // CSS-Pixel → Punkte (Diagramme)

    init(_ w: PDFWriter) { self.w = w }

    func newPage() {
        w.beginPage(width: pageW, height: pageH)
        pageNo += 1
        y = margin
        w.text("Seite \(pageNo)", x: pageW / 2, y: pageH - 9 * mm, size: 7, color: Farben.sub, anchor: .middle)
    }

    func ensure(_ h: Double) {
        if pageNo == 0 || y + h > bottom { newPage() }
    }

    func para(_ s: String, size: Double, bold: Bool = false, serif: Bool = false, color: CGColor = Farben.ink, after: Double = 4) {
        let h = w.paragraph(s, x: margin, y: y, width: contentW, size: size, bold: bold, serif: serif, color: color, draw: false)
        ensure(h)
        w.paragraph(s, x: margin, y: y, width: contentW, size: size, bold: bold, serif: serif, color: color)
        y += h + after
    }

    func render(_ r: StickResult, _ c: AnleitungContent) {
        let s = r.settings
        newPage()
        para("Stickkarten-Anleitung", size: 20, bold: true, serif: true, after: 2)
        let fmtLabel = s.formatPreset == .custom ? "\(trim(r.formatW)) × \(trim(r.formatH)) mm" : s.formatPreset.label
        para("Arbeitsanweisung auf Basis der aktuellen Einstellungen (\(fmtLabel), Falz \(s.falzposition.rawValue), Zoom \(Int((s.zoom * 100).rounded())) %).",
             size: 9, color: Farben.sub, after: 6)

        // Legende
        let legendH = 34.0
        w.ctx.setFillColor(Farben.legendBg)
        w.ctx.addPath(CGPath(roundedRect: CGRect(x: margin, y: y, width: contentW, height: legendH), cornerWidth: 5, cornerHeight: 5, transform: nil))
        w.ctx.fillPath()
        w.ctx.setLineWidth(2)
        w.ctx.setStrokeColor(Farben.vs); w.ctx.move(to: CGPoint(x: margin + 8, y: y + 9)); w.ctx.addLine(to: CGPoint(x: margin + 26, y: y + 9)); w.ctx.strokePath()
        w.text("VS — sichtbarer Stich, Vorderseite (gerader Pfeil)", x: margin + 32, y: y + 12, size: 8.5, color: Farben.ink)
        w.ctx.setStrokeColor(Farben.rs); w.ctx.move(to: CGPoint(x: margin + 8, y: y + 19)); w.ctx.addLine(to: CGPoint(x: margin + 26, y: y + 19)); w.ctx.strokePath()
        w.text("RS — verdeckter Sprung, Rückseite (gebogener Pfeil)", x: margin + 32, y: y + 22, size: 8.5, color: Farben.ink)
        w.text("Auf jeden Stich folgt unmittelbar ein Sprung — nur der letzte Schritt einer Schicht nicht.", x: margin + 8, y: y + 31, size: 7.5, color: Farben.sub)
        y += legendH + 12

        // Teil 1
        var teil = 1
        partHeader("Teil 1", "Ebenen", dot: nil)
        para("\(s.astschicht ? "Astschicht aktiv" : "Astschicht deaktiviert") · \(s.sternschicht ? "Sternschicht 1 aktiv" : "Sternschicht 1 deaktiviert") · \(s.sternschicht2 ? "Sternschicht 2 aktiv" : "Sternschicht 2 deaktiviert").",
             size: 8.5, color: Farben.sub)
        layerOverview(r)

        if s.astschicht, let arm = c.arm {
            teil += 1
            partHeader("Teil \(teil)", "Flocke (Astschicht)", dot: Farben.flocke)
            var cap = "Punkt-Kürzel: Z = Zentrum · E1–E\(s.ebenen - 1) = Ebene 1–\(s.ebenen - 1)"
            if s.astAktiv { cap += " · E{L}L/E{L}R = Seitenast links/rechts (ggf. mit Fraktal-Unterspitzen E{L}L.1a usw.)" }
            cap += " · K = Kreispunkt. Ablauf für Ast 1 von \(s.n) — für die übrigen \(s.n - 1) Äste identisch wiederholen, jeweils um \(String(format: "%.1f", 360.0 / Double(s.n)))° weitergedreht."
            para(cap, size: 8.5, color: Farben.sub)
            diagram(arm.diagram, tint: Farben.flockeTint, labelColor: Farben.ink, bgColor: Farben.flocke)
            let rows = arm.steps.enumerated().map { i, st -> [String] in
                var rs = "–"
                if let q = st.rs {
                    rs = "\(astNodeLabel(q.a)) → \(astNodeLabel(q.b))"
                    if st.rsIsTransition { rs += " (Start Ast 2 von \(s.n))" }
                }
                return ["\(i + 1)", "\(astNodeLabel(st.vs.a)) → \(astNodeLabel(st.vs.b))", rs]
            }
            table(rows)
            thread("Fadenlänge Flocke (alle \(s.n) Äste, +15 %): ≈ \(String(format: "%.0f", arm.fadenCm)) cm", color: Farben.flocke, tint: Farben.flockeTint)
        }

        let sterne: [(String, AnleitungSection?, CGColor, CGColor)] = [
            ("Stern 1", c.stern1, Farben.stern1, Farben.stern1Tint),
            ("Stern 2", c.stern2, Farben.stern2, Farben.stern2Tint),
        ]
        for (titel, sec, farbe, tint) in sterne {
            teil += 1
            if let sec = sec {
                partHeader("Teil \(teil)", titel, dot: farbe)
                let isFirst = titel == "Stern 1"
                let level = isFirst ? r.sternEbeneEff1 : r.sternEbeneEff2
                let teiler = isFirst ? r.effTeiler1 : r.effTeiler2
                let k = isFirst ? r.k1Eff : r.k2Eff
                var cap = "Verbindet \(sec.ids.count) Punkte"
                if s.astschicht { cap += " auf Ebene \(level)" }
                if teiler > 1 { cap += " (jeder \(teiler). Kreispunkt)" }
                cap += ", Schrittweite \(k). Blasses Muster im Hintergrund = vollständiger Stern; nur die ersten \(min(3, sec.steps.count)) Schritte sind grafisch dargestellt (Rest wiederholt das Prinzip)."
                para(cap, size: 8.5, color: Farben.sub)
                diagram(sec.diagram, tint: tint, labelColor: Farben.sub, bgColor: farbe)
                let rows = sec.steps.enumerated().map { i, st -> [String] in
                    let rs = st.rs.map { "\(sec.labelOf($0.a)) → \(sec.labelOf($0.b))" } ?? "– (letzter Schritt dieser Schicht)"
                    return ["\(i + 1)", "\(sec.labelOf(st.vs.a)) → \(sec.labelOf(st.vs.b))", rs]
                }
                table(rows)
                thread("Fadenlänge \(titel) (+15 %): ≈ \(String(format: "%.0f", sec.fadenCm)) cm", color: farbe, tint: tint)
            } else if titel == "Stern 2" && !s.sternschicht2 {
                partHeader("Teil \(teil)", titel, dot: farbe)
                para("Deaktiviert (zweite Sternschicht ist in den aktuellen Einstellungen nicht aktiv) — keine Daten, kein Fadenbedarf.", size: 8.5, color: Farben.sub)
            } else {
                teil -= 1
            }
        }

        ensure(40)
        let kennwerte = "Kartenformat \(trim(r.formatW)) × \(trim(r.formatH)) mm · Kreispunkte \(s.n)" + (s.astschicht ? " · Ebenen \(s.ebenen)" : "")
            + " · Mindestabstand ≈ \(String(format: "%.1f", Stick.mindestabstand)) mm · Lochdurchmesser ≈ \(String(format: "%.2f", Stick.lochDurchmesser)) mm."
        y += 8
        para(kennwerte, size: 8, color: Farben.sub)
        para("Die letzte Seite enthält das Lochmuster im Maßstab 1:1 zum Anstechen.", size: 8, color: Farben.sub)
        w.endPage()
    }

    func partHeader(_ label: String, _ title: String, dot: CGColor?) {
        ensure(60)
        y += 10
        w.ctx.setStrokeColor(Farben.line); w.ctx.setLineWidth(0.5)
        w.ctx.move(to: CGPoint(x: margin, y: y)); w.ctx.addLine(to: CGPoint(x: margin + contentW, y: y)); w.ctx.strokePath()
        y += 6
        w.text(label.uppercased(), x: margin, y: y + 6, size: 7, bold: true, color: Farben.sub)
        y += 9
        var tx = margin
        if let dot = dot {
            w.ctx.setFillColor(dot)
            w.ctx.fillEllipse(in: CGRect(x: margin, y: y + 3, width: 8, height: 8))
            tx += 13
        }
        w.text(title, x: tx, y: y + 11, size: 14, bold: true, serif: true, color: Farben.ink)
        y += 20
    }

    func thread(_ s: String, color: CGColor, tint: CGColor) {
        ensure(26)
        let tw = w.textWidth(s, size: 9) + 16
        w.ctx.setFillColor(tint)
        w.ctx.addPath(CGPath(roundedRect: CGRect(x: margin, y: y + 4, width: tw, height: 18), cornerWidth: 4, cornerHeight: 4, transform: nil))
        w.ctx.fillPath()
        w.text(s, x: margin + 8, y: y + 16, size: 9, color: color)
        y += 28
    }

    func table(_ rows: [[String]]) {
        let colX = [margin + 6, margin + 52, margin + 52 + contentW * 0.34]
        let rowH = 15.0
        func header() {
            w.text("SCHRITT", x: colX[0], y: y + 10, size: 7, bold: true, color: Farben.sub)
            w.text("VS", x: colX[1], y: y + 10, size: 7, bold: true, color: Farben.sub)
            w.text("RS", x: colX[2], y: y + 10, size: 7, bold: true, color: Farben.sub)
            w.ctx.setStrokeColor(Farben.line); w.ctx.setLineWidth(1)
            w.ctx.move(to: CGPoint(x: margin, y: y + rowH)); w.ctx.addLine(to: CGPoint(x: margin + contentW, y: y + rowH)); w.ctx.strokePath()
            y += rowH + 1
        }
        ensure(rowH * 3)
        header()
        for row in rows {
            if y + rowH > bottom {
                newPage()
                header()
            }
            w.text(row[0], x: colX[0], y: y + 10, size: 9, bold: true, color: Farben.ink)
            w.text(row[1], x: colX[1], y: y + 10, size: 9, bold: true, color: Farben.vs)
            w.text(row[2], x: colX[2], y: y + 10, size: 9, bold: true, color: Farben.rs)
            w.ctx.setStrokeColor(Farben.line); w.ctx.setLineWidth(0.4)
            w.ctx.move(to: CGPoint(x: margin, y: y + rowH)); w.ctx.addLine(to: CGPoint(x: margin + contentW, y: y + rowH)); w.ctx.strokePath()
            y += rowH
        }
        y += 4
    }

    // MARK: Übersicht der Schichten

    func layerOverview(_ r: StickResult) {
        let g = r.graph
        let pts = g.entries.map { $0.point }
        guard !pts.isEmpty else { return }
        let minX = pts.map { $0.x }.min()!, maxX = pts.map { $0.x }.max()!
        let minY = pts.map { $0.y }.min()!, maxY = pts.map { $0.y }.max()!
        let bw = max(maxX - minX, 1e-6), bh = max(maxY - minY, 1e-6)
        let card = 82.0
        ensure(card + 24)
        let s = r.settings
        let astEdges = s.astschicht ? Array(g.edges[0..<g.astCount]) : []
        let s1 = s.sternschicht ? Array(g.edges[g.astCount..<(g.astCount + g.star1Count)]) : []
        let s2 = s.sternschicht2 ? Array(g.edges[(g.astCount + g.star1Count)..<(g.astCount + g.star1Count + g.star2Count)]) : []
        let scale = (card - 12) / max(bw, bh)
        func draw(_ edges: [StickEdge], _ color: CGColor, _ lw: Double, _ ox: Double, _ oy: Double) {
            w.ctx.setStrokeColor(color); w.ctx.setLineWidth(lw)
            for e in edges {
                let a = g.point(e.a), b = g.point(e.b)
                w.ctx.move(to: CGPoint(x: ox + card / 2 + (a.x - (minX + maxX) / 2) * scale, y: oy + card / 2 + (a.y - (minY + maxY) / 2) * scale))
                w.ctx.addLine(to: CGPoint(x: ox + card / 2 + (b.x - (minX + maxX) / 2) * scale, y: oy + card / 2 + (b.y - (minY + maxY) / 2) * scale))
            }
            w.ctx.strokePath()
        }
        let cards: [(String, Bool)] = [("Flocke", s.astschicht), ("Stern 1", s.sternschicht), ("Stern 2", s.sternschicht2), ("Gesamtbild", true)]
        let gap = (contentW - 4 * card) / 3
        for (i, cd) in cards.enumerated() {
            let ox = margin + Double(i) * (card + gap)
            w.ctx.setFillColor(gray(1))
            w.ctx.setStrokeColor(Farben.line); w.ctx.setLineWidth(0.6)
            let path = CGPath(roundedRect: CGRect(x: ox, y: y, width: card, height: card), cornerWidth: 5, cornerHeight: 5, transform: nil)
            w.ctx.addPath(path); w.ctx.drawPath(using: .fillStroke)
            switch i {
            case 0: if cd.1 { draw(astEdges, Farben.flocke, 1.2, ox, y) }
            case 1: if cd.1 { draw(s1, Farben.stern1, 1.0, ox, y) }
            case 2: if cd.1 { draw(s2, Farben.stern2, 1.0, ox, y) }
            default:
                if s.astschicht { draw(astEdges, Farben.flocke, 1.1, ox, y) }
                if s.sternschicht { draw(s1, Farben.stern1, 0.9, ox, y) }
                if s.sternschicht2 { draw(s2, Farben.stern2, 0.9, ox, y) }
            }
            if !cd.1 { w.text("deaktiviert", x: ox + card / 2, y: y + card - 6, size: 6.5, color: Farben.sub, anchor: .middle) }
            w.text(cd.0.uppercased(), x: ox + card / 2, y: y + card + 11, size: 7, color: Farben.sub, anchor: .middle)
        }
        y += card + 20
    }

    // MARK: Schrittdiagramm

    func diagram(_ d: StepDiagram, tint: CGColor, labelColor: CGColor, bgColor: CGColor) {
        let pad = 8.0
        let scale = px
        let bw = d.width * scale, bh = d.height * scale
        ensure(bh + 2 * pad + 6)
        let ox = margin + pad, oy = y + pad
        let ctx = w.ctx
        ctx.setFillColor(tint)
        ctx.setStrokeColor(Farben.line); ctx.setLineWidth(0.6)
        ctx.addPath(CGPath(roundedRect: CGRect(x: margin, y: y, width: bw + 2 * pad, height: bh + 2 * pad), cornerWidth: 6, cornerHeight: 6, transform: nil))
        ctx.drawPath(using: .fillStroke)

        func P(_ x: Double, _ y: Double) -> CGPoint { CGPoint(x: ox + x * scale, y: oy + y * scale) }
        func arrow(tip: CGPoint, from: CGPoint, length: Double, half: Double, color: CGColor) {
            let dx = tip.x - from.x, dy = tip.y - from.y
            let len = max(hypot(dx, dy), 1e-9)
            let ux = dx / len, uy = dy / len
            let base = CGPoint(x: tip.x - ux * length, y: tip.y - uy * length)
            ctx.setFillColor(color)
            ctx.move(to: tip)
            ctx.addLine(to: CGPoint(x: base.x - uy * half, y: base.y + ux * half))
            ctx.addLine(to: CGPoint(x: base.x + uy * half, y: base.y - ux * half))
            ctx.closePath()
            ctx.fillPath()
        }

        for el in d.elements {
            switch el {
            case let .line(x1, y1, x2, y2, role):
                if role == .background {
                    ctx.setStrokeColor(bgColor.copy(alpha: 0.22) ?? bgColor)
                    ctx.setLineWidth(1.6 * scale)
                    ctx.move(to: P(x1, y1)); ctx.addLine(to: P(x2, y2)); ctx.strokePath()
                } else {
                    ctx.setStrokeColor(Farben.vs); ctx.setLineWidth(1.8 * scale)
                    // Linie endet kurz vor der Spitze, damit Pfeilkopf sauber sitzt
                    ctx.move(to: P(x1, y1)); ctx.addLine(to: P(x2, y2)); ctx.strokePath()
                    arrow(tip: P(x2, y2).applying(.identity), from: P(x1, y1), length: 5.8 * scale, half: 4.1 * scale, color: Farben.vs)
                }
            case let .curve(x1, y1, cx, cy, x2, y2, _):
                ctx.saveGState()
                ctx.setStrokeColor(Farben.rs); ctx.setLineWidth(1.8 * scale)
                ctx.setLineCap(.round)
                ctx.setLineDash(phase: 0, lengths: [0.1 * scale, 5 * scale])
                ctx.move(to: P(x1, y1))
                ctx.addQuadCurve(to: P(x2, y2), control: P(cx, cy))
                ctx.strokePath()
                ctx.restoreGState()
                arrow(tip: P(x2, y2), from: P(cx, cy), length: 7.6 * scale, half: 5.4 * scale, color: Farben.rs)
            case let .circle(cx, cy, r, role):
                let rect = CGRect(x: P(cx, cy).x - r * scale, y: P(cx, cy).y - r * scale, width: 2 * r * scale, height: 2 * r * scale)
                switch role {
                case .hole:
                    if d.holeOutlined {
                        ctx.setFillColor(Farben.paper); ctx.setStrokeColor(Farben.ink); ctx.setLineWidth(1.4 * scale)
                        ctx.addEllipse(in: rect); ctx.drawPath(using: .fillStroke)
                    } else {
                        ctx.setFillColor(Farben.ink); ctx.fillEllipse(in: rect)
                    }
                case .vsBadge:
                    ctx.setFillColor(gray(1)); ctx.setStrokeColor(Farben.vs); ctx.setLineWidth(2 * scale)
                    ctx.addEllipse(in: rect); ctx.drawPath(using: .fillStroke)
                default:
                    ctx.setFillColor(gray(1)); ctx.setStrokeColor(Farben.rs); ctx.setLineWidth(2 * scale)
                    ctx.addEllipse(in: rect); ctx.drawPath(using: .fillStroke)
                }
            case let .text(x, y, t, anchor, role):
                let color: CGColor = role == .vsBadge ? Farben.vs : role == .rsBadge ? Farben.rs : labelColor
                let size = (role == .label ? d.labelSize : d.badgeFontSize) * scale
                w.text(t, x: P(x, y).x, y: P(x, y).y, size: size, bold: true, color: color, anchor: anchor)
            }
        }
        y += bh + 2 * pad + 8
    }
}
