-- LUA Script - precede every function and global member with lowercase name of script + '_main'
-- Switch_Timed v3 by Necrym59
-- DESCRIPTION: This object will be treated as a switch object for activating other objects or game elements with a timed reset delay.
-- DESCRIPTION: [USE_RANGE=60(1,100)] distance
-- DESCRIPTION: [USE_PROMPT$="E to use"]
-- DESCRIPTION: [@PROMPT_DISPLAY=1(1=Local,2=Screen)]
-- DESCRIPTION: [#RESET_DELAY=5.0(0.0,60.0)] seconds
-- DESCRIPTION: [@PROMPT_DISPLAY=1(1=Local,2=Screen)]
-- DESCRIPTION: [@ITEM_HIGHLIGHT=0(0=None,1=Shape,2=Outline,3=Icon)]
-- DESCRIPTION: [HIGHLIGHT_ICON_IMAGEFILE$="imagebank\\icons\\hand.png"]
-- DESCRIPTION: <Sound0> when switch activates/deactivates

local module_misclib = require "scriptbank\\module_misclib"
local U = require "scriptbank\\utillib"
g_tEnt = {}

local switchtm 			= {}
local use_range			= {}
local use_prompt		= {}
local prompt_display	= {}
local reset_delay		= {}
local prompt_display	= {}
local item_highlight	= {}
local highlight_icon	= {}

local doonce 			= {}
local swreset			= {}
local tEnt 				= {}
local selectobj 		= {}
local keypressed 		= {}
local status 			= {}
local hl_icon 			= {}
local hl_imgwidth		= {}
local hl_imgheight		= {}


function switch_timed_properties(e, use_range, use_prompt, prompt_display, reset_delay, prompt_display, item_highlight, highlight_icon_imagefile)
	switchtm[e].use_range = use_range
	switchtm[e].use_prompt = use_prompt
	switchtm[e].prompt_display = prompt_display
	switchtm[e].reset_delay = reset_delay
	switchtm[e].prompt_display = prompt_display
	switchtm[e].item_highlight = item_highlight
	switchtm[e].highlight_icon = highlight_icon_imagefile
end 

function switch_timed_init(e)
	switchtm[e] = {}
	switchtm[e].use_range = 70
	switchtm[e].use_prompt = "E to use"
	switchtm[e].prompt_display = 1
	switchtm[e].reset_delay = 20
	switchtm[e].prompt_display = 1
	switchtm[e].item_highlight = 0
	switchtm[e].highlight_icon = "imagebank\\icons\\hand.png"	
	
	status[e] = "init"	
	hl_icon[e] = 0
	hl_imgwidth[e] = 0
	hl_imgheight[e] = 0	
	keypressed[e] = 0
	doonce[e] = 0
	tEnt[e] = 0
	g_tEnt = 0
	selectobj[e] = 0
	swreset[e] = math.huge
end
	 
function switch_timed_main(e)		

	if status[e] == "init" then
		if switchtm[e].item_highlight == 3 and switchtm[e].highlight_icon ~= "" then
			hl_icon[e] = CreateSprite(LoadImage(switchtm[e].highlight_icon))
			hl_imgwidth[e] = GetImageWidth(LoadImage(switchtm[e].highlight_icon))
			hl_imgheight[e] = GetImageHeight(LoadImage(switchtm[e].highlight_icon))
			SetSpriteSize(hl_icon[e],-1,-1)
			SetSpriteDepth(hl_icon[e],100)
			SetSpriteOffset(hl_icon[e],hl_imgwidth[e]/2.0, hl_imgheight[e]/2.0)
			SetSpritePosition(hl_icon[e],500,500)
		end
		status[e] = "endinit"
	end

	local PlayerDist = GetPlayerDistance(e)
	if PlayerDist <= switchtm[e].use_range and keypressed[e] == 0 then
		--pinpoint select object--
		module_misclib.pinpoint(e,switchtm[e].use_range, switchtm[e].item_highlight,hl_icon[e])
		tEnt[e] = g_tEnt
		--end pinpoint select object--			
	end
	
	if PlayerDist <= switchtm[e].use_range and tEnt[e] == e and GetEntityVisibility(e) == 1 then
		if switchtm[e].prompt_display == 1 and keypressed[e] == 0 then PromptLocal(e,switchtm[e].use_prompt) end
		if switchtm[e].prompt_display == 2 and keypressed[e] == 0 then Prompt(switchtm[e].use_prompt) end	
		if g_KeyPressE == 1 then
			keypressed[e] = 1
			swreset[e] = g_Time + (switchtm[e].reset_delay*1000)
			if doonce[e] == 0 then 
				SetAnimationName(e,"on")
				PlayAnimation(e)					
				StopAnimation(e)
				PlaySound(e,0)
				PerformLogicConnections(e)
				doonce[e] = 1
			end
		end			
	end
	if g_Time > swreset[e] then	
		if doonce[e] == 1 then 
			SetAnimationName(e,"off")
			PlayAnimation(e)					
			StopAnimation(e)
			PlaySound(e,0)
			PerformLogicConnections(e)
			keypressed[e] = 0			
			doonce[e] = 0
		end
	end
end
