---------------------------------------------------------------------
--   cg_shake.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.   --
---------------------------------------------------------------------
-- cinematic shake script, part of the Cine Guru GameGuru pack.
--
-- For instructions on use see Cine Guru documentation.
---------------------------------------------------------------------
local lower = string.lower

local shakes  = {}

local df_typ      = 'add'
local df_filmtime = 0.5
local df_trauma   = 50
local df_period   = 50
local df_fade     = 2

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: Cine Guru Shake. 
-- DESCRIPTION: Shake type [@MODE=1(1=Add,2=Set)]
-- DESCRIPTION: Trigger time (seconds) [DELAY#=0.5]
-- DESCRIPTION: Trauma amount [TRAUMA#=50(0,100)]
-- DESCRIPTION: Period [PERIOD#=50(1,2000)]
-- DESCRIPTION: Fade   [FADE#=2(0,10)]
local shakeTypes = {'add','set'}
function cg_shake_properties( e, typ, ftime, trauma, period, fade )
	local sh = shakes[ e ]
	if sh == nil then return end
	local styp = shakeTypes[ typ ]
	if styp   ~= df_typ      then sh.typ      = styp   end
	if ftime  ~= df_filmtime then sh.filmtime = ftime * 1000 end
	if trauma ~= df_trauma   then sh.trauma   = trauma end
	if period ~= df_period   then sh.period   = period end
	if fade   ~= df_fade     then sh.fade     = fade   end
end				   
-----------------------------------------------------

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

function cg_shake_init( e )
	shakes[ e ] = { state    = "init", 
	                typ      = df_typ, 
					filmtime = df_filmtime * 1000,
					trauma   = df_trauma, 
					period   = df_period, 
					fade     = df_fade,
					cnode    = 0, 
					node     = 0,
					ttime    = 0
				  }					 
	Hide( e )
	CollisionOff( e )
end

function CG_IsShake( e )
	return shakes[ e ] ~= nil
end

C.Register( 'shake', CG_IsShake )

local function doShake( shake )
	if shake.typ == 'add' then
		CG_AddTrauma( shake.trauma )
		CG_AddPeriod( shake.period )
		CG_AddFade( shake.fade, true )
	elseif
	   shake.typ == 'set' then
		CG_SetTrauma( shake.trauma )
		CG_SetPeriod( shake.period )
	end
	shake.state = 'done'
end

function cg_shake_main( e )
	if CG_AddTrauma == nil then return end

	local shake = shakes[ e ]
	if shake == nil then return end

    if shake.state == 'done' then
		return
	
	elseif
	   shake.state == 'init' then
		local links = C.GetEntityLinks( e, { 'camera', 'node' } )
		-- can only be connected to one camera or 
		-- one node at present
		for _, v in pairs( links ) do
			if C.isCamera( v ) then
				shake.camera = v
				shake.state  = 'idle'
				break
				
			elseif 
			   C.isNode( v ) then
				local node = CG_GetNode( v )
				shake.camera = node.camera
				shake.node   = node.node
				shake.state  = 'idle'
				break
			
			else
				Show( e )
				shake.state = 'error'
			end
		end
				
	elseif
	   shake.state == 'idle' then
		local camera, cnode, ti, dur = CG_GetActiveCamera()
		
		if camera == shake.camera then
			if shake.node == 0 then 
				if shake.filmtime <= dur and
				   ti > shake.filmtime then
					doShake( shake )
				else
					if cnode > 1 and 
					   shake.cnode ~= cnode then
						shake.cnode = cnode
						shake.ttime = shake.ttime + dur
					end
					if shake.ttime + ti > shake.filmtime then
						doShake( shake )
					end
				end
				
			elseif
		       shake.node == cnode and
		       ti > shake.filmtime then
				doShake( shake )
			end
		end
	
	elseif
	   shake.state == 'error' then
		PromptLocal( e, "CineGuru: Not correctly connected" ) 
	end
end
 

	
	


