# Removable metal carrier locating interface

The candidate uses one round pin and one diamond pin, both in metal, with replaceable hardened bushings. Separate steel seats and clamps carry the table. A dock-present sensor can report its target; it cannot establish pin seating, clean contact faces or clamp preload.

This folder is separate from frozen Rev I. It contains a reusable local dock, not an integrated retrofit or a fabrication release for the whole bed. The present small bed remains unchanged. `output/verification.json` records these limitations as explicit false qualification fields.

![CAD component preview](output/locator-dock-preview.svg)

## What is actually modeled

- Two 60 × 40 × 12 mm fixed pin blocks, with four recessed M6 mounting holes and two match-reamed Ø4 transfer dowels each.
- Two 60 × 40 × 12 mm carrier receivers, with M5 through-tapped attachment holes, two Ø4 transfer dowels and press-in replaceable bushings.
- Three primary Z supports and one fitted supplementary support, four steel carrier landing pads, four M6 × 25 drawbolts and washers.
- A separate protected state with two removable steel swarf caps. Caps are not watertight seals.

The grid and carrier are deliberately absent from the local model. The integrating assembly must provide real bearing and attachments under **every** support and locator block, and connect the receiver/landing pads to metal frame members. No part is counted as supported by an invisible frame.

[Assembled STEP](output/step/common-locator-dock.step), [protected STEP](output/protected/step/common-locator-protected.step), [interface coordinates](output/interface.json), [machining operations](output/part-operations.json), [local verification](output/verification.json).

## Selected interfaces and fit

| Item | Candidate | Nominal interface |
|---|---|---|
| Round pin | JW Winco DIN 6321-10-18-B | Ø10 g6 head, 18 mm head height, Ø6 n6 × 9 mm shank |
| Diamond pin | JW Winco DIN 6321-10-18-C | Same head/shank sizes; relief aligned along the two-pin centerline |
| Bushing, two per carrier | JW Winco DIN 179-B10-12-A-NI | Ø10 F7 bore, Ø15 n6 OD, 12 mm length |
| Clamp | Four M6 × 25 socket screws | 600–900 N verified preload each, entirely through metal |

Dimensions come from the primary [pin drawing](https://live-catalog.jwwinco.com/pdf/winco/US/6321.pdf?dispositiontype=attachment), [bushing drawing](https://live-catalog.jwwinco.com/pdf/winco/us/172n.pdf?dispositiontype=attachment) and [ISO fit table](https://live-catalog.jwwinco.com/pdf/winco/US/286_2.pdf?dispositiontype=attachment). The installed bore must measure 10.013–10.028 mm and the pin 9.986–9.995 mm; this gives 0.018–0.042 mm diametral clearance. Pressing can change the bore, so loose-part dimensions alone are insufficient.

The purchased solids omit supplier edge details. The diamond non-contact relief is schematic because the primary drawing does not fully dimension every relief facet. Inspect at least ±0.20 mm movement along the pair line while fully engaged, and verify correct clocking. Do not manufacture a diamond pin from its envelope STEP. The one-round/one-diamond arrangement follows the [Carr Lane locating principle](https://www.carrlane.com/product/locating-pins/locating-pins/round-diamond-pins/round-pins).

Bush replacement means arbor-press service of a steel cartridge, not a loose slip-fit sleeve. Match the housing bore to the delivered bush for the specified 0.010–0.020 mm interference, inspect the installed ID, and reject an assembly outside the fit range. This is a design-selected fit, not a claim that the supplier mandates that interference. Pin shanks similarly use matched 0.010–0.015 mm interference. No paint/coating is allowed on fitted or seating surfaces. After changing a pin, bush, cartridge, support shim or mounting joint, requalify and establish WCS again.

## Z support, clamps and thermal freedom

The carrier underside datum is 14 mm above the supporting grid. Locator pedestals stop at 12 mm, leaving 2 mm below receivers. Three hard seats set Z, pitch and roll; their installed bearing faces need a 0.02 mm coplanarity target. Fit the fourth support's shim while the carrier rests on those three seats. Never use that fourth support to jack a warped carrier onto an arbitrary plane.

The four clamp forces run from screw and washer into steel landing pad, hard seat and grid. Locator pins provide lateral restraint independent of friction; the two match-dowels at each cartridge carry that restraint into its parent structure. M6 clamp holes are deliberately loose slots. Generic tightening torque is not a preload measurement; establish a torque/preload procedure on the actual fasteners and lubricated condition before release.

For the large variant, the selected engineering assumption is 18 independently handled metal carriers in a 3 × 6 grid: each **438.6667 × 423.3333 mm**, with 2 mm seams, covering **1320 × 2550 mm**. The stock origin and travel belong to the large-variant layout. A proposed carrier uses new documented aluminum 38.1 × 25.4 × 3.175 mm rectangular tube, 6.35 mm backing plate and 12.7 mm HDPE. Add internal ribs so backing-sheet clear spans do not exceed 150 mm. The owned 12-inch aluminum pieces are not assumed to supply this material.

The compact stack option is **71.15 mm**: 14 mm to the bottom of the landing/receiver blocks + 38.1 mm carrier envelope + 6.35 mm backing + 12.7 mm HDPE. It requires those 12 mm steel blocks to occupy the lower portion of the carrier envelope, with frame corners pocketed/terminated and joined around them. This pocket/joint integration is not modeled or qualified in the common dock; do not overlap tube and landing solids to hide the difference.

The **current large layout instead chooses the simpler 83.15 mm stack**: 26 mm to the **top** of the landing/receiver blocks, then unnotched 38.1 mm carrier tube, 6.35 mm backing and 12.7 mm HDPE. Consequently its grid top is Z829.55, carrier tube underside is Z855.55 and finished wear surface is Z912.70. This 26 mm interval is consistent with the common dock's 14 mm lower datum plus 12 mm upper block. The upper pin projects above that plane, so the actual carrier must still provide a clearance pocket/window at each pin, and its load-bearing attachment remains to integrate.

HDPE is a replaceable wear surface, not the structural datum. Use a central low-force restraint and radial clearance at other fixings, with steel compression limiters and washers carrying tightening force. A candidate detail is an OD8 limiter in a 12 × 9 mm radial slot, plus a matching elongated washer counterbore. The limiter should finish 0.10 mm above measured local plastic thickness; screw preload must not crush the plastic. These HDPE fixings are a required carrier detail, not modeled hardware in this local dock. Actual workholding must transfer cutting force to the aluminum carrier; it cannot depend on the HDPE's low-force retention screws.

Using [Hydro 6061 expansion data](https://www.hydro.com/globalassets/01-products--services/extruded-profiles/americas/ena-resources/alloy-data-sheets/hydro_2019_data_sheet_6061.pdf) and [Ensinger HDPE data](https://www.ensingerplastics.com/en-us/shapes/polyethylene-tecafine-hdpe-natural), a 20 °C change gives approximately 0.57 mm maximum HDPE-to-aluminum radial movement for one panel. The specified slot has 2 mm radial travel around an OD8 limiter. The aluminum-to-steel pin-pitch difference is about 0.095 mm. Steel expansion is an explicit 12 µm/m/K engineering assumption. Equilibrate the assembly before precision work; clamps can restrain thermal sliding through friction, so thermal float is not a guarantee that a tightly clamped hot panel freely expands. Re-seat after a significant temperature change.

## Repeatability target and acceptance

The clean, stable-temperature target is **≤0.15 mm maximum XY point movement at any panel corner over 20 re-seats**. This is not demonstrated performance. The extreme-to-extreme clearance-only bound is already approximately 0.146 mm, before dirt, wear, joint movement or thermal effects. Thus the catalog's worst F7/g6 combination **cannot establish the combined 0.15 mm error budget**: it leaves less than 0.004 mm for everything else.

One candidate acceptance condition is measured installed pin/bush selection with **no more than 0.025 mm diametral clearance at either locator**. That reduces the clearance-only corner bound to about 0.087 mm, leaving about 0.063 mm for the combined remaining errors. It does not change the published supplier tolerances or mean every purchased pair will meet the selection requirement. The measured clearance, remaining error allocation, wear limit and 20-cycle test must all pass. A tighter requirement needs tighter accepted components or a qualified zero-point system. The small ATC's proposed ≤0.05 mm pocket-reference requirement is separate and is not established by this dock's catalog fit; qualify each pocket reference and re-probe as needed. Do not label a sensor signal or nominal CAD fit “dead nuts.”

Commission each carrier by cleaning faces, checking the three primary contacts, fitting the fourth support, indicating the pins/metal datums, and recording 20 re-seats at a controlled temperature. Use a consistent clamp order and verified preload. Record X/Y at at least three widely separated metal targets and Z at all four lands, including before/after a representative cutting load. Wipe away swarf each swap; do not lubricate with a tacky coating that traps chips. Inspect the fit again after the first service cycle and whenever results drift.

The executable member screen uses a 100 N light wood-routing force. It predicts about 0.024 mm tube bending plus 0.096 mm for a deliberately conservative 50 mm backing-strip width over a 150 mm span. That is a local member screen only: carrier joints, grid flexure, motion modules, spindle and workholding are excluded. The 300 N pin-load screen gives about 127 MPa shank bending; the supplier's allowable pin load and complete joint strength remain unverified. These arithmetic values are not a machine rigidity rating.

Eighteen independent carriers mean 36 pins, 36 bushes and 72 drawbolts, before grid/support hardware. That is a significant manual conversion count. The common module establishes a credible bolted interface; it does not claim a fast full-bed swap. Captive or over-center clamps could reduce handling only after a selected clamp's preload, reach, retention and collision paths are verified. No vendor price or delivered total has been guessed here.

## Existing small-machine audit

The Rev I beam feet already have nominal Ø6 round/relieved locators, but they locate relative to their seats. The removable front seats attach with two Ø8.5 clearance holes for M8 bolts, so removing those seats interrupts the return datum. The individual 20100 panels also have clamps without a positive XY locator. Adding two pins elsewhere does not fix either gap.

A small-machine retrofit must positively locate both removable front seats to their frame supports and each independently removed metal panel/cassette to its supported beams. Its finished working height, beam handling, storage, spoilboard reach and plasma clearance must then be rechecked. Those interfaces remain **open** in the unchanged Rev I design; this common module is a candidate building block.

## Regenerate and integrate

Run with a Python environment containing CadQuery, NumPy and ezdxf:

```text
python variants/common/location/verify_location.py
python variants/common/location/render_preview.py
```

The verifier records source hashes, static checks, the rank-six constraint matrix, arithmetic and a continuous local vertical extraction check. Supplier downloads under `sources/` are local research only and are not required by the generator/verifier. Public source facts and URLs are in `source-data.json`.

`add_locator_pair(model, prefix, centers, base_z=...)` adds the pin and receiver pairs to a compatible `cad_helpers.Model`. `add_supports(...)` adds the separate seat/landing/clamp set. Model/source integration must add actual grid and carrier attachments and prove the resulting assembly. The ATC variant may reuse the locator pair with its own supported frame and clamps; presence sensing does not prove seating or preload.
