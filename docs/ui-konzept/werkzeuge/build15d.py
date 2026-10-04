# Teil D: Stichfolge iPad/quer, Geführter Weg iPad, Hochformat, Teilfenster, Querformat
import sys, math, re
exec(open('build15.py').read())
# ---- Stichfolge-Bausteine aus build13 (ohne dessen Boards)
b13 = open('build13.py').read()
pre13 = b13[b13.index("S = open('tpl"):b13.index("PA = make(")]
_save = save
_cap = {}
exec(pre13)                         # track (Stichfolge), sequence, card_svg, chip, board ...
STR_track = track                   # Stichfolge-Leiste
track_edit = lib.track
PA = make('beides','aufwendig')
def stich_inner(section, step=None, off=()):
    cap = {}
    global save, panel_wrap
    sv, pw = save, panel_wrap
    panel_wrap = lambda inner: '@@'+inner+'@@'
    save = lambda n,h: cap.update(h=h)
    try: board('_t.dc.html','t',PA,section,step,off)
    finally: save, panel_wrap = sv, pw
    return re.search(r'@@(.*)@@', cap['h'], re.S).group(1)
def card_big(section, step, left, top, w, h):
    global W, H
    ow, oh = W, H; W, H = w, h
    try: s = card_svg(PA, section, step)
    finally: W, H = ow, oh
    return s.replace('left: 38px; top: 112px', f'left: {left}px; top: {top}px')
def seg2(active, left, top=16):
    def o(ico,lab,on):
        st='background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); font-weight: 600;' if on else ''
        return f'<a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; border-radius: 19px; font-size: 14px; {st}">{ic(ico,20)}{lab}</a>'
    return f'  <div class="glass" style="position: absolute; left: {left}px; top: {top}px; width: 300px; height: 44px; box-sizing: border-box; padding: 3px; display: flex; gap: 2px; border-radius: 22px">{o("muster","Muster",active==0)}{o("play","Stichfolge",active==1)}</div>\n'
def gbtn(ico, label, left, top): return f'  <a href="#" aria-label="{label}" class="glass" style="position: absolute; left: {left}px; top: {top}px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic(ico)}</a>\n'
def aside(inner, w=400, extra=''):
    return f'  <aside class="glass" style="position: absolute; right: 12px; top: 12px; bottom: 12px; width: {w}px; box-sizing: border-box; padding: 16px; border-radius: 34px; background: rgba(250,248,242,.9); display: flex; flex-direction: column; gap: 12px; overflow: hidden{extra}">\n{inner}\n  </aside>\n'
def ip_stich(name, title, section, step=None):
    html = (card_big(section, step, 158, 84, 440, 620) + gbtn('menu','Seitenleiste einblenden',16,16) + seg2(1,228) + gbtn('star','Als Favorit sichern',544,98) + gbtn('printer','Drucken und Teilen',696,16)
            + aside(stich_inner(section, step)))
    save(name, doc(title,1180,820,html))
lib.ICON.setdefault('menu','<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M9 5v14"/>')
ip_stich('iPad-Stichfolge-Lochmuster.dc.html','iPad Stichfolge Lochmuster','loch')
ip_stich('iPad-Stichfolge-Aeste.dc.html','iPad Stichfolge Äste','aeste',41)
ip_stich('iPad-Stichfolge-Gesamtbild.dc.html','iPad Stichfolge Gesamtbild','gesamt')
# ---- iPhone Querformat (844 x 390): Karte links, Panel rechts
def quer_card(w_, section=None, step=None):
    ch = 290; cw = round(ch*105/148)
    return cw, ch
def q_edit():
    cw,ch = quer_card(0)
    card = svgP(make('beides','aufwendig'), WELTEN[0], 'aufwendig', 'mehr', cw, ch, (150,84))
    inner = (lib.track('aeste')+lib.slider('Astwinkel','angle','55°',82)+lib.slider('Astlänge','laenge','70 %',70)+stepper('Ebenen','ebenen',4))
    return card + gbtn('back','Zurück',59,20) + seg2(0,111,20).replace('width: 300px','width: 260px') + gbtn('printer','Drucken und Teilen',381,20) + gbtn('star','Als Favorit sichern',356,60).replace('left: 356px; top: 60px','left: 296px; top: 92px') + aside(inner,340,'; right: 47px')
html = q_edit()
save('iPhone-Quer-Editor.dc.html', doc('iPhone Querformat Editor',844,390,html))
def q_stich(section, step, name, title):
    cw,ch = quer_card(0)
    card = card_big(section, step, 150, 84, cw, ch)
    html = card + gbtn('back','Zurück',59,20) + seg2(1,111,20).replace('width: 300px','width: 260px') + gbtn('printer','Drucken und Teilen',381,20) + aside(stich_inner(section, step),340,'; right: 47px')
    save(name, doc(title,844,390,html))
q_stich('aeste',41,'iPhone-Quer-Stichfolge.dc.html','iPhone Querformat Stichfolge')
# Geführter Weg quer: Aufwand
def q_wiz():
    cw,ch = quer_card(0)
    stil = 'beides'
    cards=''.join(svgP(make(stil,st),SEL_W,st,'mehr',100,141,(88+i*114,120),'0 8px 20px rgba(30,42,51,.28)', ('' if i==1 else 'opacity: .55; ')+('outline: 3px solid #1f5a4b; outline-offset: 3px;' if i==1 else '')) for i,st in enumerate(STUFEN_K))
    top = wiz_top(2,59,413,20)
    inner = f'<h2 style="margin: 0; font-family: Newsreader, Georgia, serif; font-size: 26px; line-height: 32px; font-weight: 600">Wie aufwendig?</h2>{tiles_stufe(1,100)}<div style="display: flex; gap: 8px; margin-top: auto">{cta()}</div>'
    return cards + top + aside(inner,340,'; right: 47px')
save('iPhone-Quer-Gefuehrt-Aufwand.dc.html', doc('iPhone Querformat Geführter Weg Aufwand',844,390,q_wiz()))
def ipbig(stil=STIL,stufe=STUFE,mode='mehr',over=None): return big(stil,stufe,mode,0,'l',over)
def ipad(name,title,active,card,h2,body,footer): ipad_wiz(name,title,active,card,h2,body,footer)
def ip_aufwand(sel): return three(143,200,150,212,16,sel)
# ---- iPad Geführter Weg: Aufwand Leicht / Aufwendig, Stil Flocke / Stern
def ipad_aufwand(sel,name,title): ipad(name,title,2, ip_aufwand(sel), 'Wie aufwendig?', tiles_stufe(sel,190), cta())
ipad_aufwand(0,'Gefuehrt-iPad-3b-Aufwand-Leicht.dc.html','Geführter Weg iPad Aufwand Leicht')
ipad_aufwand(2,'Gefuehrt-iPad-3c-Aufwand-Aufwendig.dc.html','Geführter Weg iPad Aufwand Aufwendig')
ipad('Gefuehrt-iPad-2b-Stil-Flocke.dc.html','Geführter Weg iPad Stil Flocke',1, ipbig('flocke','mittel','ein'), 'Welcher Stil?', tiles_stil(0,190), cta())
ipad('Gefuehrt-iPad-2c-Stil-Stern.dc.html','Geführter Weg iPad Stil Stern',1, ipbig('stern','mittel','ein'), 'Welcher Stil?', tiles_stil(1,190), cta())
print('D1 ok')
