import XCTest
@testable import StickCore

final class UnitTests: XCTestCase {
    func testDivisors() {
        XCTAssertEqual(divisorsOf(12), [1, 2, 3, 4, 6])
        XCTAssertEqual(divisorsOf(7), [1])
        XCTAssertEqual(divisorsOf(16), [1, 2, 4, 8])
    }

    func testBranchLevels() {
        XCTAssertEqual(astBranchLevels(2), [])
        XCTAssertEqual(astBranchLevels(5), [2, 3, 4])
    }

    func testAstNodeLabels() {
        XCTAssertEqual(astNodeLabel("C"), "Z")
        XCTAssertEqual(astNodeLabel("R11"), "K")
        XCTAssertEqual(astNodeLabel("A3L2"), "E2")
        XCTAssertEqual(astNodeLabel("A3L2b-1"), "E2L")
        XCTAssertEqual(astNodeLabel("A3L2b1"), "E2R")
        XCTAssertEqual(astNodeLabel("A3L2b-1f1n"), "E2L.1a")
        XCTAssertEqual(astNodeLabel("A3L2b1f1pf2n"), "E2R.1b.2a")
        XCTAssertEqual(astNodeLabel("R3f1p"), "K.1b")
        XCTAssertEqual(astNodeLabel("???"), "???")
    }

    func testDefaultsMatchWebApp() {
        let r = StickModel.compute(StickSettings())
        XCTAssertEqual(r.graph.nodeIDs.count, 8 + 1 + 8 * 3 + 8 * 2 * 2) // Ring + Zentrum + Stamm + Seitenäste (L=2,3)
        XCTAssertEqual(r.formatW, 105)
        XCTAssertEqual(r.formatH, 148)
        XCTAssertEqual(r.margins.left, 18)
    }

    func testSettingsCodableRoundTripAndMissingKeys() throws {
        var s = StickSettings()
        s.n = 11
        s.astAusblendung2 = .kleinerGleich
        s.formatPreset = .custom
        let data = try JSONEncoder().encode(s)
        XCTAssertEqual(try JSONDecoder().decode(StickSettings.self, from: data), s)
        let partial = try JSONDecoder().decode(StickSettings.self, from: Data("{\"n\":5}".utf8))
        XCTAssertEqual(partial.n, 5)
        XCTAssertEqual(partial.ebenen, 4)
    }
}
