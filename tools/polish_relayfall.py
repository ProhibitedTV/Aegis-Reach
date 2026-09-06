"""Apply the Relayfall visual-readability pass directly to the playable MAX map.

This patches the encrypted GameGuru MAX .fpm in place without rebuilding geometry.
It changes only the embedded visuals.ini and the existing six authored light entities.

Usage:
    python tools/polish_relayfall.py
    python tools/polish_relayfall.py --dry-run
    python tools/polish_relayfall.py --backup

Design target: readable blue-hour military sci-fi. Atmosphere is important, but the
player must be able to parse cover, enemies, routes, and objective landmarks before
being shot at.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

from max_archive import PASSWORD, convert
from native_format import ROOT, read_ele, write_ele

GAME = ROOT / "Aegis Reach"
MAP = GAME / "Files" / "mapbank" / "Aegis Reach - Relayfall.fpm"
TOP_LEVEL_VISUALS = GAME / "visuals.ini"
REPORT = GAME / "Design" / "visual-pass-2.json"

# Stable exposure and strong ambient separation are intentional. This is not a
# horror-night preset. The sky supplies the broad read; authored cyan/amber lights
# supply local combat language.
VISUAL_SETTINGS = {
    "sky$": "highcloud",
    "DisableSkybox": 0,
    "TimeOfday": 8,
    "Simulate24Hours": 0,
    "Exposure": 1.28,
    "PostBrightness#": 0.075,
    "PostContrast#": 1.08,
    "Gamma": 2.2,
    "DeSaturate": 0,
    "AmbienceIntensity#": 205,
    "AmbienceRed#": 176,
    "AmbienceGeen#": 196,
    "AmbienceBlue#": 224,
    "SurfaceIntensity#": 1.18,
    "SunIntensity": 1.42,
    "SunRed": 1.0,
    "SunGreen": 0.86,
    "SunBlue": 0.72,
    "SunAngleX": 38,
    "SunAngleY": 318,
    "ZenithRed": 52,
    "ZenithGreen": 78,
    "ZenithBlue": 112,
    "FogNearest#": 5200,
    "FogDistance#": 28500,
    "FogR#": 52,
    "FogG#": 72,
    "FogB#": 96,
    "BloomThreshold": 1.2,
    "BloomStrength": 0.22,
    "EnvProbeBrightness": 1.18,
    "SkyCloudiness": 0.46,
    "SkyCloudCoverage": 0.88,
    "MotionIntensity#": 0,
    "LevelVSyncEnabled": 1,
}

CYAN = 0x67D8EA
AMBER = 0xF2A45A


def patch_setting(text: str, key: str, value: object) -> str:
    line = f"visuals.{key}={value}"
    pattern = re.compile(rf"(?m)^visuals\.{re.escape(key)}=[^\r\n]*")
    if pattern.search(text):
        return pattern.sub(line, text)
    ending = "\r\n" if "\r\n" in text else "\n"
    return text.rstrip("\r\n") + ending + line + ending


def patch_visuals(data: bytes) -> tuple[bytes, dict[str, tuple[str | None, str]]]:
    text = data.decode("latin1")
    changes: dict[str, tuple[str | None, str]] = {}
    for key, value in VISUAL_SETTINGS.items():
        match = re.search(rf"(?m)^visuals\.{re.escape(key)}=([^\r\n]*)", text)
        old = match.group(1) if match else None
        text = patch_setting(text, key, value)
        changes[key] = (old, str(value))
    return text.encode("latin1"), changes


def suffix_key(entity: dict, suffix: str) -> str | None:
    for key in entity:
        if key.split(":", 1)[-1] == suffix:
            return key
    return None


def get_suffix(entity: dict, suffix: str, default=None):
    key = suffix_key(entity, suffix)
    return entity.get(key, default) if key else default


def set_suffix(entity: dict, suffix: str, value) -> bool:
    key = suffix_key(entity, suffix)
    if not key:
        return False
    entity[key] = value
    return True


def patch_lights(map_ele: bytes) -> tuple[bytes, list[dict]]:
    version, entities = read_ele(map_ele)
    changed: list[dict] = []

    for entity in entities:
        name = str(get_suffix(entity, "eleprof.name_s", ""))
        match = re.fullmatch(r"Relay illumination (\d+)", name)
        if not match:
            continue

        index = int(match.group(1))
        # Cyan carries navigation/objective readability; amber creates warmer
        # combat pockets and silhouette contrast. Larger ranges illuminate lanes
        # without turning the whole fortress into flat fullbright.
        color = CYAN if index % 2 else AMBER
        radius = 1750.0 if index in (1, 2, 3, 4) else 1550.0
        old_range = get_suffix(entity, "eleprof.light.range")
        old_color = get_suffix(entity, "eleprof.light.color")

        set_suffix(entity, "eleprof.light.range", radius)
        set_suffix(entity, "eleprof.light.color", color)
        set_suffix(entity, "eleprof.light.fLightHasProbe", 1)

        changed.append(
            {
                "name": name,
                "range_before": old_range,
                "range_after": radius,
                "color_before": old_color,
                "color_after": hex(color),
            }
        )

    result = write_ele(version, entities)
    # Protect against codec drift while touching a binary map format.
    assert read_ele(result)[0] == version
    return result, changed


def rewrite_archive(path: Path, *, dry_run: bool, backup: bool) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)

    with zipfile.ZipFile(path) as source:
        source.setpassword(PASSWORD)
        infos = source.infolist()
        payload = {info.filename: source.read(info.filename) for info in infos}

    if "visuals.ini" not in payload or "map.ele" not in payload:
        raise RuntimeError("Relayfall archive is missing visuals.ini or map.ele")

    patched_visuals, visual_changes = patch_visuals(payload["visuals.ini"])
    patched_ele, light_changes = patch_lights(payload["map.ele"])
    payload["visuals.ini"] = patched_visuals
    payload["map.ele"] = patched_ele

    report = {
        "map": str(path),
        "dry_run": dry_run,
        "visual_settings": {
            key: {"before": before, "after": after}
            for key, (before, after) in visual_changes.items()
        },
        "lights": light_changes,
    }

    if dry_run:
        return report

    if backup:
        backup_path = path.with_name(path.stem + ".pre-visual-pass-2.fpm")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
            report["backup"] = str(backup_path)

    with tempfile.NamedTemporaryFile(
        prefix="relayfall-visual-pass-", suffix=".fpm", delete=False, dir=path.parent
    ) as handle:
        temp_path = Path(handle.name)

    try:
        with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as output:
            for info in infos:
                output.writestr(info.filename, payload[info.filename])
        convert(temp_path)

        # Validate the MAX-encrypted result before replacing the playable map.
        with zipfile.ZipFile(temp_path) as check:
            check.setpassword(PASSWORD)
            assert check.read("visuals.ini") == patched_visuals
            assert check.read("map.ele") == patched_ele

        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    # Keep the inspectable project-level visual preset in sync with the map.
    if TOP_LEVEL_VISUALS.exists():
        top, _ = patch_visuals(TOP_LEVEL_VISUALS.read_bytes())
        TOP_LEVEL_VISUALS.write_bytes(top)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, default=MAP, help="alternate Relayfall .fpm")
    parser.add_argument("--dry-run", action="store_true", help="inspect planned changes only")
    parser.add_argument("--backup", action="store_true", help="keep one pre-pass .fpm beside the map")
    args = parser.parse_args()

    report = rewrite_archive(args.map, dry_run=args.dry_run, backup=args.backup)
    print("AEGIS REACH // VISUAL READABILITY PASS 2")
    print("Map:", report["map"])
    print("Visual settings:", len(report["visual_settings"]))
    print("Authored lights tuned:", len(report["lights"]))
    if args.dry_run:
        print("Dry run only; no files changed.")
    else:
        print("Relayfall patched and MAX archive validation passed.")
        print("Report:", REPORT)


if __name__ == "__main__":
    main()
