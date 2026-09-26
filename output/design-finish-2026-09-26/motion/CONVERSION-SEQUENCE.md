# Rev I conversion sequence

This is the prescribed **manual, nominal in-footprint sequence**. It uses the existing panel 1 as a temporary table in the empty rear-left panel 5 bay; no extra spoilboard, cart or lifting fixture is assumed. Current source-bound results are in [the acceptance index](../ACCEPTANCE.md).

1. **Prepare the machine.** Remove stock and cutter, drain the pan, clean and dry the work/table surfaces, park the gantry rear/high at X575/Y1275/Z100, and isolate power. Disconnect the spindle cable. The router stays mounted during the initial bed handling. No actual torch or tool lead is included in these transfer models.

2. **Store the six bare spoilboards.** Detach and stage rack top bars 1 then 2, then bare rods 1 then 2 using the restraint paths. Remove the 24 spoilboard screws to their defined tray positions; nut strips and their retainers stay on the panels. Store boards in order 4,3,2,1,6,5. Close the spoilboard guard and reinstall bare rods 2 then 1. Top bars remain staged.

3. **Store panels 6 through 2; retain panel 1.** Store panels 6,5,4,3,2 in that order. Lift the remaining front-left panel 1, move it to the normal empty rear-left bay, and lower it onto beams 3/4. Its bounds are X73.5–573.5/Y890.5–1287.5, with extrusion top Z940.8. Fit the existing four left clamp sets from beams 3/4. These provide the normal 10 mm and 3.5 mm end overlaps. This table is for the modeled head parts, at most 3 kg, with the existing joint qualification; it is not a standing or machining platform.

4. **Open the front portal while retaining beam 1.** Release beam 1's draw bolts, turn it onto its side and rest it on beam 2. Fit both temporary keeper bodies, gates, screws and locating screws before removing the two front seats. Beam1 stays captured on beam 2 during router removal.

5. **Park the router in the defined order.** Support the modeled 2.7 kg spindle continuously before releasing its pinch screws and front cap. Set the cap on panel 1; the rear clamp stays bolted to the adapter while the spindle is withdrawn and transferred through the open front portal into its cradles. Only after the spindle is supported there, remove and park the rear clamp. Move the front cap from panel 1 to its permanent lid position. Both clamp paths use the X430 bypass around the staged rack bar. Ordinary hand support is explicit; there is no modeled hidden lifting fixture. See [router transfer](ROUTER-TRANSFER.md).

6. **Make the narrower head-transfer portal.** Return both temporary keeper fixtures to their pockets. Move beam 1 into the empty front/lower rack slot. Fit the two front-row existing fully threaded M6×130 stack locks: bolt tips Z513.4, upper washers Z641.8, lower washers Z577.4 and nuts Z572.4. Beams2–4 remain installed and panel 1 remains clamped in the rear bay.

7. **Exchange the split plasma-head hardware.** Transfer the screen, front cap/insert, rear insert and detachable rear assembly to their defined supported panel 1 poses, then move the thinner guide/backplate assembly through the front gap and mount it. Reinstall the rear assembly, screen, rear insert and front cap in the proved order. Restore the modeled fasteners. The rear assembly and cap rest on broad machined faces; the insert and screen use their defined flat faces. The actual extrusion contact patches and gravity projections are checked in [head transfer evidence](integrated-verification.json).

8. **Restore the bed handling path.** With the head installed, remove the two temporary beam-stack locks and return them to their parking holes. Reverse beam 1's route via beam 2, using the keeper fixtures while refitting the front seats. Restore beam 1 to its working seats and refit its draw bolts.

9. **Store the temporary table and remaining beams.** Remove panel 1's four temporary clamp sets to their normal tray positions. Lift panel 1 from the rear bay and follow its checked front-drop route into rack slot 1. Install the rack top bars 2 then 1. Now store beams 1,2,3,4 using the normal beam sequence, including the temporary keeper/front-seat procedure for beam 1. Fit all four normal stack locks after both beam layers are seated.

Returning to the router layout requires the matching reverse preparation and part order, including rebuilding the internal panel 1 table and front portal. Router restoration has its own reverse checks. Recheck bed seating, work zero and tool setup after reassembly.

**Evidence:** [27 staging/restoration segments and six states](transfer-staging-verification.json), [router removal/restoration](router-transfer-verification.json), [split-head transfer and support](integrated-verification.json), [changed-tool compatibility with the earlier/later bed routes](conversion-prerequisites.json), [bed routes](../routes), and [restraint/keeper paths](../structure).

The proofs cover named rigid solids and the prescribed transforms. Unscrewing and inserting small hardware, fingers/grips, operator lifting ability, cables/hoses/tethers, the actual torch, as-built fits and physical restraint/preload qualification remain outside those geometric proofs. The modeled head layout does not authorize energized plasma operation.
