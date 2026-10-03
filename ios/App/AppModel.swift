import SwiftUI
import StickCore

/// Zustand der App: Einstellungen (persistent als JSON in UserDefaults), abgeleitetes Ergebnis
/// und Wiedergabe der Stichfolge.
@MainActor
final class AppModel: ObservableObject {
    private static let settingsKey = "stick.settings.v1"
    private static let appearanceKey = "stick.appearance.v1"

    @Published var settings: StickSettings {
        didSet {
            guard settings != oldValue else { return }
            result = StickModel.compute(settings)
            currentStep = result.maxStep
            stopPlayback()
            Self.save(settings, key: Self.settingsKey)
        }
    }

    @Published var appearance: AppearanceSettings {
        didSet { Self.save(appearance, key: Self.appearanceKey) }
    }

    @Published private(set) var result: StickResult
    @Published var currentStep: Int
    @Published private(set) var playing = false
    private var playTask: Task<Void, Never>?

    init() {
        let s: StickSettings = Self.load(key: Self.settingsKey) ?? StickSettings()
        let a: AppearanceSettings = Self.load(key: Self.appearanceKey) ?? AppearanceSettings()
        let r = StickModel.compute(s)
        settings = s
        appearance = a
        result = r
        currentStep = r.maxStep
    }

    // MARK: Persistenz

    private static func save<T: Encodable>(_ value: T, key: String) {
        if let data = try? JSONEncoder().encode(value) { UserDefaults.standard.set(data, forKey: key) }
    }

    private static func load<T: Decodable>(key: String) -> T? {
        guard let data = UserDefaults.standard.data(forKey: key) else { return nil }
        return try? JSONDecoder().decode(T.self, from: data)
    }

    func resetSettings() { settings = StickSettings() }

    // MARK: Wiedergabe (45 ms je Segment wie in der Web-App)

    func togglePlay() {
        if playing { stopPlayback(); return }
        if currentStep >= result.maxStep { currentStep = 0 }
        playing = true
        playTask = Task { [weak self] in
            while let self, !Task.isCancelled {
                if self.currentStep >= self.result.maxStep { break }
                try? await Task.sleep(nanoseconds: 45_000_000)
                if Task.isCancelled { break }
                self.currentStep = min(self.result.maxStep, self.currentStep + 1)
            }
            self?.playing = false
        }
    }

    func stopPlayback() {
        playTask?.cancel()
        playTask = nil
        playing = false
    }

    func rewind() {
        stopPlayback()
        currentStep = 0
    }

    func seek(_ step: Int) {
        stopPlayback()
        currentStep = max(0, min(result.maxStep, step))
    }
}

extension Color {
    init(hex: String) {
        var h = hex
        if h.hasPrefix("#") { h.removeFirst() }
        let v = UInt32(h, radix: 16) ?? 0
        self.init(
            red: Double((v >> 16) & 0xff) / 255, green: Double((v >> 8) & 0xff) / 255, blue: Double(v & 0xff) / 255)
    }
}
