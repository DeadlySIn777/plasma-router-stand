# Owned aluminum plate fit — RevE, 2026-09-24

The user reports owning **1/2-inch and 3/8-inch aluminum, 12 × 12 inches**. This review provisionally allocates **one plate of each thickness**. Quantity, alloy/temper, actual thickness and usable flatness are not yet confirmed. No CAD geometry or purchasing baseline is changed by this report.

**One 12 × 12 × 1/2-inch plate can replace the $58.74 Z-carrier raw-stock purchase (MET08), conditionally.** It cannot replace the entire aluminum stock budget. The expensive gantry feet and thrust-link supports are already aluminum; their cost comes from the integral billet construction.

## Current unchanged parts that fit the 1/2-inch plate

Coordinates are in millimetres from the lower-left corner of a 304.8 × 304.8 plate. These are bounding rectangles, not released machining programs.

| Part | Quantity | X | Y | Width | Height | Finish thickness |
|---|---:|---:|---:|---:|---:|---:|
| Z_CARRIER | 1 | 10 | 10 | 260 | 170.2 | 12.7 |
| TOOL_INTERFACE_HOLD | 1 | 10 | 186.2 | 110 | 70 | 12.7 |
| HMS40_DRIVE_SHOE_6p35, first | 1 | 126 | 186.2 | 65 | 48 | 6.35 |
| HMS40_DRIVE_SHOE_6p35, second | 1 | 197 | 186.2 | 65 | 48 | 6.35 |

The checked nest has at least **10 mm edge clearance** and **6 mm between all bounding rectangles**. Net rectangles occupy **58,192 mm²**, or **62.64%** of the 92,903.04 mm² plate area. The two drive shoes must be faced down from nominal 12.7 to 6.35 mm.

This gives **one conditional $58.74 goods credit**, not four separate credits. The tool interface and two drive shoes were already allocated to offcuts of MET07, the 1/2 × 8 × 72-inch aluminum bar. Moving them onto owned stock leaves MET07 required for the long X face and the two Y shoes. No confirmed freight reduction follows automatically.

The Z carrier and tool interface remain guarded in the current cut list because the actual Z module interfaces are not closed. Reserving the stock does not release their holes. The nominal 1/2-inch thickness is also the modeled 12.7 mm finished thickness: assess actual plate flatness and thickness before assuming both faces can be machined to final size.

If the owned plate is unsuitable or unavailable, **MET08 remains the standalone fallback purchase**. Do not count both sources as consumed stock.

## What the remaining 1/2-inch flats require

| Current part | Quantity | Each finished rectangle, mm | Total bounding area, mm² |
|---|---:|---|---:|
| X_GUIDE_FACE | 1 | 1200 × 112 | 134,400 |
| Y_SHOE_L / R | 2 | 280 × 131.3 | 73,528 |
| Z_CARRIER | 1 | 260 × 170.2 | 44,252 |
| TOOL_INTERFACE_HOLD | 1 | 110 × 70 | 7,700 |
| Total at 12.7 mm | | | **259,880** |

The 1200 mm X face cannot come from a 304.8 mm plate. Two Y shoes do fit together in one otherwise unused 12-inch plate: at (10,10) and (10,147.3), each 280 × 131.3. That alternative consumes the same owned 1/2-inch plate needed for the Z carrier. It is not an additional saving and would require repricing the shorter purchased stock before selecting it.

The twelve cassette ties are each 500 × 25.4 × 6.35 mm; they are too long for either 12-inch plate. Their four purchased tie-bar sticks remain necessary.

## 3/8-inch plate: useful stock, no immediate separate purchase credit

There are **no unchanged 9.525 mm aluminum parts** in the frozen cut list. The 3/8-inch plate can be machined down for small adapters or drive-only shoes, but those shoes already have stock allocated. It does not replace 12.7 mm rail/carrier plates or the deeper billets.

A practical redesign use is the three thrust-link supports, made as separate aluminum flange/web components rather than integral billets. These current component envelopes fit in a single 12-inch plate:

| Proposed blank, not a released joint design | X | Y | Width | Height | Machine to thickness |
|---|---:|---:|---:|---:|---:|
| X support flange, bounding rectangle | 10 | 10 | 156 | 120.8 | 6.35 |
| X support web | 10 | 136.8 | 156 | 30 | 8 |
| Left Y flange | 172 | 10 | 103.1 | 32 | 6.35 |
| Right Y flange | 172 | 48 | 103.1 | 32 | 6.35 |
| Left Y web | 172 | 86 | 32 | 40 | 8 |
| Right Y web | 210 | 86 | 32 | 40 | 8 |

All bounding rectangles pass **10 mm edges / 6 mm gaps**. They occupy **32,683.2 mm²**, or **35.18%** of the plate. This proves stock fit only. The flange-to-web connections still need fasteners, locating features/gussets, access, thread engagement and stiffness checks; additional material may be needed for those joints. The current model cannot treat a new bolted or welded seam as a continuous machined billet.

No savings are applied for this candidate. MET10 ($114.36) supplies the integral X support, but MET09 ($296.31) also supplies both gantry feet as well as the Y supports. Redesigning only the Y supports therefore does not remove the entire MET09 purchase.

## Billet parts that sheet does not directly replace

| Current part | Quantity | Current bounding envelope, mm | Why a flat-plate substitution is a redesign |
|---|---:|---|---|
| Gantry end bracket | 2 | 150 × 80 × 82.7 | Integral 12.7 flange and 70 mm downstand; a flat assembly needs defined load-bearing joints |
| Y link support | 2 | 103.1 × 32 × 46.35 | Integral 6.35 flange / 8 mm web |
| X link support | 1 | 156 × 120.8 × 36.35 | Integral 6.35 flange / 8 mm web |
| Clevis billet | 6 | 40 × 48 × 32 | Aligned ears and common pin bore; a stacked/bolted arrangement changes the pin and joint design |
| X drive shoe | 1 | 65 × 48 × 19.05 | Thicker than either owned plate; stacking changes the design |
| Spindle clamp halves | 2 | 100 × 45.25/44.75 × 40 | Clamp bore, split, blind threads and pinch-load path require the existing depth or a new verified clamp |

A future fabricated gantry-foot design would start with two 150 × 80 flanges plus two 80 × 70 webs, **35,200 mm² total** at 12.7 mm thickness. Those four component rectangles fit one otherwise unused 12-inch plate: flanges at (10,10)/(10,96), webs at (166,10)/(166,86). The owned 1/2-inch plate is already allocated to the carrier in the present proposal, so this is an alternative use, not free additional stock. It is also a component layout rather than a finished bracket design; joints and nesting must be designed together.

## Steel parts that are poor direct substitution targets

The pan-bearer hangers/endplates, bed-support feet, rack hangers, welded gussets, reservoir rim, water-pan attachments and tool parking cradles are attached to the steel chassis or pan by specified steel welds. Changing those plates to aluminum requires new mechanical connections rather than retaining the present weld callout. Their joint stiffness, bolt bearing, thread engagement, datum offsets and wet dissimilar-metal contact need review.

Small bolted sensor/cable/accessory mounts are sensible aluminum candidates when their dimensions are finalized. Current stop brackets also carry mechanical buffer loads, so they should not be treated as decorative sensor tabs. The present cost audit does not give these tiny parts separate stock purchases to delete: removing a few from a larger steel-sheet nest often leaves the sheet purchase unchanged.

## Cost interpretation and verification

- Owner fabrication labor remains **$0**.
- Reserve owned stock at **$0 new cash outlay**, without pretending it removes unrelated raw-stock purchases.
- Only **MET08 $58.74 goods** is currently identified as an independently avoidable purchase.
- Unknown alloy/temper must be resolved before using the owned aluminum as a structural substitute for the specified 6061-T6 parts.
- The existing 2 × 2 steel tube chassis remains a separate cost driver; changing small adapter material does not remove its six 20-foot tube bars.
- No orders placed, no supplier contacted, no baseline/CAD changes made by this review.

Checks: check_owned_aluminum.py asserts every proposed rectangle lies inside the 10 mm inset and every pair has at least 6 mm separation. Both layouts passed. See OWNED-ALUMINUM-INVENTORY.json for the machine-readable assumptions, coordinates and conditional credit.

Sources: current RevE cutlist.csv / cutlist.json and motion_details.py; actual-cost/metal-findings.json and METAL-AUDIT.md. Prices here are the existing audit's posted goods prices, not fresh delivery quotes.
