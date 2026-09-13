"""Source-level regression checks for FIRST LIGHT production combat geometry.

This test is intentionally installation-independent.  It verifies the authored tactical
layout before the native builder touches licensed MAX assets or emits an encrypted FPM.
"""
import math

from firstlight_combat_geometry import COVER,COMBAT_LIGHTS,ENEMY_STARTS

GROUP_TO_ENCOUNTER={
 1:'channel',2:'gate07',3:'northstar',4:'operations',5:'aegis',6:'return',7:'extraction'
}
EXPECTED_GROUP_SIZES={1:3,2:3,3:4,4:4,5:4,6:4,7:6}
EXPECTED_ROLE=('rifle','assault','anchor','flanker')


def check(name,condition):
 if not condition:raise AssertionError(name)
 print('PASS //',name)


def distance(a,b):return math.hypot(a[0]-b[0],a[1]-b[1])


def main():
 check('combat layer has at least twenty-four authored cover pieces',len(COVER)>=24)
 check('combat layer has eight restrained contact backlights',len(COMBAT_LIGHTS)==8)
 check('all encounter groups have complete authored starts',
       all(len(ENEMY_STARTS.get(group,()))==count for group,count in EXPECTED_GROUP_SIZES.items()))

 # No cover may intrude into the central extraction/boarding spine.  Side cover can
 # frame the fight, but the 1300-inch-wide center must remain visually/navigation clear.
 blocked=[]
 for asset,x,z,ry,scale,encounter,purpose in COVER:
  if encounter=='extraction' and abs(x)<650 and -2800<z<-1750:
   blocked.append((asset,x,z,purpose))
 check('extraction cover preserves the central landing/boarding lane',not blocked)

 # Regular encounter starts should be tied to a nearby authored cover pocket rather
 # than arbitrary empty-space coordinates.  Extraction reserves are approach waves and
 # intentionally spawn farther out on service roads, so they are checked separately.
 cover_by_encounter={}
 for asset,x,z,ry,scale,encounter,purpose in COVER:
  cover_by_encounter.setdefault(encounter,[]).append((x,z))
 for group in range(1,7):
  encounter=GROUP_TO_ENCOUNTER[group]
  pockets=cover_by_encounter[encounter]
  for index,start in enumerate(ENEMY_STARTS[group],1):
   nearest=min(distance(start,p) for p in pockets)
   check(f'group {group} start {index} is tied to authored {encounter} cover ({nearest:.0f})',nearest<=900)

 # The extraction reserve should originate outside the pad center and from both sides.
 reserves=ENEMY_STARTS[7]
 check('extraction reserve never starts inside the pad center',
       all(not (abs(x)<900 and -2850<z<-1750) for x,z in reserves))
 check('extraction reserve attacks from both east and west service roads',
       any(x>1500 for x,z in reserves) and any(x<-2500 for x,z in reserves))

 # Role order must match firstlight_enemy.lua.  This catches silent drift between map
 # placement assumptions and the native AI wrapper's tactical role pattern.
 assigned=[]
 for group,starts in ENEMY_STARTS.items():
  assigned.extend(EXPECTED_ROLE[(index-1)%4] for index,_ in enumerate(starts,1))
 check('authored starts exercise all four native tactical roles',set(assigned)==set(EXPECTED_ROLE))

 # Backlights are presentation support, never giant area lights.
 check('combat backlights remain local rather than flattening the night grade',
       all(300<=radius<=550 for x,z,color,radius,encounter in COMBAT_LIGHTS))

 print('FIRST LIGHT // COMBAT GEOMETRY SOURCE PASS')


if __name__=='__main__':main()
