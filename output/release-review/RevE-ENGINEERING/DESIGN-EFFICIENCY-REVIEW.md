# Rev F design, efficiency and control review

Reviewed against the current local engineering definition on 24 September 2026; sections 1 and 2 updated 25 September 2026 for the Rev F one-piece hoisted bed, which ADOPTED and superseded this review's changeover recommendations. Items headed **Proposed** are design work to adopt only after their interfaces and checks are completed.

The strongest architecture is a rigid, repeatable machine with a simple guided changeover. Its useful technology is independent gantry squaring, tool probing, isolated plasma height control, monitored water transfer and clear fault diagnosis. More automation is worthwhile only where it removes handling or detects an actual failure.

## 1. Preserve the separate structural load paths and control their datums

**Now modeled (Rev F):** ten full-length T-slot strips bear on a machine-surfaced two-layer MDF sub-bed over a welded ladder whose rails sit continuously on the receiver ledgers. The water pan is not a router support. Independent X and Y guides carry the tool and gantry; HMS40 modules transmit drive force through floating links. Two diagonal dowels locate the module; four M8 drawdowns clamp it. Stationary members receive sand ballast; the module does not.

**Adopted:** the datum problem this section raised is now solved by construction — the machine faces its own sub-bed, so receiver-height machining and shimming are deleted rather than scheduled. Remaining priority: keep joint access and debris exclusion explicit, and use the owner's aluminum only where the required finished section, joint and load path are retained.

**Why it matters:** the conservative member-only screen predicts about 0.148 mm combined vertical deflection under 100 N, or 0.74 mm under 500 N, while deliberately excluding strip continuity over four supports, MDF composite sharing and continuous rail bearing — each of which cuts the real number substantially. It is not evidence of whole-machine machining accuracy in either direction. Sand cannot remedy joint slip or increase the calculated tube section stiffness.

**Acceptance evidence:** measure the assembled loop under stated loads at several bed positions; record module repeatability (dowel re-seat) after repeated clean/remount hoists; indicate bed flatness after the surfacing pass and after the first month of humidity cycles. Do not assign an accuracy claim from the member screen alone.

Sources: [Mechanical definition](MECHANICAL-ENGINEERING.md), [strength screen](strength-screen.json).

## 2. Make the changeover easier to execute correctly — ADOPTED in Rev F

**Adopted geometry:** the changeover this section attacked no longer exists. The bed is one ~86 kg module on the owner's 567 kg (1,250 lb) overhead winch. The changeover is: park and clear the head, drain, hang the 4-leg sling on four welded ears, remove FOUR M8 drawdowns to the internal tray, lift 60 mm, winch forward out the open front window, hoist. The 60 anchors, 16 drawdowns, four staging bars, storage racks and the rear/middle/front sequencing are deleted; the sampled hoist path (three pure translations) replaces the 60-stage manual route.

**Remaining owner scope:** the winch anchorage or trolley track, sling selection, and a weighed, slow first hoist. Rigging is not modeled. Keep the four bolts in the onboard tray, keep the route swept, and recheck the sampled path if any guard, sensor or cable envelope changes.

**Acceptance evidence:** weigh the finished module; verify sling symmetry and hook height; run a timed physical changeover including drain/refill; confirm dowel re-seat repeatability at the bed surface with an indicator. Do not promise a rapid total mode change from the hoist alone — water transfer still dominates the clock (section 3).

Sources: [Swap review](SWAP-REVIEW.md), [mechanical sequence](MECHANICAL-ENGINEERING.md).

## 3. Treat water-transfer time as a measurable design requirement

**Already defined:** gravity drain into a permanently vented 135 L gross tank, a maximum 115 L whole-circuit inventory, a 24 V pump, a normal pan inventory of 79.616 L, separate fill-stop/high-high functions and passive overflow. The drain stays open throughout ROUTER mode. Router-water-ready requires a continuous drained indication plus at least 60 seconds dwell. In PLASMA mode refill follows a timed closing delay and a deliberate FILL action. The selected valve has no position-feedback output.

**Efficiency limit:** the selected pump is 7 L/min open flow; the design estimates about 13–18 minutes to refill the pan through the installed system. Even the published open-flow figure would need about 11.4 minutes for 80 L. Fast bed handling alone will not make this a fast total mode change.

**Proposed priority:** first measure actual fill/drain times and set an explicit total changeover target. Minimize unnecessary hose length and restrictions while preserving accessible filtration, a clarified pickup and the discharge air gap. If a faster pump is selected, size its electrical supply, pressure-rated lines, return paths and overflow together. A five-minute 80 L fill would require about 16 L/min delivered; this exceeds the existing 13.7 L/min circular-overflow screening estimate at 10 mm head. That pump cannot be adopted without rechecking and testing the overflow system.

**Proposed diagnostics:** elapsed fill/drain time, a no-progress alarm and disagreement detection between level signals. These are not implemented in the current relay logic. A supervisory display may observe isolated sensor states; any new shutdown path needs a defined circuit and test. The independent high-high/low-level interruption and passive inventory containment remain effective without a working screen or computer.

**Acceptance evidence:** measured wet calibration, maximum-flow overflow test, full 115 L return test, clogged-filter/no-progress response, power-interruption and held-FILL restart tests. A timed valve command does not prove valve position or a leak-tight seat.

Sources: [Water control](WATER-CONTROL.md), [water electrical definition](WATER-ELECTRICAL-REVIEW.md).

## 4. Use a supervisory interface to make the existing controls understandable

**Already implemented in a compiled prototype:** Kraken V1.1 drives X, Y1, Y2 and Z through its onboard TMC2160 channels. It supports independent dual-Y homing and isolated external Arc OK / UP / DOWN plasma height-control inputs. Motion and water controls are separate. Hardware must remove tool permission independently of Kraken, USB or an operator display. No hardware boot, motor, HF or commissioning test has been completed.

**Proposed interface:** show five distinct conditions: motion homed, selected tool mode, bed configuration confirmed, water ready and tool permission. During setup, show the first unmet condition in plain language. Keep operator confirmations visibly separate from sensor readings. A single combined PG6 permissive currently cannot identify which upstream condition failed; isolated auxiliary diagnostics and their exact input hardware must be added before individual live statuses can be claimed.

**Mode-change issue to resolve:** the present firmware changes plasma hooks through settings and requires a cold controller reset. A future guided mode-change flow should inhibit tool power, verify the controller is idle, apply the correct profile, reset as required and then require homing/probing. It must verify the firmware profile agrees with the physical tool selector before tool enable. This workflow is proposed, not an existing one-touch mode switch.

**Acceptance evidence:** demonstrate reset/power-loss defaults, mis-selected mode inhibition, physical dual-Y homing, probe behavior and loss of every required permissive. The current design has no independent axis-standstill proof. Do not imply that the HMI, a keyed confirmation or the firmware alone provides it.

Sources: [Controller definition](../../../RevE-ENGINEERING/controls/README.md), [water controller boundary](WATER-CONTROL.md).

## 5. Finish the tool interface before claiming a usable machining envelope

**Already modeled:** fresh router spoilboard is Z959.8; plasma slats are Z850. Their 109.8 mm difference exceeds the nominal 100 mm Z stroke. Independent head mounting heights are therefore required. Nominal X800/Y1000/Z100 travel is not the final usable cutting envelope.

**Proposed priority:** define two positively located head mounting positions, a repeatable probe/reference routine and connectors that prevent tool-mode confusion. Resolve ZBX80 mounting/output datums, Z travel stops and power-loss retention before designing the final adapter. Complete the floating/breakaway torch head and its complete cable/torch envelope against the real power source and torch. The present upper float-guard edge is only 3 mm beyond the nominal maximum-X head axis, so axis-center clearance does not prove torch-body clearance.

**Acceptance evidence:** full tool, clamp, cable, dust-shoe and sensor sweeps at the actual Z endpoints; usable area recalculation; retention testing with the suspended head; head-remount/probe repeatability. A ballscrew is not accepted as self-locking merely because it holds position when driven.

Sources: [Package status](PACKAGE-STATUS.md), [motion definition](MOTION-VERIFICATION.md).

## 6. Solve access and contamination before adding exterior styling

**Already modeled:** a horizontal electrical enclosure fits inside the stand, but full lid access requires draining and removing the bed and pan above it. The CAD contains space envelopes rather than a finished thermal and electrical panel layout. Finishing skins are not modeled.

**Proposed priority:** evaluate a dry, front- or side-access enclosure/backplate arrangement that can be serviced without dismantling the wet circuit. The front extraction well, internal racks, tank, foot envelope and cable bend radii are reserved volumes; an alternative cabinet position must fit around them, not silently enlarge the footprint. Separate wet plumbing service from electrical access, and give the strainer, drain union, debris basket and sensors unobstructed cleaning paths.

**Styling direction:** a consistent dark frame, clearly differentiated aluminum datum/handling parts, restrained status lighting and a small number of removable panels. Final panels should expose service fasteners and lift points rather than hiding them. Use vent/air-path design to establish cooling before assigning a smooth sealed appearance. These are proposed finish and enclosure directions, not objects already present in the model.

**Acceptance evidence:** perform removal/replacement access checks using the actual enclosure, VFD, connectors and hose tools; verify heat rejection with the final layout; repeat the bed swap checks after enclosure, covers and cable routing are added. A controller that is difficult to reach will turn minor maintenance into a full mode conversion.

Sources: [Package service tradeoff](PACKAGE-STATUS.md), [current visual brief builder](../../../build_concept_current.py).

## Corrections applied to the visual brief

The visual brief builder was reviewed independently. The current eight-page PDF applies these corrections without a CAD change:

1. State that the drain stays open in ROUTER mode; closing occurs for PLASMA with a timed delay.
2. Do not suggest a valve end switch exists. The selected valve has no position-feedback output.
3. Label timeout, no-progress and contradictory-sensor latching as proposed diagnostics; current relay logic does not implement them.
4. Present water refill and the number of mechanical release operations as current efficiency limits.
5. Separate verified nominal geometry and compiled functionality from proposed handling, diagnostics, enclosure and clamp improvements.

These recommendations preserve the user's footprint, actuator choice, onboard-driver requirement and fabrication role. They do not establish finished CAD/CAM or completed physical validation.
