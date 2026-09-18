"""Runtime regression for the FIRST LIGHT cinematic-v2 native opening."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'tools/vendor'))
from python_runtime import ensure_max_lua_runtime

scripts=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach'
source=(scripts/'firstlight_opening_native.lua').read_text()
dialogue=(scripts/'firstlight_dialogue.lua').read_text()
score=(scripts/'firstlight_score.lua').read_text()
enemy=(scripts/'firstlight_enemy.lua').read_text()
finish=(ROOT/'tools/firstlight_kestrel_finish.py').read_text()

# Presentation/audio contract: prevent the exact native-playtest regressions that led
# to cinematic-v2. FOV must be real degrees, music must use deterministic edit cues,
# opening VO must use deterministic global non-positional playback, stale HUD speech
# must not become a second cinematic channel, stock Warden AI must remain dormant until
# insertion handoff, and the night Kestrel must receive its dedicated material finish.
assert 'SetCameraPanelFOV(fov)' in source and 'SetCameraPanelFOV(fov/2)' not in source
for cue in ("{at=0,track='salt_moon_drift'", "{at=8400,track='moon_outpost_drift'",
            "{at=23500,track='orbital_catacomb'", "{at=42700,track='salt_moon_drift'"):
    assert cue in source,cue
assert 'cinematic_music_cue_serial' in source
for token in (
    'VOICE_GLOBAL_IDS={FL01_KES_001=301,FL01_KES_002=302,FL01_KES_003=303,FL01_KES_004=304}',
    'LoadGlobalSound("audiobank\\\\aegis_reach\\\\dialogue\\\\fl01_kestrel_001.wav",301)',
    'PlayGlobalSound(gid)',
    'for e=1,4096 do',
):
    assert token in dialogue,token
assert 'fl.message_until=math.max' not in dialogue,'cinematic VO regressed into the ordinary HUD message clock'
assert 'split_line(rest,62)' in dialogue and 'TextCenterOnXColor(50,top+(i-1)*4.6,3,row' in dialogue
for token in (
    'slot_for_name','cinematic_music_track','cinematic_music_cue_serial','restart_loop(id)',
    'local dialogue_speaking=aegis.dialogue_current',
    'local hud_speaking=(not aegis.cinematic_active)',
    'DisableMusicReset(1)',
):
    assert token in score,token
gate='if not aegis or aegis.insertion_complete~=true then return end'
assert gate in enemy,'stock Warden AI can initialize before insertion handoff'
assert enemy.index(gate)<enemy.index('if not w.primed then prime_native_character(e,w) end'),'AI gate must run before character_attack initialization'
for token in ('FIRST LIGHT // KESTREL CINEMATIC MATERIAL PASS','Brightness(img).enhance(1.55)',
              "metalnessStrength','0.58'","emissiveStrength','1.55'","reflectance','0.36'"):
    assert token in finish,token

LuaRuntime=ensure_max_lua_runtime(__file__)
lua=LuaRuntime(unpack_returned_tuples=True)
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

# First rendered frame is a real nose feed, using an actual FOV value rather than the
# old accidental half-FOV telephoto crop. It also publishes the first authored score cue.
g.g_Time=100;g.fl_opening_native_tick()
assert g.camera.override==3,g.camera.override
assert g.camera.freeze==1,g.camera.freeze
assert g.aegis.cinematic_beat=='ARRIVAL_NOSE',g.aegis.cinematic_beat
nose=(float(g.camera.x),float(g.camera.y),float(g.camera.z))
assert abs(nose[0]-1000)>1 or abs(nose[2]-(-10000))>1,nose
assert float(g.camera.fov)>50,g.camera.fov
assert g.aegis.cinematic_music_track=='salt_moon_drift',g.aegis.cinematic_music_track
assert int(g.aegis.cinematic_music_cue_serial)==1,g.aegis.cinematic_music_cue_serial
assert g.spoken['FL01_KES_001'] is None

# Dialogue events are timed from the moment the native opening actually begins.
g.g_Time=300;g.fl_opening_native_tick()
assert g.spoken['FL01_KES_001'] is True

# 3.0 s opening elapsed: exterior port three-quarter, distinctly separated from hull.
g.g_Time=3100;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_PORT_FWD',g.aegis.cinematic_beat
port=(float(g.camera.x),float(g.camera.y),float(g.camera.z))
assert port!=nose,(nose,port)
assert abs(port[0]-1000)>500 or abs(port[2]-(-10000))>500,port

# 6.0 s opening elapsed: high chase composition.
g.g_Time=6100;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_ISR',g.aegis.cinematic_beat
isr=(float(g.camera.x),float(g.camera.y),float(g.camera.z))
assert isr!=port,(port,isr)

# 8.7 s opening elapsed: fixed Gate security view and the second score master are live.
g.g_Time=8800;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_GATE',g.aegis.cinematic_beat
gate=(float(g.camera.x),float(g.camera.y),float(g.camera.z))
assert abs(gate[0]-(-520))<.01,gate
assert g.aegis.cinematic_music_track=='moon_outpost_drift',g.aegis.cinematic_music_track
assert g.spoken['FL01_KES_002'] is True

# 11.8 s opening elapsed: readable starboard exterior chase.
g.g_Time=11900;g.fl_opening_native_tick()
assert g.aegis.cinematic_beat=='ARRIVAL_STBD',g.aegis.cinematic_beat
stbd=(float(g.camera.x),float(g.camera.y),float(g.camera.z))
assert stbd!=gate,(gate,stbd)

# Powered-lift phase deliberately cues the darker master on the edit.
g.g_Time=23650;g.fl_opening_native_tick()
assert g.aegis.cinematic_music_track=='orbital_catacomb',g.aegis.cinematic_music_track
assert int(g.aegis.cinematic_music_cue_serial)==3,g.aegis.cinematic_music_cue_serial

# Departure returns to the Vesper exploration master before control handoff.
g.g_Time=43000;g.fl_opening_native_tick()
assert g.aegis.cinematic_music_track=='salt_moon_drift',g.aegis.cinematic_music_track
assert int(g.aegis.cinematic_music_cue_serial)==4,g.aegis.cinematic_music_cue_serial

# End restores player control, clears the authored music override and permanently gates
# any legacy insertion opener.
g.g_Time=51000;g.fl_opening_native_tick()
assert g.camera.override==0,g.camera.override
assert g.camera.unfreeze==1,g.camera.unfreeze
assert g.aegis.insertion_complete is True
assert g.aegis.cinematic_request=='OPENING_NATIVE_DONE',g.aegis.cinematic_request
assert g.aegis.cinematic_music_track is None
print('FIRST LIGHT // CINEMATIC V2 OPENING RUNTIME PASS')
print('Nose feed -> exterior chase -> security -> conversion -> touchdown -> departure uses true FOV, deterministic score cues, global opening VO, isolated HUD speech, gated Warden AI and finished Kestrel materials; control restores at handoff.')
