"""Verify and package a GameGuru MAX standalone export of Aegis Reach: First Light.

This tool intentionally operates on MAX's exported standalone directory, not the
editable project checkout. It catches the common failure mode where a source/dev
package is accidentally published as if it were a self-contained Windows build.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

DEFAULT_ROOT = Path(os.environ.get("AEGIS_STANDALONE_DIR", r"C:\AegisReachBuilds\First-Light"))
TRACKS = (
    "salt_moon_drift.wav",
    "moon_outpost_drift.wav",
    "orbital_catacomb.wav",
)
SOURCE_ONLY_TOP_LEVEL = {".git", ".github", "tools", "design", "__pycache__"}
MIN_EXPORT_BYTES = 25 * 1024 * 1024
MIN_EXE_BYTES = 512 * 1024


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def all_files(root: Path) -> list[Path]:
    return sorted(
        (p for p in root.rglob("*") if p.is_file() and p.name != "standalone-manifest.json"),
        key=lambda p: str(p.relative_to(root)).lower(),
    )


def inspect(root: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not root.is_dir():
        return {
            "root": str(root),
            "errors": [f"Standalone export directory does not exist: {root}"],
            "warnings": [],
            "files": [],
            "executables": [],
            "maps": [],
            "tracks": {},
            "lua_count": 0,
            "total_bytes": 0,
        }

    files = all_files(root)
    total_bytes = sum(p.stat().st_size for p in files)
    top_names = {p.name.lower() for p in root.iterdir()}
    source_leaks = sorted(SOURCE_ONLY_TOP_LEVEL.intersection(top_names))
    if source_leaks:
        errors.append(
            "Export contains source/editor-only top-level entries: " + ", ".join(source_leaks)
        )

    root_exes = [p for p in root.glob("*.exe") if p.is_file()]
    if not root_exes:
        errors.append("No root-level Windows executable was found in the standalone export.")
    elif not any(p.stat().st_size >= MIN_EXE_BYTES for p in root_exes):
        errors.append("Root-level EXE files are unexpectedly small; export may be incomplete.")

    maps = [p for p in files if p.suffix.lower() == ".fpm" and "first light" in p.name.lower()]
    if not maps:
        errors.append("First Light .fpm map was not found in the exported runtime tree.")

    tracks = {}
    lower_by_name: dict[str, list[Path]] = {}
    for p in files:
        lower_by_name.setdefault(p.name.lower(), []).append(p)
    for name in TRACKS:
        matches = lower_by_name.get(name.lower(), [])
        tracks[name] = [str(p.relative_to(root)) for p in matches]
        if not matches:
            errors.append(f"Required score master is missing from standalone export: {name}")

    aegis_lua = [
        p for p in files
        if p.suffix.lower() == ".lua"
        and ("aegis_reach" in str(p).lower() or p.name.lower().startswith("aegis_"))
    ]
    if not aegis_lua:
        errors.append("No Aegis Reach Lua runtime scripts were found in the export.")

    zero_runtime = [
        p for p in files
        if p.stat().st_size == 0 and p.suffix.lower() in {".exe", ".dll", ".fpm", ".lua", ".wav"}
    ]
    if zero_runtime:
        errors.append(
            "Zero-byte runtime files found: "
            + ", ".join(str(p.relative_to(root)) for p in zero_runtime[:12])
        )

    dlls = [p for p in files if p.suffix.lower() == ".dll"]
    if not dlls:
        warnings.append("No DLLs were found. Confirm this MAX build embeds all runtime dependencies.")

    if total_bytes < MIN_EXPORT_BYTES:
        errors.append(
            f"Standalone tree is only {total_bytes / (1024 * 1024):.1f} MiB; this looks incomplete."
        )

    if any(p.name.lower() in {"play first light.cmd", "collect first light.cmd"} for p in files):
        errors.append("Developer launch/collection scripts leaked into the standalone export.")

    return {
        "root": str(root),
        "errors": errors,
        "warnings": warnings,
        "files": files,
        "executables": [str(p.relative_to(root)) for p in root_exes],
        "maps": [str(p.relative_to(root)) for p in maps],
        "tracks": tracks,
        "lua_count": len(aegis_lua),
        "dll_count": len(dlls),
        "total_bytes": total_bytes,
    }


def print_report(report: dict) -> None:
    print("Aegis Reach: First Light standalone verification")
    print("Root:", report["root"])
    print("Files:", len(report.get("files", [])))
    print(f"Size: {report.get('total_bytes', 0) / (1024 * 1024):.1f} MiB")
    print("Executables:", ", ".join(report.get("executables", [])) or "NONE")
    print("First Light maps:", ", ".join(report.get("maps", [])) or "NONE")
    print("Aegis Lua scripts:", report.get("lua_count", 0))
    print("Runtime DLLs:", report.get("dll_count", 0))
    for warning in report.get("warnings", []):
        print("WARNING:", warning)
    for error in report.get("errors", []):
        print("ERROR:", error)
    print("RESULT:", "PASS" if not report.get("errors") else "FAIL")


def build_manifest(root: Path, report: dict) -> dict:
    file_rows = []
    for path in report["files"]:
        rel = str(path.relative_to(root)).replace("\\", "/")
        file_rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256(path)})
    return {
        "format": 1,
        "product": "Aegis Reach: First Light",
        "platform": "win64",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_git_head": git_head(),
        "export_directory_name": root.name,
        "file_count": len(file_rows),
        "total_bytes": report["total_bytes"],
        "executables": report["executables"],
        "first_light_maps": report["maps"],
        "tracks": report["tracks"],
        "lua_count": report["lua_count"],
        "dll_count": report["dll_count"],
        "warnings": report["warnings"],
        "files": file_rows,
    }


def verify(root: Path, manifest_path: Path | None = None) -> int:
    report = inspect(root)
    print_report(report)
    if report["errors"]:
        return 1
    if manifest_path:
        manifest = build_manifest(root, report)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print("Manifest:", manifest_path)
    return 0


def release_notes(tag: str, manifest: dict) -> str:
    exe = manifest["executables"][0] if manifest["executables"] else "the exported game executable"
    return f"""# Aegis Reach: First Light — Windows Standalone

**{tag}** is a GameGuru MAX standalone export of First Light (Mission 01) for Windows x64.

## Run
1. Download and extract the ZIP.
2. Launch `{exe}` from the extracted folder.
3. Keep the exported directory structure intact.

This artifact is the standalone player build, not the editable GameGuru MAX project package. GameGuru MAX and the authoring asset packs are not required to launch this exported build.

## Build verification
- Source commit: `{manifest['source_git_head']}`
- Files: {manifest['file_count']}
- Uncompressed size: {manifest['total_bytes'] / (1024 * 1024):.1f} MiB
- Aegis Lua scripts: {manifest['lua_count']}
- Runtime DLLs: {manifest['dll_count']}
- All three authored score masters were present at packaging time.
- `standalone-manifest.json` inside the ZIP records SHA-256 hashes for the exported files.

A clean-machine smoke test is still recommended for every new MAX engine/update before promoting a prerelease to a final release.
"""


def package(root: Path, tag: str, output_dir: Path) -> int:
    report = inspect(root)
    print_report(report)
    if report["errors"]:
        print("Refusing to package an invalid standalone export.")
        return 1

    manifest = build_manifest(root, report)
    safe_tag = tag[1:] if tag.lower().startswith("v") else tag
    package_name = f"Aegis-Reach-First-Light-{safe_tag}-win64"
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"{package_name}.zip"
    checksum_path = output_dir / f"{package_name}.zip.sha256"
    notes_path = output_dir / f"{package_name}-release-notes.md"

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(
        zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True
    ) as zf:
        prefix = Path(package_name)
        for path in report["files"]:
            rel = path.relative_to(root)
            zf.write(path, (prefix / rel).as_posix())
        zf.writestr(
            (prefix / "standalone-manifest.json").as_posix(),
            json.dumps(manifest, indent=2).encode("utf-8"),
        )

    digest = sha256(zip_path)
    checksum_path.write_text(f"{digest}  {zip_path.name}\n", encoding="ascii")
    notes_path.write_text(release_notes(tag, manifest), encoding="utf-8")
    print("PACKAGE:", zip_path)
    print("SHA256:", digest)
    print("CHECKSUM:", checksum_path)
    print("NOTES:", notes_path)
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("verify", help="verify a MAX standalone export")
    v.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    v.add_argument("--manifest", type=Path)

    pack = sub.add_parser("package", help="verify and ZIP a MAX standalone export")
    pack.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    pack.add_argument("--tag", required=True)
    pack.add_argument("--output-dir", type=Path, default=Path("dist"))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    if args.command == "verify":
        manifest = args.manifest.expanduser().resolve() if args.manifest else None
        return verify(root, manifest)
    return package(root, args.tag, args.output_dir.expanduser().resolve())


if __name__ == "__main__":
    raise SystemExit(main())
