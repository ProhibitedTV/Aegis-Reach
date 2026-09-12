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
from PIL import Image,ImageDraw,ImageFont,ImageFilter

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

from firstlight_world import ground,TERRAIN_MATERIALS,architecture,ROUTE,RETURN,service_material,INSERTION,INSERTION_YAW,CAMP_MAST,CAMP_POWER_LIGHT,CAMP_POWER_LIGHT_HEIGHT,WATER_LEVEL

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

# Original crystalline geology. The crystals deliberately use their own full UV space
# and procedural energy material instead of borrowing the general Aegis atlas.
def _mesh_tri(mesh,a,b,c):
 ux,uy,uz=b[0]-a[0],b[1]-a[1],b[2]-a[2]
 vx,vy,vz=c[0]-a[0],c[1]-a[1],c[2]-a[2]
 nx=uy*vz-uz*vy;ny=uz*vx-ux*vz;nz=ux*vy-uy*vx
 length=max(0.0001,math.sqrt(nx*nx+ny*ny+nz*nz));n=(nx/length,ny/length,nz/length)
 start=len(mesh.verts)
 for p,uv in zip((a,b,c),((.08,.96),(.92,.96),(.50,.04))):
  mesh.verts.append(p);mesh.norm.append(n);mesh.uv.append(uv)
 mesh.faces.append((start,start+1,start+2))

def _crystal_prism(mesh,x,z,r,h,angle=0,leanx=0,leanz=0):
 sides=5;lower=[];upper=[]
 for i in range(sides):
  a=math.radians(angle+i*360/sides)
  lower.append((x+math.cos(a)*r,0,z+math.sin(a)*r))
  upper.append((x+leanx+math.cos(a)*r*.82,h*.72,z+leanz+math.sin(a)*r*.82))
 tip=(x+leanx*1.45,h,z+leanz*1.45)
 for i in range(sides):
  j=(i+1)%sides
  _mesh_tri(mesh,lower[i],lower[j],upper[j])
  _mesh_tri(mesh,lower[i],upper[j],upper[i])
  _mesh_tri(mesh,upper[i],upper[j],tip)

def _build_energy_texture(filename,resonant=False):
 size=1024
 image=Image.new('RGB',(size,size));px=image.load()
 for y in range(size):
  v=y/(size-1)
  for x in range(size):
   u=x/(size-1)
   center=math.exp(-((u-.50)/.24)**2)
   edge=math.exp(-((min(u,1-u))/.055)**2)
   weave=.5+.5*math.sin(u*31+v*17+1.3*math.sin(v*11))
   cross=.5+.5*math.sin(u*13-v*29+1.1*math.sin(u*9))
   vein=math.exp(-(math.sin(u*20+v*13+1.4*math.sin(v*7))/.14)**2)
   pulse=.5+.5*math.sin(v*52+u*8+2*math.sin(v*8))
   if resonant:
    violet=.70+.30*cross;cyan=.20+.25*weave
    white=min(1,vein*.92+edge*.42+pulse*.10)
    r=12+125*center*violet+215*white
    g=8+48*center+105*cyan+220*white
    b=42+185*center+65*weave+210*white
   else:
    cyan=.60+.40*weave;violet=.20+.36*cross
    white=min(1,vein*.82+edge*.34+pulse*.08)
    r=7+62*center*violet+220*white
    g=14+128*center*cyan+210*white
    b=48+180*center+52*cross+205*white
   px[x,y]=(max(0,min(255,int(r))),max(0,min(255,int(g))),max(0,min(255,int(b))))

 glow=Image.new('RGBA',(size,size),(0,0,0,0));draw=ImageDraw.Draw(glow)
 for i in range(11):
  base=int(size*(.08+i*.082));points=[]
  for y in range(0,size+24,24):
   x=base+int(math.sin(y*.018+i*.91)*24+math.sin(y*.051+i)*9)
   points.append((x,y))
  color=(205,185,255,75) if resonant else (165,225,255,68)
  draw.line(points,fill=color,width=4+(i%3)*2)
 glow=glow.filter(ImageFilter.GaussianBlur(7))
 image=Image.alpha_composite(image.convert('RGBA'),glow)

 sharp=ImageDraw.Draw(image)
 for i in range(6):
  base=int(size*(.16+i*.135));points=[]
  for y in range(-20,size+20,34):
   x=base+int(math.sin(y*.026+i*1.7)*14)
   points.append((x,y))
  sharp.line(points,fill=(240,244,255,115),width=2)
 path=AS/filename
 image.convert('RGB').save(path,optimize=True)
 return filename

def _build_brineglass(name,texture):
 m=Mesh()
 specs=[
  (-40,-15,34,245,-8,-14,8),(18,20,27,190,12,8,-5),(58,-20,20,145,-18,10,4),
  (-72,42,19,130,25,-5,9),(12,-58,15,105,4,3,5),(78,48,12,82,-30,-2,4)
 ]
 for x,z,r,h,angle,lx,lz in specs:_crystal_prism(m,x,z,r,h,angle,lx,lz)
 path=own(name,m,texture=texture,collision=0)
 f=AS/(name+'.fpe')
 text=f.read_text().replace('roughnessStrength = 0.82','roughnessStrength = 0.38').replace('metalnessStrength = 0.22','metalnessStrength = 0.05')
 f.write_text(text+'reflectance = 0.18\nbasecolor = 4294967295\nemissivecolor = 4294967295\nemissiveMap = '+texture+'\nemissiveStrength = 0.10\n')
 return path

# One authoring layer owns all human-built spaces.
architecture(Mesh,own,add,prop,P,I,AS)

# Sparse geology: terrain carries the landscape; rocks only break long silhouettes.
ROCK=r'Max Collection\Rocks\Rock Boulder.fpe'
for x,z,sz in [(-700,-8640,110),(940,-7690,120),(-850,-5700,140),(650,-4970,120),(-490,-4390,100),(1040,-3840,120)]:
 add(ROCK,'Basalt remnant / tide channel cover',x,z,scale=sz,ry=x%180)

BRINE_TEX=_build_energy_texture('vesper_brineglass_energy.png',False)
RESONANT_TEX=_build_energy_texture('vesper_brineglass_resonant.png',True)
BRINEGLASS=_build_brineglass('Vesper Brineglass Bloom',BRINE_TEX)
RESONANT=_build_brineglass('Vesper Resonant Brineglass Bloom',RESONANT_TEX)
crystal_sites=[
 (-1180,-8030,15,16,0x365F69,65,False),(-1550,-7840,-20,22,0x6DB9C4,90,False),
 (-1490,-6120,30,34,0x65C8D8,210,False),(-1020,-5620,-15,44,0x59BDCC,240,False),
 (710,-4100,40,52,0x52C1D2,270,False),(-2650,-250,0,88,0x59D4E2,380,False),
 (2450,1850,65,96,0x62D8E5,420,False),(-1650,3750,-25,110,0x748CE8,460,True),
 (1250,4450,20,125,0x8B75E8,520,True),(350,5150,-35,138,0x9670EC,560,True),
 (450,-5570,30,27,0x579AAA,150,False),(1110,-5230,-25,35,0x5899B1,170,False)
]
for idx,(x,z,ry,scale,color,radius,resonant) in enumerate(crystal_sites,1):
 asset=RESONANT if resonant else BRINEGLASS
 prefix='Resonant Brineglass bloom' if resonant else 'Brineglass bloom'
 add(asset,prefix+' %02d'%idx,x,z,y=ground(x,z)-(8+scale*.16),ry=ry,scale=scale,kind='geology',
     **{'rx':-5 if idx%2 else 4,'rz':3 if idx%2 else -4,
        'scaley':scale*(.70 if idx<=2 else 1)-100})

# Warden occupation is a thin retrofit layer, not a second architecture system.
for x,z,angle in [(-720,-2660,0),(700,-2200,30),(1560,-1990,90)]:
 prop(P+'Concrete Barrier 01.fpe',x,z,ry=angle,scale=92)
for x,z in [(1630,-2500),(1910,-2500)]:
 prop(P+'Container 01a.fpe',x,z,ry=90,scale=82)
for x,z,ry in [(-720,-2140,0),(570,-1710,15),(-960,-560,90),(-750,2520,0),(650,2670,90)]:
 prop(P+'Hesco Barrier 01.fpe',x,z,ry=ry,scale=88)

for x,z in [(-3200,-1100),(-3250,220),(-3260,1530)]:
 prop(P+'Container 02a.fpe',x,z,ry=0,scale=90)
for x,z in [(-2810,1110),(-2690,1250)]:
 prop(P+'Gas Barrel 01a.fpe',x,z,scale=90)

weapon='Max Collection\\Weapons\\'
for x,z in [(-1570,-6800),(-2050,-2200),(-1150,100),(1550,1250),(-850,3100),(300,-2200)]:
 path=weapon+'Compact Assault Rifle Ammo.fpe'
 add(path,'Supply: rifle ammunition',x,z,y=ground(x,z)+28,kind='ammo',template=T[path],script='ammo.lua',
     **{'eleprof.quantity':120,'eleprof.hasweapon_s':r'enhanced\MK18'})

SCRIPT=r'aegis_reach\firstlight_'
START=INSERTION
p=r'_markers\Player Start.fpe'
add(p,'SEVEN // Meridian insertion',*START,y=ground(*START)+60,ry=INSERTION_YAW,kind='player',template=T[p],
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

lightp=r'_markers\White Light.fpe';lighttemplate=T[lightp]
light_locations=[
 (-2350,-7260,0xE6C49A,250),(*CAMP_MAST,0xBDA27D,330),(-2195,-7200,0xE8C49A,240),
 (-430,-5600,0xCFA875,430),(280,-5000,0xCFA875,450),(320,-4050,0xCFA875,460),
 (-520,-3100,0x67D8EA,760),(520,-3100,0x67D8EA,760),
 (-1700,-1120,0xF0A35E,820),(-1700,-180,0xF0A35E,820),
 (980,120,0xC2D7DF,560),(1530,1080,0xC2D7DF,580),
 (-760,2800,0x70C7DC,900),(760,3380,0x70C7DC,900),
 (-750,-2200,0x67D8EA,850),(-2400,950,0xD6A96A,620)
]
# One warm pool from the existing generator lamp array joins the court to the lab.
light_locations.append((*CAMP_POWER_LIGHT,0xC3AA86,420))
camp_work_light_index=len(light_locations)
for idx,(x,z,color,radius) in enumerate(light_locations,1):
 # Fixture geometry owns camp lamp height; the stock marker adds 45 inches.
 fixture={'eleprof.light.offsetup':0} if idx<=3 or idx==camp_work_light_index else {}
 add(lightp,'FL LIGHT '+str(idx),x,z,y=ground(x,z)+({1:127,2:210,3:109,camp_work_light_index:CAMP_POWER_LIGHT_HEIGHT}.get(idx,155)),kind='light',template=lighttemplate,
     script=r'markers\ConstantLight.lua',
     **{'eleprof.light.color':color,'eleprof.light.range':radius,'eleprof.light.index':idx,'eleprof.light.fLightHasProbe':0,**fixture})
crystal_light_base=len(light_locations)
for offset,(x,z,ry,scale,color,radius,resonant) in enumerate(crystal_sites,1):
 idx=crystal_light_base+offset
 fixture={'eleprof.light.offsetup':0} if offset<=2 else {}
 if offset<=5:color=sum(int(((color>>shift)&255)*.35)<<shift for shift in (0,8,16))
 add(lightp,'FL BRINEGLASS LIGHT '+str(offset),x,z,y=ground(x,z)+max(18,scale*.65),kind='light',template=lighttemplate,
     script=r'markers\ConstantLight.lua',
     **{'eleprof.light.color':color,'eleprof.light.range':radius,'eleprof.light.index':idx,'eleprof.light.fLightHasProbe':0,**fixture})

add(ct,'FIRST LIGHT // SCORE',50,-9500,y=100,kind='controller',script=r'aegis_reach\firstlight_score.lua',
    **{'eleprof.soundset_s':r'aegis_reach\music\salt_moon_drift.wav',
       'eleprof.soundset1_s':r'aegis_reach\music\moon_outpost_drift.wav',
       'eleprof.soundset2_s':r'aegis_reach\music\orbital_catacomb.wav'})

font=r'C:\Windows\Fonts\consolab.ttf'
def sign(name,lines,x,z,y,ry=0,color=(105,218,233)):
 camp_panel=name=='Evacuation Board'
 if camp_panel:
  # A painted wall panel, with the same 2.4:1 aspect in texture and geometry.
  # Full-face UVs below preserve leading text; the generic atlas margins cropped it.
  im=Image.new('RGB',(768,320),(168,174,167));d=ImageDraw.Draw(im)
  d.rectangle((15,15,752,304),outline=(69,88,89),width=3)
  d.rectangle((34,32,733,43),fill=(48,101,107))
  for i,line in enumerate(lines):
   f=ImageFont.truetype(font,38 if i==0 else 31)
   assert d.textbbox((0,0),line,font=f)[2]<690, 'Camp panel text exceeds safe width'
   d.text((38,58+i*76),line,font=f,fill=(25,54,60) if i==0 else (33,44,46))
  for rivet_x in (24,743):
   for yy in (24,295):d.ellipse((rivet_x-3,yy-3,rivet_x+3,yy+3),fill=(64,75,76))
 else:
  # Readable painted field signage, not a dark emissive billboard.
  im=Image.new('RGB',(1008,384),(174,181,175));d=ImageDraw.Draw(im)
  d.rectangle((10,10,997,373),outline=(38,66,70),width=9)
  d.rectangle((32,31,975,43),fill=(42,105,115))
  for i,line in enumerate(lines):
   size=52 if i==0 else 37
   f=ImageFont.truetype(font,size)
   while d.textbbox((0,0),line,font=f)[2]>910:
    size-=1;f=ImageFont.truetype(font,size)
   assert size>=30, 'Field sign text exceeds readable width'
   d.text((47,68+i*98),line,font=f,fill=(24,54,59) if i==0 else (32,45,48))
  for rivet_x in (25,982):
   for yy in (25,358):d.ellipse((rivet_x-4,yy-4,rivet_x+4,yy+4),fill=(60,73,75))
 tex=name+'.png';im.save(AS/tex)
 panel_y=ground(x,z)+(y-(500 if z<-5000 else 600)) if camp_panel else ground(x,z)+84
 width,height,depth=(60,25,2) if camp_panel else (168,64,4)
 m=Mesh();m.box(0,0,0,width,height,depth,0)
 face_uv=[((u*8-.07)/.86,(v-.07)/.86) for u,v in m.uv]
 # Front uses the whole image; unprinted edges/back cannot repeat cropped text.
 m.uv=[uv if i<4 else ((.47+uv[0]*.01,.91+uv[1]*.01) if camp_panel else (.50,.96)) for i,uv in enumerate(face_uv)]
 if not camp_panel:
  support=Mesh();angle=math.radians(ry)
  for px in (-66,66):
   pz=6
   wx=x+px*math.cos(angle)+pz*math.sin(angle)
   wz=z+pz*math.cos(angle)-px*math.sin(angle)
   footing=ground(wx,wz)-panel_y
   support.box(px,footing,pz,8,height-6-footing,8,2)
   support.box(px,footing,pz,14,3,14,2)
  if name=='Extraction Sign':
   # Keep the existing frame entity; its posts sit entirely behind the board.
   for i,(vx,vy,vz) in enumerate(support.verts):support.verts[i]=(vx,vy+84,vz)
   post=own(name+' Supports',support)
   add(post,'Meridian field board frame',x,z,ry=ry)
  else:
   offset=len(m.verts)
   m.verts.extend(support.verts);m.norm.extend(support.norm)
   # Sample the printed dark border for the graphite support finish.
   m.uv.extend([(.015,.50)]*len(support.uv))
   m.faces.extend(tuple(v+offset for v in f) for f in support.faces)
 path=own(name,m,tex)
 f=AS/(name+'.fpe');t=f.read_text()
 t=t.replace('metalnessStrength = 0.22','metalnessStrength = 0.0')
 f.write_text(t+'basecolor = 4294967295\nreflectance = 0.04\n')
 add(path,'Environmental sign: '+lines[0],x,z,y=panel_y,ry=ry,scale=100,kind='sign')

sign('Evacuation Board',['MERIDIAN / CAMP 12','EVACUATED: 42 / EXPECTED: 43','M. SEN - SUBSURFACE TEAM'],-2219,-7104,548,ry=270)
sign('Checkpoint Sign',['AEGIS // GATE 07','CIVILIAN EVACUATION SUSPENDED','ALL PERSONNEL RETURN INSIDE'],0,-3445,985)
sign('Power Sign',['NORTHSTAR','GRID ISOLATED / MANUAL RESTART','SERVICE ACCESS ON WEST SIDE'],-980,-1450,915)
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
terrain_json=json.loads(raw_terrain[start:end]);terrain_json.update(TERRAIN_MATERIALS);terrain_json['water_height']=WATER_LEVEL
terrain_text=json.dumps(terrain_json,indent=2).encode()
payload['ggterrain.dat']=struct.pack('<I',len(terrain_text))+terrain_text
settings=terrain_settings(payload);sculpt=bytearray(payload[SCULPT_NAME]);ed=settings['editable_size']
paint=bytearray(payload['16777216.ptd']);painted_cells=0
for gz in range(world_to_grid(-14000,ed),world_to_grid(10000,ed)+1):
 z=grid_to_world(gz,ed)
 for gx in range(world_to_grid(-10000,ed),world_to_grid(10000,ed)+1):
  x=grid_to_world(gx,ed);idx=sculpt_index(gx,gz);sculpt[idx]=1
  struct.pack_into('<f',sculpt,TYPE_BYTES+idx*4,normalized_height(ground(x,z),settings))
  material=service_material(x,z)
  if material:
   paint[gz*4096+gx]=material;painted_cells+=1
payload[SCULPT_NAME]=bytes(sculpt)
payload['16777216.ptd']=bytes(paint)

visual,_=patch_visuals(payload['visuals.ini']);visual='\r\n'.join(line for line in visual.decode('latin1').splitlines() if line.startswith('visuals.'))+'\r\n'
# Native sun RGB uses 0..255 (MAX divides by 255); full color is DeSaturate=1.
# Keep the horizon subordinate to the shelf and practical lights.
atmosphere={'FogNearest#':6200,'FogDistance#':19500,'FogR#':48,'FogG#':62,'FogB#':80,'FogA#':0.45,
 'Exposure':0.84,'SunIntensity':1.45,'SunRed':218,'SunGreen':232,'SunBlue':255,
 'SunAngleX':18,'SunAngleY':315,'SunAngleZ':0,'Simulate24Hours':0,
 'AmbienceRed#':70,'AmbienceGeen#':84,'AmbienceBlue#':108,'EnvProbeBrightness':0.75,
 'sky$':'overcast','AutoExposure':0,'DeSaturate':1,'BloomStrength':0.08,'BloomThreshold':1.5,
 'LensFlare':0,'SkyCloudCoverage':0.5,'SkyCloudiness':0.45}
water={'WaterEnable':1,'Waterheight':WATER_LEVEL,'Waterred':13,'Watergreen':37,'Waterblue':43,
 'WaterWaveAmplitude':1.5,'WaterChoppyScale':0,'WaterWindDependency':0,'WaterSpeed1':.018,
 'WaterReflection':.3,'WaterSparkleCol':.25}
for key,val in {'AmbientMusicTrack':'','AmbientMusicTrackVolume':0,**atmosphere,**water}.items():
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
 'Choir':'bespoke buried nonhuman structure + increasingly active resonant brineglass',
}
(DESIGN/'layout.json').write_text(json.dumps(placements,indent=2))
(DESIGN/'build-report.json').write_text(json.dumps({
 'map':MAP.name,'entities':len(entities),'enemy_count':sum(len(x) for x in groups.values()),
 'lights':len(light_locations)+len(crystal_sites),'assets':bank,'staged_dependencies':sorted(staged),
 'objectives':objectives,'native_terrain':True,'service_road_painted_cells':painted_cells,'route':ROUTE,'return_route':RETURN,
 'terrain_materials':TERRAIN_MATERIALS,'scene_recipe':scene_recipe,'atmosphere':atmosphere,
 'crystal_clusters':len(crystal_sites),'brineglass_materials':[BRINE_TEX,RESONANT_TEX],
 'environment_pass':'single-owner-production-recomposition','environment_polish':'sheltered-shelf-and-grounded-brineglass'
},indent=2))
print('FIRST LIGHT:',len(entities),'entities,',len(bank),'asset types,',len(light_locations)+len(crystal_sites),'lights')
print('Vesper atmosphere: darker grade /',len(crystal_sites),'brineglass blooms / 2 energy materials')
print('Environment: single-owner production recomposition / no secondary Camp 12 dressing')