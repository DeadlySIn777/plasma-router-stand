# T-slot product and quantity audit

Audit date: 2026-09-25. This is a clarification of the existing Rev E definition, not a geometry revision or an order recommendation.

## What the latest cart fragment establishes

The pasted cart text shows size **1220 mm (48 inches)**, color **silver**, and **Number of Items: 2**. It does not include the product title, ASIN, cross-section, or an unambiguous cart quantity control. The trailing `5` could refer to the order quantity, an item number, or the quantity being challenged; do not infer which meaning the user intended.

For the already selected listing, `Number of Items: 2` means two extrusion bars in each purchased pack. It does not mean that two packs cover the bed.

## Exact product record and contradictory description

The existing selection is [IXGNIJ ASIN B0BXNWK99C](https://www.amazon.com/dp/B0BXNWK99C), recorded as **20100, silver, 1220 mm × 2** in `../../bom/extrusion_amazon.json` and as bed item B01 in `verified-purchases.json`.

That source record already identifies a listing conflict: the title/profile drawing indicate a **20 mm high × 100 mm wide** extrusion, while an Amazon bullet states **20 × 20 × 1220 mm**. The saved drawing `../sources/IXGNIJ-20100-section.jpg` was visually inspected for this audit. Its labeled outside dimensions are clearly **100 × 20 mm**, with five top slots and five bottom slots. It also labels 6.2 mm top/bottom openings and advertises a general ±0.2 mm measurement error. The drawing supports the 20100 design interpretation; the contradictory bullet remains a supplier-description issue and must not silently become a 2020 substitution.

The saved `amazon-B0BXNWK99C.html` is a short Amazon response without usable product details. It is not independent evidence resolving that conflict. The live browser observation and saved product drawing are the recorded evidence. Exact received stock, section tolerances, straightness, and nut fit still need verification before fabrication release.

## Current Rev E cut quantity

| Quantity level | Existing definition |
|---|---:|
| Purchased packs | 5 |
| Bars per pack | 2 |
| Total raw bars | 10 × 1220 mm |
| Finished strips per bar | 3 × 397 mm |
| Total finished strips | 30 |
| Strips per cassette | 5 |
| Removable cassettes | 6 |

One bar uses `3 × 397 + 3 × 3 = 1200 mm`, assuming three 3 mm saw kerfs. A nominal 1220 mm bar therefore leaves **20 mm total** for end squaring and offcut. Across ten bars, the finished length is 11,910 mm, modeled cutting loss is 90 mm, and remaining stock is 200 mm. If the actual bar is precisely 48 inches rather than 1220 mm, its length is 1219.2 mm and the corresponding reserve is 19.2 mm per bar. Either stated length supports this cut plan, subject to actual stock length, squaring allowance, and kerf.

The five-pack count is internally consistent with the current cassette design. It is not evidence that five packs are the only possible bed design.

## Bed size is not machine travel

Each cassette is nominally **500 X × 397 Y mm**, assembled from five 100 mm-wide strips. Two cassette columns with one 3 mm seam make `500 + 3 + 500 = 1003 mm`. Three rows with two 3 mm seams make `397 + 3 + 397 + 3 + 397 = 1197 mm`.

Thus the existing bed is **1003 X × 1197 Y mm**, while nominal machine travel is **800 X × 1000 Y mm**. These are different dimensions. The oversized bed provides surrounding support; full tool access to its perimeter is not promised. Its size is a design choice, not a consequence of the user's nominal travel dimensions alone.

**Four two-packs contain eight 100 mm-wide bars and can supply a simple nominal 800 × 1000 mm deck** by cutting each bar to 1000 mm. That arithmetic does not preserve the current six-cassette layout, support positions, anchor pattern, handling sequence, or internal storage arrangement. Eight bars supply at most 24 of the current 397 mm strips, whereas Rev E uses 30. Reducing the purchase quantity without redesigning those interfaces would leave the present assembly incomplete.

## Scope of any correction

The cart fragment does not establish a numerical error in the existing five-pack calculation. It does establish a need to clarify whether the user's objection concerns **the product section, the number of packs, or the oversized segmented bed layout**. Confirm that distinction before changing CAD or procurement quantity. No CAD, price, or purchase quantity was changed by this audit.

## Concrete illustration omission identified

At the time of inspection, page 2 of `build_concept_current.py` drew one longitudinal center line per 100 mm strip, using `k * 100 + 50`. That shows only five apparent slot lines on a 500 mm-wide cassette. The supplier section actually has **five top slots per 100 mm strip**, centered at **10, 30, 50, 70, and 90 mm**. The 20 mm pitch is supported by the drawing's repeating 6.2 mm opening plus 13.8 mm land; the same centers are explicitly used by `bed_details.py`.

A faithful plan illustration should therefore show **25 slot centerlines per cassette**, at `10 + 20 * k` for `k = 0..24`, and may separately distinguish the four extrusion joints at 100, 200, 300, and 400 mm. Correcting this drawing does not require changing the CAD cross-section, which already models all five top slots per extrusion. The parent task is handling the PDF illustration correction.
