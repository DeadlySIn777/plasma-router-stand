"""Export the built image, source overlay, patch and traceability manifest."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import zipfile

root = Path(__file__).resolve().parent
repo = root / "grblhal-h7"

def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()

manifest = {"main": {"url": git(repo, "remote", "get-url", "origin"), "commit": git(repo, "rev-parse", "HEAD")},
            "submodules": {}, "tools": {"platformio": "6.2.0", "ststm32": "20.0.0", "stm32cubeh7": "1.12.1", "gccarmnoneeabi": "7.2.1"},
            "local_changes": ["boards/my_machine_map.h", "Src/kraken_board.c", "kraken.ini", "plasma/thc.c arc-attempt guard/default/range"],
            "physical_validation": "not performed", "image_sha256": {}}
manifest["BTT_pin_reference"] = {"url": "https://github.com/bigtreetech/BIGTREETECH-Kraken/blob/master/Firmware/generic-bigtreetech-kraken.cfg",
                                 "sha256": hashlib.sha256((root / "kraken-official.cfg").read_bytes()).hexdigest()}
for name in ["grbl", "motors", "trinamic", "plasma", "plugins"]:
    manifest["submodules"][name] = {"url": git(repo / name, "remote", "get-url", "origin"),
                                    "commit": git(repo / name, "rev-parse", "HEAD")}

firmware = root / "firmware"
firmware.mkdir(exist_ok=True)
for suffix in ["bin", "elf"]:
    src = repo / f".pio/build/kraken_v11_hybrid/firmware.{suffix}"
    dest = firmware / f"kraken-v11-hybrid.{suffix}"
    shutil.copy2(src, dest)
    manifest["image_sha256"][dest.name] = hashlib.sha256(dest.read_bytes()).hexdigest()

overlay = root / "source-overlay"
for relative in ["boards/my_machine_map.h", "Src/kraken_board.c", "kraken.ini"]:
    dest = overlay / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo / relative, dest)

patches = root / "patches"
patches.mkdir(exist_ok=True)
(patches / "plasma-arc-attempt-guard.patch").write_text(git(repo / "plasma", "diff", "--", "thc.c") + "\n")
(root / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
licenses = root / "licenses"
licenses.mkdir(exist_ok=True)
for name, source in [("grblHAL", repo / "COPYING"), ("trinamic", repo / "trinamic/COPYING"),
                     ("CMSIS", root / ".platformio/packages/framework-stm32cubeh7/Drivers/CMSIS/LICENSE.txt")]:
    if source.exists():
        shutil.copy2(source, licenses / (name + "-LICENSE.txt"))

files = ["README.md", "COMMISSIONING.md", "verification.json", "source-manifest.json", "build.ps1", "verify_port.py", "package_port.py", "build-hybrid.log", "kraken-official.cfg"]
for folder in [firmware, overlay, patches, licenses]:
    files += [str(p.relative_to(root)) for p in folder.rglob("*") if p.is_file()]
with zipfile.ZipFile(root / "Kraken-V1.1-controls-engineering.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for relative in files:
        z.write(root / relative, relative)
print(json.dumps({"package": "Kraken-V1.1-controls-engineering.zip", "binary_sha256": manifest["image_sha256"]["kraken-v11-hybrid.bin"]}, indent=2))
