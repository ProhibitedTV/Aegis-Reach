-- DESCRIPTION: Iron Warden infantry with encounter gating and distinct tactical roles.
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
  -- Reserve pairs deliberately split jobs: one closes distance while the other
  -- takes the wide route. Combined with their stagger this should read as a
  -- reinforcement pincer rather than two soldiers popping in simultaneously.
  return reserve%2==0 and "shockflank" or "assault"
 end
 local slot=((index-1)%4)+1
 if slot==1 then return "flanker" end
 if slot==2 then return "anchor" end
 if slot==3 then return "hunter" end
 return "skirmisher"
end

local function phase_gate(index,reserve)
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

function aegis_enemy_init_name(e,name)
 local reserve=tonumber(string.match(name,"RESERVE%s+(%d+)"))
 local index=tonumber(string.match(name,"WARDEN%s+(%d+)")) or reserve or 1
 local gate=phase_gate(index,reserve)
 local role=role_for(index,reserve)
 enemy[e]={reserve=reserve,index=index,gate=gate,role=role,registered=false,active=false,wake_range=1850,
   queued_at=0,activation_delay=reserve and (((reserve-1)%2)*1100) or 0}
 character_attack_init_file(e,"people\\character_attack")
 configure(e,role)
 if reserve then Hide(e);CollisionOff(e) end
end

function aegis_enemy_main(e)
 local w=enemy[e]
 if not w or not aegis or not aegis.started then return end

 if not w.registered then
  w.registered=true
  if w.reserve then aegis.reserves[e]=true else aegis.enemies[e]=true end
 end

 if not w.active then
  if aegis.phase<w.gate then return end
  if w.reserve then
   if w.queued_at==0 then w.queued_at=g_Time end
   if g_Time-w.queued_at<w.activation_delay then return end
   w.active=true
   Show(e);CollisionOn(e)
   aegis.reserves[e]=nil
   aegis.enemies[e]=true
   aegis.active_enemies[e]=true
   configure(e,w.role)
   announce_reserve(w.gate)
  else
   -- Normal troops remain visible as guards, but do not enter full combat logic
   -- until the player reaches their local encounter space. This prevents the
   -- whole fortress from becoming one long undifferentiated firefight.
   if GetPlayerDistance(e)>w.wake_range then return end
   w.active=true
   aegis.active_enemies[e]=true
   configure(e,w.role)
  end
 end

 if not aegis.extracted then character_attack_main(e) end
end
