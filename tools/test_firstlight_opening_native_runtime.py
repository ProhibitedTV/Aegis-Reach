"""Runtime regression for the hard-replacement FIRST LIGHT opening camera."""
from pathlib import Path
import math,sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'tools/vendor'))
from python_runtime import ensure_max_lua_runtime

LuaRuntime=ensure_max_lua_runtime(__file__)
lua=LuaRuntime(unpack_returned_tuples=True)
source=(ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_opening_native.lua').read_text()
source='\n'.join(line for line in source.splitlines() if not line.startswith("require 'scriptbank\\\\aegis_reach\\\\firstlight_audit'"))

lua.execute(r'''
FIRSTLIGHT_TEST=true
g_Time=0
g_KeyPressSPACE=0
g_Entity={[37]={obj=101}}
fl={started=true,born=0,message_until=999999,zone_until=999999,radio_queue={}}
aegis={started=true,insertion_complete=false}
camera={x=0,y=0,z=0,rx=0,ry=0,rz=0,override=-1,freeze=0,unfreeze=0,fov=0}
spoken={}
function GetEntityName(e) if e==37 then return 'FL KESTREL INSERTION FLIGHT' end return '' end
function GetObjectPosAng(obj) assert(obj==101);return 1000,900,-10000,-2,155,4 end
function GetGroundHeight(x,z) return 500 end
function GetGamePlayerStateCameraFov() return 60 end
function GetPostMotionIntensity() return 0 end
function GetPlayerWeaponID() return 7 end
function GetGamePlayerStateFlashlightKeyEnabled() return 1 end
function FreezePlayer() camera.freeze=camera.freeze+1 end
function UnFreezePlayer() camera.unfreeze=camera.unfreeze+1 end
function SetCameraOverride(v) camera.override=v end
function SetCameraPosition(i,x,y,z) assert(i==0);camera.x=x;camera.y=y;camera.z=z end
function SetCameraAngle(i,rx,ry,rz) assert(i==0);camera.rx=rx;camera.ry=ry;camera.rz=rz end
function SetCameraPanelFOV(v) camera.fov=v end
function SetPostMotionIntensity(v) end
function SetFlashLightKeyEnabled(v) end
function SetPlayerWeapons(v) end
function ChangePlayerWeaponID(v) end
function HideHuds() end
function ShowHuds() end
function radar_hideallsprites() end
function radar_showallsprites() end
function Panel(...) end
function TextCenterOnXColor(...) end
function TextColor(...) end
function fl_log(m) end
function fl_say(...) end
function fl_dialogue(id) spoken[id]=true;return true end
function fl_dialogue_draw_cinematic() end
function fl_dialogue_cancel() end
''')
lua.execute(source)
g=lua.globals();g.fl_opening_native_reset()

def pose():
    return (float(g.camera.x),float(g.camera.y),float(g.camera.z))

def distance_from_ship(p):
    return math.dist(p,(1000.0,900.0,-10000.0))

# The first rendered frame must already be an external Kestrel-subject chase view.
g.g_Time=100;g.fl_opening_native_tick()
assert g.camera.override==3,g.camera.override
assert g.camera.freeze==1,g.camera.freeze
assert g.aegis.cinematic_beat=='ARRIVAL_NOSE',g.aegis.cinematic_beat
nose=pose()
assert distance_from_ship(nose)>900,nose
assert nose[1]>=620,nose
assert 50<=float(g.camera.fov)<=70,g.camera.fov

# VO 001 begins 200 ms after the opening clock starts, not on the acquisition frame.
g.g_Time=350;g.fl_opening_native_tick()
assert g.spoken['FL01_KES_001'] is True

# CineGuru-style camera movement happens inside the shot even with a stationary test ship.
g.g_Time=1500;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_NOSE'
nose_mid=pose()
assert math.dist(nose,nose_mid)>40,(nose,nose_mid)
assert distance_from_ship(nose_mid)>900,nose_mid
assert 50<=float(g.camera.fov)<=70,g.camera.fov
assert 0<float(g.aegis.opening_shot_progress)<1,g.aegis.opening_shot_progress

# 3.0 s: port formation camera, a distinct live-airframe transform.
g.g_Time=3100;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_PORT_FWD',g.aegis.cinematic_beat
port=pose()
assert port!=nose_mid,(nose_mid,port)
assert distance_from_ship(port)>900,port

# 6.0 s: high tracking view should still frame the ship from outside its envelope.
g.g_Time=6100;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_ISR',g.aegis.cinematic_beat
isr=pose()
assert isr!=port,(port,isr)
assert distance_from_ship(isr)>900,isr

# 8.7 s: Gate camera auto-tracks the ship while creeping on its short authored rail.
g.g_Time=8800;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_GATE',g.aegis.cinematic_beat
gate=pose()
assert -520<gate[0]<-430,gate
assert g.spoken['FL01_KES_002'] is True

# 11.8 s: back onto a starboard formation view.
g.g_Time=11900;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_STBD',g.aegis.cinematic_beat
stbd=pose()
assert stbd!=gate,(gate,stbd)
assert distance_from_ship(stbd)>900,stbd

# A late grounded/deploy shot must never bury the camera in terrain.
g.g_Time=39000;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_DEPLOY',g.aegis.cinematic_beat
deploy=pose()
assert deploy[1]>=570,deploy
assert distance_from_ship(deploy)>900,deploy
assert 40<=float(g.camera.fov)<=60,g.camera.fov

# End restores player control and permanently gates any legacy insertion opener.
g.g_Time=51000;g.fl_opening_native_tick()
assert g.camera.override==0,g.camera.override
assert g.camera.unfreeze==1,g.camera.unfreeze
assert g.aegis.insertion_complete is True
assert g.aegis.cinematic_request=='OPENING_NATIVE_DONE',g.aegis.cinematic_request
assert abs(float(g.camera.fov)-60)<.01,g.camera.fov
print('FIRST LIGHT // CINEGURU-LANGUAGE OPENING RUNTIME PASS')
print('CHASE MOVE -> PORT FORMATION -> HIGH TRACK -> GATE RAIL/AUTO-TRACK -> STBD uses smooth within-shot motion, real FOV degrees, terrain-safe deploy framing and clean player handoff.')
