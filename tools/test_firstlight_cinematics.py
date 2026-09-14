"""Static/runtime contract tests for the FIRST LIGHT CineGuru story layer."""
import math
from firstlight_cinematics import (
    apply,SHOT_PROFILES,OPENING_SEQUENCE,OPENING_SOURCES,SHIP_MOUNT_BEATS,
    WORLD_CAMERA_BEATS,OPENING_TOTAL_MS,CAMERA_SCRIPT,CONTROLLER_SCRIPT,CAMERA_RIG_SCRIPT,
)
from firstlight_dialogue import LINES
from native_format import ROOT

class FakeBuild:
 def __init__(self):self.placements=[]
 def ground(self,x,z):return 500+0.02*x+0.01*z
 def add(self,path,name,x,z,y=None,ry=0,scale=100,script=None,kind='environment',**params):self.placements.append(dict(path=path,name=name,x=x,y=y,z=z,ry=ry,script=script,kind=kind,params=params))

def check(name,ok,checks):assert ok,name;checks.append(name)

def main():
 checks=[];fake=FakeBuild();summary=apply(fake)
 cams=[p for p in fake.placements if p['kind']=='cinematic_camera']
 controllers=[p for p in fake.placements if p['name']=='FIRST LIGHT // CINEMATIC']
 rigs=[p for p in fake.placements if p['name']=='FIRST LIGHT // CAMERA RIG']
 by={p['name']:p for p in cams}

 check('Twenty authored CineGuru story cameras are emitted',len(cams)==20 and summary['camera_count']==20,checks)
 check('Opening is a seventeen-cut documentary sequence',summary['opening']['shots']==list(OPENING_SEQUENCE) and len(OPENING_SEQUENCE)==17,checks)
 expected=list(OPENING_SEQUENCE)+['MIRA_SIGNAL','AEGIS_REVEAL','EXTRACTION']
 check('Cinematic beat names remain stable and unique',summary['beats']==expected and len({p['name'] for p in cams})==20,checks)
 check('Opening runtime remains about fifty-one seconds',OPENING_TOTAL_MS==50800 and abs(summary['opening']['seconds']-50.8)<.01,checks)
 check('No opening shot exceeds 4.2 seconds',max(SHOT_PROFILES[x]['seconds'] for x in OPENING_SEQUENCE)<=4.2,checks)
 first_line=next(x for x in LINES if x['id']=='FL01_KES_001')
 check('Recorded VO is allowed to continue across cuts',SHOT_PROFILES['ARRIVAL_PERIM']['seconds']<first_line['seconds'],checks)
 check('Opening mixes eleven Kestrel feeds with six infrastructure cameras',len(SHIP_MOUNT_BEATS)==11 and len(WORLD_CAMERA_BEATS)==6,checks)
 check('Every opening source has a physical carrier',all(OPENING_SOURCES[b]['carrier'] in ('kestrel','world') and OPENING_SOURCES[b]['mount'] for b in OPENING_SEQUENCE),checks)
 check('Ventral ISR is explicitly gimbal stabilized',OPENING_SOURCES['ARRIVAL_ISR']['mode']=='gimbal stabilized',checks)
 check('Every story camera uses CineGuru',all(p['script']==CAMERA_SCRIPT for p in cams),checks)
 check('Camera transforms are finite and elevated',all(math.isfinite(p['y']) and math.isfinite(p['ry']) and p['y']>fake.ground(p['x'],p['z']) for p in cams),checks)
 check('All cameras are always-active',all(p['params'].get('eleprof.phyalways')==1 for p in cams),checks)
 check('One always-active fail-open coordinator is emitted',len(controllers)==1 and controllers[0]['script']==CONTROLLER_SCRIPT and controllers[0]['params'].get('eleprof.phyalways')==1,checks)
 check('One always-active diegetic camera rig is emitted',len(rigs)==1 and rigs[0]['script']==CAMERA_RIG_SCRIPT and rigs[0]['params'].get('eleprof.phyalways')==1,checks)
 check('Build report rejects omniscient opening-camera language',summary['opening']['camera_language']=='diegetic military telemetry / security footage; no omniscient opening cameras',checks)
 check('Fixed perimeter and touchdown sources have real editor positions','FL CG ARRIVAL PERIM' in by and 'FL CG ARRIVAL TOUCHDOWN' in by,checks)
 check('Ship motion is explicitly independent of camera cuts','continuous opening elapsed time independent' in summary['opening']['ship_motion_clock'],checks)
 check('Extraction camera remains reserved for boarding/liftoff','boarding/liftoff' in summary['extraction'],checks)

 scripts=ROOT/'Aegis Reach/Files/scriptbank'
 cine=(scripts/'aegis_reach/firstlight_cinematic.lua').read_text(errors='replace')
 rig=(scripts/'aegis_reach/firstlight_camera_rig.lua').read_text(errors='replace')
 kestrel=(scripts/'aegis_reach/firstlight_kestrel.lua').read_text(errors='replace')
 score=(scripts/'aegis_reach/firstlight_score.lua').read_text(errors='replace')
 interact=(scripts/'aegis_reach/firstlight_interact.lua').read_text(errors='replace')
 cg=(scripts/'Cine Guru MAX/cg_cinematic_camera.lua').read_text(errors='replace')

 check('Coordinator uses CineGuru registration activation completion APIs','CG_IsCamera' in cine and 'CG_ActivateCamera' in cine and 'CG_GetActiveCamera' in cine,checks)
 check('Coordinator configures film time and focal progression','CG_GetCamera' in cine and 'cam.filmtime' in cine and 'cam.data.fls' in cine and 'cam.data.fle' in cine,checks)
 check('Coordinator retries startup registration','RETRY_MS' in cine and 'STARTUP_GRACE_MS' in cine and 'resolve_registered_camera' in cine,checks)
 check('Rolling camera confirmation gates seen state','active_camera()' in cine and 'cine.seen[beat]=true' in cine,checks)
 check('Opening chains through all rapid cuts','next_opening_beat' in cine and 'ARRIVAL_PERIM' in cine and 'ARRIVAL_DEPART' in cine,checks)
 check('Opening owns a persistent motion clock','opening_started_at' in cine and 'opening_elapsed_ms' in cine,checks)
 check('Opening keeps score ducked between chained edits','aegis.music_cinematic_duck=nextbeat~=nil' in cine and 'if not is_opening(beat) then aegis.music_cinematic_duck=false end' in cine,checks)
 check('Skipping any opening shot releases control instead of forcing remaining cuts','skipped and is_opening(beat)' in cine and 'mark_opening_seen()' in cine,checks)
 check('Opening dialogue uses stable IDs',"FL01_KES_001" in cine and "FL01_KES_004" in cine and "FL01_KES_005" in cine,checks)
 check('Camera rig follows the live Kestrel object','GetObjectPosAng' in rig and "FL KESTREL INSERTION FLIGHT" in rig and 'rotate_local' in rig,checks)
 check('Camera rig renders source telemetry','MERIDIAN INSERTION // REC' in rig and 'camera_feed_label' in rig,checks)
 check('Kestrel opening uses global elapsed time rather than per-shot elapsed','opening_ms()' in kestrel and 'ms<8400' in kestrel and 'ms<50800' in kestrel and 'beat_elapsed' not in kestrel,checks)
 check('Mira and AEGIS beats retain dialogue IDs',"FL01_MIR_001" in cine and "FL01_MIR_002" in cine and "FL01_KES_010" in cine,checks)
 check('Extraction liftoff retains dialogue IDs',"FL01_KES_016" in cine and "FL01_KES_017" in cine,checks)
 check('Cinematics fail open','cineguru_unavailable' in cine and 'start_timeout' in cine and 'opening_fallback' in cine,checks)
 check('AEGIS reveal waits for clear combat',"not fl.in_contact" in cine and "fl.stage==3" in cine,checks)
 check('Suno score supports cinematic ducking','music_cinematic_duck' in score and 'StopGlobalSound' in score,checks)
 check('Interactions request Mira and extraction beats',"fl_request_cinematic('MIRA_SIGNAL')" in interact and "fl_request_cinematic('EXTRACTION')" in interact,checks)
 check('Installed CineGuru restores player presentation','function CG_IsCamera' in cg and 'function CG_ActivateCamera' in cg and 'SetCameraOverride( 0 )' in cg and 'ShowHuds()' in cg,checks)
 print('FIRST LIGHT // CINEMATIC CONTRACT PASS')
 for item in checks:print('PASS',item)

if __name__=='__main__':main()
