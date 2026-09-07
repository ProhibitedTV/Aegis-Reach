"""Vesper native terrain and authored First Light landmark composition.

World coordinates are GameGuru MAX inches. Native terrain owns every grounded
walking surface. Installed MAX modular kits provide most human architecture and
infrastructure; bespoke meshes are reserved for unique silhouettes and Choir forms.
The route must remain readable with the HUD disabled.
"""
import math
from native_terrain_pass import gauss, rect_mask, smoothstep

ROUTE=[
 (0,-9600,1080),(-700,-8350,810),(-1700,-7350,475),(-1450,-6400,330),
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
PADS=[
 (-1700,-7160,760,580,475),     # Camp 12 floor inside the sheltered bowl
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

 # Camp 12 sits in a weathered impact hollow cut into the old salt shelf. A
 # protective crescent of terrain wraps the west/north sides while the southeast
 # remains open as the engineered road toward Gate 07. MAX terrain cannot make a
 # true overhang, so installed cliff pieces finish the rock-cut recess in architecture().
 for cx,cz,amp,sx,sz in [
  (-2850,-7350,760,760,1120),(-1900,-8350,650,1080,620),
  (-760,-7900,520,820,880),(-2780,-6480,430,620,840)
 ]:
  h+=amp*gauss(x,z,cx,cz,sx,sz)
 h-=165*gauss(x,z,-1700,-7160,1180,900)
 h-=80*gauss(x,z,-1250,-6350,720,980)

 for route,width in ((ROUTE,360),(RETURN,300)):
  distance,y=road_sample(x,z,route)
  blend=1-smoothstep(width,width+470,distance)
  h=h*(1-blend)+y*blend
 for cx,cz,hx,hz,y in PADS:
  blend=rect_mask(x,z,cx,cz,hx,hz,280)
  h=h*(1-blend)+y*blend
 pit=1-smoothstep(650,1450,math.hypot(x*.92,(z-5500)*1.10))
 h=h*(1-pit)+180*pit
 return h

TERRAIN_MATERIALS={
 'baseLayerMaterial':256|13,
 'layerStartHeight0':190,'layerEndHeight0':380,'layerMatIndex0':256|3,
 'layerStartHeight1':650,'layerEndHeight1':960,'layerMatIndex1':256|14,
 'layerStartHeight2':1650,'layerEndHeight2':2300,'layerMatIndex2':256|22,
 'layerStartHeight3':12000,'layerEndHeight3':13000,'layerMatIndex3':256|22,
 'layerStartHeight4':15000,'layerEndHeight4':16000,'layerMatIndex4':256|22,
 'slopeStart0':.30,'slopeEnd0':.62,'slopeMatIndex0':256|18,
 'slopeStart1':.80,'slopeEnd1':.98,'slopeMatIndex1':256|17,
 'reflectance':.02,'bumpiness':.55,
}

def architecture(Mesh,own,add,prop,P,I):
 """Compose First Light from installed modular kits plus a few bespoke landmarks."""
 def beam(m,x,y,z,w,h,d,c=1):m.box(x,y,z,w,h,d,c)
 def endwall(m,z,left,right,opening,h=390,color=1):
  lo,hi=opening
  if lo>left:beam(m,(lo+left)/2,0,z,lo-left,h,45,color)
  if right>hi:beam(m,(right+hi)/2,0,z,right-hi,h,45,color)
  beam(m,(lo+hi)/2,280,z,hi-lo,h-280,45,color)
 def sidewall(m,x,near,far,opening,h=390,color=1):
  lo,hi=opening
  if lo>near:beam(m,x,0,(near+lo)/2,45,h,lo-near,color)
  if far>hi:beam(m,x,0,(hi+far)/2,45,h,far-hi,color)
  beam(m,x,280,(lo+hi)/2,45,h-280,hi-lo,color)

 C='Booster Pack\\Construction Pack\\'
 CAMP='Booster Pack\\Camping Pack\\'
 CYB='Cyberpunk Streets Booster Pack\\Buildings\\'
 CYM='Cyberpunk Streets Booster Pack\\Misc\\Sidewalk Misc\\'
 CYF='Cyberpunk Streets Booster Pack\\Store Fronts\\'
 CYS='Cyberpunk Streets Booster Pack\\Streets and Sidewalks\\Sidewalks\\'
 ARC='Arctic Collection\\Cliffs\\'
 ARR='Arctic Collection\\Rocks\\'

 # GATE 07 — unique massing plus real sci-fi facade/construction pieces.
 m=Mesh()
 for x in (-760,760):
  beam(m,x,0,0,250,780,980,2)
  beam(m,x,720,-120,310,70,760,5)
 beam(m,-425,0,40,190,620,860,1);beam(m,425,0,40,190,620,860,1)
 beam(m,0,570,-80,680,150,820,2)
 for z in (-360,330):beam(m,0,555,z,720,12,22,5)
 for x in (-585,585):beam(m,x,180,-360,18,420,18,5)
 gate=own('Gate 07 Cut Portal',m)
 add(gate,'Gate 07 / military sea-wall threshold',0,-3100,y=640)
 prop(CYB+'CS_Building_Entrance_Overpass.fpe',0,-3190,y=640,ry=0,scale=68)
 prop(CYB+'CS_Building_Entrance_Overpass_Support.fpe',-610,-3190,y=640,ry=0,scale=68)
 prop(CYB+'CS_Building_Entrance_Overpass_Support.fpe',610,-3190,y=640,ry=180,scale=68)
 prop(CYB+'CS_Building_Entrance_Steps.fpe',0,-3470,y=ground(0,-3470),ry=0,scale=72)
 prop(C+'Roadblock2.fpe',-430,-3540,y=ground(-430,-3540),ry=8,scale=90)
 prop(C+'Roadblock3.fpe',430,-3540,y=ground(430,-3540),ry=-8,scale=90)
 prop(C+'Light Generator.fpe',870,-2860,y=ground(870,-2860),ry=90,scale=85)
 prop(P+'Concrete Barrier 01.fpe',-690,-3470,y=ground(-690,-3470),ry=15)
 prop(P+'Concrete Barrier 01.fpe',640,-2750,y=ground(640,-2750),ry=-12)
 prop(P+'Container 02a.fpe',1050,-3000,y=ground(1050,-3000),ry=90,scale=90)

 # NORTHSTAR — industrial cathedral, with real stairs/storage/cable work.
 m=Mesh()
 endwall(m,-1000,-950,950,(-30,470),560)
 beam(m,0,0,1000,1900,560,45)
 sidewall(m,950,-1000,1000,(-240,260),560)
 beam(m,-950,0,0,45,390,2000)
 beam(m,230,560,0,1440,30,2000,2)
 beam(m,-720,390,0,450,30,2000,2)
 for z in (-760,140,760):beam(m,-500,0,z,60,560,60,2)
 for z in (-800,0,800):beam(m,230,520,z,1440,40,65,2)
 for x in (-650,650):
  beam(m,x,0,440,150,980,150,2)
  beam(m,x,900,440,205,80,205,5)
 beam(m,0,760,440,1120,55,90,2)
 shell=own('Northstar Turbine Hall',m)
 add(shell,'Northstar / turbine nave and stack pair',-1450,-650,y=900)
 for z in (-1000,-50):prop(P+'Generator 04a.fpe',-1590,z,y=902,ry=90)
 for z in (-1110,-120):prop(I+'Storage Tank - Small.fpe',-2210,z,y=902)
 for x in (-1350,-1070):prop(I+'Control Box - Large.fpe',x,170,y=902,ry=180)
 prop(I+'Industrial Stairs.fpe',-2160,-880,y=900,ry=90,scale=95)
 prop(I+'Industrial Shelves.fpe',-2130,-120,y=900,ry=90,scale=90)
 prop(C+'CableReel.fpe',-1960,260,y=ground(-1960,260),ry=25,scale=90)
 prop(C+'Spool.fpe',-1810,320,y=ground(-1810,320),ry=-10,scale=90)
 for x,z in [(-2050,250),(-1900,380),(-1750,250)]:
  prop(P+'Wooden Crate 01a.fpe',x,z,y=ground(x,z),ry=(x+z)%30)

 # OPERATIONS — human-scale shell with installed sci-fi facade modules.
 m=Mesh()
 endwall(m,-840,-1000,1000,(-620,-180),330)
 sidewall(m,-1000,-840,660,(-100,340),330)
 sidewall(m,1000,-840,920,(450,890),330)
 beam(m,-520,0,660,960,330,35);beam(m,440,0,920,1120,330,35)
 beam(m,-40,0,790,35,330,260)
 beam(m,0,330,-90,2000,25,1500,1);beam(m,460,330,790,1080,25,260,1)
 beam(m,130,0,60,35,250,600,1);beam(m,130,245,60,35,12,620,4)
 shell=own('Meridian Operations House',m)
 add(shell,'Operations / requisitioned civilian workplace',1250,600,y=1080)
 prop(CYB+'CS_Wall_01_Entry_01.fpe',850,-235,y=1080,ry=0,scale=65)
 prop(CYB+'CS_Wall_01.fpe',1420,-235,y=1080,ry=0,scale=65)
 prop(CYB+'CS_Wall_01_NeonDecor_Blue.fpe',1800,-235,y=1080,ry=0,scale=58)
 prop(CYM+'CS_Sidewalk_Light.fpe',520,-340,y=ground(520,-340),ry=0,scale=75)
 for x,z in [(620,40),(950,720),(1670,1000)]:
  prop(P+'Desk 01a.fpe',x,z,y=1082,ry=90);prop(P+'Computer 01a.fpe',x,z,y=1157,ry=90)
 for z in (0,260,520):prop(P+'Locker 01a.fpe',2100,z,y=1082,ry=-90)
 for x in (1550,1820):prop(P+'Portable Cot 01a.fpe',x,1370,y=1082,ry=90)
 prop(P+'Desk Chair 01a.fpe',1720,900,y=1082,ry=135)
 prop(I+'Industrial Shelves.fpe',2050,720,y=1080,ry=90,scale=85)
 prop(I+'Hand Trolly.fpe',1900,1180,y=1080,ry=-20,scale=90)
 for x,z,ry in [(550,1180,0),(780,1280,8),(2050,900,90)]:
  prop(P+'Wooden Crate 01a.fpe',x,z,y=ground(x,z),ry=ry)
 prop(I+'Cylinder - Oxygen.fpe',1950,1250,y=ground(1950,1250),ry=0)

 # AEGIS — finished military/science threshold plus active excavation dressing.
 m=Mesh()
 endwall(m,-875,-1250,1250,(-300,300),680,2)
 sidewall(m,-1250,-875,875,(-280,280),680,2)
 sidewall(m,1250,-875,875,(-380,220),680,2)
 beam(m,0,680,-525,2500,45,700,2)
 for x in (-1130,-800,-470,-140,190,520,850,1180):beam(m,x,0,875,12,100,12,2)
 beam(m,0,95,875,2500,12,12,2);beam(m,0,45,875,2500,8,10,2)
 for x in (-1080,1080):
  beam(m,x,0,-760,125,1050,125,2)
  beam(m,x,180,-835,22,650,22,5)
 beam(m,0,930,-760,2050,110,170,2)
 beam(m,0,900,-850,1650,16,20,5)
 for x in (-1210,1210):
  beam(m,x,0,80,55,680,80,2);beam(m,x,450,-20,22,110,160,5)
 shell=own('AEGIS Cliff Gallery',m)
 add(shell,'AEGIS / armoured gallery and excavation portal',0,3090,y=1540)
 prop(CYB+'CS_Wall_01_Entry_02.fpe',0,2280,y=ground(0,2280),ry=0,scale=72)
 prop(CYB+'CS_Wall_01_NeonDecor_Blue_Corner.fpe',-860,2410,y=ground(-860,2410),ry=0,scale=60)
 prop(CYB+'CS_Wall_01_NeonDecor_Blue_Corner.fpe',860,2410,y=ground(860,2410),ry=180,scale=60)
 prop(CYS+'CS_Steps_01.fpe',0,2520,y=ground(0,2520),ry=0,scale=70)
 prop(C+'Light Generator.fpe',-1080,3480,y=ground(-1080,3480),ry=45,scale=85)
 prop(C+'CableReel.fpe',-900,3550,y=ground(-900,3550),ry=20,scale=90)
 prop(C+'Rebar1.fpe',980,3500,y=ground(980,3500),ry=70,scale=85)
 for x in (-880,880):prop(I+'Control Box - Tall.fpe',x,3250,y=1542,ry=180)
 for x,z,ry in [(-1050,2650,0),(980,2760,90),(780,3500,90)]:
  prop(P+'Concrete Barrier 01.fpe',x,z,y=ground(x,z),ry=ry)

 # -------------------------------------------------------------------------
 # SURVEY CAMP 12 — a sheltered crater outpost, not an open prop yard.
 # Geography explains the camp: rock crescent to the west/north, a warm communal
 # core in the lee, a high-tech field lab against the rock wall, logistics on the
 # exposed edge, and one clear road spilling southeast toward Gate 07.
 # -------------------------------------------------------------------------
 # Rock-cut recess / pseudo cave mouth. Terrain supplies the crater; installed
 # cliff/outcrop pieces provide the overhang and close-range geology MAX terrain
 # cannot make by itself.
 for path,x,z,ry,scale in [
  (ARC+'Rock Cliff B.fpe',-2600,-7460,78,72),
  (ARC+'Rock Cliff E.fpe',-2360,-7900,118,76),
  (ARC+'Rock Cliff H.fpe',-1600,-8080,168,70),
  (ARR+'Windbreak.fpe',-2580,-7000,70,92),
  (ARR+'Pillared Rock.fpe',-2470,-7190,20,82),
  (ARR+'Outcrop.fpe',-2180,-7720,145,88),
 ]:
  prop(path,x,z,y=ground(x,z)-18,ry=ry,scale=scale)

 # A small bespoke mast remains because it gives Camp 12 a unique long-range
 # silhouette without pretending to be the camp itself.
 m=Mesh();beam(m,0,0,0,24,520,24,2);beam(m,0,410,0,360,18,18,5)
 beam(m,-120,335,0,160,14,14,1);beam(m,120,360,0,160,14,14,1)
 mast=own('Camp 12 Survey Mast',m)
 add(mast,'Meridian survey mast / Camp 12',-2150,-7470,y=ground(-2150,-7470))

 # High-tech field lab is tucked into the rock recess. A freight container gives
 # it believable field-module mass while sci-fi entry/blue trim sell the research
 # purpose. Nothing sits on a generated floor plane.
 prop(C+'Freight Container.fpe',-2290,-7070,y=ground(-2290,-7070),ry=90,scale=72)
 prop(CYF+'CS_Store_Front_01_Entrance_Blue.fpe',-2220,-6810,y=ground(-2220,-6810),ry=180,scale=48)
 prop(CYB+'CS_Wall_01_NeonDecor_Blue.fpe',-2520,-6930,y=ground(-2520,-6930),ry=90,scale=46)
 prop(CYM+'CS_Neon_06.fpe',-2440,-6840,y=ground(-2440,-6840)+55,ry=90,scale=48)
 prop(C+'SurveyorStand1.fpe',-2050,-6970,y=ground(-2050,-6970),ry=18,scale=105)
 prop(C+'SurveyorStand2.fpe',-1880,-6880,y=ground(-1880,-6880),ry=-22,scale=105)
 prop(C+'CableReel.fpe',-2080,-6740,y=ground(-2080,-6740),ry=40,scale=88)

 # Cozy human core. These familiar objects are intentionally clustered instead of
 # scattered: the player should read a tiny exhausted team living here together.
 prop(CAMP+'Tent2.fpe',-1820,-7420,y=ground(-1820,-7420),ry=20,scale=92)
 prop(CAMP+'Tent4.fpe',-1450,-7480,y=ground(-1450,-7480),ry=-18,scale=90)
 prop(CAMP+'Picnic-Table.fpe',-1630,-7140,y=ground(-1630,-7140),ry=8,scale=92)
 prop(CAMP+'Log-Bench.fpe',-1460,-7020,y=ground(-1460,-7020),ry=-12,scale=92)
 prop(CAMP+'Chair.fpe',-1780,-7000,y=ground(-1780,-7000),ry=145,scale=92)
 prop(CAMP+'Lantern.fpe',-1570,-7070,y=ground(-1570,-7070),ry=0,scale=100)
 prop(CAMP+'Radio.fpe',-1710,-7040,y=ground(-1710,-7040),ry=35,scale=95)
 prop(CAMP+'Sleeping-Bag1.fpe',-1860,-7280,y=ground(-1860,-7280),ry=25,scale=92)
 prop(CAMP+'Water-Cooler.fpe',-1370,-7200,y=ground(-1370,-7200),ry=-15,scale=92)
 prop(CAMP+'Cooker-Stove.fpe',-1510,-7240,y=ground(-1510,-7240),ry=30,scale=92)
 prop(CAMP+'CoffeePot.fpe',-1550,-7190,y=ground(-1550,-7190),ry=10,scale=95)

 # Exposed eastern/southern edge: military and construction logistics form a loose
 # perimeter between the living hollow and the road out, making the camp feel like
 # a civilian survey team operating under a security umbrella.
 prop(P+'Container 01a.fpe',-1040,-7420,y=ground(-1040,-7420),ry=180,scale=86)
 prop(P+'Generator 04a.fpe',-1140,-7000,y=ground(-1140,-7000),ry=180,scale=88)
 prop(C+'Light Generator.fpe',-1220,-6750,y=ground(-1220,-6750),ry=165,scale=88)
 prop(C+'PortableWaterTank.fpe',-980,-7130,y=ground(-980,-7130),ry=0,scale=88)
 prop(C+'Ladder Open.fpe',-1040,-7310,y=ground(-1040,-7310),ry=80,scale=82)
 for x,z,ry in [(-1180,-6840,12),(-1060,-6790,-8),(-930,-6890,20)]:
  prop(P+'Wooden Crate 01a.fpe',x,z,y=ground(x,z),ry=ry)
 for x,z,ry in [(-920,-6550,12),(-1190,-6510,-10)]:
  prop(C+'Trafficbarrier.fpe',x,z,y=ground(x,z),ry=ry,scale=92)
 prop(P+'Hesco Barrier 01.fpe',-930,-7350,y=ground(-930,-7350),ry=90,scale=88)
 prop(I+'Cylinder - Oxygen.fpe',-1260,-6900,y=ground(-1260,-6900))
 prop(I+'Cylinder - Spare Oxygen.fpe',-1320,-6900,y=ground(-1320,-6900))

 # Small bespoke route markers remain only as close-range punctuation.
 m=Mesh();beam(m,0,0,0,12,125,12,2);beam(m,0,108,0,56,16,22,5)
 marker=own('Meridian Route Beacon',m)
 for i,(x,z,ry) in enumerate([
  (-1260,-6460,5),(-780,-6100,-5),(-360,-5600,8),(210,-5050,0),
  (430,-4480,10),(360,-3920,-8),(180,-3500,5),(120,-3260,0)
 ],1):
  add(marker,'Meridian route marker '+str(i),x,z,y=ground(x,z),ry=ry)

 # Real installed electrical infrastructure replaces the old generated black pylons.
 # The first pole sits outside the crater lip so the camp interior remains intimate.
 for i,(x,z,ry) in enumerate([
  (-930,-6510,0),(-300,-5750,0),(520,-4650,0),(500,-3750,0),(-520,-2980,0)
 ],1):
  prop(CYM+'CS_Street_Electrical_Pole_01.fpe',x,z,y=ground(x,z),ry=ry,scale=72)
  if i in (1,3,5):
   prop(CYM+'CS_Street_Lamp.fpe',x+110,z+40,y=ground(x+110,z+40),ry=ry,scale=72)

 # Choir deliberately uses a vocabulary unavailable in the human asset kits.
 m=Mesh()
 for x,y,z,w,h,d,angle in [
  (-420,0,0,210,2850,310,-11),(490,0,180,260,3300,340,9),
  (20,2520,100,980,300,400,-8)
 ]:
  m.box(x,y,z,w,h,d,6,angle)
 for y in (390,430,500):m.box(-420,y,-160,205,9,9,7,-11)
 arch=own('Choir Breach Arch',m)
 add(arch,'Choir / buried arch exposed by the receded sea',0,5100,y=180,ry=16)

 # Elevated inspection bridge stays bespoke because terrain falls away below it.
 m=Mesh();beam(m,0,-16,0,500,22,980,2)
 for x in (-245,245):
  beam(m,x,95,0,12,12,980,2)
  for z in (-460,0,460):beam(m,x,0,z,12,100,12,2)
 bridge=own('Excavation Service Bridge',m)
 add(bridge,'AEGIS / inspection bridge at the fracture',-940,4050,y=1540)