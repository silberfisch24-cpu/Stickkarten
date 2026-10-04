#!/bin/bash
# Startet die App im Simulator (ein iPhone, ein iPad), öffnet jeden Bereich und speichert Screenshots.
# Aufruf: screens.sh <Pfad/Stickkarten.app> <Ausgabeordner>
set -uo pipefail
APP="$1"; OUT="$2"; BUNDLE="de.stickkarten.app"
mkdir -p "$OUT"

udid_fuer() {
  xcrun simctl list devices available -j | python3 -c '
import sys, json
praefix = sys.argv[1]
d = json.load(sys.stdin)["devices"]
for runtime in sorted(d, reverse=True):
    if "iOS" not in runtime: continue
    for g in d[runtime]:
        if g["name"].startswith(praefix):
            print(g["udid"]); sys.exit(0)
sys.exit(1)' "$1"
}

for geraet in iPhone iPad; do
  UDID=$(udid_fuer "$geraet") || { echo "Kein Simulator für $geraet"; continue; }
  echo "== $geraet: $UDID"
  xcrun simctl boot "$UDID" 2>/dev/null || true
  xcrun simctl bootstatus "$UDID" -b >/dev/null
  xcrun simctl install "$UDID" "$APP"
  for modus in light dark; do
    xcrun simctl ui "$UDID" appearance "$modus"
    for bereich in start gestalten ausgabe mehr katalog; do
      xcrun simctl launch --terminate-running-process "$UDID" "$BUNDLE" -screen "$bereich" >/dev/null
      sleep 3
      xcrun simctl io "$UDID" screenshot "$OUT/${geraet}-${bereich}-${modus}.png" >/dev/null 2>&1
    done
  done
  xcrun simctl shutdown "$UDID" 2>/dev/null || true
done
ls -1 "$OUT"
