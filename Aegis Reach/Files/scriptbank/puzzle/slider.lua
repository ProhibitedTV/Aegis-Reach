-- LUA Script - precede every function and global member with lowercase name of script + '_main'
-- Slider Script v17
-- DESCRIPTION: Slides an object in 90 degree directions, ideal for crawler or grid style games.
-- DESCRIPTION: Can be activated by player or zone/switch
-- DESCRIPTION: Set Physics=ON, IsImobile=ON, AlwaysActive=ON.
-- DESCRIPTION: [PROMPT$="Press E to Activate"]
-- DESCRIPTION: [RANGE=80]
-- DESCRIPTION: [@SLIDE_MODE=1(1=Manual,2=Switch/Zone)]
-- DESCRIPTION: [@SLIDE_TYPE=1(1=Open/Close, 2=Lock Open, 3=Continuous)]
-- DESCRIPTION: [@SLIDE_DIRECTION=1(1=Left, 2=Right, 3=Up, 4=Down, 5=Forward, 6=Backward)]
-- DESCRIPTION: [SLIDE_CLOSE_DELAY=1(1,100)]
-- DESCRIPTION: [SLIDE_AMOUNT=200]
-- DESCRIPTION: [SLIDE_SPEED=1(1,20)]
-- DESCRIPTION: [DAMAGE_AMOUNT=0(0,1000)] to receive if in range and slider speed is 5 or faster
-- DESCRIPTION: [@PROMPT_DISPLAY=1(1=Local,2=Screen)]
-- DESCRIPTION: [@ITEM_HIGHLIGHT=0(0=None,1=Shape,2=Outline,3=Icon)]
-- DESCRIPTION: [HIGHLIGHT_ICON_IMAGEFILE$="imagebank\\icons\\hand.png"]
-- DESCRIPTION: <Sound0> for start sound.
-- DESCRIPTION: <Sound1> loop for moving sound.
-- DESCRIPTION: <Sound2> for end sound.

local module_misclib = require "scriptbank\\module_misclib"
local U = require "scriptbank\\utillib"
g_tEnt = {}

local slider			= {}
local prompt			= {}
local range				= {}
local slide_mode		= {}
local slide_type		= {}
local slide_close_delay	= {}
local slide_amount		= {}
local slide_speed		= {}
local slide_directon	= {}
local damage_amount		= {}
local prompt_display	= {}
local item_highlight	= {}
local highlight_icon	= {}

local status = {}
local hl_icon = {}
local hl_imgwidth = {}
local hl_imgheight = {}
local tEnt = {}
local moved = {}
local played = {}
local svol = {}
local open_time = {}
local damage_time = {}
local doonce = {}
local remote = {}

function slider_properties(e, prompt, range, slide_mode, slide_type, slide_direction, slide_close_delay, slide_amount, slide_speed, damage_amount, prompt_display, item_highlight, highlight_icon_imagefile)
	slider[e].prompt = prompt
	slider[e].range = range
	slider[e].slide_mode = slide_mode
	slider[e].slide_type = slide_type
	slider[e].slide_direction = slide_direction
	slider[e].slide_close_delay = slide_close_delay
	slider[e].slide_amount = slide_amount
	slider[e].slide_speed = slide_speed/5
	slider[e].damage_amount = damage_amount
	slider[e].prompt_display = prompt_display
	slider[e].item_highlight = item_highlight
	slider[e].highlight_icon = highlight_icon_imagefile
end

function slider_init(e)
	slider[e] = {}
	slider[e].prompt = "Press E to Activate"
	slider[e].range = 80
	slider[e].slide_mode = 1
	slider[e].slide_type = 1
	slider[e].slide_direction = 1
	slider[e].slide_close_delay = 1
	slider[e].slide_amount = 400
	slider[e].slide_speed = 3
	slider[e].damage_amount = 0
	slider[e].prompt_display = 1
	slider[e].item_highlight = 0
	slider[e].highlight_icon = "imagebank\\icons\\hand.png"

	status[e] = "init"
	tEnt[e] = 0
	g_tEnt = 0	
	moved[e] = 0
	played[e] = 0
	doonce[e] = 0
	remote[e] = 0
	svol[e] = 0
	open_time[e] = 0
	damage_time[e] = math.huge
end

function slider_main(e)

	if status[e] == "init" then
		if slider[e].item_highlight == 3 and slider[e].highlight_icon ~= "" then
			hl_icon[e] = CreateSprite(LoadImage(slider[e].highlight_icon))
			hl_imgwidth[e] = GetImageWidth(LoadImage(slider[e].highlight_icon))
			hl_imgheight[e] = GetImageHeight(LoadImage(slider[e].highlight_icon))
			SetSpriteSize(hl_icon[e],-1,-1)
			SetSpriteDepth(hl_icon[e],100)
			SetSpriteOffset(hl_icon[e],hl_imgwidth[e]/2.0, hl_imgheight[e]/2.0)
			SetSpritePosition(hl_icon[e],500,500)
		end	
		status[e] = "start"
	end	
	
	if GetPlayerDistance(e) < slider[e].range and slider[e].slide_mode == 1 and status[e] == "start" then
		--pinpoint select object--
		module_misclib.pinpoint(e,slider[e].range,slider[e].item_highlight,hl_icon[e])
		tEnt[e] = g_tEnt
		--end pinpoint select object--
		if GetPlayerDistance(e) < slider[e].range and tEnt[e] == e and GetEntityVisibility(e) == 1 then
			if slider[e].prompt_display == 1 then TextCenterOnX(50,54,1,slider[e].prompt) end
			if slider[e].prompt_display == 2 then Prompt(slider[e].prompt) end		
			if g_KeyPressE == 1 then
				status[e] = "opening"
				if played[e] == 0 then
					PlaySound(e,0)
					played[e] = 1
				end
				SetActivated(e,1)
				played[e] = 0
			end
		end	
	end
	if slider[e].slide_mode == 2 and remote[e] == 0 then 
		status[e] = "opening"
		if played[e] == 0 then
			PlaySound(e,0)
			played[e] = 1
		end
		played[e] = 0
		remote[e] = 1
	end

	if status[e] == "open" then
		if slider[e].slide_type == 1 then
			if slider[e].slide_close_delay > 0 then
				if GetTimer(e) > open_time[e] then status[e] = "closing" end
			end
		end
		if slider[e].slide_type == 2 then
			status[e] = "locked"
			SetActivated(e,0)
		end
		if slider[e].slide_type == 3 then
			if slider[e].slide_close_delay > 0 then
				if GetTimer(e) > open_time[e] then status[e] = "closing" end
			end
		end
	end
	if status[e] == "closed" and slider[e].slide_type == 1 then status[e] = "start" end
	if status[e] == "closed" and slider[e].slide_type == 3 then
		if slider[e].slide_close_delay > 0 then
			if GetTimer(e) > open_time[e] then status[e] = "opening" end
		end
	end

	if g_Entity[e].activated == 1 then
		svol[e] = (3000-GetPlayerDistance(e))/30
		SetSoundVolume(svol[e])
		if doonce[e] == 0 then
			damage_time[e] = g_Time + 100
			doonce[e] = 1
		end
		if status[e] == "opening" then
			if played[e] == 0 then
				LoopSound(e,1)
				played[e] = 1
			end
			if moved[e] < slider[e].slide_amount then
				GravityOff(e)
				CollisionOff(e)
				if slider[e].slide_direction == 1 then
					SetPosition(e,g_Entity[e]['x'] + slider[e].slide_speed,g_Entity[e]['y'],g_Entity[e]['z'])
					ResetPosition(e,g_Entity[e]['x'] + slider[e].slide_speed,g_Entity[e]['y'],g_Entity[e]['z'])
				elseif slider[e].slide_direction == 2 then
					SetPosition(e,g_Entity[e]['x'] - slider[e].slide_speed,g_Entity[e]['y'],g_Entity[e]['z'])
					ResetPosition(e,g_Entity[e]['x'] - slider[e].slide_speed,g_Entity[e]['y'],g_Entity[e]['z'])
				elseif slider[e].slide_direction == 3 then
					SetPosition(e,g_Entity[e]['x'],g_Entity[e]['y']+slider[e].slide_speed,g_Entity[e]['z'])
					ResetPosition(e,g_Entity[e]['x'],g_Entity[e]['y']+slider[e].slide_speed,g_Entity[e]['z'])
				elseif slider[e].slide_direction == 4 then
					SetPosition(e,g_Entity[e]['x'],g_Entity[e]['y']-slider[e].slide_speed,g_Entity[e]['z'])
					ResetPosition(e,g_Entity[e]['x'],g_Entity[e]['y']-slider[e].slide_speed,g_Entity[e]['z'])
				elseif slider[e].slide_direction == 5 then
					SetPosition(e,g_Entity[e]['x'],g_Entity[e]['y'],g_Entity[e]['z']+slider[e].slide_speed)
					ResetPosition(e,g_Entity[e]['x'],g_Entity[e]['y'],g_Entity[e]['z']+slider[e].slide_speed)
				elseif slider[e].slide_direction == 6 then
					SetPosition(e,g_Entity[e]['x'],g_Entity[e]['y'],g_Entity[e]['z']-slider[e].slide_speed)
					ResetPosition(e,g_Entity[e]['x'],g_Entity[e]['y'],g_Entity[e]['z']-slider[e].slide_speed)
				end
				CollisionOn(e)
				GravityOn(e)
				moved[e] = moved[e] + slider[e].slide_speed
				if moved[e] >= slider[e].slide_amount then moved[e] = slider[e].slide_amount end
			else
				status[e] = "open"
				StopSound(e,1)
				PlaySound(e,0)
				open_time[e] = GetTimer(e) + (slider[e].slide_close_delay * 1000)
			end
		end

		if status[e] == "closing" then
			SetSoundVolume(svol[e])
			if played[e] == 1 then
				LoopSound(e,1)
				played[e] = 0
			end
			if moved[e] > 0 then
				GravityOff(e)
				CollisionOff(e)
				if slider[e].slide_direction == 1 then
					SetPosition(e,g_Entity[e]['x'] - slider[e].slide_speed,g_Entity[e]['y'],g_Entity[e]['z'])
					ResetPosition(e,g_Entity[e]['x'] - slider[e].slide_speed,g_Entity[e]['y'],g_Entity[e]['z'])
				elseif slider[e].slide_direction == 2 then
					SetPosition(e,g_Entity[e]['x'] + slider[e].slide_speed,g_Entity[e]['y'],g_Entity[e]['z'])
					ResetPosition(e,g_Entity[e]['x'] + slider[e].slide_speed,g_Entity[e]['y'],g_Entity[e]['z'])
				elseif slider[e].slide_direction == 3 then
					SetPosition(e,g_Entity[e]['x'],g_Entity[e]['y']-slider[e].slide_speed,g_Entity[e]['z'])
					ResetPosition(e,g_Entity[e]['x'],g_Entity[e]['y']-slider[e].slide_speed,g_Entity[e]['z'])
				elseif slider[e].slide_direction == 4 then
					SetPosition(e,g_Entity[e]['x'],g_Entity[e]['y']+slider[e].slide_speed,g_Entity[e]['z'])
					ResetPosition(e,g_Entity[e]['x'],g_Entity[e]['y']+slider[e].slide_speed,g_Entity[e]['z'])
				elseif slider[e].slide_direction == 5 then
					SetPosition(e,g_Entity[e]['x'],g_Entity[e]['y'],g_Entity[e]['z']-slider[e].slide_speed)
					ResetPosition(e,g_Entity[e]['x'],g_Entity[e]['y'],g_Entity[e]['z']-slider[e].slide_speed)
				elseif slider[e].slide_direction == 6 then
					SetPosition(e,g_Entity[e]['x'],g_Entity[e]['y'],g_Entity[e]['z']+slider[e].slide_speed)
					ResetPosition(e,g_Entity[e]['x'],g_Entity[e]['y'],g_Entity[e]['z']+slider[e].slide_speed)
				end
				CollisionOn(e)
				GravityOn(e)
				moved[e] = moved[e] - slider[e].slide_speed
				if moved[e] <= 0 then moved[e] = 0 end
			else
				status[e] = "closed"
				StopSound(e,1)
				PlaySound(e,2)
				open_time[e] = GetTimer(e) + (slider[e].slide_close_delay * 1000)
			end
		end
		if GetPlayerDistance(e) < slider[e].range then
			if g_Time > damage_time[e] then HurtPlayer(-1,slider[e].damage_amount) end
			damage_time[e] = g_Time + 100
		end
	end
end