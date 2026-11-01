# In-footprint manual carrier transfer

The raised rack sits on the rear crossframe. The 892 mm long steel carriers run from X129 to X1021. Their 866.6 mm seat spacing clears both gantry end brackets when stored. The pan stringers, wet crossframes and continuous dry ledgers stay installed. All four nominal carrier paths stay inside the chassis plan.

**Setup.** Remove stock, job backers, cutter, dust shoe and hose. Keep both processes disabled, physically support the fully raised Z and park the bare router at head X575, gantry Y275, Z lift 100. Use the same parked bare-router configuration in both directions. Remove or keep out the storage retaining screws during the transfers. The model includes the permanently welded keeper lugs. Tool or hose handling, the actual mounting screw extraction and operator hand clearances still need physical trials.

**Store panel 4 first, then 3, 2 and 1.** Release the moving carrier's dry hold-downs. The sequence coordinates below refer to the carrier's local X-axis rotation line, which sits 22 mm ahead of the forward tube. They are geometric setup references in millimeters.

1. Lift the horizontal carrier vertically from its Z920.7 bearing to Z980. This moves the center bar straight off its round and relieved locating pair.
2. Slide it level until the rotation line reaches Y980. The flat upper surface is at Z1030.8.
3. Rotate 90 degrees about X through that line at Y980, Z980. The greatest nominal height during this motion is approximately Z1223.
4. Move the upright panel directly rearward. The rotation-line Y positions are 1446, 1391, 1336 and 1281 for panels 4 to 1 respectively. Lower the rotation line from Z980 to Z903. The narrow front face of the first crossbar then bears at Z925.
5. With all four seated, install the four M5 storage retainers from below through the shelf lugs into the carrier doublers. Remove those retainers before unloading. Restore the dry deck in reverse order.

**Verification.** The script compares every installed and parked carrier solid with the actual CAD geometry using bounding coordinates and Boolean differences. It checks 308 transfer poses against the front-parked moving assembly, fixed steel, locators, and the other three carriers in their correct positions. Sampled intersections over 0.05 mm³ are reported. Continuous conservative boxes bound each moving tube and end tie between samples. Linear segments use endpoint hulls. Each rotational step adds the maximum arc-to-chord sag for a 245 mm radius. The only interval candidates are the eight nominal locator pin and hole pairs during straight axial withdrawal. Each 6.0 mm round pin withdraws through its matching 6.3 mm bore or relieved opening.

**Plasma travel with the rack locked.** The full Cartesian sweep of the modeled plasma assembly clears the stored carriers and rack hardware within head X175–975, gantry Y275–1240 and Z lift 0–100. The test checks swept axis-aligned boxes of every modeled motion component for this rigid orthogonal travel. At gantry Y1250 the ZBX80 stage hits the foremost parked carrier. Limit the plasma setup to **gantry Y1240** until as-built validation. This corresponds to nozzle-axis Y1038.6 with the modeled tool offset. Relative to the physical rear axis limit of Y1275, the planned software cap removes 35 mm of rear travel. The rear slat center is Y1055.5. Actual usable cut area also depends on front and side sheet support, clamps and the measured nozzle.

The test excludes humans, flexible cables and torch leads, an actual cutter or torch barrel, material, speed, tolerances and elastic deflection. Measure clearance under load, check reinstalled work zero and test the configuration-specific axis limits before powered motion. [Executable check](test_swap.py) · [Results and CAD source hashes](transfer-evidence.json)

