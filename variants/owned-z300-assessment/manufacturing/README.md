# Owned Z300 candidate — unpriced manufacturing requirements

This pack reconciles the existing frame, motion, wood bed, water pan, guards
and retractable ATC into one candidate requirement schedule. It retains every
source takeoff row, its category and its evidence ID. It is complete as a
traceable requirements register; it is **not released for fabrication, CAM
posting, shopping or a delivered-price claim**. Required unmeasured interfaces
are explicit holds, not zero-quantity purchases.

Read `consolidated-schedule.csv` first. Only rows with `additive_requirement=True`
are distinct requirements. Only `include_in_new_procurement=True` rows feed the
unpriced new-material view, `new-procurement-requirements.csv`. That CSV and
`reference-and-excluded-rows.csv` are filtered views, never additional BOMs.
`selected_base=False` means an alternative/provisional item is excluded from
the selected plan. Empty quantity/new quantity means unresolved, not zero.
Quantities count the stated unit: a joint set includes its listed screw,
washer and nut; a material lot is not a guessed retail package. Source
quantities are retained separately, including the old rail-fixing zero marker.

The frame has 19 chassis 4080 cuts, 12,357.4 mm finished total, eight main feet,
and 22 ledger fastener sets. The old duplicate foot station group and frame
ledger allowance are references. Raw wood sheets/lots replace their finished
profile stock requirements. The selected reservoir includes its lid. Shared
pad/rim/pin retention material is counted once. The inherited 1,200 mm 8080
gantry beam is a separate visible requirement and engineering decision; it is
not hidden inside the chassis 4080 count. An all-4080 gantry substitution is
not approved by this pack.

The four routed plywood/MDF cassettes, their raw materials, locator/clamp
hardware and cassette storage cabinet are **proposal-only, unselected**.
The recovered owner basis is ten uncut 1,220 mm 20100 bed profiles over two
full 12.7 mm HDPE layers, with ordinary circular drilling only. Those bed
materials are not proven owned. Their final mounting/support/retention and
purchase quantities remain held; neither competing bed is a final order
list. See the machine-level `../STATUS.md` and `../candidate-requirements.json`.

The ATC source is exactly 344 rows: 63 nonadditive assembly/part references
and 281 additive source requirements. All remain **proposal-only, unselected**
pending reconciliation with the earlier owner-selected 200 mm-stroke,
311 mm-overall ATC module. The original `owned` and `procure` flags remain
in provenance columns; they are not an instruction to order a competing
custom rail/belt architecture. Its 17 assembly decompositions, deep moving
wing billets, split lock-flag sheet pieces and all source STEP/DXF hashes are
retained. A new driver channel is not silently charged when the owner already
reports drives: that row requires an owned-channel capacity check. The ATC
kit and its actual magazine interfaces remain unselected/unverified.

Owned X/Y motion assemblies, extra guide rails/blocks, drives, spindle/VFD,
electronics enclosure, plasma equipment and compressor are excluded from new
procurement on the latest owner statement. Exact supplied contents, channel
counts and interfaces still need inspection. The selected Z is **one owned
RATTMMOTOR ZBX80, 300 mm catalog-travel module with stock motor**. The prior
new 200 mm replacement is removed. Assessed working Z remains 200 mm; full
300 mm operation and controller limits are not qualified. The optional new,
unowned brake motor is excluded pending a compatible qualified retention
choice; the retention function itself remains mandatory and unresolved.

`owned-stock-crosswalk.csv` assigns exactly the existing 83 nested blanks
once to their target requirements. Only those blanks receive conditional
owned material credit. The two 12-inch sheets still require alloy/temper,
flatness, damage, true dimensions and cleanup verification. The Z carrier,
X-link support, main gantry billets, clevises and deep ATC wings gain no new
owned credit. `stock-options-and-gates.json` records alternative profile/sheet
packaging; do not add raw sheet/bar options on top of the listed blank/cut
requirements. Other gauges and unfinished stock packaging remain unpriced.

Use `candidate-custom-part-index.csv` for the 174 frame/motion custom STEP
references. Unchanged parts point to hash-checked frozen XR2 files. The two
repaired Z-joint parts point only to the clearly named candidate STEP copies here:

- `custom-step/Z_CARRIER_RELIEVED_CANDIDATE.step`: finished blank
  260 x270.2 x12.7 mm. Through relief 162.95 x6.55 mm, R3.275 ends; center
  local face X/Z =130/173.475 mm. Thickness is world Y. Preserve the ledge,
  four full M6 head seats and existing guide interfaces. Z300 mount positions
  must be measured and checked against the relief; no OEM hole pattern is invented.
- `custom-step/X_LINK_SUPPORT_D37_CANDIDATE.step`: integral new billet,
  **156 x120.8 x43.35 mm finished envelope**, with a 37 mm downstand.
  Add saw/facing cleanup allowance before choosing raw billet. Do not use
  the old 36.35 mm envelope or attach an extra strip. Four specified 5.0 mm
  pilots are tapped M6x1 through the 8 mm downstand; nominal STEP thread
  cylinders are 6 mm major envelopes, not tap-drill sizes. Lower-row edge
  distance is 9 mm, nominal radial ligament 6 mm. Material/thread tolerance,
  engagement and load proof remain held. Two upper pilots are 3.3 mm,
  tapped M4x0.7 through 6.35 mm.

Four revised front-stop/bracket STEP files also replace their old pointers.
Their base operation-reference DXFs are under `operation-reference/`: old
Y90 mounting holes are absent; the new front mount is Y105 and the rear
stays Y140, at X58.5/1091.5. The bracket base has the specified full-depth
motor-clearance corner relief. Carrier circles are nominal M6 major-envelope
references: specify a suitable nominal 5 mm pilot and M6x1 tap, not a drilled
6 mm clearance hole. Manufacture new corrected parts; no hole-plug welding
instruction is implied. The reduced 35 mm mounting spacing requires capacity
qualification. The two existing M6x12 front screws move +15 mm in Y.

Old XR2 carrier/support and these four front-stop files/notes are superseded for this candidate.
The source snapshot copies are deliberately labeled SOURCE_ONLY and are not
manufacturing authority for the six repaired custom parts. Other MIDSECTION_REFERENCE
DXFs are checking sections, not complete machining drawings. Counterbores,
edge holes, threads, welds, forming and setup belong to the referenced STEP,
source notes and physical acceptance process. Finished bounding blanks do
not include machining cleanup allowance.

The owner supplied an original uncut 65 mm spindle clamp and a complete
powered 50 mm dust boot to preserve unchanged. The current XR2 split-clamp
substitute and its six fasteners are excluded from ordering/manufacture as
the final interface. Their STEP references are explicitly provisional.
Owned clamp/boot identity is recorded in `ownership-decisions.json`. Later
owner records already confirm the clamp revision, whole-boot moving scope,
working assembly and Pegelong B0D6BCQCVR 50 mm actuator. These are answered
requirements. Installed machine attachment/home registration and moving
clearances remain an integration gate. See `../OWNER-HEAD-INTEGRATION.md`.
No new boot actuator is inferred or purchased.

Welded motion-stop assemblies are nonadditive references with separately
listed source-defined constituent blank requirements. Their parent STEP
contains the shaped perimeters/holes; no production child DXF or qualified
weld procedure is implied. The actual rated nonconductive plasma-head
tether, positive Z300 mounting set, power-off retention selection and final
cable/gland/bonding interfaces are also explicit requirements/holds.

The red reservoir is atmospheric, gravity drained and floor supported. Its
real interior usable capacity/rim/lid, water/temperature compatibility and
service access remain physical gates. A CV-15HS vacuum generator is not a
liquid pump. This pack does not authorize pressurizing the consumer tote.

Reproduce with `python variants/owned-z300-assessment/build_manufacturing_pack.py`.
`manufacturing-pack-check.json` records row/ownership/reference checks,
source consistency and output hashes. `artifact-hash-checks.json` verifies
the linked baseline manufacturing artifacts. These tests establish a
reconciled traceable list, not supplier fit, structural qualification,
physical commissioning, price/tax/shipping or compliance with the USD1,000
delivered budget. Baseline geometry and manufacturing files are unchanged.
