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
REPORT = GAME / "Design" / "visual-pass-3.json"

# This is intentionally brighter than the previous pass. The first-person weapon,
# dark MAX materials and generated architecture were all consuming the same midtones,
# so the result looked murky even when screenshots appeared technically exposed.
VISUAL_SETTINGS = {
    "sky$": "highcloud",
    "DisableSkybox": 0,
    "TimeOfday": 8,
    "Simulate24Hours": 0,
    "Exposure": 1.42,
    "PostBrightness#": 0.11,
    "PostContrast#": 1.05,
    "Gamma": 2.2,
    "DeSaturate": 1,
    "AmbienceIntensity#": 225,
    "AmbienceRed#": 188,
    "AmbienceGeen#": 205,
    "AmbienceBlue#": 228,
    "SurfaceIntensity#": 1.26,
    "SunIntensity": 1.55,
    "SunRed": 1.0,
    "SunGreen": 0.88,
    "SunBlue": 0.76,
    "SunAngleX": 38,
    "SunAngleY": 318,
    "ZenithRed": 58,
    "ZenithGreen": 84,
    "ZenithBlue": 118,
    "FogNearest#": 6500,
    "FogDistance#": 32000,
    "FogR#": 56,
    "FogG#": 76,
    "FogB#": 100,
    "BloomThreshold": 1.3,
    "BloomStrength": 0.18,
    "EnvProbeBrightness": 1.28,
    "SkyCloudiness": 0.38,
    "SkyCloudCoverage": 0.68,
    "MotionIntensity#": 0,
    "LevelVSyncEnabled": 1,
    # Belt-and-suspenders fallback. aegis_music.lua takes over at runtime with the
    # supplied score, but this checked-in bed prevents a silent scene if that controller
    # is not initialized for any reason.
    "AmbientMusicTrack": r"audiobank\aegis_reach\reach-underscore.wav",
    "AmbientMusicTrackVolume": 42,
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
    current = entity[key]
    if isinstance(current, bool):
        entity[key] = bool(value)
    elif isinstance(current, int):
        entity[key] = int(round(value))
    elif isinstance(current, float):
        entity[key] = float(value)
    elif isinstance(current, str):
        entity[key] = str(value)
    else:
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
        color = CYAN if index % 2 else AMBER
        radius = 2050 if index in (1, 2, 3, 4) else 1850
        old_range = get_suffix(entity, "eleprof.light.range")
        old_color = get_suffix(entity, "eleprof.light.color")

        set_suffix(entity, "eleprof.light.range", radius)
        set_suffix(entity, "eleprof.light.color", color)
        set_suffix(entity, "eleprof.light.fLightHasProbe", 1)

        changed.append(
            {
                "name": name,
                "range_before": old_range,
                "range_after": get_suffix(entity, "eleprof.light.range"),
                "color_before": old_color,
                "color_after": hex(int(get_suffix(entity, "eleprof.light.color", color))),
            }
        )

    result = write_ele(version, entities)
    roundtrip_version, roundtrip_entities = read_ele(result)
    assert roundtrip_version == version
    assert len(roundtrip_entities) == len(entities)
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
        backup_path = path.with_name(path.stem + ".pre-visual-pass-3.fpm")
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

        with zipfile.ZipFile(temp_path) as check:
            check.setpassword(PASSWORD)
            assert check.read("visuals.ini") == patched_visuals
            assert check.read("map.ele") == patched_ele

        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()

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
    print("AEGIS REACH // VISUAL READABILITY PASS 3")
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
