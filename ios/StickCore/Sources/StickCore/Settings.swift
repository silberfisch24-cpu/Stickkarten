import Foundation

/// Alle musterrelevanten Einstellungen (entspricht den `useState`-Werten der Web-App).
public struct StickSettings: Codable, Equatable {
    public var formatPreset: FormatPreset = .a6Hoch
    public var customW: Double = 105
    public var customH: Double = 148
    public var falzposition: Falzposition = .links

    public var n: Int = 8
    public var zoom: Double = 1

    public var astschicht: Bool = true
    public var ebenen: Int = 4
    public var astAktiv: Bool = true
    public var astWinkel: Double = 55
    public var astLaenge: Double = 0.7
    public var astWachstum: Double = 0.3
    public var fraktalTiefe: Int = 0
    public var fraktalSkalierung: Double = 0.5

    public var sternschicht: Bool = true
    public var sternEbene: Int = 2
    public var sternTeiler: Int = 1
    public var k1: Int = 3
    public var sternschicht2: Bool = false
    public var sternEbene2: Int = 4
    public var sternTeiler2: Int = 1
    public var sternVersatz2: Int = 0
    public var k2: Int = 1
    public var astAusblendung1: AstAusblendung = .keine
    public var astAusblendung2: AstAusblendung = .keine

    public init() {}

    public init(from decoder: Decoder) throws {
        // Fehlende Schlüssel (ältere gespeicherte Stände) fallen auf die Standardwerte zurück.
        self.init()
        let c = try decoder.container(keyedBy: CodingKeys.self)
        func get<T: Decodable>(_ key: CodingKeys, _ value: inout T) throws {
            if let v = try c.decodeIfPresent(T.self, forKey: key) { value = v }
        }
        try get(.formatPreset, &formatPreset)
        try get(.customW, &customW)
        try get(.customH, &customH)
        try get(.falzposition, &falzposition)
        try get(.n, &n)
        try get(.zoom, &zoom)
        try get(.astschicht, &astschicht)
        try get(.ebenen, &ebenen)
        try get(.astAktiv, &astAktiv)
        try get(.astWinkel, &astWinkel)
        try get(.astLaenge, &astLaenge)
        try get(.astWachstum, &astWachstum)
        try get(.fraktalTiefe, &fraktalTiefe)
        try get(.fraktalSkalierung, &fraktalSkalierung)
        try get(.sternschicht, &sternschicht)
        try get(.sternEbene, &sternEbene)
        try get(.sternTeiler, &sternTeiler)
        try get(.k1, &k1)
        try get(.sternschicht2, &sternschicht2)
        try get(.sternEbene2, &sternEbene2)
        try get(.sternTeiler2, &sternTeiler2)
        try get(.sternVersatz2, &sternVersatz2)
        try get(.k2, &k2)
        try get(.astAusblendung1, &astAusblendung1)
        try get(.astAusblendung2, &astAusblendung2)
    }
}

/// Reine Darstellungs-Einstellungen (haben keinen Einfluss auf das Muster).
public struct AppearanceSettings: Codable, Equatable {
    public var kartonfarbe: String = "tanne"
    public var fadenfarbe: String = "gold"
    public var zeigeVorschau: Bool = true
    public var zeigeSpruenge: Bool = true

    public init() {}

    public init(from decoder: Decoder) throws {
        self.init()
        let c = try decoder.container(keyedBy: CodingKeys.self)
        kartonfarbe = try c.decodeIfPresent(String.self, forKey: .kartonfarbe) ?? kartonfarbe
        fadenfarbe = try c.decodeIfPresent(String.self, forKey: .fadenfarbe) ?? fadenfarbe
        zeigeVorschau = try c.decodeIfPresent(Bool.self, forKey: .zeigeVorschau) ?? zeigeVorschau
        zeigeSpruenge = try c.decodeIfPresent(Bool.self, forKey: .zeigeSpruenge) ?? zeigeSpruenge
    }
}
