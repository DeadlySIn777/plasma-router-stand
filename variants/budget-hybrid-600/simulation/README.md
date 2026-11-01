# Static simulation and rigidity audit

This screen covers the compact welded hybrid at 800 × 1,000 mm nominal motion travel. The wet center support and the dry module govern different operating cases. This is a study of the individual chassis members, dry modules and supports. The simulated members do not establish the assembled machine's accuracy, structural rating or ability to machine steel.

## Geometry and analysis basis

- Two continuous 1,450 mm 4040 motion beams sit above 31.75 mm square steel backers. The three welded stations lie at Y100, 725 and 1,330 mm. The columns and crossbearers lie on X30.8, 575 and 1,119.2 mm. Crossbearer top is Z799.5, side columns bear directly under the steel backers, and center posts terminate immediately below the crossbearers. The four side X-braced bays run between Z150 and Z950. The front and back X braces use Z245 and Z830 to clear the pan and dry ledgers. No structural stiffness from MDF, pan or slats is included in the chassis.
- The code solves one-dimensional Euler–Bernoulli stiffness matrices with node displacement and rotation. It retains beam continuity, unrestrained end rotations and the Y overhangs. The longitudinal load sweep uses 151 trial positions plus the bearing stations. Curves are sampled 81 times per segment. Distributed load recovery includes the exact quartic deflection between nodes. Two independent closed-form cases reproduce within 10⁻⁹ mm. Individual solves reject net vertical-force error over 10⁻⁵ N. These checks verify implementation of the stated model.
- The 31.75 mm square tube has assumed rounded outside corners of twice the wall and inside radius of one wall. Steel modulus is 200 GPa and aluminum modulus is 69 GPa. Wall thicknesses of 1.5, 1.9 and 2.1 mm bracket the candidate tube. At 1.9 mm the calculated second moment is 31,590 mm⁴. The selected 4040 section is unverified. Its benchmark second moment is 8.3 cm⁴ with 6–10 cm⁴ sensitivity. A different manufacturer's comparable 4040 publishes 8.3 cm⁴. [4040 benchmark](https://charmaxaluminum.com/profiles/t-slot-4040/)

## Vertical motion-beam comparison

The case applies one downward 100 N load to one Y rail at a time. Posts have vertical restraint, and the estimate excludes post, weld and floor flexibility. The actual transfer of gantry weight and cutting reactions between the two Y guides will depend on tool position and bearing spacing.

| Geometry | Largest rail displacement |
|---|---:|
| Prior 4040 span with stations at Y20 / 725 / 1,430, no backing credit | 0.092 mm |
| Revised stations, no backing credit | 0.064 mm |
| Revised stations, 50% of steel backing bending stiffness participating | 0.041 mm |
| Revised stations, both tubes curve together without composite parallel-axis credit | 0.030 mm |
| Previous row with the middle side station disengaged | 0.322 mm |

The full-participation case needs continuous positive bearing or appropriate connectors. Local lift, slot fastener flexibility, separate curvature, rail-seat eccentricity and yaw can remove that benefit. The worst overhang load produces a 29.4 N incremental upward demand at a station before dead weight. Floor reactions cannot take tension. Verify the actual total dead-load preload before relying on the three-support solution. The old reference represents its bare rail under the same assumptions, rather than every part of the preceding assembly.

## Wet load and leveling

The CAD places the 830 × 1,030 mm pan over two longitudinal 4040 stringers at X370 and X780. The steel slope saddles must bear on those lines. For a 100 kg screen including the pan assembly, water and added steel, the calculation distributes the load along Y55–1,085 on the two rails and transfers the resulting forces into the three crossframes. At a 65% / 35% left-right split, the middle crossbearer receives about 430 N and 232 N at those two seats. Its peak deflection is **0.109 mm with the center foot seated and 2.291 mm with it clear** at 1.9 mm wall. Peak stringer flex with the support elevations held level is 0.108 mm. The two results come from separate component solves. Frame settlement can change the forces and the total displacement.

A separate floor-gap check distributes half of the inherited 1,299 N wet-bed-and-example-sheet load evenly along one crossbearer. With all feet level, its center reaction is 406 N and peak flex is 0.045 mm. A 0.5 mm low floor pad still engages, but the center drops 0.5 mm and its reaction falls to 288 N. With this load pattern it loses all center contact at a gap of 1.725 mm. The older 1,299 N loading is a comparison scenario, not the new machine's measured wet weight. Neither check distributes machine weight equally among nine feet.

## Racking

For a 100 N horizontal force in one 605 mm side bay, one active 25.4 × 3.175 mm tension diagonal at Z150–950 carries 166 N. Pure strap extension accounts for 0.017 mm drift. If the attachments together allow 0.1 mm of axial movement, drift rises to 0.183 mm. At 0.3 mm it reaches 0.514 mm. For welded straps these movement cases represent local deformation or looseness, not a designed clearance. They do not credit compression, prestress, favorable sharing among bays or help from the pan.

Raising the top anchors from Z780 to Z950 cuts the ideal displacement of an isolated side-post segment above a perfectly fixed brace node from 0.089 to 0.0034 mm under 100 N. The end-plane braces stop at Z830 to clear both beds. In that plane the example post tail flex is 0.046 mm, and the diagonal drift is 0.010 mm with rigid attachments or 0.123 mm with 0.1 mm combined axial attachment movement. The node and floor were held still in the post calculation. Lateral sliding and whole-frame rocking remain possible. At 100 N applied at Z1036, the overturning moment transfers roughly 95 N between opposing X support lines or 84 N between opposing Y lines. Pad friction, uneven preload and the lighter dry configuration require direct checks.

## Water pan, slats and heat

The transverse one-way floor strip spans 410 mm between stringer centerlines. The 25.4 mm-wide sloped steel channels have a 3.175 mm top and 3.175 and 1.9 mm edge webs bearing on the 4040. The check includes steel floor self-weight and the maximum local water depth in each scenario. It excludes slat and comb line loads, wall participation, welding distortion, two-way action and accidental torch impingement. It is conditional on the continuous saddles bearing along their intended lengths.

| Floor thickness | 34 mm normal water depth | 43 mm high-water scenario |
|---|---:|---:|
| 12 ga, 2.6568 mm | 0.63 mm | 0.74 mm |
| 14 ga, 1.8974 mm | 1.55 mm | 1.83 mm |

The 0.5% floor slope gives a 5.15 mm drop. The 43 mm pressure case is a high-water sensitivity. The final 80 mm wide overflow crest sits at Z893.6568, 39 mm above the 12-gauge low-end floor top. The CAD gives 26.100 L of water at normal depth and 30.208 L at the overflow crest after displacement by the steel. The Z856.5 drain invert leaves roughly 1.84 mm residual depth at the low point before distortion or debris. Under a 100 N center point load on one on-edge 30 mm slat spanning 400 mm, simple-beam flex is 0.112 mm at 12 gauge and 0.156 mm at 14 gauge. Check actual comb contact, lateral twist and wear as the slats are consumed.

With a 20 °C starting temperature, a uniform 45 / 65 °C steel pan grows 0.31 / 0.56 mm over 1,030 mm. If both materials warm equally, the 1,450 mm aluminum rail's free axial growth exceeds that of the steel backer by 0.42 / 0.75 mm. A 5 K face-to-face linear temperature gradient gives an ideal free-strip bow of roughly 0.47 mm over 410 mm for 12 ga. These are thermal sensitivities. The local torch zone can exceed the scenarios, and restraining thermal growth can trade movement for force. Reserve floating capture travel and check real temperatures and cold/warm/wet datums before service. [Hydro 6063 properties](https://www.hydro.com/Document/Index?id=7823&name=Hydro+EN+AW+6063.PDF)

## Dry module and acceptance

The revised dry carrier uses **three 50.8 mm deep × 25.4 mm wide × 1.5 mm wall** tubes on 95 mm centers. The structural comparison retains the earlier 906.6 mm seat span. To clear the stored gantry brackets, the final CAD narrows the carrier to 892 mm overall with an 866.6 mm seat span. The unchanged 906.6 mm estimate is conservative for crossbar bending under the same point load. The final single-bar flex at 100 N is 0.097 mm. At 100 N in the middle of one bar, computed bar flex falls from **0.606 to 0.111 mm** compared with the initial two-bar 25.4 mm square design. With two bars sharing 100 N it is 0.055 mm per bar. Equal sharing over all three would give 0.037 mm apiece. Actual sharing varies with stock and fixture location. The new MDF top is Z983.5. Verify the new stock-top position, tool lengths and dry Z soft limits before enabling motion.

The 100 N check below applies one physical load at mid-X on each of the four modules in turn. The angle-ledger model includes the flange-only notches over the risers. Each side receives half the vertical load. The two 25 mm deep × 1.90 mm web reinforcements on each ledger span Y116–709 and 741–1,314. Their ideal shear connection raises section inertia in those segments from about 9,042 to 44,889 mm⁴. The tabulated worst positions both fall in module 2.

| Tool position and model | Original angle ledgers with revised crossbars | Web-reinforced angle ledgers with revised crossbars |
|---|---:|---:|
| Over one crossbar, Y397.1 | 0.246 mm | **0.140 mm** (0.111 bar + 0.029 ledger) |
| Between two crossbars, Y444.6 | 0.229 mm | **0.131 mm** (0.055 bar + 0.026 ledger + 0.050 workboard) |

These are work-side displacements under explicit load-sharing assumptions. In the second case a 12 mm MDF strip of assumed effective width 100 mm spans 95 mm at E = 2.5 GPa. For 2.2–3.0 GPa the MDF contribution ranges from 0.056 to 0.041 mm. At the old 190 mm support pitch the same strip flexes eight times as much. A narrower engaged width, board damage, open-angle twist, riser movement, seating/hole compliance or weld distortion can increase displacement. The first case omits any local crushing of the board. About 0.060 mm remains against the inherited 0.20 mm comparison in that case before accounting for the rest of the loop. [MDF technical data](https://www.egger.com/get_download/1850d441-43b8-4bb6-bc27-54822733e626/Technical_datasheet_E1_TSCA_ST_CE_TD-501_English.pdf?country=AZ)

## Parked carrier rack

The final rack stores the shortened 4.79 kg bare steel carriers above the rear crossframe. The nominal center of the four stored carriers is Y1338.1, Z1032.7 mm, excluding hardware and weld mass. A 25.4 × 50.8 × 1.5 mm post rises 120.74 mm from the crossbearer at each end of the rack. The modified shelves project 76.6 mm forward and 94.6 mm rearward from the post faces. A 25 × 1.9 mm web under each projecting arm carries bending into that post.

Across all 15 nonempty combinations of parked carriers, the maximum calculated shelf-end displacement including post rotation is 0.005 mm with balanced sharing and 0.010 mm if all reactions go to a single post. For the latter static case, the maximum nominal shelf-root stress is 8.0 MPa, compared with 36.9 MPa without webs. The rack raises approximately 19.2 kg of bare frames. Verify floor bearing and global center of gravity in both modes, positive keeper engagement and the rear crossframe wall/weld joints. The analysis omits impact, accidental drops and operator loads.

**Structural qualification is open.** Verify actual tube wall and 4040 section, seat and weld load paths, angle-ledger roll, foot retention and individual floor contact, dry panel support and retention, cyclic tool loads and the complete moving gantry/head/tool-to-work loop. Static member analysis cannot establish fatigue life, collision resistance or dynamic stability. During commissioning, record applied dead weight, actual pad bearing, wet and dry datum levels, and mandrel-to-work deflection at the center and edges under incremental 25/50/75/100 N loads in each axis. Compare the full dry loop with the prior 0.20 mm at 100 N target and 0.02 mm residual on unloading. The removable bed must be measured again after a changeover.

[Simulation source](structure.py) · [All results](results.json) · [Candidate geometry](../build_candidate.py)

