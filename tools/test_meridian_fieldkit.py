"""Physical opening and native paint-format regressions; not visual approval."""
import math,zipfile
from environment_pass import Mesh
from meridian_fieldkit import shell
from native_format import ROOT
from max_archive import PASSWORD
from native_terrain_pass import terrain_settings,world_to_grid

m=shell(Mesh)
# Cast through the front wall at standing-player heights and lateral clearances.
# Catch the earlier closed-facade bug even when the source still names it a door.
for x in (40,70,104):
 for y in (5,40,72,93):
  for ids in m.faces:
   a,b,c=[m.verts[i] for i in ids]
   den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-6:continue
   u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
   v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
   if min(u,v,1-u-v)<-1e-6:continue
   z=u*a[2]+v*b[2]+(1-u-v)*c[2]
   assert not -175<z<-110, ('blocked field-lab doorway',x,y,z)
# A closed exterior is insufficient: inside views need inward-facing end panels.
# Trace toward each end at head-above-door heights, checking the first surface's
# normal from both directions. This catches a single-sided roof gable.
def end_hit(x,y,start_z,direction):
 hits=[]
 for ids in m.faces:
  a,b,c=[m.verts[i] for i in ids]
  den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-6:continue
  u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
  v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
  if min(u,v,1-u-v)<-1e-6:continue
  z=u*a[2]+v*b[2]+(1-u-v)*c[2]
  distance=(z-start_z)*direction
  if distance>1e-6:hits.append((distance,m.norm[ids[0]][2]))
 assert hits, ('missing end panel',x,y,start_z,direction)
 distance,normal=min(hits)
 assert normal*direction<-.99, ('end panel faces away from viewer',x,y,start_z,direction)
for x,y in ((0,120),(0,136),(-175,120),(175,120)):
 for direction in (-1,1):
  end_hit(x,y,direction*30,direction) # start clear of the central lamp housing
  end_hit(x,y,direction*180,-direction)
for ids in m.faces:
 a,b,c=[m.verts[i] for i in ids]
 u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
 n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
 length=math.sqrt(sum(t*t for t in n));assert length>1e-6
 assert sum(n[i]*m.norm[ids[0]][i] for i in range(3))/length>.99, 'reversed shell surface'
mapfile=ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm'
with zipfile.ZipFile(mapfile) as z:
 z.setpassword(PASSWORD);paint=z.read('16777216.ptd');ed=terrain_settings({'ggterrain.dat':z.read('ggterrain.dat')})['editable_size']
assert len(paint)==4096**2
# Native paint data uses ordinary Z rows; sculpt data uses reversed rows.
for x,z in ((-1910,-7250),(-700,-8350),(0,-9600)):
 gx=world_to_grid(x,ed);gz=world_to_grid(z,ed)
 assert paint[gz*4096+gx]==23, ('wrong native road/court material or row orientation',x,z)
with zipfile.ZipFile(ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - Relayfall.fpm') as source:
 source.setpassword(PASSWORD);original=source.read('16777216.ptd')
# Preserve unowned geography; do not mirror the route onto the far side of MAX.
for x,z in ((-1910,7250),(6000,-7250),(0,4500)):
 i=world_to_grid(z,ed)*4096+world_to_grid(x,ed)
 assert paint[i]==original[i], ('paint escaped the owned service-route area',x,z)
print('FIELD KIT PASS: physical doorway, inside/outside end panels, shell winding, native road paint, unowned terrain preservation.')
print('Native material appearance and player collision still require MAX review.')
