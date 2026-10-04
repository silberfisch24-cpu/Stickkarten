import re, sys
sys.path.insert(0,'.')
b11 = open('build11.py').read()
exec(b11[:b11.index('# ---------- iPhone Hauptreihe ----------')])
b4 = open('build4.py').read()
exec(b4[:b4.index("aeste = track('aeste')")])
PROJ = OUT
# ---------- Editor: Schicht aus ----------
pm = make('beides','mittel')
card_m = svgP(pm, WELTEN[0], 'mittel', 'mehr', CW, CH, (CL,CT))
mid_b = card_m + starbtn(CL,CT,CW) + topbar2('muster') + sheet3(SH, track('stern2')+'\n'+toggle('Schicht aktivieren','stern2',False))
save('iPhone-Editor-Sheet-Stern2-aus.dc.html', doc('iPhone Editor – Sheet mittel Stern 2 aus',390,844,mid_b))
dim='  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.28)"></div>\n'
dimmed = ('<div style="display: flex; flex-direction: column; gap: 10px; opacity: .4">'+stepper('Schrittweite','schritt',1)+stepper('Sternebene','ebenen',5)+stepper('Sternstrahlen','punkte',8)+stepper('Rotationsversatz','angle',0)+toggle('Seitenäste auslassen','aeste',False)+'</div>')
inner_g = track('stern2')+'\n'+toggle('Schicht aktivieren','stern2',False)+dimmed
big_b = svgP(pm, WELTEN[0], 'mittel', 'mehr', 246, 347, (72,108)) + topbar2('muster') + dim + sheet3(120, inner_g, ' background: #faf8f2;')
save('iPhone-Editor-Sheet-Gross-Stern2-aus.dc.html', doc('iPhone Editor – Sheet groß Stern 2 aus',390,844,big_b))
# ---------- Ausgabe: Kompakt nicht verfügbar ----------
WARN_PILL = lambda: ('<span style="align-self: flex-start; display: inline-flex; align-items: center; gap: 6px; padding: 2px 10px 2px 8px; border-radius: 13px; background: #fcefd9; color: #6b3f00; font-size: 13px; line-height: 18px; font-weight: 600">'+ic('warn',16)+'Karte zu groß</span>')
def kompakt_aus(fn_in, fn_out, title, ipad):
    s = open(PROJ+fn_in).read()
    rows = [m.start() for m in re.finditer(r'<a href="#" style="min-height: 76px', s)]
    r1, r2, r3 = rows[0], rows[1], rows[2]
    row1 = s[r1:r2]; row2 = s[r2:r3]
    sel_radio = re.search(r'<span style="color: #1f5a4b; display: flex"><svg class="i" viewBox="0 0 24 24" aria-hidden="true" style="width: 26px; height: 26px;"><circle cx="12" cy="12" r="10" fill="currentColor" stroke="none"/>.*?</svg></span></a>', row1, flags=re.S).group(0)
    # Zeile 1 abblenden
    n1 = row1.replace('border: 2px solid #1f5a4b','border: 1px solid #d9d3c4')
    n1 = n1.replace('1 Seite · A4 quer · 100 %</span>','</span>',1)
    n1 = re.sub(r'<span style="font-size: 13px; line-height: 18px; color: #5f594e"></span>', WARN_PILL(), n1, count=1)
    n1 = n1.replace('<span style="width: 72px; height: 58px;','<span style="opacity: .45; width: 72px; height: 58px;',1)
    n1 = re.sub(r'<b style="font-size: 16px; line-height: 21px;', '<b style="opacity: .45; font-size: 16px; line-height: 21px;', n1, count=1)
    n1 = n1.replace(sel_radio,'</a>')
    # Zeile 2 wählen
    n2 = row2.replace('border: 1px solid #d9d3c4','border: 2px solid #1f5a4b',1)
    n2 = re.sub(r'<span style="width: 26px; height: 26px; box-sizing: border-box; border-radius: 50%; border: 2px solid #cfc8b8"></span></a>', sel_radio, n2, count=1)
    n2 = n2.replace('1 Seite · A4 quer · 100 %','1 Seite · A4 hoch · 100 %',1)
    out = s[:r1]+n1+n2+s[r3:]
    if ipad:  # große Vorschau: Lochmuster-Seite statt Kompakt
        th = re.search(r'<svg viewBox="[^"]*" style="[^"]*">.*?</svg>', row2, flags=re.S)
        th_svg = re.sub(r'style="[^"]*"', 'style="width: 512px; height: 362px; display: block; background: #ffffff; box-shadow: 0 6px 24px rgba(30,42,51,.3);"', th.group(0), count=1)
        big_old = re.search(r'<svg viewBox="0 0 297 210" style="width: 512px; height: 362px[^"]*">.*?</svg>', out, flags=re.S).group(0)
        out = out.replace(big_old, th_svg, 1)
        out = out.replace('Kompakt</b>','Kompakt</b>',1)
    out = re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', out, count=1)
    open(PROJ+fn_out,'w').write(out)
kompakt_aus('iPhone-Ausgabe.dc.html','iPhone-Ausgabe-Kompakt-aus.dc.html','iPhone Ausgabe Kompakt nicht verfügbar',False)
kompakt_aus('iPad-Ausgabe.dc.html','iPad-Ausgabe-Kompakt-aus.dc.html','iPad Ausgabe Kompakt nicht verfügbar',True)
print('ok')
