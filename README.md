# Plasma / router CNC stand

Private working repository for the hybrid CNC router and plasma machine. Nominal requested travel is **800 mm X, 1000 mm Y and 100 mm Z**. This repository contains the design sources, CAD exports, drawings, engineering reports, firmware work and bill of materials.

**Engineering work in progress. Not released for purchasing, fabrication, firmware deployment or machine operation.** A successful file/hash or collision check does not establish whole-machine rigidity, safe lifting, electrical compatibility or machining accuracy.

## Current review status

The imported working files contain a newer one-piece hoisted bed design (called Rev F inside folders still named Rev E), alongside records from the previous six-cassette design. Three source-audit reports dated 25 September 2026 record mechanical, controller and BOM findings with source references and stated limits. See [the re-audit reports](output/reaudit-2026-09-25/) before relying on any drawing or cost total.

In particular, verify the bed support and fastening geometry, actual tool reach for the proposed MDF surfacing operation, the lifting/footprint requirements, the controller baseline, and the current purchased-parts quantities. The existing plasma cutter is not identified by its AG-60 torch listing. Historical reports remain as evidence; they are not independent approval of the latest design.

## Project files

| Area | Location |
|---|---|
| Design navigation supplied with the working project | [README-FIRST.md](README-FIRST.md) |
| Main CAD generators, cut lists, DXFs and engineering reports | [Engineering folder](output/release-review/RevE-ENGINEERING/) |
| STEP assemblies | [Assembly exports](output/release-review/RevE-ENGINEERING/step/) |
| Current concept document | [Concept PDF](output/pdf/plasma-router-stand-concept.pdf) |
| Controller source, compiled prototype and commissioning notes | [Controls](RevE-ENGINEERING/controls/) |
| BOM workbook and supporting data | [Budget folder](outputs/reve-30510/) |
| Re-audit findings | [Re-audit](output/reaudit-2026-09-25/) |
| Imported file hashes and exclusions | [Snapshot manifest](REPOSITORY-SNAPSHOT.json) |

## Snapshot and rebuild notes

This repository is a point-in-time copy of the `plasma_router_stand` project, not the surrounding multi-project workspace or its Git history. File bytes are preserved so recorded hashes remain meaningful. The import manifest records each copied file and exclusions.

Python CAD scripts use CadQuery/OpenCascade; document generation uses ReportLab and pypdf. Spreadsheet builders use the local artifact runtime. Some scripts contain original Windows runtime paths and need environment configuration on another machine. Firmware tool versions and upstream revisions are recorded in [the source manifest](RevE-ENGINEERING/controls/source-manifest.json). A clean-machine rebuild has not been certified by this upload.

Local virtual environments, Node modules, PlatformIO/build caches, logs, raw web captures, transient render data and duplicate ZIP packages are excluded. Relevant CAD exports, PDFs, spreadsheets and explicitly delivered firmware outputs are retained. Upstream firmware sources are included as ordinary files with their existing license notices; nested Git metadata is excluded. This import grants no new license over third-party source code or supplier documents.

The repository has no automatic deployment, hardware flashing or manufacturing release workflow. Publishing this snapshot does not finish the design audit.
