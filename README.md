# Stickkarten-Generator — lokales Projekt

Dieses Projekt läuft **außerhalb** jeder Vorschau-Sandbox als ganz normale
lokale Webseite. Drucken, „Als PDF speichern“ und Datei-Downloads
funktionieren hier wie auf jeder anderen Webseite auch, weil kein
eingebetteter Vorschau-iframe mehr im Weg ist.

## Voraussetzung

Node.js (Version 18 oder neuer) muss installiert sein. Prüfen mit:

```
node -v
```

Falls nicht installiert: https://nodejs.org (die "LTS"-Version reicht).

## Starten

Im Ordner dieses Projekts, im Terminal:

```
npm install
npm run dev
```

Vite gibt danach eine lokale Adresse aus (meist `http://localhost:5173`).
Diese im Browser öffnen — dort läuft die App als ganz normale Seite.

## Mit Claude Code weiterentwickeln

Falls Claude Code (die lokale CLI) installiert ist: einfach in diesem
Ordner `claude` starten. Der aktuelle Stand der Komponente liegt in
`src/StickkartenGeneratorV4.jsx` — Claude Code kann darauf direkt
aufsetzen (der bisherige Chat-Verlauf wird dabei nicht automatisch
übernommen, nur die Dateien).
