# Konsolidierung: echte Muster in allen Boards (Editor, Ausgabe, PDF, Start, Favoriten, Detail)
import re, sys, math, itertools
exec(open('build15.py').read().split("# ======================= Neue Boards")[0])   # Helfer (build11 + build8-Prelude)
exec(open('real.py').read())
PROJ = OUT
FADEN3 = {'aeste':'#d9e2e7','stern1':'#e8c987','stern2':'#ffffff'}
PATS = {'ok': make('beides','aufwendig'), 'warn': make('beides','aufwendig',w=55,l=.7), 'crit': make('beides','aufwendig',w=55,l=.8)}
def halo_nodes(p):
    pts = [(u,p['node'][u]) for u in p['used']]
    knapp=set(); eng=set()
    for (a,pa),(b,pb) in itertools.combinations(pts,2):
        d = math.dist(pa,pb)
        if d < 3.2: eng.update((a,b))
        elif d < 4.8: knapp.update((a,b))
    return knapp, eng
def rc(left, top, w, h, mode='ok', radius=8, shadow='0 14px 36px rgba(30,42,51,.28)', rel=False):
    p = PATS[mode]; node = p['node']
    pos = 'position: relative; ' if rel else f'position: absolute; left: {left}px; top: {top}px; '
    g = ''
    if mode != 'crit':
        for key in ('aeste','stern2','stern1'):
            ed = p['layers'][key]
            if ed: g += '<path d="'+''.join(f'M{node[a][0]:.1f} {node[a][1]:.1f}L{node[b][0]:.1f} {node[b][1]:.1f}' for a,b in ed)+f'" stroke="{FADEN3[key]}"/>'
    holes = ''.join(f'<circle cx="{node[u][0]:.1f}" cy="{node[u][1]:.1f}" r=".9"/>' for u in p['used'])
    halos = ''
    if mode in ('warn','crit'):
        kn, en = halo_nodes(p)
        halos += ''.join(f'<circle cx="{node[u][0]:.1f}" cy="{node[u][1]:.1f}" r="2.6" fill="#e8a23d" fill-opacity=".25" stroke="#e8a23d" stroke-width=".5"/>' for u in kn)
        halos += ''.join(f'<circle cx="{node[u][0]:.1f}" cy="{node[u][1]:.1f}" r="2.8" fill="#e0503f" fill-opacity=".3" stroke="#e0503f" stroke-width=".55"/>' for u in en)
    dots = ''
    if mode == 'crit':
        col = {}
        for key in ('aeste','stern1','stern2'):
            for a,b in p['layers'][key]:
                col.setdefault(a, FADEN3[key]); col.setdefault(b, FADEN3[key])
        dots = ''.join(f'<circle cx="{node[u][0]:.1f}" cy="{node[u][1]:.1f}" r="1" fill="{col[u]}"/>' for u in p['used'])
    return (f'<svg viewBox="0 0 105 148" style="{pos}width: {w}px; height: {h}px; border-radius: {radius}px; display: block; box-shadow: {shadow}">'
            f'<rect width="105" height="148" fill="#153a2c"/><path d="M0.4 0V148" stroke="#000" stroke-opacity=".35" stroke-width=".4" stroke-dasharray="2 1.5"/>'
            f'<g fill="none" stroke-width=".5" stroke-linecap="round">{g}</g>{"<g>"+dots+"</g>" if dots else ""}<g fill="#0c1f17" fill-opacity=".85">{holes if not dots else ""}</g>{halos}</svg>\n')
SVG_RE = re.compile(r'<svg viewBox="0 0 105 148" style="position: absolute; left: (-?\d+)px; top: (-?\d+)px; width: (\d+)px; height: (\d+)px;[^"]*">.*?</svg>\n?', re.S)
def patch_card(fn, mode):
    s = open(PROJ+fn).read()
    ms = [m for m in SVG_RE.finditer(s) if int(m.group(3)) > 150 and '<rect width="105" height="148"' in m.group(0)]
    assert ms, fn
    m = ms[0]
    s = s[:m.start()] + rc(int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4)),mode) + s[m.end():]
    open(PROJ+fn,'w').write(s); return len(ms)
MODES = {'iPhone-Editor-Sheet-Klein':'warn','iPhone-Editor-Sheet':'warn','iPhone-Editor-Sheet-Gross':'warn','iPhone-Editor-Sheet-Grundform':'warn',
 'iPhone-Editor-Sheet-Stern1':'warn','iPhone-Editor-Sheet-Warnung':'warn','iPhone-Editor-Sheet-Gross-Karte':'warn','iPhone-Editor-Sheet-Ok':'ok',
 'iPhone-Editor-Sheet-Kritisch':'crit','iPad-Editor':'warn'}
for k,mo in MODES.items():
    print(k, patch_card(k+'.dc.html', mo))

# ---- Werte der Regler passend zum echten Muster
def sub(fn, pairs):
    s = open(PROJ+fn+'.dc.html').read()
    for a,b in pairs:
        assert a in s, (fn,a)
        s = s.replace(a,b)
    open(PROJ+fn+'.dc.html','w').write(s)
W100 = [('width: 82%','width: 100%'),('calc(82% - 14px)','calc(100% - 14px)')]
for fn in ['iPhone-Editor-Sheet-Klein','iPhone-Editor-Sheet','iPhone-Editor-Sheet-Gross','iPad-Editor']:
    try: sub(fn, W100)
    except AssertionError as e: print('skip', e)
sub('iPhone-Editor-Sheet-Ok', [('>55°<','>45°<'),('70 %</b>','60 %</b>'),('width: 28%','width: 22%'),('calc(28% - 14px)','calc(22% - 14px)')])
sub('iPhone-Editor-Sheet-Kritisch', W100+[('70 %</b>','80 %</b>'),('width: 28%','width: 33%'),('calc(28% - 14px)','calc(33% - 14px)')])
