import Foundation
import Observation
import StickCore

/// App-Zustand: Arbeitsstand („Weitermachen“), Favoriten, Darstellung, Erststart. Persistent als
/// `AppState` (Schema v2) in UserDefaults, mit Übernahme der Einzelstände der ersten Portierung (v1).
@Observable
final class AppModel {
    private static let schluessel = "stick.state.v2"
    private static let v1Einstellungen = "stick.settings.v1"
    private static let v1Darstellung = "stick.appearance.v1"

    private(set) var state: AppState
    /// Aktuell bearbeitetes Muster. Änderungen nur über `aendern`, damit Ergebnis und Speicher folgen.
    private(set) var settings: StickSettings
    private(set) var result: StickResult

    init(defaults: UserDefaults = .standard) {
        let s = AppState.laden(
            v2: defaults.data(forKey: Self.schluessel),
            v1Settings: defaults.data(forKey: Self.v1Einstellungen),
            v1Appearance: defaults.data(forKey: Self.v1Darstellung))
        state = s
        let start = s.arbeitsstand ?? StickSettings()
        settings = start
        result = StickModel.compute(start)
        self.defaults = defaults
    }

    private let defaults: UserDefaults

    /// Es gibt einen Arbeitsstand, den „Weitermachen“ öffnen kann.
    var kannWeitermachen: Bool { state.arbeitsstand != nil && state.einfuehrungGesehen }

    func aendern(_ aenderung: (inout StickSettings) -> Void) {
        var neu = settings
        aenderung(&neu)
        setzen(neu)
    }

    func setzen(_ neu: StickSettings) {
        guard neu != settings else { return }
        settings = neu
        result = StickModel.compute(neu)
        state.arbeitsstand = neu
        sichern()
    }

    func zuruecksetzen() { setzen(StickSettings()) }

    func favoritSichern() {
        state.favoritHinzufuegen(settings)
        sichern()
    }

    func favoritLoeschen(_ id: UUID) {
        state.favoritLoeschen(id: id)
        sichern()
    }

    func favoritUmbenennen(_ id: UUID, _ name: String) {
        state.favoritUmbenennen(id: id, name: name)
        sichern()
    }

    func favoritDuplizieren(_ id: UUID) {
        state.favoritDuplizieren(id: id)
        sichern()
    }

    func einfuehrungAbschliessen() {
        state.einfuehrungGesehen = true
        sichern()
    }

    private func sichern() {
        if let d = state.codiert() { defaults.set(d, forKey: Self.schluessel) }
    }
}
