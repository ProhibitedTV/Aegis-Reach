"""Initialize the real installed MAX soldier interpreter under Lua 5.1."""
from pathlib import Path
import os,sys,json
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'tools/vendor'))
from lupa.lua51 import LuaRuntime
os.chdir(ROOT/'Aegis Reach/Files')
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('''g_Time=1000;g_Entity={[1]={x=0,y=600,z=0,health=100,obj=1}};
function Timer() return g_Time end
function Hide(e) end
function CollisionOff(e) end
''')
lua.execute(Path('scriptbank/aegis_reach/aegis_enemy.lua').read_text())
lua.globals().aegis_enemy_init_name(1,'IRON WARDEN 01')
count=lua.globals().g_character_attack_behavior_count
assert count>0,count
report={'lua':'5.1','real_MAX_character_behavior_instructions':count,'initialization':'passed','live_pathfinding_and_combat':'requires engine playtest'}
(ROOT/'Aegis Reach/Design/combat-bootstrap-test.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
