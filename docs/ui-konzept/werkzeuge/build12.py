import sys
sys.path.insert(0,'.')
exec(open('build11.py').read().split('# ---------- iPhone Hauptreihe ----------')[0])
STILE=[('flocke','Flocke','Nur Äste'),('stern','Stern','Nur Sterne'),('beides','Beides','Äste + Stern 1 (+ Stern 2)')]
STUF=[('leicht','Leicht','bis ca. 50 Stiche'),('mittel','Mittel','bis ca. 80 Stiche'),('aufwendig','Aufwendig','bis ca. 110 Stiche')]
INFO={('flocke','leicht'):'6 Äste · 4 Ebenen',('flocke','mittel'):'10 Äste · 4 Ebenen',('flocke','aufwendig'):'14 Äste · 3 Ebenen',
 ('stern','leicht'):'1 Stern · 6 Strahlen',('stern','mittel'):'2 Sterne · je 10 Strahlen',('stern','aufwendig'):'2 Sterne · je 14 Strahlen',
 ('beides','leicht'):'6 Äste · 4 Ebenen · Stern 1',('beides','mittel'):'8 Äste · 4 Ebenen · Stern 1',('beides','aufwendig'):'8 Äste · 5 Ebenen · Stern 1 + 2'}
def cell(stil,stufe):
    p=make(stil,stufe); w=PRE[(stil,stufe)]
    ang = f'Astwinkel {w["w"]}° · Länge {str(w["l"]).replace(".",",")}' if w.get('aeste',True) else 'ohne Äste'
    farben = {'leicht':'1 Farbe','mittel':'bis 2 Farben','aufwendig':'bis 3 Farben'}[stufe]
    if stil=='flocke': farben='1 Farbe'
    if stil=='stern' and stufe=='leicht': farben='1 Farbe'
    if stil=='beides' and stufe=='leicht': farben='1 Farbe'
    thumb=svgP(p,WELTEN[0],stufe,'mehr',84,119,None,SM)
    var=''.join(f'<span style="height: 28px; padding: 0 10px; display: inline-flex; align-items: center; border-radius: 14px; background: #efeadd; font-size: 13px; color: #5f594e">V{i}</span>' for i in (1,2,3))
    return (f'<div style="background: #fff; border: 1px solid #d9d3c4; border-radius: 22px; padding: 16px; display: flex; gap: 14px; box-sizing: border-box">{thumb}'
            f'<div style="display: flex; flex-direction: column; gap: 4px; min-width: 0"><b style="font-size: 17px">{p["stitches"]} Stiche</b><span style="font-size: 14px; line-height: 19px">{INFO[(stil,stufe)]}</span>'
            f'<span style="font-size: 13px; line-height: 18px; color: #5f594e">{ang}</span><span style="font-size: 13px; line-height: 18px; color: #5f594e">{farben} · Abstand ≥ {str(p["mind"]).replace(".",",")} mm</span>'
            f'<div style="display: flex; gap: 6px; margin-top: 6px">{var}</div></div></div>')
head=''.join(f'<div style="display: flex; flex-direction: column; gap: 2px"><b style="font-size: 20px">{n}</b><span style="font-size: 13px; color: #5f594e">{d}</span></div>' for _,n,d in STUF)
rows=''
for sk,sn,sd in STILE:
    rows+=f'<div style="display: flex; flex-direction: column; justify-content: center; gap: 2px"><b style="font-size: 20px">{sn}</b><span style="font-size: 13px; color: #5f594e">{sd}</span></div>'+''.join(cell(sk,st) for st,_,_ in STUF)
def card(title,ico,lines):
    return (f'<div style="background: #fff; border: 1px solid #d9d3c4; border-radius: 22px; padding: 20px; display: flex; flex-direction: column; gap: 10px; box-sizing: border-box"><span style="display: flex; align-items: center; gap: 10px; font-size: 17px; font-weight: 600"><span style="color: #1f5a4b; display: flex">{ic(ico)}</span>{title}</span>'
            + ''.join(f'<span style="font-size: 14px; line-height: 20px">{l}</span>' for l in lines)+'</div>')
cards=''.join([
 card('Stichzahl (Kern)','stufen',['Äste: n · (3E − 4) mit Seitenästen, n · E ohne','Stern: n Stiche je Stern (Strahlen = n)','n = Äste/Strahlen, E = Ebenen']),
 card('Platzregel A6','karte',['Innerste Ebene braucht Abstand: n · E ≤ ca. 47','Ab Abstand 4,8 mm keine Warnung (1,5 × Mindestabstand)','Ab n = 10: Astwinkel ≤ 40°, Länge ≤ 0,55']),
 card('Farben','palette',['Leicht 1, Mittel bis 2, Aufwendig bis 3 Farben','Einfarbig/Mehrfarbig ab Mittel','Flocke hat nur ein Element: immer 1 Farbe'])])
html=(f'<div style="width: 1500px; box-sizing: border-box; padding: 48px 56px 56px; display: flex; flex-direction: column; gap: 24px; background: #f4f0e6; color: #1e2a33; font-family: \'IBM Plex Sans\', system-ui, sans-serif">'
 '<div style="display: flex; flex-direction: column; gap: 6px"><h1 style="margin: 0; font-family: Newsreader, Georgia, serif; font-size: 40px; line-height: 46px; font-weight: 700">Aufwand-Stufen im Geführten Weg</h1>'
 '<span style="font-size: 15px; line-height: 21px; color: #5f594e">Richtwert ist die Stichzahl. Jede Zelle ist ein fester Parametersatz (Beispiel V1), geprüft ohne Warnung. 9 Zellen × 3 Varianten = 27 feste Muster.</span></div>'
 f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px">{cards}</div>'
 f'<div style="display: grid; grid-template-columns: 150px repeat(3, minmax(0, 1fr)); gap: 16px; align-items: stretch"><div></div>{head}{rows}</div></div>')
save('Aufwand-Stufen.dc.html', doc('Aufwand-Stufen',1500,1000,html,'#f4f0e6'))
print('ok')
