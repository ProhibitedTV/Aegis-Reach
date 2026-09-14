"""Author the FIRST LIGHT opening as a real native CineGuru camera graph.

The Lua coordinator owns story state, VO and fail-open behavior. CineGuru should own the
actual edit. GameGuru MAX serializes entity logic links as an object-link ID plus up to
ten relationship link IDs. CineGuru's cg_lib/GetEntityLinks consumes those native links
and cg_cinematic_camera follows camera->camera relationships through `nextcam`.
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


def _entity_by_name(build,name):
    for placement in build.placements:
        if placement.get('name')==name:
            idx=int(placement['id'])-1
            if 0<=idx<len(build.entities):return build.entities[idx]
    raise RuntimeError('opening camera missing before native chain pass: '+name)


def apply(build):
    entities=[_entity_by_name(build,name) for name in OPENING_CAMERA_NAMES]
    max_link=max([int(_get(e,'eleprof.iObjectLinkID',0) or 0) for e in build.entities]+[0])
    first_link=max(1000,max_link+32)
    link_ids=[first_link+i for i in range(len(entities))]

    # Clean the ten relationship slots, assign a unique native object-link ID to each
    # camera, then connect each camera to its immediate neighbors. CineGuru walks away
    # from the camera it came from, so the bidirectional graph resolves deterministically
    # into PERIM -> ... -> DEPART while remaining visible/editable in MAX.
    for entity,link_id in zip(entities,link_ids):
        _set(build,entity,'eleprof.iObjectLinkID',link_id)
        for slot in range(10):
            _set(build,entity,f'eleprof.iObjectRelationships[{slot}]',0)
            _set(build,entity,f'eleprof.iObjectRelationshipsType[{slot}]',0)
            _set(build,entity,f'eleprof.iObjectRelationshipsData[{slot}]',0)
            _set(build,entity,f'eleprof.iObjectRelationshipsDataUser[{slot}]',0)

    for i,entity in enumerate(entities):
        neighbors=[]
        if i>0:neighbors.append(link_ids[i-1])
        if i+1<len(entities):neighbors.append(link_ids[i+1])
        for slot,target_link in enumerate(neighbors):
            _set(build,entity,f'eleprof.iObjectRelationships[{slot}]',target_link)

    # This tiny controller asks the vendored CineGuru camera script to parse its native
    # relationship graph as soon as all cameras have registered. The story coordinator
    # can continue to activate ARRIVAL_PERIM; CineGuru itself then owns the cuts.
    build.add(MARKER,'FIRST LIGHT // CINEGURU NATIVE CHAIN',260,-9500,y=100,
              kind='controller',script=CHAIN_SCRIPT,
              **{'eleprof.physics':0,'eleprof.phyalways':1})

    return {
        'native_chain':True,'camera_count':len(entities),'first_camera':OPENING_CAMERA_NAMES[0],
        'last_camera':OPENING_CAMERA_NAMES[-1],'link_ids':link_ids,
        'relationship_model':'bidirectional adjacency; CineGuru nextcam traversal',
        'controller':'FIRST LIGHT // CINEGURU NATIVE CHAIN','script':CHAIN_SCRIPT,
    }
