"""Rev H completion details applied to the unchanged Rev G cassette baseline.

Parts are nominal engineering definitions. Nut-strip fit/preload, restraint load
capacity and actual fabricated tolerances require physical qualification.
"""
import math
import cadquery as cq
import bed_cassettes as bc
from cad_helpers import *

_STORED = {}
_STAGED = {}
_INITIAL = {}
_TEMPORARY = {}


def update_world_local(part, world):
    """For axis-aligned original parts only: preserve their original origin."""
    old_world=bbox(part.shape);old_local=bbox(part.local)
    offset=tuple(old_world[i]-old_local[i] for i in range(3))
    part.shape=world.clean();part.local=part.shape.translate(tuple(-v for v in offset))


def socket_bolt(d, length, head_d, head_h):
    return cyl(d,length).fuse(cyl(head_d,head_h).translate((0,0,length))).clean()


def hex_nut(d=6, af=10, height=5):
    r=af/math.sqrt(3)
    return plate([(r*math.cos(k*math.pi/3),r*math.sin(k*math.pi/3)) for k in range(6)],height,[(0,0,d)])


def nut_strips(m):
    """Two anti-slide retained strips per board replace all loose top nuts."""
    removed=[p.id for p in m.parts if p.id.startswith('G_SPOIL_') and '_NUT_' in p.id]
    for ident in removed:m.remove(ident);bc._PLACEMENTS.pop(ident,None)
    for index in range(6):
        row,col=divmod(index,2);px=bc.PANEL_X[col];py=bc.PANEL_Y[row]
        ya,yb=bc.SPOIL_Y[row];board_x=(223.5,423.5) if col==0 else (726.5,926.5)
        for j,x in enumerate(board_x,1):
            holes=[(4,y-(py+3),5) for y in (ya+25,yb-25)]
            holes += [(4,5,3),(4,386,3)]
            p=m.add_plate(f'H_NUT_STRIP_{index+1}_{j}',8,391,2.7,holes=holes,
                origin=(x-4,py+3,936.8),pn=f'H_NUT_STRIP_ROW_{row+1}',group='bed_panel',material='Low carbon steel',
                notes=['Two M5 tapped stations replace loose DIN562 nuts. Machine steel strip to 8 x 2.7 mm, break edges; 391 mm length leaves 3 mm at each panel end.',
                       'Two M3 flat-point retaining screws bear on the slot floor and hold the strip shoulders under the lips. They remain installed during every conversion. No extrusion drilling.',
                       'Set retention only, not structural routing preload. Verify actual slot dimensions, thread engagement and controlled spoilboard tightening on a sample before duplicating.'])
            p.flat['holes']=[(xx,yy,4.2 if d==5 else 2.5) for xx,yy,d in holes]
            p.flat['machining_notes']=['M5: drill 4.2 then tap M5 x 0.8 through. M3: drill 2.5 then tap M3 x 0.5 through. STEP uses nominal thread envelopes.',
                'Finished width 8.00 -0.10/+0.00, thickness 2.70 -0.05/+0.00, length 391.0 +/-0.2. Match to measured extrusion slot before manufacture.',
                'Flat-point M3 x 5 retainers: nominal slot-floor bearing Z934.7, strip Z936.8..939.5, retainer top Z939.7 below deck Z940.8.']
            bc.register(p,'panel',index,(px,py,bc.TOP))
            for k,y in enumerate((py+8,py+389),1):
                p=m.add(f'H_NUT_STRIP_SET_{index+1}_{j}_{k}',cyl(3,5),origin=(x,y,934.7),pn='STD_M3x5_FLAT_POINT_SET',group='bed_panel',material='Steel M3 flat point set screw',purchased=True,color=HARDWARE,
                    notes=['M3 x 5 flat-point retaining screw, nominal cylindrical thread envelope. Accessible through the 6.2 mm slot mouth at panel end, outside the spoilboard. Verify engagement/retention on the purchased profile.'])
                bc.register(p,'panel',index,(px,py,bc.TOP))
    return {'removed_loose_nuts':len(removed),'nut_strips':12,'M3_retaining_screws':24,
            'conversion_nut_retrievals':0,'spoilboard_screws_per_conversion':24,
            'profile_modification':'None; strip and set screws enter through the existing open slot ends.'}


def beam_stack_locks(m):
    """Sleeved stack through-bolts clamp steel to steel without crushing tube."""
    for index,by in enumerate(bc.BEAM_Y):
        datum=(113,by-25.4,842)
        for side,x in enumerate((123.0,1027.0),1):
            cutter=place(cyl(10,58.8),(x,by-26.4,895.4),u=(1,0,0),v=(0,0,-1))
            for ident in (f'G_BEAM_{index+1}',f'G_BEAM_STACK_PAD_{index+1}_{side}'):
                p=m.find(ident)
                if 'STACK_PAD' in ident:
                    px=113 if side==1 else 987
                    p.local=p.local.cut(cyl(10,8).translate((x-px,25.4,-1))).clean()
                    p.shape=place(p.local,(px,by+31.4,870),u=(1,0,0),v=(0,0,1))
                    p.part_number='H_BEAM_STACK_PAD_'+str(side)
                else:update_world_local(p,p.shape.cut(cutter))
                if p.flat:
                    # Pad local x is original global x offset; local y is Z870.
                    p.flat['holes'].append((x-(113 if side==1 else 987),25.4,10))
                p.notes.append('Rev H storage sleeve: through both side walls and stacking pad at X'+str(x)+', global Z895.4. OD10 sleeve welded flush at front wall and pad outer face before coating.')
            p=m.add(f'H_BEAM_STACK_SLEEVE_{index+1}_{side}',pipe(56.8,10,6.6),origin=(x,by-25.4,895.4),u=(1,0,0),v=(0,0,-1),pn='H_STACK_COMPRESSION_SLEEVE_56_8',group='bed_beam',material='Steel tube OD10 ID6.6',length=56.8,
                notes=['OD10 / ID6.6 x 56.8, axis along Y in router mode. Weld flush through both beam walls and the 6 mm stacking pad. In storage these sleeves align vertically; no crushing of hollow beam walls.'])
            bc.register(p,'beam',index,datum)
    for side,(shelf_id,x,parkx) in enumerate((('G_RACK_BEAM_SHELF_1_1',123,85),('G_RACK_BEAM_SHELF_2_1',1027,1065)),1):
        shelf=m.find(shelf_id);b=bbox(shelf.shape)
        tools=[]
        for y in (25.4,115.4):tools.append(cyl(6.6,8).translate((x,y,578)))
        for y in (20,120):tools.append(cyl(6.6,8).translate((parkx,y,578)))
        update_world_local(shelf,shelf.shape.cut(cq.Compound.makeCompound(tools)))
        shelf.flat['holes'].extend([(xx-b[0],yy-b[1],6.6) for xx,yy in ((x,25.4),(x,115.4),(parkx,20),(parkx,120))])
        shelf.notes.append('Two stack locking holes at Y25.4/115.4 and separate parked-bolt holes Y20/120. Match drill after welding. M6 stack bolts are mandatory before operating with the bed stored.')
        for row,(y,parky) in enumerate(((25.4,20),(115.4,120)),1):
            datum=(parkx,parky,456.6)
            p=m.add(f'H_STACK_LOCK_BOLT_{side}_{row}',socket_bolt(6,130,10,6),origin=datum,pn='STD_M6x130_FULLTHREAD_SOCKET',group='bed_restraint',material='Steel class 8.8 M6 full thread',purchased=True,color=HARDWARE,
                notes=['FULL THREAD REQUIRED over the usable 130 mm length: the parked nut sits near the head. A normal long partial-thread socket screw cannot clamp in the parking position. Verify the purchased full-thread variant before ordering.',
                       'Park clamped through separate empty-shelf hole in router mode. In storage, bolt both beams through welded sleeves and shelf; washers and M6 nut under shelf. Tighten only to qualified sleeve/rack preload.'])
            _STORED[p.id]=place(p.local,(x,y,570.2))
            # Parked bolt is tightened at the HEAD end; nut directly below shelf.
            for suffix,zpark,zstore in (('TOP_WASHER',585,698.6),('LOW_WASHER',577.4,577.4)):
                p=m.add(f'H_STACK_LOCK_{suffix}_{side}_{row}',pipe(1.6,12,6.4),origin=(parkx,parky,zpark),pn='STD_M6_WASHER_12',group='bed_restraint',material='Steel washer',purchased=True,color=HARDWARE)
                _STORED[p.id]=place(p.local,(x,y,zstore))
            p=m.add(f'H_STACK_LOCK_NUT_{side}_{row}',hex_nut(),origin=(parkx,parky,572.4),pn='STD_M6_HEX_NUT',group='bed_restraint',material='Steel M6 nut',purchased=True,color=HARDWARE)
            _STORED[p.id]=place(p.local,(x,y,572.4))
    return {'sleeves':8,'stack_bolts':4,'fastener':'FULLY THREADED M6 x 130 class 8.8 socket screw, two 12 mm OD washers and M6 nut per bolt; verify full-thread supplier variant',
        'installed_stored_centers_xy_mm':[[x,y] for x in (123,1027) for y in (25.4,115.4)],
        'sequence':'All four beams fully seated, then transfer four parked bolts into the aligned storage sleeves. Remove all four locks before moving any beam. Separate shelf parking stays outside the handling lanes.'}


def temporary_beam_capture(m):
    """Two clearance box clips close around both beams during front-seat work.

    No reliance on friction: a removable front gate closes each C profile and
    a transverse locator screw joins each clip to beam 2's sleeved thread.
    """
    by=bc.BEAM_Y[1]
    outline=[(0,0),(98,0),(98,116),(0,116),(0,110),(92,110),(92,6),(0,6)]
    for idx,x in enumerate((350.0,780.0),1):
        park=(145,900+130*(idx-1),436.096);active=(x,428,863)
        def add(ident,local,**kw):
            p=m.add(ident,local,origin=park,group='bed_temporary_restraint',**kw)
            _TEMPORARY[p.id]=place(local,active,u=(0,1,0),v=(0,0,1))
            return p
        frame=plate(outline,12.7)
        # Gate bolts along local Y through the top and bottom jaws.
        frame=frame.cut(place(cyl(5.5,118),(5,-1,6.35),u=(1,0,0),v=(0,0,-1)))
        frame=frame.cut(place(cyl(6.6,8),(91,32.4,6.35),u=(0,1,0),v=(0,0,1))).clean()
        p=add(f'H_TEMP_BOX_{idx}',frame,pn='H_TEMP_BOX_C_FRAME',material='Low carbon steel 12.7 mm',
            flat={'outline':outline,'thickness_mm':12.7,'holes':[],'slots':[],'internal':[],
                  'machining_notes':['Two edge-drilled 5.5 mm gate holes at local X5, Z6.35, along Y through both 6 mm jaws.','Back spine: edge-drill 6.6 along X at local Y32.4, Z6.35.','Use 12.7 mm steel; the owner aluminum inventory is not assumed suitable.']},
            notes=['Temporary boxed keeper around beam 1 resting on beam 2. Capture opening Y438..520, Z869..973; nominal beam1 side body begins Y439.1 and ends Z971.6.',
                   'Slide C-frame from the rear after beam1 is resting. Insert front gate and both M5 screws; engage transverse M6 locator screw in beam2 sleeve before releasing either front seat.',
                   'This is a containment fixture, not a lifting attachment. Verify actual beam stack fit and handling load before use. Remove both complete fixtures before lifting beam1.'])
        gate=box(10,104,12.7).translate((0,6,0))
        for yy in (5,98):gate=gate.cut(place(cyl(5,13),(5,yy,6.35),u=(1,0,0),v=(0,0,-1))).clean()
        add(f'H_TEMP_GATE_{idx}',gate,pn='H_TEMP_BOX_GATE',material='Low carbon steel',
            notes=['10 x 104 x 12.7 removable gate; drill/tap M5 axially at each end, 12 mm minimum engagement depth. Actual screws engage nominal 10 mm.'])
        for k,yy,direction in ((1,0,1),(2,116,-1)):
            screw=cyl(5,16).fuse(cyl(9.5,2.75).translate((0,0,-2.75))).clean()
            local=place(screw,(5,yy,6.35),u=(1,0,0),v=(0,0,-direction))
            add(f'H_TEMP_GATE_SCREW_{idx}_{k}',local,pn='STD_M5x16_BUTTON',material='Steel M5x16',purchased=True,color=HARDWARE)
        local=place(socket_bolt(6,40,10,6),(59.6,32.4,6.35),u=(0,1,0),v=(0,0,1))
        add(f'H_TEMP_LOCATOR_BOLT_{idx}',local,pn='STD_M6x40_SOCKET',material='Steel M6x40',purchased=True,color=HARDWARE,
            notes=['Transverse locator screw into beam2 compression sleeve. During storage retain this screw in the fixture with its loose M6 nut; remove that storage nut before use.'])
        add(f'H_TEMP_LOCATOR_WASHER_{idx}',place(pipe(1.6,12,6.4),(98,32.4,6.35),u=(0,1,0),v=(0,0,1)),pn='STD_M6_WASHER_12',material='Steel washer',purchased=True,color=HARDWARE)
        add(f'H_TEMP_LOCATOR_SPACER_{idx}',place(pipe(16.1,12,6.4),(75.9,32.4,6.35),u=(0,1,0),v=(0,0,1)),pn='H_TEMP_SPACER_16_1',material='Steel tube',
            notes=['OD12 ID6.4 x16.1 spacer between beam2 rear wall and clip back spine.'])
        # Stored retaining nut remains in its own lid pocket during fixture use.
        m.add(f'H_TEMP_STORAGE_NUT_{idx}',place(hex_nut(),(70.9,32.4,6.35),u=(0,1,0),v=(0,0,1)),origin=park,pn='STD_M6_HEX_NUT',group='bed_temporary_restraint',material='Steel M6 nut',purchased=True,color=HARDWARE,
              notes=['Storage-only retaining nut. Remove and leave in the dry tray before engaging fixture locator screw in beam2.'])
        # A real sleeve, replacing clearance-only contact with thin tube wall.
        sx=x+6.35
        beam=m.find('G_BEAM_2');tool=place(cyl(10,52.8),(sx,by-26.4,895.4),u=(1,0,0),v=(0,0,-1))
        update_world_local(beam,beam.shape.cut(tool))
        beam.part_number='H_BED_BEAM_924_TEMP_LOCATORS'
        p=m.add(f'H_TEMP_BEAM2_SLEEVE_{idx}',pipe(50.8,10,6),origin=(sx,by-25.4,895.4),u=(1,0,0),v=(0,0,-1),pn='H_TEMP_LOCATOR_SLEEVE_50_8',group='bed_beam',material='Machined steel',length=50.8,
            notes=['OD10 x50.8 welded flush through both beam2 walls. Drill 5 and tap M6 x1 through after welding; nominal thread envelope ID6. Temporary box-clip locator uses the rear end.'])
        bc.register(p,'beam',1,(113,by-25.4,842))
    m.add_plate('H_TEMP_TRAY_FLOOR',115,266,3,origin=(140,890,433.096),group='bed_storage',
        notes=['Seal-weld small dry fixture tray to reservoir lid; fit to actual lid flatness. Two complete box clips lie flat in the tray.'])
    for n,x in enumerate((137,255),1):
        m.add_plate(f'H_TEMP_TRAY_SIDE_{n}',266,16,3,origin=(x,890,436.096),u=(0,1,0),v=(0,0,1),pn='H_TEMP_TRAY_SIDE',group='bed_storage')
    for n,y in enumerate((890,1159),1):
        m.add_plate(f'H_TEMP_TRAY_END_{n}',115,16,3,origin=(140,y,436.096),u=(1,0,0),v=(0,0,1),pn='H_TEMP_TRAY_END',group='bed_storage')
    return {'fixtures':2,'body_material':'12.7 mm low carbon steel','working_locations_x_mm':[350,780],
        'working_opening_mm':{'y':[438,520],'z':[869,973]},
        'sequence':'After beam1 rests on beam2, fit both C bodies from rear, their front gates and two M5 screws each, then the M6 sleeved locator screws. Only then remove the front seats. Remove both fixtures and return them to the lid pockets before lifting beam1.',
        'scope':'Clearance containment and positive transverse location. Physical fit/load test and small-fixture hand access remain required.'}


def panel_rack_hoops(m):
    """Two bolted removable hoops contain front/back tilt and upward escape."""
    for side,x in enumerate((315.0,835.0),1):
        stage=(280 if side==1 else 307,1320 if side==1 else 1355,543.096)
        datum=(x,110,175)
        made=[]
        top=m.add_plate(f'H_PANEL_HOOP_TOP_{side}',30,247,3,holes=[(15,110,6.6)],origin=(x-15,0,573.5),pn='H_PANEL_HOOP_TOP',group='bed_rack_restraint',
            notes=['3 mm steel top bar, with separate 20 mm end skirts seal-welded underneath. Nominal panel top Z572; bar underside Z573.5 gives 1.5 mm lift clearance.',
                   'Two removable hoops fit outside X325..825 panel width. They contain upward escape and fore/aft top motion; bolts into steel rack seats give positive attachment.',
                   'Before conversion separate the upper bars at their M6 screws and stage them in the lid pockets. Then release and stage the bare rods on their saddles. After storing boards, reinstall rods before loading panels. Install top bars after all six panels are seated and before lowering beams.'])
        top.local=top.local.cut(cq.Solid.makeCone(3.3,6.3,3).translate((15,110,0))).clean()
        top.shape=place(top.local,(x-15,0,573.5));top.flat['machining_notes']=['Top-face 90 degree countersink diameter12.6, nominal full 3 mm plate depth; M6 x12 countersunk screw head finishes flush at Z576.5.']
        made.append(top)
        for k,y in enumerate((4,247),1):
            p=m.add_plate(f'H_PANEL_HOOP_SKIRT_{side}_{k}',30,20,3,origin=(x-15,y,553.5),u=(1,0,0),v=(0,0,1),pn='H_PANEL_HOOP_SKIRT',group='bed_rack_restraint',
                notes=['Weld to underside of top bar; front inside face Y4 and rear inside face Y244 give nominal 3.0 /3.225 mm clearance to panel bundle.'])
            made.append(p)
        rod=cyl(10,398.5).cut(cyl(6,15)).cut(cyl(6,15).translate((0,0,383.5))).clean()
        p=m.add(f'H_PANEL_HOOP_ROD_{side}',rod,origin=(x,110,175),pn='H_PANEL_HOOP_ROD_398_5',group='bed_rack_restraint',material='Machined steel round bar',length=398.5,
            notes=['OD10 x398.5 steel rod; drill5/tapM6 both ends at least15 mm deep. Nominal thread envelopes shown. Two end screws connect rack seat and top bar.'])
        made.append(p)
        screw=cyl(6,9).fuse(cq.Solid.makeCone(3,6,3).translate((0,0,9))).clean()
        p=m.add(f'H_PANEL_HOOP_UPPER_SCREW_{side}',screw,origin=(x,110,564.5),pn='STD_M6x12_CSK',group='bed_rack_restraint',material='Steel M6x12',purchased=True,color=HARDWARE);made.append(p)
        p=m.add(f'H_PANEL_HOOP_LOWER_SCREW_{side}',screw,origin=(x,110,181),u=(1,0,0),v=(0,-1,0),pn='STD_M6x12_CSK',group='bed_rack_restraint',material='Steel M6x12',purchased=True,color=HARDWARE,
            notes=['Detach the upper bar first. Then release this lower screw and remove the bare rod. Screw may be loosely rethreaded into the rod end for staged storage.']);made.append(p)
        seat=m.find(f'G_RACK_PANEL_SEAT_{side}');bb=bbox(seat.shape)
        seat.part_number='H_RACK_PANEL_SEAT_'+str(side)
        cutter=cyl(6.6,8).translate((x,110,168)).fuse(cq.Solid.makeCone(6.3,3.3,3).translate((x,110,169)))
        update_world_local(seat,seat.shape.cut(cutter))
        seat.flat['holes'].append((x-bb[0],110,6.6));seat.flat.setdefault('machining_notes',[]).append('Rev H hoop mounting hole: diameter12.6 x3 mm deep 90-degree countersink from BOTTOM face, not the top.')
        for p in made:
            _STAGED[p.id]=p.shape.translate(tuple(-v for v in datum)).rotate((0,0,0),(1,0,0),90).translate(stage)
        # Upright transverse hoop rests on its front edge; horizontal long rod
        # receives a second saddle well left of the water service hatch zones.
        stand=box(20,30,110).cut(box(16,26,112).translate((2,2,-1)))
        stand=stand.cut(place(cyl(10,32),(10,-1,110),u=(1,0,0),v=(0,0,-1))).clean()
        m.add(f'H_PANEL_HOOP_STAGE_SADDLE_{side}',stand,origin=(stage[0]-10,1270 if side==1 else 1290,433.096),pn='H_PANEL_HOOP_STAGE_SADDLE',group='bed_storage',material='Fabricated steel tube 20x30x2',
            notes=['Weld staging saddle to reservoir lid. Rod rests in an OD10 saddle at center Z543.096; upright hoop front edge rests on lid Z433.096. These separated supports prevent resting on a single edge. Match-fit actual rod, deburr and use thin replaceable anti-rattle liner within measured clearance.'])
        sy=stage[1]-398.5
        for k,y in enumerate((sy-4,sy+24),1):
            m.add_plate(f'H_PANEL_HOOP_POCKET_END_{side}_{k}',40,10,3,origin=(stage[0]-20,y,433.096),u=(1,0,0),v=(0,0,1),pn='H_PANEL_HOOP_POCKET_END',group='bed_storage',
                notes=['Weld this 10 mm-high dry receiving pocket to the lid. It restrains the upright top bar while the rod is absent. Insert bar 12 mm high then lower onto lid; no unsupported balancing on an edge.'])
        for k,xp in enumerate((stage[0]-20,stage[0]+17),1):
            m.add_plate(f'H_PANEL_HOOP_POCKET_SIDE_{side}_{k}',25,10,3,origin=(xp,sy-4,433.096),u=(0,1,0),v=(0,0,1),pn='H_PANEL_HOOP_POCKET_SIDE',group='bed_storage')
    return {'hoops':2,'lower_release_screws':2,'upper_release_screws':2,
            'installed_top_clearance_mm':1.5,'front_clearance_mm':3,'rear_clearance_mm':3.225,
            'mode_states':'Hoops bolted in both mode states. Stage top bars then rods before boards, reinstall bare rods before panels, then install top bars after panels. Both upper and lower screws require release during conversion.',
            'staging':'Two defined upright reservoir-lid poses with rod saddles; no outside footprint staging.'}


def spoil_rack_guard(m):
    """A pinned folding cap closes over all six boards, opening inside the frame."""
    m.add_plate('H_SPOIL_GUARD_ARM',79.2,30,6,origin=(50.8,450,224),group='bed_storage',
        notes=['Weld to inner face/top region of lower left side rail, matching existing spoil-rack arm elevation. Added arm carries the guard post only.'])
    post=box(20,30,340).cut(box(16,26,342).translate((2,2,-1)))
    post=post.cut(place(cyl(16.6,32),(10,-1,340),u=(1,0,0),v=(0,0,-1))).clean()
    post=post.cut(box(7,8,11).translate((14,23,330))).clean()
    m.add('H_SPOIL_GUARD_POST',post,origin=(110,450,230),pn='H_SPOIL_GUARD_POST_340',group='bed_storage',material='Steel fabricated 20x30x2 tube',length=340,
        notes=['Weld post onto added rack arm. Top half-round relief OD16.6 clears rotating hinge sleeve; pivot center X120/Z570.'])
    m.add_plate('H_SPOIL_GUARD_FRONT_EAR',20,30,4,holes=[(10,15,6.6)],origin=(110,450,555),u=(1,0,0),v=(0,0,1),group='bed_storage',
        notes=['Weld to front face of post; pivot clearance bore.'])
    m.add_plate('H_SPOIL_GUARD_INDEX_EAR',40,51,4,holes=[(10,20,6.6),(30,20,6.6),(10,40,6.6)],origin=(110,484,550),u=(1,0,0),v=(0,0,1),group='bed_storage',
        notes=['Weld to rear face of post. Three holes: pivot, CLOSED index X140/Z570, OPEN index X120/Z590. Keep rear ear at Y480..484 beyond the short boards endingY469.5.'])
    moving=[]
    p=m.add_plate('H_SPOIL_GUARD_TOP',147,411,6,internal=[rect(127,391)],origin=(128,240,573),group='bed_rack_restraint')
    # Correct inner contour has ten millimetre borders, not the helper's origin.
    p.local=plate(rect(147,411),6,internal=[[(10,10),(137,10),(137,401),(10,401)]])
    p.shape=place(p.local,(128,240,573));p.flat['internal']=[[(10,10),(137,10),(137,401),(10,401)]]
    p.notes=['Open guard is indexed vertically inside X111..127. Closed cap underside Z573 is 4.5 mm above the tallest stored boards.',
             'Weld separate front/rear/right skirts and hinge carrier to cap. Positive index bolt must engage the selected OPEN or CLOSED station. No unsupported snap-latch assumption.']
    moving.append(p)
    for name,y in (('FRONT',246),('REAR',651)):
        p=m.add_plate('H_SPOIL_GUARD_'+name,147,10,3,origin=(128,y,563),u=(1,0,0),v=(0,0,1),pn='H_SPOIL_GUARD_END_SKIRT',group='bed_rack_restraint');moving.append(p)
    p=m.add_plate('H_SPOIL_GUARD_RIGHT',402,10,3,origin=(270,246,563),u=(0,1,0),v=(0,0,1),group='bed_rack_restraint');moving.append(p)
    hinge=place(pipe(22,16,6.6),(120,454,570),u=(1,0,0),v=(0,0,-1))
    bridge=box(140,6,6).translate((125,454,573)).fuse(box(140,6,6).translate((125,473.5,573))).clean()
    tab=box(20,6,10).translate((125,473.5,565)).cut(place(cyl(6.6,8),(140,472.5,570),u=(1,0,0),v=(0,0,-1)))
    hinge=hinge.fuse(bridge).fuse(tab).clean()
    p=m.add('H_SPOIL_GUARD_HINGE_CARRIER',hinge,group='bed_rack_restraint',material='Welded steel hinge assembly',
        notes=['OD16 ID6.6 x22 hinge sleeve; two 140 x6 x6 welded bridges reach the cap right border, with full 6 mm butt-weld seams at X265. Rear 20x6x10 tab has Ø6.6 index hole at radius20. Individual STEP is in assembly coordinates. Fit pivot freely after welding.'])
    moving.append(p)
    # A single full-depth opening in the left border accepts the welded hinge
    # carrier. This is an actual through-cut outline, with no hidden pockets.
    p=m.find('H_SPOIL_GUARD_TOP')
    cap_outline=[(0,0),(147,0),(147,411),(0,411),(0,283),(10,283),
                 (10,401),(137,401),(137,10),(10,10),(10,235),(0,235)]
    p.local=plate(cap_outline,6);p.shape=place(p.local,(128,240,573))
    p.flat={'outline':cap_outline,'thickness_mm':6,'holes':[],'slots':[],'internal':[],
            'machining_notes':['Single full-depth opening in left border clears the hinge/index hardware. Two hinge-carrier bridges butt against right inner border at X137 local. No non-through hinge pockets.']}
    for part in moving:
        closed=part.shape;part.shape=closed.rotate((120,0,570),(120,1,570),-90);_STORED[part.id]=closed
    # Fixed pivot bolt: bearings at both ears; moving sleeve does not intersect.
    bolt=socket_bolt(6,50,10,6)
    m.add('H_SPOIL_GUARD_PIVOT_BOLT',bolt,origin=(120,494.4,570),u=(1,0,0),v=(0,0,1),pn='STD_M6x50_SOCKET',group='bed_storage',material='Steel M6x50',purchased=True,color=HARDWARE)
    for idx,y in enumerate((446,485.6),1):
        m.add(f'H_SPOIL_GUARD_PIVOT_WASHER_{idx}',pipe(1.6,12,6.4),origin=(120,y,570),u=(1,0,0),v=(0,0,1),pn='STD_M6_WASHER_12',group='bed_storage',material='Steel washer',purchased=True,color=HARDWARE)
    m.add('H_SPOIL_GUARD_PIVOT_NUT',hex_nut(),origin=(120,490.6,570),u=(1,0,0),v=(0,0,1),pn='STD_M6_HEX_NUT',group='bed_storage',material='Steel M6 nut',purchased=True,color=HARDWARE,
        notes=['Retained pivot bolt, set nut to allow free hinge rotation with axial play controlled; use qualified prevailing-torque nut or double-nut arrangement in the physical build.'])
    # A simple removable M6 bolt+nut, with a true second index hole for OPEN.
    for suffix,shape,pos in (
        ('BOLT',socket_bolt(6,20,10,6),(120,465.6,590)),
        ('WASHER',pipe(1.6,12,6.4),(120,484,590)),
        ('NUT',hex_nut(),(120,468.5,590))):
        p=m.add('H_SPOIL_GUARD_INDEX_'+suffix,shape,origin=pos,u=(1,0,0),v=(0,0,-1),pn='STD_M6_INDEX_'+suffix,group='bed_rack_restraint',material='Steel M6 hardware',purchased=True,color=HARDWARE)
        _STORED[p.id]=p.shape.translate((20,0,-20))
    # Keep the complete hinge/index assembly 30 mm behind the shortest board's
    # rear edge. Its bolt/nut cannot otherwise clear that board's upper corner.
    move_prefixes=('H_SPOIL_GUARD_ARM','H_SPOIL_GUARD_POST','H_SPOIL_GUARD_FRONT_EAR',
                   'H_SPOIL_GUARD_INDEX_EAR','H_SPOIL_GUARD_HINGE_CARRIER',
                   'H_SPOIL_GUARD_PIVOT_','H_SPOIL_GUARD_INDEX_')
    for p in m.parts:
        if p.id.startswith(move_prefixes):
            p.shape=p.shape.translate((0,30,0))
            if p.id in _STORED:_STORED[p.id]=_STORED[p.id].translate((0,30,0))
            p.notes.append('Rev H final assembly places this hinge/index support 30 mm aft of its local drawing datum; see assembly. Rear index ear Y510..514 clears short-board endY469.5.')
    return {'type':'Folding steel cap with bolted open/closed index stations','hinge_axis_mm':[[120,0,570],[120,1,570]],
        'open_rotation_deg':-90,'close_after':'All six spoilboards fully seated in their prescribed slots.',
        'nominal_clearances_mm':{'above_boards':4.5,'front':4,'rear':1,'right':2},
        'retention':'Index bolt remains fitted in OPEN position during transfer and CLOSED during plasma-layout storage. Pivot and index nut retention must be qualified physically.'}


def extend_router_model(m):
    _STORED.clear();_STAGED.clear();_INITIAL.clear();_TEMPORARY.clear()
    details={'revision':'H bed completion','nut_strips':nut_strips(m),'beam_stack_locks':beam_stack_locks(m),
             'temporary_beam_capture':temporary_beam_capture(m),'panel_rack_hoops':panel_rack_hoops(m),
             'spoil_rack_guard':spoil_rack_guard(m)}
    for p in m.parts:
        if p.id.startswith('H_'):_INITIAL[p.id]=p.shape
    m.holds.append('Rev H fabricated restraints, nut strips and their welds/threads require measured fit and physical load/retention qualification; nominal CAD does not establish a storage or handling rating.')
    return details


def extend_stored_model(m,source=None):
    for p in m.parts:
        if p.id in _STORED:p.shape=_STORED[p.id]
    return m


def prepare_handling_model(m):
    """Keep stack bolts parked and release/stage removable rack retainers."""
    for p in m.parts:
        if p.id in _INITIAL and p.id in _STORED:p.shape=_INITIAL[p.id]
        if p.id in _STAGED:p.shape=_STAGED[p.id]
    return m


def restraint_ids():
    return {'stored_state_ids':sorted(_STORED),'staged_state_ids':sorted(_STAGED),'temporary_capture_ids':sorted(_TEMPORARY)}


def set_temporary_capture(m,engaged=True):
    for p in m.parts:
        if p.id in _TEMPORARY:p.shape=_TEMPORARY[p.id] if engaged else _INITIAL[p.id]
    return m


def prepare_panel_handling_model(m):
    prepare_handling_model(m)
    for p in m.parts:
        if p.id.startswith(('H_PANEL_HOOP_ROD_','H_PANEL_HOOP_LOWER_SCREW_')):p.shape=_INITIAL[p.id]
        if p.id.startswith('H_SPOIL_GUARD_') and p.id in _STORED:p.shape=_STORED[p.id]
    return m


def prepare_beam_handling_model(m):
    prepare_panel_handling_model(m)
    for p in m.parts:
        if p.id in _STAGED:p.shape=_INITIAL[p.id]
    return m
