-- Preserve native failures with their traceback; never turn them into a silent success.
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
  local ok,result=xpcall(function() return fn(unpack(args)) end,debug.traceback)
  if not ok then firstlight_audit('LUA_ERROR '..name..' '..tostring(result));error(result,0) end
  return result
 end
end
