"""Controls cabinet hidden in the front bay under the water table, door forward.

Rev F relocation: the purchased 20x16x8 enclosure stands UPRIGHT between pan
bearers 1 and 2, back-bolted to two horizontal 1x1 rails on a bolt-on cage
whose stringers ride the bearer undersides OUTBOARD of the enclosure width.
The door faces the open front window, swings beneath bearer 1 and above the
lowered front tie; service needs no draining and no bed or pan removal. The
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

def make_controls_packaging(m):
    for si,cx in enumerate(CAGE_X,1):
        s=box(TUBE,STR_LEN,TUBE).cut(box(TUBE-2*TWALL,STR_LEN+2,TUBE-2*TWALL).translate((TWALL,-1,TWALL)))
        m.add(f'CAB_STRINGER_{si}',s,origin=(cx-TUBE/2,STR_Y0,STR_Z0),pn='CAB_STRINGER',group='controls_support',material='A5001x1x.083tube',length=STR_LEN,
              notes=['Bridges the undersides of pan bearers 1 and 2 with 25 mm underlap each end, outboard of the enclosure width.',
                     'Pre-drill Ø5.5 through both stringer walls at each screw station; the screw self-drills only the bearer wall. The cage unbolts without disturbing the bearers or pan.'])
        for bi,ty in enumerate((213.4,687.6),1):
            tek=cyl(11,3).fuse(cyl(5.5,35).translate((0,0,3))).clean()
            p=m.add(f'CAB_TEK_{si}_{bi}',tek,origin=(cx,ty,650.8),pn='STD_12-14x38_TEK',group='controls_support',material='#12-14x38 self-drilling screw',purchased=True,color=HARDWARE,
                    notes=['Head bears under the stringer; shank passes the pre-drilled stringer walls and self-drills the pan-bearer bottom wall.'])
            bearer=m.find('PAN_BEARER_1' if ty<450 else 'PAN_BEARER_2')
            m.permit(p.id,bearer.id,'Self-drilling screw thread pierces the bearer bottom wall.')
            m.permit(p.id,f'CAB_STRINGER_{si}','Screw passes the pre-drilled stringer walls it clamps.')
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
               'Door faces the open front window; it clears the lowered front tie (top Z151.6) by 13.4 mm and swings fully beneath pan bearer 1 (Z679.2+). Routine electrical service requires no draining and no pan or bed removal.',
               'Bottom-face gland entries preferred. VFD heat rejection, segregated wiring, gland positions and the removable internal panel require the selected equipment drawings.'])
    cap=plate(rect(436.4,233.2),1.5)
    m.add('CAB_DRIP_CAP',cap,origin=(356.8,236.8,673.5),pn='CAB_DRIP_CAP',group='controls_shield',material='Galvanized steel1.5mm',
          flat={'outline':rect(436.4,233.2),'thickness_mm':1.5,'holes':[],'slots':[],'internal':[],
                'machining_notes':['Clip-on condensation cap for the enclosure top: bend 12 mm hems down on both 436.4 edges and a 20 mm drip hem on the front edge (bends not modeled).',
                                   'Rests on the enclosure top in the 6.2 mm gap below the pan bearers; lift off for top access. Not the electrical enclosure.']},
          notes=['Sheds pan-bottom condensation forward of the door plane; hems hook the enclosure top edges, no fasteners into the enclosure skin.'])
    return {'enclosure_reserve_xyz_mm':[CAB_X0,CAB_Y0,CAB_Z0],'enclosure_dimensions_mm':[CAB_W,CAB_D,CAB_H],
        'orientation':'Upright in the front bay under the water table, door forward through the open front window.',
        'service':'Isolate electrical power and open the front door. No draining, no pan or bed removal; lift the drip cap for top access.',
        'unreleased_interfaces':['Vendor back-panel mounting hole pattern (transfer-drill the cage rails)','VFD thermal layout and wiring segregation','Cable glands and chain routes','Panel layout and legend set'],
        'drip_shield':'Clip-on 1.5 mm cap at Z673.5-675 with front drip hem; pan floor above remains the primary umbrella.'}
