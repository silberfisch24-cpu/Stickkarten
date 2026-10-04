import sys, json
sys.path.insert(0,'.')
from lib import *
OUT='/tmp/claude-0/-home-user-Stickkarten/7d64d15f-70be-5a8c-bbc1-d86911943200/scratchpad/konzept1/project/'
def save(name, html): open(OUT+name,'w').write(html)

CARD_MID = dict(left=72, top=108, w=246, h=347)
def mid_card(mode='normal'): return card(CARD_MID['left'],CARD_MID['top'],CARD_MID['w'],CARD_MID['h'],mode)

# ---- Mittel: Äste ----
inner = track('aeste') + '\n' + slider('Astwinkel','angle','55°',82) + slider('Astlänge','laenge','70 %',28) + colorrow(1)
save('iPhone-Editor-Sheet.dc.html', doc('iPhone Editor – Sheet mittel', 390, 844,
     mid_card()+topbar('muster')+sheet(471, inner)))

# ---- Mittel: Karte mit Live-Warnung ----
inner = track('karte') + '\n' + slider('Zoom','zoom','100 %',100) + formatrow()
save('iPhone-Editor-Sheet-Warnung.dc.html', doc('iPhone Editor – Warnung live', 390, 844,
     mid_card('warn')+warnchips(84,404)+topbar('muster',issues=True)+sheet(471, inner)))

# ---- Mittel: Grundform ----
inner = track('grund') + '\n' + stepper('Kreispunkte','punkte',8) + stepper('Ebenen','ebenen',4)
save('iPhone-Editor-Sheet-Grundform.dc.html', doc('iPhone Editor – Sheet mittel Grundform', 390, 844,
     mid_card()+topbar('muster')+sheet(471, inner)))

# ---- Klein ----
save('iPhone-Editor-Sheet-Klein.dc.html', doc('iPhone Editor – Sheet klein', 390, 844,
     card(25,112,340,479)+topbar('muster')+sheet(690, track('aeste'))))

# ---- Groß ----
inner = (track('aeste') + '\n' + slider('Astwinkel','angle','55°',82) + slider('Astlänge','laenge','70 %',28)
         + toggle('Seitenäste','aeste',True) + slider('Wachstum','wachstum','30 %',20) + colorrow(1))
save('iPhone-Editor-Sheet-Gross.dc.html', doc('iPhone Editor – Sheet groß', 390, 844,
     card(72,108,246,347)+topbar('muster')
     +'  <div style="position: absolute; left: 0; right: 0; top: 0; bottom: 0; background: rgba(30,42,51,.28)"></div>\n'
     +sheet(120, inner, extra=' background: #faf8f2;')))

# ---- Stichfolge (5 Abschnitte) ----
stich_card = '''  <svg viewBox="0 0 105 148" style="position: absolute; left: 38px; top: 112px; width: 313px; height: 441px; border-radius: 8px; display: block; box-shadow: 0 14px 36px rgba(30,42,51,.28)">
    <rect width="105" height="148" fill="#153a2c"/>
    <path d="M0.4 0V148" stroke="#000" stroke-opacity=".35" stroke-width=".4" stroke-dasharray="2 1.5"/>
    <g stroke="#d9e2e7" stroke-opacity=".28" stroke-width=".5" fill="none"><path d="M58 74L58 38M58 74L83.5 48.5M58 74L94 74M58 74L83.5 99.5M58 74L58 110M58 74L32.5 99.5M58 74L22 74M58 74L32.5 48.5"/></g>
    <g stroke="#ffffff" stroke-opacity=".2" stroke-width=".3" fill="none"><path d="M58 110L32.5 48.5M32.5 99.5L58 38M22 74L83.5 48.5M32.5 48.5L94 74"/></g>
    <g stroke="#e8c987" stroke-width=".5" fill="none"><path d="M58 38L83.5 99.5M83.5 48.5L58 110M94 74L32.5 99.5"/></g>
    <path d="M22 74L58 110" stroke="#7fd8ff" stroke-width=".5" stroke-dasharray="1.2 1.2" fill="none"/>
    <path d="M83.5 99.5L22.7 74.3" stroke="#ffd966" stroke-width=".9" stroke-linecap="round" fill="none"/>
    <path d="M21.67 73.86L23.67 73.72L22.99 75.38z" fill="#ffd966"/>
    <g fill="#0c1f17">''' + ''.join(f'<circle cx="{x}" cy="{y}" r=".9"/>' for x,y in P+[(58,74)]) + '''</g>
  </svg>
'''
panel = ('  <div class="glass" style="position: absolute; left: 16px; right: 16px; bottom: 22px; box-sizing: border-box; padding: 12px; border-radius: 32px; display: flex; flex-direction: column; gap: 8px">\n    '
  + track('stern1', keys=('loch','aeste','stern1','stern2','gesamt')) + '''
    <div style="display: flex; gap: 8px">
      <span style="flex: 1 1 0; height: 40px; box-sizing: border-box; padding: 0 12px; display: flex; align-items: center; gap: 8px; background: #e0f0e6; color: #14603a; border-radius: 20px; font-size: 15px; font-weight: 600"><svg class="i" viewBox="0 0 24 24" aria-hidden="true" style="width: 22px; height: 22px"><path d="M4 12h15M14 7l5 5-5 5"/></svg>K4 → K7</span>
      <span style="flex: 1 1 0; height: 40px; box-sizing: border-box; padding: 0 12px; display: flex; align-items: center; gap: 8px; background: #f8e4e0; color: #9c2f2f; border-radius: 20px; font-size: 15px; font-weight: 600"><svg class="i" viewBox="0 0 24 24" aria-hidden="true" style="width: 22px; height: 22px"><path d="M4 12h2M9 12h2M14 12h2M19 12h1M16 8l4 4-4 4" stroke-dasharray="1 4"/></svg>K7 → K5</span>
    </div>
    <div style="display: flex; align-items: center; gap: 12px; padding: 0 4px">
      <div style="position: relative; flex-grow: 1; height: 44px">
        <i style="position: absolute; left: 0; right: 0; top: 19px; height: 6px; border-radius: 3px; background: #dcd5c5"></i>
        <i style="position: absolute; left: 0; width: 50%; top: 19px; height: 6px; border-radius: 3px; background: #1f5a4b"></i>
        <i style="position: absolute; left: 0; right: 0; top: 30px; height: 8px; background: repeating-linear-gradient(90deg,#b3ab9b 0 1px,transparent 1px 36px)"></i>
        <i style="position: absolute; left: calc(50% - 14px); top: 8px; width: 28px; height: 28px; border-radius: 50%; background: #ffffff; box-shadow: 0 2px 8px rgba(30,42,51,.35)"></i>
      </div>
      <b style="min-width: 44px; text-align: right; font-size: 15px">4 / 8</b>
    </div>
    <div style="display: flex; align-items: center; justify-content: space-between">
      <a href="#" aria-label="Zum Anfang" style="width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; background: #efeadd; border-radius: 50%"><svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 5v14M18 5l-9 7 9 7z"/></svg></a>
      <a href="#" aria-label="Ein Schritt zurück" style="width: 56px; height: 56px; display: flex; align-items: center; justify-content: center; background: #efeadd; border-radius: 50%"><svg class="i" viewBox="0 0 24 24" aria-hidden="true" style="width: 28px; height: 28px"><path d="M15 6l-6 6 6 6"/></svg></a>
      <a href="#" aria-label="Wiedergabe" style="width: 68px; height: 68px; display: flex; align-items: center; justify-content: center; background: #1f5a4b; color: #ffffff; border-radius: 50%"><svg class="i" viewBox="0 0 24 24" aria-hidden="true" style="width: 32px; height: 32px; fill: currentColor"><path d="M8 5l11 7-11 7z"/></svg></a>
      <a href="#" aria-label="Ein Schritt vor" style="width: 56px; height: 56px; display: flex; align-items: center; justify-content: center; background: #efeadd; border-radius: 50%"><svg class="i" viewBox="0 0 24 24" aria-hidden="true" style="width: 28px; height: 28px"><path d="M9 6l6 6-6 6"/></svg></a>
      <a href="#" aria-label="Geschwindigkeit" style="height: 48px; box-sizing: border-box; padding: 0 12px; display: flex; align-items: center; gap: 6px; background: #efeadd; border-radius: 24px; font-size: 15px; font-weight: 600"><svg class="i" viewBox="0 0 24 24" aria-hidden="true" style="width: 22px; height: 22px"><path d="M4 18a8 8 0 1116 0M12 18l4-5"/></svg>1×</a>
    </div>
  </div>
''')
save('iPhone-Editor-Stichfolge.dc.html', doc('iPhone Editor – Stichfolge', 390, 844, stich_card+topbar('stich')+panel))

# ---- iPad Editor ----
def track_stacked(selected):
    keys=('grund','aeste','stern1','stern2','karte'); lab={'grund':'Grundform','aeste':'Äste','stern1':'Stern 1','stern2':'Stern 2','karte':'Karte'}
    it=''
    for k in keys:
        if k==selected:
            it+=f'<a href="#" style="flex: 1 1 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); border-radius: 18px; font-size: 11px; font-weight: 600">{ic(k,22)}{lab[k]}</a>'
        else:
            it+=f'<a href="#" style="flex: 1 1 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; color: #1e2a33; border-radius: 18px; font-size: 11px">{ic(k,22)}{lab[k]}</a>'
    return f'<div style="height: 64px; flex-shrink: 0; box-sizing: border-box; padding: 4px; display: flex; gap: 2px; background: #e6e1d4; border-radius: 22px">{it}</div>'
rows = (slider('Astwinkel','angle','55°',82)+slider('Astlänge','laenge','70 %',28)+toggle('Seitenäste','aeste',True)+slider('Wachstum','wachstum','30 %',20)+colorrow(1))
ipad = (card(158,84,440,620)
  + f'  <a href="#" aria-label="Seitenleiste einblenden" class="glass" style="position: absolute; left: 16px; top: 16px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: 50%"><svg class="i" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="M9 5v14"/></svg></a>\n'
  + f'  <div class="glass" style="position: absolute; left: 258px; top: 16px; width: 240px; height: 48px; box-sizing: border-box; padding: 4px; display: flex; gap: 2px; border-radius: 24px"><a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); border-radius: 20px; font-size: 14px; font-weight: 600">{ic("muster",20)}Muster</a><a href="#" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; gap: 6px; border-radius: 20px; font-size: 14px">{ic("play",20)}Stichfolge</a></div>\n'
  + f'  <a href="#" aria-label="Als Favorit sichern" class="glass" style="position: absolute; left: 640px; top: 16px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("star")}</a>\n'
  + f'  <a href="#" aria-label="Ausgabe" class="glass" style="position: absolute; left: 696px; top: 16px; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: 50%">{ic("printer")}</a>\n'
  + '  <aside class="glass" style="position: absolute; right: 12px; top: 12px; bottom: 12px; width: 400px; box-sizing: border-box; padding: 16px; border-radius: 30px; background: rgba(250,248,242,.88); display: flex; flex-direction: column; gap: 12px; overflow: hidden">\n    '
  + track_stacked('aeste') + '\n    <div style="display: flex; flex-direction: column; gap: 8px; min-height: 0">\n' + rows + '    </div>\n'
  + f'    <div style="margin-top: auto; display: flex; gap: 8px"><a href="#" aria-label="Zurücksetzen" style="width: 56px; height: 56px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; background: #efeadd; border-radius: 50%">{ic("reset")}</a><a href="#" style="flex-grow: 1; height: 56px; display: flex; align-items: center; justify-content: center; gap: 10px; background: #1f5a4b; color: #ffffff; border-radius: 28px; font-size: 17px; font-weight: 600">{ic("printer")}Ausgabe</a></div>\n  </aside>\n')
save('iPad-Editor.dc.html', doc('iPad Editor', 1180, 820, ipad))
print('ok')
