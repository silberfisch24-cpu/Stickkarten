src = open('build7.py').read()
exec(src[:src.index('SEL_W = WELTEN[0]\nLAY')])
SEL_W = WELTEN[0]
G = '<span style="color: #1f5a4b; display: flex">%s</span>'
lib.ICON['falzl']='<rect x="6" y="3" width="12" height="18" rx="2"/><path d="M9.5 3v18"/>'
body = row([tile(G%ic('kartehoch',32),True,190,'A6 hoch'), tile(G%ic('kartequer',32),False,190,'A6 quer')]) + seg3([('karte','Falz links'),('karte','Oben'),('karte','Keiner')],0)
ipad_wiz('Gefuehrt-iPad-1-Format.dc.html','Geführter Weg iPad Format',0, cardL(158,84,440,620,()), 'Welche Karte?', body, cta())
print('ok')
