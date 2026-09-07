"""Vesper native terrain and authored First Light landmark composition.

World coordinates are GameGuru MAX inches. Native terrain owns every grounded
walking surface; authored meshes provide structures, silhouettes, railings and
purpose-built machinery. The route must remain readable with the HUD disabled.
"""
import math
from native_terrain_pass import gauss, rect_mask, smoothstep

# x,z,height. The main road intentionally reads as a continuous human intervention
# through the basin rather than a collection of disconnected named rooms.
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
# Worked pads are broad enough to look deliberately graded into the terrain.
PADS=[
 (-1700,-7160,900,720,500),     # Survey Camp 12
 (0,-3100,900,620,640),         # Gate 07 threshold
 (-1450,-650,1080,1120,900),    # Northstar
 (1250,700,1120,1020,1080),     # Operations
 (0,3090,1480,980,1540),        # AEGIS gallery
 (0,-2350,1150,500,650),        # extraction
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
 # Broad salt floor and broken basalt shelves. The road is the strongest low-frequency
 # authored shape so the player can read where human activity continues.
 h=145+35*math.sin(x/1200)*math.cos(z/1000)
 h+=1080*gauss(x,z,-1400,-10000,4100,1350)
 h+=1980*gauss(x,z,-4650,-4900,1350,2600)
 h+=1450*gauss(x,z,4900,-6800,1850,2050)
 h+=2200*gauss(x,z,4300,-800,1500,2700)
 h+=1050*gauss(x,z,-4900,2100,1600,2700)
 h+=1950*gauss(x,z,0,3900,3450,2850)
 h+=1750*gauss(x,z,0,7400,2100,1000)
 h+=40*math.sin(x/270+z/590)*math.sin(z/390)
 for route,width in ((ROUTE,360),(RETURN,300)):
  distance,y=road_sample(x,z,route)
  blend=1-smoothstep(width,width+470,distance)
  h=h*(1-blend)+y*blend
 for cx,cz,hx,hz,y in PADS:
  blend=rect_mask(x,z,cx,cz,hx,hz,280)
  h=h*(1-blend)+y*blend
 # Excavation bowl creates the late reveal and a meaningful need for the service bridge.
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
 """Landmark-scale composition using stable terrain as the floor everywhere."""
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

 # -------------------------------------------------------------------------
 # GATE 07 — first monumental landmark. A civilian road is visibly swallowed by
 # a military threshold embedded in the shelf rather than ending at a small arch.
 # -------------------------------------------------------------------------
 m=Mesh()
 # Outer shelf buttresses.
 for x in (-760,760):
  beam(m,x,0,0,250,780,980,2)
  beam(m,x,720,-120,310,70,760,5)
 # Inner portal leaves a generous readable opening.
 beam(m,-425,0,40,190,620,860,1);beam(m,425,0,40,190,620,860,1)
 beam(m,0,570,-80,680,150,820,2)
 # Recessed accent bars keep the threshold readable at night.
 for z in (-360,330):beam(m,0,555,z,720,12,22,5)
 for x in (-585,585):beam(m,x,180,-360,18,420,18,5)
 gate=own('Gate 07 Cut Portal',m)
 add(gate,'Gate 07 / military sea-wall threshold',0,-3100,y=640)
 # Occupation clutter is intentionally asymmetric so the road still reads.
 prop(P+'Concrete Barrier 01.fpe',-690,-3470,y=ground(-690,-3470),ry=15)
 prop(P+'Concrete Barrier 01.fpe',640,-2750,y=ground(640,-2750),ry=-12)
 prop(P+'Container 02a.fpe',1050,-3000,y=ground(1050,-3000),ry=90,scale=90)

 # -------------------------------------------------------------------------
 # NORTHSTAR — industrial cathedral. Twin exhaust stacks make it identifiable
 # from the road before the player reaches the power objective.
 # -------------------------------------------------------------------------
 m=Mesh()
 endwall(m,-1000,-950,950,(-30,470),560)
 beam(m,0,0,1000,1900,560,45)
 sidewall(m,950,-1000,1000,(-240,260),560)
 beam(m,-950,0,0,45,390,2000)
 beam(m,230,560,0,1440,30,2000,2)
 beam(m,-720,390,0,450,30,2000,2)
 for z in (-760,140,760):beam(m,-500,0,z,60,560,60,2)
 for z in (-800,0,800):beam(m,230,520,z,1440,40,65,2)
 # Two tall stacks and a high service bridge create the long-distance silhouette.
 for x in (-650,650):
  beam(m,x,0,440,150,980,150,2)
  beam(m,x,900,440,205,80,205,5)
 beam(m,0,760,440,1120,55,90,2)
 shell=own('Northstar Turbine Hall',m)
 add(shell,'Northstar / turbine nave and stack pair',-1450,-650,y=900)
 for z in (-1000,-50):prop(P+'Generator 04a.fpe',-1590,z,y=902,ry=90)
 for z in (-1110,-120):prop(I+'Storage Tank - Small.fpe',-2210,z,y=902)
 for x in (-1350,-1070):prop(I+'Control Box - Large.fpe',x,170,y=902,ry=180)
 for x,z in [(-2050,250),(-1900,380),(-1750,250)]:
  prop(P+'Wooden Crate 01a.fpe',x,z,y=ground(x,z),ry=(x+z)%30)

 # -------------------------------------------------------------------------
 # OPERATIONS — civilian scale and evidence of people. A lower roof, porch and
 # interior partitions contrast with the industrial mass of Northstar.
 # -------------------------------------------------------------------------
 m=Mesh()
 endwall(m,-840,-1000,1000,(-620,-180),330)
 sidewall(m,-1000,-840,660,(-100,340),330)
 sidewall(m,1000,-840,920,(450,890),330)
 beam(m,-520,0,660,960,330,35);beam(m,440,0,920,1120,330,35)
 beam(m,-40,0,790,35,330,260)
 beam(m,0,330,-90,2000,25,1500,1);beam(m,460,330,790,1080,25,260,1)
 beam(m,130,0,60,35,250,600,1);beam(m,130,245,60,35,12,620,4)
 # Exterior awning announces a human entrance without creating another floor plane.
 beam(m,-390,250,-900,520,28,300,1)
 for x in (-620,-160):beam(m,x,0,-900,24,250,24,2)
 shell=own('Meridian Operations House',m)
 add(shell,'Operations / requisitioned civilian workplace',1250,600,y=1080)
 for x,z in [(620,40),(950,720),(1670,1000)]:
  prop(P+'Desk 01a.fpe',x,z,y=1082,ry=90);prop(P+'Computer 01a.fpe',x,z,y=1157,ry=90)
 for z in (0,260,520):prop(P+'Locker 01a.fpe',2100,z,y=1082,ry=-90)
 for x in (1550,1820):prop(P+'Portable Cot 01a.fpe',x,1370,y=1082,ry=90)
 prop(P+'Desk Chair 01a.fpe',1720,900,y=1082,ry=135)
 for x,z,ry in [(550,1180,0),(780,1280,8),(2050,900,90)]:
  prop(P+'Wooden Crate 01a.fpe',x,z,y=ground(x,z),ry=ry)
 prop(I+'Cylinder - Oxygen.fpe',1950,1250,y=ground(1950,1250),ry=0)

 # -------------------------------------------------------------------------
 # AEGIS — clean military construction grows vertically around the excavation.
 # A monumental cyan-edged portal creates a second major skyline event before the
 # darker Choir geometry is revealed beyond it.
 # -------------------------------------------------------------------------
 m=Mesh()
 endwall(m,-875,-1250,1250,(-300,300),680,2)
 sidewall(m,-1250,-875,875,(-280,280),680,2)
 sidewall(m,1250,-875,875,(-380,220),680,2)
 beam(m,0,680,-525,2500,45,700,2)
 for x in (-1130,-800,-470,-140,190,520,850,1180):beam(m,x,0,875,12,100,12,2)
 beam(m,0,95,875,2500,12,12,2);beam(m,0,45,875,2500,8,10,2)
 # High arrival frame; accents face the route and separate AEGIS from civilian Meridian.
 for x in (-1080,1080):
  beam(m,x,0,-760,125,1050,125,2)
  beam(m,x,180,-835,22,650,22,5)
 beam(m,0,930,-760,2050,110,170,2)
 beam(m,0,900,-850,1650,16,20,5)
 for x in (-1210,1210):
  beam(m,x,0,80,55,680,80,2);beam(m,x,450,-20,22,110,160,5)
 shell=own('AEGIS Cliff Gallery',m)
 add(shell,'AEGIS / armoured gallery and excavation portal',0,3090,y=1540)
 for x in (-880,880):prop(I+'Control Box - Tall.fpe',x,3250,y=1542,ry=180)
 for x,z,ry in [(-1050,2650,0),(980,2760,90),(780,3500,90)]:
  prop(P+'Concrete Barrier 01.fpe',x,z,y=ground(x,z),ry=ry)

 # -------------------------------------------------------------------------
 # SURVEY CAMP 12 — recognisable civilian worksite. The mast, canopy and paired
 # habitat modules create a silhouette; clutter is grouped into work zones instead
 # of sprinkled uniformly.
 # -------------------------------------------------------------------------
 m=Mesh()
 beam(m,0,0,0,28,650,28,2)
 beam(m,0,500,0,520,22,22,5)
 beam(m,-190,410,0,22,150,22,2);beam(m,190,410,0,22,150,22,2)
 beam(m,0,600,0,170,42,90,5)
 # angled sensor outriggers
 beam(m,-140,325,0,210,18,18,1);beam(m,140,370,0,210,18,18,1)
 mast=own('Camp 12 Survey Mast',m)
 add(mast,'Meridian survey mast / Camp 12',-1870,-7160,y=500)

 m=Mesh()
 for x in (-230,230):
  for z in (-170,170):beam(m,x,0,z,24,250,24,1)
 beam(m,0,245,0,520,25,400,1)
 beam(m,0,232,-185,520,18,18,5)
 canopy=own('Camp 12 Equipment Canopy',m)
 add(canopy,'Camp 12 / survey equipment shelter',-1280,-7050,y=500,ry=8)

 # Two real MAX military containers are repurposed as civilian survey modules.
 prop(P+'Container 01a.fpe',-2300,-7420,y=500,ry=0,scale=88)
 prop(P+'Container 02a.fpe',-1170,-7460,y=500,ry=180,scale=88)
 prop(P+'Generator 04a.fpe',-1320,-6740,y=500,ry=180,scale=90)
 for x,z,ry in [(-2240,-6810,10),(-2120,-6750,-5),(-1180,-6820,12),(-1060,-6760,0)]:
  prop(P+'Wooden Crate 01a.fpe',x,z,y=500,ry=ry)
 prop(I+'Cylinder - Oxygen.fpe',-1450,-6760,y=500)
 prop(I+'Cylinder - Oxygen.fpe',-1510,-6760,y=500)
 for x,z,ry in [(-2420,-7000,15),(-970,-7060,-10)]:
  prop(P+'Concrete Barrier 01.fpe',x,z,y=500,ry=ry)

 # Route beacons are small repeated punctuation, not giant goalposts.
 m=Mesh();beam(m,0,0,0,12,125,12,2);beam(m,0,108,0,56,16,22,5)
 marker=own('Meridian Route Beacon',m)
 for i,(x,z,ry) in enumerate([
  (-1260,-6460,5),(-780,-6100,-5),(-360,-5600,8),(210,-5050,0),
  (430,-4480,10),(360,-3920,-8),(180,-3500,5),(120,-3260,0)
 ],1):
  add(marker,'Meridian route marker '+str(i),x,z,y=ground(x,z),ry=ry)

 # A sparse utility spine gives the road continuity over long sight lines.
 m=Mesh();beam(m,0,0,0,16,270,16,2);beam(m,0,245,0,145,18,18,1)
 beam(m,-55,238,0,12,52,12,5);beam(m,55,238,0,12,52,12,5)
 utility=own('Meridian Utility Pylon',m)
 for i,(x,z,ry) in enumerate([
  (-2150,-7600,0),(-1060,-6660,0),(-300,-5750,0),(520,-4650,0),
  (500,-3750,0),(-520,-2980,0)
 ],1):
  add(utility,'Meridian utility pylon '+str(i),x,z,y=ground(x,z),ry=ry)

 # -------------------------------------------------------------------------
 # Choir — intentionally unlike the human construction vocabulary.
 # -------------------------------------------------------------------------
 m=Mesh()
 for x,y,z,w,h,d,angle in [
  (-420,0,0,210,2850,310,-11),(490,0,180,260,3300,340,9),
  (20,2520,100,980,300,400,-8)
 ]:
  m.box(x,y,z,w,h,d,6,angle)
 for y in (390,430,500):m.box(-420,y,-160,205,9,9,7,-11)
 arch=own('Choir Breach Arch',m)
 add(arch,'Choir / buried arch exposed by the receded sea',0,5100,y=180,ry=16)

 # Elevated inspection bridge is one of the few places where authored deck geometry
 # is required because the native terrain drops away beneath it.
 m=Mesh();beam(m,0,-16,0,500,22,980,2)
 for x in (-245,245):
  beam(m,x,95,0,12,12,980,2)
  for z in (-460,0,460):beam(m,x,0,z,12,100,12,2)
 bridge=own('Excavation Service Bridge',m)
 add(bridge,'AEGIS / inspection bridge at the fracture',-940,4050,y=1540)
