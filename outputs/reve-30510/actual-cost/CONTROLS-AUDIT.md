# Controls and water purchasing audit — Rev E
Date: 2026-09-24. Destination: Alto, GA 30510. No purchase, supplier contact, CAD change or master-BOM edit was made.

The selected component prices recovered here total **$257.57 in goods**, but this is only a partial itemization of the old allowances. It is **not a complete controls price or a savings calculation**. Eight rows remain unpriced; conditional alternatives are excluded from that subtotal. The machine's delivered actual cost still cannot be stated from these results.

The complete machine-readable schedule is [controls-findings.json](controls-findings.json). It gives quantities, old-row mappings, purchase sources, shipping groups, fit evidence and remaining work. Rows that share an old ID replace portions of that allowance; do not leave the original full allowance in the same selected total after reconciling its residual items.

## Concrete purchasing corrections

| Item | Quantity | Goods price | Decision |
|---|---:|---:|---|
| Keyed GCX1470-22 mode selector | 1 | $34.50 | Requires two added NO contacts; its supplied 2NO+2NC configuration does not implement R1/R2/P1/P2 as drawn. |
| ECX1040-2 NO contact pack | 1 pack of 2 | $8.75 | Converts the mode selector to four NO contacts. |
| GCX1300 SETUP/RUN and AUTO/DRAIN selectors | 2 | $24.00 | Reuse the two removed NC blocks from the mode selector. |
| GCX1102 green momentary buttons | 2 | $18.00 | CYCLE START and FILL; FILL also needs its NC contact. |
| GCX1104 blue reset button | 1 | $9.00 | Ordinary reset, not an E-stop. |
| GCX1101 red NC momentary buttons | 2 | $18.00 | Separate FEED HOLD and WATER STOP. |
| ECX1030-2 NC contact pack | 1 pack of 2 | $8.75 | One FILL contact; second available for the final E-stop assembly. Page currently shows backorder. |
| GCX1131 latching twist-release E-stop | 1 | $17.50 | Supplied NC contact; latest page backordered, forecast September 28. |
| DIN rail DN-R35S1-2 | 1 pack of two 1 m rails | $9.25 | Shared cabinet purchase; final panel layout must fit. |
| Adafruit4474 USB-A to USB-C data cable | 1 | $4.95 | Approximately1 m; verify routing. |
| Littelfuse0FHA0001ZXJ fuse holders | 3 | $35.10 | Pump, control, valve/timer branches. |
| Littelfuse0287010.U,10 A | 1 | $0.47 | Pump conductor protection; actual pump fuse/inrush instruction still applies. |
| Littelfuse0287001.U,1 A | 2 | $0.94 | Control and valve/timer branches. |
| Vishay1N4007-E3/54 | 10 | $3.42 | Six suppression plus four OR diodes; ten are required. |
| STMicroelectronicsSTPS20100CT | 1 | $1.57 | Active replacement candidate for the obsolete onsemi pump diode, with thermal acceptance retained. |

The modular-switch prices and compatibility come from AutomationDirect's [mode selector](https://www.automationdirect.com/adc/shopping/catalog/pushbuttons_-z-_switches_-z-_indicators/selector_switches/gcx1470-22), [two-position selector](https://www.automationdirect.com/adc/shopping/catalog/pushbuttons_-z-_switches_-z-_indicators/selector_switches/gcx1300), [NO blocks](https://www.automationdirect.com/adc/shopping/catalog/pushbuttons_-z-_switches_-z-_indicators/pushbutton_-z-_switch_-z-_indicator_accessories/contact_blocks_-z-_mounting_flanges/ecx1040-2), [NC blocks](https://www.automationdirect.com/adc/shopping/catalog/pushbuttons_-z-_switches_-z-_indicators/pushbutton_-z-_switch_-z-_indicator_accessories/contact_blocks_-z-_mounting_flanges/ecx1030-2) and [button catalog](https://www.automationdirect.com/adc/shopping/catalog/pushbuttons_-z-_switches_-z-_indicators/pushbuttons?searchStatus=bad). Verify the assembled selector's center-off and left/right closure sequence before wiring. The FILL contact timing and final guards remain to establish; a flush protective ring is not a hinged guard.

The previous onsemiMBR20100CTG is listed as obsolete. ST's [STPS20100CT](https://www.digikey.com/en/products/detail/stmicroelectronics/STPS20100CT/2827118) is active and has the required100 V dual10 A common-cathode arrangement. Pin1 and pin3 are anodes; pin2 and the exposed tab are cathode. This is a component-level substitution, with supported/insulated mounting and pump-stop heating tests still required. The [manufacturer datasheet](https://www.digikey.com/htmldatasheets/production/1010540/0/0/1/stps20100ct.pdf) supports these ratings. The water circuit remains24 VDC; none of its blade-fuse components belong on AC mains.

## Interfaces that cannot yet be called an exact compatible cart

- **E09 field isolation:** the firmware maps twelve inputs: four homes, three THC signals, E-stop status, feed hold, cycle start, probe and combined permissive. It also needs a normally-off PG2 output interface. Select the actual input current, polarity,3.3 V output levels and isolation circuit before pricing a finished board. An inexpensive two-channel SparkFunBOB-09118 was researched, but it is not adopted as a native24 V field-input board. Relay-contact wetting current must be checked.
- **E13 main power and stop chain:** exact branch current, VFD inrush, power topology and restart/monitoring circuit remain undefined. A generic contactor lot cannot be transformed into an actual price without these. Water SSRs, branch fuses and auxiliary relays are already separate; no duplicate charge belongs here.
- **E14 cables:** the25–30 m motor and25–30 m signal figures are estimates, not a routed cut list. Motor current, chain route, gauge, functional conductors and connectors remain open. A four-conductor cable that includes green/yellow PE does not provide four unrestricted motor-phase conductors. The spindle kit's supplied VFD cable must not be purchased again without a demonstrated deficiency.
- **E15 panel consumables:** produce one shared terminal/gland/label/wire schedule including the water XW terminals. This replaces overlapping lots rather than eliminating required connections.
- **E16 cooling and VFD segregation:** the selected enclosure remains an envelope. VFD loss, orientation, airflow and usable backplate space must precede the fan/housing choice.
- **E17 communications:** one internal USB cable is concretely priced. An Ethernet cable is not required for the Kraken's USB motion connection. A host-network cable is optional and must have its own actual route.
- **E21 host media/cooling:** exact in-stock cards and CB1-specific cooling are unpriced. Adafruit2820 was rejected because no longer stocked. No host or media is assumed owned.
- **E22 VFD interface:** [CNC4PC C41S](https://www.cnc4pc.com/shop/integration-electronics-spindle-control-436/c41s-c41s-pwm-variable-speed-control-board-1044) is$45.90 with isolated analog and relay outputs. Its [manual](https://cnc4pc2.s3.us-east-2.amazonaws.com/files/c41s-r1.1_user_manual_v1.pdf) specifies5 V TTL signals, so it requires a properly designed3.3→5 V buffer and5 kHz verification. It derives run from PWM; the independent PG2/hardware enable gate must remain. The$1.50 Adafruit74AHCT125 IC is currently out of stock and is not a complete interface. The old$35 allowance is not a verified drop-in purchase.
- **E08 THC:** [PoLabs PlasmaSensCompact](https://www.poscope.com/product/plasmasenscompact/) is **€148.90**, excluding VAT/shipping. Its isolated Arc OK/UP/DOWN functions suit the firmware concept. It is not a$220 USD delivered quote. Exact cutter identity, voltage connection, starting method and trigger remain conditional; an AG-60 torch name does not identify these.

## Water cost and simplification

Retain the already specified pump, valve, strainer, five working floats, six Finder auxiliaries and two Carlo Gavazzi series DC SSRs. Their old observed offers are not reasserted as newly verified here. Do not substitute generic low-cost relays without pump-load and coil-current evidence.

A [Finder39.81.0.024.0060 timer](https://www.digikey.com/en/products/detail/finder-relays-inc/39-81-0-024-0060/10055832) costs$38.59; two would replace the two AH3-3 timers functionally and save cabinet space. This is **not yet an adopted substitution**. Its[primary data](https://cdn.findernet.com/app/uploads/S39EN.pdf) specify a500 mW minimum contact load, which the close timer may miss when feeding only an SSR input. The contact wetting load, terminal schedule and minimum-load solution must be checked first. A higher documented price does not close an electrical mismatch.

The updated JSON prices the gravity-drain parts individually. The nominal 3 m pump hose requirement has a separate matched-system candidate; it is not yet adopted. No unfamiliar control circuit was changed to reach a lower price.

| Added sourced part | Purchase quantity | Goods price |
|---|---:|---:|
| [Kuriyama K3150 1-inch gravity hose](https://www.centralstateshose.com/Kuriyama-Clearbraid-K3150-multi-purpose-pvc-hose-1-inch-id-per-foot_p_23416.html) | 5 ft / 1.524 m | $16.15 |
| [Pro Flow CP150/100-304 bell reducer](https://www.proflow-dynamics.com/bell-reducer-coupling.html) | 1 | $8.17 |
| [Pro Flow U100-304 union](https://www.proflow-dynamics.com/pipe-union.html) | 1 | $12.80 |
| [Pro Flow HB100-304 drain barb](https://www.proflow-dynamics.com/hose-barb-fittings.html) | 1 | $7.86 |
| [Pro Flow CAP150-304 cleanout cap](https://www.proflow-dynamics.com/1-1-2-threaded-cap.html) | 1 | $7.28 |
| [Pro Flow NP100-CL-304 close nipple](https://www.proflow-dynamics.com/1-close-nipple-ss-304.html) | 2 | $5.24 |
| [RectorSeal 23710 T Plus 2, 1.75 oz](https://www.lowes.com/pd/rectorseal-t-plus-2-sealant/1000092785) | 1 | $5.87 |

The reducer is explicitly **female-to-female**. One nipple connects it to the union; the second connects the union to the female valve. This replaces the earlier one-piece female-to-male reducer concept. Actual nipple engagement and wrench clearance remain an assembly check. The sealant's [manufacturer](https://rectorseal.com/rectorseal-t-plus-2-group/) supports water and metal/plastic pipe. The gravity hose must remain supported, continuously descending and protected from hot slag; it is not the high-pressure pump hose.

The [GCX1131 E-stop](https://www.automationdirect.com/adc/shopping/catalog/pushbuttons_-z-_switches_-z-_indicators/emergency_stop_pushbuttons/gcx1131) is $17.50. It uses the existing GCX/ECX contact family; the [primary catalog](https://cdn.automationdirect.com/static/specs/cents22mmmush.pdf) specifies positive-opening contacts. The latest page shows a September 28 backorder forecast, not guaranteed delivery. Guards and legends remain separately unpriced under CA-39.

The conditional pump-hose set costs **$93.57**: [10 ft Parker 801-8 hose](https://www.wilson-company.com/product/801-8-blu-rl/801-series), three [30182-8-8 fittings](https://www.partsgopher.com/product/30182-8-8/82-series-30182), two [30182-6-8 fittings](https://www.partsgopher.com/product/30182-6-8/82-series-30182), and one [1/2-inch female coupling](https://www.proflow-dynamics.com/pipe-couplings.html). The coupling changes the pickup's male thread to female; it avoids mistaking an NPSM swivel for an NPT pipe connection.

Parker's [manufacturer bulletin](https://www.parker.com/content/dam/Parker-com/Literature/Hose-Products-Division/Websphere-Supporting-Literature/FCG_HPD-Thermal-Management-Hoses-Bulletin.pdf) gives 300 PSI, 28 inHg vacuum and a 125 mm minimum bend radius for this size, but excludes extreme pulsation. The diaphragm-pump application and water-treatment/corrosion compatibility therefore remain to confirm. Only matching 82-series ends belong on this candidate hose, with no worm clamps added to those connections.

If that set is adopted, the small-hose worm clamps disappear from the purchase. A [ten-piece minimum purchase of Breeze 63016 clamps](https://www.qualityfarmsupply.com/products/13-16-inch-1-1-2-inch-range-stainless-steel-hose-clamp) is $13.40, with two allocated to gravity-line retention and eight spare. The indexed offer is priced; the direct page returned 403 and should be rechecked. This makes the **whole conditional hose/clamp option $106.97**, excluded from the selected subtotal. Without adopting that option, suitable pump hose/fittings and small-hose clamps remain unresolved; the original twelve-clamp requirement is not silently priced as zero.

CAD guards and brackets belong to the material-specific metal audit, including its separate stainless-steel stock groups. They are not all covered by the two 0.120-inch mild-steel sheets. Count each metal group once; owner welding/cutting labor is not another cash purchase. Residual gasket, mesh, pipe blanks, seals and consumables remain in the former W-GUARDS/W-METAL-EXTRA scope unless already counted elsewhere.

Using a suitable existing PC for the G-code sender could remove the currently budgeted$61.97 CB1/carrier pair and reduce host-cooling/media costs. It is **conditional**, because suitable owned hardware has not been confirmed. Automatic water transfer and the independent interruption path remain in every proposal; the vented reservoir is never a pressure or vacuum vessel.

## Shipping and total interpretation

Group all AutomationDirect hardware into one order. Its published free US small-package threshold is$49; the listed hardware exceeds it. This is a policy-based zero shipping entry, not a ZIP-specific delivery promise. The NC contact pack and the latest GCX1131 page are backordered. DigiKey, Adafruit, CNC4PC and PoLabs shipping are each unknown and counted once per eventual order, not once per row. DigiKey pages also flag possible cart tariffs. Wilson Company, PartsGopher, Pro Flow Dynamics, Central States Hose, Quality Farm Supply and Lowe's are also separate, unquoted shipping groups. No delivery date from an unlocalized page is treated as an Alto promise. Taxes remain outside the goods subtotal.

Amazon-first searches did not establish a complete traceable offer for the added interfaces and modular controls, so manufacturer and authorized-distributor prices were used. Do not subtract the partial$257.57 from the old allowances and call the difference savings. The $257.57 selected partial subtotal includes $80.87 of newly priced E-stop/gravity-plumbing goods. The $106.97 conditional pump-hose/clamp set is separate. Eight rows remain unpriced, and other rows still have fit or circuit conditions. Complete those selections and consolidate carts before replacing the remaining allowances.
