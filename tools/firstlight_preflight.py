"""Fail-fast preflight for native First Light playtests."""
from pathlib import Path
import hashlib,json,subprocess,sys,zipfile
from native_format import ROOT,read_ele
from max_archive import PASSWORD

GAME=ROOT/'Aegis Reach';FILES=GAME/'Files';DESIGN=GAME/'Design/First Light';MAP=FILES/'mapbank/Aegis Reach - First Light.fpm';REPORT=DESIGN/'preflight.json'
TRACKS=['salt_moon_drift.wav','moon_outpost_drift.wav','orbital_catacomb.wav'];BAD_SCRIPTS={'weapon.lua','scriptbank\\weapon.lua'}
QA_FORBIDDEN=['TransportToFreezePositionOnly','SetFreezePosition','SetEntityHealth(e,0)','SetPlayerHealth(','g_KeyPressE=1','QuitGame()']
def sha256(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def run_test(name):
 r=subprocess.run([sys.executable,'-B',str(ROOT/'tools'/name)],cwd=ROOT)
 if r.returncode:raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: {name} returned {r.returncode}')
def normalized_script(e):return str(e.get('101:eleprof.aimain_s','')).replace('/','\\').lower()
def load_combat_geometry_manifest():
 mp=DESIGN/'combat-geometry.json';lp=DESIGN/'layout.json'
 if not mp.is_file() or not lp.is_file():raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: missing combat/layout manifests; rebuild required')
 manifest=json.loads(mp.read_text());layout=json.loads(lp.read_text());cover=[p for p in layout if p.get('kind')=='combat_cover'];lights=[p for p in layout if p.get('kind')=='combat_light'];enemies=[p for p in layout if p.get('kind')=='enemy']
 if manifest.get('cover_count',0)<24 or len(cover)!=manifest.get('cover_count'):raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: combat cover mismatch')
 if manifest.get('combat_light_count')!=8 or len(lights)!=8:raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: combat light mismatch')
 if len(manifest.get('enemy_starts',[]))!=len(enemies):raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: enemy start mismatch')
 if not manifest.get('clear_lz_center'):raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: LZ center not certified clear')
 return manifest,layout,cover,lights,enemies

def main():
 if not MAP.is_file():raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: missing map {MAP}')
 tests=['test_firstlight_lua_compat.py','test_firstlight.py','test_firstlight_composition.py','test_firstlight_approach.py','test_meridian_fieldkit.py','test_meridian_materials.py','test_firstlight_asset_cache.py','test_firstlight_combat_geometry.py','test_firstlight_collect.py','test_vesper_sky.py','test_firstlight_story_effects.py','test_firstlight_transport.py','test_firstlight_biosphere.py','test_firstlight_cinematics.py','test_firstlight_story_delivery.py','test_firstlight_kestrel_boarding.py','test_firstlight_native_engine.py','test_max_asset_library_audit.py']
 tests.append('test_firstlight_presentation_runtime.py')
 for name in tests:run_test(name)
 combat,layout,combat_cover,combat_lights,authored_enemies=load_combat_geometry_manifest()
 cine=[p for p in layout if p.get('kind')=='cinematic_camera'];controllers=[p for p in layout if p.get('name')=='FIRST LIGHT // CINEMATIC'];vehicles=[p for p in layout if p.get('kind')=='vehicle'];dialogue_audio=[p for p in layout if p.get('kind')=='dialogue_audio'];boarding_collision=[p for p in layout if p.get('name')=='FL KESTREL BOARDING COLLISION']
 if len(cine)!=5 or len(controllers)!=1:raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: expected five CineGuru cameras and one coordinator')
 if len(vehicles)!=2:raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: expected insertion and extraction Kestrel entities')
 if len(boarding_collision)!=1 or boarding_collision[0].get('kind')!='vehicle_collision':raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: expected one landed-only Kestrel boarding collision proxy')
 with zipfile.ZipFile(MAP) as archive:
  archive.setpassword(PASSWORD);version,entities=read_ele(archive.read('map.ele'));encrypted=all(info.flag_bits&1 for info in archive.infolist())
 if len(entities)!=len(layout):raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: native map has {len(entities)} entities but layout has {len(layout)}')
 bad=[str(e.get('101:eleprof.name_s','<unnamed>')) for e in entities if normalized_script(e) in BAD_SCRIPTS]
 if bad:raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: unsafe stock weapon.lua entities remain: '+', '.join(bad))
 if not encrypted:raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: map archive is not fully MAX-encrypted')
 track_info={}
 for name in TRACKS:
  path=FILES/'audiobank/aegis_reach/music'/name
  if not path.is_file():raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: missing score master {name}')
  size=path.stat().st_size
  if size<1024*1024:raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: suspiciously small score master {name}: {size}')
  track_info[name]={'bytes':size,'sha256':sha256(path)}
 required=['firstlight_audit.lua','firstlight_director.lua','firstlight_hud.lua','firstlight_effects.lua','firstlight_enemy.lua','firstlight_interact.lua','firstlight_qa.lua','firstlight_score.lua','firstlight_cinematic.lua','firstlight_biosphere.lua','firstlight_practical_light.lua','firstlight_kestrel.lua','firstlight_kestrel_boarding.lua','firstlight_dialogue.lua','firstlight_voice_marker.lua']
 for name in required:
  if not (FILES/'scriptbank/aegis_reach'/name).is_file():raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: missing runtime script {name}')
 if not (FILES/'scriptbank/aegis_reach/images/hud_pixel.png').is_file():raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: missing HUD sprite')
 for name in ['cg_cinematic_camera.lua','cg_lib.lua','cg_pnoise.lua']:
  if not (FILES/'scriptbank/Cine Guru MAX'/name).is_file():raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: missing CineGuru dependency {name}')
 qa=(FILES/'scriptbank/aegis_reach/firstlight_qa.lua').read_text(errors='replace');destructive=[x for x in QA_FORBIDDEN if x in qa]
 if destructive:raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: QA instrumentation destructive: '+', '.join(destructive))
 score=(FILES/'scriptbank/aegis_reach/firstlight_score.lua').read_text(errors='replace')
 for name in TRACKS:
  if name not in score:raise SystemExit(f'FIRST LIGHT // PREFLIGHT FAILED: score does not reference {name}')
 if 'music_cinematic_duck' not in score:raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: score is not wired for cinematic ducking')
 biosphere=[p for p in layout if str(p.get('kind','')).startswith('biosphere_')];native_practicals=[p for p in layout if p.get('native_behavior')=='responsive_practical_light']
 if len(biosphere)<30:raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: biosphere incomplete')
 if len(native_practicals)!=2:raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: responsive M-17 lights incomplete')
 manifest=json.loads((DESIGN/'dialogue-manifest.json').read_text())
 if len(manifest.get('lines',[]))<20:raise SystemExit('FIRST LIGHT // PREFLIGHT FAILED: dialogue manifest incomplete')
 report={'map':str(MAP.relative_to(ROOT)),'map_sha256':sha256(MAP),'map_bytes':MAP.stat().st_size,'map_version':version,'entity_count':len(entities),'unsafe_weapon_pickups':bad,'archive_encrypted':encrypted,'qa_observational':True,'tracks':track_info,'tests':tests,'biosphere_entity_count':len(biosphere),'responsive_practical_light_count':len(native_practicals),'combat_cover_count':len(combat_cover),'combat_light_count':len(combat_lights),'authored_enemy_start_count':len(authored_enemies),'clear_lz_center':combat.get('clear_lz_center',False),'cineguru_camera_count':len(cine),'kestrel_vehicle_count':len(vehicles),'kestrel_boarding_collision_count':len(boarding_collision),'dialogue_line_count':len(manifest['lines']),'dialogue_audio_bound_count':len(dialogue_audio),'native_playtest_required':True}
 REPORT.write_text(json.dumps(report,indent=2));print('FIRST LIGHT // PREFLIGHT PASS');print('Map entities:',len(entities));print('Map SHA256:',report['map_sha256'][:16]);print('Dialogue:',report['dialogue_line_count'],'lines /',report['dialogue_audio_bound_count'],'voice files bound');print('Kestrel:',len(vehicles),'vehicle entities / visible insertion + extraction /',len(boarding_collision),'landed boarding collision proxy');print('CineGuru story layer:',len(cine),'cameras / fail-open');print('Native MAX playtest is still required.')
if __name__=='__main__':main()
