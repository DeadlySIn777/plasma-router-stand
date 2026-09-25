# Water electrical closeout — Rev E, 2026-09-24

This is the selected water-circuit terminal allocation. The Finder auxiliaries and Carlo Gavazzi SSRs have been adopted in water-bom.json, replacing the generic Amazon relay pack and motor-relay allowance. It does not declare the complete panel released. No physical tests have been performed. The main machine's isolator, stop chain, mode selectors, bed-confirmation contacts, controller isolation and tool-power circuits remain shared interfaces.

## Component decision

The Amazon VAMRONE MY2NJ six-pack has no recovered manufacturer coil-current specification or authoritative socket drawing. Do not copy an Omron MY2 diagram onto a similarly named relay. A documented replacement is six **Finder 40.52.9.024.0000** relays with six **95.05** DIN sockets. Each relay has a 24 VDC, nominal 27 mA coil and two changeover contacts. Terminal names are A1/A2, 11 common/12 NC/14 NO, and 21 common/22 NC/24 NO. The manufacturer permits suppressed DC13 control loads using its DC1 life guidance; these relays switch only small control loads and the valve, not the refill pump. [Finder primary datasheet, pages 3, 8–9 and socket drawings](https://cdn.findernet.com/app/uploads/S40EN.pdf).

Observed distributor prices are $7.56 per relay and $7.31 per socket: **$89.22 for six complete positions**, before shipping, retaining six coil-suppression diodes in branch wiring. This replaces the $31.99 generic six-pack in the master BOM. [Relay and associated socket offer](https://www.digikey.com/en/products/detail/finder-relays-inc/40-52-9-024-0000/10055849). Amazon was checked first; a traceable exact offer and full specifications were not established there. A1 is positive in this design because of the external suppression diode, even though the bare coil itself is not polarized.

For the pump, select **two Carlo Gavazzi RM1D060D20 DC SSRs**, P_LIMIT and P_CMD. Published limits include 1–60 VDC output, 20 A continuous subject to thermal conditions, 30 A repetitive overload for 1 second, and maximum 16 mA control input. The manufacturer explicitly requires a diode for inductive loads. Terminals are 1+ and 2− for the switched load path; 3/A1+ and 4/A2− for control. The no-heatsink table covers 6 A through 70°C, but still requires attachment to a heat-dissipating mounting surface. Use the metal backplate and keep enclosure ambient at or below 40°C for the valve and other equipment. [Primary SSR datasheet](https://www.gavazziautomation.com/fileadmin/docs/pim/DATASHEET/ENG/SSR_RM1D.pdf).

DigiKey displayed **$66.50 each, $133.00 for two**, with shipping unquoted. This supersedes the $30 motor-relay allowance in the master BOM. [Exact offer](https://www.digikey.com/en/products/detail/carlo-gavazzi-inc/RM1D060D20/13277978). These are pump switches, not external motion drivers. Start-current duration and supply recovery still require commissioning; a 6 A running rating alone does not establish the pump's inrush waveform. SSRs can fail short and have off-state leakage; they are not service isolators. Two series devices provide separately controlled interruption, not a safety-category claim.

Use **onsemi MBR20100CTG** for motor flyback: connect its two anodes, pins 1 and 3, together to pump negative; connect common cathode pin 2 to pump positive. Its exposed tab is also cathode and must remain insulated from the enclosure. This 100 V dual Schottky device has 10 A per leg under specified thermal conditions. Mount it on an insulated supported terminal assembly near the pump cable termination, protect exposed leads and verify pulse heating during stop tests. It is normally reverse-biased. Do not put this diode in series with the pump. [Primary diode datasheet](https://www.onsemi.com/pdf/datasheet/mbr20100ct-d.pdf). Use six **Vishay 1N4007-E3/54** coil diodes, bands to A1, plus two of the same type for the drain-command OR circuit below. [Primary coil-diode datasheet](https://www.vishay.com/docs/88503/1n4001.pdf). The SSR control inputs need no flyback diode because they are not coils. Do not add an external diode across the electronic auto-return valve without its manufacturer's approval.

## Branch protection and terminals

Use a 10 A **Littelfuse 0287010.U** pump-branch fuse as the initial conductor-protection selection, in a **0FHA0001ZXJ** 20 A/32 VDC inline holder. Use 14 AWG stranded copper for the pump branch, including return, and retain the supplied pump lead size only where the manufacturer permits it. This is not a semiconductor-coordinated fuse or a claim of internal pump overload protection. The exact pump manual/nameplate fuse requirement and the measured starting pulse must be checked; do not increase the fuse above 10 A to conceal a startup problem. [Fuse offer/specification](https://www.digikey.com/en/products/detail/littelfuse-inc/0287010-U/3996901), [holder primary datasheet](https://www.littelfuse.com/~/media/commercial-vehicle/datasheets/automotive-fuse-holders/ato/littelfuse-fuse-holders-ato-fha-datasheet.pdf).

Provide a separate 1 A control fuse, Littelfuse 0287001.L, and separate 1 A valve/timer branch fuse of the same type. Use 18 AWG stranded copper for these branches, insulated ferrules where the terminal manufacturer allows them, covered terminal strips rated at least 30 VDC/15 A, and a dedicated 0 V return bus. All 24 V branches originate after the common machine control-power disconnect. The 14.6 A supply has at least an 8 A water-function allocation in the existing design; measure total concurrent control demand and pump startup recovery. Do not substitute an AC-only SSR.

| Terminal | Function |
|---|---|
| XW:1 / XW:2 | 24 V supply / 0 V supply |
| XW:3 | C: output of 1 A control fuse |
| XW:4 | V: output of 1 A valve/timer fuse |
| XW:5 / XW:6 | Pump positive / pump negative |
| XW:7 / XW:8 | Drain-valve positive / negative |
| XW:11–12 | F_EMPTY healthy-when-drained contact |
| XW:13–14 | F_MIN healthy-above-minimum contact |
| XW:15–16 | F_STOP healthy-below-fill-stop contact |
| XW:17–18 | F_HH healthy-below-high-high contact |
| XW:19–20 | F_LOW healthy-above-reservoir-low contact |
| XW:21–22 | External STOP_OK dry contact pair |
| XW:23–24 | B_CLEAR confirmation contact pair |
| XW:25–26 | B_LOCK confirmation contact pair |
| XW:31–32 | Floating controller-permissive output |
| XW:33–34 | Floating hardware-tool-enable output |

Pump power: XW:1 → 10 A fuse → P_LIMIT:1+ → P_LIMIT:2− → P_CMD:1+ → P_CMD:2− → XW:5 → pump+. Pump− → XW:6 → XW:2. Both SSR 4/A2− terminals go to XW:2. The MBR20100CTG cathode goes to XW:5; both anodes go to XW:6. Do not connect the motor diode across either SSR output alone.

## Actual contact allocation

All contacts below are physical contacts; a named signal is a wire node, not an additional fictitious contact. All six relay A2 terminals and both timer terminal 2 connections go to 0 V. Use labelled jumpers where one node fans out.

The common mode selector needs **two independent PLASMA NO contacts P1/P2 and two independent ROUTER NO contacts R1/R2**. They must be mutually exclusive, open in OFF, and wired as individual contact blocks because their feeds differ. SETUP/RUN needs independent complementary contacts. DRAIN/AUTO requires a linked drain NO and auto NC. Guarded FILL requires linked NO and NC contacts, with break-before-make operation. These contact requirements must be reflected in the main selector's exact SKU and assembly; they are not satisfied by assuming an existing two-terminal switch has extra poles.

1. **Float indication:** C → XW:11 → F_EMPTY → XW:12 → K_EMPTY:A1. C → XW:13 → F_MIN → XW:14 → K_MIN:A1. Each float carries one 27 mA nominal coil.
2. **Healthy control node H:** C → XW:21 → STOP_OK → XW:22 → XW:17 → F_HH → XW:18 → H. This float contact feeds only the low-current circuits specified below, never the pump, valve or timer coils.
3. **Drain command:** C → MODE.R1 → D_R anode; C → DRAIN.NO → D_O anode. Join both diode cathodes to K_DRAIN:A1. These two diodes prevent the override from backfeeding the ROUTER node. K_DRAIN:11 = V; K_DRAIN:14 → XW:7 and node DV. XW:8 goes to 0 V. K_DRAIN:12 is unused. The drain remains commanded in ROUTER independently of STOP_OK, but loss of common control power removes valve supply.
4. **Close timer:** C → MODE.P1 → K_DRAIN:21; K_DRAIN:22 → T_CLOSE:7. T_CLOSE:2 = 0 V. K_DRAIN:24 unused. Thus T_CLOSE runs only in PLASMA with no drain command. H → MODE.P2 → B_CLEAR → T_CLOSE:8; timed NO T_CLOSE:6 creates node PC. T_CLOSE:5 and instantaneous terminals 1/3/4 remain unused.
5. **Independent pump limit:** PC → SETUP.NO → XW:19 → F_LOW → XW:20 → node L. L → P_LIMIT:3/A1+. L → XW:15 → F_STOP → XW:16 → node A (FILL_ALLOWED). T_CLOSE is additionally included in P_LIMIT's enable path; high-high and reservoir-low still interrupt P_LIMIT directly without depending on the K_FILL self-hold contact.
6. **Release-to-rearm:** A → FILL.NC → K_ARM:A1. In parallel, A → K_ARM:11, K_ARM:14 → K_ARM:A1. K_ARM:12 unused. A → K_ARM:21, K_ARM:24 creates node AF. K_ARM:22 unused. Holding FILL during recovery cannot initially energize K_ARM; release is required.
7. **Fill latch and power command:** AF → FILL.NO → K_FILL:A1. In parallel, AF → K_FILL:11, K_FILL:14 → K_FILL:A1. K_FILL:12 unused. **P_CMD:3/A1+ connects directly in parallel with K_FILL:A1**, not to an invented third relay pole. The SSR adds at most 16 mA to this coil-command node. K_FILL's second pole is reserved for ready inhibition below.
8. **Drain dwell:** DV → MODE.R2 → K_EMPTY:21; K_EMPTY:24 → T_DRAIN:7. K_EMPTY:22 unused. H → B_LOCK → K_EMPTY:11; K_EMPTY:14 → T_DRAIN:8. T_DRAIN:6 → D_R_READY anode; its cathode goes to ready-OR node J. T_DRAIN:5 and instantaneous 1/3/4 unused. Loss of drained indication removes timer power and interrupts its output supply. This timing also requires actual drain-command output DV; it does not prove mechanical valve position.
9. **Plasma ready:** PC → K_MIN:11; K_MIN:14 → D_P_READY anode; its cathode goes to J. K_MIN:12 and its second contact set remain unused. PC already requires healthy STOP/high-high, PLASMA, bed-clear and completed close delay. D_R_READY and D_P_READY are two additional Vishay 1N4007-E3/54 diodes, making ten small diodes total. They prevent either ready branch from backfeeding the other; do not omit them even if the level states are normally mutually exclusive.
10. **Final ready:** J → K_FILL:21; K_FILL:22 → RUN.NO → DRAIN.AUTO-NC → K_READY:A1. K_FILL:24 unused. When K_FILL is energized its NC contact removes ready. The mode contacts and timers prevent the two source branches at J from being simultaneously valid in normal operation.
11. **Isolated outputs:** K_READY:11/14 → XW:31/32. K_READY:21/24 → XW:33/34. Both NC terminals are unused. These are floating contacts. The first joins the existing isolated PG6/EXP2-pin-7 permissive interface; the second gates the hardware tool-enable chain. Never connect 24 V directly to PG6, and never use plasma work return as control 0 V.

The AH3-3 terminal mapping above is from the manufacturer's actual wiring image: **7 positive, 2 negative; 8 common/6 delayed NO/5 delayed NC; 1 common/3 instantaneous NO/4 instantaneous NC**. Retained images are `../sources/Baomain-AH3-3-primary.jpg` and `Baomain-AH3-3-primary2.jpg`. [Manufacturer product page](https://baomain.com/products/baomain-ah3-3-24v?variant=42107472478393). Set T_CLOSE to 10 seconds. Set the three-minute T_DRAIN nominally to 75 seconds, calibrating to at least 60 seconds. A terminal inspection remains a receipt check against substituted/counterfeit products, rather than a missing drawing.

## Electrical checks and remaining limits

With nominal 27 mA Finder coils, the worst filling demand through F_HH is K_ARM + K_FILL + two 16 mA SSR inputs = **86 mA**. Even using the previous 40 mA maximum coil envelope, this is **112 mA**, below the 200 mA design ceiling. K_READY cannot normally be energized while K_FILL is on. The timers, K_DRAIN coil, valve, K_MIN coil and K_EMPTY coil are deliberately fed outside that shared float chain. F_STOP carries the two fill-control coils plus P_CMD input, at most 96 mA using the 40 mA coil envelope. These are topology calculations, not measured currents.

The logical diagram is implementable with six DPDT relays, two SPST DC SSRs and each timer's single timed pole. It has not been simulated with contact bounce, pickup/dropout timing or component failures. Diode suppression increases relay release time: verify that a brief loss of FILL_ALLOWED drops K_ARM/K_FILL fully and that a held button cannot restart after restoration. Treat very short input interruptions as a separate acceptance test, not as proven by static truth tables.

The following remain genuine release limits:

- Complete the physical panel layout for the selected Finder auxiliaries and Carlo Gavazzi SSRs. The VAMRONE pack is superseded and is not charged in the current BOM.
- AH3-3 primary material specifies a resistive contact rating; a low-current DC rating for the actual timed output has not been independently documented. Its maximum switched load here is the fill-control node, below 112 mA at 24 V, but final DC suitability still needs manufacturer confirmation or substitution by a timer with documented DC control-load rating. The known terminal map alone does not close this.
- Exact mode-selector/contact-block assembly, bed-confirmation mechanism, and input isolation board remain shared-control selections. Finder's standard AgNi contact has a published minimum switching load; the controller interface must provide sufficient wetting current, or K_READY must use a documented gold-contact variant. Do not connect the relay directly to an unknown 3.3 V input and claim guaranteed contact reliability.
- Record the pump's actual starting current and duration, fuse instruction, SSR case temperature, 24 V supply recovery, diode pulse heating and all held-button tests. The fuse protects the branch; no Type 2 SSR short-circuit coordination or pump locked-rotor protection has been demonstrated.
- Shipping for the distributor substitutions and small components is unquoted. Diode, fuse and holder procurement remain within the existing branch-wiring allowance only if the final cart supports it; do not silently mark them free.

The unknown cutter's torch-start, arc-voltage and arc-OK wiring is intentionally outside this water circuit. Identifying an AG-60 torch does not identify the power-source interface.
