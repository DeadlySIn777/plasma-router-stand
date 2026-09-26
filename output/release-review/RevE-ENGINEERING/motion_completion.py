"""Evidence-driven motion completion features for the Rev H integration.

No fabricated mating dimensions are supplied for a purchased interface. The
adapter defaults to a guarded transfer-drill blank. Optional drilled adapters
and torch clamps require explicit measurements. Brake motor is a sourced
replacement candidate, not an assumed fit to the original coupling.
"""
from dataclasses import dataclass
import math
from cad_helpers import box, cyl, plate, rect, place, bbox, Model, ALU, PURCHASED

HOLD = 'INTERFACE HOLD - INDIVIDUAL EXPORT GUARDED'
BRAKE_PN = '23HS30-5004D-B280'
BRAKE_SOURCE = ('https://www.omc-stepperonline.com/nema-23-stepper-motor-2-0nm-283-22oz-in-'
                'with-24v-4-5w-electromagnetic-brake-23hs30-5004d-b280')


@dataclass(frozen=True)
class OutputHole:
    """Measured coordinates in adapter local XY; caller selects real fastener."""
    x_mm: float
    y_mm: float
    clearance_diameter_mm: float
    head_pocket_diameter_mm: float
    head_pocket_depth_mm: float
    verified_thread: str
    verified_usable_engagement_mm: float
    evidence_id: str


def adapter_local(output_holes=()):
    """110 x 110 x 12.7 with existing, designed tool-side 90 x 26 pattern.

    Local Z=0 is output/carriage mating face. Tool mount bolt pockets open
    there; measured carriage screw pockets open at local Z=12.7. No fake
    70 mm slots. Returned flat shares the exact solid operations.
    """
    mount = [(x,y,6.6) for x in (10.,100.) for y in (22.,48.)]
    flat = dict(outline=rect(110,110), thickness_mm=12.7, holes=mount.copy(),
                slots=[], internal=[], operations=[], machining_notes=[
        'Blank only: output fixing pattern absent until recorded from actual ZBX80.',
        'Local Z=0 rear/output face; Z=12.7 front/tool face.',
        'Known custom clamp pattern 90 x 26; rear counterbores diameter10.5 depth6.',
        'Do not drill output holes through an assembled guide or ballscrew. Transfer the centers, remove and drill the plate separately.',
    ])
    s=plate(rect(110,110),12.7,mount)
    occupied=[]
    for x,y,_ in mount:
        s=s.cut(cyl(10.5,6).translate((x,y,0))).clean()
        occupied.append((x,y,10.5/2))
        flat['operations'].append(dict(type='circle',x=x,y=y,diameter=10.5,
                                       layer='MILL_REAR_COUNTERBORE_DEPTH_6'))
    if output_holes and len(output_holes)!=4:
        raise ValueError('Exactly four measured output fixing holes required; do not use guide-assembly bolts.')
    for h in output_holes:
        if not h.verified_thread or not h.evidence_id or h.verified_usable_engagement_mm<=0:
            raise ValueError('Hole thread/access/engagement measurement evidence missing')
        d,hd,depth=h.clearance_diameter_mm,h.head_pocket_diameter_mm,h.head_pocket_depth_mm
        if not 2<d<8 or not d<hd<14 or not 0<depth<=6.7:
            raise ValueError('Fastener/pocket dimensions outside this adapter design envelope')
        radius=hd/2
        if min(h.x_mm,h.y_mm,110-h.x_mm,110-h.y_mm)<radius+5:
            raise ValueError('Less than 5 mm material beyond head pocket')
        if any(math.hypot(h.x_mm-x,h.y_mm-y)<radius+r+3 for x,y,r in occupied):
            raise ValueError('Output head pocket conflicts with another pocket (3 mm minimum web)')
        occupied.append((h.x_mm,h.y_mm,radius))
        s=s.cut(cyl(d,14.7).translate((h.x_mm,h.y_mm,-1))).clean()
        s=s.cut(cyl(hd,depth).translate((h.x_mm,h.y_mm,12.7-depth))).clean()
        flat['holes'].append((h.x_mm,h.y_mm,d))
        flat['operations'].append(dict(type='circle',x=h.x_mm,y=h.y_mm,diameter=hd,
            layer='MILL_FRONT_COUNTERBORE_DEPTH_'+str(depth).replace('.','p')))
    if output_holes:
        flat['machining_notes'][0]='Output pattern from explicit measurement records; connection load/fastener check still required.'
    return s,flat


def apply_completion(m, *, replacement_brake_motor=False):
    """Apply safe metadata/blank corrections; optionally reserve brake motor.

    Call immediately after build_revg.build_model and before storage transforms.
    Keeps the interface hold. Existing spindle/clamp geometry and working
    envelope are unchanged. The motor replacement option is a procurement and
    coupling-fit candidate only; its stock motor is removed, not overlapped.
    """
    p=m.find('TOOL_ADAPTER_110'); b=bbox(p.shape)
    p.local,p.flat=adapter_local()
    p.shape=place(p.local,(b[0],b[4],b[2]),u=(1,0,0),v=(0,0,1))
    p.part_number='H_TOOL_ADAPTER_TRANSFER_BLANK'
    p.release=HOLD
    p.notes=[
        'Rev H transfer-drill blank: obsolete assumed output slots removed. No output attachment fasteners are invented.',
        'Record output height and all four fixing-hole coordinates, thread/pitch, usable depth and access before machining this guarded plate.',
        'Custom tool-side four M6 clearance holes and rear counterbores are defined; Z output attachment is not released.',
        'The present 80 mm output stack is a placement assumption, not a supplier measurement.',
    ]
    for item in m.parts:
        item.notes=[n for n in item.notes if 'torch split clamp (bore' not in n]
        if item.id=='ZBX80_OUTPUT_HOLD':
            item.notes=[
                'Exact-ASIN top view gives a 90 x 50 output carriage. The 70 mm transverse dimension joins the smaller diameter5 fixing holes; it does not qualify the larger assembly bores as tool attachments.',
                'Output height, along-travel fixing pitch, thread/depth and tool access remain unmeasured. Rev H reserves an 80 mm stack only as a placement assumption and uses an undrilled output-interface blank, without assumed adjustment slots.',
            ]
        if item.id=='ZBX80_MOTOR':
            item.notes.append('Exact B09MVYGLNQ listing checked 26 September 2026: 3 A, 1.2 N.m, 3.8 mH, 1.1 ohm, single output shaft. No rear shaft for an assumed bolt-on brake.')
    if replacement_brake_motor:
        old=m.find('ZBX80_MOTOR'); bb=bbox(old.shape)
        # Envelope remains at original flange plane and shaft axis; those mating
        # fields need confirmation before selecting this as an installed part.
        old.local=box(57,57,116.5)
        old.shape=place(old.local,bb[:3])
        old.part_number='CANDIDATE_'+BRAKE_PN
        old.material='Purchased replacement brake motor clearance envelope; not mass solid'
        old.release='REPLACEMENT CANDIDATE - COUPLING/PILOT HOLD - INDIVIDUAL EXPORT GUARDED'
        old.color=PURCHASED
        old.notes=[
            'Candidate replacement, not an add-on to the original single-ended motor. Source: '+BRAKE_SOURCE,
            '57 x 57 x 116.5 body; shaft diameter8 x21 long, D-flat15. Body extends60.5 above the old56 envelope.',
            'Two-phase1.8 degree, 5 A/phase, 2.0 N.m holding; brake power-off type, 2.8 N.m static,24 V/4.5 W.',
            'Motor mount pilot, four mounting holes, shaft alignment/engagement and coupling bore remain unverified against ZBX80. Shaft and cables not silently included in this body solid.',
            'Brake does not bypass coupling, ballscrew or attachment failure. Static rating is not an emergency-stop energy rating.',
            'Brake must engage before driver torque is removed; release only after motor torque is established. Brake coil uses a separately rated24 V switched circuit, never a motor phase or logic pin.',
        ]
        guard=m.find('ZBX80_COUPLER_GUARD')
        guard.notes=[
            'Original stock module overall envelope is 330 mm from Z1040 to1370. The optional 116.5 mm brake-motor body extends the current reserved overall envelope to390.5 mm, ending atZ1430.5.',
            'This body reserves the coupling/bracket zone only. Actual motor pilot, shaft, coupling and connector projections are unverified and are not modeled as established hardware.',
        ]
        m.holds[:]=[
            ('Z power-loss retention: a 23HS30-5004D-B280 replacement brake motor is a sourced candidate, but no installed restraint is qualified. Shaft/coupling/pilot fit, stopped-load retention, brake sequencing and response under power loss require acceptance. A ballscrew must not be assumed self-locking.'
             if h.startswith('Z power-loss retention:') else h)
            for h in m.holds]
        m.holds.append('Candidate 23HS30-5004D-B280 replaces the stock Z motor only after shaft/coupling/pilot fit, brake timing, thermal and stopped-load retention acceptance. No production brake mount released.')
    return {'adapter':'transfer-drill blank, no unverified output holes',
            'replacement_brake_motor_candidate':bool(replacement_brake_motor),
            'active_motion_holds':[h for h in m.holds if h.startswith(('Z slide:','HGR20:','HMS40:','Z power-loss retention:','Head projection','X/Y physical stops','Candidate 23HS30'))],
            'torch_interface':'measured clamp generator only; no operating torch assembly',
            'source_date':'2026-09-26'}


def extend_router_model(m):
    """Integration contract: reserves the explicitly labelled braked alternative."""
    result=apply_completion(m,replacement_brake_motor=True)
    result['brake_static_screen']=static_brake_screen(20,downward_external_force_n=200)
    result['brake_static_screen']['load_case_status']='Design screening case only:20 kg moving stack plus200 N downward force; confirm actual loads.'
    return result


def extend_stored_model(stored,source):
    """No second transform: old IDs intentionally retain Rev G storage behavior."""
    return {'status':'No extra transform required; adapter/motor retain original IDs.',
            'operational_plasma_head_present':False}


@dataclass(frozen=True)
class TorchMeasurement:
    barrel_diameter_mm: float
    straight_clamp_length_mm: float
    nozzle_to_clamp_bottom_mm: float
    barrel_diameter_uncertainty_mm: float
    evidence_id: str
    clamp_zone_confirmed_insulated: bool


def torch_clamp(measurement):
    """Separate two-piece machining candidate, NEVER invent a torch diameter.

    Same tool-side mount as custom spindle clamp. Two halves are machined from
    billet, NOT claimed to fit the owner's thin plate. Explicitly not a floating
    head/breakaway, and not installed in a whole-machine assembly by this API.
    Local tool axis (0,-45.5), Z=0 is clamp bottom, rear mating face Y=0.
    """
    d=measurement.barrel_diameter_mm
    if not 20<=d<=40:
        raise ValueError('Measured barrel outside 20..40 mm design envelope; redesign instead of scaling silently')
    if measurement.straight_clamp_length_mm<40:
        raise ValueError('40 mm straight permitted clamp zone required')
    if (not measurement.evidence_id or not measurement.clamp_zone_confirmed_insulated
        or not 0<=measurement.barrel_diameter_uncertainty_mm<=.05
        or measurement.nozzle_to_clamp_bottom_mm<=0):
        raise ValueError('Traceable insulated clamp-zone measurement required')
    bore=cyl(d,42).translate((0,-45.5,-1))
    rear=box(110,45.25,40).translate((-55,-45.25,0)).cut(bore).clean()
    front=box(110,44.75,40).translate((-55,-90.5,0)).cut(bore).clean()
    for x in (-45,45):
        for z in (7,33):
            rear=rear.cut(place(cyl(6,15),(x,0,z),u=(1,0,0),v=(0,0,1))).clean()
    for x in (-47,47):
        rear=rear.cut(place(cyl(6,15),(x,-45.25,20),u=(1,0,0),v=(0,0,-1))).clean()
        front=front.cut(place(cyl(6.6,46),(x,-91,20),u=(1,0,0),v=(0,0,-1))).clean()
    m=Model()
    for suffix,shape in [('REAR',rear),('FRONT',front)]:
        bb=bbox(shape)
        m.add('H_TORCH_CLAMP_'+suffix,shape.translate(tuple(-v for v in bb[:3])),bb[:3],
            pn='H_TORCH_CLAMP_'+suffix,group='tooling_candidate',material='6061-T6 aluminum billet',
            color=ALU,release=HOLD,notes=[
                'Measured diameter '+str(d)+' mm; evidence '+measurement.evidence_id+'. No diameter28 default exists.',
                'Review candidate only.40 mm clamp zone; finish-bore together with0.50 split shim, then verify retention without crushing barrel.',
                'Rear mount: four blind M6 x1 depth15 at X+/-45,Z7/33. Pinch: two M6 x1 depth15 from split face; mating front clearance6.6.',
                'No floating touch-off, breakaway, tool lead or electrical insulation qualification is supplied by these two solids.',
            ])
    return m


def static_brake_screen(moving_mass_kg, lead_mm=5., downward_external_force_n=0.,
                        static_design_factor=3.):
    """Conservative frictionless reverse-drive screen, not rated-axis capacity."""
    if moving_mass_kg<=0 or lead_mm<=0 or downward_external_force_n<0 or static_design_factor<1:
        raise ValueError('Invalid load inputs')
    force=moving_mass_kg*9.80665+downward_external_force_n
    required=force*(lead_mm/1000)/(2*math.pi)*static_design_factor
    return dict(mass_kg=moving_mass_kg,lead_mm=lead_mm,downward_force_n=force,
        design_factor=static_design_factor,required_static_torque_nm=required,
        candidate_static_torque_nm=2.8,static_ratio=2.8/required,
        passed_static_torque_screen=required<=2.8,
        limits='Only stopped static torque through an intact coupling/screw. No dynamic engagement, wear, timing, thermal, shaft fit or system safety conclusion.')
