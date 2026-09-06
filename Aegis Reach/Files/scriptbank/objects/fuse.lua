-- LUA Script - precede every function and global member with lowercase name of script + '_main'
-- Fuse v8 by Necrym59
-- DESCRIPTION: The attached object will give the player a fuse if collected.
-- DESCRIPTION: [PROMPT_TEXT$="E to collect"]
-- DESCRIPTION: [PICKUP_RANGE=80(1,100)]
-- DESCRIPTION: [@PICKUP_STYLE=1(1=Ranged, 2=Accurate)]
-- DESCRIPTION: [COLLECTED_TEXT$="Collected a fuse"]
-- DESCRIPTION: [@PROMPT_DISPLAY=1(1=Local,2=Screen)]
-- DESCRIPTION: [@ITEM_HIGHLIGHT=0(0=None,1=Shape,2=Outline,3=Icon)]
-- DESCRIPTION: [HIGHLIGHT_ICON_IMAGEFILE$="imagebank\\icons\\pickup.png"]
-- DESCRIPTION: Play the audio <Sound0> when picked up.

local module_misclib = require "scriptbank\\module_misclib"
local U = require "scriptbank\\utillib"
g_tEnt = {}

g_fuses = {}
local fuse				= {}
local prompt_text		= {}
local pickup_range 		= {}
local pickup_style 		= {}
local collected_text 	= {}
local prompt_display 	= {}
local item_highlight 	= {}
local highlight_icon	= {}
	
local collected			= {}
local tEnt				= {}
local selectobj 		= {}
local hl_icon			= {}
local hl_imgwidth		= {}
local hl_imgheight		= {}
local status			= {}		

function fuse_properties(e, prompt_text, pickup_range, pickup_style, collected_text, prompt_display, item_highlight, highlight_icon_imagefile)
	fuse[e].prompt_text = prompt_text
	fuse[e].pickup_range = pickup_range
	fuse[e].pickup_style = pickup_style
	fuse[e].collected_text = collected_text
	fuse[e].prompt_display = prompt_display
	fuse[e].item_highlight = item_highlight
	fuse[e].highlight_icon = highlight_icon_imagefile
end

function fuse_init_name(e)	
	fuse[e] = {}
	fuse[e].prompt_text = "E to collect"
	fuse[e].pickup_range = 80
	fuse[e].pickup_style = 1
	fuse[e].collected_text = "Collected a fuse"
	fuse[e].prompt_display = 1
	fuse[e].item_highlight = 0
	fuse[e].highlight_icon = "imagebank\\icons\\pickup.png"
	g_fuses = 0
	collected[e] = 0
	tEnt[e] = 0
	g_tEnt = 0
	selectobj[e] = 0
	status[e] = "init"
	hl_icon[e] = 0
	hl_imgwidth[e] = 0
	hl_imgheight[e] = 0	
end

function fuse_main(e)
	
	if status[e] == "init" then
		if fuse[e].item_highlight == 3 and fuse[e].highlight_icon ~= "" then
			hl_icon[e] = CreateSprite(LoadImage(fuse[e].highlight_icon))
			hl_imgwidth[e] = GetImageWidth(LoadImage(fuse[e].highlight_icon))
			hl_imgheight[e] = GetImageHeight(LoadImage(fuse[e].highlight_icon))
			SetSpriteSize(hl_icon[e],-1,-1)
			SetSpriteDepth(hl_icon[e],100)
			SetSpriteOffset(hl_icon[e],hl_imgwidth[e]/2.0, hl_imgheight[e]/2.0)
			SetSpritePosition(hl_icon[e],500,500)
		end
		status[e] = "endinit"
	end

	PlayerDist = GetPlayerDistance(e)

	if fuse[e].pickup_style == 1 then
		if PlayerDist < fuse[e].pickup_range and collected[e] == 0 then
			if GetEntityCollectable(e) == 0 then
				if fuse[e].prompt_display == 1 then PromptLocal(e,fuse[e].collected_text) end
				if fuse[e].prompt_display == 2 then Prompt(fuse[e].collected_text) end			
				g_fuses = e	
				Hide(e)
				CollisionOff(e)
				collected[e] = 1
				PlaySound(e,0)
				PerformLogicConnections(e)
				PromptDuration(fuse[e].collected_text,2000)
			end
			if GetEntityCollectable(e) == 1 or GetEntityCollectable(e) == 2 then -- if collectable or resource
				if fuse[e].prompt_display == 1 then PromptLocal(e,fuse[e].collected_text) end
				if fuse[e].prompt_display == 2 then Prompt(fuse[e].collected_text) end			
				g_fuses = e
				Hide(e)
				CollisionOff(e)
				SetEntityCollected(e,1)
				PlaySound(e,0)
				collected[e] = 1
				PerformLogicConnections(e)
			end
		end	
	end	
	
	if fuse[e].pickup_style == 2 then
		if PlayerDist <= fuse[e].pickup_range and collected[e] == 0 then
			--pinpoint select object--
			module_misclib.pinpoint(e,fuse[e].pickup_range, fuse[e].item_highlight,hl_icon[e])
			tEnt[e] = g_tEnt
			--end pinpoint select object--
		end
		if PlayerDist < fuse[e].pickup_range and tEnt[e] == e then
			if fuse[e].prompt_display == 1 then PromptLocal(e,fuse[e].prompt_text) end
			if fuse[e].prompt_display == 2 then Prompt(fuse[e].prompt_text) end	
			if g_KeyPressE == 1 then
				if GetEntityCollectable(tEnt[e]) == 0 then
					if fuse[e].prompt_display == 1 then PromptLocal(e,fuse[e].collected_text) end
					if fuse[e].prompt_display == 2 then Prompt(fuse[e].collected_text) end
					PlaySound(e,0)
					PerformLogicConnections(e)
					Hide(e)
					CollisionOff(e)
					g_fuses = e
					collected[e] = 1
					Destroy(e)
				end
				if GetEntityCollectable(tEnt[e]) == 1 or GetEntityCollectable(tEnt[e]) == 2 then  -- if collectable or resource
					if fuse[e].prompt_display == 1 then PromptLocal(e,fuse[e].prompt_text) end
					if fuse[e].prompt_display == 2 then Prompt(fuse[e].prompt_text) end
					if g_KeyPressE == 1 then				
						if fuse[e].prompt_display == 1 then PromptLocal(e,fuse[e].collected_text) end
						if fuse[e].prompt_display == 2 then PromptDuration(fuse[e].collected_text,2000) end
						SetEntityCollected(tEnt[e],1)
						PlaySound(e,0)
						PerformLogicConnections(e)
						Hide(e)
						CollisionOff(e)
						g_fuses = e
						collected[e] = 1
					end
				end
			end	
		end
	end		
end

