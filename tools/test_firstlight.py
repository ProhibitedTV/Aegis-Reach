"""Mission rules and native content checks; does not replace a human combat test."""
import sys,json,math,zipfile,ctypes as C
from pathlib import Path
from native_format import ROOT,INSTALL,read_ele,write_ele
from max_archive import PASSWORD
sys.path.insert(0,str(ROOT/'tools/vendor'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
FIRSTLIGHT_TEST=true
g_Time=1000;g_PlayerHealth=200;g_PlayerPosX=0;g_PlayerPosY=635;g_PlayerPosZ=-9500;g_PlayerAngY=0;g_KeyPressE=0;g_Entity={};calls={};ai_ticks=0
function SetPlayerHealth(v) g_PlayerHealth=v end
function SetEntityHealth(e,v) g_Entity[e].health=v end
function Hide(e) calls['hidden'..e]=true end
function Show(e) calls['hidden'..e]=false end
function CollisionOff(e) end
function CollisionOn(e) end
function PlaySound(e,s) end
function PlayNon3DSound(e,s) end
function TextColor(...) end
function TextCenterOnX(...) end
function TextCenterOnXColor(...) end
function Panel(...) end
function Prompt(t) calls.prompt=t end
function FreezePlayer() calls.frozen=true end
function FreezeAI() end
function WinGame() calls.win=true end
function SetEntityEmissiveColor(...) end
function SetEntityEmissiveStrength(...) end
function GetPlayerDistance(e) local p=g_Entity[e];return math.sqrt((p.x-g_PlayerPosX)^2+(p.y-g_PlayerPosY)^2+(p.z-g_PlayerPosZ)^2) end
package.preload['scriptbank\\\\people\\\\character_attack']=function()
 function character_attack_init_file(...) end
 function character_attack_properties(...) end
 function character_attack_main(e) ai_ticks=ai_ticks+1 end
 return true
end
''')
FILES=ROOT/'Aegis Reach/Files';g=lua.globals();checks=[]
for name in ('director','interact','enemy'):lua.execute((FILES/f'scriptbank/aegis_reach/firstlight_{name}.lua').read_text())
def check(name,ok):
 assert ok,name
 checks.append(name)
def pos(x,z):g.g_PlayerPosX=x;g.g_PlayerPosZ=z
def entity(e,x,z,hp=0):g.g_Entity[e]=lua.table_from(dict(x=x,y=600,z=z,health=hp))
def step(ms,e=None):
 for _ in range(ms//100):
  g.g_Time+=100;g.firstlight_director_main(1)
  if e:g.firstlight_interact_main(e)
g.firstlight_director_init(1);g.firstlight_director_main(1)
check('Mission starts with shield and armour, exploration score',g.fl.stage==1 and g.fl.shield==100 and g.aegis.started)
entity(2,-1250,-850);g.firstlight_interact_init_name(2,'FL POWER')
entity(3,1300,1050);g.firstlight_interact_init_name(3,'FL RECORDS')
entity(4,0,3200);g.firstlight_interact_init_name(4,'FL CORE')
entity(5,0,-2350);g.firstlight_interact_init_name(5,'FL EXTRACT')
pos(1300,1050);g.g_KeyPressE=1;step(3500,3)
check('Records cannot bypass power objective',g.fl.stage==1)
pos(-1250,-850);g.g_KeyPressE=1;step(1500,2);g.g_KeyPressE=0;step(100,2);g.g_KeyPressE=1;step(1800,2)
check('Interrupted hold resets progress',g.fl.stage==1)
entity(20,-1200,-850,100);g.fl.enemies[20]=lua.table_from(dict(active=True));step(3500,2)
check('Nearby active defender blocks terminal',g.fl.stage==1)
g.g_Entity[20].health=0;step(3200,2)
check('Power activates phase 2 after a continuous clear hold',g.fl.stage==2)
pos(1300,1050);step(3300,3)
check('Manifest advances story and discovery music',g.fl.stage==3 and g.fl.discovery_track=='discovery_choir')
pos(0,3200);step(3300,4)
check('Core reverses network and enables extraction',g.fl.stage==4)
g.g_KeyPressE=0;pos(0,-2350);step(1000,5)
check('Arrival starts extraction timer',g.fl.evac_start>0)
g.g_KeyPressE=1;step(3500,5)
check('Boarding cannot bypass holdout',not g.fl.won)
pos(2200,-2350);before=g.fl.evac_elapsed;step(5000)
check('Leaving LZ pauses landing progress',g.fl.evac_elapsed==before)
pos(0,-2350);g.g_KeyPressE=0;step(60000,5)
entity(21,200,-2250,100);g.fl.enemies[21]=lua.table_from(dict(active=True));g.g_KeyPressE=1;step(3500,5)
check('Final living defender prevents extraction',not g.fl.won)
g.g_Entity[21].health=0;step(3300,5)
check('Clean LZ completes mission with debrief',g.fl.won and g.calls.frozen)
step(2800)
check('Debrief triggers native WinGame',g.calls.win)
# Damage and repair are tested on a fresh session.
g.firstlight_director_init(1);g.firstlight_director_main(1);g.g_PlayerHealth=70;step(100)
check('Damage drains shield before armour',g.fl.shield==0 and g.fl.armour==70)
g.g_KeyPressE=0;step(5800)
check('Shield recharges after contact breaks',g.fl.shield>0 and g.fl.armour==70)
entity(8,0,-2350);g.firstlight_interact_init_name(8,'FL MED');pos(0,-2350);g.g_KeyPressE=1;step(100,8)
check('Field repair restores armour',g.fl.armour==100)
entity(9,0,-2350);g.firstlight_interact_init_name(9,'FL INTEL1');step(100,9);check('Field records are collectible',g.fl.intel.INTEL1)
entity(40,0,-2350,100);g.firstlight_enemy_init_name(40,'FL ENEMY 7 1');g.firstlight_enemy_main(40)
check('Reserve remains hidden before evacuation',g.calls.hidden40)
g.fl.stage=4;g.fl.evac_start=g.g_Time;g.firstlight_enemy_main(40);check('Reinforcements respect their arrival delay',g.calls.hidden40)
g.g_Time+=4100;g.firstlight_enemy_main(40);check('Reinforcement activates through native combat wrapper',not g.calls.hidden40 and g.ai_ticks>0)
# Native assets and encrypted archive match exactly what the engine will load.
modelchecks=0;dll=C.CDLL(str(INSTALL.parent/'assimp.dll'));dll.aiImportFile.argtypes=[C.c_char_p,C.c_uint];dll.aiImportFile.restype=C.c_void_p;dll.aiReleaseImport.argtypes=[C.c_void_p]
for p in (FILES/'entitybank/Aegis Reach/First Light').glob('*.x'):
 ptr=dll.aiImportFile(str(p).encode(),8);assert ptr,p;dll.aiReleaseImport(ptr);modelchecks+=1
check('All new architectural and sign meshes import in installed Assimp',modelchecks>=10)
with zipfile.ZipFile(FILES/'mapbank/Aegis Reach - First Light.fpm') as z:
 z.setpassword(PASSWORD);assert z.testzip() is None
 raw=z.read('map.ele');v,es=read_ele(raw);assert write_ele(v,es)==raw
 for info in z.infolist():assert info.flag_bits&1
 for asset in z.read('map.ent')[4:].decode().splitlines():assert (FILES/'entitybank'/asset).is_file(),asset
 for ent in es:
  script=ent['101:eleprof.aimain_s'];assert (FILES/'scriptbank'/script).is_file(),script
  for k,val in ent.items():
   if 'soundset' in k and isinstance(val,str) and val.lower().endswith(('.wav','.ogg')):assert (FILES/val).is_file() or (FILES/'audiobank'/val).is_file(),val
 check('MAX encrypted map CRC, entity roundtrip and all script/audio/asset references',len(es)>=300)
report=dict(checks=checks,mesh_count=modelchecks,entity_count=len(es),native_combat_playtest=False)
(ROOT/'Aegis Reach/Design/First Light/validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
