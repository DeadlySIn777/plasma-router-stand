"""Rev G manual in-footprint bed: six panels, four beams, internal storage.

Nominal engineering repair, not a released load rating. User confirmation of
manual handling remains pending. All exchange masses are dry, without work.
The bought extrusion is cut only. T-slot nut preload requires a sample test.
"""
import copy
import math
import cadquery as cq
from cad_helpers import *
from bed_details import profile_20100

TOP = 920.8
PANEL_X = (73.5, 576.5)
PANEL_Y = (76.5, 483.5, 890.5)
PANEL_L = 397.0
BEAM_Y = (65.0, 478.5, 885.5, 1299.0)
TIE_T = 9.525
PANEL_STORE_Y = (7.0,47.0,87.0,127.0,167.0,207.0)
BEAM_STORE = ((90.0,585.0),(0.0,585.0),(90.0,641.8),(0.0,641.8))
SPOIL_X = (180.0,576.5)
SPOIL_Y = ((130.0,473.5),(483.5,880.5),(890.5,1110.0))
SPOIL_STORE_SLOT = (2,3,4,5,0,1)
_PLACEMENTS = {}

def register(p, kind, index, datum):
    _PLACEMENTS[p.id] = (kind, index, tuple(datum))
    return p

def hollow_z(w,d,h,wall=3.048):
    return box(w,d,h).cut(box(w-2*wall,d-2*wall,h+2).translate((wall,wall,-1))).clean()

def transformed_to_storage(p):
    """Return stored world shape; each rigid set keeps its original local solid."""
    record = _PLACEMENTS.get(p.id)
    if record is None:return p.shape
    kind,index,datum = record
    local = p.shape.translate(tuple(-v for v in datum))
    if kind == 'panel':
        return local.rotate((0,0,0),(1,0,0),90).translate((325,PANEL_STORE_Y[index]+20,175))
    if kind == 'beam':
        fy,z = BEAM_STORE[index]
        return local.rotate((0,0,0),(1,0,0),90).translate((113,fy+78.8,z))
    if kind == 'spoil':
        # Stand the 393.5 mm X dimension vertically; handle the long boards
        # first into the rightmost slots, shorter boards later into the left.
        length=SPOIL_Y[index//2][1]-SPOIL_Y[index//2][0]
        return place(local,(135+23*SPOIL_STORE_SLOT[index],250+length,175),u=(0,0,1),v=(0,-1,0))
    if kind == 'beam_bolt':
        # Head down on the storage tray, shank supported by a drilled guide.
        return local.rotate((0,0,0),(1,0,0),180).translate((285+25*(index%2),630+18*(index//2),272))
    if kind == 'clamp':
        return local.translate((285+25*(index%2),315+40*(index//2),184))
    if kind == 'spoil_bolt':
        # Removed spoilboard screws in the existing hardware bin, head down.
        return local.rotate((0,0,0),(1,0,0),180).translate((810+11*(index%8),735+12*(index//8),456.144))
    if kind == 'spoil_nut':
        # Remove loose top-slot nuts before rotating panels, then thread each
        # onto its removed spoilboard screw in the internal hardware tray.
        return local.translate((810+11*(index%8),735+12*(index//8),442.144))
    if kind == 'front_seat':
        return local.rotate((0,0,0),(1,0,0),180).translate((310+100*index,910,442.096))
    if kind == 'front_seat_bolt':
        return local.rotate((0,0,0),(1,0,0),180).translate((325+35*index,815,464.096))
    raise ValueError(record)

def stored_bed_model(source):
    # OCC shape deep-copy/pickle is unreliable; transforms return new immutable
    # shapes, while mutable notes/flat metadata are copied explicitly.
    m=Model();m.allowed_intersections=dict(source.allowed_intersections);m.holds=list(source.holds)
    for original in source.parts:
        p=copy.copy(original);p.notes=list(original.notes);p.flat=copy.deepcopy(original.flat)
        m.parts.append(p)
    for p in m.parts:
        if p.id in _PLACEMENTS:
            p.shape=transformed_to_storage(p)
            p.notes.append('Stored within the stand for plasma layout. Empty the racks by reinstalling the bed before opening the controls cabinet.')
    return m

def make_bed(m):
    _PLACEMENTS.clear()
    # The end regions lie below the fixed seats and removable beam feet. Relieve
    # the replaceable slats, keeping 810 mm central support through X170..980.
    # This is an actual flat-pattern change, not an allowed collision.
    slat_outline=[(0,0),(880,0),(880,53),(845,53),(845,75),(35,75),(35,53),(0,53)]
    for p in m.parts:
        if p.id.startswith('WP_SLAT_'):
            bb=bbox(p.shape);p.local=plate(slat_outline,3.048)
            p.shape=place(p.local,(135,bb[4],775),u=(1,0,0),v=(0,0,1))
            p.flat={'outline':slat_outline,'thickness_mm':3.048,'holes':[],'slots':[],'internal':[]}
            p.notes.append('Rev G: relieve upper 22 mm over each 35 mm end. Central X170..980 remains at Z850 (810 mm support width); relieved ends top Z828 clear the bed seats/feet. Comb stations X195/955 unchanged.')
    # Full bearing plates on top of the ledger, not nuts hanging in oversize holes.
    # Plate overhang stays above the pan rim, five millimeters nominal clearance.
    for bi,by in enumerate(BEAM_Y):
        for side,(sx,bx) in enumerate(((75.0,138.0),(985.0,1012.0))):
            holes=[(bx-sx,30,8)]
            if side==0:holes.append((bx-sx,55,6.03))
            slots=[] if side==0 else [(bx-sx,55,12,6.03,0)]
            p=m.add_plate(f'G_SEAT_{bi+1}_{side+1}',90,80,6,holes=holes,slots=slots,origin=(sx,by-40,840),pn=f'G_SEAT_{"ROUND" if side==0 else "RELIEVED"}',group='bed_fixed',
                notes=['6 mm steel plate bears on the ledger top over 26.6 mm width. Finish seat after welding; nominal pan rim gap 5 mm, plasma support plane clearance 4 mm.',
                       'Continuous 3 mm fillets along accessible ledger contact edges. Verify actual tube corner and weld access before fabrication.',
                       'After welding, drill 6.8 and tap M8 through plate and attached boss. Match-ream left locator to 6.03 +0.01/-0.00; right slot is relieved along X. Measure actual dowels before final reaming.'])
            p.flat['holes'][0]=(bx-sx,30,6.8)
            p.flat['machining_notes']=['M8 station: drill 6.8 and tap through plate and welded boss AFTER welding.','Locator bore/slot final width 6.03 +0.01/-0.00; match to measured nominal 6 mm pin. Seat coplanarity and repeatability must be measured.']
            if bi == 0:
                # The front portal must open after the first beam is temporarily
                # parked on its side on beam 2. Permanent overhanging seats here
                # would trap every full-width crossbeam above the ledgers.
                mount_x=88.0 if side==0 else 1062.0
                mount_holes=[(mount_x-sx,yy-(by-40),8.5) for yy in (45.0,85.0)]
                p.local=p.local.cut(cq.Compound.makeCompound([cyl(8.5,8).translate((xx,yy,-1)) for xx,yy,_ in mount_holes])).clean()
                p.shape=place(p.local,(sx,by-40,840))
                p.flat['holes'].extend(mount_holes)
                p.part_number='G_FRONT_SEAT_'+('ROUND' if side==0 else 'RELIEVED')
                p.notes=[n for n in p.notes if not n.startswith('Continuous 3 mm fillets')]
                p.notes.extend(['REMOVABLE front seat: two M8x20 screws with washers attach it to welded, threaded compression sleeves in the ledger. Do not weld this seat to the ledger.',
                    'Park beam 1 on its side on beam 2 before unbolting either front seat. Refit the seats, map all four beam elevations and re-probe after conversion; clearance bolts do not establish precision relocation.'])
                register(p,'front_seat',side,(sx,by-40,840))
                ledger=m.find('MF_RECEIVER_LEDGER_'+str(side+1))
                ledger.shape=ledger.shape.cut(cq.Compound.makeCompound([cyl(18,52.8).translate((mount_x,yy,788.2)) for yy in (45.0,85.0)])).clean()
                bb=bbox(ledger.shape);ledger.local=ledger.shape.translate(tuple(-v for v in bb[:3]))
                ledger.notes.append('Front removable seat: two OD18 compression/thread sleeves at global X'+str(mount_x)+', Y45/85; bores through both walls. Weld sleeves before ballast; finish top flush Z840. Do not drill a sand-filled member.')
                for j,yy in enumerate((45.0,85.0)):
                    m.add(f'G_FRONT_LEDGER_SLEEVE_{side+1}_{j+1}',pipe(50.8,18,8),origin=(mount_x,yy,789.2),pn='G_FRONT_LEDGER_M8_SLEEVE',group='bed_fixed',material='Machined steel',
                        notes=['OD18 x 50.8 compression sleeve, nominal M8 thread envelope. Predrill 6.8 and tap M8x1.25 at least 22 deep from the top after welding to BOTH ledger walls; finish flush. Check seat-to-ledger load transfer before fabrication release.'])
                    datum_b=(mount_x,yy,827.6)
                    fast=cyl(8,20).fuse(cyl(13,8).translate((0,0,20))).clean()
                    register(m.add(f'G_FRONT_SEAT_BOLT_{side+1}_{j+1}',fast,origin=datum_b,pn='STD_M8x20_SOCKET',group='bed_release_hardware',material='Steel M8x20',purchased=True,color=HARDWARE,
                        notes=['Remove only with front beam independently supported on beam 2. Qualify preload and repeat seating; no automatic return-to-zero is claimed.']), 'front_seat_bolt',2*side+j,datum_b)
                    register(m.add(f'G_FRONT_SEAT_WASHER_{side+1}_{j+1}',pipe(1.6,16,8.4),origin=(mount_x,yy,846),pn='STD_M8_WASHER',group='bed_release_hardware',material='Steel washer',purchased=True,color=HARDWARE),'front_seat_bolt',2*side+j,datum_b)
            m.add(f'G_SEAT_BOSS_{bi+1}_{side+1}',pipe(6,20,8),origin=(bx,by-10,834),pn='G_M8_SEAT_BOSS',group='bed_fixed',material='Machined steel',
                  notes=['OD20 x 6 boss bears against the underside of the 6 mm seat plate; continuous 3 mm circular fillet. Drill/tap M8 through both pieces after welding. No gap-bridging nut weld.'])
            if bi==0:register(m.parts[-1],'front_seat',side,(sx,by-40,840))
        # One short beam fits between the stationary ledgers during vertical transfer.
        s=tube(924)
        cutters=[]
        for bx in (138,1012):
            cutters.append(cyl(18,54).translate((bx-113,15.4,-1)))
        for x in (123.5,523.5,626.5,1026.5):
            cutters.append(cyl(6,5).translate((x-113,25.4,46.8)))
        s=s.cut(cq.Compound.makeCompound(cutters)).clean()
        datum=(113,by-25.4,842)
        register(m.add(f'G_BEAM_{bi+1}',s,origin=(113,by-25.4,870),pn='G_BED_BEAM_924',group='bed_beam',material='A5002x2x.120tube',length=924,
            notes=['924 mm single 2 x 2 x .120 transverse beam. Top Z920.8. End feet are removable with the beam; storage rack receives it on its side.',
                   'Two 18 mm access bores pass both walls for captive welded compression sleeves. Four top-wall M6 stations are drilled/tapped with internal bosses.',
                   'Routing-force capacity and welded-frame compliance are not released. Map and shim beam seats before installing cut-only aluminum panels.']), 'beam',bi,datum)
        for si,px in enumerate((113,987),1):
            register(m.add_plate(f'G_BEAM_STACK_PAD_{bi+1}_{si}',50,50.8,6,origin=(px,by+31.4,870),u=(1,0,0),v=(0,0,1),pn='G_BEAM_STACK_PAD',group='bed_beam',
                                notes=['Weld 6 mm pad to rear side of beam. In storage orientation this is a bearing pad for one upper beam; no fixed upper shelf blocks the incoming lower beam. Secure stored stacks against accidental movement before operation.']), 'beam',bi,datum)
        for si,bx in enumerate((138,1012)):
            foot=plate(rect(50,50.8),6,holes=[(25,15.4,18),(25,40.4,6)])
            register(m.add(f'G_BEAM_FOOT_BASE_{bi+1}_{si+1}',foot,origin=(bx-25,by-25.4,846),pn='G_BEAM_FOOT_BASE',group='bed_beam',
                          flat={'outline':rect(50,50.8),'thickness_mm':6,'holes':[(25,15.4,18),(25,40.4,6)],'slots':[],'internal':[]},
                          notes=['Weld base, vertical foot and beam before final fitting. Locator pin press fit must use measured pin and reamed bore.']), 'beam',bi,datum)
            register(m.add(f'G_BEAM_FOOT_{bi+1}_{si+1}',hollow_z(50,50.8,18),origin=(bx-25,by-25.4,852),pn='G_BEAM_FOOT_18',group='bed_beam',
                          notes=['18 mm high fabricated hollow foot; continuous 3 mm welds to base and beam.']), 'beam',bi,datum)
            register(m.add(f'G_BEAM_SLEEVE_{bi+1}_{si+1}',pipe(66.8,18,9),origin=(bx,by-10,846),pn='G_BEAM_COMPRESSION_SLEEVE',group='bed_beam',material='Machined steel',
                          notes=['OD18 ID9 x 66.8. Weld to foot base and beam bottom wall before closing foot. Head seat Z912.8; M8 head finishes flush at Z920.8.']), 'beam',bi,datum)
            register(m.add(f'G_BEAM_LOCATOR_{bi+1}_{si+1}',cyl(6,12),origin=(bx,by+15,842),pn='G_LOCATOR_6x12',group='bed_beam',material='Hardened steel pin',purchased=True,color=HARDWARE,
                          notes=['4 mm projects below foot. Left pin enters round seat, right enters X-relieved seat. Confirm actual pin tolerance and retention; do not press an unmeasured pin into a nominal CAD bore.']), 'beam',bi,datum)
            b=cyl(8,80).fuse(cyl(13,8).translate((0,0,80))).clean()
            register(m.add(f'G_BEAM_BOLT_{bi+1}_{si+1}',b,origin=(bx,by-10,832.8),pn='STD_M8x80_SOCKET',group='bed_release_hardware',material='M8x80 steel',purchased=True,color=HARDWARE,
                          notes=['Remove after panels. Stored head-down in the guided hardware rack. Torque remains subject to qualification of seat weld and ledger wall.']), 'beam_bolt',2*bi+si,(bx,by-10,832.8))
        # Four removable clamp bridges: they bear on panel ends, not on MDF.
        for ci,cx in enumerate((123.5,523.5,626.5,1026.5)):
            idx=bi*4+ci
            m.add(f'G_CLAMP_BOSS_{bi+1}_{ci+1}',pipe(8,16,6),origin=(cx,by,909.752),pn='G_M6_BEAM_BOSS',group='bed_beam',
                  notes=['Weld under beam top wall while access is available; drill 5 and tap M6 through boss and wall after welding.'])
            register(m.parts[-1],'beam',bi,datum)
            cd=(cx,by,913.4)
            strap=m.add_plate(f'G_PANEL_CLAMP_{bi+1}_{ci+1}',20,30,6,holes=[(10,15,6.6)],origin=(cx-10,by-15,940.8),pn='G_PANEL_CLAMP_20x30',group='bed_release_hardware',
                notes=['Removable 20 x 30 x 6 clamp bridge. End bridges overlap one panel; intermediate bridges span the 10 mm panel gap. Qualify contact and preload on actual extrusion.'])
            register(strap,'clamp',idx,cd)
            register(m.add(f'G_PANEL_CLAMP_SPACER_{bi+1}_{ci+1}',pipe(19.5,8,6.6),origin=(cx,by,920.8),pn='G_CLAMP_SPACER_19_5',group='bed_release_hardware',
                           notes=['0.5 mm nominal below the clamped panel face; spacer limits gross bridge deflection, does not establish a torque rating.']), 'clamp',idx,cd)
            register(m.add(f'G_PANEL_CLAMP_WASHER_{bi+1}_{ci+1}',pipe(1.6,12,6.4),origin=(cx,by,946.8),pn='STD_M6_WASHER_12',group='bed_release_hardware',purchased=True,material='Steel washer',color=HARDWARE), 'clamp',idx,cd)
            bolt=cyl(6,35).fuse(cyl(10,6).translate((0,0,35))).clean()
            register(m.add(f'G_PANEL_CLAMP_BOLT_{bi+1}_{ci+1}',bolt,origin=cd,pn='STD_M6x35_SOCKET',group='bed_release_hardware',purchased=True,material='M6x35 steel',color=HARDWARE), 'clamp',idx,cd)
    # Each five-strip panel uses four 250 mm ties, joined by the common middle strip.
    # Staggered screw positions give two independent stations in the middle strip.
    profile=profile_20100(PANEL_L)
    nut=box(8,8,2.7).translate((-4,-4,0)).cut(cyl(5,2.7)).clean()
    panel_masses=[]
    for row,py in enumerate(PANEL_Y):
        for col,px in enumerate(PANEL_X):
            index=row*2+col; prefix=f'G_PANEL_{index+1}';datum=(px,py,TOP)
            start=len(m.parts)
            for j in range(5):
                register(m.add(f'{prefix}_STRIP_{j+1}',profile,origin=(px+100*j,py,TOP),pn='BUY_20100_CUT_397',group='bed_panel',material='Purchased6063T5profile',color=ALU,purchased=True,
                               notes=['Purchased 1220 mm strip: cut three 397 mm pieces per bar; 29 mm remains for actual kerfs/end trim. Ten bars make thirty pieces. Verify actual length and saw kerf before cutting.',
                                      'Supplier-section reconstruction, not a certified manufacturing profile or load rating.']), 'panel',index,datum)
            tie_y=((126.5,426.5),(526.5,806.5),(933.0,1126.5))[row]
            for ti,ty in enumerate(tie_y):
                for half in (0,1):
                    # The first tie bolts to strips 1,2,3; second to 3,4,5.
                    local_x=(50,150,230) if half==0 else (20,100,200)
                    part=m.add_plate(f'{prefix}_TIE_{ti+1}_{half+1}',250,20,TIE_T,slots=[(x,10,10,5.5,0) for x in local_x],origin=(px+250*half,ty-10,TOP-TIE_T),pn=f'G_PANEL_TIE_{half+1}',group='bed_panel',material='Aluminum alloy unverified',color=ALU,
                                     notes=['250 x 20 x 9.525 finished tie fits within a 12 x 12 inch blank. Twenty-four required; inventory quantity/alloy and any facing of half-inch stock remain unverified.',
                                            'The two half-width ties both bolt to the common middle extrusion. No butt-joint strength is assumed between the ties.',
                                            '10 x 5.5 slots allow +/-2.25 mm lateral shank movement to absorb actual strip-width stack. Use 15 mm washers entirely on the 20 mm tie width.'])
                    register(part,'panel',index,datum)
                    for hi,xx in enumerate(local_x):
                        x=px+250*half+xx
                        pre=f'{prefix}_TIE_{ti+1}_{half+1}_F{hi+1}'
                        screw=cyl(5,16).fuse(cyl(9.5,2.75).translate((0,0,-2.75))).clean()
                        register(m.add(pre+'_SCREW',screw,origin=(x,ty,TOP-TIE_T-1.5),pn='STD_M5x16_BUTTON',group='bed_panel',material='Steel M5x16',purchased=True,color=HARDWARE), 'panel',index,datum)
                        register(m.add(pre+'_WASHER',pipe(1.5,15,5.3),origin=(x,ty,TOP-TIE_T-1.5),pn='STD_M5_WASHER_15',group='bed_panel',material='Steel washer',purchased=True,color=HARDWARE), 'panel',index,datum)
                        register(m.add(pre+'_NUT',nut,origin=(x,ty,TOP+1.3),pn='STD_DIN562_M5',group='bed_panel',material='Steel square nut',purchased=True,color=HARDWARE,
                                       notes=['Bottom-slot lip carries clamp preload. Establish controlled tightening on a representative joint; no unsupported torque is issued.']), 'panel',index,datum)
            panel_masses.append(round(sum(p.shape.Volume()*(7.85e-6 if 'Steel' in p.material or 'steel' in p.material else 2.7e-6) for p in m.parts[start:]),3))
            # Board is a finished 18 mm solid from rough 19 mm stock, with accessible skim.
            bx=SPOIL_X[col];bw=393.5;ya,yb=SPOIL_Y[row];length=yb-ya
            notch_x=(523.5 if col==0 else 626.5)-bx; nw=24
            low_notch=row>0;high_notch=row<2
            outline=[(0,0)]
            if low_notch:outline += [(notch_x-nw/2,0),(notch_x-nw/2,12),(notch_x+nw/2,12),(notch_x+nw/2,0)]
            outline += [(bw,0),(bw,length)]
            if high_notch:outline += [(notch_x+nw/2,length),(notch_x+nw/2,length-12),(notch_x-nw/2,length-12),(notch_x-nw/2,length)]
            outline += [(0,length)]
            board_x=(223.5,423.5) if col==0 else(726.5,926.5)
            holes=[(x-bx,y-ya,5.5) for x in board_x for y in (ya+25,yb-25)]
            s=plate(outline,18,holes=holes)
            ops=[]
            for x,y,d in holes:
                pocket=cyl(10,3.01).translate((x,y,15)).fuse(cq.Solid.makeCone(2.75,5,2.25).translate((x,y,12.75))).clean()
                s=s.cut(pocket).clean();ops.append({'type':'circle','x':x,'y':y,'diameter':10,'layer':'MILL_TOP_POCKET_DEPTH_3_PLUS_CSK'})
            register(m.add(f'G_SPOIL_{index+1}',s,origin=(bx,ya,TOP+20),pn=f'G_SPOIL_R{row+1}_{col+1}',group='spoilboard',material='MDF 18 mm finished',color=(.66,.50,.31),
                           flat={'outline':outline,'thickness_mm':18,'holes':holes,'slots':[],'internal':[],'operations':ops,'machining_notes':['Rough blank 19 mm. Finish in installed machine to 18 mm after a nominal 1 mm skim. STEP is the finished state.','Pocket 10 mm diameter to 3 mm below FINISHED top, then 90 degree countersink 2.25 mm deeper.','Notches clear the middle panel clamp bridges; do not fill them.']},
                           notes=['Finished Z958.8. The entire board lies within nominal X175..975/Y121.4..1121.4 center travel. Skim the six accessible pieces individually with suitable cutter clearance checked.',
                                  'Re-probe work zero and check coplanarity following reinstallation. This does not make unsurfaced aluminum or welded seats precision datums.']), 'spoil',index,(bx,ya,TOP+20))
            for hi,(x,y,d) in enumerate(holes):
                screw=cyl(5,17.5).fuse(cq.Solid.makeCone(2.5,5,2.5).translate((0,0,17.5))).clean()
                register(m.add(f'G_SPOIL_{index+1}_BOLT_{hi+1}',screw,origin=(bx+x,ya+y,TOP+15),pn='STD_M5x20_CSK',group='bed_release_hardware',material='Steel M5x20',purchased=True,color=HARDWARE), 'spoil_bolt',index*4+hi,(bx+x,ya+y,TOP+15))
                register(m.add(f'G_SPOIL_{index+1}_NUT_{hi+1}',nut,origin=(bx+x,ya+y,TOP+16),pn='STD_DIN562_M5',group='bed_release_hardware',material='Steel square nut',purchased=True,color=HARDWARE,
                    notes=['Loose top-slot nut: after removing the spoilboard, slide it to the front end of this panel and lift through the 10 mm joint (8 mm nut, nominal 1 mm each side). Use a magnetic pickup; verify actual slot and joint access. Thread it onto the removed spoilboard screw in the hardware tray before rotating this panel. No captive-nut claim.']), 'spoil_nut',index*4+hi,(bx+x,ya+y,TOP+16))
    make_storage(m)
    # Dedicated seat tray on the reservoir lid. Seats lie broad face down, so
    # their welded bosses project upward instead of balancing on a small boss.
    m.add_plate('G_FRONT_SEAT_TRAY_FLOOR',210,120,3,origin=(300,800,433.096),group='bed_storage',
        notes=['Seal-weld this small dry hardware tray to the removable reservoir lid. Two front seats lie face down; four mounting screws and washers occupy its front row.'])
    for side,xx in enumerate((300,507)):
        m.add_plate(f'G_FRONT_SEAT_TRAY_SIDE_{side+1}',120,20,3,origin=(xx,800,436.096),u=(0,1,0),v=(0,0,1),pn='G_FRONT_SEAT_TRAY_SIDE',group='bed_storage')
    for side,yy in enumerate((803,920)):
        m.add_plate(f'G_FRONT_SEAT_TRAY_END_{side+1}',204,20,3,origin=(303,yy,436.096),u=(1,0,0),v=(0,0,1),pn='G_FRONT_SEAT_TRAY_END',group='bed_storage')
    panel_masses=[round(sum(p.shape.Volume()*(7.85e-6 if 'steel' in p.material.lower() else 2.7e-6) for p in m.parts if _PLACEMENTS.get(p.id,('',))[0]=='panel' and _PLACEMENTS[p.id][1]==i),3) for i in range(6)]
    beam_mass=[]
    for bi in range(4):
        beam_mass.append(round(sum(p.shape.Volume()*7.85e-6 for p in m.parts if _PLACEMENTS.get(p.id,('',))[0]=='beam' and _PLACEMENTS[p.id][1]==bi),3))
    return {'revision':'Rev G manual cassette repair','architecture_assumption':'Manual panels and beams; optional user preference question pending. No winch or off-machine parking assumed.',
            'bare_deck_mm':[1003,1211,20],'workplane_z_mm':940.8,'finished_spoilboard_z_mm':958.8,'rough_spoilboard_thickness_mm':19,'finished_spoilboard_thickness_mm':18,
            'panels':6,'panel_envelope_mm':[500,397,33.775],'panel_mass_kg':panel_masses,'beams':4,'beam_mass_kg':beam_mass,
            'purchased_1220_bars':10,'cuts_per_bar':'three 397 mm pieces, total residual 29 mm for kerfs/end trim','panel_clamp_M6':16,'beam_drawdown_M8':8,'spoilboard_M5':24,
            'procedure':'Remove stock, clean and dry. Park gantry rear and isolate drives. Remove/store 24 spoil screws and six boards; retrieve all 24 loose top-slot nuts through the panel-end gaps and thread each onto its stored screw. Remove/store 16 panel clamps and six panels. Release beam 1 and park it on its side on beam 2. Remove the two front seats and four seat bolts to their lid tray; the front lowering portal is now clear. Store beam 1 rear/lower, beam 2 front/lower, beam 3 rear/upper, beam 4 front/upper after releasing the eight beam bolts. Reverse for router mode. Map seats and re-probe after conversion.',
            'front_portal':'Two removable front seats; four M8 mount screws into welded ledger sleeves. Temporary beam-on-beam parking and every handling path require explicit checks.',
            'cabinet_service':'Reinstall bed and spoilboards to empty the front and left storage racks before opening controls cabinet. Fixed holders remain outside door width.',
            'release_holds':['Manual handling architecture preference confirmation','Full ordered handling sweeps with already stored parts and fingers/clearances','Actual supplier section/flatness, T-nut fit and controlled preload test','Seat welding, frame and complete tool-loop rigidity qualification','Actual aluminum inventory/alloy and shop machining capability','Measured seat/beam/panel tolerance stack and repeat installation map'],
            'storage_envelopes_mm':{'panels':[325,7,175,825,240.775,572],'beams':[113,0,585,1037,168.8,698.6],'spoilboards':[135,250,175,268,647,568.5]}}

def make_storage(m):
    # Panel support forks weld to the rear face of the lowered front frame tie.
    for side,x in enumerate((310,810),1):
        s=box(30,194.2,30).cut(box(24,196.2,24).translate((3,-1,3))).clean()
        m.add(f'G_RACK_PANEL_FORK_{side}',s,origin=(x,50.8,121.6),pn='G_RACK_PANEL_FORK',group='bed_storage',material='Steel 30x30x3 tube',length=194.2,
              notes=['Continuous 3 mm fillet to rear face of front tie at Y50.8. No member crosses cabinet door width above Z165. Dry stored bed parts only.'])
        m.add_plate(f'G_RACK_PANEL_WEB_{side}',245,17.4,6,origin=(x+12,0,151.6),u=(0,1,0),v=(0,0,1),pn='G_RACK_PANEL_WEB',group='bed_storage',notes=['Continuous web links panel shelf to the fork and front tie.'])
        m.add_plate(f'G_RACK_PANEL_SEAT_{side}',40,245,6,origin=(x-5,0,169),pn='G_RACK_PANEL_SEAT',group='bed_storage')
        # 40 mm pitch and centered 2 mm separators leave approximately 2.1 mm
        # nominal each side of a 33.775 mm panel (first/last slot are wider).
        for gi,y in enumerate((3,42.8875,82.8875,122.8875,162.8875,202.8875,243)):
            m.add_plate(f'G_RACK_PANEL_GUIDE_{side}_{gi+1}',40,25,2,origin=(x-5,y+2,175),u=(1,0,0),v=(0,0,1),pn='G_RACK_PANEL_GUIDE',group='bed_storage',
                        notes=['Deburr and fit nonabrasive replaceable edge pads within the nominal gap; prove as-built panel clearances before loading.'])
    # One shelf each side; lower beams carry the upper pair on welded stacking pads.
    for side,sx in enumerate((50.8,985),1):
        sw=79.2 if side==1 else 114.2
        for level,z in enumerate((579,),1):
            m.add_plate(f'G_RACK_BEAM_SHELF_{side}_{level}',sw,172,6,origin=(sx,0,z),pn=f'G_RACK_BEAM_SHELF_{side}',group='bed_storage',
                        notes=['Shelf welds to inner face of front leg over Y0..50.8; triangular webs support the projecting plate. Left shelf ends at X130, preserving a board-transfer lane beginning X135.'])
            gh=80
            for gi,y in enumerate((8,42),1):
                outline=[(0,0),(sw,gh),(0,gh)] if side==1 else [(sw,0),(sw,gh),(0,gh)]
                m.add_plate(f'G_RACK_BEAM_GUSSET_{side}_{level}_{gi}',sw,gh,3,outline=outline,origin=(sx,y+3,z-gh),u=(1,0,0),v=(0,0,1),pn=f'G_RACK_BEAM_GUSSET_{side}_{gh}',group='bed_storage',notes=['3 mm continuous fillet to leg and shelf. Storage-only support, not a machining load path.'])
    # Left-bay board rack: feet attach to the existing lower left side rail.
    for ri,(ay,dy,fy,gy) in enumerate(((210,234,235,243),(655,655,630,630)),1):
        m.add_plate(f'G_RACK_SPOIL_ARM_{ri}',219.2,30,6,origin=(50.8,ay,224),pn='G_RACK_SPOIL_ARM',group='bed_storage',notes=['Weld arm to inner face of left lower-side rail at Z230; arm stays beyond the stored board edges.'])
        m.add_plate(f'G_RACK_SPOIL_DROP_{ri}',160,49,6,origin=(110,dy+6,175),u=(1,0,0),v=(0,0,1),pn='G_RACK_SPOIL_DROP',group='bed_storage')
        m.add_plate(f'G_RACK_SPOIL_FOOT_{ri}',160,30,6,origin=(110,fy,169),pn='G_RACK_SPOIL_FOOT',group='bed_storage')
        for gi,x in enumerate((131,154,177,200,223,246,269)):
            m.add_plate(f'G_RACK_SPOIL_GUIDE_{ri}_{gi+1}',17,25,2,origin=(x,gy,175),u=(0,1,0),v=(0,0,1),pn='G_RACK_SPOIL_GUIDE',group='bed_storage')
    for si,x in enumerate((135,158,181,204,227,250),1):
        m.add_plate(f'G_RACK_SPOIL_RUNNER_{si}',18,365,6,origin=(x,265,169),pn='G_RACK_SPOIL_RUNNER',group='bed_storage',
                    notes=['Continuous support between front and rear rack feet. Supports all three board lengths; shorter boards do not rely on reaching the rear foot. Weld ends to the rack feet.'])
    # Dedicated shallow hardware rack attached to the cabinet's removable left cage.
    m.add_plate('G_HW_MOUNT_WEB',25,90,3,origin=(324.3,455,165),u=(0,1,0),v=(0,0,1),group='bed_storage',notes=['Weld to outside of CAB_UPRIGHT_1 before painting. Rack is removable with the cabinet cage.'])
    m.add_plate('G_HW_MOUNT_SHELF',49.3,40,6,origin=(275,440,175),group='bed_storage')
    m.add_plate('G_HW_TRAY_FLOOR',45,405,3,origin=(275,295,181),group='bed_storage')
    for si,x in enumerate((272,320),1):
        m.add_plate(f'G_HW_TRAY_SIDE_{si}',405,28,3,origin=(x,295,184),u=(0,1,0),v=(0,0,1),pn='G_HW_TRAY_SIDE',group='bed_storage')
    for ei,y in enumerate((298,700),1):
        m.add_plate(f'G_HW_TRAY_END_{ei}',45,28,3,origin=(275,y,184),u=(1,0,0),v=(0,0,1),pn='G_HW_TRAY_END',group='bed_storage')
    m.add_plate('G_HW_DRAWBOLT_GUIDE',45,80,3,holes=[(10+25*c,10+18*r,8.5) for c in (0,1) for r in range(4)],origin=(275,620,220),group='bed_storage',notes=['Holes guide the eight removed M8 bolts standing head-down in the tray.'])
    for si,x in enumerate((272,320),1):
        m.add_plate(f'G_HW_DRAWBOLT_GUIDE_RISER_{si}',80,8,3,origin=(x,620,212),u=(0,1,0),v=(0,0,1),pn='G_HW_DRAWBOLT_GUIDE_RISER',group='bed_storage')

def cassette_poses():
    return {'status':'Waypoint proposal; swept collision and human access verification still required.',
            'footprint_xy_mm':[-28.4,-14.6,1178.4,1464.6],
            'front_transfer_well_y_mm':[0,105],
            'panel_order_to_storage':[6,5,4,3,2,1],
            'beam_order_to_storage':[1,2,3,4],
            'spoilboard_order_to_storage':[4,3,2,1,6,5],
            'panel_route':'Lift clear, move to front while horizontal, rotate about X above pan and lower vertically with entire part inside front well; below Z675 translate to the furthest empty rack slot. Gantry parked rear and isolated.',
            'beam_route':'After panels and loose top nuts are stored, park beam1 on its side atop beam2. Remove the two front seats to open the portal. Transfer beam1 to lower rear, beam2 to lower front, beam3 to upper rear and beam4 to upper front. Rotate beams above the workplane before front-well descent. See continuous beam-path proof for exact ordered poses; temporary resting is not a handling rating.',
            'board_route':'Before storing any panels, orient each board with its 393.5 mm dimension vertical and drop through Y0..18 to Z235..628.5. Turn -90 degrees about Z with moving right-end pivot X=135+L*cos(theta),Y=0 so its left end goes rearward. Store row2 long boards in slots5/6 first, row1 medium boards in3/4, row3 short boards in1/2. Shift to the assigned X lane, slide rear to Y250, then lower60 onto the continuous runner.'}
