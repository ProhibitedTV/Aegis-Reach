"""CineGuru story cameras for FIRST LIGHT.

The insertion is edited like operational footage from a real campaign: short cuts
between physically plausible camera sources while Kestrel VO continues across the
edits. Ship motion is a separate continuous timeline; camera duration never stretches
to match a long radio line.
"""
import math,json,re
from firstlight_dialogue import LINES

CAMERA_SCRIPT=r'Cine Guru MAX\cg_cinematic_camera.lua'
CONTROLLER_SCRIPT=r'aegis_reach\firstlight_cinematic.lua'
CAMERA_RIG_SCRIPT=r'aegis_reach\firstlight_camera_rig.lua'
MARKER=r'Aegis Reach\Supply Crate.fpe'

OPENING_SEQUENCE=(
    'ARRIVAL_PERIM','ARRIVAL_NOSE','ARRIVAL_GATE',
    'ARRIVAL_STBD','ARRIVAL_ISR','ARRIVAL_MAST',
    'ARRIVAL_CONVERT','ARRIVAL_BELLY','ARRIVAL_GEAR',
    'ARRIVAL_LZ','ARRIVAL_FLARE','ARRIVAL_TOUCHDOWN',
    'ARRIVAL_RAMP','ARRIVAL_DEPLOY','ARRIVAL_LIFTOFF',
    'ARRIVAL_CLIMB','ARRIVAL_DEPART',
)

# These durations are editorial cuts, not dialogue containers. Recorded lines are
# intentionally allowed to continue through subsequent cuts.
_OPENING_SECONDS=(2.8,3.0,2.6,3.0,3.1,3.0,3.0,3.0,3.0,3.0,3.0,3.0,3.0,4.2,2.6,2.5,3.0)
OPENING_CUTS_MS=[]
_running=0
for _seconds in _OPENING_SECONDS:
    _running+=int(round(_seconds*1000));OPENING_CUTS_MS.append(_running)
OPENING_TOTAL_MS=OPENING_CUTS_MS[-1]

# Every source has a physical carrier. `world` sources are fixed infrastructure
# cameras; `kestrel` sources are updated every frame by firstlight_camera_rig.lua.
OPENING_SOURCES={
    'ARRIVAL_PERIM':dict(label='M12-PERIM-04',carrier='world',mount='Camp 12 perimeter security camera',mode='fixed infrastructure'),
    'ARRIVAL_NOSE':dict(label='KSTL-01 NOSE EO',carrier='kestrel',mount='forward hull electro-optical camera',mode='fixed hull'),
    'ARRIVAL_GATE':dict(label='M12-GATE-02',carrier='world',mount='south approach security camera',mode='fixed infrastructure'),
    'ARRIVAL_STBD':dict(label='KSTL-02 STBD SHOULDER',carrier='kestrel',mount='starboard shoulder maintenance camera',mode='fixed hull'),
    'ARRIVAL_ISR':dict(label='KSTL-03 VENTRAL ISR',carrier='kestrel',mount='ventral reconnaissance sensor',mode='gimbal stabilized'),
    'ARRIVAL_MAST':dict(label='M12-MAST-01',carrier='world',mount='survey mast optical camera',mode='fixed infrastructure'),
    'ARRIVAL_CONVERT':dict(label='KSTL-03A VENTRAL AFT',carrier='kestrel',mount='aft belly systems camera',mode='fixed hull'),
    'ARRIVAL_BELLY':dict(label='KSTL-04 BELLY SERVICE',carrier='kestrel',mount='port belly service camera',mode='fixed hull'),
    'ARRIVAL_GEAR':dict(label='KSTL-04 STBD GEAR',carrier='kestrel',mount='starboard landing-gear camera',mode='fixed hull'),
    'ARRIVAL_LZ':dict(label='LZ07-PERIM-01',carrier='world',mount='landing-zone perimeter camera',mode='fixed infrastructure'),
    'ARRIVAL_FLARE':dict(label='LZ07-BEACON-02',carrier='world',mount='landing beacon camera',mode='fixed infrastructure'),
    'ARRIVAL_TOUCHDOWN':dict(label='LZ07-PAD-03',carrier='world',mount='pad touchdown camera',mode='fixed infrastructure'),
    'ARRIVAL_RAMP':dict(label='KSTL-05 RAMP',carrier='kestrel',mount='rear cargo-door deployment camera',mode='fixed hull'),
    'ARRIVAL_DEPLOY':dict(label='KSTL-05 RAMP',carrier='kestrel',mount='rear cargo-door deployment camera',mode='fixed hull'),
    'ARRIVAL_LIFTOFF':dict(label='KSTL-05 RAMP',carrier='kestrel',mount='rear cargo-door deployment camera',mode='fixed hull'),
    'ARRIVAL_CLIMB':dict(label='KSTL-06 PORT SHOULDER',carrier='kestrel',mount='port shoulder maintenance camera',mode='fixed hull'),
    'ARRIVAL_DEPART':dict(label='KSTL-07 TAIL',carrier='kestrel',mount='aft tail observation camera',mode='fixed hull'),
}
SHIP_MOUNT_BEATS=tuple(beat for beat in OPENING_SEQUENCE if OPENING_SOURCES[beat]['carrier']=='kestrel')
WORLD_CAMERA_BEATS=tuple(beat for beat in OPENING_SEQUENCE if OPENING_SOURCES[beat]['carrier']=='world')

SHOT_PROFILES={
    beat:dict(seconds=seconds,fade=.06,focal_start=64,focal_end=64)
    for beat,seconds in zip(OPENING_SEQUENCE,_OPENING_SECONDS)
}
# Distinct optics make the source changes read immediately rather than like one
# invisible director teleporting around the same scene.
SHOT_PROFILES.update({
    'ARRIVAL_PERIM':dict(seconds=2.8,fade=.10,focal_start=88,focal_end=82),
    'ARRIVAL_NOSE':dict(seconds=3.0,fade=.04,focal_start=58,focal_end=62),
    'ARRIVAL_GATE':dict(seconds=2.6,fade=.04,focal_start=92,focal_end=84),
    'ARRIVAL_STBD':dict(seconds=3.0,fade=.04,focal_start=52,focal_end=56),
    'ARRIVAL_ISR':dict(seconds=3.1,fade=.04,focal_start=96,focal_end=88),
    'ARRIVAL_MAST':dict(seconds=3.0,fade=.04,focal_start=78,focal_end=86),
    'ARRIVAL_CONVERT':dict(seconds=3.0,fade=.04,focal_start=48,focal_end=54),
    'ARRIVAL_BELLY':dict(seconds=3.0,fade=.04,focal_start=46,focal_end=52),
    'ARRIVAL_GEAR':dict(seconds=3.0,fade=.04,focal_start=50,focal_end=54),
    'ARRIVAL_LZ':dict(seconds=3.0,fade=.04,focal_start=88,focal_end=80),
    'ARRIVAL_FLARE':dict(seconds=3.0,fade=.04,focal_start=72,focal_end=68),
    'ARRIVAL_TOUCHDOWN':dict(seconds=3.0,fade=.04,focal_start=62,focal_end=58),
    'ARRIVAL_RAMP':dict(seconds=3.0,fade=.04,focal_start=54,focal_end=58),
    'ARRIVAL_DEPLOY':dict(seconds=4.2,fade=.04,focal_start=58,focal_end=62),
    'ARRIVAL_LIFTOFF':dict(seconds=2.6,fade=.04,focal_start=54,focal_end=58),
    'ARRIVAL_CLIMB':dict(seconds=2.5,fade=.04,focal_start=50,focal_end=56),
    'ARRIVAL_DEPART':dict(seconds=3.0,fade=.08,focal_start=62,focal_end=72),
    'MIRA_SIGNAL':dict(seconds=9.95,fade=.35,focal_start=70,focal_end=84),
    'AEGIS_REVEAL':dict(seconds=10.75,fade=.35,focal_start=58,focal_end=90),
    'EXTRACTION':dict(seconds=7.75,fade=.35,focal_start=62,focal_end=82),
})

# Start each opening line once, at a cut boundary chosen so the previous line has
# just finished. The voice/subtitle deliberately continues while cameras keep cutting.
SHOT_LINES={beat:() for beat in OPENING_SEQUENCE}
SHOT_LINES.update({
    'ARRIVAL_PERIM':('FL01_KES_001',),
    'ARRIVAL_STBD':('FL01_KES_002',),
    'ARRIVAL_CONVERT':('FL01_KES_003',),
    'ARRIVAL_LZ':('FL01_KES_004',),
    'ARRIVAL_DEPLOY':('FL01_KES_005',),
    'MIRA_SIGNAL':('FL01_MIR_001','FL01_KES_009'),
    'AEGIS_REVEAL':('FL01_MIR_002','FL01_KES_010'),
    'EXTRACTION':('FL01_KES_016','FL01_KES_017'),
})
LINE_START_MS={
    'ARRIVAL_PERIM':200,
    'ARRIVAL_STBD':150,
    'ARRIVAL_CONVERT':300,
    'ARRIVAL_LZ':100,
    'ARRIVAL_DEPLOY':200,
}
LINE_BY_ID={line['id']:line for line in LINES}
TIMELINES={}
for beat,ids in SHOT_LINES.items():
    elapsed=LINE_START_MS.get(beat,350);TIMELINES[beat]=[]
    for line_id in ids:
        TIMELINES[beat].append((round(elapsed),line_id))
        elapsed+=LINE_BY_ID[line_id]['seconds']*1000+350


def sync_coordinator(script):
    source=script.read_text()
    camera_rows=[]
    for beat,name,*_ in SHOTS:camera_rows.append(beat+'='+json.dumps(name))
    source,n=re.subn(r'local cameras=\{[^\n]+',lambda _:'local cameras={'+','.join(camera_rows)+'}',source,count=1);assert n==1
    opening='local opening_order={'+','.join(json.dumps(x) for x in OPENING_SEQUENCE)+'}'
    source,n=re.subn(r'local opening_order=\{[^\n]+',lambda _:opening,source,count=1);assert n==1
    profiles=[]
    for beat,p in SHOT_PROFILES.items():profiles.append(beat+'={seconds='+str(p['seconds'])+',fade='+str(p.get('fade',.35))+',fls='+str(p['focal_start'])+',fle='+str(p['focal_end'])+'}')
    source,n=re.subn(r'local profiles=\{[^\n]+',lambda _:'local profiles={'+','.join(profiles)+'}',source,count=1);assert n==1
    rows=['local function update_story_timeline(beat,elapsed)']
    for index,(beat,events) in enumerate(TIMELINES.items()):
        rows.append((' if' if index==0 else ' elseif')+' beat=='+json.dumps(beat)+' then')
        for ms,line_id in events:
            line=LINE_BY_ID[line_id]
            rows.append('  if elapsed>='+str(ms)+' then mark_line('+json.dumps(line_id)+','+json.dumps(line_id)+','+json.dumps(line['speaker']+': '+line['text'])+',"",'+str(line['seconds'])+') end')
    rows+=[' end',' if fl_dialogue_draw_cinematic then fl_dialogue_draw_cinematic() end','end','local function finish_opening_handoff']
    source,n=re.subn(r'local function update_story_timeline\(beat,elapsed\).*?local function finish_opening_handoff',lambda _:'\n'.join(rows),source,count=1,flags=re.S);assert n==1
    script.write_text(source)

# beat, entity name, camera x/z, height, target x/z, target height.
# Ship-mounted entries are only editor/fail-safe transforms. World cameras retain
# these transforms at runtime and are aimed at the expected ship position for the cut.
SHOTS=(
    ('ARRIVAL_PERIM','FL CG ARRIVAL PERIM',-1050,-10350,165,-2350,-11320,760),
    ('ARRIVAL_NOSE','FL CG ARRIVAL NOSE',-1800,-11000,700,-450,-10000,350),
    ('ARRIVAL_GATE','FL CG ARRIVAL GATE',-520,-10120,115,-1100,-10460,560),
    ('ARRIVAL_STBD','FL CG ARRIVAL STBD',-900,-10100,430,-200,-9600,300),
    ('ARRIVAL_ISR','FL CG ARRIVAL ISR',550,-9800,500,-240,-8750,160),
    ('ARRIVAL_MAST','FL CG ARRIVAL MAST',-2230,-7300,190,610,-9510,520),
    ('ARRIVAL_CONVERT','FL CG ARRIVAL CONVERT',820,-9400,430,0,-9100,260),
    ('ARRIVAL_BELLY','FL CG ARRIVAL BELLY',520,-9000,350,-80,-9100,180),
    ('ARRIVAL_GEAR','FL CG ARRIVAL GEAR',230,-8800,260,-120,-9140,110),
    ('ARRIVAL_LZ','FL CG ARRIVAL LZ',610,-9420,120,80,-9020,320),
    ('ARRIVAL_FLARE','FL CG ARRIVAL FLARE',-620,-8990,55,-120,-9140,190),
    ('ARRIVAL_TOUCHDOWN','FL CG ARRIVAL TOUCHDOWN',260,-9270,24,-120,-9140,82),
    ('ARRIVAL_RAMP','FL CG ARRIVAL RAMP',80,-9200,110,-120,-9140,70),
    ('ARRIVAL_DEPLOY','FL CG ARRIVAL DEPLOY',-30,-9210,90,-120,-9140,60),
    ('ARRIVAL_LIFTOFF','FL CG ARRIVAL LIFTOFF',-80,-9200,120,-120,-9140,330),
    ('ARRIVAL_CLIMB','FL CG ARRIVAL CLIMB',500,-9000,340,80,-9350,650),
    ('ARRIVAL_DEPART','FL CG ARRIVAL DEPART',-900,-8600,560,900,-10300,1050),
    ('MIRA_SIGNAL','FL CG MIRA SIGNAL',820,650,205,1420,1050,85),
    ('AEGIS_REVEAL','FL CG AEGIS REVEAL',-1060,2070,335,0,3200,175),
    ('EXTRACTION','FL CG EXTRACTION',-1050,-3070,340,0,-2350,125),
)


def _pose(build,x,z,height,tx,tz,target_height):
    y=build.ground(x,z)+height;ty=build.ground(tx,tz)+target_height
    dx,dz=tx-x,tz-z;horizontal=max(0.001,math.hypot(dx,dz))
    yaw=math.degrees(math.atan2(dx,dz))%360
    pitch=-math.degrees(math.atan2(ty-y,horizontal))
    return y,pitch,yaw


def apply(build):
    if hasattr(build,'FILES'):sync_coordinator(build.FILES/'scriptbank/aegis_reach/firstlight_cinematic.lua')
    cameras=[]
    for beat,name,x,z,height,tx,tz,target_height in SHOTS:
        y,pitch,yaw=_pose(build,x,z,height,tx,tz,target_height);profile=SHOT_PROFILES[beat]
        build.add(MARKER,name,x,z,y=y,ry=yaw,kind='cinematic_camera',script=CAMERA_SCRIPT,
                  **{'rx':pitch,'rz':0,'eleprof.physics':0,'eleprof.phyalways':1})
        cameras.append({'beat':beat,'name':name,'x':x,'y':round(y,2),'z':z,'pitch':round(pitch,2),'yaw':round(yaw,2),
                        'seconds':profile['seconds'],'fade':profile.get('fade',.35),'focal_start':profile['focal_start'],'focal_end':profile['focal_end'],
                        'always_active':True,'diegetic_source':OPENING_SOURCES.get(beat)})
    build.add(MARKER,'FIRST LIGHT // CINEMATIC',180,-9500,y=100,kind='controller',script=CONTROLLER_SCRIPT,
              **{'eleprof.physics':0,'eleprof.phyalways':1})
    build.add(MARKER,'FIRST LIGHT // CAMERA RIG',220,-9500,y=100,kind='controller',script=CAMERA_RIG_SCRIPT,
              **{'eleprof.physics':0,'eleprof.phyalways':1})
    return {
        'system':'CineGuru MAX','camera_count':len(cameras),'beats':[c['beat'] for c in cameras],'cameras':cameras,
        'opening':{
            'shots':list(OPENING_SEQUENCE),'seconds':OPENING_TOTAL_MS/1000,
            'purpose':'rapid documentary recut using Kestrel hull feeds plus fixed Meridian security/mast cameras; recorded VO continues across edits',
            'first_action':'Restore Northstar and recover the evacuation packet',
            'camera_language':'diegetic military telemetry / security footage; no omniscient opening cameras',
            'ship_motion_clock':'continuous opening elapsed time independent of individual CineGuru cuts',
            'state_editing':'flight/convert/flare/landed changes align with camera-source cuts while the world-space flight path remains continuous',
            'sources':{beat:OPENING_SOURCES[beat] for beat in OPENING_SEQUENCE},
        },
        'camera_rig':{'controller':'FIRST LIGHT // CAMERA RIG','script':CAMERA_RIG_SCRIPT,'tracked_ship':'FL KESTREL INSERTION FLIGHT',
                      'mount_count':len(SHIP_MOUNT_BEATS),'fixed_world_camera_count':len(WORLD_CAMERA_BEATS)},
        'extraction':'Kestrel approaches visibly during gameplay; EXTRACTION camera is reserved for boarding/liftoff',
        'always_active':True,'registration_retry':True,'fail_open':True,'music_owner':'firstlight_score.lua',
    }
