import math, itertools
MIN=3.2; MOD=4.8
def build(n,e,w,l,g=0.3,R=36,sides=True,star1=True,star2=False,k1=3):
    pts={}; edges=0
    cx=cy=0
    def pol(x,y,a,r): return (x+r*math.cos(math.radians(a)), y+r*math.sin(math.radians(a)))
    for i in range(n): pts[f'R{i}']=pol(0,0,-90+i*360/n,R)
    pts['C']=(0,0); step=R/e
    for i in range(n):
        ang=-90+i*360/n
        for L in range(1,e):
            r=L*step; pts[f'A{i}L{L}']=pol(0,0,ang,r); edges+=1
            if sides and L>=2:
                for s in (-1,1):
                    bl=step*l*(1+g*(L-1)); root=pts[f'A{i}L{L}']
                    pts[f'A{i}L{L}b{s}']=pol(root[0],root[1],ang+s*w,bl); edges+=1
        edges+=1
    st=0
    for flag,k in ((star1,k1),(star2,1)):
        if flag:
            m=n; seen=set()
            for j in range(m):
                a,b=j,(j+k)%m
                key=tuple(sorted((a,b)))
                if key not in seen: seen.add(key); st+=1
    ids=list(pts); mind=1e9
    for a,b in itertools.combinations(ids,2):
        d=math.dist(pts[a],pts[b]); mind=min(mind,d)
    return edges+st, round(mind,1)
print('n e w l  -> Stiche(Äste+St1), minAbstand @R=36')
for n,e in [(6,3),(6,4),(8,4),(8,5),(10,4),(14,4),(14,5)]:
    for w,l in [(55,.7),(45,.6),(35,.5)]:
        s,m=build(n,e,w,l,star1=True)
        print(n,e,w,l,'->',s,m,'OK' if m>=MOD else ('knapp' if m>=MIN else 'ZU ENG'))
print('--- Aufwendig Äste n=14 (nur Äste, kein Stern)')
for e in (3,4):
    for w,l in [(35,.5),(30,.45),(25,.4),(20,.4)]:
        s,m=build(14,e,w,l,star1=False); print(14,e,w,l,'->',s,m,'OK' if m>=MOD else ('knapp' if m>=MIN else 'ZU ENG'))
print('--- ohne Seitenäste n=14')
for e in (4,5,6):
    s,m=build(14,e,0,0,sides=False,star1=False); print(14,e,'->',s,m)
print('--- Sterne allein: Stiche = m je Stern (k nicht diametral)')
for n in (6,10,14): print(n, n,'je Stern; zwei Sterne', 2*n)
print('--- n*e Grenze')
for n,e in [(11,4),(12,4),(12,3),(9,5),(8,5),(10,4)]:
    for w,l in [(45,.6),(35,.5),(30,.45)]:
        s,m=build(n,e,w,l,star1=False); print(n,e,w,l,'Äste allein',s,m,'OK' if m>=MOD else 'knapp' if m>=MIN else 'ZU ENG', ' n*e=',n*e)
