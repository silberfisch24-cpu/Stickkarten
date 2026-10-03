import SwiftUI
import StickCore

/// Slider mit Beschriftung („Ebenen: 4“).
struct SliderRow: View {
    let title: String
    @Binding var value: Double
    let range: ClosedRange<Double>
    var step: Double = 1

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title).font(.footnote).foregroundStyle(.secondary)
            Slider(value: $value, in: range, step: step)
        }
        .padding(.vertical, 2)
    }
}

struct IntSliderRow: View {
    let title: String
    @Binding var value: Int
    let range: ClosedRange<Int>

    var body: some View {
        if range.upperBound > range.lowerBound {
            SliderRow(
                title: title,
                value: Binding(get: { Double(value) }, set: { value = Int($0.rounded()) }),
                range: Double(range.lowerBound)...Double(range.upperBound),
                step: 1)
        } else {
            Text(title).font(.footnote).foregroundStyle(.secondary)
        }
    }
}

/// Regler und Auswahl wie in der Sidebar der Web-App.
struct ControlsView: View {
    @EnvironmentObject private var model: AppModel

    var body: some View {
        let r = model.result
        let s = model.settings
        Form {
            Section("Grundform") {
                IntSliderRow(title: "Kreispunkte: \(s.n)", value: $model.settings.n, range: 3...16)
            }

            Section("Astschicht (Baum)") {
                Toggle("aktiv", isOn: $model.settings.astschicht)
                if s.astschicht {
                    Toggle("Seitenäste", isOn: $model.settings.astAktiv)
                    IntSliderRow(title: "Ebenen: \(s.ebenen)", value: $model.settings.ebenen, range: 1...6)
                    if s.astAktiv {
                        SliderRow(title: "Astwinkel: \(Int(s.astWinkel))°", value: $model.settings.astWinkel, range: 3...55)
                        SliderRow(title: "Astlänge: \(Int((s.astLaenge * 100).rounded())) %", value: $model.settings.astLaenge, range: 0.2...2, step: 0.05)
                        SliderRow(title: "Wachstum n. außen: \(Int((s.astWachstum * 100).rounded())) %", value: $model.settings.astWachstum, range: 0...1.5, step: 0.05)
                        IntSliderRow(title: "Fraktal-Tiefe: \(s.fraktalTiefe)", value: $model.settings.fraktalTiefe, range: 0...2)
                        if s.fraktalTiefe > 0 {
                            SliderRow(title: "Fraktal-Skalierung: \(Int((s.fraktalSkalierung * 100).rounded())) %", value: $model.settings.fraktalSkalierung, range: 0.3...0.8, step: 0.05)
                        }
                    }
                }
            }

            Section("Sternschicht — Schicht 1") {
                Toggle("aktiv", isOn: $model.settings.sternschicht)
                if s.sternschicht {
                    if s.astschicht {
                        IntSliderRow(
                            title: "Sternebene: \(r.sternEbeneEff1) (\(s.ebenen)=Ring)",
                            value: Binding(get: { r.sternEbeneEff1 }, set: { model.settings.sternEbene = $0 }),
                            range: 1...s.ebenen)
                    }
                    teilerPicker(title: "Sternstrahlen: \(r.sternPunkte1)", selection: r.effTeiler1, n: s.n, options: r.teilerOptionen) {
                        model.settings.sternTeiler = $0
                    }
                    schrittweite(title: "Schrittweite", value: r.k1Eff, kMax: r.kMax1, hint: "nur 1 Verbindungsart möglich (zu wenige Sternstrahlen)") {
                        model.settings.k1 = $0
                    }
                    ausblendung(
                        exakt: r.skip1ExaktMoeglich, le: r.skip1LeMoeglich, level: r.sternEbeneEff1, cap: r.skip1CapLvl,
                        value: Binding(get: { s.astAusblendung1 }, set: { model.settings.astAusblendung1 = $0 }))
                    Toggle("zweite, unabhängige Schicht", isOn: $model.settings.sternschicht2)
                }
            }

            if s.sternschicht && s.sternschicht2 {
                Section("Sternschicht — Schicht 2") {
                    if s.astschicht {
                        IntSliderRow(
                            title: "Sternebene 2: \(r.sternEbeneEff2)",
                            value: Binding(get: { r.sternEbeneEff2 }, set: { model.settings.sternEbene2 = $0 }),
                            range: 1...s.ebenen)
                    }
                    teilerPicker(title: "Sternstrahlen 2: \(r.sternPunkte2)", selection: r.effTeiler2, n: s.n, options: r.teilerOptionen) {
                        model.settings.sternTeiler2 = $0
                    }
                    schrittweite(title: "Schrittweite 2", value: r.k2Eff, kMax: r.kMax2, hint: "nur 1 Verbindungsart (Versatz bleibt trotzdem wirksam)") {
                        model.settings.k2 = $0
                    }
                    if r.effTeiler2 > 1 {
                        IntSliderRow(
                            title: "Rotationsversatz: \(s.sternVersatz2) (von \(r.effTeiler2))",
                            value: $model.settings.sternVersatz2, range: 0...(r.effTeiler2 - 1))
                    }
                    ausblendung(
                        exakt: r.skip2ExaktMoeglich, le: r.skip2LeMoeglich, level: r.sternEbeneEff2, cap: r.skip2CapLvl,
                        value: Binding(get: { s.astAusblendung2 }, set: { model.settings.astAusblendung2 = $0 }))
                }
            }

            Section {
                Button("Alle Regler zurücksetzen", role: .destructive) { model.resetSettings() }
            }
        }
    }

    @ViewBuilder
    private func teilerPicker(title: String, selection: Int, n: Int, options: [Int], set: @escaping (Int) -> Void) -> some View {
        Picker(title, selection: Binding(get: { selection }, set: set)) {
            ForEach(options, id: \.self) { t in
                Text("\(n / t) Strahlen" + (t == 1 ? " (alle)" : " (jeder \(t).)")).tag(t)
            }
        }
    }

    @ViewBuilder
    private func schrittweite(title: String, value: Int, kMax: Int, hint: String, set: @escaping (Int) -> Void) -> some View {
        if kMax > 1 {
            IntSliderRow(title: "\(title): \(value)", value: Binding(get: { value }, set: set), range: 1...kMax)
        } else {
            VStack(alignment: .leading, spacing: 2) {
                Text(title).font(.footnote).foregroundStyle(.secondary)
                Text(hint).font(.caption).foregroundStyle(.secondary)
            }
        }
    }

    @ViewBuilder
    private func ausblendung(exakt: Bool, le: Bool, level: Int, cap: Int, value: Binding<AstAusblendung>) -> some View {
        if exakt || le {
            // gültigen Wert erzwingen, falls die gespeicherte Option aktuell nicht möglich ist
            let valid = Binding<AstAusblendung>(
                get: {
                    switch value.wrappedValue {
                    case .exakt where !exakt: return .keine
                    case .kleinerGleich where !le: return .keine
                    default: return value.wrappedValue
                    }
                },
                set: { value.wrappedValue = $0 })
            Picker("Seitenäste bei diesem Sternlevel", selection: valid) {
                Text("Alle behalten").tag(AstAusblendung.keine)
                if exakt { Text("Nur auf Sternlevel weglassen").tag(AstAusblendung.exakt) }
                if le { Text("Sternlevel und darunter weglassen").tag(AstAusblendung.kleinerGleich) }
            }
            let hinweis = ausblendungHinweis(valid.wrappedValue, level: level, cap: cap)
            Text(hinweis).font(.caption).foregroundStyle(.secondary)
        }
    }

    private func ausblendungHinweis(_ v: AstAusblendung, level: Int, cap: Int) -> String {
        switch v {
        case .exakt: return "Betrifft Ebene \(level)."
        case .kleinerGleich: return "Betrifft Ebene 2–\(cap)."
        case .keine: return "Keine Ebene betroffen."
        }
    }
}
