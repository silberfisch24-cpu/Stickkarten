import re, sys, math, os
PRE = open('build15.py').read().split("# ======================= Neue Boards")[0]
exec(PRE); exec(open('real.py').read())
PROJ = OUT
# ---- 1 Weitermachen-Kapsel: echtes Muster
PA_ = make('beides','aufwendig')
mini = svgP(PA_, WELTEN[0], 'aufwendig', 'mehr', 40, 56, None, 'none').replace('position: relative; ','position: relative; flex-shrink: 0; ')
CAP_RE = re.compile(r'<svg viewBox="0 0 105 148" style="width: (40|42)px; height: (56|58)px; flex-shrink: 0; border-radius: 6px; display: block">.*?</svg>', re.S)
for fn in ['iPhone-Start','iPhone-Mehr','iPad-Start']:
    s = open(PROJ+fn+'.dc.html').read()
    def rep(m):
        w,h = m.group(1), m.group(2)
        return svgP(PA_, WELTEN[0], 'aufwendig', 'mehr', int(w), int(h), None, 'none').replace('border-radius: 8px','border-radius: 6px')
    s2, n = CAP_RE.subn(rep, s); open(PROJ+fn+'.dc.html','w').write(s2); print(fn,'Kapsel',n)
# ---- 2 iPhone-Start: Raster
s = open(PROJ+'iPhone-Start.dc.html').read()
a = s.index('<!-- Kachel-Raster'); b = s.index('<!-- Dauerhafte')
new = ('<!-- Kachel-Raster: Bildfläche fester Höhe, Muster mittig, Name links, Aufwand als Punkte -->\n    '
       + grid2([ptile(e,86,121,196,dotsx(e)) for e in MUSTER[:6]]) + '\n  </div>\n\n  ')
save('iPhone-Start.dc.html', s[:a]+new+s[b:])
# ---- 3 iPad-Start: Raster
t = open(PROJ+'iPad-Start.dc.html').read()
g5 = lambda items: '<div style="flex-shrink: 0; display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px">'+''.join(items)+'</div>'
GR = 'grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px">'
starts = [m.start() for m in re.finditer(r'<div style="flex-shrink: 0; display: grid; '+re.escape(GR), t)]
print('Raster', len(starts))
s1, s2, s3 = starts[:3]
sec2 = t.index('<div class="sec"', s2)
end3 = t.index('</main>')
t = (t[:s1] + g5([ptile(e,68,96,162,dotsx(e)) for e in MUSTER[:5]]) + '\n    ' + g5([ptile(e,68,96,162,dotsx(e)) for e in MUSTER[5:10]]) + '\n\n    ' + t[sec2:s3]
     + g5([ptile(e,68,96,162) for e in FAV[:5]]) + '\n  ' + t[end3:])
save('iPad-Start.dc.html', t)
print('start ok')
