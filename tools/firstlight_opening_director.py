"""Add the deterministic FIRST LIGHT opening director to the production map.

CineGuru camera entities remain the authored camera mounts, but the opening game camera
is driven directly from one 50.8 second cut clock. This prevents the runtime from
silently sticking on an old CineGuru establishing shot while VO continues.
"""
import re

MARKER=r'Aegis Reach\Supply Crate.fpe'
SCRIPT=r'aegis_reach\firstlight_opening_director.lua'
NAME='FIRST LIGHT // OPENING DIRECTOR'


def _patch_legacy_coordinator(build):
    path=build.FILES/'scriptbank/aegis_reach/firstlight_cinematic.lua'
    text=path.read_text()
    old='if not cine.seen.ARRIVAL_PERIM and not cine.failed.ARRIVAL_PERIM and not cine.active and not cine.pending and not aegis.cinematic_request and g_Time-(fl.born or g_Time)>350 then'
    new='if not aegis.insertion_complete and not cine.seen.ARRIVAL_PERIM and not cine.failed.ARRIVAL_PERIM and not cine.active and not cine.pending and not aegis.cinematic_request and g_Time-(fl.born or g_Time)>350 then'
    if old in text:
        text=text.replace(old,new,1)
    elif new not in text:
        raise RuntimeError('FIRST LIGHT legacy opening guard signature changed; refusing unsafe patch')
    path.write_text(text)


def apply(build):
    _patch_legacy_coordinator(build)
    build.add(MARKER,NAME,300,-9500,y=100,kind='controller',script=SCRIPT,
              **{'eleprof.physics':0,'eleprof.phyalways':1})
    return {
        'controller':NAME,
        'script':SCRIPT,
        'camera_owner':'deterministic-director',
        'camera_sources':'17 authored CineGuru camera mounts',
        'cut_count':17,
        'opening_ms':50800,
        'legacy_opening_guard':'blocked after insertion_complete',
    }
