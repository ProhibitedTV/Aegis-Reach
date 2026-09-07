"""Build Mission 01, FIRST LIGHT, as a new native MAX level.

Preserves the prior Relayfall map. Authored terrain, encounter layout and story
objects are generated together so scenery supports the route and narrative.
"""
from pathlib import Path
import copy,json,math,re,struct,zipfile,shutil
from native_format import ROOT,INSTALL,read_ele,write_ele
from environment_pass import Mesh,clean_template,get_suffix,set_suffix,parse_bank,write_bank
from max_archive import PASSWORD,convert
from native_terrain_pass import terrain_settings,normalized_height,world_to_grid,grid_to_world,sculpt_index,TYPE_BYTES,SCULPT_NAME,vesper_height_units,rect_mask
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
 # Licensed payloads stay in the user's MAX installation. Only references enter Git.
 src=INSTALL/'entitybank'/path
 if not src.is_file():raise FileNotFoundError(src)
 staged.add(path)
 return fpe(src)

from firstlight_world import ground,PADS,TERRAIN_MATERIALS,architecture,ROUTE,RETURN


def add(path,name,x,z,y=None,ry=0,scale=100,script=None,kind='environment',template=None,**params):
 if y is None:y=ground(x,z)
 b=clean_template(template or T.get(path,static))
 data=fpe(FILES/'entitybank'/path) if path.startswith('Aegis Reach') else stage(path)
 for k in list(b):
  if k.startswith('material'):b[k]='' if isinstance(b[k],str) else 0
 for suffix,val in {'custom':0,'active':0,'maintype':1,'x':x,'y':y,'z':z,'rx':0,'ry':ry,'rz':0,'staticflag':1,'scalex':scale-100,'scaley':scale-100,'scalez':scale-100,'eleprof.name_s':name,'eleprof.texd_s':data.get('textured',''),'eleprof.effect_s':data.get('effect',r'effectbank\reloaded\apbr_basic.fx'),'eleprof.scale':float(data.get('scale','100') or 100),'eleprof.strength':0,'eleprof.isimmobile':1,'eleprof.physics':1,'eleprof.phyalways':1,'eleprof.aimain_s':'no_behavior_selected.lua','eleprof.hasweapon_s':'','eleprof.soundset_s':'','eleprof.soundset1_s':'','eleprof.soundset2_s':'','eleprof.soundset3_s':'','eleprof.soundset4_s':''}.items():set_suffix(b,suffix,val)
 if path not in bank:bank.append(path)
 set_suffix(b,'bankindex',bank.index(path)+1)
 if script:
  set_suffix(b,'staticflag',0);set_suffix(b,'eleprof.aimain_s',script)
 for suffix,val in params.items():
  if not set_suffix(b,suffix,val):raise KeyError(suffix)
 entities.append(b);placements.append(dict(id=len(entities),name=name,asset=path,x=x,y=y,z=z,rotation=ry,scale=scale,kind=kind))
 return b

def own(name,mesh,texture='aegis_atlas.png',collision=1):
 mesh.write(AS/(name+'.x'),texture)
 source=FILES/'entitybank/Aegis Reach'/texture
 if source.is_file():shutil.copy2(source,AS/texture)
 (AS/(name+'.fpe')).write_text(f'desc = {name}\nmodel = {name}.x\nscale = 100\ntextured = {texture}\nbaseColorMap = {texture}\neffect = effectbank\\reloaded\\apbr_basic.fx\ncollisionmode = {collision}\ndefaultstatic = 1\nstrength = 0\nmaterialindex = 2\nroughnessStrength = 0.82\nmetalnessStrength = 0.22\naimain = no_behavior_selected.lua\n')
 assets.append(name);return 'Aegis Reach\\First Light\\'+name+'.fpe'

# A compact single-post work light. The old two-post 335-inch fixture read as a
# giant black goalpost and accidentally became the dominant route architecture.
m=Mesh();m.box(0,0,0,18,178,18,2);m.box(0,158,0,100,22,42,6);m.box(0,154,-24,72,8,6,5);LAMP=own('Floodlight Mast',m)
m=Mesh();m.box(0,0,0,320,70,95,1);m.box(-120,65,0,45,65,95,2);m.box(120,65,0,45,65,95,2);COVER=own('Revetment',m)
P='Booster Pack\\Military Pack\\';I='Industrial Collection\\Industrial\\'
def prop(path,x,z,**kw):return add(path,path.split('\\')[-1].removesuffix('.fpe'),x,z,**kw)
architecture(Mesh,own,add,prop,P,I)

# Geology is sparse and intentional; native terrain does the heavy lifting.
ROCK=r'Max Collection\Rocks\Rock Boulder.fpe'
for x,z,sz in [(-700,-8640,110),(940,-7690,120),(-850,-5700,140),(650,-4970,120),(-490,-4390,100),(1040,-3840,120)]:
 add(ROCK,'Basalt remnant / tide channel cover',x,z,scale=sz,ry=x%180)

# Survey Camp 12: abandoned work zones layered on top of the larger silhouettes
# authored in firstlight_world.py. These objects communicate how people used it.
for x,z in [(-2030,-7280),(-1580,-7360)]:prop(P+'Tent 01a.fpe',x,z,y=500,scale=75)
for i in range(3):
 prop(P+'Portable Cot 01a.fpe',-2030+i*175,-7250,y=505,ry=90,scale=90)
 prop(P+'Wooden Crate 01a.fpe',-1400+i*145,-6870,y=500,ry=8*i)
prop(P+'Desk 01a.fpe',-1700,-6950,y=500,ry=180)
prop(P+'Computer 01a.fpe',-1700,-6950,y=575,ry=180)
prop(P+'Desk Chair 01a.fpe',-1780,-6900,y=500,ry=120)
prop(I+'Cylinder - Oxygen.fpe',-2220,-6880,y=500)

# Retrofitted checkpoint: cover faces the escape road and civilian route alike.
for x,z,angle in [(-720,-2660,0),(700,-2200,30),(1560,-1990,90)]:prop(P+'Concrete Barrier 01.fpe',x,z,ry=angle)
for x,z in [(1630,-2500),(1910,-2500)]:prop(P+'Container 01a.fpe',x,z,ry=90,scale=85)
for x,z in [(-720,-2140),(570,-1710),(-960,-560),(-750,2520),(650,2670)]:add(COVER,'Warden retrofitted fighting position',x,z)

# Return route follows a separate graded maintenance road, with concealed staging bays.
for x,z in [(-3200,-1100),(-3250,220),(-3260,1530)]:prop(P+'Container 02a.fpe',x,z,ry=0,scale=95)
for x,z in [(-2810,1110),(-2690,1250)]:prop(P+'Gas Barrel 01a.fpe',x,z)

# The player already deploys with an MK18. Do not author loose stock weapon.lua
# pickups here: native MAX has crashed loading hand-authored pickup state.
weapon='Max Collection\\Weapons\\'
for x,z in [(-1570,-6800),(-2050,-2200),(-1150,100),(1550,1250),(-850,3100),(300,-2200)]:
 path=weapon+'Compact Assault Rifle Ammo.fpe'
 add(path,'Supply: rifle ammunition',x,z,y=ground(x,z)+28,kind='ammo',template=T[path],script='ammo.lua',**{'eleprof.quantity':120,'eleprof.hasweapon_s':r'enhanced\MK18'})

# Mission entities and objective clues share one specification with the runtime.
SCRIPT=r'aegis_reach\firstlight_'
START=(0,-9500)
p=r'_markers\Player Start.fpe'
add(p,'SEVEN // Meridian insertion',*START,y=ground(*START)+60,kind='player',template=T[p],**{'eleprof.strength':200,'eleprof.lives':1,'eleprof.hasweapon_s':r'enhanced\MK18','eleprof.quantity':240,'eleprof.speed':110})
ct=r'Aegis Reach\Supply Crate.fpe'
add(ct,'FIRST LIGHT // DIRECTOR',0,-9500,y=100,kind='controller',script=SCRIPT+'director.lua',**{'eleprof.soundset_s':r'aegis_reach\firstlight\intro.wav'})
objectives=[('POWER',-1250,-850,'NORTHSTAR // RESTORE POWER'),('RECORDS',1300,1050,'OPERATIONS // RECOVER MANIFEST'),('CORE',0,3200,'AEGIS // CANCEL STRIKE'),('EXTRACT',0,-2350,'KESTREL // EXTRACTION')]
for role,x,z,label in objectives:
 asset=r'Aegis Reach\Extraction Pad.fpe' if role=='EXTRACT' else r'Aegis Reach\Relay Terminal.fpe'
 add(asset,'FL '+role,x,z,y=ground(x,z),kind='objective',script=SCRIPT+'interact.lua',**{'eleprof.soundset_s':r'aegis_reach\relay.wav','eleprof.soundset1_s':('aegis_reach\\firstlight\\'+role.lower()+'.wav') if role!='EXTRACT' else ''})
for role,x,z in [('INTEL1',-1690,-6980),('INTEL2',-2050,-5100),('INTEL3',1750,1150),('MED',-2150,-2110),('MED',650,1450),('MED',-950,2800)]:
 add(ct,'FL '+role,x,z,y=ground(x,z),scale=55,kind='intel' if role.startswith('INTEL') else 'medical',script=SCRIPT+'interact.lua')

# Groups activate locally. Delayed reserves start concealed behind architecture.
groups={
 1:[(-950,-5500),(650,-5080),(-300,-4600)],
 2:[(-800,-2700),(500,-2250),(1450,-2050)],
 3:[(-2000,-1250),(-1100,-700),(-1060,-100),(-840,80)],
 4:[(450,260),(1650,450),(850,1100),(1880,1090)],
 5:[(-750,2380),(650,2570),(-900,3160),(800,3450)],
 6:[(-2760,2150),(-3090,1570),(-3030,820),(-2950,260)],
 7:[(2050,-2550),(2050,-2380),(-3270,-1100),(-3270,-920),(2060,-2110),(-3190,-1300)]}
ep=r'Characters\Tony - Armed Response.fpe'
for group,spots in groups.items():
 for j,(x,z) in enumerate(spots,1):
  add(ep,f'FL ENEMY {group} {j}',x,z,y=ground(x,z)+5,ry=180,kind='enemy',template=T[ep],script=SCRIPT+'enemy.lua',**{'eleprof.strength':110 if group<5 else 140,'eleprof.hasweapon_s':r'enhanced\MK18' if j%3 else r'enhanced\AR','eleprof.quantity':30,'eleprof.damage':8,'eleprof.accuracy':130,'eleprof.weapondamagemultiplier':0.32,'eleprof.conerange':1300,'eleprof.isimmobile':0})

# Deliberate pools of light follow real work areas and the route spine.
lightp=r'_markers\White Light.fpe';lighttemplate=T[lightp]
light_locations=[
 (-2050,-7160,500,0xE7BB80,720),(-1320,-7000,500,0xE7BB80,720),
 (-1080,-6460,500,0xDBB890,520),(-340,-5600,300,0xDBB890,480),
 (260,-5050,120,0xDBB890,500),(300,-4050,290,0xDBB890,500),
 (-620,-3100,640,0x67D8EA,820),(620,-3100,640,0x67D8EA,820),
 (-1700,-1200,900,0xFFAC65,950),(-1700,-50,900,0xFFAC65,950),
 (1100,200,1080,0xAACEDD,650),(1600,1150,1080,0xAACEDD,650),
 (-900,2800,1540,0x70C7DC,1000),(900,3400,1540,0x70C7DC,1000),
 (-750,-2200,650,0x67D8EA,1000),
 (-2400,-450,900,0xE0B16D,700),(-2400,950,1100,0xE0B16D,700),(-2400,2350,1350,0xE0B16D,700)
]
for idx,(x,z,y,color,radius) in enumerate(light_locations,1):
 y=ground(x,z)
 fixture_height=150
 add(LAMP,'Working lamp / '+str(idx),x,z,y=y,scale=100)
 add(lightp,'FL LIGHT '+str(idx),x,z,y=y+fixture_height,kind='light',template=lighttemplate,script=r'markers\ConstantLight.lua',**{'eleprof.light.color':color,'eleprof.light.range':radius,'eleprof.light.index':idx,'eleprof.light.fLightHasProbe':0})

# Preserve the supplied score cues through the semantic controller.
add(ct,'FIRST LIGHT // SCORE',50,-9500,y=100,kind='controller',script=r'aegis_reach\firstlight_score.lua',**{'eleprof.soundset_s':r'aegis_reach\music\salt_moon_drift.wav','eleprof.soundset1_s':r'aegis_reach\music\moon_outpost_drift.wav','eleprof.soundset2_s':r'aegis_reach\music\orbital_catacomb.wav'})

# Native model signs communicate purpose and tell the evacuation story at human scale.
font=r'C:\Windows\Fonts\consolab.ttf'
def sign(name,lines,x,z,y,ry=0,color=(105,218,233)):
 im=Image.new('RGB',(1024,256),(15,27,36));d=ImageDraw.Draw(im)
 d.rectangle((4,4,1019,251),outline=color,width=8)
 for i,line in enumerate(lines):d.text((38,28+i*64),line,font=ImageFont.truetype(font,46 if i==0 else 31),fill=color if i==0 else (210,220,217))
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

sign('Evacuation Board',['MERIDIAN SURVEY','EVACUATED: 42 / EXPECTED: 43','M. SEN - SUBSURFACE TEAM'], -1800,-6780,560)
sign('Checkpoint Sign',['AEGIS // GATE 07','CIVILIAN EVACUATION SUSPENDED','ALL PERSONNEL RETURN INSIDE'],0,-3445,985)
sign('Power Sign',['NORTHSTAR','GRID ISOLATED / MANUAL RESTART','SERVICE ACCESS ON WEST SIDE'],-1250,-1675,915)
sign('Operations Sign',['OPERATIONS','MERIDIAN PERSONNEL ARCHIVE','WARDEN OVERRIDE IN FORCE'],850,-264,885)
sign('Core Sign',['AEGIS ARRAY','TARGET: MERIDIAN SHELTER 12','FIRING AUTHORITY: IRON WARDEN'],-740,2188,850)
sign('Extraction Sign',['KESTREL // LZ 07','KEEP THE LANDING ZONE CLEAR','PILOT WILL SIGNAL APPROACH'],420,-2715,750)

with zipfile.ZipFile(SOURCE) as z:
 z.setpassword(PASSWORD);payload={i.filename:z.read(i.filename) for i in z.infolist()}
version,_=read_ele(payload['map.ele']);payload['map.ele']=write_ele(version,entities);payload['map.ent']=write_bank(bank);payload['map.way']=struct.pack('<ii',0,0);payload['locked.cfg']=struct.pack('<i',0)
# True editable MAX terrain; preserve settings and replace the bounded authored region.
raw_terrain=payload['ggterrain.dat'];start=raw_terrain.index(b'{');end=raw_terrain.rindex(b'}')+1
terrain_json=json.loads(raw_terrain[start:end]);terrain_json.update(TERRAIN_MATERIALS)
terrain_text=json.dumps(terrain_json,indent=2).encode();payload['ggterrain.dat']=struct.pack('<I',len(terrain_text))+terrain_text
settings=terrain_settings(payload);sculpt=bytearray(payload[SCULPT_NAME]);ed=settings['editable_size']
for gz in range(world_to_grid(-14000,ed),world_to_grid(10000,ed)+1):
 z=grid_to_world(gz,ed)
 for gx in range(world_to_grid(-10000,ed),world_to_grid(10000,ed)+1):
  x=grid_to_world(gx,ed);idx=sculpt_index(gx,gz);sculpt[idx]=1
  struct.pack_into('<f',sculpt,TYPE_BYTES+idx*4,normalized_height(ground(x,z),settings))
payload[SCULPT_NAME]=bytes(sculpt)
visual,_=patch_visuals(payload['visuals.ini']);visual=visual.decode('latin1')
for key,val in {'AmbientMusicTrack':'','AmbientMusicTrackVolume':0,'FogNearest#':9500,'FogDistance#':31000,'Exposure':1.25,'SunIntensity':1.35,'BloomStrength':0.10}.items():visual=patch_setting(visual,key,val)
payload['visuals.ini']=visual.encode('latin1')
cfg=bytearray(payload['cfg.cfg']);struct.pack_into('<fff',cfg,0,10,-10500,20)
if b'V2\r\n' in cfg:struct.pack_into('<fffffff',cfg,cfg.index(b'V2\r\n')+8,10,2800,-10500,10,-10500,25,0)
payload['cfg.cfg']=bytes(cfg)
# Drop stale navmesh data: MAX must build it from the new authored geometry.
for key in list(payload):
 if key=='map.obs' or 'navmesh' in key.lower():del payload[key]
with zipfile.ZipFile(MAP,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
 for name,data in payload.items():out.writestr(name,data)
convert(MAP)
(DESIGN/'layout.json').write_text(json.dumps(placements,indent=2))
(DESIGN/'build-report.json').write_text(json.dumps({'map':MAP.name,'entities':len(entities),'enemy_count':sum(len(x) for x in groups.values()),'lights':len(light_locations),'assets':bank,'staged_dependencies':sorted(staged),'objectives':objectives,'native_terrain':True,'route':ROUTE,'return_route':RETURN,'terrain_materials':TERRAIN_MATERIALS},indent=2))
print('FIRST LIGHT:',len(entities),'entities,',len(bank),'asset types,',len(light_locations),'lights')
