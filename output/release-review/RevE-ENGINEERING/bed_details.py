"""One-piece hoisted bed module: steel ladder, surfaced MDF, full-length 20100 strips.

Rev F bed architecture. The module (MOD_* ids) is removed as ONE piece with the
owner's overhead winch: remove four M8 drawdowns, lift 30 mm, translate forward
out of the open front window, then hoist. Purchased 20100 strips are CUT ONLY;
all tolerance is absorbed by an in-machine surfacing pass on the MDF sub-bed.
"""
import math
import cadquery as cq
from cad_helpers import *

WALL=3.048;TOP=920.8;LIP=1.3
RAIL_SIDE=50.8;RAIL_LEN=1290;RAIL_Y0=30
RAIL_X=((55.0,80.4),(1044.2,1069.6))          # (x0, center) left/right
XM_H=38.1;XM_W=50.8;XM_WALL=3.048              # 2 x 1.5 x .120 crossmember laid flat
XM_X0=105.8;XM_LEN=938.4                       # spans between rail inner faces
XM_TOP=895.4;XM_Z0=XM_TOP-XM_H                 # 857.3, clears Z850 slat tops
MDF_T=12.7;MDF_X0=105.8;MDF_W=938.4;MDF_Y0=76.5;MDF_L=1197
MDF_Z0=XM_TOP                                  # 895.4; two layers end at 920.8
BEAM_STATIONS=(75,475,875,1275)                # crossmember centers, legacy Y
DRAW_Y=(49.6,1300.4)                           # M8 drawdowns, outside deck plan
STRIP_X0=73.5;STRIP_LEN=1197
DECK_STATIONS=(100,350,600,850,1100)           # strip-local Y, all in open bays
NOTCHES=[(1012,565,755),(1012,1162,1232)]      # float-guard notches, world x0,y0,y1
LIFT_MM=60                                     # crossmembers clear Z910 backrails in the slide
SB_X0=(108.0,573.6);SB_W=465.6                 # spoilboards clear guide shoes AND block-bolt heads

def hex_nut(af,height,hole):
    r=af/math.sqrt(3)
    return plate([(r*math.cos(k*math.pi/3),r*math.sin(k*math.pi/3)) for k in range(6)],height,[(0,0,hole)])

def profile_20100(length=STRIP_LEN):
    # Section from exact supplier drawing. Small unnamed transition radii are omitted.
    s=cq.Workplane('XY').box(100,20,length,centered=False).edges('|Z').fillet(1.5).val()
    voids=[]
    for c in (10,30,50,70,90):
        low=[(c-3.1,-.5),(c+3.1,-.5),(c+3.1,1.3),(c+5.5,1.3),
             (c+5.5,2.9),(c+3.9,6.1),(c-3.9,6.1),(c-5.5,2.9),(c-5.5,1.3),(c-3.1,1.3)]
        high=[(x,20-y) for x,y in low]
        for wire in (low,high):voids.append(plate(wire,length+2).translate((0,0,-1)))
        voids.append(cyl(5,length+2).translate((c,10,-1)))
    for c in (20,40,60,80):
        wire=[(c-2.8,1.8),(c+2.8,1.8),(c+2.8,3.3),(c+6.1,6.7),
              (c+6.1,13.3),(c+2.8,16.7),(c+2.8,18.2),(c-2.8,18.2),
              (c-2.8,16.7),(c-6.1,13.3),(c-6.1,6.7),(c-2.8,3.3)]
        voids.append(plate(wire,length+2).translate((0,0,-1)))
    # Side-root transitions are not fully dimensioned. Preserve a nominal diagonal
    # web instead of incorrectly letting side and bottom slot roots touch.
    left=[(-.5,6.4),(1.3,6.4),(1.3,4.5),(2.9,4.5),(5.7,7.6),
          (5.7,12.4),(2.9,15.5),(1.3,15.5),(1.3,13.6),(-.5,13.6)]
    for wire in (left,[(100-x,y) for x,y in left]):voids.append(plate(wire,length+2).translate((0,0,-1)))
    s=s.cut(cq.Compound.makeCompound(voids)).clean()
    return place(s,(0,length,0),u=(1,0,0),v=(0,0,1))

def make_bed(m):
    # --- Fixed-side interface: four drawdown nuts and two dowel bushings in the
    # existing receiver ledgers. All other old receiver machining is deleted.
    dowels=[(RAIL_X[0][1],150),(RAIL_X[1][1],1200)]
    for side,(x0,cx) in enumerate(RAIL_X,1):
        ledger=m.find('MF_RECEIVER_LEDGER_'+str(side))
        tools=[cyl(18,5).translate((cx,dy,836)) for dy in DRAW_Y]
        tools+=[cyl(10.05,5).translate((dx,dy,836)) for dx,dy in dowels if abs(dx-cx)<1]
        ledger.shape=ledger.shape.cut(cq.Compound.makeCompound(tools)).clean()
        bb=bbox(ledger.shape);ledger.local=ledger.shape.translate(tuple(-v for v in bb[:3]))
        ledger.notes.append(f'Module interface: Ø18 nut pockets at Y{DRAW_Y[0]}/{DRAW_Y[1]}, one Ø10.05 dowel bushing hole; through top wall only. Fill sand port relocated to Y1370, behind the module rail span.')
        for ni,dy in enumerate(DRAW_Y,1):
            m.add(f'BED_WELDNUT_{side}_{ni}',hex_nut(13,6.5,8),origin=(cx,dy,833.5),pn='STD_M8_DIN929_NUT',group='fasteners',material='M8DIN929weldnut',purchased=True,color=HARDWARE,
                  notes=['Weld inside ledger below top wall before module fit-up. Four total; drawdowns sit outside the deck plan for straight-down tool access.'])

    # --- Module steel ladder: two rails riding the ledgers, four crossmembers.
    for side,(x0,cx) in enumerate(RAIL_X,1):
        s=box(RAIL_SIDE,RAIL_LEN,RAIL_SIDE).cut(box(RAIL_SIDE-2*WALL,RAIL_LEN+2,RAIL_SIDE-2*WALL).translate((WALL,-1,WALL)))
        tools=[cyl(18,RAIL_SIDE+2).translate((25.4,dy-RAIL_Y0,-1)) for dy in DRAW_Y]
        tools+=[cyl(10,RAIL_SIDE+2).translate((25.4,dy-RAIL_Y0,-1)) for dx,dy in dowels if abs(dx-cx)<1]
        s=s.cut(cq.Compound.makeCompound(tools)).clean()
        m.add(f'MOD_RAIL_{side}',s,origin=(x0,RAIL_Y0,840),pn='MOD_RAIL',group='bed_module',material='A5002x2x.120tube',length=RAIL_LEN,
              notes=['Module side rail bears continuously on the fixed receiver ledger; no feet, seats or shims.',
                     'Ø18 sleeve bores through both walls at the two drawdown stations; Ø10 dowel bore through both walls at one station.',
                     'Weld crossmembers, ears and sleeves, then stress-relieve before MDF fit. Rail tops are NOT precision surfaces; the surfaced MDF absorbs weld tolerance.'])
        for ni,dy in enumerate(DRAW_Y,1):
            m.add(f'MOD_SLEEVE_{side}_{ni}',pipe(RAIL_SIDE,18,9),origin=(cx,dy,840),pn='MOD_COMPRESSION_SLEEVE',group='bed_module',material='Machinedsteel',length=RAIL_SIDE,
                  notes=['OD18 ID9 through both rail walls; weld and finish flush both faces. Carries M8 drawdown preload without crushing the tube.'])
            bolt=cyl(8,70).fuse(cyl(13,8).translate((0,0,70))).clean()
            m.add(f'BED_M8_{side}_{ni}',bolt,origin=(cx,dy,820.8),pn='STD_M8x70_ISO4762',group='removable_hardware',material='M8x70ISO4762class8.8',purchased=True,color=HARDWARE,
                  notes=['One of only four module drawdowns. Remove all four and store in the internal tray before hoisting. Torque 12 Nm onto clean, dry seats.'])
    for di,(dx,dy) in enumerate(dowels,1):
        m.add(f'MOD_DOWEL_{di}',cyl(10,56),origin=(dx,dy,834),pn='STD_DOWEL_10x56',group='bed_module',material='HardenedØ10dowel',purchased=True,color=HARDWARE,
              notes=['Press through both rail walls from above before MDF installation; 6 mm projects below the rail into the ledger bushing hole.',
                     'Two dowels on one diagonal locate the module; the winch lowers the module 30 mm onto them at the end of the reverse path.'])
    for bi,by in enumerate(BEAM_STATIONS,1):
        s=box(XM_LEN,XM_W,XM_H).cut(box(XM_LEN+2,XM_W-2*XM_WALL,XM_H-2*XM_WALL).translate((-1,XM_WALL,XM_WALL)))
        m.add(f'MOD_XM_{bi}',s,origin=(XM_X0,by-XM_W/2,XM_Z0),pn='MOD_CROSSMEMBER',group='bed_module',material='A5002x1.5x.120tube',length=XM_LEN,
              notes=['2 x 1.5 tube laid flat: 50.8 wide MDF seat, 38.1 tall. Butt-weld both ends to rail inner faces; top sits 4.6 mm above rail tops and defines the MDF bearing plane.',
                     'Bottom Z857.3 clears the Z850 plasma slat tops by 7.3 mm installed and 67.3 mm at handling lift, and passes the Z910 float backrails only at handling lift.'])
    ear=[(0,0),(50.8,0),(50.8,40),(32.4,100),(18.4,100),(0,40)]
    for side,(x0,cx) in enumerate(RAIL_X,1):
        for fi,ey in enumerate((RAIL_Y0,RAIL_Y0+RAIL_LEN+6),1):
            m.add_plate(f'MOD_EAR_{side}_{fi}',50.8,100,6,outline=ear,holes=[(25.4,75,16)],origin=(x0,ey,841),u=(1,0,0),v=(0,0,1),
                        pn='MOD_LIFT_EAR',group='bed_module',
                        notes=['6 mm lift ear caps the rail end; continuous 3 mm weld around the tube perimeter. Ø16 hole takes a 6 mm shackle.',
                               'Ear tops finish at Z941 so the module passes 10 mm under the rear-parked Y guide shoes at the 60 mm handling lift.',
                               'Four ears, one 4-leg sling to the overhead winch hook. Hook height at least 1.2 m above the ears; ear holes sit above the module center of mass.'])

    # --- Two-layer MDF sub-bed. Surfaced flat IN THE MACHINE before strips fit.
    def mdf_outline():
        pts=[(0,0),(MDF_W,0)]
        for nx,ny0,ny1 in NOTCHES:
            pts+= [(MDF_W,ny0-MDF_Y0),(nx-MDF_X0,ny0-MDF_Y0),(nx-MDF_X0,ny1-MDF_Y0),(MDF_W,ny1-MDF_Y0)]
        pts+=[(MDF_W,MDF_L),(0,MDF_L)]
        return pts
    deck_screws=[]
    for k in range(10):
        sx=STRIP_X0+100*k
        for si,sy in enumerate(DECK_STATIONS):
            deck_screws.append((sx+(30 if si%2==0 else 70),MDF_Y0+sy))
    teks=[]
    for by,ty in zip(BEAM_STATIONS,(86,475,875,1264)):
        for tx in (220,480,700,960):teks.append((tx,ty))
    holes=[(x-MDF_X0,y-MDF_Y0,5.5) for x,y in deck_screws]+[(x-MDF_X0,y-MDF_Y0,5.7) for x,y in teks]
    for li in range(2):
        s=plate(mdf_outline(),MDF_T,holes=holes)
        ops=[]
        if li==0:
            pockets=[cyl(16,6.001).translate((x-MDF_X0,y-MDF_Y0,-.001)) for x,y in deck_screws]
            s=s.cut(cq.Compound.makeCompound(pockets)).clean()
            ops=[{'type':'circle','x':x-MDF_X0,'y':y-MDF_Y0,'diameter':16,'layer':'MILL_UNDERSIDE_POCKET_DEPTH_6'} for x,y in deck_screws]
            mnotes=['Ø5.5 through holes at 50 deck-screw stations; Ø5.7 at 16 frame-screw stations.',
                    'UNDERSIDE: Ø16 pocket 6.0 deep at each deck-screw station for ISO7380 head and Ø15 washer.',
                    'Pocket layer is NOT a through-cut. Glue faying surface to upper layer at assembly.']
        else:
            pockets=[cyl(12,6.001).translate((x-MDF_X0,y-MDF_Y0,MDF_T-6)) for x,y in teks]
            s=s.cut(cq.Compound.makeCompound(pockets)).clean()
            ops=[{'type':'circle','x':x-MDF_X0,'y':y-MDF_Y0,'diameter':12,'layer':'MILL_TOP_POCKET_DEPTH_6_0'} for x,y in teks]
            mnotes=['Ø5.5/Ø5.7 through holes as lower layer; TOP Ø12 pocket 6.0 deep at 16 frame-screw stations keeps heads 3 mm below the surfacing pass.',
                    'Surface this face 1.0 mm nominal IN THE MACHINE after frame screws are torqued; maximum additional reface 1.0 mm before layer replacement.',
                    'Seal edges and underside after surfacing; the top face stays bare under the aluminum.']
        f={'outline':mdf_outline(),'thickness_mm':MDF_T,'holes':holes,'slots':[],'internal':[],'operations':ops,'machining_notes':mnotes}
        m.add(f'MOD_MDF_L{li+1}',s,origin=(MDF_X0,MDF_Y0,MDF_Z0+li*MDF_T),pn='BED_MDF_'+('LOWER' if li==0 else 'UPPER'),group='bed_module',
              material='MDF 1/2-inch, finish 12.7',color=(.66,.50,.31),flat=f,
              notes=['938.4 x 1197 sub-bed layer with two right-edge notches clearing the pan float guards and backrails.',
                     'The machine surfaces the assembled stack, so ledger, weld and MDF thickness tolerances do not reach the aluminum bed.'])
    for ti,(x,y) in enumerate(teks,1):
        s=cyl(5.5,29).fuse(cyl(11,3).translate((0,0,29))).clean()
        p=m.add(f'MOD_TEK_{ti}',s,origin=(x,y,885.8),pn='STD_12-14x32_TEK',group='bed_module_hardware',material='#12-14x32 self-drilling screw',purchased=True,color=HARDWARE,
                notes=['Fastens both MDF layers to a crossmember top wall; head finishes 3 mm below the pre-surfacing MDF top.'])
        xm=next(q for q in m.parts if q.id.startswith('MOD_XM_') and bbox(q.shape)[1]<y<bbox(q.shape)[4])
        m.permit(p.id,xm.id,'Self-drilling screw thread pierces the 3.048 crossmember top wall.')

    # --- Ten cut-only purchased strips, screwed to the surfaced MDF from below.
    nominal=profile_20100()
    area=nominal.Volume()/STRIP_LEN
    inertia=cq.Shape.matrixOfInertia(nominal)[0][0]/STRIP_LEN-area*STRIP_LEN**2/12
    tnut=box(8,8,2.7).translate((-4,-4,0)).cut(cyl(5,2.7)).clean()
    for k in range(10):
        sx=STRIP_X0+100*k
        m.add(f'MOD_STRIP_{k+1}',nominal,origin=(sx,MDF_Y0,TOP),pn='BUY_20100_1197',group='bed_module',material='Purchased6063T5profile',color=ALU,purchased=True,
              notes=['Section uses actual100×20/6.2opening/7.8root/Ø5cores/1.3lips/outerR1.5supplier dimensions.',
                     'ONE saw cut per purchased 1220 bar: finish 1197, no drilling, no other machining. Slots run front-to-back with no seams.',
                     'Unnamed internal transition details approximated;do not machine an extrusion fromthismodel.'])
        for si,sy in enumerate(DECK_STATIONS):
            cxs=sx+(30 if si%2==0 else 70);wy=MDF_Y0+sy
            pre=f'MOD_DECK_{k+1}_{si+1}'
            screw=cyl(5,25).fuse(cyl(9.5,2.75).translate((0,0,-2.75))).clean()
            sc=m.add(pre+'_SCREW',screw,origin=(cxs,wy,899.9),pn='STD_M5x25_ISO7380',group='bed_module_hardware',material='M5x25 button head screw',purchased=True,color=HARDWARE,
                     notes=['Installed upward with the module on stands after the surfacing pass; 6 mm hex, thread into the bottom-slot square nut.'])
            m.add(pre+'_WASHER',pipe(1.5,15,5.3),origin=(cxs,wy,899.9),pn='STD_M5_FENDER_15',group='bed_module_hardware',material='M5 fender washer 15x5.3x1.5',purchased=True,color=HARDWARE)
            nut=m.add(pre+'_NUT',tnut,origin=(cxs,wy,TOP+LIP),pn='STD_DIN562_M5',group='bed_module_hardware',material='DIN562M5square nut8x8x2.7',purchased=True,color=HARDWARE,
                      notes=['End-load into the strip bottom slot before placing the strip; nut seats on the 1.3 mm lips.'])
            m.permit(sc.id,nut.id,'M5 thread engages the square nut inside the bottom slot.')

    # --- Optional spoilboards: two full-length boards retained in the top slots.
    # Trimmed to X108..1039.2 so their raised tops pass between the guide-shoe
    # bands and their protruding block-bolt heads during the 60 mm handling
    # lift; usable cutting X175..975 is unaffected.
    for ci,bx in enumerate(SB_X0,1):
        firstslot=(STRIP_X0+50)+100*(5*(ci-1))
        boardholes=[(firstslot+100*k-bx,yy,5.5) for k in range(5) for yy in (90,1107)]
        board=plate(rect(SB_W,MDF_L),19,holes=boardholes)
        for xx,yy,d in boardholes:
            pocket=cyl(10,4).translate((xx,yy,16)).fuse(cq.Solid.makeCone(2.75,5,2.25).translate((xx,yy,13.75))).clean()
            board=board.cut(pocket)
        flat={'outline':rect(SB_W,MDF_L),'thickness_mm':19,'holes':boardholes,'slots':[],'internal':[],
              'operations':[{'type':'circle','x':xx,'y':yy,'diameter':10,'layer':'MILL_TOP_POCKET_DEPTH_3_PLUS_CSK'} for xx,yy,_ in boardholes],
              'machining_notes':['Finish 3/4-inch MDF to 19.000 mm thickness before machining.',
                 'Ten5.5mm fixing holes:10mm diameter counterbore3mm deep, then90degree countersink2.25mm deeper.',
                 'M5x20 DIN7991 heads finish3mm below board surface; maximum routine skim2mm before removing or replacing the board.']}
        m.add(f'MOD_SB_{ci}',board.clean(),origin=(bx,MDF_Y0,TOP+20),pn=f'SPOILBOARD_{"L" if ci==1 else "R"}_466x1197',group='bed_module',material='MDF 3/4-inch, finish19mm',color=(.66,.50,.31),flat=flat,
              notes=['465.6 x 1197 optional spoilboard, one per five strips; both boards from a single 1220 x 2440 sheet.',
                     'Deck edges outside X108..1039.2 stay uncovered; nominal cutting X175..975 lies fully on the boards.',
                     'Boards stay on the module through the hoist; remove them only for plasma-mode dust control or replacement.'])
        for hi,(xx,yy,d) in enumerate(boardholes,1):
            screw=cyl(5,17.5).fuse(cq.Solid.makeCone(2.5,5,2.5).translate((0,0,17.5))).clean()
            sc=m.add(f'MOD_SB_{ci}_SCREW_{hi}',screw,origin=(bx+xx,MDF_Y0+yy,TOP+16),pn='STD_M5x20_DIN7991',group='bed_module_hardware',material='M5x20 countersunk screw',purchased=True,color=HARDWARE)
            nut=m.add(f'MOD_SB_{ci}_NUT_{hi}',tnut,origin=(bx+xx,MDF_Y0+yy,TOP+16),pn='STD_DIN562_M5',group='bed_module_hardware',material='DIN562 M5 square nut8x8x2.7',purchased=True,color=HARDWARE)
            m.permit(sc.id,nut.id,'M5 thread engages the square nut inside the strip top slot.')

    steel=sum(p.shape.Volume() for p in m.parts if p.id.startswith(('MOD_RAIL','MOD_XM','MOD_EAR','MOD_SLEEVE')))*7.85e-6
    mdf=sum(p.shape.Volume() for p in m.parts if p.id.startswith(('MOD_MDF','MOD_SB_1','MOD_SB_2')) and p.material.startswith('MDF'))*7.5e-7
    alu=area*STRIP_LEN*10*2.7e-6
    module_mass=steel+mdf+alu+2.5
    return {'bare_deck_mm':[1000,1197,20],'workplane_z_mm':940.8,
            'module_stack':'Ledger 840 > rail top 890.8 > crossmember (2x1.5 flat) top 895.4 > MDF 25.4 > strip bottom 920.8 > bare T-slot 940.8 > optional spoilboard 959.8',
            'profile_nominal_section_area_mm2':area,'profile_nominal_Ixx_mm4':inertia,
            'profile_section_properties_status':'Computed from nominal reconstructed supplier section;not manufacturer-certified.',
            'module_drawdown_M8':4,'deck_M5_fasteners':50,'frame_TEK_fasteners':16,'lift_ears':4,
            'module_mass_estimate_kg':round(module_mass,1),
            'module_mass_basis':'Nominal solids: steel 7850, MDF 750, aluminum from reconstructed section area; plus 2.5 kg fastener allowance. Weigh before first hoist.',
            'handling':'Owner overhead winch, rated 567 kg (1250 lb); estimated module below 90 kg. 4-leg sling to four Ø16 ear holes.',
            'sequence':'Remove four M8 drawdowns to the tray, take slack in the sling, lift 60, winch forward out the front window, hoist clear. Reverse to install; dowels engage on the final descent.',
            'surfacing':'Torque frame screws, then face the upper MDF 1.0 nominal in-machine before strip installation. Reface only after module reinstallation, never after strips are fitted.',
            'source_profile':'https://m.media-amazon.com/images/I/71myeCep6iL._SL1500_.jpg',
            'source_square_nut':'https://norelem.co.uk/medias/07209-01-Datasheet-34408-Square-nuts-DIN-562-low-type-en.pdf'}
