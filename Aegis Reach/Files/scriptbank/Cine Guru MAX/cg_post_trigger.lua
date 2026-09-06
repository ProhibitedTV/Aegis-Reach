-----------------------------------------------------------------------------
--   cg_post_trigger.lua  Copyright C D Stapleton (AKA AmenMoses) 2022.   --
-----------------------------------------------------------------------------
-- post trigger script, part of the Cine Guru GameGuru pack.
--
-- For instructions on use see Cine Guru documentation.
---------------------------------------------------------------------
local lower = string.lower

local posts = {}

local GGsetLut = SetLutTo
local GGgetLut = GetLut

local currLut = nil

function SetLutTo( name )
	currLut = name
	GGsetLut( name )
end
	
function GetLut()
	if currLut ~= nil then return currLut end
	return GGgetLut()
end

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: Cine Guru post trigger script. 
-- DESCRIPTION: LUT to use [LUT$="none"]
-- DESCRIPTION: Trigger time (seconds) [TI=0]
-- DESCRIPTION: Duration (seconds) [DUR=0]

function cg_post_trigger_properties( e, LUT, ti, dur )
	local post = posts[ e ]
	if post == nil then return end
	if LUT  ~= "" then post.LUT  = LUT end
	if ti  > 0 then post.filmtime = ti  * 1000 end
	if dur > 0 then post.duration = dur * 1000 end
end				   
-----------------------------------------------------	

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

local find  = string.find
local sub   = string.sub

function cg_post_trigger_init( e )
	posts[ e ] = { state    = 'init' }
	Hide( e )
	CollisionOff( e )
end

function CG_IsPost( e )
	return posts[ e ] ~= nil
end

local function existingPost( e )
	for k, v in pairs( posts ) do
		if k ~= e and 
		   v.state == 'triggered' then
			return v
		end
	end
end

C.Register( 'post', CG_IsPost )

function cg_post_trigger_main( e )
	if CG_GetActiveCamera == nil then return end
	
	local this = posts[ e ]
		
	if this.state == 'init' then
		local links = C.GetEntityLinks( e, { 'camera', 'node' } )
		-- can only be connected to one camera or 
		-- one node at present
		for _, v in pairs( links ) do
			if C.isCamera( v ) then
				this.camera = v
				break

			elseif 
			   C.isNode( v ) then
				local node = CG_GetNode( v )
				this.camera = node.camera
				this.node   = node.node
				break
			
			else
				Show( e )
				this.state = 'error'
				return
			end
		end
		this.state  = 'idle'
		
	elseif
	   this.state == 'idle' then
		local camera, cnode, ti, dur = CG_GetActiveCamera()

		if camera == nil then
			if this.oldLUT ~= nil and
			   GetLut() ~= this.oldLUT then 
				SetLutTo( this.oldLUT )
				this.oldLUT = nil
			end

		elseif 
		   this.camera == nil then
			this.oldLUT = GetLut()
			if this.oldLUT ~= this.LUT then 
				SetLutTo( this.LUT )
				this.state = 'triggered'
			end
			
		elseif 
		   this.camera == camera then
			if ( this.node == nil or
				 this.node == cnode ) and
				( ti >= this.filmtime ) then
				if this.timer == nil and
				   this.duration ~= 0 then
					this.timer = C.getTime() + this.duration
				end
				
				local post = existingPost( e )
				local curLUT = GetLut()
				if post ~= nil then
					this.oldLUT = post.oldLUT
				else
					this.oldLUT = curLUT
				end
				if  curLUT ~= this.LUT then
					SetLutTo( this.LUT )
				end
				this.state = 'triggered'
			end
		end
		
	elseif
	   this.state == 'triggered' then
	    local camera = CG_GetActiveCamera()
		if C.checkForAbort( e )          or
		   camera == nil                 or
		   ( this.camera ~= nil     and 
		     camera ~= this.camera )     or
		   ( camera == this.camera  and
		     this.timer ~= nil      and
		     C.getTime() >= this.timer ) then

			if GetLut() ~= this.oldLUT then 
				SetLutTo( this.oldLUT )
				this.oldLUT = nil
			end
			if this.camera == nil then
				this.state = 'idle'
			else
				this.state = 'done'
			end
		end
	end
end