exec(open('build15d.py').read())
# ---- iPad Hochformat 820 x 1180
def g3(items): return '<div style="flex-shrink: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px">'+''.join(items)+'</div>'
hero = ('<a href="#" style="position: relative; flex-shrink: 0; height: 130px; box-sizing: border-box; padding: 18px 20px; display: flex; flex-direction: column; justify-content: flex-end; background: linear-gradient(150deg, #2a6b58, #123a2e); color: #ffffff; border-radius: 22px; overflow: hidden">'
        '<span style="font-size: 12px; letter-spacing: 1.2px; opacity: .85">GEFÜHRT</span><b style="font-family: Newsreader, Georgia, serif; font-size: 30px; line-height: 36px">Neues Muster</b></a>')
sec = lambda t: f'<div class="sec" style="margin-top: 8px">{t}</div>'
start_h = (gbtn('menu','Seitenleiste einblenden',16,16)
  + '  <main style="position: absolute; left: 0; right: 0; top: 76px; bottom: 0; box-sizing: border-box; padding: 0 28px; display: flex; flex-direction: column; gap: 12px; overflow: hidden">\n'
  '    <h1 style="margin: 0 0 6px; font-family: Newsreader, Georgia, serif; font-size: 40px; line-height: 46px; font-weight: 700">Start</h1>\n'
  + hero + sec('Fertige Muster') + g3([ptile(e,68,96,162,dotsx(e)) for e in MUSTER[:6]]) + sec('Favoriten') + g3([ptile(e,68,96,162) for e in FAV[:3]]) + '\n  </main>\n')
ipdoc('iPad-Hochformat-Start.dc.html','iPad Hochformat Start', start_h, w=820, h=1180)
# Editor Hochformat: Karte oben, Panel rechts 360 -> Karte links
ed_h = (svgP(make('beides','aufwendig'), WELTEN[0], 'aufwendig', 'mehr', 330, 465, (40,120))
  + gbtn('menu','Seitenleiste einblenden',16,16) + seg2(0,76,16).replace('width: 300px','width: 260px') + gbtn('printer','Drucken und Teilen',350,16)
  + aside(lib.track('aeste')+lib.slider('Astwinkel','angle','55°',82)+lib.slider('Astlänge','laenge','70 %',70)+stepper('Ebenen','ebenen',4), 360))
save('iPad-Hochformat-Editor.dc.html', doc('iPad Hochformat Editor',820,1180,ed_h))
# Geführter Weg Hochformat: Karte oben, Panel als Blatt unten
wz = (three(150,180,150,212,16,1)*0 + ''.join(svgP(make('beides',st),SEL_W,st,'mehr',200,282,(60+i*230,150),'0 14px 36px rgba(30,42,51,.28)', ('' if i==1 else 'opacity: .55; ')+('outline: 3px solid #1f5a4b; outline-offset: 4px;' if i==1 else '')) for i,st in enumerate(STUFEN_K[:3]) if i<3))
wz = ''.join(svgP(make('beides',st),SEL_W,st,'mehr',200,282,(40+i*200+i*0,150),'0 14px 36px rgba(30,42,51,.28)', ('' if i==1 else 'opacity: .55; ')+('outline: 3px solid #1f5a4b; outline-offset: 4px;' if i==1 else '')) for i,st in enumerate(STUFEN_K))
wz = ''.join(svgP(make('beides',st),SEL_W,st,'mehr',200,282,(70+i*240,150),'0 14px 36px rgba(30,42,51,.28)', ('' if i==1 else 'opacity: .55; ')+('outline: 3px solid #1f5a4b; outline-offset: 4px;' if i==1 else '')) for i,st in enumerate(STUFEN_K))
wz += wiz_top(2,16,16,16)
wz += panel(620,'Wie aufwendig?',tiles_stufe(1,190),cta())
save('iPad-Hochformat-Gefuehrt-Aufwand.dc.html', doc('iPad Hochformat Geführter Weg Aufwand',820,1180,wz))
# ---- Teilfenster (Slide Over): iPhone-Layout im schwebenden Fenster
def slide(name,title,bg_body,src,extra=''):
    s = open(PROJ+src).read()
    b = s[s.index('<div style="position: relative'):s.index('</x-dc>')]
    b = b[b.index('\n')+1:b.rindex('</div>')]
    win = ('  <div style="position: absolute; right: 16px; top: 12px; width: 390px; height: 796px; border-radius: 34px; overflow: hidden; background: #f4f0e6; box-shadow: 0 20px 60px rgba(30,42,51,.45)">\n'
           f'    <div style="position: relative; width: 390px; height: 796px; overflow: hidden; margin-top: -24px">{b}</div>\n  </div>\n')
    win = win.replace('<div style="position: relative; width: 390px; height: 796px; overflow: hidden; margin-top: -24px">','<div style="position: relative; width: 390px; height: 796px; overflow: hidden">')
    ipdoc(name,title,bg_body+'  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.28)"></div>\n'+win)
slide('iPad-Teilfenster-Start.dc.html','iPad Teilfenster Start (Slide Over)', ips_body, 'iPhone-Start.dc.html')
ed_body = open(PROJ+'iPad-Editor.dc.html').read(); ed_body = ed_body[ed_body.index('<div style="position: relative'):ed_body.index('</x-dc>')]; ed_body = ed_body[ed_body.index('\n')+1:ed_body.rindex('</div>')]
slide('iPad-Teilfenster-Editor.dc.html','iPad Teilfenster Editor (Slide Over)', ed_body, 'iPhone-Editor-Sheet.dc.html')
print('E ok')
