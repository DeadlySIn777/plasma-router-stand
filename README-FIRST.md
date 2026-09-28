# GM1 — Garcia Mechanical Table: two working designs, one-piece line chosen

Two sessions developed the design in parallel on 26 September 2026:

- **The one-piece hoisted bed** is what the owner asked for in this session. On 27 September, after the owner said "finish it", that line was completed as **Rev K**, and then given the owner's RapidChange tool changer and a 300 mm Z as **Rev L**.
- **Rev I** is the other session's six-panel line ([Rev I package](output/release-review/RevI-CAD/README.md), [changes](output/design-finish-2026-09-26/README.md)).

**The owner chose the one-piece line on 27 September.** Rev I stays in the repository as the alternative, and the [README](README.md) compares them.

**Start with the [Rev L CAD package](output/release-review/RevL-CAD/README.md).** It is Rev K with a 300 mm Z and a tool changer that rides on the bed module and lifts out with it. [REVL-PROCUREMENT-DELTA.md](outputs/reve-30510/actual-cost/REVL-PROCUREMENT-DELTA.md) lists what it adds. The owner also asked for a BT30 type: the [BT30 variant](output/release-review/RevL-BT30-CAD/README.md) swaps in a 3.2 kW BT30 ATC spindle and a fork rack on the same dock ([its delta](outputs/reve-30510/actual-cost/REVL-BT30-PROCUREMENT-DELTA.md)).

**Building now?** The owner has the plasma cutter and the torch, and all the drive modules are ordered (27 Sep). The [build order](output/release-review/RevL-CAD/BUILD-ORDER.md) says what can be made before the HGR20 rails and the bed extrusion arrive.

**Then the [Rev K CAD package](output/release-review/RevK-CAD/README.md).** It is Rev J's bed with the other session's Rev I head, plumbing and cabinet folded in, plus the review's fixes:

- plasma reach, with a drop bracket for the owner's PT31-style torch;
- water and coolant;
- the cabinet;
- the float stop.

[REVK-PROCUREMENT-DELTA.md](outputs/reve-30510/actual-cost/REVK-PROCUREMENT-DELTA.md) lists what Rev K adds to the shopping list. The bed module itself, how to hoist it, and what the owner provides (hoist, beam height, sling, stand) are in the [Rev J CAD package](output/release-review/RevJ-CAD/README.md). [REVJ-PROCUREMENT-DELTA.md](outputs/reve-30510/actual-cost/REVJ-PROCUREMENT-DELTA.md) lists what Rev J changed.

Rev J is the owner's 26 September requirement: one waterproof bed module of about 63 kg (galvanized steel, nine 1197 mm T-slot profiles from the same five two-packs, two HDPE top plates, no MDF). Six M10 screws hold it down. For plasma work it lifts 70 mm in place and leaves through the front window on an overhead beam-and-trolley hoist; the hoist path was checked with the sling modeled. Rev J also carries the reservoir hatches, washout closure, refill spout (moved clear of the module) and Z-adapter blank from the base branch's Rev H. That Rev H is the owner's other session's design of 26 September; this one was first published here as "Rev H" and renamed Rev J. The six-panel beds stored in the machine footprint remain documented as alternatives: that Rev H ([package](output/release-review/RevH-CAD/README.md), [completion report](output/design-completion-2026-09-26/README.md)) and Rev G ([package](output/release-review/RevG-CAD/README.md), [repair report](output/cad-repair-2026-09-25/README.md)).

**Not finished or released for fabrication.** Still to close:

- exact purchased interfaces;
- the torch measurement (the torch is now in hand);
- whole-machine rigidity;
- the owner's hoist and rigging;
- water-hardware fits;
- human handling. No current complete build price is asserted. Do not use older drawings, procurement quantities, strength screens or firmware as a manufacturing package.

- [Router assembly](output/release-review/RevK-CAD/step/RevK_ROUTER.step)
- [Plasma assembly, head and torch on the Z](output/release-review/RevK-CAD/step/RevK_PLASMA.step); [bed module alone](output/release-review/RevK-CAD/step/RevK_BED_MODULE.step)
- [Current cut list](output/release-review/RevK-CAD/cutlist.csv)
- [Historical full CAD audit](output/cad-reaudit-2026-09-25/README.md)
- [Unsent supplier dimension request](output/cad-repair-2026-09-25/SUPPLIER-DRAWING-REQUEST.md)
- [Drive modules, receiving check](output/receiving/MOTION-MODULES.md): all ordered (27 Sep), the Z with the 300 mm stroke for the tool changer; [HGR20 guide rails (still to come): receiving check and Y-rail cut planner](output/receiving/HGR20-RAIL-KITS.md)
- [26 Sep follow-up: owner decisions, procurement, open controls findings and what is left to finish](output/followup-2026-09-26/README.md)
- [GM1 controls (27 Sep), for either bed line](output/controls-2026-09-27/README.md). Simulated, not built. They cover:
  - the E-stop and power removal;
  - the mode-race and welded-relay fixes;
  - the BTT Rodent pin plan;
  - the router drain latch, the fill watchdog and the float stop.

The shared source directory remains named RevE-ENGINEERING; Rev K's own sources are in RevK-ENGINEERING, and its generated files are in RevK-CAD; Rev L's are in RevL-ENGINEERING and RevL-CAD. The concept PDF shows Rev I, not Rev K. Fusion has not been verified to load this revision.
