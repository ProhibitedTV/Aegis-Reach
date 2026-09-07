"""Pull the editor-saved Relayfall .fpm back from GameGuru MAX into the Git checkout.

Use this after native terrain sculpt/import work in MAX. The repo map is backed up before
replacement so editor-authored terrain can become the new source of truth safely.

Usage:
    python tools/sync_max_map.py pull
    python tools/sync_max_map.py pull --dry-run
"""
from __future__ import annotations

import argparse
import os
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_MAP = ROOT / "Aegis Reach" / "Files" / "mapbank" / "Aegis Reach - Relayfall.fpm"
BACKUPS = ROOT / "Aegis Reach" / "Design" / "map-backups"


def default_max_map() -> Path:
    profile = os.environ.get("USERPROFILE")
    if not profile:
        raise RuntimeError("USERPROFILE is not set; pass --source explicitly")
    return (
        Path(profile)
        / "Documents"
        / "GameGuruApps"
        / "GameGuruMAX"
        / "Files"
        / "mapbank"
        / "Aegis Reach - Relayfall.fpm"
    )


def pull(source: Path, dry_run: bool) -> None:
    if not source.exists():
        raise FileNotFoundError(f"MAX map not found: {source}")
    if not REPO_MAP.exists():
        raise FileNotFoundError(f"Repo map not found: {REPO_MAP}")

    print("AEGIS REACH // MAX MAP SYNC")
    print("MAX:", source)
    print("Repo:", REPO_MAP)
    print("MAX modified:", datetime.fromtimestamp(source.stat().st_mtime).isoformat(timespec="seconds"))
    print("Repo modified:", datetime.fromtimestamp(REPO_MAP.stat().st_mtime).isoformat(timespec="seconds"))
    print("MAX bytes:", source.stat().st_size)
    print("Repo bytes:", REPO_MAP.stat().st_size)

    if dry_run:
        print("Dry run only; no files changed.")
        return

    BACKUPS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUPS / f"Aegis Reach - Relayfall.pre-editor-sync.{stamp}.fpm"
    shutil.copy2(REPO_MAP, backup)
    shutil.copy2(source, REPO_MAP)
    print("Backup:", backup)
    print("Editor-saved map copied into the repo.")
    print("Review/test it, then commit the .fpm normally.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("pull",))
    parser.add_argument("--source", type=Path, help="override MAX Relayfall .fpm path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    pull(args.source or default_max_map(), args.dry_run)


if __name__ == "__main__":
    main()
