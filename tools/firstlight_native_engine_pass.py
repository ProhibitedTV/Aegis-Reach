"""Apply small, engine-native presentation contracts after FIRST LIGHT content layers.

This is deliberately a mutation pass, not another world composition owner. It converts
selected authored markers to specialized runtime behaviors while preserving positions,
light indices, colors, ranges, and the single-owner map composition.
"""
PRACTICAL_LIGHT_SCRIPT = r'aegis_reach\firstlight_practical_light.lua'
PRACTICALS = {
    'M-17 / fire practical 1': {'base_range':520,'purpose':'primary wreck-fire response'},
    'M-17 / fire practical 2': {'base_range':260,'purpose':'secondary wreck-fire response'},
}


def apply(build):
    changed=[]
    for entity,placement in zip(build.entities,build.placements):
        name=placement.get('name','')
        cfg=PRACTICALS.get(name)
        if not cfg:
            continue
        build.set_suffix(entity,'staticflag',0)
        build.set_suffix(entity,'eleprof.aimain_s',PRACTICAL_LIGHT_SCRIPT)
        placement['native_behavior']='responsive_practical_light'
        placement['native_behavior_purpose']=cfg['purpose']
        changed.append(name)
    if set(changed)!=set(PRACTICALS):
        missing=sorted(set(PRACTICALS)-set(changed))
        raise RuntimeError('FIRST LIGHT native-engine pass missing practical lights: '+', '.join(missing))
    return {
        'responsive_practical_lights':len(changed),
        'light_api':'GetEntityLightNumber + SetLightRange + SetLightRGB',
        'policy':'small local dynamic lights; no broad area-light flattening',
        'changed':changed,
    }
