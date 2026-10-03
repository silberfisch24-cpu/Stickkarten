# Stickkarten — native iPhone-/iPad-App (SwiftUI)

Native Portierung der Web-App `src/StickkartenGeneratorV4.jsx`. Die Web-App bleibt unverändert und ist die
fachliche Referenz (Begriffe und UI-Sprache: Deutsch — Astschicht, Sternschicht, VS/RS, Mindestabstand …).

```
ios/
├── StickCore/          Swift Package (kein UI)
│   ├── Sources/StickCore   Port der Fachlogik: buildGraph, addSternLayer, addFraktalZweige, buildStitchSequence,
│   │                       Abstands-Klassifizierung, Fadenlänge, Rmin/Rmax/Zoom, computeFlatSheet, pageFitFor,
│   │                       Anleitungs-Schritte und Schrittdiagramm-Layout
│   ├── Sources/StickPDF    Vektor-PDF: Lochmuster 1:1 und mehrseitige Anleitung
│   └── Tests               Golden-Vergleich gegen die JSX + PDF-Maßtests
├── App/                SwiftUI-App (iPhone + iPad)
├── project.yml         XcodeGen-Beschreibung → erzeugt Stickkarten.xcodeproj
└── tools/              Node-Skript, das die Golden-Files direkt aus der JSX erzeugt
```

## Was die App kann

* Regler/Auswahl wie in der Sidebar der Web-App (Kreispunkte, Astschicht mit Ebenen/Astwinkel/-länge/Wachstum,
  Sternschicht 1 und 2 mit Sternebene, Strahlen/Teiler, Schrittweite, Rotationsversatz, „Seitenäste beim Sternlevel
  weglassen“). Zusätzlich (in der Web-App nur als Zustand ohne Regler vorhanden): Fraktal-Tiefe 0–2 und -Skalierung.
* Kartenvorschau (Canvas) mit animierter Stichfolge: Play/Pause, Zurück, Slider, aktiver VS-Stich/RS-Sprung,
  Restmuster-Vorschau, Abstandswarnungen (knapp = orange, zu gering = rot), Statistik (Punkte, Stiche, Fadenlänge +15 %).
* Einstellungen: Format (A6 hoch/quer, eigenes Format), Falzposition, Zoom, Kartonfarbe, Fadenfarbe.
* Zustand bleibt erhalten (Codable-JSON in `UserDefaults`).
* **Drucken & Teilen** (Drucker-Symbol): zwei PDFs, jeweils per Teilen-Menü oder AirPrint:
  * **Lochmuster 1:1** — A4 hoch/quer wie `pageFitFor()`, 1 mm = 72/25,4 pt, Falzlinie, Panel-Rahmen, Nutzflächen-Rahmen,
    Löcher in echter Größe (Ø `LOCH_DURCHMESSER`), dazu ein 50-mm-Kontrollbalken am Blattrand. Passt der Zuschnitt nicht
    auf A4, wird verkleinert und deutlich als „nicht zum Anstechen geeignet“ markiert.
  * **Anleitung** — Ebenen-Übersicht, Flocke (Arm 1 von n als Schrittdiagramm + Tabelle), Sternschichten, Fadenlängen;
    die letzte Seite ist wieder das Lochmuster 1:1.
  Beim Drucken **A4 und „Tatsächliche Größe“/100 %** wählen; Balken nachmessen.

## Entwicklung ohne Mac: GitHub Actions

Es gibt keinen lokalen Xcode-Zwang — der Runner `macos-latest` baut und testet (`.github/workflows/ios.yml`):

| Job | Inhalt |
| --- | --- |
| `core` | `swift test` in `ios/StickCore`: Golden-Vergleich, PDF-Maße; lädt die erzeugten PDFs als Artifact **`stickkarten-pdfs`** hoch |
| `app` | `xcodegen generate` → `xcodebuild build` für den iOS-Simulator; baut außerdem ein **unsigniertes IPA** (Artifact `stickkarten-unsigned-ipa`) |

Logs bei Fehlern: `gh run view --log-failed` (bzw. Actions-Tab).

### Golden-Tests

`ios/tools/gen-golden.mjs` lädt die JSX per esbuild als Modul und ruft `buildGraph`, `buildStitchSequence`,
`computeFlatSheet`, `pageFitFor`, `buildStepDiagram` usw. **unverändert** auf. Nur die in der React-Komponente inline
berechneten Werte (Rmin/Rmax, kMax, unterdrückte Ebenen, Klassifizierung, Arm-/Stern-Abschnitte der Anleitung) sind im
Skript 1:1 nachgebaut (Zeilen sind kommentiert). Abgedeckt: ~600 Konfigurationen (Kreispunkte 3–16 × Ebenen 1–6,
Fraktaltiefe 0–2, Seitenäste an/aus, ein/zwei Sternschichten, Teiler, Versatz, Astausblendung exakt/kleinerGleich,
Formate, Falz, Zoom). Verglichen werden Knotenreihenfolge und -positionen (Toleranz 1e-9), Kantenreihenfolge,
Stichfolge, Statistik, Warnungen, Klassifizierung, Zuschnitt/Seitenwahl sowie Schritte, Beschriftungen und
Fadenlängen der Anleitung.

Neu erzeugen (nur nötig, wenn sich die JSX ändert):

```sh
cd ios/tools && npm install && npm run golden
```

Bekannte, bewusst tolerierte Abweichungen (symmetrische Muster, letztes Bit von `hypot`/`atan2` in V8 vs. Apple-libm):
(1) liegt ein Nachbarabstand *exakt* auf der Schwelle (Zoom 0 → Astabstand = Mindestabstand), darf die
Klassifizierung dieses Punkts abweichen; (2) die Lage von RS-Bögen, Zahlenkreisen und Beschriftungen in den
Schrittdiagrammen (Kollisions-/Winkel-Gleichstände) wird nur grob (< 60 px) verglichen; Linien und Lochkreise streng.
Knoten, Kanten, Stichfolge und Statistik sind davon nicht betroffen.

### PDF-Tests

`PDFTests` prüft (1) Seitenmaße 210 × 297 / 297 × 210 mm (Media-Box, ±0,01 pt), (2) alle paarweisen Lochabstände im
Seitenplan gegen das Modell (< 1 µm) und (3) das **gerenderte** PDF: Es wird mit 10 px/mm gerastert und der
Schwerpunkt jedes Lochs gegen die Soll-Position geprüft (< 0,1 mm).

> Abweichung von der Vorgabe: Das PDF entsteht mit einem CoreGraphics-PDF-Kontext statt `UIGraphicsPDFRenderer`.
> `UIGraphicsPDFRenderer` ist nur ein UIKit-Wrapper um genau diesen Kontext (gleiche Vektor-Ausgabe), lässt sich aber
> nicht unter `swift test` auf macOS prüfen — so laufen die Maßtests ohne Simulator.

## App einmalig aufs eigene Gerät bringen (Signing)

Apple verlangt für jede App auf einem echten Gerät eine Signatur. Drei Wege:

### A) Ohne eigenen Mac: unsigniertes IPA selbst signieren (kostenlose Apple-ID)

1. Im Actions-Tab den letzten grünen Lauf öffnen → Artifact **`stickkarten-unsigned-ipa`** laden und entpacken.
2. Auf einem Windows-PC/Mac [Sideloadly](https://sideloadly.io) oder [AltStore](https://altstore.io) installieren,
   iPhone/iPad per Kabel verbinden, `Stickkarten-unsigned.ipa` hineinziehen, mit der eigenen Apple-ID anmelden.
3. Auf dem Gerät: *Einstellungen → Allgemein → VPN & Geräteverwaltung* → dem eigenen Entwicklerprofil vertrauen;
   ggf. Entwicklermodus aktivieren (*Datenschutz & Sicherheit → Entwicklermodus*).
4. Mit kostenloser Apple-ID läuft die App **7 Tage**, danach muss neu signiert werden (AltStore kann das automatisch
   im WLAN). Mit bezahltem Developer-Account 1 Jahr.

### B) Mit (geliehenem) Mac und Xcode — einmalig

1. Repo klonen, `brew install xcodegen`, dann `cd ios && xcodegen generate && open Stickkarten.xcodeproj`.
2. Target *Stickkarten* → *Signing & Capabilities* → *Team* wählen (Apple-ID unter *Xcode → Settings → Accounts*
   hinzufügen). Alternativ die Team-ID in `ios/project.yml` unter `DEVELOPMENT_TEAM` eintragen und neu generieren.
3. Bundle-ID ggf. ändern (`de.stickkarten.app` ist evtl. vergeben, z. B. `de.<dein-name>.stickkarten`; in
   `project.yml` unter `PRODUCT_BUNDLE_IDENTIFIER`).
4. Gerät anschließen, als Ziel wählen, ▶︎. Dieselben Vertrauens-/Entwicklermodus-Schritte wie oben.

### C) TestFlight (Voraussetzung: Apple Developer Program, 99 USD/Jahr)

* **Mit Mac:** Bundle-ID in App Store Connect anlegen → in Xcode *Product → Archive* → *Distribute App → App Store
  Connect* → in App Store Connect unter *TestFlight* interne Tester (bis 100, ohne Review) hinzufügen → Installation
  über die TestFlight-App. Builds laufen 90 Tage.
* **Ohne Mac (CI):** In App Store Connect einen API-Key (Rolle *App Manager*) erzeugen; als Repo-Secrets ablegen
  (`ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_KEY_P8`, `DEVELOPMENT_TEAM`). Im Workflow dann
  `xcodebuild archive … -allowProvisioningUpdates -authenticationKeyPath … -authenticationKeyID … -authenticationKeyIssuerID …`
  (automatisches Signing per API-Key) und `xcodebuild -exportArchive` mit `method: app-store-connect`; der Upload
  geht mit `xcrun altool --upload-app` oder der Action `apple-actions/upload-testflight-build`. Das ist nicht
  eingerichtet, weil dafür Zugangsdaten nötig sind — die Struktur (`project.yml`, Bundle-ID, Icon,
  `ITSAppUsesNonExemptEncryption`) ist aber vorbereitet.

## Lokal bauen/testen (mit Mac)

```sh
cd ios/StickCore && swift test                 # Golden + PDF; PDFs nach $STICK_PDF_OUT, falls gesetzt
cd ios && xcodegen generate && xcodebuild build -project Stickkarten.xcodeproj -scheme Stickkarten \
  -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO
```
