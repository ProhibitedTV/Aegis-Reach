-- Preserve native failures with their traceback; never turn them into a silent success.
-- MAX's runtime does not guarantee the Lua 5.1 global `unpack`; newer Lua exposes
-- the same function as table.unpack. Resolve it once so guards work in both the
-- headless Lua 5.1 harness and the actual MAX runtime.
local firstlight_unpack = (table and table.unpack) or unpack

function firstlight_audit(message)
 if FIRSTLIGHT_TEST then return end
 local base=os.getenv('USERPROFILE')
 if not base then return end
 local file=io.open(base..'/Documents/GameGuruApps/GameGuruMAX/Files/first-light-diagnostics.log','a')
 if file then file:write(os.date('%Y-%m-%d %H:%M:%S'),' ',message,'\n');file:close() end
end

function firstlight_guard(name,fn)
 return function(...)
  local args={...}
  local ok,result=xpcall(function()
   if not firstlight_unpack then
    error('No compatible unpack implementation is available in this Lua runtime')
   end
   return fn(firstlight_unpack(args))
  end,debug.traceback)
  if not ok then firstlight_audit('LUA_ERROR '..name..' '..tostring(result));error(result,0) end
  return result
 end
end
