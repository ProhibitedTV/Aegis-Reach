"""Hard-replace the FIRST LIGHT insertion cinematic.

The seventeen legacy insertion CineGuru cameras are quarantined out of the ARRIVAL
namespace and rebound to an inert mount script. Their transforms remain in the map
only to preserve stable authoring/entity counts; CineGuru and the old coordinator can
no longer resolve or activate them. The automatic ARRIVAL bootstrap is also hard
disabled after firstlight_cinematics.py synchronizes the later-story coordinator.

The actual 50.8 second opener is owned entirely by firstlight_opening_native.lua,
called from the known-running mission HUD path. Later MIRA / AEGIS / EXTRACTION
cameras remain normal CineGuru cameras.
"""
import re

MARKER=r'Aegis Reach\Supply Crate.fpe'
SCRIPT=r'aegis_reach\firstlight_opening_director.lua'
NATIVE_SCRIPT=r'aegis_reach\firstlight_opening_native.lua'
MOUNT_SCRIPT=r'aegis_reach\firstlight_camera_mount.lua'
NAME='FIRST LIGHT // OPENING DIRECTOR'
OPENING_PREFIX='FL CG ARRIVAL '
QUARANTINE_PREFIX='FL OPENING LEGACY QUARANTINE '


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


def sync_coordinator_guard(path):
    """Normalize the generated coordinator to the native-opening ownership contract.

    firstlight_rebuild_if_needed.py calls this immediately after sync_coordinator().
    Keep it intentionally idempotent so a checked-in coordinator that is already
    disabled remains stable and does not force a rebuild on every launch.
    """
    disable_legacy_opening(path)


def quarantine_legacy_opening_cameras(build):
    """Rename and neutralize all seventeen legacy insertion cameras."""
    found=[]
    for i,(placement,entity) in enumerate(zip(build.placements,build.entities)):
        old=str(placement.get('name',''))
        if not old.startswith(OPENING_PREFIX):
            continue
        found.append(old)
        new=f'{QUARANTINE_PREFIX}{len(found):02d}'
        placement['name']=new
        if not build.set_suffix(entity,'eleprof.name_s',new):
            raise RuntimeError('opening camera entity has no name field: '+old)
        if not build.set_suffix(entity,'eleprof.aimain_s',MOUNT_SCRIPT):
            raise RuntimeError('opening camera entity has no script field: '+old)
        build.set_suffix(entity,'staticflag',0)
        build.set_suffix(entity,'eleprof.physics',0)
        build.set_suffix(entity,'eleprof.phyalways',1)
    if len(found)!=17:
        raise RuntimeError(f'expected to quarantine 17 legacy opening cameras, found {len(found)}')
    return found


def apply(build):
    sync_coordinator_guard(build.FILES/'scriptbank/aegis_reach/firstlight_cinematic.lua')
    quarantined=quarantine_legacy_opening_cameras(build)
    # Inert compatibility marker only. Its Lua script does not own camera 0.
    build.add(MARKER,NAME,300,-9500,y=100,kind='controller',script=SCRIPT,
              **{'eleprof.physics':0,'eleprof.phyalways':1})
    return {
        'controller':NAME,
        'script':SCRIPT,
        'native_camera_script':NATIVE_SCRIPT,
        'camera_owner':'mission-hud-native-hard-replacement',
        'camera_sources':'direct world poses + live Kestrel transform',
        'removed_opening_cameras':17,
        'quarantined_opening_cameras':len(quarantined),
        'opening_mount_script':MOUNT_SCRIPT,
        'cut_count':17,
        'opening_ms':50800,
        'legacy_opening_guard':'hard disabled',
        'cineguru_opening_runtime':'quarantined by name+script; CineGuru reserved for later story beats',
        'runtime_entry':'firstlight_hud.lua -> fl_opening_native_tick()',
    }
