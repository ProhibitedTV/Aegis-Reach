"""Summarize Aegis Reach runtime combat telemetry after a GameGuru MAX playtest.

Usage:
    python tools/summarize_playtest.py
    python tools/summarize_playtest.py --json
    python tools/summarize_playtest.py path/to/native-runtime.log

The director intentionally writes simple append-only text so a failed or aborted MAX
session still leaves useful balancing evidence behind.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG = ROOT / "Aegis Reach" / "Design" / "native-runtime.log"
PHASE_NAMES = {
    1: "Insertion / Northstar",
    2: "Lantern",
    3: "AEGIS core",
    4: "Kestrel extraction",
}

START_RE = re.compile(
    r"encounter_start id=(?P<id>\d+) phase=(?P<phase>\d+) contacts=(?P<contacts>\d+) "
    r"armour=(?P<armour>\d+) shield=(?P<shield>\d+)"
)
CLEAR_RE = re.compile(
    r"encounter_clear id=(?P<id>\d+) phase=(?P<phase>\d+) duration=(?P<duration>[\d.]+)s "
    r"kills=(?P<kills>\d+) armour_loss=(?P<armour_loss>\d+) shield_breaks=(?P<breaks>\d+)"
)
BREAK_RE = re.compile(
    r"shield_break total=(?P<total>\d+) phase=(?P<phase>\d+) armour=(?P<armour>\d+)"
)
SIGNAL_RE = re.compile(r"signal_mode (?P<mode>\w+) phase=(?P<phase>\d+)")
MISSION_RE = re.compile(r"mission_started .* player=(?P<position>.+)$")


def parse_log(path: Path) -> dict:
    encounters: dict[int, dict] = {}
    signal_events: list[dict] = []
    shield_events: list[dict] = []
    mission_starts = 0

    if not path.exists():
        return {
            "log": str(path),
            "available": False,
            "message": "No runtime log found. Launch Relayfall in GameGuru MAX first.",
            "encounters": [],
        }

    for line_number, raw in enumerate(path.read_text(errors="replace").splitlines(), 1):
        line = raw.strip()
        if MISSION_RE.search(line):
            mission_starts += 1

        match = START_RE.search(line)
        if match:
            values = {k: int(v) for k, v in match.groupdict().items()}
            encounter = encounters.setdefault(values["id"], {"id": values["id"]})
            encounter.update(
                phase=values["phase"],
                phase_name=PHASE_NAMES.get(values["phase"], f"Phase {values['phase']}"),
                opening_contacts=values["contacts"],
                starting_armour=values["armour"],
                starting_shield=values["shield"],
                started_line=line_number,
                completed=False,
            )
            continue

        match = CLEAR_RE.search(line)
        if match:
            values = match.groupdict()
            encounter_id = int(values["id"])
            phase = int(values["phase"])
            encounter = encounters.setdefault(encounter_id, {"id": encounter_id})
            encounter.update(
                phase=phase,
                phase_name=PHASE_NAMES.get(phase, f"Phase {phase}"),
                duration_seconds=float(values["duration"]),
                kills=int(values["kills"]),
                armour_loss=int(values["armour_loss"]),
                shield_breaks=int(values["breaks"]),
                completed=True,
                cleared_line=line_number,
            )
            continue

        match = BREAK_RE.search(line)
        if match:
            shield_events.append(
                {
                    "line": line_number,
                    "total": int(match.group("total")),
                    "phase": int(match.group("phase")),
                    "armour": int(match.group("armour")),
                }
            )
            continue

        match = SIGNAL_RE.search(line)
        if match:
            signal_events.append(
                {
                    "line": line_number,
                    "mode": match.group("mode"),
                    "phase": int(match.group("phase")),
                }
            )

    ordered = [encounters[key] for key in sorted(encounters)]
    completed = [e for e in ordered if e.get("completed")]
    phase_totals: dict[int, dict] = defaultdict(
        lambda: {"encounters": 0, "combat_seconds": 0.0, "kills": 0, "armour_loss": 0, "shield_breaks": 0}
    )
    for encounter in completed:
        phase = int(encounter.get("phase", 0))
        totals = phase_totals[phase]
        totals["encounters"] += 1
        totals["combat_seconds"] += float(encounter.get("duration_seconds", 0))
        totals["kills"] += int(encounter.get("kills", 0))
        totals["armour_loss"] += int(encounter.get("armour_loss", 0))
        totals["shield_breaks"] += int(encounter.get("shield_breaks", 0))

    total_seconds = sum(float(e.get("duration_seconds", 0)) for e in completed)
    total_kills = sum(int(e.get("kills", 0)) for e in completed)
    total_armour_loss = sum(int(e.get("armour_loss", 0)) for e in completed)
    total_breaks = max((event["total"] for event in shield_events), default=sum(int(e.get("shield_breaks", 0)) for e in completed))

    return {
        "log": str(path),
        "available": True,
        "mission_starts_in_log": mission_starts,
        "encounters": ordered,
        "totals": {
            "completed_encounters": len(completed),
            "combat_seconds": round(total_seconds, 1),
            "kills": total_kills,
            "armour_loss": total_armour_loss,
            "shield_breaks": total_breaks,
        },
        "phase_totals": {
            str(phase): {
                "phase_name": PHASE_NAMES.get(phase, f"Phase {phase}"),
                **{k: round(v, 1) if isinstance(v, float) else v for k, v in values.items()},
            }
            for phase, values in sorted(phase_totals.items())
        },
        "signal_events": signal_events,
        "shield_events": shield_events,
    }


def print_human(summary: dict) -> None:
    print("AEGIS REACH // RELAYFALL PLAYTEST TELEMETRY")
    print("=" * 47)
    if not summary.get("available"):
        print(summary.get("message", "No telemetry available."))
        print(summary.get("log", ""))
        return

    totals = summary["totals"]
    print(f"Log: {summary['log']}")
    print(f"Sessions represented: {summary['mission_starts_in_log']}")
    print(
        "Combat: "
        f"{totals['completed_encounters']} completed encounters / "
        f"{totals['combat_seconds']:.1f}s / {totals['kills']} eliminations"
    )
    print(f"Cost: {totals['armour_loss']} armour lost / {totals['shield_breaks']} shield breaks")
    print()

    for encounter in summary["encounters"]:
        status = "CLEAR" if encounter.get("completed") else "INCOMPLETE"
        line = f"#{encounter['id']} {encounter.get('phase_name', 'Unknown')} // {status}"
        if encounter.get("completed"):
            line += (
                f" // {encounter.get('duration_seconds', 0):.1f}s"
                f" // {encounter.get('kills', 0)} kills"
                f" // -{encounter.get('armour_loss', 0)} armour"
                f" // {encounter.get('shield_breaks', 0)} breaks"
            )
        else:
            line += f" // opened with {encounter.get('opening_contacts', '?')} contacts"
        print(line)

    if summary["signal_events"]:
        print("\nAEGIS signal transitions:")
        for event in summary["signal_events"]:
            print(f"  phase {event['phase']}: {event['mode']}")

    print("\nInterpretation targets:")
    print("  - Opening breach: ideally ~20-35 seconds once navigation is healthy.")
    print("  - Repeated shield breaks without armour loss can be exciting; repeated armour loss means pressure may be too sticky.")
    print("  - AEGIS-core combat should be the longest offensive beat, not an endless attrition fight.")
    print("  - Extraction should feel faster and more aggressive after the uplink boost.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", nargs="?", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    summary = parse_log(args.log)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_human(summary)


if __name__ == "__main__":
    main()
