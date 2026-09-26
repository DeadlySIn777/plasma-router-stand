# CNC / plasma actual-price audit

**Recorded priced scope: $5,262.15 goods + $86.25 known/advertised shipping = $5,348.40 USD before tax.**

**The complete delivered build price is still unknown. This is not a purchase or manufacturing release.** The remaining required items are not included as zero-dollar purchases. The earlier $7,663.82 estimate is superseded; it contained allowances, omitted stock details and an arbitrary shipping reserve.

The owner performs fabrication, machining, cutting and finishing: outside-shop labor is **$0**. This audit does not assume unconfirmed tools, stock or consumables are already owned. No orders or supplier messages were sent. Fusion remains unopened.

## Prices that can be traced to offers

| Priced portion | Goods, before tax |
|---|---:|
| Motion | $2,203.13 |
| Router bed | $399.95 |
| Router head | $309.99 |
| Controls | $268.71 |
| Water controls | $424.74 |
| Chassis | $1,261.46 |
| Standard hardware | $141.55 |
| Controls and water wiring | $252.62 |

The current register contains **75 priced lines**, **49 remaining scope entries** and a vendor-level shipping register. Every price is linked to a product or supplier. Line quantities are rounded to cents; seller checkout can differ by a cent on fractional-cent fasteners.

Amazon items total **$2,172.00**, with advertised free delivery to ZIP 30510 under the recorded order conditions. This includes two 1,000 mm Y modules, one 800 mm X module, the 100 mm Z, the two HGR20 rail kits, five extrusion packs, spindle kit, power supplies, cabinet, cable chains and listed Amazon water components. These are source prices, not proof that all mounting and electrical interfaces are finished.

The [80/20 beam](https://8020.net/40-8080.html) and [16 matching M8 nuts](https://8020.net/40-3915.html) were configured together in a ZIP-30510 cart: **$193.01 goods + $61.30 UPS Ground + $17.80 estimated tax = $272.11**. The temporary cart was cleared after recording the estimate. This tax amount applies only to that cart, not to all suppliers.

Nutty hardware is combined into one order of $90.37, below its $100 free-shipping threshold, so the $10.95 flat rate is included; adding the unpriced Rev G fasteners to this order may remove it. No duplicate delivery charge is added for each fastener row. Other blank freight cells remain unknown.

**Ordered by the owner:** M01 KHMOS HMS40 X module, 800 mm stroke, ordered 2026-09-26 (owner-reported; quantity to confirm); M02 KHMOS HMS40 Y module, 1000 mm stroke, ordered 2026-09-26 (owner-reported; quantity to confirm); M03 RATTMMOTOR ZBX80 Z module, 100 mm stroke, ordered 2026-09-26 (owner-reported; quantity to confirm). Listed prices stay in this register until the price paid is recorded. See the [drive-module receiving check](../../../output/receiving/MOTION-MODULES.md).

## Corrections to the old estimate

- Recorded the owner's 12 x 12 inch aluminum pieces, provisionally one at 1/2 inch and one at 3/8 inch. The 1/2 inch piece geometrically fits the Z carrier and smaller pieces. Qualifying its alloy and usable finished thickness can avoid MET08 ($58.74), giving $5,289.66 for the current incomplete priced scope. No credit is applied before qualification, and no duplicate offcut savings are counted. See [owned aluminum allocation](OWNED-ALUMINUM-FIT.md).
- The $775.75 square-tube line is a high retail reference, not a lowest-price buying recommendation. Bobco posts $487.50 for 5 matching 20-foot A500 Grade B bars, but advertises Los Angeles pickup; Georgia delivery is unquoted. Looper's and YAGI comparisons have further specification/availability limits. Nearby SteelMart Gainesville and Sabel Winder require quotations. See [tube comparisons](TUBE-PRICE-COMPARISON.md).
- A [Sylvania Marketplace listing](https://www.facebook.com/marketplace/item/1367277908682890/) advertises 24-foot 2 x 2 tubing for $115 each. Its recorded cut proof (five bars, $575) was made for the Rev E 36-blank schedule and has not been redone for the Rev G 30 blanks. No budget substitution is adopted until the cut proof, actual wall/grade/condition and collection are checked. See [Marketplace findings](MARKETPLACE-TUBING.md).
- Removed the unsupported $200 decorative-skin allowance: no separate appearance panels existed in the current CAD.
- Buy 5 full 20-foot chassis tubes for the 30 Rev G blanks in RevG-CAD/tube-cut-plan.json. The smallest bar remainder beyond modeled kerfs and trim is 6 mm; do not assume undersize or damaged stock will fit.
- Kept two 4 × 8 sheets for the .120-inch water assembly. The stale third nesting DXF is excluded from the current package.
- Replaced the $150 adapter-stock allowance with explicit raw-stock purchases. The unchanged billet geometry requires $813.33 of sourced aluminum stock before freight. The old allowance understated this cost. An equivalent OnlineMetals 2 x 2 x 12 inch blank replaces the prior BuyMetal source and reduces goods cost by $31.35 without a geometry change.
- Counted fabricated plugs, supports and clamps as raw stock plus owner work. No shop labor is added a second time.
- Kept price evidence separate from compatibility. Backorders, timer contact checks, hose restrictions and unresolved interfaces are visible rather than being assumed complete.

## Rev G reconciliation, 26 September 2026

Quantities were reconciled with the Rev G cut list (`output/release-review/RevG-CAD/cutlist.json`) and the owner's controller decision. 8 offers are no longer priced and are kept as dated evidence in `audit-data.json` (`superseded_offers`): E19 $32.99, E07 $129.99, E20 $28.98, MET06 $69.28, HW-N2 $12.36, HW-W1 $39.60, HW-N16 $1.44, CA-10 $4.95. The controller items went because the owner chose BTT Rodent + grblHAL on 26 September 2026 (the owner already owns a Kraken); the Rodent board itself is unpriced (CA-RODENT). MET01 is five 20 ft tubes (30 Rev G blanks), MET02 three 8 ft bars (the controls cage raised the 1 x 1 tube list to 7,730 mm), square nuts 96, spoilboard screws 25 and M8x80 drawdowns 10 (Nutty minimums).

`check_revg_stock_fit.py` packs the actual Rev G flat parts onto each registered sheet and plate size (`revg-stock-fit.json`). Every existing row covers its parts except the 6 mm plate, where two tool cradles do not fit; the 3/4 in MDF spoilboards now need only a half sheet. Two thicknesses had no row at all: 2 mm steel rack guides and 3/8 in aluminum panel ties. Those, the extra 6 mm plate, the sleeve round bar and the 30 x 30 x 3 rack-fork tube are listed as remaining scope, as are the Rev G screws, washers and locator pins without an offer. The lower subtotal is therefore NOT a cheaper Rev G build.

**The Excel workbook has not been regenerated.** `build_budget.mjs` needs the private `@oai/artifact-tool` runtime, which is not in this repository. Until it is rebuilt, `budget-data.json`, `audit-data.json` and this page are current; the workbook still shows Rev E quantities.

## Cost reductions requiring an engineering revision

Fabricated steel gantry feet and three link brackets could avoid large billets, with a preliminary goods saving of $387.17 before changed stock, shipping and consumables. This is not applied to the current subtotal: welds, post-weld datum finishing, clearances and the roughly 3.1 kg moving-mass increase still need checking.

The [VXB rod-end packs](https://vxb.com/products/4-male-rod-end-6mm-pos6-2-right-and-2-left-ha) are $39.98 for two packs with advertised US shipping, compared with $286.77 in SKF offers/benchmark prices. Their 9 mm ball width does not fit the current 7 mm clevis gap. The $246.79 comparison includes a $147.96 right-hand SKF benchmark already excluded from the priced subtotal. Against that subtotal, the possible change is $98.83 before changed pins/spacers, while also resolving the unpriced right-hand ends. Neither saving is credited before changing and checking the clevises, pins and shims.

The included spindle-kit clamp may reduce custom clamp work only after its actual hole pattern, envelope and load path are established. No credit is assumed from its mere presence in the kit.

## What prevents a real final total and CAD/CAM release

1. **Supplier dimensions and component selection:** the HMS40 base interface, rail hole pattern, Z mounting dimensions and retention, actual torch envelope, isolated controls and several finishing details remain unresolved. The existing cutter is unidentified; an AG-60 torch listing does not establish the cutter starting circuit or CNC terminals.
2. **Actual metal and delivery quotations:** remaining sheets, round/hex stock, gasket material, freight and taxes lack a delivered quote. The prepared [SteelMart material quote request](STEELMART-QUOTE-REQUEST.md) has not been sent. Supplier contact requires the owner's authorization and reply contact details.
3. **Budget-oriented design correction:** the current billet-heavy design and multiple exact metric sheet thicknesses should be simplified before purchasing. These are drawing and joint-design changes, not numerical discounts. Full cabinet service access, tool clearance and final process-specific CAM also remain open.

The successful CAD solid/intersection checks and firmware compilation do not close those missing interfaces. Physical commissioning follows a completed design; it cannot substitute for the missing pre-order drawings.

## Audit files

- [Metal quantities, stock sources and unsent RFQ](METAL-AUDIT.md)
- [Prepared SteelMart quotation request — not sent](STEELMART-QUOTE-REQUEST.md)
- [Cost-reduction decisions and stock fit proof](COSTDOWN-DECISION.md)
- [Chassis cost breakdown and owned aluminum](CHASSIS-COST-EXPLAINED.md)
- [Owned aluminum fit and allocation](OWNED-ALUMINUM-FIT.md)
- [Square-tube price comparisons and fulfillment limits](TUBE-PRICE-COMPARISON.md)
- [Georgia supplier quote candidates](TUBE-SUPPLIERS-GEORGIA.md)
- [Verified Marketplace listing details and alternate cutting plan](MARKETPLACE-TUBING.md)
- [Mechanical hardware and conditional alternatives](HARDWARE-AUDIT.md)
- [Controls and plumbing offers](CONTROLS-AUDIT.md)
- [Current machine package status](../../../output/release-review/RevE-ENGINEERING/PACKAGE-STATUS.md)

Price evidence recorded September 24, 2026. Sales tax, possible tariffs, unpriced required scope, unquoted freight, any unowned extraction/air treatment, replacement cutter/torch, fabrication tooling and paid software are outside the priced subtotal.
