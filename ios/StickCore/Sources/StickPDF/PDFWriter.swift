import Foundation
import CoreGraphics
import CoreText
import StickCore

/// Schmale Hülle um einen CoreGraphics-PDF-Kontext (dieselbe Vektor-Ausgabe wie
/// `UIGraphicsPDFRenderer`, aber ohne UIKit — dadurch auch unter `swift test` auf macOS prüfbar).
/// Koordinaten: Punkte (1/72 in), Ursprung oben links, y nach unten.
final class PDFWriter {
    let data = NSMutableData()
    let ctx: CGContext
    private(set) var pageW: Double = 0
    private(set) var pageH: Double = 0
    private var pageOpen = false

    init?(title: String) {
        guard let consumer = CGDataConsumer(data: data) else { return nil }
        let aux: [CFString: Any] = [kCGPDFContextTitle: title, kCGPDFContextCreator: "Stickkarten"]
        guard let c = CGContext(consumer: consumer, mediaBox: nil, aux as CFDictionary) else { return nil }
        ctx = c
    }

    func beginPage(width: Double, height: Double) {
        endPage()
        pageW = width
        pageH = height
        var box = CGRect(x: 0, y: 0, width: width, height: height)
        let boxData = Data(bytes: &box, count: MemoryLayout<CGRect>.size)
        let info: [CFString: Any] = [kCGPDFContextMediaBox: boxData]
        ctx.beginPDFPage(info as CFDictionary)
        pageOpen = true
        // y-Achse nach unten, Ursprung oben links
        ctx.translateBy(x: 0, y: height)
        ctx.scaleBy(x: 1, y: -1)
    }

    func endPage() {
        if pageOpen {
            ctx.endPDFPage()
            pageOpen = false
        }
    }

    func finish() -> Data {
        endPage()
        ctx.closePDF()
        return data as Data
    }

    // MARK: Text

    private func font(_ size: Double, bold: Bool, serif: Bool) -> CTFont {
        let name = serif ? (bold ? "Georgia-Bold" : "Georgia") : (bold ? "Helvetica-Bold" : "Helvetica")
        return CTFontCreateWithName(name as CFString, CGFloat(size), nil)
    }

    private func attributed(_ s: String, size: Double, bold: Bool, serif: Bool, color: CGColor) -> CFAttributedString {
        let attrs: [CFString: Any] = [kCTFontAttributeName: font(size, bold: bold, serif: serif), kCTForegroundColorAttributeName: color]
        return CFAttributedStringCreate(nil, s as CFString, attrs as CFDictionary)
    }

    func textWidth(_ s: String, size: Double, bold: Bool = false, serif: Bool = false) -> Double {
        let line = CTLineCreateWithAttributedString(attributed(s, size: size, bold: bold, serif: serif, color: gray(0)))
        return Double(CTLineGetTypographicBounds(line, nil, nil, nil))
    }

    /// Einzeiliger Text; (x, y) = Grundlinie.
    func text(_ s: String, x: Double, y: Double, size: Double, bold: Bool = false, serif: Bool = false,
              color: CGColor, anchor: TextAnchor = .start) {
        let line = CTLineCreateWithAttributedString(attributed(s, size: size, bold: bold, serif: serif, color: color))
        let width = Double(CTLineGetTypographicBounds(line, nil, nil, nil))
        var px = x
        if anchor == .middle { px -= width / 2 } else if anchor == .end { px -= width }
        ctx.saveGState()
        ctx.textMatrix = CGAffineTransform(scaleX: 1, y: -1)
        ctx.textPosition = CGPoint(x: px, y: y)
        CTLineDraw(line, ctx)
        ctx.restoreGState()
    }

    /// Umbrechender Absatz in der Breite `width`; liefert die Höhe. `draw: false` misst nur.
    @discardableResult
    func paragraph(_ s: String, x: Double, y: Double, width: Double, size: Double, bold: Bool = false,
                   serif: Bool = false, color: CGColor, draw: Bool = true) -> Double {
        let fs = CTFramesetterCreateWithAttributedString(attributed(s, size: size, bold: bold, serif: serif, color: color))
        let suggested = CTFramesetterSuggestFrameSizeWithConstraints(
            fs, CFRange(location: 0, length: 0), nil, CGSize(width: width, height: 10_000), nil)
        let height = Double(suggested.height.rounded(.up)) + 2
        if draw {
            ctx.saveGState()
            ctx.translateBy(x: x, y: y + height)
            ctx.scaleBy(x: 1, y: -1)
            ctx.textMatrix = .identity
            let path = CGPath(rect: CGRect(x: 0, y: 0, width: width, height: height), transform: nil)
            let frame = CTFramesetterCreateFrame(fs, CFRange(location: 0, length: 0), path, nil)
            CTFrameDraw(frame, ctx)
            ctx.restoreGState()
        }
        return height
    }
}

// MARK: Farben

func gray(_ g: Double, alpha: Double = 1) -> CGColor {
    CGColor(gray: CGFloat(g), alpha: CGFloat(alpha))
}

func hexColor(_ hex: String, alpha: Double = 1) -> CGColor {
    var h = hex
    if h.hasPrefix("#") { h.removeFirst() }
    let v = UInt32(h, radix: 16) ?? 0
    return CGColor(
        red: CGFloat((v >> 16) & 0xff) / 255, green: CGFloat((v >> 8) & 0xff) / 255,
        blue: CGFloat(v & 0xff) / 255, alpha: CGFloat(alpha))
}

let mm = Stick.ptPerMM
