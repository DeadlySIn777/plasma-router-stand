# Full-project re-audit - 25 September 2026

Status: **in progress; design is not released**. The GitHub import is a private working snapshot, not completion of this review.

The current mechanical source identifies a Rev F one-piece hoisted module. Older Rev E six-cassette records remain elsewhere. Evidence must be tied to actual file contents and source hashes, not simply to a revision label or an old PASS result.

Independent review workstreams:

- `mechanics.md` and `mechanics.json`: motion, bed support/fastening, reach, handling, fabrication and validation freshness.
- `controls-water.md` and `controls-water.json`: controller baseline, firmware, interlocks, water inventory/transfer and electrical definition.
- `parts-bom.md` and `parts-bom.json`: selected parts, compatibility, quantities, raw-stock coverage and mixed-revision BOM entries.

Preliminary confirmed concerns reported during the audit include MDF surfacing beyond nominal tool reach, bed screw positions at or outside MDF edges, claims about extrusion-lip loading, mixed Kraken/Rodent control definitions, and a BOM that still includes the earlier bed materials. The detailed reports govern the evidence and limitations of each finding. These concerns have not been silently corrected in the CAD during repository preparation.

The original user requirement was for mode conversion within the machine footprint. The newer hoisted-module source requires a separate scope check against that requirement and any subsequent owner instructions. Do not infer ownership or approval of a hoist from a comment in a source file alone.
