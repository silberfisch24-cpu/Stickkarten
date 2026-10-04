# UI-Konzept (Stand der Sicherung)

Dieses Dokument fasst die Entscheidungen der Planungsphase zusammen. Bilder dazu liegen in
`bilder/`. Wo ein Board gemeint ist, steht sein Dateiname in Klammern.

## 1 Rahmen

- Native SwiftUI-App unter `ios/`. iPhone und iPad gleichrangig, dieselben Bausteine auf beiden.
- Erscheinung folgt dem System (Hell/Dunkel). Sprache Deutsch, Texte für weitere Sprachen
  vorbereitet.
- So wenige Berechtigungen wie möglich: kein Kamera-, Scan- oder Importzugriff. Später ist ein
  QR-Code im PDF vorgesehen (Platzhalter ist eingezeichnet).
- Mindest-iOS: bisher iOS 17 festgelegt, siehe `abwaertskompatibilitaet.md`.
- Anleitung nur als PDF. Mitsticken ist eine Nebenfunktion (Stichfolge ist eine Ansicht, kein
  eigener Modus). Fraktal entfällt (im Kern nicht funktionsfähig).
- Zielgruppe gestuft: Einsteiger über den Geführten Weg, Fortgeschrittene im Editor.

## 2 Navigation und Screens (`Main.png`)

- iPhone: schwebende Tab-Leiste (Start, Gestalten, Ausgabe, Mehr). Darüber die Kapsel
  „Weitermachen“ (öffnet den letzten Stand).
- iPad: schwebende Seitenleiste (Start, Gestalten, Ausgabe, Muster mit Fertige Muster und
  Favoriten, Mehr). Kapsel „Weitermachen“ unten.
- **Start:** Karte „Neues Muster“ (Geführter Weg), Umschalter Muster | Favoriten,
  Kachelraster. Fertige Muster: 10 Stück mit Vorschau, Name und Aufwand, Detail mit
  „Anpassen“ (als Entwurf übernehmen) und „Als PDF“.
- **Favoriten:** Raster, Menü per Langdruck (Umbenennen, Duplizieren, Als PDF, Löschen),
  Leerzustand mit Hinweis und „Neues Muster“.
- **Editor, Stichfolge, Ausgabe, Mehr:** siehe unten. Mehr enthält Einführung, Hilfe,
  Glossar, Einstellungen, Info und Datenschutz, Alles zurücksetzen.
- Im Editor sind Tab-Leiste und Kapsel ausgeblendet.

## 3 Designregeln (`Designregeln.png`)

Grundlage Liquid Glass (iOS 26). Beim Wechsel auf eine neuere Version ändern sich nur
Materialwerte, nicht die Regeln.

- **Material:** Glas für schwebende Elemente (Leisten, Kapseln, runde Buttons), halbtransparente
  Sheets, opake weiße Flächen für Inhalte (Zeilen, Karten, Kacheln).
- **Form und Größe:** Steuerelemente Kapsel 44 pt hoch. Karten, Zeilen, Kacheln Radius 22.
  Sheets und große Panels Radius 34. Hauptaktion 56–68 pt. Tab-Leiste 64 pt, Zubehör-Kapsel
  60 pt, Seitenrand 16 pt, Abstände 8/10/12. Berührflächen mindestens 44 × 44 pt.
- **Symbole und Schrift:** Strichsymbole, Linie 2, Raster 24 (in Chips 20, groß 28). Jede
  Beschriftung hat ein Symbol. Titel 34–40 (Newsreader), Abschnitt 20, Text 17, sekundär 15,
  Hinweise 13, Tab-Beschriftung 11 (IBM Plex Sans). Texte nie kleiner als 13 (außer Tab).
- **Farben:** Akzent `#1f5a4b`, Inhaltsgrund `#f4f0e6`, Arbeitsfläche Editor `#e9e4d6`, Fläche
  `#ffffff`. Warnung `#fcefd9`/`#6b3f00`, kritisch `#fde7e3`/`#8f1d14`, in Ordnung
  `#e0f0e6`/`#14603a`. Farbe nie allein: immer Symbol und Text.
- **Umschalter:** über Inhalt Glas, auf Flächen gefüllt (`#e6e1d4`). Bei mehr als drei
  Segmenten nur das aktive mit Text.
- **Auswahlkacheln:** Rahmen 3 pt plus Tönung, kein Häkchen. Kachelhöhe 140 pt (iPad 190 pt).
- **Raster:** Bildfläche fester Höhe, Muster mittig (hoch und quer gemischt, längste Seite
  gleich), Name linksbündig, Aufwand als Punkte. Kopfbereich wird nie gestaucht.
- **Karte als Bühne:** Auf der Karte schweben nur runde Glas-Buttons (44 pt), z. B. Favorit
  oben rechts. Abschluss mit zwei gleichwertigen Kapseln.
- **Meldungen:** immer einzeilig, kurz („Lochabstand knapp“, „Löcher zu eng“).

## 4 Editor (`iPhone-Editor-Sheet*.png`, `iPad-Editor.png`)

- Vollbild-Arbeitsfläche. Obere Zeile immer gleich: Zurück (rund) · Umschalter
  Muster/Stichfolge (Glas, mittig) · Drucken (rund). Favorit-Stern schwebt oben rechts auf der
  Karte. Karte gewinnt immer den größtmöglichen Platz.
- **iPhone:** Sheet in drei Stufen. Klein: Griff und Gruppen-Tabs. Mittel: zwei Hauptregler
  untereinander (Karte bleibt sichtbar und bedienbar). Groß: alle Regler der Gruppe, opak,
  Meldungszeile oben.
- **iPad:** schwebendes Panel rechts (400 pt) mit denselben Gruppen-Tabs (Beschriftung unter
  dem Symbol) statt Sheet.
- **Gruppen (5):** Grundform, Äste, Stern 1, Stern 2, Karte.

| Gruppe | Mittel (2 Elemente) | Groß (alles) |
|---|---|---|
| Grundform | Kreispunkte, Ebenen | Hinweis zum Mindestabstand |
| Äste | Astwinkel, Astlänge | Seitenäste an/aus, Wachstum |
| Stern 1 | Schrittweite, Sternebene | Sternstrahlen, Seitenäste auslassen, Schicht an/aus |
| Stern 2 | wie Stern 1 | zusätzlich Rotationsversatz |
| Karte | Zoom, Farben | Format, Falz, Farbe je Element (Karton, Äste, Stern 1, Stern 2), Erweitert: Eigenformat |

- **Schicht aus** (`iPhone-Editor-Sheet-Stern2-aus.png`, `...Gross-Stern2-aus.png`): Mittel zeigt
  nur den Schalter „Schicht aktivieren“. Groß zeigt ihn mit den dann erscheinenden Reglern
  ausgegraut.
- **Meldungen live im Muster**, keine eigene Prüf-Ansicht. Kein Fehler: nichts. Warnung (gelb,
  „Lochabstand knapp“): Stiche bleiben, Problemstellen orange. Kritisch (rot, „Löcher zu eng“):
  nur Punktmuster in Farben, Stiche ausgeblendet, Druck gesperrt. Keine Kennzahlen-Chips. Die
  Meldung steht unten auf der Karte (Groß: oben im Sheet).
- **Ebenen als Eigenschaft der Grundform:** Ebenen bilden ein Raster aus n Punkten mal Ebenen.
  Sterne können auf jeder Ebene sitzen, auch ohne Äste. Löcher entstehen nur dort, wo sie
  gebraucht werden, die Abstandsprüfung gilt nur für benutzte Punkte (`Ebenen-Modell.png`).

## 5 Stichfolge (`Stichfolge-*.png`)

Reine Ansicht (kein Mitstick-Modus). Fünf Abschnitte: Lochmuster, Äste, Stern 1, Stern 2,
Gesamtbild. Abschnitt ohne Inhalt ist abgeblendet und nicht wählbar
(`Stichfolge-Schicht-aus.png`).

- Das Bedienpanel hat in allen Abschnitten dasselbe Gerüst mit gleichen Höhen: Abschnittsleiste
  · Chips · Regler oder Maß · Hauptaktion (68 pt). Die Leiste springt nie.
- **Äste / Stern 1 / Stern 2:** Wiedergabe der Stiche. Aktueller Stich gelb mit Pfeil, folgender
  Sprung hinten gestrichelt, erledigte Stiche in der Elementfarbe, kommende blass. Chips
  „Kx → Ky“ (Stich, grün) und Sprung (rot). Löcher sind in der Reihenfolge der ersten
  Benutzung nummeriert.
- **Lochmuster:** nur Löcher (ohne Ringe), Kennzahlen (Anzahl, kleinster Abstand), Maßstab
  50 mm, „Vorlage 1:1 drucken“.
- **Gesamtbild:** alle Schichten in ihren Farben, Stichzahl je Schicht, gesamt und geschätzter
  Faden, „Drucken und Teilen“.

## 6 Geführter Weg (`Gefuehrt-*.png`)

Ziel: einfache Nutzung, keine komplexen Einstellungen, „ready-to-use“-Ergebnis.

- **Schritte:** Format (A6 hoch/quer, Falz links/oben/keiner) → Stil (Flocke, Stern, Beides)
  → Aufwand (Leicht, Mittel, Aufwendig) → Farbwelt (3 feste Farbwelten, ab Mittel mit
  Umschalter Einfarbig/Mehrfarbig) → Auswahl (3 fest hinterlegte Varianten) → Ergebnis.
- **Aufbau:** Karte oben, festes Panel unten (Frage, eine Reihe gleich hoher Kacheln, Kapsel
  „Weiter“). Keine freien Hinweissätze. Oben Fortschritt mit Symbolen (aktiver Schritt mit
  Text). iPad: Karte links, Panel rechts.
- **Aufwand:** Im Schritt zeigen drei Karten oben die Stufen mit 1, 2 und 3 Farben.
- **Varianten fest hinterlegt, nie zufällig** (Zufall erzeugt zu viele unschöne Muster).
- **Ergebnis:** Favoritenstern auf der Karte, zwei Kapseln „Anpassen“ (Editor) und „Als PDF“
  (Ausgabe mit Kompakt vorgewählt). Das Muster wird „Letzter Stand“.
- **Abbruch:** Systemdialog „Muster verwerfen?“ mit „Verwerfen“ und „Weitermachen“, nur wenn
  schon Angaben gemacht wurden. Ein abgebrochener Weg wird nicht gemerkt.

### 6.1 Aufwand-Stufen (`Aufwand-Stufen.png`)

Richtwert ist die Stichzahl: Leicht bis etwa 50, Mittel bis etwa 80, Aufwendig bis etwa 110.
Die Stufen gelten je Stil. Farben: Leicht 1, Mittel bis 2, Aufwendig bis 3.

Formeln (aus `Graph.swift`): Äste `n · (3E − 4)` mit Seitenästen, `n · E` ohne. Stern: `n` Stiche
je Stern. Platzregel A6: ohne Warnung muss `n · E` unter etwa 47 bleiben. Warnschwelle ist
1,5 × Mindestabstand (Mindestabstand etwa 3,2 mm, also 4,8 mm).

Vorgaben des Auftraggebers: Leicht nur bis Stern 1 und bis 6 Strahlen. Mittel bis 10 Äste oder
zwei Sterne bis 10 Strahlen, Äste mit Stern 1 höchstens 8, kein Stern 2. Aufwendig: Äste oder
Sterne allein bis 14, kombiniert bis 8 mit Stern 1 und 2.

| Stil | Stufe | Parameter (Beispiel V1) | Stiche | Löcher | kleinster Abstand |
|---|---|---|---|---|---|
| Flocke (nur Äste) | Leicht | 6 Äste, 4 Ebenen, Winkel 45°, Länge 0,6 | 48 | 49 | 6,2 mm |
| Flocke (nur Äste) | Mittel | 10 Äste, 4 Ebenen, Winkel 40°, Länge 0,55 | 80 | 81 | 5,4 mm |
| Flocke (nur Äste) | Aufwendig | 14 Äste, 3 Ebenen, Winkel 35°, Länge 0,45 | 70 | 71 | 5,2 mm |
| Stern (nur Sterne) | Leicht | 6 Strahlen, Stern 1 (k=2) | 6 | 6 | 35,0 mm |
| Stern (nur Sterne) | Mittel | 10 Strahlen, Stern 1 (k=3), Stern 2 (k=2) | 20 | 20 | 10,8 mm |
| Stern (nur Sterne) | Aufwendig | 14 Strahlen, Stern 1 (k=5), Stern 2 (k=3) | 28 | 28 | 7,8 mm |
| Beides (Äste + Stern 1, aufwendig + Stern 2) | Leicht | 6 Äste, 4 Ebenen, Winkel 45°, Länge 0,6, Stern 1 (k=2) | 54 | 49 | 6,2 mm |
| Beides (Äste + Stern 1, aufwendig + Stern 2) | Mittel | 8 Äste, 4 Ebenen, Winkel 45°, Länge 0,6, Stern 1 (k=3) | 72 | 65 | 6,2 mm |
| Beides (Äste + Stern 1, aufwendig + Stern 2) | Aufwendig | 8 Äste, 5 Ebenen, Winkel 45°, Länge 0,6, Stern 1 (k=3), Stern 2 (k=1) | 104 | 89 | 5,0 mm |

Hinweise: Reine Sterne haben wenige Stiche, die Sehnen sind aber lang. Die Stichzahl allein
stuft sie zu leicht ein (Fadenlänge als zweites Maß möglich). Ab n = 10 müssen Astwinkel und
Astlänge unter den Standardwerten (55°, 0,7) liegen, sonst wird der Abstand zu eng. Jede
Zelle bekommt drei Varianten (V1 bis V3), zusammen 27 feste Muster.
Die Tabelle ist mit einem Nachbau gerechnet und vor der Umsetzung gegen den Kern zu prüfen.

## 7 Ausgabe und PDF (`iPhone-Ausgabe*.png`, `iPad-Ausgabe*.png`, `Kompakt-*.png`, `Lochmuster-Faelle.png`)

- Immer für S/W-Laserdruck. Optionen: Kompakt (Standard), Lochmuster 1:1, Anleitung (4 Seiten).
  Teilen und Drucken. iPad mit großer PDF-Vorschau, iPhone mit Vorschaubild und Lupe.
- **Kompakt (eine A4-Seite):** Lochmuster 1:1, Übersicht mit drei Figuren (Äste durchgezogen,
  Stern 1 gestrichelt, Stern 2 gepunktet) mit Farbnamen, vollständiges Einstellungsband,
  gestrichelter Platzhalter „später QR zur App“.
- Maßgeblich beim Druck ist die Seite mit dem Lochmuster. Die Vorderseite im Format der
  gefalteten Karte muss auf A4 passen (höchstens 190 × 277 mm hoch bzw. 277 × 190 quer). Die
  leere Rückseite wird gezeichnet, wenn das aufgeklappte Blatt auf A4 passt, sonst nur
  angedeutet (Zickzackkante, „Rückseite leer“).
- **Kompakt nicht verfügbar** (`iPhone-Ausgabe-Kompakt-aus.png`): zu große Karte. Zeile
  abgeblendet mit Hinweis „Karte zu groß“, Lochmuster 1:1 vorgewählt. Faustregel: Vorderseite
  höher als etwa 150 mm (A4 quer) bzw. 215 mm (A4 hoch). Grenzfall: A5 hoch, Falz links.
- Eigenformate werden auf den A4-Zuschnitt begrenzt (Experten, Karte groß, erweitert).

## 8 Änderungen am Kern und Daten

1. `StickCore`: Ebenen als Eigenschaft der Grundform, Löcher nur wo benutzt, Abstandsprüfung
   nur für benutzte Punkte. Fraktal entfernen.
2. Katalog der 27 festen Muster (Parametersätze) mit Test gegen den Kern (Stichzahl, Abstand,
   keine Warnung).
3. Kompakt-PDF in `StickPDF` (Seite, Figuren nach Strichart, Einstellungsband, QR-Platzhalter).
4. Optional: Fadenlänge als zweites Aufwandsmaß (`fadenCm` ist vorhanden).

## 9 Weitere Bereiche und Zustände

- **Mehr (iPhone, auf dem iPad in der Seitenleiste):** Einstellungen (Standardformat, Falz,
  Haptik, „Weitermachen“ anzeigen), Hilfe (fünf Themen, Themenseite „Warnungen verstehen“),
  Glossar mit Suche, Info und Datenschutz (ein Satz: alles bleibt auf dem Gerät, keine
  Berechtigungen), Einführung wiederholen, Alles zurücksetzen (Favoriten und Einstellungen,
  mit Abfrage).
- **Einführung (Erststart):** drei überspringbare Seiten, danach Start ohne „Weitermachen“.
  **Kontexthilfe:** Info-Symbol im Kopf des Sheets, je Gruppe eine Glas-Karte mit Link zum
  Glossar.
- **Favoriten:** Umbenennen (Dialog mit Tastatur), Löschen (Aktionsblatt). Vorschlag: höchstens
  24, neueste zuerst, Name beim Sichern „Muster n“.
- **Editor:** Meldung antippen öffnet Abhilfe mit Sprung zum Regler. Zurücksetzen je Gruppe oder
  für das ganze Muster mit Abfrage. Eigenformat nur unter „Erweitert“, mit Höchstmaß
  (Vorderseite 190 × 277 mm) und roter Meldung, wenn zu groß.
- **Ausgabe:** gesperrt bei kritischem Zustand (mit Erklärung und „Zum Muster“), „PDF wird
  erstellt“, Fehler mit „Erneut versuchen“.
- **Layout-Varianten:** iPhone quer (Panel rechts 340 pt), iPad hoch (Seitenleiste
  ausgeblendet, Panel 360 pt), Teilfenster (Slide Over, unter etwa 420 pt iPhone-Layout), Dunkel
  (Beispiele), größte Schrift (Beispiele). Regeln in `Designregeln 2`.
- **Zehn fertige Muster** (Platzhalter, aus den Aufwand-Stufen, nachgerechnet):

| Name | Stil | Stufe | Farbwelt | Format | Stiche | Löcher | kleinster Abstand |
|---|---|---|---|---|---|---|---|
| Flocke | Flocke | Leicht | Tannengrün | hoch | 48 | 49 | 6,2 mm |
| Eisblume | Flocke | Mittel | Mitternachtsblau | hoch | 80 | 81 | 5,4 mm |
| Raureif | Flocke | Aufwendig | Weinrot | quer | 70 | 71 | 5,2 mm |
| Aster | Stern | Leicht | Mitternachtsblau | hoch | 6 | 6 | 35,0 mm |
| Zwilling | Stern | Mittel | Tannengrün | quer | 20 | 20 | 10,8 mm |
| Polaris | Stern | Aufwendig | Weinrot | hoch | 28 | 28 | 7,8 mm |
| Funkel | Beides | Leicht | Tannengrün | hoch | 54 | 49 | 6,2 mm |
| Kristall | Beides | Mittel | Mitternachtsblau | hoch | 72 | 65 | 6,2 mm |
| Nordlicht | Beides | Aufwendig | Weinrot | hoch | 104 | 89 | 5,0 mm |
| Eisrose | Beides | Mittel | Weinrot | quer | 72 | 65 | 6,2 mm |

- **Beispielmuster „Mein Muster“** (Editor, Stichfolge, PDF): wie Nordlicht (Beides, Aufwendig:
  8 Strahlen, 5 Ebenen, Winkel 45°, Länge 60 %, Stern 1 Schrittweite 3 auf Ebene 2, Stern 2
  Schrittweite 1 auf Ebene 5). Mit Winkel 55° und Länge 70 % entsteht 3,9 mm (Warnung), mit
  80 % 2,9 mm (kritisch).

## 10 Offene Punkte

Vollständige Soll-/Kann-Prüfung, Gesamtreview und die Erklärung, was „nicht gerechnet und nicht
gerendert“ bedeutet: `gesamtreview.md`. Kurzfassung der Lücken: Begrenzungen der Regler
(Zustände), Anleitung (vier PDF-Seiten), Prüfung ohne Mac, kleine Geräte und Split View,
Impressum und Verteilung, Bild-Export-Platz, Texte und Musterkatalog.

## 11 Umsetzungsplan (Vorschlag)

1. Kernänderung (Ebenen, Fraktal) mit Tests.
2. Designsystem im Code: Farben, Maße, Glas-Kapsel, Kachel, Panel, Umschalter, mit Rückfall für
   ältere iOS-Versionen (siehe `abwaertskompatibilitaet.md`).
3. Screens: Editor und Stichfolge, dann Geführter Weg, Start/Favoriten, Ausgabe, Mehr.
4. Musterkatalog und Kompakt-PDF.
5. Bauen und Testen über einen macOS-Runner (GitHub Actions) oder lokal in Xcode, da in der
   Entwurfsumgebung kein Mac zur Verfügung steht.
