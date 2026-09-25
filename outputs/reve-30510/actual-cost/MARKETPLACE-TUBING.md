# Facebook Marketplace tubing — 24 September 2026

**A real Facebook listing offers 2 × 2 × 24 ft tubing at $115 per piece. Five usable bars fit the existing chassis blank lengths: $575 in tube goods.** That is **$355.90 below** the six-bar $930.90 retail reference, before tax, pickup and material qualification. It has not been substituted into the build total.

## Best observed lead

[Square Steel Tubing 2x2x24ft x 1/8 inch walls — Sylvania, GA](https://www.facebook.com/marketplace/item/1367277908682890/)

The live page displayed **$115 per piece**, **In stock**, **Condition New**, and **Door pickup**. Its description says 28 pieces remain and describes weathered tube with a brown rusted surface and green interior coating. These are seller claims; stock was not confirmed with the seller.

The listing is for **24 ft lengths**, not 20 ft. Its advertised wall is **1/8 inch**, while the existing model calls for **0.120 inch**. Actual wall, material grade, straightness, usable length and the coating require qualification before purchase or substitution. Sylvania is outside the intended nearby search area, so transport may erase some of the goods saving. No delivery price is stated.

## Five-bar fit calculation

The existing 36 tube blanks were repacked without changing any part length. Every part identity and copy appears exactly once. Each 24 ft bar is 7,315.2 mm; the calculation reserves **10 mm total end trim per bar** plus **3 mm kerf for each blank**.

| Bar | Blank lengths in mm | Remaining offcut |
|---|---|---:|
| 1 | 1450; 949.2 × 4; 648.8 × 3 | 88.0 mm |
| 2 | 1450; 1048.4 × 2; 1036.4; 1016; 949.2; 648.8 | 87.0 mm |
| 3 | 1450; 1048.4 × 2; 1036.4; 1016; 949.2; 648.8 | 87.0 mm |
| 4 | 1450; 1048.4; 1016 × 4; 648.8 | 73.0 mm |
| 5 | 1048.4 × 2; 1016.4 × 3; 1016 × 2 | 106.2 mm |

Net blank length is **35,976.8 mm**. Combined unused length after all kerfs and trim is **441.2 mm**. This proves blank-length feasibility only, not the suitability of a weathered seller lot. Do not cut the bars in half for transport without checking a revised cut sequence.

The complete part-to-bar allocation and source-file SHA-256 are in `marketplace-24ft-cut-proof.json`; `repack_24ft_tube.py` reproduces the calculation.

## Nearby short-stock lead

[Jefferson — 2x2 square steel tubing, $6 each](https://www.facebook.com/marketplace/item/1721520526249054/) displayed **In stock** and **Used - Like New**. The description states a **five-piece minimum ($30)** and a **31.5 inch length (800.1 mm)**. Wall and grade are not given.

These pieces are too short for the 949.2–1,450 mm frame blanks. They could only be considered for the 648.8 mm members or accessories after specification checks and a new mixed-stock cutting plan; no structural splices are assumed. It is a real inexpensive local short-stock lead, not a replacement for the entire frame lot.

## Thicker-wall alternative, not adopted

[Temple — Square Tubing](https://www.facebook.com/marketplace/item/1586230069744711/) has a **$1 placeholder headline**. The description actually offers two 2 × 2 × 1/4 inch wall, 20 ft pieces at **$110 each**, plus one 13 ft piece at **$70**. The page says **Used - Fair**, listed four weeks ago.

The wall is 0.250 inch rather than the modeled 0.120 inch, so this would add weight and require fit/load checks. The listed lot is insufficient for the full frame. No price or substitution has been adopted.

## Rejected nearby listing

[Clayton 2 × 4 inch tube, quarter-inch wall](https://www.facebook.com/marketplace/item/919614894399066/) advertises 20 ft pieces, two remaining. Its **$20 is per foot**, so a full piece is **$400**. It is the wrong section for the current chassis and is not a $20 tube bargain.

## Search and verification scope

Facebook was searched in a normal browser after dismissing the login overlay. Alto, GA and a 40-mile radius were selected, but Facebook surfaced wider-area results; the page location takes precedence over the search radius. Public web searches and web-fetch alone had failed to expose usable listings. Browser inspection found the lead above.

No seller was contacted, no message was sent, and no order was placed. Prices are observed advertisements, not delivered quotes. Existing CAD geometry and the priced build subtotal remain unchanged by this report.
