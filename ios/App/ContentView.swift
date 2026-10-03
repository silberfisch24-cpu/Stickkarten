import SwiftUI
import StickCore

struct ContentView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.horizontalSizeClass) private var hSize
    @State private var showSettings = false
    @State private var showExport = false

    var body: some View {
        NavigationStack {
            Group {
                if hSize == .regular {
                    HStack(spacing: 0) {
                        ControlsView()
                            .frame(width: 400)
                        Divider()
                        PreviewPane()
                    }
                } else {
                    TabView {
                        PreviewPane()
                            .tabItem { Label("Vorschau", systemImage: "sparkles") }
                        ControlsView()
                            .tabItem { Label("Muster", systemImage: "slider.horizontal.3") }
                    }
                }
            }
            .navigationTitle("Stickkarten")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItemGroup(placement: .navigationBarTrailing) {
                    Button { showExport = true } label: { Label("Drucken & Teilen", systemImage: "printer") }
                        .disabled(model.result.hasCritical)
                    Button { showSettings = true } label: { Label("Einstellungen", systemImage: "gearshape") }
                }
            }
            .sheet(isPresented: $showSettings) { SettingsView() }
            .sheet(isPresented: $showExport) { ExportView() }
        }
    }
}
