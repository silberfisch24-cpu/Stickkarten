import SwiftUI

/// Hauptbereiche (iPhone: Tab-Leiste, iPad: Seitenleiste).
enum Haupt: String, CaseIterable, Identifiable {
    case start, gestalten, ausgabe, mehr
    var id: String { rawValue }

    var titel: LocalizedStringKey {
        switch self {
        case .start: return "Start"
        case .gestalten: return "Gestalten"
        case .ausgabe: return "Ausgabe"
        case .mehr: return "Mehr"
        }
    }

    var symbol: String {
        switch self {
        case .start: return "house"
        case .gestalten: return "slider.horizontal.3"
        case .ausgabe: return "printer"
        case .mehr: return "ellipsis.circle"
        }
    }
}

/// Wurzel: Layout nach Größenklasse (nicht nach Gerätetyp).
struct RootView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.horizontalSizeClass) private var groesse
    @State private var auswahl: Haupt? = Startargumente.bereich

    private var aktuell: Haupt { auswahl ?? .start }

    var body: some View {
        if groesse == .regular {
            NavigationSplitView {
                List(Haupt.allCases, selection: $auswahl) { h in
                    Label(h.titel, systemImage: h.symbol).tag(h)
                }
                .navigationTitle("Stickkarten")
                .safeAreaInset(edge: .bottom) { weitermachen.padding(.bottom, DS.Mass.abstandL) }
            } detail: {
                NavigationStack { bereich(aktuell) }
            }
        } else {
            TabView(selection: Binding(get: { aktuell }, set: { auswahl = $0 })) {
                ForEach(Haupt.allCases) { h in
                    NavigationStack { bereich(h) }
                        .tabItem { Label(h.titel, systemImage: h.symbol) }
                        .tag(h)
                }
            }
            .tint(DS.Farbe.akzent)
            .overlay(alignment: .bottom) {
                weitermachen.padding(.bottom, DS.Mass.tabLeiste + DS.Mass.abstandM)
            }
        }
    }

    /// Kapsel „Weitermachen“ (öffnet den letzten Stand im Editor).
    @ViewBuilder
    private var weitermachen: some View {
        if model.kannWeitermachen && aktuell != .gestalten {
            KapselButton(titel: "Weitermachen", symbol: "arrow.uturn.forward") { auswahl = .gestalten }
        }
    }

    @ViewBuilder
    private func bereich(_ h: Haupt) -> some View {
        switch h {
        case .start: StartView()
        case .gestalten: GestaltenView()
        case .ausgabe: AusgabeView()
        case .mehr: MehrView()
        }
    }
}

/// Startargumente für die Screenshot-Prüfung in der CI: `-screen start|gestalten|ausgabe|mehr|katalog`.
enum Startargumente {
    private static var wert: String? {
        let a = ProcessInfo.processInfo.arguments
        guard let i = a.firstIndex(of: "-screen"), a.indices.contains(i + 1) else { return nil }
        return a[i + 1]
    }

    static var bereich: Haupt? { wert.flatMap(Haupt.init(rawValue:)) }
    static var zeigtKatalog: Bool { wert == "katalog" }
}
