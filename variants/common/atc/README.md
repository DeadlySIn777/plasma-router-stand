# RapidChange ATC: sourced selection boundary

Checked 26 September 2026. No purchase, vendor communication or machine firmware change was made.

The provisional choice is a **linear ER11 magazine with IR confirmation and a dust cover**, subject to the user's exact kit link. Its price is not yet a delivered quote. The live [new configurator](https://rapidchangeatc.com/shop-2/?tab=new-setup) lists the following USD goods prices:

| Pockets | Basic | Pro | Premium |
|---|---:|---:|---:|
| 4 | $400 | $550 | $700 |
| 6 | $500 | $650 | $800 |
| 8 | $600 | $750 | $900 |

The [older linear product selector](https://rapidchangeatc.com/shop/automatic-tool-changer/linear-magazines/) instead adds $100 for IR and $200 for IR plus cover to its $400/$500/$600 pocket options. These paths disagree. **$700 is a provisional four-pocket Premium allowance**, not a verified six-pocket Premium purchase. Shipping to Alto GA 30510, tax, toolsetter, collets/nuts, dock fabrication and electrical interfaces are additional/unverified. Do not total the two selectors together.

The new configurator specifies ER11 **17 mm across flats / 19.5 mm maximum nut OD**. Its 52 × 12 × 12 cm listing appears beside shipping weight and is repeated across sizes. That is **not accepted as an engineering envelope**. The small CAD shows that 520 × 120 × 120 mm volume only as a conspicuous allocation scenario; it contains no fictitious pockets or mounting holes. The existing 65 mm spindle body does not prove nut compatibility. Measure its actual nut and identify the VFD before ordering.

The [manufacturer FAQ](https://rapidchangeatc.com/faq/) provides these applicable limits: current magazine width 60 mm; at least 90 mm Z clearance for a non-inset bed installation; reverse rotation and custom M6 capability; programmable speed down to 500 RPM; suggested tightening/loosening 1500/1600 RPM; ER11 cutter OD at most 15 mm. The FAQ warns that misalignment above 0.2 mm destabilizes threading. IR checks the nut sequence, not tightening torque. Current covers use servos; earlier stepper and seven-pin wording also remains on the page, so the delivered electrical interface must govern.

The FAQ directs mounting-model downloads to [the manufacturer's Discord channel](https://discord.com/channels/1077383334080032898/1191144591840268318). The public browser returned a JavaScript application, with no retrievable model files. Searches of the official website and official GitHub organization found no public dimensioned magazine STEP/PDF. Owner-only replacement resources were not accessed. **Exact length, pocket pitch, mounting pattern, nut datum, cover sweep and connector specification remain missing inputs.** Supplier templates must be matched to the ordered current configuration.

The manufacturer's [grblHAL macro repository](https://github.com/greilick-industries/rcatc-scripts-grblhal) was inspected at commit `60c7fd539862184c4f2ba7f435e39cad866fb2fc`. It requires a suitable core, SD support and NGC expressions. Its default coordinate configuration is not machine-ready. It uses reverse rotation, IR checks, probing, tool offsets and cover logic; install no default macro as a tested machine program. This project has only reserved interfaces in [ATC-INTEGRATION.md](../controls/ATC-INTEGRATION.md); no flashed direction output or working M6 is claimed.

## Practical consequence for this project

The small machine has no spare Y travel behind its full working rectangle. An accessible magazine consumes routing space. See [small-machine candidate](../../small-atc/README.md). The larger machine can reserve a dry side lane; neither variant can release an actual magazine mount until its current drawing is supplied.

An ER11 magazine cannot accept the project's 25.4 mm surfacing cutter under the manufacturer's 15 mm limit. That cutter remains a manually installed tool, with an explicit manual-change workflow and tool-length measurement.

After each dock replacement, verify pocket references and spindle alignment. A panel's 0.15 mm return target cannot be reused as proof of ATC compatibility: homing, yaw, thermal movement, spindle tram and pocket calibration all consume the same alignment allowance. The ATC dock targets at most 0.05 mm setup-to-setup lateral movement at its pocket references, **pending a 20-cycle measurement test**, and still requires pocket verification/reprobing. Pins alone do not establish that performance.
