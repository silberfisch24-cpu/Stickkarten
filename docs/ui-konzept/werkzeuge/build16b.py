import re, sys, math, itertools
exec(open('build16a.py').read().split("MODES = {")[0])      # Helfer, rc(), PATS
def sub(fn, pairs):
    s = open(PROJ+fn+'.dc.html').read()
    for a,b in pairs:
        assert a in s, (fn,a); s = s.replace(a,b)
    open(PROJ+fn+'.dc.html','w').write(s)
try: sub('iPhone-Editor-Sheet-Grundform',[('font-size: 22px">4</b>','font-size: 22px">5</b>')])
except AssertionError: pass
# ---------- build5 (PDF-Boards, Ausgabe) mit echtem Muster neu erzeugen ----------
b5 = open('build5.py').read()
b5 = b5[:b5.index("c = json.load(open(OUT+'canvas.json'))")]
pp = PATS['ok']
b5 = b5.replace("P + Q + [(58,74)]", "HOLES")
b5 = b5.replace("(a-58)", "(a-54.5)").replace('r="2.4" fill="#26241f"','r="1.2" fill="#26241f"')
b5 = b5.replace("from lib import card as oldcard", "oldcard = lambda l,t,w,h,m: rc(l,t,w,h,'ok')")
cm_new = '''def cardmm(x, y, k, layers=('aeste','stern1','stern2')):
    sw = .35 / k
    g = f'<g transform="translate({x} {y}) scale({k})"><rect width="105" height="148" fill="#ffffff" stroke="#26241f" stroke-width="{.3/k}"/><g fill="none" stroke="#26241f" stroke-width="{sw}" stroke-linecap="round">'
    nd = pp['node']
    def path(key): return ''.join(f'M{nd[a][0]:.1f} {nd[a][1]:.1f}L{nd[b][0]:.1f} {nd[b][1]:.1f}' for a,b in pp['layers'][key])
    if 'aeste' in layers: g += f'<path d="{path("aeste")}"/>'
    if 'stern2' in layers: g += f'<path d="{path("stern2")}" stroke-dasharray="{.5/k} {1.1/k}"/>'
    if 'stern1' in layers: g += f'<path d="{path("stern1")}" stroke-dasharray="{2.4/k} {1.4/k}"/>'
    r = max(.9, .4 / k)
    g += '</g><g fill="#26241f">' + ''.join(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{r}"/>' for a, b in HOLES) + '</g></g>'
    return g
'''
a = b5.index('def cardmm'); b = b5.index('CELLS = [')
b5 = b5[:a] + cm_new + b5[b:]
b5 = b5.replace("['Kreispunkte 8', 'Ebenen 4']","['Kreispunkte 8', 'Ebenen 5']").replace("'Winkel 55° · Länge 70 %'","'Winkel 45° · Länge 60 %'").replace("'an · Ebene 4 · Strahlen 8'","'an · Ebene 5 · Strahlen 8'")
b5 = b5.replace("['an · Seitenäste an', 'Winkel","['an · Seitenäste an', 'Winkel")
ns = {}
g = dict(globals()); g.update(dict(pp=pp, HOLES=[pp['node'][u] for u in pp['used']]))
exec(b5, g)
# Faelle-Boards: Lochmuster-Seite verwendet P,Q in page_case (ersetzt über HOLES)
print('build5 ok')
# ---------- Ausgabe-Varianten (Kompakt nicht verfügbar) ----------
b14 = open('build14.py').read()
kpart = b14[b14.index('WARN_PILL'):b14.index("kompakt_aus('iPhone-Ausgabe")]
g2 = dict(globals()); g2.update(re=re, PROJ=PROJ, ic=ic)
exec(kpart + "\nkompakt_aus('iPhone-Ausgabe.dc.html','iPhone-Ausgabe-Kompakt-aus.dc.html','iPhone Ausgabe Kompakt nicht verfügbar',False)\nkompakt_aus('iPad-Ausgabe.dc.html','iPad-Ausgabe-Kompakt-aus.dc.html','iPad Ausgabe Kompakt nicht verfügbar',True)\n", g2)
print('aus ok')
