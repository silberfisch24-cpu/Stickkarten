import re
P_ = '/tmp/claude-0/-home-user-Stickkarten/7d64d15f-70be-5a8c-bbc1-d86911943200/scratchpad/konzept1/project/'
def dark(s):
    # kombinierte Muster zuerst
    pairs = [
     ('background: #ffffff; color: #1f5a4b;', 'background: #55514a; color: #8fe0c4;'),
     ('background: #ffffff; box-shadow: 0 1px 4px', 'background: #55514a; box-shadow: 0 1px 4px'),
     ('background: #e3eee8;', 'background: #1f3d36;'),
     ('background:rgba(255,255,255,.7)','background:rgba(44,41,35,.72)'), ('border:1px solid rgba(255,255,255,.8)','border:1px solid rgba(255,255,255,.14)'), ('background:rgba(250,248,242,.9)','background:rgba(34,32,27,.92)'), ('border-bottom:1px solid #ddd7c8','border-bottom:1px solid #403d35'), ('background:#ffffff;border:1px solid #d9d3c4','background:#2b2823;border:1px solid #403d35'),
     ('background: rgba(255,255,255,.7)', 'background: rgba(44,41,35,.72)'),
     ('border: 1px solid rgba(255,255,255,.8)', 'border: 1px solid rgba(255,255,255,.14)'),
     ('background: rgba(250,248,242,.88)','background: rgba(34,32,27,.9)'), ('background: rgba(250,248,242,.9)', 'background: rgba(34,32,27,.92)'),
     ('background: rgba(250,248,242,.94)', 'background: rgba(34,32,27,.94)'),
     ('background: rgba(250,248,242,.95)', 'background: rgba(34,32,27,.95)'),
     ('background: #faf8f2', 'background: #22201b'),
     ('background: #ffffff', 'background: #2b2823'),
     ('background:#ffffff', 'background:#2b2823'),
     ('background: #f4f0e6', 'background: #181611'),
     ('background: #e9e4d6', 'background: #12100c'),
     ('background: #e6e1d4', 'background: #37342d'),
     ('background: #efeadd', 'background: #37342d'),
     ('background: #dcd5c5', 'background: #4a463d'),
     ('background: #cfc8b8', 'background: #4a463d'),
     ('#d9d3c4', '#403d35'), ('#ddd7c8', '#403d35'),
     ('#1e2a33', '#efeadd'), ('#4a453c', '#cfc8b8'), ('#5f594e', '#b5ad9d'), ('#6b655a', '#b5ad9d'), ('#8a8378', '#a39b8b'),
     ('color: #1f5a4b', 'color: #8fe0c4'),
     ('background: #fcefd9', 'background: #4a3511'), ('color: #6b3f00', 'color: #f3cf8b'), ('color: #9a5a00', 'color: #f3cf8b'),
     ('background: #fde7e3', 'background: #4a1d18'), ('color: #8f1d14', 'color: #ffb4a8'), ('color: #b3261e', 'color: #ffb4a8'),
     ('background: #e0f0e6', 'background: #1d3a2c'), ('color: #14603a', 'color: #8fd7ab'),
     ('#b3ab9b', '#6b665b'),
     ('rgba(30,42,51,.35)', 'rgba(255,255,255,.35)'),
    ]
    for a,b in pairs: s = s.replace(a,b)
    # Dokument-Grund
    s = s.replace('background: #f4f0e6;','background: #181611;').replace('background: #e9e4d6;','background: #12100c;')
    return s
def mk(src, dst, title):
    s = open(P_+src).read()
    s = dark(s)
    s = re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', s, count=1)
    open(P_+dst,'w').write(s)
mk('iPhone-Start.dc.html','iPhone-Dunkel-Start.dc.html','iPhone Dunkel Start')
mk('iPhone-Editor-Sheet.dc.html','iPhone-Dunkel-Editor.dc.html','iPhone Dunkel Editor')
mk('Gefuehrt-iPhone-3-Aufwand.dc.html','iPhone-Dunkel-Gefuehrt.dc.html','iPhone Dunkel Geführter Weg')
mk('iPad-Editor.dc.html','iPad-Dunkel-Editor.dc.html','iPad Dunkel Editor')
# ---- Dynamic Type (größte Stufe): Geführter Weg 3 und Editor
def scale_fonts(seg, f=1.4):
    return re.sub(r'font-size: (\d+)px', lambda m: f'font-size: {round(int(m.group(1))*f)}px', seg)
g = open(P_+'Gefuehrt-iPhone-3-Aufwand.dc.html').read()
i = g.index('<div class="sheet"')
head, panel = g[:i], g[i:]
panel = scale_fonts(panel, 1.4)
panel = panel.replace('top: 470px','top: 330px').replace('height: 140px','height: 176px').replace('height: 52px','height: 68px')
panel = panel.replace('margin-top: auto; padding-bottom: 34px','margin-top: auto; padding-bottom: 34px')
# Bildpfad: Vorschaukarten kleiner halten (liegen oberhalb 330)
open(P_+'iPhone-GrosseSchrift-Gefuehrt.dc.html','w').write(re.sub(r'<title>[^<]*</title>','<title>iPhone Größte Schrift Geführter Weg</title>',head+panel,count=1))
e = open(P_+'iPhone-Editor-Sheet.dc.html').read()
i = e.index('<div class="sheet"')
head, sh = e[:i], e[i:]
sh = scale_fonts(sh, 1.4).replace('top: 530px','top: 380px')
open(P_+'iPhone-GrosseSchrift-Editor.dc.html','w').write(re.sub(r'<title>[^<]*</title>','<title>iPhone Größte Schrift Editor</title>',head+sh,count=1))
print('H ok')
