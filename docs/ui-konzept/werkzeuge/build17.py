# Neue Boards zur Schließung der Soll/Kann-Lücken
import re, sys, math, itertools
sys.path.insert(0,'.')
b11 = open('build11.py').read()
exec(b11[:b11.index('# ---------- iPhone Hauptreihe ----------')])
b4 = open('build4.py').read()
exec(b4[:b4.index("aeste = track('aeste')")])
PROJ = OUT
exec(open('real.py').read())
b16 = open('build16a.py').read()
exec(b16[b16.index('FADEN3 ='):b16.index('SVG_RE =')])
_c2 = {'ok':'ok','warn':'warn','krit':'crit'}
card2 = lambda l,t,w,h,mode='ok': rc(l,t,w,h,_c2[mode])
DIM = '  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.28)"></div>\n'
DIM2 = '  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.38); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px)"></div>\n'
lib.ICON['reset']='<path d="M4 5v5h5"/><path d="M5 10a8 8 0 112 8"/>'
lib.ICON['spinner']='<path d="M12 3a9 9 0 019 9" stroke-width="2.4"/><circle cx="12" cy="12" r="9" opacity=".25"/>'
lib.ICON['sprung']='<path d="M4 12h2M9 12h2M14 12h2M19 12h1M16 8l4 4-4 4"/>'
def pillrow(kind, text):
    bg, fg, icn = {'warn':('#fcefd9','#6b3f00','warn'),'crit':('#fde7e3','#8f1d14','stop')}[kind]
    return f'    <div style="flex-shrink: 0; box-sizing: border-box; padding: 10px 14px; display: flex; align-items: center; gap: 10px; background: {bg}; color: {fg}; border-radius: 16px; font-size: 14px; line-height: 19px; font-weight: 600">{ic(icn)}<span>{text}</span></div>\n'
def gross(title, name, inner, state='ok', pill=None):
    b = card2(72,108,246,347,state) + topbar2('muster') + DIM + sheet3(120, (pill or '')+inner, ' background: #faf8f2;')
    save(name, doc(title,390,844,b))
# ---- Eigenformat
seg_fmt = ('<div style="min-height: 64px; box-sizing: border-box; padding: 0 12px 0 16px; display: flex; align-items: center; gap: 12px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px">'
  f'<span style="color: #1f5a4b; display: flex">{ic("karte")}</span><span style="font-size: 16px">Format</span>'
  '<div style="flex-grow: 1; height: 44px; box-sizing: border-box; padding: 3px; display: flex; gap: 2px; background: #e6e1d4; border-radius: 21px">'
  f'<a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; border-radius: 22px; font-size: 14px">{ic("hoch",20)}A6 hoch</a>'
  f'<a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; border-radius: 22px; font-size: 14px">{ic("quer",20)}A6 quer</a></div></div>')
def erweitert(rows, open_=True):
    ch = f'<span style="color: #5f594e; display: flex; transform: rotate({90 if open_ else 0}deg)">{ic("next")}</span>'
    head = (f'<div style="min-height: 56px; box-sizing: border-box; padding: 0 12px 0 16px; display: flex; align-items: center; gap: 12px"><span style="color: #1f5a4b; display: flex">{ic("regler")}</span>'
            f'<span style="flex-grow: 1; font-size: 16px; font-weight: 600">Erweitert</span>{ch}</div>')
    return f'<div style="display: flex; flex-direction: column; gap: 10px">{head}{rows}</div>'
def limit_chip(txt, bad=False):
    bg, fg = ('#fde7e3','#8f1d14') if bad else ('#efeadd','#1e2a33')
    return f'<span style="align-self: flex-start; height: 36px; padding: 0 12px; display: inline-flex; align-items: center; gap: 6px; background: {bg}; color: {fg}; border-radius: 18px; font-size: 14px; font-weight: 600"><span style="display: flex">{ic("laenge" if not bad else "stop",20)}</span>{txt}</span>'
fmt_head = track('karte')+'\n'+seg_fmt
EF_ok = erweitert(toggle('Eigenes Format','karte',True)+stepper('Breite (mm)','laenge','105')+stepper('Höhe (mm)','laenge','148')+limit_chip('Vorderseite höchstens 190 × 277 mm'))
gross('iPhone Editor – Karte, Eigenformat','iPhone-Eigenformat.dc.html', fmt_head+EF_ok)
EF_bad = erweitert(toggle('Eigenes Format','karte',True)+stepper('Breite (mm)','laenge','<span style="color: #b3261e">205</span>')+stepper('Höhe (mm)','laenge','148')+limit_chip('Höchstens 190 × 277 mm',True))
gross('iPhone Editor – Eigenformat zu groß','iPhone-Eigenformat-zu-gross.dc.html', fmt_head+EF_bad, pill=pillrow('crit','Format zu groß für A4'))
# ---- Meldung antippen: Abhilfe
mid_b = card2(CL,CT,CW,CH,'warn') + starbtn(CL,CT,CW) + topbar2('muster') + sheet3(SH, track('aeste')+'\n'+slider('Astwinkel','angle','55°',100)+slider('Astlänge','laenge','70 %',28))
pop = ('  <div class="glass" style="position: absolute; left: 24px; right: 24px; top: 300px; box-sizing: border-box; padding: 16px; border-radius: 26px; background: rgba(250,248,242,.95); display: flex; flex-direction: column; gap: 10px; box-shadow: 0 10px 40px rgba(30,42,51,.3)">'
  f'<div style="display: flex; align-items: center; gap: 10px; color: #6b3f00">{ic("warn",28)}<b style="font-family: Newsreader, Georgia, serif; font-size: 22px; line-height: 28px; color: #1e2a33">Lochabstand knapp</b></div>'
  '<span style="font-size: 15px; line-height: 21px">Kleinster Abstand 3,9 mm. Ab 4,8 mm gilt er als sicher.</span>'
  f'<div style="display: flex; flex-direction: column; gap: 8px"><a href="#" style="height: 48px; padding: 0 16px; display: flex; align-items: center; gap: 10px; background: #efeadd; border-radius: 24px; font-size: 16px; font-weight: 600"><span style="color: #1f5a4b; display: flex">{ic("laenge")}</span>Astlänge verringern<span style="margin-left: auto; display: flex; color: #5f594e">{ic("next",20)}</span></a>'
  f'<a href="#" style="height: 48px; padding: 0 16px; display: flex; align-items: center; gap: 10px; background: #efeadd; border-radius: 24px; font-size: 16px; font-weight: 600"><span style="color: #1f5a4b; display: flex">{ic("angle")}</span>Astwinkel verringern<span style="margin-left: auto; display: flex; color: #5f594e">{ic("next",20)}</span></a></div></div>\n')
save('iPhone-Meldung-Abhilfe.dc.html', doc('iPhone Meldung antippen: Abhilfe',390,844, card2(CL,CT,CW,CH,'warn')+starbtn(CL,CT,CW)+msg('warn',CL+8,CT+CH-52,CW-16)+topbar2('muster')+sheet3(SH, track('aeste')+'\n'+slider('Astwinkel','angle','55°',100)+slider('Astlänge','laenge','70 %',28))+pop))
# ---- Drucken gesperrt (kritisch)
crit = card2(CL,CT,CW,CH,'krit') + starbtn(CL,CT,CW) + msg('krit',CL+8,CT+CH-52,CW-16) + topbar2('muster',locked=True) + sheet3(SH, track('aeste')+'\n'+slider('Astwinkel','angle','55°',100)+slider('Astlänge','laenge','80 %',33))
alert = (DIM2 + '  <div class="glass" style="position: absolute; left: 36px; right: 36px; top: 300px; box-sizing: border-box; padding: 20px 16px 16px; border-radius: 30px; background: rgba(250,248,242,.95); display: flex; flex-direction: column; gap: 12px">'
  f'<div style="display: flex; flex-direction: column; align-items: center; gap: 8px; color: #8f1d14">{ic("stop",32)}<span style="font-family: Newsreader, Georgia, serif; font-size: 24px; line-height: 30px; font-weight: 600; color: #1e2a33; text-align: center">Drucken gesperrt</span></div>'
  '<span style="text-align: center; font-size: 15px; line-height: 21px">Löcher liegen zu eng. Ändere das Muster, dann ist Drucken wieder möglich.</span>'
  '<a href="#" style="height: 52px; display: flex; align-items: center; justify-content: center; background: #1f5a4b; color: #ffffff; border-radius: 26px; font-size: 17px; font-weight: 600">Zum Muster</a></div>\n')
save('iPhone-Ausgabe-gesperrt.dc.html', doc('iPhone Ausgabe gesperrt',390,844, crit.replace('<div class="sheet"','<div class="sheet"',1)+alert))
# ---- Ausgabe: Erstellen und Fehler
src = open(PROJ+'iPhone-Ausgabe.dc.html').read()
a = src.index('<div style="display: flex; gap: 8px"><a href="#" aria-label="Vorschau mit Zoom"')
b_ = src.index('</div>\n', src.index('Drucken</a>', a))+7
def ausgabe_var(name, title, new_acts, extra_pre=''):
    s = src[:a] + new_acts + src[b_:]
    h = s.index('    <div style="display: flex; align-items: center; gap: 10px; color: #5f594e; font-size: 13px')
    s = s[:h] + extra_pre + s[h:]
    s = re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', s, count=1)
    open(PROJ+name,'w').write(s)
busy = (f'<div style="display: flex; gap: 8px"><span style="flex: 1 1 0; height: 52px; display: flex; align-items: center; justify-content: center; gap: 10px; background: #efeadd; color: #5f594e; border-radius: 26px; font-size: 17px; font-weight: 600"><span style="display: flex">{ic("spinner")}</span>PDF wird erstellt</span></div>\n')
ausgabe_var('iPhone-Ausgabe-Erstellen.dc.html','iPhone Ausgabe PDF wird erstellt', busy)
err = (f'<div style="display: flex; gap: 8px"><a href="#" style="flex: 1 1 0; height: 52px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #1f5a4b; color: #ffffff; border-radius: 26px; font-size: 17px; font-weight: 600">{ic("reset")}Erneut versuchen</a></div>\n')
errpill = f'    <div style="flex-shrink: 0; box-sizing: border-box; padding: 10px 14px; display: flex; align-items: center; gap: 10px; background: #fde7e3; color: #8f1d14; border-radius: 16px; font-size: 14px; line-height: 19px; font-weight: 600">{ic("stop")}<span>PDF konnte nicht erstellt werden</span></div>\n'
ausgabe_var('iPhone-Ausgabe-Fehler.dc.html','iPhone Ausgabe Fehler', err, errpill)
# ---- Zurücksetzen im Editor
reset_cap = f'<a href="#" style="flex-shrink: 0; height: 48px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #efeadd; border-radius: 24px; font-size: 16px; font-weight: 600">{ic("reset")}Zurücksetzen</a>'
ae = track('aeste')+'\n'+slider('Astwinkel','angle','55°',100)+slider('Astlänge','laenge','70 %',28)+toggle('Seitenäste','aeste',True)+slider('Wachstum','wachstum','30 %',20)+reset_cap
gross('iPhone Editor – Groß mit Zurücksetzen','iPhone-Editor-Zuruecksetzen-Button.dc.html', ae, 'warn', pillrow('warn','Lochabstand knapp'))
sheet_r = (DIM2 + '  <div style="position: absolute; left: 12px; right: 12px; bottom: 34px; display: flex; flex-direction: column; gap: 8px">\n'
  f'    <div class="glass" style="border-radius: 26px; overflow: hidden; background: rgba(250,248,242,.92)"><div style="padding: 14px 16px; text-align: center; font-size: 13px; line-height: 18px; color: #5f594e">Auf Ausgangswerte zurücksetzen?</div><div style="height: 1px; background: #ddd7c8"></div>'
  f'<a href="#" style="height: 56px; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 17px; font-weight: 600">{ic("aeste")}Nur Äste</a><div style="height: 1px; background: #ddd7c8"></div>'
  f'<a href="#" style="height: 56px; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 17px; color: #b3261e; font-weight: 600">{ic("reset")}Ganzes Muster</a></div>\n'
  '    <a href="#" class="glass" style="height: 56px; display: flex; align-items: center; justify-content: center; border-radius: 28px; font-size: 17px; font-weight: 600; background: rgba(250,248,242,.95)">Abbrechen</a>\n  </div>\n')
b_ae = card2(72,108,246,347,'warn') + topbar2('muster') + DIM + sheet3(120, pillrow('warn','Lochabstand knapp')+ae, ' background: #faf8f2;')
save('iPhone-Editor-Zuruecksetzen-Abfrage.dc.html', doc('iPhone Editor Zurücksetzen Abfrage',390,844,b_ae+sheet_r))
# ---- Start ohne Arbeitsstand
s = open(PROJ+'iPhone-Start.dc.html').read()
k1 = s.index('<a href="#" class="glass" style="position: absolute; left: 16px; right: 16px; bottom: 94px')
k2 = s.index('</a>', k1)+4
s = s[:k1]+s[k2:]
open(PROJ+'iPhone-Start-Erststart.dc.html','w').write(re.sub(r'<title>[^<]*</title>','<title>iPhone Start ohne Arbeitsstand</title>',s,count=1))
print('G ok')
