# Abwärtskompatibilität: Mindest-iOS und Verbreitung

Stand der Recherche: 4. Oktober 2026. Ziel: mindestens 90 % der real genutzten iPhones und
iPads erreichen.

## Verbreitung

**Apple, App-Store-Geräte, gemessen am 7. Juni 2026** (alle Geräte, die im Store Umsätze
gemacht haben):

| | Version 26 | Version 18 | älter |
|---|---|---|---|
| iPhone, alle | 79 % | 14 % | 7 % |
| iPhone, letzte vier Jahre | 86 % | 11 % | 3 % |
| iPad, alle | 68 % | 17 % | 15 % |
| iPad, letzte vier Jahre | 79 % | 16 % | 5 % |

Daraus (Version 26 oder 18): **iPhone 93 %, iPad 85 %**. Der Rest ist „älter“ (17 und davor).

**Seit Juni gestiegen:** iOS 27 erschien im September 2026. TelemetryDeck (kleinere
App-Stichprobe) zeigt Ende September 2026: iOS 27 16,3 %, iOS 26 74,6 %, iOS 18 7,1 %. Das
wären etwa 98 % auf Version 18 oder neuer. StatCounter liegt deutlich niedriger bei iOS 26
(etwa 56 %), vermutlich wegen Änderungen an der Safari-Kennung. Die Zahlen sind daher
Näherungen.

## Schlussfolgerung

- **iOS 18/iPadOS 18 als Minimum** reicht für 90 % der iPhones (93 % im Juni, inzwischen mehr).
  Beim iPad lag es im Juni mit 85 % darunter, wird durch den Anstieg seit dem Herbst aber
  vermutlich die 90 % erreichen. Diese Vermutung ist nicht belegt.
- **iOS 17/iPadOS 17 als Minimum** (aktuelle Festlegung) erreicht die 90 % auf beiden Geräten
  sicher, weil Version 17 den größten Teil der Gruppe „älter“ (7 % bzw. 15 %) ausmacht.
  Eine Aufschlüsselung der Gruppe „älter“ liefert Apple nicht.
- **Empfehlung:** iOS 17 beibehalten, solange der Mehraufwand klein ist. Wechsel auf iOS 18 nur,
  wenn eine iOS-18-Funktion (z. B. neue `Tab`-Schreibweise) den Code deutlich vereinfacht.

## Geräte-Hardware (Quelle: Herstellerlisten)

- iOS 26: iPhone 11 und neuer (iPhone XS/XR fallen weg). iPadOS 26: außer der 7. Generation alle
  Modelle von iPadOS 18.
- iOS 18: iPhone XS/XR und neuer. iOS 17: dieselben (XS und neuer).
- Für unsere App kein Hardwareproblem: Der Kern ist reine Rechnung, PDF-Erzeugung und
  Zeichnen.

## Folgen für das Design (Liquid Glass erst ab iOS 26)

Das Designziel „Liquid Glass“ ist erst ab iOS/iPadOS 26 verfügbar. Das sind heute etwa
80 % der iPhones und 70 % der iPads (mit iOS 27 noch mehr). Für die übrigen braucht jedes
Glaselement einen Rückfall. Die Tabelle beruht auf meinem Kenntnisstand der APIs und ist
**in Xcode zu prüfen**.

| Designelement | iOS 26 | Rückfall iOS 17 und 18 |
|---|---|---|
| Glas-Kapsel, runde Glas-Buttons | `glassEffect`, `GlassEffectContainer` | `.ultraThinMaterial` mit Rand und Schatten |
| Schwebende Tab-Leiste | `TabView` (Standard) | `TabView`, iOS 17/18 flach statt schwebend |
| Kapsel „Weitermachen“ über der Tab-Leiste | `tabViewBottomAccessory` | eigene Kapsel über der Tab-Leiste |
| Seitenleiste (iPad) | schwebend (Standard) | `NavigationSplitView` |
| Sheet in 3 Stufen mit bedienbarer Karte dahinter | Detents, `presentationBackgroundInteraction` | derselbe Weg (ab iOS 16.4 verfügbar) |
| Sheet-Material | Glas automatisch | `presentationBackground(.regularMaterial)` |
| Umschalter (Glas) | Glas-Variante | `Picker` mit eigenem Stil auf Material |

Weiter gilt:

- Der Aufbau (Detents, Panels, Kacheln) braucht keine iOS-26-API. Nur das Material ändert
  sich. Die Designregeln trennen das bereits (Regeln gleich, Materialwerte austauschbar).
- Vorschlag: ein zentrales Modul „Designsystem“ mit je einer Funktion pro Materialart
  (`glass()`, `sheetBackground()`), die intern `#available(iOS 26, *)` prüft. Alle Screens
  nutzen nur diese Funktionen.
- Testgeräte oder Simulatoren: mindestens ein iPhone und ein iPad mit iOS 17 und eines mit 26.

## Quellen

- Apple: <https://developer.apple.com/support/app-store/> (Stand 7. Juni 2026)
- MacTech: <https://www.mactech.com/2026/06/09/apple-79-of-all-iphones-use-ios-26-and-68-of-all-ipads-use-ipados-26/amp/>
- TelemetryDeck: <https://telemetrydeck.com/survey/apple/iOS/majorSystemVersions/>
- StatCounter: <https://gs.statcounter.com/ios-version-market-share/>
- Kompatibilität: <https://www.techradar.com/phones/ios/ios-26-compatibility-does-your-iphone-support-it-heres-the-full-list-of-supported-devices>
