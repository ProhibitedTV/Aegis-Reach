"""Hard-replace the FIRST LIGHT insertion cinematic.

The insertion no longer has CineGuru camera entities, a camera-rig entity, or a
standalone opening-director entity in the native map.  Those objects proved too easy
for MAX/CineGuru to reclaim at runtime and repeatedly produced the old external
establishing shot even when our authored timeline had changed.

The 50.8 second opener is now owned entirely by firstlight_opening_native.lua, called
from the known-running mission HUD path.  Later MIRA / AEGIS / EXTRACTION cameras are
left untouched and continue to use CineGuru.
"""
import re

NATIVE_SCRIPT=r'aegis_reach\firstlight_opening_native.lua'
OPENING_PREFIX='FL CG ARRIVAL '
REMOVE_NAMES={'FIRST LIGHT // CAMERA RIG','FIRST LIGHT // OPENING DIRECTOR'}


def disable_legacy_opening(path):
    """Permanently disable the old coordinator's insertion bootstrap.

    firstlight_cinematics.py still synchronizes the shared later-story coordinator,
    so patch this after that authoring pass.  The later MIRA/AEGIS/extraction paths
    remain live; only the automatic ARRIVAL_PERIM bootstrap is disabled.
    """
    text=path.read_text()
    pattern=(r'if (?:not aegis\.insertion_complete and )?not cine\.seen\.ARRIVAL_PERIM '
             r'and not cine\.failed\.ARRIVAL_PERIM and not cine\.active and not cine\.pending '
             r'and not aegis\.cinematic_request and g_Time-\(fl\.born or g_Time\)>350 then')
    replacement=('if false and not cine.seen.ARRIVAL_PERIM and not cine.failed.ARRIVAL_PERIM '
                 'and not cine.active and not cine.pending and not aegis.cinematic_request '
                 'and g_Time-(fl.born or g_Time)>350 then')
    text,n=re.subn(pattern,replacement,text,count=1)
    if n!=1 and replacement not in text:
        raise RuntimeError('FIRST LIGHT legacy opening guard signature changed; refusing unsafe patch')
    path.write_text(text)


def remove_legacy_opening_entities(build):
    """Delete every native insertion-camera/controller entity from the build.

    Deleting rather than neutralizing is intentional: MAX cannot fall back to an old
    opening camera that simply does not exist in map.ele.
    """
    removed=[]
    for i in range(len(build.placements)-1,-1,-1):
        name=str(build.placements[i].get('name',''))
        if name.startswith(OPENING_PREFIX) or name in REMOVE_NAMES:
            removed.append(name)
            build.placements.pop(i)
            build.entities.pop(i)
    opening=[n for n in removed if n.startswith(OPENING_PREFIX)]
    if len(opening)!=17:
        raise RuntimeError(f'expected to delete 17 legacy opening cameras, deleted {len(opening)}')
    if 'FIRST LIGHT // CAMERA RIG' not in removed:
        raise RuntimeError('legacy diegetic camera rig was not present for removal')
    return removed


def apply(build):
    disable_legacy_opening(build.FILES/'scriptbank/aegis_reach/firstlight_cinematic.lua')
    removed=remove_legacy_opening_entities(build)
    return {
        'controller':None,
        'script':NATIVE_SCRIPT,
        'native_camera_script':NATIVE_SCRIPT,
        'camera_owner':'mission-hud-native-hard-replacement',
        'camera_sources':'direct world poses + live Kestrel transform',
        'removed_opening_cameras':17,
        'removed_camera_rig':True,
        'removed_legacy_entities':len(removed),
        'cut_count':17,
        'opening_ms':50800,
        'legacy_opening_guard':'hard disabled',
        'cineguru_opening_runtime':'absent from map; CineGuru reserved for later story beats',
        'runtime_entry':'firstlight_hud.lua -> fl_opening_native_tick()',
    }
