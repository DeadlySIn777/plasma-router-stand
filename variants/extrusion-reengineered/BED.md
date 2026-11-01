# XR1 bed structure — conditional analytical screen

The selected cassette is932×257×70.8mm:12.7mm plywood skins around39.05mm core, plus6.35mm removable MDF wear. Seven9mm webs are modeled; five inner webs receive conservative global/shear credit. The front pulls end atY14, preserving theY19web. Aluminum tracks and MDF receive no stiffness credit.

At100N and raw plywoodE4000MPa reduced by25%, the ideal cassette component sum is0.174mm. Adding aligned vertical ledger and header components gives0.230mm against the0.30mm framework/bed target, leaving0.070mm for omitted joints/contact/other components. This is an analytical budget, not a measured assembled pass.

The weakerE2500MPa sensitivity gives0.311mm before those omitted components and therefore misses the target. Actual plywood stiffness in the915mm span direction must be established. Orient the932mm dimension along the declared stronger bending direction: a2×4skin layout fits one2440×1220sheet without rotating the span across that direction.

The top-skin calculation uses a25mm load strip over the45.75mm maximum clear web gap and includes the5mm short, thinner groove segment near one support. Core shear and global bending are separate terms. Glue stresses are demands only; no adhesive allowable or durability is established.

For nominal1.9mm slats screened at1.8mm minimum, the member-only results are0.051mm for150kg distributed among all8slats/two spans and0.179mm for200N at one435mm span midpoint. These do not establish a pan/table load rating: comb contacts, feet/welds, floor, shims and bearer joints require a positive load path and tests.

The four local front-frame notches clear the upright cassette channel. The front ledger joints retain three stations each, including twoX-separated back-row bolts; their local lip/contact and anti-roll behavior remains unqualified.

The cabinet stands on its own four columns and contributes no credited frame ballast. Its relieved front25×3mm strips have about360N pinned ideal buckling load over326mm (about90N forK2). Qualified side-skin restraints at410/500/600/690 shorten the largest segment to100mm, with about3831N ideal pinned buckling load. These ideal results do not qualify skin/rivet restraint, column feet, shelf connections or cabinet load capacity.

The machine remains a wood-carving/plasma development design. This report provides no steel-milling, ATC, clamp, thermal, water, electrical or complete tool-loop qualification. See review/bed-screen.json for assumptions, source hashes and acceptance requirements. No pricing is included.


## Bed datums and workholding

Four independent932×257 mm cassettes sit atX109..1041 andY103.4/362.4/621.4/880.4, with2 mm gaps. Their bottom metal seats areZ888 and the finished wear/track datum isZ958.8. Each cassette weighs approximately6.6 kg using the declared density assumptions; measure the real assembly before approving manual handling.

The structural carrier is wider than the reachable machining field. Nominal router tool-centre travel isX175..975 andY121.4..1121.4. The declared inset field isX190..960,Y141.4..1101.4, but it is NOT one uninterrupted MDF rectangle. The actual wear islands are770 mm wide and occupyY141.4..331.9,390.9..590.9,649.9..849.9 and908.9..1101.4. Aluminum track lanes, panel seams, recessed plywood edges and fasteners are separate CAM geometry.

Do not instruct full-carrier surfacing or cut across metal tracks. The maximum cutter radius assumed for the inset reach declaration is15 mm; actual tools and holder sweeps remain unqualified. Toolpaths beside a track must account for the full cutter/holder envelope, track height and real clearance. Screw centres/pockets need explicit CAM depth/keepout treatment.

Each panel has two full-width T-track envelopes, but the purchased die, nut and lip section are unselected. FourM5×60 flathead screws per track load through metal compression tubes into Al backing blocks. The top-skin rebate is6.35 mm deep; no clamp preload is meant to be carried by an unsupported MDF thickness. Actual track clamp forces, lip bending, thread stripping and glue/coating durability are not established by the100 N cutting-force screen.

Round/diamond locators establish repeatableXY registration without two-round-pin overconstraint. Their2 mm projection enters nominal6.04 mm pad bores; the pins have4 mm blind ledger seats. Fits and positive retention remain to be qualified. Three metal pad contacts establish a plane and the fourth must be adjusted to share load without rocking. Do not infer physical repeatability from the decimal coordinates in CAD.

The clamp centresX117.5/1032.5 give8.5 mm centre-to-free-edge distance and5.2 mm ligament beyond each6.6 mm bore;12 mm washers now seat entirely on the ledgers. Local flange/ligament/thread capacity is still unqualified. Two removableM6×80 sockethead clamp bolts per cassette act through64.45 mm metal sleeves onto the ledgers. Their heads lie outside the wear field and below the finished top. Eight nuts and washers bear under the ledgers. Real grip, wrench access, preload, sleeve parallelism and pad retention must be confirmed; the modeled compression path replaces the earlier low placeholder draw-latch blocks.

The CAD wear thickness6.35 mm is the FINISHED condition. Prepare pads from thicker raw stock (nominal9.525 mm MDF/qualified equivalent), face separately to the finished thickness, then install and check the958.8 datum. Assemble/final-seat the fasteners only after the facing procedure is defined. Repeatedly skimming6.35 mm pads in place would make the flush Al rails proud and is not a coplanar-bed maintenance method. Replace/re-shim pads to the datum. The1 mm skim value in screw-pocket geometry is only a head-clearance limit; it does not qualify a continuous in-machine facing operation.

## In-footprint conversion

The continuous enclosure proof inreview/transfer-check.json passes32 segments and the door motion with zero raw bed self-intersections. It proves clearance for the current nominal CAD, not hand force, ergonomics, thermal safety or physical joint performance.

Before any cassette moves, isolate power, remove the ENTIRE installed tool module (spindle and split clamp, or plasma drop/head/torch), and retain the common Z axis. Park the common gantry atY1275,headX575,Zlift100. Remove all eight cassette clamp sets and put them in the owned tool storage. Lower and secure the cabinet door. Only the common Z adapter remains during conversion; fit the next tool module after conversion is complete.

Remove panels in order4,3,2,1, loading the highest cabinet shelf first. For each panel: lift flat fromZ888 to970; move its front edge toY70.8; rotate it upright; lower the upright panel toZ400 in the front channel; rotate it flat; raise it at the front to its shelf level plus1 mm; slide rearward toY360; lower1 mm onto the shelf. Shelf bottoms are400,475.8,551.6 and627.4. Restore in order1,2,3,4 with the same path reversed.

The front frame tip notches clear the70.8 mm upright thickness. The front cabinet return lips are relieved overZ378..704 so the full-width cassette can enter. All moving cassette envelopes remain withinX0..1150,Y0..1450; no external cart or1400 mm extraction lane is used. The closed cabinet keeps stored wood below a separate steel heat shield. Do not swap hot/wet beds or leave the cabinet door open during plasma operation.

The shallow14 mm front finger pockets are for pulling a flat cassette from its shelf; the top end grips carry lifting. Actual users must prove a controlled lift/rotation without pinching or striking the frame. The source contains no powered lift, counterbalance or assumed owned winch.

## Fabrication status

review/bed-fabrication.csv includes wood/rib stock, tracks, metal blocks/tubes, pads, locators, retention hardware, pan/slats/combs, keeper parts, cabinet, plumbing and explicit unselected interfaces. It is not a priced or fabrication-released shopping list. Eight skins fit one12.7 mm sheet with932 along the qualified stiff/grain direction. The core uses separate9 mm plywood. Its seven long and eight cross/end webs per cassette need matched half-lap joinery; raw strips cannot simply overlap. Hidden joinery, glue lines and actual toolpaths remain to be detailed.

SeeWATER.md for gravity service, receiver qualification and thermal holds. No ATC, steel milling, large-machine scaling or final CAM is released by these bed checks.


The selected slats are880 mm long atX135..1015 over unchanged435 mm support spans. Neutral end overhang is5 mm and nominal pan-wall clearance is5.1 mm per end. This improves neutral bearing but does not establish lateral retention or thermal-float capacity; worst-case wall shift leaves only partial opposite-end bearing. These remain qualification holds.
