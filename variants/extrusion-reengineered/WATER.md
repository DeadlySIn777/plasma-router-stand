# XR2 water bed and completed service geometry

The nominal design now has a fixed sloping pan, keyed replaceable slats, a removable overflow return and a large positively locked cleaning hatch. Routine receiver cleaning works under the installed heat shield. Rare receiver replacement uses a defined bolted disassembly sequence. Actual received part fit, water containment, thermal performance and handling remain commissioning qualifications; this is a public review revision rather than an operating release.

## Pan and slats

The outside pan is894×1096 mm atX128..1022,Y100..1196. The floor rises fromZ812 to818.576; the rim isZ874. Floor and four walls are separate1.9 mm plain-steel plates with continuous leak-tight welds. Their local-XY millimetre DXFs are inreview/fabrication. No wet-pan bend allowance is hidden: the wet pan uses zero bends.

Eight880×40×1.9 mm slats runX135..1015 with topZ878. Three3.175 mm longitudinal combs give435 mm support spans. The central comb slot floor isZ841,3 mm above the outer comb floors838. A3.6 mm wide×3 mm deep notch at the middle of each slat keys onto that comb. Nominal lateral play is±0.2125 mm, leaving3.2 mm minimum cold overhang beyond either outer comb face. Both ends remain free to expand toward the5.1 mm nominal wall gaps. Lift a cold slat17 mm to clear all comb teeth before removing it.

With the declared expansion assumption12e-6/K and a300 K uniform temperature rise, each440 mm half grows1.584 mm; nominal remaining wall clearance is3.3035 mm including key play. This is a geometric sensitivity case, not an arc-heating or thermal-buckling rating. Differential temperatures, bowing, wear and actual kerf/thickness require cutting trials. The member-only150 kg/200 N analytical cases do not establish a whole-table load rating.

Comb feet follow the pan slope and have drainage cutouts. Specify2 mm fillets20 mm long on both sides atY200,650,1050, keeping drainage open; the combs remain on the pan for service. Qualify thin-sheet penetration, distortion and load transfer with weld coupons and a leak/load test. Nine fitted shim packs transfer pan loads to the three crossbeams. The independent dry-bed ledgers carry no load through the hot pan.

## Drain and removable overflow

The left outlet atY180 has centreZ826.48 and24 mm bore. Its invertZ814.48 leaves a small residual puddle above the lowest floor. The28OD/24ID×26 mm smooth steel stub is a fabrication interface, not anNPT thread. A selected union/adapter must join the valve assembly without forcing incompatible threads. The modeled spanner/hand access region isX50..125,Y185..320,Z790..875.

The full-port manual valve and two elbows lead to anID25/OD34 hose with100 mm centreline-radius bends. The route falls to an air-gapped outlet atX400,Y800,Z410. Its tight24/20 mm fitting bends adjacent to the valve are fitting envelopes, not flexible-hose bends. Actual fitting threads, hose bend radius, unions, retainers and handle must meet the drawn envelopes before purchase. Cold-water complete-drain and tail-flow tests establish performance; no drain-time claim comes from CAD.

The independent40×8 mm right-wall opening starts atZ863,11 mm below the rim. It feeds a welded open collector/gutter/deflector ending atZ410. Two formed1.9 mm tabs attach the return to externalM4 weld studs atY872/928,Z838; the wet wall is not drilled. To remove the cooled return, remove the two nuts/washers/spacers and slide it17 mm right off the studs. The heat shields are removed first for this rare service step.

All collector/gutter pieces have separate flat DXFs and butt-weld details. The two support tabs have53/20 mm outside legs,90-degree bend, insideR2, thickness1.9 and K0.4. Nominal flat length is69.535 mm. Validate the bend coupon for the received sheet and brake. This is the only formed wet-return tab; the pan, spout and return channels otherwise use flat welded plates. Include every blank in a combined stock nest; no free offcut or one-sheet claim is made.

## Receiver and large cleaning hatch

The selected red tote uses a conservative712×470×389 mm external envelope atX219..931,Y700..1170. This includes the larger handle/lid specification in the [Amazon candidate](https://www.amazon.com/dp/B0HN3Q77HR), consistent with the [Husky246842 reference](https://www.homedepot.com/p/311485319). Verify the supplied brand/model: the Amazon brand field was Generic. The external rectangular CAD shell is not the actual tapered interior and must not be used to infer liquid capacity or mass.

Require at least65 litres measured usable capacity with sludge/freeboard allowance, complete-base level support, sustained filled-load/leak testing, and suitable water/temperature compatibility. The20-gallon storage label alone does not prove those properties. Receiver and cabinet stand on the floor and are excluded from main-frame ballast.

The modified lid retains an open25 mm vent atX900/Y1000 outside the hatch and under the receiver shield, a50 mm drain-return aperture and a40×50 mm overflow aperture. Return outlets are19 mm above the modeled lid top391. The receiver remains open to atmosphere; the owned compressor and CV-15HS venturi are not connected.

A600×270 mm opening atX275..875,Y850..1120 gives full-interior handled-brush access. Its620×290×1.9 mm steel cover sits atZ394 and pivots aboutY1130/Z398. The full-open moving cover reachesZ688, giving12 mm to the roof planeZ700. The complete open assembly including lock hardware reachesZ689.32, leaving a more conservative10.68 mm vertical allowance; the current detail-view metadata derives that value from all hatch parts. Two4 mm removable index pins lock the hatch open; their R-clips prevent casual withdrawal. Remove both latch knobs, clips and index pins before swinging, then reinsert both index pins/clips at90 degrees.

Two25×25×3 mm Al cross-angles carry the hatch directly to the tote rim through four25×25 mm metal saddle feet. The vertical webs are coped25 mm at each end. Lid clearance cuts, bolt compression sleeves and rivnuts prevent hatch loads/preload relying on the cut plastic. Nominal feet are2 mm high; fit hard metal shims to the actual received rim height/land while retaining the frameZ391 datum. The25 mm bearing bands accommodate the body-versus-handle width uncertainty, but the actual molded rim must be inspected and load tested. Bond the metal feet to the carrier underside for retention; the bond does not carry the vertical compressive service load.

Routine cleaning requires power off, cooled water/debris and the magazine parked. The receiver stays installed. A450 mm handled brush with60 mm head reaches the modeled floor and corners through the hatch, including the areas under its border. The convex reach calculation and exact corner-tool clearances are inreview/service-check.json. Neither full-lid hinging nor reaching an entire human hand to every floor corner is assumed.

## Rare pan and receiver replacement

The CAD sequence keeps the moving pan/tote within the machine plan until handoff. Carrying the empty tote away after handoff is rare maintenance, distinct from the zero-external-extraction-space cassette swap.

1. Drain/cool the system, remove stock and both complete tool modules, and retain/park the common Z at full retract. Remove slats; leave the welded combs on the pan.
2. Remove the guide HEATSHIELDS and receiver roof, Al dry ledgers and the two front ledger arms. The main HGR guides, blocks and supported gantry remain installed. Remove all bolt-on ATC subassemblies: the empty rail/drive/lock carrier and the independently mounted hood/supports. Isolate air/electrical, retain the parked lock and undo each assembly's separate frame bolts.
3. Disconnect the valve/hose at the wet stub union, release hose clips and coil the hose atR150 under the cabinet. Unbolt/remove the overflow return. Remove the four pan keeper bolts/caps/shoulders.
4. With two people controlling the drained pan/comb assembly, lift70 mm, shift70 mm forward, rotate upright aboutY100/Z882, shift200 mm rearward and lower onto two75×70×20 mm dunnage blocks. The parked pan occupiesY238..301.9 in front of the cabinet.
5. Fit two rated adjustable clamp-head safety props to the pan rim and verify positive restraint before handlers release it. These are required service tools, not assumed owned equipment; no hoist is assumed.
6. Move the EMPTY closed receiver44 mm forward toY656..1126, then lift through the vacated pan bay to820 mm base height for handoff. Reverse the staged sequence for replacement.

The checker uses continuous per-component envelopes and analytic angular extrema, rather than a few poses. It reports pan mass and overhead height separately from handling approval. Verify at least1.92 m free overhead space, measured empty masses, sound handles, adequate two-person reach and rated temporary support/clamp resistance. CAD clearance is not a lifting rating.

## Thermal and physical qualification

The wood cabinet has a closed Al hood and a1.9 mm steel secondary roof. Its lift-off cover is held by fourM4×8 screws in real corner tabs. During bed conversion it parks in two8-degree slotted timber stands belowZ334, fully inside the plan; floor ledges, roof thread blocks and the lapped back skin have modeled fasteners. Separate engineered ledger/guide shields and receiver roof are defined inshields.py. The hatch clears the installed receiver shield; rare replacement removes it by the shield's own checked sequence. Representative cutting must establish protected wood, guide and receiver temperatures. Use35 C as the provisional return/storage commissioning limit until the actual tote, adhesive and coating establish appropriate limits.

Before operating, complete cold leak/drain/overflow tests, measured receiver-volume and long-term liquid-load checks, actual fastener/thread fits, hinge/index retention and hot-debris trials. An overflow opening is not a flow rating; verify capacity exceeds the actual fill rate. Baseline filling/draining is manual and gravity based. No pressure-tank, venturi-transfer or automatic valve operation is implied.

Evidence:review/water-check.json,review/service-check.json,review/bed-manufacturing-check.json,review/transfer-check.json andreview/bed-fabrication.csv. All CAD chores described above have nominal parts and operations; the remaining conditions concern received hardware/materials and physical commissioning.
