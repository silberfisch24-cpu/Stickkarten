# Projektplan v2: Neuportierung der iOS-App nach dem UI-Konzept

Stand: 4. Oktober 2026 · ersetzt Version 1 (Konsolidierung + Umbau der ersten Portierung)

## 0 Ausgangslage und Richtungsentscheid

Herkunft: Web-App <https://silberfisch24-cpu.github.io/Stickkarten/> (`main`, `src/StickkartenGeneratorV4.jsx`).

1. **Erste Portierung** (`claude/friendly-bell-9n9w83`): Testlauf, die Web-App in eine iOS-App zu
   wandeln. Entstanden **vor** jeder UI-Arbeit. Ergebnis: brauchbarer Kern (`StickCore`, `StickPDF`,
   Golden-Tests gegen die Web-App) und eine UI, die dem Konzept nicht entspricht.
2. **UI-Arbeit** (`claude/ui-grundanalyse`): Analyse, Konzept und Design-Artifact. Sie ist ab jetzt die
   **Referenz für Aussehen und Bedienung** und bestimmt, welche Funktionen im Code angepasst werden.
3. **Entscheid (4. Okt.):** iOS-Portierung wird **neu durchgeführt**, mit dem UI-Konzept von Beginn an.
   Die erste Portierung wird als **Archiv-Branch** gesichert. **Mindest-iOS 17.** Layout wird erst später
   im Projekt getestet. Ein MacBook steht nur eingeschränkt zur Verfügung.

Was „Aufwand“ im Konzept bedeutet: Der **Geführte Weg** legt vorbereitete Entwürfe hinter wenige
Entscheidungen. Nutzer wählen Format, Stil, Aufwand (einfach/mittel/aufwendig) und Farben und erhalten
schnell **schöne**, sofort druckbare Ergebnisse. Aufwand ist also eine Abschätzung, die Muster
einordnet, kein Eingabewert.

---

## 1 Branch-Befund (unverändert gültig)

| Branch | Rolle künftig |
|---|---|
| `main` | Web-App (Legacy, bleibt deployt, wird nicht mehr weiterentwickelt) + Neuportierung |
| `claude/friendly-bell-9n9w83` | → **`archive/ios-port-v1`** (Steinbruch, nicht mehr gemergt) |
| `claude/ui-grundanalyse` | → Konzept und Boards nach `main` (`docs/`), dann löschen |
| `ios-ci-previews` | Orphan, von der CI force-gepusht. Entfällt mit dem Archiv |
| `claude/hopeful-maxwell-kvpae5` | Arbeitsbranch dieser Sitzung (= `main` + dieser Plan) |

Probelauf (Scratch-Merge) bleibt gültig: ein einziger Konflikt (`.gitignore`), Golden-Files aus der
`main`-JSX erzeugt ergeben 0 Änderungen, Web-Build grün. Das ist jetzt nur noch relevant, weil das Archiv
den Kern liefert.

### Was aus dem Archiv übernommen wird (Empfehlung)

Neuportierung heißt: **neue App-Schicht, neue Struktur, UI-Konzept als Grundlage.** Den Kern
(`StickCore`, `StickPDF`, ca. 1800 Zeilen Swift ohne Tests) schreiben wir nicht noch einmal. Er ist gegen die
Web-App in rund 640 Fällen bit-genau geprüft. Er wird als Ausgangsbasis in die neue Struktur kopiert
und dann gezielt umgebaut. Verworfen wird die alte UI (`ios/App`, ca. 720 Zeilen). Wiederverwendbar
daraus: die Kartenzeichnung (`PreviewCanvas`), Teilen/AirPrint (`ExportView`).

Begründung: Eine Neuschreibung des Kerns kostet viel und verliert die einzige Absicherung gegen die
Web-App. Wer ihn dennoch frisch schreiben will, kann es tun. Die Golden-Tests bleiben dann das
Abnahmekriterium.

---

## 2 Antwort auf die Frage: müssen die UI-Lücken jetzt geschlossen werden?

**Nein, nicht als Zeichnung. Aber vier Dinge müssen von Anfang an im Code angelegt sein**, weil sie
sonst später Umbauten erzwingen. Der Rest kann nachgeschoben werden.

### Jetzt vorsehen (Architektur, kein Design)

| Lücke laut Gesamtreview | Was jetzt schon im Code stehen muss | Zeichnung |
|---|---|---|
| **Gegenseitige Reglerbegrenzungen** (Schrittweite, Sternebene, Strahlen, Ausblendung hängen voneinander ab) | Die Regler-Komponente kennt die Zustände *normal / angepasst / deaktiviert mit Grund* und bekommt „wirksamer Wert“ und „Grund“ vom Kern (der Kern liefert die Werte bereits: `k1Eff`, `sternEbeneEff1`, `kMax1` …). Der Editor wird um diese Komponente herum gebaut | Optik **nachschieben**, Platzhalter-Stil genügt |
| **Dynamic Type, Hell/Dunkel** auf allen Screens | Nur Design-Tokens und Text-Styles, nie feste Größen oder Farben. Kostet beim ersten Schreiben nichts, nachträglich viel | Prüfen später |
| **Breiten-/Höhenabhängigkeit** (kleines iPhone, Querformat, Split View) | Layout entscheidet nach Größenklasse und gemessener Breite, nie nach Gerätetyp | Prüfen später |
| **Texte, Barrierefreiheit** | String-Katalog von Anfang an, jede Grafik mit Beschreibungstext, Regler einstellbar (±1) | Texte später füllen |

### Nachschieben (eigene Arbeitspakete, blockieren nichts)

| Lücke | Wann |
|---|---|
| Anleitung (4 PDF-Seiten) gestalten. Der Kern erzeugt bereits eine Anleitung, sie ist nur nicht im neuen Look | nach Ausgabe-Screen |
| Kleine Geräte 320/375 pt, Split View halb, iPad 13″ | Layout-Testphase |
| Platz für Bild-Export in der Ausgabe | trivial, später |
| Impressum, Datenschutz, Verteilung (E1) | vor TestFlight |
| Kartengesten (Pinch/Pan), automatisches Hinzoomen auf Problemstellen | im Editor, Gerätetest |
| Endgültige Texte für Einführung, Hilfe, Glossar, Namen der fertigen Muster | Inhaltsschritt |

Faustregel: Eine Lücke wird nur dann vorab geschlossen, wenn sie die **Schnittstelle einer
Komponente** verändert. Ist es nur Optik oder Inhalt, wird sie später ergänzt.

---

## 3 Der Geführte Weg und die vorbereiteten Entwürfe

### 3.1 Gedanke

Statt Zufall oder freier Eingabe: ein **Generator im Projekt** (Werkzeug, nicht in der App) erzeugt je
Auswahlweg viele Kandidaten, bewertet sie und liefert die besten für die Auswahl. Die ausgewählten drei
je Weg werden als feste Parametersätze in die App eingebaut („ready-to-use“, nie „kritisch“).

```
Parameterraum ──► Kandidaten (≈50 je Weg) ──► harte Filter ──► Schönheitsmaß ──► Rangliste ──► Kontaktbogen ──► 3 Gewinner ──► Katalog in der App
   (Kern)           reproduzierbar (Seed)       gültig, druckbar     Heuristik      Top 50        (PNG/PDF)      Sichtprüfung      Test gegen den Kern
```

Ein **Weg** ist eine Kombination aus Format/Falz × Stil (Flocke, Stern, Beides) × Aufwand (leicht, mittel,
aufwendig). Das sind laut Konzept 3 × 3 = 9 Zellen je Format, je Zelle 3 Varianten = 27 Muster. Ob Farbwelt
und Format den Parametersatz verändern, ist zu klären (siehe 6): Farben sind rein visuell, das
Format ändert nur den Musterradius.

### 3.2 Aufwand definieren („was versteht man unter einfach, mittel, schwierig?“)

Das Konzept setzt Stichzahl (≈ 50 / 80 / 110) und Farben (1 / 2 / 3). Das hat Schwächen: Reine Sterne haben
wenige Stiche, aber lange Fäden. Im Konzept ist „Flocke aufwendig“ (70 Stiche) leichter als „Flocke mittel“
(80). Vorschlag für ein belastbares Maß, im Generator als Funktion, einmalig festzulegen:

| Größe | Aussage über den Aufwand | Quelle im Kern |
|---|---|---|
| Stichzahl | Dauer | `stitchCount` |
| Fadenlänge | Material, Handhabung | `fadenCm` |
| Zahl der Schichten / Fadenfarben | Fadenwechsel | Einstellungen |
| Engste Stelle | Fingerfertigkeit (kleiner Abstand = schwierig) | kleinster Lochabstand |

Daraus ein Aufwandsindex mit zwei Schwellen. **Stufen werden also gerechnet, nicht von Hand zugeordnet.**
Die Schwellen (heute 50/80/110 Stiche) bleiben Vorgabe des Auftraggebers und werden gegen die anderen
Größen geprüft. Offene Entscheidung dazu in Abschnitt 6.

### 3.3 Harte Filter (nie verhandelbar)

- `formatOk`, kein `critical`, **kein `moderate`** (keine Warnung)
- Stichzahl innerhalb der Stufe und unter dem Stichlimit 300
- Kleinster Abstand ≥ 1,5 × Mindestabstand (4,8 mm), damit auch die Warnschwelle nicht berührt wird
- Passt auf A4 (Kompakt-PDF möglich)
- Keine Duplikate (gleiche Stichfolge bis auf Drehung/Spiegelung zählt als gleich)

### 3.4 „Schön“ als Heuristik, dann Auge

Schönheit ist nicht berechenbar, aber vorsortierbar. Maße: Symmetrie (immer gegeben bei n-Strahlen, daher
unterscheidend nur bei Mehrschicht-Kombinationen), gleichmäßige Dichte, Flächenfüllung der Karte,
Abwesenheit enger Stellen, Ausgewogenheit der Schichten (Äste/Stern 1/Stern 2), Lesbarkeit der Sterne.
Die Rangliste ist **eine Vorauswahl**, die endgültigen drei wählt ein Mensch. Dafür erzeugt das Werkzeug
einen **Kontaktbogen** (Raster aus Karten, Rang, Stichzahl, Abstand). Die Auswahl der besten drei
je Weg trifft der Auftraggeber (auf dem Bogen als PNG, auch am Handy lesbar). Claude kann die Bilder
ansehen und eine Empfehlung dazu abgeben.

### 3.5 Wiederfinden desselben Musters (entschieden)

Nutzer durchlaufen den Geführten Weg mit bestimmten Angaben, sticken das Muster und wollen es später
auf dem einfachsten Weg wiederholen. Sie gehen erneut durch den Geführten Weg und müssen am Ende bei
**denselben drei vorbereiteten Mustern** ankommen. Folgen:

- Die Zuordnung *(Format, Stil, Aufwand, Farbwelt) → drei Muster* ist **eindeutig und stabil**: feste
  Katalogeinträge mit fester ID und Reihenfolge, kein Zufall, keine zeitabhängige Auswahl.
- Katalogeinträge werden nie umsortiert oder ersetzt. Bei Änderungen kommen neue IDs dazu, alte bleiben
  erhalten (ein später gesticktes Muster muss wiederfindbar bleiben). Test: Katalog-IDs sind eindeutig, die
  Zuordnung ist deterministisch.
- Der größere Katalog (ca. 12 je Weg) dient der **Direktauswahl/Favoriten** (Startseite „Fertige Muster“),
  nicht dem Geführten Weg. Kein Generator in der App.

### 3.6 Warum das den Plan verändert

- Der Kernumbau (Ebenen-Modell) ist **keine Voraussetzung für den Geführten Weg** mehr, nur für den
  freien Editor. Der Generator ist wiederholbar (Seed, Skript): Ändert sich der Kern, lassen sich die
  Entwürfe neu erzeugen.
- Die Konzeptzahlen aus dem Python-Nachbau werden damit **durch echte Kernrechnung ersetzt** (löst die
  Unstimmigkeiten W4/W5 aus Version 1 automatisch).
- Der Generator ist ein Swift-Werkzeug im Kern-Paket (Zielplattform: CI/MacBook), damit er exakt den
  App-Kern verwendet. Kein weiterer Nachbau.

---

## 4 Projektplan

Jede Phase endet mit einem PR nach `main`. Prüfung über die CI. Größen: S, M, L.

```
Phase A  Archivieren, Neustart ─► Phase B  Kern + Designsystem ─┬─► Phase C  Geführter Weg + Katalog
                                                                 └─► Phase D  Editor, Stichfolge, Ausgabe ─► Phase E  Rest ─► Phase F  Layout/Gerät ─► Phase G  Release
```

### Phase A: Archivieren und sauber neu starten (M)

| AP | Aufgabe | Abnahme |
|---|---|---|
| A1 | Branch **`archive/ios-port-v1`** aus `friendly-bell` anlegen. README-Hinweis „Steinbruch, nicht mehr gemergt“ | Branch vorhanden |
| A2 | `docs/ui-grundanalyse.md` und `docs/ui-konzept/` aus `ui-grundanalyse` nach `main` (nur Doku). `boards/` und `werkzeuge/` als Archiv-Unterordner markieren | PR gemergt, kein Code berührt |
| A3 | Neue Struktur auf `main`: `ios/` frisch, Kern aus dem Archiv kopiert (`StickCore`, `StickPDF`, Golden-Tests, `gen-golden`), alte `ios/App` **nicht** übernommen. `project.yml` mit iOS 17 | `swift test` in CI grün (Golden gegen die `main`-JSX) |
| A4 | Neue `CLAUDE.md`: Web-App ist **eingefroren** (Legacy, bleibt für Pages). UI-Referenz ist `docs/ui-konzept`. Lockfile-Fehler korrigieren. Kernumbau-Regeln (siehe 5) | Review |
| A5 | CI: `ios.yml` mit Pfadfilter, Artefakt statt Force-Push auf `ios-ci-previews` | Orphan-Branch entfernbar |
| A6 | Branches `friendly-bell`, `ui-grundanalyse`, `ios-ci-previews`, `hopeful-maxwell` nach Freigabe löschen | nur `main` und `archive/ios-port-v1` |

### Phase B: Fundament (L)

| AP | Aufgabe |
|---|---|
| B1 | **Designsystem**: Farben (inkl. Dunkel-Paare), Maße, Schriften (Newsreader, IBM Plex Sans), Symbole. `glass()`/`sheetBackground()` mit `#available(iOS 26)` und Rückfall für 17/18. Runner-Xcode prüfen (iOS-26-SDK?) |
| B2 | **Bausteine**: Glas-Kapsel, runder Button, Kachel, Umschalter, Regler mit Zuständen *normal/angepasst/deaktiviert mit Grund* (Abschnitt 2), Zähler ±, Meldungszeile, Dialoge, Sheet in drei Stufen, Panel |
| B3 | **App-Zustand** mit `@Observable`: Arbeitsstand, Favoriten (≤ 24), Einstellungen, Erststart. Persistenz mit Versionsfeld. String-Katalog |
| B4 | **Navigation**: Tab-Leiste/Seitenleiste, Kapsel „Weitermachen“, nach Größenklasse |
| B5 | **Kartenansicht** (aus `PreviewCanvas` entwickelt): Marker größer als maßstäblich, Form + Text neben Farbe, VoiceOver-Text |
| B6 | Minimale Screenshot-Ausgabe in der CI (ein Bild je Hauptscreen), damit überhaupt etwas zu sehen ist. Vollständige Matrix erst in Phase F |

### Phase C: Geführter Weg und Katalog (L, das Herzstück laut Auftrag)

| AP | Aufgabe | Abnahme |
|---|---|---|
| C1 | **Aufwandsmaß** festlegen (3.2) und als Funktion im Kern testen | Entscheidung dokumentiert |
| C2 | **Generator** (Swift-Werkzeug): Parameterraum je Weg, Seed, harte Filter, Schönheitsmaß, Duplikatprüfung, Ausgabe als JSON | Läuft in CI, gleicher Seed = gleiches Ergebnis |
| C3 | **Kontaktbogen**: Raster der Top 50 je Weg als PNG/PDF-Artifact | Bogen je Weg im Artifact |
| C4 | **Auswahl** der Gewinner (Mensch, auf dem Bogen), Parametersätze als `Katalog.json` ins Bundle | 27 Muster + 10 fertige Muster |
| C5 | **Test**: jedes Muster gegen den Kern (Stufenband, Abstand ≥ 4,8 mm, ohne Warnung, passt auf A4) | CI grün |
| C6 | **Geführter Weg** (6 Schritte, Live-Vorschau, feste Varianten, Abbruchdialog, Ergebnis wird „Letzter Stand“) | Durchlauf über alle Wege, Test der Zuordnung |

C2 und C3 laufen gegen den **heutigen** Kern. Wird der Kern später umgebaut (Phase D4), rechnet man
neu. Dank Seed ist das Minuten, nicht Tage.

### Phase D: Editor, Stichfolge, Ausgabe (L)

| AP | Aufgabe |
|---|---|
| D1 | **Editor**: Karte als Bühne, Sheet 3 Stufen (iPhone), Panel (iPad), 5 Gruppen, Live-Meldungen, „kritisch“-Zustand, Zurücksetzen, Favorit-Stern, Eigenformat unter „Erweitert“ |
| D2 | Reglerbegrenzungen mit Platzhalter-Optik (Abschnitt 2) |
| D3 | **Stichfolge** (5 Abschnitte, Wiedergabe, Nummerierung, Kennzahlen) |
| D4 | **Kernumbau Ebenen-Modell** (nur für den freien Editor): als Modus neben dem alten Verhalten. Eigenschaftstests. Danach Katalog neu rechnen (C2–C5) |
| D5 | **Ausgabe**: Kompakt-PDF (neu im Kern), Lochmuster 1:1, Anleitung, Vorschau, Teilen, AirPrint, Sperre, Fortschritt, Fehler. Eigenformat-Begrenzung auf A4 (E8) |

D4 ist bewusst nach C gerückt: Der Kern kann vorher bleiben, wie er ist. Das senkt das Risiko.

### Phase E: Rest (M)

Start, Favoriten, Fertige Muster (Vorschaubilder mit Cache), Mehr (Einführung, Hilfe, Glossar,
Einstellungen, Info), Anleitung im neuen Look, Texte füllen.

### Phase F: Layout und Gerät (M–L, wie vom Auftraggeber vorgesehen: später)

Screenshot-Matrix (kleine iPhones, Querformat, iPad hoch/quer, 13″, Slide Over, größte Schrift, Dunkel),
Barrierefreiheit, Performance beim Reglerziehen, Zustandserhalt. **Gerätetest und Probedruck**
(Kontrollbalken 50 mm nachmessen) auf dem MacBook/iPhone. Da das MacBook nur eingeschränkt nutzbar ist,
bleibt die CI das Hauptwerkzeug. Das MacBook ist vor allem für Gerätetest, Druck und gelegentlich Xcode
nötig.

### Phase G: Release (M, erst nach Entscheidung E1)

Verteilung, Bundle-ID, Signing über GitHub-Secrets, Privacy-Manifest, Impressum, TestFlight.

---

## 5 Regeln für den Kern in der Neuportierung

- Die Reihenfolge der Kanten und Stiche ist fachlich entscheidend und ändert sich nie unbeabsichtigt.
- **Golden-Tests gegen die Web-App bleiben bestehen, solange der Legacy-Pfad im Kern existiert.** Der
  Ebenen-Modus (D4) bekommt eigene Tests und ändert den Legacy-Pfad nicht.
- PDF bleibt Vektor, 1:1, mit Maßtests. Rote Tests werden nie abgeschwächt.
- Alles bleibt lokal, keine Daten werden erhoben.

---

## 6 Entscheidungen und Rest

| # | Thema | Stand |
|---|---|---|
| F1 | Kern übernehmen oder neu schreiben | Entscheidung des Auftragnehmers: **übernehmen und umbauen** (sauber, wenig Aufwand) |
| F2 | Wiederholbarkeit | entschieden, siehe 3.5 |
| F3 | Aufwandsmaß (50/80/110 plus Fadenlänge, engste Stelle) | **später**, bei der Arbeit an den Mustern (Phase C1) |
| F4 | Format und Farbwelt im Generator | mit F3 klären |
| F5 | Gewinner wählt der Auftraggeber auf dem Kontaktbogen | ja, **später** (Phase C4) |
| F6 | Bereinigung | ausgeführt, siehe 7 |

## 7 Stand der Bereinigung

- `archive/ios-port-v1` angelegt (erste Portierung samt `CLAUDE.md` und UI-Konzept-Historie).
- UI-Konzept und Analyse nach `main` per PR (`docs/`), dann entfällt `claude/ui-grundanalyse`.
- `claude/friendly-bell-9n9w83` und `ios-ci-previews` gelöscht (Inhalt liegt im Archiv).
- **Web-App und Pages-Deploy bleiben unverändert** (`src/`, `deploy.yml`, `package.json` werden nicht angefasst).
