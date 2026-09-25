# Rev G bed repair: actual modular geometry and verification limits

This replaces the rejected 87 kg one-piece bed and its 1,400 mm forward excursion. It is a **manual conversion design under review**, not an automatic bed changer and not a released machining-load rating. The user has not yet answered the optional manual-versus-assisted handling question.

The implementation is `../release-review/RevE-ENGINEERING/bed_cassettes.py`. Root integration exports a separate Rev G package; the historical Rev E/F audit and exports remain historical evidence.

## Installed bed

| Item | Nominal geometry and interface |
|---|---|
| Six aluminum panels | Each 500 × 397 mm; five cut-only 20100 sections per panel. X origins 73.5 and 576.5; Y origins 76.5, 483.5 and 890.5. |
| Purchased extrusion quantity | Ten 1,220 mm bars make thirty 397 mm pieces. The 29 mm residual per bar must cover actual saw kerfs and end trimming. |
| Deck | 1,003 × 1,211 mm including the central 3 mm X gap and two 10 mm Y joints. Bare surface Z940.8. Physical deck size is not the guaranteed cutter travel or supported stock rating. |
| Four transverse beams | 924 mm of 50.8 × 50.8 × 3.048 nominal steel tube, X113..1037; center Y65 / 478.5 / 885.5 / 1299. Main section Z870..920.8. |
| Beam supports | A 24 mm foot stack bears on the 6 mm seat at Z840..846. Compression sleeves carry the M8 drawdown force into the seats. A round locator at one end and X-relieved slot at the other avoid two rigid round-pin constraints across the width. |
| Panel ties | Four 250 × 20 × 9.525 mm ties per panel. The two half-width ties overlap the same middle extrusion through separate screws; no strength is assigned to the butt between ties. Twelve M5 screws per panel. |
| Width tolerance | 10 × 5.5 mm tie slots provide ±2.25 mm nominal shank movement. Ø15 washers remain fully on the 20 mm ties. Actual nut clearance and available tolerance must still be measured. |
| Panel retention | Sixteen removable M6 bridge clamps, four per crossbeam, with real tapped backing bosses. The middle beams use the 10 mm gaps for screw access; no invisible fastener passes through unmachined extrusion webs. |
| Spoilboards | Six independently removable pieces, each 393.5 mm wide. Y lengths 343.5, 397 and 219.5 mm. Rough stock 19 mm; modeled finished thickness 18 mm after a nominal 1 mm skim. Finished surface Z958.8. |

The board extents are X180..573.5 and X576.5..970, with Y130..473.5, Y483.5..880.5 and Y890.5..1110. All of these faces lie inside nominal X175..975 and Y121.4..1121.4 tool-center travel. The small notches at board ends clear the inner panel bridge clamps. This makes the stated surfacing operation geometrically reachable; the cutter body, actual cutting length, spindle mounting, feeds and physical tram still need validation.

There is no longer a claim that the machine can surface an unreachable full-width MDF datum underneath the aluminum. The aluminum panels bear directly on crossbeam tops. Those seats and beams must be mapped and shimmed to a measured plane; repeat installation must be checked and the work zero re-probed. The CAD does not turn welded tubing or purchased extrusion into precision surfaces.

### Real clearance changes

The replaceable plasma slats now have a 35 mm long, 22 mm deep relief at each end. Their central 810 mm width, X170..980, remains at Z850 and covers the nominal 800 mm X travel. The end reliefs finish at Z828, below the seats, feet and bolts. Both STEP solids and DXF outlines change together. Comb locations X195 and X955 remain in the full-height region. This is an explicit change in the support geometry; it must not be described as 880 mm of full-height sheet support.

The front seat pair is now removable: each seat uses two M8 screws with washers into OD18 sleeves welded through both ledger walls. Nominal stations are X88 / X1062 and Y45 / Y85. The sleeves finish flush at Z840; their top threads are machined after welding. The seat plates remain real bearing parts. The other six seats remain fixed. The front seats must come out before any beam descends through the front well; otherwise they trap the beams above the ledgers. Clearance mounting screws do not define repeatable precision location, so front-seat elevation must be rechecked after reinstallation.

## Storage entirely inside the stand

| Stored set | Nominal bounds, mm | Installation order |
|---|---|---|
| Six bare panels | X325..825, Y7..240.775, Z175..572 | Fill rear slot first, then work forward. |
| Four beams | X113..1037, Y0..168.8, Z585..698.6 | Beam1 rear/lower, beam2 front/lower, beam3 rear/upper, beam4 front/upper. |
| Six spoilboards | X135..268, Y250..647, Z175..568.5 | Long boards first into the rightmost lanes, then medium boards, then short boards. |
| Small panel hardware | Dedicated narrow rack on the removable cabinet cage | Each clamp assembly has a modeled position; eight beam bolts have an upper guide. |

Each bare panel is about **3.87 kg** from the modeled section, ties and hardware. Each beam is about **5.06 kg** including feet, locators, internal bosses and stacking pads but excluding the removed drawdown bolts. These are geometric estimates, not measured masses or ergonomic ratings. The aluminum profile section is a supplier-drawing reconstruction, not a certified mass section. Rough timber, liquid, stock and machining debris are excluded.

The short left beam shelf ends at X130, preserving a board handling lane beginning at X135. The fixed panel rack guides finish at Z200. Spoilboard handling stays at Z235..628.5 during the lower turn: 5 mm above the front rack arm's Z230 top. Continuous runners support all three board lengths; the short boards do not depend on reaching the rear rack foot.

Fixed rack members remain outside the cabinet door width above its bottom edge. Stored panels and beams intentionally block front access. **Restore the bed to its router position and empty the storage racks before opening the controls cabinet.** No claim is made that electrical servicing can occur with the racks full.

### Ordered spoilboard transfer

The physical boards are numbered by row, then left/right. Store them in order **4, 3, 2, 1, 6, 5**. Boards 3 and 4 are the longest; boards 5 and 6 are the shortest. The orientation during transfer puts the common 393.5 mm dimension vertically, so the progressively shorter horizontal handling width can pass boards already stored on the right. Remove the 24 screws first; the 24 top-slot nuts stay in their installed slots during all board movements. Remove and store those nuts only after the boards have come off, before rotating any aluminum panel. They must not be treated as captive nuts.

After removing their screws, lift one board 40 mm, move it horizontally to the front preparation position, turn it 90 degrees in the horizontal plane, and stand it above the front opening. Move the standing board to Y0..18 and lower it to Z235. Its lower turn uses a moving right-end pivot: X = 135 + L cos(theta), Y = 0, for a -90 degree yaw. The resulting vertical lane occupies X135..153. Shift to its assigned X lane, move rearward 250 mm, then lower 60 mm onto its runner. All previously stored boards remain obstacles in the check.

`check_spoil_transfer.py` performs an adaptive continuous check using exact B-rep minimum distances and a conservative maximum displacement for every point between evaluated poses. It does not equate a few collision-free snapshots with a continuous proof. The JSON records the source hash, per-segment result, exact modeled obstacles and whether the source stayed unchanged during the run. This check excludes fingers, operator reach, loose leads and the paths used to remove fasteners.

### Ordered beam transfer

The panels, boards, their clamps, loose nuts and router tool are stored first. Remove the two drawdown bolts of beam1. Lift that beam 80 mm, move its datum to Y78.8, then rotate it 90 degrees onto its side. Moving the datum before rotation is essential: rotation at the original Y39.6 datum would put the beam outside the front footprint.

Raise its lower face to Z940.8, move it above beam2, then lower it 20 mm onto beam2. The temporary pose is X113..1037 / Y439.1..517.9 / Z920.8..977.6. The nominal steel center of volume is at Y468.10, inside the nominal contact band Y453.1..489.9. This establishes a gravity-resting pose; it does **not** supply lateral restraint against a bump while the operator removes the front seats.

With beam1 independently supported, remove the two front seats and their four screws. Lift beam1 20 mm, return it to the front portal on its side, lower its bottom to Z588, move it rearward 90 mm, then lower 3 mm onto the rear lower shelf. Release beam2, lift it 80 mm, move it to the front, rotate it onto its side, and lower it onto the front lower shelf at Z585. Release beam3 and repeat, stopping at Z644.8 before moving rearward and lowering 3 mm onto the first beam's stacking pads. Beam4 then occupies the front upper position at Z641.8. The return sequence removes the upper pair first.

`verify_revg_beam_path.py` checks these **25 continuous segments**, retaining every previously stored beam as an obstacle. The temporary parking contact, unchanged source hashes and equality of final path geometry to the stored model are recorded in `beam-path-check.json`. The prescribed XY envelope is X113..1037 / Y0..1330.4, entirely within the frame rectangle. Small fasteners and the front seat assemblies change state explicitly between the large-part movements; their hand-transfer paths remain unverified.

### Number of handled items

The modeled conversion involves 24 spoilboard screws, 24 separate top-slot nuts, 16 panel clamp assemblies, eight beam drawdown screws and four front-seat screws with washers. It also moves six spoilboards, six aluminum panels, four beams and two front-seat assemblies. That is **52 screws plus retrieval of 24 loose nuts**. This is a manual, budget-oriented architecture. No quick-change time, automatic handling or tool-free claim is supported by the model.

## Rigidity, fabrication and purchasing limits

For a screening example only, assume an ideal simply supported single beam with E = 200,000 N/mm², the nominal square-corner section, and an 874 mm support-center span. The section has I = 222,159 mm⁴. A 250 N midspan point load gives approximately 0.0783 mm beam deflection and 6.25 MPa nominal bending stress. This excludes seat, foot, weld, ledger, frame, panel, gantry and spindle compliance. It is **not** a machine accuracy rating, a payload rating or an aluminum-cutting qualification. The complete force path must be checked against an actual cutting-force/deflection target before release.

The panel nut still loads the extrusion slot lips under tightening. Direct metal support removes the old MDF creep claim but does not remove the need to test the real extrusion, nut and controlled preload. Do not issue a guessed torque. Loose top-slot nuts are now removed and threaded onto their stored screws; the physical nut-retrieval access is still unverified. Stored boards, panels and stacked beams require positive restraint against accidental movement. The storage guides and gravity-resting pads alone do not establish a restraint rating, and beam1's temporary parking pose has no validated anti-tip or anti-slide device.

Twenty-four tie blanks are required. One 12 × 12 inch piece cannot provide all of them. The user's aluminum quantity and alloy are unknown; this design does not silently credit two usable 3/8-inch sheets. Half-inch stock would require facing if used to reach the selected 9.525 mm tie thickness. The cut list must distinguish owned verified stock, unverified inventory and additional purchases.

Remaining release evidence includes front-seat and small-hardware hand transfer, finger/handling access, temporary-park and storage retention, real vendor interfaces, actual weld and tube corner fit, seat flatness and repeatability, the complete rigidity budget, motor torque/current compatibility and the unmeasured plasma torch/height-control assembly. Continuous large-part geometry checks do not establish those physical requirements.
