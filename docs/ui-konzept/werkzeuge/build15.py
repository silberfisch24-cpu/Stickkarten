import sys, re
sys.path.insert(0,'.')
b11 = open('build11.py').read()
exec(b11[:b11.index('# ---------- iPhone Hauptreihe ----------')])
PROJ = OUT
SEL_W = WELTEN[0]
b8 = open('build8.py').read()

s8 = b8[b8.index("lib.ICON['pencil']"):b8.index('# 1 Favoriten gefüllt')]
exec(s8)

print([k for k in globals() if k in ('ASIDE','NAV','CAPS','wiz_top','ipad_wiz','topbar2','sheet3','FAV','ptile','start_frame')])

# ======================= Neue Boards (Page "Lücken") =======================
MS = open(PROJ+'iPhone-Mehr.dc.html').read()
MEHR_NAV = MS[MS.index('<nav'):MS.index('</nav>')+6]
MEHR_CAPS = MS[MS.index('<a href="#" class="glass" style="position: absolute; left: 16px; right: 16px; bottom: 94px'):MS.index('<nav')]
EXTRA_CSS = MS[MS.index('.row{'):MS.index('</style>')]
LIST_ICO = {
 'shield':'<path d="M12 3l7 3v5c0 5-3 8-7 10-4-2-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
 'book':'<path d="M5 4h10a3 3 0 013 3v13H8a3 3 0 01-3-3zM5 17a3 3 0 013-3h10"/>',
 'info':'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>',
 'search':'<circle cx="11" cy="11" r="7"/><path d="M16 16l5 5"/>',
 'hand':'<path d="M8 12V6a1.5 1.5 0 013 0v5M11 11V4.5a1.5 1.5 0 013 0V11M14 11V6a1.5 1.5 0 013 0v7c0 4-2 7-6 7-3 0-4-2-6-5l-1-2a1.5 1.5 0 012-2l2 2"/>',
 'doc':'<path d="M6 3h8l4 4v14H6zM14 3v4h4M9 12h6M9 16h6"/>',
 'scale':'<path d="M4 6h16M4 6v12h16V6M8 6v4M12 6v3M16 6v4"/>',
 'bulb':'<path d="M9 18h6M10 21h4M12 3a6 6 0 00-3.5 11c.6.6 1 1.3 1 2h5c0-.7.4-1.4 1-2A6 6 0 0012 3z"/>',
 'next':'<path d="M9 6l6 6-6 6"/>',
 'chev':'<path d="M9 6l6 6-6 6"/>',
}
for k,v in LIST_ICO.items(): lib.ICON.setdefault(k,v)
lib.ICON['info']=LIST_ICO['info']
GRN = lambda s: f'<span style="color: #1f5a4b; display: flex">{s}</span>'
def lrow(ico, label, sub='', red=False, chev=True, value=''):
    c = '#b3261e' if red else '#1f5a4b'
    subh = f'<span style="display: block; font-size: 13px; line-height: 17px; color: #5f594e; font-weight: 400">{sub}</span>' if sub else ''
    val = f'<span style="color: #5f594e; font-size: 16px">{value}</span>' if value else ''
    ch = '<svg class="i c" viewBox="0 0 24 24" aria-hidden="true" style="margin-left: auto"><path d="M9 6l6 6-6 6"/></svg>' if chev else ''
    ml = 'margin-left: auto;' if value else ''
    return (f'<a href="#" class="row"><svg class="i" viewBox="0 0 24 24" aria-hidden="true" style="color: {c}; width: 28px; height: 28px">{lib.ICON[ico]}</svg>'
            f'<span class="t" style="{"color: #b3261e;" if red else ""}"><span style="display: flex; flex-direction: column"><span>{label}</span>{subh}</span><span style="{ml}">{val}</span>{ch if not value else ch.replace("margin-left: auto","margin-left: 0")}</span></a>')
def grp(*rows, style=''): return f'<div class="grp" style="{style}">'+''.join(rows)+'</div>'
def mdoc(name, title, body, nav=True, caps=False):
    html = doc(title,390,844,body+(MEHR_CAPS if caps else '')+(MEHR_NAV if nav else ''),'#f4f0e6')
    html = html.replace('</style>', EXTRA_CSS+'</style>',1)
    save(name, html)
def backbar(label='Mehr'):
    return (f'  <a href="#" aria-label="Zurück" class="glass" style="position: absolute; left: 16px; top: 59px; height: 44px; box-sizing: border-box; padding: 0 16px 0 8px; display: flex; align-items: center; gap: 2px; border-radius: 22px; font-size: 16px; font-weight: 600">{ic("back")}{label}</a>\n')
def mpage(h1, inner, label='Mehr', size=34):
    return (backbar(label)+f'  <div style="position: absolute; left: 0; right: 0; top: 115px; bottom: 100px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px; overflow: hidden">\n'
            f'    <h1 style="margin: 0 16px 4px; font-family: \'Newsreader\', Georgia, serif; font-size: {size}px; line-height: {size+6}px; font-weight: 700">{h1}</h1>\n{inner}\n  </div>\n')
def segcard(label, ico, opts, sel):
    o=''
    for i,t in enumerate(opts):
        st = 'background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); font-weight: 600;' if i==sel else ''
        o += f'<a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; border-radius: 19px; font-size: 14px; {st}">{t}</a>'
    return (f'<div style="margin: 0 16px; box-sizing: border-box; padding: 12px 16px; display: flex; flex-direction: column; gap: 10px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px">'
            f'<div style="display: flex; align-items: center; gap: 12px"><span style="color: #1f5a4b; display: flex">{ic(ico)}</span><span style="font-size: 16px">{label}</span></div>'
            f'<div style="height: 44px; box-sizing: border-box; padding: 3px; display: flex; gap: 2px; background: #e6e1d4; border-radius: 22px">{o}</div></div>')
def mtoggle(label, ico, on=True): return '<div style="margin: 0 16px; display: flex; flex-direction: column">'+toggle(label,ico,on)+'</div>'
def note(t): return f'<p style="margin: 0 32px; font-size: 13px; line-height: 18px; color: #5f594e">{t}</p>'

# ---- 1 Einstellungen
mdoc('iPhone-Einstellungen.dc.html','iPhone Einstellungen', mpage('Einstellungen',
  segcard('Standardformat','karte',['A6 hoch','A6 quer'],0)+segcard('Falz','falzl',['Links','Oben','Keiner'],0)
  +mtoggle('Haptische Rückmeldung','hand',True)+mtoggle('Weitermachen anzeigen','play',True)
  +note('Format und Falz gelten für neue Muster. Das Erscheinungsbild folgt dem System.')))
# ---- 2 Hilfe
mdoc('iPhone-Hilfe.dc.html','iPhone Hilfe', mpage('Hilfe',
  grp(lrow('wizard','Erste Schritte'),lrow('regler','Muster gestalten'),lrow('warn','Warnungen verstehen'),lrow('play','Sticken nach Stichfolge'),lrow('printer','Drucken und Papier'))
  + grp(lrow('book','Glossar'))))
# ---- 3 Hilfe-Thema
def pill(kind, ico, t):
    c={'ok':('#e0f0e6','#14603a'),'warn':('#fcefd9','#6b3f00'),'crit':('#fde7e3','#8f1d14')}[kind]
    return f'<span style="align-self: flex-start; display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px 4px 10px; border-radius: 16px; background: {c[0]}; color: {c[1]}; font-size: 14px; line-height: 20px; font-weight: 600">{ic(ico,18)}{t}</span>'
def hcard(kind, ico, t, text, mini=''):
    return (f'<div style="margin: 0 16px; box-sizing: border-box; padding: 14px 16px; display: flex; gap: 14px; align-items: center; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px">'
            f'<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 6px">{pill(kind,ico,t)}<span style="font-size: 15px; line-height: 21px">{text}</span></div>{mini}</div>')
def minidist(d, col):
    return (f'<svg viewBox="0 0 60 60" style="width: 64px; height: 64px; flex-shrink: 0"><rect width="60" height="60" rx="14" fill="#efeadd"/>'
            f'<circle cx="{30-d}" cy="24" r="4.5" fill="#153a2c"/><circle cx="{30+d}" cy="24" r="4.5" fill="#153a2c"/>'
            f'<path d="M{30-d} 38H{30+d}M{30-d} 34V42M{30+d} 34V42" stroke="{col}" stroke-width="2.2" stroke-linecap="round" fill="none"/></svg>')
mdoc('iPhone-Hilfe-Thema.dc.html','iPhone Hilfe Thema', mpage('Warnungen verstehen',
  hcard('ok','check','Kein Fehler','Alle Löcher haben genug Abstand.',minidist(13,'#14603a'))
  +hcard('warn','warn','Knapp','Der Faden liegt eng. Die Karte lässt sich noch sticken.',minidist(8,'#9a5a00'))
  +hcard('crit','stop','Zu eng','Löcher würden reißen. Drucken ist gesperrt.',minidist(4,'#b3261e'))
  +grp(lrow('book','Glossar'),lrow('regler','Abstände anpassen')), 'Hilfe', 30))
# ---- 4 Glossar
TERMS=[('Äste','Linien vom Mittelpunkt nach außen, mit Seitenästen.'),('Falz','Die Knickkante der Karte.'),('Grundform','Strahlen und Ebenen, auf denen alle Löcher liegen.'),
 ('Lochabstand','Kleinster Abstand zweier Löcher, in Millimetern.'),('Sprung','Der Faden läuft auf der Rückseite zum nächsten Loch.'),('Stern 1 und 2','Sternlinien zwischen Löchern der Grundform.'),('Stich','Eine Linie von Loch zu Loch.'),('Stichfolge','Alle Stiche in der Reihenfolge des Stickens.')]
def trow(t,d,last=False):
    bd = '' if last else 'border-bottom: 1px solid #ddd7c8;'
    return f'<div style="box-sizing: border-box; padding: 10px 16px; display: flex; flex-direction: column; gap: 2px; {bd}"><b style="font-size: 17px; line-height: 22px">{t}</b><span style="font-size: 14px; line-height: 19px; color: #5f594e">{d}</span></div>'
search = f'<div style="margin: 0 16px; height: 44px; box-sizing: border-box; padding: 0 14px; display: flex; align-items: center; gap: 8px; background: #e6e1d4; border-radius: 22px; color: #5f594e; font-size: 16px">{ic("search",20)}Suchen</div>'
mdoc('iPhone-Glossar.dc.html','iPhone Glossar', mpage('Glossar', search+'<div class="grp" style="overflow: hidden">'+''.join(trow(t,d,i==len(TERMS)-1) for i,(t,d) in enumerate(TERMS))+'</div>','Mehr'))
# ---- 5 Info und Datenschutz
appico = ('<svg viewBox="0 0 105 148" style="width: 56px; height: 78px; border-radius: 8px; box-shadow: 0 3px 10px rgba(30,42,51,.25)"><rect width="105" height="148" fill="#153a2c"/>'
          '<g stroke="#e8c987" stroke-width="2" fill="none"><path d="M58 38L83.5 99.5M83.5 48.5L58 110M94 74L32.5 99.5M83.5 99.5L22 74M58 110L32.5 48.5M32.5 99.5L58 38M22 74L83.5 48.5M32.5 48.5L94 74"/></g></svg>')
hero_i = f'<div style="display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 6px 0 4px">{appico}<b style="font-family: Newsreader, Georgia, serif; font-size: 24px; line-height: 30px">Stickkarten</b><span style="font-size: 14px; color: #5f594e">Version 1.0</span></div>'
priv = (f'<div style="margin: 0 16px; box-sizing: border-box; padding: 14px 16px; display: flex; gap: 14px; align-items: center; background: #e0f0e6; color: #14603a; border-radius: 22px"><span style="display: flex">{ic("shield",32)}</span>'
        '<span style="font-size: 15px; line-height: 21px; font-weight: 600">Alles bleibt auf diesem Gerät. Kein Konto, keine Werbung, keine Berechtigungen.</span></div>')
mdoc('iPhone-Info.dc.html','iPhone Info und Datenschutz', mpage('Info und Datenschutz', hero_i+priv+grp(lrow('doc','Datenschutzerklärung'),lrow('book','Lizenzen und Quellen')),'Mehr',30))
# ---- 6 Alles zurücksetzen
base = (backbar('Mehr')*0) + MS[MS.index('  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; box-sizing'):MS.index('</x-dc>')].rstrip()
base = base[:base.rindex('</div>')]
sheetR = ('  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.38); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px)"></div>\n'
  '  <div style="position: absolute; left: 12px; right: 12px; bottom: 34px; display: flex; flex-direction: column; gap: 8px">\n'
  f'    <div class="glass" style="border-radius: 26px; overflow: hidden; background: rgba(250,248,242,.9)"><div style="padding: 14px 16px; text-align: center; font-size: 13px; line-height: 18px; color: #5f594e">Favoriten und Einstellungen werden gelöscht.</div><div style="height: 1px; background: #ddd7c8"></div><a href="#" style="height: 56px; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 17px; color: #b3261e; font-weight: 600">{ic("reset")}Alles zurücksetzen</a></div>\n'
  f'    <a href="#" class="glass" style="height: 56px; display: flex; align-items: center; justify-content: center; border-radius: 28px; font-size: 17px; font-weight: 600; background: rgba(250,248,242,.95)">Abbrechen</a>\n  </div>\n')
mdoc('iPhone-Zuruecksetzen.dc.html','iPhone Zurücksetzen', base+'\n'+sheetR, nav=False)
print('A ok')

# ---- Einführung (3 Seiten, Vollbild ohne Tab-Leiste)
def dotsrow(n, cur):
    return '<div style="display: flex; gap: 8px; justify-content: center">'+''.join(f'<i style="width: {22 if i==cur else 8}px; height: 8px; border-radius: 4px; background: {"#1f5a4b" if i==cur else "#cfc8b8"}"></i>' for i in range(n))+'</div>'
def intro(name, title, art, h, sub, cta_t, cur, skip=True):
    sk = f'  <a href="#" class="glass" style="position: absolute; right: 16px; top: 59px; height: 44px; box-sizing: border-box; padding: 0 18px; display: flex; align-items: center; border-radius: 22px; font-size: 16px; font-weight: 600">Überspringen</a>\n' if skip else ''
    body = (art + sk
      + '  <div style="position: absolute; left: 24px; right: 24px; top: 500px; display: flex; flex-direction: column; gap: 10px; align-items: center; text-align: center">\n'
      + f'    <h1 style="margin: 0; font-family: \'Newsreader\', Georgia, serif; font-size: 34px; line-height: 40px; font-weight: 700">{h}</h1>\n'
      + f'    <span style="font-size: 17px; line-height: 24px; color: #4a453c">{sub}</span>\n  </div>\n'
      + f'  <div style="position: absolute; left: 16px; right: 16px; bottom: 34px; display: flex; flex-direction: column; gap: 18px">{dotsrow(3,cur)}<a href="#" style="height: 56px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #1f5a4b; color: #ffffff; border-radius: 28px; font-size: 17px; font-weight: 600">{cta_t}{ic("next") if cur<2 else ""}</a></div>\n')
    save(name, doc(title,390,844,body,'#f4f0e6'))
P_M = make('beides','mittel')
art1 = svgP(P_M, WELTEN[0], 'mittel', 'mehr', 245, 346, (72,125))
sheet_art = ('  <div class="sheet" style="position: absolute; left: 36px; right: 36px; top: 150px; height: 300px; box-sizing: border-box; padding: 12px 16px; border-radius: 34px; display: flex; flex-direction: column; gap: 10px">'
  + track('aeste', h=44) + slider('Astwinkel','angle','45°',55,False) + slider('Astlänge','laenge','60 %',60,False) + '</div>\n')
art2 = svgP(make('beides','leicht'), WELTEN[1], 'leicht', 'mehr', 110, 155, (40,86), '0 14px 36px rgba(30,42,51,.28)', 'transform: rotate(-6deg);') + sheet_art.replace('left: 36px','left: 100px').replace('right: 36px','right: 20px').replace('top: 150px','top: 140px').replace('height: 300px','height: 280px')
paper = ('<svg viewBox="0 0 105 148" style="position: absolute; left: 48px; top: 130px; width: 170px; height: 240px; background: #ffffff; box-shadow: 0 14px 36px rgba(30,42,51,.28); border-radius: 4px; transform: rotate(-4deg)">'
  + ''.join(f'<circle cx="{P_M["node"][u][0]:.1f}" cy="{P_M["node"][u][1]:.1f}" r="1.1" fill="#1e2a33"/>' for u in P_M['used'])+'</svg>')
card3 = svgP(P_M, WELTEN[0], 'mittel', 'mehr', 150, 211, (190,200), '0 14px 36px rgba(30,42,51,.28)', 'transform: rotate(5deg);')
art3 = paper + card3 + f'  <span class="glass" style="position: absolute; left: 150px; top: 330px; width: 64px; height: 64px; display: flex; align-items: center; justify-content: center; border-radius: 50%; color: #1f5a4b">{ic("printer",30)}</span>\n'
intro('iPhone-Einfuehrung-1.dc.html','iPhone Einführung 1',art1,'Muster zum Sticken','Gestalte Karten aus Linien und Löchern.','Weiter',0)
intro('iPhone-Einfuehrung-2.dc.html','iPhone Einführung 2',art2,'Alles lässt sich anpassen','Regler verändern das Muster sofort.','Weiter',1)
intro('iPhone-Einfuehrung-3.dc.html','iPhone Einführung 3',art3,'Drucken und sticken','Lochmuster ausdrucken, Karte stechen, Stichfolge folgen.','Los geht’s',2,False)

# ---- Kontexthilfe im Editor
eb = open(PROJ+'iPhone-Editor-Sheet.dc.html').read()
body_e = eb[eb.index('<div style="position: relative'):eb.index('</x-dc>')]
body_e = body_e[:body_e.rindex('</div>')]
body_e = body_e.replace('<div class="sheet" style="position: absolute;', f'<div class="sheet" data-x style="position: absolute;',1)
k = body_e.index('data-x'); k2 = body_e.index('>', k)+1
info_btn = f'\n<a href="#" aria-label="Hilfe zur Gruppe" style="position: absolute; left: 10px; top: 0; width: 44px; height: 32px; display: flex; align-items: center; justify-content: center; color: #1f5a4b">{ic("info",22)}</a>'
body_e = body_e[:k2]+info_btn+body_e[k2:]
pop = ('  <div class="glass" style="position: absolute; left: 16px; right: 16px; top: 318px; box-sizing: border-box; padding: 16px; border-radius: 26px; background: rgba(250,248,242,.94); display: flex; flex-direction: column; gap: 10px; box-shadow: 0 10px 40px rgba(30,42,51,.3)">'
  f'<div style="display: flex; align-items: center; gap: 10px"><span style="color: #1f5a4b; display: flex">{ic("aeste",28)}</span><b style="font-family: Newsreader, Georgia, serif; font-size: 22px; line-height: 28px">Äste</b></div>'
  '<span style="font-size: 15px; line-height: 21px">Linien vom Mittelpunkt nach außen. Winkel und Länge bestimmen die Seitenäste.</span>'
  f'<a href="#" style="align-self: flex-start; height: 40px; padding: 0 16px; display: flex; align-items: center; gap: 6px; background: #efeadd; border-radius: 20px; font-size: 15px; font-weight: 600">{ic("book",20)}Im Glossar nachlesen</a></div>\n'
  '  <i style="position: absolute; left: 22px; top: 497px; width: 20px; height: 20px; background: rgba(250,248,242,.94); transform: rotate(45deg); border-radius: 4px"></i>\n')
save('iPhone-Kontexthilfe.dc.html', doc('iPhone Kontexthilfe im Editor',390,844, body_e[body_e.index('\n')+1:]+pop))

# ---- Favoriten: Umbenennen / Löschen
FB = start_frame(grid2([ptile(e,86,121,196) for e in FAV[:6]]))
DIM = '  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.38); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px)"></div>\n'
def keyboard():
    def key(t, w=33, dark=False):
        bg = '#c9c4b6' if dark else '#ffffff'
        return f'<span style="width: {w}px; height: 42px; display: flex; align-items: center; justify-content: center; background: {bg}; border-radius: 6px; font-size: 22px; box-shadow: 0 1px 0 rgba(30,42,51,.3)">{t}</span>'
    r1=''.join(key(c) for c in 'qwertzuiop'); r2=''.join(key(c) for c in 'asdfghjkl'); r3=key('⇧',42,True)+''.join(key(c) for c in 'yxcvbnm')+key('⌫',42,True)
    r4=key('123',90,True)+key('Leerzeichen',170)+key('Fertig',90,True)
    row_ = lambda x: f'<div style="display: flex; gap: 6px; justify-content: center">{x}</div>'
    return f'  <div style="position: absolute; left: 0; right: 0; bottom: 0; height: 300px; box-sizing: border-box; padding: 10px 3px 0; background: #d5d1c4; display: flex; flex-direction: column; gap: 12px">{row_(r1)}{row_(r2)}{row_(r3)}{row_(r4)}</div>\n'
alertR = ('  <div class="glass" style="position: absolute; left: 36px; right: 36px; top: 200px; box-sizing: border-box; padding: 20px 16px 16px; border-radius: 30px; background: rgba(250,248,242,.94); display: flex; flex-direction: column; gap: 12px">'
  '<div style="text-align: center; font-family: Newsreader, Georgia, serif; font-size: 24px; line-height: 30px; font-weight: 600">Umbenennen</div>'
  f'<div style="height: 48px; box-sizing: border-box; padding: 0 14px; display: flex; align-items: center; background: #ffffff; border: 2px solid #1f5a4b; border-radius: 16px; font-size: 17px">Mein Stern<i style="width: 2px; height: 22px; background: #1f5a4b; margin-left: 2px"></i><span style="margin-left: auto; color: #8a8378; display: flex">{ic("close",20)}</span></div>'
  f'<div style="display: flex; gap: 8px"><a href="#" style="flex: 1 1 0; height: 48px; display: flex; align-items: center; justify-content: center; background: #efeadd; border-radius: 24px; font-size: 17px">Abbrechen</a><a href="#" style="flex: 1 1 0; height: 48px; display: flex; align-items: center; justify-content: center; background: #1f5a4b; color: #ffffff; border-radius: 24px; font-size: 17px; font-weight: 600">Sichern</a></div></div>\n')
save('iPhone-Favoriten-Umbenennen.dc.html', doc('iPhone Favoriten Umbenennen',390,844, FB+DIM+alertR+keyboard(),'#f4f0e6'))
sheetL = ('  <div style="position: absolute; left: 12px; right: 12px; bottom: 34px; display: flex; flex-direction: column; gap: 8px">\n'
  f'    <div class="glass" style="border-radius: 26px; overflow: hidden; background: rgba(250,248,242,.9)"><div style="padding: 14px 16px; text-align: center; font-size: 13px; line-height: 18px; color: #5f594e">„Mein Stern“ aus den Favoriten löschen?</div><div style="height: 1px; background: #ddd7c8"></div><a href="#" style="height: 56px; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 17px; color: #b3261e; font-weight: 600">{ic("trash")}Löschen</a></div>\n'
  '    <a href="#" class="glass" style="height: 56px; display: flex; align-items: center; justify-content: center; border-radius: 28px; font-size: 17px; font-weight: 600; background: rgba(250,248,242,.95)">Abbrechen</a>\n  </div>\n')
save('iPhone-Favoriten-Loeschen.dc.html', doc('iPhone Favoriten Löschen',390,844, FB+DIM+sheetL,'#f4f0e6'))

# ---- Geführter Weg 2 Stil: Flocke, Stern allein
iph('Gefuehrt-iPhone-2b-Stil-Flocke.dc.html','Geführter Weg 2 Stil Flocke',1, big('flocke','mittel','ein'), panel(470,'Welcher Stil?',tiles_stil(0),cta()))
iph('Gefuehrt-iPhone-2c-Stil-Stern.dc.html','Geführter Weg 2 Stil Stern',1, big('stern','mittel','ein'), panel(470,'Welcher Stil?',tiles_stil(1),cta()))
print('B ok')

# ======================= iPad =======================
MUSTER = [('Wintersterne',0,('stern1',),3,False),('Eiskristall',1,('aeste','stern1'),3,False),('Nordlicht',2,('aeste','stern1','stern2'),3,False),
 ('Schneeflocke',1,('stern1',),2,True),('Tannenzweig',0,('aeste','stern1'),4,True),('Rosenstern',2,('stern1',),4,False),
 ('Polarstern',1,('aeste','stern1','stern2'),3,False),('Kleiner Stern',0,('stern1',),2,False),('Eisblume',2,('aeste','stern1'),2,True),('Sternenreigen',0,('aeste','stern1','stern2'),4,False)]
def dotsx(e): return dots(len(e[2]))
# Seitenleiste: Eintrag "Info und Datenschutz" ergänzen
ASIDE2 = ASIDE.replace('<a href="#"><svg', '<a href="#"><svg')  # unverändert
_i = ASIDE2.index('Einstellungen</a>')+len('Einstellungen</a>')
ASIDE2 = ASIDE2[:_i] + f'\n      <a href="#">{ic("info")}Info und Datenschutz</a>' + ASIDE2[_i:]
def aside_sel2(label):
    a = ASIDE2.replace('<a href="#" class="sel">','<a href="#">')
    i = a.index(label+'</a>'); k = a.rindex('<a href="#">',0,i)
    return a[:k]+'<a href="#" class="sel">'+a[k+len('<a href="#">'):]
def ipdoc(name, title, inner, bg='#f4f0e6', w=1180, h=820):
    save(name, doc(title,w,h,ISTYLE.replace('</style>','.g4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}</style>')+'\n'+inner,bg))
def imain(h1, inner, pad='24px 28px 0'):
    return (f'  <main style="position: absolute; left: 304px; right: 0; top: 0; bottom: 0; box-sizing: border-box; padding: {pad}; display: flex; flex-direction: column; gap: 12px; overflow: hidden">\n'
            f'    <h1 style="margin: 0 0 6px; flex-shrink: 0; font-family: \'Newsreader\', Georgia, serif; font-size: 40px; line-height: 46px; font-weight: 700">{h1}</h1>\n{inner}\n  </main>\n')
def narrow(inner, w=560): return f'<div style="width: {w}px; display: flex; flex-direction: column; gap: 12px; margin-left: 0">{inner}</div>'
def unmargin(h): return h.replace('margin: 0 16px;','margin: 0;')
# ---- iPad Einstellungen
ipdoc('iPad-Einstellungen.dc.html','iPad Einstellungen', aside_sel2('Einstellungen')+imain('Einstellungen', narrow(
  unmargin(segcard('Standardformat','karte',['A6 hoch','A6 quer'],0)+segcard('Falz','falzl',['Links','Oben','Keiner'],0)+mtoggle('Haptische Rückmeldung','hand',True)+mtoggle('Weitermachen anzeigen','play',True))
  +'<p style="margin: 0 16px; font-size: 13px; line-height: 18px; color: #5f594e">Format und Falz gelten für neue Muster. Das Erscheinungsbild folgt dem System.</p>')))
# ---- iPad Hilfe (Liste links, Thema rechts) und Glossar
def ilist(sel):
    items=[('wizard','Erste Schritte'),('regler','Muster gestalten'),('warn','Warnungen verstehen'),('play','Sticken nach Stichfolge'),('printer','Drucken und Papier'),('book','Glossar')]
    out=''
    for ico,lab in items:
        on = lab==sel
        st = 'background: #e3eee8; box-shadow: inset 0 0 0 2px #1f5a4b;' if on else ''
        out += f'<a href="#" style="height: 52px; box-sizing: border-box; padding: 0 14px; display: flex; align-items: center; gap: 12px; border-radius: 18px; font-size: 17px; {"font-weight: 600;" if on else ""} {st}"><span style="color: #1f5a4b; display: flex">{ic(ico)}</span>{lab}</a>'
    return f'<div style="width: 300px; flex-shrink: 0; box-sizing: border-box; padding: 8px; display: flex; flex-direction: column; gap: 4px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px; align-self: flex-start">{out}</div>'
topic = unmargin(hcard('ok','check','Kein Fehler','Alle Löcher haben genug Abstand.',minidist(13,'#14603a'))+hcard('warn','warn','Knapp','Der Faden liegt eng. Die Karte lässt sich noch sticken.',minidist(8,'#9a5a00'))+hcard('crit','stop','Zu eng','Löcher würden reißen. Drucken ist gesperrt.',minidist(4,'#b3261e')))
ipdoc('iPad-Hilfe.dc.html','iPad Hilfe', aside_sel2('Hilfe und Glossar')+imain('Hilfe und Glossar',
  '<div style="display: flex; gap: 20px; align-items: flex-start">'+ilist('Warnungen verstehen')+f'<div style="flex-grow: 1; max-width: 520px; display: flex; flex-direction: column; gap: 12px"><h2 style="margin: 0 0 4px; font-family: Newsreader, Georgia, serif; font-size: 28px; line-height: 34px; font-weight: 600">Warnungen verstehen</h2>{topic}</div></div>'))
gl = '<div class="grp" style="margin: 0; overflow: hidden">'+''.join(trow(t,d,i==len(TERMS)-1) for i,(t,d) in enumerate(TERMS[:6]))+'</div>'
ipdoc('iPad-Glossar.dc.html','iPad Glossar', aside_sel2('Hilfe und Glossar')+imain('Hilfe und Glossar',
  '<div style="display: flex; gap: 20px; align-items: flex-start">'+ilist('Glossar')+f'<div style="flex-grow: 1; max-width: 520px; display: flex; flex-direction: column; gap: 12px">{search.replace("margin: 0 16px;","margin: 0;")}{gl}</div></div>'))
ipdoc('iPad-Info.dc.html','iPad Info und Datenschutz', aside_sel2('Info und Datenschutz')+imain('Info und Datenschutz', narrow(
  hero_i+unmargin(priv)+unmargin(grp(lrow('doc','Datenschutzerklärung'),lrow('book','Lizenzen und Quellen'),style='margin: 0;')))))
# ---- iPad Einführung (Formularblatt über Start)
IPS = open(PROJ+'iPad-Start.dc.html').read()
ips_body = IPS[IPS.index('<div style="position: relative'):IPS.index('</x-dc>')]
ips_body = ips_body[ips_body.index('\n')+1:ips_body.rindex('</div>')]
art_i = svgP(P_M, WELTEN[0], 'mittel', 'mehr', 220, 310, (0,0), '0 14px 36px rgba(30,42,51,.28)').replace('position: absolute; left: 0px; top: 0px; ','position: relative; ')
formsheet = ('  <div class="glass" style="position: absolute; left: 50%; top: 50%; width: 640px; height: 520px; margin: -260px 0 0 -320px; box-sizing: border-box; padding: 28px 32px 24px; border-radius: 34px; background: rgba(250,248,242,.96); display: flex; flex-direction: column; gap: 14px">\n'
  f'    <div style="flex-grow: 1; display: flex; gap: 32px; align-items: center"><span style="flex-shrink: 0; display: flex">{art_i}</span><div style="display: flex; flex-direction: column; gap: 12px"><h1 style="margin: 0; font-family: Newsreader, Georgia, serif; font-size: 36px; line-height: 42px; font-weight: 700">Muster zum Sticken</h1><span style="font-size: 18px; line-height: 26px; color: #4a453c">Gestalte Karten aus Linien und Löchern.</span></div></div>\n'
  f'    {dotsrow(3,0)}\n    <div style="display: flex; gap: 8px"><a href="#" style="flex: 1 1 0; height: 52px; display: flex; align-items: center; justify-content: center; background: #efeadd; border-radius: 26px; font-size: 17px; font-weight: 600">Überspringen</a><a href="#" style="flex: 1 1 0; height: 52px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #1f5a4b; color: #ffffff; border-radius: 26px; font-size: 17px; font-weight: 600">Weiter{ic("next")}</a></div>\n  </div>\n')
ipdoc('iPad-Einfuehrung.dc.html','iPad Einführung', ips_body+DIM+formsheet)
print('C ok')
