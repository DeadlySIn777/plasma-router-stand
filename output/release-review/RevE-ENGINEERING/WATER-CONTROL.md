# Rev E water transfer and interlocks

Engineering selection, 2026-09-24. This defines the water subsystem and its interface to the separate Kraken controls package. It is not a claim that hardware has been assembled or tested. Amazon prices were read with delivery set to Alto, GA 30510; the drain timer uses the manufacturer offer with unquoted shipping; tax is excluded. `water-bom.json` separates actual displayed prices from allowances.

## Arrangement and corrected inventory

Use gravity to drain the pan into the permanently vented reservoir, and a continuous-duty 24 V pump to refill from its clarified compartment. Keep the compressor and CV-15HS vacuum generator available for their intended pneumatic uses; neither connects to this fabricated water tank. No pressurized water reservoir, vacuum tank, accumulator, or compressed-air demand is part of this design.

The reservoir has 900 x 600 x 250 mm internal dimensions, nominal gross capacity 135 L. Its lower profile makes room for the controls cabinet within the stand. Charge the complete circuit with **115 L maximum**, measured only with the pan fully drained and the pump stopped. Earlier tank dimensions, the 110 L assumption, 220 mm settling weir and 75 mm-high pickup are superseded.

| Item | Rev E value |
|---|---:|
| Internal reservoir floor datum | Z178.048 mm |
| Settling weir height above floor | 50 mm |
| Clarified pickup axis above floor | 25 mm |
| Pickup pipe | NPS 1/2 SCH40, OD21.3 / ID15.8 mm |
| Reservoir low-level pump trip | 55 mm above floor, Z233.048 |
| Plasma minimum operating water level | Z810 mm |
| Normal fill stop | Z820 mm |
| Passive pan overflow crest | Z825 mm |
| Independent high-high trip | Z827 mm |
| Pan rim / slat top | Z835 / Z850 mm |
| Passive overflow | NPS 1.5 SCH40, ID40.9 mm |

The float trip levels are **wet-calibrated setpoints**, not the locations of their mounting threads. Use adjustable brackets and record actual switch hysteresis during commissioning. Four pan floats must be shielded from sparks and loose slats in removable, freely communicating guards outside the tool envelope. Keep the independent high-high float in a separate guard from the fill-stop float. Put the reservoir low float in the clarified bay. Five switches are used; one supplied spare remains unused.

The pan holds approximately 79.9 L at Z820 after slat and comb displacement. Allowing 1 L in hoses, about 34.1 L remains in the reservoir. Water above the 50 mm weir connects both bays; the remaining level is approximately 63.4 mm above the floor, with about 4.5 L above the low-level stop. The analytic area conservatively treats the baffle as occupying the full depth. This is a screening calculation, not a substitute for measuring the fabricated tank. Settled material, evaporation and leaks consume that margin. Clean the tank rather than increasing inventory above the mark.

The reservoir emergency overflow is an internal standpipe at X500/Y1270, with its crest at Z420.048, 242 mm above the internal floor. Nominal capacity to that level is approximately 130 L after the conservative baffle-area correction. A further 1 L displacement reserve leaves approximately 129 L, providing about 14 L of space when all 115 L returns. Confirm this reserve against the final internal solids and measured fill. Keep the tank permanently vented. Route its emergency overflow to the visible catch vessel inside the machine footprint; it is an overfill indication, not a substitute for limiting inventory.

## Selected pump, valve and filter

Final CAD comparison: modeled pan water at Z820 is 79.616 L, slightly below the conservative 79.912 L inventory calculation. Modeled reservoir solids occupy 0.5323 L below the overflow crest, within the 1 L displacement reserve. `state-summary.json` records the contributing solids. Retain the conservative inventory limits; fabrication and wet calibration still verify actual volumes.

- **Pump:** SEAFLO SFDP2-018-120-31, 24 V, 1.8 GPM / 7 L/min open flow, 6 A maximum, 3/8-18 FNPT ports. The manufacturer lists continuous duty. Allow approximately 13-18 minutes to refill 80 L through the installed plumbing, then measure the real time. The 120 PSI rating is the pressure-switch shutoff setting; this application has an open discharge. Never install a shutoff or spray nozzle on the discharge. Both suction and discharge hoses/fittings must tolerate the pump's full shutoff pressure in case of a blockage. [Supplier](https://seaflodirect.com/seaflo-24v-1-8-gpm-120-psi-31-series-dc-diaphragm-pump-self-priming-high-pressure-water-pump-for-rvs-boats-agriculture-and-cleaning-w-built-in-pressure-switch/), [manufacturer drawing and duty table, printed page 04](https://seaflolatinamerica.com/wp-content/uploads/2024/03/2018-industrial-pumps-7mcom.pdf), [Amazon](https://www.amazon.com/dp/B0DW67Z14F).
- **Drain valve:** U.S. Solid USS-MSV00009, 1-inch NPT, stainless, two-wire auto-return normally closed, operated at 24 VDC. It opens on power and normally closes when power is removed. Allow 10 seconds for closure; it has no position-feedback output. Its capacitor requires about one minute energized before automatic return is assured. The design contains the complete inventory whether this valve is open or closed, and never relies on an uncharged valve to prevent a spill. It cannot be manually turned. [Manufacturer](https://ussolid.com/products/u-s-solid-motorized-ball-valve-1-stainless-steel-electrical-ball-valve-with-full-port-9-24-v-ac-dc-2-wire-auto-return-html), [manual](https://file.ussolid.com/content/JFMSV/JFMSV-User-manual.pdf), [Amazon](https://www.amazon.com/dp/B06WWR1FRK).
- **Inlet strainer:** SEAFLO SFWS-500-02, 1/2-inch NPT ports, 50-mesh stainless screen and removable clear bowl. Place it before the pump, accessible for cleaning. It removes coarse debris; it does not make abrasive plasma fines harmless. The settling compartment and regular cleaning are still necessary. [Amazon](https://www.amazon.com/dp/B0H7K7G8GF).

Pump drawing envelope is 210 x 86 x 114.5 mm. Four nominal diameter-5 mounting holes have 58 mm longitudinal and 85 mm transverse spacing; the rear pair is 46 mm from the motor-tail end. Use the rubber feet without crushing them. Reserve flexible hose space at both side-facing ports; the manufacturer does not dimension the port axes. The product-family drawing must be compared with the delivered bracket before drilling a replacement part. The valve's Amazon envelope is 4.13 x 3.23 x 2.91 inches without port datums: reserve a conservative 125 mm cube and support adjacent pipe, without inventing valve bolt holes or a fixed face-to-face dimension.

The refill discharge must end above the pan rim with a visible **25 mm minimum air gap** above the maximum possible water surface, under a splash guard outside the tool path. This prevents a stopped pump or failed internal check valve from siphoning the pan back. Do not submerge the hose outlet. Route both gravity returns continuously downhill with no valve on the emergency overflow. Keep the drain union, basket removal path and filter bowl accessible.

## Operator sequence

1. Stop the job, park the head, inhibit tool power with the existing keyed SETUP control, and verify the controller is idle. Mode changes never occur during a job.
2. Selecting **ROUTER** automatically inhibits refill and opens the drain. The drained float must indicate low water continuously for 60 seconds before router-water-ready becomes true. This delay also provides the valve capacitor charging interval. The drain remains open throughout router mode. Router permission additionally requires the actual bed-lock interlock from the mechanical design.
3. To prepare plasma, remove the router bed. Rev J: release the six M10 drawdowns and lift the one-piece module out through the front of the machine with the overhead hoist (`output/release-review/RevJ-CAD/README.md`). Rev G alternative: store its six spoilboards, six panels and four beams on the internal racks in the order given in `output/cad-repair-2026-09-25/bed-architecture.md`. Remove chips, coolant residue and any wood dust from the pan, slats, seat pads and rails, and inspect before confirming bed-clear. Select **PLASMA** and keep SETUP selected. The drain closes; the 10-second timer prevents refill until its closing time has elapsed. Press guarded **FILL** once. The pump latches on and stops at the normal fill float. STOP, reservoir low, high-high, lost bed-clear, a mode change, loss of control power or the main stop chain also drops the fill latch. The release-to-rearm circuit requires the button to be released and pressed again after an interruption; that function must be verified in the terminal drawing and physical acceptance test.
4. Select RUN only after the level is stable. Plasma-water-ready requires minimum level, no high-high condition, bed-clear, no active transfer, and drain-close delay complete. Refill during cutting is inhibited. Loss of minimum level removes tool permission and asserts the controller's door/permissive input. Refill requires another deliberate SETUP/FILL operation.
5. A guarded maintained **DRAIN** override opens the drain and disables both tool permission and the fill latch. Returning it to AUTO does not restart refill. With all power absent the selected valve is not a manual drain; retain water safely until control power or a planned service-drain method is available.

## Hardwired logic and controller boundary

All field contacts in the following table close in the named healthy state, so an open cable inhibits the corresponding operation. Fit suppression across DC relay coils. Float switches carry relay-coil current only, never pump or valve current. The selected floats are specified for 0.5 A / 10 W maximum. Use coils below0.1 A each and keep the aggregate load through any float below0.2 A /4.8 W, including parallel relay coils fed from a shared healthy-contact chain.

| Tag | Healthy / asserted state |
|---|---|
| F_EMPTY | Pan below calibrated drained threshold; not a claim of a bone-dry pan |
| F_MIN | Pan level above plasma minimum |
| F_STOP | Pan below normal fill-stop level |
| F_HH | Pan below independent high-high level |
| F_LOW | Reservoir above minimum pump level |
| B_CLEAR | Plasma bed-configuration permissive; sensing/keyed confirmation still owned by overall machine |
| B_LOCK | Router bed-configuration permissive; sensing/keyed confirmation still owned by overall machine |
| SETUP | Existing keyed tool-power inhibit active, controller idle confirmed by operator |
| STOP_OK | Water STOP and existing machine stop chain healthy |

Use six Finder 40.52.9.024.0000 DPDT auxiliary relays with 95.05 sockets: K_ARM for release-to-rearm, K_FILL for the self-holding fill command, K_DRAIN for drain command and changeover interlock, K_MIN and K_EMPTY for float indication, and K_READY for two isolated permissive outputs. No relay remains spare. The guarded FILL button needs mechanically linked NO and NC contacts. K_ARM drops whenever FILL_ALLOWED is lost and cannot rearm while FILL remains pressed. The nominal coils draw 27 mA. Two Carlo Gavazzi RM1D060D20 DC SSRs, P_CMD and P_LIMIT, switch the pump positive lead in series; their inputs draw at most 16 mA each. The conservative shared float-chain demand is 112 mA using a 40 mA auxiliary-coil envelope. See [the terminal allocation](WATER-ELECTRICAL-REVIEW.md) for actual contacts, branch fuses, suppression, diode isolation and remaining panel-interface requirements. These documented devices replace the generic auxiliary pack and motor-relay allowance in the master BOM.

```text
DRAIN = ROUTER mode OR guarded DRAIN override
T_CLOSE = 10 s on-delay while DRAIN is false and PLASMA is selected
T_DRAIN = 60 s on-delay while ROUTER AND DRAIN AND F_EMPTY

FILL_ALLOWED = PLASMA AND SETUP AND B_CLEAR AND T_CLOSE
               AND NOT DRAIN AND STOP_OK AND F_LOW AND F_HH AND F_STOP
K_ARM = FILL_ALLOWED AND (FILL released/NC OR K_ARM holding contact)
K_FILL = FILL_ALLOWED AND K_ARM AND (FILL pressed/NO OR K_FILL holding contact)
P_CMD input = same command node as K_FILL coil (wired in parallel)
P_LIMIT input = PLASMA AND SETUP AND B_CLEAR AND STOP_OK AND F_LOW AND F_HH
                AND T_CLOSE AND NOT DRAIN

24V+ -- pump branch fuse -- P_LIMIT output -- P_CMD output -- pump+ ; pump- -- 0V

ROUTER_WATER_READY = ROUTER AND T_DRAIN AND F_EMPTY AND B_LOCK
PLASMA_WATER_READY = PLASMA AND T_CLOSE AND F_MIN AND F_HH AND B_CLEAR AND NOT DRAIN
K_READY = STOP_OK AND F_HH AND RUN AND NOT K_FILL AND NOT DRAIN_OVERRIDE
          AND (ROUTER_WATER_READY OR PLASMA_WATER_READY)
```

F_HH directly interrupts P_LIMIT's input circuit independently of the fill-stop relay path. Thus a failed-short P_CMD still loses pump power when high-high or low-level turns off P_LIMIT. These are ordinary controls, not a certified safety relay system; simultaneous failed-short outputs are outside this single-fault screen. SSR off-state leakage means they are not service isolators. Passive overflow must still pass the complete pump flow. No additional safety-category or PL claim is made.

T_CLOSE is BAOMAIN AH3-3 AC/DC24V, 0-60 second range, set to10 seconds. **Only one pole is timed; the other is instantaneous.** Use its timed normally-open pole and verify the printed connection diagram on the actual timer. The drawing must not mistakenly treat both poles as delayed. T_DRAIN is the **BAOMAIN AH3-3-24V-3Min**, 24 VDC, three-minute range with socket, [manufacturer variant 42107472478393](https://baomain.com/products/baomain-ah3-3-24v?variant=42107472478393). Its observed price is $10.79; shipping to Alto remains unquoted. Set it nominally to 75 seconds and calibrate to at least 60 seconds. This replaces the unselected six-minute-range allowance; verify the delivered terminal diagram and the contact duty of the selected low-power coil. A60-second maximum-range timer is not sufficient to guarantee a minimum60-second dwell at the low end of its timing tolerance.

K_READY pole1 joins the existing isolated **PG6 / EXP2 pin7** permissive/safety-door interface. K_READY pole2 gates the existing hardware tool-enable chain. Do not apply24 V to PG6, and do not connect these floating contacts to plasma work return. The Kraken firmware does not run this sequence. Existing E-stop hardware, tool selector, door/breakaway interfaces, contactors, enclosure, DIN rail and controller isolation are shared-control items, not charged again to the water BOM.

This design has no independent machine-motion IDLE signal. SETUP removes tool permission and reports door-open to grblHAL; the operator must stop/park and confirm IDLE before changing beds. Do not advertise an automatic bed-swap cycle or hardwired axis standstill proof. B_CLEAR and B_LOCK are required interface conditions, not existing proven sensors. With the Rev G bed, a single presence switch or guard key cannot prove that all parts were removed. With the Rev J one-piece module, one presence sensor at a seat pad can show whether the module is in or out. Neither can prove that every bed fastener was tightened correctly (Rev J: six M10 drawdowns; Rev G: 16 panel bridge clamps, eight beam drawdowns and four front-seat screws). If the final implementation uses keyed operator confirmation, its label and procedure must explicitly require removal/installation inspection and fastener-torque checks. Such confirmation must not be described as automatic preload verification. Actual sensors/key contacts and their mounting must be defined by the mechanical/control design before the complete machine is released. The analytical contact-state check in `water-verification.json` covers 147,456 combinations, three release-to-rearm sequences, and the inventory arithmetic; it does not validate physical contact allocation, pickup/dropout races or wet performance.

## Plumbing quantities and electrical allowance boundary

The allowance covers: one1.5F-NPT to1M-NPT pan reducer; one1-inch union; one1M-NPT-to1-inch-barb drain tailpiece; one1.5F-NPT cleanout cap; one1/2F-NPT-to1/2-inch-barb pickup fitting; two1/2M-NPT-to1/2-inch-barb strainer fittings; two3/8M-NPT-to1/2-inch-barb pump fittings; compatible thread sealant; short nipples as required by the valve's undimensioned thread engagement. Final nipple lengths remain adjustable assembly dimensions, not CNC-cut structural dimensions. No NPSM/NPT substitution is permitted without the correct sealing adapter.

Allow1.5 m of1-inch drain hose,3 m of reinforced1/2-inch suction/discharge hose rated at least150 PSI at the operating temperature, and twelve stainless clamps. Keep suction short, avoid high loops, and reserve more than the published minimum bend radius. The vent and passive overflow are fabricated pipe already included in the pan/tank package. The reservoir cleanout is capped during operation; removal is a deliberate maintenance operation after draining.

A shared Mean Well LRS-350-24 supply provides24 V /14.6 A for the pump, valve and low-power controls. Amazon B013ETVO12 was$31.40 with free eligible-batch shipping; it is listed as **shared, zero incremental water cost** in this BOM. Preserve at least8 A of its output budget for water functions, including relay loads/start allowance. The terminal allocation selects a 10 A fuse and 14 AWG pump branch for conductor protection, with separate 1 A control and valve/timer branches. The pump's own fuse requirement and actual starting waveform still need checking; the branch fuse does not establish internal motor or semiconductor protection. Supply mains wiring and protected mounting belong to the common electrical design. [Mean Well datasheet](https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF).

## Acceptance evidence still required

- Fill with measured water, wet-calibrate all five floats, check their hysteresis and normal contact state, then unplug each sensor in turn to verify inhibition. Verify drained means the residual film level intended by the CAD slope, after the full60-second dwell.
- Demonstrate that disconnecting F_HH stops the pump even with P_CMD temporarily commanded on. Demonstrate that normal fill completion, STOP, low level and mode change unlatch refill and require a new FILL action.
- Test the enlarged overflow at maximum actual pump flow with the normal fill-stop held in the fill state. Water must remain below Z835 and return freely to the reservoir. A circular-weir screening calculation gives about13.7 L/min at10 mm head for ID40.9 and Cd0.6; entrance/pipe losses and fouling require the real test.
- Drain all115 L from the system to the tank without overflow. Confirm no unintended siphon with the pump off and verify the inlet air gap, basket service path, strainers and spill routing.
- Run the actual fill interval at the highest expected enclosure temperature, record pump current and temperature, verify power supply recovery and inspect hose leakage. Keep the pump below its60°C liquid limit and the valve actuator within its40°C ambient limit.
- Verify the physical relay/timer terminal diagram, power-relay motor suitability, pump fuse, B_CLEAR/B_LOCK implementation and complete schematic before energizing the assembled panel. These are concrete release gates, not completed tests.

Source drawings retained in `../sources/SEAFLO31-drawing.png`, `SEAFLO-industrial-2018.pdf`, `USS-MSV-manual.pdf`, and their rendered pages. The ordinary SEAFLO33 intermittent-duty pump is not the selected refill pump.
