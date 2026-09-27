# Noncontact pin feedback

Use two separate **Panasonic PM-U25-P** slot sensors on each guided locking pin: one for full engagement and one for full withdrawal. The current small carrier uses four sensors for its two magazine locks. The large mechanism uses six, including its separate shutter catch. The small closure interface remains unfinished. The flag is attached to the actual guided pin. A solenoid command or plunger position does not establish pin engagement.

The 6 mm pin stroke is a mechanical displacement, not the sensor's 6 mm optical slot width. Place the two beams and flags so their confirmed endpoint windows are separated by an unconfirmed interval. Neither complementary output from a single beam can establish both endpoints. CAD brackets need adjustment for the delivered sensor and measured pin endpoints.

The manufacturer drawing gives a 13.4 × 16 × 6 mm body, a 6 mm wide slot, two Ø3.2 mm mounting holes on 8 mm centers, and a mounting row 2.5 mm above the body bottom. The beam is 2 mm below the top; the slot bottom is 5.5 mm below the top. These are the nominal drawing dimensions, not a fabrication tolerance for the flag. Use an opaque metal flag and retain clearance from both slot faces through the complete stroke.

Wire brown to the protected 24 V field supply, blue to field return and white (Dark-ON PNP) to its dedicated isolated input circuit. Insulate black (Light-ON). The sensor permits 5–24 V DC ±10%, consumes at most 15 mA, and can source 50 mA. Its output drop is specified as at most 1 V at 16 mA or 2 V at 50 mA. The [wiring definition](../controls/WIRING.md) must include the PNP input circuit and this drop; do not treat a powered output as a dry contact.

Four sensors add up to 60 mA of supply load; six add up to 90 mA, before their output loads. Their fixed cable is 1 m; provide a stationary strain relief and connector. The cable is not the bending-resistant variant. Keep the sensor bodies stationary wherever possible.

Enclose the optical slots against chips, dust and direct light. Debris can block a beam and falsely resemble a flag. The controller must reject contradictory endpoint states and require observed transitions during travel, but these checks do not eliminate all common-cause faults. Component specifications and the manufacturer's component classification do not qualify the machine's stop system or its alignment accuracy.

Drawing-based selection is complete; procurement and physical qualification remain open. DigiKey listed **$13.00 USD each**, **$52.00 for four** or **$78.00 for six**, on 26 September 2026, but showed the U variant on backorder. Shipping, tax and any import charge are unknown. This is a goods-price observation, not an available delivered quote. Other PM-25 shapes require different brackets and are not drop-in substitutions.

Sources: [Panasonic product](https://industry.panasonic.com/global/en/products/fasys/sensor/micro/number/pm-u25-p), [manufacturer catalog, pages 4, 5, 10 and 13](https://industry.panasonic.com/ac/e_download/fasys/sensor/micro/catalog/pm-254565_e_cata.pdf?f_cd=402226&via=ok), [DigiKey listing](https://www.digikey.com/en/products/detail/panasonic-industry/PM-U25-P/5962566). The downloaded manufacturer drawing was rendered and visually inspected. [Machine-readable dimensions and source record](pin-sensor.json).
