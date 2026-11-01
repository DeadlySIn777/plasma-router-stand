# XR1 water circuit and service limits

This revision models a fixed sloping pan, a manual gravity drain and a separate open overflow into the red floor-supported receiver requested by the user. It is a review design. The tote liquid rating, actual fittings, thermal protection, lid-removal path and flow tests are unresolved; the water assembly is not a fabrication or operating release.

## Geometry and load path

The pan is894 mm wide by1096 mm long outside, fromX128..1022 andY100..1196. Nominal plain steel is14ga/1.9 mm; strength screens use1.8 mm minimum. The wet floor rises fromZ812 to818.576, with rimZ874. Eight transverse880×40×1.9 mm sacrificial slats stand atZ878 and bear on three separate3.175 mm longitudinal combs. The slats runX135..1015, giving5 mm neutral end overhang beyond the outer comb centres and full neutral comb bearing, with5.1 mm nominal pan-wall clearance at each end. Lateral walk and thermal float remain unqualified; a worst-case shift to a wall reduces opposite-end bearing, so this is not a retained-load rating. The comb feet contact the sloping floor, with local drainage notches; their real bearing/weld/load transfer must be qualified. Nine small shim packs carry the pan onto three frame crossbeams. The dry cassettes carry directly on independent Al ledgers and do not load the pan.

Four pan ears provide positive uplift capture. The front-left is round, front-right floats inX, and the rear pair have radial clearance. The cap/shoulder stack leaves1 mm nominal ear uplift freedom. Tightening the keeper bolt must preload its cap and shoulder, rather than squeeze the thermally moving steel ear. The small frame brackets, threads, welds and real bend radii still need shop details and proof loads.

A provisional operating water plane isZ854,24 mm below the slat tops. Overflow starts at the actual wall opening invertZ863,11 mm below the rim. These are design datums, not cutter-manufacturer-approved cutting settings. The final water-check report calculates displaced volume from the current CAD and separates operating, overflow and brim cases.

## Gravity return

The left wall outlet is atY180 with centreZ826.48 and a24 mm bore. Its invertZ814.48 is2 mm above the local floor and2.48 mm above the lowest front floor; a small residual puddle remains. This is not a complete sludge-emptying claim.

A smoothOD28/ID24 steel stub ends atX102 and is welded to the wet wall. It is not anNPT male thread. A swept90-degree adapter turns toward the rear-facing full-port valve atX82,Y200..254. A second fitting turns downward. The flexible line is modeled asID25/OD34 with tangent100 mm centreline-radius bends, outside the cabinet atX82, then across the rear bay to an outlet atX400,Y800,Z410. Its path has no upward section. The tight20 mm bends adjacent to the valve are selected-fitting envelopes, not permission to kink a hose.

The valve, two adapters, unions/seals, hose and retainers remain unselected. Verify actual threads, pressure-free drainage configuration, port minimum, bend radius, temperatures, chemical compatibility, handle access and hose retention before a purchasing or machining release. Flow depends on the selected fittings, hose, debris and available head; CAD clearance is not a drain-time test. A removable coarse catch basket/sludge service arrangement also needs selection.

The independent right-wall overflow is40×8 mm atY880..920,Z863..871. It leads to an open vertical collector, a sloping open gutter and a deflector ending atZ410 over the receiver. It must remain separate from the shutoff drain. Its supports and flat patterns are not fabrication released. A blocked-drain fill test must establish flow/freeboard; the presence of an opening does not prove overflow capacity.

## Red receiver

The conservative clearance envelope is712×470×389 mm atX219..931,Y700..1170,Z0..389. It includes the handle/lid dimensions in the [Amazon candidate listing](https://www.amazon.com/dp/B0HN3Q77HR), consistent with the larger external dimensions of the [Husky20-gallon model246842 listing](https://www.homedepot.com/p/311485319). The user's photo gives smaller body dimensions; the larger envelope is retained. Brand/part identity and actual body taper must be checked on the received unit.

A listing's20-gallon storage designation is not a measurement of65 litres usable water capacity. Require at least65 L measured usable capacity with freeboard, a sustained filled-load/leak test, material/temperature compatibility and suitable support under the complete base. The rectangular CAD shell is a clearance envelope; its much larger internal geometric volume must not be used as a tote capacity or liquid rating. Its mass is also only an estimated shell mass. The tote is supported by the floor and is excluded from machine-frame ballast and foot-load calculations.

The removable lid is represented atZ389..391, with a50 mm drain-return opening atX400/Y800, a40×50 mm overflow opening atX880/Y875 and a permanently open25 mm vent atX700/Y1000. Return outlets atZ410 have19 mm air gap above the modeled lid,21 mm above the body. Verify the real lid shape/clips and return clearances. Keep the receiver vented and unpressurized; the owned compressor and CV-15HS venturi are not connected to this circuit.

Full upward hinging is unavailable under the pan: a470 mm lid swing above a389 mm box would reach about859 mm. A lid-removal/hatch service path has not yet been established. The present cabinet floor/back and the fixed returns constrain forward withdrawal. Do not claim that the tote or lid can simply be pulled out with the machine assembled. A split hatch or revised service opening must be designed and checked before release.

## Storage and thermal qualification

The wood cassettes store in a closed Al hood below the pan. Its primary roof is0.8 mm Al atZ710, with a sacrificial1.9 mm plain-steel shield atZ715..716.9; the clear air gap is4.2 mm. The pan floor is at least about96 mm above the shield. The separate floor cabinet has four columns and rear anti-tip links; it does not hang from the hot pan or add ballast to the main frame.

The steel roof is a heat/spatter barrier, not a proven temperature rating. The narrow pan-side shadow strips likewise do not qualify exposed Al ledgers, guides, seals or cables for plasma. Complete removable ledger/guide shields, edge closures and thermal tests are still required. Use a provisional commissioning limit of35 C for return water and the wood-storage environment until the received tote, adhesive and coatings establish suitable limits; this is a design requirement, not a supplier rating. The receiver also needs its own qualified heat-shadow protection. Test representative cutting duration and blocked/leak scenarios with the cabinet closed, then inspect the shield and measure storage/receiver temperatures.

The baseline sequence is: isolate motion/tool power; allow the pan and contents to cool; verify receiver usable capacity/freeboard and open vent; clean accessible sludge; open the gravity valve; confirm both returns are unobstructed. No compressed-air pressurization, venturi transfer or automatic solenoid actuation is part of this revision. Future automation requires the actual owned valve data, level/temperature feedback and a defined failure state before it enters CAD or procurement.

See review/water-check.json for current geometry/capacity evidence, review/transfer-check.json for cassette conversion, review/bed-screen.json for conditional load screens, and review/bed-fabrication.csv for all candidate parts including explicit unselected interfaces. No price or cart change is made by this design work.
