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
ids={site[0]:i for i,site in enumerate(EFFECTS,1)}
for role,i in ids.items():g.firstlight_effects_init_name(i,'FL FX '+role)

def tick(indices=None):
 g.g_Time+=120
 for e in (indices or range(1,len(EFFECTS)+1)):g.firstlight_effects_main(e)

def active(role):return bool(g.calls['active'+str(ids[role])])

tick(range(1,7))
assert active('CAMP_FAULT') and active('GATE_SMOKE') and not active('POWER_VENT') and not active('ARRAY_FAULT')
g.fl.stage=2;tick()
assert not active('CAMP_FAULT') and active('POWER_VENT'), 'power repair must quiet the fault and start the vent'
g.fl.stage=3;tick();assert active('ARRAY_FAULT')
g.fl.stage=4;tick();assert not active('ARRAY_FAULT'), 'cancelled firing bus must stop sparking'

# Ordinary effects retain tight culling/hysteresis.
g.dist=2500;tick(range(1,7));assert not any(g.calls['active'+str(e)] for e in range(1,7))
g.dist=2200;tick(range(1,7));assert not active('GATE_SMOKE'), 'distance hysteresis lost'
g.dist=1800;tick(range(1,7));assert active('GATE_SMOKE')
g.fl.won=True;tick(range(1,7));assert not any(g.calls['active'+str(e)] for e in range(1,7))
g.fl.won=False;g.g_PlayerHealth=0;tick(range(1,7));assert not active('GATE_SMOKE')
g.g_PlayerHealth=200;g.fl.stage=1;g.dist=500;tick(range(1,7))
before=g.calls.bursts1 or 0
for _ in range(20):tick(range(1,7))
assert (g.calls.bursts1 or 0)-before<=1, 'sparks burst every frame'
for e in range(1,7):g.firstlight_effects_exit(e)

# Wreck FX are now a layered landmark: two flames, distant smoke and intermittent arcing.
wreck=[ids[r] for r in ('WRECK_FIRE','WRECK_FIRE_AUX','WRECK_SMOKE','WRECK_SPARKS')]
def wreck_tick(distance):
 g.dist=distance;g.g_Time+=120
 for e in wreck:g.firstlight_effects_main(e)

g.fl.won=False;g.g_PlayerHealth=200;g.fl.stage=1
wreck_tick(500)
assert all(active(r) for r in ('WRECK_FIRE','WRECK_FIRE_AUX','WRECK_SMOKE','WRECK_SPARKS'))
assert g.calls['audio'+str(ids['WRECK_FIRE'])]
assert g.calls.volume<=58

wreck_tick(3000)
assert active('WRECK_FIRE') and active('WRECK_FIRE_AUX') and active('WRECK_SMOKE') and active('WRECK_SPARKS')
assert not g.calls['audio'+str(ids['WRECK_FIRE'])]

wreck_tick(5600)
assert not active('WRECK_FIRE') and not active('WRECK_FIRE_AUX') and active('WRECK_SMOKE') and not active('WRECK_SPARKS')
wreck_tick(7000);assert not any(active(r) for r in ('WRECK_FIRE','WRECK_FIRE_AUX','WRECK_SMOKE','WRECK_SPARKS'))
g.fl.won=True;wreck_tick(500)
assert not any(active(r) for r in ('WRECK_FIRE','WRECK_FIRE_AUX','WRECK_SMOKE','WRECK_SPARKS'))
assert not g.calls['audio'+str(ids['WRECK_FIRE'])]
for e in wreck:g.firstlight_effects_exit(e)

# Native review regression: the wreck must remain visually strong enough to read at distance.
fx={role:(preset,scale) for role,preset,x,z,y,scale,story in EFFECTS}
assert fx['WRECK_FIRE'][1]>=60
assert fx['WRECK_FIRE_AUX'][1]>=40
assert fx['WRECK_SMOKE'][1]>=80
assert fx['WRECK_SPARKS'][0]=='embers2' and fx['WRECK_SPARKS'][1]>=24

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
print('STORY EFFECTS PASS: native markers, stage consequences, culling, layered wreck FX and debris grounding.')
print('Native MAX smoke/fire scale and source alignment still require visual review.')
