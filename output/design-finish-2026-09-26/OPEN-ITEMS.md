# What still prevents a complete machine release

Rev I supplies substantial corrected geometry and circuit definitions. It is
not a final order list or a fabrication/operation release. These are specific
remaining inputs and engineering tasks, rather than a request to approve the
manual bed architecture again.

| Item | Current work | What closes it |
|---|---|---|
| Ordered Y and planned X/Z modules | Catalog travel/lead identified; model and transfer blank preserved | Actual base-slot/nut fit, carriage patterns, heights, stroke datums, motor/coupling/pilot dimensions. Use the existing arrival worksheet before cutting their mating holes. |
| Actual plasma torch and cutter | Defined floating/breakaway mechanism; replaceable insert remains blank | Measure barrel and straight grip; identify CUT-50 version, start circuit and documented isolated interface. Record nozzle datum, lead/tether and operating limits. An AG-60 listing is not this evidence. |
| Rigidity and bed connections | Actual-section beam/joint/storage screens, proposed 100 N / 0.20 mm target | Actual motion compliance and full tool-to-work test, sound tube/welds, slip and repeat-seating checks. Actual extrusion coupon must establish permissible M5 clamp load. No normal torque-table substitution. |
| Electrical panel and stop/power/brake system | Kraken baseline, water/tool netlist, isolated run/probe/head-presence schematics, restart prevention and selected speed converter | Finish populated-panel mounting/thermal layout and actual power/stop/brake schematic using received VFD, motor/brake and cutter interfaces; manufacture and bench-test interface hardware and harnesses; commission pins, timing, current and EMI. Router Z zero is manual. Circuit simulation is not this completion. |
| Plumbing end connections | Supported drain, main pressure/suction routes, strainer carrier and service paths | Measure purchased ports/valve makeup/strainer width, select exact fitting stacks within the recorded zones, then leak/prime/flow/overflow and blocked-filter tests. |
| Purchased enclosure | Correct nominal case and backplate; modeled gland covers and drilled chassis supports | Received door/hinge/latch/bottom-cutout/standoff geometry, opening access, gland sealing and populated heat rejection. Modified enclosure rating is unclaimed. |
| Material and procurement | Current mechanical schedule and fixed net 2-inch tube list | Actual scrap usable lengths/wall/condition, aluminum quantity/alloy and current delivered quotes. Earlier cost workbooks do not price Rev I. |

The owner reported Y is on the way and X/Z planned for Monday 28 September.
Unpublished mating dimensions cannot be verified from a generic seller
picture before those parts or exact manufacturer drawings are available.
Known custom geometry remains reproducible; guarded interfaces must not be
turned into guessed manufacturing holes to make the package look complete.

References: [arrival measurements](../design-completion-2026-09-26/motion/ARRIVAL-MEASUREMENTS.md),
[motion ordering interfaces](../design-completion-2026-09-26/motion/ORDER-AND-INTERFACES.md),
[scrap tube inputs](../design-completion-2026-09-26/SCRAP-TUBE-GUIDE.md),
[joint requirements](structure/JOINTS.md), [controls](controls/README.md),
[service details](service/README.md), [head details](motion/README.md).

No order, supplier message, hardware flash, live motion, torch start or cutting
operation has been performed. The public repository is a design record; a
successful push does not change any release condition above.
