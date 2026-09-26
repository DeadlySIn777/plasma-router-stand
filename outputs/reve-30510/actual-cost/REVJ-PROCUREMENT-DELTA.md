# GM1 Rev J — what the one-piece bed and the Rev H water work change in the shopping list

Computed from the two CAD cut lists (`revj_procurement_delta.py` → `revj-procurement-delta.json`), the two 2 × 2 tube plans and the stock-fit check (`check_revg_stock_fit.py --cad RevJ-CAD`). The design is in [RevJ-CAD](../../../output/release-review/RevJ-CAD/README.md). Compared with Rev G, the bed, its receiver and the bed storage change. So does the water service taken from the base branch's Rev H: reservoir hatches, washout closure, drain reserves and a refill spout moved clear of the module. The Z adapter becomes a transfer-drill blank. Frame, water table, motion and controls are otherwise the same as Rev G.

This design was first published on this branch as "Rev H". It was renamed Rev J on 26 September 2026 because the base branch's Rev H is a different design, the six-panel bed; that Rev H is not priced here.

## No longer needed (Rev G bed)

| What | Rev G quantity | Register row |
|---|---:|---|
| 397 mm extrusion pieces (30 cut from the 10 bars) | 30 | B01, still bought; see below |
| MDF spoilboards (3/4 in MDF sheet) | 6 | MET-GAP-14 |
| Aluminum panel ties, 3/8 in plate or bar | 24 | MET-GAP-17 |
| 2 mm steel rack guides | 28 | MET-GAP-16 |
| 30 × 30 × 3 mm rack-fork tube | 2 | MET-GAP-19 |
| Extra 1/4 × 12 × 12 in plate for the tool cradles | 1 | MET-GAP-15: Rev J's 6 mm parts (38) fit one 24 × 48 in plate (MET13) |
| Beams, beam feet, seats, front seats, clamp bridges, bosses, racks, hardware trays | 135 flat pieces, 6 tubes, 60 machined | shop-made from registered stock |
| M5 × 20 DIN 7991 spoilboard screws | 24 | N3 |
| M8 × 80 beam drawdowns | 8 | N5 |
| M8 × 20 front-seat screws | 4 | unpriced |
| M5 × 16 button screws and 15 mm washers (ties) | 72 + 72 | unpriced |
| M6 × 35 clamp screws | 16 of 20 | unpriced |
| 6 × 12 locator pins | 8 | unpriced |

## New for Rev J

| What | Quantity | Stock or purchase |
|---|---:|---|
| 20100 profile cut to 1,197 mm | 9 | From the same **five two-packs (B01)**: one saw cut per bar, one bar spare |
| Module rails, 2 × 2 × .120, 1,330.9 mm | 2 | 2 × 2 tube: the plan needs **5 full 20 ft bars plus about 1.84 m** (two crossmembers, trim and kerfs). An 8 ft length covers it; the tube plan as written buys a 6th 20 ft bar |
| Crossmembers, 2 × 2 × .120, 912.4 mm | 4 | as above |
| HDPE plates 398 × 1,000, 3/4 in sheet finished to 18 mm | 2 | **One 48 × 48 in sheet** of 3/4 in HDPE (new) |
| Lift lugs, 3/8 in steel 50 × 75 | 4 | 3/8 in plate: the lugs and the existing 8 mm parts need **one 12 × 36 in or 24 × 24 in** piece instead of MET14's 12 × 24 in, or add a 3/8 × 4 × 12 in flat bar for the lugs |
| Crossmember end plates 6 mm, seat pads 6 mm | 8 + 6 | MET13 1/4 × 24 × 48 in (covered) |
| Rail end caps, .120 sheet | 4 | MET-GAP-1 (covered) |
| Bolt tray, 3 mm stainless | 5 pieces | One 12 × 12 in piece of 3 mm (or 11 ga) 304 (new) |
| Compression and ledger sleeves, OD18 × 50.8 | 6 + 6 | Round bar, MET-GAP-18: 12 × 50.8 mm plus cuts still fits a 36 in bar |
| M10 × 80 ISO 4762 A4-70 + M10 washers A4 | 6 + 6 | the only release screws |
| M5 × 8 ISO 7380 A4 button screws | 36 | strips to crossmembers |
| M5 × 12 ISO 4762 A4 + 15 mm A4 washers | 12 + 12 | HDPE plates |
| M5 DIN 562 A4 square nuts | 48 | the N1 Nutty offer is this stainless nut: 48 instead of 96 |
| Ø10 × 56 hardened stainless dowel pins | 2 | locating pins |
| Hot-dip galvanizing of the module weldment | about 32 kg of steel | galvanizer's minimum lot charge usually governs |

## New for Rev J from the base branch's Rev H water service and Z adapter

| What | Quantity | Stock or purchase |
|---|---:|---|
| Hatch covers, .120 steel, 360 × 215 and 310 × 140 | 2 | MET-GAP-1 .120 sheet (covered: 2 sheets of 48 × 96 with everything else) |
| Cover parking pockets and pull tabs, 3 mm steel | 16 + 2 | MET-GAP-2 3 mm sheet (covered) |
| Washout flange Ø90 × 6 and refill gusset 45 × 60 × 6 | 1 + 1 | MET13 1/4 × 24 × 48 in (covered with the other 38 six-mm parts) |
| Washout cover Ø90 × 4 mm | 1 | **MET-GAP-24**: 4 mm plate, 6 × 6 in (new) |
| Refill spout, NPS 1/2 schedule 40, three mitered pieces | 1 | **MET-GAP-25**: 18 in threaded-one-end nipple or cut length (new) |
| Hatch gaskets 360 × 215 and 310 × 140, washout gasket Ø90, 2 mm EPDM | 3 | From the 906 × 606 mm centre offcut of the reservoir gasket sheet, MET-GAP-13 (covered) |
| M5 weld nuts and M5 × 16 socket screws (hatches) | 12 + 12 | unpriced, in HW-GAP-H03 |
| M6 × 25 socket screws, M6 washers, M6 nyloc nuts (washout cover) | 4 + 4 + 4 | unpriced, in HW-GAP-H03 |
| Drain reducer, valve and union reserves; refill hose connection reserve | space only | purchased plumbing still to select; no fittings are invented |
| Z adapter, 110 × 110 × 12.7 aluminum | 1 | same blank as before, now an undrilled transfer blank (H_TOOL_ADAPTER_TRANSFER_BLANK) |
| Braked Z-motor candidate 23HS30-5004D-B280 | 0 for now | the model reserves its envelope in place of the stock ZBX80 motor; **not a purchase** until the ZBX80 shaft, pilot and coupling are measured (HW-GAP-R05) |

Owner scope, not in the register: overhead beam, trolley and hoist; 4-leg sling; four 3/8 in screw-pin shackles; module stand or cart.

## Effect on the priced register

The priced register ([REAL-COST.md](REAL-COST.md)) was re-baselined to Rev J on 26 September 2026. It showed **$5,334.09** priced then; with the owner-reported $82 for the 1,200 mm rail kit it is **$5,336.10** ($5,249.85 goods + $86.25 known shipping), with 73 priced lines. Before the re-baseline it showed $5,348.40. The Rev H water-service rows raise the unpriced entries from 49 to 51 and leave the priced total unchanged.

- **B01** stays at five two-packs.
- **N1** is 48 stainless square nuts ($3.65).
- **N3** (MDF screws) and **N5** (M8 × 80 drawdowns) are superseded, as are MET-GAP-14, 15, 16, 17 and 19 (MDF, extra 1/4 in plate, 2 mm sheet, aluminum ties, rack tube).
- **New unpriced rows:** MET-GAP-20 HDPE, MET-GAP-21 stainless 3 mm, MET-GAP-22 3/8 × 4 in bar, MET-GAP-23 8 ft of 2 × 2 tube, MET-GAP-24 4 mm plate, MET-GAP-25 1/2 in pipe, J-GALV galvanizing. HW-GAP-H06/H07/H08 describe the Rev J stainless module hardware; HW-GAP-H03 now includes the hatch and washout fasteners, and HW-GAP-R05 the braked-motor candidate.
- **2 × 2 tube:** the owner is looking for it at a scrapyard. The Rev J list of 32 blanks is in the [package README](../../../output/release-review/RevJ-CAD/README.md#2--2-tube-for-the-scrapyard). MET01 and MET-GAP-23 price new stock only.

The lower total is **not a cheaper build**: the new Rev J items are still unpriced. The Nutty order ($76.06) stays below its $100 free-shipping threshold unless the Rev J stainless fasteners are bought there too.
