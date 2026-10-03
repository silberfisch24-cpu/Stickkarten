import SwiftUI
import StickCore

struct PreviewPane: View {
    @EnvironmentObject private var model: AppModel

    var body: some View {
        let r = model.result
        ScrollView {
            VStack(spacing: 12) {
                PreviewCanvas(result: r, appearance: model.appearance, currentStep: model.currentStep)
                    .frame(maxHeight: 560)
                    .padding(8)
                    .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 10))

                playback(r)
                warnings(r)
                stats(r)
                legend
            }
            .padding()
        }
    }

    private func playback(_ r: StickResult) -> some View {
        HStack(spacing: 12) {
            Button { model.togglePlay() } label: {
                Image(systemName: model.playing ? "pause.fill" : "play.fill").frame(width: 28, height: 28)
            }
            .buttonStyle(.bordered)
            .disabled(r.hasCritical)
            Button { model.rewind() } label: {
                Image(systemName: "backward.end.fill").frame(width: 28, height: 28)
            }
            .buttonStyle(.bordered)
            .disabled(r.hasCritical)
            Slider(
                value: Binding(get: { Double(model.currentStep) }, set: { model.seek(Int($0.rounded())) }),
                in: 0...Double(max(r.maxStep, 1)), step: 1)
                .disabled(r.hasCritical || r.maxStep == 0)
            Text("\(model.currentStep) / \(r.maxStep)")
                .font(.footnote.monospacedDigit()).foregroundStyle(.secondary)
                .frame(minWidth: 62, alignment: .trailing)
        }
    }

    @ViewBuilder
    private func warnings(_ r: StickResult) -> some View {
        if !r.warnungen.isEmpty {
            VStack(alignment: .leading, spacing: 4) {
                ForEach(Array(r.warnungen.enumerated()), id: \.offset) { _, w in
                    Label(w, systemImage: "exclamationmark.triangle.fill")
                        .font(.footnote)
                        .foregroundStyle(r.hasCritical ? Color(hex: gefahrFarbeHex) : Color(hex: warnFarbeHex))
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(10)
            .background((r.hasCritical ? Color(hex: gefahrFarbeHex) : Color(hex: warnFarbeHex)).opacity(0.15), in: RoundedRectangle(cornerRadius: 8))
        }
    }

    private func stats(_ r: StickResult) -> some View {
        HStack(spacing: 8) {
            stat("Punkte", "\(r.graph.nodeIDs.count)")
            stat("Stiche", "\(r.stitchCount)")
            stat("Fadenlänge (+15 %)", String(format: "%.1f cm", r.fadenCm))
        }
    }

    private func stat(_ label: String, _ value: String) -> some View {
        VStack(spacing: 2) {
            Text(value).font(.headline)
            Text(label).font(.caption2).foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 8)
        .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 8))
    }

    private var legend: some View {
        let karton = Kartonfarbe.mit(id: model.appearance.kartonfarbe)
        let faden = Color(hex: Fadenfarbe.mit(id: model.appearance.fadenfarbe).hex)
        let items: [(String, Color, String)] = [
            ("━", faden, " Vorderseite (1×)"),
            ("┅", .gray, " Rückseiten-Sprung"),
            ("➤", Color(hex: karton.aktivVS), " aktiver VS-Schritt"),
            ("➤", Color(hex: karton.aktivRS), " aktiver RS-Sprung"),
            ("●", Color(hex: warnFarbeHex), " Abstand knapp"),
            ("●", Color(hex: gefahrFarbeHex), " Abstand zu gering"),
        ]
        var text = Text("")
        for (i, item) in items.enumerated() {
            let sep = i == 0 ? "" : "  ·  "
            let symbol = Text(item.0).foregroundColor(item.1)
            text = text + Text(sep) + symbol + Text(item.2)
        }
        return text
            .font(.caption)
            .foregroundStyle(.secondary)
            .frame(maxWidth: .infinity, alignment: .leading)
    }
}
