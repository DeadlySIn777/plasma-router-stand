# CNC / plasma BOM — Alto, Georgia 30510

> **SUPERSEDED DESIGN BASIS — NOT AN ORDER LIST.** The extrusion-bed and pre-order engineering review is now recorded in [PREORDER-STATUS.md](../../output/release-review/PREORDER-STATUS.md). Motion-module qualification, controller/live-THC compatibility and manufacturing interfaces are unresolved. The workbook alongside this brief still represents the older Rev C concept and has not been converted to a released Rev D BOM.

Prices researched September 24, 2026. USD. Sales tax is additional.

The retained, destination-checked Amazon components total **$1,382.44 including advertised delivery to Alto**. The revised proposal uses a **Kraken V1.1 with onboard drivers**, with Manta M5P retained as an alternative. The full Rev C concept has **87 BOM rows**, including owned, zero-quantity and alternative items. Controller firmware and live plasma THC remain unresolved and development is unpriced.

| Exact Amazon item | Qty | Unit price | Goods | Shipping |
|---|---:|---:|---:|---|
| [KHMOS HMS40 X, 800 mm](https://www.amazon.com/dp/B0C7GQTRRX) | 1 | $236.00 | $236.00 | $0 shown to Alto |
| [KHMOS HMS40 Y, 1000 mm](https://www.amazon.com/dp/B0C7GN24S1) | 2 | $260.00 | $520.00 | $0 shown to Alto |
| [RATTMMOTOR ZBX80, 100 mm](https://www.amazon.com/dp/B09MVYGLNQ) | 1 | $112.00 | $112.00 | $0 shown to Alto |
| [Zhong Hua Jiang 1.5 kW / 110 V ER11 spindle kit](https://www.amazon.com/dp/B0BF5R3LNC) | 1 | $309.99 | $309.99 | $0 shown to Alto |
| [MEAN WELL LRS-350-36](https://www.amazon.com/dp/B071HSNP83) | 1 | $36.07 | $36.07 | $0 shown to Alto |
| [MEAN WELL LRS-150-24](https://www.amazon.com/dp/B018RE4CWW) | 1 | $23.50 | $23.50 | Qualifying Amazon basket |
| [VEVOR 20 × 16 × 8-inch steel enclosure](https://www.amazon.com/dp/B0924BN1P5) | 1 | $84.90 | $84.90 | $0 shown to Alto |
| [Enclosed 25 × 50 mm cable chain, R55, 1 m](https://www.amazon.com/dp/B0DSPK5X4V) | 2 | $29.99 | $59.98 | Qualifying Amazon basket |
| **Total** | | | **$1,382.44** | **$0.00 shown** |

Small Amazon-shipped items rely on the qualifying basket of at least $35. This retained basket excludes Prime-only discounts, tax and the separately listed CB1 screenshot offer. Delivery and stock must be rechecked at checkout. Motors are included in the four motion modules; the spindle kit includes its VFD, 65 mm clamp, wires, wrenches and ER11 collets, so those are not purchased twice. The linked spindle is ER11, despite the earlier ER17 wording. External DM556T drivers and the separate 5 V supply have been removed from purchases.

## Onboard motion control

| Core hardware | Parts price | Delivery evidence |
|---|---:|---|
| Kraken V1.1 + CB1 + Pi4B carrier | **$191.96** | BIQU advertises free shipping above $59; CB1 screenshot shows Prime free delivery. Alto checkout unverified. |
| Manta M5P + CB1 + four TMC5160T Pro modules | **$159.82** | Same shipping qualifications; alternative is excluded from build totals. |

The [Kraken V1.1 is $129.99](https://biqu.equipment/products/kraken-for-voron-phoenix), the user screenshot CB1 is $32.99, and its required [Pi4B carrier is $28.98](https://biqu.equipment/products/pi4b-adapter-v1-0?variant=39919128969314). Kraken cannot accept a bare CB1 directly. The Manta screenshot board is $59.99 and accepts CB1 directly; its [four-pack of TMC5160T Pro plug-in drivers is $66.84](https://biqu.equipment/products/tmc5160-pro-v1-0?variant=40301980647522). These modules sit on the motherboard. Neither route uses external motor-driver boxes. Exact Amazon Kraken V1.1 ASIN B0F7RQY6Z4 was unavailable, so the official store supplies that price.

The proposed Kraken allocation is S1=X, S2=Y-left, S3=Y-right and S4=Z, with independent Y home switches. [BTT specifies eight integrated TMC2160 drivers](https://global.bttwiki.com/Kraken.html); V1.1 S1-S4 have a published 4.7 A maximum, whereas the older V1.0 uses different sense resistors and an 8 A maximum. These are not the motor current settings. X/Y motor phase ratings still need confirmation. The 36 V supply feeds HV only; DCIN uses 24 V. Driver cooling, connectors and host power require final checks.

The board hardware supports the requested arrangement, but firmware support is a separate requirement. Stock Klipper and Marlin support both boards. Neither has a verified ready-to-flash live plasma THC package in this review. The current [grblHAL H7 board list](https://github.com/dresco/STM32H7xx/blob/master/driver.json) has no Kraken mapping, and the old [Klipper-plasma processor list](https://github.com/proto3/klipper-plasma/blob/master/src/stm32/Kconfig) lacks both target processors. Adding an external up/down THC box does not by itself solve the firmware integration. The workbook therefore replaces the assumed Mesa interface/I/O with explicitly unresolved provisions, adds a spindle interface allowance, and removes the separate LinuxCNC PC purchase.

## Complete concept budget

| Route | Common goods | Water-option goods | Shipping and reserves | Planning total |
|---|---:|---:|---:|---:|
| Electric refill pump + motorized drain | $7,717.27 | $827.18 | $570.00 | **$9,114.45** |
| Pneumatic air-displacement chamber | $7,717.27 | $985.00 | $565.00 | **$9,267.27** |

These are **planning estimates**, not delivered supplier quotations. The common-goods subtotal contains $2,045.05 of observed prices, including the user-provided CB1 price, and **$5,672.22 of explicit allowances**. CNC firmware development, live THC integration and any required additional hardware remain unpriced beyond the listed provisional allowances. Local fabrication, fit-specific hardware and freight remain material uncertainties. Do not interpret cents on formula totals as quotation precision.

The current concept includes a sand-filled six-leg chassis, four paired removable bed beams, six aluminum/MDF deck panels, datum hardware, a storage rack with lift-off covers, guards, motion hardware, spindle, controls and a water-change system. It is substantially more than the earlier basic stand/pan scope. The workbook keeps every allowance editable and shows its source or missing selection beside the row.

DIY welding/assembly labor and welding consumables, tax, fabrication tools, shop wiring installation and paid CAD/CAM licenses are excluded. CB1, carrier, storage and cooling are budgeted; a network browser device is assumed available and a local control screen is unpriced. Extraction/air-treatment equipment is required if unavailable and its allowances remain separate. A non-HF plasma replacement is an optional comparison, not an assumed purchase.

## Metal sourcing

Ask [SteelMart Gainesville](https://steelmartatlanta.com/steelmart-gainesville-ga/) first for one consolidated stock/cutting/delivery quote. Their listed address is 455 Industrial Boulevard, Gainesville, GA 30501, phone 770-297-6675. [Metal Supermarkets Buford](https://www.metalsupermarkets.com/location/buford/) and [Cherokee Steel](https://cherokeesteel.com/) are additional regional sources.

Published remote suppliers are price comparisons. An Oklahoma or Los Angeles raw-stock price is not a Georgia delivered price.

- The full 2 × 2 × .120-inch tubing takeoff is **29.6372 m / 97.235 ft**, across 29 finished pieces. It fits **five full 20-foot bars** with the stated 3 mm saw kerf and 10 mm trim per bar. Do not have the stock arbitrarily halved before applying the nesting.
- [Looper's published list](https://www.loopersmetalworks.com/metal-products/) gives $403 for five nominal 20-foot 2-inch, 11-gauge tubes, before cuts and freight; actual wall must be confirmed.
- [Online Metals' exact .120-inch tube](https://www.onlinemetals.com/en/buy/carbon-steel/2-x-0-12-carbon-steel-square-tube-a500-a513-hot-rolled/pid/10343) showed $1,011.50 for five 20-foot bars. This wide range is why the workbook uses an explicitly unquoted $500 local raw-stock allowance.
- The six deck subplates nest in one 48 × 48-inch **5/16-inch 6061-T651** plate. [Online Metals](https://www.onlinemetals.com/en/buy/aluminum/0-3125-aluminum-plate-6061-t651/pid/14480) showed $759.54 before cutting/freight; the local $600 allowance still needs a quote.
- [80/20 standard 40-8080](https://8020.net/40-8080.html), 1200 mm, calculates to $151.73 including one cut but excluding shipping and extra machining. Its approximately 7.64 kg mass must be included in the moving-gantry checks.

The workbook's Metal quotes sheet includes the exact tubing cuts, stock nesting and other supplier comparisons. US-stock adjustments are explicit: 1-inch panel frames require 346.2 mm inner members; the 25.4 + 7.9375 + 19.05 mm panel stack is 52.3875 mm, giving a nominal unskimmed deck height of 973.1875 mm. Measure actual stock and re-establish the working datum after surfacing.

## Compressor and water system

Your 12 CFM compressor, CV-15HS vacuum generator, existing solenoids and similar straight torch are counted as **owned: $0 new purchase**.

Commercial pneumatic tables use compressed air to displace water upward from a lower chamber, then vent the air so water returns by gravity. [Torchmate documents this arrangement](https://torchmate.com/uploads/manuals/5100-Users-Guide.pdf). It can eliminate the electric refill pump and motorized liquid drain.

The present Rev C reservoir is vented and **must not be pressurized**. The pneumatic option needs a separately engineered chamber with at least 125 L usable return capacity, appropriate pressure/vacuum ratings, reinforcement, cleaning access, restricted air inlet, matched regulation/relief, pressure indication and controlled venting. The overflow arrangement must also be designed for the sealed chamber; it cannot simply copy an open return into the vented tank. The $700 chamber line is an allowance, not a fabricator's offer or a pressure-vessel design.

About 0.65 m lift corresponds to roughly 0.93 psi static head before losses. That is not a regulator or relief setting. Even 1 psi across a 900 × 500 mm flat panel creates about 3.1 kN of force. Pressure protection and chamber construction therefore need actual sizing. Where aluminum plasma cutting is intended, address the manufacturer's guidance on hydrogen accumulation in dual-chamber water tables before selecting this arrangement.

The [documented CONVUM CV-15HS](https://shop.convum.com/products/200100006) is a vacuum generator rated at 100 L/min air consumption at 0.5 MPa, approximately 3.5 CFM at 73 psi. Your manufacturer has not been confirmed. It is potentially useful for small sealed vacuum fixtures, but is not needed for gravity drainage and should not ingest dirty plasma water. Existing solenoid voltage, ports, flow and minimum operating pressure remain unknown.

A third compressor-fed route retains the vented tank and uses an air-operated diaphragm refill pump. [Graco Husky 307 D32966](https://fastoolnow.com/graco-d32966-husky-307-polypropylene-aodd-plastic-pump-w-npt-standard-air-valve/) was observed at $668, before unverified shipping. It replaces the $204.19 electric pump; it is not added alongside it. The component difference is $463.81 before air-control fittings, mounting, freight and media-compatibility checks. No finished third-route total is claimed.

## CNC completion items

The BOM provisions four independent onboard motor channels, dual-Y homing, spindle control, touch-off and a provisional plasma-interface budget. Live height-control firmware is not implemented or verified. It is not a released electrical or fabrication package.

The [Bestarc reference](https://www.amazon.com/dp/B0FH296V6K) explicitly uses high-frequency ignition. Pilot arc does not mean non-HF. Your actual cutter model, start/arc signal connections and arc-voltage interface remain unconfirmed. The existing AG60/SG55-style head alone cannot establish compatibility. The optional [BTC500XP 11GEN](https://www.bestarc.com/products/btc500xp-11gen-cnc-plasma-cutter) is a non-HF comparison, but its 1:1 arc output still requires a correctly designed isolated interface.

Before releasing purchases for fit-specific components, finish the HMS mounting and moment/load checks, motor ratings, head geometry, clamp/locator details, control I/O allocation and water-option drawing. The former Mesa 7I96S/7I84U selections are removed. A completed firmware and plasma-interface plan must precede a CNC/plasma readiness claim.
