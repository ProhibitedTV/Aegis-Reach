-- LUA Script - precede every function and global member with lowercase name of script + '_main'
-- Switch_Sequence v3 by Necrym59
-- DESCRIPTION: Will create a switch to an ActivateIfUsed link when completed in the correct order.
-- DESCRIPTION: [TOTAL_SWITCHES=1(1,5)] in group
-- DESCRIPTION: [SWITCH_NUMBER=1(1,5)] this switch number
-- DESCRIPTION: [SWITCH_RESET=5(1,20)] seconds before reset to off
-- DESCRIPTION: [USE_RANGE=60 (1,100)] distance to use
-- DESCRIPTION: [USE_PROMPT$="E to use"]
-- DESCRIPTION: [@PROMPT_DISPLAY=1(1=Local,2=Screen)]
-- DESCRIPTION: [@ITEM_HIGHLIGHT=0(0=None,1=Shape,2=Outline,3=Icon)]
-- DESCRIPTION: [HIGHLIGHT_ICON_IMAGEFILE$="imagebank\\icons\\hand.png"]
-- DESCRIPTION: <Sound0> when switch activated
-- DESCRIPTION: <Sound1> when completed

local module_misclib = require "scriptbank\\module_misclib"
local U = require "scriptbank\\utillib"
g_tEnt = {}
g_SwitchesSequenced = 0

local switch_seq 		= {}
local total_switches	= {}
local switch_number		= {}
local switch_reset		= {}
local use_range			= {}
local use_prompt		= {}
local prompt_display	= {}
local item_highlight	= {}
local highlight_icon	= {}

local switch_seq_active 	= {}
local doonce 				= {}
local tEnt 					= {}
local selectobj 			= {}
local item_highlight		= {}
local reset					= {}
local completed				= {}
local status 				= {}
local hl_icon 				= {}
local hl_imgwidth			= {}
local hl_imgheight			= {}

function switch_sequence_properties(e, total_switches, switch_number, switch_reset, use_range, use_prompt, prompt_display, item_highlight, highlight_icon_imagefile)
	switch_seq[e].total_switches = total_switches
	switch_seq[e].switch_number = switch_number
	switch_seq[e].switch_reset = switch_reset
	switch_seq[e].use_range = use_range
	switch_seq[e].use_prompt = use_prompt
	switch_seq[e].prompt_display = prompt_display
	switch_seq[e].item_highlight = item_highlight
	switch_seq[e].highlight_icon = highlight_icon_imagefile
end 

function switch_sequence_init(e)
	switch_seq[e] = {}
	switch_seq[e].total_switches = 1	
	switch_seq[e].switch_number = 1
	switch_seq[e].switch_reset = 5	
	switch_seq[e].use_range = 70
	switch_seq[e].use_prompt = "E to use"
	switch_seq[e].prompt_display = 1
	switch_seq[e].item_highlight = 0
	switch_seq[e].highlight_icon = "imagebank\\icons\\hand.png"
	
	g_SwitchesSequenced = 0
	status[e] = "init"	
	hl_icon[e] = 0
	hl_imgwidth[e] = 0
	hl_imgheight[e] = 0		
	doonce[e] = 0
	tEnt[e] = 0
	g_tEnt = 0
	reset[e] = math.huge
	completed[e] = 0
	selectobj[e] = 0
	--Set switch to off
	SetAnimationName(e,"off")
	PlayAnimation(e)					
	StopAnimation(e)
end
	 
function switch_sequence_main(e)

	if status[e] == "init" then
		if switch_seq[e].item_highlight == 3 and switch_seq[e].highlight_icon ~= "" then
			hl_icon[e] = CreateSprite(LoadImage(switch_seq[e].highlight_icon))
			hl_imgwidth[e] = GetImageWidth(LoadImage(switch_seq[e].highlight_icon))
			hl_imgheight[e] = GetImageHeight(LoadImage(switch_seq[e].highlight_icon))
			SetSpriteSize(hl_icon[e],-1,-1)
			SetSpriteDepth(hl_icon[e],100)
			SetSpriteOffset(hl_icon[e],hl_imgwidth[e]/2.0, hl_imgheight[e]/2.0)
			SetSpritePosition(hl_icon[e],500,500)
		end
		status[e] = "endinit"
	end		

	local PlayerDist = GetPlayerDistance(e)
	if PlayerDist <= switch_seq[e].use_range then
		--pinpoint select object--
		module_misclib.pinpoint(e,switch_seq[e].use_range,switch_seq[e].item_highlight,hl_icon[e])
		tEnt[e] = g_tEnt
		--end pinpoint select object--			
	end	
	if PlayerDist <= switch_seq[e].use_range and tEnt[e] == e and GetEntityVisibility(e) == 1 then
		if switch_seq[e].prompt_display == 1 then PromptLocal(e,switch_seq[e].use_prompt) end
		if switch_seq[e].prompt_display == 2 then Prompt(switch_seq[e].use_prompt) end
		if g_KeyPressE == 1 then			
			if switch_seq[e].switch_number == g_SwitchesSequenced+1 then
				g_SwitchesSequenced = switch_seq[e].switch_number
				if g_SwitchesSequenced == switch_seq[e].total_switches and completed[e] == 0 then
					ActivateIfUsed(e)
					completed[e] = 1
				end	
			end
			if doonce[e] == 0 then 
				SetActivated(e,1)
				SetAnimationName(e,"on")
				PlayAnimation(e)					
				StopAnimation(e)
				PlaySound(e,0)
				PerformLogicConnections(e)
				reset[e] = g_Time + (switch_seq[e].switch_reset * 1000)
				doonce[e] = 1
			end
		end
	end
	if g_Time > reset[e] then
		if doonce[e] == 1 and g_SwitchesSequenced ~= switch_seq[e].total_switches then
			SetAnimationName(e,"off")
			PlayAnimation(e)					
			StopAnimation(e)
			PlaySound(e,0)
			PerformLogicConnections(e)
			SetActivated(e,0)
			g_SwitchesSequenced = 0
			doonce[e] = 0
		end	
	end	
end
