# Structural pan and carving-pad simulation

The whole-table study uses the steel work supports in both operating modes. Eight 40 mm-deep slats carry four separate 826 × 250 × 19.05 mm carving pads in woodworking mode. The slats are positively attached to three longitudinal combs. The pads have four removable hold-downs each. Remove every pad, clamp and detachable nut cage before plasma cutting.

## Coupled plate and beam model

The calculation uses PyNiteFEA 3.2.1 MITC4 quadrilateral shells for the particleboard. Separate beam layers represent the slats, edge members, center backbone and transverse frame bearers. Vertical springs connect the layers. Their rotations remain independent, and the model credits no composite action between particleboard and steel. Steel torsion is effectively omitted. Coordinate offsets between the numerical layers distinguish the degrees of freedom and have no claimed physical thickness.

The particleboard assumptions are E = 2,500 MPa, Poisson ratio 0.25 and actual thickness 19.05 mm. The final pad fronts lie at Y121.4, 372.4, 623.4 and 874.4. Eight slat support lines sit at Y161.4, 331.4, 412.4, 582.4, 663.4, 833.4, 914.4 and 1084.4. Three crossbearers sit at Y100, 600 and 1100, supported at X33.4 and 1116.6. The real design's clear crossbearer spans are shorter, so these calculations retain a slightly conservative span.

The outer combs sit at X165 and 985. Their 12 mm residual webs, the 1.8974 mm floor and 60 mm structural edge members are treated as welded composite steel sections. The 35 mm front and rear walls determine the pan's retained water height. The outside edge extensions require actual shear-transferring welds. The center comb is directly backed by the structural rectangular-tube spine. Removing a support, allowing a weld to slip or relying on a loose pan contact invalidates the corresponding model constraints.

Each load case applies 100 N through a 25 × 25 mm patch. Sixteen cases cover near-edge and middle locations on all four pads. This is an incremental dry-mode rigidity calculation. It includes work-side support movement through the steel grid. It omits the guide, gantry, spindle, floor-pad and welded-joint compliance and does not establish total tool-to-work movement.

## Results

| Calculation | Largest work-side movement |
|---|---:|
| Final pad positions, 16 load locations, signed continuous seat constraints, minimum edge section | 0.1836 mm |
| Final pad positions, compression-only seat lines and four discrete clamps per pad, all 16 cases | 0.1899 mm |
| Earlier pad positions, worst nominal patch, mesh refined from 50 mm to 25 mm | 0.1838 mm |
| Earlier pad positions, reduced board properties, 18 mm and E = 2,000 MPa, four selected cases | 0.2013 mm |

The worst final patch lies near X785, Y1111.9 on the fourth pad. The first-pad critical contact case at X365, Y133.9 gives 0.1793 mm. The other final middle locations give approximately 0.097–0.125 mm. The final contact solve has 1,350 shell elements, 272 steel beam segments and 1,805 nodes. In the earlier layout the worst nominal patch lay near X365, Y87.5. Refining that nominal solution changed it by about 0.4%. Each solved case balances the applied 100 N against its floor reactions to within 0.000001 N.

The contact model permits separation between the wood and slat seat lines. It retains positive restraint at X365 and 785 on both support lines of each pad, matching the four intended hold-downs. It requires those actual attachments. The model also requires the welded slats to transmit uplift into the combs. Consumable slats must be replaced and their support datum checked before using them again as a carving bed.

The final models reduce the ideal edge section from 54,936 to 38,977 mm⁴. They use a 33.1026 mm wall above the inside floor, the upper 13 mm of the outer extension at its windows, a 5 mm residual comb web at the drain ports and their connecting floor strip. These minima are applied along the whole edge, even where the actual section has more material. In the earlier pad arrangement this reduction changed the worst checked contact case from 0.1897 to 0.1901 mm. The final arrangement moves every pad and slat 46.4 mm rearward to cover the actual router-axis envelope.

The narrower one-dimensional strip study predicted larger local movement because it excluded the panel's transverse load sharing. The shell model includes that plate action while preserving the flexible steel supports. Its result still leaves little room against an illustrative 0.20 mm total-loop target. The lower-property sensitivity exceeds that value on the work side alone.

## Physical qualification

With the table assembled and leveled, reference an indicator from the spindle mount to the work surface. Apply controlled 25, 50, 75 and 100 N loads above the slat spans, at the near-edge patch and near the rear travel limit. Record loaded movement and residual movement after unloading. Repeat after a bed swap and after replacing any slat. Inspect the board thickness and stiffness, the seating contacts, the retained fasteners and the steel edge welds.

The nominal calculation supports a light woodworking and carving candidate. Milling capacity, dynamic accuracy, fatigue strength, vibration behavior, fire and fume control, and the actual thermal response require separate verification.

[PyNite model and quad documentation](https://pynite.readthedocs.io/en/latest/FEModel3D.html)

[Executable model](plate_fem.py) · [Final 16 contact cases](plate-shifted.json) · [Final 16 signed-seat cases](plate-shifted-linear.json) · [Earlier refined mesh](plate-fine.json) · [Earlier reduced board properties](plate-low.json) · [Source and result hashes](analysis-manifest.json)
