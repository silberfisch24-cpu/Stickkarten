import SwiftUI
import StickCore

/// Platzhalter der Hauptbereiche. Inhalt entsteht in den Phasen C bis E nach docs/ui-konzept.

struct StartView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: DS.Mass.abstandL) {
                Text("Stickkarten").font(DS.Schrift.titel)
                Text("Neues Muster, fertige Muster und Favoriten folgen.")
                    .font(DS.Schrift.sekundaer).foregroundStyle(.secondary)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(DS.Mass.rand)
        }
        .background(DS.Farbe.inhaltsgrund)
        .navigationTitle("Start")
        .navigationBarTitleDisplayMode(.inline)
    }
}

/// Karte mit Live-Meldung. Der Editor mit Sheet und Gruppen folgt in Phase D.
struct GestaltenView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        VStack(spacing: DS.Mass.abstandL) {
            KartenView(result: model.result, appearance: model.state.appearance)
                .clipShape(RoundedRectangle(cornerRadius: DS.Mass.radiusKarte / 2, style: .continuous))
                .padding(.horizontal, DS.Mass.rand)
            meldung
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(DS.Farbe.arbeitsflaeche)
        .navigationTitle("Gestalten")
        .navigationBarTitleDisplayMode(.inline)
    }

    @ViewBuilder
    private var meldung: some View {
        if model.result.hasCritical {
            MeldungsZeile(art: .kritisch, text: "Löcher zu eng")
        } else if model.result.hasModerate {
            MeldungsZeile(art: .warnung, text: "Lochabstand knapp")
        }
    }
}

struct AusgabeView: View {
    var body: some View {
        ContentUnavailableView("Ausgabe", systemImage: "printer",
                               description: Text("Lochmuster und Anleitung als PDF folgen."))
            .background(DS.Farbe.inhaltsgrund)
            .navigationTitle("Ausgabe")
            .navigationBarTitleDisplayMode(.inline)
    }
}

struct MehrView: View {
    var body: some View {
        List {
            NavigationLink { DesignKatalogView() } label: {
                Label("Designsystem", systemImage: "paintpalette")
            }
        }
        .navigationTitle("Mehr")
        .navigationBarTitleDisplayMode(.inline)
    }
}
