# Echte Muster (pat.py) für Raster, Favoriten und Detail
FERTIG = [  # Name, Stil, Stufe, Welt, quer
 ('Flocke','flocke','leicht',0,False),('Eisblume','flocke','mittel',1,False),('Raureif','flocke','aufwendig',2,True),
 ('Aster','stern','leicht',1,False),('Zwilling','stern','mittel',0,True),('Polaris','stern','aufwendig',2,False),
 ('Funkel','beides','leicht',0,False),('Kristall','beides','mittel',1,False),('Nordlicht','beides','aufwendig',2,False),('Eisrose','beides','mittel',2,True)]
FAV = [
 ('Mein Stern','beides','mittel',0,False),('Winterlicht','beides','mittel',1,True),('Kleine Flocke','flocke','leicht',2,False),
 ('Schneekristall','flocke','mittel',1,False),('Für Oma','stern','mittel',0,True),('Weihnacht','beides','leicht',2,False),
 ('Sternenstaub','stern','aufwendig',0,True),('Tannenzweig','flocke','aufwendig',1,False)]
MUSTER = FERTIG
STUFE_N = {'leicht':1,'mittel':2,'aufwendig':3}
def dotsx(e): return dots(STUFE_N[e[2]])
def thumb(e, W, H, n=2):
    nm, stil, stufe, wi, quer = e
    s = svgP(make(stil,stufe), WELTEN[wi], stufe, 'mehr', W, H, None, '0 3px 10px rgba(30,42,51,.25)')
    if quer:
        inner = s[s.index('>')+1:s.rindex('</svg>')]
        return (f'<svg viewBox="0 0 148 105" style="position: relative; width: {H}px; height: {round(H*105/148)}px; border-radius: 8px; display: block; box-shadow: 0 3px 10px rgba(30,42,51,.25)">'
                f'<g transform="translate(0 105) rotate(-90)">{inner}</g></svg>')
    return s
