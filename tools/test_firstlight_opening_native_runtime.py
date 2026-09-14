"""Runtime regression for the hard-replacement FIRST LIGHT opening camera."""
from pathlib import Path
import sys

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

# The first rendered frame must already be the hull-mounted nose EO feed.
g.g_Time=100;g.fl_opening_native_tick()
assert g.camera.override==3,g.camera.override
assert g.camera.freeze==1,g.camera.freeze
assert g.aegis.cinematic_beat=='ARRIVAL_NOSE',g.aegis.cinematic_beat
nose=(float(g.camera.x),float(g.camera.y),float(g.camera.z))
assert abs(nose[0]-1000)>1 or abs(nose[2]-(-10000))>1,nose
assert g.spoken['FL01_KES_001'] is True

# 3.0 s: port shoulder camera, a distinct live-airframe transform.
g.g_Time=3100;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_PORT_FWD',g.aegis.cinematic_beat
port=(float(g.camera.x),float(g.camera.y),float(g.camera.z))
assert port!=nose,(nose,port)

# 6.0 s: stabilized ventral ISR looking at Meridian rather than along the hull.
g.g_Time=6100;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_ISR',g.aegis.cinematic_beat
isr=(float(g.camera.x),float(g.camera.y),float(g.camera.z))
assert isr!=port,(port,isr)

# 8.7 s: first external context shot is fixed Gate CCTV; second VO is live.
g.g_Time=8800;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_GATE',g.aegis.cinematic_beat
gate=(float(g.camera.x),float(g.camera.y),float(g.camera.z))
assert abs(gate[0]-(-520))<.01,gate
assert g.spoken['FL01_KES_002'] is True

# 11.8 s: back onto a Kestrel-mounted starboard shoulder feed.
g.g_Time=11900;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_STBD',g.aegis.cinematic_beat
stbd=(float(g.camera.x),float(g.camera.y),float(g.camera.z))
assert stbd!=gate,(gate,stbd)

# End restores player control and permanently gates any legacy insertion opener.
g.g_Time=51000;g.fl_opening_native_tick()
assert g.camera.override==0,g.camera.override
assert g.camera.unfreeze==1,g.camera.unfreeze
assert g.aegis.insertion_complete is True
assert g.aegis.cinematic_request=='OPENING_NATIVE_DONE',g.aegis.cinematic_request
print('FIRST LIGHT // ONBOARD-FIRST OPENING RUNTIME PASS')
print('NOSE -> PORT SHOULDER -> ISR -> GATE CCTV -> STBD changes camera 0 on one 50.8s clock; player control restores at handoff.')
