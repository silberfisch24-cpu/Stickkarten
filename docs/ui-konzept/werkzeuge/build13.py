import sys, math
sys.path.insert(0,'.')
from pat import *
src = open('build7.py').read()
exec(src[:src.index('SEL_W = WELTEN[0]\nLAY')])
SEL_W = WELTEN[0]
S = open('tpl/stichfolge_orig.html').read()
TOP = S[S.index('<div style="position: absolute; left: 16px; right: 16px; top: 59px'):S.index('<a href="#" aria-label="Als Favorit')]
STAR = S[S.index('<a href="#" aria-label="Als Favorit'):S.index('<div class="glass" style="position: absolute; left: 16px; right: 16px; bottom: 22px')]
tr = S.index('<div style="display: flex; align-items: center; justify-content: space-between">')
TRANSPORT = S[tr:S.index('</div>\n  </div>\n</div>\n</x-dc>')+6]
ICO = {  # Symbole der Abschnitte (aus dem bisherigen Board)
 'loch':'<circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="8" stroke-dasharray="2 3"/>',
 'aeste':'<path d="M12 21V9M12 15l-5-4M12 12l5-4M12 9V3"/>',
 's1':'<path d="M11 2l7 12H4zM11 18L4 6h14z" transform="translate(0 1) scale(.9)"/><text x="17" y="22" font-size="10" font-weight="700" fill="currentColor" stroke="none">1</text>',
 's2':'<path d="M11 2l7 12H4zM11 18L4 6h14z" transform="translate(0 1) scale(.9)"/><text x="17" y="22" font-size="10" font-weight="700" fill="currentColor" stroke="none">2</text>',
 'gesamt':'<path d="M12 3l9 5-9 5-9-5zM3 13l9 5 9-5"/>'}
SECT = [('loch','Lochmuster'),('aeste','Äste'),('s1','Stern 1'),('s2','Stern 2'),('gesamt','Gesamtbild')]
def track(active, off=()):
    out=''
    for k,lab in SECT:
        svg=lambda sz='': f'<svg class="i" viewBox="0 0 24 24" aria-hidden="true"{sz}>{ICO[k]}</svg>'
        SZ=' style="width: 20px; height: 20px;"'
        if k==active:
            out+=f'<a href="#" style="flex: 0 0 auto; padding: 0 14px; display: flex; align-items: center; justify-content: center; gap: 6px; background: #ffffff; color: #1f5a4b; box-shadow: 0 1px 4px rgba(30,42,51,.25); border-radius: 19px; font-size: 14px; font-weight: 600">{svg(SZ)}<span style="color: #1e2a33">{lab}</span></a>'
        else:
            op = ' opacity: .3;' if k in off else ''
            out+=f'<a href="#" aria-label="{lab}" style="flex: 1 1 0; display: flex; align-items: center; justify-content: center; color: #1e2a33; border-radius: 20px;{op}">{svg()}</a>'
    return f'<div style="height: 44px; flex-shrink: 0; box-sizing: border-box; padding: 3px; display: flex; gap: 2px; background: #e6e1d4; border-radius: 22px">{out}</div>'
# ---- Stichfolge aus dem Muster ----
def sequence(p):
    edges=[]
    for key in ('aeste','stern1','stern2'):
        for a,b in p['layers'][key]: edges.append((key,a,b))
    segs=[]; cur=None
    for key,a,b in edges:
        near,far=a,b
        if near==cur: near,far=b,a
        if cur is not None: segs.append(('jump',cur,near,key))
        segs.append(('stitch',near,far,key)); cur=far
    return edges, segs
def holes_numbering(segs):
    num={}
    for t,a,b,k in segs:
        for n in (a,b):
            if n not in num: num[n]=len(num)+1
    return num
def length(p,a,b): return math.dist(p['node'][a],p['node'][b])
W, H = 313, 441
def card_svg(p, section, step, w=WELTEN[0]):
    node=p['node']; cols={'aeste':w[1],'stern1':w[2],'stern2':w[3]}
    edges,segs=sequence(p)
    stitches=[s for s in segs if s[0]=='stitch']
    order=['aeste','stern1','stern2']
    g=''; hl=''
    sect_key={'aeste':'aeste','s1':'stern1','s2':'stern2'}.get(section)
    cnt={k:0 for k in order}
    idx_in={}  # laufender Index je Schicht
    sec_stitches=[s for s in stitches if s[3]==sect_key] if sect_key else []
    cur=None; nxt_jump=None
    for si,s in enumerate(stitches):
        k=s[3]; a,b=node[s[1]],node[s[2]]
        line=f'M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}'
        if section=='gesamt' or section=='loch' and False:
            g+=f'<path d="{line}" stroke="{cols[k]}" stroke-width=".5"/>'; continue
        if section=='loch': continue
        if k==sect_key:
            j=sec_stitches.index(s)+1
            if j<step: g+=f'<path d="{line}" stroke="{cols[k]}" stroke-width=".55"/>'
            elif j==step: cur=s
            else: g+=f'<path d="{line}" stroke="#ffffff" stroke-opacity=".18" stroke-width=".4"/>'
        else:
            before = order.index(k) < order.index(sect_key)
            if before: g+=f'<path d="{line}" stroke="{cols[k]}" stroke-opacity=".45" stroke-width=".4"/>'
            else: g+=f'<path d="{line}" stroke="#ffffff" stroke-opacity=".10" stroke-width=".3"/>'
    if cur:
        a,b=node[cur[1]],node[cur[2]]
        hl+=f'<path d="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}" stroke="#ffd966" stroke-width=".9" stroke-linecap="round" fill="none"/>'
        ang=math.atan2(b[1]-a[1],b[0]-a[0]); L=2.2
        tip=b; l=(b[0]-L*math.cos(ang)+L*.45*math.sin(ang), b[1]-L*math.sin(ang)-L*.45*math.cos(ang)); r=(b[0]-L*math.cos(ang)-L*.45*math.sin(ang), b[1]-L*math.sin(ang)+L*.45*math.cos(ang))
        hl+=f'<path d="M{tip[0]:.1f} {tip[1]:.1f}L{l[0]:.1f} {l[1]:.1f}L{r[0]:.1f} {r[1]:.1f}z" fill="#ffd966"/>'
        # folgender Sprung (hinten): gestrichelt
        gi=stitches.index(cur)
        if gi+1<len(stitches):
            nx=stitches[gi+1]; c=node[nx[1]]
            hl+=f'<path d="M{b[0]:.1f} {b[1]:.1f}L{c[0]:.1f} {c[1]:.1f}" stroke="#7fd8ff" stroke-width=".5" stroke-dasharray="1.2 1.2" fill="none"/>'
    r_h = 1.2 if section=='loch' else .9
    fill = '#0c1f17' if section!='loch' else '#0c1f17'
    holes=''.join(f'<circle cx="{node[u][0]:.1f}" cy="{node[u][1]:.1f}" r="{r_h}"/>' for u in p['used'])
    ringh=''
    return (f'<svg viewBox="0 0 105 148" style="position: absolute; left: 38px; top: 112px; width: {W}px; height: {H}px; border-radius: 8px; display: block; box-shadow: 0 14px 36px rgba(30,42,51,.28)">'
            f'<rect width="105" height="148" fill="{w[0]}"/><path d="M0.4 0V148" stroke="#000" stroke-opacity=".35" stroke-width=".4" stroke-dasharray="2 1.5"/>'
            f'<g fill="none" stroke-linecap="round">{g}</g>{hl}{ringh}<g fill="{fill}">{holes}</g></svg>\n')
def chip(kind, txt):
    if kind=='stitch':
        return f'<span style="flex: 1 1 0; height: 40px; box-sizing: border-box; padding: 0 12px; display: flex; align-items: center; gap: 8px; background: #e0f0e6; color: #14603a; border-radius: 20px; font-size: 15px; font-weight: 600"><svg class="i" viewBox="0 0 24 24" aria-hidden="true" style="width: 22px; height: 22px"><path d="M4 12h15M14 7l5 5-5 5"/></svg>{txt}</span>'
    if kind=='jump':
        return f'<span style="flex: 1 1 0; height: 40px; box-sizing: border-box; padding: 0 12px; display: flex; align-items: center; gap: 8px; background: #f8e4e0; color: #9c2f2f; border-radius: 20px; font-size: 15px; font-weight: 600"><svg class="i" viewBox="0 0 24 24" aria-hidden="true" style="width: 22px; height: 22px"><path d="M4 12h2M9 12h2M14 12h2M19 12h1M16 8l4 4-4 4" stroke-dasharray="1 4"/></svg>{txt}</span>'
    return f'<span style="flex: 1 1 0; height: 40px; box-sizing: border-box; padding: 0 12px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #efeadd; border-radius: 20px; font-size: 15px; font-weight: 600">{txt}</span>'
def slider(cur,total):
    pct=cur/total*100
    return (f'<div style="display: flex; align-items: center; gap: 12px; padding: 0 4px"><div style="position: relative; flex-grow: 1; height: 44px">'
      f'<i style="position: absolute; left: 0; right: 0; top: 19px; height: 6px; border-radius: 3px; background: #dcd5c5"></i>'
      f'<i style="position: absolute; left: 0; width: {pct:.0f}%; top: 19px; height: 6px; border-radius: 3px; background: #1f5a4b"></i>'
      f'<i style="position: absolute; left: 0; right: 0; top: 30px; height: 8px; background: repeating-linear-gradient(90deg,#b3ab9b 0 1px,transparent 1px 36px)"></i>'
      f'<i style="position: absolute; left: calc({pct:.0f}% - 14px); top: 8px; width: 28px; height: 28px; border-radius: 50%; background: #ffffff; box-shadow: 0 2px 8px rgba(30,42,51,.35)"></i></div>'
      f'<b style="min-width: 64px; text-align: right; font-size: 15px">{cur} / {total}</b></div>')
def panel_wrap(inner): return f'<div class="glass" style="position: absolute; left: 16px; right: 16px; bottom: 22px; box-sizing: border-box; padding: 12px; border-radius: 32px; display: flex; flex-direction: column; gap: 8px">{inner}</div>'
def dot(c): return f'<i style="width: 14px; height: 14px; border-radius: 50%; background: {c}; border: 1px solid rgba(30,42,51,.3); flex-shrink: 0"></i>'
def board(name,title,p,section,step=None,off=()):
    edges,segs=sequence(p); num=holes_numbering(segs)
    stitches=[s for s in segs if s[0]=='stitch']
    key={'aeste':'aeste','s1':'stern1','s2':'stern2'}.get(section)
    inner=track(section,off)
    if key:
        secs=[s for s in stitches if s[3]==key]; total=len(secs); cur=secs[step-1]
        gi=stitches.index(cur)
        a=num[cur[1]]; b=num[cur[2]]
        chips=chip('stitch',f'K{a} → K{b}')
        if gi+1<len(stitches): chips+=chip('jump',f'K{b} → K{num[stitches[gi+1][1]]}')
        inner+=f'<div style="display: flex; gap: 8px">{chips}</div>'+slider(step,total)+TRANSPORT
    elif section=='loch':
        nh=len(p['used'])
        inner+=('<div style="display: flex; gap: 8px">'+chip('x',f'<span style="color: #1f5a4b; display: flex">{ic("loch",22)}</span>{nh} Löcher')
          +chip('x',f'<span style="color: #1f5a4b; display: flex">{ic("abstand",22)}</span>≥ {str(p["mind"]).replace(".",",")} mm')+'</div>')
        inner+=('<div style="height: 44px; display: flex; align-items: center; gap: 12px; padding: 0 4px"><span style="color: #1f5a4b; display: flex">'+ic("abstand",22)+'</span>'
          '<div style="position: relative; flex-grow: 1; height: 14px; border-left: 2px solid #1e2a33; border-right: 2px solid #1e2a33"><i style="position: absolute; left: 0; right: 0; top: 6px; height: 2px; background: #1e2a33"></i></div><b style="min-width: 64px; text-align: right; font-size: 15px">50 mm</b></div>')
        inner+=f'<a href="#" style="height: 68px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #1f5a4b; color: #ffffff; border-radius: 34px; font-size: 17px; font-weight: 600">{ic("printer")}Vorlage 1:1 drucken</a>'
    else:
        tot=len(stitches); ln=sum(length(p,a,b) for _,a,b in edges)
        jl=sum(math.dist(p['node'][segs[i][1]],p['node'][segs[i][2]]) for i in range(len(segs)) if segs[i][0]=='jump')
        cm=(ln+jl)*1.15/10
        cn={k:len(p['layers'][k]) for k in ('aeste','stern1','stern2')}
        leg=''.join(f'<span style="flex: 1 1 0; height: 40px; display: flex; align-items: center; justify-content: center; gap: 6px; background: #efeadd; border-radius: 20px; font-size: 14px; font-weight: 600">{dot(c)}{n}</span>' for c,n in ((WELTEN[0][1],cn['aeste']),(WELTEN[0][2],cn['stern1']),(WELTEN[0][3],cn['stern2'])) )
        inner+=f'<div style="display: flex; gap: 8px">{leg}</div>'
        tchip=lambda ico,t: f'<span style="flex: 1 1 0; height: 44px; box-sizing: border-box; padding: 0 12px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #efeadd; border-radius: 22px; font-size: 15px; font-weight: 600"><span style="color: #1f5a4b; display: flex">{ic(ico,22)}</span>{t}</span>'
        inner+='<div style="display: flex; gap: 8px">'+tchip("stufen",f"{tot} Stiche")+tchip("faden",f"ca. {cm/100:.1f} m".replace(".",","))+'</div>'
        inner+=f'<a href="#" style="height: 68px; display: flex; align-items: center; justify-content: center; gap: 8px; background: #1f5a4b; color: #ffffff; border-radius: 34px; font-size: 17px; font-weight: 600">{ic("printer")}Drucken und Teilen</a>'
    html=card_svg(p,section,step)+TOP+STAR+panel_wrap(inner)
    save(name, doc(title,390,844,html))
    return dict(stitches=len(stitches), holes=len(p['used']))
lib.ICON['loch']=ICO['loch']; lib.ICON['abstand']='<path d="M4 12h16M7 9l-3 3 3 3M17 9l3 3-3 3"/>'; lib.ICON['faden']='<path d="M5 19c4 0 3-6 7-6s3-6 7-6M5 19a1 1 0 100-.1M19 7a1 1 0 100-.1"/>'
PA = make('beides','aufwendig'); PM = make('beides','mittel')
info = {}
info['loch']=board('Stichfolge-Lochmuster.dc.html','Stichfolge Lochmuster',PA,'loch')
info['aeste']=board('Stichfolge-Aeste.dc.html','Stichfolge Äste',PA,'aeste',41)
board('iPhone-Editor-Stichfolge.dc.html','Stichfolge Stern 1',PA,'s1',4)
board('Stichfolge-Stern2.dc.html','Stichfolge Stern 2',PA,'s2',3)
info['gesamt']=board('Stichfolge-Gesamtbild.dc.html','Stichfolge Gesamtbild',PA,'gesamt')
board('Stichfolge-Schicht-aus.dc.html','Stichfolge Schicht aus',PM,'s1',4,off=('s2',))
print(info)
