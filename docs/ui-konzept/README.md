# UI-Konzept Stickkarten-Generator (iPhone und iPad)

Sicherung des Konzept- und Designstands aus der Planungsphase. Grundlage ist
`docs/ui-grundanalyse.md` (Analyse). Dieses Verzeichnis enthält das daraus entstandene
Konzept und den Designentwurf. Der Code in `ios/` wurde dabei **nicht** verändert.

> **Hinweis:** `boards/` und `werkzeuge/` sind Archiv zum Nachvollziehen. Die erste iOS-Portierung liegt
> unverändert im Branch `archive/ios-port-v1`. Der aktuelle Plan steht in `docs/projektplan-konsolidierung.md`.

## Inhalt

| Pfad | Inhalt |
|---|---|
| `konzept.md` | Das Konzept als Text: Screens, Designregeln, Editor, Geführter Weg, Aufwand-Stufen, Stichfolge, Ausgabe, Kernänderungen, offene Punkte, Umsetzungsplan |
| `gesamtreview.md` | Abschließende Prüfung: Konsolidierung, Soll-/Kann-Matrix, Gesamtreview, was „nicht gerechnet und nicht gerendert“ bedeutet |
| `abwaertskompatibilitaet.md` | Recherche zu Mindest-iOS-Version und Verbreitung, Folgen für das Design |
| `bilder/` | Alle Boards als PNG (Stand der Sicherung). Die Schrift ist die Ersatzschrift des Rechners, nicht die Designschrift (Newsreader und IBM Plex Sans) |
| `boards/` | Dieselben Boards als HTML (Quelle der PNGs) |
| `canvas.json` | Anordnung der Boards auf dem Design-Canvas (Position, Größe, Titel, Notizen) |
| `werkzeuge/` | Python-Skripte, die die Boards erzeugen (siehe unten) |

## Das Artifact

Das Design lag als Design-Artifact bei Claude vor (privat, Version 47):
<https://claude.ai/artifact/Wdgor4wDnKDuDFM3iv1X31>

Eine neue Claude-Sitzung kann es über das Artifact-Werkzeug lesen (`action: "read"`, Pfad
`project/<Board>.dc.html`). Die Final-Pages dort sind Kopien des Arbeitsstands und werden mit
`werkzeuge/regen_final.py` neu erzeugt. Das Artifact ist die Quelle der Anordnung. Diese
Sicherung ist die Quelle der Inhalte, falls das Artifact nicht mehr erreichbar ist.

## Boards ansehen

- Als Bild: `bilder/<Name>.png`. Die Boardnamen stehen in `canvas.json` (Feld `title`).
- Beispiele: `Gefuehrt-iPhone-3-Aufwand.png`, `Stichfolge-Aeste.png`, `iPhone-Editor-Sheet.png`,
  `Aufwand-Stufen.png` (Tabelle der festen Muster), `Designregeln.png`.

## Werkzeuge (nur zum Nachvollziehen)

- `lib.py`: Bausteine (Symbole, Sheets, Regler).
- `pat.py`: rechnet echte Muster nach dem Vorbild von `ios/StickCore/.../Graph.swift`
  (Stichzahl, Lochabstand). Enthält die Parametersätze der Aufwand-Stufen (`PRE`).
- `build*.py`: erzeugen die Boards (`build6`/`build7`/`build11`: Geführter Weg,
  `build13`: Stichfolge, `build14`: Schicht aus und Ausgabe, `build15*`: Mehr, Einführung,
  iPad, Querformat; `build16*`: Konsolidierung auf echte Muster; `build17`: Zustände;
  `build18`: Dunkel und große Schrift; `real.py`: fertige Muster und Favoriten;
  `render.js`: Boards als PNG).
- `calc_stiche.py`: Vorrechnung der Stichzahlen und Abstände.
- **Die Skripte enthalten feste Pfade der Entwurfs-Sitzung** (`/tmp/claude-0/...`). Vor einer
  Wiederverwendung anpassen. Sie sind keine Produktivwerkzeuge.

## Stand und Vorbehalte

- Das Design ist ein Entwurf. Gerendert wurde im Browser, getestet wurde nichts auf einem Gerät.
- Die Muster der Aufwand-Stufen sind mit einem eigenen Nachbau des Kerns gerechnet. Vor der
  Umsetzung gegen den echten Kern prüfen.
- Namen, Farbwelten und Beispielmuster auf Start, Favoriten und Detail sind Platzhalter.
