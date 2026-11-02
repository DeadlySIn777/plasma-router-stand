"""Integrated small-table frame and paired-4080 gantry, millimetres.

Reference geometry is a mounting envelope; profile section, core and slot
qualification still requires the purchased die. No original source is changed.
"""
from pathlib import Path
import hashlib,json,os,sys,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/'owned-z300-assessment'))
import candidate_motion_factory as C
import frame as X
S=C.S;cq=S.cq
FRAME_FRONT=-160.
FRAME_REAR=1600.
FRAME_LENGTH=FRAME_REAR-FRAME_FRONT
FRONT_POST_Y=-100.
FRONT_POST_SHIFT=-200.
SIDE_SHIFT=25.
GANTRY_RISE=40.
WORKING_Z=250.
COUPLER_X=(-25.,75.,225.,375.,525.,675.,825.,975.,1125.,1175.)

def side_of(n):
    for side,dx in(('L',-SIDE_SHIFT),('R',SIDE_SHIFT)):
        if re.search(r'(?:^|_)'+side+r'(?:_|$)',n):return side,dx
    return None,0.

def shift_y_side(parts):
    out=[]
    for n,s,c in parts:
        if n.startswith(('Y_','HMS_Y_','GANTRY_END_BRACKET_','GANTRY_WEB_BOLT_',
                         'GANTRY_UNDERSIDE_BOLT_','GANTRY_TNUT_','XR_SADDLE_','XR_STOP_')):
            _,dx=side_of(n)
            if dx:s=s.translate((dx,0,0))
        out.append((n,s,c))
    return out

def frame_parts():
    parts=[]
    for n,s,c in X.frame_parts():
        if n=='XR_EX_PAN_X_1'or re.fullmatch(r'XR_(?:PAN_BEARING_ANGLE|EX_DRY_ARM|DRY_ARM_ANGLE)_[LR]_1',n):
            continue
        side,dx=side_of(n);left=side=='L'
        if dx:s=s.translate((dx,0,0))
        if n in ('XR_EX_L_HEADER','XR_EX_R_HEADER'):
            b=S.bounds(s);s=X.bar(b[0],FRAME_FRONT,b[2]+GANTRY_RISE,'Y',FRAME_LENGTH)
        elif n.startswith(('XR_EX_L_POST_','XR_EX_R_POST_')):
            b=S.bounds(s);s=X.bar(b[0],b[1],b[2],'Z',b[5]-b[2]+GANTRY_RISE)
            if n.endswith('_1'):s=s.translate((0,FRONT_POST_SHIFT,0))
        elif n.startswith('XR_TOP_FISHPLATE_'):
            s=s.translate((0,0,GANTRY_RISE))
            if n.endswith('_1'):s=s.translate((0,FRONT_POST_SHIFT,0))
        elif n.startswith('XR_EX_PAN_X_'):
            b=S.bounds(s);s=X.bar(X.P.INNER_LEFT-SIDE_SHIFT,b[1],b[2],'X',X.P.CROSS_LENGTH+2*SIDE_SHIFT)
        elif n.startswith('XR_PAN_BEARING_ANGLE_'):
            i=int(n.rsplit('_',1)[1])-1
            s=X.bearing_angle(X.P.INNER_LEFT-SIDE_SHIFT if left else X.P.INNER_RIGHT+SIDE_SHIFT,
                X.P.POST_CENTRES_Y[i],X.P.PAN_BEARER_BOTTOM,80.,80.,left)
        elif n.startswith('XR_EX_DRY_ARM_'):
            i=int(n.rsplit('_',1)[1])-1
            arm_length=X.ARM_LENGTH+SIDE_SHIFT
            ax=X.P.INNER_LEFT-SIDE_SHIFT if left else X.P.INNER_RIGHT+SIDE_SHIFT-arm_length
            s=X.bar(ax,X.P.POST_CENTRES_Y[i]-40,X.ARM_BOTTOM-2.425,'X',arm_length,flat=True)
        elif n.startswith('XR_DRY_ARM_ANGLE_'):
            i=int(n.rsplit('_',1)[1])-1
            s=X.bearing_angle(X.P.INNER_LEFT-SIDE_SHIFT if left else X.P.INNER_RIGHT+SIDE_SHIFT,
                X.P.POST_CENTRES_Y[i],X.ARM_BOTTOM-2.425,40.,X.ARM_ANGLE_LEG,left)
        elif n.startswith('XR_SIDE_X_'):
            bay,j=map(int,n.split('_')[-2:])
            if bay==1:
                outer=X.P.LEFT_X-SIDE_SHIFT if left else X.P.RIGHT_X+40+SIDE_SHIFT
                sg=-1 if left else 1;offset=0 if j==1 else 3
                za,zb=(160.,900.)if j==1 else(900.,160.)
                xx=outer+sg*offset
                s=X.strap((xx,80.+FRONT_POST_SHIFT,za),(xx,610.,zb),(sg,0,0))
        elif n.startswith('XR_SIDE_SPACER_'):
            bay,k=map(int,n.split('_')[-2:])
            if bay==1 and k==1:s=s.translate((0,FRONT_POST_SHIFT,0))
        elif n.startswith(('XR_FOOT_PLATE_','XR_RATED_FOOT_','XR_FOOT_LOCKNUT_')):
            if re.search(r'_[LR]_1(?:_ALLOWANCE)?$',n):s=s.translate((0,FRONT_POST_SHIFT,0))
        elif n.startswith('XR_END_X_'):
            tag=n.split('_')[-2];j=int(n[-1]);yy=60+FRONT_POST_SHIFT if tag=='FRONT'else 1220
            normal=-1 if tag=='FRONT'else 1;lo,hi=(120,360)if tag=='FRONT'else(175,900)
            offset=0 if j==1 else 3;za,zb=(lo,hi)if j==1 else(hi,lo)
            s=X.strap((X.P.LEFT_X+20-SIDE_SHIFT,yy+normal*offset,za),
                (X.P.RIGHT_X+20+SIDE_SHIFT,yy+normal*offset,zb),(0,normal,0))
        elif n.startswith('XR_END_SPACER_'):
            s=s.translate((-SIDE_SHIFT if n.endswith('_1')else SIDE_SHIFT,0,0))
            if '_FRONT_'in n:s=s.translate((0,FRONT_POST_SHIFT,0))
        if n.startswith('XR_EX_DRY_ARM_'):
            i=int(n.rsplit('_',1)[1])
            if i in(1,3):
                xx=105. if left else 1045.
                # The full faces move40mm forward to clear the retained
                # long-Z lower end during tilt; rear bed bearer follows.
                # AtY1140 this access bore is open at the arm's front edge.
                yy=1140. if i==3 else X.P.POST_CENTRES_Y[i-1]
                s=s.cut(cq.Solid.makeCylinder(6.25,42,cq.Vector(xx,yy,X.ARM_BOTTOM-3.425),cq.Vector(0,0,1))).clean()
        parts.append((n,s,c))
    # A front pan bearer is hung from both continuous headers. Vertical steel
    # cheeks transfer gravity in their own plane; welded lower seats support
    # the beam directly. This avoids an unsupported 530mm wet-pan overhang
    # without putting a post or a low brace through the bed-assist corridor.
    for side in('L','R'):
        # The inner-face guide blocks sweepZ1051..1095. Keep the hanger
        # below1046 and spread four bolts along the lower header slot.
        plate=X.box(25.8,260.,720.15,6.35,80.,325.85).fuse(
            X.box(25.8,220.,1013.,6.35,160.,33.)).clean()
        for yy in(240.,280.,320.,360.):
            plate=plate.cut(cyl(6.6,8.35,(24.8,yy,1033.),(1,0,0)))
        for zz in(746.5,786.5):plate=plate.cut(cyl(8.5,8.35,(24.8,300.,zz),(1,0,0)))
        seat=X.box(32.15,260.,720.15,80.,80.,6.35)
        bracket=plate.fuse(seat).clean()
        if side=='R':bracket=bracket.mirror('YZ',(575,0,0))
        parts.append(('INT_PAN_FRONT_HEADER_HANGER_'+side,bracket,(.25,.31,.34)))
    beam=X.bar(32.15,280.,726.5,'X',1085.7)
    for x,d in((32.15,(1,0,0)),(1117.85,(-1,0,0))):
        for zz in(746.5,786.5):beam=beam.cut(cyl(8.,25.,(x,300.,zz),d))
    parts.append(('INT_EX_PAN_FRONT_300',beam.clean(),(.16,.20,.23)))
    return parts

def cyl(d,h,o,v=(0,1,0)):
    return cq.Solid.makeCylinder(d/2,h,cq.Vector(*o),cq.Vector(*v))

def paired_gantry(parts):
    old=next(s for n,s,c in parts if n=='GANTRY_8080')
    oldx,y,z,*_=S.bounds(old);x=oldx-SIDE_SHIFT;length=1200+2*SIDE_SHIFT
    negative=S.box(S.bounds(old)).cut(old)
    beams=[]
    for tag,yy in (('FRONT',y),('REAR',y+40)):
        s=X.bar(x,yy,z,'X',length).cut(negative)
        # Clearance allocations for the retained 22x13.7x5.9 M8 T-nut
        # envelope and11.3mm screw projection. These are minimum PURCHASED
        # T-slot interface requirements, not cuts to machine into a profile
        # or an assertion of the actual Amazon supplier die.
        for zz in(z+20,z+60):
            if tag=='FRONT':
                s=s.cut(X.box(x-1,y-1,zz-4.1,length+2,15.5,8.2))
                s=s.cut(X.box(x-1,y+4.22,zz-6.95,length+2,6.10,13.9))
        s=s.cut(X.box(x-1,yy+20-4.1,z-1,length+2,8.2,15.5))
        s=s.cut(X.box(x-1,yy+20-6.95,z+4.22,length+2,13.9,6.10))
        for xx in COUPLER_X:s=s.cut(cyl(10.1,82,(xx,y-1,z+40)))
        beams.append(('INT_GANTRY_4080_'+tag,s.clean(),(.46,.52,.55)))
    face=next(s for n,s,c in parts if n=='X_GUIDE_FACE')
    result=[p for p in parts if p[0]not in('GANTRY_8080','X_GUIDE_FACE')]+beams
    # Two40mm rail datum strips replace the full112mm face. All rail/beam
    # attachment holes and counterbores remain from the reference model;
    # the open centre gives the inter-profile couplers full access.
    for tag,z0 in(('LOWER',z-10),('UPPER',z+50)):
        strip=face.intersect(X.box(oldx-1,y-20,z0,1202,40,40)).clean()
        result.append(('INT_GANTRY_GUIDE_BAR_'+tag,strip,(.64,.70,.74)))
    hardware=(.34,.38,.41)
    for i,xx in enumerate(COUPLER_X,1):
        tube=cyl(10,80,(xx,y,z+40)).cut(cyl(7,82,(xx,y-1,z+40)))
        result.append((f'INT_GANTRY_COMPRESSION_TUBE_{i}',tube.clean(),hardware))
        for tag,yy in(('FRONT',y-1.6),('REAR',y+80)):
            w=cyl(12,1.6,(xx,yy,z+40)).cut(cyl(6.6,3.6,(xx,yy-1,z+40)))
            result.append((f'INT_GANTRY_M6_WASHER_{tag}_{i}',w.clean(),hardware))
        bolt=cyl(6,100,(xx,y-1.6,z+40)).fuse(cyl(10,6,(xx,y-7.6,z+40)))
        result.append((f'INT_GANTRY_M6x100_{i}',bolt.clean(),hardware))
        nut=cyl(11.6,5,(xx,y+81.6,z+40)).cut(cyl(6,7,(xx,y+80.6,z+40)))
        result.append((f'INT_GANTRY_M6_NUT_{i}',nut.clean(),hardware))
    return result

def configure_motion(parts,preserve_tool_ids=()):
    """Raise purchased fixed hardware; preserve actual tool working datums."""
    preserve=set(preserve_tool_ids)
    raised=[]
    for n,s,c in shift_y_side(parts):
        tool=S.cls(n)=='Y_X_Z_tool'or n in preserve
        if not tool or n=='ZBX80_OUTPUT_HOLD':s=s.translate((0,0,GANTRY_RISE))
        raised.append((n,s,c))
    return paired_gantry(raised)

def motion_parts(plasma=False,gantry_y=775.,head_x=575.,z_lift=100.):
    assert 0<=z_lift<=WORKING_Z
    ref=min(z_lift,200.)
    parts=C.motion_parts(plasma,gantry_y,head_x,ref)
    if z_lift>ref:
        parts=[(n,s.translate((0,0,z_lift-ref))if S.cls(n)=='Y_X_Z_tool'else s,c)for n,s,c in parts]
    return configure_motion(parts)

def motion_class(n):
    if n.startswith('INT_GANTRY_'):return 'Y_gantry_or_drive'
    return S.cls(n)

def frame_cutlist():
    p=X.P
    return ([dict(id=f'CHASSIS_POST_{i+1}',length_mm=q+GANTRY_RISE,section='4080')for i,q in enumerate([p.POST_LENGTH]*4+[p.POST_LENGTH-80]*2)]
        +[dict(id='CHASSIS_Y_'+s,length_mm=FRAME_LENGTH,section='4080')for s in('L','R')]
        +[dict(id='PAN_FRONT_300',length_mm=1085.7,section='4080')]
        +[dict(id=f'PAN_X_{i+1}',length_mm=p.CROSS_LENGTH+2*SIDE_SHIFT,section='4080')for i in(1,2)]
        +[dict(id='REAR_FOOTBASE_'+s,length_mm=300,section='4080')for s in('L','R')]
        +[dict(id=f'DRY_BED_ARM_{side}_{i}',length_mm=75.2+SIDE_SHIFT,section='4080')for side in('L','R')for i in(2,3)]
        +[dict(id='GANTRY_'+s,length_mm=1200+2*SIDE_SHIFT,section='4080')for s in('FRONT','REAR')])

def verify():
    out=HERE/'output';out.mkdir(exist_ok=True)
    parts=motion_parts();old=[]
    for n,s,c in shift_y_side(C.motion_parts(False,775,575,100)):
        if S.cls(n)!='Y_X_Z_tool'or n=='ZBX80_OUTPUT_HOLD':s=s.translate((0,0,GANTRY_RISE))
        old.append((n,s,c))
    lookup={n:s for n,s,_ in parts}
    new=[p for p in parts if p[0].startswith('INT_GANTRY_')]
    obstacles=[p for p in old if p[0]not in('GANTRY_8080','X_GUIDE_FACE')]
    pairs=S.exact_pairs(new,obstacles)
    # Every new gantry body travels with Y. Continuous relative X motion of
    # the head uses the established conservative material-cover proof.
    relative=[]
    for n,s,_ in new:
        for nf,sf,_ in obstacles:
            cls=S.cls(nf)
            span=(400 if cls in('Y_X_head','Y_X_Z_tool')else 0,
                  500 if cls=='stationary'else 0,
                  150 if cls=='Y_X_Z_tool'else 0)
            b=S.bounds(s);sb=[b[k]-span[k]for k in range(3)]+[b[k+3]+span[k]for k in range(3)]
            if not S.overlap(sb,S.bounds(sf)):continue
            if not any(span):
                volume=s.intersect(sf).Volume()
                q=dict(passed=volume<.05,method='Zero-relative-motion exact volume; designed tangency need not have positive distance.',overlap_mm3=volume)
            else:q=S.translation_cover_proof(s,sf,[-v for v in span],list(span))
            relative.append(dict(moving=n,obstacle=nf,**q))
    new_self=[]
    for i,(n,s,_)in enumerate(new):
        for nf,sf,_ in new[i+1:]:
            if not S.overlap(S.bounds(s),S.bounds(sf)):continue
            v=s.intersect(sf).Volume()
            if v>.05:new_self.append(dict(a=n,b=nf,overlap_mm3=v))
    tube_pairs=[]
    for i in range(1,len(COUPLER_X)+1):
        tube=lookup[f'INT_GANTRY_COMPRESSION_TUBE_{i}']
        tube_pairs.append(dict(station=i,beam_intersection_mm3=sum(tube.intersect(lookup['INT_GANTRY_4080_'+k]).Volume()for k in('FRONT','REAR')),
            bolt_intersection_mm3=tube.intersect(lookup[f'INT_GANTRY_M6x100_{i}']).Volume()))
    data=dict(study='PAIRED4080_GANTRY_AND_FRONT_PARKING_BAY_CHASSIS',
        frame_cutlist=frame_cutlist(),gantry_cross_section_mm=[80,80],gantry_4080_quantity=2,
        guide_datum_bars=dict(quantity=2,finished_mm=[1200,40,12.7],
            source='Two exact material subsets of the former full-width face; retained source holes/counterbores. New/unowned long stock unless evidenced.',
            new_supplier_HGR_holes='Transfer from the actual supplied1200mm rails; original phase/pitch is not silently changed.'),
        profile_interface_representation='Outer mounting model with minimum T-slot cavity clearance allocations. Not supplier die geometry. No machining of those purchased-profile cavity allocations is instructed.',
        required_Tnut_cavity=dict(opening_min_mm=8.2,nut_envelope_mm=[22,13.7,5.9],nut_inset_mm=4.32,screw_projection_mm=11.3),
        beam_section_properties_basis='Two independently qualified4080profiles. No parallel-axis/composite stiffness credit or torsional capacity is asserted for the unqualified coupler joints.',
        Y_side_translation_mm=dict(L=-SIDE_SHIFT,R=SIDE_SHIFT),
        gantry_and_header_rise_mm=GANTRY_RISE,
        owned_module_catalogue_stroke_mm=300,assessed_working_Z_mm=WORKING_Z,
        tool_working_Z_datums_changed=False,
        fixed_frame_inner_X_mm=[X.P.INNER_LEFT-SIDE_SHIFT,X.P.INNER_RIGHT+SIDE_SHIFT],
        fixed_frame_header_Y_mm=[FRAME_FRONT,FRAME_REAR],
        front_post_centre_Y_mm=FRONT_POST_Y,
        pan_bearer_centres_Y_mm=[300.,630.,1180.],
        front_pan_hangers=dict(quantity=2,stepped_plate_bounding_blank_mm=[160,325.85,6.35],
            plate_profile='80mm-wide vertical stem Y260..340,Z720.15..1046; integral160mm-wide top Y220..380,Z1013..1046',
            welded_seat_mm=[80,80,6.35],header_bolt_Y_mm=[240,280,320,360],header_bolt_Z_mm=1033,
            header_fixings='8 M6 profile-face sets total, actual compatible nuts/screw lengths and joint capacity held',
            beam_end_fixings='4 M8 end-core sets total; nominal thread-major CAD bores are not tap drills',
            load_path='Pan -> fitted shims -> 4080 beam -> welded bearing seats -> steel hanger cheeks -> continuous 4080 headers -> six posts.'),
        reason_for_front_bay='Moves the upright full bed ahead of the entire plasma-head working sweep while keeping changeover inside the permanent frame plan.',
        coupling=dict(count=len(COUPLER_X),axes_X_mm=list(COUPLER_X),centre_Z_from_beam_bottom_mm=40,
            through_bores_mm=10.1,compression_tubes_mm=[10,7,80],screws='M6x100',washers=2*len(COUPLER_X),nuts=len(COUPLER_X),
            qualification='Actual profile flat land, drilled webs, preload, sleeve length tolerance, slip, thread and load sharing require inspection/qualification.'),
        display_pairs=pairs,relative_continuous=relative,new_self_intersections=new_self,tube_checks=tube_pairs,
        frame_finished4080_length_mm=sum(p['length_mm']for p in frame_cutlist()),
        source_sha256={p.relative_to(ROOT).as_posix():S.sha(p)for p in[Path(__file__),Path(C.__file__),Path(S.__file__),Path(X.__file__)]},
        fabrication_release=False,physical_rigidity_qualified=False)
    data['passed']=not pairs['unexpected']and not new_self and all(q['passed']for q in relative)and all(q['beam_intersection_mm3']<1e-7 and q['bolt_intersection_mm3']<1e-7 for q in tube_pairs)
    (out/'frame-gantry-check.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(passed=data['passed'],display_hits=pairs['unexpected'],relative_count=len(relative),relative_failed=[(q['moving'],q['obstacle'])for q in relative if not q['passed']],frame_m=data['frame_finished4080_length_mm']/1000)),flush=True)
    return 0 if data['passed']else 1

if __name__=='__main__':
    try:code=verify()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
