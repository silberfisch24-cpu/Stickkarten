import Foundation

public struct Point: Equatable {
    public var x: Double
    public var y: Double
    public init(x: Double, y: Double) { self.x = x; self.y = y }
}

func polar(_ cx: Double, _ cy: Double, _ angleDeg: Double, _ r: Double) -> Point {
    let rad = (angleDeg * Double.pi) / 180
    return Point(x: cx + r * cos(rad), y: cy + r * sin(rad))
}

public func dist(_ p1: Point, _ p2: Point) -> Double {
    hypot(p1.x - p2.x, p1.y - p2.y)
}

public func divisorsOf(_ n: Int) -> [Int] {
    var ds: [Int] = []
    var d = 1
    while d <= n {
        if n % d == 0 && n / d >= 2 { ds.append(d) }
        d += 1
    }
    return ds
}

/// Ebenen, auf denen Seitenäste überhaupt existieren können (L = 2 … ebenen-1).
public func astBranchLevels(_ ebenen: Int) -> [Int] {
    var levels: [Int] = []
    var L = 2
    while L <= ebenen - 1 {
        levels.append(L)
        L += 1
    }
    return levels
}

/// JS-`Math.round` für positive Werte (Halbe werden aufgerundet).
func jsRound(_ x: Double) -> Double { (x + 0.5).rounded(.down) }
