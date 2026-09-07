"""Bind First Light to the actual MAX storyboard and refresh every menu preview."""
from storyboard import *
from PIL import Image,ImageDraw,ImageFont
import math,json
GAME=ROOT/'Aegis Reach';FILES=GAME/'Files';out=FILES/'imagebank/aegis_reach/firstlight';out.mkdir(parents=True,exist_ok=True)
s=load();backup=GAME/'Design/First Light/previous-storyboard.dat'
if not backup.exists():shutil.copy2(PROJECT,backup)
s.customprojectfolder=(str(ROOT)+'\\').encode();s.game_description=b'FIRST LIGHT // MISSION 01\nFind out why Relayfall went dark. Restore Northstar, recover the missing survey crew\'s records, and stop AEGIS firing on Shelter 12.'
s.game_world_edge_text=b'Return to the Meridian service route.'
s.Nodes[7].title=b'FIRST LIGHT';s.Nodes[7].levelnumber=b'MISSION 01';s.Nodes[7].level_name=b'mapbank\\Aegis Reach - First Light.fpm'
base=Image.new('RGB',(1920,1080),(10,21,32));d=ImageDraw.Draw(base)
for x in range(1080,1900,70):d.line((x,75,x,1000),fill=(19,40,53))
for y in range(120,1000,70):d.line((1050,y,1840,y),fill=(19,40,53))
for r in (150,250,350):d.ellipse((1430-r,525-r,1430+r,525+r),outline=(29,63,77),width=2)
d.line((105,125,920,125),fill=(86,207,220),width=3);d.line((105,950,1800,950),fill=(43,77,89),width=2)
for i in range(8):d.rectangle((1200+i*65,700-(i%3)*55,1225+i*65,710-(i%3)*55),fill=(59,125,140))
base.save(out/'operations-panel.png')
white=(.87,.93,.94,1);cyan=(.35,.83,.88,1)
def text(n,i,label,x,y,scale=1,kind=2):
 n.widget_used[i]=1;n.widget_type[i]=kind;n.widget_label[i].value=label.encode();n.widget_pos[i][:]=(x,y);n.widget_font_size[i]=scale
 n.widget_font[i].value=b'Default Font';n.widget_font_color[i][:]=white;n.widget_size[i][:]=(1,1)
 n.widget_name[i].value=('firstlight_'+str(n.id)+'_'+str(i)).encode()
 s.widget_colors[n.id-49000][i][:]=(1,1,1,1) if 49000<=n.id<49150 else (1,1,1,1)
def label(n,i,label,x=None,y=None,scale=None):
 n.widget_label[i].value=label.encode()
 if x is not None:n.widget_pos[i][:]=(x,y)
 if scale is not None:n.widget_font_size[i]=scale
for ni,n in enumerate(s.Nodes):
 if not n.used or ni in (0,7,13):continue
 n.screen_backdrop=b'imagebank\\aegis_reach\\firstlight\\operations-panel.png';n.screen_backdrop_transparent=0;n.screen_backdrop_placement=1
 for j in range(10):n.screen_backdrop_ratio_placement[j]=1
 for j in range(100):
  if n.widget_used[j]:n.widget_font_color[j][:]=white;s.widget_colors[ni][j][:]=(1,1,1,1)
 # All settings and system screens inherit one consistent small identity label.
 text(n,95,'AEGIS REACH / VANGUARD FIELD SYSTEMS',50,94,.48)
n=s.Nodes[1];n.screen_backdrop=b'imagebank\\aegis_reach\\title-art.png';n.screen_music=b'audiobank\\aegis_reach\\music\\salt_moon_drift.wav';n.loop_music=1
label(n,0,'DEPLOY // FIRST LIGHT',27,60,1.15);n.widget_used[1]=0
label(n,2,'MISSION BRIEFING',27,71,1.0);label(n,3,'EXIT TO DESKTOP',27,82,.85)
text(n,4,'AEGIS REACH',27,24,2.2);text(n,5,'F I R S T   L I G H T',27,36,1.0);text(n,6,'42 EVACUATED. ONE STILL MISSING.',27,45,.65);n.widget_used[7]=0
n=s.Nodes[2];label(n,0,'APPROACHING MERIDIAN SHELF',32,61,1.1);n.widget_pos[1][:]=(32,76)
label(n,2,'Look for survey records and weapon caches away from the direct route.',50,88,.6);text(n,3,'FIRST LIGHT',32,41,1.8)
n=s.Nodes[4];n.title=b'Mission Briefing'
for j in range(100):n.widget_used[j]=0
text(n,0,'FIRST LIGHT / OPERATION ORDER',50,15,1.5)
brief=['Relayfall has cut off the colony. Restore the Northstar power grid.','The civilian survey camp was evacuated in a hurry. One name remains.','Cross the dry channel. Use the basalt shoulders to choose your approach.','Find the Operations manifest and learn why the Wardens sealed Shelter 12.','Cancel the AEGIS firing order, then hold Gate 7 until Kestrel can land.','Cyan marks operating systems. Amber marks occupied machinery.','Your shield recharges out of contact. Repair stations restore armour.']
for i,line in enumerate(brief,3):text(n,i,line,50,29+(i-3)*7,.72)
text(n,2,'BACK TO OPERATIONS',50,83,1,kind=1);n.widget_action[2]=6;n.widget_normal_thumb[2].value=b'editors\\templates\\buttons\\default.png'
for ni,headline,line in [(5,'FIRST LIGHT / COMPLETE','The strike is cancelled. Mira is still below the relay.'),(6,'SIGNAL LOST','Seven is down. Deploy again and find another approach.')]:
 n=s.Nodes[ni];label(n,1,headline,50,32,1.8);text(n,2,line,50,47,.8);label(n,0,'RETURN TO OPERATIONS',50,72,1)
n=s.Nodes[8];label(n,0,'TACTICAL PAUSE',35,14,1.5);label(n,1,'RETURN TO MAIN MENU',35,29,.9)
n.widget_used[2]=0;n.widget_used[3]=0
for j,y in [(4,42),(5,53),(7,64),(6,79)]:n.widget_pos[j][:]=(35,y)
for ni,title in [(10,'DISPLAY / FIELD OPTICS'),(11,'AUDIO / COMMUNICATIONS'),(12,'CONTROLS / OPERATOR GUIDE')]:label(s.Nodes[ni],0,title,50,14,1.45)
n=s.Nodes[12]
label(n,2,'WASD - Move\nMouse - Look\nSpace - Jump\nShift - Sprint',22,34,.85)
label(n,4,'LMB - Fire\nRMB - Aim\nR - Reload\n1-9 / Wheel - Weapon',53,34,.85)
label(n,6,'Hold E - Operate terminal\nE - Read field record\nE - Use repair supplies\nEsc - Pause',82,34,.75)
for ni in (9,14):
 n=s.Nodes[ni]
 if not n.used:continue
 for j in range(1,9):n.widget_used[j]=0
 label(n,0,'SESSION OPERATIONS',50,25,1.4)
 text(n,20,'First Light is played as one continuous operation.',50,44,.8)
 text(n,21,'Return to the main menu to begin a fresh deployment.',50,54,.75)
# Accurate diagram of the authored route, not a gameplay screenshot.
layout=json.loads((GAME/'Design/First Light/layout.json').read_text())
plan=Image.new('RGB',(900,1500),(10,21,32));pd=ImageDraw.Draw(plan)
def pos(x,z):return int(450+x*.085),int(380-z*.095)
for o in layout:
 x,y=pos(o['x'],o['z'])
 if not(20<x<880 and 80<y<1450):continue
 color={'enemy':(211,113,80),'objective':(87,226,229),'intel':(225,193,121),'medical':(96,205,141),'light':(239,171,96)}.get(o['kind'],(49,72,88))
 r=7 if o['kind'] in ('objective','intel') else 3
 pd.rectangle((x-r,y-r,x+r,y+r),fill=color)
font=ImageFont.truetype(r'C:\Windows\Fonts\consolab.ttf',28)
pd.text((35,28),'FIRST LIGHT / MISSION PLAN',font=font,fill=(186,229,232))
for name,x,z in [('INSERTION',0,-9500),('SURVEY CAMP',-1700,-7100),('DRY CHANNEL',0,-5200),('GATE 07 / LZ',0,-2350),('NORTHSTAR',-1250,-850),('OPERATIONS',1300,1050),('AEGIS',0,3200)]:
 px,py=pos(x,z);pd.text((max(25,min(620,px+15)),py-20),name,font=ImageFont.truetype(r'C:\Windows\Fonts\consola.ttf',20),fill=(205,227,230))
plan.save(out/'mission-plan.png');s.Nodes[7].thumb=b'imagebank\\aegis_reach\\firstlight\\mission-plan.png'
# Rebuild storyboard previews from the native widget labels and coordinates.
for ni,n in enumerate(s.Nodes):
 if not n.used or ni in (0,7,13):continue
 im=base.copy();dr=ImageDraw.Draw(im)
 for j in range(100):
  if not n.widget_used[j] or n.widget_type[j] not in (1,2,6,7):continue
  labeltext=n.widget_label[j].value.decode(errors='replace')
  if not labeltext:continue
  f=ImageFont.truetype(r'C:\Windows\Fonts\consola.ttf',max(10,int(abs(n.widget_font_size[j])*32)))
  x,y=n.widget_pos[j];dr.multiline_text((x*19.2,y*10.8),labeltext,font=f,fill=(212,233,237),anchor='ma',align='center',spacing=7)
 filename='screen-'+str(ni)+'.png';im.resize((768,432)).save(out/filename)
 n.thumb=('imagebank\\aegis_reach\\firstlight\\'+filename).encode()
 n.screen_thumb=n.thumb;n.thumb_id=0;n.screen_backdrop_id=0
s.iChanged=0;PROJECT.write_bytes(bytes(s))
print('FIRST LIGHT storyboard connected; every menu backdrop and preview refreshed')
