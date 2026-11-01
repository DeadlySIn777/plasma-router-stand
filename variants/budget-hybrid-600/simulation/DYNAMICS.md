# Column buckling, vibration and dry support stability

The nine-support compact chassis has three distinct checks. The compression loads at the feet include contributions from the whole machine. The lateral vibration estimate depends on gantry position, effective mass and joint motion. Overturning depends on the support polygon and loaded center of gravity. Run `python dynamics.py` alongside the current [static results](results.json) to reproduce the [numerical cases](dynamics.json).

### Column and foot

For straight, concentrically loaded 31.75 mm steel tube, the pinned-end elastic calculation uses π²EI/(KL)² with K=1. A cantilever end condition uses K=2. The full exposed post lengths are 914.75 mm at the outside and 698.25 mm at the center. The E=200 GPa rounded-corner sections come from the static screen. [Air Force Stress Analysis Manual, simple columns](https://engineeringlibrary.org/reference/simple-column-analysis-air-force-stress-manual)

| Nominal wall | Outside K=1 / K=2 | Center K=1 / K=2 |
|---|---:|---:|
| 1.5 mm | 62.14 / 15.53 kN | 106.65 / 26.66 kN |
| 1.9 mm | 74.52 / 18.63 kN | 127.90 / 31.97 kN |
| 2.1 mm | 80.11 / 20.03 kN | 137.49 / 34.37 kN |

The pinned-column estimates imply stresses of 337–607 MPa. Euler's elastic assumption breaks down above the tube material's proportional limit. Weld distortion, eccentricity, local wall buckling, end plates, threaded stem extension and load sharing require separate verification.

The seller claims 220 lbf (979 N) for **one leveling foot**. The largest single reaction from the simplified wet crossbeam case is 406 N. Machine dead weight, moving gantry, payload, uneven foot preload and lateral effects are additional. Compare a measured worst-case support load with verified installed foot, weld, nut, pad and floor capacities. [Selected leveling feet](https://www.amazon.com/dp/B08H5DPHFJ)

### Lateral vibration and spindle forcing

The screen combines one loaded X or Y brace panel in series with one 1.9 mm post tail above its upper brace node. The ideal lateral stiffness is 1,786–5,009 N/mm at the rail. An assumed effective mass of 20, 60 or 120 kg gives **19.4–79.7 Hz** using √(k/m)/(2π). These are sensitivity inputs. The actual modal mass and sharing among frame panels are unmeasured. [MIT vibration equations](https://web.mit.edu/2.151/www/Handouts/FirstSecondOrder.pdf)

When the assumed total brace-end movement reaches 0.3 mm at 100 N, the calculated secant stiffness falls to 193–252 N/mm. Across all slip and mass cases the apparent frequencies span 6.4–79.7 Hz. Free play and friction have amplitude-dependent behavior, so converting secant stiffness to Hz cannot determine a small-signal resonant frequency. The assembled head, deck, motors, fluid, cabling and floor can introduce other modes.

At an illustrative 3,000 rpm, shaft imbalance excites 50 Hz and a two-flute cut excites 100 Hz. At 12,000 rpm those frequencies are 200 and 400 Hz. The former 50 Hz example falls inside the ideal frame sensitivity range. These examples establish no acceptable speed range or chatter margin.

### Dry tipping and bearing tilt

At the 1.9 mm wall assumption, six bare side posts, three center posts, three crossbeams and twelve straps weigh 26.80 kg. Using just that subset, the least restoring moment about opposite outside foot centerlines corresponds to a **138 N external horizontal push in X or 155 N in Y** at 1,036 mm height. Resistance to sliding under 100 N would require a static friction coefficient of 0.381 for this subset. The bearing-line force transfers are 95 N and 84 N respectively. Use actual machine mass, loaded center of gravity and known seated feet to assess the installed case. A lost outside support, a raised tool or overhanging stock changes the pivot or moment. Cutting forces between mounted tool and workpiece also differ from an external push on the machine.

A 0.5 mm height difference between opposite support lines corresponds to 0.0263° roll or 0.0233° pitch. The corresponding reference-plane height change over the nominal 800 or 1,000 mm travel is 0.368 or 0.407 mm. A rigid tilt shared by the rail and bed cancels in their relative height. Local twist or differential rail-to-bed tilt is the accuracy concern.

### Measurements on the assembly

With tool power isolated, seat the pads and check load distribution under dry and filled conditions. With a force gauge, apply a modest reversible lateral force at the left and right rail above Y725 and measure floor-to-rail displacement on both sides. Repeat with an indicator between a fixed tool shank and the supported bed at machine center and near travel corners. Record applied force, displacement and return hysteresis. Avoid approaching either theoretical tipping threshold.

Attach accelerometers near the spindle clamp and a bearing support. With the empty toolholder stationary, use an instrumented hammer in X and Y at the rail and head mount. Repeat at near/middle/far gantry positions and in dry and operating-fill states. Compare force-normalized responses and coherence, record observed peaks and damping, and compare the measured peaks with shaft/tooth frequencies at the intended speed. [Siemens impact-test method](https://community.sw.siemens.com/s/article/Modal-Testing-A-Guide)
