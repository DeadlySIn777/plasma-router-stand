# Rev H CAD verification index

**Recorded checks: PASS.** Recorded nominal CAD geometry and named continuous paths, with source-matching independent STEP readback. This is not a fabrication, operational-plasma, structural, controls or physical-safety release.

| Check | Current result |
|---|---|
| [Integrated solids, shared parts and nine poses](verification.json) | PASS |
| [Independent final STEP readback](step-verification.json) | PASS |
| [Six spoilboard continuous routes](routes/spoil-transfer-check.json) | PASS |
| [Six panel continuous routes](routes/panel-path-check.json) | PASS |
| [Four beam continuous routes](routes/beam-path-check.json) | PASS |
| [Added restraint and temporary capture paths](bed/restraint-paths.json) | PASS |
| [Two temporary C-body tray-to-beam routes](bed/temporary-fixture-transfer.json) | PASS |
| [Integrated hatch and washout service paths](water/integrated-verification.json) | PASS |
| [Final assembly exports](../release-review/RevH-CAD/engineering-manifest.json) | PASS |
| [Current RevH_ROUTER STEP bytes](../release-review/RevH-CAD/step/RevH_ROUTER.step) | PASS |
| [Current RevH_BED_STORED STEP bytes](../release-review/RevH-CAD/step/RevH_BED_STORED.step) | PASS |

diagnostic-before-final-freeze contains superseded diagnostic reports. A historical STEP_EXPORT_STALE/PENDING status in verification.json is superseded only for export readback by the current passing step-verification.json; its geometry/source findings are not rewritten.

Current results do not close purchased-interface measurements, coupling/brake fit and response, the unfinished floating/breakaway plasma head, flexible cable/hoses, rigidity or physical commissioning. Read each linked report for its exact exclusions.

[Complete hashes and provenance](acceptance-index.json).
