# Rev H bed completion

Rev H keeps six 500 × 397 mm extrusion panels, four 924 mm bed crossbeams,
the ten selected 1220 mm extrusion bars, and the in-machine storage layout.
The additions are actual solids with revised fabrication geometry in
`bed_completion.py`; they are not assertions that the complete machine is ready
for fabrication.

## Completed design changes

- Twelve steel nut strips replace the twenty-four loose spoilboard nuts. Each
  strip remains in its existing extrusion slot, held by two accessible M3
  flat-point screws. The twenty-four spoilboard screws still release for a
  conversion, but no loose nuts need to be retrieved from the slots.
- Eight OD10/ID6.6 compression sleeves pass through the four beams and their
  stacking pads. Four fully threaded M6 × 130 bolts now connect both stored beam tiers to their
  steel shelves. Separate parked-bolt holes remain outside the handling lanes.
  Bolt preload passes through sleeves rather than unsupported tube walls.
- Two steel box clips close around the temporary beam1-on-beam2 stack. Each has
  a removable front gate and a transverse M6 locator into a welded, tapped sleeve
  in beam2. The fixture contains the beam by geometry, rather than depending on
  friction. It is not a lifting device.
- Two bolted panel-rack hoops limit upward escape and fore/aft tipping of the
  six stored panels. Their rods and top bars have separate, deliberate handling
  steps; moving a complete hoop sideways through loaded panels is prohibited.
- A folding steel cap covers the spoilboard rack. A real pivot and removable
  index bolt define its open and closed states. It folds inside the frame, and
  its fixed support remains outside the board transfer lane.
- The unequal left/right stack pads and panel seats have distinct part numbers.
  Beam2 has its own part number because its fixture-sleeve holes differ. The cap
  uses a through-cut C outline; there are no hidden hinge pockets.

## Conversion order

1. Remove stock, clean/dry the bed, park the gantry and isolate the drives. Park
   the spindle and its mounting hardware using the existing tool-storage steps.
2. Release the two upper hoop screws and stage the detached top bars in their
   lid pockets in order **1 then 2**. Then release the lower screws and transfer
   the two bare rods, also **1 then 2**, to their saddles through the separate rod lane. Moving complete hoops is not
   part of the checked sequence. The spoil cap stays pinned open; small removed
   hardware stays in the dry tray.
3. Remove the twenty-four spoilboard screws and store the six boards in the
   existing order **4, 3, 2, 1, 6, 5**. Leave the nut strips and their retaining
   screws installed in the panels. Close and pin the spoil cap.
4. Return the two bare rods **2 then 1** to the empty panel rack and reinstall their lower
   screws. Keep the top bars in their lid pockets.
5. Remove the sixteen panel clamp sets. Store the panels in order **6, 5, 4, 3,
   2, 1**, leaving all four beams and their front seats installed.
6. Move the hoop top bars **2 then 1** by the prescribed under-pan route, lower them over the
   panel ends, and fit their upper screws. Do not move a complete assembled hoop
   across the loaded rack.
7. Release beam1 and park it on its side on beam2. Move the bare box bodies
   **1 then 2** by the transfer route below and insert both from the rear. Then
   fit both gates and their M5 screws, followed by the sleeved M6 locator screws.
   Only after these are in place may the four front-seat mounting screws and
   the two seats be removed.
8. Remove the gates and locator hardware, then return the bare box bodies
   **2 then 1** to the dry tray by reversing their transfer routes before lifting
   beam1. Store the beams in order **1 rear/lower, 2 front/lower, 3 rear/upper,
   4 front/upper**. Fit all four stack-lock bolts through the aligned sleeves and
   shelves, with washers and nuts.
9. Reverse this order for router mode. Map seats, verify coplanarity and re-probe
   after conversion. The removable front seats do not establish automatic
   return-to-zero.

These changes eliminate loose-nut retrieval and add real containment. They do
not make the conversion quick: the original 52 release fasteners remain, and
the restraints add operations. No conversion-time claim is made.

## Check scope and physical release requirements

`check_bed_completion.py` checks both full integrated Rev H assembled states. The integrated
`check_restraint_paths.py` checks the added large-part operations against the
complete Rev H model. Existing panel, board and beam path checkers use the three
phase helpers in `bed_completion.py`, so their obstruction states match the
sequence above. Historical Rev G reports are preserved.

Nominal zero-overlap checks do not establish tolerance allowance, operator
reach, hand clearance, welding capacity, resistance to shock/vibration, or
retention of real threaded hardware. Fit a representative nut-strip joint to
the actual extrusion before making twelve. Verify the rod/saddle fits, hoop
skirt gaps, gate/beam clearances, welded compression sleeves, and controlled
fastener preload on the fabricated machine. The owner aluminum sheets are not
assumed to replace the specified steel restraint parts.

The long stack-lock screws need a verified **fully threaded** variant. An
ordinary partial-thread M6 × 130 socket screw cannot clamp its nut near the head
in the separate parked position. This is a procurement constraint, not an
interchangeable substitute.

The lower hoop screws have 17.4 mm of vertical clearance above the front fork.
Use a suitable low-profile hex tool; real tool and hand access still require a
physical check. Small screw, nut, gate, spacer and hand motions remain outside
the continuous transfer proof; gate insertion has an explicit geometric
clearance argument and the complete capture state is checked for intersections.

## Checked temporary box-body route

With beam1 resting on beam2, both front seats still installed, and both storage
racks restrained, detach each gate and its hardware before moving the bare
C body. Move body 1 before body 2. Starting at its tray datum X145, Y900/1030,
Z436.096, lift to Z620, shift to X200, and move to Y68. Rotate 90 degrees about
X at that datum to stand the body in the front clearance, then lift the datum
to Z1000. Rotate 90 degrees about Z, shift X to 350/780, move Y to 548, lower to
Z863, and insert 120 mm toward the front to Y428. All coordinates are assembly
millimetres and rotations use the right-hand rule. The matching checker
contains every exact transform and treats the other C body as an obstacle.

For removal, first remove both gates and locator hardware, then reverse body 2
followed by body 1. Each inverse route has the same fixed bodies as its forward
route; the already-removed front seats reduce the obstacle set. Remove both
fixtures before lifting beam1. Neither body is a lifting attachment.

## Current verification

- `bed-completion-check.json`: both complete integrated Rev H states, 1448 parts
  each, zero unresolved intersections, unchanged CAD sources.
- `restraint-paths.json`: 18 prescribed paths / 86 continuous segments; panel
  top-bar staging and return, bare-rod staging and return, folding guard sweep,
  and rear C-body insertion. All pass inside the 1150 × 1450 mm footprint.
  The two transient assembled states also have zero unresolved intersections.
- `temporary-fixture-transfer.json`: 2 additional full tray-to-capture paths,
  10 segments per body, both pass within the footprint. Their final insertion
  segments repeat the insertion already checked in the restraint report.
- The carrier decomposition is checked by Boolean symmetric difference with
  its actual welded CAD solid before its constituent angular sweeps are used.
  No moving bridge or tab collision is waived.

The CAD source frozen for these checks is
`bed_completion.py` SHA256
`629bc43a9a7482074b2ce003024d2ff79542c9f8b860b07dbab13a40d8327406`.
Each report records the complete source set it actually evaluated.
