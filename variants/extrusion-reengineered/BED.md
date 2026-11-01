# XR2 bed structure â€” conditional analytical screen

The selected cassette is932Ã—257Ã—70.8mm:12.7mm plywood skins around39.05mm core, plus6.35mm removable MDF wear. Seven 9 mm longitudinal webs and eight cross/end webs form the core; five inner longitudinal webs receive conservative global/shear credit. The front pulls end atY14, preserving theY19web. Aluminum tracks and MDF receive no stiffness credit.

At100N and raw plywoodE4000MPa reduced by25%, the cassette calculation includes the actual half-lap bands with reduced core shear area. Adding aligned vertical ledger and header components gives0.233mm against the0.30mm framework/bed target, leaving0.067mm for omitted joints/contact/other components. This is an analytical budget, not a measured assembled pass.

The weakerE2500MPa sensitivity gives0.314mm before those omitted components and therefore misses the target. Actual plywood stiffness in the915mm span direction must be established. Orient the932mm dimension along the declared stronger bending direction: a2Ã—4skin layout fits one2440Ã—1220sheet without rotating the span across that direction.

The top-skin calculation uses a25mm load strip over the45.75mm maximum clear web gap and includes the5mm short, thinner groove segment near one support. Core shear and global bending are separate terms. Glue stresses are demands only; no adhesive allowable or durability is established.

For nominal1.9mm slats screened at1.8mm minimum, the member-only results are0.051mm for150kg distributed among all8slats/two spans and0.179mm for200N at one435mm span midpoint. These do not establish a pan/table load rating: comb contacts, feet/welds, floor, shims and bearer joints require a positive load path and tests.

The four local front-frame notches clear the upright cassette channel. The front ledger joints retain three stations each, including twoX-separated back-row bolts; their local lip/contact and anti-roll behavior remains unqualified.

The cabinet stands on its own four columns and contributes no credited frame ballast. Its relieved front25Ã—3mm strips have about360N pinned ideal buckling load over326mm (about90N forK2). Qualified side-skin restraints at410/500/600/690 shorten the largest segment to100mm, with about3831N ideal pinned buckling load. These ideal results do not qualify skin/rivet restraint, column feet, shelf connections or cabinet load capacity.

The machine remains a wood-carving/plasma development design. This bed screen does not qualify steel milling, tool-changer controls, thermal/water/electrical systems or the complete tool loop; those have separate design and commissioning evidence. See review/bed-screen.json for assumptions, source hashes and acceptance requirements. No pricing is included.


## Bed datums and workholding

Four independent932Ã—257 mm cassettes sit atX109..1041 andY103.4/362.4/621.4/880.4, with2 mm gaps. Their bottom metal seats areZ888 and the finished wear/track datum isZ958.8. Each cassette weighs approximately6.6 kg using the declared density assumptions; measure the real assembly before approving manual handling.

The structural carrier is wider than the reachable machining field. Nominal router tool-centre travel isX175..975 andY121.4..1121.4. The declared inset field isX190..960,Y141.4..1101.4, but it is NOT one uninterrupted MDF rectangle. The actual wear islands are770 mm wide and occupyY141.4..331.9,390.9..590.9,649.9..849.9 and908.9..1101.4. Aluminum track lanes, panel seams, recessed plywood edges and fasteners are separate CAM geometry.

Do not instruct full-carrier surfacing or cut across metal tracks. The maximum cutter radius assumed for the inset reach declaration is15 mm; actual tools and holder sweeps remain unqualified. Toolpaths beside a track must account for the full cutter/holder envelope, track height and real clearance. Screw centres/pockets need explicit CAM depth/keepout treatment.

Each panel has two full-width T-track envelopes, but the purchased die, nut and lip section are unselected. FourM5Ã—60 flathead screws per track load through metal compression tubes into Al backing blocks. The top-skin rebate is6.35 mm deep; no clamp preload is meant to be carried by an unsupported MDF thickness. Actual track clamp forces, lip bending, thread stripping and glue/coating durability are not established by the100 N cutting-force screen.

Round/diamond locators establish repeatableXY registration without two-round-pin overconstraint. Their2 mm projection enters nominal6.04 mm pad bores; the pins have4 mm blind ledger seats. Each dock pad now has two countersunk3Ã—10 wood screws and0.15 mm hard-epoxy bedding in a3.325 mm pocket; metal/epoxy/wood form a continuous compressive seat. Cure on a flat datum jig, then verify coplanarity before adjusting the fourth seat. Fits and positive retention remain to be qualified. Three metal pad contacts establish a plane and the fourth must be adjusted to share load without rocking. Do not infer physical repeatability from the decimal coordinates in CAD.

The clamp centresX117.5/1032.5 give8.5 mm centre-to-free-edge distance and5.2 mm ligament beyond each6.6 mm bore;The lower 12 mm washers seat entirely on the ledgers. Local flange/ligament/thread capacity is still unqualified. Two removableM6Ã—80 sockethead clamp bolts per cassette act through64.45 mm metal sleeves onto the ledgers. Full-seat D-shaped18ODÃ—1.6 steel spreader washers bridge the10.2 mm wood bores; grind1.5 mm from the outboard washer edge toX110/right1040. Socket heads are outside the wear field and may stand1.25 mm above the wear datum; the bare-tool clearance checker includes them. M6Ã—80 retains1.0 mm nominal projection beyond the lower5 mm nut. Eight nuts and washers bear under the ledgers. Real grip, wrench access, preload, sleeve parallelism and the defined screw/bedding process must be commissioned; the modeled compression path replaces the earlier low placeholder draw-latch blocks.

The CAD wear thickness6.35 mm is the FINISHED condition. Prepare pads from thicker raw stock (nominal9.525 mm MDF/qualified equivalent), face separately to the finished thickness, then install and check the958.8 datum. Assemble/final-seat the fasteners only after the facing procedure is defined. Repeatedly skimming6.35 mm pads in place would make the flush Al rails proud and is not a coplanar-bed maintenance method. Replace/re-shim pads to the datum. The1 mm skim value in screw-pocket geometry is only a head-clearance limit; it does not qualify a continuous in-machine facing operation.

## In-footprint conversion

The continuous enclosure proof inreview/transfer-check.json passes 32 segments and the lift-off cover motion with zero raw bed self-intersections. It proves clearance for the current nominal CAD, not hand force, ergonomics, thermal safety or physical joint performance.

Before any cassette moves, isolate power, remove the ENTIRE installed tool module (spindle and split clamp, or plasma drop/head/torch), and retain the common Z axis. Park the common gantry atY1275,headX575 and maximumP.Z_TRAVEL retract. Remove all eight cassette clamp sets and put them in the owned tool storage. Remove the fourM4Ã—8 cover screws, pull the cover forward below the pan, lower it atY0, and park it on its two8-degree slotted blocks belowZ334. Only the common Z adapter remains during conversion; fit the next tool module after conversion is complete.

Remove panels in order1,2,3,4, loading the lowest cabinet shelf first. Every forward slot is empty before the next panel slides across it. For each panel: lift flat fromZ888 to950; move its front edge toY70.8; rotate it upright; lower the upright panel toZ400 in the front channel; rotate it flat; raise it at the front to its shelf level plus1 mm; slide rearward toY360; lower1 mm onto the shelf. Shelf bottoms are400,475.8,551.6 and627.4. Restore in order4,3,2,1 with the same path reversed.

The front frame tip notches clear the70.8 mm upright thickness. The front cabinet return lips are relieved overZ378..704 so the full-width cassette can enter. All moving cassette envelopes remain withinX0..1150,Y0..1450; no external cart or1400 mm extraction lane is used. The lift-off cover uses tapped corner tabs; the hood floor and roof have real screwed ledges/blocks, and its lapped back skin has eight blind rivets. The closed cabinet keeps stored wood below a separate steel heat shield. Do not swap hot/wet beds or leave the cabinet door open during plasma operation.

The top grip openings are24Ã—40 mm atlocalY82..122, preserving internal core webs. The shallow14 mm front finger pockets are for pulling a flat cassette from its shelf; the top end grips carry lifting. Actual users must prove a controlled lift/rotation without pinching or striking the frame. The source contains no powered lift, counterbalance or assumed owned winch.

## Fabrication status

review/bed-fabrication.csv includes wood/rib stock, tracks, metal blocks/tubes, pads, locators, retention hardware, pan/slats/combs, keeper parts, cabinet, plumbing and explicit unselected interfaces. It is not a priced or fabrication-released shopping list. Eight skins fit one12.7 mm sheet with932 along the qualified stiff/grain direction. The core uses separate9 mm plywood. Its seven long and eight cross/end webs have actual9.10 mm opposing half-lap slots19.575 mm deep. Finished wood is exported as19 single-solid components per cassette, including the small end segments formed by the clamp bores. The flat profiles and secondary pocket/edge-bore operations are defined inreview/fabrication and the manufacturing report. Prepare bores in a cheek-plate jig and trial-fit tubes before bonding the top skin. The0.10 mm joint gap is for adhesive and actual-stock fit, not overlapping material.

SeeWATER.md for gravity service, receiver qualification and thermal holds. See the separate ATC design for its mechanism. These bed checks do not release steel milling, large-machine scaling or final machine-specific CAM.


The selected slats are880 mm long atX135..1015 over unchanged435 mm support spans. The central3.6Ã—3 mm key controls lateral position while both ends float toward5.1 mm wall gaps. The3.6Ã—3 mm central key now restricts walk toÂ±0.2125 mm and leaves3.2 mm cold end overhang; ends float for expansion. The manufacturing report quantifies thermal clearance. Differential heating/bowing and actual kerf remain physical trials.


The completed receiver service hatch and rare pan/tote replacement sequence are inWATER.md andbed_service.py. The service check includes fixed shields and the stowed ATC for routine work; rare pan replacement explicitly removes the ATC rail/drive/lock carrier and the independent hood/support assembly. No main HGR guide is removed or left supporting an unrestrained gantry.
