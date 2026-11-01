# XR1 engineering audit

The redesign resolves specific architecture defects. Physical supplier
interfaces and assembled-machine performance remain release gates; they are
not hidden behind a successful CAD export.

## Open CAD details before a purchasing or manufacturing release

The digital pass applies to the assemblies and motions that are actually
modeled. It does not close the following unfinished design details:

- Full ledger/guide and receiver heat shields and their attachments. The two
  narrow shadow-strip blanks become five disconnected pieces after relief
  cuts; they are not a complete mounted thermal enclosure.
- A reservoir lid hatch/removal and deep-cleaning path. The selected box fits
  its operating bay, but full upward lid hinging and simple forward withdrawal
  do not fit the current cabinet/pan arrangement.
- Final eggcrate half-lap machining, pan/overflow flat patterns, actual bend
  radii, glue process and delivered-plywood thickness allowances.
- Retractable ATC installation and its tool/slide/Z interference proof. The
  earlier kit study has not been integrated into XR1.

These are design tasks, separately from physical load, flow and thermal tests.
They must not be silently called complete or treated as zero-cost omissions.
The takeoff records unselected shields, water hardware and service interfaces.
Pricing remains paused, and this package is for engineering review.

| Issue | XR1 disposition | Required evidence |
|---|---|---|
| Redundant double-tier frame, short upper posts and long machined steel caps | Replaced with six posts, two headers, three pan bearers and short accessible saddles | Frame geometry, cut schedule and interface checks |
| Rear support too far forward of parked gantry | Two short 4080 base beams add rear feet at Y1410 | Stability sensitivity plus measured mass/CG and foot contact |
| Weak open-ledger torsion | Larger 50.8 × 50.8 × 6.35 aluminum angle with multiple arm fasteners | Ledger bending/twist screen; actual joint and beam tests |
| Thin MDF carrier flex | Glued plywood torsion boxes; MDF is a replaceable wear layer | Bed sensitivity, adhesive/fabrication process and proof test |
| Added dry-bed beams collide with old slat height | Revised complete vertical stack; lower pan and slats | Actual assembly and rigid-axis travel checks |
| Front bed exchange exceeds footprint or hits braces | Front channel, low front crossbraces and under-pan cassette storage | Sampled transfer path and actual handling trial |
| Router load goes through pan sheet | Separate dry ledgers and bearing arms | Continuous modeled load path; bracket/slot qualification |
| Unreachable full-table surfacing | Defined 770 × 960 mm wear field within nominal tool-center limits | Field inset and actual tool/clamp clearance |
| Custom mounts omitted or indiscriminately simplified | Selective billet gantry brackets and clevises; plate Y-link supports, per user preference; explicit manufacturing list | Stock, fastener access, thread/bearing calculations and proof loads |
| Owned aluminum counted more than once | Two explicit 304.8 mm square stock nests with cut gaps | Owned-stock geometry report; actual alloy and size |
| Sand or water assumed to fix frame rigidity | Neither receives elastic-stiffness credit; dry stability is screened independently | Measured dry assembly and actual joints |
| Nominal 4080 size treated as a section property | Published reference minima and weaker-section sensitivity | Actual vendor die, straightness and T-slot allowables |
| Drain/overflow capacity and wood storage | Atmospheric receiver and explicit volume/clearance checks; closed shields | Cold-water flow/leak test and hot-zone temperature trial |
| Unknown cutter/torch represented as operational | No invented nozzle, electrical interface or delivered lead | Delivered equipment measurements and correct interface documentation |

## Acceptance before fabrication release

1. Record the actual X/Y/Z mounting geometry, rail/block dimensions, module
   stroke and screw lead. Update adapter holes and compare the delivered
   hardware to the modeled envelopes. The old cart is not a source of dimensions.
2. Obtain or measure the actual 4080 section and slot geometry. Confirm the
   section-property minimum, nut fit, core tapping, rail seat straightness and
   allowed bolt preload. Decorative CAD grooves cannot establish these.
3. Close the custom-part manufacturing list, plate allocation and every joint
   thread/edge-distance detail. Verify tool access and that screws cannot bottom
   in the shallow extrusion cavities. Do not assume custom mounts arrived with
   the user's owned actuators.
4. Square the frame, fit all bearing seats and level the eight feet. Test
   ±100 N loads at the intended tool/work datum and inspect for permanent joint
   slip. Measure frame/bed and complete tool-loop displacement separately.
   Select any higher proof load using the actual fastener/profile allowables.
5. Check rear/side tipping and floor sliding at the extreme gantry poses using
   measured dry masses and CGs. Do not count pan water as dry-mode ballast.
6. Cold-test the pan, drain and overflow at the actual fill rate. Verify usable
   receiver volume, venting, hose fall, fittings, thermal float and service access.
7. Trial conversion with equivalent cassette weights, unpowered axes and the
   final guards/hoses installed. CAD transfer poses do not prove hand clearance.
8. Verify the actual torch grip/projection, plasma-start interface, interference
   suppression, Z power-loss retention and interlocks. Measure storage/shield
   temperatures during representative plasma use before permitting wood there.

## What the calculations do not certify

Closed-form screens examine individual members, support brackets, load paths,
mass/CG sensitivity and ideal torsion-box behavior. They are not a complete
assembled-frame FEA, weld qualification, contact/friction analysis, modal test
or operational machine certification. Dynamic cutting, actual adhesive quality,
profile lip pullout, thermal distortion, fatigue and flexible services require
their stated physical acceptance tests. The budget cannot be declared met
until the audited takeoff has been repriced with shipping and tax.
