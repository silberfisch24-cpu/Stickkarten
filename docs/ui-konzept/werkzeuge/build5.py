import sys, json, random
sys.path.insert(0,'.')
from lib import *
import lib
exec(open('build4.py').read().split('# ---------- Mittel-Boards ----------')[0].split("OUT=")[0].replace("import sys, json, re","import sys, json, re"))
OUT='/tmp/claude-0/-home-user-Stickkarten/7d64d15f-70be-5a8c-bbc1-d86911943200/scratchpad/konzept1/project/'
def save(name, html): open(OUT+name,'w').write(html)
lib.ICON['ruler']='<path d="M3 17L17 3l4 4L7 21zM8 12l2 2M11 9l2 2M14 6l2 2"/>'
lib.ICON['eye']='<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>'
lib.ICON['share']='<path d="M12 3v12M8 7l4-4 4 4M5 12v8h14v-8"/>'
lib.ICON['check']='<circle cx="12" cy="12" r="10" fill="currentColor" stroke="none"/><path d="M7.5 12.5l3 3 6-7" stroke="#ffffff"/>'
lib.ICON['kompakt']='<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M13 9h5M13 12h5M13 15h5"/><rect x="6" y="8" width="5" height="8" rx="1"/>'
lib.ICON['lochmuster']='<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1"/><circle cx="14" cy="10" r="1"/><circle cx="9" cy="15" r="1"/><circle cx="14" cy="15" r="1"/>'
lib.ICON['info']='<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>'
lib.ICON['anleitung']='<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 12h7M9 15h7M9 18h4"/>'

# ---------- Kompakt-PDF (mm-Raster) ----------
rnd = random.Random(7)
def qr(x, y, s, n=21):
    cell = s / n
    out = f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="#ffffff"/>'
    def finder(fx, fy):
        return (f'<rect x="{x+fx*cell}" y="{y+fy*cell}" width="{7*cell}" height="{7*cell}" fill="#26241f"/><rect x="{x+(fx+1)*cell}" y="{y+(fy+1)*cell}" width="{5*cell}" height="{5*cell}" fill="#fff"/><rect x="{x+(fx+2)*cell}" y="{y+(fy+2)*cell}" width="{3*cell}" height="{3*cell}" fill="#26241f"/>')
    out += finder(0,0) + finder(n-7,0) + finder(0,n-7)
    for r in range(n):
        for c in range(n):
            if (r < 8 and c < 8) or (r < 8 and c > n-9) or (r > n-9 and c < 8): continue
            if rnd.random() < .5:
                out += f'<rect x="{x+c*cell:.2f}" y="{y+r*cell:.2f}" width="{cell:.2f}" height="{cell:.2f}" fill="#26241f"/>'
    return out
def cardmm(x, y, k, layers=('aeste','stern1','stern2')):
    """Schwarzweiß-Miniatur der Vorderseite, k = Maßstab auf 105 x 148 mm; Elemente nur über Linienart getrennt"""
    sw = .35 / k
    g = f'<g transform="translate({x} {y}) scale({k})"><rect width="105" height="148" fill="#ffffff" stroke="#26241f" stroke-width="{.3/k}"/><g fill="none" stroke="#26241f" stroke-width="{sw}" stroke-linecap="round">'
    if 'aeste' in layers: g += f'<path d="{"".join(f"M58 74L{a} {b}" for a,b in P)}"/>'
    if 'stern2' in layers: g += f'<path d="{pathpts(Q,1)}" stroke-dasharray="{.5/k} {1.1/k}"/>'
    if 'stern1' in layers: g += f'<path d="{pathpts(P,3)}" stroke-dasharray="{2.4/k} {1.4/k}"/>'
    r = max(.9, .4 / k)
    g += '</g><g fill="#26241f">' + ''.join(f'<circle cx="{a}" cy="{b}" r="{r}"/>' for a, b in P + Q + [(58,74)]) + '</g></g>'
    return g
CELLS = [
 ('Karte', ['A6 hoch · Falz links', 'Zoom 100 %', 'Karton Tannengrün']),
 ('Grundform', ['Kreispunkte 8', 'Ebenen 4']),
 ('Äste', ['an · Seitenäste an', 'Winkel 55° · Länge 70 %', 'Wachstum 30 % · Silber']),
 ('Stern 1', ['an · Ebene 2 · Strahlen 8', 'Schrittweite 3', 'Seitenäste auslassen: nein', 'Farbe Gold']),
 ('Stern 2', ['an · Ebene 4 · Strahlen 8', 'Schrittweite 1 · Versatz 0', 'Seitenäste auslassen: nein', 'Farbe Weiß']),
]
def cells_svg(cells, positions):
    out = ''
    for (t, lines), (x, y) in zip(cells, positions):
        out += f'<text x="{x}" y="{y}" font-size="2.9" font-weight="700" fill="#26241f">{t}</text>'
        for i, l in enumerate(lines):
            out += f'<text x="{x}" y="{y+4+i*3.5}" font-size="2.5" fill="#26241f">{l}</text>'
    return out
def qr_platz(x, y, sz):
    return (f'<rect x="{x}" y="{y}" width="{sz}" height="{sz}" fill="none" stroke="#26241f" stroke-opacity=".4" stroke-width=".25" stroke-dasharray="1.5 1.5"/>'
            f'<text x="{x+sz/2}" y="{y+sz/2-.5}" font-size="2" text-anchor="middle" fill="#6b655a">später</text><text x="{x+sz/2}" y="{y+sz/2+2.5}" font-size="2" text-anchor="middle" fill="#6b655a">QR zur App</text>')
def figs(x, y, k, dx, labelpos='unten'):
    out = ''
    for i, (name, col, lay) in enumerate([('Äste', 'Silber', ('aeste',)), ('Stern 1', 'Gold', ('stern1',)), ('Stern 2', 'Weiß', ('stern2',))]):
        fx = x + i * dx
        out += cardmm(fx, y, k, lay)
        out += f'<text x="{fx+105*k/2:.1f}" y="{y+148*k+3.4:.1f}" font-size="2.3" font-weight="700" text-anchor="middle" fill="#26241f">{name}</text><text x="{fx+105*k/2:.1f}" y="{y+148*k+6.4:.1f}" font-size="2.3" text-anchor="middle" fill="#26241f">{col}</text>'
    return out
def kompakt_inner():
    s = '<rect width="297" height="210" fill="#ffffff"/>'
    s += '<g transform="translate(10 10)"><rect width="210" height="148" fill="none" stroke="#26241f" stroke-width=".3"/>'
    s += '<line x1="105" y1="0" x2="105" y2="148" stroke="#26241f" stroke-width=".25" stroke-dasharray="3 2"/>'
    s += '<rect x="123" y="14" width="73" height="120" fill="none" stroke="#26241f" stroke-opacity=".35" stroke-width=".2" stroke-dasharray="1.5 1.5"/>'
    s += '<g transform="translate(105 0)" fill="rgba(0,0,0,.65)">' + ''.join(f'<circle cx="{a}" cy="{b}" r=".46"/>' for a, b in P + Q + [(58,74)]) + '</g></g>'
    s += '<g transform="translate(10 162)"><line x1="0" y1="0" x2="50" y2="0" stroke="#26241f" stroke-width=".4"/><line x1="0" y1="-1.5" x2="0" y2="1.5" stroke="#26241f" stroke-width=".4"/><line x1="50" y1="-1.5" x2="50" y2="1.5" stroke="#26241f" stroke-width=".4"/><text x="25" y="4.2" font-size="2.4" text-anchor="middle" fill="#26241f">50 mm</text></g>'
    s += '<text x="226" y="15" font-size="5" font-weight="700" fill="#26241f">Mein Muster</text><text x="226" y="19.5" font-size="2.6" fill="#6b655a">A6 hoch · Falz links</text>'
    s += cardmm(226, 23, .5) + figs(226, 100, .16, 21)
    s += '<text x="10" y="172" font-size="2.9" font-weight="700" letter-spacing=".3" fill="#6b655a">EINSTELLUNGEN</text>'
    s += cells_svg(CELLS, [(10 + i * 49, 179) for i in range(5)])
    s += qr_platz(260, 174, 26)
    s += '<text x="10" y="206" font-size="2.3" fill="#6b655a">Stickkarten · Kompakt · Maßstab 1:1 – beim Drucken A4 und 100 % wählen · Schwarzweiß</text>'
    return s
KOMP = kompakt_inner()
def paper(wpx, extra=''):
    return f'<svg viewBox="0 0 297 210" style="width: {wpx}px; height: {round(wpx*210/297)}px; display: block; background: #ffffff; box-shadow: 0 6px 24px rgba(30,42,51,.3);{extra}">{KOMP}</svg>'
def mini_loch(wpx):
    d = ''.join(f'<circle cx="{105+a}" cy="{b}" r="2.4" fill="#26241f"/>' for a, b in P + Q + [(58,74)])
    return f'<svg viewBox="0 0 210 148" style="width: {wpx}px; height: {round(wpx*148/210)}px; display: block; background: #ffffff; border: 1px solid #cfc8b8"><line x1="105" y1="0" x2="105" y2="148" stroke="#26241f" stroke-dasharray="6 4" stroke-width="1.2"/>{d}</svg>'
def mini_anl(hpx):
    bars = ''.join(f'<rect x="20" y="{40+i*14}" width="{140 if i%3 else 100}" height="5" fill="#cfc8b8"/>' for i in range(11))
    return f'<svg viewBox="0 0 210 297" style="height: {hpx}px; width: {round(hpx*210/297)}px; display: block; background: #ffffff; border: 1px solid #cfc8b8"><rect x="20" y="14" width="90" height="12" fill="#26241f"/>{bars}</svg>'

# ---------- Kompakt-PDF-Board ----------
save('Kompakt-PDF.dc.html', doc('Kompakt-PDF', 1188, 840,
     f'<svg viewBox="0 0 297 210" style="position: absolute; left: 0; top: 0; width: 1188px; height: 840px; display: block">{KOMP}</svg>', bg='#ffffff'))

# ---------- Ausgabe iPhone ----------
def optrow(kind, title, sub, thumb, sel):
    ring = 'border: 2px solid #1f5a4b;' if sel else 'border: 1px solid #d9d3c4;'
    chk = f'<span style="color: #1f5a4b; display: flex">{ic("check",26)}</span>' if sel else '<span style="width: 26px; height: 26px; box-sizing: border-box; border-radius: 50%; border: 2px solid #cfc8b8"></span>'
    return (f'    <a href="#" style="min-height: 76px; box-sizing: border-box; padding: 8px 14px 8px 8px; display: flex; align-items: center; gap: 12px; background: #ffffff; {ring} border-radius: 22px">'
            f'<span style="width: 72px; height: 58px; display: flex; align-items: center; justify-content: center; background: #efeadd; border-radius: 14px; flex-shrink: 0">{thumb}</span>'
            f'<span style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column"><b style="font-size: 16px; line-height: 21px; display: flex; align-items: center; gap: 8px"><span style="color: #1f5a4b; display: flex">{ic(kind,20)}</span>{title}</b><span style="font-size: 13px; line-height: 18px; color: #5f594e">{sub}</span></span>{chk}</a>\n')
rows = (optrow('kompakt','Kompakt','1 Seite · A4 quer · 100 %', mini_loch(0) if False else paper(56), True)
        + optrow('lochmuster','Lochmuster 1:1','1 Seite · A4 quer · 100 %', mini_loch(56), False)
        + optrow('anleitung','Anleitung','4 Seiten · A4 hoch', mini_anl(46), False))
hint = f'    <div style="display: flex; align-items: center; gap: 10px; color: #5f594e; font-size: 13px; line-height: 18px"><span style="color: #1f5a4b; display: flex">{ic("ruler",22)}</span><span>Beim Drucken A4 und 100 % wählen. Kontrollbalken (50 mm) nachmessen.</span></div>\n'
acts = (f'    <div style="display: flex; gap: 8px"><a href="#" aria-label="Vorschau mit Zoom" style="width: 52px; height: 52px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; background: #efeadd; border-radius: 26px">{ic("eye")}</a>'
        f'<a href="#" style="flex: 1 1 0; height: 52px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #1f5a4b; color: #ffffff; border-radius: 26px; font-size: 17px; font-weight: 600">{ic("share")}Teilen</a>'
        f'<a href="#" style="flex: 1 1 0; height: 52px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #efeadd; border-radius: 26px; font-size: 17px; font-weight: 600">{ic("printer")}Drucken</a></div>\n')
head = f'    <div style="display: flex; align-items: center; gap: 10px; font-size: 20px; font-weight: 600"><span style="color: #1f5a4b; display: flex">{ic("printer")}</span>Drucken und Teilen</div>\n'
dim = '  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.28)"></div>\n'
body = card(51,108,288,406) if False else ''
import importlib
from lib import card as oldcard
b = oldcard(72,108,246,347,'normal') + dim
b += (f'  <div class="sheet" style="position: absolute; left: 0; right: 0; top: 330px; bottom: 0; box-sizing: border-box; padding: 8px 16px 0; border-radius: 34px 34px 0 0; display: flex; flex-direction: column; gap: 10px; overflow: hidden; background: #faf8f2">\n'
      f'    <div style="display: flex; justify-content: center; padding: 2px 0 4px"><i style="width: 40px; height: 5px; border-radius: 3px; background: rgba(30,42,51,.35)"></i></div>\n{head}{rows}{hint}{acts}  </div>\n')
save('iPhone-Ausgabe.dc.html', doc('iPhone Ausgabe', 390, 844, b))

# ---------- Ausgabe iPad ----------
left = (f'  <div style="position: absolute; left: 24px; top: 24px; width: 560px; bottom: 24px; background: #e4dfd2; border-radius: 26px; display: flex; align-items: center; justify-content: center">{paper(512)}'
        f'<span class="glass" style="position: absolute; left: 16px; bottom: 16px; height: 44px; box-sizing: border-box; padding: 0 16px; display: flex; align-items: center; gap: 8px; border-radius: 22px; font-size: 15px; font-weight: 600">{ic("kompakt",20)}1 / 1</span>'
        f'<a href="#" aria-label="Vergrößern" class="glass" style="position: absolute; right: 16px; bottom: 16px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("zoom")}</a></div>\n')
rows_ipad = (optrow('kompakt','Kompakt','1 Seite · A4 quer · 100 %', paper(56), True)
        + optrow('lochmuster','Lochmuster 1:1','1 Seite · A4 quer · 100 %', mini_loch(56), False)
        + optrow('anleitung','Anleitung','4 Seiten · A4 hoch', mini_anl(46), False))
right = (f'  <div style="position: absolute; left: 608px; top: 24px; right: 24px; bottom: 24px; display: flex; flex-direction: column; gap: 10px">\n{head}{rows_ipad}{hint}'
         f'    <div style="margin-top: auto; display: flex; gap: 8px"><a href="#" style="flex: 1 1 0; height: 56px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #1f5a4b; color: #ffffff; border-radius: 28px; font-size: 17px; font-weight: 600">{ic("share")}Teilen</a>'
         f'<a href="#" style="flex: 1 1 0; height: 56px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #efeadd; border-radius: 28px; font-size: 17px; font-weight: 600">{ic("printer")}Drucken</a></div>\n  </div>\n')
panel = f'  <div class="sheet" style="position: absolute; left: 110px; top: 70px; width: 960px; height: 680px; border-radius: 34px; background: #faf8f2; overflow: hidden">\n{left}{right}  </div>\n'
save('iPad-Ausgabe.dc.html', doc('iPad Ausgabe', 1180, 820, oldcard(158,84,440,620,'normal') + dim + panel))


# ---------- Lochmuster-Seite: Formatfälle ----------
def page_case(orient, front, fx, fy, flat, hint=None, title='', extra=''):
    """front=(w,h) Vorderseite, (fx,fy) Lage auf der Seite (mm), hint: ('links'|'oben', mm) angedeutete Rückseite"""
    pw, ph = (297, 210) if orient == 'quer' else (210, 297)
    w, h = front
    s = f'<rect width="{pw}" height="{ph}" fill="#ffffff"/>'
    s += f'<rect x="10" y="10" width="{pw-20}" height="{ph-20}" fill="none" stroke="#26241f" stroke-opacity=".25" stroke-width=".25" stroke-dasharray="2 2"/>'
    # Vorderseite
    s += f'<rect x="{fx}" y="{fy}" width="{w}" height="{h}" fill="none" stroke="#26241f" stroke-width=".35"/>'
    sc = min(w / 105, h / 148, 1.45) if w < h else min(w / 105, h / 148)
    cx, cy = fx + w / 2, fy + h / 2
    s += '<g fill="#26241f">' + ''.join(f'<circle cx="{cx+(a-58)*sc:.2f}" cy="{cy+(b-74)*sc:.2f}" r=".46"/>' for a, b in P + Q + [(58,74)]) + '</g>'
    # Rückseite (leer)
    if flat == 'voll-links':
        s += f'<rect x="{fx-w}" y="{fy}" width="{w}" height="{h}" fill="none" stroke="#26241f" stroke-opacity=".45" stroke-width=".25" stroke-dasharray="3 2"/>'
        s += f'<line x1="{fx}" y1="{fy}" x2="{fx}" y2="{fy+h}" stroke="#26241f" stroke-width=".3" stroke-dasharray="3 2"/>'
        s += f'<text x="{fx-w/2}" y="{fy+h/2}" font-size="3" text-anchor="middle" fill="#6b655a">leer</text>'
    elif flat == 'voll-oben':
        s += f'<rect x="{fx}" y="{fy-h}" width="{w}" height="{h}" fill="none" stroke="#26241f" stroke-opacity=".45" stroke-width=".25" stroke-dasharray="3 2"/>'
        s += f'<line x1="{fx}" y1="{fy}" x2="{fx+w}" y2="{fy}" stroke="#26241f" stroke-width=".3" stroke-dasharray="3 2"/>'
        s += f'<text x="{fx+w/2}" y="{fy-h/2}" font-size="3" text-anchor="middle" fill="#6b655a">leer</text>'
    elif flat == 'angedeutet-oben':
        hh = hint
        s += f'<line x1="{fx}" y1="{fy}" x2="{fx+w}" y2="{fy}" stroke="#26241f" stroke-width=".3" stroke-dasharray="3 2"/>'
        s += f'<path d="M{fx} {fy} V{fy-hh} L{fx+w*.12} {fy-hh-2} L{fx+w*.25} {fy-hh+1} L{fx+w*.38} {fy-hh-2} L{fx+w*.5} {fy-hh+1} L{fx+w*.62} {fy-hh-2} L{fx+w*.75} {fy-hh+1} L{fx+w*.88} {fy-hh-2} L{fx+w} {fy-hh} V{fy}" fill="none" stroke="#26241f" stroke-opacity=".45" stroke-width=".25" stroke-dasharray="3 2"/>'
        s += f'<text x="{fx+w/2}" y="{fy-hh/2+1}" font-size="3" text-anchor="middle" fill="#6b655a">Rückseite leer</text>'
    elif flat == 'angedeutet-links':
        hh = hint
        s += f'<line x1="{fx}" y1="{fy}" x2="{fx}" y2="{fy+h}" stroke="#26241f" stroke-width=".3" stroke-dasharray="3 2"/>'
        s += f'<path d="M{fx} {fy} H{fx-hh} L{fx-hh-2} {fy+h*.12} L{fx-hh+1} {fy+h*.25} L{fx-hh-2} {fy+h*.38} L{fx-hh+1} {fy+h*.5} L{fx-hh-2} {fy+h*.62} L{fx-hh+1} {fy+h*.75} L{fx-hh-2} {fy+h*.88} L{fx-hh} {fy+h} H{fx}" fill="none" stroke="#26241f" stroke-opacity=".45" stroke-width=".25" stroke-dasharray="3 2"/>'
        s += f'<text x="{fx-hh/2}" y="{fy+h/2}" font-size="3" text-anchor="middle" fill="#6b655a" transform="rotate(-90 {fx-hh/2} {fy+h/2})">Rückseite leer</text>'
    # Kontrollbalken
    by = ph - 14
    s += f'<g transform="translate(10 {by})"><line x1="0" y1="0" x2="50" y2="0" stroke="#26241f" stroke-width=".4"/><line x1="0" y1="-1.5" x2="0" y2="1.5" stroke="#26241f" stroke-width=".4"/><line x1="50" y1="-1.5" x2="50" y2="1.5" stroke="#26241f" stroke-width=".4"/><text x="25" y="4.2" font-size="2.4" text-anchor="middle" fill="#26241f">50 mm</text></g>'
    s += extra
    k = 1.55
    return f'<svg viewBox="0 0 {pw} {ph}" style="width: {round(pw*k)}px; height: {round(ph*k)}px; display: block; background: #ffffff; box-shadow: 0 6px 24px rgba(30,42,51,.3)">{s}</svg>'
def case_card(svg, t1, t2, icon, t3, note=''):
    return (f'<div style="display: flex; flex-direction: column; gap: 12px"><div style="height: 462px; display: flex; align-items: flex-end">{svg}</div>'
            f'<div style="display: flex; flex-direction: column; gap: 6px"><b style="font-size: 17px; line-height: 22px">{t1}</b><span style="font-size: 14px; line-height: 20px; color: #4a453c">{t2}</span>'
            f'<span style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: #1f5a4b">{ic(icon,20)}{t3}</span><span style="font-size: 13px; line-height: 18px; color: #5f594e">{note}</span></div></div>')
cases = (case_card(page_case('quer',(105,148),115,31,'voll-links'),'A6 hoch · Falz links','Zuschnitt 210 × 148 mm · Seite A4 quer · 1:1','check','Rückseite ganz gezeigt','Passt auf A4.')
    + case_card(page_case('hoch',(105,148),52,70,'angedeutet-oben',hint=36),'A6 hoch · Falz oben','Zuschnitt 105 × 296 mm · Seite A4 hoch · 1:1','info','Rückseite nur angedeutet','Zuschnitt größer als A4, gedruckt wird nur die Vorderseite.')
    + case_card(page_case('hoch',(148,105),31,115,'voll-oben'),'A6 quer · Falz oben','Zuschnitt 148 × 210 mm · Seite A4 hoch · 1:1','check','Rückseite ganz gezeigt','Passt auf A4.')
    + case_card(page_case('hoch',(148,210),52,43,'angedeutet-links',hint=32),'A5 hoch · Falz links','Zuschnitt 296 × 210 mm · Seite A4 hoch · 1:1','info','Rückseite nur angedeutet','Größer als A4 quer, die Vorderseite 148 × 210 mm passt hoch.'))
save('Lochmuster-Faelle.dc.html', doc('Lochmuster-Seite Fälle', 1560, 860,
    '<div style="position: absolute; left: 64px; top: 48px; right: 64px; display: flex; flex-direction: column; gap: 8px"><h1 style="margin: 0; font-family: \'Newsreader\', Georgia, serif; font-size: 34px; line-height: 40px; font-weight: 700">Lochmuster-Seite: Formatfälle</h1>'
    '<span style="font-size: 15px; line-height: 21px; color: #4a453c; max-width: 1000px">Gedruckt wird immer nur die Vorderseite mit den Löchern, im Maßstab 1:1, in Schwarzweiß für den Laserdrucker. Passt der ganze Zuschnitt auf A4, ist die leere Rückseite ganz gezeigt, sonst nur angedeutet (gebrochene Kante).</span></div>'
    '<div style="position: absolute; left: 64px; top: 168px; right: 64px; display: grid; grid-template-columns: 482px 326px 326px 326px; gap: 32px; align-items: end">' + cases + '</div>', bg='#f4f0e6'))

# ---------- Kompakt-Fälle (hoch) ----------
ex1 = ('<text x="125" y="20" font-size="5" font-weight="700" fill="#26241f">Mein Muster</text><text x="125" y="24.5" font-size="2.6" fill="#6b655a">A6 hoch · Falz oben</text>'
       + cardmm(125, 28, .6) + figs(125, 122, .2, 25)
       + '<text x="10" y="209" font-size="2.9" font-weight="700" letter-spacing=".3" fill="#6b655a">EINSTELLUNGEN</text>'
       + cells_svg(CELLS, [(10, 216), (73, 216), (136, 216), (10, 243), (73, 243)]) + qr_platz(150, 238, 26))
ex2 = ('<text x="10" y="233" font-size="3.8" font-weight="700" fill="#26241f">Mein Muster</text><text x="10" y="237" font-size="2.2" fill="#6b655a">A5 hoch · Falz links</text>'
       + cardmm(10, 240, .24)
       + cells_svg(CELLS, [(78, 233), (121, 233), (160, 233), (78, 259), (121, 259)]))
kp1 = page_case('hoch',(105,148),10,46,'angedeutet-oben',hint=36,extra=ex1)
kp2 = page_case('hoch',(148,210),52,10,'angedeutet-links',hint=32,extra=ex2)
txt3 = ('<div style="height: 462px; width: 326px; box-sizing: border-box; padding: 24px; display: flex; flex-direction: column; justify-content: center; gap: 14px; background: #ffffff; border: 1px dashed #8a8378; border-radius: 22px">'
        f'<span style="display: flex; align-items: center; gap: 10px; font-size: 17px; font-weight: 600">{ic("stop",24)}Zu groß für Kompakt</span>'
        '<span style="font-size: 14px; line-height: 20px; color: #4a453c">Die Vorderseite lässt zu wenig Platz für Übersicht und Einstellungen. „Kompakt“ ist dann abgeblendet; es bleiben Lochmuster 1:1 und Anleitung.</span>'
        '<span style="font-size: 14px; line-height: 20px; color: #4a453c">Richtwert: Vorderseite bis etwa 150 mm Höhe auf A4 quer, bis etwa 215 mm auf A4 hoch.</span></div>')
save('Kompakt-Faelle.dc.html', doc('Kompakt: Fälle', 1560, 900,
    '<div style="position: absolute; left: 64px; top: 48px; right: 64px; display: flex; flex-direction: column; gap: 8px"><h1 style="margin: 0; font-family: \'Newsreader\', Georgia, serif; font-size: 34px; line-height: 40px; font-weight: 700">Kompakt-PDF: Grenzfälle</h1>'
    '<span style="font-size: 15px; line-height: 21px; color: #4a453c; max-width: 1000px">Kompakt braucht neben dem Lochmuster Platz für Übersicht und Einstellungen. Oben links bequem, in der Mitte der Grenzfall (A5), rechts die Folge, wenn es nicht mehr passt.</span></div>'
    '<div style="position: absolute; left: 64px; top: 168px; right: 64px; display: grid; grid-template-columns: 326px 326px 326px; gap: 40px; align-items: end">'
    + case_card(kp1,'A6 hoch · Falz oben','A4 hoch · 1:1 · Rückseite angedeutet','check','Kompakt passt bequem','Übersicht rechts, Einstellungen darunter.')
    + case_card(kp2,'A5 hoch · Falz links','A4 hoch · 1:1 · Rückseite angedeutet','info','Grenzfall','Nur ein schmales Band unten bleibt für Übersicht und Einstellungen.')
    + '<div style="display: flex; flex-direction: column; gap: 12px">' + txt3 + '<div style="display: flex; flex-direction: column; gap: 6px"><b style="font-size: 17px; line-height: 22px">Größere Vorderseite</b><span style="font-size: 14px; line-height: 20px; color: #4a453c">z. B. 150 × 230 mm</span><span style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: #9a5a00">' + ic("warn",20) + 'Kompakt nicht anwählbar</span></div></div>'
    + '</div>', bg='#f4f0e6'))
c = json.load(open(OUT+'canvas.json')); B = c['boards']
B['Kompakt-PDF.dc.html'] = {"x":3050,"y":0,"w":1188,"h":840,"title":"Kompakt-PDF (A4 quer, 1 Seite, Beispiel)"}
B['iPhone-Ausgabe.dc.html'] = {"x":3050,"y":960,"w":390,"h":844,"title":"iPhone · Ausgabe"}
B['Lochmuster-Faelle.dc.html'] = {"x":3050,"y":2000,"w":1560,"h":860,"title":"Lochmuster-Seite: Formatfälle (S/W, 1:1)"}
B['Kompakt-Faelle.dc.html'] = {"x":4700,"y":2000,"w":1560,"h":900,"title":"Kompakt-PDF: Grenzfälle (S/W, 1:1)"}
B['iPad-Ausgabe.dc.html'] = {"x":3520,"y":960,"w":1180,"h":820,"title":"iPad · Ausgabe mit PDF-Vorschau"}
for k in ['Kompakt-PDF.dc.html','iPhone-Ausgabe.dc.html','iPad-Ausgabe.dc.html','Lochmuster-Faelle.dc.html','Kompakt-Faelle.dc.html']:
    if k not in c['order']: c['order'].append(k)
json.dump(c, open(OUT+'canvas.json','w'), ensure_ascii=False, indent=2)
print('ok')
