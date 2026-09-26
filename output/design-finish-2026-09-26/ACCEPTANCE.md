# Rev I verification index

**Recorded checks: PASS.** Explicit nominal geometry, named handling/service paths, conditional structural arithmetic and bounded circuit-model behavior. This is not a complete fabrication, physical rigidity, electrical safety, HF compatibility or operating-machine release.

| Check | Result |
|---|---|
| [Three assembly states; shared parts; nine router and nine head poses](verification.json) | PASS |
| [Independent current STEP readback](step-verification.json) | PASS |
| [Six spoilboard routes](routes/spoil-transfer-check.json) | PASS |
| [Six panel routes](routes/panel-path-check.json) | PASS |
| [Four support-beam routes](routes/beam-path-check.json) | PASS |
| [Structural arithmetic and nominal states; full-machine rigidity remains unqualified](structure/calculations.json) | PASS |
| [Reinforced storage restraint routes](structure/reinforced-restraint-paths.json) | PASS |
| [Temporary keeper-body transfer](structure/temporary-fixture-transfer.json) | PASS |
| [Water servicing, cabinet plates and enlarged hose sweeps](service/verification-build_revi.json) | PASS |
| [Float, normal breakaway and head machining definitions](motion/mechanism-verification.json) | PASS |
| [Head fastener envelopes and exact individual export inventory](motion/head-package-verification.json) | PASS |
| [Split-head transfer through the phased machine](motion/integrated-verification.json) | PASS |
| [Temporary panel/beam preparation and restoration for head transfer](motion/transfer-staging-verification.json) | PASS |
| [Router tool transfer and its bed-sequence prerequisites](motion/router-transfer-verification.json) | PASS |
| [Changed tool obstacles across the full conversion sequence](motion/conversion-prerequisites.json) | PASS |
| [Conversion prerequisite input-report identities](motion/conversion-prerequisites.json) | PASS |
| [Water/tool terminal graph and bounded fault sequences](controls/verification.json) | PASS |
| [Current generated terminal wiring and reviewed control documents](controls/verification.json) | PASS |
| [Normally-off run interface electrical screen](controls/run-interface.json) | PASS |
| [Current authored run-interface drawing](controls/run-interface.json) | PASS |
| [Isolated head/probe schematic and bounded fault response](controls/head-interface-verification.json) | PASS |
| [Final source-bound assembly exports](../release-review/RevI-CAD/engineering-manifest.json) | PASS |
| [Part inventory, individual solids and drawing package](package-verification.json) | PASS |
| [Head detail rendered from current CAD](head-preview-verification.json) | PASS |
| [Concept PDF build inputs](pdf/build-verification.json) | PASS |
| [Four-page visual review of the current PDF](pdf/visual-review.json) | PASS |
| [Exported panel/beam inventory and nominal mass reconciliation](structure/calculations.json) | PASS |
| [Current RevI_ROUTER file](../release-review/RevI-CAD/step/RevI_ROUTER.step) | PASS |
| [Current RevI_BED_STORED file](../release-review/RevI-CAD/step/RevI_BED_STORED.step) | PASS |
| [Current RevI_PLASMA_HARDWARE file](../release-review/RevI-CAD/step/RevI_PLASMA_HARDWARE.step) | PASS |

The initial findings and rejected diagnostic routes are retained as history. Only the source-matching records above support the current package. A PASS here does not mean the machine is ready to fabricate or operate.

[Open engineering and measured inputs](OPEN-ITEMS.md). [Full hashes](acceptance-index.json).
