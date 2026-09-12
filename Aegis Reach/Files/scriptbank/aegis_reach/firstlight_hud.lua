-- Native percentage-coordinate HUD. Only real mission/vital values are shown.
local pixel=nil
local function rect(x,y,w,h,r,g,b,a)
 if not pixel and LoadImage and CreateSprite then
  local ok,id=pcall(function()
   return CreateSprite(LoadImage('scriptbank\\aegis_reach\\images\\hud_pixel.png'))
  end)
  if ok and id and id>0 then pixel=id;SetSpriteOffset(pixel,0,0);SetSpritePosition(pixel,500,500) end
 end
 if pixel then
  SetSpriteSize(pixel,w,h);SetSpriteColor(pixel,r,g,b,a or 255)
  PasteSpritePosition(pixel,x,y)
 end
end

function fl_hud_reset()
 if pixel and DeleteSprite then pcall(DeleteSprite,pixel) end
 pixel=nil
end

function fl_hud_delta(bearing,yaw)
 return (bearing-yaw+540)%360-180
end

local function meter(y,value,r,g,b)
 value=math.max(0,math.min(100,value or 0))
 for i=0,4 do
  local x=79+i*3.5
  rect(x,y,3.1,.8,58,73,81,220)
  local fill=math.max(0,math.min(1,(value-i*20)/20))
  if fill>0 then rect(x,y,3.1*fill,.8,r,g,b,255) end
 end
end

function fl_hud_draw(objective,meters,bearing,yaw,shield,armour)
 yaw=(yaw or 0)%360
 rect(2.2,2.1,27.8,6.5,8,16,22,185)
 rect(2.2,2.1,.18,6.5,89,190,210,225)
 TextColor(3.1,3,2,'FIRST LIGHT',116,211,224)
 TextColor(3.1,6,2,objective,232,239,239)
 local delta=fl_hud_delta(bearing,yaw)
 local direction=math.abs(delta)<25 and 'AHEAD' or (math.abs(delta)>145 and 'BEHIND' or (delta>0 and 'RIGHT' or 'LEFT'))
 TextColor(3.1,10,2,'NAV  '..math.floor(meters)..' m  /  '..direction,244,196,100)

 -- Heading strip spans 120 degrees; the gold cursor tracks the actual target.
 rect(32,2.1,36,5.2,8,16,22,110)
 rect(33.2,5.7,33.6,.13,153,179,188,180)
 local cardinals={[0]='N',[90]='E',[180]='S',[270]='W'}
 for angle=0,345,15 do
  local d=fl_hud_delta(angle,yaw)
  if math.abs(d)<=60 then
   local x=50+d*.28
   rect(x,cardinals[angle] and 4.7 or 5.2,.10,cardinals[angle] and 1 or .5,179,203,212,230)
   if cardinals[angle] then TextCenterOnXColor(x,2.7,2,cardinals[angle],210,225,230) end
  end
 end
 rect(49.9,5.5,.2,1.1,230,240,240,255)
 local target_x=50+math.max(-60,math.min(60,delta))*.28
 rect(target_x-.18,6.1,.36,.65,244,196,100,255)

 rect(78,83.5,20,14,8,16,22,185)
 TextColor(79,85,2,'SHIELD  '..math.floor(shield),116,211,224)
 meter(89,shield,65,183,236)
 TextColor(79,91.5,2,'ARMOUR  '..math.floor(armour),232,239,239)
 meter(95.5,armour,212,222,225)
end
