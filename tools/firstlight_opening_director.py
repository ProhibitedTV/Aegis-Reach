"""Hard-replace the FIRST LIGHT insertion cinematic.

The seventeen insertion CineGuru camera entities are physically deleted from the
native map.  MAX therefore has no legacy external insertion camera it can fall back
to.  Harmless compatibility/controller markers remain because later-story tooling
expects them, but they cannot render an insertion without those camera entities.

The 50.8 second opener is owned entirely by firstlight_opening_native.lua, called
from the known-running mission HUD path. Later MIRA / AEGIS / EXTRACTION cameras are
left untouched and continue to use CineGuru.
"""
import re

MARKER=r'Aegis Reach\Supply Crate.fpe'
SCRIPT=r'aegis_reach\firstlight_opening_director.lua'
NATIVE_SCRIPT=r'aegis_reach\firstlight_opening_native.lua'
NAME='FIRST LIGHT // OPENING DIRECTOR'
OPENING_PREFIX='FL CG ARRIVAL '


def disable_legacy_opening(path):
    """Permanently disable the old coordinator's insertion bootstrap."""
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


def remove_legacy_opening_cameras(build):
    """Delete all seventeen native insertion camera entities from map.ele/layout."""
    removed=[]
    for i in range(len(build.placements)-1,-1,-1):
        name=str(build.placements[i].get('name',''))
        if name.startswith(OPENING_PREFIX):
            removed.append(name)
            build.placements.pop(i)
            build.entities.pop(i)
    if len(removed)!=17:
        raise RuntimeError(f'expected to delete 17 legacy opening cameras, deleted {len(removed)}')
    return removed


def apply(build):
    disable_legacy_opening(build.FILES/'scriptbank/aegis_reach/firstlight_cinematic.lua')
    removed=remove_legacy_opening_cameras(build)
    # Inert compatibility marker only. Its Lua script does not own camera 0.
    build.add(MARKER,NAME,300,-9500,y=100,kind='controller',script=SCRIPT,
              **{'eleprof.physics':0,'eleprof.phyalways':1})
    return {
        'controller':NAME,
        'script':SCRIPT,
        'native_camera_script':NATIVE_SCRIPT,
        'camera_owner':'mission-hud-native-hard-replacement',
        'camera_sources':'direct world poses + live Kestrel transform',
        'removed_opening_cameras':len(removed),
        'cut_count':17,
        'opening_ms':50800,
        'legacy_opening_guard':'hard disabled',
        'cineguru_opening_runtime':'absent from map; CineGuru reserved for later story beats',
        'runtime_entry':'firstlight_hud.lua -> fl_opening_native_tick()',
    }
