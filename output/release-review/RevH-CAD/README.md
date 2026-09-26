# Rev H - integrated working CAD

Rev H adds captive bed hardware, defined storage restraints, reservoir service hatches, a refill spout and a corrected Z-adapter blank. **The machine is not finished or released for fabrication, CAM execution or operation.** Purchased interfaces, the actual plasma head, full structural qualification and several electrical/plumbing details remain open.

- [Router assembly STEP](step/RevH_ROUTER.step)
- [Bed and router tools stored STEP](step/RevH_BED_STORED.step)
- [Router preview](previews/RevH_ROUTER.png), [stored preview](previews/RevH_BED_STORED.png), [front storage](previews/RevH_BED_STORED_front.png)
- [Concept PDF](../../pdf/plasma-router-stand-concept.pdf)
- [Completion changes and evidence](../../design-completion-2026-09-26/README.md)
- [Component schedule](cutlist.csv), [manufacturing operations](part-operations.json), [individual STEP parts](parts/), [flat DXFs](dxf/)
- [Tube stock nest](TUBE-CUT-PLAN.md), [scrap shopping guide](../../design-completion-2026-09-26/SCRAP-TUBE-GUIDE.md), [sheet layouts](nesting/sheet-nesting.json)
- [Build manifest and source hashes](engineering-manifest.json), [router validation](RevH_ROUTER-validation.json), [storage validation](RevH_BED_STORED-validation.json)

## Geometry and hardware

| Item | Current definition |
|---|---|
| Nominal travel | X800 / Y1000 / Z100 mm |
| Selected X/Y catalog lead | 10 mm per screw revolution; not screw diameter |
| Bare deck | 1003 x 1211 mm, including joints |
| Removable deck panels | Six 500 x 397 mm panels; separate reachable spoilboards |
| Extrusion stock | Ten 1220 mm bars = five two-packs; three 397 mm strips per bar |
| Bed beams | Four 924 mm lengths of nominal 50.8 square x 3.048 wall tube |
| Bare / finished spoilboard top | Z940.8 / Z958.8 mm |
| Captive top-slot hardware | Twelve machined nut strips and 24 M3 retainers replace 24 loose nuts |
| Storage restraints | Sleeved beam-stack bolts, panel retainers and a folding spoilboard guard |
| Temporary beam support | Two boxed keepers secure beam 1 to beam 2 during front-seat removal |
| Routine tank cleaning | Two gasketed hatches, upright cover pockets and a bolted washout cover |
| Refill outlet | Fabricated pipe with 30 mm nominal air gap above the pan rim |

The bare bed exceeds nominal travel; only the separate reachable spoilboards are assigned in-machine surfacing. Final tool, workpiece, clamp and cable envelopes remain to be verified. Added retainers require their own release and staging steps. This is a manual conversion, not a quick or automatic changer.

The adapter deliberately has no invented purchased-carriage holes. Its known custom clamp holes remain, with the output pattern awaiting recorded measurements. The larger motor block represents an optional brake-motor candidate, not a verified Z installation. The stored-bed configuration still has no actual floating/breakaway plasma head.

## Using the files

Run [build_revh.py](../RevE-ENGINEERING/build_revh.py) to generate this revision. Shared sources remain in the legacy-named directory. Rev G and older exports are historical and must not be mixed into the Rev H component schedule.

The manifest's `baseline_rev_g_metadata` is explicitly historical input. Its old conversion procedure and mass estimates are not current Rev H instructions. Use the completion metadata and the current bed handling report. Per-component operations and the exported solids define the nominal new parts.

Individual exports remain review geometry. Notes distinguish tapping, counterboring and other machining from through cuts; guarded purchased interfaces are excluded. Sheet nests use generic 4 x 8 stock for geometric layout, not the owner's small plate inventory or a direction to buy whole sheets. Tube nesting assumes full usable 20-ft lengths; actual scrap must be re-nested.

The exact verification scope and outstanding work are recorded in the completion report. Neither a clear CAD state nor a valid STEP establishes strength, repeatability, hand clearance or hardware compatibility. No new complete delivered build price or successful Fusion import is asserted.
