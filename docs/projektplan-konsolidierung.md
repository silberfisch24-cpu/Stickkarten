# Projektplan: Branch-Konsolidierung und Vorbereitung der UI-Umsetzung

Stand: 4. Oktober 2026 · Grundlage: Code-Analyse aller Branches des Repos `silberfisch24-cpu/Stickkarten`
Ziel: (1) alle Arbeitsstände sauber in `main` zusammenführen, (2) die UI aus `claude/ui-grundanalyse`
(`docs/ui-konzept/`) so vorbereiten, dass die Umsetzung in `ios/App` ohne Überraschungen starten kann.

---

## 1 Befund: Branch-Landkarte

| Branch | Stand | Inhalt | Verhältnis zu `main` |
|---|---|---|---|
| `main` (= `claude/hopeful-maxwell-kvpae5`) | `ee33a6a` | Web-App (Vite/React, `src/StickkartenGeneratorV4.jsx`, 1675 Zeilen), Pages-Deploy, `package-lock.json`, **neu:** Ein-Klick-PDF-Export (jsPDF, html2canvas, svg2pdf.js) | – |
| `claude/friendly-bell-9n9w83` | `94b6813` | **Native iOS-App** `ios/` (StickCore-Port, StickPDF, SwiftUI-App, XcodeGen, Golden-Tests), `ios.yml`, `CLAUDE.md` (Projektregeln), 43 Dateien / ca. 4300 Zeilen | 11 Commits voraus, 6 zurück. Abzweig vor Deploy-Workflow und PDF-Export |
| `claude/ui-grundanalyse` | `9b0a463` | friendly-bell-Stand (ohne `CLAUDE.md`) **plus** `docs/ui-grundanalyse.md` und `docs/ui-konzept/` (Konzept, Gesamtreview, Abwärtskompatibilität, 111 PNG, 111 HTML-Boards, `canvas.json`, 31 Python/JS-Skripte, insgesamt 11,7 MB) | Reine Obermenge von friendly-bell bis auf `CLAUDE.md`. Code unter `ios/` ist identisch |
| `ios-ci-previews` | `ee2a348` | Orphan-Branch (keine gemeinsame Historie), 24 PNG-Vorschauen der CI-PDFs, wird von `ios.yml` bei jedem Push **force-gepusht** | nicht mergebar, nicht gedacht dafür |

Beziehung der Branches:

```
main ──────────────────────────────● ee33a6a (Deploy-Fix, .gitignore, PDF-Export)
   \
    └─ friendly-bell ── ios/ ── CLAUDE.md (94b6813)
            └─(Merge 8d07b05)─ ui-grundanalyse ── docs/ui-grundanalyse + docs/ui-konzept
```

### 1.1 Was im Probelauf geprüft wurde

Ein Scratch-Merge von `main` mit `friendly-bell` und mit `ui-grundanalyse` ergab:

| Prüfung | Ergebnis |
|---|---|
| Merge-Konflikte | Genau **einer**: `.gitignore` (beide Seiten haben die Datei neu angelegt). Lösung: Vereinigung beider Inhalte. `package.json`, `deploy.yml` und JSX mergen automatisch und behalten den Stand von `main` |
| Golden-Files neu aus der `main`-JSX erzeugt (`npm run golden`, ca. 640 Konfigurationen) | **0 geänderte Dateien.** Der PDF-Export in `main` hat die Fachlogik nicht berührt |
| `npm ci && npm run build` (Web) auf dem Merge-Stand | grün |
| `swift test`, `xcodebuild` | **nicht prüfbar** (kein Mac in dieser Umgebung). Läuft erst in der CI |

Konsequenz: Die Zusammenführung ist technisch unkritisch. Die eigentliche Arbeit liegt in den
inhaltlichen Widersprüchen (Abschnitt 2).

---

## 2 Analyse: Widersprüche und Lücken

### 2.1 Konsolidierung (Repo-Hygiene)

| # | Fund | Wirkung | Maßnahme |
|---|---|---|---|
| K1 | `CLAUDE.md` nennt „keine `package-lock.json`“, `main` hat inzwischen eine (und `deploy.yml` nutzt `npm ci`) | Falsche Regel für künftige Sessions | In `CLAUDE.md` korrigieren |
| K2 | `friendly-bell` hat die **alte** `deploy.yml` (Node 20, `npm install`) und altes `package.json` (ohne jsPDF) | Bei falscher Konfliktlösung würde der Pages-Deploy oder der PDF-Export zurückgedreht | Beim Merge immer `main`-Stand behalten (Scratch-Merge bestätigt, dass Git das automatisch tut) |
| K3 | `ui-grundanalyse` enthält `ios/` doppelt zu `friendly-bell` | Zwei Merges derselben Dateien | Erst `friendly-bell` mergen, danach bleibt für `ui-grundanalyse` nur `docs/` übrig |
| K4 | `docs/ui-konzept/werkzeuge/*.py` enthalten feste Pfade der Entwurfs-Sitzung (`/tmp/claude-0/...`) und sind „keine Produktivwerkzeuge“ | 31 Wegwerfskripte im Hauptzweig | Mitnehmen (Nachvollziehbarkeit), aber in der Doku klar als Archiv kennzeichnen. Alternative: nur `bilder/`, `konzept.md`, `gesamtreview.md`, `canvas.json` übernehmen und Boards/Werkzeuge im Branch lassen |
| K5 | `ios.yml` pusht per `git push -f` auf `ios-ci-previews` (Schreibrecht `contents: write`) | Orphan-Branch wächst nicht, ist aber ein Dauerzustand | Beibehalten, bis die Screenshot-Prüfung (Phase 1) die PDF-Vorschauen als Artifact liefert. Dann Branch und Schritt entfernen |
| K6 | Branch-Leichen nach dem Merge: `friendly-bell`, `ui-grundanalyse`, `hopeful-maxwell` | Unübersichtlich | Nach erfolgreichem Merge löschen. Das Design-Artifact (`claude.ai/artifact/Wdgor4wDnKDuDFM3iv1X31`) bleibt davon unberührt |

### 2.2 Konzept gegen Code: inhaltliche Widersprüche

| # | Fund | Quelle | Auswirkung |
|---|---|---|---|
| **W1** | **Referenzregel gegen Kernumbau.** `CLAUDE.md`: „Web-App ist die Referenz, Golden-Tests müssen grün bleiben.“ Das Konzept verlangt aber einen Kernumbau (Ebenen als Eigenschaft der Grundform, Löcher nur wo benutzt, Abstandsprüfung nur für benutzte Punkte, Fraktal entfernen). Das ändert Knoten, Klassifizierung und Stichzahlen und bricht die Golden-Tests gegen die JSX | `konzept.md` §8 gegen `CLAUDE.md` | Größte Entscheidung des Projekts → **Entscheidung D1** |
| W2 | Mindest-iOS: `ios/project.yml` hat `deploymentTarget iOS 16.0`, Analyse und Konzept legen **iOS 17** fest (`@Observable`, `sensoryFeedback`). `AppModel` nutzt noch `ObservableObject` | `project.yml`, `ui-grundanalyse.md` E9 | Anheben und migrieren. Teil von Phase 3 |
| W3 | Liquid Glass (`glassEffect`) braucht den iOS-26-SDK, also eine neue Xcode-Version auf dem Runner. Ob `macos-latest` sie hat, ist ungeprüft. Ohne passenden SDK lässt sich `#available(iOS 26, *)` nicht kompilieren | `abwaertskompatibilitaet.md` | In Phase 1 prüfen (`xcodebuild -version` steht schon im Job). Falls nötig, Xcode-Version im Workflow wählen |
| W4 | **Aufwand-Tabelle ist in sich unstimmig:** „Flocke Aufwendig“ hat 70 Stiche, „Flocke Mittel“ aber 80. Aufwendig ist also leichter als Mittel, obwohl die Stufen über die Stichzahl (50 / 80 / 110) definiert sind. Reine Sterne (6 / 20 / 28 Stiche) liegen weit unter den Schwellen | `konzept.md` §6.1 | Muster neu festlegen und gegen den echten Kern rechnen (Phase 2) |
| W5 | **Alle Konzeptzahlen stammen aus einem Python-Nachbau** (`pat.py`), nicht aus dem Swift-Kern. Nur 9 von 27 festen Mustern sind überhaupt gerechnet. Die 10 „fertigen Muster“ sind Platzhalter | `gesamtreview.md` §5 | Katalog-Test gegen `StickCore` (Stichzahl, Mindestabstand, keine Warnung) als Abnahmekriterium |
| W6 | Das Ebenen-Modell („Sterne auf jeder Ebene, auch ohne Äste“) widerspricht der heutigen Logik, in der `sternEbene` nur mit Astschicht wirkt und der Ring immer vollständig gesetzt wird | `konzept.md` §4, `Graph.swift` | Teil des Kernumbaus. Muss exakt spezifiziert werden, bevor Code entsteht (Phase 2, AP 2.1) |
| W7 | Fraktal: Das Konzept streicht es („im Kern nicht funktionsfähig“). Der Kern hat es aber, und 120 Golden-Fälle (`fraktal.json`) prüfen es gegen die JSX. Der Port zeigt außerdem Fraktal-Regler, die die Web-App nicht hat | `konzept.md` §1, `README` ios | In UI und Persistenz sofort weglassen. Entfernung im Kern erst nach D1 |
| W8 | Konzept-Lücken laut eigenem Gesamtreview: gegenseitige Reglerbegrenzungen (Zustand „Wert angepasst / nicht wählbar, weil …“) **nicht gezeichnet**, Anleitung (4 PDF-Seiten) **nicht gestaltet**, kleine Geräte (320/375 pt) und Split View halb nicht gezeichnet, Bild-Export-Platz fehlt, Impressum fehlt | `gesamtreview.md` §2–3 | Als Design-Nachlauf in Phase 4 und 5 einplanen |
| W9 | Designschriften Newsreader und IBM Plex Sans sind nicht eingebunden (PNGs zeigen Ersatzschrift) | `ui-konzept/README.md` | Lizenz prüfen (beide OFL), als Ressourcen ins Bundle, Phase 3 |
| W10 | Die heutige App (`ios/App`, ca. 720 Zeilen: TabView Vorschau/Muster, Sheets für Einstellungen und Export) entspricht dem neuen Konzept nicht. Es ist ein **Neubau der UI-Schicht**, kein Umbau. `StickCore` und `StickPDF` bleiben | `ContentView.swift` | Wiederverwendbar: `PreviewCanvas` (Zeichnung), `ExportView`-Logik (Teilen/AirPrint), Persistenz-Muster |
| W11 | Persistenz: heute ein Schlüssel `stick.settings.v1` in `UserDefaults`. Das Konzept braucht Arbeitsstand + Favoriten (max. 24) + Einstellungen + Erststart-Flag | `AppModel.swift`, `konzept.md` §9 | Schema v2 mit Migration von v1 (Phase 3) |
| W12 | Keine Prüfung des Layouts möglich (E5 offen). Das Gesamtreview nennt das „die größte offene Voraussetzung“ | `ui-grundanalyse.md` §8 | Phase 1, **vor** jeder Screen-Arbeit |

---

## 3 Entscheidungen, die vor dem Start fallen müssen

| # | Frage | Empfehlung | Warum |
|---|---|---|---|
| **D1** | Wer ist nach dem Kernumbau die fachliche Referenz? | **Web-App einfrieren** (bleibt als Legacy deployt, keine Logikänderungen mehr). Der Swift-Kern wird Referenz. Die bestehenden Golden-Tests laufen weiter gegen den Legacy-Pfad, bis der neue Pfad steht. Danach neue Tests: Eigenschaftstests plus Katalog-Test plus Snapshots aus dem Swift-Kern. `CLAUDE.md` entsprechend ändern | Der Umbau ändert die Fachlogik absichtlich. Golden gegen die JSX hielte ihn auf. Die Web-App weiterzuentwickeln verdoppelt den Aufwand für ein Produkt, das das Konzept gar nicht mehr vorsieht |
| **D2** | Kernumbau als **neuer Modus** (Legacy bleibt erreichbar) oder als **Ersatz**? | Zunächst **Modus** (`LayerModel.legacy` / `.ebenen`), nach grünen Katalog-Tests Legacy entfernen | Golden bleiben bis dahin gültig, Rückfall ist möglich, kleine Reviews |
| **D3** | Mindest-iOS 17 beibehalten? | Ja (wie festgelegt). `project.yml` auf 17 | Reichweite ≥ 90 % laut Recherche. iOS 18 nur, wenn der Code dadurch deutlich einfacher wird |
| **D4** | Umfang von `docs/ui-konzept` im Hauptzweig | `konzept.md`, `gesamtreview.md`, `abwaertskompatibilitaet.md`, `bilder/`, `canvas.json` ja. `boards/` und `werkzeuge/` als Archiv-Unterordner mitnehmen, in der README klar als „nur Nachvollziehen“ markieren | Quelle der Wahrheit bleibt im Repo, falls das Artifact verschwindet. 11,7 MB sind unkritisch |
| D5 | Verteilung (E1), Bundle-ID, Signing, Impressum | **Nicht jetzt.** Blockiert weder Konsolidierung noch UI-Bau | Erst vor TestFlight nötig (Phase 7) |

D1 und D2 bestimmen die Reihenfolge in Phase 2. Alles andere hat eine tragfähige Voreinstellung.

---

## 4 Projektplan

Größen: S ≈ ein Arbeitsgang, M ≈ mehrere, L ≈ größerer Block. Jede Phase endet mit einem Pull Request
nach `main` (Regel aus `CLAUDE.md`: nie direkt auf `main`). Prüfung ausschließlich über die CI.

```
Phase 0  Konsolidierung ──► Phase 1  Prüfbarkeit (E5) ──┬─► Phase 2  Kernumbau ──────┐
                                                        └─► Phase 3  Designsystem ───┤
                                                                                     ▼
                                                              Phase 4  Screens ─► Phase 5  Qualität ─► Phase 6  Release
```

Phase 2 und 3 laufen parallel (andere Verzeichnisse: `ios/StickCore` gegen `ios/App`), nur über
eine kleine Schnittstelle gekoppelt (siehe 4.3).

### Phase 0: Konsolidierung (Aufwand M, Voraussetzung für alles)

| AP | Aufgabe | Abnahme |
|---|---|---|
| 0.1 | PR „iOS-App und Projektregeln“: `friendly-bell` nach `main`. `.gitignore` per Vereinigung lösen, sonst `main`-Stand behalten | CI: `core` und `app` grün, Pages-Deploy unverändert, Web-Build grün |
| 0.2 | `CLAUDE.md` korrigieren (K1: Lockfile, `npm ci`). D1/D2 vorläufig als Hinweis eintragen | Review |
| 0.3 | PR „UI-Konzept und Design“: `ui-grundanalyse` nach `main` (nach 0.1 nur noch `docs/`, rein dokumentarisch). `docs/ui-konzept/README.md` um Archiv-Hinweis (K4) und Verweis auf diesen Plan ergänzen | Merge ohne Konflikt, kein iOS-CI-Lauf nötig (Pfadfilter) |
| 0.4 | Branches `friendly-bell`, `ui-grundanalyse`, `hopeful-maxwell` löschen. `ios-ci-previews` bleibt (K5) | Nur `main` und `ios-ci-previews` übrig |
| 0.5 | Diesen Plan einchecken (liegt schon in `docs/projektplan-konsolidierung.md`) | Review durch Auftraggeber, **D1–D4 beantwortet** |

Risiko: gering. Reihenfolge 0.1 vor 0.3 einhalten, sonst liegt `ios/` doppelt im Diff.

### Phase 1: Prüfbarkeit ohne Mac (E5) (Aufwand M)

Ohne Screenshot-Prüfung bleibt jede Layoutaussage eine Vermutung (Q7). Deshalb zuerst.

| AP | Aufgabe | Abnahme |
|---|---|---|
| 1.1 | Xcode- und SDK-Version des Runners feststellen (W3). Falls iOS-26-SDK fehlt: Xcode im Workflow auswählen oder Glas nur per Fallback bauen | Ergebnis in `ios/README.md` |
| 1.2 | Neuer CI-Job `screens`: Simulator starten, App mit Startargument in einen Zustand versetzen (Screen, Gerät, Schriftgröße, Hell/Dunkel), Screenshot ablegen, als Artifact hochladen | Artifact mit Bildern erscheint je PR |
| 1.3 | Matrix: iPhone SE (375), iPhone 16 (393), iPhone Pro Max (440), iPhone quer, iPad 11″ hoch/quer, iPad 13″, Slide Over; Dynamic Type Standard/größte Stufe; Hell/Dunkel | Matrix deckt die in `gesamtreview.md` §2 als „nicht gezeichnet“ geführten Fälle ab |
| 1.4 | Vergleichsbasis: Konzept-PNGs in `docs/ui-konzept/bilder` als Soll, Screenshots als Ist, nebeneinander im Artifact (zunächst ohne automatischen Pixelvergleich) | Sichtprüfung möglich |
| 1.5 | `ios-ci-previews`-Schritt ablösen, PDF-Vorschauen als Artifact (K5) | Orphan-Branch kann gelöscht werden |

Hinweis: Dies prüft Layout und Zustände. Haptik, Gesten, Antwortzeit und Maßhaltigkeit des Drucks
bleiben Gerätetest und Probedruck (Phase 5).

### Phase 2: Kernumbau (Aufwand L, hängt an D1/D2)

| AP | Aufgabe | Abnahme |
|---|---|---|
| 2.1 | Spezifikation des Ebenen-Modells (W6) als kurzes Dokument mit Beispielen: Raster n × Ebenen, wann entsteht ein Loch, welche Punkte zählen für die Abstandsprüfung, Wirkung auf Stern-Ebene ohne Äste | Review, bevor Code entsteht |
| 2.2 | `LayerModel` in `StickCore` (Modus nach D2), Legacy-Pfad unverändert | Alte Golden-Tests unverändert grün |
| 2.3 | Neue Tests für den Ebenen-Modus: Eigenschaften (Kantenreihenfolge, Stichfolge ist durchgehender Weg, jeder Stich gefolgt von Sprung, Abstand nur für benutzte Punkte), Snapshots aus dem Swift-Kern | grün in CI |
| 2.4 | **Musterkatalog** (`Katalog.swift`): feste Parametersätze, 3 Stile × 3 Stufen × 3 Varianten = 27, plus die 10 fertigen Muster. W4 beheben (Stufen nach Stichzahl ordnen). Test: Stichzahl in Stufenband, kleinster Abstand ≥ 1,5 × Mindestabstand, `severity == ok`, `!hasCritical`, Farbzahl je Stufe | Alle 27 grün gegen den **echten** Kern (W5) |
| 2.5 | Aufwand-Zuordnung (Stil + Stufe + Variante → Parameter) als reine Funktion für den Geführten Weg | Test: jede Kombination liefert ein gültiges Muster |
| 2.6 | Fraktal: aus Persistenz und UI entfernen. Kern-Entfernung nach D1 entscheiden (W7) | Entscheidung dokumentiert |
| 2.7 | **Kompakt-PDF** in `StickPDF`: eine A4-Seite (Lochmuster 1:1, Übersicht mit Strichstilen je Schicht, Einstellungsband, QR-Platzhalter), Fall „Kompakt nicht verfügbar“. Anleitung (4 Seiten) auf Konzept anpassen | `PDFTests` (Seitenmaß, Lochabstand, Rasterprüfung) grün, Sichtprüfung der Vorschau-PNG |
| 2.8 | Eigenformat-Begrenzung (E8): Validierung „Zuschnitt passt mit 10 mm Rand auf A4“ im Kern | Unit-Tests der Grenzfälle (A5 gefaltet fällt heraus) |

Unveränderliche Regeln aus `CLAUDE.md` gelten weiter: Kantenreihenfolge nie unabsichtlich ändern,
PDF immer Vektor und 1:1, rote Tests nie abschwächen.

### Phase 3: Designsystem und App-Gerüst (Aufwand L, parallel zu Phase 2)

| AP | Aufgabe | Abnahme |
|---|---|---|
| 3.1 | `deploymentTarget` auf iOS 17, `AppModel` auf `@Observable` (D3, W2) | Build grün |
| 3.2 | Modul `Design`: Farben (Akzent `#1f5a4b`, Inhalt `#f4f0e6`, Arbeitsfläche `#e9e4d6`, Warnung/Kritisch/OK-Paare mit Dunkel-Varianten), Maße (Radien 22/34, Kapsel 44, Haupt 56–68, Rand 16, Abstände 8/10/12), Schriften (Newsreader, IBM Plex Sans einbinden, W9), Symbole | Katalog-Screen „Designsystem“ rendert in der Screenshot-Matrix |
| 3.3 | Material-Funktionen mit Rückfall: `glass()`, `sheetBackground()` mit `#available(iOS 26, *)` (siehe `abwaertskompatibilitaet.md`) | Screenshots auf iOS 17/18 und 26 |
| 3.4 | Bausteine: Glas-Kapsel, runder Glas-Button, Kachel (Rahmen 3 pt, Höhe 140/190), Umschalter, Regler mit Wertanzeige, Zähler ±, Meldungszeile (einzeilig), Dialoge, Panel (iPad) / Sheet mit 3 Stufen (iPhone) | Katalog-Screen vollständig, jede Komponente mit Dynamic Type und Dunkel |
| 3.5 | Zeichnung der Karte: `PreviewCanvas` zu `KartenView` weiterentwickeln (Pinch/Pan, Marker größer als maßstäblich, Form + Text statt nur Farbe, VoiceOver-Beschreibung) | Screenshots, Gesten nur Gerätetest |
| 3.6 | Persistenz v2: Arbeitsstand, Favoriten (≤ 24, neueste zuerst, Name „Muster n“), Einstellungen, Erststart-Flag. Migration von `stick.settings.v1` | Unit-Tests der Migration und der Favoritenregeln |
| 3.7 | Texte in String-Katalog (`Localizable.xcstrings`), Deutsch (E12) | Keine Literale in Views |
| 3.8 | Navigationsgerüst: Tab-Leiste (iPhone) / Seitenleiste (iPad) mit Start, Gestalten, Ausgabe, Mehr, Kapsel „Weitermachen“, Größenklassen-gesteuert (nicht gerätetypgesteuert) | Screenshot-Matrix zeigt Gerüst auf allen Breiten |

Schnittstelle zu Phase 2 (damit beide parallel arbeiten können): ein Protokoll `PatternProviding`
(Einstellungen → `StickResult`, Katalog, Aufwand-Zuordnung). Phase 3 entwickelt gegen den
Legacy-Kern, Phase 2 tauscht die Implementierung später aus.

### Phase 4: Screens (Aufwand L, hängt an Phase 1, 2.4, 3)

Reihenfolge nach Risiko und Abhängigkeit, jeweils ein PR:

| AP | Screen | Wesentlicher Inhalt | Abhängigkeit |
|---|---|---|---|
| 4.1 | **Editor** | Karte als Bühne, Sheet 3 Stufen (iPhone) / Panel (iPad), 5 Gruppen, Live-Meldungen, Zustand „kritisch“, Zurücksetzen mit Rückfrage, Favorit-Stern, Eigenformat unter „Erweitert“ | 3.x, 2.2 für Ebenen |
| 4.2 | **Reglerbegrenzungen** (Lücke W8) | Zustand „Wert angepasst“ / „nicht wählbar, weil …“ für Schrittweite, Sternebene, Strahlen, Ausblendung. **Erst im Design nachziehen**, dann bauen | Design-Nachlauf |
| 4.3 | **Stichfolge** | 5 Abschnitte, Wiedergabe, Nummerierung nach erster Benutzung, Kennzahlen, abgeblendete leere Abschnitte | 4.1 |
| 4.4 | **Ausgabe** | Kompakt / Lochmuster 1:1 / Anleitung, Vorschau, Teilen, AirPrint, Sperre, Fortschritt, Fehler | 2.7 |
| 4.5 | **Geführter Weg** | 6 Schritte, Live-Vorschau, feste Varianten, Abbruchdialog, Ergebnis wird „Letzter Stand“ | 2.4, 2.5 |
| 4.6 | **Start, Favoriten, Fertige Muster** | Kachelraster, Vorschaubilder aus dem Kartenmodell mit Cache, Muster-Detail, Menü per Langdruck | 2.4, 3.6 |
| 4.7 | **Mehr** | Einführung (3 Seiten), Hilfe (5 Themen), Glossar mit Suche, Einstellungen, Info/Datenschutz, „Alles zurücksetzen“ | Texte |
| 4.8 | **Anleitung (4 Seiten) gestalten** (Lücke W8) | Design festlegen, dann `StickPDF` | Design-Nachlauf |

Eine Empfehlung für die Reihenfolge: **4.1 zuerst als vertikaler Durchstich** (Editor mit echtem Kern,
Screenshot-Matrix, Gerätetest). Das ist laut Gesamtreview „der schwerste Punkt“. Alles Weitere baut
auf demselben Fundament.

### Phase 5: Qualität (Aufwand M–L)

| AP | Aufgabe |
|---|---|
| 5.1 | Barrierefreiheit: VoiceOver-Reihenfolge und -Texte für Karte/Diagramme, Regler als einstellbar (±1), nicht nur Farbe |
| 5.2 | Dynamic Type und Dunkel für **alle** Screens (nicht nur je ein Beispiel), Kontrast messen |
| 5.3 | Kleine Geräte (320/375 pt), Split View halb, Tastatur (Eigenformat) |
| 5.4 | Performance: Live-Neuberechnung beim Reglerziehen messen (älteres iPhone, größtes Muster), Vorschaubilder cachen |
| 5.5 | Zustandserhalt: Rotation, Fensterwechsel, App-Neustart (Q5) |
| 5.6 | **Gerätetest und Probedruck** des Lochmusters (50-mm-Kontrollbalken nachmessen). Nur so ist die Maßhaltigkeit belegt |

### Phase 6: Release-Vorbereitung (Aufwand M, erst nach D5)

Verteilungsweg (E1), Apple-Developer-Zugang, eigene Bundle-ID (heute Platzhalter `de.stickkarten.app`),
CI-Signing über GitHub-Secrets, Privacy-Manifest (UserDefaults), Datenschutztext, Impressum, Symbol,
TestFlight intern. Nichts davon blockiert die Phasen davor.

---

## 5 Risiken

| Risiko | Wahrscheinlichkeit | Gegenmaßnahme |
|---|---|---|
| Kernumbau verändert Stichfolgen unbeabsichtigt | mittel | Modus statt Ersatz (D2), Legacy-Golden bleiben, Eigenschaftstests |
| Konzeptzahlen halten dem echten Kern nicht stand (W4, W5) | hoch | Katalog-Test als hartes Abnahmekriterium in 2.4 |
| Runner-Xcode zu alt für Glas-APIs (W3) | mittel | Prüfung in 1.1, Rückfall-Material ist ohnehin Pflicht |
| Layout ist ohne Mac nur über Screenshots beurteilbar | sicher | Phase 1 vor Phase 4. Gerätetest als Abschluss |
| Echtes Liquid Glass sieht anders aus als die HTML-Nachahmung | sicher | Boards sind Spezifikation, nicht Nachweis. Abweichungen im Screenshot-Vergleich bewerten, nicht pixelgenau nachbauen |
| Ein einzelner großer PR für die UI | mittel | Ein PR je Arbeitspaket aus Phase 4, kleine Commits |
| CI-Minuten (macOS-Runner) | niedrig | `ios.yml` ist per Pfadfilter auf `ios/**` begrenzt. Screenshot-Matrix nur bei PR, nicht bei jedem Push |

---

## 6 Nächste Schritte

1. D1–D4 klären (Abschnitt 3). Ohne Antwort gelten die Empfehlungen.
2. Phase 0 starten: PR für `friendly-bell`, danach `ui-grundanalyse`. Das ist mechanisch und
   im Probelauf konfliktarm.
3. Parallel Phase 1 vorbereiten (Xcode-Version des Runners feststellen).
4. Design-Nachlauf (W8: Reglerbegrenzungen, Anleitung, kleine Geräte) vor Phase 4.2 und 4.8 ansetzen.
