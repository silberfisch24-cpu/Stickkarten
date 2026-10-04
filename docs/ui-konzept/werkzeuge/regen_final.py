import json,shutil,os,glob
c=json.load(open('canvas.json')); B=c['boards']; N=c['notes']; O=c['order']
for k in [k for k in B if k.startswith('F-')]:
    del B[k]; O.remove(k)
for k in [k for k,v in N.items() if v.get('page') in ('iphone','ipad')]: del N[k]
IPH=[('Navigation und Ausgabe',[('iPhone-Start','Start'),('iPhone-Mehr','Mehr'),('iPhone-Ausgabe','Ausgabe'),('iPhone-Ausgabe-Kompakt-aus','Ausgabe-Kompakt-aus')]),
 ('Geführter Weg',[('Gefuehrt-iPhone-1-Format','Gefuehrt-1-Format'),('Gefuehrt-iPhone-2-Stil','Gefuehrt-2-Stil'),('Gefuehrt-iPhone-3-Aufwand','Gefuehrt-3-Aufwand'),('Gefuehrt-iPhone-4-Farben','Gefuehrt-4-Farben'),('Gefuehrt-iPhone-4b-Farben-Einfarbig','Gefuehrt-4-Farben-einfarbig'),('Gefuehrt-iPhone-5-Auswahl','Gefuehrt-5-Auswahl'),('Gefuehrt-iPhone-6-Ergebnis','Gefuehrt-6-Ergebnis')]),
 ('Geführter Weg: weitere Zustände',[('Gefuehrt-iPhone-3b-Aufwand-Leicht','Gefuehrt-3-Leicht'),('Gefuehrt-iPhone-3c-Aufwand-Aufwendig','Gefuehrt-3-Aufwendig'),('Gefuehrt-iPhone-4c-Farben-Leicht','Gefuehrt-4-Farben-Leicht'),('Gefuehrt-iPhone-4d-Farben-Aufwendig','Gefuehrt-4-Farben-Aufwendig'),('Gefuehrt-iPhone-5b-Auswahl-Variante2','Gefuehrt-5-Variante2'),('Gefuehrt-iPhone-7-Abbruch','Gefuehrt-Abbruch')]),
 ('Muster und Favoriten',[('iPhone-Favoriten','Favoriten'),('iPhone-Favoriten-Leer','Favoriten-leer'),('iPhone-Favoriten-Menue','Favoriten-Menue'),('iPhone-Muster-Detail','Muster-Detail')]),
 ('Editor: Sheet-Stufen und Gruppen',[('iPhone-Editor-Sheet-Klein','Editor-klein'),('iPhone-Editor-Sheet','Editor-mittel-Aeste'),('iPhone-Editor-Sheet-Gross','Editor-gross-Aeste'),('iPhone-Editor-Sheet-Grundform','Editor-mittel-Grundform'),('iPhone-Editor-Sheet-Stern1','Editor-mittel-Stern1')]),
 ('Editor: Karte und Meldungen',[('iPhone-Editor-Sheet-Warnung','Editor-mittel-Karte'),('iPhone-Editor-Sheet-Gross-Karte','Editor-gross-Karte'),('iPhone-Editor-Sheet-Ok','Editor-kein-Fehler'),('iPhone-Editor-Sheet-Kritisch','Editor-kritisch'),('iPhone-Editor-Sheet-Stern2-aus','Editor-Stern2-aus'),('iPhone-Editor-Sheet-Gross-Stern2-aus','Editor-gross-Stern2-aus')]),
 ('Stichfolge (5 Abschnitte)',[('Stichfolge-Lochmuster','Stichfolge-Lochmuster'),('Stichfolge-Aeste','Stichfolge-Aeste'),('iPhone-Editor-Stichfolge','Stichfolge-Stern1'),('Stichfolge-Stern2','Stichfolge-Stern2'),('Stichfolge-Gesamtbild','Stichfolge-Gesamtbild'),('Stichfolge-Schicht-aus','Stichfolge-Stern2-aus')])]
IPD=[('Navigation, Editor, Ausgabe',[('iPad-Start','Start'),('iPad-Editor','Editor'),('iPad-Ausgabe','Ausgabe'),('iPad-Ausgabe-Kompakt-aus','Ausgabe-Kompakt-aus')]),
 ('Geführter Weg',[(f'Gefuehrt-iPad-{n}',n) for n in ['1-Format','2-Stil','3-Aufwand','4-Farben','5-Auswahl','6-Ergebnis']]),
 ('Geführter Weg: weitere Zustände',[('Gefuehrt-iPad-4c-Farben-Leicht','4-Farben-Leicht'),('Gefuehrt-iPad-4d-Farben-Aufwendig','4-Farben-Aufwendig'),('Gefuehrt-iPad-7-Abbruch','Abbruch')]),
 ('Muster und Favoriten',[('iPad-Favoriten','Favoriten'),('iPad-Muster-Detail','Muster-Detail')])]
newfiles=set()
def build(page, dev, rows, pitch, w, h, offen, offen_x):
    fn=f'F-{dev}-00-Designregeln.dc.html'; shutil.copy('Designregeln.dc.html',fn); newfiles.add(fn)
    B[fn]={'x':0,'y':0,'w':1280,'h':1420,'title':'Designregeln','page':page}; O.append(fn)
    N[f'{page}_r0']={'x':0,'y':-240,'text':'Designregeln','kind':'title1','maxW':1280,'page':page}
    N[f'{page}_t']={'x':0,'y':-560,'text':{'iphone':'iPhone – erste finale Entwürfe','ipad':'iPad – erste finale Entwürfe'}[page],'kind':'title1','maxW':3000,'page':page}
    y=1420+360; idx=1; first=y
    for ri,(rt,items) in enumerate(rows,1):
        N[f'{page}_r{ri}']={'x':0,'y':y-240,'text':rt,'kind':'title1','maxW':max(len(items)*pitch,1200),'page':page}
        for i,(src,short) in enumerate(items):
            fn=f'F-{dev}-{idx:02d}-{short}.dc.html'; shutil.copy(src+'.dc.html',fn); newfiles.add(fn)
            B[fn]={'x':i*pitch,'y':y,'w':w,'h':h,'title':f'{idx:02d} {B[src+".dc.html"]["title"].split(" · ",1)[-1]}','page':page}; O.append(fn); idx+=1
        y+=h+360
    N[f'{page}_open']={'x':offen_x,'y':first,'w':520,'maxH':900,'text':offen,'fill':'orange','size':'m','page':page}
build('iphone','iPhone',IPH,470,390,844,'Noch offen (iPhone)\n\n• Einführung und Hilfe\n• Querformat',1410)
build('ipad','iPad',IPD,1260,1180,820,'Noch offen (iPad)\n\n• Stichfolge\n• Mehr, Hilfe, Einstellungen\n• Hochformat und Teilfenster',3780)
json.dump(c,open('canvas.json','w'),ensure_ascii=False,indent=2)
existing=set(os.path.basename(p) for p in glob.glob('F-*.dc.html'))
old=sorted(existing-newfiles)
for f in old: os.remove(f)
m={f'project/{f}':f'project/{f}' for f in sorted(newfiles)}
for f in old: m[f'project/{f}']=None
json.dump(m,open('/tmp/publish_map.json','w'),ensure_ascii=False)
print(len(newfiles),'neu',len(old),'alt')
