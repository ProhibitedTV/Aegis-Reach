"""Production combat-space pass layered on top of the proven First Light world build.

This module deliberately does not replace firstlight_world.py.  It adds sparse combat
geometry after the baseline world has been composed, so the mission keeps Astra's
landmarks and route while giving MAX's native Stay Back / Get Close / Wide Flank /
Use Cover tactics authored positions to work with.

Every pocket preserves a clear traversal spine.  Cover is placed as offset triangles:
a fallback position, an advance position and a lateral/flank position.  The landing
pad center remains empty for Kestrel/extraction readability.
"""
from pathlib import Path
import json

CONSTRUCTION='Booster Pack\\Construction Pack\\'
MILITARY='Booster Pack\\Military Pack\\'

# asset, x, z, yaw, scale, encounter, tactical purpose
COVER=[
 # Dry Tide Channel // first readable Warden contact.  Sparse, low cover only.
 (CONSTRUCTION+'Roadblock2.fpe',-690,-5480,18,84,'channel','rifle fallback'),
 (CONSTRUCTION+'Roadblock3.fpe', 540,-5120,-14,84,'channel','assault advance'),
 (MILITARY+'Concrete Barrier 01.fpe',-120,-4740,82,88,'channel','anchor crossfire'),

 # Gate 07 // retain the central gate opening and create two side fights.
 (MILITARY+'Hesco Barrier 01.fpe',-980,-2760,8,86,'gate07','west fallback'),
 (MILITARY+'Concrete Barrier 01.fpe',620,-2580,-18,90,'gate07','east advance'),
 (MILITARY+'Wooden Crate 01a.fpe',1160,-2310,12,86,'gate07','east flank stepping cover'),

 # Northstar // machinery remains the visual owner; these pieces connect the gaps.
 (MILITARY+'Concrete Barrier 01.fpe',-980,-1180,10,90,'northstar','objective approach'),
 (MILITARY+'Hesco Barrier 01.fpe',-930,-430,92,86,'northstar','assault pocket'),
 (MILITARY+'Wooden Crate 01a.fpe',-2250,-390,-15,90,'northstar','anchor pocket'),
 (MILITARY+'Wooden Crate 01a.fpe',-760,120,25,86,'northstar','flank exit'),

 # Operations // keep the workplace readable; use light cover around its perimeter.
 (MILITARY+'Concrete Barrier 01.fpe',470,360,8,88,'operations','south approach'),
 (MILITARY+'Wooden Crate 01a.fpe',780,1160,-12,86,'operations','west flank'),
 (MILITARY+'Concrete Barrier 01.fpe',1840,1160,88,88,'operations','east anchor'),

 # AEGIS // stronger military retrofit against the alien excavation silhouette.
 (MILITARY+'Hesco Barrier 01.fpe',-640,2860,4,90,'aegis','west rifle pocket'),
 (MILITARY+'Concrete Barrier 01.fpe',610,2940,-8,92,'aegis','east assault pocket'),
 (MILITARY+'Hesco Barrier 01.fpe',-980,3380,88,88,'aegis','anchor fallback'),
 (MILITARY+'Concrete Barrier 01.fpe',940,3490,18,90,'aegis','wide flank pocket'),

 # Return service road // cover punctuation makes the retreat feel authored, not empty.
 (MILITARY+'Concrete Barrier 01.fpe',-2780,1880,72,88,'return','upper return bend'),
 (MILITARY+'Hesco Barrier 01.fpe',-3010,1040,4,88,'return','mid return hold'),
 (MILITARY+'Concrete Barrier 01.fpe',-2770,260,92,88,'return','lower return crossfire'),
 (CONSTRUCTION+'Roadblock2.fpe',-2450,-930,-12,84,'return','gate re-entry'),

 # LZ // four offset pieces frame the pad.  Nothing is placed in the central 900-inch lane.
 (MILITARY+'Hesco Barrier 01.fpe',-920,-2500,6,90,'extraction','west south fallback'),
 (MILITARY+'Concrete Barrier 01.fpe',900,-2490,-8,90,'extraction','east south fallback'),
 (MILITARY+'Concrete Barrier 01.fpe',-880,-2010,88,90,'extraction','west north advance'),
 (MILITARY+'Hesco Barrier 01.fpe',920,-1980,92,90,'extraction','east north advance'),
]

# Revised dormant starts align tactical roles with the cover pockets above.  Index role
# pattern is rifle, assault, anchor, flanker and then repeats.
ENEMY_STARTS={
 1:[(-760,-5440),(500,-5070),(-160,-4680)],
 2:[(-900,-2700),(600,-2460),(1370,-2200)],
 3:[(-2050,-1180),(-940,-610),(-2180,-260),(-760,80)],
 4:[(470,300),(1600,470),(1850,1100),(760,1160)],
 5:[(-700,2800),(620,2880),(-980,3330),(940,3440)],
 6:[(-2820,1900),(-3060,1320),(-3020,560),(-2710,-180)],
 7:[(2050,-2550),(1780,-2180),(-3270,-1100),(-3050,-760),(2060,-2110),(-3190,-1300)],
}

# Backlights sit behind likely contact positions so silhouettes read against Vesper's dark
# grade.  They are deliberately fewer/weaker than the landmark lighting layer.
COMBAT_LIGHTS=[
 (-650,-5350,0xCFA875,360,'channel'),
 (1120,-2500,0xE6B77A,430,'gate07'),
 (-2180,-700,0xE6B77A,420,'northstar'),
 (1830,980,0xC2D7DF,400,'operations'),
 (-1050,3270,0x70C7DC,500,'aegis'),
 (1050,3380,0x748CE8,520,'aegis'),
 (-1660,-2350,0xE6B77A,460,'extraction-west'),
 (1660,-2350,0xE6B77A,460,'extraction-east'),
]


def _set_entity_position(build,entity,x,z):
 build.set_suffix(entity,'x',x)
 build.set_suffix(entity,'z',z)
 build.set_suffix(entity,'y',build.ground(x,z)+5)


def apply(build):
 """Mutate an imported build_first_light module after its baseline composition."""
 for asset,x,z,ry,scale,encounter,purpose in COVER:
  build.prop(asset,x,z,ry=ry,scale=scale)
  build.placements[-1]['kind']='combat_cover'
  build.placements[-1]['encounter']=encounter
  build.placements[-1]['purpose']=purpose

 moved=[]
 for entity,placement in zip(build.entities,build.placements):
  name=placement.get('name','')
  if not name.startswith('FL ENEMY '):continue
  _,_,group,index=name.split()
  group=int(group);index=int(index)
  starts=ENEMY_STARTS.get(group)
  if not starts or index>len(starts):continue
  x,z=starts[index-1]
  _set_entity_position(build,entity,x,z)
  placement['x']=x;placement['y']=build.ground(x,z)+5;placement['z']=z
  placement['combat_role']=('rifle','assault','anchor','flanker')[(index-1)%4]
  moved.append({'group':group,'index':index,'x':x,'z':z,'role':placement['combat_role']})

 lightp=r'_markers\\White Light.fpe'
 template=build.T[lightp]
 first_index=len(build.light_locations)+len(build.crystal_sites)+1
 for offset,(x,z,color,radius,encounter) in enumerate(COMBAT_LIGHTS):
  idx=first_index+offset
  build.add(lightp,'FL COMBAT LIGHT '+str(offset+1),x,z,y=build.ground(x,z)+145,
            kind='combat_light',template=template,script=r'markers\\ConstantLight.lua',
            **{'eleprof.light.color':color,'eleprof.light.range':radius,
               'eleprof.light.index':idx,'eleprof.light.fLightHasProbe':0})
  build.placements[-1]['encounter']=encounter

 return {
  'cover_count':len(COVER),
  'combat_light_count':len(COMBAT_LIGHTS),
  'enemy_starts':moved,
  'clear_lz_center':True,
  'design_rule':'offset cover triangles with preserved traversal spine',
 }


def write_manifest(path,summary):
 Path(path).write_text(json.dumps(summary,indent=2))
