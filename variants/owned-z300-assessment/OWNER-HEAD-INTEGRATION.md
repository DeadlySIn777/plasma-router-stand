# Owned clamp and powered boot: integration remains open

The original owner CAD was already supplied. It has now been recovered from
the other local project and copied byte-for-byte into this candidate:

- [Original 65 mm clamp](sources/owned-head/R10%20-%20original%20uncut%2065%20mm%20spindle%20clamp.step)
- [Original dust boot](sources/owned-head/Spindle%20dust%20boot.step)
- [Recovered owner constraints](sources/owned-head/recovered-owner-basis.json)
- [Later working-assembly confirmation](sources/owned-head/owner-working-boot.json)
- [Owner geometry/motion decisions](sources/owned-head/owner-decisions.json)
- [Previously selected actuator](sources/owned-head/owner-actuator-selection.json)
- [Read-only inspection](output/owned-head-inspection.json)

The clamp's source SHA256 is
`506d12b3f749db3eeec03e133b519fd93e45ff1b6cb80bd8fa568d3fb0dba1cb`;
the boot's is
`3716855cf25a308de3db696ae827578d7803bfe4665fd1a6535f311a5246a044`.
Neither supplied solid nor the brush groove has been changed.

The current full proposal still contains the provisional manufactured split
clamp inherited from XR2. It does **not** represent this owned head. Those
substitute clamp parts and their dedicated hardware are not selected for
purchase or machining. The previous nominal head clearance results do not
qualify the unintegrated owner clamp, boot, actuator or hose.

The later October 2 records confirm the **entire boot moves**, the machined
clamp matches the supplied original-uncut STEP, and the existing assembly
already works. The owner selected the **Pegelong B0D6BCQCVR, 50 mm actuator**.
These facts supersede the older record's unknown identity, moving-body and
clamp-revision fields. No new actuator or clamp modification is selected.

The old
coaxial illustrative mate is clear at its reference pose but is not a working
joint definition. A fresh exact-solid diagnostic reproduces overlap at boot
offsets −30, −40 and −50 mm: respectively 30.619, 102.000 and 9.795 mm³.
These are six sampled positions of an inferred pose; they establish that this
pose cannot simply be adopted. They do not prove the actual parts are unusable.

Finishing the machine attachment requires registering that existing working
assembly and its actuator/home/end positions in the new machine coordinates,
with the actual spindle/nut datum and independent hose support. Do not ask for
the known actuator identity or invent a different moving subassembly. The
source geometry remains authoritative; the inferred diagnostic is not evidence
that the owner's working assembly fails. The removable adapter and affected
tool/ATC/bed/service paths must be checked after this integration is complete.

Reproduce the read-only diagnostic with `inspect_owned_head.py`. Its successful
exit means the inspection and source preservation completed, not that the
head fits. The report retains `OWNER_HEAD_INTEGRATION_OPEN` and false release
flags.
