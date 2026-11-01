"""Mounted XR2 steel splash/heat guards; not sealed fume extraction.

All modeled exterior joints have clearance holes and fasteners. Frame screws
show only external grip because the vendor slot/nut cavity is unqualified.
Their real in-slot threads and matching nuts remain in the hardware schedule.
"""
from pathlib import Path
from functools import lru_cache
import csv,hashlib,json,math,os,sys
import cadquery as cq
import params as P

HERE=Path(__file__).resolve().parent
OUT=HERE/'review'
STEEL=(.31,.36,.40);FAST=(.48,.51,.53)
T=1.9
GUIDE_Y0,GUIDE_Y1=65.,1435.
ARMOR_Y0,ARMOR_Y1=80.,1200.
MOUNT_Y=P.POST_CENTRES_Y
ARMOR_Y=(200.,700.,1100.)
ATC_RELIEF_Y=(1055.,1422.)
ATC_RELIEF_Z=(1031.5,1068.)
ATC_SHELF_RELIEF_Y=((1223.,1267.),(1323.,1367.))
ATC_SHELF_RELIEF_Z=(1000.65,1035.5)
ROOT_X=575.
ROOF_X0,ROOF_X1=208.,942.
ROOF_Y0,ROOF_Y1=834.,1154.
ROOF_Z=700.
RECEIVER_CLIP_T=6.

def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def cyl(r,h,p,d=(0,0,1)):return cq.Solid.makeCylinder(r,h,cq.Vector(*p),cq.Vector(*d))
def mirror(s,left):return s if left else s.mirror('YZ',(ROOT_X,0,0))
def bore(s,r,p,h,d=(0,0,1)):return s.cut(cyl(r,h,p,d)).clean()
def hexnut(p,axis=(1,0,0),size=7.,height=3.2,hole=4.):
    plane=cq.Plane(origin=p,normal=axis)
    s=cq.Workplane(plane).polygon(6,size/math.cos(math.pi/6)).extrude(height).val()
    return bore(s,hole/2,tuple(a-b*.1 for a,b in zip(p,axis)),height+.2,axis)
def washer(p,axis=(1,0,0),outer=9.,inner=4.5,t=.8):
    return cyl(outer/2,t,p,axis).cut(cyl(inner/2,t+.2,tuple(a-b*.1 for a,b in zip(p,axis)),axis)).clean()
def button(p,axis,length=8.,d=4.,head_d=8.,head_h=2.2):
    # p is underhead face; positive axis points toward the screw tip.
    tip=tuple(a+b*length for a,b in zip(p,axis))
    sh=cyl((d-.1)/2,length,p,axis)
    head=cyl(head_d/2,head_h,p,tuple(-v for v in axis))
    return sh.fuse(head).clean()
def profile(y,L,start,segments):
    wp=cq.Workplane(cq.Plane(origin=(0,y,0),xDir=(1,0,0),normal=(0,-1,0))).moveTo(*start)
    for segment in segments:
        wp=wp.lineTo(*segment) if len(segment)==2 and isinstance(segment[0],(float,int)) else wp.threePointArc(segment[0],segment[1])
    return wp.close().extrude(-L).val().clean()
def arcpoint(x,z,r,a):return (x+r*math.cos(math.radians(a)),z+r*math.sin(math.radians(a)))

@lru_cache(None)
def guide_panel():
    # BottomR2 inside bend; topR1 open180hem with2mm return/web gap.
    s=profile(GUIDE_Y0,GUIDE_Y1-GUIDE_Y0,(89.,936.),[
       (99.,936.),(arcpoint(99,939.9,3.9,-45),(102.9,939.9)),
       (102.9,1064.1),(arcpoint(100,1064.1,2.9,90),(97.1,1064.1)),
       (97.1,1057.),(99.,1057.),(99.,1064.1),
       (arcpoint(100,1064.1,1.,90),(101.,1064.1)),(101.,939.9),
       (arcpoint(99,939.9,2.,-45),(99.,937.9)),(89.,937.9)])
    # Steel ATC backbars replace the relieved upper band.2mm edgeclearance.
    s=s.cut(box(80.,ATC_RELIEF_Y[0],ATC_RELIEF_Z[0],40.,ATC_RELIEF_Y[1]-ATC_RELIEF_Y[0],40.)).clean()
    # The shifted ATC supports cross the web below the main backbar opening.
    for y0,y1 in ATC_SHELF_RELIEF_Y:
        s=s.cut(box(80.,y0,ATC_SHELF_RELIEF_Z[0],45.,y1-y0,ATC_SHELF_RELIEF_Z[1]-ATC_SHELF_RELIEF_Z[0])).clean()
    for cy in MOUNT_Y:
        for yy in (cy-20,cy+20):s=bore(s,2.25,(100.,yy,952.),4.,(1,0,0))
    for yy in ARMOR_Y:s=bore(s,2.25,(94.,yy,935.),4.)
    return s

@lru_cache(None)
def sided_guide_panel(left):
    s=mirror(guide_panel(),left)
    if not left:
        s=s.cut(box(1000.,1402.,1018.,70.,48.,57.))
        s=s.cut(box(1000.,1409.,1012.,70.,41.,6.)).clean()
    return s

@lru_cache(None)
def guide_clip(cy):
    # Formedhat,1.9mm, insidebendR2,60mm wide alongY.
    s=profile(cy-30,60.,(50.8,944.),[(52.7,944.),(52.7,960.1),
       (arcpoint(54.7,960.1,2,135),(54.7,962.1)),(97.1,962.1),
       (arcpoint(97.1,960.1,2,45),(99.1,960.1)),(99.1,944.),
       (101.,944.),(101.,960.1),
       (arcpoint(97.1,960.1,3.9,45),(97.1,964.)),(54.7,964.),
       (arcpoint(54.7,960.1,3.9,135),(50.8,960.1))])
    for yy in (cy-20,cy+20):
        s=bore(s,3.3,(49.8,yy,952.),4.,(1,0,0))
        s=bore(s,2.25,(98.1,yy,952.),4.,(1,0,0))
    return s

@lru_cache(None)
def ledger_armor():
    # Main2-bend J sheet plus weldedtopcap and3butt-welded mountingtabs.
    s=profile(ARMOR_Y0,ARMOR_Y1-ARMOR_Y0,(83.55,934.1),[
        (85.45,934.1),(85.45,895.9),
        (arcpoint(87.45,895.9,2,225),(87.45,893.9)),(128.1,893.9),
        (arcpoint(128.1,890,3.9,45),(132.,890.)),(132.,876.),
        (130.1,876.),(130.1,890.),
        (arcpoint(128.1,890,2,45),(128.1,892.)),(87.45,892.),
        (arcpoint(87.45,895.9,3.9,225),(83.55,895.9))])
    s=s.fuse(box(73.2,ARMOR_Y0,934.1,12.25,ARMOR_Y1-ARMOR_Y0,T))
    for yy in ARMOR_Y:
        s=s.fuse(box(85.45,yy-15,934.1,13.55,30.,T))
        s=bore(s,2.25,(94.,yy,933.1),4.)
    return s.clean()

@lru_cache(None)
def receiver_roof():
    # Weldedrectangular blanks avoid unqualified bend development atcorners.
    x0,x1,y0,y1,z=ROOF_X0,ROOF_X1,ROOF_Y0,ROOF_Y1,ROOF_Z
    s=box(x0,y0,z,x1-x0,y1-y0,T)
    s=s.fuse(box(x0,y0,z+T,T,y1-y0-T,20-T),
       box(x1-T,y0,z+T,T,y1-y0-T,20-T),
       box(x0+T,y0,z+T,x1-x0-2*T,T,20-T),
       box(x0,y1-T,z+T,x1-x0,T,28-T)).clean()
    for x in (300.,850.):
        for zz in (709.,720.):s=bore(s,2.25,(x,y1-T-.1,zz),T+.2,(0,1,0))
    return s

@lru_cache(None)
def receiver_clip(x):
    s=box(x-20,1154.,700.,40.,RECEIVER_CLIP_T,98.)
    for zz in (709.,720.):s=bore(s,2.25,(x,1153.9,zz),6.2,(0,1,0))
    for zz in (746.5,786.5):s=bore(s,3.3,(x,1153.9,zz),6.2,(0,1,0))
    return s

def shield_parts(hot=False):
    out=[]
    def add(n,s,c=STEEL):out.append((n,s.clean(),c))
    for side,left in (('L',True),('R',False)):
        add('SH_GUIDE_'+side+'_R2_OPEN_HEM_ATC_RELIEF',sided_guide_panel(left))
        for i,cy in enumerate(MOUNT_Y,1):
            add(f'SH_GUIDE_CLIP_{side}_{i}',mirror(guide_clip(cy),left))
            for j,yy in enumerate((cy-20,cy+20),1):
                # ActualM6x12; only3.5mm exteriorgrip is represented.
                screw=button((54.3,yy,952.),(-1,0,0),3.5,6,10.5,3.3)
                add(f'SH_GUIDE_FRAME_M6x12_EXTERNAL_GRIP_{side}_{i}_{j}',mirror(screw,left),FAST)
                add(f'SH_GUIDE_FRAME_WASHER_{side}_{i}_{j}',mirror(washer((52.7,yy,952.),outer=12,inner=6.6,t=1.6),left),FAST)
                add(f'SH_GUIDE_PANEL_M4x8_{side}_{i}_{j}',mirror(button((103.7,yy,952.),(-1,0,0)),left),FAST)
                add(f'SH_GUIDE_PANEL_WASHER_{side}_{i}_{j}',mirror(washer((102.9,yy,952.)),left),FAST)
                add(f'SH_GUIDE_PANEL_NUT_{side}_{i}_{j}',mirror(hexnut((95.9,yy,952.)),left),FAST)
        if hot:
            add('SH_LEDGER_'+side+'_REMOVABLE_WELDED_ARMOR',mirror(ledger_armor(),left))
            for i,yy in enumerate(ARMOR_Y,1):
                add(f'SH_LEDGER_WELDNUT_M4_{side}_{i}',mirror(hexnut((94,yy,930.9),(0,0,1)),left),FAST)
                add(f'SH_LEDGER_REMOVE_M4x8_{side}_{i}',mirror(button((94,yy,938.7),(0,0,-1)),left),FAST)
                add(f'SH_LEDGER_WASHER_{side}_{i}',mirror(washer((94,yy,937.9),(0,0,1)),left),FAST)
    add('SH_RECEIVER_WELDED_ROOF',receiver_roof())
    for i,x in enumerate((300.,850.),1):
        add(f'SH_RECEIVER_CLIP_{i}',receiver_clip(x))
        for j,zz in enumerate((746.5,786.5),1):
            add(f'SH_RECEIVER_FRAME_M6x16_EXTERNAL_GRIP_{i}_{j}',button((x,1152.4,zz),(0,1,0),7.6,6,10.5,3.3),FAST)
            add(f'SH_RECEIVER_FRAME_WASHER_{i}_{j}',washer((x,1152.4,zz),(0,1,0),12,6.6,1.6),FAST)
        for j,zz in enumerate((709.,720.),1):
            add(f'SH_RECEIVER_M4x12_{i}_{j}',button((x,1151.3,zz),(0,1,0),12.),FAST)
            add(f'SH_RECEIVER_WASHER_{i}_{j}',washer((x,1151.3,zz),(0,1,0)),FAST)
            add(f'SH_RECEIVER_NUT_{i}_{j}',hexnut((x,1160.,zz),(0,1,0)),FAST)
    return out

def manufacturing():
    ba90=math.pi/2*(2+.5*T)
    ba180=math.pi*(1+.5*T)
    guide_width=10+ba90+124.2+ba180+7.1
    armor_width=38.2+ba90+40.65+ba90+14
    clip_width=16.1+ba90+42.4+ba90+16.1
    rows=[['GUIDE_FORMED_L',1,1370,guide_width,T,'BottomR2/90deg;topR1/180deg openhem2mmgap;web124.2straight;return7.1. FinishedY65..1435;commonATCreliefand2localsupportshelfnotches.'],
          ['GUIDE_FORMED_R',1,1370,guide_width,T,'Mirrorformedsection;commonATCandcradlereliefsplusrearMOTORreliefY1402..1450/Z1018..1075,locallydeepertoZ1012overY1409..1450. ATCsteelmotorshroudreplacesthemissingbarrier.'],
          ['GUIDE_CLIP',6,60,clip_width,T,'2xR2/90deg bends;straightlegs16.1/bridge42.4.2postØ6.6+2guardØ4.5.'],
          ['LEDGER_MAIN_J',2,1120,armor_width,T,'2xR2/90deg bends;straightlengths38.2/40.65/14. Hot-only; removebeforecassetteconversion.'],
          ['LEDGER_TOPCAP',2,1120,12.25,T,'Butt/T-weldtocrownofJsheet; seal/stitchafterfixturing.'],
          ['LEDGER_MOUNTTAB',6,30,13.55,T,'Buttweldtotopcapedge;Ø4.5 atworldX94/Y200,700,1100.'],
          ['RECEIVER_BASE',1,734,320,T,'Flatrectweldedtofourreturns;Z700.'],
          ['RECEIVER_SIDE',2,318.1,18.1,T,'Weldontopbase;2sideedges.'],
          ['RECEIVER_FRONT',1,730.2,18.1,T,'Weldbetweensideedges.'],
          ['RECEIVER_REAR',1,734,26.1,T,'Weldontopbase;4xØ4.5 atX300/850,Z709/720.'],
          ['RECEIVER_CLIP',2,98,40,RECEIVER_CLIP_T,'NEW6mmsteelstripstock;4bores:2xØ6.6 tobearerZ746.5/786.5;2xØ4.5 toroofZ709/720.']]
    holes={'guide_panel':'6xØ4.5 normalX atY80/120/610/650/1160/1200,Z952;3xØ4.5 normalZ atX94,Y200/700/1100. Mirrorforright.',
           'ATC_relief':'CommonupperbandY1055..1422,Z1031.5..1068 throughprofile. LocalBOTHsidewebslotsY1223..1267and1323..1367,Z1000.65..1035.5,throughX80..125left/mirroredright,cleartheATCsupportcradles. RIGHTONLYrearreliefX1000..1070,Y1402..1450,Z1018..1075;lowerextensionZ1012..1018overY1409..1450only. MatchATCsteelbackbars+cradles+fixedmotorshroud;lowerguidewebstayscontinuous.',
           'hem':'Rinside1,Router2.9;2mmgapbetweenreturnedlegandweb. DeburrandcloseendswithoutgrowingXbeyond102.9.',
           'bend_note':'DevelopmentusesneutralK0.5 nominal. Shopmustvalidatebendcoupon/springbackandsheetthickness;finishprofilesandholecoordinatescontrol. No guessed Kfactorisafabricationtolerance.'}
    hardware={'M6x12_button_guide_external_grip':12,'M6x16_button_receiver_external_grip':4,
              'M6_washer_OD12_t1p6':16,'matching_M6_slot_nut_actualfit_hold':16,
              'M4x8_button_fixedguide':12,'M4x12_button_receiver':4,'M4_washer_OD9_t0p8_fixed':16,'M4_hexnut_fixed':16,
              'M4x8_removable_armor':6,'M4_washer_removable':6,'M4_weldnut_armor':6}
    report={'revision':P.REVISION,'release':False,'parts':rows,'flat_columns':['blank_id','quantity','length_mm','developed_width_mm','thickness_mm','notes'],
       'hole_and_bend_instructions':holes,'hardware':hardware,
       'gross_rectangular_sheet_area_mm2':sum(q*l*w for _,q,l,w,_,_ in rows),
       'stock_by_thickness_mm':{'1.9_gross_rectangular_area_mm2':sum(q*l*w for _,q,l,w,t,_ in rows if t==1.9),
                               '6.0_receiver_clips_area_mm2':sum(q*l*w for _,q,l,w,t,_ in rows if t==6.)},
       'mode':'Guidesandreceiverroofremaininbothmodes. Ledgerarmorandits6removablescrews/washersarehot-only.',
       'support':'Guideclipstotwoactualverticalpostslots;receiverclipstorearbearerfronttwohorizontalrows. Externalgripendsattheframeface;matchingslotnutsandthreadtipsnotfakedinsolidprofileenvelope.',
       'service':['Remove6top-accessM4armorscrewsandliftbothledgerarmorsbeforebedconversion. Keepweldnutswitharmor.',
          'Normalreceiverhatchservice:roofstaysinstalled,minimumroofZ700versushatchmax688;12mmnominalgapbeforecompliance.',
          'Roofmaintenanceonly:closehatch,remove4M4roofjoints,pull7.1mmforwardFIRST,lift40mm,rotatefrontdown90degaboutrearY1146.9/Z740. Testactualhandsandclearancesbeforeuse.',
          'Guidesarenonsealedspatterguards;remove12M4screwsforrailgreasing/inspectionwhileframeclipsstayinstalled.'],
       'limits':['Notafumeextractor,pressurereceiverorcompletefireenclosure','ATCbackbarsreplacetherelievedupperguideband;verifytheminstalledbeforeplasma',
                 'Noexposedgalvanizedorcoatedsteelinthehotzone','Qualifyguardtemperature,spatterpath,corrosion/bonding,clippreloadandactualtool/cablemotion'],
       'source_sha256':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('shields.py','frame.py','params.py')}}
    OUT.mkdir(exist_ok=True)
    report['manufacturing_files']=manufacturing_files(rows,guide_width,armor_width,clip_width,ba90,ba180)
    roof_mass=receiver_roof().Volume()*7.85e-6
    per_clip_moment=roof_mass*9.80665/2*160
    clipI=40*RECEIVER_CLIP_T**3/12
    clip_length=746.5-(709+720)/2
    rotation=per_clip_moment*clip_length/(P.STEEL_E_MPA*clipI)
    deflection=rotation*320+per_clip_moment*clip_length**2/(2*P.STEEL_E_MPA*clipI)
    report['receiver_support_screen']={'roof_mass_kg_from_solid':roof_mass,'clip_thickness_mm':RECEIVER_CLIP_T,
       'ideal_clip_rotation_rad':rotation,'ideal_roof_tip_drop_due_clip_bending_mm':deflection,
       'hatch_open_max_z_mm':688.,'nominal_vertical_hatch_gap_mm':12.,
       'hatch_gap_minus_clip_component_mm':12-deflection,
       'per_clip_gravity_moment_Nmm':per_clip_moment,'M4_force_couple_component_N':per_clip_moment/11,
       'qualification':'Ideal steelstripbendingonly;addroof/weld/fastener/contactcompliance. No operator,storageorworkloadrating.'}
    (OUT/'shield-manufacturing.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    with (OUT/'shield-fabrication.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(report['flat_columns']);w.writerows(rows)
    return report

def manufacturing_files(rows,gw,aw,cw,ba90,ba180):
    import ezdxf
    folder=OUT/'shields';folder.mkdir(exist_ok=True)
    records=[]
    for name,qty,L,W,t,notes in rows:
        doc=ezdxf.new('R2010');doc.units=4;ms=doc.modelspace()
        for layer in ('CUT_OUTER','CUT_HOLES','BEND_REFERENCE','SHOP_NOTES'):doc.layers.new(layer)
        outline=[(0,0),(L,0),(L,W),(0,W)]
        holes=[];bends=[]
        if name.startswith('GUIDE_FORMED'):
            a,b=ATC_RELIEF_Y[0]-GUIDE_Y0,ATC_RELIEF_Y[1]-GUIDE_Y0
            u=10+ba90+ATC_RELIEF_Z[0]-939.9
            shelf_u=10+ba90+ATC_SHELF_RELIEF_Z[0]-939.9
            shelf_edge=[]
            for y0,y1 in reversed(ATC_SHELF_RELIEF_Y):
                x0,x1=y0-GUIDE_Y0,y1-GUIDE_Y0
                shelf_edge +=[(x1,u),(x1,shelf_u),(x0,shelf_u),(x0,u)]
            outline=[(0,0),(L,0),(L,W),(b,W),(b,u),*shelf_edge,(a,u),(a,W),(0,W)]
            if name.endswith('_R'):
                motor_y=1402.-GUIDE_Y0;motor_u=10+ba90+1018.-939.9
                lower_y=1409.-GUIDE_Y0;lower_u=10+ba90+1012.-939.9
                outline=[(0,0),(L,0),(L,lower_u),(lower_y,lower_u),(lower_y,motor_u),(motor_y,motor_u),(motor_y,u),*shelf_edge,(a,u),(a,W),(0,W)]
            holes=[(yy-GUIDE_Y0,10+ba90+952-939.9,4.5) for cy in MOUNT_Y for yy in (cy-20,cy+20)]
            holes +=[(yy-GUIDE_Y0,5.,4.5) for yy in ARMOR_Y]
            bends=[(10+ba90/2,[(0,L)]),(10+ba90+124.2+ba180/2,[(0,a)] if name.endswith('_R') else[(0,a),(b,L)])]
        elif name=='GUIDE_CLIP':
            holes=[(v,8.,6.6) for v in (10.,50.)]+[(v,16.1+ba90+42.4+ba90+8.1,4.5) for v in (10.,50.)]
            bends=[(16.1+ba90/2,[(0,L)]),(16.1+ba90+42.4+ba90/2,[(0,L)])]
        elif name=='LEDGER_MAIN_J':
            bends=[(38.2+ba90/2,[(0,L)]),(38.2+ba90+40.65+ba90/2,[(0,L)])]
        elif name=='LEDGER_MOUNTTAB':holes=[(15.,8.55,4.5)]
        elif name=='RECEIVER_REAR':holes=[(x-ROOF_X0,z-701.9,4.5) for x in (300.,850.) for z in (709.,720.)]
        elif name=='RECEIVER_CLIP':holes=[(z-700,20,4.5 if z<730 else 6.6) for z in (709.,720.,746.5,786.5)]
        ms.add_lwpolyline(outline,close=True,dxfattribs={'layer':'CUT_OUTER'})
        for x,y,d in holes:ms.add_circle((x,y),d/2,dxfattribs={'layer':'CUT_HOLES'})
        for y,ranges in bends:
            for x0,x1 in ranges:ms.add_line((x0,y),(x1,y),dxfattribs={'layer':'BEND_REFERENCE'})
        text=f'{name};QTY{qty};plainsteel{t}mm;mmunits. {notes} BenddevelopmentK0.5nominal;validatecoupon. Finishedprofilecontrols. DevelopmentnotCAMrelease.'
        ms.add_mtext(text,dxfattribs={'layer':'SHOP_NOTES','char_height':3,'insert':(L+15,W),'width':160})
        path=folder/(name+'.dxf');doc.saveas(path)
        reread=ezdxf.readfile(path);assert reread.units==4 and not reread.audit().has_errors
        records.append({'file':str(path.relative_to(HERE)),'quantity':qty,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'units':'mm','cut_holes':len(holes),'bend_reference_lines':sum(len(r) for _,r in bends)})
    for old in ('GUIDE_FORMED.dxf','GUIDE_FINISHED.step'):
        stale=folder/old
        if stale.exists():stale.unlink()
    for name,shape in (('GUIDE_FINISHED_L',sided_guide_panel(True)),('GUIDE_FINISHED_R',sided_guide_panel(False)),('GUIDE_CLIP_FINISHED',guide_clip(100.)),
                       ('LEDGER_ARMOR_FINISHED',ledger_armor()),('RECEIVER_ROOF_FINISHED',receiver_roof()),
                       ('RECEIVER_CLIP_FINISHED',receiver_clip(300.))):
        path=folder/(name+'.step');cq.exporters.export(shape,str(path))
        imported=cq.importers.importStep(str(path)).val()
        assert imported.isValid() and len(imported.Solids())==1,(name,len(imported.Solids()))
        assert abs(imported.Volume()-shape.Volume())<max(.1,shape.Volume()*1e-7)
        records.append({'file':str(path.relative_to(HERE)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'step_roundtrip_valid':True,'solids':1})
    return records

def roof_service_envelopes():
    # Removeall4M4roofjointsbeforemotion. PullfirsttoavoidM6frameheads.
    x,dx=ROOF_X0,ROOF_X1-ROOF_X0
    rear=ROOF_Y1-7.1;z=740.;R=math.hypot(320.,28.)
    pull=box(x,ROOF_Y0-7.1,700.,dx,327.1,28.)
    lift=box(x,ROOF_Y0-7.1,700.,dx,320.,68.)
    c=cq.Vector(x,rear,z);left=cq.Vector(x,rear-R,z);down=cq.Vector(x,rear,z-R)
    mid=cq.Vector(x,rear-R/math.sqrt(2),z-R/math.sqrt(2))
    wire=cq.Wire.assembleEdges([cq.Edge.makeLine(c,left),cq.Edge.makeThreePointArc(left,mid,down),cq.Edge.makeLine(down,c)])
    quarter=cq.Solid.extrudeLinear(wire,[],cq.Vector(dx,0,0))
    upper=box(x,rear-R,z,dx,R,28.)
    return [('ROOF_SERVICE_PULL_BOX',pull,STEEL),('ROOF_SERVICE_LIFT_BOX',lift,STEEL),
            ('ROOF_SERVICE_ROTATION_ENVELOPE',quarter.fuse(upper).clean(),STEEL)]

def check():
    from build import clashes,bounds
    from frame import frame_parts
    from bed import bed_parts
    from bed import receiver_hatch_parts
    from motion import motion_parts
    from itertools import product
    OUT.mkdir(exist_ok=True);report={'revision':P.REVISION,'release':False,'states':{},
        'nominal_axis_travel_mm':{'X':P.X_TRAVEL,'Y':P.Y_TRAVEL,'Z':P.Z_TRAVEL},
        'checked_endpoint_head_X_mm':[575-P.X_TRAVEL/2,575+P.X_TRAVEL/2],
        'checked_endpoint_Yguide_mm':[775-P.Y_TRAVEL/2,775+P.Y_TRAVEL/2],
        'checked_endpoint_Zlift_mm':[0.,P.Z_TRAVEL]}
    for hot in (False,True):
        label='HOT' if hot else'WOOD';parts=shield_parts(hot)
        bad=[n for n,s,_ in parts if not s.isValid() or len(s.Solids())!=1]
        r={'parts':len(parts),'invalid_or_disconnected':bad,'self':clashes(parts,parts,True),
           'frame':clashes(parts,frame_parts()),'bed':clashes(parts,bed_parts(hot))}
        print(label, {k:len(v['positive_intersections']) for k,v in r.items() if isinstance(v,dict)},flush=True)
        sweep={}
        for x,y,z in product((575-P.X_TRAVEL/2,575+P.X_TRAVEL/2),
                              (775-P.Y_TRAVEL/2,775+P.Y_TRAVEL/2),(0.,P.Z_TRAVEL)):
            for n,s,_ in motion_parts(hot,y,x,z):
                b=bounds(s)
                if n not in sweep:sweep[n]=b
                else:
                    for k in range(3):sweep[n][k]=min(sweep[n][k],b[k]);sweep[n][k+3]=max(sweep[n][k+3],b[k+3])
        env=[('SWEEP_'+n,box(*b[:3],*[b[i+3]-b[i] for i in range(3)]),STEEL) for n,b in sweep.items()]
        r['motion_union_box_proof']=clashes(parts,env)
        print(label,'motionboxhits',len(r['motion_union_box_proof']['positive_intersections']),flush=True)
        report['states'][label]=r
    fixed_shields=[p for p in shield_parts(False) if p[0]!='SH_RECEIVER_WELDED_ROOF' and not p[0].startswith(('SH_RECEIVER_M4','SH_RECEIVER_WASHER','SH_RECEIVER_NUT'))]
    fixed=frame_parts()+bed_parts(True)+fixed_shields
    report['receiver_roof_service']=clashes(roof_service_envelopes(),fixed)
    report['receiver_roof_service']['scope']='Conservativefullpull/liftboxesandfilledquarterdiskplusupperbandcovercontinuous90degreefrontdownrotation. Closehatchandremove4M4roofjointsbeforepull7.1,lift40,rotate.'
    report['receiver_hatch_open']=clashes(shield_parts(False),receiver_hatch_parts(True))
    report['passed']=all(not r['invalid_or_disconnected'] and all(not v['positive_intersections'] for v in r.values() if isinstance(v,dict) and 'positive_intersections'in v) for r in report['states'].values()) and not report['receiver_roof_service']['positive_intersections'] and not report['receiver_hatch_open']['positive_intersections']
    report['scope']='Exactguardself/frame/bed checks and exactguardagainstconservativeunionboxofeachmotionpartat8corners. Emptyunionboxintersectionsproveexternalclearanceforinheritedindependenttranslations;ATCaccessoriesandconversion/servicegetseparatechecks.'
    report['source_sha256']={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('shields.py','params.py','frame.py','bed.py','motion.py')}
    (OUT/'shield-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    try:
        m=manufacturing();print('Shieldgrosssheetarea_m2',m['gross_rectangular_sheet_area_mm2']/1e6,flush=True)
        r=check() if '--check'in sys.argv else None
        code=0 if r is None or r['passed'] else 1
    except Exception:
        import traceback;traceback.print_exc();code=2
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
