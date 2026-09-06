-- LUA Script - precede every function and global member with lowercase name of script + '_main'
-- Task Tool v11 by Necrym59
-- DESCRIPTION: This object will give the player a designated task-tool if collected.
-- DESCRIPTION: [PROMPT_TEXT$="E to collect"]
-- DESCRIPTION: [PICKUP_RANGE=90(1,100)]
-- DESCRIPTION: [@PICKUP_STYLE=1(1=Ranged, 2=Accurate)]
-- DESCRIPTION: [@TOOL_TYPE=1(1=Crowbar, 2=Screwdriver, 3=Spanner, 4=Cutter, 5=Named Tool)]
-- DESCRIPTION: [TOOL_NAME$=""] Name of entity for Named Tool
-- DESCRIPTION: [@PROMPT_DISPLAY=1(1=Local,2=Screen)]
-- DESCRIPTION: [@ITEM_HIGHLIGHT=0(0=None,1=Shape,2=Outline,3=Icon)]
-- DESCRIPTION: [HIGHLIGHT_ICON_IMAGEFILE$="imagebank\\icons\\pickup.png"]
-- DESCRIPTION: Play the audio <Sound0> when picked up.

local module_misclib = require "scriptbank\\module_misclib"
local U = require "scriptbank\\utillib"
g_tEnt = {}

g_tasktool				= {}
g_tasktoolname			= {}
local tasktool			= {}
local prompt_text		= {}
local pickup_range 		= {}
local pickup_style 		= {}
local tool_type			= {}
local tool_name 		= {}
local prompt_display	= {}
local item_highlight	= {}
local highlight_icon	= {}

local collected 		= {}
local status 			= {}
local hl_icon 			= {}
local hl_imgwidth		= {}
local hl_imgheight		= {}
local tEnt				= {}
local selectobj			= {}

function task_tool_properties(e, prompt_text, pickup_range, pickup_style, tool_type, tool_name, prompt_display, item_highlight, highlight_icon_imagefile)
	tasktool[e].prompt_text = prompt_text
	tasktool[e].pickup_range = pickup_range
	tasktool[e].pickup_style = pickup_style
	tasktool[e].tool_type = tool_type
	tasktool[e].tool_name = tool_name
	tasktool[e].prompt_display = prompt_display
	tasktool[e].item_highlight = item_highlight
	tasktool[e].highlight_icon = highlight_icon_imagefile
end

function task_tool_init(e)
	tasktool[e] = {}
	tasktool[e].prompt_text = "to collect"
	tasktool[e].pickup_range = 80
	tasktool[e].pickup_style = 1
	tasktool[e].tool_type = 1
	tasktool[e].tool_name = ""
	tasktool[e].prompt_display = 1
	tasktool[e].item_highlight = 0
	tasktool[e].highlight_icon = "imagebank\\icons\\pickup.png"
	
	g_tasktool = 0
	g_tasktoolname = ""
	g_tEnt = 0
	collected[e] = 0
	tEnt[e] = 0
	selectobj[e] = 0
	status[e] = "init"
	hl_icon[e] = 0
	hl_imgwidth[e] = 0
	hl_imgheight[e] = 0		
end

function task_tool_main(e)

	if status[e] == "init" then
		if tasktool[e].item_highlight == 3 and tasktool[e].highlight_icon ~= "" then
			hl_icon[e] = CreateSprite(LoadImage(tasktool[e].highlight_icon))
			hl_imgwidth[e] = GetImageWidth(LoadImage(tasktool[e].highlight_icon))
			hl_imgheight[e] = GetImageHeight(LoadImage(tasktool[e].highlight_icon))
			SetSpriteSize(hl_icon[e],-1,-1)
			SetSpriteDepth(hl_icon[e],100)
			SetSpriteOffset(hl_icon[e],hl_imgwidth[e]/2.0, hl_imgheight[e]/2.0)
			SetSpritePosition(hl_icon[e],500,500)
		end		
		if tasktool[e].tool_type == 1 then tasktool[e].tool_name = "Crowbar" end
		if tasktool[e].tool_type == 2 then tasktool[e].tool_name = "Screwdriver" end
		if tasktool[e].tool_type == 3 then tasktool[e].tool_name = "Spanner" end
		if tasktool[e].tool_type == 4 then tasktool[e].tool_name = "Cutter" end
		if tasktool[e].tool_type == 5 then tasktool[e].tool_name = tasktool[e].tool_name end
		status[e] = "endinit"
	end

	local PlayerDist = GetPlayerDistance(e)

	if tasktool[e].pickup_style == 1 then
		if PlayerDist < tasktool[e].pickup_range and collected[e] == 0 then
			if GetEntityCollectable(tEnt[e]) == 0 then
				if tasktool[e].prompt_display == 1 then PromptLocal(e,tasktool[e].tool_name.. " collected") end
				if tasktool[e].prompt_display == 2 then Prompt(tasktool[e].tool_name.. " collected") end
				PlaySound(e,0)
				PerformLogicConnections(e)
				g_tasktool = tasktool[e].tool_type
				g_tasktoolname = tasktool[e].tool_name
				collected[e] = 1
				Destroy(e)
			end
			if GetEntityCollectable(tEnt[e]) == 1 or GetEntityCollectable(tEnt[e]) == 2 then
				PlaySound(e,0)
				PerformLogicConnections(e)
				g_tasktool = tasktool[e].tool_type
				g_tasktoolname = tasktool[e].tool_name
				SetEntityCollected(tEnt[e],1)
				collected[e] = 1
			end
		end
	end

	if tasktool[e].pickup_style == 2 and PlayerDist < tasktool[e].pickup_range then
		--pinpoint select object--
		module_misclib.pinpoint(e,tasktool[e].pickup_range,tasktool[e].item_highlight,hl_icon[e])
		tEnt[e] = g_tEnt
		--end pinpoint select object--
		if PlayerDist < tasktool[e].pickup_range and collected[e] == 0 and tEnt[e] == e and GetEntityVisibility(e) == 1 then
			if tasktool[e].prompt_display == 1 then PromptLocal(e,tasktool[e].prompt_text) end
			if tasktool[e].prompt_display == 2 then Prompt(tasktool[e].prompt_text) end
			if GetEntityCollectable(tEnt[e]) == 0 then
				if g_KeyPressE == 1 then
					if tasktool[e].prompt_display == 1 then PromptLocal(e,tasktool[e].tool_name.. " collected") end
					if tasktool[e].prompt_display == 2 then Prompt(tasktool[e].tool_name.. " collected") end
					PlaySound(e,0)
					PerformLogicConnections(e)
					g_tasktool = tasktool[e].tool_type
					g_tasktoolname = tasktool[e].tool_name
					collected[e] = 1
					Destroy(e)
				end
			end
			if GetEntityCollectable(tEnt[e]) == 1 or GetEntityCollectable(tEnt[e]) == 2 then
				if g_KeyPressE == 1 then
					if tasktool[e].prompt_display == 1 then PromptLocal(e,tasktool[e].tool_name.. " collected") end
					if tasktool[e].prompt_display == 2 then Prompt(tasktool[e].tool_name.. " collected") end
					PlaySound(e,0)
					PerformLogicConnections(e)
					g_tasktool = tasktool[e].tool_type
					g_tasktoolname = tasktool[e].tool_name
					SetEntityCollected(tEnt[e],1)
					collected[e] = 1
				end
			end
		end
	end
end

