"""Rev D SOLID-GEOMETRY STUDY -- NOT RELEASED FOR FABRICATION OR CAM.

Units: mm. X right, Y rearward, Z above floor. This is a separate study;
it does not supersede the Rev C concept PDF or claim supplier interface accuracy.

Run with the existing CadQuery environment, from any working directory:
  smart_compressor/enclosure/.venv/Scripts/python.exe -u build_revd_study.py

Nominal hollow tube sections are real solids, with square idealized corners.
Purchased 20100 profiles are explicitly solid ENVELOPES: their cavities, slots,
mass and machining interfaces are NOT represented by those envelopes.
"""
from pathlib import Path
from dataclasses import dataclass, field
import hashlib
import json
import math
import os
import sys
import time

import cadquery as cq

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'step'
OUT.mkdir(parents=True, exist_ok=True)
TUBE = 50.8
WALL = 3.048                    # 0.120 inch, not an assumed exact 11-gauge wall
SHEET = 3.048                   # US-stock study: 0.120 inch sheet
CAP_THICK = 7.9375              # 5/16 inch rail cap, explicit US-stock adaptation
BEAM_LENGTH = 1044.0
BEAM_TOP = 920.8
PROFILE_TOP = 940.8
SLOPE = 0.01
FLOOR_NORMAL_T = SHEET
FLOOR_VERTICAL_T = FLOOR_NORMAL_T * math.sqrt(1 + SLOPE**2)
ANGLE = 25.0
TOL_VOL = 0.01                  # numerical intersection tolerance, mm^3
TOL_DIM = 1e-5

STATUS = 'NOT RELEASED - SOLID GEOMETRY STUDY ONLY'
STEEL = (.25, .31, .34)
ALUMINUM = (.68, .73, .75)
REFERENCE = (.93, .61, .21)
MDF = (.71, .53, .31)
PAN = (.49, .57, .61)


def box(x, y, z, dx, dy, dz):
    return cq.Workplane('XY').box(dx, dy, dz, centered=False).translate((x, y, z)).val()


def bbox(s):
    b = s.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


def hollow_tube(x, y, z, length, axis):
    """Square-corner nominal hollow section, open at both ends."""
    d = [TUBE, TUBE, TUBE]
    d[axis] = length
    outer = box(x, y, z, *d)
    p = [x + WALL, y + WALL, z + WALL]
    inner = [TUBE - 2*WALL] * 3
    p[axis] = [x, y, z][axis] - 1
    inner[axis] = length + 2
    return outer.cut(box(*p, *inner)).clean()


def yz_prism(points, x, thickness_x):
    return cq.Workplane('YZ', origin=(x, 0, 0)).polyline(points).close().extrude(thickness_x).val()


def floor_z(y):
    return 735 + SLOPE * (1275 - y)


def floor_top(y):
    return floor_z(y) + FLOOR_VERTICAL_T


@dataclass
class Part:
    id: str
    shape: cq.Shape
    group: str
    material: str
    geometry_basis: str
    holds: list[str] = field(default_factory=list)
    color: tuple = STEEL
    expected_volume: float | None = None
    purchased_envelope: bool = False

    def transformed(self, shape):
        return Part(self.id, shape, self.group, self.material, self.geometry_basis,
                    self.holds.copy(), self.color, self.expected_volume, self.purchased_envelope)


fixed = []
beam_templates = []
panel_templates = []


def add(target, ident, shape, group, material='steel', basis='nominal concept dimensions',
        holds=(), color=STEEL, expected=None, envelope=False):
    p = Part(ident, shape, group, material, basis, list(holds), color, expected, envelope)
    target.append(p)
    return p


def add_tube(target, ident, xyz, length, axis, group='main_frame'):
    return add(target, ident, hollow_tube(*xyz, length, axis), group,
               basis='50.8 x 50.8 x 3.048 mm nominal hollow tube; square-corner idealization',
               holds=['Confirm supplier corner radii and actual wall tolerance.',
                      'Weld preparation, weld specification, vent/fill ports and local reinforcement are not detailed.'],
               expected=length*(TUBE**2-(TUBE-2*WALL)**2))


# Main frame: the 18 stationary members in the Rev C cut list.
for side, x in enumerate((0.0, 1099.2), 1):
    for station, y in enumerate((0.0, 699.6, 1399.2), 1):
        add_tube(fixed, f'MF_LEG_{side}_{station}', (x, y, 50), 949.2, 2)
        add(fixed, f'FOOT_PLATE_{side}_{station}', box(x-15, y-15, 0, 80, 80, 12),
            'floor_support', basis='80 x 80 x 12 mm blank envelope',
            holds=['Foot plate holes, load-rated foot, thread block, leg closure and reinforcement HOLD.'],
            expected=80*80*12)
        add(fixed, f'FOOT_ADJUSTER_{side}_{station}_ENVELOPE', box(x+16, y+16, 12, 18, 18, 38),
            'floor_support', material='purchased part envelope, no mass',
            basis='Rev C height reservation; not a selected adjustable foot',
            holds=['Actual foot dimensions, rating and load path HOLD.'], color=REFERENCE,
            expected=18*18*38, envelope=True)
    add_tube(fixed, f'MF_TOP_Y_{side}', (x, 0, 999.2), 1450, 1)
    for station, y in enumerate((50.8, 750.4), 1):
        add_tube(fixed, f'MF_LOWER_SIDE_{side}_{station}', (x, y, 230), 648.8, 1)
    add(fixed, f'RAIL_CAP_{side}_BLANK', box(x-24.6, 0, 1050, 100, 1450, CAP_THICK),
        'rail_cap', basis='1450 x 100 x 7.9375 mm blank; 5/16-inch US-stock adaptation',
        holds=['Rail mounting pattern, leveling method, surface finish and flatness HOLD.',
               'Cap datum is 0.0625 mm below original 8 mm cap top.'],
        color=ALUMINUM, expected=100*1450*CAP_THICK)

for name, y, z in [('FRONT_LOW',0,50),('REAR_LOW',1399.2,230),
                   ('FRONT_UPPER',0,679.2),('REAR_UPPER',1399.2,679.2)]:
    add_tube(fixed, 'MF_END_'+name, (50.8, y, z), 1048.4, 0)
for side, x in enumerate((50.8, 1048.4), 1):
    add_tube(fixed, f'MF_RECEIVER_LEDGER_{side}', (x, 0, 789.2), 1450, 1)

# Correct pan-bearer blanks: 1032.4 mm plus 8 mm plate allowance at each end.
for i, y in enumerate((175.0, 675.0, 1175.0), 1):
    add_tube(fixed, f'PAN_BEARER_{i}', (58.8, y, 679.2), 1032.4, 0, 'pan_support')
    for end, x in enumerate((50.8, 1091.2), 1):
        add(fixed, f'PAN_BEARER_END_{i}_{end}_ENVELOPE', box(x,y,679.2,8,TUBE,TUBE),
            'pan_support', basis='8 mm end-plate allowance; 50.8 mm square outline is a reservation',
            holds=['Plate outline, bolts, welds and connections HOLD.'], color=REFERENCE,
            expected=8*TUBE*TUBE, envelope=True)

# Pan: five separate constant-thickness sheet solids with a real 1% floor slope.
# Floor normal thickness is exactly SHEET; top offset therefore differs slightly
# from the vertical sheet dimension. Weld and bend details are intentionally absent.
floor = yz_prism([(75,floor_z(75)),(1275,floor_z(1275)),
                  (1275,floor_top(1275)),(75,floor_top(75))],115,920)
pan_holds = ['Study uses 0.120-inch sheet, not an asserted exact 11-gauge thickness.',
             'Drain/sump, overflow, cleanout, corner welding, flat patterns and support cradles HOLD.']
add(fixed, 'PAN_SLOPED_FLOOR', floor, 'water_pan', basis='920 x 1200 mm plan; 1% slope down to rear; 3.048 mm normal thickness',
    holds=pan_holds, color=PAN, expected=920*1200*FLOOR_VERTICAL_T)
for side, x in enumerate((115, 1035-SHEET), 1):
    shp = yz_prism([(75,floor_top(75)),(1275,floor_top(1275)),(1275,835),(75,835)],x,SHEET)
    expected = SHEET*1200*(835-(floor_top(75)+floor_top(1275))/2)
    add(fixed, f'PAN_SIDE_{side}', shp, 'water_pan', basis='Sloping lower edge follows floor; fixed rim Z=835',
        holds=pan_holds, color=PAN, expected=expected)
for name, y in [('FRONT',75),('REAR',1275-SHEET)]:
    shp = yz_prism([(y,floor_top(y)),(y+SHEET,floor_top(y+SHEET)),(y+SHEET,835),(y,835)],115+SHEET,920-2*SHEET)
    expected = (920-2*SHEET)*SHEET*(835-(floor_top(y)+floor_top(y+SHEET))/2)
    add(fixed, 'PAN_END_'+name, shp, 'water_pan', basis='Constant vertical rim, cut lower edge follows slope',
        holds=pan_holds, color=PAN, expected=expected)
for i, y in enumerate(range(120,1240,60),1):
    add(fixed, f'SLAT_{i:02d}', box(135,y,775,880,SHEET,75), 'slats',
        basis='880 x 75 x 3.048 mm vertical strip; US .120-inch sheet adaptation',
        holds=['Comb supports, retention, sacrificial notch arrangement and plasma grounding HOLD.'],
        expected=880*SHEET*75)

# A transparent-style reference in STEP (color may render opaque in some viewers).
# It is kept in both configurations to check that stored parts avoid the wet bay.
add(fixed, 'RESERVOIR_EXTERNAL_ENVELOPE', box(110,800,175,930,530,380), 'reference_obstacle',
    material='reference envelope, no mass', basis='Rev C exterior clearance reservation only',
    holds=['NOT a vessel or fabrication model. Walls, baffles, lid, supports and plumbing HOLD.',
           'Existing concept is vented; no pressure or vacuum rating is implied.'],
    color=(.43,.68,.71), expected=930*530*380, envelope=True)

# One removable paired beam, local origin at left finished end, Y at pair center,
# Z at tube bottom. Tube blanks are 1032 mm and finished width is 1044 mm.
for j, y in enumerate((-50.8,0.0),1):
    add_tube(beam_templates, f'TUBE_{j}', (6,y,0),1032,0,'removable_beam')
for j, x in enumerate((0,1038),1):
    add(beam_templates, f'END_DIAPHRAGM_{j}', box(x,-50.8,0,6,101.6,50.8), 'removable_beam',
        basis='6 mm end diaphragm blank',
        holds=['Hole pattern, welds and seam/load-transfer connections HOLD. End plates alone do not prove equal load sharing.'],
        expected=6*101.6*50.8)
for j, x in enumerate((6,998),1):
    add(beam_templates, f'RISER_FOOT_{j}_ENVELOPE', box(x,-45,-30,40,90,30),'removable_beam',
        basis='40 x 90 x 30 mm reservation, NOT a solid stock specification',
        holds=['Foot construction, receiver seats, locator pins and draw-down hardware HOLD.',
               'Primary clamp solids omitted: old illustrative clamps collided with panel corners.'],
        color=REFERENCE, expected=40*90*30,envelope=True)

# One direct-bearing cassette, local bottom of purchased profiles at Z=0.
# Slots/cavities cannot be invented from an outer dimension or listing image.
for j in range(5):
    add(panel_templates, f'STRIP_{j+1}_PURCHASED_ENVELOPE',box(j*100,0,0,100,397,20), 'cassette',
        material='purchased 6063-T5 profile envelope, no mass',
        basis='20 x 100 x 397 mm outer envelope for IXGNIJ 20100 / ASIN B0BXNWK99C',
        holds=['Supplier section/slot geometry, straightness, load properties and T-nut interface HOLD.',
               'Envelope volume is not aluminum volume and must not be used for weight.'],
        color=ALUMINUM,expected=100*397*20,envelope=True)
for j, y in enumerate((75,297),1):
    add(panel_templates,f'UNDERSIDE_TIE_{j}_BLANK',box(0,y,-6,500,25,6), 'cassette',
        material='aluminum, alloy pending',basis='500 x 25 x 6 mm tie-bar blank placed within beam-free bay',
        holds=['Joining bolts, T-nuts, hole positions, hardware projection and alloy HOLD.',
               'Tie bars keep strip order; their presence does not establish monolithic panel stiffness.'],
        color=ALUMINUM,expected=500*25*6)
add(panel_templates,'OPTIONAL_19mm_MDF_BLANK',box(0,0,20,500,397,19),'optional_spoilboard',
    material='MDF',basis='Optional 19 mm blank/clearance envelope, not part of the bare T-slot work plane',
    holds=['Fastening, pocket access, spoilboard surfacing and dust protection HOLD.',
           'US 3/4-inch stock is nominally 19.05 mm and adds 0.05 mm if selected.'],
    color=MDF,expected=500*397*19)


def named_transform(template, prefix, transform):
    p = template.transformed(transform(template.shape))
    p.id = prefix + p.id
    return p


def config(stowed=False, optional_mdf=True):
    result = list(fixed)
    for i, y in enumerate((75,475,875,1275) if not stowed else (120,230,340,450),1):
        if stowed:
            transform = lambda s,y=y: s.rotate((0,0,0),(0,1,0),-ANGLE).translate((111.5,y,185))
        else:
            transform = lambda s,y=y: s.translate((53,y,870))
        result.extend(named_transform(p,f'BEAM_{i}_',transform) for p in beam_templates)
    for row in range(3):
        for col in range(2):
            if stowed:
                # X_local -> Z_world, Y_local -> X_world, Z_local -> Y_world.
                # Tie bar starts at world Y; optional MDF ends at Y+45.
                x, y = (130,623)[col], (525,580,635)[row]
                transform = lambda s,x=x,y=y: s.rotate((0,0,0),(1,1,1),-120).translate((x,y+6,150))
            else:
                x,y=(73.5,576.5)[col],(76.5,476.5,876.5)[row]
                transform = lambda s,x=x,y=y: s.translate((x,y,BEAM_TOP))
            for p in panel_templates:
                if not optional_mdf and p.group=='optional_spoilboard': continue
                result.append(named_transform(p,f'PANEL_{row+1}_{col+1}_',transform))
    return result


def bounds_overlap(a,b):
    return all(min(a[k+3],b[k+3])-max(a[k],b[k]) > TOL_DIM for k in range(3))


def parts_bounds(parts):
    bb=[bbox(p.shape) for p in parts]
    return [min(v[k] for v in bb) for k in range(3)] + [max(v[k] for v in bb) for k in range(3,6)]


def validate(parts, name):
    unique = {p.id for p in parts}
    assert len(unique)==len(parts), 'Duplicate part ids'
    records=[]
    for p in parts:
        assert p.shape.isValid(), p.id
        assert len(p.shape.Solids())==1, p.id
        vol=p.shape.Volume()
        assert vol>0,p.id
        assert p.expected_volume is not None,p.id
        assert abs(vol-p.expected_volume) < max(TOL_VOL,p.expected_volume*1e-8),(p.id,vol,p.expected_volume)
        records.append({'id':p.id,'group':p.group,'material':p.material,
                        'geometry_basis':p.geometry_basis,'release_status':'HOLD',
                        'purchased_or_reference_envelope':p.purchased_envelope,
                        'volume_mm3':round(vol,6),'volume_not_material_mass':p.purchased_envelope,
                        'bounds_mm':[round(v,6) for v in bbox(p.shape)],
                        'solid_valid':True,'solid_count':1,'analytic_volume_match':True,
                        'open_items':p.holds})
    intersections=[]
    candidates=0
    for i,a in enumerate(parts):
        ba=records[i]['bounds_mm']
        for j in range(i+1,len(parts)):
            b=parts[j]
            if not bounds_overlap(ba,records[j]['bounds_mm']):continue
            candidates+=1
            volume=a.shape.intersect(b.shape).Volume()
            if volume>TOL_VOL:
                intersections.append({'a':a.id,'b':b.id,'intersection_mm3':round(volume,6)})
    stowed=name=='stowed_with_optional_mdf'
    storage=[]
    if stowed:
        clear=[75,65,150,1080,745,700]
        for rec in records:
            if rec['id'].startswith(('BEAM_','PANEL_')):
                bb=rec['bounds_mm']
                inside=all(bb[k]>=clear[k]-TOL_DIM and bb[k+3]<=clear[k+3]+TOL_DIM for k in range(3))
                assert inside,(rec['id'],'outside clear storage',bb)
                storage.append({'id':rec['id'],'within_clear_storage_box':True})
    return {'configuration':name,'status':STATUS,'parts':records,'part_count':len(parts),
            'assembly_bounds_mm':[round(v,6) for v in parts_bounds(parts)],
            'sum_component_volume_mm3':round(sum(p.shape.Volume() for p in parts),6),
            'broad_phase_candidate_pairs':candidates,'intersections_over_tolerance':intersections,
            'intersection_tolerance_mm3':TOL_VOL,'storage_containment':storage,
            'limitations':['Static solids only; no travel path, lift-out path, full gantry/head, cable or hose simulation.',
                           'Contacts are not verified structural connections; several necessary supports are omitted.',
                           'No stress, fatigue, modal or deflection validation; no physical fit or manufacturing release.']}


def export_configuration(parts,name):
    report=validate(parts,name)
    path=OUT/(name+'_NOT_RELEASED.step')
    assembly=cq.Assembly(name='RevD_STUDY_NOT_RELEASED_'+name)
    for p in parts:
        assembly.add(p.shape,name=p.id,color=cq.Color(*p.color))
    assembly.save(str(path),exportType='STEP',mode='default')
    reread=cq.importers.importStep(str(path)).val()
    assert reread.isValid(),name
    assert len(reread.Solids())==len(parts),(name,len(reread.Solids()),len(parts))
    original_vol=sum(p.shape.Volume() for p in parts)
    assert abs(reread.Volume()-original_vol)<max(.1,original_vol*1e-8),name
    bb=bbox(reread)
    expected=parts_bounds(parts)
    assert all(abs(a-b)<1e-4 for a,b in zip(bb,expected)),(name,bb,expected)
    report['step_roundtrip']={'passed':True,'unit_basis':'mm','solid_count':len(reread.Solids()),
                              'volume_match':True,'bounds_match':True,
                              'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    print(name, 'parts',len(parts),'clashes',len(report['intersections_over_tolerance']),
          'STEP bytes',path.stat().st_size,flush=True)
    return report


def main():
    start=time.monotonic()
    configurations={
        'assembled_bare_extrusion':config(False,False),
        'assembled_with_optional_mdf':config(False,True),
        'stowed_with_optional_mdf':config(True,True),
    }
    reports=[export_configuration(v,k) for k,v in configurations.items()]
    parameters={
        'status':STATUS,'coordinate_system':'mm; X right, Y rear, Z above floor',
        'mainframe_nominal_mm':[1150,1450,1050],
        'tube_section_mm':[TUBE,TUBE,WALL],
        'rail_cap_thickness_mm':CAP_THICK,'sheet_normal_thickness_mm':SHEET,
        'pan_plan_mm':[920,1200],'pan_rim_z_mm':835,
        'pan_floor_bottom_z_mm':{'front':747,'rear':735},'pan_floor_slope':SLOPE,
        'fixed_pan_bearer_top_mm':730,
        'pan_cradle_gap_mm':{'frontmost_bearer_near_edge':16,'rearmost_bearer_near_edge':6},
        'pan_cradle_status':'HOLD: sloping pan does not rest directly on bearers; measured gaps vary across width of each bearer.',
        'panel_count':6,'panel_xy_mm':[500,397],
        'deck_xy_mm':[1003,1197],'deck_x_limits_mm':[73.5,1076.5],
        'deck_y_limits_mm':[76.5,1273.5],
        'beam_y_centers_mm':[75,475,875,1275],
        'beam_bottom_z_mm':870,'beam_top_z_mm':BEAM_TOP,
        'paired_beam_finished_mm':[1044,101.6,50.8],
        'cassette_strip_count':30,'cassette_strip_outer_mm':[100,397,20],
        'strip_end_bearing_each_mm':49.3,'strip_clear_span_mm':298.4,
        'underside_ties_per_panel':2,'underside_tie_blank_mm':[500,25,6],
        'underside_tie_local_y_mm':[75,297],'bare_workplane_z_mm':PROFILE_TOP,
        'optional_mdf_mm':19,'optional_mdf_workplane_z_mm':959.8,
        'stowed_panel_envelope_mm':[397,45,500],
        'stowed_panel_x_origins_mm':[130,623],'stowed_panel_y_origins_mm':[525,580,635],
        'stowed_panel_base_z_mm':150,'stowed_beam_origin_x_mm':111.5,
        'stowed_beam_y_centers_mm':[120,230,340,450],
        'stowed_beam_origin_z_mm':185,'stowed_beam_angle_deg':25,
        'storage_clear_box_minmax_mm':[75,65,150,1080,745,700],
        'profile_source_url':'https://www.amazon.com/dp/B0BXNWK99C',
        'reference_parameters':'../../bed-system/design-parameters.json',
    }
    omissions=[
        {'id':'H01','part_scope':'HMS40 X/Y, ZBX80, gantry and heads','reason':'Not modeled in this bounded study. Supplier mounting drawings, payload/moment ratings, actual head geometry and full travel needed.'},
        {'id':'H02','part_scope':'20100 purchased profiles','reason':'Solid outer envelopes only; supplier cavities/slots, tolerances, alloy evidence and mounting hardware require verification.'},
        {'id':'H03','part_scope':'Panel joining/locating/clamping','reason':'Tie blanks exist, but hole patterns, T-nuts, pin/bushing fits, retained hardware and load paths are unspecified.'},
        {'id':'H04','part_scope':'Primary beam clamps and receiver seats','reason':'Old illustrative clamps interfered with panel corners. Omitted here; positive hold-down/locating interfaces must be designed below the beam top or outside panel footprint.'},
        {'id':'H05','part_scope':'Beam riser feet','reason':'Only clearance reservations modeled; no assertion that these are solid blocks or finished parts.'},
        {'id':'H06','part_scope':'Mainframe diagonal braces and their joints','reason':'30 x 30 x 3 angle requirement remains. Mitered lengths, placement/attachment and connections not sufficiently defined for a released solid.'},
        {'id':'H07','part_scope':'Pan cradles and slat combs','reason':'Missing from original geometry; pan sits 5-17 mm above bearer top depending Y, and slats need independent supports. Must be detailed.'},
        {'id':'H08','part_scope':'Pan manufacturing','reason':'No drain, sump, overflow holes, weld/bend definitions, corner reliefs or sheet flat-pattern release. Floor now has physical 1% slope.'},
        {'id':'H09','part_scope':'Reservoir and water controls','reason':'Outer envelope only. Vented versus pressure-rated architecture, walls, supports, valves, ports, service access and plumbing need selected design.'},
        {'id':'H10','part_scope':'Cabinet and storage rack','reason':'Validated containment is inside a reserved clear box, not actual racks/retainers or collision-free insertion/removal. Handles, clamps, fasteners and covers omitted.'},
        {'id':'H11','part_scope':'Welded tube fabrication','reason':'Nominal square corner hollow tubes; stock radii/tolerances, weld prep, tube venting/sand fill, weld sequence and machined/shimmed rail datums remain.'},
        {'id':'H12','part_scope':'Feet, ground supports and total loads','reason':'Plates and height envelopes shown; actual rated feet/thread blocks, reinforcement and load capacity must be verified.'},
        {'id':'H13','part_scope':'CAM and manufacturing release','reason':'No G-code, toolpaths, sheet DXFs or fabrication authorization produced. Machines, tools, stock, workholding, tolerances and inspection plan unknown.'},
    ]
    manifest={'revision':'Rev D STUDY','status':STATUS,'parameters':parameters,
              'configuration_files':[r['step_roundtrip']['file'] for r in reports],
              'omissions_and_release_holds':omissions,
              'all_modeled_solids_valid':True,'all_step_roundtrips_passed':True,
              'all_modeled_static_part_pairs_clear':not any(r['intersections_over_tolerance'] for r in reports),
              'what_passing_checks_mean':'The represented solids are valid and avoid positive-volume overlaps; this does not prove completeness, stiffness, load capacity, purchased-part accuracy or manufacturing readiness.',
              'runtime_seconds':round(time.monotonic()-start,2)}
    (ROOT/'study-parameters.json').write_text(json.dumps(parameters,indent=2)+'\n',encoding='utf-8')
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (ROOT/'validation.json').write_text(json.dumps(reports,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k in ['status','all_modeled_solids_valid','all_step_roundtrips_passed','all_modeled_static_part_pairs_clear','runtime_seconds']}),flush=True)
    if not manifest['all_modeled_static_part_pairs_clear']:
        print('UNRESOLVED INTERSECTIONS:',json.dumps([r['intersections_over_tolerance'] for r in reports]),flush=True)
        return 2
    return 0


if __name__=='__main__':
    try:
        code=main()
    except Exception:
        import traceback
        traceback.print_exc()
        code=1
    sys.stdout.flush()
    sys.stderr.flush()
    # Known local OCP/VTK shutdown issue; all checks and writes precede this exit.
    os._exit(code)
