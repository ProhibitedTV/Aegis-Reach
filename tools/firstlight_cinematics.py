"""CineGuru story cameras for FIRST LIGHT.

The opening now uses a multi-shot Kestrel approach, orbit, descent, touchdown and
climb-out sequence.  Each shot owns one mechanical ship state so the unavoidable
mesh-state swaps happen under camera cuts while position/attitude motion remains
continuous inside the shot.
"""
import math,json,re
from firstlight_dialogue import LINES

CAMERA_SCRIPT=r'Cine Guru MAX\cg_cinematic_camera.lua'
CONTROLLER_SCRIPT=r'aegis_reach\firstlight_cinematic.lua'
MARKER=r'Aegis Reach\Supply Crate.fpe'

OPENING_SEQUENCE=(
    'ARRIVAL_WIDE','ARRIVAL_PASS','ARRIVAL_ORBIT','ARRIVAL_DESCENT',
    'ARRIVAL_HANDOFF','ARRIVAL_LIFTOFF','ARRIVAL_CLIMB','ARRIVAL_DEPART',
)

SHOT_PROFILES={
    'ARRIVAL_WIDE':dict(seconds=9.0,fade=.24,focal_start=54,focal_end=72),
    'ARRIVAL_PASS':dict(seconds=10.2,fade=.12,focal_start=58,focal_end=82),
    'ARRIVAL_ORBIT':dict(seconds=9.7,fade=.14,focal_start=62,focal_end=86),
    'ARRIVAL_DESCENT':dict(seconds=12.7,fade=.14,focal_start=66,focal_end=88),
    'ARRIVAL_HANDOFF':dict(seconds=4.7,fade=.18,focal_start=70,focal_end=84),
    'ARRIVAL_LIFTOFF':dict(seconds=2.6,fade=.12,focal_start=62,focal_end=78),
    'ARRIVAL_CLIMB':dict(seconds=2.4,fade=.12,focal_start=60,focal_end=76),
    'ARRIVAL_DEPART':dict(seconds=3.0,fade=.16,focal_start=56,focal_end=72),
    'MIRA_SIGNAL':dict(seconds=5.2,fade=.35,focal_start=70,focal_end=84),
    'AEGIS_REVEAL':dict(seconds=6.3,fade=.35,focal_start=58,focal_end=90),
    'EXTRACTION':dict(seconds=6.0,fade=.35,focal_start=62,focal_end=82),
}
SHOT_LINES={
 'ARRIVAL_WIDE':('FL01_KES_001',),
 'ARRIVAL_PASS':('FL01_KES_002',),
 'ARRIVAL_ORBIT':('FL01_KES_003',),
 'ARRIVAL_DESCENT':('FL01_KES_004',),
 'ARRIVAL_HANDOFF':('FL01_KES_005',),
 'ARRIVAL_LIFTOFF':(),
 'ARRIVAL_CLIMB':(),
 'ARRIVAL_DEPART':(),
 'MIRA_SIGNAL':('FL01_MIR_001','FL01_KES_009'),
 'AEGIS_REVEAL':('FL01_MIR_002','FL01_KES_010'),
 'EXTRACTION':('FL01_KES_016','FL01_KES_017'),
}
LINE_BY_ID={line['id']:line for line in LINES}
TIMELINES={}
for beat,ids in SHOT_LINES.items():
 elapsed=.35;TIMELINES[beat]=[]
 for line_id in ids:
  TIMELINES[beat].append((round(elapsed*1000),line_id))
  elapsed+=LINE_BY_ID[line_id]['seconds']+.35
 if ids:
  SHOT_PROFILES[beat]['seconds']=round(elapsed+.3,2)

def sync_coordinator(script):
 source=script.read_text()
 camera_rows=[]
 for beat,name,*_ in SHOTS:
  camera_rows.append(beat+'='+json.dumps(name))
 source,n=re.subn(r'local cameras=\{[^\n]+',lambda _:'local cameras={'+','.join(camera_rows)+'}',source,count=1)
 assert n==1
 opening='local opening_order={'+','.join(json.dumps(x) for x in OPENING_SEQUENCE)+'}'
 source,n=re.subn(r'local opening_order=\{[^\n]+',lambda _:opening,source,count=1)
 assert n==1
 profiles=[]
 for beat,p in SHOT_PROFILES.items():
  profiles.append(beat+'={seconds='+str(p['seconds'])+',fade='+str(p.get('fade',.35))+',fls='+str(p['focal_start'])+',fle='+str(p['focal_end'])+'}')
 source,n=re.subn(r'local profiles=\{[^\n]+',lambda _:'local profiles={'+','.join(profiles)+'}',source,count=1)
 assert n==1
 rows=['local function update_story_timeline(beat,elapsed)']
 for index,(beat,events) in enumerate(TIMELINES.items()):
  rows.append((' if' if index==0 else ' elseif')+' beat=='+json.dumps(beat)+' then')
  for ms,line_id in events:
   line=LINE_BY_ID[line_id]
   rows.append('  if elapsed>='+str(ms)+' then mark_line('+json.dumps(line_id)+','+json.dumps(line_id)+','+json.dumps(line['speaker']+': '+line['text'])+',"",'+str(line['seconds'])+') end')
 rows+=[' end',' if fl_dialogue_draw_cinematic then fl_dialogue_draw_cinematic() end','end','local function finish_opening_handoff']
 source,n=re.subn(r'local function update_story_timeline\(beat,elapsed\).*?local function finish_opening_handoff',lambda _:'\n'.join(rows),source,count=1,flags=re.S)
 assert n==1
 script.write_text(source)

SHOTS=(
    # beat, name, camera x/z, height, target x/z, target height
    # Distant valley reveal: Kestrel is a moving silhouette before we ever cut close.
    ('ARRIVAL_WIDE','FL CG ARRIVAL WIDE',2450,-11100,720,-1050,-10050,520),
    # Side tracking composition for the fast low approach across the abandoned shelf.
    ('ARRIVAL_PASS','FL CG ARRIVAL PASS',-900,-10450,430,-120,-9300,310),
    # Three-quarter view across the facility while the ship curves around the outpost.
    ('ARRIVAL_ORBIT','FL CG ARRIVAL ORBIT',1500,-8650,520,-260,-8820,330),
    # Low telephoto descent angle; the cut masks conversion -> full powered-lift state.
    ('ARRIVAL_DESCENT','FL CG ARRIVAL DESCENT',-1150,-8550,300,-120,-9140,170),
    # Ground-level touchdown/ramp hero shot.  The landed-state swap happens on this cut.
    ('ARRIVAL_HANDOFF','FL CG ARRIVAL HANDOFF',720,-9300,145,-120,-9140,88),
    # Separate departure edits hide landed -> flare -> convert -> cruise state changes.
    ('ARRIVAL_LIFTOFF','FL CG ARRIVAL LIFTOFF',-420,-9500,180,-120,-9140,430),
    ('ARRIVAL_CLIMB','FL CG ARRIVAL CLIMB',1160,-8460,390,150,-9320,720),
    ('ARRIVAL_DEPART','FL CG ARRIVAL DEPART',-1720,-7600,650,860,-10020,1040),
    ('MIRA_SIGNAL','FL CG MIRA SIGNAL',820,650,205,1420,1050,85),
    ('AEGIS_REVEAL','FL CG AEGIS REVEAL',-1060,2070,335,0,3200,175),
    # Boarding shot owns the extraction Kestrel lift-off, not the combat approach.
    ('EXTRACTION','FL CG EXTRACTION',-1050,-3070,340,0,-2350,125),
)


def _pose(build,x,z,height,tx,tz,target_height):
    y=build.ground(x,z)+height
    ty=build.ground(tx,tz)+target_height
    dx,dz=tx-x,tz-z
    horizontal=max(0.001,math.hypot(dx,dz))
    yaw=math.degrees(math.atan2(dx,dz))%360
    pitch=-math.degrees(math.atan2(ty-y,horizontal))
    return y,pitch,yaw


def apply(build):
    if hasattr(build,'FILES'):sync_coordinator(build.FILES/'scriptbank/aegis_reach/firstlight_cinematic.lua')
    cameras=[]
    for beat,name,x,z,height,tx,tz,target_height in SHOTS:
        y,pitch,yaw=_pose(build,x,z,height,tx,tz,target_height)
        profile=SHOT_PROFILES[beat]
        build.add(
            MARKER,name,x,z,y=y,ry=yaw,kind='cinematic_camera',script=CAMERA_SCRIPT,
            **{'rx':pitch,'rz':0,'eleprof.physics':0,'eleprof.phyalways':1}
        )
        cameras.append({
            'beat':beat,'name':name,'x':x,'y':round(y,2),'z':z,
            'pitch':round(pitch,2),'yaw':round(yaw,2),
            'seconds':profile['seconds'],'fade':profile.get('fade',.35),
            'focal_start':profile['focal_start'],'focal_end':profile['focal_end'],
            'always_active':True,
        })
    build.add(
        MARKER,'FIRST LIGHT // CINEMATIC',180,-9500,y=100,kind='controller',
        script=CONTROLLER_SCRIPT,**{'eleprof.physics':0,'eleprof.phyalways':1}
    )
    return {
        'system':'CineGuru MAX','camera_count':len(cameras),'beats':[c['beat'] for c in cameras],
        'cameras':cameras,
        'opening':{
            'shots':list(OPENING_SEQUENCE),
            'purpose':'introduce the Kestrel as a vehicle: distant approach, close pass, outpost orbit, conversion/descent, touchdown, then a staged climb-out before control returns',
            'first_action':'Restore Northstar and recover the evacuation packet',
            'seconds':sum(SHOT_PROFILES[x]['seconds'] for x in OPENING_SEQUENCE),
            'state_editing':'major Kestrel mesh-state swaps occur only under CineGuru cuts; movement inside every shot remains continuous',
        },
        'extraction':'Kestrel approaches visibly during gameplay; EXTRACTION camera is reserved for boarding/liftoff',
        'always_active':True,'registration_retry':True,'fail_open':True,
        'music_owner':'firstlight_score.lua',
    }
