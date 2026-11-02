# Design status — 1 November 2026

**Not finished. Do not order or fabricate from this candidate as a final machine.**
The owned-Z300/working-Z200 study is a checked review proposal. It still differs
from previously supplied owner hardware and bed requirements. These are CAD
integration tasks, not merely commissioning checks.

| Area | Current evidence | Open work |
|---|---|---|
| 4080 frame and owned Z | Nominal owned-family 300 mm body; no gantry raise; assessed X800/Y1000/Z200 | Exact received mounting/output patterns, actual mass and power-off retention; additional 100 mm operating range unqualified |
| Gantry member | Current proposal inherits a separate 1200 mm 8080 beam, explicitly listed in the takeoff | Reconcile with the 4080-only preference; ownership and a qualified replacement arrangement are not established |
| Custom carrier/link | Flange relief and deeper integral support correct the two inherited defects | Material, fastener/joint capacity and physical fit |
| Front Y stops | Matched base/carrier relief, forward screw moved Y90→105; full seats retained; 0.5 mm nominal gap to conservative motor-bracket envelope | Received bracket envelope, stop loads, welds and reduced 35 mm bolt spacing capacity |
| Candidate motion | External-domain and relative-motion proofs pass for the stated nominal candidate | These do not qualify unintegrated owner tooling, flexible services, actual joints or dynamics |
| Candidate changeover/service | Current four-cassette and water-service routes pass within the footprint | Proof does not cover a continuous HDPE/20100 bed or actual working owner head |
| Owned spindle head | Original clamp/boot STEPs recovered unchanged; whole-boot 50 mm movement, Pegelong actuator identity and working-assembly confirmation already recorded | Integrate that existing assembly and its machine attachment, installed home/endpoints, spindle/nut datum and hose support. Substitute split clamp is unselected |
| Router bed | Recovered requirement is ten uncut 1220 mm 20100 profiles over two full nominal 12.7 mm HDPE sheets, circular drilling only | Current routed ply/MDF cassettes do not implement this requirement. Redesign support, retention and in-footprint changeover before selecting bed parts |
| Magazine movement | Previously selected 311 mm overall / 200 mm stroke module drawing exists | Reconcile it with the current custom guide/belt alternative; exact module and RapidChange attachment, pockets, nut sensing and sequence remain open |
| Manufacturing takeoff | Consolidated unpriced candidate schedule, ownership and superseded-part dispositions | Proposal inventory is not a final order list while bed/head/magazine integration remains open |
| Complete price | USD 1,000 delivered constraint retained; owned equipment credited only where evidenced | Complete landed cost has not been established; shopping remains paused |
| Separate 4×8 | Earlier separate study retained | Not completed or released by the small-table work |

Use the [owner head integration note](OWNER-HEAD-INTEGRATION.md) for the recovered
parts and the distinction between an inferred CAD pose and the existing working
assembly. The model/actuator identities and clamp geometry do not need to be
requested again. No clamp cut, boot redesign or replacement actuator is selected.

The active frame preference remains **4080 extrusion for woodworking/carving
and sheet plasma**. Recovering earlier hardware/bed requirements does not
resurrect the older welded steel frame, resin filling or steel-milling claim.

Scoped geometry reports can pass while this machine-level status remains open.
Physical alignment, complete spindle-to-work stiffness, joint/rail capacities,
tool retention, electrical isolation/controls, actual cutter start/THC interface,
water flow, thermal protection and loaded operation also remain unqualified.
No controller settings, operating limits or firmware have been applied.

[Current review-package integrity check](output/current-review-package-check.json)
binds the scoped motion/path/export reports and the consolidated takeoff to
their source and artifact hashes. Its passing result explicitly retains false
machine-completion, fabrication-release and delivered-budget flags.
