# Small machine: retractable ATC feasibility

**A 200 mm stroke is a plausible parking motion for a new compact tray. It is not a drop-in way to retain the full 800 × 1,000 mm work area through tool changes.** The current tray height intersects a full-size workpiece when deployed. The previous fixed bridge cannot simply stay in place while only the magazine moves.

This study preserves the frozen machine and earlier ATC variant. [study.py](study.py) reads their cached dimensions, checks selected swept envelopes and exports two clearly named allocation STEP files. It does not supply a purchased magazine model, mounting pattern, slide hardware, actuator or fabrication release. [feasibility.json](feasibility.json) records the inputs, source hashes and numerical results.

## What 200 mm can do

| Alternative | Deployed Y | Parked Y after 200 mm | Result |
|---|---:|---:|---|
| Earlier 120 mm deep allocation | 980–1,100 | 1,180–1,300 | Its tall scenario intersects the Z module at full rear travel. |
| Earlier entire bridge | 950–1,190 | 1,150–1,390 | Low spindle still overlaps the shelf. Sufficient rear movement for its tall magazine would exceed the chassis footprint. |
| New 60 mm body scenario | 1,070–1,130 | 1,270–1,330 | Conditional parked corridor; at least 10.4 mm behind the screened low Z-module envelope. |
| New 80 mm deep moving tray | 1,060–1,140 | 1,260–1,340 | Fits the 1,450 mm Y outline; still passes above occupied stock during M6. |

The compact body is **520 mm long only as a study variable**, with unverified heights of 40, 60, 90 and 120 mm. Its assumed middle pocket line at Y1,100 would be within the tool-axis limit of Y1,121.4. Neither pocket positions nor endcaps/cover/cables are verified. The parked screen spans the full nominal X/Y travel and both Z limits for the named cached gantry, Z and tool envelopes. It is not a full-machine collision certificate.

RapidChange reports a current 60 mm magazine body width and 90 mm clearance for a magazine mounted without an inset; exact model files are distributed through its Discord. Those two dimensions do not define a complete product envelope. [Manufacturer FAQ](https://rapidchangeatc.com/faq/)

## Why stock height changes the answer

The finished MDF is Z958.8. The previous tray underside is Z959.8, leaving only 1 mm over bare MDF. A full-size 12, 25 or 50 mm workpiece intersects that tray. The study also applies an allocated 15 mm clamp/fixture height above the stock, including throughout the linear deployment sweep.

Using **5 mm allocated working clearance**, a **6.35 mm tray** and the manufacturer's **90 mm non-inset allowance**, the following is a packaging screen against the current simplified spindle bottom at full retract, Z1,060:

| Stock thickness | Extra apparent retract clearance needed | With fixtures 15 mm above stock | With those fixtures and an added 13 mm guide stack |
|---:|---:|---:|---:|
| 12 mm | 12.15 mm | 27.15 mm | 40.15 mm |
| 25 mm | 25.15 mm | 40.15 mm | 53.15 mm |
| 50 mm | 50.15 mm | 65.15 mm | 78.15 mm |
| 75 mm | 75.15 mm | 90.15 mm | 103.15 mm |

If 25, 50 or 75 mm denotes the **combined stock-and-clamp height**, use 25.15, 50.15 or 75.15 mm respectively in the second column; do not add the clamp height twice.

These are **not final Z-axis sizing values**: the actual nut datum, cutter length, pocket engagement motion, dust shoe, fixture positions and magazine cover remain unknown. The 90 mm allowance is not a measured toolpath. Raising the tray also changes its parked interference with the X/Z assembly and requires another sweep. Tools passing below the magazine can require still more clearance.

## Rail and mechanism

A 200 mm **rail** is shorter than a slide with 200 mm **travel**. As one dimensional example, HIWIN's MGN12H page lists a 45.4 mm long block, 27 mm width and 13 mm overall height. Two blocks at an assumed 80 mm center spacing and 10 mm end allowances occupy 145.4 mm including the end allowances: a 200 mm rail leaves **54.6 mm travel**. A 200 mm stroke requires at least **345.4 mm rail**, before final end-hole/stop details; 350 mm is a sizing example, not a selected qualified assembly. [HIWIN dimensions](https://www.hiwin.de/en/Products/Linear-guideways/Blocks/Miniature-guides/MGN-HIRES-series/MGN12HZ1CM/p/MGN12HZ1CM)

The shared [guide calculation](../guide-stroke-check.json) uses the catalog's **45.8 mm maximum block envelope**, giving **54.2 mm travel on a 200 mm rail** and **345.8 mm minimum rail for 200 mm travel** with the same assumptions. The 350 mm example remains unchanged. [HIWIN catalog, printed page 88](https://www.hiwin.com/wp-content/uploads/HIWIN-Linear-Guideway-Catalog.pdf#page=91)

Both guide supports must remain outside the usable X stock span and the spindle/clamp swept envelope, while clearing the existing Y rails and shoes. This study does not place fictitious supports in that space. The moving tray needs an actual load path to those supports. Guide depth added above the stock worsens the height budget; side-mounted or recessed guides still need full geometry and stiffness checks.

Use a guided tray, positive deployed locating stop, separate clamp, parked/deployed sensors, and a protected cover with chip drainage. The actuator is not selected. The M6 sequence must park/retract the spindle clear of the tray sweep, deploy, confirm position and clamp, run the measured pocket sequence, then retract and confirm parked before cutting resumes. A sensor does not establish mechanical repeatability. See the existing [ATC controls interface](../../common/controls/ATC-INTEGRATION.md); moving-dock sensors and sequencing are additional work.

## Remedies that preserve the requested working area

1. **More measured Z clearance and a tray above the stock/fixtures.** Keep the full cutting rectangle only after checking the loaded tool, complete magazine, tray, fixed guides, clamps and all M6 sweeps. More Z travel alone does not guarantee enough physical clearance.
2. **An outboard service position beyond full-size stock.** Requires additional reachable X or Y service travel and associated frame/axis design. Current Y modules are already ordered; no axis substitution or purchase is authorized by this study.
3. **A reserved clear strip.** This is simpler but reduces usable bed area and does not meet the user's full-bed objective.

Run with a CadQuery Python environment: `python variants/retractable-atc/small-study/study.py`. The STEP files show allocation bodies and nominal stock only; overlapping bodies in the deployed view deliberately demonstrate the failed height condition. No holes or manufacturing interfaces are implied.
