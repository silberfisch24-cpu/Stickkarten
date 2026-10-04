import SwiftUI

@main
struct StickkartenApp: App {
    @State private var model = AppModel()

    var body: some Scene {
        WindowGroup {
            Group {
                if Startargumente.zeigtKatalog {
                    NavigationStack { DesignKatalogView() }
                } else {
                    RootView()
                }
            }
            .environment(model)
            .tint(DS.Farbe.akzent)
        }
    }
}
