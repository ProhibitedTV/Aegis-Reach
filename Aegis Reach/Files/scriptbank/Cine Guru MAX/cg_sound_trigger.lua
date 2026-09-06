-----------------------------------------------------------------------------
--   cg_sound_trigger.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.   --
-----------------------------------------------------------------------------
-- timer-delayed sound playing script, part of the Cine Guru GameGuru pack.
--
-- For instructions on use see Cine Guru documentation.
-----------------------------------------------------------------------------
local lower = string.lower

local triggered = {}

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: Cine Guru Sound trigger script. 
-- DESCRIPTION: Play mode play/loop [@PMODE=1(1=Play,2=Loop)] 
-- DESCRIPTION: Trigger time (seconds) [TI#=0]
-- DESCRIPTION: <Sound0> 
local pmodes = {'play', 'loop'}
function cg_sound_trigger_properties( e, pmode, ti )
	local trigger = triggered[ e ]
	if trigger == nil then return end
	trigger.playmode = pmodes[ pmode ]
	trigger.tTime = ti * 1000 
end				   
-----------------------------------------------------	

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

function cg_sound_trigger_init( e )
	triggered[ e ] = { state = 'init' }
    Hide( e )
	CollisionOff( e )
end

function CG_IsSound( e )
	return triggered[ e ] ~= nil
end

C.Register( 'sound', CG_IsSound )

function cg_sound_trigger_main( e )
	if CG_GetActiveCamera == nil then return end
	
	local trigger = triggered[ e ]
	if trigger == nil then return end

	if trigger.state == 'init' then
		local links = C.GetEntityLinks( e, { 'camera' } )
		-- can only be connected to one camera or 
		-- one node at present
		for _, v in pairs( links ) do
			if C.isCamera( v ) then
				trigger.camera = v
				trigger.node   = 0
				trigger.state  = 'idle'
				break
			elseif 
			   C.isNode( v ) then
				local node = CG_GetNode( v )
				trigger.camera = node.camera
				trigger.node   = node.node
				trigger.state  = 'idle'
				break
			end
		end	
		if trigger.camera == nil then
			Show( e )
			trigger.state = 'no camera'
			return
		end		-- can only be connected to one camera or node at present
		
    elseif 
	   trigger.state == 'idle' then  
		local camera, cnode = CG_GetActiveCamera()
		if camera == trigger.camera  and
		   ( trigger.node == 0       or
		     trigger.node == cnode ) then
			trigger.timer = C.getTime() + trigger.tTime
			trigger.state = 'wait'
		end
	end
	
    if trigger.state == 'wait' then
		if C.checkForAbort( e ) then 
			trigger.state = 'aborted'
			Destroy( e )
			return
		elseif
		   C.getTime() >= trigger.timer then
			if trigger.playmode == 'play' then
				PlaySound( e, 0 )
				trigger.state = 'playing'
			end 
			if trigger.playmode == 'loop' then
				LoopSound( e, 0 )
				trigger.state = 'looping'
			end
		end 
	
	elseif 
	   trigger.state == 'looping' and
		( C.checkForAbort( e ) or
		  CG_GetActiveCamera() ~= trigger.camera ) then
		StopSound( e, 0 )
		trigger.state = 'done'
		Destroy( e )

	elseif
	   trigger.state == 'playing' and
	   C.checkForAbort( e ) then
		StopSound( e, 0 )
		trigger.state = 'done'
		Destroy( e )  

	elseif 
	   trigger.state == 'no camera' then
		PromptLocal( e, "CineGuru: Sound trigger - no camera attached" )
    end
end