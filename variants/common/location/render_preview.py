"""Orthographic SVG preview from actual local dock B-rep tessellation."""
from pathlib import Path
import math,html,os,sys
import locator_dock as d
HERE=Path(__file__).resolve().parent
m,meta=d.build_dock()
def project(p):return (.78*p.x-.62*p.y, .28*p.x+.35*p.y-.94*p.z)
triangles=[]
for p in m.parts:
    verts,tris=p.shape.tessellate(.3,.15)
    for tri in tris:
        pts=[verts[i] for i in tri]
        q=[project(v) for v in pts]
        normal=(pts[1]-pts[0]).cross(pts[2]-pts[0])
        shade=.73+.27*abs(normal.z)/max(normal.Length,1e-9)
        col='#'+''.join(f'{int(255*c*shade):02x}' for c in p.color)
        triangles.append((sum(v.x+v.y+v.z*.2 for v in pts)/3,q,col))
allq=[q for _,ps,_ in triangles for q in ps]
xmin=min(q[0] for q in allq);xmax=max(q[0] for q in allq)
ymin=min(q[1] for q in allq);ymax=max(q[1] for q in allq)
scale=min(800/(xmax-xmin),340/(ymax-ymin))
def xy(q):return (80+(q[0]-xmin)*scale,150+(q[1]-ymin)*scale)
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="830" viewBox="0 0 1120 830">',
   '<rect width="1120" height="830" fill="#f2f5f8"/>',
   '<style>text{font-family:Arial,sans-serif;fill:#152b3a}.title{font-size:29px;font-weight:700}.sub{font-size:16px}.small{font-size:14px}.label{font-size:17px;font-weight:700}</style>',
   '<text x="45" y="55" class="title">Repeatable metal locator dock · component preview</text>',
   '<text x="45" y="86" class="sub">25 actual CAD solids. Supporting grid and metal carrier are integration requirements.</text>',
   '<text x="45" y="112" class="small">One round pin + one diamond pin locate XY. Separate seats and drawbolts carry table loads.</text>']
for _,q,col in sorted(triangles,key=lambda t:t[0]):
    pts=' '.join(f'{xy(p)[0]:.2f},{xy(p)[1]:.2f}' for p in q)
    s.append(f'<polygon points="{pts}" fill="{col}" stroke="{col}" stroke-width=".2"/>')
s += ['<rect x="45" y="525" width="1030" height="250" rx="10" fill="white"/>',
      '<text x="68" y="558" class="label">Interface section (dimensions in mm)</text>']
# Not a fabricated table; represent required carrier with dashed outline.
for x in (100,430):
    s.append(f'<rect x="{x}" y="652" width="160" height="48" fill="#556879"/>')
    s.append(f'<rect x="{x}" y="596" width="160" height="48" fill="#78868f"/>')
s += ['<rect x="169" y="580" width="22" height="72" fill="#bda13f"/>',
      '<rect x="160" y="596" width="40" height="48" fill="none" stroke="#a98323" stroke-width="6"/>',
      '<rect x="423" y="644" width="174" height="56" fill="#556879"/>',
      '<line x1="67" y1="700" x2="650" y2="700" stroke="#253b49" stroke-width="3"/>',
      '<text x="680" y="599" class="small">Pin top: base +30 (±0.1)</text>',
      '<text x="680" y="624" class="small">Receiver / steel landing: +14 to +26</text>',
      '<text x="680" y="649" class="small">Hard Z datum: +14; fixed pin block top: +12</text>',
      '<text x="680" y="674" class="small">2 mm separation keeps pin shoulder off Z datum</text>',
      '<text x="680" y="699" class="small">Grid top: 0; full support required beneath blocks</text>',
      '<text x="100" y="733" class="small">Locating interface</text>',
      '<text x="430" y="733" class="small">Separate load-bearing interface</text>',
      '<text x="45" y="808" class="small">Local geometric checks pass. Not an integrated bed, supplier-certified model, or measured repeatability guarantee.</text>',
      '</svg>']
(HERE/'output'/'locator-dock-preview.svg').write_text('\n'.join(s),encoding='utf8')
print('Wrote locator-dock-preview.svg',flush=True)
sys.stdout.flush();os._exit(0)
