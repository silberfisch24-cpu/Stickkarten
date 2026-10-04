import SwiftUI

/// Platzhalter: Die Oberfläche entsteht nach dem UI-Konzept (docs/ui-konzept), siehe Projektplan.
struct ContentView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        VStack(spacing: 12) {
            Text("Stickkarten").font(.largeTitle)
            Text("\(model.result.stitchCount) Stiche")
                .foregroundStyle(.secondary)
        }
        .padding()
    }
}
