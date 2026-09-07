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
 src=INSTALL/'entitybank'/path
 if not src.is_file():raise FileNotFoundError(src)
 data=fpe(src)
 for q in [src,*src.parent.glob(src.stem+'.*')]:
  if q.is_file():
   dst=FILES/q.relative_to(INSTALL);dst.parent.mkdir(parents=True,exist_ok=True)
   if not dst.exists():shutil.copy2(q,dst)
   staged.add(str(q.relative_to(INSTALL)))
 for val in data.values():
  val=val.replace('\\','/')
  if not re.search(r'\.(dds|png|dbo|x|wav|ogg|jpg|bmp)$',val,re.I):continue
  for q in (src.parent/val,INSTALL/val):
   if q.is_file():
    dst=FILES/q.relative_to(INSTALL);dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists():shutil.copy2(q,dst)
    staged.add(str(q.relative_to(INSTALL)));break
 return data

# Native topography: natural outer shelf with flat pads ONLY where engineers built.
PADS=[(-1700,-7100,720,650,500),(-1350,-700,820,1000,598),(1250,700,810,900,598),(0,2850,1100,850,598)]
def ground(x,z):
 h=vesper_height_units(x,z)
 if -3000<z<3900 and abs(x)<2850:h=598
 for cx,cz,hx,hz,y in PADS:
  blend=rect_mask(x,z,cx,cz,hx,hz,400)
  h=h*(1-blend)+y*blend
 return h

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

m=Mesh();m.box(0,-25,0,800,25,800,1);FLOOR=own('Service Foundation',m)
m=Mesh();m.box(0,0,0,600,330,50,1);m.box(0,300,0,615,35,70,2);m.box(0,30,-27,590,12,5,4);WALL=own('Service Wall',m)
m=Mesh();m.box(0,0,0,160,290,60,1);m.box(380,0,0,160,290,60,1);m.box(190,250,0,550,80,70,2);PORTAL=own('Open Service Door',m)
m=Mesh();m.box(0,0,0,380,60,30,4);m.box(0,5,-18,370,48,5,6);SIGNBASE=own('Sign Support',m)
m=Mesh();m.box(-100,0,0,30,335,30,2);m.box(100,0,0,30,335,30,2);m.box(0,310,0,270,40,70,6);m.box(0,302,-39,230,16,6,5);LAMP=own('Floodlight Mast',m)
m=Mesh();m.box(0,0,0,320,70,95,1);m.box(-120,65,0,45,65,95,2);m.box(120,65,0,45,65,95,2);COVER=own('Revetment',m)
m=Mesh()
for i in range(5):m.box(0,i*10,i*100,700,10,100,2)
RAMP=own('Five Step Service Ramp',m)
m=Mesh()
for i in range(7):m.box(-650+i*210,0,0,65,450+(i%3)*95,115,6)
RIBS=own('Choir Excavation Ribs',m,'vesper_story_atlas.png')
# Deck route in the facility: remove the old box-grid layout entirely in this mission.
for x in range(-2400,2401,800):
 for z in range(-2600,3801,800):add(FLOOR,'Poured foundation',x,z,y=600)
# Cliffs constrain combat space; foreground boulders break sightlines rather than fill routes.
ROCK=r'Max Collection\Rocks\Rock Boulder.fpe';TALL=r'Max Collection\Rocks\Rock Tall Long.fpe'
for side in (-1,1):
 for i,z in enumerate(range(-9600,4001,750)):
  x=side*(3150+450*math.sin(i*1.1));add(TALL,'Basalt escarpment',x,z,scale=300+(i%3)*90,ry=i*47)
for x,z,sz in [(-650,-8550,200),(800,-8170,220),(-650,-6480,150),(900,-5900,150),(-1350,-5560,170),(600,-4750,210),(-850,-3940,180),(1050,-3550,180)]:add(ROCK,'Windward basalt / combat cover',x,z,scale=sz,ry=x%180)
# Landmark remnants and the view toward the moon.
for p in ('Aurelia','Orbital Spine','Relay Crown','Service Gantry'):
 src=FILES/'entitybank/Aegis Reach'/(p+'.fpe')
 if not src.exists():
  from environment_pass import build_assets
  build_assets();break
add(r'Aegis Reach\Aurelia.fpe','Aurelia above the Meridian shelf',-15000,22000,y=11800,scale=100)
for i in range(3):add(r'Aegis Reach\Orbital Spine.fpe','Broken orbital infrastructure',7600+i*2600,12000+i*1700,y=6200+i*900,ry=20+i*25)
# Threshold: a wall follows the old sea line, interrupted at the road.
for x in (-2550,-1950,-1350,1350,1950,2550):add(WALL,'AEGIS wall built across the civilian road',x,-3000)
add(r'Aegis Reach\Service Gantry.fpe','Gate 7',0,-3000,y=600)
# Genuine installed props, composed by function and history.
P='Booster Pack\\Military Pack\\'
I='Industrial Collection\\Industrial\\'
C='Cyberpunk Streets Booster Pack\\Misc\\'
def prop(path,x,z,**kw):return add(path,Path(path).stem,x,z,**kw)
# Evacuation camp: abandoned beds, a packed cargo line, overturned chairs and a roster desk.
for x,z in [(-2030,-7280),(-1580,-7360)]:prop(P+'Tent 01a.fpe',x,z,y=500,scale=75)
for i in range(3):
 prop(P+'Portable Cot 01a.fpe',-2030+i*175,-7250,y=505,ry=90,scale=90)
 prop(P+'Wooden Crate 01a.fpe',-1400+i*145,-6870,y=500,ry=8*i)
prop(P+'Desk 01a.fpe',-1700,-6950,y=500,ry=180)
prop(P+'Computer 01a.fpe',-1700,-6950,y=575,ry=180)
prop(P+'Desk Chair 01a.fpe',-1780,-6900,y=500,ry=120)
prop(I+'Cylinder - Oxygen.fpe',-2220,-6880,y=500)
# Checkpoint: barricades face BOTH ways; its operators were containing civilians.
for x,z in [(-650,-2570),(550,-2320),(1250,-1980)]:prop(P+'Concrete Barrier 01.fpe',x,z,y=600,ry=15)
for i in range(3):prop(P+'Container 01a.fpe',1500+i*240,-2440,y=600,ry=90,scale=85)
prop(P+'Generator 01a.fpe',-2050,-2350,y=600,ry=90)
for x,z in [(-1000,-2170),(200,-1820),(-2200,-1750),(1500,-1530)]:add(COVER,'Checkpoint hard cover',x,z,y=600)
# POWER HALL: generator court, shadowed flanking aisle, a raised maintenance position.
for x in (-2100,-1500,-900):
 for z in (-1520,350):add(WALL,'Northstar turbine hall outer wall',x,z,y=600)
for z in (-1200,-600,0):add(WALL,'Northstar west facade',-2400,z,y=600,ry=90)
for z in (-1100,-200):prop(P+'Generator 04a.fpe',-1650,z,y=600,ry=90)
for z in (-850,-300):prop(I+'Storage Tank - Small.fpe',-2200,z,y=600)
for x in (-1400,-1100):prop(I+'Control Box - Large.fpe',x,150,y=600,ry=180)
for x,z in [(-1850,-1150),(-1000,-650),(-1500,100)]:add(COVER,'Turbine maintenance cover',x,z,y=600)
# OPERATIONS: roofed room with multiple entrances and a quiet record alcove.
for x in (850,1650):
 for z in (100,900):add(FLOOR,'Operations roof',x,z,y=970)
for x in (650,1250,1850):
 for z in (-350,1650):add(WALL,'Operations outer facade',x,z,y=600)
for z in (0,600,1200):
 add(WALL,'Operations east facade',2250,z,y=600,ry=90)
for z in (0,1200):add(WALL,'Operations west facade',250,z,y=600,ry=90)
# Width-600 opening at west center allows a second entrance/flank.
for i in range(5):prop(P+'Locker 01a.fpe',1950,200+i*240,y=600,ry=-90)
for x,z in [(780,50),(1250,450),(1700,950)]:
 prop(P+'Desk 01a.fpe',x,z,y=600,ry=90);prop(P+'Computer 01a.fpe',x,z,y=675,ry=90)
for x in (750,1050,1350):prop(P+'Portable Cot 01a.fpe',x,1380,y=600,ry=90)
# CORE: a horseshoe chamber built over a excavation. Ribs predate all human work.
for x in (-1000,-400,200,800):add(WALL,'Core north blastwall',x,3800,y=600)
for z in (2300,2900,3500):
 for x in (-1250,1250):add(WALL,'Core flank buttress',x,z,y=600,ry=90)
for x in (-800,0,800):add(FLOOR,'Core observation canopy',x,3000,y=1200)
add(RIBS,'Excavation predating AEGIS',0,3500,y=600)
add(r'Aegis Reach\Relay Crown.fpe','AEGIS uplink crown',0,3100,y=600)
for x in (-900,900):prop(I+'Control Box - Tall.fpe',x,3350,y=600,ry=180)
for x,z in [(-650,2480),(550,2670),(-900,3170),(800,3560)]:add(COVER,'Core security position',x,z,y=600)
# Evacuation route returns through a service yard, with cover facing the pursuit.
for z in (-800,500,1750):
 prop(P+'Container 02a.fpe',-2650,z,y=600,ry=0,scale=95)
for i in range(4):prop(P+'Gas Barrel 01a.fpe',-2350+(i%2)*110,1200+(i//2)*130,y=600)
# Loot is placed in believable supply/story spaces, with distinct weapon choices.
weapon='Max Collection\\Weapons\\'
for path,name,x,z,qty in [(weapon+'Patrol Rifle.fpe','Survey watch rifle',-1550,-6890,60),(weapon+'Tactical Pump Shotgun.fpe','Checkpoint breach shotgun',1700,-2200,32)]:
 add(path,name,x,z,y=(535 if z<-5000 else 650),kind='weapon',template=T[path],script='weapon.lua',**{'eleprof.quantity':qty})
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
 add(asset,'FL '+role,x,z,y=600,kind='objective',script=SCRIPT+'interact.lua',**{'eleprof.soundset_s':r'aegis_reach\relay.wav','eleprof.soundset1_s':('aegis_reach\\firstlight\\'+role.lower()+'.wav') if role!='EXTRACT' else ''})
for role,x,z in [('INTEL1',-1690,-6980),('INTEL2',-2050,-5100),('INTEL3',1750,1150),('MED',-2150,-2110),('MED',650,1450),('MED',-950,2800)]:
 add(ct,'FL '+role,x,z,y=ground(x,z),scale=55,kind='intel' if role.startswith('INTEL') else 'medical',script=SCRIPT+'interact.lua')
# Groups activate locally. Delayed reserves start concealed behind architecture.
groups={
 1:[(-950,-5500),(650,-5080),(-300,-4600)],
 2:[(-800,-2700),(500,-2250),(1450,-2050)],
 3:[(-2000,-1250),(-1100,-700),(-1750,-100),(-1150,160)],
 4:[(650,100),(1650,450),(850,1100),(1850,1350)],
 5:[(-750,2380),(650,2570),(-900,3160),(800,3450)],
 6:[(-2100,2100),(-2450,1450),(2000,2200),(2200,1700)],
 7:[(1600,-1750),(1850,-1850),(-2100,-1750),(-2350,-1800),(1400,-1400),(-1800,-1400)]}
ep=r'Characters\Tony - Armed Response.fpe'
for group,spots in groups.items():
 for j,(x,z) in enumerate(spots,1):
  add(ep,f'FL ENEMY {group} {j}',x,z,y=ground(x,z)+5,ry=180,kind='enemy',template=T[ep],script=SCRIPT+'enemy.lua',**{'eleprof.strength':110 if group<5 else 140,'eleprof.hasweapon_s':r'enhanced\MK18' if j%3 else r'enhanced\AR','eleprof.quantity':30,'eleprof.damage':8,'eleprof.accuracy':130,'eleprof.weapondamagemultiplier':0.32,'eleprof.conerange':1300,'eleprof.isimmobile':0})
# Lighting follows fixture locations, no invisible blanket of overlapping probes.
lightp=r'_markers\White Light.fpe';lighttemplate=T[lightp]
light_locations=[(-1750,-7000,500,0xE7BB80,720),(-850,-2920,600,0x67D8EA,850),(850,-2920,600,0x67D8EA,850),(-1700,-1200,600,0xFFAC65,950),(-1700,-50,600,0xFFAC65,950),(1100,200,600,0xAACEDD,650),(1600,1150,600,0xAACEDD,650),(-900,2800,600,0x70C7DC,1000),(900,3400,600,0x70C7DC,1000),(0,-2350,600,0x67D8EA,1000)]
for z in (-8100,-6100,-3800):light_locations.append((750,z,ground(750,z),0xDBB890,500))
for z in (-1800,-450,950,2350):light_locations.append((-2400,z,600,0xE0B16D,700))
for idx,(x,z,y,color,radius) in enumerate(light_locations,1):
 add(LAMP,'Working lamp / '+str(idx),x,z,y=y)
 add(lightp,'FL LIGHT '+str(idx),x,z,y=y+305,kind='light',template=lighttemplate,script=r'markers\ConstantLight.lua',**{'eleprof.light.color':color,'eleprof.light.range':radius,'eleprof.light.index':idx,'eleprof.light.fLightHasProbe':0})
# Preserve the player's three supplied score cues through the proven adaptive controller.
add(ct,'FIRST LIGHT // SCORE',50,-9500,y=100,kind='controller',script=r'aegis_reach\aegis_music.lua',**{'eleprof.soundset_s':r'aegis_reach\music\salt_moon_drift.wav','eleprof.soundset1_s':r'aegis_reach\music\moon_outpost_drift.wav','eleprof.soundset2_s':r'aegis_reach\music\orbital_catacomb.wav'})
# Native model signs communicate purpose and tell the evacuation story at human scale.
font=r'C:\Windows\Fonts\consolab.ttf'
def sign(name,lines,x,z,y,ry=0,color=(105,218,233)):
 im=Image.new('RGB',(1024,256),(15,27,36));d=ImageDraw.Draw(im)
 d.rectangle((4,4,1019,251),outline=color,width=8)
 for i,line in enumerate(lines):d.text((38,28+i*64),line,font=ImageFont.truetype(font,46 if i==0 else 31),fill=color if i==0 else (210,220,217))
 tex=name+'.png';im.save(AS/tex)
 m=Mesh();m.box(0,0,0,440,110,8,0)
 # Whole-texture mapping on every face; no atlas segmentation for readable signage.
 m.uv=[(u*8,v) for u,v in m.uv]
 path=own(name,m,tex)
 add(path,'Environmental sign: '+lines[0],x,z,y=y,ry=ry,kind='sign')
sign('Evacuation Board',['MERIDIAN SURVEY','EVACUATED: 42 / EXPECTED: 43','M. SEN - SUBSURFACE TEAM'], -1800,-6780,560)
sign('Checkpoint Sign',['AEGIS // GATE 07','CIVILIAN EVACUATION SUSPENDED','ALL PERSONNEL RETURN INSIDE'],0,-3000,950)
sign('Power Sign',['NORTHSTAR','GRID ISOLATED / MANUAL RESTART','SERVICE ACCESS ON WEST SIDE'],-1250,-1510,780)
sign('Operations Sign',['OPERATIONS','MERIDIAN PERSONNEL ARCHIVE','WARDEN OVERRIDE IN FORCE'],850,-365,790)
sign('Core Sign',['AEGIS ARRAY','TARGET: MERIDIAN SHELTER 12','FIRING AUTHORITY: IRON WARDEN'],0,3790,850)
sign('Extraction Sign',['KESTREL // LZ 07','KEEP THE LANDING ZONE CLEAR','PILOT WILL SIGNAL APPROACH'],0,-2880,670)

with zipfile.ZipFile(SOURCE) as z:
 z.setpassword(PASSWORD);payload={i.filename:z.read(i.filename) for i in z.infolist()}
version,_=read_ele(payload['map.ele']);payload['map.ele']=write_ele(version,entities);payload['map.ent']=write_bank(bank);payload['map.way']=struct.pack('<ii',0,0);payload['locked.cfg']=struct.pack('<i',0)
# True editable MAX terrain; preserve settings and replace the bounded authored region.
settings=terrain_settings(payload);sculpt=bytearray(payload[SCULPT_NAME]);ed=settings['editable_size']
for gz in range(world_to_grid(-12500,ed),world_to_grid(7500,ed)+1):
 z=grid_to_world(gz,ed)
 for gx in range(world_to_grid(-10000,ed),world_to_grid(10000,ed)+1):
  x=grid_to_world(gx,ed);idx=sculpt_index(gx,gz);sculpt[idx]=1
  struct.pack_into('<f',sculpt,TYPE_BYTES+idx*4,normalized_height(ground(x,z),settings))
payload[SCULPT_NAME]=bytes(sculpt)
visual,_=patch_visuals(payload['visuals.ini']);visual=visual.decode('latin1')
for key,val in {'AmbientMusicTrack':'','AmbientMusicTrackVolume':0,'FogNearest#':9500,'FogDistance#':31000,'Exposure':1.22,'SunIntensity':1.15,'BloomStrength':0.15}.items():visual=patch_setting(visual,key,val)
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
(DESIGN/'build-report.json').write_text(json.dumps({'map':MAP.name,'entities':len(entities),'enemy_count':sum(len(x) for x in groups.values()),'lights':len(light_locations),'assets':bank,'staged_dependencies':sorted(staged),'objectives':objectives,'native_terrain':True},indent=2))
print('FIRST LIGHT:',len(entities),'entities,',len(bank),'asset types,',len(light_locations),'lights')
