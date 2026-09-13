"""Geometry, collision and native set-piece contracts; not visual acceptance."""
import json,math,zipfile
from native_format import ROOT,read_ele
from max_archive import PASSWORD
from environment_pass import Mesh
from firstlight_transport import (
    hull,recorder,detached_engine,torn_panel,collision_box,
    SITE,CRASH_YAW,world_offset,COLLISION_SCRIPT
)
from firstlight_story_effects import EFFECTS
from firstlight_world import ground,road_sample,ROUTE

x,z,y=SITE
for fn in (hull,recorder,detached_engine,torn_panel):
 mesh=fn(Mesh)
 assert len(mesh.verts)==len(mesh.norm)==len(mesh.uv)
 assert mesh.faces
 for face in mesh.faces:
  a,b,c=[mesh.verts[i] for i in face]
  u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
  n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
  assert sum(k*k for k in n)>1e-8,'degenerate transport triangle'
  assert sum(n[i]*mesh.norm[face[0]][i] for i in range(3))>0,'normal opposes winding'

m=hull(Mesh)
assert abs(min(v[1] for v in m.verts))<1e-6,'crash-attitude hull is not grounded'
assert max(v[1] for v in m.verts)-min(v[1] for v in m.verts)>170,'wreck silhouette collapsed vertically'
# Baked pitch/roll should create a strong fore/aft height difference rather than a parked stance.
nose=[v[1] for v in m.verts if v[2]<-250]
aft=[v[1] for v in m.verts if v[2]>170]
assert nose and aft and (sum(aft)/len(aft)-sum(nose)/len(nose))>45,'M-17 no longer reads nose-down'

# Rotated visual footprint remains clear of the authored combat road.
a=math.radians(CRASH_YAW);co,si=math.cos(a),math.sin(a)
for xx,yy,zz in m.verts:
 wx=x+xx*co+zz*si;wz=z-xx*si+zz*co
 assert road_sample(wx,wz,ROUTE)[0]>360,'transport enters combat road'
 assert y+yy-ground(wx,wz)>-1.0,'transport sinks below native crash shelf'

with zipfile.ZipFile(ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm') as archive:
 _,entities=read_ele(archive.read('map.ele',pwd=PASSWORD))
byname={e['101:eleprof.name_s']:e for e in entities}

assert 'FL FLIGHTLOG' in byname
assert byname['M-17 / recoverable security ammunition']['101:eleprof.quantity']==60
assert byname['FL FX WRECK_FIRE']['101:eleprof.soundset_s']==r'misc\Campfire_loop.wav'
assert 'M-17 / detached starboard engine' in byname
assert 'M-17 / torn hull panel 1' in byname and 'M-17 / torn hull panel 2' in byname
assert 'M-17 / ejected cargo' in byname

# Native-review regression: the render shell does not own collision. Four tighter box
# colliders live inside it and are hidden every native frame by a dedicated script, so
# proxy atlas geometry can never protrude through the authored wreck again.
colliders=[name for name in byname if name.startswith('M-17 / collision ')]
assert len(colliders)==4,colliders
for name in colliders:
 e=byname[name]
 # physics/phyalways are authoring/build properties and are not serialized as stable
 # direct map.ele keys by every MAX format revision. The runtime contract that *does*
 # survive the archive is the dedicated hide-only proxy script; source/FPE checks below
 # certify that those proxies remain collision-enabled and always-authored as physics.
 assert e['101:eleprof.aimain_s']==COLLISION_SCRIPT,(name,e['101:eleprof.aimain_s'])
bank=ROOT/'Aegis Reach/Files/entitybank/Aegis Reach/First Light'
for name in ('Meridian M17 Collision Forward','Meridian M17 Collision Cargo',
             'Meridian M17 Collision Port Engine','Meridian M17 Collision Starboard Root'):
 text=(bank/(name+'.fpe')).read_text(errors='replace').lower()
 assert 'collisionmode = 0' in text,name

transport=(ROOT/'tools/firstlight_transport.py').read_text(errors='replace')
assert ("'eleprof.physics':1" in transport and "'eleprof.phyalways':1" in transport), \
       'collision proxies are no longer authored as persistent physics entities'
proxy=(ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_collision_proxy.lua').read_text(errors='replace')
assert 'Hide(e)' in proxy,'collision proxy no longer hides render geometry'
# Comments document CollisionOff as forbidden; reject an executable call, not the word.
assert 'CollisionOff(' not in proxy,'collision proxy must never disable physics'

# Main render shell and cosmetic debris intentionally do not contribute concave collision.
shell=(bank/'Meridian M17 Transport Wreck.fpe').read_text(errors='replace').lower()
assert 'collisionmode = 11' in shell

fx={role:(preset,scale) for role,preset,xx,zz,yy,scale,story in EFFECTS}
assert fx['WRECK_FIRE'][1]>=60 and fx['WRECK_FIRE_AUX'][1]>=40
assert fx['WRECK_SMOKE'][1]>=80 and 'WRECK_SPARKS' in fx

for name in ('M-17 / ruptured cargo','M-17 / ejected cargo','FL FLIGHTLOG'):
 e=byname[name];assert abs(e['101:y']-ground(e['101:x'],e['101:z']))<.5

print('M-17 PASS: canted wreck geometry, hidden box-collision cores, detached engine, debris trail, layered fire/smoke, flight record and supplies.')
print('Native MAX collision feel, particle scale and final wreck readability still require player review.')
