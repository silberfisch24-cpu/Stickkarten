import SwiftUI
import StickCore

/// Kartenansicht (Einheit: mm). Löcher sind klein (Ø ≈ 0,9 mm ≈ 3 pt), darum werden Marker für
/// „knapp“ (Kreis) und „zu eng“ (Raute) mindestens 5 pt groß gezeichnet und unterscheiden sich in der
/// Form, nicht nur in der Farbe.
struct KartenView: View {
    let result: StickResult
    let appearance: AppearanceSettings
    /// Anzahl gezeichneter Schritte der Stichfolge. `nil` = alle.
    var schritt: Int? = nil

    var body: some View {
        Canvas { ctx, size in zeichnen(&ctx, size) }
            .aspectRatio(CGFloat(result.formatW / max(result.formatH, 0.001)), contentMode: .fit)
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(beschreibung)
    }

    private var beschreibung: String {
        var t = "Stickkarte mit \(result.graph.nodeIDs.count) Löchern und \(result.stitchCount) Stichen."
        if result.hasCritical {
            t += " Löcher zu eng, Stiche ausgeblendet."
        } else if result.hasModerate {
            t += " Lochabstand knapp."
        }
        return t
    }

    private func zeichnen(_ ctx: inout GraphicsContext, _ size: CGSize) {
        let r = result
        let karton = Kartonfarbe.mit(id: appearance.kartonfarbe)
        let faden = Color(hex: Fadenfarbe.mit(id: appearance.fadenfarbe).hex)
        let s = min(Double(size.width) / r.formatW, Double(size.height) / r.formatH)
        ctx.translateBy(x: (Double(size.width) - r.formatW * s) / 2, y: (Double(size.height) - r.formatH * s) / 2)
        ctx.scaleBy(x: s, y: s)
        ctx.fill(Path(CGRect(x: 0, y: 0, width: r.formatW, height: r.formatH)), with: .color(Color(hex: karton.hex)))

        let falz = StrokeStyle(lineWidth: 0.3, dash: [2, 1.5])
        if r.settings.falzposition == .links {
            var p = Path(); p.move(to: CGPoint(x: 0.4, y: 0)); p.addLine(to: CGPoint(x: 0.4, y: r.formatH))
            ctx.stroke(p, with: .color(.black.opacity(0.35)), style: falz)
        } else if r.settings.falzposition == .oben {
            var p = Path(); p.move(to: CGPoint(x: 0, y: 0.4)); p.addLine(to: CGPoint(x: r.formatW, y: 0.4))
            ctx.stroke(p, with: .color(.black.opacity(0.35)), style: falz)
        }
        let nutz = CGRect(x: r.margins.left, y: r.margins.top, width: r.usableW, height: r.usableH)
        ctx.stroke(Path(nutz), with: .color(.black.opacity(0.15)), style: StrokeStyle(lineWidth: 0.25, dash: [1.5, 1.5]))

        let g = r.graph
        func pt(_ id: String) -> CGPoint { let p = g.point(id); return CGPoint(x: p.x, y: p.y) }

        if !r.hasCritical {
            let segs = r.segments
            let bis = min(schritt ?? segs.count, segs.count)
            var stiche = Path(), spruenge = Path()
            for i in 0..<bis {
                let sg = segs[i]
                if i == bis - 1 && schritt != nil { continue }
                if sg.isJump {
                    if appearance.zeigeSpruenge { spruenge.move(to: pt(sg.a)); spruenge.addLine(to: pt(sg.b)) }
                } else {
                    stiche.move(to: pt(sg.a)); stiche.addLine(to: pt(sg.b))
                }
            }
            ctx.stroke(spruenge, with: .color(.white.opacity(0.3)), style: StrokeStyle(lineWidth: 0.18, dash: [0.6, 0.8]))
            ctx.stroke(stiche, with: .color(faden), style: StrokeStyle(lineWidth: 0.4, lineCap: .round))
        }

        var ok = Path(), warn = Path(), krit = Path()
        let basis = Stick.lochDurchmesser / 2
        let markerR = max(basis + 0.25, 2.5 / s)
        for (id, p) in g.entries {
            switch r.severity[id] ?? .ok {
            case .ok:
                ok.addEllipse(in: CGRect(x: p.x - basis, y: p.y - basis, width: 2 * basis, height: 2 * basis))
            case .moderate:
                warn.addEllipse(in: CGRect(x: p.x - markerR, y: p.y - markerR, width: 2 * markerR, height: 2 * markerR))
            case .critical:
                krit.move(to: CGPoint(x: p.x, y: p.y - markerR))
                krit.addLine(to: CGPoint(x: p.x + markerR, y: p.y))
                krit.addLine(to: CGPoint(x: p.x, y: p.y + markerR))
                krit.addLine(to: CGPoint(x: p.x - markerR, y: p.y))
                krit.closeSubpath()
            }
        }
        ctx.fill(ok, with: .color(.black.opacity(0.4)))
        ctx.fill(warn, with: .color(Color(hex: warnFarbeHex)))
        ctx.stroke(warn, with: .color(.black.opacity(0.5)), style: StrokeStyle(lineWidth: 0.2))
        ctx.fill(krit, with: .color(Color(hex: gefahrFarbeHex)))
        ctx.stroke(krit, with: .color(.white), style: StrokeStyle(lineWidth: 0.25))
    }
}
