import sys, re
sys.path.insert(0,'.')
from pat import *
src = open('build7.py').read()
exec(src[:src.index('SEL_W = WELTEN[0]\nLAY')])
SEL_W = WELTEN[0]
G = '<span style="color: #1f5a4b; display: flex">%s</span>'
lib.ICON['falzl']='<rect x="6" y="3" width="12" height="18" rx="2"/><path d="M9.5 3v18"/>'
lib.ICON['falzo']='<rect x="6" y="3" width="12" height="18" rx="2"/><path d="M6 7.5h12"/>'
lib.ICON['falzk']='<rect x="6" y="3" width="12" height="18" rx="2"/>'
lib.ICON['einfarbig']='<circle cx="12" cy="12" r="8" fill="currentColor"/>'
lib.ICON['mehrfarbig']='<circle cx="9" cy="9" r="5"/><circle cx="15" cy="9" r="5"/><circle cx="12" cy="15" r="5"/>'
lib.ICON['regler']='<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>'
lib.ICON['warn']='<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17v.01"/>'
lib.ICON['trash']='<path d="M4 7h16M10 11v6M14 11v6M6 7l1 12h10l1-12M9 7V4h6v3"/>'
def tile(inner, sel, h=140, label=''):
    ring = 'border: 1px solid #1f5a4b; box-shadow: inset 0 0 0 2px #1f5a4b; background: #e3eee8;' if sel else 'border: 1px solid #d9d3c4; background: #ffffff;'
    lb = f'<b style="font-size: 16px; line-height: 20px">{label}</b>' if label else ''
    return f'<a href="#" style="flex: 1 1 0; height: {h}px; box-sizing: border-box; padding: 8px 4px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; border-radius: 22px; {ring}">{inner}{lb}</a>'
NCOL = {'leicht':1,'mittel':2,'aufwendig':3}
STUFEN_K = ['leicht','mittel','aufwendig']
def colors(p, w, stufe, mode='mehr'):
    pres=[k for k in ('aeste','stern1','stern2') if p['layers'][k]]
    nc = 1 if mode=='ein' else NCOL[stufe]
    pal=[w[1],w[2],w[3]]
    return {k: pal[min(i,nc-1)] for i,k in enumerate(pres)}
def svgP(p, w, stufe, mode='mehr', W=245, H=346, pos=None, shadow='0 14px 36px rgba(30,42,51,.28)', extra=''):
    cols=colors(p,w,stufe,mode)
    node=p['node']
    posst = f'position: absolute; left: {pos[0]}px; top: {pos[1]}px; ' if pos else 'position: relative; '
    g=''
    for key in ('aeste','stern2','stern1'):
        ed=p['layers'][key]
        if ed:
            g+=f'<path d="'+''.join(f'M{node[a][0]:.1f} {node[a][1]:.1f}L{node[b][0]:.1f} {node[b][1]:.1f}' for a,b in ed)+f'" stroke="{cols[key]}"/>'
    holes=''.join(f'<circle cx="{node[u][0]:.1f}" cy="{node[u][1]:.1f}" r=".9"/>' for u in p['used'])
    return (f'<svg viewBox="0 0 105 148" style="{posst}width: {W}px; height: {H}px; border-radius: 8px; display: block; box-shadow: {shadow}; {extra}">'
            f'<rect width="105" height="148" fill="{w[0]}"/><path d="M0.4 0V148" stroke="#000" stroke-opacity=".35" stroke-width=".4" stroke-dasharray="2 1.5"/>'
            f'<g fill="none" stroke-width=".5" stroke-linecap="round">{g}</g><g fill="#0c1f17" fill-opacity=".85">{holes}</g></svg>\n')
SM = '0 3px 10px rgba(30,42,51,.25)'
# --- Aktueller Demo-Zustand: Stil Beides, Aufwand Mittel, Farbwelt 1
STIL, STUFE = 'beides','mittel'
def big(stil=STIL, stufe=STUFE, mode='mehr', welt=0, sz='p', over=None, onecolor=False):
    p = make(stil,stufe,**(over or {}))
    if sz=='p': return svgP(p,WELTEN[welt],stufe,mode,245,346,(72,108))
    return svgP(p,WELTEN[welt],stufe,mode,440,620,(158,84))
def mini(stil,stufe,welt,mode,W,H,over=None):
    return svgP(make(stil,stufe,**(over or {})),WELTEN[welt],stufe,mode,W,H,None,SM)
def three(left, top, w, h, gap, sel, stil=STIL):
    out=''
    for i,st in enumerate(STUFEN_K):
        x=left+i*(w+gap)
        out += svgP(make(stil,st),SEL_W,st,'mehr',w,h,(x,top),'0 14px 36px rgba(30,42,51,.28)', ('' if i==sel else 'opacity: .55; ')+('outline: 3px solid #1f5a4b; outline-offset: 4px;' if i==sel else ''))
    return out
def tiles_stufe(sel,h=140):
    nm=['Leicht','Mittel','Aufwendig']
    return row([tile(G%ic('stufen',32)+dots(i+1),i==sel,h,nm[i]) for i in range(3)])
STILN = [('aeste','Flocke'),('sternloch','Stern'),('both','Beides')]
def tiles_stil(sel=2,h=140): return row([tile(G%ic(ico,32),i==sel,h,lab) for i,(ico,lab) in enumerate(STILN)])
def farb_toggle(sel): return seg3([('einfarbig','Einfarbig'),('mehrfarbig','Mehrfarbig')],sel)
def tiles_welt(stufe,mode,W=80,H=113,h=140):
    return row([tile(mini(STIL,stufe,i,mode,W,H),i==0,h) for i in range(3)])
VAR = [{}, dict(st1=dict(k=3,level=3)), dict(st1=dict(k=2,level=4))]
def tiles_var(sel,W=80,H=113,h=140):
    return row([tile(mini(STIL,STUFE,0,'mehr',W,H,VAR[i]),i==sel,h) for i in range(3)])
def stage_tiles_h(h): return h
def top_back_close():
    return (f'  <div style="position: absolute; left: 16px; right: 16px; top: 59px; height: 44px; display: flex; gap: 8px; align-items: center"><a href="#" aria-label="Zurück" class="glass" style="width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("back")}</a><div style="flex-grow: 1"></div><a href="#" aria-label="Schließen" class="glass" style="width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("close")}</a></div>\n')
def star_btn(left,top): return f'  <a href="#" aria-label="Als Favorit sichern" class="glass" style="position: absolute; left: {left}px; top: {top}px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("star")}</a>\n'
WIZ = {}   # name -> (title, html)
def iph(name,title,active,card,pn): save(name, doc(title,390,844,card+wiz_top(active)+pn))
# ---------- iPhone Hauptreihe ----------
iph('Gefuehrt-iPhone-1-Format.dc.html','Geführter Weg 1 Format',0, cardL(72,108,245,346,()),
    panel(470,'Welche Karte?', row([tile(G%ic('kartehoch',32),True,140,'A6 hoch'), tile(G%ic('kartequer',32),False,140,'A6 quer')])+seg3([('karte','Falz links'),('karte','Oben'),('karte','Keiner')],0), cta()))
iph('Gefuehrt-iPhone-2-Stil.dc.html','Geführter Weg 2 Stil',1, big(mode='ein'), panel(470,'Welcher Stil?',tiles_stil(2),cta()))
def aufwand_board(name,title,sel,stil=STIL):
    iph(name,title,2, three(25,150,104,147,14,sel,stil), panel(470,'Wie aufwendig?',tiles_stufe(sel),cta()))
aufwand_board('Gefuehrt-iPhone-3-Aufwand.dc.html','Geführter Weg 3 Aufwand',1)
iph('Gefuehrt-iPhone-4-Farben.dc.html','Geführter Weg 4 Farben',3, big(), panel(470,'Welche Farbwelt?',farb_toggle(1)+tiles_welt('mittel','mehr'),cta('Varianten zeigen')))
iph('Gefuehrt-iPhone-4b-Farben-Einfarbig.dc.html','Geführter Weg 4 Farben einfarbig',3, big(mode='ein'), panel(470,'Welche Farbwelt?',farb_toggle(0)+tiles_welt('mittel','ein'),cta('Varianten zeigen')))
iph('Gefuehrt-iPhone-5-Auswahl.dc.html','Geführter Weg 5 Auswahl',4, big(over=VAR[0]), panel(470,'Welche Variante?',tiles_var(0),cta('Diese nehmen','check')))
res = big(sz='p').replace('left: 72px; top: 108px; width: 245px; height: 346px','left: 60px; top: 108px; width: 270px; height: 381px') + star_btn(276,118)
iph('Gefuehrt-iPhone-6-Ergebnis.dc.html','Geführter Weg 6 Ergebnis',4, '', '')  # Platzhalter, unten überschrieben
save('Gefuehrt-iPhone-6-Ergebnis.dc.html', doc('Geführter Weg 6 Ergebnis',390,844, res+top_back_close()+panel(560,'Dein Muster ist fertig','',cta('Anpassen','regler',False)+cta('Als PDF','printer'))))
# ---------- iPhone weitere Zustände ----------
aufwand_board('Gefuehrt-iPhone-3b-Aufwand-Leicht.dc.html','Geführter Weg 3 Aufwand Leicht',0)
aufwand_board('Gefuehrt-iPhone-3c-Aufwand-Aufwendig.dc.html','Geführter Weg 3 Aufwand Aufwendig',2)
# Leicht: keine Umschalter, eine Farbe
iph('Gefuehrt-iPhone-4c-Farben-Leicht.dc.html','Geführter Weg 4 Farben Leicht',3, big(stufe='leicht'), panel(470,'Welche Farbwelt?',tiles_welt('leicht','mehr',80,113,140),cta('Varianten zeigen')))
iph('Gefuehrt-iPhone-4d-Farben-Aufwendig.dc.html','Geführter Weg 4 Farben Aufwendig',3, big(stufe='aufwendig'), panel(470,'Welche Farbwelt?',farb_toggle(1)+tiles_welt('aufwendig','mehr'),cta('Varianten zeigen')))
iph('Gefuehrt-iPhone-5b-Auswahl-Variante2.dc.html','Geführter Weg 5 Auswahl Variante 2',4, big(over=VAR[1]), panel(470,'Welche Variante?',tiles_var(1),cta('Diese nehmen','check')))
# Abbruch
base = big()+wiz_top(2)+panel(470,'Wie aufwendig?',tiles_stufe(1),cta())
sheetA = ('  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.38); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px)"></div>\n'
  '  <div style="position: absolute; left: 12px; right: 12px; bottom: 34px; display: flex; flex-direction: column; gap: 8px">\n'
  f'    <div class="glass" style="border-radius: 26px; overflow: hidden; background: rgba(250,248,242,.9)"><div style="padding: 14px 16px; text-align: center; font-size: 13px; line-height: 18px; color: #5f594e">Muster verwerfen?</div><div style="height: 1px; background: #ddd7c8"></div><a href="#" style="height: 56px; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 17px; color: #b3261e; font-weight: 600">{ic("trash")}Verwerfen</a></div>\n'
  f'    <a href="#" class="glass" style="height: 56px; display: flex; align-items: center; justify-content: center; gap: 8px; border-radius: 28px; font-size: 17px; font-weight: 600; background: rgba(250,248,242,.95)">{ic("play")}Weitermachen</a>\n  </div>\n')
save('Gefuehrt-iPhone-7-Abbruch.dc.html', doc('Geführter Weg Abbruch',390,844, base+sheetA))
# ---------- iPad ----------
def ipbig(stil=STIL,stufe=STUFE,mode='mehr',over=None): return big(stil,stufe,mode,0,'l',over)
def ipt(h=190): return h
def ipad(name,title,active,card,h2,body,footer): ipad_wiz(name,title,active,card,h2,body,footer)
ipad('Gefuehrt-iPad-1-Format.dc.html','Geführter Weg iPad Format',0, cardL(158,84,440,620,()), 'Welche Karte?',
     row([tile(G%ic('kartehoch',32),True,190,'A6 hoch'), tile(G%ic('kartequer',32),False,190,'A6 quer')])+seg3([('karte','Falz links'),('karte','Oben'),('karte','Keiner')],0), cta())
ipad('Gefuehrt-iPad-2-Stil.dc.html','Geführter Weg iPad Stil',1, ipbig(mode='ein'), 'Welcher Stil?', tiles_stil(2,190), cta())
def ip_aufwand(sel): return three(143,200,150,212,16,sel)
ipad('Gefuehrt-iPad-3-Aufwand.dc.html','Geführter Weg iPad Aufwand',2, ip_aufwand(1), 'Wie aufwendig?', tiles_stufe(1,190), cta())
ipad('Gefuehrt-iPad-4-Farben.dc.html','Geführter Weg iPad Farben',3, ipbig(), 'Welche Farbwelt?', farb_toggle(1)+tiles_welt('mittel','mehr',80,113,190), cta('Varianten zeigen'))
ipad('Gefuehrt-iPad-5-Auswahl.dc.html','Geführter Weg iPad Auswahl',4, ipbig(over=VAR[0]), 'Welche Variante?', tiles_var(0,100,141,190), cta('Diese nehmen','check'))
res_i = ipbig().replace('left: 158px; top: 84px','left: 158px; top: 84px') + star_btn(544,98)
ipad('Gefuehrt-iPad-6-Ergebnis.dc.html','Geführter Weg iPad Ergebnis',4, res_i, 'Dein Muster ist fertig', '', cta('Anpassen','regler',False)+cta('Als PDF','printer'))
ipad('Gefuehrt-iPad-4c-Farben-Leicht.dc.html','Geführter Weg iPad Farben Leicht',3, ipbig(stufe='leicht'), 'Welche Farbwelt?', tiles_welt('leicht','mehr',80,113,190), cta('Varianten zeigen'))
ipad('Gefuehrt-iPad-4d-Farben-Aufwendig.dc.html','Geführter Weg iPad Farben Aufwendig',3, ipbig(stufe='aufwendig'), 'Welche Farbwelt?', farb_toggle(1)+tiles_welt('aufwendig','mehr',80,113,190), cta('Varianten zeigen'))
# Abbruch iPad: Alert mittig
ip_base = open(OUT+'Gefuehrt-iPad-3-Aufwand.dc.html').read()
body_ip = ip_base[ip_base.index('<div style="position: relative'):ip_base.index('</x-dc>')]
body_ip = body_ip[:body_ip.rindex('</div>')]
alert = ('  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.38); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px)"></div>\n'
  '  <div class="glass" style="position: absolute; left: 50%; top: 50%; width: 340px; margin: -110px 0 0 -170px; border-radius: 34px; background: rgba(250,248,242,.92); padding: 24px 16px 16px; box-sizing: border-box; display: flex; flex-direction: column; gap: 10px">\n'
  f'    <div style="text-align: center; font-family: Newsreader, Georgia, serif; font-size: 24px; line-height: 30px; font-weight: 600">Muster verwerfen?</div>\n'
  f'    <a href="#" style="height: 52px; display: flex; align-items: center; justify-content: center; gap: 8px; border-radius: 26px; background: #efeadd; color: #b3261e; font-size: 17px; font-weight: 600">{ic("trash")}Verwerfen</a>\n'
  f'    <a href="#" style="height: 52px; display: flex; align-items: center; justify-content: center; gap: 8px; border-radius: 26px; background: #1f5a4b; color: #ffffff; font-size: 17px; font-weight: 600">{ic("play")}Weitermachen</a>\n  </div>\n')
save('Gefuehrt-iPad-7-Abbruch.dc.html', doc('Geführter Weg iPad Abbruch',1180,820, body_ip[body_ip.index('\n')+1:]+alert))
print('ok')
