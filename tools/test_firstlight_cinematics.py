"""Static/runtime contract tests for the FIRST LIGHT CineGuru story layer."""
import math

from firstlight_cinematics import apply,SHOTS,SHOT_PROFILES,CAMERA_SCRIPT,CONTROLLER_SCRIPT
from native_format import ROOT


class FakeBuild:
    def __init__(self):self.placements=[]
    def ground(self,x,z):return 500+0.02*x+0.01*z
    def add(self,path,name,x,z,y=None,ry=0,scale=100,script=None,kind='environment',**params):
        self.placements.append(dict(path=path,name=name,x=x,y=y,z=z,ry=ry,script=script,kind=kind,params=params))


def check(name,ok,checks):
    assert ok,name
    checks.append(name)


def main():
    checks=[]
    fake=FakeBuild();summary=apply(fake)
    cameras=[p for p in fake.placements if p['kind']=='cinematic_camera']
    controllers=[p for p in fake.placements if p['name']=='FIRST LIGHT // CINEMATIC']
    byname={p['name']:p for p in cameras}
    check('Four sparse authored CineGuru story cameras are emitted',len(cameras)==4 and summary['camera_count']==4,checks)
    check('Cinematic beat names remain stable and unique',summary['beats']==['ARRIVAL','MIRA_SIGNAL','AEGIS_REVEAL','EXTRACTION'] and len({p['name'] for p in cameras})==4,checks)
    check('Every story camera uses the installed CineGuru cinematic-camera script',all(p['script']==CAMERA_SCRIPT for p in cameras),checks)
    check('Camera transforms are finite and elevated above native terrain',all(math.isfinite(p['y']) and math.isfinite(p['ry']) and p['y']>fake.ground(p['x'],p['z']) for p in cameras),checks)
    check('All CineGuru cameras are always-active for native registration',all(p['params'].get('eleprof.phyalways')==1 for p in cameras) and summary['always_active'],checks)
    check('One always-active fail-open mission-side cinematic coordinator is emitted',len(controllers)==1 and controllers[0]['script']==CONTROLLER_SCRIPT and controllers[0]['params'].get('eleprof.phyalways')==1 and summary['fail_open'],checks)
    check('Build manifest records startup registration retry semantics',summary['registration_retry'] is True,checks)
    check('Arrival is a deliberate briefing-length beat',SHOT_PROFILES['ARRIVAL']['seconds']>=9 and summary['opening']['seconds']==SHOT_PROFILES['ARRIVAL']['seconds'],checks)
    check('Arrival camera is a high establishing view',byname['FL CG ARRIVAL']['y']-fake.ground(byname['FL CG ARRIVAL']['x'],byname['FL CG ARRIVAL']['z'])>=400,checks)
    check('Opening manifest states human stakes and first action','42 missing colonists' in summary['opening']['purpose'] and summary['opening']['first_action'].startswith('Restore Northstar'),checks)

    scripts=ROOT/'Aegis Reach/Files/scriptbank'
    cine=(scripts/'aegis_reach/firstlight_cinematic.lua').read_text(errors='replace')
    score=(scripts/'aegis_reach/firstlight_score.lua').read_text(errors='replace')
    interact=(scripts/'aegis_reach/firstlight_interact.lua').read_text(errors='replace')
    cg=(scripts/'Cine Guru MAX/cg_cinematic_camera.lua').read_text(errors='replace')

    check('Coordinator uses CineGuru registration, activation and completion APIs','CG_IsCamera' in cine and 'CG_ActivateCamera' in cine and 'CG_GetActiveCamera' in cine,checks)
    check('Coordinator configures CineGuru film time and focal progression','CG_GetCamera' in cine and 'configure_camera' in cine and 'cam.filmtime' in cine and 'cam.data.fls' in cine and 'cam.data.fle' in cine,checks)
    check('Coordinator retries native camera registration instead of consuming first failure','RETRY_MS' in cine and 'STARTUP_GRACE_MS' in cine and 'resolve_registered_camera' in cine and 'activate_pending' in cine,checks)
    confirm=cine[cine.index('local function confirm_pending'):cine.index('local function begin_pending')]
    check('A story beat is marked seen only after a rolling camera is confirmed','active_camera()' in confirm and 'cine.seen[beat]=true' in confirm,checks)
    check('Opening has a script-load-order fallback request',"fl_request_cinematic('ARRIVAL')" in cine and "g_Time-(fl.born or g_Time)>350" in cine,checks)
    check('Opening briefing establishes the missing colonists','Forty-two colonists' in cine and 'No beacon. No traffic.' in cine,checks)
    check('Opening briefing introduces Mira without explaining the mystery','MIRA SEN // LAST BURST' in cine and 'array waking' in cine and 'SIGNAL LOST' in cine,checks)
    check('Opening briefing gives the Warden clue and actionable mission','Warden transponder crossed Gate 07' in cine and 'Restore Northstar. Recover the evacuation packet. Find our people.' in cine,checks)
    check('Arrival failure degrades to an in-game story briefing','play_arrival_fallback' in cine and "Mira's last burst died with Northstar" in cine,checks)
    check('Arrival handoff returns to the first playable objective','Touchdown confirmed. Northstar is ahead.' in cine and 'Then we find the forty-two.' in cine,checks)
    check('Cinematics explicitly fail open instead of owning mission progression','cineguru_unavailable' in cine and 'start_timeout' in cine and "cine.failed[beat]=true" in cine,checks)
    check('AEGIS reveal waits for a clear combat pocket',"not fl.in_contact" in cine and "fl.stage==3" in cine,checks)
    check('Suno score remains authoritative and supports cinematic ducking','music_cinematic_duck' in score and 'StopGlobalSound' in score,checks)
    check('Story interactions request Mira and extraction camera beats',"fl_request_cinematic('MIRA_SIGNAL')" in interact and "fl_request_cinematic('EXTRACTION')" in interact,checks)
    check('Installed CineGuru exposes registration, named activation, camera configuration and player restoration','function CG_IsCamera' in cg and 'function CG_ActivateCamera' in cg and 'function CG_GetCamera' in cg and 'SetCameraOverride( 0 )' in cg and 'ShowHuds()' in cg,checks)

    print('FIRST LIGHT // CINEMATIC CONTRACT PASS')
    for item in checks:print('PASS',item)


if __name__=='__main__':main()
