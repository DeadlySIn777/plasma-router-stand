"""Record dimensions transcribed from exact listing drawings, without pixel scaling."""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
p=ROOT/'module-mounting-field-register.json'
d=json.loads(p.read_text(encoding='utf-8'))
d['status']='HMS40 NOMINAL MATING DIMENSIONS RECOVERED; ZBX80 OUTPUT INTERFACE PARTIAL'
d['source_urls']['hms40_engineering_drawing']='https://m.media-amazon.com/images/S/aplus-media-library-service-media/e029d02f-52aa-453f-bd88-9a2b586ceecb.jpg'
h=d['hms40']
h['drawing_path']='sources/HMS40-dimensioned-drawing-2026-02-10.jpg'
h['drawing_identification']={'title':'HMS40-L□□-S□□-M57-BC','manufacturer':'Sichuan Khmos Technology Co., Ltd.','printed_date':'2026-02-10','variant':'57×56 inline stepper; bracketed dimensions apply to alternate servo flange'}
h['nominal_fields']=[
 {'field':'inline motor overall length','value':'stroke + 201 mm','use':'S+145 bracket plus 56 motor; supersedes rounded marketing S+200'},
 {'field':'800 mm overall length','value_mm':1001},
 {'field':'1000 mm overall length','value_mm':1201},
 {'field':'module body length excluding motor bracket','value':'stroke + 125 mm'},
 {'field':'carriage along travel × transverse','value_mm':[65,48]},
 {'field':'carriage top above base mounting plane','value_mm':65.5},
 {'field':'carriage top output fasteners','value':'4 × M4, depth 10 mm'},
 {'field':'output hole pitch along × transverse','value_mm':[30,30]},
 {'field':'along-travel hole distances from nonmotor carriage face','value_mm':[16,46]},
 {'field':'transverse edge margins','value_mm':[9,9],'use':'derived from 48 width and centered 30 pitch'},
 {'field':'bottom slot nut threads','value':'M4'},
 {'field':'bottom slot centerline separation','value_mm':28},
 {'field':'side slot thread','value':'M3'},
 {'field':'side slot height from bottom','value_mm':19},
 {'field':'side carriage holes','value':'4 × M3 depth 6 mm, bilateral; center 32.5 from nonmotor face, first 15 below top, second 10 lower'},
 {'field':'end cap width / nonmotor height','value_mm':[42,60]},
 {'field':'motor bracket height','value_mm':75},
 {'field':'motor width × length','value_mm':[57,56]},
 {'field':'screw axis above bottom','value_mm':45},
 {'field':'screw diameter / selected lead','value_mm':[16,10]},
 {'field':'800 mm module net mass','value_kg':3.9},
 {'field':'1000 mm module net mass','value_kg':4.6},
 {'field':'printed repeatability','value':'±0.03 mm','use':'supplier claim; not finished-machine accuracy'},
 {'field':'10 mm lead advertised thrust / maximum speed','value':'251 N / 350 mm/s','use':'not a motor torque-speed curve or a warranted DIY feed rate'}
]
h['missing_fields']=[
 'Base slot opening/undercut and actual supplied nut engagement geometry.',
 'Exact motor current, torque-speed curve and wiring connector/cable envelope.',
 'Travel-end output-face datum and available overtravel need unambiguous confirmation before homing limits are released.',
 'Module moment/stiffness qualifications for intended cutting loads; additional guides under engineering review.'
]
h['public_cad_search']='The exact listing A+ detailed engineering drawing was recovered after the earlier main-gallery-only search. It closes carriage-hole thread/depth/pitch, output height, slot centerline and inline-motor geometry gaps. No supplier STEP recovered.'
h['fabrication_release']=False
d['action_before_order']='Complete the Rev E mating/support design from the recovered nominal drawings, resolve remaining Z output interface and actual motor/plasma interfaces, then reconcile BOM, geometry and commissioning requirements. Recovery of a drawing is not validation of the entire machine.'
d['zbx80']['public_cad_search']='Main gallery and all observed A+ source images inspected. None publishes the missing along-travel output-hole pitch, usable tapped depth or assembled output height. An unverified customer-reported 30 mm pitch is deliberately not used as a manufacturing dimension.'
d['drawing_hashes_sha256']={n:hashlib.sha256((ROOT/'sources'/n).read_bytes()).hexdigest() for n in ['HMS40-dimensioned-drawing-2026-02-10.jpg','IXGNIJ-20100-section.jpg','B09MVYGLNQ-gallery-2.jpg','B09MVYGLNQ-gallery-3.jpg','B09MVYGLNQ-gallery-4.jpg']}
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Updated supplier field register and five source image hashes.')
