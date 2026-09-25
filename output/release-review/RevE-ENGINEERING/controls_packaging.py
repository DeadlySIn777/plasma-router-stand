"""Controls cabinet hidden in the front bay under the water table, door forward.

Rev F relocation: the purchased 20x16x8 enclosure stands UPRIGHT between pan
bearers 1 and 2, back-bolted to two horizontal 1x1 rails on a bolt-on cage
whose stringers ride the bearer undersides OUTBOARD of the enclosure width.
The nominal enclosure reserve faces the front window between bearer 1 and the
lowered front tie; the selected door/hinge/latch must still be checked. A separate
welded drip shield is carried by the cage, with no enclosure penetrations. The
tank lid keeps only the tool-park and hardware-tray holes.
"""
import math
import cadquery as cq
from cad_helpers import *
from frame_details import hexpart

CAB_W=406.4;CAB_H=508.0;CAB_D=203.2
CAB_X0=371.8;CAB_Y0=251.8;CAB_Z0=165.0          # body X371.8-778.2, Y251.8-455, Z165-673
CAGE_X=(340.0,810.0)                             # stringer/upright centerlines, outboard of body
TUBE=25.4;TWALL=2.1082                           # 1 x 1 x .083 brace stock
STR_Y0=200.8;STR_LEN=499.2                       # 25 mm underlap at bearers 1 and 2
STR_Z0=679.2-TUBE                                # 653.8, up against bearer bottoms
RAIL_Z=(190.0,620.0)                             # back-rail centerlines
BACK=CAB_Y0+CAB_D                                # 455.0
STR_HOLE_D=6.0                                  # 0.25 radial clearance to the nominal 5.5 screw envelope
STR_HOLE_Y=(213.4-STR_Y0,687.6-STR_Y0)            # local Y12.6 / Y486.8, through both tube walls
CAP_W=436.4;CAP_PLAN_D=233.2;CAP_T=1.5
CAP_ORIGIN=(356.8,236.8,675.5)
CAP_SLOPE=0.01                                  # rear high; water runs toward the front drip lip
CAP_CS=1/math.sqrt(1+CAP_SLOPE**2);CAP_SN=CAP_SLOPE*CAP_CS
CAP_V=(0,CAP_CS,CAP_SN);CAP_N=(0,-CAP_SN,CAP_CS)
CAP_D=CAP_PLAN_D/CAP_CS                          # true developed roof-sheet length
CAP_MOUNT_X=(8.0,CAP_W-8.0);CAP_MOUNT_Y=(63.2,183.2)
CAP_TAB_T=3.048

def cap_point(x,y,z=0):
    """Installed point from the shield's X / uphill / normal local datum."""
    return (CAP_ORIGIN[0]+x,CAP_ORIGIN[1]+CAP_CS*y-CAP_SN*z,CAP_ORIGIN[2]+CAP_SN*y+CAP_CS*z)

def make_drip_shield(m):
    holes=[(x,y,5.5) for x in CAP_MOUNT_X for y in CAP_MOUNT_Y]
    roof=m.add_plate('CAB_DRIP_CAP',CAP_W,CAP_D,CAP_T,holes=holes,origin=CAP_ORIGIN,u=(1,0,0),v=CAP_V,
        group='controls_shield',material='Mild steel1.5mm',
        notes=['Flat 436.4 x %.6f x 1.5 mm roof, mounted rear high at 1%% slope; four Ø5.5 holes at the DXF coordinates. No bends or bend allowance.'%CAP_D,
               'Continuously seal-weld the separate 20 mm front lip to the roof underside along the front edge. Control distortion, leak-test, then coat all faces; do not weld galvanized sheet.',
               'Support and retention come from four cage tabs and M5 fasteners. No attachment to, or assumed load bearing by, the purchased enclosure.',
               'Rear and side edges are intentionally plain so the shield can withdraw 230 mm forward parallel to its 1% slope, then lower 100 mm into the front bay for hand removal. Remove all four M5 bolts/nuts first. Confirm the actual enclosure door and hinge envelope before release.',
               'After welding and coating, check at least 2 mm roof-to-enclosure clearance and 1 mm clearance to the bearer along the withdrawal path; adjust or remake tabs/shield if either check fails. These are as-built checks, not assumed vendor tolerances.'])
    roof.flat['machining_notes']=['No bends. Flat roof sheet; separate front drip lip is welded on after cutting.',
                                  'Install rear high: 1% slope, datum front roof underside (356.8,236.8,675.5) mm.']
    m.add_plate('CAB_DRIP_FRONT_LIP',CAP_W,20,CAP_T,origin=cap_point(0,CAP_T,-20),u=(1,0,0),v=CAP_N,
        group='controls_shield',material='Mild steel1.5mm',
        notes=['Flat 436.4 x 20 x 1.5 mm front drip lip. Top edge meets roof underside; exterior front face lies at roof local Y0. Continuous sealed weld; no bend allowance.',
               'Installed lip is ahead of the nominal cabinet door plane. Selected enclosure latch/hinge motion remains to be checked.'])
    for si,(xx,cx) in enumerate(zip(CAP_MOUNT_X,CAGE_X),1):
        left_x=cx+TUBE/2 if si==1 else CAB_X0+CAB_W
        width=CAB_X0-left_x if si==1 else cx-TUBE/2-left_x
        local_x=left_x-CAP_ORIGIN[0]
        for yi,yy in enumerate(CAP_MOUNT_Y,1):
            m.add_plate(f'CAB_CAP_TAB_{si}_{yi}',width,30,CAP_TAB_T,holes=[(xx-local_x,15,5.5)],origin=cap_point(local_x,yy-15,-CAP_TAB_T),u=(1,0,0),v=CAP_V,
                pn='CAB_CAP_TAB_LEFT' if si==1 else 'CAB_CAP_TAB_RIGHT',group='controls_support',material='A36 steel0.120insheet',
                notes=['Weld outer 30 mm edge to the inner vertical face of its cage stringer. Tab upper face follows the roof 1% slope and touches its underside; tack using the drilled roof as an alignment fixture, then remove roof before final welding.',
                       'Ø5.5 through-hole takes M5 retaining bolt. Deburr both bearing faces; coat weldment before final assembly. This tab does not bear on the enclosure.'])
            bolt=cyl(5,20).fuse(cyl(8.5,5).translate((0,0,20))).clean()
            m.add(f'CAB_CAP_BOLT_{si}_{yi}',bolt,origin=cap_point(xx,yy,CAP_T-20),u=(1,0,0),v=CAP_V,pn='STD_M5x20_SOCKET',group='controls_shield',material='M5x20 class8.8 socket screw',purchased=True,color=HARDWARE,
                  notes=['Through Ø5.5 roof/tab holes, normal to the 1% roof plane. Remove bolt and nut before withdrawing the shield.'])
            m.add(f'CAB_CAP_NUT_{si}_{yi}',hexpart(8,5,5),origin=cap_point(xx,yy,-CAP_TAB_T-5),u=(1,0,0),v=CAP_V,pn='STD_M5_NYLOC',group='controls_shield',material='M5 nyloc nut',purchased=True,color=HARDWARE,
                  notes=['Nominal 8AF x 5 envelope; retained below cage tab, outside enclosure side wall.'])
    return {'roof_flat_mm':[CAP_W,CAP_D,CAP_T],'front_lip_flat_mm':[CAP_W,20,CAP_T],
            'datum_world_mm':CAP_ORIGIN,'slope_rear_high':CAP_SLOPE,'mount_holes_local_xy_mm':[[x,y] for x in CAP_MOUNT_X for y in CAP_MOUNT_Y],
            'attachment':'Four welded cage tabs, four M5x20 socket screws and M5 nyloc nuts; no vendor enclosure penetrations.',
            'fabrication':'Two flat sheets, continuously seal-welded at front lip. No bends, K factor or developed bend allowance required.',
            'service':'Remove four M5 retaining bolts and nuts; withdraw roof/lip weldment 230 mm forward parallel to its slope, then lower 100 mm into front bay. Actual selected enclosure projection remains a hold.'}

def make_controls_packaging(m):
    for si,cx in enumerate(CAGE_X,1):
        s=box(TUBE,STR_LEN,TUBE).cut(box(TUBE-2*TWALL,STR_LEN+2,TUBE-2*TWALL).translate((TWALL,-1,TWALL)))
        bores=[cyl(STR_HOLE_D,TUBE+2).translate((TUBE/2,hy,-1)) for hy in STR_HOLE_Y]
        s=s.cut(cq.Compound.makeCompound(bores)).clean()
        m.add(f'CAB_STRINGER_{si}',s,origin=(cx-TUBE/2,STR_Y0,STR_Z0),pn='CAB_STRINGER',group='controls_support',material='A5001x1x.083tube',length=STR_LEN,
              notes=['Bridges the undersides of pan bearers 1 and 2 with 25 mm underlap each end, outboard of the enclosure width.',
                     'Drill two Ø6.0 clearance holes along local +Z through BOTH tube walls: local X12.7, Y12.6 and Y486.8 from the square-cut end. These bores are cut into the individual STEP.',
                     'The Ø6.0 bores provide 0.25 mm nominal radial clearance to the modeled Ø5.5 #12 shank. The screw self-drills only the bearer wall. The cage unbolts without disturbing the bearers or pan.'])
        for bi,ty in enumerate((213.4,687.6),1):
            tek=cyl(11,3).fuse(cyl(5.5,35).translate((0,0,3))).clean()
            p=m.add(f'CAB_TEK_{si}_{bi}',tek,origin=(cx,ty,650.8),pn='STD_12-14x38_TEK',group='controls_support',material='#12-14x38 self-drilling screw',purchased=True,color=HARDWARE,
                    notes=['Head bears under the stringer; shank passes the pre-drilled stringer walls and self-drills the pan-bearer bottom wall.'])
            bearer=m.find('PAN_BEARER_1' if ty<450 else 'PAN_BEARER_2')
            m.permit(p.id,bearer.id,'Self-drilling screw thread pierces the bearer bottom wall.')
        v=box(TUBE,TUBE,STR_Z0-165.0).cut(box(TUBE-2*TWALL,TUBE-2*TWALL,STR_Z0-165.0+2).translate((TWALL,TWALL,-1)))
        m.add(f'CAB_UPRIGHT_{si}',v,origin=(cx-TUBE/2,BACK,165.0),pn='CAB_UPRIGHT',group='controls_support',material='A5001x1x.083tube',length=STR_Z0-165.0,
              notes=['Welded T to its stringer at the top; both back rails weld across the pair. Fabricate the cage as one weldment, then bolt it up into the bearers.'])
        m.permit(f'CAB_UPRIGHT_{si}',f'CAB_STRINGER_{si}','Welded T joint between upright and stringer.')
    for ri,rz in enumerate(RAIL_Z,1):
        rl=CAGE_X[1]-CAGE_X[0]-TUBE
        r=box(rl,TUBE,TUBE).cut(box(rl+2,TUBE-2*TWALL,TUBE-2*TWALL).translate((-1,TWALL,TWALL)))
        m.add(f'CAB_RAIL_{ri}',r,origin=(CAGE_X[0]+TUBE/2,BACK,rz-TUBE/2),pn='CAB_RAIL',group='controls_support',material='A5001x1x.083tube',length=rl,
              notes=['Horizontal back rail welded across both uprights; carries the enclosure back-panel bolts.',
                     'Transfer-drill the two Ø6.6 bolt holes per rail from the selected enclosure back panel; nominal stations X460/X690.'])
        for si in (1,2):
            m.permit(f'CAB_RAIL_{ri}',f'CAB_UPRIGHT_{si}','Welded rail-to-upright joint.')
        for hi,hx in enumerate((460.0,690.0),1):
            b=cyl(10,6).fuse(cyl(6,45).translate((0,0,6))).clean()
            bolt=m.add(f'CAB_BOLT_{ri}_{hi}',b,origin=(hx,447.5,rz),u=(1,0,0),v=(0,0,-1),pn='STD_M6x45_SOCKET',group='controls_support',material='M6x45 socket screw',purchased=True,color=HARDWARE,
                  notes=['Through the enclosure back panel and both rail walls; nyloc at the rear face. Positions are nominal until the vendor back panel is transfer-drilled.'])
            m.permit(bolt.id,f'CAB_RAIL_{ri}','M6 through-bolt crosses both rail walls.')
            m.permit(bolt.id,'BUY_CONTROL_ENCLOSURE_RESERVE','Bolt crosses the purchased enclosure back-panel envelope at its vendor mounting holes.')
            m.add(f'CAB_NYLOC_{ri}_{hi}',hexpart(10,6,6),origin=(hx,BACK+TUBE+1,rz),u=(0,0,1),v=(1,0,0),pn='STD_M6_NYLOC',group='controls_support',material='M6 nyloc nut',purchased=True,color=HARDWARE)
    m.add('BUY_CONTROL_ENCLOSURE_RESERVE',box(CAB_W,CAB_D,CAB_H),origin=(CAB_X0,CAB_Y0,CAB_Z0),pn='BUY_CONTROL_ENCLOSURE_20x16x8',group='controls_envelope',material='Purchased controls enclosure',purchased=True,color=(.15,.18,.19),
        release='PACKAGING ENVELOPE - VENDOR MOUNTING AND PANEL LAYOUT TO BE VERIFIED',
        notes=['20x16x8 inch external reserve standing UPRIGHT in the front bay: X371.8-778.2, Y251.8-455, Z165-673.',
               'Nominal body clears the lowered front tie (top Z151.6) by 13.4 mm and pan bearer 1 underside (Z679.2) by 6.2 mm. These body margins do not qualify the actual door, hinges or latch; obtain that envelope before release.',
               'Bottom-face gland entries preferred. VFD heat rejection, segregated wiring, gland positions and the removable internal panel require the selected equipment drawings.'])
    shield=make_drip_shield(m)
    return {'enclosure_reserve_xyz_mm':[CAB_X0,CAB_Y0,CAB_Z0],'enclosure_dimensions_mm':[CAB_W,CAB_D,CAB_H],
        'stringer_drilling':{'diameter_mm':STR_HOLE_D,'local_xy_mm':[[TUBE/2,hy] for hy in STR_HOLE_Y],'direction':'Local +Z through both tube walls','shank_nominal_radial_clearance_mm':(STR_HOLE_D-5.5)/2},
        'orientation':'Upright in the front bay under the water table, door forward through the open front window.',
        'service':'Isolate electrical power before cabinet work. For shield removal take out four M5 retaining fasteners and withdraw the cap forward on its 1% slope; verify the selected enclosure door and hinge envelope before release.',
        'unreleased_interfaces':['Vendor back-panel mounting hole pattern (transfer-drill the cage rails)','Selected enclosure roof, door, hinge and latch envelope; confirm drip-shield and service clearance','VFD thermal layout and wiring segregation','Cable glands and chain routes','Panel layout and legend set'],
        'drip_shield':shield}
