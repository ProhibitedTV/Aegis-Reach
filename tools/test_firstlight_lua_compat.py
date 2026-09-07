"""Regression test for Lua runtime differences between headless tests and GameGuru MAX."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools/vendor'))

from python_runtime import ensure_max_lua_runtime

LuaRuntime = ensure_max_lua_runtime(__file__)
lua = LuaRuntime(unpack_returned_tuples=True)

# GameGuru MAX ships Lua 5.2.3. In that runtime table.unpack exists and the legacy
# Lua 5.1 global unpack does not. Keep the shape explicit so this exact native crash
# remains covered even if the vendored runtime changes later.
lua.execute('''
FIRSTLIGHT_TEST=true
assert(table.unpack ~= nil)
unpack = nil
''')

audit = ROOT / 'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_audit.lua'
lua.execute(audit.read_text())
lua.execute('''
function firstlight_probe(a,b) return a+b end
firstlight_probe = firstlight_guard('firstlight_probe', firstlight_probe)
''')

result = lua.globals().firstlight_probe(17, 25)
assert result == 42, result
print('FIRST LIGHT // LUA RUNTIME COMPAT PASS')
print('GameGuru MAX Lua 5.2 guard path verified: table.unpack / no global unpack')
