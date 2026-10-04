import Foundation

/// Ein gesichertes Muster (Favorit).
public struct Favorit: Codable, Equatable, Identifiable {
    public var id: UUID
    public var name: String
    public var settings: StickSettings
    public var erstellt: Date

    public init(id: UUID = UUID(), name: String, settings: StickSettings, erstellt: Date = Date()) {
        self.id = id
        self.name = name
        self.settings = settings
        self.erstellt = erstellt
    }
}

/// Gesamter dauerhaft gespeicherter App-Zustand (Schema v2): Arbeitsstand („Weitermachen“),
/// Favoriten, Darstellung und Erststart-Merker. Fehlende Schlüssel fallen auf Standardwerte zurück.
public struct AppState: Codable, Equatable {
    public static let aktuelleVersion = 2
    public static let maxFavoriten = 24

    public var version = AppState.aktuelleVersion
    public var arbeitsstand: StickSettings?
    public var favoriten: [Favorit] = []
    public var einfuehrungGesehen = false
    public var appearance = AppearanceSettings()

    public init() {}

    public init(from decoder: Decoder) throws {
        self.init()
        let c = try decoder.container(keyedBy: CodingKeys.self)
        arbeitsstand = try c.decodeIfPresent(StickSettings.self, forKey: .arbeitsstand)
        favoriten = try c.decodeIfPresent([Favorit].self, forKey: .favoriten) ?? []
        einfuehrungGesehen = try c.decodeIfPresent(Bool.self, forKey: .einfuehrungGesehen) ?? false
        appearance = try c.decodeIfPresent(AppearanceSettings.self, forKey: .appearance) ?? AppearanceSettings()
        version = Self.aktuelleVersion
    }

    // MARK: Favoriten (neueste zuerst, höchstens 24, Name beim Sichern „Muster n“)

    /// Nächste freie Nummer für „Muster n“ (höchste vorhandene + 1).
    public var naechsteMusterNummer: Int {
        let nummern = favoriten.compactMap { f -> Int? in
            guard f.name.hasPrefix("Muster ") else { return nil }
            return Int(f.name.dropFirst("Muster ".count))
        }
        return (nummern.max() ?? 0) + 1
    }

    /// Fügt einen Favoriten vorn ein. `nil`, wenn das Limit erreicht ist.
    @discardableResult
    public mutating func favoritHinzufuegen(_ settings: StickSettings, name: String? = nil, jetzt: Date = Date()) -> Favorit? {
        guard favoriten.count < Self.maxFavoriten else { return nil }
        let rein = name?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let f = Favorit(name: rein.isEmpty ? "Muster \(naechsteMusterNummer)" : rein, settings: settings, erstellt: jetzt)
        favoriten.insert(f, at: 0)
        return f
    }

    public mutating func favoritUmbenennen(id: UUID, name: String) {
        let rein = name.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !rein.isEmpty, let i = favoriten.firstIndex(where: { $0.id == id }) else { return }
        favoriten[i].name = rein
    }

    /// Dupliziert einen Favoriten (Kopie steht vorn). `nil` bei Limit oder unbekannter ID.
    @discardableResult
    public mutating func favoritDuplizieren(id: UUID, jetzt: Date = Date()) -> Favorit? {
        guard let f = favoriten.first(where: { $0.id == id }) else { return nil }
        return favoritHinzufuegen(f.settings, name: "\(f.name) Kopie", jetzt: jetzt)
    }

    public mutating func favoritLoeschen(id: UUID) {
        favoriten.removeAll { $0.id == id }
    }

    // MARK: Laden und Migration

    /// Lädt den Zustand. Ohne v2-Daten werden die Einzelstände der ersten Portierung (v1) übernommen.
    public static func laden(v2: Data?, v1Settings: Data?, v1Appearance: Data?) -> AppState {
        let dec = JSONDecoder()
        if let v2, let s = try? dec.decode(AppState.self, from: v2) { return s }
        var s = AppState()
        if let d = v1Settings, let st = try? dec.decode(StickSettings.self, from: d) { s.arbeitsstand = st }
        if let d = v1Appearance, let a = try? dec.decode(AppearanceSettings.self, from: d) { s.appearance = a }
        return s
    }

    public func codiert() -> Data? { try? JSONEncoder().encode(self) }
}
