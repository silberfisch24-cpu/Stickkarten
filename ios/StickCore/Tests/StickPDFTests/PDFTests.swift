import XCTest
import CoreGraphics
import Foundation
import StickCore
@testable import StickPDF

final class PDFTests: XCTestCase {
    let ptPerMM = 72.0 / 25.4

    // MARK: Hilfen

    func settings(_ edit: (inout StickSettings) -> Void = { _ in }) -> StickSettings {
        var s = StickSettings()
        s.zoom = 0.5
        edit(&s)
        return s
    }

    func document(_ data: Data) throws -> CGPDFDocument {
        let provider = try XCTUnwrap(CGDataProvider(data: data as CFData))
        return try XCTUnwrap(CGPDFDocument(provider))
    }

    func outputDir() -> URL {
        if let p = ProcessInfo.processInfo.environment["STICK_PDF_OUT"], !p.isEmpty {
            let url = URL(fileURLWithPath: p, isDirectory: true)
            try? FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
            return url
        }
        return FileManager.default.temporaryDirectory
    }

    /// Rendert Seite 1 mit `pxPerMM` Pixeln pro Millimeter in ein Graustufen-Bitmap (Zeile 0 = oben).
    func rasterize(_ doc: CGPDFDocument, page index: Int = 1, pxPerMM: Double) throws -> (pixels: [UInt8], w: Int, h: Int) {
        let page = try XCTUnwrap(doc.page(at: index))
        let box = page.getBoxRect(.mediaBox)
        let sc = pxPerMM / ptPerMM
        let w = Int((box.width * sc).rounded()), h = Int((box.height * sc).rounded())
        var buf = [UInt8](repeating: 255, count: w * h)
        let ok: Bool = buf.withUnsafeMutableBytes { raw in
            guard let ctx = CGContext(data: raw.baseAddress, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w,
                                      space: CGColorSpaceCreateDeviceGray(), bitmapInfo: CGImageAlphaInfo.none.rawValue) else { return false }
            ctx.setFillColor(CGColor(gray: 1, alpha: 1))
            ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
            ctx.scaleBy(x: sc, y: sc)
            ctx.drawPDFPage(page)
            return true
        }
        XCTAssertTrue(ok)
        return (buf, w, h)
    }

    // MARK: Seitenmaße

    func testPageSizesAreExactA4InBothOrientations() throws {
        // Hochformat-Fall: sehr hoher Zuschnitt
        var tall = settings { $0.formatPreset = .custom; $0.customW = 80; $0.customH = 200; $0.falzposition = .keine }
        tall.n = 6
        let rTall = StickModel.compute(tall)
        XCTAssertEqual(rTall.pageFit.orientation, .hoch)
        var doc = try document(Lochmuster.pdf(rTall))
        XCTAssertEqual(doc.numberOfPages, 1)
        var box = try XCTUnwrap(doc.page(at: 1)).getBoxRect(.mediaBox)
        XCTAssertEqual(Double(box.width), 210 * ptPerMM, accuracy: 0.01)
        XCTAssertEqual(Double(box.height), 297 * ptPerMM, accuracy: 0.01)

        // Querformat-Fall: Standardkarte A6 hoch, Falz links => 210 × 148 mm
        let rWide = StickModel.compute(settings())
        XCTAssertEqual(rWide.pageFit.orientation, .quer)
        doc = try document(Lochmuster.pdf(rWide))
        box = try XCTUnwrap(doc.page(at: 1)).getBoxRect(.mediaBox)
        XCTAssertEqual(Double(box.width), 297 * ptPerMM, accuracy: 0.01)
        XCTAssertEqual(Double(box.height), 210 * ptPerMM, accuracy: 0.01)
    }

    // MARK: Lochabstände mm-genau (aus dem Seitenplan)

    func testPlanHoleSpacingMatchesModelToMicrometers() {
        for edit: (inout StickSettings) -> Void in [
            { _ in },
            { $0.n = 12; $0.ebenen = 5; $0.fraktalTiefe = 1 },
            { $0.falzposition = .oben; $0.formatPreset = .a6Quer },
            { $0.falzposition = .keine; $0.sternschicht2 = true; $0.n = 10; $0.sternTeiler2 = 2 },
        ] {
            let r = StickModel.compute(settings(edit))
            let plan = Lochmuster.plan(r)
            XCTAssertEqual(plan.holes.count, r.graph.nodeIDs.count)
            XCTAssertEqual(plan.scale, 1, accuracy: 1e-12, "diese Konfigurationen müssen 1:1 passen")
            let pts = r.graph.entries.map { $0.point }
            var maxErr = 0.0
            for i in 0..<pts.count {
                for j in (i + 1)..<pts.count {
                    let modelMM = hypot(pts[i].x - pts[j].x, pts[i].y - pts[j].y)
                    let pdfMM = Double(hypot(plan.holes[i].x - plan.holes[j].x, plan.holes[i].y - plan.holes[j].y)) / ptPerMM
                    maxErr = max(maxErr, abs(modelMM - pdfMM))
                }
            }
            XCTAssertLessThan(maxErr, 1e-6, "Lochabstand weicht um \(maxErr) mm ab")
            XCTAssertEqual(Double(plan.holeRadiusPt) / ptPerMM * 2, Stick.lochDurchmesser, accuracy: 1e-9)
        }
    }

    // MARK: Lochpositionen aus dem gerenderten PDF

    func testRenderedHolesSitAtExpectedPositions() throws {
        let r = StickModel.compute(settings())
        XCTAssertFalse(r.hasCritical)
        let plan = Lochmuster.plan(r)
        let doc = try document(Lochmuster.pdf(r))
        let ppm = 10.0
        let img = try rasterize(doc, pxPerMM: ppm)
        let sc = ppm / ptPerMM

        let lines: [CGRect] = [plan.sheetRect, plan.panelRect]
        func clear(_ p: CGPoint) -> Bool {
            let m = 1.6 * ptPerMM
            for rc in lines {
                if abs(Double(p.x - rc.minX)) < m || abs(Double(p.x - rc.maxX)) < m { if p.y > rc.minY - m && p.y < rc.maxY + m { return false } }
                if abs(Double(p.y - rc.minY)) < m || abs(Double(p.y - rc.maxY)) < m { if p.x > rc.minX - m && p.x < rc.maxX + m { return false } }
            }
            if let f = plan.foldLine, abs(Double(p.x - f.from.x)) < m || abs(Double(p.y - f.from.y)) < m && f.from.x != f.to.x { return false }
            // gestrichelte Nutzfläche (Rand 14/18 mm vom Panel)
            let u = r.margins
            let usable = CGRect(x: plan.panelRect.minX + u.left * ptPerMM, y: plan.panelRect.minY + u.top * ptPerMM,
                                width: r.usableW * ptPerMM, height: r.usableH * ptPerMM)
            if abs(Double(p.x - usable.minX)) < m || abs(Double(p.x - usable.maxX)) < m || abs(Double(p.y - usable.minY)) < m || abs(Double(p.y - usable.maxY)) < m { return false }
            return true
        }

        var checked = 0
        var maxOff = 0.0
        let win = Int((0.9 * ppm).rounded())
        for h in plan.holes where clear(h) {
            let cx = Double(h.x) * sc, cy = Double(h.y) * sc
            var sum = 0.0, sx = 0.0, sy = 0.0
            for dy in -win...win {
                for dx in -win...win {
                    let px = Int(cx.rounded()) + dx, py = Int(cy.rounded()) + dy
                    guard px >= 0, py >= 0, px < img.w, py < img.h else { continue }
                    let v = 255.0 - Double(img.pixels[py * img.w + px])
                    sum += v; sx += v * (Double(px) + 0.5); sy += v * (Double(py) + 0.5)
                }
            }
            XCTAssertGreaterThan(sum, 50 * 255 * 0.3, "kein Loch an erwarteter Stelle")
            guard sum > 0 else { continue }
            let offMM = hypot(sx / sum - cx, sy / sum - cy) / ppm
            maxOff = max(maxOff, offMM)
            checked += 1
        }
        XCTAssertGreaterThanOrEqual(checked, 15, "zu wenige Löcher geprüft")
        XCTAssertLessThan(maxOff, 0.1, "gerendertes Loch weicht um \(maxOff) mm ab")
    }

    // MARK: Nicht-1:1-Fall

    func testOversizedSheetIsScaledAndFlagged() throws {
        let r = StickModel.compute(settings { $0.formatPreset = .a6Quer }) // 296 × 105 mm > 277 mm nutzbar
        let plan = Lochmuster.plan(r)
        XCTAssertFalse(plan.fits)
        XCTAssertLessThan(plan.scale, 1)
        XCTAssertEqual(plan.scale, 277.0 / 296.0, accuracy: 1e-9)
        _ = try document(Lochmuster.pdf(r))
    }

    // MARK: Anleitung + Artefakte

    func testAnleitungPDFHasPagesAndEndsWithLochmuster() throws {
        let r = StickModel.compute(settings { $0.n = 10; $0.ebenen = 5; $0.sternschicht2 = true; $0.sternTeiler2 = 2; $0.k2 = 1; $0.zoom = 0.7 })
        let data = Anleitung.pdf(r)
        let doc = try document(data)
        XCTAssertGreaterThanOrEqual(doc.numberOfPages, 3)
        let last = try XCTUnwrap(doc.page(at: doc.numberOfPages)).getBoxRect(.mediaBox)
        let fit = r.pageFit
        XCTAssertEqual(Double(last.width), fit.pageW * ptPerMM, accuracy: 0.01)
        XCTAssertEqual(Double(last.height), fit.pageH * ptPerMM, accuracy: 0.01)
        let first = try XCTUnwrap(doc.page(at: 1)).getBoxRect(.mediaBox)
        XCTAssertEqual(Double(first.width), 210 * ptPerMM, accuracy: 0.01)
    }

    func testWriteSamplePDFsForArtifact() throws {
        let dir = outputDir()
        let samples: [(String, StickSettings)] = [
            ("standard", settings { $0.zoom = 1 }),
            ("zwei-sternschichten", settings { $0.n = 12; $0.ebenen = 5; $0.sternschicht2 = true; $0.sternTeiler2 = 2; $0.sternVersatz2 = 1; $0.k1 = 2 }),
            ("fraktal", settings { $0.n = 8; $0.ebenen = 4; $0.fraktalTiefe = 2; $0.astWinkel = 35; $0.zoom = 1 }),
            ("a6-quer-falz-oben", settings { $0.formatPreset = .a6Quer; $0.falzposition = .oben; $0.n = 10; $0.zoom = 0.8 }),
            ("einzelkarte-ohne-aeste", settings { $0.falzposition = .keine; $0.astAktiv = false; $0.n = 14; $0.ebenen = 3 }),
        ]
        for (name, s) in samples {
            let r = StickModel.compute(s)
            let loch = Lochmuster.pdf(r)
            let anl = Anleitung.pdf(r)
            XCTAssertGreaterThan(loch.count, 500, name)
            XCTAssertGreaterThan(anl.count, 2000, name)
            try loch.write(to: dir.appendingPathComponent("lochmuster-\(name).pdf"))
            try anl.write(to: dir.appendingPathComponent("anleitung-\(name).pdf"))
        }
    }
}
