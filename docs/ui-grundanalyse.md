# Stickkarten (native iOS-App unter `/ios`) — UI-Grundanalyse

Status: Entwurf zur gemeinsamen Diskussion · **keine Design-Entscheidungen**, nur Bestandsaufnahme und Anforderungen.
Nächster Schritt (separat): gemeinsames UI-Konzept → danach Design.

Bezugsgröße ist ausschließlich die SwiftUI-App unter `ios/` (Branch `claude/friendly-bell-9n9w83`, Stand `48c0296`).
Die Web-App (`src/StickkartenGeneratorV4.jsx`) ist nur fachliche Referenz und **nicht** Gegenstand dieser Analyse.
(Eine frühere Fassung dieses Dokuments bezog sich fälschlich auf die Web-App; sie ist hiermit ersetzt.)

## 0. Ausgangslage

### 0.1 Was die App heute ist

- Native SwiftUI-App, **iOS ≥ 16.0**, iPhone und iPad (`TARGETED_DEVICE_FAMILY 1,2`), alle Orientierungen (iPhone ohne Kopfüber), eine Szene (`project.yml`).
- Fachlogik als Swift-Package `StickCore` (Graph, Stichfolge, Abstandsprüfung, Fadenlänge, Anleitungs-Diagramme) plus `StickPDF` (Vektor-PDF: Lochmuster 1:1, mehrseitige Anleitung). Per Golden-Tests gegen die Web-App abgesichert — **die Logik steht, offen ist die Oberfläche.**
- Zustand: ein einziger Stand (`StickSettings` + `AppearanceSettings`) als JSON in `UserDefaults`, Neuberechnung bei jeder Änderung (`AppModel`).
- Entwicklung **ohne Mac**: Build und Tests nur über GitHub Actions (`macos-latest`); es gibt keine UI-Tests und keine Simulator-Screenshots.

### 0.2 Aufbau der Oberfläche heute

| Bestandteil | Datei | Verhalten |
|---|---|---|
| Container | `ContentView.swift:10-41` | `NavigationStack`; Toolbar rechts: *Drucken & Teilen*, *Einstellungen* |
| **Breite Größenklasse** (`hSize == .regular`) | `ContentView.swift:13-19` | `HStack`: `ControlsView` **fest 400 pt** · Divider · `PreviewPane` |
| **Kompakte Größenklasse** | `ContentView.swift:20-27` | `TabView` mit zwei Tabs: *Vorschau* · *Muster* |
| Vorschau | `PreviewPane.swift`, `PreviewCanvas.swift` | `ScrollView`: Karte (max. 560 pt hoch) → Wiedergabeleiste → Warnungen → Statistik → Legende |
| Muster (Regler) | `Controls.swift` | `Form` mit Sektionen Grundform, Astschicht, Sternschicht 1, Sternschicht 2, „Alle Regler zurücksetzen“ |
| Einstellungen | `SettingsView.swift` (Sheet) | Sektion *Karte* (Format, Eigenes Format, Falz, **Zoom**) und *Darstellung* (Kartonfarbe, Fadenfarbe, zwei Schalter) |
| Drucken & Teilen | `ExportView.swift` (Sheet) | Segment *Lochmuster 1:1 / Anleitung*, `PDFView`-Vorschau, *Teilen* (`ShareLink`), *AirPrint* |

Es gibt **keine** eigene Anleitung auf dem Bildschirm (nur PDF), **keine** Hilfe/Erklärungen, **keine** mehrere Entwürfe, **keine** Vorlagen.

---

## 1. Was braucht eine App allgemein?

| # | Bereich | Inhalt | Stand in der iOS-App | Relevanz |
|---|---|---|---|---|
| 1.1 | **Informationsarchitektur / Navigation** | Wo bin ich, wie komme ich zurück; Haupt- vs. Nebenfunktionen | Tabs (iPhone) bzw. Zwei-Spalten (iPad); `NavigationStack` ohne Push-Ziele; Zoom steckt in den Einstellungen | hoch |
| 1.2 | **Onboarding / Hilfe** | Begriffe (Kreispunkt, Ebene, Sternschicht, Schrittweite, VS/RS, Mindestabstand), Erststart | nicht vorhanden | hoch |
| 1.3 | **Kern-Workflow** | Entwerfen → Prüfen → Sticken → Drucken | nur lose Abfolge, kein Sticken-Modus | hoch |
| 1.4 | **Eingabe** | Regler, Auswahl, Zahlenfelder, Schalter; Abhängigkeiten | vorhanden (`Form`), 15+ Steuerelemente | hoch |
| 1.5 | **Rückmeldung / Fehler / Leerzustände** | Warnungen, Erklärung, Abhilfe | Warnbox in der Vorschau; Abhilfe verweist auf Bedienelemente an anderer Stelle | hoch |
| 1.6 | **Persistenz** | Letzter Stand, mehrere Entwürfe, Vorlagen | nur *ein* Stand (`UserDefaults`) | hoch |
| 1.7 | **Export / Teilen / Drucken** | PDF, Teilen-Menü, AirPrint, Dateien | vorhanden (`ShareLink`, `UIPrintInteractionController`) | hoch |
| 1.8 | **App-Einstellungen** | Darstellung, Standardwerte, Info | vermischt mit Karteneinstellungen | mittel |
| 1.9 | **Barrierefreiheit** | VoiceOver, Dynamic Type, Kontrast, nicht nur Farbe, „Bewegung reduzieren“ | Systemsteuerelemente ja; Canvas, Legende, Punktfarben nein | hoch |
| 1.10 | **Performance** | Live-Neuberechnung beim Ziehen, PDF-Erzeugung | Berechnung und PDF laufen im Hauptthread (siehe 5.3, 5.7) | mittel |
| 1.11 | **Plattform-Pflichten für die Verteilung** | App-Symbol ✓, Startbildschirm (leer `UILaunchScreen`), Privacy-Manifest (UserDefaults ist „Required-Reason-API“), Datenschutz-URL, Impressum/Händlerstatus, Altersfreigabe | teilweise (Icon, Export-Compliance) | je nach Verteilweg (E1) |
| 1.12 | **Lokalisierung** | Strings, Zahlenformat | Deutsch hartkodiert | später |
| 1.13 | **Fehlertoleranz** | Rückgängig, Zurücksetzen, Eingabevalidierung | Zurücksetzen ohne Rückfrage; kein Undo; keine Validierung der mm-Felder | mittel |
| 1.14 | **Test- und Prüfbarkeit der UI** | Layout je Gerät verifizieren | **fehlt** — ohne Mac nur Build-Test (siehe 5.9) | hoch |

---

## 2. Allgemeine Regeln für iPhone und iPad (SwiftUI, iOS ≥ 16)

### 2.1 Plattformregeln

| Thema | Regel | Konsequenz für uns |
|---|---|---|
| **Touch-Ziele** | mind. 44 × 44 pt, Abstand ≥ 8 pt | Wiedergabe-Icons sind 28 × 28 pt Symbole in `.bordered`-Buttons (`PreviewPane.swift:28,33`) → Trefferfläche real prüfen |
| **Größenklassen statt Gerätetyp** | Layout nach `horizontalSizeClass`/`verticalSizeClass` bzw. tatsächlicher Breite | iPad ist **nicht** immer „regular“ (Split View/Slide Over/Stage Manager); großes iPhone quer kann „regular“ sein |
| **Safe Areas** | System berücksichtigt sie, solange nichts per `ignoresSafeArea` überschrieben wird | Querformat: seitliche Aussparung, unten Home-Indikator → Inhalt am Rand beachten |
| **Dynamic Type** | Text über Text-Styles (`.footnote`, `.headline`) skaliert automatisch | gilt für `Form` und Statistik; **nicht** für Canvas-Inhalte; bei größter Schrift brechen 3-Spalten-Reihen (Statistik) |
| **Navigation** | iPhone: Hierarchie/Tabs/Sheets; iPad: `NavigationSplitView`/Sidebar | iOS 16 bietet `NavigationSplitView`, `presentationDetents` (Sheets mit Höhenstufen), `ViewThatFits`, `Grid` |
| **Sheets** | Unter iOS 16 mit Detents (`.medium/.large`) und Drag-Indikator | passend für „Regler über der Karte“ |
| **Tastatur** | `decimalPad` hat **keine** Return/Fertig-Taste | Eigenes-Format-Felder brauchen eine Tastatur-Toolbar |
| **Darstellung** | System-Hell/Dunkel; System-Farben | App folgt dem System (Systemfarben); Kartenfarbe bleibt fest → Kontrast zum Hintergrund prüfen |
| **Bewegung** | `accessibilityReduceMotion` beachten | Auto-Wiedergabe der Stichfolge optional/ruhig |
| **Haptik / Rückmeldung** | `UIImpactFeedbackGenerator` (iOS 16); `.sensoryFeedback` erst iOS 17 | Einrasten bei ganzzahligen Reglern möglich |
| **Hardware-Tastatur / Pointer (iPad)** | `keyboardShortcut`, Hover-Effekte | Leertaste = Play, Pfeile = Schritt |
| **Multitasking** | Ohne `UIRequiresFullScreen` ist die App in Split View/Stage Manager nutzbar (aktuell der Fall) | Fensterbreite zwischen ~320 und Vollbild; Layout muss darauf reagieren |
| **Display-Sperre** | `UIApplication.shared.isIdleTimerDisabled` | für den Mitstick-Modus |
| **Drucken/Teilen** | `ShareLink`, `UIPrintInteractionController` (auf iPad Ankerposition/Popover beachten), `fileExporter` | vorhanden; iPad-Verhalten des Druckdialogs ungetestet |
| **Läuft auch auf Mac/Vision** | Bei `TARGETED_DEVICE_FAMILY 1,2` läuft die App ohne Zutun auf Apple-Silicon-Macs („iPad-App auf Mac“) | Fenster frei skalierbar, Maus statt Touch — mitdenken, nicht priorisieren |

### 2.2 Größenklassen-Matrix (Näherung)

| Situation | Breite × Höhe (Klasse) |
|---|---|
| iPhone SE/mini/Standard hoch | compact × regular (375–393 pt breit) |
| iPhone Pro Max hoch | compact × regular (430–440 pt) |
| iPhone quer (Standard) | compact × compact (Höhe ~340–390 pt) |
| iPhone Plus/Max quer | **regular** × compact |
| iPad Vollbild hoch/quer | regular × regular (744–1032 bzw. 1133–1376 pt breit) |
| iPad Split View 1/3, Slide Over | compact × regular (~320–400 pt breit) |
| iPad Split View 1/2, 2/3, Stage Manager | je nach Breite compact oder regular |

Aus der Tabelle folgt: Mit nur **einer** Weiche (`hSize == .regular`) wie heute lassen sich weder „großes iPhone quer“ noch „iPad im Zwei-Drittel-Fenster“ sinnvoll bedienen.

---

## 3. Welche Screens braucht die App?

| # | Screen | Zweck | In der iOS-App heute | Priorität |
|---|---|---|---|---|
| S1 | **Editor / Vorschau** | Karte ansehen, Stichfolge abspielen, Kennzahlen | `PreviewPane` (Tab bzw. rechte Spalte) | Muss |
| S2 | **Muster (Parameter)** — Unterbereiche: S2a Grundform · S2b Astschicht · S2c Sternschicht 1 · S2d Sternschicht 2 | Muster gestalten | `ControlsView` (eine lange `Form`) | Muss |
| S3 | **Karte & Format** | Format, Falz, **Zoom/Musterradius**, Randmaße | im Einstellungs-Sheet versteckt | Muss (umziehen) |
| S4 | **Darstellung** | Kartonfarbe, Fadenfarbe, Restmuster, Sprünge | im Einstellungs-Sheet | Muss |
| S5 | **Prüfung / Hinweise** | Probleme verstehen und beheben | Warnbox am Ende der Vorschau | Muss |
| S6 | **Sticken (Mitstick-Modus)** | Stich für Stich nachvollziehen | Wiedergabeleiste in S1 | Muss (Konzept offen, E2) |
| S7 | **Anleitung (Bildschirm)** | Arbeitsanweisung lesen | nur PDF in S9 | Soll |
| S8 | **Lochmuster 1:1** | Druckvorlage zum Anstechen | PDF in S9 | Muss |
| S9 | **Drucken & Teilen** | PDF wählen, ansehen, teilen, drucken | `ExportView` (Sheet) | Muss |
| S10 | **App-Einstellungen / Info** | Standardwerte, Version, Datenschutz | Mix mit S3/S4 | Soll |
| S11 | **Meine Entwürfe** | speichern/laden/duplizieren | nicht vorhanden | Soll (E3) |
| S12 | **Vorlagen / Start** | Beispiele als Einstieg | nicht vorhanden | Soll (E4) |
| S13 | **Hilfe / Glossar / Erststart** | Begriffe erklären | nicht vorhanden | Soll |

---

## 4. Funktionen je Screen

### S1 Editor / Vorschau
- Kartenvorschau (Format, Falz, Nutzfläche, Löcher nach Abstand eingefärbt, Stiche, Sprünge, aktives Segment)
- Wiedergabe: Play/Pause, Zurück zum Anfang, Positionsregler (bis ~600 Segmente), Zähler „n / max“
- Kennzahlen: Punkte, Stiche, Fadenlänge (+15 %)
- Warnungen, Legende
- Zugang zu S2–S6, S9; **fehlend:** Zoom/Verschieben der Karte, Rückgängig

### S2 Muster
| Bereich | Steuerelemente | Abhängigkeiten |
|---|---|---|
| Grundform | Kreispunkte 3–16 | bestimmt Strahlen-Auswahl, k-Grenzen, Mindestradius |
| Astschicht | aktiv, Seitenäste, Ebenen 1–6, Astwinkel 3–55°, Astlänge 20–200 %, Wachstum 0–150 %, Fraktal-Tiefe 0–2, Fraktal-Skalierung 30–80 % | Seitenäste ab Ebene 2; Fraktal nur mit Seitenästen |
| Sternschicht 1 | aktiv, Sternebene (nur mit Astschicht), Strahlen (Teiler von n), Schrittweite, „Seitenäste bei diesem Sternlevel“, Schalter „zweite Schicht“ | Schrittweite-Maximum hängt von Strahlen/Astschicht ab; Ausblendung nur wenn wirksam |
| Sternschicht 2 | wie 1, plus Rotationsversatz | nur wenn Schicht 1 aktiv |
| Fußbereich | „Alle Regler zurücksetzen“ | zerstörend, ohne Rückfrage |

Anforderungen an alle Bereiche: Wert gut sichtbar, Feineinstellung, erklärende Hinweise, Rückmeldung bei automatischer Korrektur (z. B. wenn k gekürzt wird).

### S3 Karte & Format · S4 Darstellung
- Format (A6 hoch/quer, Eigenes Format mit Breite/Höhe in mm), Falzposition (links/oben/keine), **Zoom**, Hinweiszeile mit Radius/Faden/Rand/Mindestabstand
- Kartonfarbe, Fadenfarbe, „Restmuster als Vorschau“, „Rückseiten-Sprünge anzeigen“

### S5 Prüfung
- Alle Warnungen mit Schwere (blockierend / knapp / Hinweis) und **direkter Abhilfe** (Sprung zum zuständigen Regler)
- Markierung der betroffenen Löcher in der Karte; Erklärung des Mindestabstands

### S6 Sticken
- Aktueller Schritt groß: Nummer, VS-Anweisung („E2 → E3“), anschließender RS-Sprung (Beschriftungen liefert `StickCore` bereits für die Anleitung)
- Schritt vor/zurück, Sprung zu Ast/Schicht, Fortschritt, Tempo für Auto-Wiedergabe (heute fest 45 ms — zum Mitsticken zu schnell)
- Display bleibt an, Position wird gemerkt, Fadenlänge je Schicht

### S7 Anleitung (Bildschirm) · S8 Lochmuster · S9 Drucken & Teilen
- S7: Teile (Ebenen, Flocke, Sterne), Schritttabellen, Fadenlängen in lesbarer Bildschirmform
- S8: 1:1-Plan mit Falzlinie, Löchern, 50-mm-Kontrollbalken, Hinweis „A4, 100 %“, Verkleinerungswarnung bei Zuschnitt > A4
- S9: PDF-Auswahl, Vorschau, Teilen, AirPrint, Statusanzeige beim Erzeugen, Sperre bei kritischem Abstand mit Erklärung

### S10–S13
- S10: Info/Version, Datenschutz, Zurücksetzen, Standardwerte
- S11: Liste mit Vorschaubild, Name, Datum; neu/duplizieren/umbenennen/löschen
- S12: Beispielmuster mit Vorschau, „Als Entwurf übernehmen“
- S13: Glossar, kurze Einführung, Erklärtexte zu Mindestabstand, Schrittweite, Sternebene

---

## 5. Zu erwartende Layout-Probleme je Screen — iPhone vs. iPad

Quellenangaben beziehen sich auf den aktuellen Code. „Zu prüfen“ = aus dem Code abgeleitet, aber nicht auf einem Gerät/Simulator bestätigt (siehe 5.9).

### 5.1 Container / Navigation (`ContentView`)

| Problem | iPhone | iPad |
|---|---|---|
| **Vorschau und Regler sind getrennte Tabs** (`:21-26`) | **Kernproblem:** Beim Ändern eines Reglers ist die Karte nicht sichtbar; der Effekt muss durch Tab-Wechsel kontrolliert werden. Direkte Rückkopplung (Live-Ansicht) fehlt | – |
| **Fester 400-pt-Regler-Streifen** (`:16`) | **Quer, Plus/Max (regular):** Regler 400 pt, Vorschau bleibt bei ~430 pt Breite und ~340 pt Höhe → Karte winzig | **Hoch (744/820/834 pt):** Vorschau nur ~340–430 pt breit; **Split View 2/3 (~680 pt):** Vorschau ~280 pt; Regler dauerhaft belegen > 50 % |
| **Eine einzige Weiche** (`hSize == .regular`) | iPhone quer (Standard, compact) fällt auf Tabs zurück, obwohl dort Platz für nebeneinander wäre (aber wenig Höhe) | iPad im schmalen Fenster springt abrupt auf Tabs (Zustand der Tabs/Scrollposition geht verloren, zu prüfen) |
| **Toolbar** (`:32-36`) | zwei Icons rechts, Titel „Stickkarten“ ohne Funktion | gleiche Toolbar; für iPad wäre Titel/Aktionsgruppe mit mehr Platz möglich |
| **`NavigationStack` ohne Push-Ziele** | – | Master-Detail (`NavigationSplitView`) wäre das Standardmuster |
| **Exportknopf deaktiviert bei kritischem Abstand ohne Erklärung** (`:34`) | Nutzer sieht ein graues Symbol, erfährt nicht warum | gleich |

### 5.2 S1 Vorschau (`PreviewPane`, `PreviewCanvas`)

| Problem | iPhone | iPad |
|---|---|---|
| **Alles in einer `ScrollView`** (`:9-22`): Karte, Wiedergabe, Warnungen, Statistik, Legende | A6 hoch bei ~358 pt Breite ist ~505 pt hoch (`maxHeight 560`); auf ~700 nutzbaren pt bleibt kaum Platz → **Wiedergabeleiste, Warnungen, Statistik liegen unterhalb des sichtbaren Bereichs**; zum Bedienen der Wiedergabe muss man die Karte aus dem Bild scrollen | **Hoch:** passt; **quer (1133×~744):** Karte 560 pt + Leiste + Statistik + Legende > sichtbare Höhe → auch dort Scrollen nötig |
| **Querformat-Karte (A6 quer)** | Karte nur ~255 pt hoch → Rest der Fläche leer, genau hier hätte ein Sheet Platz | gleiche Logik, weniger kritisch |
| **iPhone quer (Höhe ~340 pt):** | Karte (hoch) ≤ ~300 pt hoch; Löcher ≈ 2–3 pt; Wiedergabeleiste unterhalb nicht erreichbar ohne Scrollen | – |
| **Wiedergabeleiste, 4 Elemente in einer Zeile** (`:26-44`) | 2 Buttons (28-pt-Symbole), Zähler (min. 62 pt), Regler bekommt ~170 pt für bis zu ~600 Positionen → ≈ 0,3 pt je Schritt; **Feinwahl per Finger unmöglich**, keine ±1-Tasten | genug Breite, Regler-Feinheit bleibt Problem |
| **Kein Zoom/Verschieben der Karte** | Löcher Ø 0,92 mm ≈ 3 pt, Mindestabstand 3,2 mm ≈ 11 pt (bei 105 mm ↔ 358 pt); der +0,25-mm-Aufmaß der Warnpunkte ist kaum sichtbar → Problemstellen nicht beurteilbar | größere Karte, Problem bleibt vorhanden |
| **Legende als verketteter `Text` mit Symbolen** (`:81-102`) | wird zum 3–4-zeiligen `.caption`-Absatz; Farbe als Hauptmerkmal; VoiceOver liest „━ ┅ ➤ ●“ | eine bis zwei Zeilen |
| **Statistik 3 Spalten** (`:63-69`) | bei großer Dynamic-Type-Stufe bricht „Fadenlänge (+15 %)“ um bzw. wird gekürzt | passt |
| **Warnbox unter der Karte** (`:47-61`) | Kritische Warnung (Stiche verschwinden!) steht außerhalb des Blickfelds → Karte wirkt „leer/kaputt“ | gleich, aber meist sichtbar |
| **Canvas ohne Accessibility** | Karte für VoiceOver unsichtbar; Zustand (knapp/zu gering) nur über Farbe | gleich |
| **Karten-/Hintergrundfarbe** | Systemhintergrund (hell/dunkel) + feste Kartonfarbe: Elfenbein auf hellem Grund, Tanne auf dunklem Grund → Rahmen/Kontrast prüfen | gleich |

### 5.3 S2 Muster (`ControlsView`)

| Problem | iPhone | iPad |
|---|---|---|
| **Lange einspaltige `Form`** (:45-117), bis zu 17 Steuerelemente pro Schicht | viel Scrollen; keine Orientierung („wo bin ich“), kein Einklappen der Sektionen | 400-pt-Streifen: dieselbe lange Liste, bei kleiner Höhe noch mehr Scrollen |
| **Regler zeigen Wert nur im kleinen Label** (`footnote`, `.secondary`, `Controls.swift:13`) | Daumen verdeckt Regler; Wert klein/blass → Feineinstellung (z. B. Astwinkel 3–55°, Schrittweite) ungenau | gleich |
| **Ganzzahlige Auswahl als Regler** (Kreispunkte 3–16, Ebenen 1–6, Fraktal 0–2) | Stepper/Segmente wären treffsicherer | gleich |
| **Bedingte Felder** (erscheinen/verschwinden) | Zeilen springen, Scrollposition rutscht; es fehlt der Hinweis *warum* etwas nicht da ist | gleich |
| **Stilles Anpassen** (`r.k1Eff`, `effTeiler`, `sternEbeneEff`): Wert ändert sich, wenn n/Ebenen verkleinert werden | keine Rückmeldung | gleich |
| **Abhängigkeitskette** (n → Strahlen → k → Ausblendung) | Reihenfolge der Bedienung unklar | Master-Detail würde Gruppen übersichtlicher machen |
| **Rückkopplung zur Karte fehlt** (siehe 5.1) | gravierend | nur im breiten Layout gelöst |
| **Neuberechnung im Hauptthread** (`AppModel.settings.didSet` → `StickModel.compute`, plus JSON-Speichern bei **jedem** Reglerschritt) | bei n = 16, 6 Ebenen, Fraktal 2 evtl. spürbar ruckelnd, besonders auf älteren iPhones (**zu messen**) | schneller, Prinzip gleich |
| **„Alle Regler zurücksetzen“** (`:114-116`) | rot, ohne Bestätigung/Undo; liegt am Ende der langen Liste | gleich |
| **Menü-Picker** (Strahlen: „8 Strahlen (alle)“, Ausblendung: lange Texte) | Zeilentext wird gekürzt oder umbrochen | breiter, unkritisch |

### 5.4 S3/S4 Einstellungen (`SettingsView`)

| Problem | iPhone | iPad |
|---|---|---|
| **Zoom (verändert das Muster!) liegt im Sheet** (`:23`) | Sheet verdeckt die Karte; Zoom ist die einzige Abhilfe bei „zu geringem Abstand“ und steht in einem anderen Screen als die Warnung („…bis der Zoom verkleinert wird“) | Formular-Sheet ist mittig, Karte dahinter teilweise sichtbar, aber nicht interaktiv |
| **Mischung** Karte (musterrelevant) und Darstellung (nur Anzeige) | Sheet-Titel „Einstellungen“ suggeriert „selten benutzt“ | gleich |
| **mm-Felder mit `decimalPad`** (`:47-56`) | **kein Fertig/Return** → Tastatur lässt sich nicht schließen; keine Wertebereichs-Prüfung (0, negativ, riesig) | Hardware-Tastatur ok; Prüfung fehlt |
| **Hinweis-Text als einzelner Absatz** (`:24`) | langer `caption`-Block mit 6 Fakten | gleich |
| **Sheet-Größe** | `.large` voll; keine Detents | Standard-Formsheet |

### 5.5 S5 Prüfung

| Problem | iPhone | iPad |
|---|---|---|
| **Warnungen stehen am Seitenende der Vorschau** | siehe 5.2 | – |
| **Nicht handlungsfähig:** Text nennt die Abhilfe, bietet aber keinen Sprung zum Regler | Wechsel Tab/Sheet nötig | Regler-Spalte links sichtbar, Zoom aber weiter im Sheet |
| **Schwere nur über Farbe + Icon in einer Zeile** | Farbsehschwäche, kleine Punkte | gleich |
| **Kritischer Zustand blendet Stiche aus und sperrt Wiedergabe/Export** | Nutzer sieht deaktivierte Bedienelemente ohne Begründung am Element selbst | gleich |

### 5.6 S6 Sticken (heute: Wiedergabeleiste)

| Problem | iPhone | iPad |
|---|---|---|
| **Nur grafisch, keine Textanweisung** (VS/RS-Beschriftungen wie in der Anleitung fehlen) | Beim Mitsticken ist ein kleines Pfeilsymbol auf einer 3-pt-Lochkarte nicht ablesbar | wie iPhone; mehr Fläche für Textspalte neben der Karte |
| **Nur Slider + Play, kein „Nächster Stich“** | Bedienung mit einer Hand/mit Faden in der Hand unpraktisch; Trefferflächen klein, nicht im Daumenbereich | iPad im Ständer: große Tasten links/rechts, Pfeiltasten/Leertaste |
| **Auto-Wiedergabe fix 45 ms** (`AppModel:62`) | zum Betrachten ok, zum Mitsticken unbrauchbar | gleich |
| **Display-Sperre/Idle Timer nicht gesetzt** | Bildschirm dunkelt während des Stickens ab | gleich |
| **Fortschritt wird bei jeder Mustereinstellung auf „fertig“ gesetzt** (`didSet`: `currentStep = maxStep`) | Position geht beim Zurückkommen aus Einstellungen verloren | gleich |
| **Rotation** | Hoch ↔ quer ändert Layout; Position muss erhalten bleiben | frei drehbar |

### 5.7 S7–S9 Anleitung, Lochmuster, Drucken & Teilen (`ExportView`)

| Problem | iPhone | iPad |
|---|---|---|
| **A4-PDF auf Bildschirmbreite** (`PDFView.autoScales`) | A4-Hochformat auf ~358 pt → Fließtext ≈ 4–5 pt, Beschriftungen in den Diagrammen nicht lesbar; Anleitung ist ein **Druckdokument**, keine Bildschirmanleitung | A4 auf ~700–800 pt: lesbar; Diagramme klein |
| **Lochmuster A6+Falz = A4-Querformat** | Querseite im Hochformat-Sheet: ~358 × 253 pt, nur mit Zoom nutzbar | passt gut |
| **Segmentwahl + Vorschau + Hinweis + drei Toolbar-Aktionen** | Hinweistext (nur beim Lochmuster) unten, Toolbar mit „Schließen · Teilen · AirPrint“ eng; wichtigste Druckhinweise (A4, 100 %) werden leicht übersehen | genug Platz |
| **PDF-Erzeugung im Hauptthread** (`generate()` per `.task`, `Task.yield` dazwischen) | Anleitung mit vielen Diagrammen kann den Fortschrittsindikator einfrieren (**zu messen**); Sheet ist bis dahin leer | gleich |
| **`updateUIView` setzt `document` bei jedem Update neu** (`:18-20`) | Zoom und Scrollposition können bei Zustandswechsel (Segmentumschaltung, Rotation) zurückspringen (**zu prüfen**) | gleich |
| **AirPrint: `present(animated:)`** (`:116-126`) | funktioniert als Seitendialog | auf dem iPad Ankerposition/Popover nicht gesetzt (**zu prüfen**) |
| **Druckskalierung** | Dialog bietet „Seite anpassen“; Kontrollbalken ist die einzige Absicherung und erscheint nur im PDF, nicht als Hilfe in der App | gleich |
| **Sperre bei kritischem Abstand** | Export-Symbol grau ohne Hinweis | gleich |
| **Kein 1:1 am Display** | Das Lochmuster darf auf dem Bildschirm nicht als maßstäblich verstanden werden | gleich |

### 5.8 S10–S13 (neue Screens)

| Problem | iPhone | iPad |
|---|---|---|
| Entwurfsliste mit Vorschaubildern | `List` einspaltig, Swipe-Aktionen | Raster oder Sidebar in `NavigationSplitView` |
| Vorlagen-Auswahl | Karussell/Liste, Vorschau pro Eintrag rendern (Canvas/Bild) | Raster 3–4 Spalten |
| Hilfe/Glossar | Detailseiten, kurze Texte; Verlinkung aus Reglern („?“) | Sidebar + Text |
| Persistenz-Migration | `StickSettings` besitzt tolerante Decodierung (neue Felder ok); Mehr-Entwurf-Modell braucht eigenes Schema + Migration vom heutigen Einzelstand | gleich |

### 5.9 Querschnittsthemen

| # | Thema | Befund |
|---|---|---|
| Q1 | **Layout-Verifikation ohne Mac** | CI baut nur; es gibt keinen Weg, Layouts je Gerät zu sehen. Bis jetzt entstehen PNG-Vorschauen nur für PDFs (Branch `ios-ci-previews`), nicht für die App-Oberfläche. Ohne Screenshot-Matrix (z. B. iPhone SE/16/Pro Max, iPad mini/Pro, hoch/quer, Dynamic Type groß, Hell/Dunkel) bleiben alle Layoutaussagen Vermutungen. |
| Q2 | **Weichen im Layout** | genau eine (`hSize`); keine Reaktion auf Höhe, Fenstergröße, Dynamic Type |
| Q3 | **Schriftgrößen** | meist System-Textstile (gut), aber `caption`/`caption2`/`footnote` für wichtige Inhalte (Wert der Regler, Statistik-Label, Legende, Warnungen) |
| Q4 | **Barrierefreiheit** | Canvas ohne Label/Beschreibung; Farbe als Zustandsträger; Wiedergabe-Icons nur mit automatischen (englischen) Symbolnamen statt deutscher Beschriftung (zu prüfen) |
| Q5 | **Zustandserhalt** | Eine Konfiguration; Tab, Scrollposition, Wiedergabeposition werden nicht gespeichert |
| Q6 | **Fehlende Erklärungen** | Fachbegriffe (Sternebene, Schrittweite, Rotationsversatz, Ausblendung) ohne Hilfetext |
| Q7 | **Fraktal-Funktion** | in der iOS-App bedienbar, in der Web-App nicht — Funktionsumfang ist dort bereits größer als in der Referenz |
| Q8 | **Performance** | `compute` + JSON-Speichern pro Reglerschritt synchron; Canvas wird bei jedem Wiedergabeschritt komplett neu gezeichnet (Pfade über alle Segmente) |

---

## 6. Prioritäten aus der Analyse

1. **Vorschau und Regler müssen gleichzeitig sichtbar sein** (iPhone: Vorschau oben + Sheet mit Detents oder Umschalter *Entwerfen / Ansehen*; iPad: Split-View-Layout mit flexibler Spaltenbreite statt fester 400 pt).
2. **Mehrere Layout-Weichen** statt `hSize` allein: Breite, Höhe, Fenstergröße und Dynamic Type.
3. **Zoom/Format/Abhilfe bei Warnungen** gehören in die Nähe der Karte und der Warnung, nicht in ein Sheet.
4. **Sticken** braucht eine eigene Oberfläche (große Tasten, Textanweisung, Display bleibt an).
5. **Anleitung als Bildschirmdokument** getrennt vom Druck-PDF denken; PDF bleibt Druck-/Teilen-Ergebnis.
6. **Layout-Screenshots in der CI** einführen, bevor das Design festgelegt wird (E5).

---

## 7. Offene Entscheidungen für das gemeinsame Konzept

| # | Frage | Auswirkung |
|---|---|---|
| E1 | **Verteilung:** nur eigenes Gerät (Sideloading/TestFlight) oder App Store? | Datenschutz-/Impressumspflichten, Privacy-Manifest, Review-Anforderungen |
| E2 | **Ist Mitsticken am Gerät ein Kernszenario?** | eigener Sticken-Modus (S6) vs. Wiedergabeleiste |
| E3 | **Mehrere Entwürfe speichern** oder nur letzter Stand? | S11, Datenmodell, Migration |
| E4 | **Vorlagen/Beispiele** und Erststart-Einführung? | S12/S13 |
| E5 | **Wie prüfen wir Layouts ohne Mac?** (CI-Screenshots per Simulator/`ImageRenderer`) | Grundlage für jede Design-Entscheidung |
| E6 | **Experten- vs. Einfachmodus** für Parameter (Grundlagen zuerst, Details ausklappbar)? | Struktur von S2 |
| E7 | **Anleitung auf dem Bildschirm** lesbar oder nur als PDF? | S7 ja/nein |
| E8 | **Zuschnitt > A4:** mehrseitiger Kachel-Druck gewünscht? | S8-Funktion |
| E9 | **Mindest-iOS 16** beibehalten? (iOS 17 bringt `@Observable`, `sensoryFeedback`, bessere Sheets/Scroll-APIs) | verfügbare Bausteine |
| E10 | **Mac/„iPad-App auf Mac“** nur tolerieren oder mitgestalten? | Fenstergrößen, Pointer |
| E11 | **Hell/Dunkel:** Systemfolge beibehalten (Web war fest dunkel)? | Farbkonzept, Kartenrahmen |
| E12 | **Sprache:** nur Deutsch oder vorbereitet für mehrere? | String-Struktur |

---

## 8. Vorgehen danach

1. Analyse gemeinsam durchgehen; Entscheidungen E1–E12 klären (zuerst E2, E3, E5).
2. Gemeinsames Konzept: Navigationsmodell, Screen-Karte, Layout-Regeln je Größenklasse, Komponentenliste.
3. Design (separater Schritt): visuelle Sprache und Prototyp je Gerät.
4. Umsetzung in `ios/App` mit Screenshot-Matrix in der CI.
