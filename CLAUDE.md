# Stickkarten-Generator

Generator für bestickte Karten (Papiersticken): Muster aus Astschicht (Flocke) und
Sternschicht(en), mit Stichfolge, Mindestabstand-Prüfung, Fadenlänge, Lochmuster und
Anleitung als PDF. UI und Fachbegriffe sind durchgehend Deutsch.

## Stand und Richtung
- Plan: `docs/projektplan-konsolidierung.md` (maßgeblich, Phasen A–G).
- UI-Referenz für Aussehen und Bedienung: `docs/ui-konzept/` (`konzept.md`, `gesamtreview.md`,
  Boards unter `bilder/`) und `docs/ui-grundanalyse.md`. Das UI wird nach diesem Konzept gebaut,
  nicht nach der ersten Portierung.
- Die **erste iOS-Portierung** liegt nur noch im Branch `archive/ios-port-v1` (Steinbruch, wird nie
  gemergt).
- Die **Web-App ist eingefroren** (Legacy). `src/` und der Pages-Deploy (`deploy.yml`) bleiben
  lauffähig und werden nicht weiterentwickelt. Ausnahme: Fehlerbehebung.

## Struktur
- `src/StickkartenGeneratorV4.jsx`: Web-App (Vite/React), Legacy. Fachliche Referenz für den
  Legacy-Pfad des Kerns.
- `ios/StickCore/`: Swift Package. `StickCore` (Logik ohne UI) und `StickPDF` (Vektor-PDF per
  CoreGraphics: Lochmuster 1:1, Anleitung).
- `ios/App/`: SwiftUI-App (iOS 17, iPhone und iPad). `ios/project.yml` (XcodeGen) erzeugt das
  Projekt, `*.xcodeproj` wird nicht eingecheckt.
- `ios/tools/gen-golden.mjs`: erzeugt die Golden-Files aus der JSX.
- `.github/workflows/`: `deploy.yml` (Web, Pages), `ios.yml` (iOS auf macos-latest).

## Verbindliche Regeln
- Reihenfolge der Kanten und Stiche ist fachlich entscheidend (Stichweg), nie unabsichtlich ändern.
  Golden-Tests müssen grün bleiben, solange der Legacy-Pfad im Kern existiert. Änderungen an der
  Fachlogik gehen als **neuer Modus** neben den Legacy-Pfad, nicht als Ersatz.
- Rmin/Rmax, kMax, Astausblendung, Klassifizierung und Arm-/Stern-Abschnitte stecken unexportiert in
  der JSX und sind in `gen-golden.mjs` nachgebaut. Wer den Legacy-Pfad ändert, passt beides an.
- Bewusst tolerierte Abweichungen (JS-`hypot`/`atan2` vs. Apple-libm, nur bei exakten Gleichständen):
  Klassifizierung bei Nachbarabstand exakt auf der Schwelle, Lage von RS-Bögen, Zahlenkreisen und
  Beschriftungen. Nicht darüber hinaus aufweichen.
- Lochmuster-PDF maßstabsgetreu 1:1 (1 mm = 72/25,4 pt), immer Vektor, nie Bild. `PDFTests` müssen
  bestehen. Rote Tests nie abschwächen oder überspringen, erst die Ursache klären.
- Konstanten stehen in Swift zentral in `Stick` (`Constants.swift`), `testConstantsMatchReference`
  hält sie gegen die JSX synchron.
- Keine Daten erheben oder versenden, alles bleibt lokal. Nichts einbauen, was das ändert
  (Analytics, Netzwerkzugriffe), ohne Rückfrage.
- Texte und Fachbegriffe Deutsch (VS/RS, Astschicht, Sternschicht, Falz …), in String-Katalogen.
- UI: nur Design-Tokens und Text-Styles (Dynamic Type, Hell/Dunkel), Layout nach Größenklasse und
  Breite, nie nach Gerätetyp. Jede Grafik hat eine Beschreibung für VoiceOver.
- Geführter Weg: Zuordnung (Format, Stil, Aufwand, Farbwelt) → drei Muster ist fest und stabil.
  Katalog-IDs werden nie umsortiert oder ersetzt, neue Muster bekommen neue IDs.

## Arbeitsweise
- Änderungen per Pull Request, nie direkt auf `main`. Kleine Commits. In Sessions den vorgegebenen
  Entwicklungs-Branch verwenden.
- Kein lokaler Mac und kein Simulator in Cloud-Sessions. Geprüft wird über GitHub Actions (`actions_list`,
  `get_job_logs`). Layout wird erst später im Projekt getestet (Phase F), Gerätetest auf dem MacBook.
- Neue Logik bekommt Tests in `StickCore`. Bei Fehlern erst den Test schreiben.

## Befehle
- Web: `npm ci`, `npm run dev`, `npm run build` (mit `package-lock.json`).
- Golden-Files neu erzeugen: `cd ios/tools && npm install && npm run golden`
- iOS-Tests (nur Mac/CI): `cd ios/StickCore && swift test`. Mit `STICK_PDF_OUT=<Ordner>` werden
  Beispiel-PDFs geschrieben (CI-Artifact `stickkarten-pdfs`).
- App bauen: `cd ios && xcodegen generate && xcodebuild build -project Stickkarten.xcodeproj
  -scheme Stickkarten -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO`

## Veröffentlichung (noch nicht eingerichtet)
Zuerst privat über TestFlight. Es fehlen Apple-Developer-Zugang, eigene Bundle-ID (Platzhalter
`de.stickkarten.app`) und CI-Signing. Zertifikate und Tokens nur als GitHub-Secrets.
