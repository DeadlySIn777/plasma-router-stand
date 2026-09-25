# Revision C metal and material takeoff — 24 September 2026

Basis: `output/bed-system/design-parameters.json`, the Rev C material table in `bed_system_pages.py`, and Rev C scene geometry in `build_bed_system.py`. Chassis 1150 × 1450; rail-support height 1050; four paired bridge beams; six 497 × 397 panels. USD; destination Alto, Georgia 30510. No orders or supplier messages sent. Prices below are public observations, **not delivered quotations**. Sales tax, freight, cutting, machining and fabrication remain additional unless stated.

The main purchasing recommendation is to request the exact cut list from **SteelMart Gainesville**, and ask **Metal Supermarkets Buford** or **Cherokee Steel** for metric plate and tube alternatives. Amazon was searched first for 8080 extrusion and the large aluminum plates; this research did not obtain a verifiable Amazon price for an exact 1200 mm standard 8080 or a 497 × 397 × 8 mm plate. Small 12-inch Amazon plates cannot yield the required panel blanks.

## Exact 2-inch tube takeoff

Specify weldable carbon steel square tube **2 × 2 × 0.120 inch**, not 2 × 2 × 0.083. Request ASTM A500 Grade B/C or the fabricator's approved equivalent and material identification. A500/A513 retail descriptions can require confirming the actually supplied specification.

| Assembly | Qty | Cut length mm | Net length mm |
|---|---:|---:|---:|
| Top Y-support tubes | 2 | 1450 | 2900 |
| Fixed receiver ledgers | 2 | 1450 | 2900 |
| Six legs | 6 | 949.2 | 5695.2 |
| Lower side ties | 4 | 648.8 | 2595.2 |
| End ties | 4 | 1048.4 | 4193.6 |
| **Stationary chassis subtotal** | **18** | | **18284** |
| Fixed pan-bearer tube blanks | 3 | 1032.4 nominal | 3097.2 |
| Removable bridge tube blanks | 8 | 1032 | 8256 |
| **Total** | **29** | | **29637.2 mm / 97.235 ft** |

Five full **20-foot / 6096 mm bars** suffice with the following verified nesting. The calculation includes 3 mm kerf per piece and 10 mm total trim allowance per bar. Confirm stock is full usable length and the fabricator's actual saw kerf before cutting; increase allowances if the welder requires rough blanks for final facing.

| 20-foot bar | Cuts, mm | Offcut after stated kerf/trim |
|---|---|---:|
| 1 | 1450 × 4 | 274.0 mm |
| 2 | 1048.4 × 4; 1032.4; 648.8 | 193.2 mm |
| 3 | 1032.4 × 2; 1032 × 2; 949.2 × 2 | 40.8 mm |
| 4 | 1032 × 4; 949.2 × 2 | 41.6 mm |
| 5 | 1032 × 2; 949.2 × 2; 648.8 × 3 | 156.2 mm |

Purchased 30.480 m; finished pieces 29.6372 m; utilization **97.23%**. Offcuts 705.8 mm, kerf 87 mm, trim 50 mm. Do not first cut every stock bar into equal 10-foot halves: that changes the nesting and can increase purchases. Have the supplier cut the actual parts or transport lengths that preserve the nesting. There is no spare full-length tube in this quantity.

A 12-foot alternative needs **9 × 3657.6 mm**, or 32.9184 m purchased, 90.03% utilization. The repeatable calculation and every cut are in `cut_stock_check.py` and `cut_stock_check.json`.

## Remaining takeoff

| Item | Rev C requirement | Purchase / fabrication basis |
|---|---|---|
| Panel frame tube | 25 × 25 × 2 mm carbon steel; 12 × 497 and 18 × 347 mm | Net **12.210 m**, 30 cuts. Obtain cut parts or **2 × 6 m + 1 × 1 m**. Two 20-foot bars are 18 mm short even before kerf. Three full 6 m bars work but leave a large reusable offcut. |
| Chassis diagonal braces | 30 × 30 × 3 mm angle; five braces | Rev C centerline lengths: 2 × 907.331; 2 × 904.060; 1 × 1206.493 mm; total **4.8293 m**. Buy 1 × 6 m, or 1 × 20 ft. These are centerline measurements; final saw lengths and miters follow attachment detail. |
| Rail cap/mounting strips | 2 × 1450 × 100 × 8 mm steel | Net area 0.290 m²; approximately **18.21 kg**. Quote two cut blanks with straightness and final datum machining/shimming specified. Do not expect hot-rolled flats to establish a precision rail plane without finishing. |
| Removable beam end diaphragms | 8 × 101.6 × 50.8 × 6 mm steel | Two per paired beam; end faces plus tube blanks give 1044 mm overall. Quote laser/waterjet or saw-cut blanks; weld distortion/facing allowance remains shop detail. |
| Pan-bearer end plates | 6 plates, 8 mm steel | Two per bearer. Nominal 1032.4 tube + two 8 mm plates =1048.4 span before fit clearance. Plate outline/bolt details remain to be released; 50.8-square footprints are only the tube envelope. |
| Bridge riser feet | 8 feet, finished 30 mm rise | Rendering envelope 40 × 90 × 30 per foot. Final hollow/fabricated vs solid construction, contact pads and screw hardware remain a fabrication quote. Do not buy eight solid blocks solely because the renderer uses boxes. |
| Foot/base plates | 6 × 80 × 80 × 12 mm shown | Approx. 3.62 kg steel before holes; actual leveling-foot hardware/interface controls final plate design. |
| Fixed water pan | 920 × 1200 × 100 mm outside; 3 mm steel; approximately 1% floor slope to sump | Quote fabricated pan with accessible cleanout, welded fittings, overflow and leak test. Floor projection 920 × 1200 plus sidewall allowance totals roughly **1.514 m² / 35.7 kg** of 3 mm steel, before sump/cleats. Flat rendering is not a brake pattern. Floor developed length and trapezoidal sidewalls depend on drainage direction and joint design. |
| Plasma slats | 19 × 880 × 75 × 3 mm steel | Net **1.254 m²**, approximately **29.53 kg**. Quote sheared/laser-cut strips. One 4 × 8 ft sheet yields the slats with ample usable remainder; final slots/comb supports remain additional. |
| Pan plus slat sheet stock | About 2.768 m² net, excluding sump/cleats | Conservatively **2 × 4 × 8 ft sheets** of specified 3 mm steel for separate straightforward nesting. Do not claim one sheet fits just from area. Shop nesting may combine remnants with other 3 mm parts. US 11-gauge/.120 sheet is a thickness substitution requiring measured geometry adjustment. |
| Aluminum subplates | 6 × 497 × 397 × 8 mm | **1.183854 m²**, approx. **25.57 kg**. Six exact finished pieces, or a 1005 × 1205 minimum rough nesting envelope before supplier edge allowance. A 48 × 48 in sheet fits the six pieces in a two-by-three array with 3 mm kerfs. Specify alloy/temper and flatness; Rev C only says aluminum and does not release a plate flatness tolerance. |
| Replaceable MDF | 6 × 497 × 397 × 19 mm | One nominal 4 × 8 ft sheet easily yields six plus spare panels. Actual 3/4-inch MDF is 19.05 mm; measure and surface the assembled deck. Exact datum becomes a commissioning measurement. |
| Gantry extrusion | 1 × 1200 mm standard 8080 aluminum | Use a documented standard section. Profile mass and bending/torsional properties are needed for Y carriage and moment checks. Do not substitute a light extrusion by external size alone. |
| Light skins and front covers | 1.5–2 mm flanged aluminum; two approx.503 × 566 covers and four approx.615 × 498 side skins | Front/side visible projected area about **1.794 m²** before flanges and cutouts. A 4 × 8 ft sheet has sufficient area for these faces and modest returns, but final nesting depends on flange geometry. Cabinet interior liner/shelf, rack structure and wet-zone shields are additional. Use fabricated quote until unfolded blanks/supports exist. **Ignore the exaggerated 4–5 mm cabinetry thicknesses in the schematic render.** |
| Cabinet/panel/beam rack supports | Full-width 1005 × 550 × 680 mm clear storage | Separate load-bearing rack crossmembers, padded supports and attachments need detailing/quote. Aluminum skins carry no stored-bed load. |
| Vented reservoir | 900 × 500 × 350 mm internal, 157.5 L gross; 125 L usable return capacity | Quote material suitable for the liquid/additive, baffles, sludge cleanout, cover, vent, pickup, overflow and support shelf. Wall thickness/material and final external envelope are not released; **not included in pan sheet allowance**. |
| Small interface materials | Motor/gantry/head adapters, gussets, receiver seats, pads, caps, fill/drain bungs, clamps, locating inserts, fasteners | Not all dimensions released. Obtain a separate allowance/quote rather than claiming omitted pieces cost zero. |
| Dry sand | Approx. 58 kg in the stationary chassis only | Three 50 lb bags =68.0 kg purchased if that retail pack is chosen. Actual fill volume depends on ports/closed compartments. Keep sand out of removable beams and deck frames. |

## Public price observations and regional options

All observations accessed 24 September 2026. Search-index prices and live-page prices sometimes differed; the latest directly readable page is used where available. Stock labels are not confirmation of allocation or delivery to 30510.

| Source and item | Observed price USD | Application and delivery status |
|---|---:|---|
| [SteelMart Gainesville](https://steelmartatlanta.com/steelmart-gainesville-ga/) | Quote required | 455 Industrial Blvd, Gainesville GA30501; **770-297-6675**. Will-call/counter sales, cutting and delivery offered. Current stock, all cutting fees and Alto delivery cost require a quote. Regional first choice for chassis stock and cut sheet. |
| [Metal Supermarkets Buford](https://www.metalsupermarkets.com/location/buford/) | Quote required | 4908 Golden Parkway, Suite400, Buford GA30518. Cut-to-size service; listed delivery area includes Cornelia. Delivery to Alto, exact stock and charge remain unconfirmed. |
| [Cherokee Steel](https://cherokeesteel.com/) | Quote required | 196 Leroy Anderson Rd, Monroe GA30655; **770-207-4621**. Carbon steel/aluminum, bandsaw/plate saw/waterjet services. Ask for exact metric and finished plate alternatives; shipping not quoted. |
| [Looper's 2 × 2 11-ga tube](https://www.loopersmetalworks.com/metal-products/) | **$4.03/ft; $80.60 per20ft; $403 forfive** | Published stock-price list dated9/17/26; $3/cut and possible partial-length uplift. **Oklahoma benchmark**, not local quote. Confirm actual wall; no Alto freight quote. |
| [Bobco exact2 × 2 × .120 tube](https://www.bobcometal.com/hot-rolled-steel-square-tube-2-inch-x-0-12.html) | **$97.50 per20ft; $487.50 forfive** | Price visible in indexed supplier listing; direct page returned403. A500B listing, Los Angeles pickup. Georgia shipment/freight unverified; use as benchmark, not recommended distant freight order. |
| [Online Metals exact2 × 2 × .120, part10343](https://www.onlinemetals.com/en/buy/carbon-steel/2-x-0-12-carbon-steel-square-tube-a500-a513-hot-rolled/pid/10343) | **$202.30 per20ft; $1011.50 forfive**; **$100.72 per12ft; $906.48 fornine** | Directly readable latest product page. Cuts and freight to30510 additional/unquoted. A500/A513 designation; confirm supplied grade. Earlier indexed prices were lower and were superseded. |
| [Parker Steel metric catalog](https://www.metricmetal.com/wp-content/uploads/2024/05/RG-201123-FULL-CATALOG-COMPRESSED.pdf) | Quote required | US metric supplier catalog lists **25 × 25 × 2** square tube,1.442kg/m. Confirm current allocation, length options, cuts and freight. Exact-dimensional route for panel frames. |
| [Online Metals / A-Z Metals1 ×1 ×.083 tube](https://www.onlinemetals.com/en/buy/carbon-steel/1-inch-x-083-inch-carbon-steel-square-tube-a500-a513/pid/mp-00064364) | **$15.58 per60-inch piece; $140.22 fornine** | Page says2-business-day ship lead from Mesa AZ; arrival/cost to30510 unconfirmed. **Not exact25 ×25 ×2:** section25.4,wall2.1082. Nine5ft pieces nest the RevC lengths, but using them requires innercuts346.2 instead of347 and revising panel stack+.4mm; price comparison only. |
| [Steel Supply LP1¼ ×1¼ ×⅛ angle](https://www.steelsupplylp.com/sku/100002) | **$24.19 per20ft** | Near-size31.75 ×31.75 ×3.175 benchmark for30 ×30 ×3, not automatic substitute. Page marks freight shipment; stock messaging is ambiguous. No delivery amount. |
| [Looper's11-ga4 ×8 sheet](https://www.loopersmetalworks.com/metal-products/) | **$173.60 each; $347.20 fortwo** | Oklahoma published raw-sheet benchmark; shear fee listed separately. Actual3mm vs11gauge must be resolved. Fabricated pan, slope, drain fittings, leak test and slat cutting additional. |
| [Online Metals3 ×⅛ flat, part10007](https://www.onlinemetals.com/en/buy/carbon-steel/0-125-x-3-carbon-steel-rectangle-bar-commercial-quality-hot-rolled/pid/10007) | **$18.14 per72-inch; $181.40 forten** | Ten6ft bars yield20 ×880 slats with3mm kerfs and one spare. This is76.2mm high ×3.175 thick stock, requiring trimming/clearance updates for RevC75 ×3. Freight unquoted. Alternative to sheet-cut slats, not additive to the two-sheet pan/slat allowance. |
| [Online Metals exact8mm5754, part29508](https://www.onlinemetals.com/en/buy/aluminum/8mm-aluminum-plate-grade-5754/pid/29508) | **$902.42 per24 ×36-inch blank; $2707.26 forthree** | Three blanks yield two panels each. Exact thickness but grade/flatness needs acceptance. Public high-cost comparison; request cut-to-size local material before paying this. Freight unquoted. |
| [Online Metals5/16-inch6061-T651, part14480](https://www.onlinemetals.com/en/buy/aluminum/0-3125-aluminum-plate-6061-t651/pid/14480) | **$759.54 per48 ×48-inch sheet** | Latest directly readable price; earlier indexed$915.25 superseded. One sheet yields six panels; saw cutting/finished edges extra. **7.9375mm**, so it is0.0625mm thinner than RevC8mm and not a silent exact replacement. Lower overall height can be captured in datum setup or shim design after approval of material/tolerances. Freight unquoted. |
| [80/20 standard40-8080](https://8020.net/40-8080.html) | **$0.1231/mm +$4.01 cut = $151.73 for1200mm** | Manufacturer lists6063-T6, Ix=Iy171.6341cm⁴,0.3563lb/in → about7.64kg at1200mm. Cut-only calculation; tapping/other machining, tax and shipping extra. No delivery date/quote to30510. |
| [BCI .080-inch5052-H32 aluminum48 ×96](https://bciimage.com/product/aluminium-sheet-080-5052-h32-0-08-x-48-x-96/) | **$510 per4 ×8 sheet** |2.032mm near-size skin stock. Supplier explicitly requires an extra quote for oversized shipment; **do not call this free delivery**. Stock/ETA confirmation offered. Flange fabrication and finish additional. |
| [Looper's .080-inch5052-H32 aluminum4 ×10](https://www.loopersmetalworks.com/metal-products/) | **$254.64 per4 ×10 sheet** | Lower regional raw-stock benchmark; verify listing/alloy and availability. Oklahoma source, not delivered Georgia price. Quote local equivalent rather than assuming long-distance shipping is economical. |
| [Home Depot3/4-inchMDF panel](https://www.homedepot.com/p/309177124) | **No price observable** | Product page confirms actual19.05mm thickness and49 ×97-inch panel. Local store stock, pickup price and delivery to30510 not verified; leave quote-required. |

## Budget treatment and release conditions

Do **not** add every price row: several are alternative purchase routes for the same part. The five-bar chassis price benchmarks span **$403–$1011.50 for raw stock only**, before grade confirmation, cuts and freight. The gantry extrusion has a concrete manufacturer calculation of **$151.73**. An exact full-machine metal subtotal is not available because metric aluminum, tank construction, cabinet supports, machined seats and interface plates still need quotes/details.

For a reviewable procurement sheet, separate (a) public price-backed line items, (b) explicit dimensional substitutions requiring revision, and (c) fabrication/finish/freight allowances. A local quote must state material and grade, finished/rough dimensions, kerf, tolerances, weld/facing allowances, leak testing, finish, tax, delivery and unloading terms. No amount in this report proves delivery is included.

Useful RFQ wording: “Please price the Rev C29-piece2 ×2 ×.120 tube schedule from five20ft bars, with each piece labeled. Separately price the30-piece25 ×25 ×2 panel frame schedule; two1450 ×100 ×8 rail strips; six80 ×80 ×12 foot plates; eight101.6 ×50.8 ×6 diaphragms; fabricated920 ×1200 ×100 sloped3mm pan; nineteen880 ×75 ×3 slats; and six497 ×397 ×8 aluminum plates. Quote raw material, processing, finish, and delivery to AltoGA30510 separately. Identify any proposed imperial substitution and actual supplied thickness. Please include usable stock length and your cutting tolerances.”

This is a takeoff for engineering review, not released fabrication drawings. Published supplier descriptions and dimensional arithmetic have been checked; a final tolerance stack, flatness acceptance and load test remain machine commissioning work.

## US-stock procurement adjustments to Rev C

For the proposed US purchasing route, quote **1 × 1 × .083 inch panel tube**, **5/16-inch aluminum subplates**, and **3/4-inch MDF**. These are explicit procurement adjustments; the existing concept drawings have not been changed or released.

- Panel frame cuts: **12 × 497 mm** and **18 × 346.2 mm** (the latter replaces347 mm to retain397 mm outside width around25.4 mm tube). Net tube12.1956 m. Prefer **two24-foot bars if stocked**, or two20-foot bars plus a short drop. Two20-foot bars remain too short before allowing kerf.
- Nominal panel stack:25.4 +7.9375 +19.05 = **52.3875 mm**. At920.8 mm panel datum, router surface becomes **973.1875 mm before skim**, compared with972.8 mm in the metric concept. Actual material thickness and final surfacing determine the installed plane.
- Quote two rail strips1450 ×100 ×**7.9375 mm** from5/16 steel instead of8 mm; nominal cap datum changes **−0.0625 mm**. Account for this in rail leveling and head clearance. A4-inch-wide bar is101.6 mm, so it requires width trimming or a documented width adaptation too.
- Keep exact8 mm5754's$2707.26 comparison out of the proposed purchase total. Quote affordable finished5/16 6061-T651 blanks locally, with flatness/finish requirements; the publicly observable Online Metals48 ×48 benchmark is$759.54 before cuts/freight.
- Locating hardware, sleeve lengths, clamp travel and tool-tip clearance still require the measured dimensions. No existing released drawing is implied by this addendum.
