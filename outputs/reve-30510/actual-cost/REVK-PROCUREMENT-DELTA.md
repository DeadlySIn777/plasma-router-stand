# GM1 Rev K — what the completed one-piece line adds to the shopping list

Computed from the Rev J and Rev K CAD cut lists (`revk_procurement_delta.py` → `revk-procurement-delta.json`) and the GM1 controls parts list. The design is in [RevK-CAD](../../../output/release-review/RevK-CAD/README.md) and the [GM1 controls](../../../output/controls-2026-09-27/README.md).

**Nothing here is priced.** The [actual-price audit](REAL-COST.md) still stands at the Rev J scope, **$5,336.10**. Every Rev K and controls item below is new, unpriced scope until an offer is linked. The frame, bed module, water table and motion are unchanged from Rev J, so the 2 × 2 tube list and the Rev J rows stay as they are.

## Replaced (Rev J reserve → Rev K part)

| Rev J | Rev K |
|---|---|
| Drain reducer, valve, union and drop reserves (space only) | Rev I's welded reducer, 1 in motorized valve, nipples and removable tail with its flanges and parking cup |
| Refill hose connection reserve | Rev I's pressure hose (lowered 20 mm) and a smaller fitting zone |
| 20 × 16 × 8 in controls enclosure reserve | Rev I's VEVOR 500 × 400 × 200 box, with Rev K's gland plates, fan and filter |
| 20 mm drip-cap front lip | 8 mm lip (the door now opens) |
| Refill spout | The same spout with its riser 2 mm longer (32 mm air gap) |

## New purchased items

**Plasma head (Rev I design)**

- 4 igus RJ4JP-01-08 bearings.
- 1 Omron D2HW-C202MR float switch and 3 D2HW-C203MR presence switches.
- 3 Supermagnete CSN-20 pot magnets.
- 47 M3 and M4 socket screws, and 3 M4 × 16 countersunk.

**Torch mounting (Rev K)**

- 1 one-piece clamp collar, 28 mm bore.
- 4 M6 × 20 countersunk screws (bracket to head).
- 4 M6 × 30 socket screws with washers and nylocs (adapter to bracket).
- 2 M5 × 20 socket screws for parking.
- The torch is the owner's: a PT31-style straight machine torch, 270 × 28 mm.

**Drain and strainer (Rev I design)**

- USS MSV00009 1 in normally-closed motorized valve.
- SEAFLO SFWS-500-02 strainer.
- M4 and M6 fasteners: 4 M6 × 30 head-down, 6 M4 × 35 head-down, 4 M4 × 16, nylocs and weld nuts.

**Hoses**

- Parker 801-6 (3/8 in) hose: the pressure route plus the rerouted suction route, cut to measured ends.
- Parker 82 series end fittings, not yet selected.

**Manual reservoir drain (Rev K)**

- 1/2 NPT 3000# half coupling.
- 1/2 in street elbow, close nipple, full-port ball valve.
- 1/2 MNPT × 3/4 garden-hose adapter and cap.

**Cabinet (Rev K)**

- IP54 filter fan (120 mm class, 24 V DC, 40 m³/h or more) and a matching outlet filter.
- 8 EMC glands (4 × M20, 4 × M16).
- 18 nylon glands (4 × M25, 2 × M20, 12 × M16) and blanking plugs.
- 16 mm² bond braid.
- 8 M5 × 16 head-down screws and nylocs.

**Seals.** Nitrile (NBR) sheet instead of the registered EPDM sheet, for the reservoir, hatch, washout and drain-tail gaskets. The cabinet gland gaskets stay closed-cell EPDM.

## GM1 controls parts

From [gm1-components.json](../../../output/controls-2026-09-27/gm1-components.json) ("added"):

- **Safety relay:** Pilz PNOZ X2.8P or an equivalent with a monitored reset.
- **Contactors:** 2 Schneider LC1D18BD with coil suppressors.
- **Operator devices:** E-stop, RESET button, safety fuse and holder.
- **Force-guided relays:** 7 Omron G7SA with 7 sockets.
- **Finder relays and timers:**
  - 4 Finder 40.52: K_RDY_R and K_RDY_P, plus K_DRAINED and K_EMPTY_B (new);
  - 2 Finder 80.01 timers: T_BRAKE, plus T_FILL (new).
- **Selector block:** ZBE101 contact block.
- **Interface:**
  - isolated 0–10 V conditioner;
  - arc-OK current switch;
  - 48 V to 24 V DC-DC;
  - interface-board parts.
- **Cutter-side start box (new):**
  - K_TS interposing relay with reinforced isolation;
  - die-cast box;
  - 24 V supply.

Retired from Rev I's list: the C41S, the LTV-817 and five Finder relays (K_READY, K_REQUEST, K_RUN_ARM, K_VFD_RUN, K_TORCH_RUN).

The BTT Rodent, the THCAD-300 (owned) and the braked Z motor were already required.

## New fabricated parts and their stock

The table is from `check_revg_stock_fit.py --cad RevK-CAD` (`revk-stock-fit.json`). That script packs the DXF outlines onto the sheet and plate sizes already in the register.

| Stock | New Rev K parts on it | Result |
|---|---|---|
| **2 mm stainless** (MET-GAP-6, one 12 × 12 in) | 2 gland plates 175 × 150, 2 head bearing caps | **Short: needs 3 pieces of 12 × 12 in** (or one 12 × 24 plus one 12 × 12) |
| **3/8 in aluminum** (no row) | Head backplate 110 × 130 | **New requirement:** one 12 × 12 in piece. The owner's 3/8 in piece fits, if its alloy qualifies |
| **1/2 in 6061 aluminum** (no row; not counted by the check) | Drop bracket 110 × 225 | **New requirement:** one 6 × 12 in piece. The owner's 1/2 in piece is allocated to the Z carrier |
| 1/4 in steel finished to 6 mm (MET13, 24 × 48 in) | Drain flanges and reducer, strainer tray, suction standoffs, rear posts and stanchion | Covered |
| 1/4 in steel as rolled, 6.35 (from MET13; not counted by the check) | 3 park feet 40 × 30, head release plate 97 × 110 | Probably fits in the MET13 offcut; confirm when nesting |
| 3 mm steel (MET-GAP-2, 36 × 48 in) | VFD plate 210 × 389, roof gussets, hose-clamp straps, strainer lands, uprights and tops, drain park base, suction guides | Covered |
| .120 steel (MET-GAP-1, two 48 × 96) | Drain wall strap | Covered |
| 1.5 mm steel (MET-GAP-3, 24 × 24 in) | Drip lip 436 × 8, VFD drip roof 200 × 240 | Covered |
| 1.5 mm stainless (MET-GAP-5) | Head splash screen and tabs | Covered |
| 8 mm steel (MET14) and 3 mm stainless | none new | Short and new, as already recorded for Rev J |

## Machined and turned parts

- **Plasma head, Rev I design:** two crossbars, float carriage, float stop, clamp halves, cam, switch brackets, seats, ball buttons, magnet spacers, tether eyes, lead saddle.
- **Stock for the head:**
  - two ground Ø8 h6 shafts, 118 mm;
  - acetal for the bushing spacers and cam;
  - an insulating insert blank, bored to the measured torch + 0.10.
- **Drain screen basket:** 0.8 mm perforated 304, Ø40 × 40 with a Ø60 flange.
- **Park pads:** three, from 3 mm steel.
- **Hose clamp blocks:** six, 20 × 37 × 14 mild steel offcuts.
- **Strainer posts:** two 58 mm pieces of 1 × 1 × .083 tube.
- **Refill spout:** NPS 1/2 pipe, as Rev J (riser 2 mm longer).

## How to use this

Add these rows to the register as unpriced scope when quotes are gathered. The owner's two 12 × 12 in aluminum pieces are still uncounted:

- The 3/8 in piece would take the head backplate (110 × 130).
- The 1/2 in piece is already allocated to the Z carrier, so the drop bracket (110 × 225 × 12.7) probably needs its own piece.
