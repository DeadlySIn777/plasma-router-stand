"""Coupled MITC4 particleboard shells, bending grillage, vertical seat ties. N-mm units."""
from pathlib import Path
import json,math,importlib.util
from Pynite import FEModel3D
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('sec',HERE.parents[1]/'budget-hybrid-600'/'simulation'/'structure.py')
sec=importlib.util.module_from_spec(spec);spec.loader.exec_module(sec)
T=1.8974
def edge_i(h=60.,root=12.):
    ss=[(T*h,h/2,T*h**3/12),(3.175*root,root/2,3.175*root**3/12),(4.05*T,T/2,4.05*T**3/12)]
    c=sum(a*z for a,z,i in ss)/sum(a for a,z,i in ss)
    return sum(i+a*(z-c)**2 for a,z,i in ss)
def edge_min_i():
    # Lower wall ends35mm above OUTSIDE floor. At a lip window only13mm of
    # its upper strip remains. The drain ports leave5mm of comb web.
    wall=35.-T
    ss=[(T*wall,wall/2,T*wall**3/12),
        (T*13,wall+12+6.5,T*13**3/12),
        (3.175*5,2.5,3.175*5**3/12),
        (4.05*T,T/2,4.05*T**3/12)]
    c=sum(a*z for a,z,i in ss)/sum(a for a,z,i in ss)
    return sum(i+a*(z-c)**2 for a,z,i in ss)
def axis_mesh(a,b,step,extras=()):
    n=math.ceil((b-a)/step)
    return sorted(set([round(a+(b-a)*i/n,6) for i in range(n+1)]+[float(x) for x in extras if a<=x<=b]))
def run(Ew=2500.,th=19.05,mesh=50.,middle_foot=False,case_indices=None,compression_contact=False,minimum_edge=False,pad_offset=0.):
    m=FEModel3D();m.add_material('steel',200000,200000/2.6,.3,0.);m.add_material('wood',Ew,Ew/2.5,.25,0.)
    chosen_edge_i=edge_min_i() if minimum_edge else edge_i()
    for name,I in [('slat',T*40**3/12),('edge',chosen_edge_i),('rhs',sec.tube_i(1.5,25.4,50.8))]:
        m.add_section(name,1000.,I,I,1e-6)
    nn={};axes={};springs=0;members=0
    def node(layer,x,y):
        key=(layer,round(x,6),round(y,6))
        if key not in nn:
            nm='N'+str(len(nn));nn[key]=nm
            m.add_node(nm,float(x),float(y),{'plate':1.,'slat':0.,'edge':-1.,'frame':-2.}[layer])
            m.def_support(nm,True,True,False,False,False,True)
            axes[nm]=set()
        return nn[key]
    def tie(a,b,compression_only=False):
        nonlocal springs
        springs+=1;m.add_spring('S'+str(springs),a,b,1e7,comp_only=compression_only)
    def line(layer,points,sect,axis):
        nonlocal members
        for a,b in zip(points,points[1:]):
            i=node(layer,*a);j=node(layer,*b)
            members+=1;m.add_member('M'+str(members),i,j,'steel',sect)
            axes[i].add(axis);axes[j].add(axis)
    Xedges=(165.,575.,985.);ystations=(100.,600.,1100.)
    slatys=[75+pad_offset+251*i+o for i in range(4) for o in (40.,210.)]
    # Mesh includes two patch footprints per panel, actual 25mm square pressure patches.
    patches=[]
    for panel in range(4):
        front=75+pad_offset+251*panel
        for x,y in ((365.,front+12.5),(365.,front+125.),(575.,front+125.),(785.,front+237.5)):
            patches.append((x,y))
    xs=axis_mesh(162.,988.,mesh,[*Xedges,163,987,365,785,*[x+d for x,y in patches for d in(-12.5,12.5)]])
    # Slat beams span the panel entire width; only actual slat ends163..987.
    sx=sorted(set([163.,*Xedges,987.,*[x for x in xs if 163<x<987]]))
    for y in slatys:line('slat',[(x,y) for x in sx],'slat','X')
    ey=sorted(set([62.,1079.,*ystations,*slatys]))
    for x in Xedges:line('edge',[(x,y) for y in ey],'rhs' if x==575 else'edge','Y')
    for y in slatys:
        for x in Xedges:tie(node('slat',x,y),node('edge',x,y))
    fx=sorted(set([33.4,1116.6,*Xedges]))
    for y in ystations:
        line('frame',[(x,y) for x in fx],'rhs','X')
        for x in Xedges:tie(node('edge',x,y),node('frame',x,y))
    # All four boards remain mechanically independent, with signed clamp seats.
    elements=[];wheres={}
    for panel in range(4):
        front=75+pad_offset+251*panel
        ys=axis_mesh(front,front+250.,mesh,[front+40,front+210,*[y+d for x,y in patches if front<=y<=front+250 for d in(-12.5,12.5)]])
        for xa,xb in zip(xs,xs[1:]):
            for ya,yb in zip(ys,ys[1:]):
                ids=[node('plate',x,y) for x,y in ((xa,ya),(xb,ya),(xb,yb),(xa,yb))]
                name='Q'+str(len(elements))
                m.add_quad(name,*ids,th,'wood')
                elements.append((name,(xa+xb)/2,(ya+yb)/2,(xb-xa)*(yb-ya),panel))
        for y in (front+40,front+210):
            for x in xs:
                if 163<=x<=987:
                    is_clamp=abs(x-365)<1e-5 or abs(x-785)<1e-5
                    tie(node('plate',x,y),node('slat',x,y),compression_contact and not is_clamp)
    # Fix torsion rotations only where a beam node has no bending member about that axis.
    for key,nm in nn.items():
        layer,x,y=key
        if layer!='plate':
            as_=axes[nm]
            m.def_support(nm,True,True,False,'Y' not in as_,'X' not in as_,True)
    for y in ystations:
        for x in (33.4,1116.6):
            nm=node('frame',x,y);m.def_support(nm,True,True,True,True,False,True)
    if middle_foot:m.def_support(node('frame',575.,600.),True,True,True,True,False,True)
    for case,(cx,cy) in enumerate(patches):
        if case_indices is not None and case not in case_indices:continue
        cname='P'+str(case);chosen=[r for r in elements if abs(r[1]-cx)<12.5+1e-5 and abs(r[2]-cy)<12.5+1e-5]
        # Element centroids exactly tile patch because patch edges are meshed.
        area=sum(r[3] for r in chosen)
        for name,x,y,a,panel in chosen:m.add_quad_surface_pressure(name,-100./area,cname)
        m.add_load_combo(cname,{cname:1.})
    print('Model built',len(m.nodes),'nodes',len(elements),'quads',len(m.load_combos),'load cases',flush=True)
    if compression_contact:
        m.analyze(log=False,check_stability=True,sparse=True,max_iter=50)
    else:
        m.analyze_linear(log=False,check_stability=True,sparse=True)
    results=[]
    for case,(cx,cy) in enumerate(patches):
        if case_indices is not None and case not in case_indices:continue
        cn='P'+str(case)
        woodnodes=[(nm,x,y) for (lay,x,y),nm in nn.items() if lay=='plate']
        w=max(woodnodes,key=lambda r:-m.nodes[r[0]].DZ[cn])
        # vertical equilibrium against actual six/seven floor contacts
        reactions=sum(n.RxnFZ[cn] for n in m.nodes.values())
        results.append({'patch_XY_mm':[cx,cy],'worst_wood_node_XY_mm':[w[1],w[2]],'max_workside_mm':-m.nodes[w[0]].DZ[cn],
                        'sum_RZ_N':reactions})
    return dict(Ewood_MPa=Ew,wood_mm=th,mesh_mm=mesh,middle_foot=middle_foot,
          node_count=len(m.nodes),quad_count=len(elements),steel_member_count=members,
          ideal_seat_ks_N_per_mm=1e7,compression_contact=compression_contact,minimum_edge=minimum_edge,pad_offset_mm=pad_offset,edge_composite_I_mm4=chosen_edge_i,cases=results,
          max_mm=max(r['max_workside_mm'] for r in results))
if __name__=='__main__':
    import sys
    args=sys.argv[1:]
    runid=args[0] if args else'base'
    ew=float(args[1]) if len(args)>1 else 2500.
    mesh=float(args[2]) if len(args)>2 else 50.
    foot=bool(int(args[3])) if len(args)>3 else False
    subset=[int(x) for x in args[4].split(',')] if len(args)>4 else None
    comp=bool(int(args[5])) if len(args)>5 else False
    thick=float(args[6]) if len(args)>6 else 19.05
    min_edge=bool(int(args[7])) if len(args)>7 else False
    offset=float(args[8]) if len(args)>8 else 0.
    out=run(ew,thick,mesh,foot,subset,comp,min_edge,offset)
    (HERE/('plate-'+runid+'.json')).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
