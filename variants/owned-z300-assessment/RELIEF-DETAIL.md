# Separate carrier/link-support repair candidate

The frozen XR2 upper carrier extension occupies the same space as the separate X-link support flange: **156 × 12.7 × 6.35 = 12,580.62 mm³**. These are two custom manufactured parts. Their shared XY motion does not make this physical interference acceptable.

The candidate changes only `Z_CARRIER` and `X_LINK_SUPPORT`. It uses the owned-Z300 stock-motor overlay, retains the existing 270.2 mm carrier height and assesses the same 200 mm working range. It does not revise frozen XR2 files or the earlier fit study.

## Carrier through-relief

The horizontal obround is **162.95 mm overall × 6.55 mm high, R3.275 ends**, through the full 12.7 mm plate. In the plate face, its centre is X130 / Z173.475 mm from the carrier's minimum corner. Across is world X, up is world Z, and plate thickness is world Y.

At the X575/Y-guide775 reference pose, its end centres are X496.8 and X653.2. Its bottom is Z1313.2 and top Z1319.75. The lower carrier remains intact up to its original Z1313.2 ledge. This gives a nominal **156 × 12.7 = 1,981.2 mm²** bearing patch under the flange and 0.20 mm top clearance. The original 260 × 270.2 × 12.7 mm outer blank remains unchanged and one solid.

The four M6 axes stay at X515/635, Z1285.2/1301.2. The upper row retains 7 mm from the modeled Ø10 head edge to the slot floor and 8.7 mm from the Ø6.6 bore edge. The check also verifies a complete Ø12 annular carrier seat at each axis; that test does not select an additional washer.

## Complete lower support taps

The original 30 mm downstand puts its lower M6 axes only 2 mm above its bottom edge, breaking the nominal Ø6 thread envelope out by 1 mm. The revised integral support extends this downstand **7 mm**, from Z1283.2 down to Z1276.2, giving 37 mm total height. The lower tap centres now have 9 mm edge distance and **6 mm material beyond the nominal thread radius**.

All four axes, the 12.7 mm carrier grip, 8 mm support thickness, nominal 7.3 mm engagement and 0.7 mm tip reserve remain unchanged. STEP bores show nominal M6 major diameter. The specified operation is Ø5.0 pilot drilling followed by M6×1 tapping; qualify that process against the actual material, tolerances and usable depth before machining.

The larger integral support has a finished bounding blank of **156 × 120.8 × 43.35 mm**, versus 36.35 mm previously. **Treat its billet as new or separately verified existing stock. No owned-stock credit or cleanup allowance is included.** It is one integral part, not a strip added to an already machined bracket.

## Check scope and limits

`output/custom-joint-repair-check.json` binds source hashes, both local custom STEP exports and the stock-Z300 head STEP. It checks valid single solids, zero positive carrier/support overlap, the bearing patch, all four seats/tap bores, preserved original material, added-support material over nominal relative/external travel, and the complete changed custom parts against the other motion parts. The four specific co-moving M6 thread interfaces are checked by exact nonpenetration and unchanged relative transforms; physical thread fit is not inferred from zero-clearance nominal cylinders.

The relief leaves at least 48.525 mm of continuous carrier material on each side. At the narrowest section, ideal weak-axis and in-plane section ratios are approximately 0.373 and 0.754. These are geometric section comparisons, not stiffness or strength acceptance. Local stresses, fatigue, joints and the complete tool-to-work loop remain unqualified.

The actual Z300 mounting rows must avoid the relief and have adequate support spacing and edge distances. The exact bearing floor, 0.20 mm top clearance, corner/edge treatment and both custom parts require a defined machining/assembly tolerance stack. The actual actuator mass, delivered interfaces, retention and full 300 mm operating envelope remain separate acceptance items. Fabrication release remains false.

For assembly integration, `custom_joint_repair.apply_repairs(parts)` accepts an already selected motion tuple list and returns a new list, preserving names, poses and colors. Only the carrier and support change. The function neither selects/stretches a Z module nor writes files.
