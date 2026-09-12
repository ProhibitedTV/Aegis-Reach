"""Vesper native terrain and authored First Light landmark composition.

World coordinates are GameGuru MAX inches. Native terrain owns every grounded
walking surface. Installed MAX modular kits provide ordinary human architecture.
Bespoke meshes are reserved for a handful of silhouettes and the Choir.
"""
import math
from native_terrain_pass import gauss, rect_mask, smoothstep

# The opening is a playable approach, with the lab just left of the court.
INSERTION=(-900,-8200)
INSERTION_LOOK_AT=(-2060,-7250)
INSERTION_YAW=math.degrees(math.atan2(INSERTION_LOOK_AT[0]-INSERTION[0],INSERTION_LOOK_AT[1]-INSERTION[1]))%360
CAMP_MAST=(-2145,-6960)
CAMP_POWER=(-2150,-7550)
CAMP_POWER_YAW=175
CAMP_POWER_SCALE=86
# Installed generator lamp array, measured in its DBO local coordinates.
_power_angle=math.radians(CAMP_POWER_YAW)
CAMP_POWER_LIGHT=(CAMP_POWER[0]-31.5*math.cos(_power_angle)*CAMP_POWER_SCALE/100,
                  CAMP_POWER[1]+31.5*math.sin(_power_angle)*CAMP_POWER_SCALE/100)
CAMP_POWER_LIGHT_HEIGHT=148*CAMP_POWER_SCALE/100

ROUTE=[
 (0,-9600,1080),(-700,-8350,810),(-1700,-7350,500),(-1450,-6400,310),
 (0,-5150,120),(300,-4150,290),(0,-3100,640),(0,-2350,650),
 (-1250,-1750,900),(-1300,-850,900),(-650,-520,900),(-250,-520,930),
 (250,-250,1000),(850,-260,1080),(1300,1050,1080),(2100,1250,1080),
 (2470,1250,1080),(2470,1750,1170),(0,1900,1380),(0,2200,1540),
 (0,2850,1540),(0,3200,1540)
]
RETURN=[
 (-900,3020,1540),(-1500,3020,1520),(-2250,2100,1280),(-2900,1000,1010),
 (-2900,-350,900),(-2550,-1600,700),(-1100,-2300,650)
]
WATER_LEVEL=65
BRINE_POOLS=((650,-5590,240,180),(930,-5380,240,145))

PADS=[
 (-1905,-7250,615,410,500),
 (0,-3100,900,620,640),
 (-1450,-650,1080,1120,900),
 (1250,700,1120,1020,1080),
 (0,3090,1480,980,1540),
 (0,-2350,1150,500,650),
]

def road_sample(x,z,points):
 best=(1e9,0)
 for a,b in zip(points,points[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1]
  t=max(0,min(1,((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz)))
  dist=math.hypot(x-a[0]-t*dx,z-a[1]-t*dz)
  if dist<best[0]:best=(dist,a[2]+(b[2]-a[2])*t)
 return best

def ground(x,z):
 h=145+35*math.sin(x/1200)*math.cos(z/1000)
 h+=1080*gauss(x,z,-1400,-10000,4100,1350)
 h+=1980*gauss(x,z,-4650,-4900,1350,2600)
 h+=1450*gauss(x,z,4900,-6800,1850,2050)
 h+=2200*gauss(x,z,4300,-800,1500,2700)
 h+=1050*gauss(x,z,-4900,2100,1600,2700)
 h+=1950*gauss(x,z,0,3900,3450,2850)
 h+=1750*gauss(x,z,0,7400,2100,1000)
 h+=40*math.sin(x/270+z/590)*math.sin(z/390)
 h+=230*gauss(x,z,-2700,-7350,1050,1500)
 h+=170*gauss(x,z,-1650,-8250,1650,720)
 h+=120*gauss(x,z,-650,-7600,700,1150)
 # Authored shelf shoulders: protect the route centre and all combat pads.
 # Relief stops before the first encounter; these are low banks, never cave walls.
 focus=(1-smoothstep(-6500,-5950,z))*rect_mask(x,z,-750,-8050,2500,1850,600)
 if focus>0:
  h+=focus*(190*gauss(x,z,-2750,-7330,390,820)
            +135*gauss(x,z,-2270,-6660,600,260)
            +95*gauss(x,z,-2200,-7860,530,270)
            +150*gauss(x,z,-930,-9100,420,580)
            +120*gauss(x,z,520,-8650,310,740))
  # The opening MAX frame hid the lab behind the inner descent shoulder.
  # A broad shallow cut opens the facade sightline; road grade is restored below.
  h-=focus*240*gauss(x,z,-1160,-8370,410,630)
  distance,_=road_sample(x,z,ROUTE)
  shoulder=smoothstep(190,420,distance)
  h+=focus*shoulder*(13*math.sin((x+z*.32)/105)+7*math.sin((z-x*.22)/53))
 for route,width in ((ROUTE,390),(RETURN,300)):
  feather=470
  if route is ROUTE and z<-6000:
   transition=smoothstep(-6500,-6000,z)
   width=170+220*transition;feather=260+210*transition
  distance,y=road_sample(x,z,route)
  blend=1-smoothstep(width,width+feather,distance)
  h=h*(1-blend)+y*blend
 for cx,cz,hx,hz,y in PADS:
  blend=rect_mask(x,z,cx,cz,hx,hz,280)
  h=h*(1-blend)+y*blend
 # The September 10 native frame exposed a ~20m bank immediately behind the
 # lab. Cut it back into a shallow sheltered bench; the flat court stays intact.
 shelter=rect_mask(x,z,-2780,-7270,360,460,450)*(1-smoothstep(-2520,-2380,x))
 if shelter>0:
  bench=500+.42*max(0,-x-2490)+.10*max(0,abs(z+7270)-360)
  h-=max(0,h-bench)*shelter
 pit=1-smoothstep(650,1450,math.hypot(x*.92,(z-5500)*1.10))
 h=h*(1-pit)+180*pit
 # Shallow residual brine beside the lower road, never across it.
 distance,_=road_sample(x,z,ROUTE)
 for px,pz,rx,rz in BRINE_POOLS:
  r=math.hypot((x-px)/rx,(z-pz)/rz)
  blend=(1-smoothstep(.25,1.65,r))*smoothstep(350,450,distance)
  h-=max(0,h-35)*blend
 # Wheel ruts are shallow native relief; preserve camp/combat pad heights.
 if -7800<z<-3650 and not any(abs(x-px)<hx+20 and abs(z-pz)<hz+20 for px,pz,hx,hz,_ in PADS):
  h-=3*(1-smoothstep(12,27,abs(distance-62)))
 return h

TERRAIN_MATERIALS={
 'baseLayerMaterial':256|22,
 'layerStartHeight0':-40,'layerEndHeight0':180,'layerMatIndex0':256|22,
 'layerStartHeight1':660,'layerEndHeight1':960,'layerMatIndex1':256|18,
 'layerStartHeight2':1650,'layerEndHeight2':2300,'layerMatIndex2':256|18,
 'layerStartHeight3':12000,'layerEndHeight3':13000,'layerMatIndex3':256|22,
 'layerStartHeight4':15000,'layerEndHeight4':16000,'layerMatIndex4':256|22,
 'slopeStart0':.24,'slopeEnd0':.58,'slopeMatIndex0':256|18,
 'slopeStart1':.80,'slopeEnd1':.98,'slopeMatIndex1':256|18,
 'reflectance':.02,'bumpiness':.55,
}


def service_material(x,z):
 """Native paint IDs are one-based; zero leaves MAX height/slope materials.

 MAX GGTerrain_GetMaterialIndex uses ordinary Z rows for paint, unlike sculpt.
 Only the insertion-to-Gate service route and Camp 12 court are painted.
 """
 for px,pz,rx,rz in BRINE_POOLS:
  if math.hypot((x-px)/rx,(z-pz)/rz)<1.10:return 19
 if not(-9800<=z<=-3050 and -3500<=x<=1500):return 0
 distance,_=road_sample(x,z,ROUTE[:7])
 edge=132+14*math.sin(z/83)+8*math.sin(z/31)
 court=rect_mask(x,z,-1910,-7250,595,400,70)
 if distance<edge:
  return 16 if abs(distance-62)<23 else 23  # wheel bands continue through the open court
 if court>.5:return 23  # installed mineral fines; no white/snow material
 return 0

def architecture(Mesh,own,add,prop,P,I,asset_dir):
 """Compose First Light with one clear visual owner per space."""
 def beam(m,x,y,z,w,h,d,c=1):m.box(x,y,z,w,h,d,c)

 C='Booster Pack\\Construction Pack\\'
 CYB='Cyberpunk Streets Booster Pack\\Buildings\\'
 CYM='Cyberpunk Streets Booster Pack\\Misc\\Sidewalk Misc\\'
 CYS='Cyberpunk Streets Booster Pack\\Streets and Sidewalks\\Sidewalks\\'

 # One original transportable field lab; installed equipment remains restrained.
 from meridian_fieldkit import build as build_fieldkit
 lab,mast=build_fieldkit(Mesh,own,asset_dir)
 camp_y=500
 add(lab,'Camp 12 / Meridian field lab',-2350,-7270,y=camp_y,ry=270)
 prop(P+'Desk 01a.fpe',-2390,-7130,y=camp_y+0.4,ry=0,scale=100)
 prop(P+'Desk Chair 01a.fpe',-2315,-7160,y=camp_y,ry=90,scale=100)
 add(mast,'Camp 12 / Meridian survey mast',*CAMP_MAST,y=camp_y,ry=270)
 prop(C+'Light Generator.fpe',*CAMP_POWER,y=camp_y,ry=CAMP_POWER_YAW,scale=CAMP_POWER_SCALE)
 prop(C+'CableReel.fpe',-2010,-7570,y=camp_y,ry=90,scale=64)
 prop(C+'Freight Container.fpe',-1825,-7000,y=camp_y,ry=90,scale=68)
 prop(P+'Wooden Crate 01a.fpe',-1735,-7120,y=camp_y,ry=0,scale=68)
 prop(C+'SurveyorStand1.fpe',-1950,-6875,y=camp_y,ry=18,scale=102)
 prop(C+'SurveyorStand2.fpe',-2040,-6875,y=camp_y,ry=-20,scale=102)
 # Two waist-high edge markers, never a perimeter wall. The installed barrier
 # origin is at one end (local X=-127.63..0.77), not at its visual centre.
 for x,z in ((-1430,-7357),(-1500,-6999)):
  prop(P+'Concrete Barrier 01.fpe',x,z,y=camp_y,ry=90,scale=92)

 gate_y=640
 prop(CYB+'CS_Building_Entrance_Overpass.fpe',0,-3160,y=gate_y,ry=0,scale=72)
 prop(CYB+'CS_Building_Entrance_Overpass_Support.fpe',-610,-3160,y=gate_y,ry=0,scale=72)
 prop(CYB+'CS_Building_Entrance_Overpass_Support.fpe',610,-3160,y=gate_y,ry=180,scale=72)
 prop(CYB+'CS_Building_Entrance_Overpass_Wall.fpe',-800,-3110,y=gate_y,ry=90,scale=65)
 prop(CYB+'CS_Building_Entrance_Overpass_Wall.fpe',800,-3110,y=gate_y,ry=-90,scale=65)
 prop(CYB+'CS_Building_Entrance_Steps.fpe',0,-3470,y=ground(0,-3470),ry=0,scale=72)
 prop(C+'Roadblock2.fpe',-430,-3540,y=ground(-430,-3540),ry=8,scale=90)
 prop(C+'Roadblock3.fpe',430,-3540,y=ground(430,-3540),ry=-8,scale=90)
 prop(C+'Light Generator.fpe',850,-2860,y=ground(850,-2860),ry=90,scale=82)
 prop(P+'Concrete Barrier 01.fpe',-690,-3470,y=ground(-690,-3470),ry=15,scale=92)
 prop(P+'Container 02a.fpe',1030,-3000,y=ground(1030,-3000),ry=90,scale=86)

 m=Mesh()
 for x in (-430,430):
  beam(m,x,0,0,125,930,125,2)
  beam(m,x,850,0,175,70,175,5)
 beam(m,0,700,0,900,40,90,2)
 stacks=own('Northstar Stack Pair',m)
 add(stacks,'Northstar / stack pair',-1510,-540,y=900)
 prop(CYB+'CS_Building_Entrance_Overpass_02.fpe',-1420,-760,y=900,ry=90,scale=64)
 prop(CYB+'CS_Building_Entrance_Overpass_Support.fpe',-1420,-1230,y=900,ry=90,scale=64)
 prop(CYB+'CS_Building_Entrance_Overpass_Support.fpe',-1420,-280,y=900,ry=-90,scale=64)
 for z in (-1120,-250):
  prop(P+'Generator 04a.fpe',-1700,z,y=902,ry=90,scale=92)
  prop(I+'Storage Tank - Small.fpe',-2180,z,y=902,ry=0,scale=95)
 prop(I+'Industrial Stairs.fpe',-2150,-840,y=900,ry=90,scale=92)
 prop(I+'Industrial Shelves.fpe',-2110,-50,y=900,ry=90,scale=86)
 for x,z in [(-1320,-80),(-1080,-80)]:
  prop(I+'Control Box - Large.fpe',x,z,y=902,ry=180,scale=92)
 prop(C+'CableReel.fpe',-1950,250,y=ground(-1950,250),ry=25,scale=86)

 op_y=1080
 prop(CYB+'CS_Wall_01_Entry_01.fpe',720,-230,y=op_y,ry=0,scale=62)
 prop(CYB+'CS_Wall_01_Window.fpe',1260,-230,y=op_y,ry=0,scale=62)
 prop(CYB+'CS_Wall_01.fpe',1800,-230,y=op_y,ry=0,scale=62)
 prop(CYB+'CS_Wall_01.fpe',2110,280,y=op_y,ry=90,scale=62)
 prop(CYB+'CS_Wall_01_Entry_03.fpe',2110,820,y=op_y,ry=90,scale=62)
 prop(CYB+'CS_Wall_01.fpe',2110,1360,y=op_y,ry=90,scale=62)
 prop(CYB+'CS_Wall_01_Overhang.fpe',1180,-70,y=op_y+6,ry=0,scale=62)
 prop(CYB+'CS_Roof_Tile_4x4.fpe',1450,580,y=op_y+260,ry=0,scale=60)
 prop(CYM+'CS_Sidewalk_Light.fpe',540,-340,y=ground(540,-340),ry=0,scale=72)
 for x,z in [(900,300),(1280,600)]:
  prop(P+'Desk 01a.fpe',x,z,y=op_y+2,ry=90,scale=90)
  prop(P+'Computer 01a.fpe',x,z,y=op_y+77,ry=90,scale=90)
 for z in (300,560):
  prop(P+'Locker 01a.fpe',1900,z,y=op_y+2,ry=-90,scale=90)
 prop(I+'Industrial Shelves.fpe',1850,1100,y=op_y,ry=90,scale=82)
 prop(I+'Hand Trolly.fpe',1660,1180,y=op_y,ry=-20,scale=86)
 prop(P+'Portable Cot 01a.fpe',1350,1180,y=op_y+2,ry=90,scale=88)

 aegis_y=1540
 m=Mesh()
 for x in (-720,720):
  beam(m,x,0,0,100,900,100,2)
  beam(m,x,210,-65,18,520,18,5)
 beam(m,0,820,0,1540,95,150,2)
 frame=own('AEGIS Arrival Frame',m)
 add(frame,'AEGIS / arrival frame',0,3090,y=aegis_y)
 prop(CYB+'CS_Wall_01_Entry_02.fpe',0,2320,y=ground(0,2320),ry=0,scale=70)
 prop(CYB+'CS_Building_Entrance_Overpass_02.fpe',0,3260,y=aegis_y,ry=0,scale=62)
 prop(C+'Light Generator.fpe',-1060,3500,y=ground(-1060,3500),ry=45,scale=82)
 prop(C+'CableReel.fpe',-890,3560,y=ground(-890,3560),ry=20,scale=86)
 prop(C+'Rebar1.fpe',960,3500,y=ground(960,3500),ry=70,scale=82)
 for x in (-820,820):
  prop(I+'Control Box - Tall.fpe',x,3250,y=aegis_y+2,ry=180,scale=92)
 for x,z,ry in [(-980,2700,0),(930,2780,90)]:
  prop(P+'Concrete Barrier 01.fpe',x,z,y=ground(x,z),ry=ry,scale=92)

 m=Mesh();beam(m,0,0,0,10,105,10,2);beam(m,0,90,0,42,13,18,5)
 marker=own('Meridian Route Beacon',m)
 for i,(x,z,ry) in enumerate([
  (-1180,-6380,5),(-430,-5650,8),(280,-5000,0),(350,-4010,-8),(140,-3380,0)
 ],1):
  add(marker,'Meridian route marker '+str(i),x,z,y=ground(x,z),ry=ry)

 for i,(x,z,ry) in enumerate([
  (-320,-5660,0),(470,-4630,0),(-500,-3030,0)
 ],1):
  prop(CYM+'CS_Street_Electrical_Pole_01.fpe',x,z,y=ground(x,z),ry=ry,scale=68)
  if i in (2,3):
   prop(CYM+'CS_Street_Lamp.fpe',x+95,z+35,y=ground(x+95,z+35),ry=ry,scale=68)

 m=Mesh()
 for x,y,z,w,h,d,angle in [
  (-420,0,0,210,2850,310,-11),(490,0,180,260,3300,340,9),
  (20,2520,100,980,300,400,-8)
 ]:
  m.box(x,y,z,w,h,d,6,angle)
 for y in (390,430,500):m.box(-420,y,-160,205,9,9,7,-11)
 arch=own('Choir Breach Arch',m)
 add(arch,'Choir / buried arch exposed by the receded sea',0,5100,y=180,ry=16)

 m=Mesh();beam(m,0,-16,0,500,22,980,2)
 for x in (-245,245):
  beam(m,x,95,0,12,12,980,2)
  for z in (-460,0,460):beam(m,x,0,z,12,100,12,2)
 bridge=own('Excavation Service Bridge',m)
 add(bridge,'AEGIS / inspection bridge at the fracture',-940,4050,y=1540)
