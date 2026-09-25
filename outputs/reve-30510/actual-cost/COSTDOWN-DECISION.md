# Cost reduction decision — 2026-09-24

**The coordinator adopted the cheaper source for the existing MET12 raw blank. Neither the fabricated steel brackets nor VXB rod ends is adopted.** This review changes no CAD and adds no fabrication labor charge. The revised sourced goods subtotal is **$5,734.94**, plus **$75.30** known/advertised shipping, for **$5,810.24 before tax for priced scope only**. This remains an incomplete machine total.

## A reduction that preserves the current geometry

Replace the MET12 BuyMetal 2 × 2 × 12 inch 6061-T6511 square bar ($102.42) with **one [OnlineMetals part 1120, 12 inches, $71.07](https://www.onlinemetals.com/en/buy/aluminum/2-aluminum-square-bar-6061-t6511-extruded/pid/1120)**. The direct product page refreshed on September 24 shows $71.07 each and $71.07 for one. An earlier search result showed $76.06; use the directly refreshed price. Freight and tax remain unquoted. **Goods reduction: $31.35.** This is an equivalent raw-material purchase, independent of motor specifications; it is not a new finished clamp.

The existing machining allocation still fits:

- Two clamp halves: 100 × 45.25 × 40 and 100 × 44.75 × 40 mm. One X drive shoe: 65 × 48 × 19.05 mm.
- Along the bar, 100 + 100 + 65 + three 3 mm saw kerfs + 10 mm total trim = **284 mm**. The seller's [general cut tolerance](https://www.onlinemetals.com/en/tolerances) is ±0.125 inch, giving a minimum 12-inch stock length of **301.625 mm**, or 17.625 mm additional margin.
- Its [extruded square-bar tolerance](https://www.onlinemetals.com/en/aluminum-tolerances) for this size is ±0.024 inch. Minimum cross section is 50.1904 mm square, above the widest required 48 mm section. Finish machining and incoming material inspection remain necessary.
- Same alloy, temper and production form as the current stock route. Quantity is one piece; no bulk discount is assumed. Update the cost source, not the finished-part drawings or material properties.

A [222 Steel offer through Walmart](https://www.walmart.com/ip/14640555631) advertises the same nominal stock for $34.57 and free shipping. Its web result used Sacramento 95829, and the browser destination check encountered a CAPTCHA. It remains an unadopted candidate; no Alto delivered saving is asserted.

## Fabricated steel gantry feet and three link supports

**Decision: suitable redesign direction, not a purchase-ready substitution.** The proposed $387.17 is $296.31 MET09 + $114.36 MET10 − $23.50 additional steel. It requires replacing **both feet and all three supports**. Changing only the feet leaves Y supports allocated to MET09, so that whole billet cannot simply be removed.

Exact geometry is in [motion_details.py](<C:/Users/Gluis/OneDrive/Documents/ChatGPT/New project/plasma_router_stand/output/release-review/RevE-ENGINEERING/motion_details.py:389>): gantry feet start at line 389; Y supports at line 415; X support at line 501. The current parts are integral aluminum shapes. Proposed plate sizes, locations and candidate nests are recorded in `metal-findings.json`, `unadopted_plate_bracket_option`.

Required before adoption: specify weld joints and weld access; preserve the 12.7 mm foot web and existing 9.3 mm screw engagement; finish contact faces and hole locations after welding; detail weld clearance at shoe windows and bolt seats; revise the plate nest for all support parts; update moving mass, joint/stiffness screening, motion clearance and swap checks. Current member calculations do not qualify those new welded joints. The roughly 3.1 kg added moving mass is preliminary. Motor data are needed for final motion performance, but missing motor data do not prevent drawing the weldments and doing these geometric checks now. Additional shipping, consumables and any extra plate are not included in the proposed saving.

## VXB rod-end packs

**Decision: not compatible with the frozen clevises; a bounded local redesign is possible.** [Two VXB Kit215 packs](https://vxb.com/products/4-male-rod-end-6mm-pos6-2-right-and-2-left-ha) cost $39.98 with advertised free US shipping. They supply four RH and four LH ends; install three of each, keep two spares. The [POS6 table](https://vxb.com/products/pos6-male-rod-end-6mm-right-hand-bearing) gives a 9 mm ball width. Current SKF geometry uses a 6 mm ball in a 7 mm clevis gap with two 0.5 mm shims.

`motion_details.py` lines 291–352 defines all six clevises, pins, shims, rod ends and the three 80 mm eye-center links. Widening the gap to 10 mm while retaining both 6 mm ears changes the shoulder stack from 20 to 23 mm. A 25 mm shoulder needs a defined 2 mm external spacer; the existing 20 mm pin is unsuitable. Reposition ears and shims, verify the pin/thread/nut stack, preserve mounting-hole clearance and 80 mm centers, and check coupler engagement and articulation through travel. Regenerate affected CAD and clearance checks. Use VXB's own ratings and check play/wear; the SKF qualification cannot transfer automatically. These local geometric edits do not inherently require waiting for motor data, but they have not been done in the released review model.

**Do not subtract $246.79 from the current priced subtotal.** That comparison uses $286.77 for all six SKF ends, including a $147.96 RH benchmark that is currently excluded from the priced basket. Only $138.81 for three SKF LH ends is presently priced. If the VXB redesign is later accepted, it replaces that priced line with $39.98 and resolves the previously unpriced RH requirement: **$98.83 reduction to today's priced goods**, before revised pins and spacers. The $246.79 figure is only a comparison against the combined offer/benchmark set, not a verified delivered saving.

Review basis: `metal-findings.json`, `hardware-findings.json`, `audit-data.json`, `MOTION-VERIFICATION.md`, `MECHANICAL-ENGINEERING.md`, `strength-screen.py`, and the source geometry above. No orders, supplier messages or CAD edits were made by this review.
