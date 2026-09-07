"""Collect one First Light native MAX run into a compact review report.

Run this after exiting or stopping a playtest. It does not alter the map or MAX
state. Local reports are intentionally ignored by Git.
"""
from pathlib import Path
import json
import os
import re
import time

from native_format import ROOT, INSTALL

GAME = ROOT / 'Aegis Reach'
DESIGN = GAME / 'Design/First Light'
TARGET = Path(os.environ['USERPROFILE']) / 'Documents/GameGuruApps/GameGuruMAX/Files'
OUT = DESIGN / 'runtime-reports'

LOGS = [
    TARGET / 'first-light-diagnostics.log',
    TARGET / 'first-light-runtime.log',
    TARGET / 'aegis-native-runtime.log',
    GAME / 'Guru-Game.log',
    INSTALL.parent / 'Guru-Game.log',
]

PATTERNS = {
    'lua_errors': re.compile(r'LUA_ERROR|LUA ERROR|attempt to (?:call|index)|stack traceback', re.I),
    'music_init': re.compile(r'FIRST_LIGHT music_init|music_fallback', re.I),
    'music_states': re.compile(r'music_state state=', re.I),
    'enemy_activation': re.compile(r'enemy_activated', re.I),
    'qa_actor_samples': re.compile(r'QA_ACTOR|actor e=', re.I),
    'qa_failures': re.compile(r'QA_NATIVE_FAILURE', re.I),
    'qa_complete': re.compile(r'QA_NATIVE_COMPLETE', re.I),
    'mission_complete': re.compile(r'MISSION_COMPLETE', re.I),
}


def read_text(path):
    try:
        return path.read_text(errors='replace')
    except OSError:
        return ''


def tail_lines(text, count=220):
    lines = text.splitlines()
    return lines[-count:]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')

    launch_path = DESIGN / 'last-launch.json'
    preflight_path = DESIGN / 'preflight.json'
    launch = json.loads(launch_path.read_text()) if launch_path.is_file() else {}
    preflight = json.loads(preflight_path.read_text()) if preflight_path.is_file() else {}

    logs = {}
    merged = []
    for path in LOGS:
        if not path.is_file():
            continue
        text = read_text(path)
        key = str(path)
        logs[key] = {
            'bytes': path.stat().st_size,
            'modified': path.stat().st_mtime,
            'tail': tail_lines(text),
        }
        merged.extend(text.splitlines())

    evidence = {}
    for name, pattern in PATTERNS.items():
        hits = [line for line in merged if pattern.search(line)]
        evidence[name] = hits[-60:]

    blockers = []
    if evidence['lua_errors']:
        blockers.append('Lua/runtime error recorded')
    if evidence['qa_failures']:
        blockers.append('Native QA failure recorded')
    if launch.get('qa') and not evidence['qa_complete']:
        blockers.append('QA launch did not record QA_NATIVE_COMPLETE')
    if not evidence['music_init']:
        blockers.append('No score initialization evidence found')

    report = {
        'captured_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'launch': launch,
        'preflight': preflight,
        'logs': logs,
        'evidence': evidence,
        'blockers': blockers,
        'human_review_required': [
            'opening vista and terrain composition',
            'music audible at useful mix level',
            'no visible T-pose or animation pop on activation',
            'enemy navigation and cover use',
            'no floating/intersecting geometry',
            'Northstar / Operations / AEGIS visual differentiation',
            'return-route combat and extraction readability',
        ],
    }

    path = OUT / f'first-light-native-{stamp}.json'
    path.write_text(json.dumps(report, indent=2))

    print('FIRST LIGHT // NATIVE RUN COLLECTED')
    print('Report:', path)
    print('Logs found:', len(logs))
    print('Lua errors:', len(evidence['lua_errors']))
    print('Music evidence:', len(evidence['music_init']) + len(evidence['music_states']))
    print('Enemy activation lines:', len(evidence['enemy_activation']))
    print('QA actor samples:', len(evidence['qa_actor_samples']))
    if blockers:
        print('BLOCKERS:')
        for item in blockers:
            print(' -', item)
    else:
        print('No log-level blocker detected. Visual/combat review still required.')


if __name__ == '__main__':
    main()
