"""Collect one First Light native MAX run into a production tuning report.

Run this after exiting or stopping a playtest. It does not alter the map or MAX
state. Each launch snapshots append-only log offsets, so this collector analyzes only
the current run and cannot inherit stale errors/events from an earlier playtest.
Local reports are intentionally ignored by Git.
"""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime
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
    'director_ticks': re.compile(r'\btick stage=.*\bpressure=', re.I),
    'combat_enter': re.compile(r'combat_enter', re.I),
    'combat_clear': re.compile(r'combat_clear', re.I),
    'enemy_activation': re.compile(r'enemy_activated', re.I),
    'enemy_down': re.compile(r'enemy_down', re.I),
    'squad_start': re.compile(r'squad_start', re.I),
    'squad_clear': re.compile(r'squad_clear', re.I),
    'reveal_held': re.compile(r'reveal_held', re.I),
    'evacuation_started': re.compile(r'evacuation_started', re.I),
    'qa_actor_samples': re.compile(r'QA_ACTOR|actor e=', re.I),
    'qa_failures': re.compile(r'QA_NATIVE_FAILURE|QA_GEOMETRY_WARNING', re.I),
    'qa_complete': re.compile(r'QA_NATIVE_COMPLETE', re.I),
    'mission_complete': re.compile(r'MISSION_COMPLETE', re.I),
}

KV = re.compile(r'([A-Za-z_]+)=([^\s]+)')
STAMP = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b')


def read_since(path, offset):
    """Read bytes appended after a launch snapshot; recover safely from log rotation."""
    try:
        size=path.stat().st_size
        start=max(0,int(offset or 0))
        rotated=start>size
        if rotated:start=0
        with path.open('rb') as f:
            f.seek(start)
            data=f.read()
        return data.decode('utf-8',errors='replace'),start,size,rotated
    except OSError:
        return '',0,0,False


def tail_lines(text, count=260):
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


def kv(line):
    return dict(KV.findall(line))


def number(values,key,cast=float,default=None):
    try:return cast(values[key])
    except (KeyError,TypeError,ValueError):return default


def line_time(line):
    match=STAMP.match(line)
    if not match:return None
    try:return datetime.strptime(match.group(1),'%Y-%m-%d %H:%M:%S')
    except ValueError:return None


def band(value):
    if value>=72:return 'CRITICAL'
    if value>=42:return 'HIGH'
    if value>=16:return 'ELEVATED'
    return 'LOW'


def build_tuning(evidence):
    ticks=[]
    for line in evidence['director_ticks']:
        values=kv(line)
        pressure=number(values,'pressure',int)
        if pressure is None:continue
        ticks.append({
            'pressure':pressure,
            'band':band(pressure),
            'contacts':number(values,'contacts',int,0),
            'health':number(values,'health',int),
            'kills':number(values,'kills',int),
            'stage':number(values,'stage',int),
            'budget':number(values,'budget',int),
        })

    activations=[]
    for line in evidence['enemy_activation']:
        values=kv(line)
        activations.append({
            'group':number(values,'group',int),
            'index':number(values,'index',int),
            'role':values.get('role'),
            'reason':values.get('reason'),
            'wait_ms':number(values,'wait',int,0),
            'budget':number(values,'budget',float),
            'time':line_time(line),
        })

    held=[]
    for line in evidence['reveal_held']:
        values=kv(line)
        held.append({
            'entity':number(values,'e',int),
            'group':number(values,'group',int),
            'role':values.get('role'),
            'watched_ms':number(values,'watched_ms',int,0),
            'distance':number(values,'distance',int),
        })

    squads=[]
    for line in evidence['squad_clear']:
        values=kv(line)
        squads.append({
            'group':number(values,'group',int),
            'duration_s':round(number(values,'duration_ms',int,0)/1000,1),
            'armour_loss':number(values,'armour_loss',int,0),
            'end_armour':number(values,'end_armour',int),
            'end_shield':number(values,'end_shield',int),
            'peak_pressure':number(values,'peak_pressure',int,0),
        })

    evac_time=line_time(evidence['evacuation_started'][-1]) if evidence['evacuation_started'] else None
    extraction_arrivals=[]
    if evac_time:
        for event in activations:
            if event['group']==7 and event['time']:
                extraction_arrivals.append({
                    'index':event['index'],'role':event['role'],
                    'seconds_after_evac_start':round((event['time']-evac_time).total_seconds(),1)
                })

    bands=Counter(t['band'] for t in ticks)
    roles=Counter(a['role'] for a in activations if a['role'])
    reasons=Counter(a['reason'] for a in activations if a['reason'])
    groups=Counter(str(a['group']) for a in activations if a['group'] is not None)
    held_entities=defaultdict(int)
    for event in held:
        if event['entity'] is not None:
            held_entities[str(event['entity'])]=max(held_entities[str(event['entity'])],event['watched_ms'] or 0)

    pressure_values=[t['pressure'] for t in ticks]
    contacts=[t['contacts'] for t in ticks]
    health=[t['health'] for t in ticks if t['health'] is not None]
    max_squad_peak=max([s['peak_pressure'] for s in squads],default=0)
    peak_pressure=max(max(pressure_values,default=0),max_squad_peak)

    tuning_flags=[]
    if peak_pressure>=95:
        tuning_flags.append('Pressure reached 95+; inspect whether the fight became unreadable or merely climactic.')
    if squads and all((s['duration_s'] or 0)<8 for s in squads):
        tuning_flags.append('Every cleared squad resolved in under eight seconds; encounters may be too brittle/easy.')
    for squad in squads:
        if squad['duration_s']>90:
            tuning_flags.append(f"Squad {squad['group']} took {squad['duration_s']}s to clear; inspect navigation, hiding or excessive durability.")
        if squad['armour_loss']>=60:
            tuning_flags.append(f"Squad {squad['group']} removed {squad['armour_loss']} armour; review fairness/cover before adding pressure.")
    if reasons.get('visibility_timeout',0)>2:
        tuning_flags.append('Several regular enemies hit the visibility timeout; staging points may be too exposed to the approach sightline.')
    if held_entities and max(held_entities.values())>=3000:
        tuning_flags.append('At least one staging point was watched for ~3s; inspect that reveal in captured/native play.')

    return {
        'director_samples':len(ticks),
        'peak_pressure':peak_pressure,
        'pressure_band_samples':dict(bands),
        'max_contacts_sampled':max(contacts,default=0),
        'minimum_health_sampled':min(health,default=None),
        'activation_count':len(activations),
        'activations_by_group':dict(groups),
        'activations_by_role':dict(roles),
        'activations_by_reason':dict(reasons),
        'held_reveal_entities':dict(held_entities),
        'max_reveal_hold_ms':max(held_entities.values(),default=0),
        'squads_cleared':squads,
        'extraction_arrivals':extraction_arrivals,
        'combat_entries':len(evidence['combat_enter']),
        'combat_clears':len(evidence['combat_clear']),
        'tuning_flags':tuning_flags,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')

    launch_path = DESIGN / 'last-launch.json'
    preflight_path = DESIGN / 'preflight.json'
    launch = json.loads(launch_path.read_text()) if launch_path.is_file() else {}
    preflight = json.loads(preflight_path.read_text()) if preflight_path.is_file() else {}
    offsets=launch.get('log_offsets',{})

    logs = {}
    merged = []
    for path in LOGS:
        if not path.is_file():
            continue
        text,start,total,rotated=read_since(path,offsets.get(str(path),0))
        logs[str(path)] = {
            'bytes_total': total,
            'run_offset': start,
            'run_bytes': max(0,total-start),
            'rotated_since_launch':rotated,
            'tail': tail_lines(text),
        }
        merged.extend(text.splitlines())

    evidence = {}
    for name, pattern in PATTERNS.items():
        hits = [line for line in merged if pattern.search(line)]
        evidence[name] = hits[-180:]

    tuning=build_tuning(evidence)
    blockers = []
    notes = []
    if evidence['lua_errors']:
        blockers.append('Lua/runtime error recorded in this run')
    if evidence['qa_failures']:
        blockers.append('Native QA/geometry warning recorded in this run')
    if launch.get('qa') and not evidence['qa_complete']:
        notes.append('QA run ended before mission completion; this is not itself a failure in observational QA mode')
    if not evidence['music_init']:
        blockers.append('No score initialization evidence found in this run')
    if not offsets:
        notes.append('Launch manifest predates per-run log offsets; evidence may include historical appended log content')
    if not evidence['squad_start'] and evidence['enemy_activation']:
        notes.append('Enemy activation exists without squad metrics; runtime scripts may not match the launch Git head')

    report = {
        'captured_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'launch': launch,
        'preflight': preflight,
        'logs': logs,
        'tuning':tuning,
        'evidence': evidence,
        'blockers': blockers,
        'notes': notes,
        'human_review_required': [
            'opening vista and terrain composition',
            'music audible at useful mix level and radio duck feels natural',
            'no visible T-pose, animation pop or center-view spawn reveal',
            'rifle uses cover / assault closes / anchor holds / flanker takes a lateral route',
            'new cover pockets help Recast navigation rather than snagging it',
            'combat backlights improve silhouettes without flattening Vesper night grade',
            'no floating/intersecting geometry or z-fighting',
            'Northstar / Operations / AEGIS visual differentiation',
            'return-route combat and two-sided extraction readability',
            'landing-zone center remains clear for boarding',
        ],
    }

    path = OUT / f'first-light-native-{stamp}.json'
    path.write_text(json.dumps(report, indent=2,default=str))

    print('FIRST LIGHT // NATIVE RUN COLLECTED')
    print('Report:', path)
    print('Logs found:', len(logs),'(current-run slices)')
    print('Lua errors:', len(evidence['lua_errors']))
    print('Music evidence:', len(evidence['music_init']) + len(evidence['music_states']))
    print('Enemy activations:', tuning['activation_count'])
    print('Squads cleared:', len(tuning['squads_cleared'])),'/ 7')
    print('Peak pressure:', tuning['peak_pressure'])
    print('Max contacts sampled:', tuning['max_contacts_sampled'])
    print('Visibility-held entities:',len(tuning['held_reveal_entities']),'max hold',tuning['max_reveal_hold_ms'],'ms')
    if tuning['extraction_arrivals']:
        print('Extraction arrivals:',' / '.join(f"#{e['index']} {e['seconds_after_evac_start']}s" for e in tuning['extraction_arrivals']))
    for squad in tuning['squads_cleared']:
        print(f"SQUAD {squad['group']}: {squad['duration_s']}s / armour -{squad['armour_loss']} / peak {squad['peak_pressure']}")
    if tuning['tuning_flags']:
        print('TUNING FLAGS:')
        for item in tuning['tuning_flags']:print(' ~',item)
    if evidence['lua_errors']:
        print('LATEST UNIQUE LUA/RUNTIME ERRORS:')
        for line in unique_tail(evidence['lua_errors']):print(' !',line)
    if evidence['qa_failures']:
        print('QA / GEOMETRY WARNINGS:')
        for line in unique_tail(evidence['qa_failures']):print(' !',line)
    if blockers:
        print('BLOCKERS:')
        for item in blockers:print(' -',item)
    else:
        print('No log-level blocker detected. Visual/combat review still required.')
    for item in notes:print('NOTE:',item)


if __name__ == '__main__':
    main()
