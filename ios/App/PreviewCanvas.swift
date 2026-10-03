import SwiftUI
import StickCore

/// Kartenvorschau mit animierter Stichfolge (Port der SVG-Vorschau der Web-App; Einheit: mm).
struct PreviewCanvas: View {
    let result: StickResult
    let appearance: AppearanceSettings
    let currentStep: Int

    var body: some View {
        Canvas { ctx, size in
            draw(&ctx, size)
        }
        .aspectRatio(CGFloat(result.formatW / max(result.formatH, 0.001)), contentMode: .fit)
    }

    private func draw(_ ctx: inout GraphicsContext, _ size: CGSize) {
        let r = result
        let karton = Kartonfarbe.mit(id: appearance.kartonfarbe)
        let faden = Color(hex: Fadenfarbe.mit(id: appearance.fadenfarbe).hex)
        let s = min(Double(size.width) / r.formatW, Double(size.height) / r.formatH)
        ctx.translateBy(x: (Double(size.width) - r.formatW * s) / 2, y: (Double(size.height) - r.formatH * s) / 2)
        ctx.scaleBy(x: s, y: s)

        ctx.fill(Path(CGRect(x: 0, y: 0, width: r.formatW, height: r.formatH)), with: .color(Color(hex: karton.hex)))

        // Falzlinie + Nutzfläche
        let fold = StrokeStyle(lineWidth: 0.3, dash: [2, 1.5])
        if r.settings.falzposition == .links {
            var p = Path(); p.move(to: CGPoint(x: 0.4, y: 0)); p.addLine(to: CGPoint(x: 0.4, y: r.formatH))
            ctx.stroke(p, with: .color(.black.opacity(0.35)), style: fold)
        } else if r.settings.falzposition == .oben {
            var p = Path(); p.move(to: CGPoint(x: 0, y: 0.4)); p.addLine(to: CGPoint(x: r.formatW, y: 0.4))
            ctx.stroke(p, with: .color(.black.opacity(0.35)), style: fold)
        }
        let usable = CGRect(x: r.margins.left, y: r.margins.top, width: r.usableW, height: r.usableH)
        ctx.stroke(Path(usable), with: .color(.black.opacity(0.15)), style: StrokeStyle(lineWidth: 0.25, dash: [1.5, 1.5]))

        let g = r.graph
        func pt(_ id: String) -> CGPoint { let p = g.point(id); return CGPoint(x: p.x, y: p.y) }

        if !r.hasCritical {
            let segs = r.segments
            let step = min(currentStep, segs.count)

            // Restmuster als blasse Vorschau
            if appearance.zeigeVorschau && step < segs.count {
                var p = Path()
                for i in step..<segs.count where !segs[i].isJump {
                    p.move(to: pt(segs[i].a)); p.addLine(to: pt(segs[i].b))
                }
                ctx.stroke(p, with: .color(.white.opacity(0.14)), style: StrokeStyle(lineWidth: 0.25))
            }

            // Bereits gestickt: Stiche (1×) und Rückseiten-Sprünge (gestrichelt)
            var stitches = Path()
            var jumps = Path()
            for i in 0..<step {
                let sg = segs[i]
                if i == step - 1 { continue } // aktives Segment separat
                if sg.isJump {
                    if appearance.zeigeSpruenge { jumps.move(to: pt(sg.a)); jumps.addLine(to: pt(sg.b)) }
                } else {
                    stitches.move(to: pt(sg.a)); stitches.addLine(to: pt(sg.b))
                }
            }
            ctx.stroke(jumps, with: .color(.white.opacity(0.3)), style: StrokeStyle(lineWidth: 0.18, dash: [0.6, 0.8]))
            ctx.stroke(stitches, with: .color(faden), style: StrokeStyle(lineWidth: 0.4, lineCap: .round))

            // aktives Segment mit Pfeilspitze
            if step > 0 {
                let sg = segs[step - 1]
                let a = pt(sg.a), b = pt(sg.b)
                let color = Color(hex: sg.isJump ? karton.aktivRS : karton.aktivVS)
                var p = Path(); p.move(to: a); p.addLine(to: b)
                ctx.stroke(p, with: .color(color), style: StrokeStyle(lineWidth: sg.isJump ? 0.45 : 0.55, lineCap: .round))
                ctx.fill(arrowHead(from: a, to: b), with: .color(color))
            }
        }

        // Lochpunkte, nach Abstand eingefärbt
        var ok = Path(), warn = Path(), crit = Path()
        let baseR = Stick.lochDurchmesser / 2
        for (id, p) in g.entries.map({ ($0.id, $0.point) }) {
            let sev = r.severity[id] ?? .ok
            let rad = sev == .ok ? baseR : baseR + 0.25
            let rect = CGRect(x: p.x - rad, y: p.y - rad, width: 2 * rad, height: 2 * rad)
            switch sev {
            case .ok: ok.addEllipse(in: rect)
            case .moderate: warn.addEllipse(in: rect)
            case .critical: crit.addEllipse(in: rect)
            }
        }
        ctx.fill(ok, with: .color(.black.opacity(0.4)))
        ctx.fill(warn, with: .color(Color(hex: warnFarbeHex)))
        ctx.fill(crit, with: .color(Color(hex: gefahrFarbeHex)))
    }

    /// Pfeilspitze wie der SVG-Marker der Web-App (1,8 mm, Spitze 0,36 mm über dem Endpunkt).
    private func arrowHead(from a: CGPoint, to b: CGPoint) -> Path {
        let dx = b.x - a.x, dy = b.y - a.y
        let len = max(hypot(dx, dy), 1e-9)
        let ux = dx / len, uy = dy / len
        let tip = CGPoint(x: b.x + ux * 0.36, y: b.y + uy * 0.36)
        let base = CGPoint(x: tip.x - ux * 1.8, y: tip.y - uy * 1.8)
        var p = Path()
        p.move(to: tip)
        p.addLine(to: CGPoint(x: base.x - uy * 0.9, y: base.y + ux * 0.9))
        p.addLine(to: CGPoint(x: base.x + uy * 0.9, y: base.y - ux * 0.9))
        p.closeSubpath()
        return p
    }
}
