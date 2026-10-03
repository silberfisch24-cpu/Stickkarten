import SwiftUI
import StickCore

struct SettingsView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        let r = model.result
        NavigationStack {
            Form {
                Section("Karte") {
                    Picker("Kartenformat", selection: $model.settings.formatPreset) {
                        ForEach(FormatPreset.allCases) { Text($0.label).tag($0) }
                    }
                    if model.settings.formatPreset == .custom {
                        mmField("Breite (mm)", value: $model.settings.customW)
                        mmField("Höhe (mm)", value: $model.settings.customH)
                    }
                    Picker("Falzposition", selection: $model.settings.falzposition) {
                        ForEach(Falzposition.allCases) { Text($0.label).tag($0) }
                    }
                    SliderRow(title: "Zoom: \(Int((model.settings.zoom * 100).rounded())) %", value: $model.settings.zoom, range: 0...1, step: 0.02)
                    Text("Radius \(Int(r.R.rounded())) mm · Faden \(Int(Stick.fadenStraenge))-strängig · Karton 250 g/m² · Rand min. \(Int(Stick.randMin)) mm, Falz min. \(Int(Stick.falzMin)) mm · Mindestabstand \(String(format: "%.1f", Stick.mindestabstand)) mm.")
                        .font(.caption).foregroundStyle(.secondary)
                }

                Section("Darstellung") {
                    Picker("Kartonfarbe", selection: $model.appearance.kartonfarbe) {
                        ForEach(Kartonfarbe.alle) { Text($0.label).tag($0.id) }
                    }
                    Picker("Fadenfarbe", selection: $model.appearance.fadenfarbe) {
                        ForEach(Fadenfarbe.alle) { Text($0.label).tag($0.id) }
                    }
                    Toggle("Restmuster als Vorschau", isOn: $model.appearance.zeigeVorschau)
                    Toggle("Rückseiten-Sprünge anzeigen", isOn: $model.appearance.zeigeSpruenge)
                }
            }
            .navigationTitle("Einstellungen")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) { Button("Fertig") { dismiss() } }
            }
        }
    }

    private func mmField(_ title: String, value: Binding<Double>) -> some View {
        HStack {
            Text(title)
            Spacer()
            TextField("mm", value: value, format: .number)
                .keyboardType(.decimalPad)
                .multilineTextAlignment(.trailing)
                .frame(width: 90)
        }
    }
}
