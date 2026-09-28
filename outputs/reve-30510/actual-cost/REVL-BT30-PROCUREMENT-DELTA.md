# GM1 Rev L, BT30 variant — what the BT30 spindle changes on the shopping list

The BT30 variant is Rev L with a 3.2 kW BT30 ATC spindle in place of the 1.5 kW ER11, and a six-pocket fork rack on the dock in place of the RapidChange magazine. The design is in [RevL-BT30-CAD](../../../output/release-review/RevL-BT30-CAD/README.md). The [Rev L delta](REVL-PROCUREMENT-DELTA.md) still applies to the dock's guides, drive, stops, sensors and the controls M12–M14; this page lists only what the BT30 adds, drops or changes.

**Nothing here is priced.** The [actual-price audit](REAL-COST.md) stands at the Rev J scope, **$5,336.10**. The figures in brackets are order-of-magnitude retail guesses for planning, not quotes.

## Changed

| Was (Rev L, ER11) | Now (BT30) |
|---|---|
| 1.5 kW 110 V ER11 air-cooled spindle, Ø65 × 259, 2.7 kg | **3.2 kW 220 V BT30 ATC spindle**, the owner's Amazon listing B0HJ89DJL6 ("3.2KW 24000RPM 4-pole BT30"), drawn as Ø105 × 450 and 15 kg. Read the listing for the body diameter, length, mass, drawbar air pressure, sensors and the rated frequency (4-pole at 24,000 rpm is 800 Hz) before ordering the clamp stock (about $500–$800) |
| 1.5 kW VFD in the cabinet (Rev K) | **4 kW single-phase-input VFD with at least 800 Hz output**, set for the spindle's 220 V / 800 Hz V/f curve (about $150–$250). It is bigger than the Rev K plate allows (K_VFD_PLATE, 210 × 390): check its size and its heat (about 150–200 W at full load) against the cabinet |
| RapidChange ER11 magazine (kit, $400–$900) | **Not needed.** A fork rack: a 5/8 in aluminum bar and six plastic BT30 forks (below) |
| ER11 collets and nuts | **BT30 holders** (below) |
| Split spindle clamp 110 × 90.5 × 40, two halves | **One-piece clamp 130 × 155.5 × 100** bored 105, slit at the front |
| Z drop adapter 110 × 220 × 1/2 in | **110 × 220 × 3/4 in** (the same outline, eight clamp holes, deeper counterbores; the plasma drop bracket fits it unchanged) |
| Spindle cradle on the reservoir lid (two 110 mm cradles) | **Two 140 mm cradles** further left, for the spindle with its clamp on it |

## New purchased parts

**Tooling**

- 6 × BT30 tool holder with a 60 mm projection (BT30-ER32-60 or ER20-60; the rack is drawn for 60 mm), each with its pull stud (the spindle listing says which stud: MAS403 P30T 45° is usual) (about $25–$40 each).
- ER32 (or ER20) collets for the owner's shanks; ER nuts if not supplied with the holders.
- 6 × BT30 tool fork, plastic with spring lips, for a 46 mm flange (about $8–$15 each).
- A tool setter is still not drawn (it could sit on the tray's right strip).

**Air** (the ER11 machine had no air)

- Compressor able to hold 6–8 bar at the spindle during a release (a release uses about 0.3 L each), with a receiver of a few litres near the machine, a filter-regulator and a water separator.
- 1 × 5/2 (or 3/2) solenoid valve, 24 V DC, 1/4 in, for the drawbar release; 1 × 3/2 valve for the taper blow-off if the spindle has a separate port; tubing, push fittings and a pressure switch (24 V, set at 5.5 bar).

**Controls (M15–M16 in the BT30 README; not built into gm1_circuit.py)**

- 2 × Finder 40.52.9.024.0000 relay and 95.05 socket (K_DRAWBAR: valve; K_RELEASED: the spindle's "released" sensor).
- Interface board additions: 2 more PC817 optocouplers with resistors (the spindle's clamp sensors on MCP23017 GPA6 and GPB4), and the ULN2803A channels for GPB2 (valve) and GPB3 (blow-off), already fitted for M13.
- A VFD with a programmable relay output set to "running", for the release interlock.
- Supply: 3.2 kW at 220 V single phase draws about 18 A at full load; the router mode's circuit must carry it (the plasma cutter is on its own circuit and never runs at the same time).

**Fasteners**

- 8 × M6 × 20 socket head (clamp to adapter; the same as Rev L's four, plus four).
- 2 × M8 × 60 socket head and 2 × M8 nyloc (clamp pinch bolts).
- 6 × M5 × 16 socket head (rack bar to the tray, from below).
- 12 × M5 × 12 (forks to the bar; not drawn).
- 4 × M6 weld nut and 4 × M6 × 20 socket head (cradle bases).

## New fabricated parts and their stock

| Part | Qty | Stock | Note |
|---|---:|---|---|
| Spindle clamp, one piece, 130 × 130.5 × 100 with two 20 × 25 lugs | 1 | 6061 billet, about 135 × 160 × 105 | Bore to the measured spindle +0.03 with the slit shimmed closed; eight blind M6 in the back, Ø8.5 through the lugs |
| Z adapter 110 × 220 × 3/4 in (replaces Rev L's 1/2 in) | 1 | 3/4 in 6061 plate | Eight 6.6 clamp holes with 10.5 counterbores 12.35 deep (6.7 web); front counter-slots 12.95 deep (6.1 web); carriage slots wait for the delivered slide |
| Rack bar 520 × 80 × 5/8 in, six 52 mm open slots, six M5 | 1 | 5/8 in 6061 plate or bar | Pockets at 90 mm, X350–800 |
| Carrier, 590 × 193 U-plate with six 56 mm open slots (replaces Rev L's 167 mm carrier) | 1 | 1/4 in steel plate | The tray starts 26 mm further forward and runs to Y1165 |
| Rear upstand 530 × 7.65 on edge | 1 | 1/4 in steel strip | The front upstand is dropped: the bar stiffens the front |
| Cradle plates 140 × 80 × 6 and bases 30 × 150 × 1/8 in | 2 + 2 | Steel offcuts | Replace Rev L's ER11 cradle; four new 6.6 holes in the reservoir lid |

Rev L's magazine saddles and risers are not made. About 4 kg of aluminum and steel in all; the dock with its bought parts is about 14 kg with six holders, and the module about 77 kg.

## Rough total against Rev L

Spindle about +$400 over the ER11, VFD +$100, six holders and forks about +$250, air about +$150–$300 (more if there is no compressor), clamp and adapter stock about +$100, relays and optocouplers about +$30, minus the RapidChange kit (−$400 to −$900): **roughly the same money as Rev L with the RapidChange kit, or a few hundred dollars more**, for a 3.2 kW spindle that changes BT30 holders instead of bare ER11 cutters. The [BT30 README](../../../output/release-review/RevL-BT30-CAD/README.md) lists what the variant costs in other ways: a 20 kg head on the ZBX80, 26 mm of Y reach moved forward, and stored tools limited to 30 mm below the nut.

## 28 September additions

The [Rev L delta's 28 September section](REVL-PROCUREMENT-DELTA.md#28-september-additions-tool-setter-work-light-pilot-lamps-second-e-stop) applies here unchanged: the tool setter sits on this variant's carrier wing at the same X (896) on its own pocket line (Y1073.65), the light bar is on the same gantry beam, and the lamps, light switch and second E-stop are cabinet parts. Nothing BT30-specific is added.

## How to use this

Choose the spindle first: its diameter sets the clamp bore and its length the cradle spacing. Check the listing's numbers against the envelope (Ø105 × 450, 15 kg) before cutting anything. The rest of the [Rev L build order](../../../output/release-review/RevL-CAD/BUILD-ORDER.md) stands; the rack replaces step 5's magazine saddles.
