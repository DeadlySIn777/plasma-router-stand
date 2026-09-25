# CNC / plasma actual-price audit

**Recorded priced scope: $5,734.94 goods + $75.30 known/advertised shipping = $5,810.24 USD before tax.**

**The complete delivered build price is still unknown. This is not a purchase or manufacturing release.** The remaining required items are not included as zero-dollar purchases. The earlier $7,663.82 estimate is superseded; it contained allowances, omitted stock details and an arbitrary shipping reserve.

The owner performs fabrication, machining, cutting and finishing: outside-shop labor is **$0**. This audit does not assume unconfirmed tools, stock or consumables are already owned. No orders or supplier messages were sent. Fusion remains unopened.

## Prices that can be traced to offers

| Priced portion | Goods, before tax |
|---|---:|
| Motion | $2,203.13 |
| Router bed | $469.23 |
| Router head | $309.99 |
| Controls | $460.67 |
| Water controls | $424.74 |
| Chassis | $1,392.71 |
| Standard hardware | $216.90 |
| Controls and water wiring | $257.57 |

The current workbook contains **83 priced lines**, **43 remaining scope entries** and a vendor-level shipping register. Every price is linked to a product or supplier. Line quantities are rounded to cents; seller checkout can differ by a cent on fractional-cent fasteners.

Amazon items total **$2,204.99**, with advertised free delivery to ZIP 30510 under the recorded order conditions. This includes two 1,000 mm Y modules, one 800 mm X module, the 100 mm Z, the two HGR20 rail kits, five extrusion packs, spindle kit, power supplies, cabinet, cable chains, CB1 and listed Amazon water components. These are source prices, not proof that all mounting and electrical interfaces are finished.

The [80/20 beam](https://8020.net/40-8080.html) and [16 matching M8 nuts](https://8020.net/40-3915.html) were configured together in a ZIP-30510 cart: **$193.01 goods + $61.30 UPS Ground + $17.80 estimated tax = $272.11**. The temporary cart was cleared after recording the estimate. This tax amount applies only to that cart, not to all suppliers.

Nutty hardware is combined into one order above its $100 advertised free-shipping threshold. No duplicate delivery charge is added for each fastener row. Other blank freight cells remain unknown.

## Corrections to the old estimate

- Recorded the owner's 12 x 12 inch aluminum pieces, provisionally one at 1/2 inch and one at 3/8 inch. The 1/2 inch piece geometrically fits the Z carrier and smaller pieces. Qualifying its alloy and usable finished thickness can avoid MET08 ($58.74), giving $5,751.50 for the current incomplete priced scope. No credit is applied before qualification, and no duplicate offcut savings are counted. See [owned aluminum allocation](OWNED-ALUMINUM-FIT.md).
- The $930.90 square-tube line is a high retail reference, not a lowest-price buying recommendation. Bobco posts $585.00 for six matching 20-foot A500 Grade B bars, but advertises Los Angeles pickup; Georgia delivery is unquoted. Looper's and YAGI comparisons have further specification/availability limits. Nearby SteelMart Gainesville and Sabel Winder require quotations. See [tube comparisons](TUBE-PRICE-COMPARISON.md).
- A [Sylvania Marketplace listing](https://www.facebook.com/marketplace/item/1367277908682890/) advertises 24-foot 2 x 2 tubing for $115 each. The alternate cut proof fits all 36 blanks into five bars, giving $575 goods and a $355.90 difference from the retail reference before pickup/tax/qualification. No budget substitution is adopted until actual wall/grade/condition and collection are checked. See [Marketplace findings](MARKETPLACE-TUBING.md).
- Removed the unsupported $200 decorative-skin allowance: no separate appearance panels existed in the current CAD.
- Retained six full 20-foot chassis tubes because the cut plan needs them. One bar has no surplus beyond its modeled kerfs and trim; do not assume undersize or damaged stock will fit.
- Kept two 4 × 8 sheets for the .120-inch water assembly. The stale third nesting DXF is excluded from the current package.
- Replaced the $150 adapter-stock allowance with explicit raw-stock purchases. The unchanged billet geometry requires $813.33 of sourced aluminum stock before freight. The old allowance understated this cost. An equivalent OnlineMetals 2 x 2 x 12 inch blank replaces the prior BuyMetal source and reduces goods cost by $31.35 without a geometry change.
- Counted fabricated plugs, supports and clamps as raw stock plus owner work. No shop labor is added a second time.
- Kept price evidence separate from compatibility. Backorders, timer contact checks, hose restrictions and unresolved interfaces are visible rather than being assumed complete.

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
