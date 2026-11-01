"""Keep unmeasured physical interfaces visible instead of inventing a release.

Generate a concise measurement worksheet; never infer 'verified' from CAD.
"""
from pathlib import Path
import csv, hashlib, json
import params as P

HERE=Path(__file__).resolve().parent

ROWS=[
 ('Y_MODULE','X/Y motion module model, actual stroke, screw lead, motor variant','model; mm/rev; mm','HMS40 nominal integration; 1000Y/800X travel','Measure one full screw revolution against carriage travel; record real bottom slots, carriage face and endpoint envelopes. Update interface adapters against actual modules.'),
 ('Z_AND_TOOL','Delivered replacement Z geometry, spindle/collet datums and longest retained tool','mm','200mm redesigned Z; nominal spindle reference970..1170 with10mm axial setup rise','Record actual collet/nut and tool-tip datums, permitted clamp gripping region, motor/brake/retention and thread depths. Verify the15..50mm loaded-tool and26.35mm below-magazine-base limits against actual tools; these use different reference planes.'),
 ('GUIDES','Guide rail/block model, fixing positions, straightness and parallelism','model; mm','HGR20 design seats; 0.05mm/1000mm nominal alignment target','Record every physical rail hole and screw stack. Verify seat straightness under final torque and rail parallelism over travel; no invented fixed rail pitch.'),
 ('EXTRUSION','Actual 4080 die, section properties, slot/core geometry, allowable joints','mm2; mm4; N; Nmm','A>=785; Istrong>=529000; Iweak>=134000','Obtain supplier section drawing and permitted slot-nut/bolt preloads. Confirm all used faces, nut fit, core taps and screw bottoming in the selected profile.'),
 ('FASTENERS','Actual grade, thread engagement and tightening for each grip stack','mm; Nmm','Use the frame, bed, motion, shields and ATC schedules together','Check every thin plate seat, washer ligament, slot lip, screw tip and tool access. Nominal threaded CAD bores are not pilot-drill sizes.'),
 ('STOCK','Owned aluminum dimensions/alloy, plywood thickness/grain and glue process','mm; alloy; grade','Two 304.8mm-square Al blanks; 12.7mm skins; qualified span E>=4000MPa','Verify measured stocks and machining allowance. Cut rib joints to measured ply; face/prepare datum surfaces. Deep billets and unlisted plates have no ownership credit.'),
 ('ATC_KIT','Exact magazine, spindle/nut compatibility, retained tools and reverse sequence','model; mm; rpm','See ATC-INTERFACE.md and actual reach report','Verify the actual supplier magazine envelope and pocket/thread interfaces. Confirm spindle/VFD can execute the manufacturer tool-change cycle and the designed clearance applies to actual tools/fixtures.'),
 ('ATC_MECHANISM','Selected lock springs, cylinders, drive, belt, guides and sensors','model; N; mm','See the ATC fabrication schedule and mechanism report','Select real springs meeting the stated rate, free length, compressed length and coil-bind limits. Confirm delivered actuator revision/fittings and drive/coupler/belt fits. Test withdrawal and return forces, positive pin engagement, gate retention, sensor gaps and loss-of-air behavior with the actual loaded rack.'),
 ('PLASMA','Cutter identity/start type, isolated CNC start and torch grip/nozzle','model; mm','User CUT50/VIVARC identification is incomplete','Use the real cutter manual and torch dimensions. Verify isolated start/arc sensing, EMI arrangement, touch-off/breakaway and direct work-return/bonding path. Do not infer start type from pilot arc.'),
 ('RESERVOIR','Red tote measured usable volume and liquid/temperature load suitability','L; degC','65L usable minimum; atmospheric venting','Measure the actual tapered box/lid, approved liquid load and usable fill mark. Confirm removable return plumbing and empty-box service access with real lid/handles.'),
 ('FRAME_LOAD','Framework/bed displacement and permanent joint movement','mm at N','<=0.30mm at100N; permanent structural-joint motion target<=0.05mm','Measure +/-X,+/-Y,+/-Z at representative and extreme head positions. Measure complete spindle-to-work compliance separately. Select any proof load only after checking actual hardware allowables.'),
 ('STABILITY','Dry fixed/moving masses, CGs, all-foot contact and floor friction','kg; mm; N','Rear and side stability per structure-screen.json','Weigh assemblies, calculate actual support reactions in extreme poses, level all eight feet and verify overturning/sliding margins. Floor cabinet and receiver are not attached frame ballast.'),
 ('WATER_TEST','Pan leak, gravity drain, overflow flow and real residual water','L/min; L','Test at intended maximum fill flow','Cold-test with real fittings/hoses and verify independent overflow reaches the vented receiver. Confirm lid air gaps and capacity, then empty/disconnect and trial the entire service path.'),
 ('THERMAL_TEST','Protected wood, aluminum/guide, receiver and hose temperatures','degC','Use limits for the actual selected materials/components','Clean dust/chips, perform representative plasma duty cycles with guards installed, and measure protected surfaces. Qualify wood storage during plasma only after this test.'),
 ('CONVERSION','Cassette mass, grips, human clearance and actual accessories','kg; mm','32 continuous CAD segment enclosures plus actual handling trial','Power isolate, positively retain Z and remove complete tool module and cassette clamps. Trial with final shields, ATC parked, plumbing and actual weights. No outside-footprint parking is allocated.'),
]

def run():
    rows=[dict(id=i,measurement=m,units=u,design_basis=d,verification=v,
               actual_value='',evidence='',status='UNMEASURED') for i,m,u,d,v in ROWS]
    report={'revision':P.REVISION,'physical_release':False,
        'meaning':'A CAD pass never fills this worksheet. Actual measurements and supplier evidence are required before manufacturing unknown mating interfaces and commissioning the machine.',
        'rows':rows,'budget':{'cap_usd':1000,'verified_delivered_total':None,'pricing_paused':True},
        'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),HERE/'params.py')}}
    out=HERE/'review';out.mkdir(exist_ok=True)
    (out/'release-register.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    # Never overwrite a user's completed worksheet while regenerating reports.
    worksheet=HERE/'MEASUREMENTS-BLANK.csv'
    with worksheet.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Physical release remains false; generated',len(rows),'explicit measurement/acceptance entries.')

if __name__=='__main__':run()
