"""Regression contract for the Kestrel landed boarding collision proxy."""
import json
from native_format import ROOT
from environment_pass import Mesh
from firstlight_kestrel import LANDED_CONTACT_Y
from firstlight_kestrel_boarding import boarding_collision_mesh,NAME,SCRIPT,LZ
from python_runtime import ensure_max_lua_runtime

m=boarding_collision_mesh(Mesh)
assert m.faces and len(m.verts)==len(m.norm)==len(m.uv)
for face in m.faces:
    a,b,c=[m.verts[i] for i in face]
    u=[b[i]-a[i] for i in range(3)]
    v=[c[i]-a[i] for i in range(3)]
    n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    assert sum(q*q for q in n)>1e-8,face

xs=[p[0] for p in m.verts];ys=[p[1] for p in m.verts];zs=[p[2] for p in m.verts]
assert min(xs)<=-72 and max(xs)>=72,'boarding proxy no longer covers full ramp width'
assert min(zs)<=280 and max(zs)>=526,'boarding proxy lost vestibule or ramp reach'
assert min(ys)<=LANDED_CONTACT_Y and max(ys)>=42,'boarding proxy lost ground-to-floor slope'

script_path=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_kestrel_boarding.lua'
source=script_path.read_text(errors='replace')
for token in ('aegis.kestrel_landed==true','not aegis.kestrel_depart','CollisionOn','CollisionOff','Hide(e)'):
    assert token in source,token

LuaRuntime=ensure_max_lua_runtime(__file__)
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('FIRSTLIGHT_TEST=true')
lua.execute((ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_audit.lua').read_text(errors='replace'))
lua.execute(r'''
collision={};g_Entity={[1]={obj=1,x=0,y=496,z=-2350}}
function Hide(e) end
function CollisionOn(e) collision[e]=true end
function CollisionOff(e) collision[e]=false end
function GravityOff(e) end
function SetEntityAlwaysActive(e,v) end
fl={started=true}
aegis={kestrel_landed=false,kestrel_depart=false}
''')
lua.execute('\n'.join(line for line in source.splitlines() if not line.startswith("require ")))
lua.execute(r'''
firstlight_kestrel_boarding_init(1)
assert(collision[1]==false)
firstlight_kestrel_boarding_main(1)
assert(collision[1]==false)
aegis.kestrel_landed=true
firstlight_kestrel_boarding_main(1)
assert(collision[1]==true)
aegis.kestrel_depart=true
firstlight_kestrel_boarding_main(1)
assert(collision[1]==false)
''')

layout=json.loads((ROOT/'Aegis Reach/Design/First Light/layout.json').read_text())
proxies=[p for p in layout if p.get('name')=='FL KESTREL BOARDING COLLISION']
assert len(proxies)==1,'expected one Kestrel boarding collision proxy'
proxy=proxies[0]
assert proxy.get('kind')=='vehicle_collision'
assert proxy.get('landing_only') is True
assert proxy.get('collision_mode')=='polygon'
assert (proxy.get('x'),proxy.get('z'))==LZ

fpe=ROOT/'Aegis Reach/Files/entitybank/Aegis Reach/First Light'/f'{NAME}.fpe'
assert fpe.is_file(),'boarding proxy FPE missing; rebuild required'
assert 'collisionmode = 1' in fpe.read_text(errors='replace')

print('FIRST LIGHT // KESTREL BOARDING COLLISION PASS')
print('Landed-only polygon ramp + vestibule collision enables after touchdown and clears before liftoff.')
