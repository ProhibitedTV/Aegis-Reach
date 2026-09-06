-- swimming v6 by Necrym59
-- DESCRIPTION: A global behavior that activates swimming animations when underwater and can
-- DESCRIPTION: [REARM_WEAPON!=0] when leaving water.
-- DESCRIPTION: [OXYGEN_DISPLAY!=0] display oxygen level.

g_have_scubagear = {}
local lower = string.lower
local swimming 			= {}
local rearm_weapon		= {}
local oxygen_display	= {}
local arm_set_name		= {}
local arm_animation		= {}
local arm_speed			= {}
local oxygen_bar		= {}


local startframe 	= {}
local endframe 		= {}
local last_gun		= {}
local status 		= {}
local oxbarsprite	= {}
local oxlevel		= {}
local oxbarwidth	= {}
local doonce		= {}

function swimming_properties(e,rearm_weapon, oxygen_display, arm_set_name, arm_animation, arm_speed, oxygen_bar)
	swimming[e].rearm_weapon = rearm_weapon or 0
	swimming[e].oxygen_display = oxygen_display or 0
	swimming[e].arm_set_name = "interactive\\swimming"
	swimming[e].arm_animation = "breaststroke"
	swimming[e].arm_speed = 100
	swimming[e].oxygen_bar = "imagebank\\HUD Library\\MISC\\progress-bar.png"
end

function swimming_init(e)
	swimming[e] = {}
	swimming[e].rearm_weapon = rearm_weapon	
	swimming[e].oxygen_display = 0
	swimming[e].arm_set_name = "interactive\\swimming"
	swimming[e].arm_animation = ""
	swimming[e].arm_speed = 100
	swimming[e].oxygen_bar = "imagebank\\HUD Library\\MISC\\progress-bar.png"	
	
	g_have_scubagear = 0
	doonce[e] = 0
	oxlevel[e] = 0
	oxbarwidth[e] =	0
	last_gun = g_PlayerGunName	
	SetEntityAlwaysActive(e,1)
	status[e] = "init"	
end

function swimming_main(e)

	if status[e] == "init" then
		if swimming[e].oxygen_bar ~= "" then			
			oxbarsprite[e] = CreateSprite(LoadImage(swimming[e].oxygen_bar))
			SetSpriteSize(oxbarsprite[e],5,-1)
			SetSpriteColor(oxbarsprite[e],0,200,255,200)			
			SetSpriteOffset(oxbarsprite[e],(800/50)/2,0)
			SetSpritePosition(oxbarsprite[e],200,200)
			oxbarwidth[e] = GetDesktopWidth()/200
		end	
		SetGamePlayerControlUnderwater(0)
		SetGamePlayerControlInWaterState(0)
		SetUnderwaterOff()
		if (RawSoundExist(underwaterSound) == 1) then
			StopRawSound(underwaterSound)
		end
		swimming[e].arm_animation = "breaststroke"
		status[e] = "start"
	end	

	-- Get last_gun before ChangePlayerWeaponID(0) is called in gameplayercontrol.
	if (GetGamePlayerStateUnderwater() == 0 and GetGamePlayerStatePlayerY() < GetGamePlayerStateWaterlineY()) then
		if g_PlayerGunName ~= swimming[e].arm_set_name then
			last_gun = g_PlayerGunName
		end		
	end

	local animplaying = GunAnimationPlaying() 														-- Always call this to allow it to stop current animation.
	if (g_PlayerPosY < GetWaterHeight() and GetGamePlayerControlInWaterState() >= 2) then 			-- Player Underwater and below waterlevel check
		oxlevel[e] = GetGamePlayerControlDrownTimestamp()-Timer()
		SetSpriteSize(oxbarsprite[e],(oxlevel[e]/oxbarwidth[e])/50,0.5)			
		SetSpriteOffset(oxbarsprite[e],((oxlevel[e]/oxbarwidth[e])/50)/2,0)
		if oxlevel[e] < 3000 then SetSpriteColor(oxbarsprite[e],255,0,0,200) end
		if swimming[e].oxygen_display == 1 and g_have_scubagear == 0 then PasteSpritePosition(oxbarsprite[e],50,95) end
		ForceGunUnderWater(1)																		-- Allow Underwater Arm/Gun Display
		if status[e] == "start" then			
			AddPlayerWeapon(swimming[e].arm_set_name)												-- Add Temporary arms/weapon to Player
			local WeaponID = GetWeaponID(swimming[e].arm_set_name)									-- Get weapon id of arms/weapon
			SetWeaponSlot(11,WeaponID,WeaponID)														-- Set special weapon slot 11 for arms/weapon
			ChangePlayerWeapon(swimming[e].arm_set_name)											-- Change to Temporary arms/weapon in slot 11
			doonce[e] = 1
			status[e] = "animstart"
		end	
		startframe,endframe = GetGunAnimationFramesFromName(swimming[e].arm_animation)				-- Get animation start/end frames for required animation.
		if status[e] == "animstart" then
			if endframe > 0 then
				status[e] = "animrunning"
			end
		elseif status[e] == "animrunning" then
			if animplaying == 0 then
				if g_PlrKeyW == 0 then
					swimming[e].arm_animation = "wading"
					startframe,endframe = GetGunAnimationFramesFromName(swimming[e].arm_animation)	-- Get animation start/end frames for required animation.			
					SetGunAnimationSpeed(swimming[e].arm_speed)										-- Set animation speed of arms/weapon
					PlayGunAnimation(startframe,endframe)											-- Play animation of arms/weapon
				end
				if g_PlrKeyW == 1 then
					swimming[e].arm_animation = "breaststroke"
					startframe,endframe = GetGunAnimationFramesFromName(swimming[e].arm_animation)	-- Get animation start/end frames for required animation.			
					SetGunAnimationSpeed(swimming[e].arm_speed)										-- Set animation speed of arms/weapon
					PlayGunAnimation(startframe,endframe)											-- Play animation of arms/weapon
				end
				if g_PlrKeyW == 1 and g_KeyPressSHIFT == 1 then
					swimming[e].arm_animation = "breaststroke"
					startframe,endframe = GetGunAnimationFramesFromName(swimming[e].arm_animation)	-- Get animation start/end frames for required animation.			
					SetGunAnimationSpeed(swimming[e].arm_speed*1.5)									-- Set increased animation speed of arms/weapon
					PlayGunAnimation(startframe,endframe)											-- Play animation of arms/weapon
				end
			end
		end
	else																									
		ForceGunUnderWater(0)																		-- Turn Off Underwater Arm/Gun Display
		if doonce[e] == 1 then
			RemovePlayerWeapon(11)
			SetPlayerWeapons(1)
			if swimming[e].rearm_weapon == 0 then ChangePlayerWeapon(0) end							-- Restore to null arms/weapon
			if swimming[e].rearm_weapon == 1 then ChangePlayerWeapon(last_gun) end					-- Restore to stored carried arms/weapon of Player
			status[e] = "init"
			doonce[e] = 0
		end	
    end
end