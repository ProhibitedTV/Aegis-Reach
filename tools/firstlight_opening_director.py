"""Add the FIRST LIGHT opening compatibility layer to the production map.

The seventeen opening entities are physical/editor-space camera mounts only. They are
made deliberately inert so CineGuru cannot compete for the real GameGuru camera.
The actual 50.8-second insertion camera is driven from the mission HUD tick through
firstlight_opening_native.lua; the legacy opening-director entity remains as an inert
compatibility marker only. Later story cameras still use CineGuru normally.
"""

MARKER=r'Aegis Reach\Supply Crate.fpe'
SCRIPT=r'aegis_reach\firstlight_opening_director.lua'
NATIVE_SCRIPT=r'aegis_reach\firstlight_opening_native.lua'
MOUNT_SCRIPT=r'aegis_reach\firstlight_camera_mount.lua'
NAME='FIRST LIGHT // OPENING DIRECTOR'
OPENING_PREFIX='FL CG ARRIVAL '


def sync_coordinator_guard(path):
    text=path.read_text()
    old='if not cine.seen.ARRIVAL_PERIM and not cine.failed.ARRIVAL_PERIM and not cine.active and not cine.pending and not aegis.cinematic_request and g_Time-(fl.born or g_Time)>350 then'
    new='if not aegis.insertion_complete and not cine.seen.ARRIVAL_PERIM and not cine.failed.ARRIVAL_PERIM and not cine.active and not cine.pending and not aegis.cinematic_request and g_Time-(fl.born or g_Time)>350 then'
    if old in text:
        text=text.replace(old,new,1)
    elif new not in text:
        raise RuntimeError('FIRST LIGHT legacy opening guard signature changed; refusing unsafe patch')
    path.write_text(text)


def neutralize_opening_cineguru(build):
    """Turn only the seventeen insertion cameras into inert transform markers."""
    count=0
    for placement,entity in zip(build.placements,build.entities):
        name=str(placement.get('name',''))
        if not name.startswith(OPENING_PREFIX):
            continue
        if not build.set_suffix(entity,'eleprof.aimain_s',MOUNT_SCRIPT):
            raise RuntimeError('opening camera entity has no aimain_s field: '+name)
        build.set_suffix(entity,'staticflag',0)
        build.set_suffix(entity,'eleprof.physics',0)
        build.set_suffix(entity,'eleprof.phyalways',1)
        count+=1
    if count!=17:
        raise RuntimeError(f'expected 17 opening camera mounts, found {count}')
    return count


def apply(build):
    sync_coordinator_guard(build.FILES/'scriptbank/aegis_reach/firstlight_cinematic.lua')
    mounts=neutralize_opening_cineguru(build)
    # Kept only as an inert compatibility marker for older build/report tooling.
    build.add(MARKER,NAME,300,-9500,y=100,kind='controller',script=SCRIPT,
              **{'eleprof.physics':0,'eleprof.phyalways':1})
    return {
        'controller':NAME,
        'script':SCRIPT,
        'native_camera_script':NATIVE_SCRIPT,
        'camera_owner':'mission-hud-native',
        'camera_sources':'direct world poses + live Kestrel transform',
        'opening_mount_script':MOUNT_SCRIPT,
        'inert_opening_mounts':mounts,
        'cut_count':17,
        'opening_ms':50800,
        'legacy_opening_guard':'blocked after insertion_complete',
        'cineguru_opening_runtime':'disabled; CineGuru reserved for later story beats',
        'runtime_entry':'firstlight_hud.lua -> fl_opening_native_tick()',
    }
