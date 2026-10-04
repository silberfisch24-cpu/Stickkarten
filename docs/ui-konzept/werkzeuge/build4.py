import sys, json, re
sys.path.insert(0,'.')
import lib
from lib import *
exec(open('build2.py').read().split('# Mittel: gemeinsame Geometrie')[0].split("# --- zusätzliche Bausteine ---")[1].replace('lib.ICON','lib.ICON'))
OUT='/tmp/claude-0/-home-user-Stickkarten/7d64d15f-70be-5a8c-bbc1-d86911943200/scratchpad/konzept1/project/'
def save(name, html): open(OUT+name,'w').write(html)

# ---------- neue Bausteine ----------
def gbtn(icon, label, extra=''):
    return f'<a href="#" aria-label="{label}" class="glass" style="width: 44px; height: 44px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border-radius: 50%;{extra}">{ic(icon)}</a>'
def topbar2(active, locked=False, top=59):
    def seg(key, icon, label):
        sel = ' background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); font-weight: 600;' if key == active else ''
        return f'<a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; border-radius: 19px; font-size: 14px;{sel}">{ic(icon,20)}{label}</a>'
    return (f'  <div style="position: absolute; left: 16px; right: 16px; top: {top}px; height: 44px; display: flex; gap: 8px; align-items: center">\n'
        f'    {gbtn("back","Zurück")}\n'
        f'    <div class="glass" style="flex-grow: 1; height: 44px; box-sizing: border-box; padding: 3px; display: flex; gap: 2px; border-radius: 22px">{seg("muster","muster","Muster")}{seg("stich","play","Stichfolge")}</div>\n'
        f'    {gbtn("printer","Drucken und Teilen" + (" (gesperrt)" if locked else ""), " opacity: .4;" if locked else "")}\n  </div>\n')
def starbtn(cl, ct, cw):
    return f'  <a href="#" aria-label="Als Favorit sichern" class="glass" style="position: absolute; left: {cl+cw-44-10}px; top: {ct+10}px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("star")}</a>\n'
def card2(left, top, w, h, mode='ok'):
    """ok: Muster | warn: Muster + orange Markierung | krit: nur Punktmuster mit Farben"""
    holes_ok = ''.join(f'<circle cx="{x}" cy="{y}" r=".9"/>' for x, y in P + Q + [(58,74)])
    spokes = ''.join(f'M58 74L{x} {y}' for x, y in P)
    body = ''
    if mode in ('ok','warn'):
        body += (f'<g fill="none" stroke-width=".5"><path d="{spokes}" stroke="{FADEN["aeste"]}"/><path d="{pathpts(Q,1)}" stroke="{FADEN["stern2"]}"/><path d="{pathpts(P,3)}" stroke="{FADEN["stern1"]}"/></g>'
                 f'<g fill="#0c1f17">{holes_ok}</g>')
    if mode == 'warn':
        body += ('<circle cx="73.3" cy="58.7" r="5" fill="#e8a23d" fill-opacity=".25" stroke="#e8a23d" stroke-width=".9"/>'
                 '<circle cx="42.7" cy="58.7" r="5" fill="#e8a23d" fill-opacity=".25" stroke="#e8a23d" stroke-width=".9"/>')
    if mode == 'krit':
        ok_pts = [p for p in P + Q if p not in [Q[1], Q[7]]]
        body += ('<g fill="#cfe3d8" fill-opacity=".75">' + ''.join(f'<circle cx="{x}" cy="{y}" r="1.4"/>' for x, y in ok_pts) + '</g>'
                 '<circle cx="73.3" cy="58.7" r="1.9" fill="#e8a23d"/><circle cx="42.7" cy="58.7" r="1.9" fill="#e8a23d"/>'
                 '<g fill="#e0503f"><circle cx="58" cy="74" r="2.2"/></g><circle cx="58" cy="74" r="6" fill="none" stroke="#e0503f" stroke-width=".7"/>')
    return (f'  <svg viewBox="0 0 105 148" style="position: absolute; left: {left}px; top: {top}px; width: {w}px; height: {h}px; border-radius: 8px; display: block; box-shadow: 0 14px 36px rgba(30,42,51,.28)">'
        f'<rect width="105" height="148" fill="#153a2c"/><path d="M0.4 0V148" stroke="#000" stroke-opacity=".35" stroke-width=".4" stroke-dasharray="2 1.5"/>{body}</svg>\n')
TXT = {'warn': 'Lochabstand knapp', 'krit': 'Löcher zu eng'}
def msg(kind, left, top, w, h=44):
    bg, fg, icn = ('#fcefd9', '#6b3f00', 'warn') if kind == 'warn' else ('#fde7e3', '#8f1d14', 'stop')
    return (f'  <div style="position: absolute; left: {left}px; top: {top}px; width: {w}px; height: {h}px; box-sizing: border-box; padding: 0 14px; display: flex; align-items: center; gap: 10px; background: {bg}; color: {fg}; border-radius: 22px; font-size: 16px; line-height: 20px; font-weight: 600; box-shadow: 0 4px 14px rgba(30,42,51,.18)">'
            f'{ic(icn)}<span>{TXT[kind]}</span></div>\n')
def msgrow(kind):
    bg, fg, icn = ('#fcefd9', '#6b3f00', 'warn') if kind == 'warn' else ('#fde7e3', '#8f1d14', 'stop')
    return (f'    <div style="flex-shrink: 0; box-sizing: border-box; padding: 10px 14px; display: flex; align-items: center; gap: 10px; background: {bg}; color: {fg}; border-radius: 16px; font-size: 14px; line-height: 19px; font-weight: 600">{ic(icn)}<span>{TXT[kind]}</span></div>\n')
def sheet3(top, inner, extra=''):
    return (f'  <div class="sheet" style="position: absolute; left: 0; right: 0; top: {top}px; bottom: 0; box-sizing: border-box; padding: 8px 16px 0; border-radius: 34px 34px 0 0; display: flex; flex-direction: column; gap: 10px; overflow: hidden;{extra}">\n'
        f'    {grabber()}\n    {inner}\n  </div>\n')

# ---------- Mittel-Boards ----------
SH=530; CL,CT,CW,CH=51,108,288,406
def mid(inner, title, state):
    b = card2(CL,CT,CW,CH,state) + starbtn(CL,CT,CW)
    if state in ('warn','krit'): b += msg(state, CL+8, CT+CH-8-44, CW-16)
    b += topbar2('muster', locked=(state=='krit')) + sheet3(SH, inner)
    return doc(title,390,844,b)
aeste = track('aeste')+'\n'+slider('Astwinkel','angle','55°',82)+slider('Astlänge','laenge','70 %',28)
save('iPhone-Editor-Sheet.dc.html', mid(aeste,'iPhone Editor – Sheet mittel Äste (Warnung)','warn'))
save('iPhone-Editor-Sheet-Ok.dc.html', mid(aeste,'iPhone Editor – Sheet mittel Äste (kein Fehler)','ok'))
save('iPhone-Editor-Sheet-Kritisch.dc.html', mid(aeste,'iPhone Editor – Sheet mittel Äste (kritisch)','krit'))
save('iPhone-Editor-Sheet-Stern1.dc.html', mid(track('stern1')+'\n'+stepper('Schrittweite','schritt',3)+stepper('Sternebene','ebenen',2),'iPhone Editor – Sheet mittel Stern 1','warn'))
save('iPhone-Editor-Sheet-Grundform.dc.html', mid(track('grund')+'\n'+stepper('Kreispunkte','punkte',8)+stepper('Ebenen','ebenen',4),'iPhone Editor – Sheet mittel Grundform','warn'))
save('iPhone-Editor-Sheet-Warnung.dc.html', mid(track('karte')+'\n'+slider('Zoom','zoom','100 %',100)+wells(),'iPhone Editor – Sheet mittel Karte','warn'))

# Klein
b = card2(25,112,340,479,'warn')+starbtn(25,112,340)+msg('warn',33,112+479-8-44,324)+topbar2('muster')+sheet3(690, track('aeste'))
save('iPhone-Editor-Sheet-Klein.dc.html', doc('iPhone Editor – Sheet klein',390,844,b))

# Groß
dim='  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.28)"></div>\n'
inner_ae = msgrow('warn')+track('aeste')+'\n'+slider('Astwinkel','angle','55°',82)+slider('Astlänge','laenge','70 %',28)+toggle('Seitenäste','aeste',True)+slider('Wachstum','wachstum','30 %',20)
save('iPhone-Editor-Sheet-Gross.dc.html', doc('iPhone Editor – Sheet groß',390,844,
    card2(72,108,246,347,'warn')+topbar2('muster')+dim+sheet3(120, inner_ae, ' background: #faf8f2;')))
inner_ka = (msgrow('warn')+track('karte')+'\n'+slider('Zoom','zoom','100 %',100)+formatrow()+falzrow()
    +colorrow2('Karton','karton',0)+colorrow2('Äste','aeste',1)+colorrow2('Stern 1','stern1',0)+colorrow2('Stern 2','stern2',2))
save('iPhone-Editor-Sheet-Gross-Karte.dc.html', doc('iPhone Editor – Sheet groß Karte',390,844,
    card2(72,108,246,347,'warn')+topbar2('muster')+dim+sheet3(120, inner_ka, ' background: #faf8f2;')))

# Stichfolge: Topbar + Favorit
f=open(OUT+'iPhone-Editor-Stichfolge.dc.html').read()
a=f.index('  <div style="position: absolute; left: 16px; right: 16px; top: 59px;')
b2=f.index('  <div class="glass" style="position: absolute; left: 16px; right: 16px; bottom: 22px')
f=f[:a]+topbar2('stich')+starbtn(38,112,313)+f[b2:]
save('iPhone-Editor-Stichfolge.dc.html', f)

# iPad
def track_stacked(selected):
    keys=('grund','aeste','stern1','stern2','karte'); lab={'grund':'Grundform','aeste':'Äste','stern1':'Stern 1','stern2':'Stern 2','karte':'Karte'}
    it=''
    for k in keys:
        base='flex: 1 1 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; border-radius: 18px; font-size: 11px;'
        sel=' background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); font-weight: 600;' if k==selected else ' color: #1e2a33;'
        it+=f'<a href="#" style="{base}{sel}">{ic(k,22)}{lab[k]}</a>'
    return f'<div style="height: 64px; flex-shrink: 0; box-sizing: border-box; padding: 4px; display: flex; gap: 2px; background: #e6e1d4; border-radius: 22px">{it}</div>'
rows=(slider('Astwinkel','angle','55°',82)+slider('Astlänge','laenge','70 %',28)+toggle('Seitenäste','aeste',True)+slider('Wachstum','wachstum','30 %',20))
ipad=(card2(158,84,440,620,'warn')+starbtn(158,84,440)+msg('warn',166,84+620-8-44,424)
  + f'  <a href="#" aria-label="Seitenleiste einblenden" class="glass" style="position: absolute; left: 16px; top: 16px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%"><svg class="i" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="M9 5v14"/></svg></a>\n'
  + f'  <div class="glass" style="position: absolute; left: 228px; top: 16px; width: 300px; height: 44px; box-sizing: border-box; padding: 3px; display: flex; gap: 2px; border-radius: 22px"><a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); border-radius: 19px; font-size: 14px; font-weight: 600">{ic("muster",20)}Muster</a><a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; border-radius: 19px; font-size: 14px">{ic("play",20)}Stichfolge</a></div>\n  <a href="#" aria-label="Drucken und Teilen" class="glass" style="position: absolute; left: 696px; top: 16px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("printer")}</a>\n'
  + '  <aside class="glass" style="position: absolute; right: 12px; top: 12px; bottom: 12px; width: 400px; box-sizing: border-box; padding: 16px; border-radius: 34px; background: rgba(250,248,242,.88); display: flex; flex-direction: column; gap: 12px; overflow: hidden">\n    '
  + track_stacked('aeste') + '\n    <div style="display: flex; flex-direction: column; gap: 8px; min-height: 0">\n' + rows + '    </div>\n'
  + f'    <div style="margin-top: auto; display: flex; gap: 8px"><a href="#" aria-label="Zurücksetzen" style="width: 56px; height: 56px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; background: #efeadd; border-radius: 50%">{ic("reset")}</a></div>\n  </aside>\n')
save('iPad-Editor.dc.html', doc('iPad Editor',1180,820,ipad))

print('ok')
