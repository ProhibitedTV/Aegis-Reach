"""Geometry/footing and native set-piece contracts; not visual acceptance."""
import json,math,zipfile
from native_format import ROOT,read_ele
from max_archive import PASSWORD
from environment_pass import Mesh
from firstlight_transport import hull,recorder,SITE
from firstlight_world import ground,road_sample,ROUTE

x,z,y=SITE
m=hull(Mesh)
for fn in (hull,recorder):
 mesh=fn(Mesh)
 assert len(mesh.verts)==len(mesh.norm)==len(mesh.uv)
 for face in mesh.faces:
  a,b,c=[mesh.verts[i] for i in face]
  u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
  n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
  assert sum(k*k for k in n)>1e-8,'degenerate transport triangle'
  assert sum(n[i]*mesh.norm[face[0]][i] for i in range(3))>0,'normal opposes winding'
for xx,yy,zz in m.verts:
 if yy==0:assert abs(ground(x+xx,z+zz)-y)<.5,'transport landing foot floats'
 assert road_sample(x+xx,z+zz,ROUTE)[0]>450,'transport enters combat road'
# No transformed mesh sinks below the native crash shelf.
assert min(y+yy-ground(x+xx,z+zz) for xx,yy,zz in m.verts)>-.5
with zipfile.ZipFile(ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm') as archive:
 _,entities=read_ele(archive.read('map.ele',pwd=PASSWORD))
byname={e['101:eleprof.name_s']:e for e in entities}
assert 'FL FLIGHTLOG' in byname
assert byname['M-17 / recoverable security ammunition']['101:eleprof.quantity']==60
assert byname['FL FX WRECK_FIRE']['101:eleprof.soundset_s']==r'misc\Campfire_loop.wav'
for name in ('M-17 / ruptured cargo','FL FLIGHTLOG'):
 e=byname[name];assert abs(e['101:y']-ground(e['101:x'],e['101:z']))<.5
print('M-17 PASS: nondegenerate geometry, outward normals, grounded feet, clear road, flight record and supplies.')
print('Native MAX silhouette, collision, fire and audio remain pending player review.')
