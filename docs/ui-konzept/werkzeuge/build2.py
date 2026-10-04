import sys, json
sys.path.insert(0,'.')
from lib import *
import lib
OUT='/tmp/claude-0/-home-user-Stickkarten/7d64d15f-70be-5a8c-bbc1-d86911943200/scratchpad/konzept1/project/'
def save(name, html): open(OUT+name,'w').write(html)

# --- zusätzliche Bausteine ---
lib.ICON['karton']='<rect x="5" y="3" width="14" height="18" rx="2"/>'
def colorrow2(label, icon, sel=0):
    sws=''
    for i,c in enumerate(SW):
        ring=f'box-shadow: 0 0 0 2px #ffffff, 0 0 0 4px #1f5a4b;' if i==sel else ''
        sws+=f'<a href="#" aria-label="Farbe {i+1}" style="width: 36px; height: 44px; display: flex; align-items: center; justify-content: center"><i style="width: 26px; height: 26px; border-radius: 50%; background: {c}; border: 1px solid rgba(30,42,51,.25); {ring}"></i></a>'
    return (f'    <div style="min-height: 52px; box-sizing: border-box; padding: 0 8px 0 16px; display: flex; align-items: center; gap: 10px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px">\n'
        f'      <span style="color: #1f5a4b; display: flex">{ic(icon)}</span><span style="flex-grow: 1; font-size: 16px">{label}</span>{sws}\n    </div>\n')
def wells():
    items=[('karton','#153a2c','#e8c987'),('aeste','#d9e2e7','#1e2a33'),('stern1','#e8c987','#1e2a33'),('stern2','#ffffff','#1e2a33')]
    w=''
    for k,bg,fg in items:
        w+=f'<a href="#" aria-label="Farbe {k}" style="width: 44px; height: 44px; display: flex; align-items: center; justify-content: center"><i style="width: 40px; height: 40px; box-sizing: border-box; border-radius: 50%; background: {bg}; color: {fg}; border: 1px solid rgba(30,42,51,.3); display: flex; align-items: center; justify-content: center">{ic(k,22)}</i></a>'
    return (f'    <div style="min-height: 64px; box-sizing: border-box; padding: 0 8px 0 16px; display: flex; align-items: center; gap: 8px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px">\n'
        f'      <span style="color: #1f5a4b; display: flex">{ic("palette")}</span><span style="flex-grow: 1; font-size: 16px">Farben</span>{w}\n    </div>\n')
def falzrow():
    def opt(label, sel):
        if sel: return f'<a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); border-radius: 22px; font-size: 14px; font-weight: 600">{label}</a>'
        return f'<a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; border-radius: 22px; font-size: 14px">{label}</a>'
    return (f'    <div style="min-height: 64px; box-sizing: border-box; padding: 0 12px 0 16px; display: flex; align-items: center; gap: 12px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px">\n'
        f'      <span style="color: #1f5a4b; display: flex"><svg class="i" viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 4v16" stroke-dasharray="2 2"/></svg></span><span style="font-size: 16px">Falz</span>\n'
        f'      <div style="flex-grow: 1; height: 44px; box-sizing: border-box; padding: 3px; display: flex; gap: 2px; background: #e6e1d4; border-radius: 21px">{opt("Links",True)}{opt("Oben",False)}{opt("Keiner",False)}</div>\n    </div>\n')
def headchips():
    return (f'<div style="position: absolute; left: 16px; top: 8px; display: flex; gap: 6px">'
        f'<span style="height: 30px; box-sizing: border-box; padding: 0 10px; display: flex; align-items: center; gap: 4px; background: #fde7e3; color: #b3261e; border-radius: 15px; font-size: 14px; font-weight: 700">{ic("stop",18)}6</span>'
        f'<span style="height: 30px; box-sizing: border-box; padding: 0 10px; display: flex; align-items: center; gap: 4px; background: #fcefd9; color: #9a5a00; border-radius: 15px; font-size: 14px; font-weight: 700">{ic("warn",18)}2</span></div>')
def sheet2(top, inner, chips=False, extra=''):
    return (f'  <div class="sheet" style="position: absolute; left: 0; right: 0; top: {top}px; bottom: 0; box-sizing: border-box; padding: 8px 16px 0; border-radius: 34px 34px 0 0; display: flex; flex-direction: column; gap: 10px; overflow: hidden;{extra}">\n'
        f'    {headchips() if chips else ""}{grabber()}\n    {inner}\n  </div>\n')

# Mittel: gemeinsame Geometrie, Warnungen in allen Gruppen sichtbar
SH=530
def mid(inner, title):
    return doc(title, 390, 844, card(51,108,288,406,'warn')+warnchips(63,466)+topbar('muster',issues=True)+sheet2(SH, inner))
save('iPhone-Editor-Sheet.dc.html', mid(track('aeste')+'\n'+slider('Astwinkel','angle','55°',82)+slider('Astlänge','laenge','70 %',28),'iPhone Editor – Sheet mittel Äste'))
save('iPhone-Editor-Sheet-Stern1.dc.html', mid(track('stern1')+'\n'+stepper('Schrittweite','schritt',3)+stepper('Sternebene','ebenen',2),'iPhone Editor – Sheet mittel Stern 1'))
save('iPhone-Editor-Sheet-Grundform.dc.html', mid(track('grund')+'\n'+stepper('Kreispunkte','punkte',8)+stepper('Ebenen','ebenen',4),'iPhone Editor – Sheet mittel Grundform'))
save('iPhone-Editor-Sheet-Warnung.dc.html', mid(track('karte')+'\n'+slider('Zoom','zoom','100 %',100)+wells(),'iPhone Editor – Sheet mittel Karte'))

# Klein: Karte groß, Warnungen sichtbar
save('iPhone-Editor-Sheet-Klein.dc.html', doc('iPhone Editor – Sheet klein',390,844,
    card(25,112,340,479,'warn')+warnchips(37,543)+topbar('muster',issues=True)+sheet2(690, track('aeste'))))

# Groß: Warnungen im Sheet-Kopf (Karte ist verdeckt)
dim='  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.28)"></div>\n'
inner_ae=track('aeste')+'\n'+slider('Astwinkel','angle','55°',82)+slider('Astlänge','laenge','70 %',28)+toggle('Seitenäste','aeste',True)+slider('Wachstum','wachstum','30 %',20)
save('iPhone-Editor-Sheet-Gross.dc.html', doc('iPhone Editor – Sheet groß',390,844,
    card(72,108,246,347,'warn')+topbar('muster',issues=True)+dim+sheet2(120, inner_ae, chips=True, extra=' background: #faf8f2;')))
inner_ka=(track('karte')+'\n'+slider('Zoom','zoom','100 %',100)+formatrow()+falzrow()
    +colorrow2('Karton','karton',0)+colorrow2('Äste','aeste',1)+colorrow2('Stern 1','stern1',0)+colorrow2('Stern 2','stern2',2))
save('iPhone-Editor-Sheet-Gross-Karte.dc.html', doc('iPhone Editor – Sheet groß Karte',390,844,
    card(72,108,246,347,'warn')+topbar('muster',issues=True)+dim+sheet2(120, inner_ka, chips=True, extra=' background: #faf8f2;')))

# iPad: Warnungen sichtbar, keine Farbzeile
s=open(OUT+'iPad-Editor.dc.html').read()
s=s.replace('<rect width="105" height="148" fill="#153a2c"/>','<rect width="105" height="148" fill="#153a2c"/>',1)
open(OUT+'iPad-Editor.dc.html','w').write(s)
rows=(slider('Astwinkel','angle','55°',82)+slider('Astlänge','laenge','70 %',28)+toggle('Seitenäste','aeste',True)+slider('Wachstum','wachstum','30 %',20))
def track_stacked(selected):
    keys=('grund','aeste','stern1','stern2','karte'); lab={'grund':'Grundform','aeste':'Äste','stern1':'Stern 1','stern2':'Stern 2','karte':'Karte'}
    it=''
    for k in keys:
        if k==selected:
            it+=f'<a href="#" style="flex: 1 1 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); border-radius: 22px; font-size: 11px; font-weight: 600">{ic(k,22)}{lab[k]}</a>'
        else:
            it+=f'<a href="#" style="flex: 1 1 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; color: #1e2a33; border-radius: 22px; font-size: 11px">{ic(k,22)}{lab[k]}</a>'
    return f'<div style="height: 64px; flex-shrink: 0; box-sizing: border-box; padding: 4px; display: flex; gap: 2px; background: #e6e1d4; border-radius: 22px">{it}</div>'
dot='<i style="position: absolute; right: 8px; top: 8px; width: 10px; height: 10px; border-radius: 50%; background: #e0503f; border: 2px solid #ffffff"></i>'
ipad=(card(158,84,440,620,'warn')+warnchips(170,656)
  + f'  <a href="#" aria-label="Seitenleiste einblenden" class="glass" style="position: absolute; left: 16px; top: 16px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: 50%"><svg class="i" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="M9 5v14"/></svg></a>\n'
  + f'  <div class="glass" style="position: absolute; left: 258px; top: 16px; width: 240px; height: 48px; box-sizing: border-box; padding: 4px; display: flex; gap: 2px; border-radius: 24px"><a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); border-radius: 20px; font-size: 14px; font-weight: 600">{ic("muster",20)}Muster</a><a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; border-radius: 20px; font-size: 14px">{ic("play",20)}Stichfolge</a></div>\n'
  + f'  <a href="#" aria-label="Als Favorit sichern" class="glass" style="position: absolute; left: 640px; top: 16px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("star")}</a>\n'
  + f'  <a href="#" aria-label="Ausgabe (gesperrt: Löcher zu eng)" class="glass" style="position: absolute; left: 696px; top: 16px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: 50%; opacity: .6">{ic("printer")}{dot}</a>\n'
  + '  <aside class="glass" style="position: absolute; right: 12px; top: 12px; bottom: 12px; width: 400px; box-sizing: border-box; padding: 16px; border-radius: 30px; background: rgba(250,248,242,.88); display: flex; flex-direction: column; gap: 12px; overflow: hidden">\n    '
  + track_stacked('aeste') + '\n    <div style="display: flex; flex-direction: column; gap: 8px; min-height: 0">\n' + rows + '    </div>\n'
  + f'    <div style="margin-top: auto; display: flex; gap: 8px"><a href="#" aria-label="Zurücksetzen" style="width: 56px; height: 56px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; background: #efeadd; border-radius: 50%">{ic("reset")}</a><a href="#" style="flex-grow: 1; height: 56px; display: flex; align-items: center; justify-content: center; gap: 10px; background: #1f5a4b; color: #ffffff; border-radius: 28px; font-size: 17px; font-weight: 600; opacity: .5">{ic("printer")}Ausgabe</a></div>\n  </aside>\n')
save('iPad-Editor.dc.html', doc('iPad Editor',1180,820,ipad))

# Übersicht
u=open(OUT+'Detents-Uebersicht.dc.html').read()
reps=[('Zoom + Format','Zoom + Farben'),('Falzposition, Kartonfarbe; Erweitert: Eigenes Format','Format, Falz, Farbe je Element (Karton, Äste, Stern 1, Stern 2); Erweitert: Eigenes Format')]
for o,n in reps:
    assert o in u,o; u=u.replace(o,n)
a=u.index('Farbe des Elements (Äste')
a0=u.rfind('<div style="display: flex; align-items: center; gap: 12px; margin-top: 6px',0,a)
b=u.index('</div>\n',a)+len('</div>\n')
note=f'<div style="display: flex; align-items: center; gap: 12px; margin-top: 6px; padding: 14px 20px; background: #fcefd9; color: #6b3f00; border-radius: 22px; font-size: 15px"><span style="display: flex">{ic("warn")}</span><span>Warnungen (knapp, zu eng) sind in allen Gruppen und Stufen sichtbar: auf der Karte (Klein, Mittel) und als Zähler im Sheet-Kopf (Groß).</span></div>\n'
u=u[:a0]+note+u[b:]
open(OUT+'Detents-Uebersicht.dc.html','w').write(u)

c=json.load(open(OUT+'canvas.json')); B=c['boards']
B['iPhone-Editor-Sheet-Stern1.dc.html']={"x":1880,"y":4952,"w":390,"h":844,"title":"iPhone · Editor – Sheet mittel (Gruppe Stern 1)"}
B['iPhone-Editor-Sheet-Gross-Karte.dc.html']={"x":2350,"y":4952,"w":390,"h":844,"title":"iPhone · Editor – Sheet groß (Gruppe Karte, mit Farben)"}
B['iPhone-Editor-Sheet-Warnung.dc.html']['title']='iPhone · Editor – Sheet mittel (Gruppe Karte: Zoom + Farben)'
B['iPhone-Editor-Sheet-Grundform.dc.html']['title']='iPhone · Editor – Sheet mittel (Gruppe Grundform)'
B['iPhone-Editor-Sheet.dc.html']['title']='iPhone · Editor – Sheet mittel (Basis, Gruppe Äste)'
B['iPhone-Editor-Sheet-Gross.dc.html']['title']='iPhone · Editor – Sheet groß (Gruppe Äste)'
c['order']+=['iPhone-Editor-Sheet-Stern1.dc.html','iPhone-Editor-Sheet-Gross-Karte.dc.html']
json.dump(c,open(OUT+'canvas.json','w'),ensure_ascii=False,indent=2)
print('ok')
