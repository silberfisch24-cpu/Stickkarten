import Foundation

public enum FoldAxis: String, Codable {
    case v, h
}

/// Maße des flachen, ungefalteten Zuschnitts, aus dem die (gefaltete) Karte entsteht,
/// plus Versatz des vorderen (bestickten) Panels darin.
public struct FlatSheet: Equatable {
    public var w: Double
    public var h: Double
    public var offX: Double
    public var offY: Double
    public var foldAxis: FoldAxis?
    public var foldPos: Double?
}

public func computeFlatSheet(w: Double, h: Double, falzposition: Falzposition) -> FlatSheet {
    switch falzposition {
    case .links: return FlatSheet(w: w * 2, h: h, offX: w, offY: 0, foldAxis: .v, foldPos: w)
    case .oben: return FlatSheet(w: w, h: h * 2, offX: 0, offY: h, foldAxis: .h, foldPos: h)
    case .keine: return FlatSheet(w: w, h: h, offX: 0, offY: 0, foldAxis: nil, foldPos: nil)
    }
}

public enum PageOrientation: String, Codable {
    case hoch, quer
}

public struct PageFit: Equatable {
    public var orientation: PageOrientation
    public var pageW: Double
    public var pageH: Double
    public var availW: Double
    public var availH: Double
    public var scale: Double
    public var fits: Bool
}

public let pageMarginMM = 10.0

/// Passende A4-Seitenausrichtung für den Zuschnitt: 1:1 hat Vorrang; passt keine
/// Ausrichtung bei 100 %, wird die mit der geringsten Verkleinerung gewählt.
public func pageFitFor(_ flat: FlatSheet) -> PageFit {
    func option(_ o: PageOrientation, _ pw: Double, _ ph: Double) -> PageFit {
        let availW = pw - 2 * pageMarginMM
        let availH = ph - 2 * pageMarginMM
        let scale = min(1, min(availW / flat.w, availH / flat.h))
        return PageFit(orientation: o, pageW: pw, pageH: ph, availW: availW, availH: availH, scale: scale, fits: scale >= 0.999)
    }
    let hoch = option(.hoch, 210, 297)
    let quer = option(.quer, 297, 210)
    if hoch.fits && quer.fits { return flat.w >= flat.h ? quer : hoch }
    if hoch.fits { return hoch }
    if quer.fits { return quer }
    return hoch.scale >= quer.scale ? hoch : quer
}
