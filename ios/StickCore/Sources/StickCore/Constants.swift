import Foundation

/// Feste Randbedingungen — 1:1 aus der Web-App (`Feste Randbedingungen`).
public enum Stick {
    public static let fadenStraenge = 3.0
    public static let fadenDurchmesser = fadenStraenge * 0.17 // mm
    public static let lochDurchmesser = min(1.5, max(0.5, fadenDurchmesser * 1.8)) // mm
    public static let mindestabstand = max(2.0, lochDurchmesser * 3.5) // mm
    public static let randMin = 14.0 // mm
    public static let falzMin = 18.0 // mm
    public static let stichLimit = 300
    /// 100–150 % des Mindestabstands = mäßig eng; darunter = zu gering
    public static let moderatFaktor = 1.5
    /// Fadenzuschlag (+15 %)
    public static let fadenZuschlag = 1.15
    /// 1 mm in PDF-Punkten
    public static let ptPerMM = 72.0 / 25.4
}

public enum FormatPreset: String, Codable, CaseIterable, Identifiable {
    case a6Hoch = "a6-hoch"
    case a6Quer = "a6-quer"
    case custom

    public var id: String { rawValue }

    public var label: String {
        switch self {
        case .a6Hoch: return "A6 Hochformat, 105 × 148 mm (A5 gefaltet)"
        case .a6Quer: return "A6 Querformat, 148 × 105 mm (A5 gefaltet)"
        case .custom: return "Eigenes Format"
        }
    }

    /// nil bei `.custom`
    public var size: (w: Double, h: Double)? {
        switch self {
        case .a6Hoch: return (105, 148)
        case .a6Quer: return (148, 105)
        case .custom: return nil
        }
    }
}

public enum Falzposition: String, Codable, CaseIterable, Identifiable {
    case links, oben, keine
    public var id: String { rawValue }
    public var label: String {
        switch self {
        case .links: return "Links"
        case .oben: return "Oben"
        case .keine: return "Keine (Einzelkarte)"
        }
    }
}

/// „Seitenäste beim Sternlevel weglassen“ — je Sternschicht.
public enum AstAusblendung: String, Codable, CaseIterable, Identifiable {
    case keine, exakt, kleinerGleich
    public var id: String { rawValue }
}

public struct Kartonfarbe: Identifiable, Equatable {
    public let id: String
    public let label: String
    public let hex: String
    public let aktivVS: String
    public let aktivRS: String

    public static let alle: [Kartonfarbe] = [
        Kartonfarbe(id: "tanne", label: "Tannengrün", hex: "#153a2c", aktivVS: "#ffd966", aktivRS: "#7fd8ff"),
        Kartonfarbe(id: "mitternacht", label: "Mitternachtsblau", hex: "#10203a", aktivVS: "#ffcf5c", aktivRS: "#8fe6c8"),
        Kartonfarbe(id: "bordeaux", label: "Bordeaux", hex: "#481621", aktivVS: "#ffd97a", aktivRS: "#7fe0e0"),
        Kartonfarbe(id: "elfenbein", label: "Elfenbein", hex: "#efe6d6", aktivVS: "#a8650a", aktivRS: "#1f4e8c"),
    ]
    public static func mit(id: String) -> Kartonfarbe { alle.first { $0.id == id } ?? alle[0] }
}

public struct Fadenfarbe: Identifiable, Equatable {
    public let id: String
    public let label: String
    public let hex: String

    public static let alle: [Fadenfarbe] = [
        Fadenfarbe(id: "gold", label: "Gold", hex: "#e8c987"),
        Fadenfarbe(id: "silber", label: "Silber", hex: "#d9e2e7"),
        Fadenfarbe(id: "weiss", label: "Weiß", hex: "#ffffff"),
        Fadenfarbe(id: "blau", label: "Mitternachtsblau", hex: "#3a5a8c"),
    ]
    public static func mit(id: String) -> Fadenfarbe { alle.first { $0.id == id } ?? alle[0] }
}

public let warnFarbeHex = "#e8a23d" // mäßig eng
public let gefahrFarbeHex = "#e0503f" // zu gering
