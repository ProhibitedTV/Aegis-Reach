-- LUA Script - precede every function and global member with lowercase name of script + '_main'
-- Collapsing Floor v9
-- DESCRIPTION: Creates a collapsing Floor area oject when walked on. Physics=ON, Gravity=ON
-- DESCRIPTION: [PROMPT_TEXT$="Floor is collapsing"]
-- DESCRIPTION: [@COLLAPSE_TYPE=1(1=Collapse, 2=Disappear, 3=Fading)]
-- DESCRIPTION: [COLLAPSE_DELAY=2000(1,3000)]
-- DESCRIPTION: [COLLAPSE_RANGE=50(0,100)]
-- DESCRIPTION: [@DAMAGE_TYPE=2(1=Death Damage, 2=Fall Damage)]
-- DESCRIPTION: [COLLISION_SCALE#=0.95(0.75,1.00)]
-- DESCRIPTION: <Sound0> for collapsing sound.

local collapse_floor 		= {}
local collapse_type 		= {}
local collapse_delay 		= {}
local collapse_range 		= {}
local damage_type 			= {}
local collision_scale 		= {}

local status 				= {}
local fade_delay 			= {}
local fade_level			= {}
local collapse_delay_new 	= {}
local shown 				= {}
local onfloor 				= {}
local startheight 			= {}
local collapsing 			= {}
local played 				= {}
local damaged				= {}
local curhealth				= {}
local showonce 				= {}

function collapsing_floor_properties(e, prompt_text, collapse_type, collapse_delay, collapse_range, damage_type, collision_scale)
	collapse_floor[e].prompt_text = prompt_text
	collapse_floor[e].collapse_type = collapse_type or 1
	collapse_floor[e].collapse_delay = collapse_delay
	collapse_floor[e].collapse_range = collapse_range
	collapse_floor[e].damage_type = damage_type or 1
	collapse_floor[e].collision_scale = collision_scale
end

function collapsing_floor_init(e)
	collapse_floor[e] = {}
	collapse_floor[e].prompt_text = ""
	collapse_floor[e].collapse_type = 1
	collapse_floor[e].collapse_delay = 2000
	collapse_floor[e].collapse_range = 80
	collapse_floor[e].damage_type = 1
	collapse_floor[e].collision_scale = 0.95

	shown[e] = 1
	onfloor[e] = 0
	showonce[e] = 0
	damaged[e] = 0
	curhealth[e] = 0
	played[e] = 0
	startheight[e] = g_Entity[e]['y']
	GravityOff(e)
	collapsing[e] = 0
	fade_level[e] = GetEntityBaseAlpha(e)
	SetEntityTransparency(e,1)
	status[e] = "init"
end

function collapsing_floor_main(e)
	if status[e] == "init"	then
		local obj = g_Entity[e].obj
		ConstrainObjMotion(obj,0,0,0)
		ConstrainObjRotation(obj,0,0,0)
		status[e] = "wait"
	end
	SetBodyScaling(g_Entity[e]['obj'],collapse_floor[e].collision_scale,collapse_floor[e].collision_scale,collapse_floor[e].collision_scale)

	if status[e] == "wait" then
		onfloor[e]=IntersectAll(g_PlayerPosX,g_PlayerPosY,g_PlayerPosZ,g_Entity[e]['x'],-1,g_Entity[e]['z'],0)
		if onfloor[e] == g_Entity[e]['obj'] and GetPlayerDistance(e) <= collapse_floor[e].collapse_range then
			status[e] = "active"
			collapse_delay_new[e] = g_Time + collapse_floor[e].collapse_delay
		end
	end
	if status[e] == "active" then
		if collapse_floor[e].collapse_type == 1 then
			if g_Time > collapse_delay_new[e] then
				if played[e] == 0 then
					PlaySound(e,0)
					played[e] = 1
				end
				collapsing[e] = 1
				GravityOn(e)
				local obj = g_Entity[e].obj
				ConstrainObjMotion(obj,1,1,1)
				ConstrainObjRotation(obj,1,1,1)
				PushObject(obj,0,0,0)
				if showonce[e] == 0 then
					PromptDuration(collapse_floor[e].prompt_text,1000)
					showonce[e] = 1
				end
				PerformLogicConnections(e)
				status[e] = "fallen"
			end
		end
		if collapse_floor[e].collapse_type == 2 then
			if g_Time > collapse_delay_new[e] then
				Hide(e)
				if played[e] == 0 then
					PlaySound(e,0)
					played[e] = 1
				end
				CollisionOff(e)
				if showonce[e] == 0 then
					PromptDuration(collapse_floor[e].prompt_text,1000)
					showonce[e] = 1
				end
				PerformLogicConnections(e)
				status[e] = "fallen"
			end
		end
		if collapse_floor[e].collapse_type == 3 then
			if g_Time > collapse_delay_new[e] then
				if fade_level[e] > 0 then
					SetEntityBaseAlpha(e,fade_level[e])
					fade_level[e] = fade_level[e]-1
				end
				if fade_level[e] <= 0 then
					Hide(e)
					if played[e] == 0 then
						PlaySound(e,0)
						played[e] = 1
					end
					CollisionOff(e)
					if showonce[e] == 0 then
						PromptDuration(collapse_floor[e].prompt_text,1000)
						showonce[e] = 1
					end
					PerformLogicConnections(e)
					status[e] = "fallen"
				end
			end
		end
	end
	if status[e] == "fallen" then
		if collapse_floor[e].damage_type == 1 then
			curhealth[e] = g_PlayerHealth
			if g_PlayerPosY < startheight[e] - 100 then
				if damaged[e] == 0 then
					HurtPlayer(e,g_PlayerHealth)
					damaged[e] = 1
				end
			end
		end
		if collapse_floor[e].damage_type == 2 then
			if g_PlayerPosY < startheight[e] then
				if damaged[e] == 0 then
					HurtPlayer(e,0)
					damaged[e] = 1
				end
			end
		end
	end
end