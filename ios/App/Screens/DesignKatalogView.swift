import SwiftUI

/// Katalog aller Bausteine mit ihren Zuständen. Dient der Sichtprüfung (Screenshot-Matrix in der CI).
struct DesignKatalogView: View {
    @State private var wert = 55.0
    @State private var wert2 = 40.0
    @State private var zahl = 8
    @State private var kachel = 1
    @State private var umschalter = 0
    @State private var sheet = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: DS.Mass.abstandL + 8) {
                Text("Designsystem").font(DS.Schrift.titel)

                Group {
                    Text("Schaltflächen").font(DS.Schrift.abschnitt)
                    HStack {
                        KapselButton(titel: "Anpassen", symbol: "slider.horizontal.3") {}
                        RundButton(symbol: "star", beschriftung: "Favorit") {}
                    }
                    KapselButton(titel: "Als PDF", symbol: "doc", haupt: true) {}
                }

                Group {
                    Text("Umschalter und Kacheln").font(DS.Schrift.abschnitt)
                    Umschalter(auswahl: $umschalter, optionen: [
                        (0, "Muster", "sparkles"), (1, "Stichfolge", "point.topleft.down.curvedto.point.bottomright.up"),
                    ])
                    HStack {
                        ForEach(0..<3, id: \.self) { i in
                            Kachel(titel: LocalizedStringKey(["Leicht", "Mittel", "Aufwendig"][i]),
                                   symbol: "snowflake", gewaehlt: kachel == i) { kachel = i }
                        }
                    }
                }

                Group {
                    Text("Regler").font(DS.Schrift.abschnitt)
                    ParamRegler(titel: "Astwinkel", wert: $wert, bereich: 3...55, schritt: 1, anzeige: { "\(Int($0))°" })
                    ParamRegler(titel: "Schrittweite", wert: $wert2, bereich: 0...100, schritt: 1,
                                anzeige: { "\(Int($0)) %" }, zustand: .angepasst("Auf 2 begrenzt, weil nur 5 Strahlen"))
                    ParamRegler(titel: "Sternebene", wert: $wert2, bereich: 0...100, schritt: 1,
                                anzeige: { "\(Int($0)) %" }, zustand: .deaktiviert("Sternschicht ist aus"))
                    ZaehlerRegler(titel: "Kreispunkte", wert: $zahl, bereich: 3...16)
                }

                Group {
                    Text("Meldungen").font(DS.Schrift.abschnitt)
                    MeldungsZeile(art: .ok, text: "Alles in Ordnung")
                    MeldungsZeile(art: .warnung, text: "Lochabstand knapp")
                    MeldungsZeile(art: .kritisch, text: "Löcher zu eng")
                }

                KapselButton(titel: "Sheet in drei Stufen", symbol: "rectangle.bottomhalf.inset.filled") { sheet = true }
            }
            .padding(DS.Mass.rand)
        }
        .background(DS.Farbe.inhaltsgrund)
        .navigationTitle("Designsystem")
        .navigationBarTitleDisplayMode(.inline)
        .stufenSheet(isPresented: $sheet) {
            VStack(spacing: DS.Mass.abstandL) {
                Text("Grundform").font(DS.Schrift.abschnitt).padding(.top, DS.Mass.abstandL)
                ZaehlerRegler(titel: "Kreispunkte", wert: $zahl, bereich: 3...16).padding(.horizontal, DS.Mass.rand)
                Spacer()
            }
        }
    }
}
