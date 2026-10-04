import re, sys, math
PRE = open('build15.py').read().split("# ======================= Neue Boards")[0]
exec(PRE); exec(open('real.py').read())
PROJ = OUT
b8 = open('build8.py').read()
body8 = b8[b8.index('# 1 Favoriten gefüllt'):]
i4 = body8.index('# 4 Muster-Detail'); i5 = body8.index('# 5 iPad Favoriten'); i6 = body8.index('# 6 iPad Muster-Detail')
exec(body8[:i4])            # iPhone: Favoriten, leer, Menü
# Menü: Kontextkachel nutzt FAV[0]; ok
exec(body8[i5:i6])          # iPad Favoriten
# ---- Detail: Winterlicht (beides, mittel, Welt 1, 2 Farben)
def fact(ico, t):
    return f'<span style="height: 36px; padding: 0 12px; display: inline-flex; align-items: center; gap: 6px; background: #efeadd; border-radius: 18px; font-size: 14px"><span style="color: #1f5a4b; display: flex">{ic(ico,20)}</span>{t}</span>'
facts = '<div style="display: flex; gap: 8px; flex-wrap: wrap">'+fact('kartehoch','A6')+fact('stufen',dots(2))+fact('palette','2')+'</div>'
pw = make('beides','mittel')
det = svgP(pw, WELTEN[1], 'mittel', 'mehr', 270, 381, (60,108))
det += f'  <a href="#" aria-label="Als Favorit sichern" class="glass" style="position: absolute; left: 276px; top: 118px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("star")}</a>\n'
det += f'  <a href="#" aria-label="Zurück" class="glass" style="position: absolute; left: 16px; top: 59px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("back")}</a>\n'
det += panel(520,'Winterlicht',facts,cta('Anpassen','regler',False)+cta('Als PDF','printer'))
save('iPhone-Muster-Detail.dc.html', doc('iPhone Muster Detail',390,844,det))
cd = svgP(pw, WELTEN[1], 'mittel', 'mehr', 440, 620, (158,84))
cd += f'  <a href="#" aria-label="Als Favorit sichern" class="glass" style="position: absolute; left: 544px; top: 98px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("star")}</a>\n'
cd += f'  <a href="#" aria-label="Zurück" class="glass" style="position: absolute; left: 16px; top: 16px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("back")}</a>\n'
cd += ('  <aside class="glass" style="position: absolute; right: 12px; top: 12px; bottom: 12px; width: 400px; box-sizing: border-box; padding: 24px 16px 16px; border-radius: 34px; background: rgba(250,248,242,.9); display: flex; flex-direction: column; gap: 14px; overflow: hidden">\n'
       f'    <h2 style="margin: 0; font-family: Newsreader, Georgia, serif; font-size: 30px; line-height: 36px; font-weight: 600">Winterlicht</h2>\n    {facts}\n    <div style="display: flex; gap: 8px; margin-top: auto">{cta("Anpassen","regler",False)}{cta("Als PDF","printer")}</div>\n  </aside>\n')
save('iPad-Muster-Detail.dc.html', doc('iPad Muster Detail',1180,820,cd))
# iPad Favoriten: Seitenleiste mit Info-Eintrag
s = open(PROJ+'iPad-Favoriten.dc.html').read()
if 'Info und Datenschutz' not in s:
    k = s.index('Einstellungen</a>')+len('Einstellungen</a>')
    s = s[:k]+'\n      <a href="#">'+ic("info")+'Info und Datenschutz</a>'+s[k:]; open(PROJ+'iPad-Favoriten.dc.html','w').write(s)
# ---- Schicht aus: Muster ohne Stern 2 (gleiche Grundform wie "Mein Muster")
b13 = open('build13.py').read()
exec(b13[b13.index("S = open('tpl"):b13.index("PA = make(")])
PM = make('beides','aufwendig', st2=None)
board('Stichfolge-Schicht-aus.dc.html','Stichfolge Schicht aus',PM,'s1',4,off=('s2',))
b14 = open('build14.py').read()
b4 = open('build4.py').read()
print('d ok')
