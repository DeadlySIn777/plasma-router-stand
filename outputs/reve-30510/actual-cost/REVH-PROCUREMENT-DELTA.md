# GM1 Rev H — what the one-piece bed changes in the shopping list

Computed from the two CAD cut lists (`revh_procurement_delta.py` → `revh-procurement-delta.json`), the two 2 × 2 tube plans and the stock-fit check (`check_revg_stock_fit.py --cad RevH-CAD`). The design is in [RevH-CAD](../../../output/release-review/RevH-CAD/README.md). Only the bed, its receiver and the bed storage change. Frame, water system, motion and controls are the same as Rev G.

## No longer needed (Rev G bed)

| What | Rev G quantity | Register row |
|---|---:|---|
| 397 mm extrusion pieces (30 cut from the 10 bars) | 30 | B01, still bought; see below |
| MDF spoilboards (3/4 in MDF sheet) | 6 | MET-GAP-14 |
| Aluminum panel ties, 3/8 in plate or bar | 24 | MET-GAP-17 |
| 2 mm steel rack guides | 28 | MET-GAP-16 |
| 30 × 30 × 3 mm rack-fork tube | 2 | MET-GAP-19 |
| Extra 1/4 × 12 × 12 in plate for the tool cradles | 1 | MET-GAP-15: Rev H's 6 mm parts (38) fit one 24 × 48 in plate (MET13) |
| Beams, beam feet, seats, front seats, clamp bridges, bosses, racks, hardware trays | 135 flat pieces, 6 tubes, 60 machined | shop-made from registered stock |
| M5 × 20 DIN 7991 spoilboard screws | 24 | N3 |
| M8 × 80 beam drawdowns | 8 | N5 |
| M8 × 20 front-seat screws | 4 | unpriced |
| M5 × 16 button screws and 15 mm washers (ties) | 72 + 72 | unpriced |
| M6 × 35 clamp screws | 16 of 20 | unpriced |
| 6 × 12 locator pins | 8 | unpriced |

## New for Rev H

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

Owner scope, not in the register: overhead beam, trolley and hoist; 4-leg sling; four 3/8 in screw-pin shackles; module stand or cart.

## Effect on the priced register

Rev H is the current design, but the priced register ([REAL-COST.md](REAL-COST.md)) has not been re-baselined yet and still carries the Rev G bed rows. The main changes it needs:

- **B01** stays at five two-packs.
- **MET01** needs a sixth 2 × 2 length, 8 ft being enough.
- **MET14** grows to 12 × 36 in, or gets a small flat bar.
- **N1** drops to 48 nuts; N3 and N5 drop out.
- **New unpriced rows:** HDPE sheet, stainless tray sheet, stainless module hardware, galvanizing.
- **Rev G-only unpriced rows** (MDF, ties, 2 mm sheet, 30 × 30 tube, the extra 1/4 in plate) leave the scope.
