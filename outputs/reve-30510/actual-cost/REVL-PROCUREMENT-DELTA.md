# GM1 Rev L — what the 300 mm Z and the tool changer add to the shopping list

Rev L is Rev K with a 300 mm Z slide and a RapidChange-type tool changer ("the dock") on the bed module. The design is in [RevL-CAD](../../../output/release-review/RevL-CAD/README.md); the controls changes are M12 and M13 in the [GM1 controls](../../../output/controls-2026-09-27/README.md). The fabricated parts below are from the Rev L new-parts cut list ([cutlist.csv](../../../output/release-review/RevL-CAD/cutlist.csv)).

**Nothing here is priced.** The [actual-price audit](REAL-COST.md) still stands at the Rev J scope, **$5,336.10**. The [Rev K delta](REVK-PROCUREMENT-DELTA.md) is unpriced too, and this adds to it.

## Changed

| Was | Now |
|---|---|
| RATTMMOTOR ZBX80, 100 mm stroke (M03) | **The same ZBX80 with a 300 mm stroke** (the listing offers 100–600 mm). Ordered (owner, 27 September) |

## The tool changer kit

- **RapidChange ER11 linear magazine**, the owner's choice ("the rapidautochanger or something like that"). The pocket count and options (IR check, dust cover) are the owner's call.
- The other session's research ([RapidChange selection](../../../variants/common/atc/README.md)) found goods prices of $400–$900 on the maker's configurator, from 4 pockets Basic to 8 pockets Premium, and says the two selectors disagree. It is not a quote: freight, tax, collets, nuts and a tool setter are extra.
- The dock is drawn for a magazine up to 520 × 60 × 80 mm, with cutters up to 15 mm in diameter hanging at most 36.55 mm below it. Check the chosen kit against that before ordering.
- ER11 collets and nuts for each tool. The spindle kit's ER11 nut must match the kit's nut: measure it.

## New purchased parts

**Guides and drive (on the bed module)**

- 2 × HIWIN MGNR12 rail, cut to 281 mm with the first hole 10 mm from the front end.
- 2 × HIWIN MGN12H block.
- 1 × 24 V DC worm gearmotor, about 30 rpm, 8 mm output shaft, self-locking (JGY-370 class), about 49 × 30 × 50 mm.
- 2 × GT2 20-tooth pulley, 6 mm belt, 8 mm bore.
- 1 × GT2 6 mm belt, about 0.6 m, closed by the carrier clamp.
- 1 × 8 mm idler shaft and 2 × F688ZZ flanged bearings, for the front pulley.
- 1 × stiff compression spring for the belt clamp (preload at the front stop).
- 2 × M8 inductive sensor, PNP NO, 2 mm range, 10–30 V, with cables.
- 1 × M12 8-pin panel receptacle and a matching cable to the cabinet.

**Fasteners**

- 8 × M5 T-nut for 20-series slots, and 8 × M5 × 12 button head (feet to strips).
- 8 × M5 × 30 socket head (saddles through the risers).
- 8 × M3 × 10 socket head and M3 washers (blocks).
- 22 × M3 × 8 socket head (rails).

**Controls (M12, M13)**

- 1 × Omron G7SA-2A2B 24 VDC force-guided relay and P7SA-10F socket (K_DIR, spindle reverse).
- 2 × Finder 40.52.9.024.0000 relay and 95.05 socket (K_DOCK_RUN, K_DOCK_DIR).
- 1 × 2 A time-delay fuse and holder (F_DOCK).
- 2 × roller-lever microswitch, NC, IP67, and 2 × 1N4007 (dock end of travel).
- Interface board additions: ULN2803A, 2 × PC817 with resistors, one more 470 Ω pull-up.

## New fabricated parts and their stock

| Part | Qty | Stock | Note |
|---|---:|---|---|
| Rail beam, 285 mm | 2 | 1 × 2 × .083 in steel rectangular tube, 0.6 m | Scrap or new tube; not the 2 × 2 frame list |
| Rail seat bar, 25.4 × 285, machined to 9.05 | 2 | 3/8 × 1 in steel flat bar, 0.6 m | Weld on the tube, then machine the rail seat flat |
| Carrier, 590 × 167 U-plate with a 480 × 40 window | 1 | 1/4 in steel plate | Probably fits the MET13 1/4 in plate offcut (24 × 48 in); confirm when nesting |
| Feet 60 × 40, drive tab 36 × 61, belt clamp, two upstands (478 and 530 × 17.65 on edge) | 4, 1, 1, 2 | 1/4 in steel plate and strip | As above |
| Front and rear stops, pulley brackets, sensor bases and uprights, connector bracket | 9 | 1/4–1/2 in steel offcuts | Small blocks, welded to the right beam |
| Motor plate, 98 × 78 | 1 | 3/16 in steel | Welded to the right beam end |
| Magazine saddle blanks, 40 × 65 | 2 | 1/4 in aluminum | Drill the magazine holes from the delivered kit |
| Risers, 12 OD × 5.5 ID × 17.65 | 8 | 12 mm steel bar or tube | Turned |

About 6 kg of steel and aluminum in all; the dock with its bought parts is about 10.6 kg, with 3.3 kg allowed for the magazine and cutters.

## Frame fill

Rev L moves the frame's 18 fill holes to each tube's high end so every tube can be filled full ([build order, section 6](../../../output/release-review/RevL-CAD/BUILD-ORDER.md#6-filling-the-frame)). The weld bungs and M20 plugs stay 18 of each. The frame tubes and the two ported top-rail end caps (SAND_ENDCAP_2IN_PORTED) appear in the Rev L new-parts cut list only because their holes moved; their stock is unchanged.

Fill material is not priced:
- **Epoxy sand** (the owner is considering it): about 12–15 L of slow, low-viscosity epoxy and fine dry sand, about 36 L of fill in all. If the threaded plugs are left out, 18 push-in hole plugs for 30 mm (1-3/16 in) holes.
- **Dry sand:** about 36 L.

## How to use this

The [build order](../../../output/release-review/RevL-CAD/BUILD-ORDER.md) says which of these parts gate which build steps.

Add these rows to the register as unpriced scope when quotes are gathered. The RapidChange kit is the largest item, and its exact configuration decides the magazine interface, so choose it before drilling the saddles.
