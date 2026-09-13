"""Story-effect stage transitions and exact native marker/footing contracts."""
import sys, json, zipfile
from pathlib import Path
from native_format import ROOT, INSTALL, read_ele
from max_archive import PASSWORD
from firstlight_story_effects import EFFECTS, MARKER, SCRIPT, damaged_junction, scorched_case
from firstlight_world import ground
from environment_pass import Mesh
from python_runtime import ensure_lua51_runtime

LuaRuntime=ensure_lua51_runtime(__file__)
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
g_Time=1000;g_PlayerHealth=200;fl={started=true,stage=1,won=false};calls={};dist=500
function CollisionOff(e) end
function EffectStop(e) calls['active'..e]=false end
function EffectStart(e) calls['active'..e]=true end
function EffectSetOpacity(...) end
function EffectSetSpeed(...) end
function EffectSetColor(...) end
function EffectSetLifespan(...) end
function EffectSetBurstMode(...) end
function EffectSetLocalRotation(...) end
function EffectFireBurst(e) calls['bursts'..e]=(calls['bursts'..e] or 0)+1 end
function GetPlayerDistance(e) return dist end
function LoopSound(e,slot) calls['audio'..e]=true end
function StopSound(e,slot) calls['audio'..e]=false end
function SetSoundVolume(v) calls.volume=v end
''')
lua.execute((ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_effects.lua').read_text())
g=lua.globals()
def tick():
 g.g_Time+=120
 for e in range(1,7):g.firstlight_effects_main(e)
for e,site in enumerate(EFFECTS,1):g.firstlight_effects_init_name(e,'FL FX '+site[0])
tick()
assert g.calls.active1 and g.calls.active2 and not g.calls.active4 and not g.calls.active6
g.fl.stage=2;tick()
assert not g.calls.active1 and g.calls.active4, 'power repair must quiet the fault and start the vent'
g.fl.stage=3;tick();assert g.calls.active6
g.fl.stage=4;tick();assert not g.calls.active6, 'cancelled firing bus must stop sparking'
g.dist=2500;tick();assert not any(g.calls['active'+str(e)] for e in range(1,7))
g.dist=2200;tick();assert not g.calls.active2, 'distance hysteresis lost'
g.dist=1800;tick();assert g.calls.active2
g.fl.won=True;tick();assert not any(g.calls['active'+str(e)] for e in range(1,7))
g.fl.won=False;g.g_PlayerHealth=0;tick();assert not g.calls.active2
g.g_PlayerHealth=200;g.fl.stage=1;g.dist=500;tick()
before=g.calls.bursts1 or 0
for _ in range(20):tick()
assert (g.calls.bursts1 or 0)-before<=1, 'sparks burst every frame'
for e in range(1,7):g.firstlight_effects_exit(e)
assert not any(g.calls['active'+str(e)] for e in range(1,7))

# Wreck smoke is readable from the road; close fire audio never becomes global.
for e,site in enumerate(EFFECTS[6:],7):g.firstlight_effects_init_name(e,'FL FX '+site[0])
def wreck_tick(distance):
 g.dist=distance;g.g_Time+=120
 for e in (7,8):g.firstlight_effects_main(e)
wreck_tick(500);assert g.calls.active7 and g.calls.active8 and g.calls.audio7
assert g.calls.volume<=48
wreck_tick(2800);assert g.calls.active7 and g.calls.active8 and not g.calls.audio7
wreck_tick(4000);assert not g.calls.active7 and g.calls.active8
g.fl.won=True;wreck_tick(500);assert not g.calls.active8 and not g.calls.audio7
for e in (7,8):g.firstlight_effects_exit(e)

design=ROOT/'Aegis Reach/Design/First Light'
layout=json.loads((design/'layout.json').read_text())
with zipfile.ZipFile(ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm') as z:
 _,entities=read_ele(z.read('map.ele',pwd=PASSWORD))
by_name={e['101:eleprof.name_s']:e for e in entities}
assert len([p for p in layout if p['kind']=='story_effect'])==len(EFFECTS)
for role,preset,x,z,y,scale,story in EFFECTS:
 e=by_name['FL FX '+role]
 assert (e['101:x'],e['101:y'],e['101:z'])==(x,y,z)
 assert e['101:staticflag']==0 and e['101:eleprof.aimain_s']==SCRIPT
 assert e['320:eleprof.newparticle.bParticle_Show_At_Start']==0
 assert e['320:eleprof.newparticle.bParticle_Full_Screen']==0
 assert e['321:eleprof.newparticle.emittername']=='particlesbank/'+preset
 assert (INSTALL/'particlesbank'/(preset+'.arx')).is_file()
for name,fn in [('Camp 12 / severed civilian bus',damaged_junction),
                ('Gate 07 / damaged evacuation cargo',scorched_case),
                ('Operations / purged physical records',scorched_case)]:
 e=by_name[name]
 for x,y,z in fn(Mesh).verts:
  if abs(y)<.001:
   assert abs(ground(e['101:x']+x,e['101:z']+z)-e['101:y'])<.5, ('floating debris footing',name)
print('STORY EFFECTS PASS: native markers, stage consequences, culling, burst cadence and debris grounding.')
print('Native MAX smoke/spark scale, opacity and source alignment still require visual review.')
