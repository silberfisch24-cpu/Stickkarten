import SwiftUI
import UIKit

/// Design-Tokens nach docs/ui-konzept (Designregeln). Keine festen Farben oder Größen in Views.
enum DS {
    enum Farbe {
        static let akzent = Color(hell: "#1f5a4b", dunkel: "#5fb39d")
        static let inhaltsgrund = Color(hell: "#f4f0e6", dunkel: "#1c1b18")
        static let arbeitsflaeche = Color(hell: "#e9e4d6", dunkel: "#26241f")
        static let flaeche = Color(hell: "#ffffff", dunkel: "#2b2a26")
        static let umschalter = Color(hell: "#e6e1d4", dunkel: "#34322b")
        static let warnungGrund = Color(hell: "#fcefd9", dunkel: "#3d2e12")
        static let warnungText = Color(hell: "#6b3f00", dunkel: "#f5c987")
        static let kritischGrund = Color(hell: "#fde7e3", dunkel: "#4a1f1b")
        static let kritischText = Color(hell: "#8f1d14", dunkel: "#ffb4a9")
        static let okGrund = Color(hell: "#e0f0e6", dunkel: "#16352a")
        static let okText = Color(hell: "#14603a", dunkel: "#8fd9b0")
    }

    enum Mass {
        static let kapsel: CGFloat = 44
        static let hauptaktion: CGFloat = 56
        static let radiusKarte: CGFloat = 22
        static let radiusSheet: CGFloat = 34
        static let rand: CGFloat = 16
        static let abstandS: CGFloat = 8
        static let abstandM: CGFloat = 10
        static let abstandL: CGFloat = 12
        static let kachelHoehe: CGFloat = 140
        static let kachelHoehePad: CGFloat = 190
        static let tabLeiste: CGFloat = 64
    }

    /// Text-Styles (skalieren mit Dynamic Type). Die Designschriften Newsreader und IBM Plex Sans
    /// werden später eingebunden; bis dahin Serif für Titel und Systemschrift für Text.
    enum Schrift {
        static let titel = Font.system(.largeTitle, design: .serif).weight(.semibold)
        static let abschnitt = Font.system(.title3, design: .serif).weight(.semibold)
        static let text = Font.body
        static let sekundaer = Font.subheadline
        static let hinweis = Font.footnote
    }
}

extension Color {
    /// Hex-Farbe `#rrggbb`.
    init(hex: String) {
        var h = hex
        if h.hasPrefix("#") { h.removeFirst() }
        let v = UInt32(h, radix: 16) ?? 0
        self.init(
            red: Double((v >> 16) & 0xff) / 255, green: Double((v >> 8) & 0xff) / 255, blue: Double(v & 0xff) / 255)
    }

    /// Farbpaar für Hell/Dunkel (folgt dem System).
    init(hell: String, dunkel: String) {
        self.init(uiColor: UIColor { traits in
            let hex = traits.userInterfaceStyle == .dark ? dunkel : hell
            var h = hex
            if h.hasPrefix("#") { h.removeFirst() }
            let v = UInt32(h, radix: 16) ?? 0
            return UIColor(
                red: CGFloat((v >> 16) & 0xff) / 255, green: CGFloat((v >> 8) & 0xff) / 255,
                blue: CGFloat(v & 0xff) / 255, alpha: 1)
        })
    }
}
