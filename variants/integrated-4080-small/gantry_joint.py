"""Fitted gantry-face substitution and end closure bridges, millimetres.

Existing monolithic bottom brackets are retained. The steel face replaces
both new aluminium guide strips; its welded rear lands preserve the12.7mm
datum stack and real8mm counterbores. No supplier rail pattern is invented.
"""
from pathlib import Path
from functools import lru_cache
import cadquery as cq

HERE=Path(__file__).resolve().parent
ENABLED=True
PREFIX='INT_GANTRY_JOINT_'
FACE_ID=PREFIX+'STEEL_RAIL_FACE'
REMOVED_IDS=('INT_GANTRY_GUIDE_BAR_LOWER','INT_GANTRY_GUIDE_BAR_UPPER')
CAP_X=(-25.,15.,1100.,1175.)
T=6.35
STEEL=(.30,.35,.39);HARD=(.38,.41,.44)

def bounds(s):
    b=s.BoundingBox();return[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]

def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def cyl(d,h,p,n=(0,1,0)):return cq.Solid.makeCylinder(d/2,h,cq.Vector(*p),cq.Vector(*n))

def _axes(shape,diameter):
    result=set()
    for f in shape.Faces():
        if f.geomType()!='CYLINDER':continue
        c=f._geomAdaptor().Cylinder();a=c.Axis();p=a.Location()
        if abs(a.Direction().Y())>.999 and abs(2*c.Radius()-diameter)<1e-5:
            result.add((round(p.X(),7),round(p.Z(),7)))
    return sorted(result)

def source_datums(parts):
    table={n:s for n,s,_ in parts}
    bars=[table[n]for n in REMOVED_IDS]
    bb=[bounds(s)for s in bars];beam=bounds(table['INT_GANTRY_4080_FRONT'])
    m8=sorted(set(q for s in bars for q in _axes(s,8.5)))
    m6=sorted(set(q for s in bars for q in _axes(s,6.)))
    couplers=[]
    for n,s,_ in parts:
        if n.startswith('INT_GANTRY_COMPRESSION_TUBE_'):
            b=bounds(s);couplers.append(((b[0]+b[3])/2,(b[2]+b[5])/2))
    assert len(m8)==8 and len(m6)==4,(m8,m6)
    assert abs(bb[0][1]-bb[1][1])<1e-7 and abs(bb[0][4]-bb[1][4])<1e-7
    assert abs((bb[0][4]-bb[0][1])-12.7)<1e-7
    return dict(x0=min(b[0]for b in bb),front_y=bb[0][1],beam_front_y=beam[1],
        lower_z=min(b[2]for b in bb),beam_top_z=beam[5],length=1200.,height=112.,
        retained_M8_axes=m8,retained_M6_axes=m6,coupler_access_axes=sorted(couplers))

def make_face(d):
    x,y,z=d['x0'],d['front_y'],d['lower_z']
    face=box(x,y,z,1200,T,112)
    lands=[]
    for cx,cz in d['retained_M8_axes']:
        lands.append(box(cx-12.5,y+T,cz-12.5,25,T,25))
    # Two source M6 pairs are10mm apart. One shared30x20 land per pair
    # gives a full edge seat, replacing the old upper strip's half bores.
    xs=sorted(set(cx for cx,cz in d['retained_M6_axes']))
    for xa,xb in((xs[0],xs[1]),(xs[2],xs[3])):
        cz=next(zz for xx,zz in d['retained_M6_axes']if xx==xa)
        lands.append(box((xa+xb)/2-15,y+T,cz-10,30,T,20))
    face=face.fuse(*lands).clean()
    for cx,cz in d['retained_M8_axes']:
        face=face.cut(cyl(8.5,14.7,(cx,y-1,cz)))
        face=face.cut(cyl(13.5,8,(cx,y,cz)))
    for cx,cz in d['retained_M6_axes']:
        face=face.cut(cyl(6,14.7,(cx,y-1,cz)))
    # The original horizontal coupler heads occupied the open gap between
    # guide strips. Preserve tool/head access through the new continuousweb.
    for cx,cz in d['coupler_access_axes']:
        face=face.cut(cyl(12.5,T+2,(cx,y-1,cz)))
    return face.clean()

def cap_parts(d):
    out=[];y,z=d['beam_front_y'],d['beam_top_z']
    for j,x in enumerate(CAP_X,1):
        cap=box(x-16,y,z,32,80,T)
        for yy in(y+20,y+60):cap=cap.cut(cyl(6.6,T+2,(x,yy,z-1),(0,0,1)))
        out.append((PREFIX+f'TOP_BRIDGE_{j}',cap.clean(),STEEL))
        for k,yy in enumerate((y+20,y+60),1):
            washer=cyl(12,1.6,(x,yy,z+T),(0,0,1)).cut(cyl(6.6,3.6,(x,yy,z+T-1),(0,0,1))).clean()
            out.append((PREFIX+f'TOP_WASHER_{j}_{k}',washer,HARD))
            # External grip only. The remaining12.05mm goes into the actual
            # purchased T-slot/nut; no fabricated die cavity is cut here.
            screw=cyl(6,7.95,(x,yy,z),(0,0,1)).fuse(cyl(10,6,(x,yy,z+T+1.6),(0,0,1))).clean()
            out.append((PREFIX+f'TOP_M6x20_EXTERNAL_GRIP_{j}_{k}',screw,HARD))
    return out

def apply_joint(parts):
    if not ENABLED or any(n==FACE_ID for n,_,_ in parts):return list(parts)
    d=source_datums(parts)
    return [p for p in parts if p[0]not in REMOVED_IDS]+[(FACE_ID,make_face(d),STEEL)]+cap_parts(d)

def metadata(d):
    return dict(replaces=list(REMOVED_IDS),front_datum_Y_mm=d['front_y'],
        preserved_face_stack_mm=12.7,face_X_Z_thickness_mm=[1200,112,T],
        rear_M8_lands=dict(quantity=8,finished_X_Z_thickness_mm=[25,25,T]),
        upper_M6_lands=dict(quantity=2,finished_X_Z_thickness_mm=[30,20,T]),
        retained_M8_axes_X_Z_mm=d['retained_M8_axes'],
        M8_counterbore_diameter_depth_mm=[13.5,8],M8_remaining_bearing_web_mm=4.7,
        retained_M6_axes_X_Z_mm=d['retained_M6_axes'],M6_tap='5.0pilot through;M6x1through12.7totalstack',
        existing_coupler_head_access=dict(diameter_mm=12.5,axes_X_Z_mm=d['coupler_access_axes'],
            end_axes_make_intentional_half_round_edge_notches=True),
        source_M6_edge_seat_repaired=True,minimum_M6_axis_to_upper_edge_mm=12,
        actual_HGR20_rail_M5_pattern_known=False,
        rail_process='Transferactualownedrails;4.2pilot/tapM5x.8through6.35steelafterpatternverification. No guessedpitch/phase.',
        top_bridges=dict(quantity=4,finished_X_Y_thickness_mm=[32,80,T],X_mm=list(CAP_X),
            hole_Y_from_front_mm=[20,60],hole_diameter_mm=6.6,
            screws='8M6x20socket+8M6washers+8actualdie-compatibleTnuts',
            external_grip_mm=7.95,internal_projection_mm=12.05,
            required_actual_cavity_depth_min_mm=13.05,
            actual_nut_thread_engagement_acceptance_mm=5.9),
        existing_bottom_brackets_retained=True,
        load_path='Front/rearbeamupperfaces -> topbridges/axialbolts -> oppositeupperface; originalmonolithicbottombrackets tiebothlowerfaces. Continuoussteelwebtiesrailrows;originalsleevecouplersretained.',
        weld_and_fit='Rearlandsattachedbeforefinalbore/counterbore/tapoperations;fixturestraight,alternatewelds;finishfrontdatumsandcoplanarbacklands. Hardshimsallowedforactualprofilefit;requireflatness/railalignmentinspection.',
        weld_detail='Minimum2mmfilletsonoppositesidesofeachrearland;actualmaterial/weldprocess/capacityunqualified.',
        rail_datum_flatness_acceptance_mm=.05,rear_land_coplanarity_acceptance_mm=.05,
        offcut_is_owned=False,offcut_parent_material_already_new_purchase=True,
        purchased_profile_section_or_Tnut_fit_verified=False,bolted_composite_action_qualified=False,
        whole_machine_rigidity_qualified=False,fabrication_release=False,operating_release=False)

def nest_offcuts(hanger_parts):
    """Allocate14 blanks in already-required NEW hanger sidebands.

    The old4datum22mmblanks stay explicitly present. All positions fit the
    original325.85mmminimum hangerheight, so a tallerstemneedsnoextraarea.
    """
    table={n:s for n,s,_ in hanger_parts};rows=[]
    for i in range(4):rows.append(dict(id=f'EXISTING_STOP_DATUM_{i+1}',hanger='L',u=2.,v=2.+26*i,w=22.,h=22.,new_allocation=False))
    for j,(u,v)in enumerate(((2.,110.),(2.,196.),(124.,2.),(124.,88.)),1):
        rows.append(dict(id=PREFIX+f'TOP_BRIDGE_{j}',hanger='L',u=u,v=v,w=34.,h=82.,new_allocation=True))
    for j in range(8):rows.append(dict(id=f'GJ_M8_REAR_LAND_{j+1}',hanger='R',u=2.,v=2.+31*j,w=27.,h=27.,new_allocation=True))
    for j in range(2):rows.append(dict(id=f'GJ_M6_UPPER_LAND_{j+1}',hanger='R',u=124.,v=2.+26*j,w=32.,h=22.,new_allocation=True))
    for r in rows:
        h=table['INT_PAN_FRONT_HEADER_HANGER_'+r['hanger']];b=bounds(h)
        local=h.translate(tuple(-q for q in b[:3]))
        raw=box(0,r['u'],r['v'],T,r['w'],r['h'])
        r['hanger_material_overlap_mm3']=abs(raw.intersect(local).Volume())
        r['within_original_minimum_blank']=r['u']>=2 and r['v']>=2 and r['u']+r['w']<=158 and r['v']+r['h']<=290.85
        r['passed']=r['within_original_minimum_blank']and r['hanger_material_overlap_mm3']<1e-5
    for i,r in enumerate(rows):
        for s in rows[i+1:]:
            if r['hanger']!=s['hanger']:continue
            # Rectangles need at least4mm separation in an axis; raw blanks
            # include1mm per edge cleanup for all newly allocated parts.
            assert(r['u']+r['w']+4<=s['u']or s['u']+s['w']+4<=r['u']or
                   r['v']+r['h']+4<=s['v']or s['v']+s['h']+4<=r['v']),(r,s)
    assert all(r['passed']for r in rows),rows
    return dict(parent_material='TwoalreadyrequiredNEW160x325.85x6.35steppedhangerblanks,or taller',
        actual_owned_material_credit=0,additional_raw_hanger_blank_purchase_quantity=0,
        allocation_count=14,existing_datum_allocations=4,placements=rows,
        new_blank_cleanup_each_edge_mm=1.,minimum_blank_separation_mm=4.,passed=True,
        scope='Sidebandsareallocatedonce;frontsteelfaceisaseparatenewlongstockpurchase. Machining/welds/hardwarearenotfree.')
