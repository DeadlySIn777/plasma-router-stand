# XR2 structure screen — development, not fabrication release

Finished profile: **12.3574m**. Six continuous posts reduce the largest supported header span to550mm; a four-post1080mm span bends7.57times as much under an equal midpoint point load.

At the conditional minimum section properties,75kg moving mass split across the headers produces an ideal rear-overhang gravity deflection of0.066mm per header. A100N transverse service force split between them adds0.035mm at the270mm overhang. These are member calculations; they do not include joint or owned motion compliance.

The selected50.8×50.8×6.35 dry ledgers require torsion restraint. Under100N split across both ledgers, the ideal550mm-span bending plus eccentric-torsion component is0.047mm, versus0.026mm for40×40×3 closed tube. Four attachment stations per arm restrain support roll; actual joint compliance still needs a test.

The bare frame material estimate is35.2kg before feet, hardware, bed, pan, storage and owned motion. Do not use decorative CAD volume as a real weight. The two300mm rear base members move the rear foot centres fromY1180 toY1410. At75kg moving mass/CGY1355, stationaryCGY650 and100N rearward atZ1053, at least21.2kg stationary mass is required for the chosen1.5moment ratio; water ballast is unavailable in dry mode. Actual mass, CG and foot contact must be measured.

Strap pairs are nominal1.9mm uncoated steel, matching the pan-sheet stock plan. Capacity and elastic compliance use a conservative1.8mm minimum thickness; measure the real sheet. Straps are tension-only. Two0.05mm end slips add approximately0.10–0.17mm of racking before elastic strap action, which can consume much of the0.30mm framework/bed target. Slot lip, joint-slip, foot and assembled tool-loop tests are therefore required.

Conditional profile properties are taken from the[manufacturer reference table](https://us.misumi-ec.com/pdf/fa/2019/2019_US_2768.pdf). They are procurement requirements, not properties attributed to an unverified Amazon die.

See structure-screen.json for all loads, formulas, sensitivities, limitations and acceptance tests. No pricing is included.
