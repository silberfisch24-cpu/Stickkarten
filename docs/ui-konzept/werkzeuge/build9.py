import re
src = open('build8.py').read()
exec(src[:src.index('# 1 Favoriten gefüllt')])
MUSTER = [('Wintersterne',0,('stern1',),3,False),('Eiskristall',1,('aeste','stern1'),3,False),('Nordlicht',2,('aeste','stern1','stern2'),3,False),
 ('Schneeflocke',1,('stern1',),2,True),('Tannenzweig',0,('aeste','stern1'),4,True),('Rosenstern',2,('stern1',),4,False),
 ('Polarstern',1,('aeste','stern1','stern2'),3,False),('Kleiner Stern',0,('stern1',),2,False),('Eisblume',2,('aeste','stern1'),2,True),('Sternenreigen',0,('aeste','stern1','stern2'),4,False)]
def dotsx(e): return dots(len(e[2]))
# iPhone-Start: Raster ersetzen
s = open(PROJ+'iPhone-Start.dc.html').read()
a = s.index('<!-- Kachel-Raster'); b = s.index('<!-- Dauerhafte')
new = ('<!-- Kachel-Raster: Bildfläche fester Höhe, Muster mittig, Name links, Aufwand als Punkte -->\n    '
       + grid2([ptile(e,86,121,196,dotsx(e)) for e in MUSTER[:6]]) + '\n  </div>\n\n  ')
s = s[:a]+new+s[b:]
save('iPhone-Start.dc.html', s)
# iPad-Start: beide Raster ersetzen, Hero mit 5 Schritten
t = open(PROJ+'iPad-Start.dc.html').read()
icons5 = re.search(r'<span style="display: flex; align-items: center; gap: 8px; font-size: 14px; opacity: .9">.*?</span>', START, flags=re.S).group(0).replace('gap: 8px','gap: 10px')
t = re.sub(r'<span style="display: flex; align-items: center; gap: 10px; font-size: 14px; opacity: .9">.*?</span>', icons5, t, count=1, flags=re.S)
g5 = lambda items: '<div style="flex-shrink: 0; display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px">'+''.join(items)+'</div>'
a = t.index('<div class="grid">'); b = t.index('<div class="sec"', a)
t = t[:a] + g5([ptile(e,68,96,162,dotsx(e)) for e in MUSTER[:5]]) + '\n    ' + g5([ptile(e,68,96,162,dotsx(e)) for e in MUSTER[5:10]]) + '\n\n    ' + t[b:]
a = t.index('<div class="grid">'); b = t.index('</main>')
t = t[:a] + g5([ptile(e,68,96,162) for e in FAV[:5]]) + '\n  ' + t[b:]
save('iPad-Start.dc.html', t)
print('ok', 'Favorit<' in t)
