# Start with the owned-Z300 candidate

The current [integration candidate](variants/owned-z300-assessment/README.md)
uses the already-owned **RATTMMOTOR ZBX80 with 300 mm stroke** on the 4080
wood/plasma frame. The assessed working box is **800 X / 1000 Y / 200 Z mm**;
full 300 mm operation remains unqualified. No gantry raise is proposed.
Two inherited custom-joint defects are corrected in the new proposal parts.
The new 200 mm Z is excluded from this candidate's purchase plan.

- [Owned-Z300 woodworking proposal](variants/owned-z300-assessment/output/proposal-assemblies/Z300_STOCK_WORK200_CUSTOM_JOINT_PROPOSAL_WOOD.step)
- [Owned-Z300 plasma proposal](variants/owned-z300-assessment/output/proposal-assemblies/Z300_STOCK_WORK200_CUSTOM_JOINT_PROPOSAL_PLASMA.step)
- [Proposal assembly checks](variants/owned-z300-assessment/output/proposal-assemblies/candidate-assembly-check.json)
- [Custom-joint repair and machining detail](variants/owned-z300-assessment/RELIEF-DETAIL.md)
- [Current ownership and candidate limits](variants/owned-z300-assessment/candidate-requirements.json)

The entries below are the frozen XR2 200 mm baseline. Its old carrier/link
support must not be substituted for the corrected candidate parts.

- [Frozen XR2 design](variants/extrusion-reengineered/README.md)
- [Frozen XR2 woodworking STEP](variants/extrusion-reengineered/review/XR2_WOOD.step)
- [Frozen XR2 plasma STEP](variants/extrusion-reengineered/review/XR2_PLASMA.step)
- [Earlier XR2 printable review](output/pdf/plasma-router-stand-XR2-review.pdf)
- [Scoped XR2 evidence index](variants/extrusion-reengineered/review/package-check.json)
- [Physical release register](variants/extrusion-reengineered/review/release-register.json)
- [CAM setup and custom-part files](variants/extrusion-reengineered/CAM-SETUP.md)

This is a nominal engineering/CAM-preparation package. Actual vendor interfaces,
retention, assembled stiffness, water flow, thermal behavior and automatic ATC
operation still require the specified evidence. The USD 1,000 delivered cap
has not been verified. No new pricing or shopping was performed in XR2.

Earlier XR1, Rev G/Rev I, 4x8 and other variants are historical or separate
development. Do not mix their drawings, screw leads, firmware, tests or
purchase quantities into XR2. Use the [variant index](variants/README.md)
for historical context.
