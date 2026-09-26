# Motion scale check — 26 September 2026

The selected X/Y HMS40 listings and manufacturer family information identify ball-screw drives with 10 mm lead. The earlier supplier-request draft incorrectly called them belt modules and has been corrected.

The exact Amazon variation data was rechecked after the owner's lead question:

- [B0C7GQTRRX](https://www.amazon.com/dp/B0C7GQTRRX?th=1): `800mm Stroke`, `10mm Lead`.
- [B0C7GN24S1](https://www.amazon.com/dp/B0C7GN24S1?th=1): `1000mm Stroke`, `10mm Lead`.

Both the selected product title and the ASIN-to-variation map agree. Lead is carriage displacement per screw revolution, not screw diameter. This evidence identifies the selected catalog variants; it does not inspect the owner's order or the delivered hardware. Confirm the supplied Y lead by measuring actual displacement per screw revolution before final configuration, using the supplier's handling procedure.

The current Kraken source already assumes screw drives; no firmware scale change is required from this terminology correction:

| Axis | Motor angle assumed | Microsteps | Screw lead | Calculated pulses/mm | Existing source |
|---|---:|---:|---:|---:|---:|
| X | 1.8 degrees | 16 | 10 mm/rev | 320 | 320 |
| Y1 and Y2 | 1.8 degrees | 16 | 10 mm/rev | 320 | 320 |
| Z | 1.8 degrees | 16 | 5 mm/rev | 640 | 640 |

Calculation: `(360 / step_angle) * microsteps / lead`. These are electrical pulse scales, not accuracy claims. Screw lead, motor angle and direction must match the exact delivered variants. Confirm actual displacement before establishing usable travel limits.

Source inspected: `RevE-ENGINEERING/controls/source-overlay/kraken.ini`. The 500 mA RMS defaults are unchanged commissioning values. The motor phase-current labeling does not automatically define a TMC RMS current setting. The prototype binary has not been flashed or physically tested in this task.

No controller build or pin change was needed for this check. The current port covers Kraken V1.1, not the different V1.0 current-sense hardware. Full electrical stop, brake timing, THC/cutter isolation and hardware commissioning remain separate work.

Product references and pre-order interface details are in the accompanying motion completion report; a listing's stroke option does not determine its mounting geometry.
