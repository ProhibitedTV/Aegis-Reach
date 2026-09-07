"""Stage the supplied Aegis Reach score masters into the GameGuru project.

The ChatGPT/GitHub connector can edit repository text but cannot reliably stream the
large WAV attachment bytes into GitHub. This tool makes the runtime integration
repeatable on the development machine: it locates the original Suno downloads in
common folders, verifies/records them, and copies full-quality WAVs into audiobank.

Examples:
    python tools/import_music.py
    python tools/import_music.py --source "%USERPROFILE%\Downloads" --strict
    python tools/import_music.py --source "D:\Music\Aegis Reach"

Production deploy calls stage_music(strict=False), so once the three masters exist in
Downloads/Desktop/Music or already in the repo, `max_playtest.py deploy --production`
will stage and deploy them automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT / "Aegis Reach"
DEST = GAME / "Files" / "audiobank" / "aegis_reach" / "music"
MANIFEST = GAME / "Design" / "music-manifest.json"

TRACKS = [
    {
        "id": "salt_moon_drift",
        "canonical": "salt_moon_drift.wav",
        "aliases": ["Salt Moon Drift.wav", "salt_moon_drift.wav"],
        "expected_sha256": "1f8fd2b632df61d3229e957c87f5cdef4315794f943fc218181f7609bd585b68",
        "expected_seconds": 179.640,
        "role": "Vesper exterior / human discovery",
        "slot": 0,
    },
    {
        "id": "moon_outpost_drift",
        "canonical": "moon_outpost_drift.wav",
        "aliases": ["Moon Outpost Drift.wav", "moon_outpost_drift.wav"],
        "expected_sha256": "2028f2f2d4e3f0cda7e97dbf403e38ef16d3dd56be5d996c87a419ccba496a0a",
        "expected_seconds": 142.608,
        "role": "fortress / tactical pressure / AEGIS resolution",
        "slot": 1,
    },
    {
        "id": "orbital_catacomb",
        "canonical": "orbital_catacomb.wav",
        "aliases": ["Orbital Catacomb(1).wav", "Orbital Catacomb.wav", "orbital_catacomb.wav"],
        "expected_sha256": "bfcad4c9585fe55667d2295a5fc5ad0ac1512702485e12aadd4ce45284b398c8",
        "expected_seconds": 154.512,
        "role": "AEGIS interference / Choir discovery / deep interior",
        "slot": 2,
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audio_info(path: Path) -> dict:
    with wave.open(str(path), "rb") as audio:
        return {
            "channels": audio.getnchannels(),
            "sample_rate": audio.getframerate(),
            "sample_width_bytes": audio.getsampwidth(),
            "frames": audio.getnframes(),
            "seconds": round(audio.getnframes() / audio.getframerate(), 3),
        }


def default_sources() -> list[Path]:
    roots = [Path.cwd(), ROOT, ROOT.parent]
    profile = os.environ.get("USERPROFILE")
    home = Path(profile) if profile else Path.home()
    roots.extend([
        home / "Downloads", home / "Desktop", home / "Music",
        home / "OneDrive" / "Downloads", home / "OneDrive" / "Desktop", home / "OneDrive" / "Music",
    ])
    result = []
    seen = set()
    for root in roots:
        try:
            key = str(root.resolve()).lower()
        except OSError:
            key = str(root).lower()
        if key not in seen:
            seen.add(key)
            result.append(root)
    return result


def find_track(track: dict, sources: list[Path]) -> Path | None:
    # Prefer an already staged canonical master.
    existing = DEST / track["canonical"]
    if existing.exists():
        return existing

    for source in sources:
        if source.is_file():
            if source.name.lower() in {name.lower() for name in track["aliases"]}:
                return source
            continue
        if not source.is_dir():
            continue
        for alias in track["aliases"]:
            candidate = source / alias
            if candidate.exists():
                return candidate
    return None


def stage_music(extra_sources: list[Path] | None = None, *, strict: bool = False) -> dict:
    sources = list(extra_sources or []) + default_sources()
    DEST.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    entries = []
    missing = []
    for track in TRACKS:
        source = find_track(track, sources)
        destination = DEST / track["canonical"]
        if source is None:
            missing.append(track["id"])
            entries.append({**track, "status": "missing", "destination": str(destination.relative_to(ROOT))})
            continue

        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)
        info = audio_info(destination)
        digest = sha256(destination)
        entries.append({
            **track,
            "status": "staged",
            "source": str(source),
            "destination": str(destination.relative_to(ROOT)),
            "sha256": digest,
            "master_hash_match": digest == track["expected_sha256"],
            "bytes": destination.stat().st_size,
            **info,
        })

    report = {
        "format": "PCM WAV masters; GameGuru MAX non-3D sound slots",
        "destination": str(DEST.relative_to(ROOT)),
        "tracks": entries,
        "missing": missing,
        "ready": not missing,
    }
    MANIFEST.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if strict and missing:
        raise FileNotFoundError("Missing score masters: " + ", ".join(missing))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", type=Path, default=[], help="extra source file or directory; repeatable")
    parser.add_argument("--strict", action="store_true", help="fail unless all three supplied masters are found")
    args = parser.parse_args()

    report = stage_music(args.source, strict=args.strict)
    print("AEGIS REACH // SCORE IMPORT")
    for track in report["tracks"]:
        if track["status"] == "staged":
            match = "master verified" if track["master_hash_match"] else "different revision"
            print(f"[OK] {track['id']}: {track['seconds']:.3f}s / {track['sample_rate']} Hz / {match}")
        else:
            print(f"[--] {track['id']}: not found")
    print("Manifest:", MANIFEST)
    if report["missing"]:
        print("Missing files can be supplied with --source <folder-or-file>.")
    else:
        print("All score masters staged for MAX deployment.")


if __name__ == "__main__":
    main()
