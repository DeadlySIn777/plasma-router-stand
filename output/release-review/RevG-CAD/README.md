# Rev G — corrected working CAD

**Not finished or released for purchasing, fabrication, CAM execution or operation.** Use this revision for design review. Amber components are nominal purchased-part envelopes; their mounting interfaces are not all verified.

- [Router assembly STEP](step/RevG_ROUTER.step)
- [Stored bed and router tools STEP](step/RevG_BED_STORED.step) — actual plasma tool still missing
- [Router preview](previews/RevG_ROUTER.png) / [stored preview](previews/RevG_BED_STORED.png) / [front storage](previews/RevG_BED_STORED_front.png)
- [Current concept PDF](../../pdf/plasma-router-stand-concept.pdf)
- [Repair report and remaining findings](../../cad-repair-2026-09-25/README.md)
- [Component schedule](cutlist.csv), [operations](part-operations.json), [individual STEP parts](parts/), [flat DXFs](dxf/)
- [Tube cutting schedule](TUBE-CUT-PLAN.md), [general sheet nesting](nesting/sheet-nesting.json)
- [Manifest and source hashes](engineering-manifest.json), [router validation](RevG_ROUTER-validation.json), [storage validation](RevG_BED_STORED-validation.json)

## Bed dimensions

| Item | Current nominal model |
|---|---|
| Requested axis travel | X800 / Y1000 / Z100 mm |
| Overall bare bed | X1003 x Y1211 mm, including joints |
| Removable panels | Six 500 x397 x33.775 mm including ties/fasteners |
| Dry panel mass | About 3.866 kg, model estimate |
| Bed beams | Four 924 mm; about 5.060 kg each, model estimate |
| Bare / finished spoilboard top | Z940.8 /958.8 mm |
| Purchased extrusion | Ten 1220 mm bars = five two-packs |
| Cuts | Three 397 mm strips per bar; 29 mm residual for kerfs/trim |

The entire bare deck is larger than nominal tool travel. Only the six separate spoilboards are assigned an in-machine surfacing process. Neither nominal travel nor those surface bounds establishes the final usable cutting envelope.

Conversion stays geometrically within the frame for the prescribed large-part routes. It assumes manual handling, including 52 removed screws/clamp fasteners and 24 loose-nut retrievals. Positive restraint, fingers, operator reach, small-part transfers and actual fit remain open. Cabinet access requires reinstalling the bed to clear the storage racks.

## File scope

Both assemblies have 1283 valid solids and no unresolved static overlaps above the nominal checker threshold. Both STEP files reimported with matching solid counts and volumes. Separate checks cover nine router poses and ordered continuous panel/board/beam paths. These results do not establish strength or physical safety.

Individual exports are design-review geometry, not automatically production-released parts. Some holes are pilot sizes requiring operations such as tapping/reaming; non-through DXF layers must not be cut as through contours. The provisional Z adapter is deliberately excluded, as are purchased envelope parts and invalid legacy torch clamps. Explicit comparison-only adapter files are under the repair evidence folder.

Sources remain in [RevE-ENGINEERING](../RevE-ENGINEERING/) for continuity. Run [build_revg.py](../RevE-ENGINEERING/build_revg.py), not the old RevF hoisted-bed build, for this revision. Older exported files remain historical and must not be mixed into the current schedule.

General nesting uses 4 x 8 stock envelopes and nominal contours; it is not proof of sufficient owned 12 x 12 blanks or a final kerf-compensated toolpath. The prior cost workbook has not been reconciled to Rev G quantities, and no current complete delivered price is claimed.
