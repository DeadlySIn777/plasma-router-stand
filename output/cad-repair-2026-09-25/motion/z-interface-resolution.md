# ZBX80 interface evidence — 25 September 2026

**The three missing mating fields remain open. A mistaken hole identification is corrected.** No substitute model or photograph-scaled dimension was adopted.

The exact [100 mm ASIN B09MVYGLNQ listing](https://www.amazon.com/dp/B09MVYGLNQ) was accessible during this check. Its gallery still references the saved seller images in the existing source manifest. The relevant original images are:

- [Top drawing](https://m.media-amazon.com/images/I/61WxScULDML._SL1500_.jpg): 90 mm transverse by 50 mm along-travel carriage, smaller Ø5 holes and larger Ø7 bores. **The 70 mm transverse dimension connects the smaller Ø5 hole row.** It does not dimension the larger Ø7 bore pattern. The longitudinal spacing, thread and depth of the small holes are absent.
- [Fixing-hole identification](https://m.media-amazon.com/images/I/71E5oziXi9L._SL1500_.jpg): identifies four small output fixing holes. It does not specify their thread, depth or datum tolerance.
- [Side drawing](https://m.media-amazon.com/images/I/61HH-r4RqQL._SL1500_.jpg): dimensions the carriage body at 35 mm high, base extrusion at20 mm, end blocks at67/78 mm. **It does not dimension the assembled base-mounting-plane to output-face distance.** Adding20+35 omits the intervening guide/block stack.
- [Bottom drawing](https://m.media-amazon.com/images/I/51wBxuUiRML._SL1500_.jpg): supplies profile annotations and identifies movable M5 nuts, without a complete nut/undercut/interface drawing.

The current listing text also identifies M5 nuts for the side and bottom slots. Those nuts are separate from the output fixing holes; the label does not establish the output-hole thread.

## CAD action

The incorrect assertion that the Ø7 bores have70 mm transverse spacing is removed from `motion_details.py`. The two unsupported M6×16 carriage screw solids and their overlap permissions are removed. A trueØ7 plain bore cannot provide an M6 internal thread, and an M6 shank cannot pass a trueØ5 hole. The model now explicitly identifies the missing fastening connection.

The two7×30 adapter slots and their11×30 recesses remain provisional visualization geometry. They are **not** a verified fit to the four supplier fixing holes. The individual adapter export is guarded until the mating drawing is established. MT01 closes only the internal STEP/DXF rotation/depth mismatch; MT05 remains an open physical interface.

## Exact information needed to finish this connection

| Field | Required evidence / measurement |
| --- | --- |
| Base-to-output height | With the module resting on its actual base mounting face, measure perpendicular distance to the flat output mounting face. Record the datum faces, actual value and measurement uncertainty. Do not substitute the35 mm carriage-body height. |
| Four output fixing holes | For every small fixing hole: transverse and along-travel coordinates from specified carriage edges, plain or threaded, bore diameter or thread major diameter and pitch, usable thread/through depth, entry counterbore if any and backside access. Confirm that the four holes are available for the added tool, not occupied guide fasteners. |
| Attachment stack | After the above: select screw count, grade, head/washer, length, usable engagement or nut arrangement and installation access; assess the connection load path. Rebuild the adapter around that verified pattern. |
| Base attachment | Nut type/thread, undercut width/depth, slot centerlines, available insertion route and usable screw engagement. |
| Operating datums | Output location at both stroke limits, allowable overtravel, motor/cable projection and the separate power-off Z restraint. |

## Research boundary

The existing field register, saved top/side/fixing-hole drawings and exact-ASIN current listing were checked. Targeted public searches did not produce a revision-controlled primary drawing closing the missing height, longitudinal output-hole pitch or hole thread/depth. Generic ZBX80/Plus variants and third-party CAD were not substituted for this exact module. No supplier message was sent.

The earlier field register's appended25 September paragraph also misattributes70 mm toØ7 and claims the slots accommodate an unknown pitch. That paragraph is superseded by this evidence; preserve the original record as history. The related torch-barrel assumption is not verified by these Z-slide sources and remains unresolved.
