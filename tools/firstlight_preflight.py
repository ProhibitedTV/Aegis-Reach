"""Fail-fast preflight for native First Light playtests.

This is deliberately stricter than the general structural test: it verifies the
runtime map that MAX is about to load, the three authored score masters, and the
absence of known load-blocking stock weapon.lua pickups. It also runs the Lua 5.2
compatibility and mission-rule suites before a native launch.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile

from native_format import ROOT, read_ele
from max_archive import PASSWORD

GAME = ROOT / 'Aegis Reach'
FILES = GAME / 'Files'
DESIGN = GAME / 'Design/First Light'
MAP = FILES / 'mapbank/Aegis Reach - First Light.fpm'
REPORT = DESIGN / 'preflight.json'
TRACKS = [
    'salt_moon_drift.wav',
    'moon_outpost_drift.wav',
    'orbital_catacomb.wav',
]
BAD_SCRIPTS = {'weapon.lua', 'scriptbank\\weapon.lua'}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def run_test(name):
    path = ROOT / 'tools' / name
    result = subprocess.run([sys.executable, str(path)], cwd=ROOT)
    if result.returncode:
        raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: {name} returned {result.returncode}')


def normalized_script(entity):
    return str(entity.get('101:eleprof.aimain_s', '')).replace('/', '\\').lower()


def main():
    if not MAP.is_file():
        raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: missing map {MAP}')

    run_test('test_firstlight_lua_compat.py')
    run_test('test_firstlight.py')

    with zipfile.ZipFile(MAP) as archive:
        archive.setpassword(PASSWORD)
        version, entities = read_ele(archive.read('map.ele'))
        encrypted = all(info.flag_bits & 1 for info in archive.infolist())

    bad = [
        str(e.get('101:eleprof.name_s', '<unnamed>'))
        for e in entities
        if normalized_script(e) in BAD_SCRIPTS
    ]
    if bad:
        raise SystemExit(
            'FIRST LIGHT // PREFLIGHT FAILED: unsafe stock weapon.lua entities remain: '
            + ', '.join(bad)
        )
    if not encrypted:
        raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: map archive is not fully MAX-encrypted')

    track_info = {}
    for name in TRACKS:
        path = FILES / 'audiobank/aegis_reach/music' / name
        if not path.is_file():
            raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: missing score master {name}')
        size = path.stat().st_size
        if size < 1024 * 1024:
            raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: suspiciously small score master {name}: {size} bytes')
        track_info[name] = {'bytes': size, 'sha256': sha256(path)}

    required_scripts = [
        'firstlight_audit.lua',
        'firstlight_director.lua',
        'firstlight_enemy.lua',
        'firstlight_interact.lua',
        'firstlight_score.lua',
    ]
    for name in required_scripts:
        path = FILES / 'scriptbank/aegis_reach' / name
        if not path.is_file():
            raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: missing runtime script {name}')

    score_text = (FILES / 'scriptbank/aegis_reach/firstlight_score.lua').read_text(errors='replace')
    for name in TRACKS:
        if name not in score_text:
            raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: score controller does not reference {name}')

    report = {
        'map': str(MAP.relative_to(ROOT)),
        'map_sha256': sha256(MAP),
        'map_bytes': MAP.stat().st_size,
        'map_version': version,
        'entity_count': len(entities),
        'unsafe_weapon_pickups': bad,
        'archive_encrypted': encrypted,
        'tracks': track_info,
        'tests': ['test_firstlight_lua_compat.py', 'test_firstlight.py'],
        'native_playtest_required': True,
    }
    DESIGN.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2))

    print('FIRST LIGHT // PREFLIGHT PASS')
    print('Map entities:', len(entities))
    print('Map SHA256:', report['map_sha256'][:16])
    print('Score masters:', ', '.join(TRACKS))
    print('Unsafe stock weapon pickups: 0')
    print('Native MAX playtest is still required.')


if __name__ == '__main__':
    main()
