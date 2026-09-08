"""Build Mission 01, FIRST LIGHT, as a native GameGuru MAX level.

The playable slice is rebuilt from native terrain, a single authored environment
composition, mission/runtime entities, and installed local MAX asset references.
Licensed DLC payloads are never copied into the repository.
"""
from pathlib import Path
import json,math,struct,zipfile,shutil
from native_format import ROOT,INSTALL,read_ele,write_ele
from environment_pass import Mesh,clean_template,set_suffix,write_bank
from max_archive import PASSWORD,convert
from native_terrain_pass import terrain_settings,normalized_height,world_to_grid,grid_to_world,sculpt_index,TYPE_BYTES,SCULPT_NAME
from polish_relayfall import patch_visuals,patch_setting
from PIL import Image,ImageDraw,ImageFont

GAME=ROOT/'Aegis Reach';FILES=GAME/'Files';AS=FILES/'entitybank/Aegis Reach/First Light';AS.mkdir(parents=True,exist_ok=True)
SOURCE=FILES/'mapbank/Aegis Reach - Relayfall.fpm';MAP=FILES/'mapbank/Aegis Reach - First Light.fpm'
DESIGN=GAME/'Design/First Light';DESIGN.mkdir(parents=True,exist_ok=True)
T=json.loads((ROOT/'tools/reference/entity-templates.json').read_text())
static=next(v for k,v in T.items() if 'Warehouse - Red Grey' in k)
assets=[];entities=[];bank=[];placements=[];staged=set()

def fpe(path):
 d={}
 for line in path.read_text(errors='replace').splitlines():
  if '=' in line and not line.lstrip().startswith(';'):
   k,v=line.split('=',1);d[k.strip().lower()]=v.strip()
 return d

def stage(path):
 src=INSTALL/'entitybank'/path
 if not src.is_file():raise FileNotFoundError(src)
 staged.add(path)
 return fpe(src)

from firstlight_world import ground,TERRAIN_MATERIALS,architecture,ROUTE,RETURN

def add(path,name,x,z,y=None,ry=0,scale=100,script=None,kind='environment',template=None,**params):
 if y is None:y=ground(x,z)
 b=clean_template(template or T.get(path,static))
 data=fpe(FILES/'entitybank'/path) if path.startswith('Aegis Reach') else stage(path)
 for k in list(b):
  if k.startswith('material'):b[k]='' if isinstance(b[k],str) else 0
 for suffix,val in {
  'custom':0,'active':0,'maintype':1,'x':x,'y':y,'z':z,'rx':0,'ry':ry,'rz':0,
  'staticflag':1,'scalex':scale-100,'scaley':scale-100,'scalez':scale-100,
  'eleprof.name_s':name,'eleprof.texd_s':data.get('textured',''),
  'eleprof.effect_s':data.get('effect',r'effectbank\reloaded\apbr_basic.fx'),
  'eleprof.scale':float(data.get('scale','100') or 100),'eleprof.strength':0,
  'eleprof.isimmobile':1,'eleprof.physics':1,'eleprof.phyalways':1,
  'eleprof.aimain_s':'no_behavior_selected.lua','eleprof.hasweapon_s':'',
  'eleprof.soundset_s':'','eleprof.soundset1_s':'','eleprof.soundset2_s':'',
  'eleprof.soundset3_s':'','eleprof.soundset4_s':''
 }.items():set_suffix(b,suffix,val)
 if path not in bank:bank.append(path)
 set_suffix(b,'bankindex',bank.index(path)+1)
 if script:
  set_suffix(b,'staticflag',0);set_suffix(b,'eleprof.aimain_s',script)
 for suffix,val in params.items():
  if not set_suffix(b,suffix,val):raise KeyError(suffix)
 entities.append(b)
 placements.append(dict(id=len(entities),name=name,asset=path,x=x,y=y,z=z,rotation=ry,scale=scale,kind=kind))
 return b

def own(name,mesh,texture='aegis_atlas.png',collision=1):
 mesh.write(AS/(name+'.x'),texture)
 source=FILES/'entitybank/Aegis Reach'/texture
 if source.is_file():shutil.copy2(source,AS/texture)
 (AS/(name+'.fpe')).write_text(
  f'desc = {name}\nmodel = {name}.x\nscale = 100\ntextured = {texture}\n'
  f'baseColorMap = {texture}\neffect = effectbank\\reloaded\\apbr_basic.fx\n'
  f'collisionmode = {collision}\ndefaultstatic = 1\nstrength = 0\nmaterialindex = 2\n'
  'roughnessStrength = 0.82\nmetalnessStrength = 0.22\naimain = no_behavior_selected.lua\n'
 )
 assets.append(name)
 return 'Aegis Reach\\First Light\\'+name+'.fpe'

P='Booster Pack\\Military Pack\\';I='Industrial Collection\\Industrial\\'
def prop(path,x,z,**kw):return add(path,path.split('\\')[-1].removesuffix('.fpe'),x,z,**kw)

# Original crystalline geology. These are deliberately low-poly mineral prisms rather
# than fantasy crystals: they read as old hypersaline brineglass exposed by erosion.
def _mesh_tri(mesh,a,b,c,color=5):
 ux,uy,uz=b[0]-a[0],b[1]-a[1],b[2]-a[2]
 vx,vy,vz=c[0]-a[0],c[1]-a[1],c[2]-a[2]
 nx=uy*vz-uz*vy;ny=uz*vx-ux*vz;nz=ux*vy-uy*vx
 length=max(0.0001,math.sqrt(nx*nx+ny*ny+nz*nz));n=(nx/length,ny/length,nz/length)
 start=len(mesh.verts)
 for p,(u,v) in zip((a,b,c),((.12,.90),(.88,.90),(.50,.08))):
  mesh.verts.append(p);mesh.norm.append(n);mesh.uv.append(((color+u)/8,v))
 mesh.faces.append((start,start+1,start+2))

def _crystal_prism(mesh,x,z,r,h,angle=0,leanx=0,leanz=0,color=5):
 sides=5;lower=[];upper=[]
 for i in range(sides):
  a=math.radians(angle+i*360/sides)
  lower.append((x+math.cos(a)*r,0,z+math.sin(a)*r))
  upper.append((x+leanx+math.cos(a)*r*.82,h*.72,z+leanz+math.sin(a)*r*.82))
 tip=(x+leanx*1.45,h,z+leanz*1.45)
 for i in range(sides):
  j=(i+1)%sides
  _mesh_tri(mesh,lower[i],lower[j],upper[j],color)
  _mesh_tri(mesh,lower[i],upper[j],upper[i],color)
  _mesh_tri(mesh,upper[i],upper[j],tip,color)

def _build_brineglass():
 m=Mesh()
 specs=[
  (-40,-15,34,245,-8,-14,8),(18,20,27,190,12,8,-5),(58,-20,20,145,-18,10,4),
  (-72,42,19,130,25,-5,9),(12,-58,15,105,4,3,5),(78,48,12,82,-30,-2,4)
 ]
 for x,z,r,h,angle,lx,lz in specs:_crystal_prism(m,x,z,r,h,angle,lx,lz,5)
 path=own('Vesper Brineglass Bloom',m,collision=0)
 f=AS/'Vesper Brineglass Bloom.fpe'
 text=f.read_text().replace('roughnessStrength = 0.82','roughnessStrength = 0.18').replace('metalnessStrength = 0.22','metalnessStrength = 0.08')
 f.write_text(text+'reflectance = 0.58\n')
 return path

# One authoring layer owns all human-built spaces.
architecture(Mesh,own,add,prop,P,I)

# Sparse geology: terrain carries the landscape; rocks only break long silhouettes.
ROCK=r'Max Collection\Rocks\Rock Boulder.fpe'
for x,z,sz in [(-700,-8640,110),(940,-7690,120),(-850,-5700,140),(650,-4970,120),(-490,-4390,100),(1040,-3840,120)]:
 add(ROCK,'Basalt remnant / tide channel cover',x,z,scale=sz,ry=x%180)

# Brineglass is a visual breadcrumb toward the anomaly. Early blooms are small/cyan;
# growth becomes larger and more violet near AEGIS and the Choir fracture.
BRINEGLASS=_build_brineglass()
crystal_sites=[
 (-950,-8650,15,62,0x45C9D7,260),(1120,-7900,-20,55,0x45C9D7,240),
 (1300,-6050,30,68,0x4BC9D8,300),(-980,-5350,-15,72,0x4BC9D8,320),
 (1100,-4250,40,78,0x52D1DF,340),(-2650,-250,0,88,0x59D4E2,380),
 (2450,1850,65,96,0x62D8E5,420),(-1650,3750,-25,110,0x748CE8,460),
 (1250,4450,20,125,0x8B75E8,520),(350,5150,-35,138,0x9670EC,560)
]
for idx,(x,z,ry,scale,color,radius) in enumerate(crystal_sites,1):
 add(BRINEGLASS,'Brineglass bloom %02d'%idx,x,z,y=ground(x,z)-4,ry=ry,scale=scale,kind='geology')

# Warden occupation is a thin retrofit layer, not a second architecture system.
for x,z,angle in [(-720,-2660,0),(700,-2200,30),(1560,-1990,90)]:
 prop(P+'Concrete Barrier 01.fpe',x,z,ry=angle,scale=92)
for x,z in [(1630,-2500),(1910,-2500)]:
 prop(P+'Container 01a.fpe',x,z,ry=90,scale=82)
for x,z,ry in [(-720,-2140,0),(570,-1710,15),(-960,-560,90),(-750,2520,0),(650,2670,90)]:
 prop(P+'Hesco Barrier 01.fpe',x,z,ry=ry,scale=88)

# Return route: three staging bays are enough to explain the Warden reserve route.
for x,z in [(-3200,-1100),(-3250,220),(-3260,1530)]:
 prop(P+'Container 02a.fpe',x,z,ry=0,scale=90)
for x,z in [(-2810,1110),(-2690,1250)]:
 prop(P+'Gas Barrel 01a.fpe',x,z,scale=90)

# The player deploys armed. Stock weapon.lua pickups remain prohibited after a
# native MAX load crash; ammunition uses the known-safe ammo.lua path.
weapon='Max Collection\\Weapons\\'
for x,z in [(-1570,-6800),(-2050,-2200),(-1150,100),(1550,1250),(-850,3100),(300,-2200)]:
 path=weapon+'Compact Assault Rifle Ammo.fpe'
 add(path,'Supply: rifle ammunition',x,z,y=ground(x,z)+28,kind='ammo',template=T[path],script='ammo.lua',
     **{'eleprof.quantity':120,'eleprof.hasweapon_s':r'enhanced\MK18'})

SCRIPT=r'aegis_reach\firstlight_'
START=(0,-9500)
p=r'_markers\Player Start.fpe'
add(p,'SEVEN // Meridian insertion',*START,y=ground(*START)+60,kind='player',template=T[p],
    **{'eleprof.strength':200,'eleprof.lives':1,'eleprof.hasweapon_s':r'enhanced\MK18','eleprof.quantity':240,'eleprof.speed':110})
ct=r'Aegis Reach\Supply Crate.fpe'
add(ct,'FIRST LIGHT // DIRECTOR',0,-9500,y=100,kind='controller',script=SCRIPT+'director.lua',
    **{'eleprof.soundset_s':r'aegis_reach\firstlight\intro.wav'})
objectives=[
 ('POWER',-1250,-850,'NORTHSTAR // RESTORE POWER'),
 ('RECORDS',1300,1050,'OPERATIONS // RECOVER MANIFEST'),
 ('CORE',0,3200,'AEGIS // CANCEL STRIKE'),
 ('EXTRACT',0,-2350,'KESTREL // EXTRACTION')
]
for role,x,z,label in objectives:
 asset=r'Aegis Reach\Extraction Pad.fpe' if role=='EXTRACT' else r'Aegis Reach\Relay Terminal.fpe'
 add(asset,'FL '+role,x,z,y=ground(x,z),kind='objective',script=SCRIPT+'interact.lua',
     **{'eleprof.soundset_s':r'aegis_reach\relay.wav',
        'eleprof.soundset1_s':('aegis_reach\\firstlight\\'+role.lower()+'.wav') if role!='EXTRACT' else ''})
for role,x,z in [('INTEL1',-1690,-6980),('INTEL2',-2050,-5100),('INTEL3',1750,1150),
                 ('MED',-2150,-2110),('MED',650,1450),('MED',-950,2800)]:
 add(ct,'FL '+role,x,z,y=ground(x,z),scale=55,kind='intel' if role.startswith('INTEL') else 'medical',
     script=SCRIPT+'interact.lua')

# Encounter logic is deliberately preserved during this environment pass.
groups={
 1:[(-950,-5500),(650,-5080),(-300,-4600)],
 2:[(-800,-2700),(500,-2250),(1450,-2050)],
 3:[(-2000,-1250),(-1100,-700),(-1060,-100),(-840,80)],
 4:[(450,260),(1650,450),(850,1100),(1880,1090)],
 5:[(-750,2380),(650,2570),(-900,3160),(800,3450)],
 6:[(-2760,2150),(-3090,1570),(-3030,820),(-2950,260)],
 7:[(2050,-2550),(2050,-2380),(-3270,-1100),(-3270,-920),(2060,-2110),(-3190,-1300)]
}
ep=r'Characters\Tony - Armed Response.fpe'
for group,spots in groups.items():
 for j,(x,z) in enumerate(spots,1):
  add(ep,f'FL ENEMY {group} {j}',x,z,y=ground(x,z)+5,ry=180,kind='enemy',template=T[ep],
      script=SCRIPT+'enemy.lua',
      **{'eleprof.strength':110 if group<5 else 140,
         'eleprof.hasweapon_s':r'enhanced\MK18' if j%3 else r'enhanced\AR',
         'eleprof.quantity':30,'eleprof.damage':8,'eleprof.accuracy':130,
         'eleprof.weapondamagemultiplier':0.32,'eleprof.conerange':1300,'eleprof.isimmobile':0})

# Invisible native lights reinforce visible fixtures and let brineglass cast a real
# pool of color onto the terrain instead of reading as a painted emissive prop.
lightp=r'_markers\White Light.fpe';lighttemplate=T[lightp]
light_locations=[
 (-2050,-7060,0xE6B77A,680),(-1460,-7180,0xE6B77A,620),(-1690,-6800,0x73D8E8,480),
 (-430,-5600,0xCFA875,430),(280,-5000,0xCFA875,450),(320,-4050,0xCFA875,460),
 (-520,-3100,0x67D8EA,760),(520,-3100,0x67D8EA,760),
 (-1700,-1120,0xF0A35E,820),(-1700,-180,0xF0A35E,820),
 (980,120,0xC2D7DF,560),(1530,1080,0xC2D7DF,580),
 (-760,2800,0x70C7DC,900),(760,3380,0x70C7DC,900),
 (-750,-2200,0x67D8EA,850),(-2400,950,0xD6A96A,620)
]
for idx,(x,z,color,radius) in enumerate(light_locations,1):
 add(lightp,'FL LIGHT '+str(idx),x,z,y=ground(x,z)+155,kind='light',template=lighttemplate,
     script=r'markers\ConstantLight.lua',
     **{'eleprof.light.color':color,'eleprof.light.range':radius,'eleprof.light.index':idx,'eleprof.light.fLightHasProbe':0})
crystal_light_base=len(light_locations)
for offset,(x,z,ry,scale,color,radius) in enumerate(crystal_sites,1):
 idx=crystal_light_base+offset
 add(lightp,'FL BRINEGLASS LIGHT '+str(offset),x,z,y=ground(x,z)+82,kind='light',template=lighttemplate,
     script=r'markers\ConstantLight.lua',
     **{'eleprof.light.color':color,'eleprof.light.range':radius,'eleprof.light.index':idx,'eleprof.light.fLightHasProbe':0})

add(ct,'FIRST LIGHT // SCORE',50,-9500,y=100,kind='controller',script=r'aegis_reach\firstlight_score.lua',
    **{'eleprof.soundset_s':r'aegis_reach\music\salt_moon_drift.wav',
       'eleprof.soundset1_s':r'aegis_reach\music\moon_outpost_drift.wav',
       'eleprof.soundset2_s':r'aegis_reach\music\orbital_catacomb.wav'})

# Human-scale signage carries story; it is not used as a substitute for path design.
font=r'C:\Windows\Fonts\consolab.ttf'
def sign(name,lines,x,z,y,ry=0,color=(105,218,233)):
 im=Image.new('RGB',(1024,256),(15,27,36));d=ImageDraw.Draw(im)
 d.rectangle((4,4,1019,251),outline=color,width=8)
 for i,line in enumerate(lines):
  d.text((38,28+i*64),line,font=ImageFont.truetype(font,46 if i==0 else 31),fill=color if i==0 else (210,220,217))
 tex=name+'.png';im.save(AS/tex)
 if name in ('Evacuation Board','Extraction Sign'):
  height=y-(500 if z<-5000 else 600)
  support=Mesh()
  for px in (-195,195):support.box(px,0,0,16,height+50,16,2)
  post=own(name+' Supports',support)
  add(post,'Meridian field board frame',x,z,ry=ry)
 m=Mesh();m.box(0,0,0,440,110,8,0)
 m.uv=[(u*8,v) for u,v in m.uv]
 path=own(name,m,tex)
 add(path,'Environmental sign: '+lines[0],x,z,y=ground(x,z)+(y-(500 if z<-5000 else 600)),ry=ry,kind='sign')

sign('Evacuation Board',['MERIDIAN SURVEY','EVACUATED: 42 / EXPECTED: 43','M. SEN - SUBSURFACE TEAM'],-1800,-6780,560)
sign('Checkpoint Sign',['AEGIS // GATE 07','CIVILIAN EVACUATION SUSPENDED','ALL PERSONNEL RETURN INSIDE'],0,-3445,985)
sign('Power Sign',['NORTHSTAR','GRID ISOLATED / MANUAL RESTART','SERVICE ACCESS ON WEST SIDE'],-1250,-1675,915)
sign('Operations Sign',['OPERATIONS','MERIDIAN PERSONNEL ARCHIVE','WARDEN OVERRIDE IN FORCE'],850,-264,885)
sign('Core Sign',['AEGIS ARRAY','TARGET: MERIDIAN SHELTER 12','FIRING AUTHORITY: IRON WARDEN'],-740,2188,850)
sign('Extraction Sign',['KESTREL // LZ 07','KEEP THE LANDING ZONE CLEAR','PILOT WILL SIGNAL APPROACH'],420,-2715,750)

with zipfile.ZipFile(SOURCE) as z:
 z.setpassword(PASSWORD);payload={i.filename:z.read(i.filename) for i in z.infolist()}
version,_=read_ele(payload['map.ele'])
payload['map.ele']=write_ele(version,entities)
payload['map.ent']=write_bank(bank)
payload['map.way']=struct.pack('<ii',0,0)
payload['locked.cfg']=struct.pack('<i',0)

raw_terrain=payload['ggterrain.dat'];start=raw_terrain.index(b'{');end=raw_terrain.rindex(b'}')+1
terrain_json=json.loads(raw_terrain[start:end]);terrain_json.update(TERRAIN_MATERIALS)
terrain_text=json.dumps(terrain_json,indent=2).encode()
payload['ggterrain.dat']=struct.pack('<I',len(terrain_text))+terrain_text
settings=terrain_settings(payload);sculpt=bytearray(payload[SCULPT_NAME]);ed=settings['editable_size']
for gz in range(world_to_grid(-14000,ed),world_to_grid(10000,ed)+1):
 z=grid_to_world(gz,ed)
 for gx in range(world_to_grid(-10000,ed),world_to_grid(10000,ed)+1):
  x=grid_to_world(gx,ed);idx=sculpt_index(gx,gz);sculpt[idx]=1
  struct.pack_into('<f',sculpt,TYPE_BYTES+idx*4,normalized_height(ground(x,z),settings))
payload[SCULPT_NAME]=bytes(sculpt)

# Darker Vesper grade. The previous exposure/sun pair washed the old sea shelf toward
# beige and clipped the horizon. Lower global exposure lets local practicals and the
# brineglass pools carry the night scene; modest bloom supports emissive mystery.
visual,_=patch_visuals(payload['visuals.ini']);visual=visual.decode('latin1')
atmosphere={'FogNearest#':8200,'FogDistance#':28000,'Exposure':0.93,'SunIntensity':0.95,'BloomStrength':0.15}
for key,val in {'AmbientMusicTrack':'','AmbientMusicTrackVolume':0,**atmosphere}.items():
 visual=patch_setting(visual,key,val)
payload['visuals.ini']=visual.encode('latin1')

cfg=bytearray(payload['cfg.cfg']);struct.pack_into('<fff',cfg,0,10,-10500,20)
if b'V2\r\n' in cfg:
 struct.pack_into('<fffffff',cfg,cfg.index(b'V2\r\n')+8,10,2800,-10500,10,-10500,25,0)
payload['cfg.cfg']=bytes(cfg)

for key in list(payload):
 if key=='map.obs' or 'navmesh' in key.lower():del payload[key]

with zipfile.ZipFile(MAP,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
 for name,data in payload.items():out.writestr(name,data)
convert(MAP)

scene_recipe={
 'Camp 12':'compact Meridian field lab + survey/power/logistics clusters',
 'Gate 07':'modular overpass threshold + Warden retrofit',
 'Northstar':'twin-stack industrial yard',
 'Operations':'low modular civilian workplace',
 'AEGIS':'arrival frame + modular excavation threshold',
 'Choir':'bespoke buried nonhuman structure + increasingly active brineglass',
}
(DESIGN/'layout.json').write_text(json.dumps(placements,indent=2))
(DESIGN/'build-report.json').write_text(json.dumps({
 'map':MAP.name,'entities':len(entities),'enemy_count':sum(len(x) for x in groups.values()),
 'lights':len(light_locations)+len(crystal_sites),'assets':bank,'staged_dependencies':sorted(staged),
 'objectives':objectives,'native_terrain':True,'route':ROUTE,'return_route':RETURN,
 'terrain_materials':TERRAIN_MATERIALS,'scene_recipe':scene_recipe,'atmosphere':atmosphere,
 'crystal_clusters':len(crystal_sites),'environment_pass':'single-owner-production-recomposition'
},indent=2))
print('FIRST LIGHT:',len(entities),'entities,',len(bank),'asset types,',len(light_locations)+len(crystal_sites),'lights')
print('Vesper atmosphere: darker grade /',len(crystal_sites),'brineglass blooms')
print('Environment: single-owner production recomposition / no secondary Camp 12 dressing')