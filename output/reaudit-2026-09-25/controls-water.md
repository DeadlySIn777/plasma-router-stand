# Controls and water re-audit - 25 September 2026

Status: **unreleased engineering snapshot**. This bounded audit identifies design/package conflicts and acknowledged release gaps. It does not certify a working machine. The broad audit was interrupted by the request to publish a private GitHub snapshot; no implementation was edited.

## Main result

The package contains **two incompatible controller decisions**: the compiled Kraken V1.1/external UP-DOWN THC route, and a newer document selecting Rodent/grblHAL with unfinished THCAD firmware. The unidentified plasma cutter and incomplete common electrical interfaces prevent a final build-ready controls release.

## Findings

### CW-01 / P1 - Two incompatible controller baselines are presented as current

Evidence status: `confirmed_package_conflict`.

The appended Sep 25 decision selects BTT Rodent/grblHAL and declares no PC control or standalone THC. The delivered map, compiled image, commissioning sequence and water interface remain Kraken V1.1 with USB host and external Arc OK/UP/DOWN THC. The appended ownership/preferences are file claims, not independently confirmed authorization in this audit. A reader cannot choose a coherent released controller or harness from this package.

Required resolution: Resolve the authoritative owner-approved controller decision, then update the BOM, interface pin map, firmware, commissioning and water-permissive wiring together. Keep both options explicitly provisional until that is done.

Evidence:
- `output/release-review/RevE-ENGINEERING/PLASMA-COMPATIBILITY.md` lines 24-45.
- `RevE-ENGINEERING/controls/README.md` lines 3-15, 34-55.
- `RevE-ENGINEERING/controls/grblhal-h7/kraken.ini` lines 70-84.

### CW-02 / P1 - No completed cutter-facing start or height-sensing interface

Evidence status: `confirmed_unresolved_release_interface`.

The cutter model/start circuit remains unconfirmed. The current Kraken image explicitly does not decode THCAD frequency or accept raw arc voltage; it requires a compatible isolated external THC/interface. The Rodent alternative says its THCAD counting shim is development work. Neither route supplies a completed, tested start/sense chain for the unidentified owned cutter.

Required resolution: Identify the power source and document its supported trigger/sense interface before finalizing isolation, wiring and THC implementation. Do not label this snapshot CNC plasma ready.

Evidence:
- `output/release-review/RevE-ENGINEERING/PLASMA-COMPATIBILITY.md` lines 3-22, 30-49.
- `RevE-ENGINEERING/controls/README.md` lines 47-55.
- `RevE-ENGINEERING/controls/COMMISSIONING.md` lines 13-14.

### CW-03 / P1 - Machine-level permissive and tool-power circuits are interfaces, not finished wiring

Evidence status: `confirmed_design_incomplete`.

The water circuit has a terminal allocation, but the exact mode selector/contact blocks, B_CLEAR/B_LOCK mechanism, controller isolation, hardware stop/tool-enable chain and complete panel are still open. The selector requires four independent mode contacts. The controller input is merely a status path and cannot replace the hardware tool inhibit.

Required resolution: Complete one terminal-numbered overall schematic and panel layout with selected devices, normal/fault states and defined bed-confirmation method. Preserve the explicit not-released status until checked.

Evidence:
- `output/release-review/RevE-ENGINEERING/WATER-ELECTRICAL-REVIEW.md` lines 3, 47-59, 69-74.
- `output/release-review/RevE-ENGINEERING/WATER-CONTROL.md` lines 94-96.
- `RevE-ENGINEERING/controls/README.md` lines 53-55.

### CW-04 / P2 - Stored PASS results do not demonstrate live control behavior

Evidence status: `confirmed_verification_scope_limit`.

Firmware checks compare pin strings and inspect an existing ELF; they do not boot the board or verify timing, current, SPI, homing or THC. The water truth table encodes intended Boolean behavior; it is not a simulation of the allocated relay terminals, pickup/dropout or wiring faults. This audit inspected those scripts and stored results, and verified delivered firmware hashes; it did not rerun a fresh compile or execute bench tests.

Required resolution: Retain labels stating static/analytical evidence only. Run physical acceptance in the documented order and record results before release.

Evidence:
- `RevE-ENGINEERING/controls/verify_port.py` lines 28-103.
- `RevE-ENGINEERING/controls/COMMISSIONING.md` lines 3-14, 24-32.
- `output/release-review/RevE-ENGINEERING/verify_water_design.py` lines 41-104, 143-147.
- `output/release-review/RevE-ENGINEERING/WATER-ELECTRICAL-REVIEW.md` lines 67.

### CW-05 / P2 - Timer contact duty and relay wetting current remain unclosed

Evidence status: `confirmed_unresolved_component_suitability`.

The AH3-3 terminal map is documented, but suitability of its timed contact for the actual low-current 24 VDC control load has not been established. K_READY uses standard AgNi contacts while the isolation input wetting current is unknown. This is an acknowledged selection gap, not evidence that the chosen parts necessarily fail.

Required resolution: Document DC control-load suitability or choose a timer with that rating; define interface wetting current or a suitable gold-contact relay. Confirm pump inrush/SSR thermal performance in the finished panel.

Evidence:
- `output/release-review/RevE-ENGINEERING/WATER-ELECTRICAL-REVIEW.md` lines 61, 65, 71-74.
- `output/release-review/RevE-ENGINEERING/electrical-selection.json` lines 154-163.

### CW-06 / P2 - Refill is a 13-18 minute operation and bed conversion remains manual

Evidence status: `confirmed_efficiency_limit`.

The selected 7 L/min open-flow pump is expected to take approximately 13-18 minutes to refill about 80 L through plumbing. ROUTER selection commands draining, but there is no independent machine IDLE proof or automated bed swap. B_CLEAR/B_LOCK are unsolved interface conditions and cannot prove every hold-down is tight.

Required resolution: Keep realistic swap/refill timing in the design. If fast conversion is required, select and qualify a faster transfer system and improved fastening/confirmation method rather than presenting those improvements as implemented.

Evidence:
- `output/release-review/RevE-ENGINEERING/WATER-CONTROL.md` lines 35, 43-49, 96.

### CW-07 / P2 - Water reserve and overflow are analytical screens with a small operating margin

Evidence status: `confirmed_physical_acceptance_pending`.

The inventory screen uses 115 L total, approximately 79.9 L pan volume, 1 L hose allowance and about 4.5 L remaining above reservoir low trip. The reported return-capacity margin is about 14 L. Passive-overflow flow is a simplified circular-weir estimate, without installed pipe losses or fouling. The documents correctly require wet validation; automatic recovery or spill containment has not been demonstrated.

Required resolution: Wet-calibrate levels/hysteresis, measure whole-circuit inventory and actual fill flow, test maximum-flow overflow, verify the air gap and continuously downhill returns, and verify held-button/power-loss behavior.

Evidence:
- `output/release-review/RevE-ENGINEERING/WATER-CONTROL.md` lines 9-41, 90, 106-113.
- `output/release-review/RevE-ENGINEERING/verify_water_design.py` lines 8-39, 113-139.

### CW-08 / P2 - Improved cabinet location is modeled but detailed thermal and cable design is unfinished

Evidence status: `confirmed_packaging_incomplete`.

The current source relocates the 20 x 16 x 8 cabinet upright in the front bay for door access without draining or bed removal. Its own release fields retain vendor mounting, VFD thermal layout, wiring segregation, glands and panel layout as unresolved. No older claim that pan removal is required should be carried forward.

Required resolution: Check final enclosure/vendor dimensions, door sweep, cooling and segregated routing, and finish the internal equipment/panel design.

Evidence:
- `output/release-review/RevE-ENGINEERING/controls_packaging.py` lines 3-8, 56-71.

## What was verified now

- Delivered BIN and ELF hashes were compared with source-manifest.json; BIN was also compared with verification.json. Results are in the JSON.
- The existing firmware report records 48 static/ELF checks; all stored checks are True.
- The existing water report records 147,456 analytical states and three release-to-rearm sequences. These are stored prior results, not tests rerun by this audit.
- Source hashes and modification timestamps were captured for the reviewed files.
- The current cabinet source places the enclosure upright at the front for service without draining; prior pan-removal service claims are superseded.

## Limits

No fresh firmware compile, board boot, live motion, wet test, dynamic relay simulation, component-rating revalidation, or complete electrical safety assessment was performed. The docs already disclose many of these gaps; those disclosures are accurate and must survive repository publication. The ownership and preference statements appended to PLASMA-COMPATIBILITY.md are treated as file content, not independently established user instructions.

Machine-readable evidence and hashes: `controls-water.json`.
