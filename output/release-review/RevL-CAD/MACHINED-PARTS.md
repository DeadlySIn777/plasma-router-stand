# Machined parts in GM1 Rev L (28 September)

Counted from the Rev L router state (`RevL_ROUTER-validation.json`, 1,302 part instances, 405 part numbers) with the
operations recorded for each part number in `RevK-CAD` and `RevL-CAD` (`part-operations.json`, the `MILL_` and
`CSK_` layers of the DXFs). "Machined" here means the part needs a lathe or a mill: a bore, a pocket, a counterbore,
a thread cut on a turned part, or a shape milled from a billet. Saw cuts, plasma- or laser-cut sheet, bench drilling
and tapping, folding and welding are not counted.

## Where the count comes from

| Process | Part numbers | Pieces |
|---|---:|---:|
| Bought (hardware, rails, motors, spindle, hoses, envelopes) | 133 | 795 |
| Cut sheet or plate (plasma, laser or waterjet, then drilled) | 120 | 253 |
| Saw-cut tube or pipe | 49 | 59 |
| Board, sheet rubber, weld deposits | 16 | 19 |
| Small welded or drilled steel not in a class above | 37 | 44 |
| **Needs a lathe or a mill** | **56** | **141** |

Of the 141 pieces, 79 are simple turned parts (bungs, plugs, sleeves, standoffs, spacers) and 62 are mill parts or
mixed. Two clusters carry most of it: the frame fill ports (36 pieces) and the plasma floating head (32 pieces).

## The machined parts, by cluster

| Cluster | Part numbers | Pieces | What the machining is |
|---|---:|---:|---|
| Frame fill ports: `SAND_M20_BUNG`, `SAND_M20_PLUG` | 2 | 36 | Ø30 x 10 bung drilled 18.5 and tapped M20 x 1.5; plug with an M20 x 1.5 shank and a 6 mm hex socket |
| Bed sleeves: `J_LEDGER_M10_SLEEVE`, `MOD_COMPRESSION_SLEEVE` | 2 | 12 | Ø18 x 51 sleeves bored 9 or 10.5, welded through the rails and ledgers, faced flush |
| Feet: `FT_PAD` | 1 | 6 | 80 x 80 x 12.7 plate with a Ø32 pocket 2 mm deep for the leveling foot |
| Gantry drive links and adapters: `GANTRY_END_BRACKET_L/R`, `X_LINK_SUPPORT`, `Y_LINK_SUPPORT_L/R`, `MOTION_CLEVIS_BILLET`, `LINK_COUPLER_M6_RHLH_28`, `HMS40_DRIVE_SHOE_6p35/19p05`, `Y_DATUM_BAR` | 10 | 19 | 6061 billets (150 x 80 x 83 end brackets, 156 x 121 x 36 and 103 x 32 x 46 link supports, six 40 x 48 x 32 clevises bored and reamed), RH/LH tapped hex couplers, counterbored drive shoes, two 8 x 45 x 1450 datum bars |
| Home and stop cams: `X_HOME_CAM`, `Y_CAM_L_FRONT`, `Y_CAM_R_FRONT` | 3 | 3 | Small A36 cams with a 3 mm web |
| Spindle clamp: `SPINDLE_SPLIT_CLAMP_FRONT/REAR` | 2 | 2 | Two 110 x 45 x 40 aluminium halves bored Ø65 and tapped (the BT30 variant has one 130 x 156 x 100 billet instead, `SPINDLE_CLAMP_BT30`) |
| Plasma floating head: `I_HEAD_*` (clamps, crossbars, float carriage, acetal cam, four L brackets, two insulating inserts, counterbored release plate, cone/V/flat seats, three R3 ball buttons, two Ø8 rods with M4 ends, acetal bushes, spacers, eyes, saddle) | 26 | 32 | A kinematic breakaway mount with a floating carriage and an initial-height switch, mostly aluminium, some hardened steel and acetal |
| Small turned spacers and standoffs: `FLOAT_STANDOFF`, `VENT_SCREEN_SLEEVE`, `MOD_ATC_RISER_12x7p65`, `K_HEAD_PARK_PAD`, `WP_HOLD_SPACER_1..4`, `PUMP_SPACER`, `MOD_ATC_FRONT_STOP` | 10 | 31 | Ø12 stainless standoffs, a tapped screen sleeve, 12 OD x 5.5 ID risers, pads and spacers |

## What could be bought or simplified instead

Nothing below is changed in the model. Each item is an owner decision; taking one means editing the generator,
re-running the checks and re-issuing the package, and the build order lists what has been bought already.

| Option | Pieces removed | What changes |
|---|---:|---|
| Fill ports as weld-on 3/4 NPT forged half couplings with square-head plugs (the same family as the drain's 1/2 NPT coupling) | 36 | Ø21 hole instead of Ø18.5 in each filled tube; about $6 per port bought instead of two lathe pieces |
| Bed sleeves cut from DOM tube: 3/4 in x 0.188 wall (Ø19.05, 9.5 bore) for the M8 drawdowns, 3/4 in x 0.156 wall (11.1 bore) for the M10 ledger bolts | 12 | Saw cut and face only; rail and ledger holes become Ø19.05 |
| Feet: a bought M16 swivel leveling foot with an 80 mm pad, no pocket | 6 | The pad stays a cut plate with five drilled holes |
| Standoffs, risers, spacers and park pads as stock items (stainless M5 standoffs, 12 OD steel spacers, HDPE pads) | 31 | Lengths rounded to stock sizes, 7.65 mm risers become 8 mm with the shim moved |
| Spindle clamp bought: 65 mm two-bolt clamp for the ER11 spindle, 105 mm clamp for the BT30 | 2 (BT30: 1) | Removes the single largest billet of the BT30 variant; the clamp's own bolt pattern replaces the plate holes |
| Plasma head bought: a floating torch holder with an initial-height switch and a magnetic breakaway | 32 | Loses the kinematic repeatability, the tether and the release-plate design; the Rev I head checks would be redone for the bought holder |
| Gantry links kept, with the six clevises as bought clevis brackets, the RH/LH couplers as stock stud connectors and the datum bars from 5/16 x 1-3/4 in ground flat stock | 11 | The end brackets, link supports and drive shoes stay milled: they set the rail parallelism |

Taking every option leaves about 20 machined pieces, all on a mill: the gantry end brackets, the three link supports,
the three drive shoes, the three cams and whatever is kept of the clevises. Taking only the first four (the cheap
turned parts) removes 85 pieces and changes no interface the owner has bought parts for.
