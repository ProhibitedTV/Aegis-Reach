"""Deploy/launch First Light using MAX's native external-project registration."""
from pathlib import Path
import argparse,shutil,subprocess,os,json
from native_format import ROOT,INSTALL
GAME=ROOT/'Aegis Reach';FILES=GAME/'Files'
TARGET=Path(os.environ['USERPROFILE'])/'Documents/GameGuruApps/GameGuruMAX/Files'
REG=TARGET/'projectbank/Aegis Reach';DESIGN=GAME/'Design/First Light'
def deploy():
 REG.mkdir(parents=True,exist_ok=True)
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
 # Native MAX parser consumes the remainder of the command line as the project name.
 cmd='"'+str(INSTALL.parent/'GameGuruMAX.exe')+'" project='+('1' if qa else '0')+'Aegis Reach'
 p=subprocess.Popen(cmd,cwd=INSTALL.parent,env=env)
 (DESIGN/'last-launch.json').write_text(json.dumps({'pid':p.pid,'qa':qa,'project':str(GAME)},indent=2))
 print('GameGuru MAX launched:',p.pid,'AUTOMATED QA' if qa else 'NORMAL PLAY')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['deploy','play','qa']);a=p.parse_args()
 if a.command=='deploy':deploy()
 else:launch(a.command=='qa')
