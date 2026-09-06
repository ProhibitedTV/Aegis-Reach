-- DESCRIPTION: The object will destroy when activated.

function activate_to_destroy_init(e)
end
 
function activate_to_destroy_main(e)
	if g_Entity[e]['activated'] == 1 then 
		SetEntityHealth(e,0)
		ActivateIfUsed(e)
		Destroy(e)
	end
end