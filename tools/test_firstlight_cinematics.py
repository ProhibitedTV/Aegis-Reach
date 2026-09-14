"""Static/runtime contract tests for the FIRST LIGHT CineGuru story layer."""
import math
from firstlight_cinematics import apply,SHOTS,SHOT_PROFILES,OPENING_SEQUENCE,OPENING_MOUNTS,CAMERA_SCRIPT,CONTROLLER_SCRIPT,CAMERA_RIG_SCRIPT
from native_format import ROOT
class FakeBuild:
 def __init__(self):self.placements=[]
 def ground(self,x,z):return 500+0.02*x+0.01*z
 def add(self,path,name,x,z,y=None,ry=0,scale=100,script=None,kind='environment',**params):self.placements.append(dict(path=path,name=name,x=x,y=y,z=z,ry=ry,script=script,kind=kind,params=params))
def check(name,ok,checks):assert ok,name;checks.append(name)
def main():
 checks=[];fake=FakeBuild();summary=apply(fake);cams=[p for p in fake.placements if p['kind']=='cinematic_camera'];controllers=[p for p in fake.placements if p['name']=='FIRST LIGHT // CINEMATIC'];rigs=[p for p in fake.placements if p['name']=='FIRST LIGHT // CAMERA RIG'];by={p['name']:p for p in cams}
 check('Eleven authored CineGuru story cameras are emitted',len(cams)==11 and summary['camera_count']==11,checks)
 check('Opening is an eight-shot Kestrel approach and departure sequence',summary['opening']['shots']==list(OPENING_SEQUENCE) and len(OPENING_SEQUENCE)==8,checks)
 expected=list(OPENING_SEQUENCE)+['MIRA_SIGNAL','AEGIS_REVEAL','EXTRACTION']
 check('Cinematic beat names remain stable and unique',summary['beats']==expected and len({p['name'] for p in cams})==11,checks)
 check('Opening edits use fast fades rather than eight slow dissolves',max(SHOT_PROFILES[x]['fade'] for x in OPENING_SEQUENCE)<=.24,checks)
 check('Every story camera uses CineGuru',all(p['script']==CAMERA_SCRIPT for p in cams),checks)
 check('Camera transforms are finite and elevated',all(math.isfinite(p['y']) and math.isfinite(p['ry']) and p['y']>fake.ground(p['x'],p['z']) for p in cams),checks)
 check('All cameras are always-active',all(p['params'].get('eleprof.phyalways')==1 for p in cams),checks)
 check('One always-active fail-open coordinator is emitted',len(controllers)==1 and controllers[0]['script']==CONTROLLER_SCRIPT and controllers[0]['params'].get('eleprof.phyalways')==1,checks)
 check('One always-active diegetic camera rig is emitted',len(rigs)==1 and rigs[0]['script']==CAMERA_RIG_SCRIPT and rigs[0]['params'].get('eleprof.phyalways')==1,checks)
 check('All eight opening feeds have plausible physical mount identities',tuple(OPENING_MOUNTS)==OPENING_SEQUENCE and all(OPENING_MOUNTS[b]['mount'] for b in OPENING_SEQUENCE),checks)
 check('Ventral orbit feed is explicitly gimbal stabilized',OPENING_MOUNTS['ARRIVAL_ORBIT']['mode']=='gimbal stabilized',checks)
 check('Build report rejects omniscient opening-camera language',summary['opening']['camera_language']=='diegetic documentary / military telemetry; no omniscient opening cameras',checks)
 check('Opening wide retains a safe editor fallback transform',by['FL CG ARRIVAL WIDE']['z']<-10000 and by['FL CG ARRIVAL WIDE']['y']-fake.ground(by['FL CG ARRIVAL WIDE']['x'],by['FL CG ARRIVAL WIDE']['z'])>=700,checks)
 check('Touchdown and departure receive dedicated edits','FL CG ARRIVAL HANDOFF' in by and 'FL CG ARRIVAL LIFTOFF' in by and 'FL CG ARRIVAL DEPART' in by,checks)
 check('Opening state swaps are explicitly hidden by camera cuts','state_editing' in summary['opening'] and 'under CineGuru cuts' in summary['opening']['state_editing'],checks)
 check('Extraction camera is reserved for boarding/liftoff','boarding/liftoff' in summary['extraction'],checks)
 scripts=ROOT/'Aegis Reach/Files/scriptbank';cine=(scripts/'aegis_reach/firstlight_cinematic.lua').read_text(errors='replace');rig=(scripts/'aegis_reach/firstlight_camera_rig.lua').read_text(errors='replace');score=(scripts/'aegis_reach/firstlight_score.lua').read_text(errors='replace');interact=(scripts/'aegis_reach/firstlight_interact.lua').read_text(errors='replace');cg=(scripts/'Cine Guru MAX/cg_cinematic_camera.lua').read_text(errors='replace')
 check('Coordinator uses CineGuru registration activation completion APIs','CG_IsCamera' in cine and 'CG_ActivateCamera' in cine and 'CG_GetActiveCamera' in cine,checks)
 check('Coordinator configures film time and focal progression','CG_GetCamera' in cine and 'cam.filmtime' in cine and 'cam.data.fls' in cine and 'cam.data.fle' in cine,checks)
 check('Coordinator retries startup registration','RETRY_MS' in cine and 'STARTUP_GRACE_MS' in cine and 'resolve_registered_camera' in cine,checks)
 check('Rolling camera confirmation gates seen state','active_camera()' in cine and 'cine.seen[beat]=true' in cine,checks)
 check('Opening chains through the complete approach sequence','next_opening_beat' in cine and 'ARRIVAL_WIDE' in cine and 'ARRIVAL_DEPART' in cine,checks)
 check('Opening keeps score ducked between chained edits','aegis.music_cinematic_duck=nextbeat~=nil' in cine and 'if not is_opening(beat) then aegis.music_cinematic_duck=false end' in cine,checks)
 check('Skipping any opening shot releases control instead of forcing the remaining cuts','skipped and is_opening(beat)' in cine and 'mark_opening_seen()' in cine,checks)
 check('Opening dialogue uses stable IDs',"FL01_KES_001" in cine and "FL01_KES_004" in cine and "FL01_KES_005" in cine,checks)
 check('Mira and AEGIS beats have dialogue IDs',"FL01_MIR_001" in cine and "FL01_MIR_002" in cine and "FL01_KES_010" in cine,checks)
 check('Extraction liftoff has dialogue IDs',"FL01_KES_016" in cine and "FL01_KES_017" in cine,checks)
 check('Cinematics fail open','cineguru_unavailable' in cine and 'start_timeout' in cine and 'opening_fallback' in cine,checks)
 check('AEGIS reveal waits for clear combat',"not fl.in_contact" in cine and "fl.stage==3" in cine,checks)
 check('Camera rig follows a real Kestrel object transform','GetObjectPosAng' in rig and "FL KESTREL INSERTION FLIGHT" in rig and 'rotate_local' in rig,checks)
 check('Camera rig includes hull ISR gear ramp and tail sources',all(token in rig for token in ('NOSE EO','STBD SHOULDER','VENTRAL ISR','STBD GEAR','RAMP','PORT SHOULDER','TAIL')),checks)
 check('Suno score supports cinematic ducking','music_cinematic_duck' in score and 'StopGlobalSound' in score,checks)
 check('Interactions request Mira and extraction beats',"fl_request_cinematic('MIRA_SIGNAL')" in interact and "fl_request_cinematic('EXTRACTION')" in interact,checks)
 check('Installed CineGuru restores player presentation','function CG_IsCamera' in cg and 'function CG_ActivateCamera' in cg and 'SetCameraOverride( 0 )' in cg and 'ShowHuds()' in cg,checks)
 print('FIRST LIGHT // CINEMATIC CONTRACT PASS')
 for item in checks:print('PASS',item)
if __name__=='__main__':main()
