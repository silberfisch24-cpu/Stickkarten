# Hilfsbausteine für die Editor-Boards (nur Textbausteine, keine Logik)
HEAD = '''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>__TITLE__</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&amp;family=Newsreader:wght@600&amp;display=swap" rel="stylesheet">
<style>
body{margin:0}
a{text-decoration:none;color:inherit}
.i{width:24px;height:24px;flex-shrink:0;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.glass{background:rgba(255,255,255,.7);-webkit-backdrop-filter:blur(20px) saturate(1.6);backdrop-filter:blur(20px) saturate(1.6);border:1px solid rgba(255,255,255,.8);box-shadow:0 4px 18px rgba(30,42,51,.14)}
.sheet{background:rgba(250,248,242,.9);-webkit-backdrop-filter:blur(28px) saturate(1.6);backdrop-filter:blur(28px) saturate(1.6);border:1px solid rgba(255,255,255,.85);box-shadow:0 -6px 30px rgba(30,42,51,.18)}
.ticks{height:8px;background:repeating-linear-gradient(90deg,#b3ab9b 0 1px,transparent 1px 22.6px)}
</style>
</helmet>
'''
TAIL = '''</x-dc>
<script type="text/x-dc" data-dc-script data-props='{"$preview":{"width":__W__,"height":__H__}}'>
class Component extends DCLogic {
  renderVals() { return {}; }
}
</script>
</body>
</html>
'''
def doc(title, w, h, body, bg='#e9e4d6'):
    return (HEAD.replace('__TITLE__', title)
        + f'<div style="position: relative; width: {w}px; height: {h}px; box-sizing: border-box; background: {bg}; color: #1e2a33; font-family: \'IBM Plex Sans\', system-ui, sans-serif; overflow: hidden">\n'
        + body + '</div>\n' + TAIL.replace('__W__', str(w)).replace('__H__', str(h)))

# ---- Symbole (24er Raster) ----
ICON = {
 'grund': '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="4" r="1"/><circle cx="12" cy="20" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="20" cy="12" r="1"/>',
 'aeste': '<path d="M12 21V9M12 15l-5-4M12 12l5-4M12 9V3"/>',
 'stern1': '<path d="M11 2l7 12H4zM11 18L4 6h14z" transform="translate(0 1) scale(.9)"/><text x="17" y="22" font-size="10" font-weight="700" fill="currentColor" stroke="none">1</text>',
 'stern2': '<path d="M11 2l7 12H4zM11 18L4 6h14z" transform="translate(0 1) scale(.9)"/><text x="17" y="22" font-size="10" font-weight="700" fill="currentColor" stroke="none">2</text>',
 'karte': '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 3v18" stroke-dasharray="2 2"/>',
 'muster': '<path d="M12 3l8 14H4zM12 21L4 7h16z"/>',
 'play': '<path d="M8 5l11 7-11 7z"/>',
 'star': '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
 'printer': '<path d="M7 9V4h10v5M7 17H4V9h16v8h-3M7 14h10v6H7z"/>',
 'back': '<path d="M15 6l-6 6 6 6"/>',
 'palette': '<path d="M12 3a9 9 0 100 18c1.5 0 2-1 1.5-2s0-2 1.5-2h2a3 3 0 003-3c0-6-4-11-8-11z"/><circle cx="8" cy="11" r="1"/><circle cx="12" cy="7.5" r="1"/><circle cx="16" cy="11" r="1"/>',
 'angle': '<path d="M5 19L12 5l7 14M8 13h8"/>',
 'laenge': '<path d="M4 12h16M4 12l4-4M4 12l4 4M20 12l-4-4M20 12l-4 4"/>',
 'ebenen': '<path d="M4 20h16M6 20v-4h4v-4h4V8h4V4"/>',
 'wachstum': '<path d="M4 18c4 0 5-2 6-5s3-6 10-7M15 6h5v5"/>',
 'schritt': '<path d="M4 12h4M10 12h4M16 12h4M17 8l3 4-3 4"/>',
 'punkte': '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="4" r="1.3"/><circle cx="12" cy="20" r="1.3"/><circle cx="4" cy="12" r="1.3"/><circle cx="20" cy="12" r="1.3"/>',
 'zoom': '<circle cx="11" cy="11" r="7"/><path d="M8 11h6M16 16l5 5"/>',
 'reset': '<path d="M4 5v5h5"/><path d="M5 10a8 8 0 112 8"/>',
 'warn': '<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17.5v.01"/>',
 'stop': '<path d="M8 3h8l5 5v8l-5 5H8l-5-5V8z"/><path d="M9 9l6 6M15 9l-6 6"/>',
 'loch': '<circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="8" stroke-dasharray="2 3"/>',
 'gesamt': '<path d="M12 3l9 5-9 5-9-5zM3 13l9 5 9-5"/>',
 'hoch': '<rect x="7" y="3" width="10" height="18" rx="2"/>',
 'quer': '<rect x="3" y="7" width="18" height="10" rx="2"/>',
 'chev_up': '<path d="M6 15l6-6 6 6"/>',
}
def ic(name, size=None, extra=''):
    st = f' style="width: {size}px; height: {size}px;{extra}"' if size else (f' style="{extra}"' if extra else '')
    return f'<svg class="i" viewBox="0 0 24 24" aria-hidden="true"{st}>{ICON[name]}</svg>'

TINT = {}
FADEN = {'aeste': '#d9e2e7', 'stern1': '#e8c987', 'stern2': '#ffffff'}  # Fadenfarben auf dem Karton

def glass_btn(icon, label, extra=''):
    return f'<a href="#" aria-label="{label}" class="glass" style="width: 48px; height: 48px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border-radius: 50%;{extra}">{ic(icon)}</a>'

def topbar(active, issues=False, top=59):
    def seg(key, icon, label):
        if key == active:
            return f'<a href="#" style="flex: 1.9 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); border-radius: 20px; font-size: 14px; font-weight: 600">{ic(icon)}{label}</a>'
        return f'<a href="#" aria-label="{label}" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; border-radius: 20px">{ic(icon)}</a>'
    dot = '<i style="position: absolute; right: 6px; top: 6px; width: 10px; height: 10px; border-radius: 50%; background: #e0503f; border: 2px solid #ffffff"></i>' if issues else ''
    out = f'<a href="#" aria-label="Ausgabe{" (gesperrt: Löcher zu eng)" if issues else ""}" class="glass" style="position: relative; width: 48px; height: 48px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border-radius: 50%;{" opacity: .6" if issues else ""}">{ic("printer")}{dot}</a>'
    return (f'  <div style="position: absolute; left: 16px; right: 16px; top: {top}px; height: 48px; display: flex; gap: 8px; align-items: center">\n'
        f'    {glass_btn("back","Zurück")}\n'
        f'    <div class="glass" style="flex-grow: 1; height: 48px; box-sizing: border-box; padding: 4px; display: flex; gap: 2px; border-radius: 24px">{seg("muster","muster","Muster")}{seg("stich","play","Stichfolge")}</div>\n'
        f'    {glass_btn("star","Als Favorit sichern")}\n    {out}\n  </div>\n')

def track(selected, keys=('grund','aeste','stern1','stern2','karte'), labels=None, h=44):
    labels = labels or {'grund':'Grundform','aeste':'Äste','stern1':'Stern 1','stern2':'Stern 2','karte':'Karte',
                        'loch':'Lochmuster','gesamt':'Gesamtbild'}
    items = ''
    for k in keys:
        col = TINT.get(k)
        stc = f' color: {col};' if col else ''
        if k == selected:
            items += f'<a href="#" style="flex: 0 0 auto; padding: 0 14px; display: flex; align-items: center; justify-content: center; gap: 6px; background: #ffffff;{stc or " color: #1f5a4b;"} box-shadow: 0 1px 4px rgba(30,42,51,.25); border-radius: 19px; font-size: 14px; font-weight: 600">{ic(k if k in ICON else "muster",20)}<span style="color: #1e2a33">{labels[k]}</span></a>'
        else:
            items += f'<a href="#" aria-label="{labels[k]}" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; color: {col or "#1e2a33"}; border-radius: 20px">{ic(k if k in ICON else "muster")}</a>'
    return f'<div style="height: {h}px; flex-shrink: 0; box-sizing: border-box; padding: 3px; display: flex; gap: 2px; background: #e6e1d4; border-radius: {h//2}px">{items}</div>'

def grabber(expand=True):
    e = f'<a href="#" aria-label="Alle Einstellungen der Gruppe" style="position: absolute; right: 10px; top: 0; width: 44px; height: 32px; display: flex; align-items: center; justify-content: center; color: #5f594e">{ic("chev_up",22)}</a>' if expand else ''
    return e + '<div style="display: flex; justify-content: center; padding: 2px 0 4px"><i style="width: 40px; height: 5px; border-radius: 3px; background: rgba(30,42,51,.35)"></i></div>'

def slider(label, icon, value, pct, ticks=True):
    t = '<div class="ticks" style="margin: -6px 4px 4px"></div>' if ticks else ''
    return (f'    <div style="box-sizing: border-box; padding: 10px 16px 6px; display: flex; flex-direction: column; gap: 2px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px">\n'
        f'      <div style="display: flex; align-items: center; gap: 12px"><span style="color: #1f5a4b; display: flex">{ic(icon)}</span><span style="flex-grow: 1; font-size: 16px">{label}</span><b style="font-size: 17px">{value}</b></div>\n'
        f'      <div style="position: relative; height: 44px"><i style="position: absolute; left: 0; right: 0; top: 19px; height: 6px; border-radius: 3px; background: #dcd5c5"></i><i style="position: absolute; left: 0; width: {pct}%; top: 19px; height: 6px; border-radius: 3px; background: #1f5a4b"></i><i style="position: absolute; left: calc({pct}% - 14px); top: 8px; width: 28px; height: 28px; border-radius: 50%; background: #ffffff; box-shadow: 0 2px 8px rgba(30,42,51,.35)"></i></div>\n      {t}\n    </div>\n')

def stepper(label, icon, value):
    return (f'    <div style="min-height: 64px; box-sizing: border-box; padding: 0 12px 0 16px; display: flex; align-items: center; gap: 12px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px">\n'
        f'      <span style="color: #1f5a4b; display: flex">{ic(icon)}</span><span style="flex-grow: 1; font-size: 16px">{label}</span>\n'
        f'      <a href="#" aria-label="Weniger" style="width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; background: #efeadd; border-radius: 50%"><svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 12h12"/></svg></a>\n'
        f'      <b style="min-width: 22px; text-align: center; font-size: 22px">{value}</b>\n'
        f'      <a href="#" aria-label="Mehr" style="width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; background: #efeadd; border-radius: 50%"><svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 6v12M6 12h12"/></svg></a>\n    </div>\n')

def toggle(label, icon, on=True):
    kn = '<i style="width: 27px; height: 27px; border-radius: 50%; background: #ffffff"></i>'
    return (f'    <div style="min-height: 56px; box-sizing: border-box; padding: 0 16px; display: flex; align-items: center; gap: 12px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px">\n'
        f'      <span style="color: #1f5a4b; display: flex">{ic(icon)}</span><span style="flex-grow: 1; font-size: 16px">{label}</span>\n'
        f'      <span style="width: 51px; height: 31px; box-sizing: border-box; padding: 2px; display: flex; justify-content: {"flex-end" if on else "flex-start"}; background: {"#1f5a4b" if on else "#cfc8b8"}; border-radius: 16px">{kn}</span>\n    </div>\n')

SW = ['#e8c987', '#d9e2e7', '#ffffff', '#3a5a8c', '#c9506b']
def colorrow(sel=0, tint='#1f5a4b'):
    sws = ''
    for i, c in enumerate(SW):
        ring = f'box-shadow: 0 0 0 2px #ffffff, 0 0 0 4px {tint};' if i == sel else ''
        sws += f'<a href="#" aria-label="Farbe {i+1}" style="width: 40px; height: 44px; display: flex; align-items: center; justify-content: center"><i style="width: 28px; height: 28px; border-radius: 50%; background: {c}; border: 1px solid rgba(30,42,51,.25); {ring}"></i></a>'
    return (f'    <div style="min-height: 52px; box-sizing: border-box; padding: 0 8px 0 16px; display: flex; align-items: center; gap: 10px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px">\n'
        f'      <span style="color: {tint}; display: flex">{ic("palette")}</span><span style="flex-grow: 1; font-size: 16px">Farbe</span>{sws}\n    </div>\n')

def formatrow():
    def opt(icon, label, sel):
        if sel:
            return f'<a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); border-radius: 22px; font-size: 14px; font-weight: 600">{ic(icon,20)}{label}</a>'
        return f'<a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; border-radius: 22px; font-size: 14px">{ic(icon,20)}{label}</a>'
    return (f'    <div style="min-height: 64px; box-sizing: border-box; padding: 0 12px 0 16px; display: flex; align-items: center; gap: 12px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px">\n'
        f'      <span style="color: #1f5a4b; display: flex">{ic("karte")}</span><span style="font-size: 16px">Format</span>\n'
        f'      <div style="flex-grow: 1; height: 44px; box-sizing: border-box; padding: 3px; display: flex; gap: 2px; background: #e6e1d4; border-radius: 21px">{opt("hoch","A6 hoch",True)}{opt("quer","A6 quer",False)}</div>\n    </div>\n')

# ---- Karte ----
P = [(58,38),(83.5,48.5),(94,74),(83.5,99.5),(58,110),(32.5,99.5),(22,74),(32.5,48.5)]
Q = [(58,52.4),(73.3,58.7),(79.6,74),(73.3,89.3),(58,95.6),(42.7,89.3),(36.4,74),(42.7,58.7)]
def pathpts(pts, k):
    return ''.join(f'M{pts[i][0]} {pts[i][1]}L{pts[(i+k)%8][0]} {pts[(i+k)%8][1]}' for i in range(8))
def card(left, top, w, h, mode='normal', radius=8):
    """mode: normal | warn (Stiche blass, Problemstellen markiert)"""
    op = '1' if mode == 'normal' else '.4'
    spokes = ''.join(f'M58 74L{x} {y}' for x, y in P)
    holes = ''.join(f'<circle cx="{x}" cy="{y}" r=".9"/>' for x, y in P + Q + [(58,74)])
    halos = ''
    if mode == 'warn':
        halos = ('<circle cx="58" cy="74" r="9" fill="#e0503f" fill-opacity=".22" stroke="#e0503f" stroke-width="1"/>'
                 '<circle cx="73.3" cy="58.7" r="5" fill="#e8a23d" fill-opacity=".22" stroke="#e8a23d" stroke-width=".9"/>'
                 '<circle cx="42.7" cy="58.7" r="5" fill="#e8a23d" fill-opacity=".22" stroke="#e8a23d" stroke-width=".9"/>')
    return (f'  <svg viewBox="0 0 105 148" style="position: absolute; left: {left}px; top: {top}px; width: {w}px; height: {h}px; border-radius: {radius}px; display: block; box-shadow: 0 14px 36px rgba(30,42,51,.28)">'
        f'<rect width="105" height="148" fill="#153a2c"/><path d="M0.4 0V148" stroke="#000" stroke-opacity=".35" stroke-width=".4" stroke-dasharray="2 1.5"/>'
        f'<g opacity="{op}" fill="none" stroke-width=".5"><path d="{spokes}" stroke="{FADEN["aeste"]}"/><path d="{pathpts(Q,1)}" stroke="{FADEN["stern2"]}"/><path d="{pathpts(P,3)}" stroke="{FADEN["stern1"]}"/></g>'
        f'<g fill="#0c1f17">{holes}</g>{halos}</svg>\n')

def warnchips(left, top, zu_eng=6, knapp=2):
    return (f'  <div style="position: absolute; left: {left}px; top: {top}px; display: flex; gap: 8px">'
        f'<span class="glass" style="height: 36px; box-sizing: border-box; padding: 0 12px; display: flex; align-items: center; gap: 6px; border-radius: 22px; font-size: 15px; font-weight: 700; color: #b3261e">{ic("stop",20)}{zu_eng}</span>'
        f'<span class="glass" style="height: 36px; box-sizing: border-box; padding: 0 12px; display: flex; align-items: center; gap: 6px; border-radius: 22px; font-size: 15px; font-weight: 700; color: #9a5a00">{ic("warn",20)}{knapp}</span></div>\n')

def sheet(top, inner, cls='sheet', extra=''):
    return (f'  <div class="{cls}" style="position: absolute; left: 0; right: 0; top: {top}px; bottom: 0; box-sizing: border-box; padding: 8px 16px 0; border-radius: 34px 34px 0 0; display: flex; flex-direction: column; gap: 10px; overflow: hidden;{extra}">\n'
        f'    {grabber()}\n    {inner}\n  </div>\n')
