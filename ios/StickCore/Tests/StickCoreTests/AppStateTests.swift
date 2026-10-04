import XCTest
@testable import StickCore

final class AppStateTests: XCTestCase {
    func testFavoritenNeuesteZuerstUndNamen() {
        var s = AppState()
        let a = s.favoritHinzufuegen(StickSettings())!
        let b = s.favoritHinzufuegen(StickSettings())!
        XCTAssertEqual(s.favoriten.map(\.id), [b.id, a.id])
        XCTAssertEqual(s.favoriten.map(\.name), ["Muster 2", "Muster 1"])
    }

    func testLimit24() {
        var s = AppState()
        for _ in 0..<AppState.maxFavoriten { XCTAssertNotNil(s.favoritHinzufuegen(StickSettings())) }
        XCTAssertNil(s.favoritHinzufuegen(StickSettings()))
        XCTAssertEqual(s.favoriten.count, 24)
    }

    func testNummerWirdNachLoeschenNichtWiederverwendet() {
        var s = AppState()
        s.favoritHinzufuegen(StickSettings())
        let b = s.favoritHinzufuegen(StickSettings())!
        s.favoritLoeschen(id: s.favoriten.last!.id) // „Muster 1“ weg
        XCTAssertEqual(s.favoriten.map(\.name), ["Muster 2"])
        XCTAssertEqual(s.naechsteMusterNummer, 3)
        XCTAssertEqual(b.name, "Muster 2")
    }

    func testUmbenennenUndDuplizieren() {
        var s = AppState()
        let f = s.favoritHinzufuegen(StickSettings())!
        s.favoritUmbenennen(id: f.id, name: "  Eisblume ")
        XCTAssertEqual(s.favoriten[0].name, "Eisblume")
        s.favoritUmbenennen(id: f.id, name: "   ") // leer wird ignoriert
        XCTAssertEqual(s.favoriten[0].name, "Eisblume")
        let k = s.favoritDuplizieren(id: f.id)!
        XCTAssertEqual(k.name, "Eisblume Kopie")
        XCTAssertEqual(s.favoriten.first?.id, k.id)
        XCTAssertEqual(k.settings, f.settings)
    }

    func testCodableRundlaufUndFehlendeSchluessel() throws {
        var s = AppState()
        var st = StickSettings(); st.n = 10
        s.arbeitsstand = st
        s.favoritHinzufuegen(st)
        s.einfuehrungGesehen = true
        let d = try XCTUnwrap(s.codiert())
        XCTAssertEqual(try JSONDecoder().decode(AppState.self, from: d), s)
        let leer = try JSONDecoder().decode(AppState.self, from: Data("{}".utf8))
        XCTAssertEqual(leer, AppState())
    }

    func testMigrationVonV1() throws {
        var st = StickSettings(); st.n = 12
        var ap = AppearanceSettings(); ap.kartonfarbe = "nacht"
        let enc = JSONEncoder()
        let s = AppState.laden(v2: nil, v1Settings: try enc.encode(st), v1Appearance: try enc.encode(ap))
        XCTAssertEqual(s.arbeitsstand?.n, 12)
        XCTAssertEqual(s.appearance.kartonfarbe, "nacht")
        XCTAssertEqual(s.version, 2)
        XCTAssertTrue(s.favoriten.isEmpty)
        // v2 hat Vorrang vor v1
        let v2 = try XCTUnwrap(AppState().codiert())
        XCTAssertNil(AppState.laden(v2: v2, v1Settings: try enc.encode(st), v1Appearance: nil).arbeitsstand)
    }
}
