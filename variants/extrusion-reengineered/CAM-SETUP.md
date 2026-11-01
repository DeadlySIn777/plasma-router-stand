# XR2 setup and CAM preparation

The assembled CAD uses millimetres, X right, Y rear and Z upward. The nominal
wood setup origin is assembly **X190 / Y141.4 / Z958.8**. Establish this origin
on the assembled, squared machine after docking and clamping the cassettes;
it is not an instruction to enter an unmeasured work offset.

`cam_reference.py` exports the four actual replaceable wear-pad solids and
their top boundary/screw-recess loops in that setup coordinate system. The
770 x 960 mm enclosing field contains tracks and cassette seams. Use the pad
faces, not a single rectangle, when preparing a wear-surface operation.

Import the current WOOD assembly as the fixture, then add actual stock,
hold-downs, track bolts, tool and holder. Offset obstacles by the full cutter
and holder envelope. Check travel and approach/retract clearance with those
items present. The general XYZ clearance report excludes these added items.

Prepare replacement MDF pads to the designed 6.35 mm finished thickness
before fitting them flush with the track datum. Repeatedly skimming below
fixed track tops makes the pads lower than their neighboring tracks. Replace
the pads or explicitly reset the entire support datum instead.

For custom parts, use the matching individual STEP and manufacturing manifest.
Record the stock datum, alloy/temper, material thickness, thread specification
and remaining supplier-interface checks in each setup. The plate-section
reference DXFs do not replace counterbore, countersink, edge-drilling, tap or
bend information. The bed, sheet-metal shields and ATC have separate schedules.

No controller postprocessor, automatic M6 cycle or plasma program is assumed
qualified. A plasma setup needs the actual torch/nozzle projection, isolated
cutter interface, touch-off/breakaway and height-control behavior. An ATC setup
needs the actual magazine, retained tools, spindle/VFD sequence, hard docking
and all state interlocks. Follow the current ATC fit result; a modeled slider
alone does not provide tool-change clearance.

The measurement worksheet and release register list the physical inputs that
remain open. No production G-code has been created from unverified equipment.
