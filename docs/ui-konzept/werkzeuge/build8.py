import re
src = open('build7.py').read()
exec(src[:src.index('SEL_W = WELTEN[0]')])
PROJ = OUT
SEL_W = WELTEN[0]
lib.ICON['pencil']='<path d="M4 20l1-4L16 5l3 3L8 19zM14 7l3 3"/>'
lib.ICON['copy']='<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 00-2-2H6a2 2 0 00-2 2v8a2 2 0 002 2h2"/>'
lib.ICON['trash']='<path d="M4 7h16M10 11v6M14 11v6M6 7l1 12h10l1-12M9 7V4h6v3"/>'
lib.ICON['heart']='<path d="M12 20s-7-4.5-7-10a4 4 0 017-2.6A4 4 0 0119 10c0 5.5-7 10-7 10z"/>'
lib.ICON['starhohl']=lib.ICON.get('star','')
START = open(PROJ+'iPhone-Start.dc.html').read()
BOTTOM = START[START.index('<!-- Dauerhafte'):START.index('</x-dc>')].rstrip()
BOTTOM = BOTTOM[:BOTTOM.rindex('</div>')]          # äußeres Board-Div entfernen
NAV = BOTTOM[BOTTOM.index('<nav'):]
CAPS = BOTTOM[:BOTTOM.index('<nav')]
IPS = open(PROJ+'iPad-Start.dc.html').read()
ISTYLE = IPS[IPS.index('<style>'):IPS.index('</style>')+8]
ASIDE = IPS[IPS.index('<!-- Schwebende Seitenleiste -->'):IPS.index('<!-- Inhalt -->')]
def aside_sel(name):
    a = ASIDE.replace('<a href="#" class="sel">','<a href="#">')
    i = a.index('</svg>Favoriten</a>') if name=='Favoriten' else None
    if name=='Favoriten':
        k = a.rindex('<a href="#">', 0, i)
        a = a[:k]+'<a href="#" class="sel">'+a[k+len('<a href="#">'):]
    return a
FAV = [  # Name, Welt, Layer, s1k, quer?
 ('Mein Stern',0,('aeste','stern1'),3,False),('Winterlicht',1,('stern1',),2,True),('Kleine Flocke',2,('aeste','stern1'),4,False),
 ('Schneekristall',1,('aeste','stern1'),3,False),('Für Oma',0,('stern1',),3,True),('Weihnacht',2,('aeste','stern1'),2,False),
 ('Sternenstaub',0,('aeste','stern1'),4,True),('Eisblume',1,('stern1',),4,False)]
def thumb(e, W, H, n=2):
    nm, wi, lay, k, quer = e
    w = WELTEN[wi]
    svg = (cardL(0,0,W,H,lay,karton=w[0],faden=lvfad(w,len(lay)),s1k=k)
            .replace('position: absolute; left: 0px; top: 0px; ','position: relative; ')
            .replace('box-shadow: 0 14px 36px rgba(30,42,51,.28)','box-shadow: 0 3px 10px rgba(30,42,51,.25)'))
    if quer:   # Querformat: gleiche Karte, um 90 Grad gedreht, längste Seite = H
        inner = svg[svg.index('>')+1:svg.rindex('</svg>')]
        svg = (f'<svg viewBox="0 0 148 105" style="position: relative; width: {H}px; height: {round(H*105/148)}px; border-radius: 8px; display: block; box-shadow: 0 3px 10px rgba(30,42,51,.25)">'
               f'<g transform="translate(0 105) rotate(-90)">{inner}</g></svg>')
    return svg
def ptile(e, W, H, h, extra='', style=''):
    return (f'<a href="#" style="position: relative; height: {h}px; box-sizing: border-box; padding: 14px 14px 12px; display: flex; flex-direction: column; align-items: stretch; gap: 10px; background: #ffffff; border: 1px solid #d9d3c4; border-radius: 22px; {style}"><span style="width: 100%; height: {H}px; display: flex; align-items: center; justify-content: center">{thumb(e,W,H)}</span>'
            f'<span style="width: 100%; display: flex; align-items: center; gap: 6px; font-size: 16px; font-weight: 600; line-height: 20px"><span style="flex-grow: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{e[0]}</span>{extra}</span></a>')
HERO = ('<a href="#" style="position: relative; flex-shrink: 0; height: 120px; box-sizing: border-box; padding: 16px 16px 14px; display: flex; flex-direction: column; justify-content: flex-end; background: linear-gradient(150deg, #2a6b58, #123a2e); color: #ffffff; border-radius: 22px; overflow: hidden">'
        f'<span style="font-size: 12px; letter-spacing: 1.2px; opacity: .85">GEFÜHRT</span><b style="font-family: \'Newsreader\', Georgia, serif; font-size: 26px; line-height: 32px">Neues Muster</b></a>')
def top_seg(sel):
    def o(ico, lab, on):
        st = 'background: #ffffff; box-shadow: 0 1px 4px rgba(30,42,51,.22); font-weight: 600;' if on else ''
        return f'<a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 8px; {st} border-radius: 19px; font-size: 15px">{ic(ico,20)}{lab}</a>'
    return f'<div style="flex-shrink: 0; height: 44px; box-sizing: border-box; padding: 3px; display: flex; gap: 2px; background: #e6e1d4; border-radius: 22px">{o("karte","Muster",sel==0)}{o("star","Favoriten",sel==1)}</div>'
def start_frame(inner, caps=True):
    return (f'  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; box-sizing: border-box; padding: 59px 16px 0; display: flex; flex-direction: column; gap: 12px; overflow: hidden">\n'
            f'    <h1 style="margin: 0; flex-shrink: 0; font-family: \'Newsreader\', Georgia, serif; font-size: 40px; line-height: 46px; font-weight: 700">Stickkarten</h1>\n    {HERO}\n    {top_seg(1)}\n    {inner}\n  </div>\n'
            + (CAPS if caps else '') + NAV + '\n')
def grid2(items): return '<div style="flex-shrink: 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px">'+''.join(items)+'</div>'
def pdoc(name, title, w, h, body): save(name, doc(title, w, h, body, '#f4f0e6'))
STAR_ON = f'<span style="color: #1f5a4b; display: flex">{ic("star",20)}</span>'
# 1 Favoriten gefüllt
pdoc('iPhone-Favoriten.dc.html','iPhone Favoriten',390,844, start_frame(grid2([ptile(e,86,121,196) for e in FAV[:6]])))
# 2 Favoriten leer
leer = ('<div style="flex-grow: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; padding-bottom: 150px">'
        f'<span style="width: 88px; height: 88px; border-radius: 50%; background: #e6e1d4; color: #1f5a4b; display: flex; align-items: center; justify-content: center">{ic("star",40)}</span>'
        '<b style="font-family: \'Newsreader\', Georgia, serif; font-size: 24px; line-height: 30px; font-weight: 600">Noch keine Favoriten</b>'
        f'<a href="#" style="height: 52px; padding: 0 24px; display: flex; align-items: center; gap: 8px; background: #1f5a4b; color: #ffffff; border-radius: 26px; font-size: 17px; font-weight: 600">{ic("wizard")}Neues Muster</a></div>')
pdoc('iPhone-Favoriten-Leer.dc.html','iPhone Favoriten leer',390,844, start_frame(leer, False))
# 3 Kontextmenü
def mitem(ico, lab, red=False):
    c = 'color: #b3261e;' if red else ''
    return f'<a href="#" style="height: 48px; padding: 0 16px; display: flex; align-items: center; gap: 14px; font-size: 17px; {c}">{lab}<span style="margin-left: auto; display: flex">{ic(ico)}</span></a>'
menu_body = start_frame(grid2([ptile(e,86,121,196) for e in FAV[:6]]))
menu_body += ('  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.38); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px)"></div>\n'
  f'  <div style="position: absolute; left: 16px; width: 173px; top: 305px">{ptile(FAV[0],86,121,196,"",f"box-shadow: 0 14px 36px rgba(30,42,51,.35); transform: scale(1.03);")}</div>\n'
  f'  <div class="glass" style="position: absolute; left: 16px; top: 511px; width: 250px; border-radius: 22px; overflow: hidden; background: rgba(250,248,242,.88)">{mitem("pencil","Umbenennen")}<div style="height: 1px; background: #ddd7c8; margin: 0 16px"></div>{mitem("copy","Duplizieren")}<div style="height: 1px; background: #ddd7c8; margin: 0 16px"></div>{mitem("printer","Als PDF")}<div style="height: 1px; background: #ddd7c8; margin: 0 16px"></div>{mitem("trash","Löschen",True)}</div>\n')
pdoc('iPhone-Favoriten-Menue.dc.html','iPhone Favoriten Menü',390,844, menu_body)
# 4 Muster-Detail (fertiges Muster)
def fact(ico, t):
    return f'<span style="height: 36px; padding: 0 12px; display: inline-flex; align-items: center; gap: 6px; background: #efeadd; border-radius: 18px; font-size: 14px"><span style="color: #1f5a4b; display: flex">{ic(ico,20)}</span>{t}</span>'
facts = '<div style="display: flex; gap: 8px; flex-wrap: wrap">'+fact('kartehoch','A6')+fact('stufen',dots(2))+fact('palette','2')+'</div>'
e = FAV[1]
det = cardL(60,108,270,381,('aeste','stern1'),karton=WELTEN[1][0],faden=lvfad(WELTEN[1],2))
det += f'  <a href="#" aria-label="Als Favorit sichern" class="glass" style="position: absolute; left: 276px; top: 118px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("star")}</a>\n'
det += f'  <a href="#" aria-label="Zurück" class="glass" style="position: absolute; left: 16px; top: 59px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("back")}</a>\n'
det += panel(520,'Winterlicht',facts,cta('Anpassen','regler',False)+cta('Als PDF','printer'))
save('iPhone-Muster-Detail.dc.html', doc('iPhone Muster Detail',390,844,det))
# 5 iPad Favoriten
cells = ''.join(ptile(e,100,141,230) for e in FAV)
ib = (ISTYLE.replace('</style>','.g4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}</style>') + ASIDE.replace('x','x',0) if False else '')
ib = ISTYLE.replace('</style>','.g4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}</style>') + '\n' + aside_sel('Favoriten') + (
  '  <main style="position: absolute; left: 304px; right: 0; top: 0; bottom: 0; box-sizing: border-box; padding: 24px 28px 0; display: flex; flex-direction: column; gap: 12px; overflow: hidden">\n'
  '    <h1 style="margin: 0 0 6px; font-family: \'Newsreader\', Georgia, serif; font-size: 40px; line-height: 46px; font-weight: 700">Favoriten</h1>\n'
  f'    <div class="g4">{cells}</div>\n  </main>\n')
save('iPad-Favoriten.dc.html', doc('iPad Favoriten',1180,820,ib,'#f4f0e6'))
# 6 iPad Muster-Detail
cd = cardL(158,84,440,620,('aeste','stern1'),karton=WELTEN[1][0],faden=lvfad(WELTEN[1],2))
cd += f'  <a href="#" aria-label="Als Favorit sichern" class="glass" style="position: absolute; left: 544px; top: 98px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("star")}</a>\n'
cd += f'  <a href="#" aria-label="Zurück" class="glass" style="position: absolute; left: 16px; top: 16px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("back")}</a>\n'
cd += ('  <aside class="glass" style="position: absolute; right: 12px; top: 12px; bottom: 12px; width: 400px; box-sizing: border-box; padding: 24px 16px 16px; border-radius: 34px; background: rgba(250,248,242,.9); display: flex; flex-direction: column; gap: 14px; overflow: hidden">\n'
       f'    <h2 style="margin: 0; font-family: Newsreader, Georgia, serif; font-size: 30px; line-height: 36px; font-weight: 600">Winterlicht</h2>\n    {facts}\n    <div style="display: flex; gap: 8px; margin-top: auto">{cta("Anpassen","regler",False)}{cta("Als PDF","printer")}</div>\n  </aside>\n')
save('iPad-Muster-Detail.dc.html', doc('iPad Muster Detail',1180,820,cd))
print('ok')
