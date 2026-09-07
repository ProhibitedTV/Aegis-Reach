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
    'qa_failures': re.compile(r'QA_NATIVE_FAILURE|QA_GEOMETRY_WARNING', re.I),
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


def unique_tail(lines, limit=12):
    out=[];seen=set()
    for line in reversed(lines):
        clean=line.strip()
        if clean and clean not in seen:
            seen.add(clean);out.append(clean)
        if len(out)>=limit:break
    return list(reversed(out))


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
    notes = []
    if evidence['lua_errors']:
        blockers.append('Lua/runtime error recorded')
    if evidence['qa_failures']:
        blockers.append('Native QA/geometry warning recorded')
    if launch.get('qa') and not evidence['qa_complete']:
        notes.append('QA run ended before mission completion; this is not itself a failure in observational QA mode')
    if not evidence['music_init']:
        blockers.append('No score initialization evidence found')

    report = {
        'captured_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'launch': launch,
        'preflight': preflight,
        'logs': logs,
        'evidence': evidence,
        'blockers': blockers,
        'notes': notes,
        'human_review_required': [
            'opening vista and terrain composition',
            'music audible at useful mix level',
            'no visible T-pose or animation pop on activation',
            'enemy navigation and cover use',
            'no floating/intersecting geometry or z-fighting',
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
    if evidence['lua_errors']:
        print('LATEST UNIQUE LUA/RUNTIME ERRORS:')
        for line in unique_tail(evidence['lua_errors']):print(' !',line)
    if evidence['qa_failures']:
        print('QA / GEOMETRY WARNINGS:')
        for line in unique_tail(evidence['qa_failures']):print(' !',line)
    if blockers:
        print('BLOCKERS:')
        for item in blockers:
            print(' -', item)
    else:
        print('No log-level blocker detected. Visual/combat review still required.')
    for item in notes:print('NOTE:',item)


if __name__ == '__main__':
    main()
