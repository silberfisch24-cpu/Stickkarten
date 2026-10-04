import Foundation
import CoreGraphics
import StickCore

/// Berechneter Seitenaufbau des Lochmusters (Seite in Punkten, Löcher in Seitenkoordinaten,
/// Ursprung oben links) — wird gezeichnet und in Tests unabhängig vom PDF-Parsing geprüft.
public struct LochmusterPlan {
    public var pageWidthPt: Double
    public var pageHeightPt: Double
    public var orientation: PageOrientation
    /// Druckmaßstab (1 = echtes 1:1)
    public var scale: Double
    public var fits: Bool
    /// Zuschnitt in Seitenkoordinaten (Punkte)
    public var sheetRect: CGRect
    /// Vorderes (besticktes) Panel (Punkte)
    public var panelRect: CGRect
    public var holes: [CGPoint]
    public var holeRadiusPt: Double
    public var foldLine: (from: CGPoint, to: CGPoint)?
}

public enum Lochmuster {
    /// Seitenaufbau: Zuschnitt zentriert auf A4 (hoch oder quer wie `pageFitFor`), 1 mm = 72/25,4 pt.
    public static func plan(_ r: StickResult) -> LochmusterPlan {
        let flat = r.flat
        let fit = r.pageFit
        let s = fit.scale
        let x0 = (fit.pageW - flat.w * s) / 2
        let y0 = (fit.pageH - flat.h * s) / 2
        func pt(_ mmX: Double, _ mmY: Double) -> CGPoint {
            CGPoint(x: (x0 + mmX * s) * mm, y: (y0 + mmY * s) * mm)
        }
        let sheet = CGRect(x: x0 * mm, y: y0 * mm, width: flat.w * s * mm, height: flat.h * s * mm)
        let panelOrigin = pt(flat.offX, flat.offY)
        let panel = CGRect(x: panelOrigin.x, y: panelOrigin.y, width: r.formatW * s * mm, height: r.formatH * s * mm)
        let holes = r.graph.entries.map { pt(flat.offX + $0.point.x, flat.offY + $0.point.y) }
        var fold: (from: CGPoint, to: CGPoint)? = nil
        if let axis = flat.foldAxis, let pos = flat.foldPos {
            fold = axis == .v ? (from: pt(pos, 0), to: pt(pos, flat.h)) : (from: pt(0, pos), to: pt(flat.w, pos))
        }
        return LochmusterPlan(
            pageWidthPt: fit.pageW * mm, pageHeightPt: fit.pageH * mm, orientation: fit.orientation,
            scale: s, fits: fit.fits, sheetRect: sheet, panelRect: panel, holes: holes,
            holeRadiusPt: Stick.lochDurchmesser / 2 * s * mm, foldLine: fold)
    }

    /// Einseitiges Vektor-PDF mit dem Lochmuster im Maßstab 1:1.
    public static func pdf(_ r: StickResult) -> Data {
        guard let w = PDFWriter(title: "Stickkarten-Lochmuster") else { return Data() }
        drawPage(w, r)
        return w.finish()
    }

    /// Eine Lochmuster-Seite in einen laufenden PDF-Kontext zeichnen.
    static func drawPage(_ w: PDFWriter, _ r: StickResult) {
        let plan = plan(r)
        w.beginPage(width: plan.pageWidthPt, height: plan.pageHeightPt)
        let ctx = w.ctx
        let ink = hexColor("#26241f")

        // Kopfzeile + Maßstabskontrolle liegen im 10-mm-Seitenrand außerhalb des Zuschnitts.
        let format = formatName(r)
        w.text("Stickkarten — Lochmuster \(plan.fits ? "1:1" : "(auf \(Int((plan.scale * 100).rounded())) % verkleinert)")",
               x: 10 * mm, y: 6 * mm, size: 8, bold: true, color: ink)
        w.text("\(format) · Falz \(r.settings.falzposition.rawValue) · \(r.graph.nodeIDs.count) Löcher Ø \(String(format: "%.2f", Stick.lochDurchmesser)) mm",
               x: 10 * mm, y: 9 * mm, size: 6.5, color: hexColor("#6b6558"))
        let hint = plan.fits
            ? "Drucken mit „Tatsächliche Größe“ / 100 % — nicht „An Seite anpassen“."
            : "Zuschnitt größer als A4: Darstellung verkleinert, NICHT zum direkten Anstechen geeignet."
        w.text(hint, x: plan.pageWidthPt - 10 * mm, y: 6 * mm, size: 6.5, color: plan.fits ? ink : hexColor("#b23b3b"), anchor: .end)

        // Zuschnitt, Falz, Panel, Nutzfläche
        ctx.setStrokeColor(ink)
        ctx.setLineWidth(0.3 * mm * plan.scale)
        ctx.stroke(plan.sheetRect)

        if let fold = plan.foldLine {
            ctx.saveGState()
            ctx.setLineWidth(0.25 * mm * plan.scale)
            ctx.setLineDash(phase: 0, lengths: [3 * mm * plan.scale, 2 * mm * plan.scale])
            ctx.move(to: fold.from)
            ctx.addLine(to: fold.to)
            ctx.strokePath()
            ctx.restoreGState()
        }

        ctx.saveGState()
        ctx.setLineWidth(0.25 * mm * plan.scale)
        ctx.stroke(plan.panelRect)
        ctx.restoreGState()

        ctx.saveGState()
        ctx.setStrokeColor(gray(0.26 + 0.0, alpha: 0.35))
        ctx.setLineWidth(0.2 * mm * plan.scale)
        ctx.setLineDash(phase: 0, lengths: [1.5 * mm * plan.scale, 1.5 * mm * plan.scale])
        let usable = CGRect(
            x: plan.panelRect.minX + r.margins.left * plan.scale * mm,
            y: plan.panelRect.minY + r.margins.top * plan.scale * mm,
            width: r.usableW * plan.scale * mm, height: r.usableH * plan.scale * mm)
        ctx.stroke(usable)
        ctx.restoreGState()

        // Löcher in tatsächlicher Größe
        ctx.setFillColor(gray(0.4))
        let rad = plan.holeRadiusPt
        for h in plan.holes {
            ctx.fillEllipse(in: CGRect(x: h.x - rad, y: h.y - rad, width: 2 * rad, height: 2 * rad))
        }

        // Maßstabsbalken (50 mm) zur Kontrolle nach dem Drucken
        let barY = plan.pageHeightPt - 6 * mm
        let barX = 10 * mm
        let barLen = 50 * mm * plan.scale
        ctx.setStrokeColor(ink)
        ctx.setLineWidth(0.3 * mm)
        ctx.move(to: CGPoint(x: barX, y: barY)); ctx.addLine(to: CGPoint(x: barX + barLen, y: barY))
        for i in 0...5 {
            let x = barX + Double(i) * 10 * mm * plan.scale
            ctx.move(to: CGPoint(x: x, y: barY - 1.5 * mm)); ctx.addLine(to: CGPoint(x: x, y: barY + 1.5 * mm))
        }
        ctx.strokePath()
        w.text("Kontrolle: Balken muss gedruckt \(plan.fits ? "50 mm" : "\(Int((50 * plan.scale).rounded())) mm") lang sein",
               x: barX + barLen + 3 * mm, y: barY + 1 * mm, size: 6.5, color: ink)
    }

    static func formatName(_ r: StickResult) -> String {
        let s = r.settings
        if s.formatPreset == .custom { return "Format \(trim(r.formatW)) × \(trim(r.formatH)) mm" }
        return "Format \(trim(r.formatW)) × \(trim(r.formatH)) mm (A5 gefaltet)"
    }
}

func trim(_ v: Double) -> String {
    v == v.rounded() ? String(Int(v)) : String(format: "%.1f", v)
}
