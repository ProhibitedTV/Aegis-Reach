"""Deploy/launch First Light using MAX's native external-project registration."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

from native_format import ROOT,INSTALL

GAME=ROOT/'Aegis Reach';FILES=GAME/'Files'
TARGET=Path(os.environ['USERPROFILE'])/'Documents/GameGuruApps/GameGuruMAX/Files'
REG=TARGET/'projectbank/Aegis Reach';DESIGN=GAME/'Design/First Light'
MAP=FILES/'mapbank/Aegis Reach - First Light.fpm'
TRACKS=('salt_moon_drift.wav','moon_outpost_drift.wav','orbital_catacomb.wav')
RUNTIME_LOGS=(
 TARGET/'first-light-diagnostics.log',
 TARGET/'first-light-runtime.log',
 TARGET/'aegis-native-runtime.log',
 GAME/'Guru-Game.log',
 INSTALL.parent/'Guru-Game.log',
)


def run_tool(name):
 cmd=[sys.executable,'-B',str(ROOT/'tools'/name)]
 subprocess.run(cmd,cwd=ROOT,check=True)


def ensure_current_build():
 run_tool('firstlight_rebuild_if_needed.py')


def apply_load_safety():
 run_tool('firstlight_load_safety.py')


def run_preflight():
 run_tool('firstlight_preflight.py')


def git_head():
 try:
  return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
 except Exception:
  return 'unknown'


def file_sha256(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()


def runtime_log_offsets():
 offsets={}
 for path in RUNTIME_LOGS:
  try:offsets[str(path)]=path.stat().st_size
  except OSError:offsets[str(path)]=0
 return offsets


def launch_manifest(qa,pid,log_offsets):
 tracks={}
 for name in TRACKS:
  path=FILES/'audiobank/aegis_reach/music'/name
  tracks[name]={'exists':path.is_file(),'bytes':path.stat().st_size if path.is_file() else 0}
 return {
  'pid':pid,
  'qa':qa,
  'qa_mode':'observational' if qa else None,
  'project':str(GAME),
  'git_head':git_head(),
  'launched_at':time.strftime('%Y-%m-%d %H:%M:%S'),
  'map':str(MAP),
  'map_bytes':MAP.stat().st_size if MAP.is_file() else 0,
  'map_sha256':file_sha256(MAP) if MAP.is_file() else None,
  'tracks':tracks,
  'original_art':json.loads((ROOT/'.local-review/firstlight-asset-cache.json').read_text()),
  'log_offsets':log_offsets,
  'collect_after_run':'python tools\\firstlight_collect.py',
 }


def deploy():
 # Rebuild only when authored generation sources changed. This is what propagates
 # world/geometry fixes into the binary .fpm without rewriting it every launch.
 ensure_current_build()
 # The canonical map may still contain legacy loose pickups from an older binary
 # build. Strip only the known-bad stock weapon.lua entities, then prove the exact
 # runtime map is structurally safe before MAX sees it.
 apply_load_safety()
 run_tool('firstlight_asset_cache.py')
 run_preflight()

 REG.mkdir(parents=True,exist_ok=True)
 DESIGN.mkdir(parents=True,exist_ok=True)
 # MAX load_storyboard consults remoteproject.txt only when no local project DAT exists.
 # Preserve the conflicting installed project before registering the external checkout.
 backup_dir=TARGET.parent/'aegis-registration-backups'
 for name in ('project203.dat','project.dat'):
  source=REG/name
  if source.is_file():
   backup_dir.mkdir(parents=True,exist_ok=True)
   destination=backup_dir/(time.strftime('%Y%m%d-%H%M%S')+'-'+name)
   if destination.exists():raise FileExistsError(destination)
   shutil.move(str(source),str(destination))
   print('Preserved conflicting local storyboard:',destination)
 old=REG/'remoteproject.txt'
 backup=DESIGN/'previous-remoteproject.txt'
 if old.exists() and not backup.exists():shutil.copy2(old,backup)
 # A registered external project resolves every authored resource from its Files folder.
 old.write_text(str(ROOT)+'\\\r\n',encoding='ascii')
 print('MAX project registration:',old)
 print('Authoritative playable project:',GAME)


def launch(qa=False):
 deploy()
 env=os.environ.copy()
 env.pop('AEGIS_FIRSTLIGHT_QA',None)
 if qa:env['AEGIS_FIRSTLIGHT_QA']='1'
 # Snapshot append-only logs before MAX starts. The collector uses these offsets so
 # a new run can never inherit an old Lua error, QA warning or activation event.
 log_offsets=runtime_log_offsets()
 # Native MAX parser consumes the remainder of the command line as the project name.
 cmd='"'+str(INSTALL.parent/'GameGuruMAX.exe')+'" project='+('1' if qa else '0')+'Aegis Reach'
 p=subprocess.Popen(cmd,cwd=INSTALL.parent,env=env)
 manifest=launch_manifest(qa,p.pid,log_offsets)
 (DESIGN/'last-launch.json').write_text(json.dumps(manifest,indent=2))
 print('GameGuru MAX launched:',p.pid,'OBSERVATIONAL QA' if qa else 'NORMAL PLAY')
 if qa:print('QA mode records evidence only: no teleporting, forced input, healing, or enemy kills.')
 print('Git head:',manifest['git_head'][:12])
 print('Runtime map:',manifest['map_sha256'][:16] if manifest['map_sha256'] else 'missing')
 print('Log baselines captured:',len(log_offsets))
 print('After exiting MAX: python tools\\firstlight_collect.py')


if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['deploy','play','qa']);a=p.parse_args()
 if a.command=='deploy':deploy()
 else:launch(a.command=='qa')
