# Stickkarten (native iOS-App) — UI-Grundanalyse für eine Neugestaltung

Status: Entwurf zur gemeinsamen Diskussion · **keine Design-Entscheidungen**.
Nächster Schritt (separat): gemeinsames UI-Konzept → danach Design.

## 0. Grundlage und Abgrenzung

- Die App wird unter `ios/` als **SwiftUI-App für iPhone und iPad** entwickelt (Projektstand iOS ≥ 16; **festgelegt: iOS 17**, siehe Abschnitt 7).
- Die **bestehende Oberfläche wird bewusst ignoriert** — sie ist weder Vorbild noch Kritikgegenstand. Das UI wird von Grund auf neu entworfen.
- **Der Code dient nur als Informationsquelle** für: was die App kann, welche Eingaben es gibt (mit Wertebereichen und Abhängigkeiten), welche Ergebnisse berechnet werden, welche physikalischen Randbedingungen gelten. Quellen: `ios/StickCore` (Fachlogik, PDF) und die Web-Referenz `src/StickkartenGeneratorV4.jsx`.
- Annahmen (bitte korrigieren):
  - A1. Nutzerin/Nutzer stickt von Hand (Karton, Nadel, Faden) und benutzt iPhone/iPad als Entwurfs-, Vorlagen- und Nachschlagewerkzeug.
  - A2. Alles läuft lokal, ohne Konto und Server.
  - A3. Sprache zunächst Deutsch.
  - A4. Entwickelt wird **ohne Mac** (Build/Tests nur über GitHub Actions); das beeinflusst, wie wir Layouts überprüfen (siehe E5).

---

## A. Funktionaler Kern (aus dem Code abgeleitet)

### A.1 Was die App leistet

Aus Parametern entsteht ein **Lochmuster** für eine gestickte Karte (Kreispunkte, optional „Astschicht“ = Baum/Flocke, optional eine oder zwei „Sternschichten“ = Sehnenmuster). Daraus werden berechnet:

1. die **Kartenansicht** (Löcher, Stiche, Rückseiten-Sprünge),
2. die **Stichfolge** (jeder Stich auf der Vorderseite „VS“, danach ein verdeckter Sprung auf der Rückseite „RS“),
3. eine **Machbarkeitsprüfung** (Mindestabstand der Löcher, Stichlimit, gültige Kombination),
4. **Kennzahlen** (Punkte, Stiche, Fadenlänge +15 %),
5. **Druckvorlagen als PDF**: Lochmuster 1:1 zum Anstechen und eine mehrseitige Anleitung (Ebenenübersicht, Schrittdiagramme, Tabellen, Fadenlängen).

### A.2 Eingaben

| Gruppe | Eingabe | Wertebereich / Auswahl | Abhängigkeit |
|---|---|---|---|
| Karte | Format | A6 hoch 105×148 mm · A6 quer 148×105 mm · eigenes Format (Breite/Höhe mm) | Zuschnitt = doppelte Fläche bei Falz |
| Karte | Falzposition | links · oben · keine | Falzseite braucht größeren Rand (Falz ≥ 18 mm, sonst ≥ 14 mm) |
| Karte | Zoom (Musterradius) | 0–100 % zwischen Mindest- und Maximalradius | Mindestradius hängt von Kreispunkten/Ebenen ab; passt nichts → Format ungültig |
| Grundform | Kreispunkte n | 3–16 | bestimmt Strahlen-Auswahl und Schrittweiten |
| Astschicht | aktiv | an/aus | |
| Astschicht | Ebenen | 1–6 | |
| Astschicht | Seitenäste | an/aus | Seitenäste erst ab Ebene 2 |
| Astschicht | Astwinkel / Astlänge / Wachstum nach außen | 3–55° / 20–200 % / 0–150 % | nur mit Seitenästen |
| Astschicht | Fraktal-Tiefe / -Skalierung | 0–2 / 30–80 % | Skalierung nur bei Tiefe > 0 |
| Sternschicht 1 | aktiv | an/aus | |
| Sternschicht 1 | Sternebene | 1…Ebenen (Ebenen = äußerer Ring) | nur mit Astschicht |
| Sternschicht 1 | Sternstrahlen | Teiler von n („alle“, „jeder 2.“ …) | |
| Sternschicht 1 | Schrittweite k | 1…kMax | kMax hängt von Strahlen und Astschicht ab; bei kMax = 1 gibt es keine Auswahl |
| Sternschicht 1 | Seitenäste auf Sternlevel weglassen | keine · nur Sternlevel · Sternlevel und darunter | nur anbietbar, wenn dort Seitenäste existieren |
| Sternschicht 2 | aktiv + alle Felder wie Schicht 1 | | nur mit Schicht 1; zusätzlich **Rotationsversatz** 0…(Teiler−1) |
| Darstellung | Kartonfarbe, Fadenfarbe | 4 Kartonfarben, 4 Fadenfarben | rein visuell |
| Darstellung | Restmuster-Vorschau, Rückseiten-Sprünge | an/aus | rein visuell |

Insgesamt **rund 25 Eingaben**, mit zahlreichen **bedingten** und **gegenseitig begrenzten** Werten.

### A.3 Ausgaben und Zustände

- Kartenmodell: bis zu einigen Hundert Punkte; Stichlimit-Richtmaß **300 Stiche** (≈ bis 600 Schritte inkl. Sprüngen).
- Ampel je Loch: **ok · knapp (< 150 % Mindestabstand) · zu gering (< Mindestabstand)**.
- **Zustand „kritisch“**: Es dürfen keine Stiche gezeigt und kein PDF erzeugt werden, solange Löcher zu eng liegen — Abhilfe: Zoom, Kreispunkte oder Ebenen verringern.
- Weitere Hinweise: keine Schicht aktiv · ungültiges Format · mehr als 300 Stiche.
- Kennzahlen: Punkte, Stiche, Fadenlänge gesamt und je Schicht.
- PDFs: Lochmuster 1:1 (A4 hoch oder quer, 1 mm = 72/25,4 pt, Falzlinie, Rahmen, 50-mm-Kontrollbalken; Verkleinerungswarnung, wenn Zuschnitt > A4) und Anleitung (mehrere A4-Seiten, letzte Seite = Lochmuster).

### A.4 Physikalische Randbedingungen, die das UI betreffen

| Größe | Wert | Folge fürs UI |
|---|---|---|
| Lochdurchmesser | ≈ 0,92 mm | auf dem Display bei 105 mm ↔ 358 pt ≈ **3 pt** — ohne Zoom kaum erkennbar |
| Mindestabstand | ≈ 3,2 mm | ≈ 11 pt auf dem iPhone — Warnmarkierungen müssen größer dargestellt werden als maßstäblich |
| Kartenverhältnis | A6 hoch ≈ 1 : 1,41 · A6 quer ≈ 1,41 : 1 · eigenes Format beliebig | Layout darf kein festes Kartenformat voraussetzen |
| Druck 1:1 | nur über PDF/Drucker; Bildschirm kann nicht maßstäblich anzeigen | der Bildschirm darf kein „Echtmaß“ versprechen |
| Zuschnitt mit Falz | 210 × 148 mm (A6) → A4 quer | Papierorientierung ist Teil der Druckinformation |

### A.5 Was Nutzerinnen/Nutzer mit der App tun wollen (Aufgaben)

| # | Aufgabe | Dauer / Situation |
|---|---|---|
| T1 | Ein Muster **entwerfen** und sofort beurteilen | iterativ, viele schnelle Änderungen |
| T2 | **Machbarkeit** prüfen und Probleme beheben | punktuell, nach T1 |
| T3 | Die Stichfolge **verstehen oder mitsticken** | längere Sitzung, Gerät neben dem Karton |
| T4 | Das **Lochmuster ausdrucken** und zum Anstechen nutzen | selten, aber präzise |
| T5 | Die **Anleitung** lesen/drucken | beim Vorbereiten |
| T6 | **Wiederfinden** früherer Muster, Varianten ablegen | wiederkehrend |
| T7 | **Lernen**, was die Begriffe und Parameter bewirken | Einstieg, Nachschlagen |

Die Screens in Abschnitt 3 leiten sich aus diesen Aufgaben ab, nicht aus der bisherigen Oberfläche.

---

## 1. Was braucht eine App allgemein?

| # | Bereich | Inhalt | Relevanz für diese App |
|---|---|---|---|
| 1.1 | **Informationsarchitektur / Navigation** | klare Hauptbereiche, Rückweg, Zustand beim Wiederkommen | hoch — mehrere Aufgaben (T1–T7) |
| 1.2 | **Kern-Workflow** | Entwerfen → Prüfen → Sticken/Drucken als nachvollziehbare Abfolge | hoch |
| 1.3 | **Eingabe komplexer, abhängiger Parameter** | Gruppierung, Reihenfolge, Bedingungen, Zusammenfassungen | hoch (≈ 25 Eingaben) |
| 1.4 | **Rückmeldung, Warnungen, Leerzustände** | Ursache + Abhilfe + direkter Weg dorthin | hoch (Zustand „kritisch“ blockiert Wesentliches) |
| 1.5 | **Onboarding / Hilfe / Glossar** | Begriffe (Kreispunkt, Ebene, Sternschicht, Schrittweite, VS/RS, Mindestabstand) | hoch |
| 1.6 | **Persistenz** | letzter Stand, mehrere Entwürfe, Vorlagen, Sicherung | hoch |
| 1.7 | **Ausgabe: Teilen, Drucken, Dateien** | PDF-Vorschau, Teilen-Menü, AirPrint, Dateien-App | hoch |
| 1.8 | **App-Einstellungen** | Darstellung, Standardwerte, Info, Zurücksetzen | mittel |
| 1.9 | **Barrierefreiheit** | VoiceOver (auch für grafische Inhalte), Dynamic Type, Kontrast, nicht nur Farbe, Bewegung reduzieren | hoch |
| 1.10 | **Performance und Reaktionszeit** | Live-Neuberechnung beim Ziehen, PDF-Erzeugung, Animation | mittel — messen |
| 1.11 | **Fehlertoleranz** | Rückgängig, Zurücksetzen mit Rückfrage, Eingabevalidierung | mittel |
| 1.12 | **Verteilung / Pflichtangaben** | App-Symbol, Startbild, Privacy-Manifest (UserDefaults), Datenschutz, Impressum je nach Weg | je nach E1 |
| 1.13 | **Lokalisierung** | Strings trennen, Zahlenformat | später |
| 1.14 | **Testbarkeit der UI** | Layout-Prüfung je Gerät ohne Mac | hoch (E5) |

---

## 2. Allgemeine Regeln für iPhone und iPad

### 2.1 Plattformregeln (SwiftUI, iOS ≥ 16)

| Thema | Regel | Konsequenz |
|---|---|---|
| Touch-Ziele | mind. 44 × 44 pt, ≥ 8 pt Abstand | gilt für alle Tasten, besonders im Mitstick-Modus |
| Größenklassen | nach `horizontalSizeClass`/`verticalSizeClass` und realer Breite entscheiden, nicht nach „iPhone/iPad“ | iPad kann so schmal wie ein iPhone sein; großes iPhone quer kann „regular“ sein |
| Safe Areas | System respektiert sie; Hintergründe dürfen darunter laufen, Bedienelemente nicht | Dynamic Island, Home-Indikator, Querformat-Aussparungen |
| Dynamic Type | Text-Styles verwenden; Layouts müssen mit sehr großer Schrift umbrechen | feste Spaltenzahlen vermeiden |
| Navigation | iPhone: Tabs, Hierarchie, Sheets; iPad: `NavigationSplitView`/Sidebar | passend zu Aufgabenbereichen |
| Sheets | `presentationDetents` (iOS 16): klein/mittel/groß, Drag-Indikator | geeignet für „Regler über der Karte“ |
| Eingabe | `decimalPad` hat keine Return-Taste; Tastatur verdeckt untere Hälfte | Tastaturleiste, Scroll-in-View |
| Darstellung | System-Hell/Dunkel, System-Farben, SF Symbols | Kartenfarbe bleibt Inhalt, nicht Theme |
| Bewegung/Haptik | Reduzierte Bewegung beachten; `UIImpactFeedbackGenerator` (iOS 16), `sensoryFeedback` erst iOS 17 | Animation ruhig und abschaltbar |
| Gesten | Systemgesten (Rand-Wischen zurück, Home-Wischen) nicht blockieren; Zoom/Pan der Karte nicht mit Seiten-Scroll kollidieren lassen | Gestenkonzept pro Screen festlegen |
| Hardware-Tastatur / Trackpad (iPad) | `keyboardShortcut`, Hover | Wiedergabe-Steuerung per Tastatur |
| Multitasking | Split View/Slide Over/Stage Manager: Fensterbreite ~320 pt bis Vollbild, frei veränderbar | Layout muss kontinuierlich reagieren |
| Display-Sperre | `isIdleTimerDisabled` | Mitstick-Modus |
| Drucken/Teilen | `ShareLink`, `UIPrintInteractionController` (iPad: Ankerpunkt), Dateien-App | PDF-Ausgabe ist Kernfunktion |
| Läuft auch auf Mac/Vision | bei iPhone+iPad-Ziel ohne Zutun | tolerieren, nicht priorisieren (E10) |
| Orientierung | iPad alle; iPhone hoch + quer | Querformat nicht vergessen |

### 2.2 Größenklassen und Gerätebreiten (Näherung, pt)

| Situation | Klasse (breit × hoch) | Maße |
|---|---|---|
| iPhone SE/mini hoch | compact × regular | 375 × 667–812 |
| iPhone Standard hoch | compact × regular | 390–393 × 844–852 |
| iPhone Pro Max hoch | compact × regular | 430–440 × 932–956 |
| iPhone quer | compact × compact (Plus/Max: regular × compact) | Höhe nur ~340–440 |
| iPad mini hoch / quer | regular × regular | 744 × 1133 / 1133 × 744 |
| iPad 11″/Air hoch / quer | regular × regular | 820–834 × 1180–1194 / umgekehrt |
| iPad Pro 13″ hoch / quer | regular × regular | 1032 × 1376 / 1376 × 1032 |
| iPad Split View 1/3, Slide Over | compact × regular | ~320–400 breit |
| iPad Split View 1/2, 2/3, Stage Manager | compact oder regular | ~507–820 breit |

Folge: Für das Konzept sollten **mindestens drei Breitenstufen** (schmal ≲ 600 · mittel · weit ≳ 900) **und die Höhe** (iPhone quer) berücksichtigt werden.

---

## 3. Welche Screens werden benötigt?

Abgeleitet aus den Aufgaben T1–T7 (A.5) und den Funktionen (A.1–A.3).

| # | Screen | Aufgabe | Priorität |
|---|---|---|---|
| S1 | **Muster / Editor** — Karte + Parameter | T1 | Muss |
| S2 | **Parametergruppen** (Unterbereiche von S1): Karte & Format · Grundform · Astschicht · Sternschicht 1 · Sternschicht 2 · Darstellung | T1 | Muss |
| S3 | **Prüfung** (Machbarkeit, Warnungen, Abhilfe) | T2 | Muss |
| S4 | **Sticken** (Stichfolge nachvollziehen/mitsticken) | T3 | Muss (Umfang: E2) |
| S5 | **Lochmuster** (Druckvorlage 1:1 mit Druckhinweisen) | T4 | Muss |
| S6 | **Anleitung** (Arbeitsanweisung) | T5 | Muss (Bildschirm oder nur PDF: E7) |
| S7 | **Ausgabe** (PDF wählen, ansehen, teilen, drucken) | T4, T5 | Muss |
| S8 | **Meine Entwürfe** | T6 | Soll (E3) |
| S9 | **Vorlagen / Start** | T6, T7 | Soll (E4) |
| S10 | **Hilfe / Glossar / Erststart** | T7 | Soll |
| S11 | **App-Einstellungen / Info** | – | Soll |

Wie diese Screens zu Navigation und Bereichen zusammengefasst werden, ist Teil des Konzepts, nicht der Analyse.

---

## 4. Funktionen je Screen

### S1 Muster / Editor
- Karte anzeigen (Format, Falz, Nutzfläche, Löcher mit Ampel, Stiche)
- Sofortige Rückmeldung auf jede Änderung (T1 lebt von Iteration)
- Zugriff auf alle Parametergruppen (S2); Zusammenfassung des aktuellen Musters
- Kennzahlen (Punkte, Stiche, Fadenlänge) und Prüfstatus (Ampel) dauerhaft erreichbar
- Rückgängig/Wiederholen, Zurücksetzen mit Rückfrage
- Karte zoomen/verschieben, um Löcher und enge Stellen zu beurteilen
- Einstieg zu S3, S4, S5–S7

### S2 Parametergruppen
- Alle Eingaben aus A.2, gruppiert; bedingte Eingaben nur zeigen, wenn wirksam — mit Hinweis, *warum* andere fehlen
- Aktueller Wert gut lesbar; Feineinstellung (±1); Standardwert je Gruppe
- Sichtbare Rückmeldung, wenn ein Wert wegen anderer Werte begrenzt oder angepasst wird (z. B. Schrittweite, Sternebene)
- Kurzerklärung je Begriff (Zugang zu S10)
- Format-Eingabe mit Validierung (positive mm-Werte, sinnvolle Grenzen) und Tastaturhilfe

### S3 Prüfung
- Alle Probleme mit Schwere (blockierend / knapp / Hinweis), Ursache und **konkreter Abhilfe mit direktem Sprung zum zuständigen Parameter**
- Betroffene Löcher in der Karte markieren (nicht nur farblich), dorthin zoomen
- Erklärung des Mindestabstands und des Stichlimits
- Zustand „kritisch“: klar erklären, warum Stiche/Wiedergabe/Ausgabe fehlen

### S4 Sticken
- Aktueller Schritt groß: Nummer, VS-Anweisung („von → nach“), anschließender RS-Sprung
- Schritt vor/zurück, Sprung zu Ast/Schicht, Fortschritt „n / gesamt“, Position merken
- Automatische Wiedergabe mit einstellbarem Tempo (Betrachten) und manueller Modus (Mitsticken)
- Karte mit hervorgehobenem aktuellem Segment, automatischer Ausschnitt/Zoom
- Display bleibt an; Fadenlänge und Fadenwechsel je Schicht

### S5 Lochmuster
- Maßstabsgetreuer Plan (Zuschnitt, Falzlinie, Rahmen, Löcher, Kontrollbalken)
- Papierformat/-ausrichtung ablesbar, Warnung bei Zuschnitt > A4 (Verkleinerung ⇒ nicht zum Anstechen)
- Hinweise: 100 % / „Tatsächliche Größe“, Kontrollbalken nachmessen
- Ausgabe starten (S7)

### S6 Anleitung
- Ebenenübersicht, Flocke (Arm 1 von n als Schrittdiagramm + Tabelle), Sterne, Fadenlängen, Legende VS/RS
- Gliederung/Sprungmarken; auf dem Bildschirm lesbar (falls E7 = ja)
- Ausgabe starten (S7)

### S7 Ausgabe
- PDF wählen (Lochmuster, Anleitung), Vorschau, Teilen, AirPrint, in Dateien sichern
- Status beim Erzeugen; Fehlermeldung; Sperre bei kritischem Zustand **mit Erklärung**
- Druckhinweise gut sichtbar

### S8 Meine Entwürfe · S9 Vorlagen · S10 Hilfe · S11 Einstellungen
- S8: Liste mit Vorschaubild, Name, Datum; neu, duplizieren, umbenennen, löschen; Import/Export als Datei
- S9: Beispielmuster mit Vorschau; „Als Entwurf übernehmen“
- S10: Erststart-Einführung (kurz), Glossar, Erklärung Mindestabstand/Schrittweite/Sternebene; Kontexthilfe aus S2
- S11: Standardwerte, Darstellung (Hell/Dunkel/System), Zurücksetzen, Version, Datenschutz, Impressum

---

## 5. Zu erwartende Layout-Probleme je Screen — iPhone vs. iPad

Die Probleme ergeben sich aus den **Inhalten** (Kartenverhältnisse, Lochgröße, Parameterzahl, A4-Dokumente) und aus den Gerätegrößen — nicht aus einer bestehenden Oberfläche.
Kürzel: **iPh-H** iPhone hoch · **iPh-Q** iPhone quer · **iPad-H** iPad hoch · **iPad-Q** iPad quer · **iPad-S** iPad im Teilfenster.

### S1 Muster / Editor

| Problem | iPhone | iPad |
|---|---|---|
| **Karte und ≈ 25 Eingaben konkurrieren um Platz.** Eine A6-Hochkarte ist bei 358 pt Breite ≈ 505 pt hoch; nutzbar sind ≈ 700 pt Höhe | **iPh-H:** Karte und Regler können nicht gleichzeitig groß sein; es braucht ein Modell, in dem die Karte bei jeder Reglerbewegung sichtbar bleibt (z. B. verkleinerbare/umschaltbare Vorschau, Sheet mit Höhenstufen) | **iPad-H:** Aufteilung oben/unten oder Seitenspalte; **iPad-Q:** Seitenspalte; beides erfordert flexible, nicht feste Spaltenbreiten |
| **Kartenverhältnis variabel** (hoch, quer, eigenes Format, extrem schmal/breit) | A6 quer ist nur ≈ 255 pt hoch → viel freier Platz; extremes eigenes Format braucht Begrenzung | die Karte muss in jeder Fensterform sinnvoll „passen“ |
| **iPhone quer:** nutzbare Höhe ≈ 340 pt | **iPh-Q:** Hochkarte ≤ ~300 pt hoch → Löcher ≈ 2–3 pt; Regler kaum parallel unterzubringen → Querformat braucht eigenes Konzept (Vollbild-Karte + Seitenleiste oder Regler per Sheet) | – |
| **Löcher sind winzig** (Ø ≈ 3 pt; Mindestabstand ≈ 11 pt) | Zoom/Pan nötig; Warnmarkierungen müssen unabhängig vom Maßstab gut sichtbar sein; Zoomgeste darf nicht mit Scrollen/Sheet-Ziehen kollidieren | etwas größer, Prinzip gleich |
| **Kennzahlen + Prüfstatus müssen sichtbar bleiben**, ohne die Karte zu verdrängen | kompakte Statusleiste statt eigener Fläche | kann großzügiger ausfallen |
| **Safe Areas / Dynamic Island / Home-Indikator** | Bedienelemente am unteren Rand dürfen nicht mit dem Home-Indikator oder Sheet-Griff kollidieren | Stage-Manager-Fensterrand, Querformat-Aussparungen |
| **Hell/Dunkel + feste Kartonfarbe** (Elfenbein bis Mitternachtsblau) | Karte muss sich vom Systemhintergrund in beiden Modi abheben (Rahmen/Schatten/Untergrund) | gleich |

### S2 Parametergruppen

| Problem | iPhone | iPad |
|---|---|---|
| **Viele Eingaben mit Abhängigkeiten** | Gruppierung, Reihenfolge und „Zusammenfassung statt Detail“ nötig; sonst langes Scrollen ohne Orientierung | Gruppenliste links, Detail rechts möglich |
| **Bedingte Eingaben** erscheinen/verschwinden | Layout darf nicht springen; Platzhalter oder Hinweis, warum etwas fehlt | gleich |
| **Gegenseitige Begrenzungen** (n → Strahlen → k → Ausblendung) | Änderung eines Werts kann einen anderen verändern — das muss sichtbar werden | gleich |
| **Wertwahl per Finger:** Daumen verdeckt Regler; Bereiche wie 3–55° oder 0–150 % sind fein | große Wertanzeige, Feinschritte, für kleine Ganzzahlbereiche (3–16, 1–6, 0–2) Alternativen zu Reglern | Zeiger/Pencil präziser; trotzdem ±-Bedienung vorsehen |
| **Lange Optionstexte** („Sternlevel und darunter weglassen“, „8 Strahlen (jeder 1.)“) | schmale Breite → Umbruch/Kürzung; Beschriftung und Auswahl auf eigene Zeilen | passt eher |
| **Tastatur bei Formateingabe** | verdeckt Felder, `decimalPad` ohne Return | Hardware-Tastatur: Tab-Reihenfolge |
| **Live-Neuberechnung beim Ziehen** | auf älteren iPhones bei großen Mustern evtl. spürbar (messen); Eingabe darf nicht ruckeln | Reserve größer |
| **Erklärtexte** zu fachlichen Begriffen | Platz knapp → ausklappbar/verlinkt statt dauerhaft | dauerhaft möglich |

### S3 Prüfung

| Problem | iPhone | iPad |
|---|---|---|
| **Zustand „kritisch“ entzieht Stiche, Wiedergabe und Ausgabe** | die Erklärung muss dort stehen, wo der Nutzer das Fehlen bemerkt (Karte, gesperrte Taste), nicht nur in einer Liste | gleich; mehr Platz für Erklärung neben der Karte |
| **Abhilfe liegt bei anderen Parametern** (Zoom, n, Ebenen) | Sprung/Direktbedienung nötig, ohne die Karte zu verlassen | Seitenspalte erlaubt gleichzeitige Sicht |
| **Mehrere Warnungen gleichzeitig** | Priorisierung (blockierend zuerst), Platz begrenzt | Liste möglich |
| **Farbe allein reicht nicht** (orange/rot, kleine Punkte) | zusätzlich Form/Text/Zahl; VoiceOver-Beschreibung | gleich |
| **Problemstellen sind winzig** | automatisches Zoomen auf die Stelle | gleich |

### S4 Sticken

| Problem | iPhone | iPad |
|---|---|---|
| **Gerät liegt neben dem Karton, Hände belegt** | große Tasten (≥ 56 pt) im Daumenbereich, wenig Ablenkung | iPad im Ständer: Tasten links/rechts, Hardware-Tasten; große Schrift aus Distanz |
| **Bis ~600 Schritte** | Schieberegler als Hauptsteuerung ungeeignet (≈ 0,3 pt je Schritt); Feinwahl per Tasten, grobe Sprünge per Ast/Schicht | gleich |
| **Anweisung muss lesbar sein, die Karte ist es oft nicht** | Textanweisung als eigenes Element, Karte mit Auto-Zoom auf aktuelle Stelle | Textspalte neben Karte |
| **Bildschirm dunkelt ab / dreht** | Idle-Timer deaktivieren; Rotation darf Position nicht verlieren | iPad-S: Fensterwechsel |
| **Karte + Anweisung + Tasten + Fortschritt gleichzeitig** | **iPh-H** ist sehr eng; **iPh-Q** noch enger (≈ 340 pt Höhe) | **iPad-Q** komfortabel |
| **Animationsgeschwindigkeit** | schnelle Auto-Wiedergabe zum Betrachten ≠ Tempo zum Sticken | gleich; „Bewegung reduzieren“ beachten |

### S5 Lochmuster

| Problem | iPhone | iPad |
|---|---|---|
| **Bildschirm ≠ 1:1** | darf keinen Maßstab versprechen; Hinweis „nur gedruckt maßgetreu“ | gleich |
| **A6 + Falz = 210 × 148 mm ⇒ A4 quer** | Querseite im Hochformat-Screen: ~358 × 253 pt, Zoom nötig | passt gut (besonders iPad-Q) |
| **Zuschnitt > A4 (eigenes Format)** | Verkleinerungswarnung gut sichtbar; ggf. Kachel-Druck (E8) | gleich |
| **Druckskalierung durch den Systemdialog** | Hinweis „100 % / Tatsächliche Größe“ muss vor dem Druck gelesen werden; Kontrollbalken erklären | gleich; AirPrint-Dialog mit Ankerpunkt |

### S6 Anleitung

| Problem | iPhone | iPad |
|---|---|---|
| **Inhalt ist für A4 gedacht** (Diagramme mit vielen Beschriftungen, Tabellen mit 3 Spalten) | Schrittdiagramme auf ~358 pt Breite nicht lesbar → Zoom/Scrollen, Hochkant→Quer, oder eigene Bildschirmfassung (E7) | A4-Breite fast erreicht; Diagramme noch klein, Zoom sinnvoll |
| **Lange, gegliederte Dokumente** | Navigation (Teile) nötig | Inhaltsverzeichnis als Seitenleiste |
| **Tabellen** | Spaltenbreite/Umbruch bei Kürzeln (z. B. „E2L.1a → E2L“) | gleich bzw. luftig |
| **Zwei Darstellungen (Bildschirm vs. Druck)** | Bildschirm- und Druckfassung nicht zwingend identisch | gleich |

### S7 Ausgabe

| Problem | iPhone | iPad |
|---|---|---|
| **PDF-Vorschau (A4) im kleinen Fenster** | A4-Hoch ≈ 358 pt breit → Detail nur mit Zoom; Querseiten (Lochmuster) noch kleiner | gut lesbar |
| **Aktionen Teilen / Drucken / Sichern + Hinweise** | Platz für Hinweise und Aktionen teilen; wichtigste Druckhinweise dürfen nicht untergehen | Popover-Verhalten für Teilen/Drucken beachten |
| **Erzeugungsdauer** | Fortschrittsanzeige; Bedienung darf nicht einfrieren (messen) | gleich |
| **Zustand „kritisch“** | Sperre mit Begründung und Weg zur Abhilfe | gleich |

### S8–S11 (neue Screens)

| Problem | iPhone | iPad |
|---|---|---|
| Listen mit Vorschaubildern (Entwürfe, Vorlagen) | einspaltig, Wischaktionen, Vorschaubilder effizient erzeugen | Raster oder Sidebar |
| Hilfe/Glossar | kurze Detailseiten, Kontextlinks aus Parametern | Sidebar + Text |
| Erststart | wenige, überspringbare Schritte | gleiche Inhalte, mehr Raum |
| Einstellungen | kurze Liste | Detailbereich |
| Datenmodell | Wechsel von Einzelstand zu mehreren Entwürfen braucht Schema + Migration (heutige Speicherung ist tolerant gegenüber neuen Feldern) | gleich |

### Querschnitt (alle Screens)

| # | Thema | Erwartung |
|---|---|---|
| Q1 | **Breitenabhängigkeit** | Alle Screens müssen von ~320 pt bis > 1300 pt kontinuierlich funktionieren |
| Q2 | **Höhe als Engpass** | iPhone quer (~340 pt) und iPad mit Tastatur |
| Q3 | **Dynamic Type** | größte Schriftstufen dürfen keine Bedienelemente abschneiden |
| Q4 | **Barrierefreiheit der Grafik** | Karte, Diagramme und Lochmarkierungen brauchen sprachliche Entsprechungen |
| Q5 | **Zustandserhalt** | Auswahl, Scroll-/Zoomposition und Sticken-Fortschritt bei Rotation, Fensterwechsel, App-Neustart |
| Q6 | **Hell/Dunkel** | Karten- und Diagrammdarstellung in beiden Modi prüfen |
| Q7 | **Verifikation ohne Mac** | Ohne Screenshot-Matrix (Geräte × Ausrichtung × Schriftgröße × Hell/Dunkel) bleiben Layoutaussagen Vermutungen |

---

## 6. Prioritäten aus der Analyse

1. **Karte und Parameter in direkter Rückkopplung** — das ist der zentrale Layoutkonflikt auf dem iPhone und bestimmt die Grundstruktur.
2. **Breiten- und höhenabhängiges Layout** statt Gerätetyp-Entscheidung; iPhone quer und iPad-Teilfenster sind Sonderfälle mit eigenem Konzept.
3. **Prüfen und Beheben aus einem Guss** (Warnung → Ursache → Parameter), weil der Zustand „kritisch“ das Ergebnis blockiert.
4. **Sticken als eigener, ruhiger Modus** (falls E2 = ja).
5. **Druck-Ergebnisse (Lochmuster, Anleitung) klar von Bildschirmdarstellung trennen**; Bildschirm ist nie 1:1.
6. **Einarbeitung** (Begriffe, Vorlagen) mitdenken, nicht nachträglich anhängen.

---

## 7. Festgelegte Entscheidungen (Stand der Klärungsrunde) und ihre Folgen

| # | Thema | Entscheidung | Folge fürs Konzept |
|---|---|---|---|
| E2 | Mitsticken | **Nebenfunktion** | Kein eigener Sticken-Modus, keine Display-Sperre/Fortschrittsspeicherung nötig. Die Stichfolge bleibt eine **Ansichtsfunktion** zum Verstehen des Musters (Wiedergabe) — Screen S4 entfällt als eigener Bereich. |
| E3 | Entwürfe | **Letzter Stand + Favoriten** | Kein vollständiges Projektarchiv. Es gibt einen Arbeitsstand („Weitermachen“) und eine kleine Favoritenliste. S8 wird zu „Favoriten“ (Teil der Startseite). |
| E7 | Anleitung | **Nur als PDF** | Keine Bildschirmfassung der Anleitung (S6 entfällt als eigener Screen). Anleitung und Lochmuster sind reine **Ausgabeprodukte** (S7); der Bildschirm zeigt sie in einer PDF-Vorschau. Layoutthema „Anleitung lesbar auf dem Handy“ wird zur PDF-Vorschau-Frage (Zoom, Seitenwahl). |
| E6 | Zielgruppe | **Gestuft einfach/erweitert, plus geführter Einstieg, plus 10 fertige Muster** | Drei Wege zum Muster: (1) **Geführter Weg** für Einsteiger, (2) **fertige Muster**, (3) **freier Editor** mit Einfach-/Experten-Stufe. |
| – | Leitgerät | **iPhone und iPad gleichrangig** | Zwei eigenständig gestaltete Layouts, keine „Hochskalierung“ und keine „reduzierte“ Fassung. |
| E1 | Verteilung | **Noch offen** | Pflichtangaben (Datenschutz, Impressum, Privacy-Manifest) im Konzept vorsehen, aber nicht ausgestalten. |
| E11 | Hell/Dunkel | **System folgen** | Kein eigener Schalter; Kartonfarbe ist Inhalt. |
| E6b | Formate | **Standardformate im Normalmodus, Eigenformat nur im Expertenbereich** | Eigenformat nur in der erweiterten Stufe. |
| E8 | Zuschnitt > A4 | **Eigenformate auf A4-Zuschnitt begrenzen** | Eingabe wird validiert: Zuschnitt (bei Falz doppelte Fläche) muss mit 10 mm Rand auf A4 hoch **oder** quer passen. Folge: **kein Kachel-Druck**, keine Verkleinerungswarnung mehr nötig; größtes sinnvolles gefaltetes Format ist A6 (A5 gefaltet = 296 mm Zuschnittsbreite passt nicht auf A4). Die zulässigen Maximalmaße sind im Konzept sichtbar zu machen. |
| E9 | iOS-Version | **iOS 17** | `@Observable`, `sensoryFeedback`, verbesserte Scroll-/Sheet-APIs nutzbar. |
| E12 | Sprache | **Deutsch, für Mehrsprachigkeit vorbereitet** | Texte von Anfang an in String-Katalogen. |
| – | Rückgängig | **Nur „Auf Ausgangswert zurücksetzen“** (mit Rückfrage) | Kein Verlauf/Undo. Zurücksetzen auf Gruppen- und Gesamtebene. |
| – | Bild-Export | **Später** | Platz im Ausgabebereich vorsehen, kein Bestandteil des ersten Konzepts. |
| – | Start | **Startseite** | Zentrale Einstiegsseite: Weitermachen · Geführter Weg · 10 fertige Muster · Favoriten. |
| – | Geführter Weg | Legt Format/Falz, Grundstil, Aufwand/Komplexität und Farben fest; **einfache Bedienung, keine komplexen Einstellungen, Ergebnis immer „ready-to-use“ und schön** | Der Weg muss intern **immer ein gültiges, hübsches, druckbares Muster** erzeugen (keine „kritisch“-Zustände, innerhalb Stichlimit). Technisch: Zuordnung Aufwand → Parameter-Set (n, Ebenen, Sternschichten), nicht freie Eingabe. |
| – | Fertige Muster | 10 Stück, Anzeige: **Vorschaubild + Name + Schwierigkeit/Aufwand**, **als Entwurf übernehmbar** | Kuratierter, fester Inhalt (Presets). Keine Kurzbeschreibung. Schwierigkeit lässt sich aus Stichzahl/Fadenlänge ableiten. |

### 7.1 Auswirkungen auf die Screenliste (Abschnitt 3)

| Screen | Status |
|---|---|
| S1 Muster / Editor | bleibt, mit **Einfach/Experte**-Stufen |
| S2 Parametergruppen | bleibt; Einfachstufe zeigt nur wenige Hauptparameter |
| S3 Prüfung | bleibt; im Geführten Weg und in den fertigen Mustern tritt „kritisch“ nie auf |
| S4 Sticken | **entfällt als Modus**; Stichfolge als Ansichtsfunktion im Editor |
| S5 Lochmuster | bleibt als Ausgabeprodukt (PDF) |
| S6 Anleitung | **entfällt als Screen**; nur PDF |
| S7 Ausgabe | bleibt; Lochmuster- und Anleitungs-PDF, Teilen, AirPrint |
| S8 Entwürfe | wird **Favoriten** + „Weitermachen“ |
| S9 Vorlagen | wird **„10 fertige Muster“** |
| S10 Hilfe/Glossar | bleibt (wichtig wegen Einsteiger-Zielgruppe) |
| S11 Einstellungen/Info | bleibt, kleiner (kein Hell/Dunkel-Schalter) |
| **Neu: Startseite** | zentraler Einstieg |
| **Neu: Geführter Weg** | mehrstufiger Assistent (Format/Falz → Stil → Aufwand → Farben → Ergebnis) |

### 7.2 Auswirkungen auf die Layout-Probleme (Abschnitt 5)

- Entfallen: Sticken-spezifische Probleme (Daumenbereich, Display-Sperre, Mitstick-Tempo) und die Bildschirmfassung der Anleitung.
- Neu zu beachten: **Startseite** (Karten/Raster aus Vorschaubildern, iPhone ein- bis zweispaltig, iPad Raster), **Geführter Weg** (Schrittanzeige, große Auswahlkarten, Live-Vorschau des entstehenden Musters neben/über den Fragen), **Muster-Galerie** (10 Vorschaubilder, Schwierigkeit lesbar).
- Weiterhin entscheidend: Karte und Parameter in direkter Rückkopplung (Editor), Zoom auf kleine Löcher, Breiten-/Höhenabhängigkeit (iPhone quer, iPad-Teilfenster), PDF-Vorschau auf kleinen Displays.
- Vorschaubilder (Favoriten, Muster) müssen effizient aus dem Kartenmodell erzeugt werden (Cache, kein Neuberechnen pro Zelle).

---

## 8. Noch offen

| # | Frage | Stand |
|---|---|---|
| E5 | Wie prüfen wir Layouts ohne Mac (Simulator-Screenshots in der CI)? | **offen — Voraussetzung für das Design** |
| O1 | Welche Parameter bilden die **Einfachstufe** des Editors? | Vorschlag im Konzept |
| O2 | Welche **zehn** Muster werden angeboten (Auswahl/Kuratierung)? | Design-/Inhaltsschritt |
| O3 | Wie definieren wir **Schwierigkeit/Aufwand** (Stichzahl, Fadenlänge, Schichten)? | Vorschlag im Konzept |
| O4 | **Favoriten:** Anzahl, Benennung, Löschen, Sortierung? | Konzept |
| O5 | **Umfang der Hilfe** (Erststart, Glossar, Kontexthilfe)? | Konzept |
| E1 | Verteilungsweg (App Store oder nicht)? | bewusst offen |
| E10 | Mac („iPad-App auf Mac“): tolerieren? | Vorschlag: tolerieren, nicht gestalten |

---

## 9. Vorgehen danach

1. E5 klären (wie Layouts ohne Mac sichtbar werden), O1–O5 als Vorschläge im Konzept ausarbeiten.
2. **Gemeinsames UI-Konzept:** Navigationsmodell (Startseite, Editor, Geführter Weg, Galerie, Favoriten, Ausgabe, Hilfe), Layout-Regeln je Breiten-/Höhenstufe für iPhone und iPad, Komponentenliste.
3. **Design** (separater Schritt): visuelle Sprache, Komponenten, Prototyp je Gerät.
4. Umsetzung in `ios/App` mit Screenshot-Matrix in der CI.
