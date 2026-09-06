---------------------------------------------------------------------
--   cg_mark.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.   --
---------------------------------------------------------------------
-- cinematic mark script, part of the Cine Guru GameGuru pack.
--
-- For instructions on use see Cine Guru documentation.
---------------------------------------------------------------------

local V = require "scriptbank\\vectlib"

local marks  = {}

local lower = string.lower

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: MAX Cine|Guru Mark Entity. 
-- DESCRIPTION: [YOffset=-50(-100,100)]
-- DESCRIPTION: [XOffset=0(-100,100)]
-- DESCRIPTION: [ZOffset=0(-100,100)]

function cg_mark_properties( e, yoff, xoff, zoff )
	xoff = xoff or 0
	zoff = zoff or 0
	local mark = marks[ e ]
	if mark == nil then return end
	mark.posOff = V.Create( xoff, yoff, zoff )
end				

function cg_mark_init_name( e, name )
	marks[ e ] = { name   = lower( name),
	               state  = 'init',
				   posOff = V.Create( 0, -50, 0 )
				 }
	Hide( e )
	CollisionOff( e )
end

function CG_GetMark( name )
	for k, v in pairs( marks ) do
		if v.state == 'ready' and 
		   v.name  ==  name   then
			return v.pos.x, v.pos.y, v.pos.z, 
			       v.ang.x, v.ang.y, v.ang.z
		end
	end
end

function CG_GetMarkWithOffset( name )
	for k, v in pairs( marks ) do
		if v.state == 'ready' and 
		   v.name  ==  name   then
		    local np = V.Add( v.pos, v.posOff )
			return k, v.obj, np.x, np.y, np.z
		end
	end
end

function cg_mark_main( e )
	local mark = marks[ e ]
	if mark == nil then return end

    if mark.state == 'init' then
		mark.obj   = g_Entity[ e ].obj
		local x, y, z, xa, ya, za = GetObjectPosAng( mark.obj )
		mark.pos = V.Create( x, y, z )
		mark.ang = V.Create( xa, ya, za )
		mark.state = 'ready'
	end
end
 

	
	


