"""Localized consequences of evacuation, bus isolation and evidence destruction.

Original debris geometry plus installed MAX particle presets, referenced only.
Effect markers remain native entities; Lua controls their mission-stage lifecycle.
"""
from meridian_fieldkit import ATLAS, NORMAL, SURFACE, strut

SCRIPT = r'aegis_reach\firstlight_effects.lua'
MARKER = r'_markers\Particles.fpe'
# role, preset, x, z, absolute emitter y, native editor scale, story purpose
EFFECTS = [
 ('CAMP_FAULT','embers2',-2110,-7020,542,18,'civilian bus forcibly severed; clears after power restore'),
 ('GATE_SMOKE','smoke_billowy',-700,-3140,658,28,'cargo damaged when the evacuation road was sealed'),
 ('GATE_EMBERS','embers2',-700,-3140,651,16,'residual heat inside the ruptured case'),
 ('POWER_VENT','camp smoke',-1650,-540,1242,30,'generator exhaust resumes after Northstar restart'),
 ('ARCHIVE_SMOKE','smoke_billowy',1660,1350,1098,22,'physical records burned outside Operations'),
 ('ARRAY_FAULT','embers2',-450,3253,1620,18,'overloaded firing bus; clears when AEGIS is cancelled'),
 # M-17 native review pass: two flame bodies, a much larger smoke column and a
 # separate electrical burst make the wreck read as disabled from the road.
 ('WRECK_FIRE','fire_and_smoke',-1561,-5487,474,62,'ruptured starboard mount burns hot against the hull'),
 ('WRECK_FIRE_AUX','fire_and_smoke',-1504,-5549,430,42,'detached engine still burns after separation'),
 ('WRECK_SMOKE','smoke_billowy',-1608,-5451,520,88,'dense aft smoke column makes the forced landing readable at distance'),
 ('WRECK_SPARKS','embers2',-1574,-5480,486,28,'intermittent electrical arcing at the torn engine bus'),
]


def damaged_junction(Mesh):
 m=Mesh()
 m.box(0,0,0,48,5,42,2)
 m.box(0,5,17,42,50,6,0)
 for x in (-19,19):m.box(x,5,0,4,50,34,0)
 m.box(0,51,0,42,4,34,1)
 m.box(0,12,10,28,30,5,7)
 for x in (-9,0,9):
  strut(m,(x,36,5),(x+3,24,-8),2,2)
  strut(m,(x+3,24,-8),(x-2,9,-15),2,2)
 # Open, still-hinged enclosure door; no solid panel across the fault bay.
 m.box(-31,5,-11,28,44,3,0,58)
 for x in (-10,10):
  strut(m,(x,6,10),(x,3,33),3,2)
 return m


def scorched_case(Mesh):
 m=Mesh();m.box(0,0,0,72,8,44,1)
 for x in (-34,34):m.box(x,8,0,4,25,44,2)
 m.box(0,8,20,64,25,4,1)
 m.box(-16,8,-20,32,19,4,1)
 m.box(19,8,-20,22,9,4,1) # ruptured front lip
 m.box(0,9,0,61,2,33,7)
 for x in (-21,-7,8,22):m.box(x,11,0,9,7,27,1)
 # Detached lid and torn edge lie on the same measured native pad.
 m.box(-60,0,0,42,2,34,1,12)
 for x in (-29,29):m.box(x,2,-24,8,12,5,2)
 return m


def apply(build):
 models={}
 for name,fn in [('Meridian Severed Junction',damaged_junction),('Meridian Scorched Case',scorched_case)]:
  path=build.own(name,fn(build.Mesh),ATLAS)
  f=build.AS/(name+'.fpe');s=f.read_text()
  s=s.replace('roughnessStrength = 0.82','roughnessStrength = 1.0').replace('metalnessStrength = 0.22','metalnessStrength = 1.0')
  f.write_text(s+f'normalMap = {NORMAL}\nnormalStrength = 0.65\nsurfaceMap = {SURFACE}\nreflectance = 0.04\n')
  models[name]=path
 for model,name,x,z in [
  ('Meridian Severed Junction','Camp 12 / severed civilian bus',-2110,-7000),
  ('Meridian Scorched Case','Gate 07 / damaged evacuation cargo',-700,-3140),
  ('Meridian Scorched Case','Operations / purged physical records',1660,1350),
 ]:
  build.add(models[model],name,x,z)
 for role,preset,x,z,y,scale,story in EFFECTS:
  if not (build.INSTALL/'particlesbank'/(preset+'.arx')).is_file():
   raise FileNotFoundError('Required installed MAX particle preset: '+preset)
  audio={'eleprof.soundset_s':r'misc\Campfire_loop.wav'} if role=='WRECK_FIRE' else {}
  build.add(MARKER,'FL FX '+role,x,z,y=y,scale=scale,kind='story_effect',script=SCRIPT,
   **{'eleprof.physics':0,'eleprof.phyalways':0,
      'eleprof.newparticle.emittername':'particlesbank/'+preset,
      'eleprof.newparticle.bParticle_Show_At_Start':0,
      'eleprof.newparticle.bParticle_Preview':0,
      'eleprof.newparticle.bParticle_Looping_Animation':1,
      'eleprof.newparticle.bParticle_Full_Screen':0,**audio})
  build.placements[-1].update(preset=preset,story=story)
 return {'effect_count':len(EFFECTS),'debris_count':3,'installed_presets':sorted({e[1] for e in EFFECTS})}
