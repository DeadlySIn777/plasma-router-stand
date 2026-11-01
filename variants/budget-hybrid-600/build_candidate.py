"""Review geometry for the nine-foot hybrid. Dimensions in millimetres."""
import json
from pathlib import Path
import sys
import cadquery as cq

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'extrusion-wood-plasma'
sys.path.insert(0, str(BASE))
from frame import bar, box, cyl, frame_parts, bolted_datums
from process_bed import tube_x, tube_y, tube_z, yz

OUT = HERE / 'review'
S = 31.75
T = 1.90
PAN = 2.6568
OVERFLOW_X = 520.
STATIONS = (100., 725., 1330.)
XS = (30.8, 1119.2)
GRAY, DARK, BLUE, AL, WOOD = (.44,.49,.52), (.20,.31,.36), (.12,.40,.51), (.66,.71,.73), (.73,.55,.34)

def pieces():
    common, dry, wet = [], [], []
    def add(name, solid, color=GRAY, target=common):
        target.append((name, solid, color))
    def flatbrace(name, a, b, normal):
        delta = cq.Vector(*b)-cq.Vector(*a)
        plane = cq.Plane(origin=a, xDir=delta.normalized().toTuple(), normal=normal)
        stock = cq.Workplane(plane).center(delta.Length/2,0).rect(delta.Length+25.4,25.4).extrude(3.175).val()
        add(name, stock, BLUE)
    for k,x in enumerate(XS):
        side = 'LR'[k]
        add(side+'_motion_4040',bar(x-20,0,1016,'Y',1450),DARK)
        backing=tube_y(x-S/2,0,1016-S,S,1450,S,T)
        for y in STATIONS:
            for yy in (y-31,y+31):
                backing=backing.cut(cyl(3.3,5,(x,yy,1012))).cut(cyl(6.2,5,(x,yy,983.5)))
        add(side+'_steel_backing',backing.clean(),BLUE)
        for i,y in enumerate(STATIONS):
            add(f'{side}_column_{i}',tube_z(x-S/2,y-S/2,69.5,S,S,1016-S-69.5,T))
            ix = x+S/2 if not k else x-S/2-33
            add(f'{side}_end_bearing_seat_{i}',box(ix,y-S/2,799.5-S-4.76,33,S,4.76))
        for i,(y1,y2) in enumerate(zip(STATIONS,STATIONS[1:])):
            # Opposite faces allow both welded straps to pass without crossing.
            for j,(zl,zh,n) in enumerate(((150,950,-1),(950,150,1))):
                px=x+n*S/2
                flatbrace(f'{side}_wall_X_{i}_{j}',(px,y1,zl),(px,y2,zh),(n,0,0))
    for j,y in enumerate((STATIONS[0],STATIONS[-1])):
        for k,(zl,zh,n) in enumerate(((245,830,-1),(830,245,1))):
            yp=y+n*S/2
            flatbrace(f'end_X_{j}_{k}',(XS[0],yp,zl),(XS[1],yp,zh),(0,n,0))
    for i,y in enumerate(STATIONS):
        add(f'bearer_{i}',tube_x(XS[0]+S/2,y-S/2,799.5-S,XS[1]-XS[0]-S,S,S,T),BLUE)
        add(f'center_post_{i}',tube_z(575-S/2,y-S/2,69.5,S,S,799.5-S-69.5,T))
        for k,x in enumerate((XS[0],575.,XS[1])):
            pad=cyl(20,8,(x,y,0)).fuse(cyl(4,56.74,(x,y,8)),box(x-S/2,y-S/2,64.74,S,S,4.76))
            add(f'foot_{i}_{k}_envelope',pad.clean(),DARK)
        for k,x in enumerate((136.5,1013.5)):
            add(f'deck_riser_{i}_{k}',tube_z(x-12.7,y-12.7,799.5,25.4,25.4,118.025,1.5))
    for k,x in enumerate((370.,780.)):
        add(f'pan_4040_{k}',bar(x-20,0,799.5,'Y',1450),DARK)
        for i,y in enumerate(STATIONS):
            for j,n in enumerate((-1,1)):
                low=y+S/2 if n>0 else y-43
                tab=box(x-12,low,796.325,24,43-S/2,3.175)
                add(f'pan_slot_tab_{k}_{i}_{j}',tab.cut(cyl(3.3,5,(x,y+n*31,796))),BLUE)
        top=[(55,852.),(1085,857.15)]
        cap=yz(x-12.7,25.4,[(y,z-3.175) for y,z in top]+list(reversed(top)))
        for side,width in ((x-12.7,3.175),(x+12.7-1.90,1.90)):
            cap=cap.fuse(yz(side,width,[(55,839.5),(1085,839.5),(1085,857.15-3.175),(55,852.-3.175)]))
        add(f'pan_sloped_channel_{k}',cap.clean())
        # Capture the pan outside its wet floor. Tabs bear on posts at both end walls.
        for j,y in enumerate((55.,1085.)):
            py=y-18 if not j else y
            cy=py+9
            slot=cyl(5,8,(x,cy,864 if not j else 869.15))
            if j or k: slot=slot.fuse(cyl(5,8,(x+2,cy,864 if not j else 869.15)),box(x,cy-5,864 if not j else 869.15,2,10,8))
            z=866+j*5.15
            add(f'pan_ear_{k}_{j}',box(x-14,py,z,28,18,3.175).cut(slot),BLUE)
            add(f'pan_capture_boss_{k}_{j}',cyl(6.8,z-839.5,(x,cy,839.5)).cut(cyl(3.3,z-838,(x,cy,839.4))))
            add(f'pan_shoulder_keeper_{k}_{j}',cyl(4.7,4,(x,cy,z)).fuse(cyl(8,2.4,(x,cy,z+4))).cut(cyl(3.15,7,(x,cy,z-.1))),AL)
    # Outside the wet pan and all kerf paths: sheet skirts return into short dry-side tabs.
    for k,x in enumerate((84.,1064.)):
        add(f'side_heat_shield_{k}',box(x,49,868,1.9,1120,94),DARK)
        for j,y in enumerate(STATIONS[:2]):
            x0=85.9 if not k else 1026.2
            add(f'shield_tab_{k}_{j}',box(x0,y-6,905,37.9 if not k else 37.8,12,3.175),BLUE)
    for k,x0 in enumerate((129.,995.6)):
        # Seats face inward, with steel bearing directly on each welded riser.
        xleg=x0 if k==0 else x0+25.4-3.175
        ledge=box(x0,60,917.525,25.4,1335,3.175).fuse(box(xleg,60,895.3,3.175,1335,22.225))
        # Remove leg material where each riser bears under the shelf.
        for y in STATIONS:
            rx=(136.5,1013.5)[k]-12.7
            ledge=ledge.cut(box(rx,y-12.7,799.5,25.4,25.4,118.025))
        for i in range(4):
            for offset in (34.7,224.7):
                ledge=ledge.cut(cyl(3.3,6,(x0+12.7,103.4+i*259+offset,916)))
            yp=103.4+i*259+129
            ledge=ledge.cut(cyl(3,7,(x0+12.7,yp,916)))
            add(f'locator_{k}_{i}',cyl(3,8,(x0+12.7,yp,917.525)),AL)
        add(f'dry_ledger_{k}',ledge.clean(),BLUE)
        for j,(a,b) in enumerate(((116.,709.),(741.,1314.))):
            add(f'dry_ledger_stiffener_{k}_{j}',box(xleg,a,870.3,1.9,b-a,25),BLUE)
    for n,s,c in frame_parts():
        if n.startswith('CAP_'): add(n,s,c)
    def floor(y): return 852+(y-55)*.005
    add('pan_floor',yz(160,830,[(55,floor(55)),(1085,floor(1085)),(1085,floor(1085)+PAN),(55,floor(55)+PAN)]),DARK)
    for i,x in enumerate((160.,990.-PAN)):
        add(f'pan_side_{i}',yz(x,PAN,[(55,floor(55)+PAN),(1085,floor(1085)+PAN),(1085,floor(1085)+50),(55,floor(55)+50)]),DARK)
    for i,y in enumerate((55.,1085.-PAN)):
        wall=yz(160+PAN,830-2*PAN,[(y,floor(y)+PAN),(y+PAN,floor(y+PAN)+PAN),(y+PAN,floor(y+PAN)+50),(y,floor(y)+50)])
        if not i: wall=wall.cut(cyl(10,6,(305,y-1,866.5),(0,1,0))).cut(box(OVERFLOW_X-40,y-1,852+PAN+39,80,7,12))
        add(f'pan_end_{i}',wall,DARK)
    # Drop box connects the pan's low wall opening to a welded 1 in nominal nipple.
    # The actual valve installation and open overflow remain accessible from below.
    drainbox=box(282,10,824,46,45,56).cut(box(283.9,11.9,825.9,42.2,43.2,52.2))
    drainbox=drainbox.cut(cyl(16.8,4,(305,32.5,823)))
    add('drain_drop_box',drainbox,DARK)
    add('drain_1in_nipple_envelope',cyl(16.7,50.8,(305,32.5,775.1)).cut(cyl(13,52,(305,32.5,774.9))),GRAY)
    # Open formed chutes. The gap below the removable manual valve is reserved for
    # the selected fitting stack. The separate overflow bypasses that valve.
    for label,x,y0,z0,y1,z1 in (('drain',305.,16.,665.,267.,317.),('overflow',OVERFLOW_X,21.,825.,265.,310.)):
        w,t=62.,1.9
        chute=yz(x-w/2,w,[(y0,z0-t),(y1,z1-t),(y1,z1),(y0,z0)])
        for edge in (x-w/2,x+w/2-t):
            chute=chute.fuse(yz(edge,t,[(y0,z0),(y1,z1),(y1,z1+12),(y0,z0+12)]))
        add(f'open_{label}_chute',chute.clean(),GRAY)
    # Full-width receiver lip and central bottom outlet collect the whole notch.
    hood=box(OVERFLOW_X-43,22,847,86,33,56).cut(box(OVERFLOW_X-41.1,23.9,848.9,82.2,31.2,56))
    hood=hood.cut(box(OVERFLOW_X-20,28,846.5,40,14,4))
    add('overflow_splash_hood',hood.clean(),BLUE)
    slatys=[79.0+i*108.5 for i in range(10)]
    for k,x in enumerate((175.,575.,975.)):
        comb=yz(x-1.5875,3.175,[(62,floor(62)+PAN),(1079,floor(1079)+PAN),(1079,floor(1079)+PAN+31.75),(62,floor(62)+PAN+31.75)])
        for y in slatys: comb=comb.cut(box(x-3,y-.3,881,7,PAN+.6,18))
        for y in range(93,1060,115): comb=comb.cut(box(x-3,y,floor(y)+PAN-.2,7,16,7))
        add(f'comb_{k}',comb.clean())
    for i,y in enumerate(slatys): add(f'slat_{i:02}',box(163,y,881,824,PAN,30))
    for i in range(4):
        parts=[]
        for j,off in enumerate((22.,117.,212.)):
            tube=tube_x(129,off,0,892,25.4,50.8,1.5)
            if j!=1:
                for x in (141.7,1008.3):
                    tube=tube.cut(cyl(3.3,4,(x,off+12.7,-1))).cut(cyl(6,4,(x,off+12.7,48)))
                for x in (236.,914.):tube=tube.cut(cyl(3.3,4,(x,off+12.7,48)))
                if j==0:
                    # Inside doubler takes the parked carrier's M5 hold-down.
                    # The 5 mm thread envelope is for clash review, not the tap drill.
                    tube=tube.fuse(box(935,off+1.5,20.4,10,4.76,10))
                    tube=tube.cut(cyl(2.5,8,(940,off-.1,25.4),(0,1,0))).clean()
            else:
                for k,x in enumerate((141.7,1008.3)):
                    hole=cyl(3.15,7,(x,129,-1))
                    if k: hole=hole.fuse(cyl(3.15,7,(x+1.5,129,-1)),box(x,125.85,-1,1.5,6.3,7))
                    tube=tube.cut(hole)
            parts.append((f'bridge_{i}_crossrail_{j}',tube,BLUE))
        for j,x in enumerate((129,995.6)):
            for k,st in enumerate((47.4,142.4)):
                parts.append((f'bridge_{i}_end_tie_{j}_{k}',tube_y(x,st,0,25.4,69.6,25.4,1.5),BLUE))
        y=103.4+i*259
        for n,s,c in parts:
            dry.append((n,s.translate((0,y,920.7)),c))
            wet.append((n,s.rotate((0,0,0),(1,0,0),90).translate((0,1281+55*i,903)),c))
        board=box(162,1,50.8,826,255,12)
        for x in (236.,914.):
            for off in (34.7,224.7):
                board=board.cut(cyl(3.3,14,(x,off,50.1))).cut(cq.Solid.makeCone(6.1,3.3,2.8,cq.Vector(x,off,62.8),cq.Vector(0,0,-1)))
        dry.append((f'wood_only_backer_{i}',board.translate((0,y,920.7)),WOOD))
    # Raised rack over the rear crossframe; open approach above the dry ledgers.
    for k,x in enumerate((205.,946.)):
        add(f'rack_riser_{k}',tube_z(x,1304.6,799.5,25.4,50.8,920.24-799.5,1.5),GRAY)
        add(f'rack_shelf_{k}',box(x,1228,920.24,25.4,222,4.76),BLUE)
        if k==1:
            for i in range(4):
                yp=1281+55*i-25.4
                lug=box(933,yp-9,920.24,13,18,4.76).cut(cyl(2.75,6,(940,yp,920)))
                add(f'rack_keeper_lug_{i}',lug,BLUE)
                screw=cyl(2.45,14,(940,yp,920.24)).fuse(cyl(4.5,4.8,(940,yp,915.44)))
                add(f'locked_storage_M5_{i}',screw,AL,wet)
        for j,(a,b) in enumerate(((1228.,1304.6),(1355.4,1450.))):
            add(f'rack_shelf_web_{k}_{j}',box(x+11.75,a,895.24,1.9,b-a,25),BLUE)
        for j,y in enumerate((1227.8,1282.4,1337.4,1392.4,1447.4)):
            add(f'rack_separator_{k}_{j}',box(x,y,925,25.4,1.9,22),GRAY)
    for k,(a,b) in enumerate(((XS[0],575.),(575.,XS[1]))):
        add(f'rack_cross_tie_{k}',tube_x(a+S/2,1330-S/2,502.24-S,b-a-S,S,S,T),BLUE)
    # Gross outside envelope only. The seller's 15 US gal capacity controls.
    add('receiver_open_steel_15gal_envelope',cyl(276.25,273,(345,365,0)).cut(cyl(274.75,273,(345,365,1.5))),AL)
    return common,dry,wet

def main():
    from build import clashes, export
    from motion_context import motion_parts
    OUT.mkdir(parents=True,exist_ok=True)
    fixed,dry,wet=pieces()
    report={}
    fixed_check=clashes(fixed,fixed,True)
    phase_names=('L_motion_','R_motion_','L_steel_backing','R_steel_backing','L_column_','R_column_',
                 'L_end_bearing_','R_end_bearing_','L_wall_X_','R_wall_X_','end_X_','bearer_','center_post_',
                 'foot_','pan_4040_','pan_slot_tab_')
    stand=[part for part in fixed if part[0].startswith(phase_names)]
    report['STAND']={'export':export(OUT/'STAND.step',stand),'frame':clashes(stand,stand,True)}
    for mode,deck,hot in [('CARVING',dry,False),('PLASMA',wet,True)]:
        motion=bolted_datums(motion_parts(hot))
        allparts=fixed+deck+motion
        if not all(s.isValid() for _,s,_ in allparts): raise ValueError('Invalid solid')
        report[mode]={'export':export(OUT/(mode+'.step'),allparts),
                      'frame_and_bed':fixed_check,'deck_vs_fixed':clashes(deck,fixed),
                      'deck_self':clashes(deck,deck,True),'motion_vs_frame_deck_display_pose':clashes(motion,fixed+deck)}
    (OUT/'geometry.json').write_text(json.dumps(report,indent=2))
    print({m:{k:len(v.get('interferences_gt_0p05_mm3',[])) for k,v in c.items()} for m,c in report.items()})
if __name__=='__main__': main()
