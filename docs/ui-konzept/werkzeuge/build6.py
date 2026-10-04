import sys, json
sys.path.insert(0,'.')
import lib
from lib import *
OUT='/tmp/claude-0/-home-user-Stickkarten/7d64d15f-70be-5a8c-bbc1-d86911943200/scratchpad/konzept1/project/'
def save(name, html): open(OUT+name,'w').write(html)
lib.ICON['close']='<path d="M6 6l12 12M18 6L6 18"/>'
lib.ICON['check']='<circle cx="12" cy="12" r="10" fill="currentColor" stroke="none"/><path d="M7.5 12.5l3 3 6-7" stroke="#ffffff"/>'
lib.ICON['next']='<path d="M9 6l6 6-6 6"/>'
lib.ICON['stufen']='<path d="M4 20h16M6 20v-4h4v-4h4V8h4V4"/>'
lib.ICON['wizard']='<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5L18 18M18 6l-2.5 2.5M8.5 15.5L6 18"/>'
lib.ICON['kartehoch']='<rect x="7" y="3" width="10" height="18" rx="2"/>'
lib.ICON['kartequer']='<rect x="3" y="7" width="18" height="10" rx="2"/>'
lib.ICON['both']='<path d="M12 3l8 14H4zM12 21L4 7h16z"/><path d="M12 21V9M12 15l-5-4M12 12l5-4"/>'
lib.ICON['auswahl']='<rect x="3" y="6" width="5" height="12" rx="1.5"/><rect x="9.5" y="6" width="5" height="12" rx="1.5"/><rect x="16" y="6" width="5" height="12" rx="1.5"/>'
lib.ICON['mischen']='<path d="M4 7h3c5 0 5 10 10 10h3M4 17h3c1.5 0 2.5-.8 3.5-2M13.5 9C14.5 7.8 15.5 7 17 7h3M17 4l3 3-3 3M17 14l3 3-3 3"/>'
lib.ICON['regler']='<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>'
lib.ICON['sternloch']='<path d="M12 3l8 14H4zM12 21L4 7h16z"/>'

# ---- Karte mit wählbaren Ebenen / Farben ----
def cardL(left, top, w, h, layers=(), karton='#153a2c', faden=None, holes=True, s1k=3, s2k=1, w_=None):
    faden = faden or {'aeste': '#e8c987', 'stern1': '#e8c987', 'stern2': '#e8c987'}
    s = f'<svg viewBox="0 0 105 148" style="position: absolute; left: {left}px; top: {top}px; width: {w}px; height: {h}px; border-radius: 8px; display: block; box-shadow: 0 14px 36px rgba(30,42,51,.28)"><rect width="105" height="148" fill="{karton}"/><path d="M0.4 0V148" stroke="#000" stroke-opacity=".35" stroke-width=".4" stroke-dasharray="2 1.5"/><g fill="none" stroke-width=".5">'
    if 'aeste' in layers: s += f'<path d="{"".join(f"M58 74L{a} {b}" for a,b in P)}" stroke="{faden["aeste"]}"/>'
    if 'stern2' in layers: s += f'<path d="{pathpts(Q,s2k)}" stroke="{faden["stern2"]}"/>'
    if 'stern1' in layers: s += f'<path d="{pathpts(P,s1k)}" stroke="{faden["stern1"]}"/>'
    s += '</g>'
    if holes: s += '<g fill="#0c1f17" fill-opacity=".85">' + ''.join(f'<circle cx="{a}" cy="{b}" r=".9"/>' for a, b in P + Q + [(58,74)]) + '</g>'
    return s + '</svg>\n'

# ---- Kopfzeile ----
STEPS = [('karte','Format'),('aeste','Stil'),('stufen','Aufwand'),('palette','Farben'),('auswahl','Auswahl')]
def wiz_top(active, left=16, right=16, top=59, width=None):
    segs = ''
    for i, (ico, lab) in enumerate(STEPS):
        if i == active:
            segs += f'<a href="#" style="flex: 0 0 auto; padding: 0 14px; display: flex; align-items: center; gap: 6px; background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); border-radius: 19px; font-size: 14px; font-weight: 600">{ic(ico,20)}{lab}</a>'
        else:
            done = i < active
            segs += f'<a href="#" aria-label="{lab}" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; border-radius: 19px; color: {"#1f5a4b" if done else "#1e2a33"}; opacity: {1 if done else .75}">{ic(ico,20)}</a>'
    seg = f'<div class="glass" style="flex-grow: 1; height: 44px; box-sizing: border-box; padding: 3px; display: flex; gap: 2px; border-radius: 22px">{segs}</div>'
    return (f'  <div style="position: absolute; left: {left}px; right: {right}px; top: {top}px; height: 44px; display: flex; gap: 8px; align-items: center">\n'
            f'    <a href="#" aria-label="Zurück" class="glass" style="width: 44px; height: 44px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("back")}</a>\n    {seg}\n'
            f'    <a href="#" aria-label="Abbrechen" class="glass" style="width: 44px; height: 44px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("close")}</a>\n  </div>\n')

# ---- Bausteine ----
def optile(ico, label, sel, sub=''):
    ring = 'border: 2px solid #1f5a4b; background: #e3eee8;' if sel else 'border: 1px solid #d9d3c4; background: #ffffff;'
    chk = f'<span style="position: absolute; right: 8px; top: 8px; color: #1f5a4b; display: flex">{ic("check",22)}</span>' if sel else ''
    return (f'<a href="#" style="position: relative; flex: 1 1 0; min-height: 104px; box-sizing: border-box; padding: 12px 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; border-radius: 22px; {ring}">{chk}'
            f'<span style="color: #1f5a4b; display: flex">{ic(ico,32)}</span><b style="font-size: 16px; line-height: 20px">{label}</b>{sub}</a>')
def dots(n):
    return '<span style="display: flex; gap: 4px">' + ''.join(f'<i style="width: 8px; height: 8px; border-radius: 50%; background: {"#1f5a4b" if i < n else "#cfc8b8"}"></i>' for i in range(3)) + '</span>'
def seg3(opts, sel):
    it = ''
    for i, (ico, lab) in enumerate(opts):
        if i == sel: it += f'<a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); border-radius: 19px; font-size: 14px; font-weight: 600">{ic(ico,20)}{lab}</a>'
        else: it += f'<a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; border-radius: 19px; font-size: 14px">{ic(ico,20)}{lab}</a>'
    return f'<div style="height: 44px; box-sizing: border-box; padding: 3px; display: flex; gap: 2px; background: #e6e1d4; border-radius: 22px">{it}</div>'
def swrow(label, ico, colors, sel):
    sw = ''
    for i, c in enumerate(colors):
        ring = 'box-shadow: 0 0 0 2px #ffffff, 0 0 0 4px #1f5a4b;' if i == sel else ''
        sw += f'<a href="#" aria-label="{label} {i+1}" style="width: 44px; height: 44px; display: flex; align-items: center; justify-content: center"><i style="width: 32px; height: 32px; border-radius: 50%; background: {c}; border: 1px solid rgba(30,42,51,.3); {ring}"></i></a>'
    return (f'<div style="min-height: 64px; box-sizing: border-box; padding: 0 8px 0 16px; display: flex; align-items: center; gap: 10px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px"><span style="color: #1f5a4b; display: flex">{ic(ico)}</span><span style="flex-grow: 1; font-size: 16px">{label}</span>{sw}</div>')
def cta(label, ico='next', primary=True, grow=True):
    bg = 'background: #1f5a4b; color: #ffffff;' if primary else 'background: #efeadd;'
    return f'<a href="#" style="{"flex: 1 1 0;" if grow else ""} height: 52px; display: flex; align-items: center; justify-content: center; gap: 8px; {bg} border-radius: 26px; font-size: 17px; font-weight: 600">{label}{ic(ico)}</a>'
def panel(top, title, body, footer):
    return (f'  <div class="sheet" style="position: absolute; left: 0; right: 0; top: {top}px; bottom: 0; box-sizing: border-box; padding: 22px 16px 0; border-radius: 34px 34px 0 0; display: flex; flex-direction: column; gap: 12px; overflow: hidden; background: rgba(250,248,242,.94)">\n'
            f'    <h2 style="margin: 0; font-family: \'Newsreader\', Georgia, serif; font-size: 28px; line-height: 34px; font-weight: 600">{title}</h2>\n    {body}\n    <div style="display: flex; gap: 8px; margin-top: auto; padding-bottom: 34px">{footer}</div>\n  </div>\n')
KART = ['#153a2c', '#10203a', '#481621', '#efe6d6']
FAD = ['#e8c987', '#d9e2e7', '#ffffff', '#3a5a8c']
ALL = {'aeste': '#e8c987', 'stern1': '#e8c987', 'stern2': '#e8c987'}

def phone(name, title, active, card, panel_html):
    save(name, doc(title, 390, 844, card + wiz_top(active) + panel_html))
# G1 Format
phone('Gefuehrt-iPhone-1-Format.dc.html','Geführter Weg 1 Format',0, cardL(72,108,245,346,()),
  panel(470,'Welche Karte?', '<div style="display: flex; gap: 10px">'+optile('kartehoch','A6 hoch',True)+optile('kartequer','A6 quer',False)+'</div>'+seg3([('karte','Falz links'),('karte','Oben'),('karte','Keiner')],0), cta('Weiter')))
# G2 Stil
phone('Gefuehrt-iPhone-2-Stil.dc.html','Geführter Weg 2 Stil',1, cardL(72,108,245,346,('stern1',)),
  panel(470,'Welcher Stil?', '<div style="display: flex; gap: 10px">'+optile('aeste','Flocke',False)+optile('sternloch','Stern',True)+optile('both','Beides',False)+'</div>', cta('Weiter')))
# ---- Farbwelten und Aufwandsstufen ----
WELTEN = [  # Karton, Äste, Stern 1, Stern 2
  ('#153a2c','#e8c987','#ffffff','#e0a08a'),
  ('#10203a','#d9e2e7','#ffffff','#8fb3d9'),
  ('#481621','#e8c987','#efe6d6','#d98a8a'),
  ('#efe6d6','#3a5a8c','#153a2c','#b0443a')]
STUFEN = [('Leicht',1,('stern1',),'bis 40 Stiche'),('Mittel',2,('aeste','stern1'),'40–120 Stiche'),('Aufwendig',3,('aeste','stern1','stern2'),'bis 300 Stiche')]
def fad(w): return {'aeste': w[1], 'stern1': w[2], 'stern2': w[3]}
def lvfad(w, n):  # Leicht: nur eine Farbe (Stern 1 in der Fadenfarbe der Welt)
    f = fad(w)
    if n == 1: f['stern1'] = w[1]
    return f
def mini(layers, w, n, W, H):
    return (cardL(0,0,W,H,layers,karton=w[0],faden=lvfad(w,n)).replace('position: absolute; left: 0px; top: 0px; ','position: relative; ')
            .replace('box-shadow: 0 14px 36px rgba(30,42,51,.28)','box-shadow: 0 2px 6px rgba(30,42,51,.25)'))
def tile(inner, sel, extra=''):
    ring = 'border: 2px solid #1f5a4b; background: #e3eee8;' if sel else 'border: 1px solid #d9d3c4; background: #ffffff;'
    chk = f'<span style="position: absolute; right: 6px; top: 6px; color: #1f5a4b; display: flex; background: #ffffff; border-radius: 50%">{ic("check",22)}</span>' if sel else ''
    return f'<a href="#" style="position: relative; flex: 1 1 0; box-sizing: border-box; padding: 14px 4px; display: flex; flex-direction: column; align-items: center; gap: 6px; border-radius: 22px; {ring}">{chk}{inner}</a>'
SEL_W = WELTEN[0]
# G3 Aufwand: Kacheln zeigen das Muster in 1 / 2 / 3 Farben
def stufe_tiles(sel, W=70, H=99):
    out = ''
    for i,(n,k,lay,st) in enumerate(STUFEN):
        out += tile(mini(lay,SEL_W,k,W,H)+f'<b style="font-size: 16px; line-height: 20px">{n}</b>{dots(k)}<span style="font-size: 13px; line-height: 17px; color: #5f594e; text-align: center">{st}</span>', i==sel)
    return out
phone('Gefuehrt-iPhone-3-Aufwand.dc.html','Geführter Weg 3 Aufwand',2, cardL(72,108,245,346,STUFEN[1][2],karton=SEL_W[0],faden=lvfad(SEL_W,2)),
  panel(470,'Wie aufwendig?', '<div style="display: flex; gap: 8px">'+stufe_tiles(1)+'</div><span style="font-size: 13px; line-height: 18px; color: #5f594e">Mehr Aufwand heißt mehr Elemente, mehr Farben und mehr Stiche.</span>', cta('Weiter')))
# G4 Farben: Farbwelten (streng eine Auswahl)
def welt_tiles(sel, n, W=70, H=99):
    lay = STUFEN[1][2]
    return ''.join(tile(mini(lay,w,n,W,H), i==sel) for i,w in enumerate(WELTEN))
phone('Gefuehrt-iPhone-4-Farben.dc.html','Geführter Weg 4 Farben',3, cardL(72,108,245,346,STUFEN[1][2],karton=SEL_W[0],faden=lvfad(SEL_W,2)),
  panel(470,'Welche Farbwelt?', '<div style="display: flex; gap: 8px">'+welt_tiles(0,2)+'</div><span style="font-size: 13px; line-height: 18px; color: #5f594e">Fein einstellen kannst du jede Farbe später im Editor.</span>', cta('Varianten zeigen')))

# G5 Auswahl
VARS = [('Klassisch','',dict(layers=('aeste','stern1'),s1k=3,s2k=1)),
        ('Zart','',dict(layers=('aeste','stern1'),s1k=2,s2k=1)),
        ('Dicht','',dict(layers=('aeste','stern1'),s1k=4,s2k=1))]
def vthumb(name, sub, kw, sel, W=86, H=121):
    ring = 'border: 2px solid #1f5a4b; background: #e3eee8;' if sel else 'border: 1px solid #d9d3c4; background: #ffffff;'
    chk = f'<span style="position: absolute; right: 6px; top: 6px; color: #1f5a4b; display: flex; background: #ffffff; border-radius: 50%">{ic("check",22)}</span>' if sel else ''
    svg = cardL(0,0,W,H,kw['layers'],karton=SEL_W[0],faden=FAD2,s1k=kw['s1k'],s2k=kw['s2k']).replace('position: absolute; left: 0px; top: 0px; ','position: relative; ').replace('box-shadow: 0 14px 36px rgba(30,42,51,.28)','box-shadow: 0 2px 6px rgba(30,42,51,.25)')
    return (f'<a href="#" style="position: relative; flex: 1 1 0; box-sizing: border-box; padding: 14px 4px; display: flex; flex-direction: column; align-items: center; gap: 6px; border-radius: 22px; {ring}">{chk}{svg}</a>')
FAD2 = lvfad(SEL_W,2)
def auswahl_body(sel):
    return '<div style="display: flex; gap: 8px">' + ''.join(vthumb(n,sb,kw,i==sel) for i,(n,sb,kw) in enumerate(VARS)) + '</div>'
for idx in (0,):
    n,sb,kw = VARS[idx]
    swipe = f'<span style="position: absolute; left: 0; right: 0; top: 462px"></span>'
    phone('Gefuehrt-iPhone-5-Auswahl.dc.html','Geführter Weg 5 Auswahl',4,
      cardL(72,108,245,346,kw['layers'],karton=SEL_W[0],faden=FAD2,s1k=kw['s1k'],s2k=kw['s2k']),
      panel(470,'Welche Variante?', auswahl_body(idx)+'<span style="font-size: 13px; line-height: 18px; color: #5f594e">Drei fest abgestimmte Muster zu deinen Angaben. Im Editor änderbar.</span>',
        cta('Diese nehmen','check')))
# G6 Ergebnis
res = cardL(60,108,270,381,('aeste','stern1'),karton=SEL_W[0],faden=FAD2)
res += f'  <a href="#" aria-label="Als Favorit sichern" class="glass" style="position: absolute; left: 276px; top: 118px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("star")}</a>\n'
bar = (f'  <div style="position: absolute; left: 16px; right: 16px; top: 59px; height: 44px; display: flex; gap: 8px; align-items: center"><a href="#" aria-label="Zurück" class="glass" style="width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("back")}</a><div style="flex-grow: 1"></div><a href="#" aria-label="Schließen" class="glass" style="width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("close")}</a></div>\n')
foot = cta('Anpassen','regler',False)+cta('Als PDF','printer')
pn = panel(520,'Dein Muster ist fertig','<span style="font-size: 15px; line-height: 21px; color: #5f594e">Als PDF ausgeben oder im Editor weiter anpassen.</span>',foot)
save('Gefuehrt-iPhone-6-Ergebnis.dc.html', doc('Geführter Weg 6 Ergebnis',390,844, res+bar+pn))

# ---- iPad ----
def ipad_wiz(name, title, active, card, h2, body, footer):
    top = (f'  <a href="#" aria-label="Zurück" class="glass" style="position: absolute; left: 16px; top: 16px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("back")}</a>\n'
           f'  <div style="position: absolute; left: 228px; top: 16px; width: 380px; display: flex">'
           + wiz_top(active, 0, 0, 0).replace('position: absolute; left: 0px; right: 0px; top: 0px; height: 44px; display: flex; gap: 8px; align-items: center','display: flex; flex-grow: 1; gap: 8px; align-items: center').replace(f'<a href="#" aria-label="Zurück" class="glass" style="width: 44px; height: 44px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("back")}</a>\n','').replace(f'    <a href="#" aria-label="Abbrechen" class="glass" style="width: 44px; height: 44px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("close")}</a>\n','')
           + '</div>\n'
           f'  <a href="#" aria-label="Abbrechen" class="glass" style="position: absolute; left: 696px; top: 16px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("close")}</a>\n')
    pn = ('  <aside class="glass" style="position: absolute; right: 12px; top: 12px; bottom: 12px; width: 400px; box-sizing: border-box; padding: 24px 16px 16px; border-radius: 34px; background: rgba(250,248,242,.9); display: flex; flex-direction: column; gap: 14px; overflow: hidden">\n'
          f'    <h2 style="margin: 0; font-family: \'Newsreader\', Georgia, serif; font-size: 30px; line-height: 36px; font-weight: 600">{h2}</h2>\n    {body}\n    <div style="display: flex; gap: 8px; margin-top: auto">{footer}</div>\n  </aside>\n')
    save(name, doc(title, 1180, 820, card + top + pn))
def lrow(ico, label, sub, sel):
    ring = 'border: 2px solid #1f5a4b; background: #e3eee8;' if sel else 'border: 1px solid #d9d3c4; background: #ffffff;'
    chk = f'<span style="color: #1f5a4b; display: flex">{ic("check",26)}</span>' if sel else '<span style="width: 26px; height: 26px; box-sizing: border-box; border-radius: 50%; border: 2px solid #cfc8b8"></span>'
    return f'<a href="#" style="min-height: 76px; box-sizing: border-box; padding: 0 16px; display: flex; align-items: center; gap: 14px; border-radius: 22px; {ring}"><span style="color: #1f5a4b; display: flex">{ic(ico,32)}</span><span style="flex-grow: 1; display: flex; flex-direction: column"><b style="font-size: 17px; line-height: 22px">{label}</b><span style="font-size: 13px; line-height: 18px; color: #5f594e">{sub}</span></span>{chk}</a>'
body_stil = lrow('aeste','Flocke','Äste von der Mitte nach außen',False)+lrow('sternloch','Stern','Sehnen zwischen den Punkten',True)+lrow('both','Beides','Flocke und Stern kombiniert',False)
ipad_wiz('Gefuehrt-iPad-2-Stil.dc.html','Geführter Weg iPad Stil',1, cardL(158,84,440,620,('stern1',)), 'Welcher Stil?', body_stil, cta('Weiter'))
# iPad Ergebnis
res_i = cardL(158,84,440,620,('aeste','stern1'),karton=SEL_W[0],faden=FAD2)
res_i += f'  <a href="#" aria-label="Als Favorit sichern" class="glass" style="position: absolute; left: 544px; top: 98px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("star")}</a>\n'
foot_i = cta('Anpassen','regler',False)+cta('Als PDF','printer')
def lrow_m(inner, label, sub, sel):
    ring = 'border: 2px solid #1f5a4b; background: #e3eee8;' if sel else 'border: 1px solid #d9d3c4; background: #ffffff;'
    chk = f'<span style="color: #1f5a4b; display: flex">{ic("check",26)}</span>' if sel else '<span style="width: 26px; height: 26px; box-sizing: border-box; border-radius: 50%; border: 2px solid #cfc8b8"></span>'
    return f'<a href="#" style="min-height: 104px; box-sizing: border-box; padding: 0 16px; display: flex; align-items: center; gap: 14px; border-radius: 22px; {ring}">{inner}<span style="flex-grow: 1; display: flex; flex-direction: column"><b style="font-size: 17px; line-height: 22px">{label}</b><span style="font-size: 13px; line-height: 18px; color: #5f594e">{sub}</span></span>{chk}</a>'
body_aw = ''.join(lrow_m(mini(lay,SEL_W,kk,60,85), n, f'{kk} Farbe{"n" if kk>1 else ""} · {st}', i==1) for i,(n,kk,lay,st) in enumerate(STUFEN))
ipad_wiz('Gefuehrt-iPad-3-Aufwand.dc.html','Geführter Weg iPad Aufwand',2, cardL(158,84,440,620,STUFEN[1][2],karton=SEL_W[0],faden=lvfad(SEL_W,2)), 'Wie aufwendig?', body_aw, cta('Weiter'))
ipad_wiz('Gefuehrt-iPad-4-Farben.dc.html','Geführter Weg iPad Farben',3, cardL(158,84,440,620,STUFEN[1][2],karton=SEL_W[0],faden=lvfad(SEL_W,2)), 'Welche Farbwelt?',
  '<div style="display: flex; gap: 10px">'+welt_tiles(0,2,72,101).replace('flex: 1 1 0;','flex: 1 1 0;')+'</div><span style="font-size: 15px; line-height: 21px; color: #5f594e">Fein einstellen kannst du jede Farbe später im Editor.</span>', cta('Varianten zeigen'))
ipad_wiz('Gefuehrt-iPad-5-Auswahl.dc.html','Geführter Weg iPad Auswahl',4, cardL(158,84,440,620,VARS[0][2]['layers'],karton=SEL_W[0],faden=FAD2,s1k=3,s2k=1), 'Welche Variante?',
  '<div style="display: flex; gap: 10px">'+''.join(vthumb(n,sb,kw,k==0,104,147) for k,(n,sb,kw) in enumerate(VARS))+'</div><span style="font-size: 15px; line-height: 21px; color: #5f594e">Drei fest abgestimmte Muster zu deinen Angaben. Im Editor änderbar.</span>',
  cta('Diese nehmen','check'))
ipad_wiz('Gefuehrt-iPad-6-Ergebnis.dc.html','Geführter Weg iPad Ergebnis',4, res_i, 'Dein Muster ist fertig', '<span style="font-size: 15px; line-height: 21px; color: #5f594e">Als PDF ausgeben oder im Editor weiter anpassen.</span>', foot_i)
print('ok')
