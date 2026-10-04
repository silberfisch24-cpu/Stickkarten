import SwiftUI

extension View {
    /// Glas für schwebende Elemente: Liquid Glass ab iOS 26, davor Material mit Rand und Schatten.
    @ViewBuilder
    func glas<S: InsettableShape>(_ form: S) -> some View {
        if #available(iOS 26, *) {
            self.glassEffect(.regular, in: form)
        } else {
            self
                .background(.ultraThinMaterial, in: form)
                .overlay(form.stroke(Color.white.opacity(0.35), lineWidth: 0.5))
                .shadow(color: .black.opacity(0.12), radius: 8, y: 2)
        }
    }

    /// Hintergrund halbtransparenter Sheets.
    func sheetHintergrund() -> some View {
        presentationBackground(.regularMaterial)
    }

    /// Sheet in drei Stufen (klein, mittel, groß). Bis „mittel“ bleibt die Karte dahinter bedienbar.
    func stufenSheet<Inhalt: View>(
        isPresented: Binding<Bool>, @ViewBuilder inhalt: @escaping () -> Inhalt
    ) -> some View {
        sheet(isPresented: isPresented) {
            inhalt()
                .presentationDetents([.height(96), .medium, .large])
                .presentationBackgroundInteraction(.enabled(upThrough: .medium))
                .presentationDragIndicator(.visible)
                .presentationCornerRadius(DS.Mass.radiusSheet)
                .sheetHintergrund()
        }
    }
}
