# GM1 — Garcia Mechanical Table: two working designs, owner's choice pending

Two sessions developed the design in parallel on 26 September 2026. **Rev J** is the one-piece hoisted bed the owner asked for in this session. **Rev I** is the other session's six-panel line, with a new floating head, plumbing supports and control circuits ([Rev I package](output/release-review/RevI-CAD/README.md), [changes](output/design-finish-2026-09-26/README.md)). Neither contains the other's latest work; the [README](README.md) compares them, and choosing one is the owner's decision.

For Rev J, open the [Rev J CAD package](output/release-review/RevJ-CAD/README.md). It covers the one-piece bed module, how to change beds, what the owner provides (hoist, beam height, sling, stand) and what was checked. [REVJ-PROCUREMENT-DELTA.md](outputs/reve-30510/actual-cost/REVJ-PROCUREMENT-DELTA.md) lists what Rev J changes in the shopping list.

Rev J is the owner's 26 September requirement: one waterproof bed module of about 63 kg (galvanized steel, nine 1197 mm T-slot profiles from the same five two-packs, two HDPE top plates, no MDF). Six M10 screws hold it down. For plasma work it lifts 70 mm in place and leaves through the front window on an overhead beam-and-trolley hoist; the hoist path was checked with the sling modeled. Rev J also carries the reservoir hatches, washout closure, refill spout (moved clear of the module) and Z-adapter blank from the base branch's Rev H. That Rev H is the owner's other session's design of 26 September; this one was first published here as "Rev H" and renamed Rev J. The six-panel beds stored in the machine footprint remain documented as alternatives: that Rev H ([package](output/release-review/RevH-CAD/README.md), [completion report](output/design-completion-2026-09-26/README.md)) and Rev G ([package](output/release-review/RevG-CAD/README.md), [repair report](output/cad-repair-2026-09-25/README.md)).

**Not finished or released for fabrication.** Exact purchased interfaces, plasma tooling, whole-machine rigidity, the owner's hoist and rigging, water hardware and human handling still require closure. No current complete build price is asserted. Do not use older drawings, procurement quantities, strength screens or firmware as a manufacturing package.

- [Router assembly](output/release-review/RevJ-CAD/step/RevJ_ROUTER.step)
- [Plasma layout, bed module out](output/release-review/RevJ-CAD/step/RevJ_PLASMA_LAYOUT.step); [bed module alone](output/release-review/RevJ-CAD/step/RevJ_BED_MODULE.step)
- [Current cut list](output/release-review/RevJ-CAD/cutlist.csv)
- [Historical full CAD audit](output/cad-reaudit-2026-09-25/README.md)
- [Unsent supplier dimension request](output/cad-repair-2026-09-25/SUPPLIER-DRAWING-REQUEST.md)
- [Drive modules, receiving check](output/receiving/MOTION-MODULES.md): Y modules ordered; X and Z to be ordered Monday 28 Sep (please confirm); [HGR20 guide rails (still to order): receiving check and Y-rail cut planner](output/receiving/HGR20-RAIL-KITS.md)
- [26 Sep follow-up: owner decisions, procurement, open controls findings and what is left to finish](output/followup-2026-09-26/README.md)

The source directory remains named RevE-ENGINEERING, but current generated files are in RevJ-CAD. The concept PDF shows Rev I, not Rev J. Fusion has not been verified to load this revision.
