"""Retain an inert compatibility marker for the retired FIRST LIGHT CineGuru opener.

FIRST LIGHT's insertion is now a hard native replacement owned by
firstlight_opening_native.lua.  The seventeen legacy `FL CG ARRIVAL ...` camera
entities are quarantined by firstlight_opening_director before this pass runs.

For compatibility with older reports/tests we still author the historical chain
controller, but when the hard-replacement state is present it has no camera graph
to activate.  A partially removed legacy graph is treated as corruption and fails
loudly rather than producing a mixed opening implementation.
"""

OPENING_CAMERA_NAMES=(
    'FL CG ARRIVAL PERIM','FL CG ARRIVAL NOSE','FL CG ARRIVAL GATE',
    'FL CG ARRIVAL STBD','FL CG ARRIVAL ISR','FL CG ARRIVAL MAST',
    'FL CG ARRIVAL CONVERT','FL CG ARRIVAL BELLY','FL CG ARRIVAL GEAR',
    'FL CG ARRIVAL LZ','FL CG ARRIVAL FLARE','FL CG ARRIVAL TOUCHDOWN',
    'FL CG ARRIVAL RAMP','FL CG ARRIVAL DEPLOY','FL CG ARRIVAL LIFTOFF',
    'FL CG ARRIVAL CLIMB','FL CG ARRIVAL DEPART',
)
MARKER=r'Aegis Reach\Supply Crate.fpe'
CHAIN_SCRIPT=r'aegis_reach\firstlight_cineguru_chain.lua'
CONTROLLER='FIRST LIGHT // CINEGURU NATIVE CHAIN'


def _suffix_key(entity,suffix):
    for key in entity:
        if key.split(':',1)[-1]==suffix:return key
    return None


def _get(entity,suffix,default=0):
    key=_suffix_key(entity,suffix)
    return entity.get(key,default) if key else default


def _set(build,entity,suffix,value):
    if not build.set_suffix(entity,suffix,value):
        raise RuntimeError('native CineGuru chain field missing from entity template: '+suffix)


def _find_entity_by_name(build,name):
    for placement in build.placements:
        if placement.get('name')==name:
            idx=int(placement['id'])-1
            if 0<=idx<len(build.entities):return build.entities[idx]
    return None


def _add_controller(build):
    build.add(MARKER,CONTROLLER,260,-9500,y=100,
              kind='controller',script=CHAIN_SCRIPT,
              **{'eleprof.physics':0,'eleprof.phyalways':1})


def apply(build):
    found=[(name,_find_entity_by_name(build,name)) for name in OPENING_CAMERA_NAMES]
    entities=[entity for _,entity in found if entity is not None]

    # Current production contract: firstlight_opening_director has already renamed
    # and neutralized every legacy ARRIVAL camera. Preserve only the inert chain
    # controller so old reports/tests and local MAX projects remain compatible.
    if not entities:
        _add_controller(build)
        return {
            'native_chain':False,'camera_count':0,'first_camera':None,'last_camera':None,
            'link_ids':[],
            'relationship_model':'retired; no ARRIVAL camera graph after native hard replacement',
            'controller':CONTROLLER,'script':CHAIN_SCRIPT,
            'compatibility_only':True,
        }

    # Anything between zero and all seventeen means the build mixed two opening
    # generations. Never silently publish that state.
    if len(entities)!=len(OPENING_CAMERA_NAMES):
        missing=[name for name,entity in found if entity is None]
        raise RuntimeError('partial legacy CineGuru opening graph survived hard replacement; missing: '+', '.join(missing))

    # Legacy fallback retained for old authoring order only. A production build
    # should never reach this path because the native opening pass runs first.
    max_link=max([int(_get(e,'eleprof.iObjectLinkID',0) or 0) for e in build.entities]+[0])
    first_link=max(1000,max_link+32)
    link_ids=[first_link+i for i in range(len(entities))]

    for entity,link_id in zip(entities,link_ids):
        _set(build,entity,'eleprof.iObjectLinkID',link_id)
        for slot in range(10):
            _set(build,entity,f'eleprof.iObjectRelationships[{slot}]',0)
            _set(build,entity,f'eleprof.iObjectRelationshipsType[{slot}]',0)
            _set(build,entity,f'eleprof.iObjectRelationshipsData[{slot}]',0)

    for i,entity in enumerate(entities):
        neighbors=[]
        if i>0:neighbors.append(link_ids[i-1])
        if i+1<len(entities):neighbors.append(link_ids[i+1])
        for slot,target_link in enumerate(neighbors):
            _set(build,entity,f'eleprof.iObjectRelationships[{slot}]',target_link)

    _add_controller(build)
    return {
        'native_chain':True,'camera_count':len(entities),'first_camera':OPENING_CAMERA_NAMES[0],
        'last_camera':OPENING_CAMERA_NAMES[-1],'link_ids':link_ids,
        'relationship_model':'legacy bidirectional adjacency; should not occur in production hard-replacement build',
        'controller':CONTROLLER,'script':CHAIN_SCRIPT,
        'compatibility_only':False,
    }
