"""Regression test for native-run tuning telemetry without launching GameGuru MAX."""
from firstlight_collect import build_tuning


def check(name,value):
    assert value,name
    print('PASS //',name)


def main():
    evidence={
        'director_ticks':[
            '2026-09-13 02:00:10 tick stage=1 zone=GATE music=combat pressure=18 budget=4 x=0 z=-2700 contacts=1 health=190 kills=0',
            '2026-09-13 02:00:22 tick stage=1 zone=GATE music=combat pressure=57 budget=4 x=0 z=-2500 contacts=3 health=148 kills=1',
            '2026-09-13 02:00:34 tick stage=1 zone=GATE music=combat pressure=76 budget=3 x=0 z=-2200 contacts=2 health=121 kills=2',
        ],
        'enemy_activation':[
            '2026-09-13 02:00:09 enemy_activated group=2 index=1 role=rifle reason=proximity wait=0 entity=10 budget=4',
            '2026-09-13 02:00:10 enemy_activated group=2 index=2 role=assault reason=proximity wait=0 entity=11 budget=4',
            '2026-09-13 02:01:04 enemy_activated group=7 index=1 role=rifle reason=extraction_wave wait=0 entity=20 budget=5',
            '2026-09-13 02:01:07 enemy_activated group=7 index=2 role=assault reason=extraction_wave wait=0 entity=21 budget=5',
        ],
        'reveal_held':[
            '2026-09-13 02:00:08 reveal_held e=10 group=2 role=rifle watched_ms=900 distance=840',
            '2026-09-13 02:00:09 reveal_held e=10 group=2 role=rifle watched_ms=1900 distance=800',
        ],
        'squad_clear':[
            '2026-09-13 02:00:38 squad_clear group=2 duration_ms=29000 armour_loss=22 end_armour=78 end_shield=16 peak_pressure=81',
        ],
        'evacuation_started':['2026-09-13 02:01:00 evacuation_started'],
        'combat_enter':['2026-09-13 02:00:10 combat_enter contacts=1 budget=4'],
        'combat_clear':['2026-09-13 02:00:39 combat_clear pressure=12'],
    }
    tuning=build_tuning(evidence)
    check('peak pressure includes squad peak',tuning['peak_pressure']==81)
    check('pressure bands are classified',tuning['pressure_band_samples']=={'ELEVATED':1,'HIGH':1,'CRITICAL':1})
    check('maximum sampled contacts parsed',tuning['max_contacts_sampled']==3)
    check('minimum sampled health parsed',tuning['minimum_health_sampled']==121)
    check('role activation histogram parsed',tuning['activations_by_role']['rifle']==2 and tuning['activations_by_role']['assault']==2)
    check('visibility hold is reduced to per-entity max',tuning['held_reveal_entities']['10']==1900)
    check('squad outcome parsed',tuning['squads_cleared'][0]['duration_s']==29.0 and tuning['squads_cleared'][0]['armour_loss']==22)
    arrivals=tuning['extraction_arrivals']
    check('extraction wave deltas are relative to holdout start',arrivals[0]['seconds_after_evac_start']==4.0 and arrivals[1]['seconds_after_evac_start']==7.0)
    check('combat entry and clear counts parsed',tuning['combat_entries']==1 and tuning['combat_clears']==1)
    print('FIRST LIGHT // COLLECTOR TELEMETRY PASS')


if __name__=='__main__':main()
