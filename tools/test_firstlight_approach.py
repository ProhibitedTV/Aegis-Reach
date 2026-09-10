"""Opening composition safeguards against the rebuilt native map, not visual approval."""
import math,struct,zipfile
from native_format import ROOT,read_ele
from native_terrain_pass import terrain_settings,sculpt_index,SCULPT_NAME,TYPE_BYTES
from max_archive import PASSWORD

path=ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm'
with zipfile.ZipFile(path) as archive:
 archive.setpassword(PASSWORD)
 _,entities=read_ele(archive.read('map.ele'))
 settings=terrain_settings({'ggterrain.dat':archive.read('ggterrain.dat')})
 sculpt=archive.read(SCULPT_NAME)
by_name={e['101:eleprof.name_s']:e for e in entities}

def height(x,z):
 ed=settings['editable_size'];fx=(x/ed*.5+.5)*4096;fz=(z/ed*.5+.5)*4096
 gx,gz=math.floor(fx),math.floor(fz);tx,tz=fx-gx,fz-gz
 def sample(dx,dz):
  i=sculpt_index(gx+dx,gz+dz)
  assert sculpt[i]==1, 'approach is not authored native terrain'
  h=struct.unpack_from('<f',sculpt,TYPE_BYTES+i*4)[0]
  return settings['offset_y']+h*(settings['height'] if h>=0 else settings['minHeight'])
 return (sample(0,0)*(1-tx)+sample(1,0)*tx)*(1-tz)+(sample(0,1)*(1-tx)+sample(1,1)*tx)*tz

player=by_name['SEVEN // Meridian insertion']
x,z,yaw=player['101:x'],player['101:z'],player['101:ry']
# The field lab should occupy a substantial angle near the opening centre.
angles=[]
for xx in (-2487,-2213):
 for zz in (-7480,-7060):
  a=math.degrees(math.atan2(xx-x,zz-z));angles.append((a-yaw+180)%360-180)
assert min(angles)>-22 and max(angles)<12, ('lab outside opening focus',angles)
assert max(angles)-min(angles)>12, ('lab remains a distant miniature',angles)
assert z<-7800, 'spawn skipped the approach into camp'
# Check the serialized terrain, including grid interpolation, along the view ray.
eye=height(x,z)+64;clearance=[]
for i in range(1,100):
 t=i/100;xx=x+(-2210-x)*t;zz=z+(-7198-z)*t;yy=eye+(565-eye)*t
 clearance.append(yy-height(xx,zz))
assert min(clearance)>20, ('terrain hides the entrance',min(clearance))
# The backing bank should meet the court without the old near-vertical cliff.
profile=[height(xx,-7270) for xx in range(-2800,-2519,20)]
assert max(abs(b-a)/20 for a,b in zip(profile,profile[1:]))<1, 'steep wall returned behind lab'
assert height(-2800,-7270)<700, 'backing bank still overpowers lab'

mast=by_name['Camp 12 / Meridian survey mast'];lamp=by_name['FL LIGHT 2']
assert (mast['101:x'],mast['101:z'])==(lamp['101:x'],lamp['101:z'])
for dx in (-23,23):
 for dz in (-23,23):assert abs(height(mast['101:x']+dx,mast['101:z']+dz)-mast['101:y'])<.5
for name in ('FL LIGHT 1','FL LIGHT 2','FL LIGHT 3','FL BRINEGLASS LIGHT 1','FL BRINEGLASS LIGHT 2'):
 assert by_name[name]['326:eleprof.light.offsetup']==0, ('unintended fixture height offset',name)
assert lamp['101:eleprof.light.range']<abs(lamp['101:x']-(-2700)), 'mast still reaches rear cliff'
# Maintain the non-combat arrival while preserving native enemy positions.
for e in entities:
 if e['101:eleprof.name_s'].startswith('FL ENEMY'):
  assert math.hypot(e['101:x']-x,e['101:z']-z)>1800, 'spawn enters the first engagement'
print('APPROACH PASS: lab framing, native terrain sightline/grade, mast grounding and fixture offsets.')
print('Native MAX composition, exposure and collision still need screenshot/walkthrough review.')
