import Observation
import StickCore

/// App-Zustand (Gerüst). Arbeitsstand, Favoriten und Einstellungen folgen in Phase B.
@Observable
final class AppModel {
    var settings = StickSettings()

    var result: StickResult { StickModel.compute(settings) }
}
