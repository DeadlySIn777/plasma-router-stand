# 4×8 retractable magazine — conditional packaging study

A **true 200 mm cross-slide stroke can fit in the existing dry side strip without reducing the 1219.2 × 2438.4 mm sheet area**, provided the entire moving magazine/carrier/tool envelope is no wider than the 160 mm allocation below. The original 200 mm-wide allocation plus a 200 mm stroke does not fit the 387.5 mm corridor between deck edge X1450 and the right Y-carriage allocation at X1837.5, before clearances. Retraction protects and parks the magazine; this larger layout already preserved the full sheet with its fixed side bay.

| Item | Conditional allocation |
|---|---|
| Moving magazine, carrier and stored-tool envelope | 160 × 600 × 140 mm; no purchased-part geometry claimed |
| Change pose | X1465–1625 / Y400–1000 / Z800–940 |
| Park pose | X1665–1825 / Y400–1000 / Z800–940 |
| Slide motion | 200 mm along X; tool-change line assumed X1545 |
| Fixed guide/drive reserve | X1470–1820 / Y390–1010 / Z750–800 |
| Fixed hood | X1655–1830 / Y380–1020; roof Z960–962 |
| Shutter | X1653–1655 / Y382–1018; closed Z800–960, open Z970–1130 |
| Closest side clearance | 3 mm parked allocation to hood wall; 7.5 mm hood to Y-carriage allocation |
| Open shutter clearance | 20 mm below the modeled gantry lower chord |

The [change STEP](change-allocation.step) and [parked STEP](parked-allocation.step) contain only seven explicitly named allocation/hood solids each. The [two-state plan](plan.svg) shows the existing deck edge and Y-carriage boundary. Orange is the unselected slide/drive volume; purple is a bounded moving envelope. There are no invented magazine pockets, rail mounting holes, actuator interfaces or completed frame brackets. The 2 mm hood sheets are a packaging concept, with no fabricated bends, fasteners, seals or guides released.

**A 200 mm rail is not a 200 mm stroke.** For a length example, HIWIN lists an MGN12H nominal block length of 45.4 mm; its catalog maximum envelope is 45.8 mm including end details. Two blocks per rail at 80 mm center spacing, 200 mm movement and 10 mm allowance at each end need at least **345.8 mm**. A **350 mm rail** is therefore the illustrative candidate, with 12.1 mm actual end margins in this layout. The same two-block arrangement on a 200 mm rail leaves only **54.2 mm travel**; a single block leaves 134.2 mm with the same margins. These are length calculations, not guide or moment-capacity selection. [HIWIN nominal dimensions](https://www.hiwin.de/en/Products/Linear-guideways/Blocks/Miniature-guides/MGN-HIRES-series/MGN12HZ1CM/p/MGN12HZ1CM), [HIWIN maximum-envelope catalog, PDF page 91 / printed page 88](https://www.hiwin.com/wp-content/uploads/HIWIN-Linear-Guideway-Catalog.pdf#page=91). Section 2-4-19, revision G99TE24-2410, separates L and Lmax; Note 3 includes screws and end-seal lips in Lmax.

The manufacturer states a 60 mm magazine width, but that is not the entire selected magazine, endcap, cover, connector, carrier and tool envelope. Its exact current drawing still has to fit the 160 × 600 × 140 allocation. The manufacturer's 90 mm installation clearance does not establish the actual spindle/tool engagement heights for this machine. [RapidChange FAQ](https://rapidchangeatc.com/faq/).

## What the executable check establishes

Run `python study.py` in a CadQuery environment. It reads the existing full-sheet source without changing it and emits [feasibility.json](feasibility.json), with source hashes and fresh STEP readbacks. It checks both endpoints, the continuous 200 mm magazine sweep and 170 mm shutter sweep against the existing frame, deck, pan and conservative full-Y gantry sweeps. The spindle/Z allocation stays at X780 for slide and shutter motion. It also checks the hood and low slide reserve against an explicit surfacing cutter occupancy at Z900–1050. That bounded cutter interval is an assumption, not a model of a selected spindle/holder.

The full-deck surfacing center reaches X1462.7. With its 12.7 mm cutter radius, the tool reaches X1475.4. The parked assembly clears this occupancy, and the fixed rail/drive reserve sits at least 100 mm below it. **The deployed magazine intersects that extreme surfacing occupancy.** Full-deck surfacing therefore requires PARKED and SHUTTER CLOSED; it must not run with the magazine extended. The full sheet itself remains outside the deployed magazine. The 200 mm magazine slide also intersects the closed shutter, proving why SHUTTER OPEN must be established first.

The intended interlocked sequence is: stop machining and move the spindle to the clear slide position; open and verify the shutter; extend to a rigid mechanical locating stop and verify the deployed clamp; perform a separately qualified M6 sequence; retract after the spindle is clear; verify PARKED; close and verify the shutter; then permit routing subject to the other machine interlocks. This hood has not been qualified against plasma heat, spatter, conductive dust or electrical interference, so PARKED and CLOSED alone must not enable plasma. A slide end switch alone does not establish the repeatable pocket alignment or reaction stiffness needed to loosen and tighten collets. The stops, deployed clamp, shutter actuator, position sensors, wiring, support brackets, cable loop, below-pocket tool clearance and actual Z engagement remain unresolved.

This is a **conditional envelope feasibility result**, not an operating ATC or a fabrication release. Actual purchased dimensions can consume the small side clearances and require a different hood or narrower carrier. The other machine's bed conversion remains separate; this study does not modify or requalify that mechanism. No old variant source or report is rewritten.
