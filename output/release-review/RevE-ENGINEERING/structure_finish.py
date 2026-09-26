"""Rev I structural completion extension; historical Rev H source remains untouched."""
import cadquery as cq
import bed_completion as h
from cad_helpers import *

ROD_DIAMETER=14.0
SOCKET_BORE=14.2
SOCKET_OD=18.2

def extend_router_model(m):
    for side,x in ((1,315.0),(2,835.0)):
        rod=m.find('H_PANEL_HOOP_ROD_'+str(side))
        rod.local=cyl(ROD_DIAMETER,398.5).cut(cyl(6,15)).cut(cyl(6,15).translate((0,0,383.5))).clean()
        rod.shape=place(rod.local,(x,110,175));rod.part_number='I_PANEL_HOOP_ROD_14x398_5'
        rod.material='Machined steel round bar; certified yield >=300 MPa'
        rod.notes=['Diameter14.00 +/-0.05; length398.5. Drill5/tapM6 both ends at least15 deep. No coating on receiver engagement length or saddle contact.',
            'Lower40 mm is laterally supported by the socket. Storage-retention design case100 N horizontal at one rod top; no lifting or personnel load.',
            'The specified minimum material yield300 MPa is a procurement acceptance requirement, not an assertion about unidentified scrap.']
        seat=m.find('G_RACK_PANEL_SEAT_'+str(side));bb=bbox(seat.shape)
        seat_x=300.0 if side==1 else 805.0
        seat.local=plate(rect(45,245),8,holes=[(x-seat_x,110,SOCKET_OD)])
        seat.shape=place(seat.local,(seat_x,0,167));seat.flat['thickness_mm']=8;seat.flat['outline']=rect(45,245)
        seat.part_number='I_RACK_PANEL_SEAT_'+str(side)
        seat.flat['holes']=[(x-seat_x,110,SOCKET_OD)]
        seat.flat['machining_notes']=[n for n in seat.flat.get('machining_notes',[]) if 'Rev H hoop mounting hole' not in n]
        seat.flat['machining_notes'].append('Hoop receiver: drill/finish diameter18.2 fit to actual turned socket. Socket projects3 below bottom face (seat bottomZ167); weld underside only, then finish bore. No seat countersink.')
        seat.notes.append('Rev I seat45 x245 x8; widened outward5 mm to support the full underside socket weld. Top remainsZ175. Socket carries rod bending through40 mm bearing length; bottom screw retains axially, not as a cantilever fixing.')
        web=m.find('G_RACK_PANEL_WEB_'+str(side));wb=bbox(web.shape)
        outline=[(0,0),(245,0),(245,15.4),(124,15.4),(124,10.4),(96,10.4),(96,15.4),(0,15.4)]
        web.local=plate(outline,6);web.shape=place(web.local,(wb[0],0,151.6),u=(0,1,0),v=(0,0,1))
        web.part_number='I_RACK_PANEL_WEB_SOCKET_RELIEF';web.flat['outline']=outline
        web.notes.append('28 x5 upper-edge relief at worldZ162, station96..124 clears the socket projection and underside weld. Remaining web height10.4; square notch corners may be eased within the removed material.')
        socket=cyl(SOCKET_OD,51).cut(cyl(SOCKET_BORE,41).translate((0,0,11))).cut(cyl(6.6,12).translate((0,0,-1))).cut(cq.Solid.makeCone(6.3,3.3,3)).clean()
        m.add('I_PANEL_ROD_SOCKET_'+str(side),socket,origin=(x,110,164),pn='I_PANEL_ROD_SOCKET_18_2x51',group='bed_fixed',material='Machined low carbon steel; yield >=250 MPa',length=51,
              notes=['Turn OD18.2 x51. Guide bore14.20 +0.05/-0.00,40 deep from TOP. Axial throughhole6.6; bottom90deg countersink12.6x3 deep.',
              'Fit through8 mm rack seat with3 mm lower projection. Continuous3 mm fillet under seat ONLY. Finish guide bore after welding; no paint in bore. Deburr entrance without reducing full bearing length.',
              'Actual diametral sliding clearance0.15..0.30 mm with specified rod tolerance. Socket topZ215 gives40 mm engagement. Nominal panel side clearance0.9 mm; verify >=0.5 mm after welding.'])
        weld=cq.Solid.makeCone(SOCKET_OD/2,SOCKET_OD/2+3,3).cut(cyl(SOCKET_OD,3)).clean()
        m.add('I_PANEL_ROD_SOCKET_WELD_'+str(side),weld,origin=(x,110,164),pn='I_ROD_SOCKET_WELD_3',group='weld_definition',material='E70 weld deposit',
              notes=['Nominal3 mm continuous underside fillet. Weld geometry is included for clearance; preparation and sound fusion require shop qualification.'])
        lower=m.find('H_PANEL_HOOP_LOWER_SCREW_'+str(side))
        lower.local=cyl(6,17).fuse(cq.Solid.makeCone(3,6,3).translate((0,0,17))).clean()
        lower.shape=place(lower.local,(x,110,184),u=(1,0,0),v=(0,-1,0));lower.part_number='STD_M6x20_CSK';lower.material='Steel M6x20 class8.8'
        lower.notes=['Rev I M6x20 countersunk screw replaces M6x12;9 mm nominal engagement into rod after socket base. Release after upper bar removal, then lift rod60 mm to clear40 mm socket. Axial retention only.']
        saddle=m.find('H_PANEL_HOOP_STAGE_SADDLE_'+str(side));old=bbox(saddle.shape)
        tool=place(cyl(ROD_DIAMETER,32),(old[0]+10,old[1]-1,543.096),u=(1,0,0),v=(0,0,-1))
        h.update_world_local(saddle,saddle.shape.cut(tool));saddle.part_number='I_PANEL_HOOP_STAGE_SADDLE_14'
        saddle.notes=['Revised matching diameter14 open saddle; rod centerZ543.096 unchanged. Finish to actual shaft; no thick liner or paint within nominal fit.']
        stage=(280 if side==1 else 307,1320 if side==1 else 1355,543.096)
        for p in (rod,lower):
            h._INITIAL[p.id]=p.shape
            h._STAGED[p.id]=p.shape.translate((-x,-110,-175)).rotate((0,0,0),(1,0,0),90).translate(stage)
        h._INITIAL[saddle.id]=saddle.shape
    for p in m.parts:
        if p.id.startswith(('G_PANEL_CLAMP_BOLT_','G_BEAM_BOLT_','G_FRONT_SEAT_BOLT_','G_SPOIL_')) and ('BOLT' in p.id or 'SCREW' in p.id):
            p.notes.append('Rev I current preload definition is in output/design-finish-2026-09-26/structure/JOINTS.md; historical 12/6 N m torque examples are not instructions for this joint. Do not substitute ordinary bolt-table torque for extrusion/bridge limits.')
    return {'revision':'I','rod_mm':[14,398.5],'rod_material_min_yield_MPa':300,'socket_mm':{'OD':18.2,'bore':14.2,'height':51,'engagement':40},
        'design_case':'100 N horizontal at one panel rod top; storage restraint only',
        'nominal_panel_clearance_mm':0.9,'assembly_changes':['Two rods','Two lowerM6x20 screws','Two receiver sockets and underside welds','Two enlarged saddle cuts','Two8 mm receiver seats and relieved webs'],
        'source_scope':'Calculations and physical acceptance in output/design-finish-2026-09-26/structure. No complete tool-to-work rigidity rating.'}

def extend_stored_model(m,source=None):
    return m

