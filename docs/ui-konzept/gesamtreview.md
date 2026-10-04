# Gesamtreview UI (Stand: Design-Artifact Version 47)

Dieses Dokument fasst die abschließende Prüfung des UI-Entwurfs zusammen: was bei der
Konsolidierung geändert wurde, welche Soll- und Kann-Vorgaben der Grundanalyse umgesetzt,
teilweise oder gar nicht vorbereitet sind, wie der Gesamtstand zu bewerten ist und was
„nicht gerechnet und nicht gerendert“ bedeutet.

## 1 Konsolidierung: was geändert wurde

Die Page „Lücken schließen“ wurde aufgelöst. Alle Boards stehen jetzt auf der Page
„Arbeitsstand“ (neue Reihen unten). Die Final-Pages (iPhone, iPad) sind neu erzeugt.

Gefundene Inkonsistenzen und ihre Behebung:

| Fund | Behebung |
|---|---|
| Editor-, Ausgabe- und PDF-Boards zeigten ein altes, von Hand gezeichnetes 8er-Sternmuster. Es passte weder zu den Reglerwerten (Kreispunkte 8, Ebenen 4) noch zur Stichfolge oder zum Geführten Weg. | Alle Boards zeigen jetzt dasselbe, mit dem Mustermodell gerechnete Muster („Mein Muster“: 8 Strahlen, 5 Ebenen, Äste, Stern 1 und 2, 104 Stiche, kleinster Abstand 5,0 mm). |
| Warn- und Fehlerzustand waren erfunden (zwei orange Kreise, ein roter Kreis). | Die Zustände entstehen aus den Reglerwerten: Astwinkel 55° und Astlänge 70 % ergeben 3,9 mm (Warnung), 80 % ergeben 2,9 mm (kritisch), 45° und 60 % ergeben 5,0 mm (in Ordnung). Die Markierungen sitzen an den tatsächlich zu engen Löchern. |
| Reglerstellung stimmte nicht: 55° stand bei 82 % des Reglers, obwohl 55° das Maximum ist. | 55° steht am rechten Anschlag. Werte und Stellung in allen Editor-Boards angeglichen. |
| Kompakt-PDF, Lochmuster-Seite und Vorschauen zeigten 8 Löcher. | Alle zeigen die 89 Löcher des Beispielmusters, Einstellungsband mit den richtigen Werten. |
| „Schicht aus“ (Stern 2) lief auf einem anderen Muster als „Mein Muster“. | Gleiches Muster ohne Stern 2. |
| Start, Favoriten und Muster-Detail zeigten alte Beispielmuster. | Zehn fertige Muster und acht Favoriten aus den gerechneten Aufwand-Stufen, Namen kurz genug für fünf Spalten. Das Detail zeigt „Winterlicht“ (Beides, Mittel, 2 Farben). |
| Kapsel „Weitermachen“ zeigte ein altes Symbol. | Zeigt das echte Muster. |
| Zwei verwaiste Boards (Start flach, Editor-Einstellungen). | Gelöscht. |
| Designregeln hatten keine Regeln für Dialoge, Dunkel, Breite, Lesbarkeit. | Neues Board „Designregeln 2“ (auch in beiden Final-Pages). |
| Seitenleiste iPad ohne „Info und Datenschutz“. | In allen iPad-Boards ergänzt. |

Neu gezeichnet zur Schließung von Lücken: Eigenformat (gültig und zu groß), Meldung antippen
mit Abhilfe, Zurücksetzen im Editor (Schaltfläche und Abfrage), Ausgabe gesperrt, PDF wird
erstellt, PDF-Fehler, Start ohne Arbeitsstand, Dunkel (vier Boards), größte Schrift (zwei
Boards).

## 2 Soll- und Kann-Vorgaben der Grundanalyse

Stufen: **voll** = im Design ausgearbeitet, **teilweise** = Teil gezeichnet oder nur
beschrieben, **fehlt** = nicht vorbereitet.

### Screens (Abschnitt 3 und 4 der Grundanalyse)

| Vorgabe | Stand | Anmerkung |
|---|---|---|
| S1 Editor mit Karte und Parametern, Rückfrage beim Zurücksetzen | voll | Zurücksetzen je Gruppe oder ganzes Muster (neu) |
| S1 Karte zoomen und verschieben (Pinch, Ziehen) | teilweise | Nur der Zoom-Regler ist gezeichnet. Gesten sind nicht dargestellt (lassen sich nicht in Standbildern zeigen). |
| S1 Kennzahlen und Prüfstatus dauerhaft erreichbar | teilweise | Bewusst geändert: Meldung live auf der Karte, Kennzahlen nur in der Stichfolge (Gesamtbild). |
| S2 Alle Eingaben gruppiert | voll | Fünf Gruppen, Karte inklusive Farben und Eigenformat |
| S2 Gegenseitige Begrenzungen sichtbar (Schrittweite, Sternebene, Seitenäste auslassen) | **fehlt** | Zustand „Wert wurde angepasst“ und „nicht anwählbar, weil …“ ist nicht gezeichnet. |
| S2 Hinweis, warum eine Eingabe fehlt | teilweise | Nur bei „Schicht aus“. |
| S2 Feineinstellung ±1 an Reglern | teilweise | Zähler haben ± Tasten, die Regler nicht. Für VoiceOver als „einstellbar“ vorgesehen. |
| S2 Format-Eingabe mit Validierung | voll | Eigenformat, Höchstmaß sichtbar, rote Meldung. Zahlentastatur nicht gezeichnet. |
| S3 Prüfung mit Ursache und Abhilfe | voll | Als Live-Meldung mit antippbarer Abhilfe (Sprung zum Regler). Keine eigene Prüfliste (bewusst). |
| S3 Betroffene Löcher markieren, hinzoomen | teilweise | Markierung ja, automatisches Zoomen nicht. |
| S4 Stichfolge als Ansicht | voll | Fünf Abschnitte, iPhone, iPad, Querformat |
| S5 Lochmuster mit Druckhinweisen | voll | Kompakt, Lochmuster 1:1, Formatfälle |
| S6 Anleitung (nur PDF) | teilweise | Wählbar in der Ausgabe. **Die vier Seiten der Anleitung sind nicht gestaltet.** |
| S7 Ausgabe mit Vorschau, Teilen, Drucken, Sperre, Status, Fehler | voll | Zustände neu gezeichnet. AirPrint und Dateien sichern kommen vom System. |
| S8 Favoriten (Umbenennen, Löschen, Duplizieren) | voll | Anzahl und Sortierung sind nicht entschieden (Vorschlag unten). |
| S9 Zehn fertige Muster | voll | Muster und Namen sind Platzhalter (O2 offen). |
| S10 Erststart, Hilfe, Glossar, Kontexthilfe | voll | Alle Texte Platzhalter. |
| S11 Einstellungen, Info, Datenschutz | voll | **Impressum fehlt** (E1 offen). |
| Startseite, Geführter Weg | voll | Alle Zustände auf iPhone und iPad |
| Bild-Export („später“), Platz vorsehen | **fehlt** | In der Ausgabe ist kein Platz markiert. |
| QR-Code im PDF („später“) | voll | Platzhalter im Kompakt-PDF |

### Querschnitt (Abschnitt 5 der Grundanalyse)

| Vorgabe | Stand | Anmerkung |
|---|---|---|
| Q1 Breite 320 bis über 1300 pt | teilweise | Gezeichnet: iPhone 390, iPad 1180 und 820, Slide Over 390. **Nicht gezeichnet:** kleines iPhone (320/375 pt), Split View halb, iPad 13 Zoll. |
| Q2 Höhe als Engpass | teilweise | iPhone quer gezeichnet (drei Boards). Tastatur auf dem iPad nicht. |
| Q3 Dynamic Type | teilweise | Zwei Beispiel-Boards und eine Regel. Kein Test aller Screens. |
| Q4 Barrierefreiheit der Grafik | teilweise | Nur als Regel (Beschreibung der Karte, Regler einstellbar). Keine geprüften Texte, keine Reihenfolge für VoiceOver. |
| Q5 Zustandserhalt | teilweise | Konzept „Letzter Stand“ und „Weitermachen“. Details (Scrollposition, Zoom, Stichfolge-Position) nicht festgelegt. |
| Q6 Hell und Dunkel | teilweise | Vier Dunkel-Boards als Beispiel, Palette festgelegt. Nicht alle Screens, Kontrast nicht gemessen. |
| Q7 Verifikation ohne Mac | **fehlt** | Siehe Abschnitt 4. Das ist die größte offene Voraussetzung. |

### Entscheidungen E und Fragen O

| Punkt | Stand |
|---|---|
| E1 Verteilung, Pflichtangaben (Impressum, Privacy-Manifest) | offen |
| E5 Layouts ohne Mac prüfen | offen |
| E8 Eigenformat auf A4 begrenzt, Maximalmaße sichtbar | voll (Höchstmaß als Chip) |
| E9 iOS 17 | entschieden, Rückfall für Glas in `abwaertskompatibilitaet.md` |
| E10 Mac | offen (Vorschlag: tolerieren) |
| E12 Mehrsprachigkeit | nur als Regel, keine Ansicht |
| O1 Einfachstufe des Editors | Vorschlag: Sheet „Mittel“ (zwei Hauptregler je Gruppe) |
| O2 Zehn fertige Muster | Platzhalter aus den Aufwand-Stufen, Kuratierung offen |
| O3 Aufwand-Definition | entschieden: Stichzahl (50, 80, 110), Farben 1, 2, 3 |
| O4 Favoriten | Vorschlag: höchstens 24, neueste zuerst, Name beim Sichern „Muster n“ |
| O5 Umfang der Hilfe | Vorschlag: fünf Themen, Glossar, Kontexthilfe je Gruppe |

## 3 Offene Punkte, nach Gewicht

1. **Gegenseitige Begrenzungen der Regler** (S2). Das ist der größte fachliche Zustandsraum
   (Schrittweite, Sternebene, Strahlen, Ausblendung hängen voneinander ab) und fehlt im Design.
2. **Anleitung (vier PDF-Seiten).** Das Produkt ist gewählt, aber nicht gestaltet.
3. **Verifikation ohne Mac** (E5) und damit die Prüfung aller Layoutaussagen.
4. **Kleine Geräte** (iPhone SE/mini, 320–375 pt) und **Split View halb**.
5. Impressum und Verteilung (E1), Bild-Export-Platz.
6. Texte (Einführung, Hilfe, Glossar, Datenschutz) und Katalog der zehn Muster.
7. Dunkel und Dynamic Type für alle Screens statt je einem Beispiel.

## 4 Gesamtreview des UI-Stands

**Was belastbar ist**

- Das Konzept ist in sich schlüssig: drei Wege zum Muster (Geführt, Fertige Muster, Editor),
  ein Editor mit fünf Gruppen, eine reine Ansicht für die Stichfolge, PDF als einziges
  Ausgabeprodukt.
- Die Regeln sind festgeschrieben (Designregeln und Designregeln 2), die Boards halten sie
  nach der Konsolidierung ein. Muster und Zahlen sind jetzt überall dieselben.
- Die Bausteine sind auf iPhone und iPad gleich. Dadurch ist der Umfang für die Umsetzung
  überschaubar: Kachel, Panel/Sheet, Umschalter, Regler, Zähler, Meldung, Dialog.
- Die fachlichen Zahlen (Aufwand-Stufen, Warnschwellen) sind aus dem Kern abgeleitet und
  nachgerechnet.

**Risiken**

- **Schwerster Punkt:** Der Editor mit Live-Berechnung auf dem iPhone ist der Kern des
  Produkts und hängt am Kern-Umbau (Ebenen als Eigenschaft der Grundform). Bis dieser steht,
  sind die Warnungen im Design nur Behauptungen.
- Liquid Glass ist ab iOS 26. Für iOS 17 und 18 braucht jedes schwebende Element einen
  Rückfall. Das ist machbar, aber ein eigener Arbeitsschritt.
- Das Lochmuster muss auf dem Papier maßhaltig sein. Das ist weder gezeichnet noch gerechnet
  prüfbar, sondern nur durch einen Ausdruck mit Messung.
- Viele Texte und Muster sind Platzhalter.

**Empfehlung für die nächsten Schritte**

1. Kern-Umbau mit Tests (Ebenen, Katalog der 27 Muster gegen den echten Kern).
2. Designsystem im Code und ein Prototyp von Editor und Geführtem Weg.
3. Screenshot-Prüfung auf einem macOS-Runner (E5) gegen die Boards.
4. Danach die offenen Entwürfe (Begrenzungen, Anleitung, kleine Geräte).

## 5 Was „nichts gerechnet und gerendert“ bedeutet

**Nicht gerechnet.** Alle Zahlen im Konzept (Stichzahlen, Lochabstände, Aufwand-Stufen,
Warnschwellen, Fadenlänge) stammen aus einem **eigenen Nachbau** der Formeln des Kerns
(`ios/StickCore`, Datei `Graph.swift`) in Python. Der echte Swift-Kern wurde nicht
ausgeführt. Folgen:

- Abweichungen sind möglich, besonders bei Rundung, bei der Wahl des Musterradius aus
  Zoom, Format und Falz und bei Randfällen. Alle Abstände beziehen sich auf einen festen
  Radius von etwa 35 mm.
- Die Warnschwellen (3,2 mm und 4,8 mm) stammen aus der Analyse. Ob die gerechneten
  Beispielmuster im echten Kern ohne Warnung durchlaufen, ist unbewiesen.
- Die 27 festen Muster sind nur als Konzept belegt (neun Zellen gerechnet, V2 und V3 nicht
  ausgearbeitet).
- Der Kern wird erst durch den Umbau (Ebenen in der Grundform) so, wie das Design ihn
  voraussetzt.

**Nicht gerendert.** Alle Boards sind **Zeichnungen aus HTML und CSS**. Sie wurden im
Browser dargestellt, nicht von SwiftUI auf einem iPhone oder iPad. Folgen:

- Das Glas ist eine Nachahmung. Echtes Liquid Glass (Brechung, Reaktion auf Inhalt) sieht
  anders aus und wirkt anders auf Kontrast und Lesbarkeit.
- Schrift, Zeilenumbrüche, Sicherheitsbereiche (Notch, Home-Indikator), Tastatur,
  Animation, Gesten, Haptik und Antwortzeit beim Ziehen eines Reglers sind ungeprüft.
- Die PNG-Bilder im Repository verwenden eine Ersatzschrift, weil der Rechner Newsreader
  und IBM Plex Sans nicht hatte. Die Schriften müssen außerdem in die App eingebunden
  werden.
- Die Karte wurde nicht auf echter Pixeldichte geprüft. Ein Loch (0,92 mm) ist auf dem
  Bildschirm etwa 3 pt groß. Ob Zoom, Markierungen und Berührflächen dafür ausreichen, zeigt
  erst ein Gerät.
- Kontraste (hell und dunkel), VoiceOver und Dynamic Type sind nicht gemessen oder
  getestet.
- Der Ausdruck wurde nicht gemacht. Ob das PDF 1:1 maßhaltig druckt (Kontrollbalken 50 mm),
  zeigt nur ein Probedruck.

**Was daraus folgt:** Das Design ist ein belastbarer **Entwurf und eine Spezifikation**,
kein Nachweis. Die Prüfung gegen die Wirklichkeit geschieht in drei Stufen: Kern-Tests
für die Zahlen, ein SwiftUI-Prototyp mit Simulator-Screenshots (macOS-Runner) für das
Layout, ein Gerätetest samt Probedruck für Gefühl, Lesbarkeit und Maßhaltigkeit.
