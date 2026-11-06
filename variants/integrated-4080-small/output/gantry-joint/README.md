# Gantry joint and steel rail-face revision

The existing two 1250 mm 4080 beams and monolithic 150 × 80 mm bottom corner
brackets remain. Those brackets already support both profiles; adding duplicate
lower corner plates would consume material without providing a new load path.

This revision replaces both new 1200 × 40 × 12.7 mm aluminum guide strips with
one continuous 1200 × 112 × 6.35 mm steel face. Eight attached 25 × 25 × 6.35 mm
rear lands preserve the original 12.7 mm datum stack and eight M8 axes. The
13.5 mm counterbores remain 8 mm deep, leaving a 4.7 mm steel bearing web.
Two attached 30 × 20 mm upper lands support the four retained M6 axes. The new
112 mm face restores their full edge seats; the previous short upper strip
left those holes as half circles at its top edge. Ten 12.5 mm access openings
keep the existing horizontal coupler heads accessible, including intentional
half-round edge notches at the two face ends.

Four 32 × 80 × 6.35 mm steel bridges join the beam top faces near both ends.
Together with the existing bottom brackets they provide separated upper and
lower reaction paths against relative beam roll. Midspan top bridges were
rejected because they intersect the owned X-axis module. The retained sleeve
couplers still hold the beam pair together; no composite-section or whole
girder torsional stiffness is assumed merely because the new bridges fit.

The bridges need eight M6×20 screws, eight 1.6 mm washers and eight compatible
T-nuts. Their nominal external grip is 7.95 mm, leaving 12.05 mm inside the
received profile. Verify the actual nut/lip/cavity and complete engagement,
including at least 1 mm clearance beyond the measured screw tip. The nominal
cavity requirement is 13.05 mm; actual measured stack tolerances govern.
STEP shows the external screw grip, with internal supplier interfaces held.

The four bridge blanks and ten rear-land blanks have explicit allocations in
the sidebands of the two already-required **new** pan-hanger blanks. The four
existing stop-datum blanks remain separately allocated. The layout fits the
original 160 × 325.85 mm minimum area and therefore also fits the current
taller hangers. This is material reuse within an existing new purchase, not
owned stock or free machining. The long steel face is an additional raw-stock
purchase that replaces both long aluminum purchases.

The nominal custom-part moving-mass increase is about **4.091 kg**, before the
complete additional fastener/T-nut mass, welds or coating. Y-axis drive and
acceleration acceptance must include it. A price saving is not asserted until
the selected steel stock and delivery are quoted.

Attach the rear lands before final machining; fixture and alternate welds to
control distortion. Inspect front-datum flatness and rear-land coplanarity to
0.05 mm, fitting hard shims or finishing the lands to retain the 12.7 mm stack.
Actual material, thickness, welding process, contact, preload, thread capacity
and loaded slip remain qualification requirements. The actual owned HGR20
rail pattern must be transferred and checked before M5 rail drilling; its
pitch/phase is not invented in the drawings.

`gantry-joint-check.json` binds the source, five STEP readbacks, machining
drawings, offcut nest and relative-motion checks. The DXFs have explicit mm
units and separate machining/reference layers. The offcut-layout parent
outline is a reference window, not an instruction to cut an obsolete hanger.
`GJ_FACE_DRILL_SCHEDULE.csv` records the retained source axes and operations.
The component-only cap screen is not a measured whole-machine stiffness or
operating release. Rebuild with `check_gantry_joint.py` before `mechanical.py`.
