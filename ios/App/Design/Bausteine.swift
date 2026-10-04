import SwiftUI

// MARK: Schaltflächen

/// Kapsel (44 pt). `haupt`: gefüllte Hauptaktion (56 pt), sonst Glas.
struct KapselButton: View {
    let titel: LocalizedStringKey
    let symbol: String
    var haupt = false
    let aktion: () -> Void

    var body: some View {
        Button(action: aktion) {
            Label(titel, systemImage: symbol)
                .font(DS.Schrift.text.weight(.semibold))
                .padding(.horizontal, 20)
                .frame(minHeight: haupt ? DS.Mass.hauptaktion : DS.Mass.kapsel)
        }
        .buttonStyle(KapselStil(haupt: haupt))
    }
}

private struct KapselStil: ButtonStyle {
    let haupt: Bool

    @ViewBuilder
    func makeBody(configuration: Configuration) -> some View {
        if haupt {
            configuration.label
                .foregroundStyle(.white)
                .background(DS.Farbe.akzent, in: Capsule())
                .opacity(configuration.isPressed ? 0.8 : 1)
        } else {
            configuration.label
                .foregroundStyle(DS.Farbe.akzent)
                .glas(Capsule())
                .opacity(configuration.isPressed ? 0.8 : 1)
        }
    }
}

/// Runder Glas-Button (mindestens 44 × 44 pt) mit Beschreibung für VoiceOver.
struct RundButton: View {
    let symbol: String
    let beschriftung: LocalizedStringKey
    let aktion: () -> Void

    var body: some View {
        Button(action: aktion) {
            Image(systemName: symbol)
                .font(.body.weight(.semibold))
                .foregroundStyle(DS.Farbe.akzent)
                .frame(width: DS.Mass.kapsel, height: DS.Mass.kapsel)
                .glas(Circle())
        }
        .buttonStyle(.plain)
        .accessibilityLabel(beschriftung)
    }
}

// MARK: Auswahl

/// Auswahlkachel: Rahmen 3 pt plus Tönung, kein Häkchen.
struct Kachel: View {
    let titel: LocalizedStringKey
    let symbol: String
    let gewaehlt: Bool
    let aktion: () -> Void
    @Environment(\.horizontalSizeClass) private var groesse

    var body: some View {
        let form = RoundedRectangle(cornerRadius: DS.Mass.radiusKarte, style: .continuous)
        Button(action: aktion) {
            VStack(spacing: DS.Mass.abstandM) {
                Image(systemName: symbol).font(.title)
                Text(titel).font(DS.Schrift.text.weight(.medium)).multilineTextAlignment(.center)
            }
            .foregroundStyle(DS.Farbe.akzent)
            .frame(maxWidth: .infinity, minHeight: groesse == .regular ? DS.Mass.kachelHoehePad : DS.Mass.kachelHoehe)
            .background(gewaehlt ? DS.Farbe.akzent.opacity(0.1) : DS.Farbe.flaeche, in: form)
            .overlay(form.stroke(DS.Farbe.akzent, lineWidth: gewaehlt ? 3 : 0))
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(gewaehlt ? .isSelected : [])
    }
}

/// Umschalter. Bei mehr als drei Segmenten zeigt nur das aktive seinen Text.
struct Umschalter<Wert: Hashable>: View {
    @Binding var auswahl: Wert
    let optionen: [(wert: Wert, titel: LocalizedStringKey, symbol: String)]

    var body: some View {
        HStack(spacing: 4) {
            ForEach(optionen.indices, id: \.self) { i in
                let o = optionen[i]
                let aktiv = o.wert == auswahl
                Button { auswahl = o.wert } label: {
                    Group {
                        if aktiv || optionen.count <= 3 {
                            Label(o.titel, systemImage: o.symbol)
                        } else {
                            Image(systemName: o.symbol)
                        }
                    }
                    .font(DS.Schrift.sekundaer.weight(.semibold))
                    .foregroundStyle(aktiv ? Color.white : DS.Farbe.akzent)
                    .padding(.horizontal, 14)
                    .frame(minWidth: DS.Mass.kapsel, minHeight: DS.Mass.kapsel)
                    .background(aktiv ? DS.Farbe.akzent : Color.clear, in: Capsule())
                }
                .buttonStyle(.plain)
                .accessibilityLabel(o.titel)
                .accessibilityAddTraits(aktiv ? .isSelected : [])
            }
        }
        .padding(4)
        .glas(Capsule())
    }
}

// MARK: Regler mit Zuständen

/// Zustand eines Reglers. Der Kern liefert „wirksamen Wert“ und Grund (z. B. `k1Eff`, `kMax1`).
enum ReglerZustand: Equatable {
    case normal
    /// Der Wert wurde wegen anderer Werte angepasst (Hinweistext nennt die Ursache).
    case angepasst(String)
    /// Nicht wählbar, weil … (Grund).
    case deaktiviert(String)
}

private struct ReglerHinweis: View {
    let zustand: ReglerZustand

    var body: some View {
        switch zustand {
        case .normal:
            EmptyView()
        case .angepasst(let text):
            Label(text, systemImage: "arrow.triangle.2.circlepath")
                .font(DS.Schrift.hinweis)
                .foregroundStyle(DS.Farbe.warnungText)
        case .deaktiviert(let text):
            Label(text, systemImage: "lock")
                .font(DS.Schrift.hinweis)
                .foregroundStyle(.secondary)
        }
    }
}

struct ParamRegler: View {
    let titel: LocalizedStringKey
    @Binding var wert: Double
    let bereich: ClosedRange<Double>
    let schritt: Double
    let anzeige: (Double) -> String
    var zustand: ReglerZustand = .normal

    private var gesperrt: Bool { if case .deaktiviert = zustand { return true } else { return false } }

    var body: some View {
        VStack(alignment: .leading, spacing: DS.Mass.abstandS) {
            HStack {
                Text(titel).font(DS.Schrift.text)
                Spacer()
                Text(anzeige(wert)).font(DS.Schrift.text.monospacedDigit().weight(.semibold))
            }
            Slider(value: $wert, in: bereich, step: schritt)
                .tint(DS.Farbe.akzent)
                .disabled(gesperrt)
                .accessibilityLabel(titel)
                .accessibilityValue(anzeige(wert))
            ReglerHinweis(zustand: zustand)
        }
        .opacity(gesperrt ? 0.5 : 1)
    }
}

/// Zähler mit ± für kleine Ganzzahlbereiche (z. B. Kreispunkte 3–16, Ebenen 1–6).
struct ZaehlerRegler: View {
    let titel: LocalizedStringKey
    @Binding var wert: Int
    let bereich: ClosedRange<Int>
    var zustand: ReglerZustand = .normal

    private var gesperrt: Bool { if case .deaktiviert = zustand { return true } else { return false } }

    var body: some View {
        VStack(alignment: .leading, spacing: DS.Mass.abstandS) {
            HStack {
                Text(titel).font(DS.Schrift.text)
                Spacer()
                Button { wert = max(bereich.lowerBound, wert - 1) } label: {
                    Image(systemName: "minus").frame(width: DS.Mass.kapsel, height: DS.Mass.kapsel)
                }
                .disabled(wert <= bereich.lowerBound)
                .accessibilityLabel("Verringern")
                Text("\(wert)").font(DS.Schrift.text.monospacedDigit().weight(.semibold)).frame(minWidth: 28)
                Button { wert = min(bereich.upperBound, wert + 1) } label: {
                    Image(systemName: "plus").frame(width: DS.Mass.kapsel, height: DS.Mass.kapsel)
                }
                .disabled(wert >= bereich.upperBound)
                .accessibilityLabel("Erhöhen")
            }
            .foregroundStyle(DS.Farbe.akzent)
            ReglerHinweis(zustand: zustand)
        }
        .disabled(gesperrt)
        .opacity(gesperrt ? 0.5 : 1)
    }
}

// MARK: Meldung

/// Einzeilige Meldung mit Symbol und Text (Farbe nie allein).
struct MeldungsZeile: View {
    enum Art { case ok, warnung, kritisch }

    let art: Art
    let text: LocalizedStringKey

    private var symbol: String {
        switch art {
        case .ok: return "checkmark.circle"
        case .warnung: return "exclamationmark.triangle"
        case .kritisch: return "xmark.octagon"
        }
    }

    private var grund: Color {
        switch art {
        case .ok: return DS.Farbe.okGrund
        case .warnung: return DS.Farbe.warnungGrund
        case .kritisch: return DS.Farbe.kritischGrund
        }
    }

    private var vordergrund: Color {
        switch art {
        case .ok: return DS.Farbe.okText
        case .warnung: return DS.Farbe.warnungText
        case .kritisch: return DS.Farbe.kritischText
        }
    }

    var body: some View {
        Label(text, systemImage: symbol)
            .font(DS.Schrift.sekundaer.weight(.semibold))
            .lineLimit(1)
            .foregroundStyle(vordergrund)
            .padding(.horizontal, 14)
            .frame(minHeight: DS.Mass.kapsel)
            .background(grund, in: Capsule())
    }
}
