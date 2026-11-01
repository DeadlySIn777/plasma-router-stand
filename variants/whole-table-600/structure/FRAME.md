# Six-leg frame rigidity screen

The final table uses two continuous 50.8 mm square steel rails, six braced posts and three transverse bed bearers. The rail supports lie at Y100, 600 and 1100. The physical rails run from Y0 to Y1450, so their rear overhang is 350 mm. Four outside posts are 31.75 mm square and the two middle posts are 50.8 mm square. Each leg has a welded short foot tube, a bearing cap and a floor plate. Actual floor contact and trapped steel leveling shims are part of the load path.

The independent member calculation assumes E = 200,000 MPa and screens tube walls of 1.5, 1.9 and 2.1 mm. Rounded-corner second moments are calculated by numerical integration using outer radius 2t and inner radius t. The selected retail gauge has to be measured. Modelled stock envelopes alone establish neither its grade nor its section properties.

## Continuous guide rails

For a 1.9 mm wall the rounded 50.8 mm square tube has I = 142,508 mm⁴. A 100 N force at Y350 gives 0.0066 mm movement at its load point with all three rail supports engaged. A force at the last modelled guide-block center Y1365 gives 0.0577 mm there, and the unsupported rail end moves 0.0797 mm. A deliberately severe 100 N force directly on the end at Y1450 gives 0.1128 mm.

With 100 N shared equally between two guide-block centers 180 mm apart, their mean movement is about 0.0038 mm at guide midpoint Y275 and 0.0228 mm at the rear guide midpoint Y1275. These are one-rail vertical member results. Actual tool and gantry moments, crossbeam movement, joint compliance and loads shared between the two rails require the assembled machine.

The boxed steel rail has a substantially stiffer material and section than the earlier schematic 4040 stock. The earlier source lacked certified extrusion inertia and joint stiffness, so these calculations do not establish a numerical whole-machine improvement over that table. The earlier shallow dry-carrier member gave 0.606 mm movement at 100 N by itself. The new coupled work-side model includes both the panels and their steel grid and gives approximately 0.190 mm across its sixteen final contact cases. The scopes of those figures differ.

## Braces, feet and pan

One active 19.05 × 3.175 mm tension strap in a 500 mm side bay carries about 160 N for a 100 N lateral force. Its anchors lie at Z150 and Z775, giving a 625 mm rise. Pure axial extension gives 0.0170 mm of lateral movement. A total 0.1 mm of anchor movement raises that to 0.177 mm. For the 1083.2 mm end bay with 480 mm brace rise, the corresponding values are 0.0117 mm and 0.121 mm. Only the tension diagonal is credited. Each rectangular side strap is 804.39 mm long, including 2 mm beyond each anchor center. Three fit an 8-foot stock length with the stated cuts. Welded ends, steel spacer pads and the differing post widths form the actual connections shown by the final CAD.

The pan floor is supported by the two structural edge assemblies, the center backbone and three transverse bearers. A simply supported 420 × 500 mm plate cell in 1.8974 mm sheet predicts approximately 0.272 mm of sag at a 20 mm water head, 0.354 mm at 26 mm and 0.476 mm at 35 mm. These are ideal small-deflection plate calculations and omit initial fabrication distortion, leaks, slag and blocked drainage. The carving mode is a drained setup.

The prescribed support elevations in the beam calculation require all six feet to bear on the actual floor. A loose foot, an untrapped shim or a rocking stand changes the model. Full loop measurements need to include the spindle mount, work surface, rail positions, front and rear travel limits, and repeated conversion between modes.

[Member calculations](frame.py) · [Calculated cases](frame.json) · [Coupled carving-bed simulation](PLATE.md)
