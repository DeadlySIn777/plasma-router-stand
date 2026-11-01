# Z200 power-off retention candidate

The [STEPPERONLINE 23HS22-2804D-B200](https://www.omc-stepperonline.com/nema-23-stepper-1-26nm-178oz-in-w-brake-friction-torque-2-0nm-283oz-in-23hs22-2804d-b200) is a documented power-off brake motor:57 mm frame,88 mm body package,8 x21 mm front shaft,2.8 A phases and a2 Nm static brake released by24 VDC/11.5 W. It is a new replacement candidate, not confirmed owned inventory or a verified drop-in fit.

It could keep the module's motor front datum and add32 mm at the rear **only if** the actual ZXHT80 flange, pilot, shaft and coupler match. The RATTMMOTOR listing does not publish these dimensions. Similar motor names appear with different shaft diameters, so compatibility cannot be inferred from NEMA23 or a motor name alone. The supplier datasheet exists, but its image/PDF downloads were blocked here; no unseen flange dimensions were invented.

For20 kg moving mass plus100 N downward force on the5 mm-lead screw, the ideal torque is0.236 Nm. A chosen3x static screening factor requires0.707 Nm, below the candidate's2 Nm static rating. This comparison does not qualify stopping delay, release/engagement control, the coupling or the module's load capacity. A20 ms unconstrained delay would permit about1.96 mm of drop;50 ms permits12.26 mm. Actual response must be measured.

The separate SWB-03 brake requires an exposed matching rear shaft and rear mounting holes. Those are not established on the supplied single-output-shaft motor, so simply appending that brake is unsupported.

**Design gate:** obtain the ZXHT80 front motor/coupler drawing or measure the delivered interfaces, select the complete brake motor/coupler, integrate fail-safe brake control and verify loaded power-loss retention before claiming operational Z retention.
