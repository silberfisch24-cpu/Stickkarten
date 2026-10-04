import math, itertools
CX, CY, R0 = 54.5, 74.0, 35.0
def pol(x,y,a,r): return (x+r*math.cos(math.radians(a)), y+r*math.sin(math.radians(a)))
def pattern(n, e=0, w=45, l=.6, g=.3, st1=None, st2=None, aeste=True, R=R0):
    """st = dict(k=, level=) level: 1..e (e = Ring); ohne Äste: e = Anzahl Ebenen der Grundform."""
    E = max(e,1)
    step = R/E
    node = {}
    def ring(i,L):  # Punkt Strahl i, Ebene L (E = Außenring)
        return f'P{i}_{L}'
    for i in range(n):
        ang = -90+i*360/n
        for L in range(1,E+1): node[ring(i,L)] = pol(CX,CY,ang,L*step)
    used=set(); layers={'aeste':[], 'stern1':[], 'stern2':[]}
    if aeste:
        node['C']=(CX,CY)
        for i in range(n):
            ang=-90+i*360/n; prev='C'
            for L in range(1,E):
                layers['aeste'].append((prev,ring(i,L))); prev=ring(i,L)
                if L>=2:
                    for s in (-1,1):
                        root=node[ring(i,L)]; bl=step*l*(1+g*(L-1))
                        bid=f'B{i}_{L}_{s}'; node[bid]=pol(root[0],root[1],ang+s*w,bl)
                        layers['aeste'].append((ring(i,L),bid))
            layers['aeste'].append((prev,ring(i,E)))
    for key,st in (('stern1',st1),('stern2',st2)):
        if st:
            k=st['k']; lv=min(max(1,st.get('level',E)),E); m=n; seen=set()
            for j in range(m):
                a,b=j,(j+k)%m; kk=tuple(sorted((a,b)))
                if kk in seen: continue
                seen.add(kk); layers[key].append((ring(a,lv),ring(b,lv)))
    for ed in layers.values():
        for a,b in ed: used.add(a); used.add(b)
    stitches=sum(len(v) for v in layers.values())
    pts=[node[u] for u in used]
    mind=min(math.dist(a,b) for a,b in itertools.combinations(pts,2))
    return dict(node=node,layers=layers,used=used,stitches=stitches,mind=round(mind,1))
PRE = {
 ('flocke','leicht'):   dict(n=6, e=4, w=45, l=.6),
 ('flocke','mittel'):   dict(n=10,e=4, w=40, l=.55),
 ('flocke','aufwendig'):dict(n=14,e=3, w=35, l=.45),
 ('stern','leicht'):    dict(n=6, e=1, aeste=False, st1=dict(k=2)),
 ('stern','mittel'):    dict(n=10,e=2, aeste=False, st1=dict(k=3,level=2), st2=dict(k=2,level=1)),
 ('stern','aufwendig'): dict(n=14,e=2, aeste=False, st1=dict(k=5,level=2), st2=dict(k=3,level=1)),
 ('beides','leicht'):   dict(n=6, e=4, w=45, l=.6, st1=dict(k=2,level=2)),
 ('beides','mittel'):   dict(n=8, e=4, w=45, l=.6, st1=dict(k=3,level=2)),
 ('beides','aufwendig'):dict(n=8, e=5, w=45, l=.6, st1=dict(k=3,level=2), st2=dict(k=1,level=5)),
}
def make(stil,stufe,**over):
    p=dict(PRE[(stil,stufe)]); p.update(over); return pattern(**p)
if __name__=='__main__':
    for k in PRE:
        p=make(*k); print(k, 'Stiche',p['stitches'],'minAbstand',p['mind'],'OK' if p['mind']>=4.8 else 'knapp' if p['mind']>=3.2 else 'ZU ENG')
