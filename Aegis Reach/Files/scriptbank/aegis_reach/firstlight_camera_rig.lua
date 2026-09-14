require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Legacy diegetic opening-camera rig retained as a compatibility marker.
-- The HUD-native hard-replacement opener now owns camera 0 directly. This script may
-- still position any legacy authoring camera objects that exist in old maps, but it
-- must never draw a second telemetry overlay while the native opener is active.
local rig={ship_obj=nil,cameras={}}

local mounts={
 ARRIVAL_NOSE={name='FL CG ARRIVAL NOSE',off={0,154,-378},aim={0,-0.08,-1},roll=1.0,vibe=0.18},
 ARRIVAL_STBD={name='FL CG ARRIVAL STBD',off={360,112,20},aim={-1,-0.10,0.32},roll=1.0,vibe=0.45},
 ARRIVAL_ISR={name='FL CG ARRIVAL ISR',off={0,48,-60},target={-240,-8750,120},roll=0.12,vibe=0.10},
 ARRIVAL_CONVERT={name='FL CG ARRIVAL CONVERT',off={0,54,235},aim={0,-0.22,-1},roll=0.78,vibe=0.38},
 ARRIVAL_BELLY={name='FL CG ARRIVAL BELLY',off={-125,46,90},aim={0.34,-0.58,-1},roll=0.72,vibe=0.44},
 ARRIVAL_GEAR={name='FL CG ARRIVAL GEAR',off={250,42,110},aim={-0.18,-1,0.20},roll=0.75,vibe=0.55},
 ARRIVAL_RAMP={name='FL CG ARRIVAL RAMP',off={0,138,410},aim={0,-0.18,1},roll=0.35,vibe=0.12},
 ARRIVAL_DEPLOY={name='FL CG ARRIVAL DEPLOY',off={0,138,410},aim={0,-0.22,1},roll=0.35,vibe=0.10},
 ARRIVAL_LIFTOFF={name='FL CG ARRIVAL LIFTOFF',off={0,138,410},aim={0,-0.22,1},roll=0.40,vibe=0.48},
 ARRIVAL_CLIMB={name='FL CG ARRIVAL CLIMB',off={-360,112,30},aim={1,-0.08,0.25},roll=1.0,vibe=0.42},
 ARRIVAL_DEPART={name='FL CG ARRIVAL DEPART',off={0,158,420},aim={0,-0.05,1},roll=1.0,vibe=0.28},
}

local feeds={
 ARRIVAL_PERIM='M12-PERIM-04 // LIVE',ARRIVAL_NOSE='KSTL-01 NOSE EO // LIVE',ARRIVAL_GATE='M12-GATE-02 // LIVE',
 ARRIVAL_STBD='KSTL-02 STBD SHOULDER // LIVE',ARRIVAL_ISR='KSTL-03 VENTRAL ISR // TRACK',ARRIVAL_MAST='M12-MAST-01 // LIVE',
 ARRIVAL_CONVERT='KSTL-03A VENTRAL AFT // LIVE',ARRIVAL_BELLY='KSTL-04 BELLY SERVICE // LIVE',ARRIVAL_GEAR='KSTL-04 STBD GEAR // LIVE',
 ARRIVAL_LZ='LZ07-PERIM-01 // LIVE',ARRIVAL_FLARE='LZ07-BEACON-02 // LIVE',ARRIVAL_TOUCHDOWN='LZ07-PAD-03 // LIVE',
 ARRIVAL_RAMP='KSTL-05 RAMP // LIVE',ARRIVAL_DEPLOY='KSTL-05 RAMP // DEPLOY',ARRIVAL_LIFTOFF='KSTL-05 RAMP // LIVE',
 ARRIVAL_CLIMB='KSTL-06 PORT SHOULDER // LIVE',ARRIVAL_DEPART='KSTL-07 TAIL // LIVE',
}

local rad=math.rad
local deg=math.deg
local sin=math.sin
local cos=math.cos
local sqrt=math.sqrt
local atan=math.atan2

local function rotate_local(x,y,z,rx,ry,rz)
 local cr,sr=cos(rad(rz)),sin(rad(rz));local x1,y1,z1=x*cr-y*sr,x*sr+y*cr,z
 local cp,sp=cos(rad(rx)),sin(rad(rx));local x2,y2,z2=x1,y1*cp-z1*sp,y1*sp+z1*cp
 local cy,sy=cos(rad(ry)),sin(rad(ry));return x2*cy+z2*sy,y2,-x2*sy+z2*cy
end

local function look_angles(cx,cy,cz,tx,ty,tz,roll)
 local dx,dy,dz=tx-cx,ty-cy,tz-cz;local flat=math.max(0.001,sqrt(dx*dx+dz*dz))
 return -deg(atan(dy,flat)),deg(atan(dx,dz)),roll or 0
end

local function is_ready()
 if not rig.ship_obj then return false end
 for beat,_ in pairs(mounts) do if not rig.cameras[beat] then return false end end
 return true
end
local function publish_ready()if aegis then aegis.kestrel_camera_rig_ready=is_ready() end end

local function scan()
 if not g_Entity or not GetEntityName then publish_ready();return end
 for id,ent in pairs(g_Entity) do
  if ent and ent.obj then
   local ok,name=pcall(GetEntityName,id)
   if ok and name then
    if name=='FL KESTREL INSERTION FLIGHT' then rig.ship_obj=ent.obj end
    for beat,m in pairs(mounts) do if name==m.name then rig.cameras[beat]=ent.obj end end
   end
  end
 end
 publish_ready()
end

local function active_beat()if not aegis then return nil end;return aegis.cinematic_beat or aegis.cinematic_request end

local function position_mount(beat,m,shipx,shipy,shipz,rx,ry,rz)
 local obj=rig.cameras[beat];if not obj then return end
 local ox,oy,oz=m.off[1],m.off[2],m.off[3]
 if active_beat()==beat and m.vibe and m.vibe>0 then
  local t=(g_Time or 0)*0.001;ox=ox+sin(t*29.0+#beat)*m.vibe;oy=oy+sin(t*37.0+#beat*.7)*m.vibe*.55;oz=oz+sin(t*23.0+#beat*.3)*m.vibe*.35
 end
 local dx,dy,dz=rotate_local(ox,oy,oz,rx,ry,rz);local cx,cy,cz=shipx+dx,shipy+dy,shipz+dz
 local tx,ty,tz
 if m.target then
  tx,tz=m.target[1],m.target[2]
  if GetGroundHeight then local ok,h=pcall(GetGroundHeight,tx,tz);if ok and type(h)=='number' then ty=h+m.target[3] else ty=shipy+m.target[3] end else ty=shipy+m.target[3] end
 else
  local ax,ay,az=rotate_local(m.aim[1],m.aim[2],m.aim[3],rx,ry,rz);tx,ty,tz=cx+ax*1000,cy+ay*1000,cz+az*1000
 end
 local pitch,yaw,roll=look_angles(cx,cy,cz,tx,ty,tz,rz*(m.roll or 1))
 if PositionObject then PositionObject(obj,cx,cy,cz) end;if RotateObject then RotateObject(obj,pitch,yaw,roll) end
end

local function draw_feed_label()
 if not aegis or aegis.opening_native_active then return end
 local beat=active_beat();local label=beat and feeds[beat] or nil
 if not label or not aegis.cinematic_active then return end
 if Panel then Panel(2,2,31,9) end
 if TextCenterOnXColor then
  TextCenterOnXColor(16.5,3.0,1,label,103,220,230)
  TextCenterOnXColor(16.5,6.1,1,'MERIDIAN INSERTION // REC',144,165,178)
 end
 aegis.camera_feed_label=label
end

function firstlight_camera_rig_init(e)
 rig.ship_obj=nil;rig.cameras={};if aegis then aegis.kestrel_camera_rig_ready=false end
 Hide(e);CollisionOff(e);if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end;scan()
end

function firstlight_camera_rig_main(e)
 if not is_ready() then scan() end
 if is_ready() and GetObjectPosAng then
  local x,y,z,rx,ry,rz=GetObjectPosAng(rig.ship_obj)
  if x then for beat,m in pairs(mounts) do position_mount(beat,m,x,y,z,rx or 0,ry or 0,rz or 0) end else if aegis then aegis.kestrel_camera_rig_ready=false end end
 end
 publish_ready();draw_feed_label()
end

firstlight_camera_rig_init=firstlight_guard('firstlight_camera_rig_init',firstlight_camera_rig_init)
firstlight_camera_rig_main=firstlight_guard('firstlight_camera_rig_main',firstlight_camera_rig_main)
