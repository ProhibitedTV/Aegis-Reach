-- Native MAX infantry, authored encounter groups and concealed reinforcements.
require 'scriptbank\\people\\character_attack'
local soldiers={}
function firstlight_enemy_init_name(e,name)
 local group,index=string.match(name,'FL ENEMY (%d+) (%d+)');group=tonumber(group);index=tonumber(index)
 soldiers[e]={group=group,index=index,active=false,registered=false,queued=0}
 character_attack_init_file(e,'people\\character_attack')
 local anchor=index%3==0
 character_attack_properties(e,0,anchor and 0 or 1,anchor and 450 or 300,anchor and 1 or 0,0,index%2==0 and 3 or 2,0,1,14000,1,1500,0,0)
 if group>=6 then Hide(e);CollisionOff(e) end
end
function firstlight_enemy_main(e)
 local w=soldiers[e]
 if not w or not fl or not fl.started or fl.won then return end
 if not w.registered then fl.enemies[e]=w;w.registered=true end
 if g_Entity[e] and g_Entity[e].health<=0 then return end
 if not w.active then
  local stage=w.group<=3 and 1 or (w.group==4 and 2 or (w.group==5 and 3 or 4))
  if fl.stage<stage then return end
  if w.group==1 and g_Time-fl.born<22000 then return end
  if w.group==7 then
   if fl.evac_start==0 then return end
   local delay=({4000,7000,22000,25000,40000,43000})[w.index]
   if g_Time-fl.evac_start<delay then return end
  elseif w.group==6 then
   if w.queued==0 then w.queued=g_Time end
   if g_Time-w.queued<w.index*1700 then return end
  elseif GetPlayerDistance(e)>(w.group==1 and 1550 or 1250) then return end
  w.active=true;Show(e);CollisionOn(e)
  fl_log('enemy_activated group='..w.group..' index='..w.index..' entity='..e)
 end
 character_attack_main(e)
end
