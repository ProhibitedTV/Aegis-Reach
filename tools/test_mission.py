"""Headless logic tests. These do not claim to replace an in-engine playtest."""
import sys,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools/vendor'))
from lupa import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
g_Time=1000;g_PlayerHealth=200;g_PlayerPosX=0;g_PlayerPosY=660;g_PlayerPosZ=-2700;g_KeyPressE=0
g_Entity={};calls={};ai_ticks=0
function SetPlayerHealth(v) g_PlayerHealth=v end
function Hide(e) calls['hidden'..e]=true end
function Show(e) calls['shown'..e]=true end
function CollisionOff(e) end
function CollisionOn(e) end
function PlaySound(e,n) end
function LoopSound(e,n) end
function FreezePlayer() calls.frozen=true end
function FreezeAI() end
function WinGame() calls.win=true end
function Text(...) end
function TextColor(...) end
function TextCenterOnX(...) end
function TextCenterOnXColor(...) end
function Prompt(s) calls.prompt=s end
function GetPlayerDistance(e)
 local a=g_Entity[e];return math.sqrt((g_PlayerPosX-a.x)^2+(g_PlayerPosZ-a.z)^2+(g_PlayerPosY-a.y)^2)
end
package.preload['scriptbank\\\\people\\\\character_attack']=function()
 function character_attack_init_file(e,p) end
 function character_attack_properties(e,... ) calls['profile'..e]={...} end
 function character_attack_main(e) ai_ticks=ai_ticks+1 end
 return true
end
''')
for p in (ROOT/'Aegis Reach/Files/scriptbank/aegis_reach').glob('*.lua'):lua.execute(p.read_text())
g=lua.globals();results=[]
def ok(name,condition):
 assert condition,name
 results.append(name)
def entity(i,x,z):g.g_Entity[i]=lua.table_from({'x':x,'y':600,'z':z,'health':100})
def pos(x,z):g.g_PlayerPosX=x;g.g_PlayerPosZ=z
def advance(ms,fn=None,e=1):
 for _ in range(ms//100):
  g.g_Time+=100;g.aegis_director_main(1)
  if fn:fn(e)

g.aegis_director_init(1);g.aegis_director_main(1)
ok('mission starts with 100 armour + 100 shield',g.aegis.shield==100 and g.aegis.armour==100 and g.aegis.phase==1)
g.g_PlayerHealth=135;advance(100)
ok('damage drains shield first',g.aegis.shield==35 and g.aegis.armour==100)
advance(5000);ok('shield recharge waits for safe interval',g.aegis.shield==35)
advance(1200);ok('shield recharges after combat delay',g.aegis.shield>35)
g.g_PlayerHealth=50;advance(100);ok('excess damage reaches armour',g.aegis.shield==0 and g.aegis.armour==50)

entity(2,800,850);g.aegis_medical_init(2);pos(800,850);g.g_KeyPressE=1;g.aegis_medical_main(2)
ok('field repair restores armour',g.aegis.armour==100)
g.aegis.armour=50;g.aegis_medical_main(2);ok('field repair is single use',g.aegis.armour==50)
g.aegis.armour=100;g.aegis.shield=100;g.g_PlayerHealth=200;g.aegis.last_health=200

# Encounter pacing: nearby opening guards should engage, later sectors should wait.
entity(20,0,0);pos(0,0);g.aegis_enemy_init_name(20,'IRON WARDEN 01')
before=g.ai_ticks;g.aegis_enemy_main(20)
ok('opening guard wakes inside encounter radius',g.ai_ticks==before+1)
profile=g.calls['profile20']
ok('flanker role requests a wide flank',profile[6]==3 and profile[4]==0)
entity(21,0,0);g.aegis_enemy_init_name(21,'IRON WARDEN 02');profile=g.calls['profile21']
ok('anchor role defends its firing position',profile[4]==1 and profile[2]==0)
entity(22,0,0);g.aegis_enemy_init_name(22,'IRON WARDEN 06')
before=g.ai_ticks;g.aegis_enemy_main(22)
ok('later encounter stays dormant before its phase',g.ai_ticks==before)
g.aegis.phase=2;g.aegis_enemy_main(22)
ok('later encounter wakes when its phase is reached',g.ai_ticks==before+1)
for i in (20,21,22):g.g_Entity[i].health=0

# Relay sequence.
g.aegis.phase=1
for i,(x,z) in enumerate([(-700,-1100),(800,850),(0,2870)],10):
 entity(i,x,z);g.aegis_relay_init_name(i,'RELAY '+str(i-9))
pos(800,850);advance(4000,g.aegis_relay_main,11);ok('relay order cannot be skipped',g.aegis.phase==1)
pos(-700,-1100);advance(1500,g.aegis_relay_main,10);g.g_KeyPressE=0;advance(100,g.aegis_relay_main,10)
g.g_KeyPressE=1;advance(1800,g.aegis_relay_main,10);ok('releasing E resets the override hold',g.aegis.phase==1)
advance(1500,g.aegis_relay_main,10);ok('first relay advances mission',g.aegis.phase==2)

entity(30,950,2520);g.aegis_enemy_init_name(30,'RESERVE 01')
before=g.ai_ticks;g.aegis_enemy_main(30)
ok('reserve stays dormant before its trigger',not g.calls['shown30'] and g.ai_ticks==before)
pos(800,850);advance(3200,g.aegis_relay_main,11);g.aegis_enemy_main(30)
ok('second relay activates reserve infantry',g.aegis.phase==3 and g.calls['shown30'] and g.ai_ticks==before+1)
profile=g.calls['profile30']
ok('reserve infantry enters combat already alerted',profile[7]==1 and profile[6]==2)

pos(0,2870);advance(3200,g.aegis_relay_main,12);ok('third relay unlocks extraction',g.aegis.phase==4)
entity(40,0,-2510);entity(41,150,-2450);g.aegis.enemies[41]=True;g.aegis_extract_init(40);pos(0,-2510)
advance(4000,g.aegis_extract_main,40);ok('nearby hostiles block extraction',not g.aegis.extracted)
g.g_Entity[41].health=0;g.g_Entity[30].health=0;advance(3300,g.aegis_extract_main,40)
ok('clear LZ and held E complete the mission',g.aegis.extracted and g.calls.frozen and g.aegis.score>3000)
ok('debrief cannot fire on the extraction frame',not g.calls.win)
advance(2200);ok('debrief reaches MAX win screen',g.calls.win)

report={'passed':len(results),'checks':results,'in_engine_playtest':False,'limits':'GameGuru screenshot capture unavailable; collision, rendering and real NPC combat still require in-engine validation.'}
(ROOT/'Aegis Reach/Design/logic-test-results.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
