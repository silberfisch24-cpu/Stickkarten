import re, sys
sys.path.insert(0,'.')
b11 = open('build11.py').read()
exec(b11[:b11.index('# ---------- iPhone Hauptreihe ----------')])
b4 = open('build4.py').read()
exec(b4[:b4.index("aeste = track('aeste')")])
PROJ = OUT
# ---------- Editor: Schicht aus ----------
pm = make('beides','aufwendig',st2=None)
card_m = svgP(pm, WELTEN[0], 'aufwendig', 'mehr', CW, CH, (CL,CT))
mid_b = card_m + starbtn(CL,CT,CW) + topbar2('muster') + sheet3(SH, track('stern2')+'\n'+toggle('Schicht aktivieren','stern2',False))
save('iPhone-Editor-Sheet-Stern2-aus.dc.html', doc('iPhone Editor – Sheet mittel Stern 2 aus',390,844,mid_b))
dim='  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.28)"></div>\n'
dimmed = ('<div style="display: flex; flex-direction: column; gap: 10px; opacity: .4">'+stepper('Schrittweite','schritt',1)+stepper('Sternebene','ebenen',5)+stepper('Sternstrahlen','punkte',8)+stepper('Rotationsversatz','angle',0)+toggle('Seitenäste auslassen','aeste',False)+'</div>')
inner_g = track('stern2')+'\n'+toggle('Schicht aktivieren','stern2',False)+dimmed
big_b = svgP(pm, WELTEN[0], 'aufwendig', 'mehr', 246, 347, (72,108)) + topbar2('muster') + dim + sheet3(120, inner_g, ' background: #faf8f2;')
save('iPhone-Editor-Sheet-Gross-Stern2-aus.dc.html', doc('iPhone Editor – Sheet groß Stern 2 aus',390,844,big_b))
