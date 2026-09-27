"""Detailed small-machine retracting carrier candidate. Frozen Rev I is read-only.

Actual magazine mounting remains two blank replaceable saddles. Proposed Z200 is
an installation requirement, not a substituted purchased module or supplier CAD.
"""
from pathlib import Path
import hashlib,json,math,os,sys
import cadquery as cq
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
LEGACY=ROOT/'output/release-review/RevE-ENGINEERING'
sys.path[:0]=[str(LEGACY),str(ROOT/'variants/retractable-atc/hardware')]
from cad_helpers import Model,box,cyl,plate,rect,place,bbox,validate,export
import hardware

BLUE=(.12,.48,.65);STEEL=(.3,.37,.4);GOLD=(.8,.6,.25);PINK=(.75,.25,.62)
RB=1007.; WT=1020.; TOP=1026.35; MAG=1050.35
CENTERS=(121.,1029.); SUPPORTS=(1105.,1205.,1330.)

def cap(d,L,hd,hh):return cyl(d,L).fuse(cyl(hd,hh).translate((0,0,L))).clean()
def nut(d,af,h):return cq.Workplane('XY').polygon(6,af/math.cos(math.pi/6)).extrude(h).val().cut(cyl(d,h))
def add(m,n,s,origin=(0,0,0),**kw):return m.add(n,s,origin,**kw)
def threaded(m,a,b):m.permit(a,b,'Nominal external screw cylinder in explicitly tapped minor bore; no helical thread geometry.')
def washer(m,n,od,id,t,xyz):return add(m,n,cyl(od,t).cut(cyl(id,t)),xyz,pn=f'WASHER_{id}_{od}_{t}',material='steel',group='fasteners')
def screw(m,n,d,L,xyz,hd=None,hh=None,**kw):
    return add(m,n,cap(d,L,hd or d*1.8,hh or d),xyz,pn=f'CAP_M{d}x{L}',material='class8.8 steel',group='fasteners',**kw)

def build(travel=0,unlocked=False,allocations=False):
    assert 0<=travel<=200
    m=Model();moving=[]
    for side,cx in enumerate(CENTERS):
        mirror=side==1
        # Steel mounting strip, positioned outside the complete low-spindle sweep.
        h=[(16.5,50+25*i,2.5) for i in range(14)]
        h += [(16.5,y-1030,6.6) for c in SUPPORTS for y in (c-10,c+10)]
        h += [(x,8.5,4.2) for x in ((8.5,26.5) if not mirror else (6.5,24.5))]
        h += [(x,410.9,4.2) for x in (6.5,26.5)]
        if not mirror:h += [(16.5,25,8.5),(16.5,400,8.5)]
        p=m.add_plate(f'BASE_{side}',33,420,12.7,holes=h,origin=(cx-16.5,1030,994.3),
            pn=f'SM_BASE_STRIP_{side}',color=STEEL,notes=['Rail mounts:14x M3 TAP; stop mounts M5 TAP. Six base mounts ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â¹Ãƒâ€¦Ã¢â‚¬Å“6.6/ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â¹Ãƒâ€¦Ã¢â‚¬Å“11x6 deep counterbore. Machine rail seat after welding supports.'])
        for c in SUPPORTS:
            for y in (c-10,c+10):
                localtool=cyl(11,6).translate((16.5,y-1030,6.7))
                p.local=p.local.cut(localtool);p.flat.setdefault('operations',[]).append({'type':'circle','x':16.5,'y':y-1030,'diameter':11,'layer':'COUNTERBORE_11_DEPTH6'})
        if mirror:
            p.local=p.local.cut(box(35,5,5.9).translate((-1,365.2,0)))
            p.flat.setdefault('operations',[]).append({'type':'slot','x':16.5,'y':367.7,'length':42,'width':5,'angle':0,'layer':'UNDERSIDE_RELIEF_DEPTH5p9'})
            p.notes.append('Underside open relief Y1395.2..1400.2, depth5.9, full33mm width; leaves6.8mm ligament and1mm clearance to existing rear gusset.')
        p.local=p.local.clean();p.shape=p.local.translate((cx-16.5,1030,994.3))
        rail=hardware.rail_350().rotate((0,0,0),(0,0,1),90)
        add(m,f'RAIL_{side}',rail,(cx,1070,RB),pn='HIWIN_MGNR12_350_E10',group='guides',purchased=True,color=GOLD)
        for i in range(14):
            s=screw(m,f'RAIL_{side}_BOLT_{i}',3,8,(cx,1080+25*i,1002.5),hd=5.5,hh=3)
            threaded(m,s.id,p.id)
        for j,c in enumerate(SUPPORTS):
            x0=6.35 if not mirror else 1012.5
            holes=[((cx-x0),y,6.6) for y in (15,35)]
            m.add_plate(f'SHELF_{side}_{j}',131.15,50,6.35,holes=holes,origin=(x0,c-25,987.95),pn='SM_SUPPORT_SHELF_L' if not mirror else 'SM_SUPPORT_SHELF_R',color=STEEL)
            sx=6.35 if not mirror else 1105.55
            add(m,f'SPACER_{side}_{j}',box(38.1,50,4.9),(sx,c-25,994.3),pn='SM_SUPPORT_SPACER_38_50_4p9',color=STEEL,
                notes=['Finish6.35stock to4.9; top bears against underside of original2in chassis tube. Weld3mm fillets, machine rail datum afterward.'])
            wx=38.1 if not mirror else 1105.55
            m.add_plate(f'WEB_{side}_{j}',50,38.1,6.35,origin=(wx,c-25,949.85),u=(0,1,0),v=(0,0,1),pn='SM_SUPPORT_WEB_50_38p1_6p35',color=STEEL)
            for end,yy in enumerate((c-16.5,c+25)):
                outline=[(0,0),(0,38.1),(76.55,38.1)]
                # Mirror the triangular gusset about the chassis midplane.
                s=plate(outline,6.35)
                shape=place(s,(44.45,yy,949.85),u=(1,0,0),v=(0,0,1))
                if mirror:shape=shape.mirror('YZ',(575,0,0))
                q=add(m,f'GUSSET_{side}_{j}_{end}',shape,pn=f'SM_GUSSET_{side}',color=STEEL)
                q.local=s;q.flat={'outline':outline,'thickness_mm':6.35,'holes':[],'slots':[],'internal':[]}
            for k,y in enumerate((c-10,c+10)):
                screw(m,f'BASE_{side}_{j}_BOLT_{k}',6,20,(cx,y,981),hd=10.5,hh=6)
                washer(m,f'BASE_{side}_{j}_WASH_{k}',12,6.4,1.6,(cx,y,986.35))
                add(m,f'BASE_{side}_{j}_NUT_{k}',nut(5,10,3.2),(cx,y,983.15),pn='ISO4035_M6_THIN_NUT_3p2',group='fasteners')
                threaded(m,f'BASE_{side}_{j}_BOLT_{k}',f'BASE_{side}_{j}_NUT_{k}')
        for j,y in enumerate((1103.,1183.)):
            q=add(m,f'MOV_BLOCK_{side}_{j}',hardware.mgn12h_block().rotate((0,0,0),(0,0,1),90),(cx,y+travel,RB),pn='HIWIN_MGN12H',group='moving',purchased=True,color=GOLD);moving.append(q.id)
        holes=[(x,y-1045,3.3) for x in (5,25) for y in (1093,1113,1173,1193)]
        holes += [(15,10,6.05),(15,185,6.05)]
        wing_outline=[(0,0),(30,0),(30,81.4),(37.5,81.4),(37.5,106.8),(30,106.8),(30,190.9),(0,190.9)] if not mirror else [(0,0),(30,0),(30,190.9),(0,190.9),(0,106.8),(-7.5,106.8),(-7.5,81.4),(0,81.4)]
        q=m.add_plate(f'MOV_WING_{side}',30,190.9,6.35,outline=wing_outline,holes=holes,origin=(cx-15,1045+travel,WT),pn=f'SM_WING_{side}_190p9_6p35',group='moving',color=BLUE,
            notes=['ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Â¹Ãƒâ€¦Ã¢â‚¬Å“6.05 +0.02 lock holes; right wing holes spare. Both ends extend beyondcarriages; matched endpoints retain rail end margins.'])
        q.local=q.local.cut(box(2,190.9,1.75).translate((28 if mirror else 0,0,0))).clean()
        q.shape=q.local.translate((cx-15,1045+travel,WT))
        q.flat.setdefault('operations',[]).append({'type':'slot','x':30 if mirror else 0,'y':95.45,'length':194.9,'width':4,'angle':90,'layer':'BOTTOM_EDGE_RELIEF_DEPTH1p75'})
        q.notes.append('Mill outer2mm edge underside1.75mm deep over190.9length; retain upper4.6mm and full top washer seats. Clears original Y-block screwheads.')
        moving.append(q.id)
        for j,y in enumerate((1093,1113,1173,1193)):
            for k,x in enumerate((cx-10,cx+10)):
                a=washer(m,f'MOV_WASH_{side}_{j}_{k}',7,3.2,.5,(x,y+travel,TOP));moving.append(a.id)
                a=screw(m,f'MOV_BOLT_{side}_{j}_{k}',3,10,(x,y+travel,1016.85),hd=5.5,hh=3);moving.append(a.id)
        # Positive endpoint stops straddle rail where necessary; screw motor is not the stop.
        for end,sy in [('F',1033.),('R',1435.9)]:
            s=box(30,12 if end=='F' else 10,19.35)
            cols=(7,25) if end=='F' and not mirror else (5,23) if end=='F' else (5,25)
            if end=='F':s=s.cut(box(2,12,19.35).translate((28 if mirror else 0,0,0)))
            for xx in cols:s=s.cut(cyl(5.5,22).translate((xx,5.5 if end=='F' else 5, -1))).cut(cyl(9.5,5).translate((xx,5.5 if end=='F' else 5,14.35)))
            q=add(m,f'STOP_{side}_{end}',s,(cx-15,sy,RB),pn=f'SM_STOP_{end}_{side}' if end=='F' else f'SM_STOP_{end}',color=STEEL,
                notes=['Front/rear face is fitted endpoint stop; frontcontacts moving tongue atY1045; rear atY1435.9.'])
            for k,xx in enumerate(tuple(cx-15+c for c in cols)):
                s=screw(m,f'STOP_{side}_{end}_BOLT_{k}',5,25,(xx,sy+(5.5 if end=='F' else 5),996.35),hd=8.5,hh=5)
                threaded(m,s.id,f'BASE_{side}')
    # A deep crossmember remains behind nominal full stock during the complete stroke.
    length=863.;tube=box(length,25.4,50.8).cut(box(length+2,19.05,44.45).translate((-1,3.175,3.175)))
    q=add(m,'MOV_CROSSBEAM',tube,(143.5,1126.4+travel,969.2),pn='SM_RHS_50p8_25p4_3p175_L863',group='moving',color=BLUE,length=863);moving.append(q.id)
    for x in (138.5,1006.5):
        q=m.add_plate(f'MOV_BEAM_CAP_{x}',25.4,50.8,5,origin=(x,1126.4+travel,969.2),u=(0,1,0),v=(0,0,1),pn='SM_BEAM_CAP_25p4_50p8_5',group='moving',color=BLUE);moving.append(q.id)
    holes=[(x,y,4.2) for x in (10,30,530,550) for y in (25,70)]
    internal=[[(40,15),(520,15),(520,76.4),(40,76.4)]]
    q=m.add_plate('MOV_OPEN_CARRIER',560,101.8,6.35,holes=holes,internal=internal,origin=(295,1050+travel,WT),pn='SM_OPEN_CARRIER_560_101p8_6p35',group='moving',color=BLUE,
        notes=['Eight M5 TAPTHRU riser screws. Central throughwindow preserves below-magazine cutter clearance; no pocket pattern inferred. Weld rearland overcrossbeam.']);moving.append(q.id)
    for side,x0 in enumerate((295,815)):
        q=m.add_plate(f'MOV_MAG_SADDLE_{side}',40,65,6.35,holes=[(x,y,5.5) for x in (10,30) for y in (10,55)],origin=(x0,1065+travel,1044),pn='SM_MAG_SADDLE_BLANK_40_65_6p35',group='moving',color=BLUE,material='Aluminum plate; alloy/condition to verify; finish6.35mm from owned9.525mm stock',
            notes=['BLANK SUPPLIER INTERFACE: four riser clearance holes only. Actual magazine attachment holes require official model or measured template.']);moving.append(q.id)
        for i,xx in enumerate((x0+10,x0+30)):
            for j,yy in enumerate((1075,1120)):
                q=add(m,f'MOV_RISER_{side}_{i}_{j}',cyl(12,17.65).cut(cyl(5.5,17.65)),(xx,yy+travel,TOP),pn='SM_RISER_OD12_ID5p5_L17p65',group='moving',color=GOLD);moving.append(q.id)
                q=washer(m,f'MOV_MAG_WASH_{side}_{i}_{j}',10,5.3,1,(xx,yy+travel,MAG));moving.append(q.id)
                q=screw(m,f'MOV_MAG_BOLT_{side}_{i}_{j}',5,30,(xx,yy+travel,1021.35),hd=8.5,hh=5);moving.append(q.id)
                threaded(m,q.id,'MOV_OPEN_CARRIER')
    # Shared sourced motor, with nut barrel directed toward motor to preserve10mm endmargin.
    add(m,'SLIDE_MOTOR',hardware.pose(hardware.slide_motor(),(115,1040,967.25),direction=(0,1,0)),pn='17E19S1684MB4_300RS',group='drive',purchased=True,color=GOLD)
    q=add(m,'MOV_LEAD_NUT',hardware.pose(hardware.slide_nut(),(115,1130+travel,967.25),direction=(0,-1,0)),pn='17E19_POM_NUT',group='moving',purchased=True,color=GOLD);moving.append(q.id)
    # Mount flange has sourced31square/22pilot; wiring boot remains separate delivered-part check.
    q=m.add_plate('MOTOR_PLATE',42.3,42.3,6.35,holes=[(21.15,21.15,22.4)]+[(x,z,3.5) for x in (5.65,36.65) for z in (5.65,36.65)],origin=(93.85,1040,946.1),u=(1,0,0),v=(0,0,1),pn='SM_MOTOR_PLATE',color=STEEL)
    # Source normal is-Y: plate extends toward motor, so use explicit forward placement.
    q.shape=q.local.moved(cq.Plane(origin=(93.85,1046.35,946.1),xDir=(1,0,0),normal=(0,-1,0)).location)
    for x in (96.85,127.8):
        add(m,f'MOTOR_SUPPORT_{x}',box(8,9,5.9),(x,1040,988.4),pn='SM_MOTOR_SUPPORT_8_9_5p9',color=STEEL)
    for i,xx in enumerate((99.5,130.5)):
        for j,zz in enumerate((951.75,982.75)):
            s=hardware.pose(cap(3,10,5.5,3),(xx,1036.35,zz),direction=(0,1,0))
            add(m,f'MOTOR_MOUNT_BOLT_{i}_{j}',s,pn='CAP_M3x10',group='fasteners')
    # Nut attachment is a fabricated vertical fork connected to the carrier wing.
    flangeholes=[(15,15,13)]+[(15+9.525*math.cos(math.radians(a)),15+9.525*math.sin(math.radians(a)),3.5) for a in (0,120,240)]
    flangeoutline=[(0,0),(35,0),(35,28.5),(10,28.5),(0,21)]
    flange=plate(flangeoutline,5,holes=flangeholes)
    q=add(m,'MOV_NUT_BRACKET',place(flange,(100,1135+travel,952.25),u=(1,0,0),v=(0,0,1)),pn='SM_NUT_BRACKET',group='moving',color=BLUE);q.local=flange;q.flat={'outline':flangeoutline,'thickness_mm':5,'holes':flangeholes,'slots':[],'internal':[]};moving.append(q.id)
    for i,a in enumerate((0,120,240)):
        xx=115+9.525*math.cos(math.radians(a));zz=967.25+9.525*math.sin(math.radians(a))
        q=add(m,f'MOV_NUT_BOLT_{i}',hardware.pose(cap(3,16,5.5,3),(xx,1119+travel,zz),direction=(0,1,0)),pn='CAP_M3x16',group='moving');moving.append(q.id)
        q=add(m,f'MOV_NUT_WASH_{i}',hardware.pose(cyl(6,.5).cut(cyl(3.2,.5)),(xx,1125.69+travel,zz),direction=(0,1,0)),pn='WASHER_3p2_6_p5',group='moving');moving.append(q.id)
        q=add(m,f'MOV_NUT_NUT_{i}',hardware.pose(nut(2.5,5.5,2.4),(xx,1123.29+travel,zz),direction=(0,1,0)),pn='M3_HEX_NUT',group='moving');moving.append(q.id)
        threaded(m,f'MOV_NUT_BOLT_{i}',q.id)
    q=add(m,'MOV_NUT_TIE',box(10.5,5,5),(128,1130+travel,980.75),pn='SM_NUT_TIE_10p5_5_5',group='moving',color=BLUE);moving.append(q.id)
    # Positive locks: independent guided pin; actuator/cam module follows in lock.py.
    from lock import add_locks
    lock_meta=add_locks(m,unlocked=unlocked)
    if allocations:
        add(m,'UNVERIFIED_MAGAZINE_ACCEPTANCE',box(520,60,80),(315,1070+travel,MAG),pn='UNVERIFIED_ALLOCATION_NOT_PART',purchased=True,group='allocation',color=PINK)
    for p in m.parts:
        if p.group=='fasteners' or p.id.startswith(('MOV_NUT_BOLT_','MOV_NUT_WASH_','MOV_NUT_NUT_')):
            p.purchased=True;p.release='STANDARD FASTENER ENVELOPE - VERIFY PURCHASED GRADE'
    meta={'status':'DETAILED MECHANISM CANDIDATE; actualATC and proposedZ200 interfaces unreleased',
        'travel_mm':travel,'controls_axis_coordinate_mm':200-travel,'unlocked':unlocked,'moving_ids':moving,'rail_base_z':RB,
        'carrier_bottom_z':WT,'magazine_base_z':MAG,'combined_stock_clamp_height_mm':50,
        'magazine_acceptance':{'max_length_mm':520,'nominal_body_width_mm':60,'shown_height_mm':80,
            'max_closed_height_for_5mm_screen_mm':87.65,'clear_tool_window_xy':[335,1065,815,1120],
            'max_projection_below_base_for_5mm_stock_gap_mm':36.55},
        'proposed_Z_travel_mm':200,'confirmed_baseline_Z_travel_mm':100,
        'screw_nut_y_bounds_deployed':[1119,1130],'screw_nut_y_bounds_parked':[1319,1330],
        'screw_end_y':1340,'screw_end_margin_mm':10,'rail_min_end_margins_mm':[10.1,14.1],
        'lock':lock_meta}
    return m,meta

def main():
    HERE.mkdir(exist_ok=True)
    passed=True
    for name,t,un in [('DEPLOYED',0,False),('TRAVELLING',100,True),('PARKED',200,False)]:
        m,meta=build(t,un);r=export(m,HERE/'output','SMALL_'+name,individual=name=='DEPLOYED')
        passed &= not r['unresolved_intersections']
        print(name,r['part_count'],r['unresolved_intersections'],flush=True)
        (HERE/'output'/f'{name}-interface.json').write_text(json.dumps(meta,indent=2)+'\n')
    return 0 if passed else 2
if __name__=='__main__':
    code=main();sys.stdout.flush();sys.stderr.flush();os._exit(code)

