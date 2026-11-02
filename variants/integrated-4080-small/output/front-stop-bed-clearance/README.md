# Front stop parking for bed conversion

Both complete front stop assemblies remain unchanged during cutting. Their
original bumper/striker contact and roller/cam relationships are preserved.
During bed movement, each assembly parks400mm rearward on the existing header.
Four small fixed datum blocks establish its operating and parkedYstations.

The manual path is40mm inboard,400mm rearward, then40mm outboard. Remove the
four header screws and washers and disconnect both switch service connectors
before handling the assemblies. Existing operating slot nuts remain in place;
four additional parked-position nuts receive the same screws. Reconnect and
prove bothNCinputs, confirm stop retention and rehome at commissioning speed
before enabling motion. Parking is permitted only with head tooling removed,
common headX975/Y1275/Z250, gantry locked and all six guide screens stored.

The continuous material-enclosure check covers the path with the bed fully
flat and fully upright. The reverse path has identical swept material. Bed
tilting itself uses parked stops; both cutting modes restore their original
operating positions. Exact purchased-profile fit, service connectors, cable
handling, positive motion interlocks and crash-energy capacity remain held.

Guide screen handling has separate endpoint routes. With the flat bed, use
the front corridorY−114.2..−63.1. With the bed positively pinned upright, use
Y25.8..76.9, between the upright bed and panfront. Both return to identical
under-pan rack positions. Restore front stops before restoring the screens,
because the stop transfer crosses the fitted screen plane. Keep the head
removed and common gantry parked throughout these manual operations.

`apply_front_stop_state(parts, state)` takes original operating motion tuples
and adds the fixed datum hardware. State is`operating`or`parked`; it is not a
state setter for already-translated snapshots. `module_at(parts, side, stage,
t)` returns the actual assembly during its three transfer stages, excluding
the explicitly removed header screws and washers. Guide handling uses
`guide_handling_pose(..., upright=False)`for the flat-bed corridor and
`upright=True`for the upright corridor.

The additive takeoff grants no new ownership credit. The datumDXF describes
only the simple20mm square block face; supplier slot/nut engagement and actual
machine commissioning are not established by these drawings.
