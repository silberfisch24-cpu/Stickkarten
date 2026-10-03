# Stickkarten-Generator — UI-Grundanalyse (iPhone & iPad)

Status: Entwurf zur gemeinsamen Diskussion · **keine Design-Entscheidungen**, nur Bestandsaufnahme und Anforderungen.
Nächster Schritt (separat): gemeinsames UI-Konzept → danach Design.

## 0. Ausgangslage und Annahmen

**Was die App heute ist:** eine einzelne React-Komponente (`src/StickkartenGeneratorV4.jsx`, ~1600 Zeilen), als Webseite über GitHub Pages ausgeliefert. Sie erzeugt aus Parametern (Kreispunkte, Astschicht, bis zu zwei Sternschichten) ein Lochmuster für eine gestickte Karte, zeigt den Stichablauf animiert, prüft Mindestabstände und erzeugt eine druckbare Anleitung samt 1:1-Lochmuster sowie einen SVG-Export.

**Annahmen (bitte korrigieren, falls falsch):**

- A1. Zielplattform ist **Safari auf iPhone und iPad** (Webapp, ggf. „Zum Home-Bildschirm“), keine native App. Das schlägt sich vor allem in Abschnitt 2 nieder.
- A2. Nutzerin/Nutzer ist eine Person, die von Hand stickt — also **am Tisch mit Karton, Nadel, Faden** — und das Gerät als Vorlage/Hilfe daneben benutzt.
- A3. Die App bleibt **offline-fähig, ohne Konto, ohne Server** (alles rechnet lokal).
- A4. Sprache zunächst nur Deutsch.

**Zwei Nutzungsmodi, die sich im Layout widersprechen** (Hypothese, in Abschnitt 7 als Entscheidung geführt):

| Modus | Situation | Anforderung an die UI |
|---|---|---|
| **Entwerfen** | Parameter ändern, Ergebnis ansehen | große Vorschau + schnell erreichbare Regler |
| **Sticken** | Gerät liegt/steht neben dem Karton, Hände sind belegt | große Schrift, große Tasten, „Nächster Stich“, Display bleibt an, wenig Ablenkung |

---

## 1. Was braucht eine App allgemein?

Checkliste; die letzte Spalte bewertet die Relevanz für *diese* App.

| # | Bereich | Inhalt | Heute vorhanden? | Relevanz |
|---|---|---|---|---|
| 1.1 | **Informationsarchitektur / Navigation** | Wo bin ich, wie komme ich zurück, was ist Haupt- und was Nebenfunktion | Nein — ein Bildschirm plus zwei Overlays | hoch |
| 1.2 | **Onboarding / Hilfe** | Erklärung der Begriffe (Kreispunkt, Ebene, Sternschicht, VS/RS, Schrittweite), Beispielkarte | Nein; Begriffe nur in der Anleitung | hoch |
| 1.3 | **Kern-Workflow** | Entwerfen → Prüfen → Sticken → Drucken/Teilen | Teilweise, ohne geführten Ablauf | hoch |
| 1.4 | **Eingabe** | Regler, Auswahl, Zahlenfelder, Schalter; Abhängigkeiten zwischen Werten | Ja, aber dicht und teils stumm korrigierend | hoch |
| 1.5 | **Status, Feedback, Fehler** | Warnungen, Leerzustände, „nicht möglich weil …“ | Warnbox, aber nur 44 px hoch; kritischer Zustand blendet die Stiche aus | hoch |
| 1.6 | **Persistenz** | Entwurf speichern/laden, letzter Stand nach Neuladen, Voreinstellungen | **Nein** — jedes Neuladen setzt alles zurück | hoch (iOS räumt Safari-Tabs im Hintergrund ab) |
| 1.7 | **Vorlagen / Presets** | Startpunkte statt 15 Regler von Null | Nein | hoch (auf Touch deutlich wichtiger als am Desktop) |
| 1.8 | **Export / Teilen / Drucken** | PDF, SVG, AirPrint, Teilen-Dialog | Blob-Download und `window.print()` | hoch |
| 1.9 | **App-Einstellungen** | Darstellung, Einheiten, Sprache, Standardwerte | Vermischt mit Karteneinstellungen | mittel |
| 1.10 | **Barrierefreiheit** | VoiceOver, Dynamic Type, Kontrast, nicht nur Farbe, „Bewegung reduzieren“ | Nein (Farbe als einziger Warnindikator, Schrift 9,5–13 px) | hoch |
| 1.11 | **Performance** | Live-Neuberechnung beim Ziehen, Abstandsprüfung O(n²), Animation | Läuft, aber ungeprüft auf älteren iPhones | mittel |
| 1.12 | **Offline / Installierbarkeit** | Manifest, Icons, Service Worker | Nein | mittel |
| 1.13 | **Fehlertoleranz** | Rückgängig, „Zurücksetzen“, ungültige Eingaben | Nein (nur stilles Clamping) | mittel |
| 1.14 | **Sprache / Lokalisierung** | Strings, Zahlenformat (Komma) | Deutsch hartkodiert | später |
| 1.15 | **Rechtliches / Info** | Impressum, Datenschutz (hier: „es werden keine Daten gesendet“), Version | Nein | später (Pflicht bei öffentlicher Seite) |

---

## 2. Allgemeine Regeln für iPhone und iPad

### 2.1 Plattform-Regeln (Apple Human Interface Guidelines, sinngemäß)

| Regel | Vorgabe | Konsequenz für uns |
|---|---|---|
| Touch-Ziele | mind. **44 × 44 pt**, Abstand ≥ 8 pt zwischen Zielen | heutige Buttons 28 × 28 px, Checkboxen ~13 px → alles zu klein |
| Schriftgröße | Fließtext ~17 pt; absolutes Minimum ~11 pt; Dynamic Type respektieren | heute 9,5–13 px |
| Safe Areas | Inhalt nicht unter Statusleiste/Dynamic Island (oben ~47–62 pt), Home-Indikator (unten ~34 pt), Querformat: Kerbe seitlich (~59 pt) | `viewport-fit=cover` + `env(safe-area-inset-*)` fehlt |
| Größenklassen statt Gerätemodelle | Layout richtet sich nach **verfügbarer Breite** (compact/regular), nicht nach „iPhone/iPad“ | iPad im Split View / Stage Manager kann so schmal wie ein iPhone sein |
| Navigation | iPhone: Tab-Leiste unten oder Hierarchie mit Zurück (links oben); iPad: Seitenleiste/Split-View | aktuell keine Navigation |
| Sheets | Bottom Sheets mit **Detents** (klein/mittel/groß) sind das iOS-Standardmuster für Zusatzinhalte | passt gut zu „Vorschau oben, Regler im Sheet“ |
| Gesten | Wischen vom linken Rand = Zurück; Wischen von unten = Home; Ecke oben rechts = Kontrollzentrum | keine Bedienelemente am äußersten Rand; Regler nicht direkt am linken Rand |
| Orientierung | iPad: alle Ausrichtungen unterstützen; iPhone: Hoch- und Querformat sinnvoll behandeln | Vorschau im Querformat auf iPhone ist nur ~300 pt hoch |
| Darstellung | Hell/Dunkel folgt dem System | App ist fest dunkel; Anleitung fest hell |
| Eingabe | Tastatur verdeckt untere Hälfte; iPad: Hardware-Tastatur, Trackpad/Maus (Hover, Rechtsklick), Tastaturkürzel | Zahlenfelder (Eigenes Format) brauchen `inputmode`, Scroll-in-View |
| Bedienung mit einer Hand | Wichtige Aktionen im unteren Drittel (Daumenzone) | v. a. im Sticken-Modus |
| Bewegung | „Bewegung reduzieren“ beachten | Auto-Play-Animation optional/abschaltbar |

### 2.2 Web-spezifische Regeln (weil wir in Safari laufen)

| Thema | Regel / Stolperstein |
|---|---|
| **Viewport-Höhe** | `100vh`/`94vh` enthält in Safari die ein-/ausfahrende Adressleiste → `dvh`/`svh` verwenden; sonst springt das Layout |
| **Eingabefelder** | Schrift < 16 px in `<input>`/`<select>` löst in iOS einen Zoom beim Fokussieren aus |
| **Zoom / Gesten** | Pinch-Zoom der Seite vs. Pinch-Zoom in der Vorschau → `touch-action` bewusst setzen; Regler in scrollbaren Containern konkurrieren mit dem Scrollen |
| **Native Controls** | `<select>` wird auf iOS zum Rad-Picker (gut, aber Dunkelstil schlecht steuerbar); `<input type=range>` ist ohne Anpassung klein und der Daumen verdeckt den Griff |
| **Drucken** | `window.print()` öffnet das iOS-Druckmenü (AirPrint, „Als PDF sichern“ per Teilen); `@page`-Regeln und benannte Seiten sind in WebKit nur teilweise unterstützt; Skalierung wird im Dialog vom Nutzer bestimmt |
| **Dateien speichern** | Blob-Download landet in „Dateien/Downloads“ oder öffnet sich in einem Tab; sauberer ist `navigator.share({files})` (Teilen-Dialog) |
| **1:1-Maßstab** | CSS-Millimeter entsprechen auf Displays **nicht** physischen Millimetern. Ein echtes 1:1 gibt es **nur im Druck** |
| **Hintergrund-Tabs** | Safari kann Tabs verwerfen → Zustand muss in `localStorage`/IndexedDB liegen |
| **Display-Sperre** | Für den Sticken-Modus: Screen Wake Lock API (in Safari ab iOS 16.4 verfügbar) |
| **Als App installiert (PWA)** | Eigene Statusleiste, kein Adressfeld, kein Zurück-Button des Browsers → eigene Navigation zwingend; Manifest + Icons + Service Worker für Offline |
| **Haptik** | Safari bietet keine Vibration/Haptik-API → Feedback rein visuell |
| **Zahlenformat** | Dezimalkomma in Anzeige; Eingabe via `inputmode="decimal"` |

### 2.3 Breitenklassen als Arbeitsgrundlage (Näherungswerte, Hochformat in pt)

| Gerät | Breite × Höhe (ca.) | Hinweis |
|---|---|---|
| iPhone SE / mini | 375 × 667 / 812 | schmalster Fall (Referenz „klein“) |
| iPhone 15/16 | 390–393 × 844–852 | Referenz „normal“ |
| iPhone Pro Max | 430–440 × 932–956 | Referenz „groß“ |
| iPhone quer | 667–956 × 375–440 (Höhe!) | Höhe ist der Engpass, seitliche Kerbe |
| iPad mini | 744 × 1133 | |
| iPad 10,9″ / Air / Pro 11″ | 820–834 × 1180–1194 | |
| iPad Pro 13″ | 1032 × 1376 | |
| iPad quer | 1133–1376 × 744–1032 | Sidebar + Vorschau möglich |
| iPad Split View / Stage Manager | ab ~320 bis > 700 breit | verhält sich wie iPhone; Layout muss **breitenbasiert** umschalten |

Vorschlag: drei Breitenstufen als Grundlage für alle Layout-Entscheidungen — **kompakt** (< 600), **mittel** (600–900), **weit** (> 900).

---

## 3. Welche Screens braucht unsere App?

Aus der heutigen Funktionalität abgeleitet; „Neu“ markiert Screens, die es heute nicht gibt, aber aus Abschnitt 1 folgen.

| # | Screen | Zweck | Heute | Priorität |
|---|---|---|---|---|
| S1 | **Editor** (Hauptscreen) | Karte ansehen und Muster gestalten | Ja (Sidebar + Vorschau) | Muss |
| S2 | **Parameter-Bereiche** (als Unterseiten/Sheets des Editors): S2a Karte & Format · S2b Grundform · S2c Astschicht · S2d Sternschicht 1 · S2e Sternschicht 2 · S2f Darstellung | Parameter gruppiert bearbeiten | Ja, alle in einer Sidebar bzw. Popover | Muss |
| S3 | **Prüfung / Hinweise** | Warnungen (Abstand, Stichzahl, ungültige Kombination) verstehen und beheben | Teilweise (Warnbox) | Muss |
| S4 | **Sticken** (Ablaufmodus) | Stich für Stich nachvollziehen/mitsticken | Teilweise (Playback-Leiste) | Muss |
| S5 | **Anleitung** | Arbeitsanweisung: Ebenenübersicht, Äste, Sterne, Tabellen, Fadenlängen | Ja (Overlay) | Muss |
| S6 | **Lochmuster 1:1** | Maßstabsgetreuer Ausdruck zum Anstechen | Ja (letzte Seite der Anleitung) | Muss |
| S7 | **Export / Teilen** | SVG, PDF, Drucken | Ja (zwei Buttons an verschiedenen Stellen) | Muss |
| S8 | **App-Einstellungen** | Darstellung, Standardwerte, Info | Vermischt mit S2a/S2f | Soll |
| S9 | **Meine Entwürfe** | Speichern, Laden, Duplizieren, Löschen | **Neu** | Soll (Entscheidung E3) |
| S10 | **Vorlagen / Start** | Beispiele als Einstieg | **Neu** | Soll |
| S11 | **Hilfe / Glossar** | Begriffe, kurze Einführung | **Neu** | Soll |
| S12 | **Info / Rechtliches** | Version, Datenschutz, Impressum | **Neu** | Später |

---

## 4. Funktionen je Screen

### S1 Editor
- Kartenvorschau (Format, Falz, Rand, Löcher, Stiche, Sprünge), Kartonfarbe/Fadenfarbe
- Zugriff auf alle Parametergruppen (S2)
- Statusanzeige: Zahl Punkte / Stiche / Fadenlänge; Ampel für Mindestabstand
- Zugriff auf S3, S4, S5, S7
- Zurücksetzen / Rückgängig (neu)
- Vorschau prüfen: Zoomen/Verschieben, ggf. Messhilfe (Abstand zweier Löcher in mm) (optional)

### S2 Parameter-Bereiche
| Bereich | Steuerelemente (heute) | Abhängigkeiten |
|---|---|---|
| S2a Karte & Format | Format-Preset, Eigene Breite/Höhe, Falzposition (links/oben/keine), Zoom/Musterradius | Falz ändert Randfläche und Radiusbereich |
| S2b Grundform | Kreispunkte 3–16 | bestimmt Teiler, k-Grenzen, Mindestradius |
| S2c Astschicht | an/aus, Seitenäste an/aus, Ebenen 1–6, Astwinkel 3–55°, Astlänge 20–200 %, Wachstum 0–150 % | Seitenäste ab Ebene 2; (Fraktaltiefe/-skalierung existieren im Code, **haben keine Bedienung**) |
| S2d Sternschicht 1 | an/aus, Sternebene (nur mit Astschicht), Sternstrahlen (Teiler von n), Schrittweite k, „Seitenäste bei diesem Sternlevel“ | k-Obergrenze hängt von Strahlen und Astschicht ab; Auslassungsoption nur wenn wirksam |
| S2e Sternschicht 2 | wie 1, plus Rotationsversatz | nur wenn Schicht 1 an |
| S2f Darstellung | Kartonfarbe, Fadenfarbe, „Restmuster als Vorschau“, „Rückseiten-Sprünge anzeigen“ | – |

Anforderungen an alle Bereiche: Wert immer sichtbar, Feineinstellung (±1), Standardwert wiederherstellen, deaktivierte/irrelevante Optionen erklären statt verstecken, stilles Clamping sichtbar machen.

### S3 Prüfung / Hinweise
- Liste aller Probleme mit Schwere (blockierend / knapp / Hinweis) und **konkreter Abhilfe** („Zoom verkleinern“, „Kreispunkte auf ≤ 12“)
- Markierung der betroffenen Löcher in der Vorschau, Springen zum Problem
- Erklärung Mindestabstand (Faden-/Lochdurchmesser)
- Stichlimit (300) und Fadenbedarf

### S4 Sticken
- Aktueller Schritt groß: *Nr., VS-Anweisung („E2 → E3“), anschließender RS-Sprung*
- Vor/Zurück um 1 Schritt (primär), Springen zu Schritt/Ast, Auto-Play mit einstellbarem Tempo (heute fix 45 ms — für echtes Sticken viel zu schnell)
- Fortschritt (z. B. „Stich 12 / 80“), Wiederholungshinweis „Ast 2 von 8“
- Vorschau mit hervorgehobenem aktuellem Segment, optional Ausschnitt/Zoom auf aktuellen Bereich
- Display wach halten, Fortschritt merken
- Fadenwechsel/-länge pro Schicht

### S5 Anleitung
- Kopf: Kennwerte, Legende (VS/RS)
- Teil 1 Ebenenübersicht, Teil 2 Flocke (Ast 1 von n + Tabelle), Teil 3/4 Sterne (erste Schritte + Tabelle)
- Fadenlängen je Schicht
- Aktionen: Drucken, Als PDF teilen, Schließen
- Springen zwischen Teilen (Inhaltsverzeichnis)

### S6 Lochmuster 1:1
- Maßstabsgetreue Darstellung des Zuschnitts inkl. Falzlinie, Rand, Panel
- Klare Druckhinweise („100 %“, „Tatsächliche Größe“), Prüfmaß (z. B. 50-mm-Balken oder Kalibrierkästchen zum Nachmessen nach dem Druck)
- Warnung, wenn der Zuschnitt größer als A4 ist (Kacheln/Mehrseitendruck als Zukunftsoption)
- Papierformat-Wahl (A4/Letter) (optional)

### S7 Export / Teilen
- Optionen: Anleitung als PDF, Lochmuster als PDF, Vorlage als SVG, Entwurf als Datei (Sichern)
- Drucken (AirPrint), Teilen-Dialog
- Erfolgs-/Fehlermeldung; Hinweis, wenn blockiert (kritischer Abstand)

### S8 App-Einstellungen
- Darstellung (System/Hell/Dunkel), Standardformat, Standardfarben, Wiedergabetempo
- Entwurf zurücksetzen / Daten löschen
- Info/Version

### S9 Meine Entwürfe · S10 Vorlagen · S11 Hilfe · S12 Info
- S9: Liste mit Vorschaubild, Name, Datum; neu / duplizieren / umbenennen / löschen; Export/Import als Datei
- S10: 6–10 kuratierte Startmuster mit Vorschau; „Als Entwurf übernehmen“
- S11: Glossar, 3-Schritt-Einführung, Kurzerklärung Mindestabstand, Faden/Kartonwahl
- S12: Version, Datenschutz („alles lokal“), Impressum

---

## 5. Zu erwartende Layout-Probleme je Screen — iPhone vs. iPad

Legende: **K** = kompakt/iPhone hoch · **Kq** = iPhone quer · **M** = iPad hoch (mittel) · **W** = iPad quer (weit) · **Sp** = iPad Split View/Stage Manager (verhält sich wie K bzw. M)

### S1 Editor

| Problem | iPhone | iPad |
|---|---|---|
| **Konkurrenz um Platz:** Karte (A6 hoch ≈ 1 : 1,41) braucht Höhe, 15+ Regler brauchen noch mehr | **K:** Bei 358 pt Breite wäre die Karte ~505 pt hoch — auf ~750 nutzbaren pt bleiben ~250 pt für alles andere. Vorschau und Regler können nicht gleichzeitig dauerhaft groß sein → Bottom Sheet mit Detents oder Vollbild-Vorschau | **M:** Karte oben, Parameter darunter möglich (ca. 55/45), Karte aber max. begrenzen. **W:** Sidebar links + Vorschau rechts passt; Sidebar-Breite muss flexibel sein |
| **Querformat-Karte (A6 quer)** | **K:** nur ~255 pt hoch → ungewohnt viel Restfläche, hier passt sogar Sheet darunter | geringes Problem |
| **iPhone quer** | **Kq:** Höhe ~340 pt nutzbar → Karte (hoch) maximal ~300 pt hoch → Löcher winzig; Regler praktisch nur als schmales Seitenpanel | – |
| **Feste Proportion 16:9 und `maxHeight: 94vh`** (Zeile 1573) | im Hochformat des Handys unbrauchbar, weil der Rahmen ein Querformat erzwingt | iPad hoch: Rahmen lässt ~40 % der Höhe ungenutzt |
| **Fixe Sidebar 440 px** (Zeile 1581) | passt nicht (> Bildschirmbreite) | **M** 744–834: Sidebar frisst > 50 % der Breite; **Sp** noch schlimmer |
| **Lochgröße auf dem Display:** Ø ≈ 0,9 mm ≈ 3 pt, Mindestabstand ≈ 3,2 mm ≈ 11 pt (bei 105 mm ↔ 358 pt) | Farbige Warnpunkte (+0,25 mm) kaum erkennbar; Pinch-Zoom in der Vorschau nötig | etwas besser (größere Karte), Zoom trotzdem sinnvoll |
| **Statistik + Legende + Warnbox + Playback** unter der Karte | verbrauchen zusammen ~160 pt → müssen in Sheet/Kopfzeile wandern | **W** passt darunter |
| **Safe Areas:** Dynamic Island/Home-Indikator | Kopfzeile und Sheet-Griff kollidieren ohne `env(safe-area-inset-*)` | in der Regel geringer, aber Stage-Manager-Rahmen/Querformat beachten |
| **Safari-Leiste:** `vh` springt | Layout ruckelt beim Scrollen | gleich |
| **Dunkle UI + Kartonfarbe Elfenbein** | hoher Kontrast zum Rahmen ok; auf OLED sehr dunkle Flächen: Kontrast der blassen Texte (#7d93a8, 9,5–11 px) zu klein | – |

### S2 Parameter-Bereiche

| Problem | iPhone | iPad |
|---|---|---|
| **Mehrspaltige Reihen** (`Row cols=3/4`, Zeile 1294/1311) | **K:** 3–4 Regler in einer Zeile → je ~80–110 pt; Beschriftungen wie „Wachstum n. außen: 30 %“ und Selects wie „8 Strahlen (jeder 1.)“ werden abgeschnitten → einspaltig | **M/W:** 2 Spalten sinnvoll; 4 weiterhin zu viel |
| **Regler per Touch:** Griff vom Finger verdeckt, Wert nur im Label, Scrollen vs. Ziehen | **K:** Wert oben groß, Regler volle Breite, ±-Tasten; ganzzahlige Werte (3–16, 1–6) eher als Stepper/Segmente | gleich, Pencil/Maus: Hover-Feedback möglich |
| **Native `<select>`** | Rad-Picker verdeckt untere Bildschirmhälfte, ok; Dunkelstil begrenzt | Popover am Feld; Listenbreite beachten |
| **Bedingte Felder** (erscheinen/verschwinden: Sternebene, Versatz, Auslassungs-Option, Seitenäste) | Layout springt, Scrollposition verschiebt sich; Nutzer sieht nicht, *warum* etwas fehlt | gleich, aber mehr Platz für Platzhalter/Erklärtext |
| **Stilles Clamping** (`Math.min(k1, kMax1)`, `effTeiler`) | Wert ändert sich ohne Rückmeldung, wenn n verkleinert wird | gleich |
| **Abhängigkeitsketten** (n → Teiler → k → Auslassung) | Reihenfolge der Bearbeitung unklar, bei 3+ Bereichen viel Scrollen | **W:** Gruppenliste links, Bereich rechts reduziert Scrollen |
| **Live-Rückmeldung:** Änderung an Regler soll Karte sichtbar ändern | **K:** Karte teils vom Sheet verdeckt → Mini-Vorschau im Sheet-Kopf oder Detent so wählen, dass Karte sichtbar bleibt | **W** unproblematisch |
| **Tastatur** bei Eigenem Format | verdeckt Felder; `inputmode`, ≥ 16 px, Scroll-in-View, „Fertig“-Taste | Hardware-Tastatur: Tab-Reihenfolge, Pfeiltasten für Regler |
| **Fraktaltiefe/-skalierung ohne UI** | Entscheidung, ob das Feature auftaucht (mehr Regler = mehr Platzbedarf) | |

### S3 Prüfung / Hinweise

| Problem | iPhone | iPad |
|---|---|---|
| **Warnbox fix 44 px hoch** (Zeile 1598) mit Scroll | Mehrzeilige Warnungen unlesbar, bei kritischem Zustand wichtigste Information versteckt | bei **W** etwas Luft, aber Prinzip gleich |
| **Kritischer Zustand blendet alle Stiche aus** (Zeile 1409) | Leere Karte ohne unmittelbar sichtbare Erklärung (Warnung evtl. außerhalb des Sheets) → Hinweis direkt an der Karte | gleich |
| **Farbe als einziger Indikator** (Orange/Rot Punkte) | zusätzlich Form/Text/Zahl nötig (Farbsehschwäche, kleine Punkte) | gleich |
| **Navigation zu Problemstellen** | Tippen auf Warnung → Zoom auf Stelle (Fingerziel ≥ 44 pt) | Hover/Pointer-Highlight möglich |

### S4 Sticken

| Problem | iPhone | iPad |
|---|---|---|
| **Bedienleiste mit 7 Elementen in einer Zeile** (Play, Reset, Slider, Zähler, Export; Zeile 1462) | **K:** passt nicht; Slider hat nur Restbreite. Trennen in: Transport (groß, unten) + Scrubber (eigene Zeile). Export gehört nicht hierher | **M/W:** Passt, aber Touch-Größen beachten |
| **Slider mit bis zu ~600 Positionen** (2 × Stiche) | 1 pt Daumenbewegung ≈ mehrere Schritte → Feinsteuerung nur über Tasten (±1, ±Ast) | gleich |
| **Aktueller Schritt nur grafisch** | Textanweisung (Schritt, von→nach) in großer Schrift neben/unter der Karte | **W:** Karte links, Anweisung rechts (Spalte) |
| **Auto-Play 45 ms** | Für Betrachtung ok, zum Mitsticken unbrauchbar → Tempo, „Nächster Schritt“-Modus | gleich |
| **Einhandbedienung am Tisch** | Haupttasten im unteren Drittel, ≥ 56 pt; Display-Sperre verhindern | iPad im Ständer (quer): große Tasten links/rechts, Hardware-Tasten (Leertaste/Pfeile) |
| **Detailerkennbarkeit** | Karte nicht ganz passend → automatisches Zoomen auf aktuelle Stelle | Kartengröße reicht eher |
| **Rotation während des Stickens** | Layout darf Zustand nicht verlieren | iPad frei drehbar, Wechsel quer/hoch ohne Reset |

### S5 Anleitung

| Problem | iPhone | iPad |
|---|---|---|
| **Fixes Blatt 960 px, Innenabstand 40 px, SVG-Breite bis 856 px** (Zeilen 626, 897) | **K:** Grafik wird auf ~310 pt herunterskaliert → Beschriftung (10,5 px) ≈ 4 pt, nicht lesbar. Querformat oder Zoom/Scroll-Container pro Grafik; alternativ Schritt-für-Schritt-Kartenstapel | **M:** 744–834 ≈ Blattbreite, Skalierung ~0,8; **W:** passt |
| **Tabellen** (Schritt / VS / RS) | 3 Spalten gehen, Text „E2L.1a → E2L“ umbricht; Zeilen mit festem Mindestabstand | gleich bzw. luftiger |
| **Ebenen-Übersicht** (4 Karten à 130 px + „=“) | umbricht in 2 × 2, das „=“-Symbol verwaist | **M/W:** passt in eine Reihe |
| **Werkzeugleiste mit drei Textbuttons** (Zeile 684ff.) | läuft über → Icons + Menü | passt |
| **Overlay `position: fixed` + innerer Scroll** | Rubber-Banding, Scroll-Durchgriff auf Hintergrund, `100vh` | wie iPhone, zusätzlich Stage-Manager-Fenstergröße |
| **Drucken / Speichern** | Der Hinweis „Sandbox/Download“ ist veraltet — die Seite läuft jetzt gehostet; iOS-Druckdialog (Teilen → PDF) ist der natürliche Weg | AirPrint am iPad komfortabel; Tastaturkürzel ⌘P |
| **Zwei Darstellungen** (Bildschirm vs. Druck) | Screen-Layout und Druck-Layout dürfen unterschiedlich sein; heute dieselbe Struktur mit CSS-Overrides | gleich |
| **Navigation im langen Dokument** | Inhaltsverzeichnis/Teilsprünge, Rückkehr zum Editor | **W:** Inhaltsverzeichnis als Seitenleiste |

### S6 Lochmuster 1:1

| Problem | iPhone | iPad |
|---|---|---|
| **Display ≠ 1:1** | `width: 105mm` ist auf dem Gerät **nicht** 105 mm → darf auf dem Display nicht als Maßstab versprochen werden; Hinweis „Nur gedruckt maßgetreu“ | gleich |
| **Zuschnitt vs. A4** | A6 mit Falz (210 × 148 mm) passt nur im **A4-Querformat** (nutzbar 277 × 190 mm); die Seite muss also quer gedruckt werden, was in WebKit wegen der benannten `@page` nicht sicher greift. Eigene, größere Formate überschreiten A4 ganz → Verkleinerung (dann nicht anstechbar) | gleich |
| **Druckskalierung** | iOS-Druckdialog bietet „Seite anpassen“ (kann verfälschen) | AirPrint, gleiche Gefahr |
| **Kontrolle nach dem Druck** | Kalibrierbalken ergänzen | gleich |
| **Querformat-Seite im Hochformat-Dokument** (benannte `@page`) | in WebKit teils ignoriert → Ausrichtung im Dialog manuell | gleich |

### S7 Export / Teilen

| Problem | iPhone | iPad |
|---|---|---|
| **Blob-Download-Verhalten** | öffnet teils im Tab statt zu speichern, „Dateien“-Ziel unklar | Popover-Position beim Teilen-Dialog beachten |
| **Mehrere Export-Orte** (SVG-Button in Playback-Leiste, Druck-Icon im Kopf) | Zentralisieren in einem „Teilen/Exportieren“-Sheet | gleich |
| **Blockiert bei kritischem Abstand** (Button disabled ohne Erklärung) | Erklärung + Link zu S3 | gleich |

### S8 Einstellungen / S2a-S2f-Überschneidung

| Problem | iPhone | iPad |
|---|---|---|
| **Popover 300 px absolut positioniert** (Zeile 1577) | Rechts oben, maxHeight 80 % des 16:9-Rahmens → kaum nutzbar | Popover ok, aber Mischung aus Karten- und App-Einstellungen |
| **Karteneinstellung vs. App-Einstellung** | trennen: Format/Falz/Zoom gehören zur Karte, Farben zur Darstellung, nur Rest zur App | **W:** Master-Detail |

### S9 Entwürfe · S10 Vorlagen · S11 Hilfe · S12 Info

| Problem | iPhone | iPad |
|---|---|---|
| Listen mit Vorschaubildern | einspaltig, Wischgesten (löschen) | Raster 2–4 Spalten oder Sidebar |
| Vorschau-Rendering vieler Karten | SVG-Miniaturen, Performance bei vielen Einträgen | gleich |
| Hilfe-Texte | kurz, mit Bild; lange Texte nur als Detailseite | Seitenleiste + Text |

### Querschnitts-Layoutprobleme (gelten in allen Screens)

| # | Thema | Befund im Ist-Stand |
|---|---|---|
| Q1 | Viewport-Meta | kein `viewport-fit=cover`, keine Safe-Area-Nutzung (`index.html`) |
| Q2 | Höhe | `94vh`, `100vh` statt `dvh` |
| Q3 | Schriftgrößen | 9,5–13 px für Bedienelemente; Inputs/Selects < 16 px → Auto-Zoom beim Fokus |
| Q4 | Touch-Ziele | 28 × 28 px Buttons; Checkboxen/Radio native Größe |
| Q5 | Breitenlogik | keine einzige Media-/Container-Query; alles Pixelwerte |
| Q6 | Farbschema | fest dunkel (App) + fest hell (Anleitung), kein System-Modus |
| Q7 | Zustand | nicht persistiert; Neuladen/Hintergrund = Verlust |
| Q8 | Barrierefreiheit | SVG ohne Beschriftung, Warnstatus nur über Farbe, keine `aria-live`-Hinweise |
| Q9 | Performance | Neuaufbau aller Segmente bei jeder Reglerbewegung; Prüfung O(n²) über alle Knoten |
| Q10 | Architektur | ein 1600-Zeilen-File mit Inline-Styles → Layout-Umbau ohne Aufteilung teuer |

---

## 6. Prioritäten aus der Analyse

1. **Layout muss breitenbasiert werden** (kompakt / mittel / weit), nicht gerätebasiert.
2. **Der Editor braucht ein anderes Verhältnis Vorschau ↔ Regler** auf dem iPhone (Sheet/Detents oder Vollbild-Umschaltung); auf dem iPad ist die Seitenleiste nur ab „weit“ tragfähig.
3. **Sticken** ist vermutlich der wertvollste Modus auf dem Handy/iPad und braucht eine eigene, ruhige Oberfläche (große Schritte, Wake Lock).
4. **Anleitung und Lochmuster** sind Druckprodukte; auf dem Bildschirm sollten sie lesbar *und* getrennt vom Druck-Layout konzipiert werden.
5. **Persistenz und Vorlagen** sind auf Touch keine Kür: ohne sie ist das Einstellen von 15 Parametern bei jedem Start zu aufwendig.
6. **Fehler-/Warnkonzept** muss sichtbar, erklärend und nicht nur farbig sein.

---

## 7. Offene Entscheidungen für das gemeinsame Konzept

| # | Frage | Optionen / Auswirkung |
|---|---|---|
| E1 | Webapp im Browser, installierte PWA oder später native App? | bestimmt Navigationsmuster (eigene Zurück-Logik in PWA), Dateiablage, Offline |
| E2 | Ist **Sticken am Gerät** (Mitsticken) ein Kernszenario oder nur Ansicht? | Eigener Modus S4 mit Wake Lock und großen Tasten vs. Playback-Leiste |
| E3 | Sollen **Entwürfe speicherbar** sein (mehrere) oder genügt „letzter Stand“? | S9 ja/nein; Datenmodell, Import/Export |
| E4 | Gibt es **Vorlagen/Beispiele** als Einstieg? | S10 ja/nein; Onboarding |
| E5 | Wie viel Expertentum: **alle Parameter sichtbar** oder gestuft („einfach / erweitert“)? | beeinflusst Parameterstruktur stark |
| E6 | Fraktal-Funktion (Tiefe, Skalierung): **wieder anbieten** oder entfernen? | Heute im Code, nicht bedienbar |
| E7 | Muss die Anleitung **auf dem Bildschirm** gut lesbar sein oder nur ausdruckbar? | beeinflusst Neuaufbau von S5 |
| E8 | Wird das Lochmuster mit **mehrseitigem/Kachel-Druck** gebraucht, wenn der Zuschnitt > A4 ist? | S6-Funktion |
| E9 | Soll die App **Hell/Dunkel nach System** folgen? | Farbkonzept |
| E10 | Mehrsprachigkeit absehbar? | String-Handling früh trennen |
| E11 | Welche **iPhone-/iPad-Modelle und iOS-Mindestversion** sind relevant? | Wake Lock (iOS ≥ 16.4), `dvh` (iOS ≥ 15.4), Container Queries (iOS ≥ 16) |
| E12 | Wird die **SVG-Datei** tatsächlich weiterverwendet (Plotter/Schneideplotter), oder genügt PDF? | Umfang S7 |

---

## 8. Vorgehen danach

1. Diese Analyse gemeinsam durchgehen; Annahmen A1–A4 und Entscheidungen E1–E12 klären.
2. **Gemeinsames Konzept:** Navigationsmodell, Screen-Karte, Layout-Regeln pro Breitenstufe, Komponentenliste (Regler, Stepper, Sheet, Karten, Warnhinweise).
3. **Design** (separater Schritt): visuelle Sprache, Komponenten, Prototyp je Breitenstufe.
4. **Umsetzung:** Aufteilen des Monolithen in Komponenten, dann Layout-Umbau.
