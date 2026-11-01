# XR2 nominal custom machining pack

The custom STEP files contain the actual designed frame and motion solids.
Each part is translated so its world-aligned minimum corner is at 0,0,0;
the index records the original assembly origin. Right and left parts remain
separate. Units are millimetres. Reimport checks are in the review report.

Use the matching frame/motion manifests for material, thread and interface
notes. Nominal thread cylinders are not tap-drill diameters. Preserve the
billet gantry corners and six clevises as integral parts. Do not substitute
touching plates for one-piece bearing angles. Allow facing and saw cleanup
outside the listed finished blank dimensions.

The explicitly labeled MIDSECTION_REFERENCE DXFs are cross-sections for
checking planar plate profiles. They are not complete machining drawings:
counterbores, countersinks, edge holes, taps and bend information live in
the STEP/manifests. Bed, pan, shields and ATC have their own fabrication
files; the custom-part index does not replace those schedules.

This is a nominal engineering pack for CAM preparation. Do not post or
run a toolpath until the delivered hardware interfaces, stock/alloy,
thread depths and physical acceptance items in the release register close.
