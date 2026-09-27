# Automatic lock release actuator

Working selection: **Delta DSOL-1151-24C**, a continuously rated 24 V pull
solenoid. A separate guided steel pin carries the locking load. The solenoid
withdraws that pin only after the slide or shutter has unloaded it; its plunger
is not a structural lock. Spring engagement is the intended unpowered state.

The [Delta product page](https://www.deltaww.com/en-US/products/solenoids) links
the [manufacturer drawing](https://filecenter.deltaww.com/Products/download/04/0409/DSOL-1151.pdf).
That download currently redirects to an unavailable page. The original Delta
sheet was retrieved through the public [Datasheet Archive listing](https://www.datasheetarchive.com/?q=dsol-1151),
visually inspected, and identified by SHA-256 in [lock-actuator.json](lock-actuator.json).
It is research material, not a new project-authored supplier model.

The body is approximately **50 x 29 x 25 mm**. Its opposed mounting faces are
different: use the face with two 8-32 UNC holes at 15.875 mm axial spacing and
12.497 mm height. The first hole is 7.112 mm from the front body plane. The
drawing depicts the **energized** position. Provide room for the extended
plunger, insulated terminal boots and wiring, not just the body box. Do not
substitute M4 screws in the UNC holes. Screw engagement depth is not specified
by the sheet and must be checked before selecting screw length.

The mechanism uses only **6 mm** of withdrawal: a nominal 4 mm engaged pin
plus 2 mm clearance. The continuous-duty force curve suggests roughly 5 N at
that air gap, but it is a plotted typical value, not a guaranteed hot pull
rating. Use an adjustable external stop to limit the actual maximum air gap
to 6 mm. The pin return spring should require at most 1 N over its working
stroke; friction, plunger/pin weight, orientation and sensor force consume the
remaining pull margin. A low-force or noncontact sensor is preferable to a
stiff microswitch acting directly on the pin.

Verify withdrawal at minimum supply voltage after thermal soak, at the coldest
intended operating temperature, and with the real guided pin and return spring.
It must also extend and fully engage with power removed. A stalled or loaded
pin must cause a timeout and inhibit motion, rather than repeated hammering or
an increased coil voltage. The two position signals must sense the **lock pin**,
not merely the solenoid plunger or the electrical command.

The sheet specifies 7.5 W, 76.8 ohms +/-10% at 25 C and 100% duty, but also
prints 0.4 A for the 24 V version. Since 24/76.8 is 0.3125 A, those nominal
figures are not mutually exact. Allocate at least **0.4 A per coil**, with
additional allowance for supply tolerance and cold resistance. Protect each
field branch and suppress its inductive transient. A flyback diode slows
spring return; include that delay in the measured engagement timeout.
Follow the [isolated control design](../controls/README.md); no 24 V load or
sensor connects directly to an MCU pin.

The [US distributor listing](https://www.digikey.com/en/products/detail/delta-electronics/DSOL-1151-24C/18661275)
showed **USD 23.72 each** on 26 September 2026. Shipping, tax and any tariff are
unquoted. This is a component allowance, not a complete installed lock price.
The supplier curve, spring/pin friction, actual thread depth and complete lock
strength still require qualification before this candidate can be released.
