# Full-project re-audit - 25 September 2026

Status: **three source-audit reports recorded; findings remain open and design is not released**. This bounded audit was documented for the private GitHub snapshot. It does not include physical commissioning, a fresh complete firmware build, or independent qualification of every purchased component.

The current mechanical source identifies a Rev F one-piece hoisted module. Older Rev E six-cassette records remain elsewhere. Evidence must be tied to actual file contents and source hashes, not simply to a revision label or an old PASS result.

Independent review workstreams:

- [Mechanical audit](mechanics.md) and [evidence JSON](mechanics.json): 10 findings covering motion, bed support/fastening, reach, handling, fabrication and validation freshness.
- [Controls and water audit](controls-water.md) and [evidence JSON](controls-water.json): 8 findings covering controller baseline, firmware, interlocks, water inventory/transfer and electrical definition.
- [Parts and BOM audit](parts-bom.md) and [evidence JSON](parts-bom.json): 10 findings covering selected parts, compatibility, quantities, raw-stock coverage and mixed-revision BOM entries.

Confirmed concerns include MDF surfacing beyond nominal tool reach, bed screw positions at or outside MDF edges, claims about extrusion-lip loading, mixed Kraken/Rodent control definitions, and a BOM that still includes the earlier bed materials. Current motion-verification data contains reported clashes while older prose says zero; the audit distinguishes a possible checker-fixture problem from a proven physical collision. The detailed reports govern the evidence and limitations of each finding. These concerns have not been silently corrected in the CAD during repository preparation.

**T-slot cutting conflict:** current Rev F source uses ten strips cut to 1197 mm, while older purchasing records still instruct thirty 397 mm cuts. Five two-packs contain ten bars in both cases, so an unchanged pack count does not validate the cutting instruction. Resolve the adopted bed revision before cutting.

The original user requirement was for mode conversion within the machine footprint. The newer hoisted-module source requires a separate scope check against that requirement and any subsequent owner instructions. Do not infer ownership or approval of a hoist from a comment in a source file alone.

## Owner identification follow-up

The owner subsequently identified the cutter as **VIV ARC CUT-50**. See the [identity follow-up](CUTTER-IDENTITY-FOLLOWUP.md). The historical reports above retain their original evidence; CW-02 remains open for the exact version and cutter-facing interfaces.
