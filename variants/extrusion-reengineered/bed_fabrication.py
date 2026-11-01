"""Manufacturable XR2 nominal parts, mm DXFs and machining-operation tables."""
from pathlib import Path
from math import sqrt,atan,degrees,pi
import hashlib,json,csv,os,sys
import cadquery as cq
import ezdxf
import params as P
import bed as B
HERE=Path(__file__).resolve().parent
OUT=HERE/'review';FAB=OUT/'fabrication'
OP_ASSETS=set()

def flat_rect(w,h):return B.box(0,0,0,w,h,1)

def topface(s):
    ff=[f for f in s.Faces() if f.normalAt().z>.99]
    return max(ff,key=lambda f:f.Area()).translate((0,0,-max(f.Center().z for f in ff)))

def export_face(name,face,thick,qty,material,rows):
    path=FAB/(name+'.dxf');cq.exporters.exportDXF(face,str(path),doc_units=4)
    doc=ezdxf.readfile(path);bb=face.BoundingBox()
    assert doc.units==4
    assert face.isValid() and face.Area()>0
    # Import/extrude profile proves that holes and perimeter form a real flat part.
    wp=cq.importers.importDXF(str(path));solid=wp.wires().toPending().extrude(thick).val()
    error=abs(solid.Volume()-face.Area()*thick)
    assert solid.isValid() and error<max(.05,face.Area()*thick*1e-6),(name,error)
    rows.append({'id':name,'quantity':qty,'material':material,'flat_length_mm':bb.xlen,
      'flat_width_mm':bb.ylen,'thickness_mm':thick,'area_mm2':face.Area(),
      'dxf':str(path.relative_to(HERE)),'units':'mm','roundtrip_volume_error_mm3':error,
      'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})

def rectangle(name,w,h,t,qty,mat,rows,holes=()):
    s=flat_rect(w,h)
    for x,y,r in holes:s=s.cut(B.cyl(x,y,-.1,r,1.2))
    export_face(name,topface(s),t,qty,mat,rows)

def projected_face(shape,normal_axis,origin):
    fs=[]
    for f in shape.Faces():
        n=f.normalAt()
        if abs(getattr(n,normal_axis))>.999:fs.append(f)
    f=max(fs,key=lambda q:q.Area());ox,oy,oz=origin
    if normal_axis=='x':return f.translate((-f.Center().x,-oy,-oz)).rotate((0,0,0),(0,0,1),-90).rotate((0,0,0),(1,0,0),-90)
    if normal_axis=='y':return f.translate((-ox,-f.Center().y,-oz)).rotate((0,0,0),(1,0,0),-90)
    return f.translate((-ox,-oy,-f.Center().z))


def ops_dxf(path,ops):
    d=ezdxf.new();d.units=4;m=d.modelspace()
    for op in ops:
        layer=op['layer']
        if layer not in d.layers:d.layers.new(layer)
        if 'rounded_rect' in op:
            x,y,w,h,r=op['rounded_rect'];b=2**.5-1
            m.add_lwpolyline([(x+r,y,0),(x+w-r,y,b),(x+w,y+r,0),(x+w,y+h-r,b),(x+w-r,y+h,0),(x+r,y+h,b),(x,y+h-r,0),(x,y+r,b)],format='xyb',close=True,dxfattribs={'layer':layer})
        elif 'rect' in op:
            x,y,w,h=op['rect'];m.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],close=True,dxfattribs={'layer':layer})
        elif 'circle' in op:
            x,y,r=op['circle'];m.add_circle((x,y),r,dxfattribs={'layer':layer})
    d.saveas(path)
    OP_ASSETS.add(Path(path))

def run():
    FAB.mkdir(exist_ok=True,parents=True);rows=[];operations=[]
    sources={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('params.py','bed.py','bed_fabrication.py')}
    x0=P.PANEL_X
    # Pre-drillstock skins:holes/pockets are separate named operations to prevent
    # an ambiguousDXF from treating a blindpocket as a throughcut.
    for top in (False,True):
        tag='TOP_SKIN' if top else'BOTTOM_SKIN';s=flat_rect(P.PANEL_WIDTH,P.PANEL_LENGTH)
        for x in (132.,994.):s=s.cut(B.box(x-x0,82,-.1,24,40,1.2))
        for x in (117.5,1032.5):s=s.cut(B.cyl(x-x0,128.5,-.1,5.1,1.2))
        for cy in B.TRACK_CENTRES:
            for x in B.TRACK_BOLTS:s=s.cut(B.cyl(x-x0,cy,-.1,4.1,1.2))
        export_face(tag,topface(s),12.7,4,'structural_plywood',rows)
        ops=[]
        if top:
            for y in B.TRACK_CENTRES:ops.append({'layer':'TOP_POCKET_6p35','rect':[B.TRACK_X0-.1-x0,y-9.6,826.2,19.2],'depth_mm':6.35,'face':'TOP'})
        else:
            for y in B.TRACK_CENTRES:
                for x in B.TRACK_BOLTS:ops.append({'layer':'BOTTOM_POCKET_9p525','rect':[x-x0-10.1,y-10.1,20.2,20.2],'depth_mm':9.525,'face':'BOTTOM'})
            for x in (117.5,1032.5):
                for y in (40.,217.):
                    ops.append({'layer':'BOTTOM_PAD_POCKET_3p325','rect':[x-x0-8.1,y-12.6,16.2,25.2],'depth_mm':3.325,'face':'BOTTOM'})
                    for dx,dy in ((-4.,-7.),(4.,7.)):
                        ops.append({'layer':'BOTTOM_PILOT_2p2_DEPTH10','circle':[x-x0+dx,y+dy,1.1],'depth_mm':10.,'face':'BOTTOM'})
        ops_dxf(str(FAB/(tag+'_OPERATIONS.dxf')),ops);operations.append({'part':tag,'operations':ops})
    for i in range(4):
        front=P.PANEL_Y0+i*P.PANEL_PITCH;ya=max(28.5,B.SKIM[2]-front);yb=min(228.5,B.SKIM[3]-front);height=yb-ya
        holes=[(x-190,y,1.75) for x in (205.,445.,705.,945.) for y in (20.,height-20)]
        rectangle(f'WEAR_PAD_PANEL_{i+1}',770,height,6.35,1,'MDF_finished_from_9p525',rows,holes)
        op=[];topop=[]
        for x in (205.,445.,705.,945.):
            for y in (20.,height-20):
                op.append({'layer':'TOP_COUNTERBORE_D8_DEPTH2','circle':[x-190,y,4.],'depth_mm':2.})
                topop.append({'layer':'TOP_PILOT_D2p5_DEPTH11p75','circle':[x-109,y+ya,1.25],'depth_mm':11.75})
        ops_dxf(str(FAB/f'WEAR_PAD_PANEL_{i+1}_OPERATIONS.dxf'),op)
        ops_dxf(str(FAB/f'TOP_SKIN_PANEL_{i+1}_PILOTS.dxf'),topop)
        operations.append({'part':f'WEAR_PAD_PANEL_{i+1}','operations':op,
           'counterbore_cone':'Below2mmcounterbore,6.8to3.5countersink1.65deep;headtop2mmbelowfinishedsurface. Use3.5x16flatwoodscrews,pilot2.5,totaldepth11.75inply;finishthicknessbeforedrilling.'})
    # Interlockingeggcrate profiles:9.10wide mating slots, oppositehalfdepths.
    for j,cy in enumerate(B.WEB_CENTRES,1):
        s=flat_rect(P.PANEL_WIDTH,B.CORE)
        for cx in B.CROSS_X_CENTRES:
            s=s.cut(B.box(cx-x0-B.LAP_SLOT_WIDTH/2,B.CORE-B.LAP_NOTCH_DEPTH,-.1,B.LAP_SLOT_WIDTH,B.LAP_NOTCH_DEPTH+.1,1.2))
        if j==1:
            for x in (250.,820.):s=s.cut(B.box(x-x0,22-B.BOTTOM,-.1,80,20,1.2))
        export_face(f'LONG_WEB_{j:02}_PROFILE',topface(s),9.,4,'structural_plywood',rows)
        bores=[]
        if cy in B.TRACK_CENTRES:bores=[{'x_mm':x-x0,'y_from_web_face_mm':4.5,'diameter_mm':8.2,'axis':'Z','depth_mm':B.CORE} for x in B.TRACK_BOLTS]
        if cy==128.5:bores=[{'x_mm':x-x0,'y_from_web_face_mm':4.5,'diameter_mm':10.2,'axis':'Z','depth_mm':B.CORE} for x in (117.5,1032.5)]
        operations.append({'part':f'LONG_WEB_{j:02}','edge_bores_before_closure':bores,
           'process':'Fixturebetween sacrificial cheekplates;prepareverticalbores andtrialtube fit beforebondingtopskin. Actualfinishedsegments are separateSTEPsolids.'})
    for j,cx in enumerate(B.CROSS_X_CENTRES,1):
        s=flat_rect(P.PANEL_LENGTH,B.CORE)
        for cy in B.WEB_CENTRES:s=s.cut(B.box(cy-B.LAP_SLOT_WIDTH/2,-.1,-.1,B.LAP_SLOT_WIDTH,B.LAP_NOTCH_DEPTH+.1,1.2))
        export_face(f'CROSS_WEB_{j:02}_PROFILE',topface(s),9.,4,'structural_plywood',rows)
    pan=B.pan_parts()
    for n,s,c in pan:
        if n=='HOT_PAN_PLAIN14GA_FLOOR':
            face=max((f for f in s.Faces() if f.normalAt().z>.99),key=lambda f:f.Area())
            face=face.translate((-P.PAN_X0,-P.PAN_Y0,-P.PAN_FLOOR_FRONT)).rotate((0,0,0),(1,0,0),-degrees(atan(P.PAN_SLOPE)))
            export_face('PAN_FLOOR',face,1.9,1,'plain_mild_steel',rows)
        elif n.startswith('HOT_PAN_WALL_'):
            export_face(n,projected_face(s,'x',(0,P.PAN_Y0,P.PAN_FLOOR_FRONT)),1.9,1,'plain_mild_steel',rows)
        elif n in ('HOT_PAN_FRONT','HOT_PAN_REAR'):
            export_face(n,projected_face(s,'y',(P.PAN_X0+B.PAN_T,0,s.BoundingBox().zmin)),1.9,1,'plain_mild_steel',rows)
        elif n.startswith('HOT_COMB_'):
            export_face(n,projected_face(s,'x',(0,P.PAN_Y0+10,P.PAN_FLOOR_FRONT)),3.175,1,'plain_mild_steel',rows)
        elif n.startswith('HOT_SLAT_01'):
            export_face('SLAT_880_CENTRE_KEY',projected_face(s,'y',(B.SLAT_X0,0,P.SLAT_TOP-40)),1.9,8,'plain_mild_steel',rows)
    for name,part,col in B.pan_retainers():
        if name.startswith('PAN_WELDED_EAR_'):
            export_face(name,projected_face(part,'z',(part.BoundingBox().xmin,part.BoundingBox().ymin,0)),1.9,1,'plain_mild_steel',rows)
        elif name=='PAN_KEEPER_FL_CAP_1MM_UPLIFT':
            export_face('PAN_KEEPER_CAP',projected_face(part,'z',(part.BoundingBox().xmin,part.BoundingBox().ymin,0)),3.,4,'Al_new_stock',rows)
    # Weldedwetpan/spout/collector/gutter use flatbutt-jointed plates, ZERO bends.
    for args in [('OVERFLOW_SPOUT_TOP_BOTTOM',34,44,1.9,2),('OVERFLOW_SPOUT_SIDES',34,8.2,1.9,2),
        ('OVERFLOW_COLLECTOR_BACK',44,409,1.9,1),('OVERFLOW_COLLECTOR_SIDES',18.1,409,1.9,2),
        ('OVERFLOW_COLLECTOR_FLOOR',18.1,40.2,1.9,1),('OVERFLOW_GUTTER_FLOOR',sqrt(176**2+3**2),40.2,1.9,1),
        ('OVERFLOW_DEFLECTOR',53.9,44,1.9,1)]:rectangle(*args,'plain_mild_steel',rows)
    poly=[(0,0),(176,3),(176,15),(0,12)]
    f=cq.Face.makeFromWires(cq.Wire.makePolygon([cq.Vector(x,y,0) for x,y in poly]+[cq.Vector(*poly[0],0)]))
    export_face('OVERFLOW_GUTTER_SIDES',f,1.9,2,'plain_mild_steel',rows)
    # Formedbracket:neutral-axisdevelopment and nominalthroughholecoordinate.
    bendR,K,t=2.,.4,1.9;BA=pi/2*(bendR+K*t);flat=53+20-2*(bendR+t)+BA
    rectangle('OVERFLOW_SUPPORT_BRACKET_FLAT',flat,12,t,2,'plain_mild_steel',rows,
       holes=[(11.1,6.,2.2)])
    operations.append({'part':'OVERFLOW_SUPPORT_BRACKET_FLAT','bend':{
       'angle_deg':90,'inside_radius_mm':bendR,'K_factor':K,'bend_allowance_mm':BA,
       'outer_legs_mm':[20,53],'flat_length_mm':flat,'first_tangent_from_short_edge_mm':20-(bendR+t),
       'bend_centreline_from_short_edge_mm':20-(bendR+t)+BA/2,
       'note':'Cut/drillflat,form90deg overR2mandrel. CouponcalibrationadjustsKforreceivedsteel;nominalCADhasactualR2/R3.9bend.'}})
    # Servicehatchbaseplate:two simple rearreliefs for knuckles/pinheads.
    hs=flat_rect(620,290)
    for cx in B.HATCH_PIN_X:
        hs=hs.cut(B.box(cx-10.2-265,1125.8-840,-.1,8.4,4.3,1.2))
        hs=hs.cut(B.box(cx-15.2-265,1126.2-840,-.1,3.4,3.9,1.2))
    for x in (300.,850.):hs=hs.cut(B.cyl(x-265,5.,-.1,2.2,1.2))
    export_face('SERVICE_HATCH_COVER',topface(hs),1.9,1,'plain_mild_steel',rows)
    operations.append({'part':'SERVICE_HATCH_COVER','underside_counterbores':[{'x_mm':35.,'y_mm':5.,'diameter_mm':10.2,'depth_mm':.8},{'x_mm':585.,'y_mm':5.,'diameter_mm':10.2,'depth_mm':.8}],
       'weld':'Twomovingknuckles andindexears;drill/ream4.4mmhingeaxis afterwelding;preservepinheadclearances.'})
    leaf=flat_rect(40,18.5)
    for x in (6.,34.):leaf=leaf.cut(B.cyl(x,8.5,-.1,2.2,1.2))
    for x,y,w,h in ((21.8,-.1,8.4,2.8),(20.4,-1.5,2.3,15.2),(4.8,-.1,3.4,2.4)):
        leaf=leaf.cut(B.box(x,y,-.1,w,h,1.2))
    export_face('HATCH_FIXED_HINGE_LEAF_FINISHED',topface(leaf),1.9,2,'plain_mild_steel',rows)
    ear=B.cyl(5,5,0,5,1).cut(B.cyl(5,5,-.1,2.2,1.2))
    export_face('HATCH_FIXED_INDEX_EAR',topface(ear),1.9,2,'plain_mild_steel',rows)
    ear=B.cyl(5,13,0,5,1).fuse(B.box(2.5,0,0,5,13,1))
    for x,y in ((7.,3.),(5.,13.)):ear=ear.cut(B.cyl(x,y,-.1,2.2,1.2))
    export_face('HATCH_MOVING_INDEX_EAR',topface(ear),1.9,2,'plain_mild_steel',rows)
    operations.append({'part':'HATCH_FIXED_HINGE_LEAF_FINISHED','finish':'FlatDXFincludesallreliefs;weld8ODknuckle andfixedindexear;axisdrill4.4throughafterweld.'})
    operations.append({'part':'HATCH_KNUCKLES','stock':'OD8roundsteel4piecesx8long;axisdrill4.4mm','pins':'2mainclevispins4x30envelope,2indexpins4x9envelope;receivedhardwaremustmatch.'})
    for front in (True,False):
        tag='F' if front else'R';holes=[]
        if front:holes=[(81.,10.,3.1),(631.,10.,3.1)]
        else:
            for cx in B.HATCH_PIN_X:
                for x in (cx-14,cx+14):holes.append((x-219,15.,2.2))
        rectangle('HATCH_CROSS_ANGLE_'+tag+'_TOP_VIEW',712,25,3,1,'purchased_Al_angle_operation_view',rows,holes)
        operations.append({'part':'HATCH_CROSS_ANGLE_'+tag,'stock':'25x25x3AlangleL712,notaflatstrip','cope':'Removeverticalweblast25mmeachend;retain25wideupperflange. Verticallegextends22mmbelowflange.'})
    for front in (True,False):
        holes=[(4.,5.5,1.1),(12.,19.5,1.1)]
        if front:holes.append((8.,12.5,3.02))
        rectangle('DOCK_PAD_'+('ROUND_BORE' if front else'PLAIN'),16,25,3.175,8,'Al_owned_nested',rows,holes)
    operations.append({'part':'DOCK_PADS','underside':'Countersink2holes5.6diameter x1.7deep;3x10flatwoodscrews;0.15hardepoxybeddingbridges3.325pocketdepthtopad3.175.'})
    washer=B.cyl(9,9,0,9,1).cut(B.cyl(9,9,-.1,3.3,1.2)).intersect(B.box(1.5,0,-.1,17,18,1.2))
    export_face('M6_D_WASHER_FINISH_VIEW',topface(washer),1.6,8,'purchased_steel_washer',rows)
    rows[-1]['stock_form']='purchased_washer'
    rectangle('HATCH_RIM_FOOT_25x25',25,25,2,4,'Al_new_stock',rows)
    for r in rows:
        if r['material']=='purchased_Al_angle_operation_view':r['stock_form']='purchased_angle'
    lidops=[{'layer':'REFERENCE_OUTLINE_DO_NOT_CUT','rect':[0,0,712,470]},
            {'layer':'CUT_HATCH','rounded_rect':[56,150,600,270,3]},
            {'layer':'CUT_DRAIN_PORT','circle':[181,100,25]},
            {'layer':'CUT_OVERFLOW_PORT','rect':[661,175,40,50]},
            {'layer':'OPEN_VENT','circle':[681,300,12.5]}]
    for yy in (135.,425.):
        for xx in (0.,687.):lidops.append({'layer':'CUT_RIM_FEET_CLEARANCE','rect':[xx-.1,yy-.1,25.2,25.2]})
        wy=yy if yy==135. else yy+22
        lidops.append({'layer':'CUT_ANGLE_WEB_SLOT','rect':[24.9,wy-.1,662.2,3.2]})
    for cx in B.HATCH_PIN_X:
        for x in (cx-14,cx+14):lidops.append({'layer':'DRILL_SLEEVE_6p2','circle':[x-219,440,3.1]})
    for x in (300.,850.):lidops.append({'layer':'RIVNUT_TAIL_RELIEF_8p2','circle':[x-219,145,4.1]})
    ops_dxf(str(FAB/'RECEIVER_LID_MODIFICATION_TEMPLATE.dxf'),lidops)
    operations.append({'part':'RECEIVER_LID_MODIFICATION_TEMPLATE','process':'Registertoactualtoterim;outer712x470isREFERENCEONLY. Transferopening/portsafterconfirmingmoldedribs,hingesandcarrierland.0.1mmclearancearoundmetalsaddles.'})
    cabinet=B.storage_parts(False)
    for n,part,col in cabinet:
        if n in ('COLD_CASE_FLOOR_NOT_A_WORKBED','COLD_CASE_ROOF','COLD_CASE_SECONDARY_STEEL_ROOF_AIRGAP5_THERMAL_HOLD'):
            material='plain_mild_steel' if 'SECONDARY' in n else'Al_new_sheet'
            t=1.9 if 'SECONDARY' in n else.8
            export_face(n,projected_face(part,'z',(part.BoundingBox().xmin,part.BoundingBox().ymin,0)),t,1,material,rows)
        elif n.startswith('COLD_CASE_SIDE_'):
            export_face(n,projected_face(part,'x',(0,350,378.8)),.8,1,'Al_new_sheet',rows)
        elif n=='COLD_CASE_BACK':
            export_face(n,projected_face(part,'y',(104,0,378.8)),.8,1,'Al_new_sheet',rows)
    rectangle('CABINET_LIFTOFF_FRONT_COVER',956,332,.8,1,'Al_new_sheet',rows,
       holes=[(x,z,2.2) for x in (6.,950.) for z in (32.,312.)])
    rectangle('CABINET_COVER_THREADED_TAB',12,20,6,4,'Al_new_stock',rows,holes=[(6.,10.,1.65)])
    operations.append({'part':'CABINET_COVER_THREADED_TAB','process':'Matchcoperearface3x3fullheightaroundcornerangle;weldtabfirst,thendrill3.3andtapM4x.7blind6mm. FourM4x8bolts+1.6washersgive5.6mmengagement.'})
    rectangle('CABINET_ROOF_THREADED_BLOCK',12,12,6,4,'Al_new_stock',rows,holes=[(6.,6.,1.25)])
    rectangle('CABINET_FLOOR_LEDGE',20,20,3,4,'Al_new_stock',rows,holes=[(10.,10.,1.25)])
    operations.append({'part':'CABINET_FLOOR_LEDGE_AND_ROOF_BLOCK','process':'Weldcornerattachmentswithfacecontact,drill2.5andtapM3. FloorM3x6/primaryroofM3x8,allwith.8washers. Backskinlapuses8M4blindrivets3.8mmgrip.'})
    stands=B.cabinet_cover_blocks(True)
    sa=cq.Assembly(name='COVER_PARKING_STANDS')
    for n,q,c in stands:sa.add(q,name=n)
    sa.save(str(FAB/'COVER_PARKING_STANDS.step'))
    export_face('COVER_PARKING_BLOCK_SIDE_PROFILE',projected_face(stands[0][1],'x',(0,0,0)),30.,2,'laminated_plywood_stock',rows)
    operations.append({'part':'COVER_PARKING_STANDS','stock':'2blocks30x60x20finished;laminate2x12.7plythenfaceto20','slot':'1.2wide,8degreesfromvertical,blindbottom5mm;sourceSTEPisfinishedgeometry.','wood_offcut_nest_mm':[[1900+34*i,2,30,60] for i in range(4)],'nest_note':'Fourraw12.7layersfitbeyondtheeight932x257skins(twoXends1870);noadditionalfullsheetrequired.'})
    # Independentmanufacturingrebuild:readtheDXFslapprofiles,orientintoXYZ,
    # andapplythedeclaredcommoncorebores/frontpulloperations. ComparetofinishedCAD.
    coretools=[B.cyl(x,y,B.BOTTOM-.1,4.1,B.CORE+.2) for x in B.TRACK_BOLTS for y in B.TRACK_CENTRES]
    coretools += [B.cyl(x,128.5,B.BOTTOM-.1,5.1,B.CORE+.2) for x in (117.5,1032.5)]
    coretools += [B.box(x,-.1,22,80,14.1,20) for x in (250.,820.)]
    coretool=B.fuse(coretools);rebuild=[]
    sourceparts=B.cassette_local_parts(0)
    for group,centres in (('LONG',B.WEB_CENTRES),('CROSS',B.CROSS_X_CENTRES)):
        for j,centre in enumerate(centres,1):
            raw=cq.importers.importDXF(str(FAB/f'{group}_WEB_{j:02}_PROFILE.dxf')).wires().toPending().extrude(9.).val()
            if group=='LONG':
                raw=raw.rotate((0,0,0),(1,0,0),90).translate((109,centre+4.5,B.BOTTOM))
            else:
                raw=raw.rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),90).translate((centre-4.5,0,B.BOTTOM))
            finished=raw.cut(coretool)
            targets=[q[1] for q in sourceparts if q[0].startswith(f'CAS1_{group}_WEB_{j:02}_')]
            target=targets[0] if len(targets)==1 else B.fuse(targets)
            error=finished.cut(target).Volume()+target.cut(finished).Volume()
            rebuild.append({'part':f'{group}_WEB_{j:02}','symmetric_difference_mm3':error,'passed':error<.1})
    operations.append({'part':'CORE_ASSEMBLY_COMMON_OPERATIONS','origin_world_mm':[109,0,B.BOTTOM],
      'through_vertical_bores':[{'x_mm':x-109,'y_mm':y,'diameter_mm':8.2,'depth_mm':B.CORE} for x in B.TRACK_BOLTS for y in B.TRACK_CENTRES]+[{'x_mm':x-109,'y_mm':128.5,'diameter_mm':10.2,'depth_mm':B.CORE} for x in (117.5,1032.5)],
      'front_pull_pockets':[{'x_mm':x-109,'z_mm':22,'width_mm':80,'height_mm':20,'axis':'positiveY','depth_mm':14} for x in (250.,820.)],
      'process':'Fixturecoreinassembledalignment,preparecommonbores/pullpocketsbeforeclosingtopskin;thisincludespartialbores/pocketsinend/crosswalls. Cleanandtrialfitallmetalinsertsthenbondskins.'})
    ops_dxf(str(FAB/'CORE_FRONT_PULLS_OPERATIONS.dxf'),[{'layer':'REFERENCE_BOX','rect':[0,0,932,B.BOX_H]},
       *[{'layer':'FRONT_POCKET_POSY_DEPTH14','rect':[x-109,22,80,20],'depth_mm':14} for x in (250.,820.)]])
    # Exactfinishedwoodassemblypartsareseparateone-solidSTEPcomponents.
    wood=[(n,s,c) for n,s,c in B.cassette_local_parts(0) if c==B.PLY]
    a=cq.Assembly(name=P.REVISION+'_CASSETTE_JOINERY')
    for n,s,c in wood:a.add(s,name=n,color=cq.Color(*c))
    a.save(str(FAB/'CASSETTE_JOINERY.step'))
    imported=cq.importers.importStep(str(FAB/'CASSETTE_JOINERY.step')).val()
    assert imported.isValid() and len(imported.Solids())==len(wood)
    from build import clashes
    joinery=clashes(wood,wood,True)
    result={'revision':P.REVISION,'release':False,'units':'mm','flat_parts':rows,
      'steel_blanks':[r for r in rows if r['material']=='plain_mild_steel'],
      'operations':operations,'DXF_secondary_operation_rebuild_checks':rebuild,'joinery':{'STEP_sha256':hashlib.sha256((FAB/'CASSETTE_JOINERY.step').read_bytes()).hexdigest(),'STEP_roundtrip_valid':imported.isValid(),'STEP_roundtrip_solids':len(imported.Solids()),'wood_component_count':len(wood),'all_single_valid_solids':all(s.isValid() and len(s.Solids())==1 for n,s,c in wood),
       'raw_exact_intersections':joinery,'lap_slot_width_mm':B.LAP_SLOT_WIDTH,'notch_depth_mm':B.LAP_NOTCH_DEPTH,
       'nominal_joint_clearance_mm':B.JOINT_CLEARANCE,'crossing_x_mm':list(B.CROSS_X_CENTRES)},
      'wet_pan_bends':0,'slat_retention':{'central_notch_width_mm':3.6,'central_notch_depth_mm':3.,'central_comb_minimum_width_mm':3.175,'cold_lateral_play_each_way_mm':.2125,'minimum_cold_overhang_beyond_comb_face_mm':3.2,'thermal_assumption_alpha_per_K':12e-6,'thermal_sensitivity_delta_K':300,'half_length_growth_mm':440*12e-6*300,'remaining_wall_clearance_mm':5.1-.2125-440*12e-6*300,'lift_to_clear_all_comb_teeth_mm':17.,'physical_limit':'Differentialtemperature,bowing,wearandactualkerfarecommissioningchecks;nodistributedloadratingisinferred.'},'weld_schedule':[
       'Leak-tightcontinuousweldfloor/perimeterandspout. Grindpanoutsideenvelope flush atledgerpassages.',
       'Combs:2mmfillets20mmlong,bothsides,centredY200/650/1050; keepdrainageopen. Combsremainonpanforservice.',
       'Collector/gutter:butt-weldflatplateswithnooverlappingstock;2R2formedtabsweldtooutsidecollectorfaces;2externalM4weldstudsfixpanwithoutwetwallholes.',
       'Noone-sheetsteelclaim. Nestallpan/slat/guard/brace/hatchblanksjointlybeforeordering.'
      ],'physical_interfaces':['Measureplythickness/moistureandtriallapcoupon;adjust9.10slotfortheactualstock whilepreservingnominal.10clearance.',
       'Receivedtrackdie,fasteners,toterim/heatcompatibilityandthreadfitsmustmeetthedeclaredinterfaces.',
       'Weldpenetration,distortion,gluebond/preloadandloadtestsremainphysicalqualifications,notomittedCADoperations.'],
      'source_sha256':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('params.py','bed.py','bed_fabrication.py')}}
    generated={HERE/r['dxf'] for r in rows}
    generated.update(OP_ASSETS)
    generated.update(FAB/n for n in ('TOP_SKIN_OPERATIONS.dxf','BOTTOM_SKIN_OPERATIONS.dxf',
      'RECEIVER_LID_MODIFICATION_TEMPLATE.dxf','CASSETTE_JOINERY.step','COVER_PARKING_STANDS.step'))
    old=FAB/'HATCH_FIXED_HINGE_LEAF.dxf'
    if old.exists() and old.parent.resolve()==FAB.resolve():old.unlink()
    output_checks={}
    for q in generated:
        assert q.exists(),q
        if q.suffix=='.dxf':
            dd=ezdxf.readfile(q);assert dd.units==4 and not dd.audit().has_errors
        output_checks[str(q.relative_to(HERE))]=hashlib.sha256(q.read_bytes()).hexdigest()
    result['output_sha256']=output_checks
    result['joinery']['STEP_roundtrip_volume_error_mm3']=abs(imported.Volume()-sum(s.Volume() for n,s,c in wood))
    result['source_consistent_during_check']=sources==result['source_sha256']
    result['passed']=all(q['passed'] for q in rebuild) and result['source_consistent_during_check'] and result['joinery']['STEP_roundtrip_volume_error_mm3']<.1 and all(r['roundtrip_volume_error_mm3']<max(.05,r['area_mm2']*r['thickness_mm']*1e-6) for r in rows) and result['joinery']['all_single_valid_solids'] and not joinery['positive_intersections']
    (OUT/'bed-manufacturing-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':result['passed'],'DXFparts':len(rows),'wood_components':len(wood),'joinery_hits':joinery['positive_intersections']},indent=2),flush=True)
    return 0 if result['passed'] else 1

if __name__=='__main__':
    try:code=run()
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
