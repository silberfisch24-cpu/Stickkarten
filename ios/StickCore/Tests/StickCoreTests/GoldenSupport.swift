import XCTest
import Foundation
@testable import StickCore

// Decodable-Spiegel der von ios/tools/gen-golden.mjs erzeugten JSON-Dateien.

struct GMargins: Decodable { var top, right, bottom, left: Double }

struct GDerived: Decodable {
    var formatW, formatH: Double
    var margins: GMargins
    var usableW, usableH, cx, cy, Rmax, Rmin: Double
    var formatOk: Bool
    var R: Double
    var effTeiler1, effTeiler2, kMax1, kMax2, sternEbeneEff1, sternEbeneEff2, k1Eff, k2Eff: Int
    var unterdrueckteEbenen: [Int]
}

struct GNodes: Decodable { var ids: [String]; var x: [Double]; var y: [Double] }
struct GEdges: Decodable { var a: [String]; var b: [String]; var len: [Double]; var id: [String] }
struct GCounts: Decodable { var ast, star1, star2: Int }
struct GSegments: Decodable { var a: [String]; var b: [String]; var jump: [Int] }
struct GStats: Decodable {
    var stitchCount, jumpCount, maxStep: Int
    var frontLength, jumpLength, fadenCm: Double
}
struct GFlat: Decodable {
    var w, h, offX, offY: Double
    var foldAxis: String?
    var foldPos: Double?
}
struct GPageFit: Decodable {
    var orientation: String
    var pageW, pageH, availW, availH, scale: Double
    var fits: Bool
}
struct GStep: Decodable { var vs: [String]; var rs: [String]?; var rsIsTransition: Bool }
struct GElement: Decodable { var k: String; var v: [Double]; var s: String?; var anchor: String? }
struct GArm: Decodable {
    var armEdgeCount: Int
    var steps: [GStep]
    var labels: [[String]]
    var fadenCm: Double
    var width, height: Double
    var elements: [GElement]
}
struct GStern: Decodable {
    var ids: [String]
    var labels: [String]
    var steps: [GStep]
    var fadenCm: Double
    var width, height: Double
    var elements: [GElement]
}
struct GAnleitung: Decodable { var arm: GArm?; var stern1: GStern?; var stern2: GStern? }

struct GRecord: Decodable {
    var name: String
    var settings: StickSettings
    var derived: GDerived
    var nodes: GNodes
    var edges: GEdges
    var counts: GCounts
    var segments: GSegments
    var stats: GStats
    var severity: String
    var hasCritical, hasModerate: Bool
    var warnungen: [String]
    var flat: GFlat
    var pageFit: GPageFit
    var anleitung: GAnleitung?
}

struct GLayout: Decodable {
    var w, h: Double
    var falz: String
    var flat: GFlat
    var pageFit: GPageFit
}

func loadGolden<T: Decodable>(_ name: String, as type: T.Type = T.self) throws -> T {
    guard let base = Bundle.module.resourceURL else { throw NSError(domain: "golden", code: 1) }
    let url = base.appendingPathComponent("Golden/\(name).json")
    let data = try Data(contentsOf: url)
    return try JSONDecoder().decode(T.self, from: data)
}

/// Sammelt Abweichungen und meldet höchstens `limit` davon einzeln (damit ein Fehler im Port
/// nicht das gesamte CI-Log mit tausenden Zeilen flutet).
final class Checker {
    private(set) var failures = 0
    private var shown = 0
    let limit = 25
    var context = ""

    func expect(_ ok: @autoclosure () -> Bool, _ msg: @autoclosure () -> String, file: StaticString = #filePath, line: UInt = #line) {
        if ok() { return }
        failures += 1
        if shown < limit {
            shown += 1
            XCTFail("[\(context)] \(msg())", file: file, line: line)
        }
    }

    func close(_ a: Double, _ b: Double, _ tol: Double, _ what: @autoclosure () -> String, file: StaticString = #filePath, line: UInt = #line) {
        expect(abs(a - b) <= tol || (a.isNaN && b.isNaN), "\(what()): Swift \(a) ≠ JS \(b)", file: file, line: line)
    }

    func finish(_ what: String, file: StaticString = #filePath, line: UInt = #line) {
        if failures > shown { XCTFail("\(what): insgesamt \(failures) Abweichungen (\(shown) gezeigt)", file: file, line: line) }
    }
}
