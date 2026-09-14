"""Runtime regression for the documentary-style FIRST LIGHT opening cameras."""
from native_format import ROOT
from python_runtime import ensure_max_lua_runtime
from firstlight_cinematics import OPENING_SEQUENCE,OPENING_SOURCES,SHIP_MOUNT_BEATS,WORLD_CAMERA_BEATS

assert len(OPENING_SEQUENCE)==17
assert len(SHIP_MOUNT_BEATS)==11
assert len(WORLD_CAMERA_BEATS)==6
assert OPENING_SOURCES['ARRIVAL_ISR']['mode']=='gimbal stabilized'
assert all(OPENING_SOURCES[b]['carrier']=='kestrel' for b in SHIP_MOUNT_BEATS)
assert all(OPENING_SOURCES[b]['carrier']=='world' for b in WORLD_CAMERA_BEATS)

LuaRuntime=ensure_max_lua_runtime(__file__)
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
function firstlight_guard(n,f) return f end
g_Time=1000
aegis={cinematic_active=true,cinematic_beat='ARRIVAL_NOSE'}
g_Entity={};names={};objpose={};campos={};camrot={};texts={}
function GetEntityName(e) return names[e] end
function Hide(e) end
function CollisionOff(e) end
function SetEntityAlwaysActive(e,v) end
function GetGroundHeight(x,z) return 500 end
function Panel(...) end
function TextCenterOnXColor(x,y,size,text,...) texts[#texts+1]=text end
function GetObjectPosAng(obj)
 local p=objpose[obj]
 if not p then return nil end
 return p.x,p.y,p.z,p.rx,p.ry,p.rz
end
function PositionObject(obj,x,y,z) campos[obj]={x=x,y=y,z=z} end
function RotateObject(obj,rx,ry,rz) camrot[obj]={rx=rx,ry=ry,rz=rz} end

names[1]='FL KESTREL INSERTION FLIGHT';g_Entity[1]={obj=101}
objpose[101]={x=100,y=600,z=-9000,rx=2,ry=180,rz=6}
local camera_names={
 'FL CG ARRIVAL PERIM','FL CG ARRIVAL NOSE','FL CG ARRIVAL GATE','FL CG ARRIVAL STBD','FL CG ARRIVAL ISR','FL CG ARRIVAL MAST',
 'FL CG ARRIVAL CONVERT','FL CG ARRIVAL BELLY','FL CG ARRIVAL GEAR','FL CG ARRIVAL LZ','FL CG ARRIVAL FLARE','FL CG ARRIVAL TOUCHDOWN',
 'FL CG ARRIVAL RAMP','FL CG ARRIVAL DEPLOY','FL CG ARRIVAL LIFTOFF','FL CG ARRIVAL CLIMB','FL CG ARRIVAL DEPART'
}
for i,name in ipairs(camera_names) do
 local e=9+i;local obj=209+i;names[e]=name;g_Entity[e]={obj=obj};objpose[obj]={x=0,y=0,z=0,rx=0,ry=0,rz=0}
end
g_Entity[99]={obj=999};names[99]='FIRST LIGHT // CAMERA RIG'
''')
source=(ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_camera_rig.lua').read_text(errors='replace')
lua.execute('\n'.join(line for line in source.splitlines() if not line.startswith('require ')))
lua.execute(r'''
firstlight_camera_rig_init(99)
assert(aegis.kestrel_camera_rig_ready==true,'ship camera rig did not publish ready state')
firstlight_camera_rig_main(99)

local mounted={211,213,214,216,217,218,222,223,224,225,226}
for _,obj in ipairs(mounted) do assert(campos[obj]~=nil and camrot[obj]~=nil,'camera mount not positioned '..obj) end
local fixed={210,212,215,219,220,221}
for _,obj in ipairs(fixed) do assert(campos[obj]==nil,'world camera was incorrectly attached to ship '..obj) end

local ship=objpose[101]
local nose=campos[211]
local d=math.sqrt((nose.x-ship.x)^2+(nose.y-ship.y)^2+(nose.z-ship.z)^2)
local expected=math.sqrt(154^2+378^2)
assert(math.abs(d-expected)<0.01,'nose mount lost rigid offset')
assert(math.abs(camrot[214].rz-ship.rz*.12)<0.01,'ISR roll stabilization regressed')
for _,obj in ipairs({222,223,224}) do assert(campos[obj]~=nil) end
assert(math.abs(campos[222].x-campos[223].x)<0.001 and math.abs(campos[223].x-campos[224].x)<0.001)

local oldx,oldz=nose.x,nose.z
ship.x=1100;ship.y=700;ship.z=-8500;ship.rx=-4;ship.ry=128;ship.rz=-9
g_Time=1500;aegis.cinematic_beat='ARRIVAL_STBD';firstlight_camera_rig_main(99)
assert(aegis.kestrel_camera_rig_ready==true)
local newnose=campos[211]
assert(math.abs(newnose.x-oldx)>100 or math.abs(newnose.z-oldz)>100,'camera did not follow translated ship')
local nd=math.sqrt((newnose.x-ship.x)^2+(newnose.y-ship.y)^2+(newnose.z-ship.z)^2)
assert(math.abs(nd-expected)<0.01,'camera offset changed under ship rotation')
local rendered='';for _,v in pairs(texts) do rendered=rendered..' '..v end
assert(string.find(rendered,'KSTL%-02 STBD SHOULDER'),'active feed telemetry label missing')
''')
print('FIRST LIGHT // DIEGETIC CAMERA RIG PASS')
print('11 Kestrel-mounted feeds follow the live airframe; 6 infrastructure cameras remain world-fixed; feed telemetry renders.')
