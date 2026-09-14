"""Retain only an inert compatibility marker for the retired FIRST LIGHT opener graph.

The insertion is now owned by firstlight_opening_native.lua from the mission HUD path.
All legacy `FL CG ARRIVAL ...` cameras are quarantined before this pass runs, so this
module must never try to rediscover or relink them.  Keeping the controller entity is
useful for stable authoring/entity counts and older validation/reporting surfaces, but
it has no camera relationships and cannot activate the insertion.
"""

MARKER=r'Aegis Reach\Supply Crate.fpe'
CHAIN_SCRIPT=r'aegis_reach\firstlight_cineguru_chain.lua'


def apply(build):
    build.add(MARKER,'FIRST LIGHT // CINEGURU NATIVE CHAIN',260,-9500,y=100,
              kind='controller',script=CHAIN_SCRIPT,
              **{'eleprof.physics':0,'eleprof.phyalways':1})
    return {
        'native_chain':False,
        'camera_count':0,
        'first_camera':None,
        'last_camera':None,
        'link_ids':[],
        'relationship_model':'disabled; HUD-native opening owns camera 0',
        'controller':'FIRST LIGHT // CINEGURU NATIVE CHAIN',
        'script':CHAIN_SCRIPT,
        'compatibility_marker_only':True,
    }
