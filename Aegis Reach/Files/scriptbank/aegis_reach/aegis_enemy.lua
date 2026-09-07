-- DESCRIPTION: Iron Warden infantry with encounter gating and distinct tactical roles.
--
-- IMPORTANT MAX DETAIL:
-- Character models in GameGuru MAX are not guaranteed to animate merely because a
-- character behavior has been initialized. Our old encounter gate returned before the
-- stock character behavior ever ran, leaving visible dormant soldiers in their bind/T
-- pose. Dormant guards now explicitly loop their named idle animation, while enemies
-- from future phases stay hidden until their encounter becomes relevant.
require "scriptbank\\people\\character_attack"

local enemy={}

local profiles={
 flanker={0,1,320,0,0,3,0,1,12000,1,1500,0,0},
 anchor={0,0,500,1,0,4,0,1,18000,1,1600,0,0},
 hunter={0,1,260,0,0,2,0,1,12000,1,1500,0,0},
 skirmisher={0,1,420,0,1,1,0,1,15000,1,1350,0,0},
 assault={0,1,220,0,0,2,1,1,14000,1,1800,0,0},
 shockflank={0,1,300,0,0,3,1,1,13000,1,1800,0,0}
}

local function configure(e,role)
 local p=profiles[role] or profiles.skirmisher
 character_attack_properties(e,p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10],p[11],p[12],p[13])
end

local function role_for(index,reserve)
 if reserve then
  return reserve%2==0 and "shockflank" or "assault"
 end
 local slot=((index-1)%4)+1
 if slot==1 then return "flanker" end
 if slot==2 then return "anchor" end
 if slot==3 then return "hunter" end
 return "skirmisher"
end

local function phase_gate(index,reserve,shelf)
 if shelf then return 1 end
 if reserve then return reserve<=2 and 3 or 4 end
 if index<=5 then return 1 end
 if index<=8 then return 2 end
 return 3
end

local function announce_reserve(gate)
 if not aegis or not aegis_message then return end
 aegis.reserve_announced=aegis.reserve_announced or {}
 if aegis.reserve_announced[gate] then return end
 aegis.reserve_announced[gate]=true
 if gate==3 then
  aegis_message("KESTREL: Warden quick-response team moving on the AEGIS core!",6)
 else
  aegis_message("KESTREL: Pursuit squad at the landing zone. Finish this fight!",6)
 end
end

local function announce_shelf()
 if not aegis or not aegis_message or aegis.shelf_contact_announced then return end
 aegis.shelf_contact_announced=true
 aegis_message("KESTREL: Patrol on the old sea floor. Use the basalt for angles -- don't cross the shelf flat.",6)
end

local function set_visible(e,w,visible)
 if visible then
  if w.hidden then
   Show(e)
   CollisionOn(e)
   w.hidden=false
   w.idle_started=false
  end
 else
  if not w.hidden then
   Hide(e)
   CollisionOff(e)
   w.hidden=true
  end
 end
end

local function start_guard_idle(e,w)
 if w.hidden or w.active or w.idle_started then return end
 -- MAX characters supplied with Soldier Animations expose the named "idle" clip.
 -- pcall keeps a third-party/DLC character with a different animation set from taking
 -- the mission down; it will simply remain hidden or hand off to character_attack.
 pcall(function()
  SetAnimationName(e,"idle")
  SetAnimationSpeed(e,100)
  LoopAnimation(e)
 end)
 w.idle_started=true
end

function aegis_enemy_init_name(e,name)
 local reserve=tonumber(string.match(name,"RESERVE%s+(%d+)"))
 local shelf=string.find(name,"SHELF WARDEN",1,true)~=nil
 local index=tonumber(string.match(name,"WARDEN%s+(%d+)")) or reserve or 1
 local gate=phase_gate(index,reserve,shelf)
 local role=role_for(index,reserve)
 enemy[e]={
  reserve=reserve,shelf=shelf,index=index,gate=gate,role=role,
  registered=false,active=false,wake_range=shelf and 2700 or 1850,
  queued_at=0,activation_delay=reserve and (((reserve-1)%2)*1100) or 0,
  hidden=false,idle_started=false
 }

 character_attack_init_file(e,"people\\character_attack")
 configure(e,role)

 local w=enemy[e]
 -- Only the opening encounter should be visible at mission start. Future-phase and
 -- optional shelf contacts appearing as statues telegraphs content and caused the
 -- glaring T-pose screenshot. They become visible when their encounter is relevant.
 if reserve or shelf or gate>1 then
  set_visible(e,w,false)
 else
  set_visible(e,w,true)
  start_guard_idle(e,w)
 end
end

function aegis_enemy_main(e)
 local w=enemy[e]
 if not w or not aegis or not aegis.started then return end

 local on_shelf=(g_PlayerPosZ or 0)<-3300

 -- The original fortress troops always count toward mission progress, even while a
 -- future phase is hidden. Shelf patrols remain optional and register only after the
 -- player intentionally crosses the south breach.
 if not w.registered then
  if w.shelf and not on_shelf then return end
  w.registered=true
  if w.reserve then aegis.reserves[e]=true else aegis.enemies[e]=true end
 end

 if not w.active then
  if aegis.phase<w.gate then
   if not w.reserve then set_visible(e,w,false) end
   return
  end
  if w.shelf and not on_shelf then
   set_visible(e,w,false)
   return
  end

  if w.reserve then
   if w.queued_at==0 then w.queued_at=g_Time end
   if g_Time-w.queued_at<w.activation_delay then return end
   set_visible(e,w,true)
   w.active=true
   aegis.reserves[e]=nil
   aegis.enemies[e]=true
   aegis.active_enemies[e]=true
   configure(e,w.role)
   announce_reserve(w.gate)
  else
   -- Phase is live, so the soldier can now exist in the scene. Keep a real idle
   -- animation until the player enters the authored wake radius, then restart the
   -- stock character behavior so animation/weapon/navigation ownership is clean.
   set_visible(e,w,true)
   start_guard_idle(e,w)
   if GetPlayerDistance(e)>w.wake_range then return end
   w.active=true
   w.idle_started=false
   aegis.active_enemies[e]=true
   configure(e,w.role)
   if w.shelf then announce_shelf() end
  end
 end

 if not aegis.extracted then character_attack_main(e) end
end
