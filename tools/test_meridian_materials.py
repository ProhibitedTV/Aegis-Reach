"""Guard actual material channels, UV coverage and normal-map prerequisites."""
from pathlib import Path
import hashlib
import math
import tempfile
from PIL import Image,ImageStat
from environment_pass import Mesh
from meridian_fieldkit import textures,shell,mast,utility_spine,ATLAS,EMISSION,NORMAL,SURFACE,TILE
from native_format import ROOT

# Every rendered triangle needs a noncollapsed UV frame before normal mapping.
for mesh in (shell(Mesh),mast(Mesh),utility_spine(Mesh)):
 for ids in mesh.faces:
  a,b,c=[mesh.uv[i] for i in ids]
  area=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
  assert abs(area)>1e-10, ('collapsed normal-map UV triangle',ids)

with tempfile.TemporaryDirectory() as directory:
 folder=Path(directory);textures(folder)
 names=(ATLAS,EMISSION,NORMAL,SURFACE)
 first={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in names}
 textures(folder)
 assert first=={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in names}, 'nondeterministic material build'
 images={name:Image.open(folder/name) for name in names}
 try:
  assert all(im.size==(8*TILE,TILE) for im in images.values())
  normal=images[NORMAL];surface=images[SURFACE];emission=images[EMISSION]
  assert normal.mode=='RGB' and surface.mode=='RGBA'
  assert surface.getchannel('R').getextrema()==(255,255), 'unexpected baked shading'
  assert surface.getchannel('A').getextrema()==(255,255), 'reflectance multiplier must remain neutral'
  # Normals must point outward, have unit length and remain shallow.
  pixels=normal.tobytes()
  for r,g,b in zip(pixels[0::3],pixels[1::3],pixels[2::3]):
   x,y,z=(r/127.5-1,g/127.5-1,b/127.5-1)
   assert z>.85 and abs(math.sqrt(x*x+y*y+z*z)-1)<.012
  for tile in (4,5):
   patch=normal.crop((tile*TILE,0,(tile+1)*TILE,TILE))
   assert patch.getextrema()==((128,128),(128,128),(255,255)), 'bumpy light diffuser'
  # The rivets/seams must be inside the UV crop, not drawn in discarded gutters.
  for x,y in ((32,32),(23,100)):
   cx,cy=round(x*TILE/256),round(y*TILE/256)
   patch=normal.crop((cx-7,cy-7,cx+8,cy+8))
   assert patch.getchannel('B').getextrema()[0]<255, 'invisible surface detail'
   assert .07*TILE<cx<.93*TILE and .07*TILE<cy<.93*TILE
  # Printed identification is ink on paint, not an embossed normal-map label.
  patch=normal.crop((6*TILE+90,220,6*TILE+420,426))
  assert patch.getextrema()==((128,128),(128,128),(255,255))
  steel=ImageStat.Stat(surface.crop((2*TILE+100,100,2*TILE+400,400))).mean
  paint=ImageStat.Stat(surface.crop((100,100,400,400))).mean
  assert steel[2]>190 and paint[2]<5 and steel[1]+35<paint[1], 'paint/steel response collapsed'
  for tile in (0,1,2,3,6,7):
   assert emission.crop((tile*TILE,0,(tile+1)*TILE,TILE)).getbbox() is None, 'unintended glowing panel'
 finally:
  for im in images.values():im.close()

# Verify the deployed FPEs reference the generated maps and do not suppress them.
folder=ROOT/'Aegis Reach/Files/entitybank/Aegis Reach/First Light'
for name in ('Meridian Field Lab','Camp 12 Survey Mast','Camp 12 Utility Spine'):
 fields={k.strip().lower():v.strip() for k,v in
         (line.split('=',1) for line in (folder/(name+'.fpe')).read_text().splitlines() if '=' in line)}
 for field,filename in (('normalmap',NORMAL),('surfacemap',SURFACE)):
  assert fields[field]==filename and (folder/filename).is_file()
 assert float(fields['roughnessstrength'])==1 and float(fields['metalnessstrength'])==1
 assert 0<float(fields['normalstrength'])<=1
print('MERIDIAN MATERIAL PASS: valid UV frames, visible details, coordinated channels, deterministic original maps.')
print('Native MAX response remains unreviewed; these checks do not establish visual quality.')
