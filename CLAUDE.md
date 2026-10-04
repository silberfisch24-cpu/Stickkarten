# Stickkarten-Generator

Generator für bestickte Karten (Papiersticken): Muster aus Astschicht (Flocke) und
Sternschicht(en), mit Stichfolge, Mindestabstand-Prüfung, Fadenlänge, Lochmuster und
Anleitung als PDF. UI und Fachbegriffe sind durchgehend Deutsch.

## Struktur
- `src/StickkartenGeneratorV4.jsx`: Web-App (Vite/React) und **fachliche Referenz**.
- `ios/StickCore/`: Swift Package mit zwei Targets:
  - `StickCore`: reine Logik ohne UI (Graph, Stichfolge, Abstände, Fadenlänge, Format/Falz,
    Anleitungsschritte, Schrittdiagramm-Layout).
  - `StickPDF`: Vektor-PDF per CoreGraphics (Lochmuster 1:1, Anleitung).
- `ios/App/`: SwiftUI-App für iPhone und iPad. `ios/project.yml` (XcodeGen) erzeugt das
  Xcode-Projekt; `*.xcodeproj` wird nicht eingecheckt.
- `ios/tools/gen-golden.mjs`: erzeugt die Golden-Files aus der JSX.
- `ios/README.md`: Signing, Sideloading, TestFlight.
- `.github/workflows/`: `deploy.yml` (Web, Pages), `ios.yml` (iOS auf macos-latest).

## Verbindliche Regeln
- Die Web-App ist die Referenz. Logikänderungen zuerst dort, dann in Swift nachziehen und
  die Golden-Files neu erzeugen. Betrifft die Änderung Rmin/Rmax, kMax, Astausblendung,
  Klassifizierung oder die Arm-/Stern-Abschnitte der Anleitung, auch `gen-golden.mjs`
  anpassen: Diese Werte stecken unexportiert in der Komponente und sind dort nachgebaut.
- Die Reihenfolge der Kanten und Stiche ist fachlich entscheidend (Stichweg) und darf nie
  unabsichtlich geändert werden. Golden-Tests müssen grün bleiben.
- Bewusst tolerierte Abweichungen (JS-`hypot`/`atan2` vs. Apple-libm, nur bei exakten
  Gleichständen): Klassifizierung eines Punkts, dessen Nachbarabstand exakt auf der Schwelle
  liegt, und die Lage von RS-Bögen, Zahlenkreisen und Beschriftungen in den Diagrammen.
  Nicht darüber hinaus aufweichen; Knoten, Kanten, Stichfolge und Statistik sind exakt.
- Das Lochmuster-PDF ist maßstabsgetreu 1:1 (1 mm = 72/25,4 pt), immer Vektor, nie Bild.
  `PDFTests` (Seitenmaße, Lochabstände, gerastertes PDF) müssen bestehen. Rote Tests nie
  abschwächen oder überspringen, erst die Ursache klären.
- Konstanten (Fadenstränge, Loch-Ø, Mindestabstand, Rand 14 mm, Falz 18 mm, Stichlimit 300)
  stehen in Swift zentral in `Stick` (`Constants.swift`). `testConstantsMatchReference`
  hält sie gegen die JSX synchron.
- Keine Daten erheben oder versenden, alles bleibt lokal. Nichts einbauen, was das ändert
  (Analytics, Netzwerkzugriffe), ohne Rückfrage.
- Neue Texte und Fachbegriffe auf Deutsch (VS/RS, Astschicht, Sternschicht, Falz …).

## Arbeitsweise
- Änderungen per Pull Request, nie direkt auf `main`. Kleine Commits. In Sessions den
  vorgegebenen Entwicklungs-Branch verwenden.
- Es gibt keinen lokalen Mac und keinen Simulator. Geprüft wird über GitHub Actions: pushen,
  Log lesen, korrigieren. In der Cloud-Session über die GitHub-MCP-Tools (`actions_list`,
  `get_job_logs`), lokal mit `gh run view --log-failed`.
- UI-Verhalten (Bedienung, Teilen-Menü, AirPrint) ist nur kompiliert, nicht getestet. Vor
  Releases auf einem Gerät prüfen (unsigniertes IPA aus dem Artifact, siehe `ios/README.md`).
- Neue Logik bekommt Tests in `StickCore`. Bei Fehlern erst den Test schreiben.
- Bei Layoutänderungen an den PDFs zusätzlich ansehen: Die CI pusht PNG-Vorschauen auf den
  Branch `ios-ci-previews`.

## Befehle
- Web: `npm install`, `npm run dev`, `npm run build` (keine `package-lock.json`).
- Golden-Files neu erzeugen: `cd ios/tools && npm install && npm run golden`
- iOS-Tests (nur auf einem Mac): `cd ios/StickCore && swift test`. In der CI: Job `core`.
  Mit `STICK_PDF_OUT=<Ordner>` werden die Beispiel-PDFs dorthin geschrieben.
- App bauen: `cd ios && xcodegen generate && xcodebuild build -project Stickkarten.xcodeproj
  -scheme Stickkarten -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO`

## Veröffentlichung (noch nicht eingerichtet)
- Geplant: zuerst privat über TestFlight (intern). Dafür fehlen Apple-Developer-Zugang,
  eigene Bundle-ID (aktuell Platzhalter `de.stickkarten.app`) und CI-Signing, siehe
  `ios/README.md`.
- Zertifikate, Schlüssel und Tokens nur als GitHub-Secrets, nie im Repo.
