# What the profile subtotal leaves out

This is a quoting takeoff for the chassis in [frame.py](frame.py). It distinguishes delivered profile stock from what joins and supports that stock. Use the actual purchased slot shape, allowable preload and joint load ratings to specify hardware. No thread purchase or fabrication release follows from a clearance hole alone.

| Item | Six-foot frame | Nine-foot frame | What the model calls for |
|---|---:|---:|---|
| 4040 extrusion cuts | 19 | 22 | Base + three independent 730 mm center legs on the recommended hybrid. |
| Foot assemblies | 6 | 9 | Leveling foot, load-rated threaded attachment and foot pad; CAD is an envelope. Check the actual floor and bearing/leveling range. |
| Side leg/tier splice plates | 12 | 12 | Exterior 6 mm plates; color-coded in the STEP, bearing between post and rail end faces. |
| Under-crossmember bearing shelves | 6 | 6 | 96 × 70 × 6.35 mm blanks; four M6 clearance holes each. |
| Center-post clips | 0 | 6 | Two 6 mm T-shaped plates at each additional leg, 4 holes per plate. |
| Braces | 12 | 12 | 30 × 4 mm steel flat; opposing straps on side and end planes. Second strap is spaced clear at the crossing. Select end fasteners for reversal and verify no slip. |
| Brace stand-off spacers | 12 | 12 | 5 mm spacers at the off-plane strap ends. |
| Continuous rail caps | 2 | 2 | 1,450 × 101.6 × 7.9375 mm (4 × 5/16 inch section) blanks; flatness/fastening matters. |
| Inside guide datum strips | 2 | 2 | 1,450 × 45 × 8 mm; new bolted mount to extrusion, flush before rails go on. Actual rail holes require transfer. |

**Candidate chassis-to-slot fastening stations: 148 base / 172 with center feet.** Base count: 64 side-splice, 24 shelf, 24 brace, 16 cap and 20 datum. Center-post clips add 24. The cap and datum locations use flush heads; verify pocket/head dimensions on the actual screw before machining. Other locations require different screw lengths for the plate/spacer stacks. Counts exclude rail/actuator, pan retention, feet, dry ledgers/rack, bed, tool, enclosure and spares. A cheap 20-piece corner kit therefore does not price the frame. See [candidate fasteners](FASTENERS.md) and [extrusion and remaining steel](SOURCING.md).

The installed motion uses two 1,000 mm Y and one 800 mm X HMS40 modules, independent HGR20 guides, a separate 1,200 mm gantry extrusion, and the 100 mm Z stage. This geometry is carried forward from the smaller machine. **None of those motion components, including the moving gantry beam, is in the stationary-frame profile subtotal.** If they are not already owned, price them separately. Custom plate, reservoir, electrics and fume/dust control also remain outside that subtotal.
