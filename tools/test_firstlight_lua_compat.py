"""Regression test for Lua runtime differences between headless tests and GameGuru MAX."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools/vendor'))

from python_runtime import ensure_lua51_runtime

LuaRuntime = ensure_lua51_runtime(__file__)
lua = LuaRuntime(unpack_returned_tuples=True)

# MAX's runtime exposed table.unpack but not the legacy Lua 5.1 global unpack in the
# native First Light run. Simulate that API shape while still using our vendored Lua
# 5.1 harness so the guard remains portable across both environments.
lua.execute('''
FIRSTLIGHT_TEST=true
table.unpack = table.unpack or unpack
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
print('guard works with table.unpack and no global unpack')
