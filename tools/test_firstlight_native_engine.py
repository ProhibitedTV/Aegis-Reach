"""Engine-level contracts learned from MAX's native behaviors and production limits."""
import json
import zipfile

from native_format import ROOT,read_ele
from max_archive import PASSWORD
from firstlight_combat_geometry import COMBAT_LIGHTS
from firstlight_native_engine_pass import PRACTICALS,PRACTICAL_LIGHT_SCRIPT


def main():
    assert COMBAT_LIGHTS and max(v[3] for v in COMBAT_LIGHTS)<=550

    lua=(ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_practical_light.lua').read_text(errors='replace')
    for token in ('GetEntityLightNumber','SetLightRange','SetLightRGB'):
        assert token in lua,token
    assert 'g_Time+70' in lua,'practical light should be throttled rather than recalculated every frame'

    fx=(ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_effects.lua').read_text(errors='replace')
    for token in ('EffectStart','EffectStop','GetPlayerDistance','next_check=g_Time+100'):
        assert token in fx,token

    layout=json.loads((ROOT/'Aegis Reach/Design/First Light/layout.json').read_text())
    bylayout={p['name']:p for p in layout}
    for name in PRACTICALS:
        assert bylayout[name].get('native_behavior')=='responsive_practical_light',name

    map_path=ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm'
    with zipfile.ZipFile(map_path) as archive:
        _,entities=read_ele(archive.read('map.ele',pwd=PASSWORD))
    byname={e['101:eleprof.name_s']:e for e in entities}
    for name in PRACTICALS:
        script=str(byname[name]['101:eleprof.aimain_s']).replace('/','\\').lower()
        assert script==PRACTICAL_LIGHT_SCRIPT.lower(),(name,script)

    bank=ROOT/'Aegis Reach/Files/entitybank/Aegis Reach/First Light'
    for filename in ('Vesper Salt Scrub.fpe','Vesper Brine Reed.fpe','Vesper Crust Skitter.fpe','Meridian M17 Transport Wreck.fpe','Meridian M17 Detached Engine.fpe'):
        text=(bank/filename).read_text(errors='replace').lower()
        assert 'collisionmode = 11' in text,filename

    print('FIRST LIGHT // NATIVE ENGINE CONTRACT PASS')
    print('Local-light budget, throttled MAX light API, distance-cull FX and no-collision ambience verified.')


if __name__=='__main__':main()
