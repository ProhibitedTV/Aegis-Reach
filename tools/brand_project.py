from storyboard import *
from PIL import Image,ImageDraw,ImageFont
import json,math
GAME=ROOT/'Aegis Reach';FILES=GAME/'Files';s=load()
backup=GAME/'Design/initial-project203.dat'
if not backup.exists():shutil.copy2(PROJECT,backup)
art=b'imagebank\\aegis_reach\\title-art.png'
music=b'audiobank\\aegis_reach\\reach-underscore.wav'
s.game_description=b'AEGIS REACH: RELAYFALL\nYou are Vanguard Seven. Retake three relays from the Iron Wardens, cancel the orbital strike, and reach the Kestrel extraction pad.\n\nAn original single-mission sci-fi infantry prototype.'
s.game_developer_desc=b'Original scenario, modular station assets, gameplay and audio created for this local GameGuru MAX project. Stock soldiers and weapons: The Game Creators.'
s.game_world_edge_text=b'MISSION BOUNDARY // Return to the relay outpost.'
s.game_thumb=art;s.project_readonly=0
n=s.Nodes[7];n.title=b'RELAYFALL';n.levelnumber=b'Mission 01';n.level_name=b'mapbank\\Aegis Reach - Relayfall.fpm'
n.thumb=b'imagebank\\aegis_reach\\tactical-map.png';n.iEditEnable=1
s.Nodes[0].thumb=art
for i,n in enumerate(s.Nodes):
 if not n.used or i in (0,7,13):continue
 n.screen_backdrop=art;n.screen_backdrop_placement=1
 for j in range(10):n.screen_backdrop_ratio_placement[j]=1
 for j in range(100):
  if n.widget_used[j]:
   n.widget_font_color[j][:]=(0.84,0.94,0.98,1.0)
   s.widget_colors[i][j][:]=(0.84,0.94,0.98,1.0)

def label(n,i,text):n.widget_label[i].value=text.encode('ascii')
def text(n,i,content,x,y,scale=1):
 n.widget_used[i]=1;n.widget_type[i]=2;n.widget_action[i]=0
 label(n,i,content);n.widget_pos[i][:]=(x,y);n.widget_size[i][:]=(1,1)
 n.widget_font[i].value=b'Default Font';n.widget_font_size[i]=scale
 n.widget_font_color[i][:]=(0.77,0.93,0.97,1)
 n.widget_name[i].value=('aegis_text_'+str(n.id)+'_'+str(i)).encode()
 n.widget_layer[i]=0;n.widget_read_only[i]=1

n=s.Nodes[1];n.screen_music=music;n.loop_music=1
label(n,0,'DEPLOY // RELAYFALL');label(n,2,'MISSION BRIEFING');label(n,3,'EXIT TO DESKTOP')
n.widget_used[1]=0
for j,y in [(0,62),(2,71),(3,80)]:n.widget_pos[j][:]=(24,y);n.widget_font_size[j]=.9
text(n,4,'AEGIS REACH',24,25,2.0);text(n,5,'R E L A Y F A L L',24,35,.9)
text(n,6,'ONE OPERATIVE. THREE RELAYS. A COLONY TO SAVE.',24,44,.48)
text(n,7,'VANGUARD OPERATIONS // MISSION 01',24,91,.45)

n=s.Nodes[2];label(n,0,'INSERTION IN PROGRESS');label(n,2,'Break contact for 5.5 seconds to recharge your shield. Hold E at each relay.')
n.widget_pos[0][:]=(27,77);n.widget_pos[1][:]=(27,85);n.widget_pos[2][:]=(50,95)
text(n,3,'RELAYFALL',27,60,1.4)

n=s.Nodes[4];n.title=b'Mission Briefing';n.widget_used[1]=0
label(n,0,'OPERATION // RELAYFALL');n.widget_pos[0][:]=(35,12);n.widget_font_size[0]=1.35
brief=[('The Iron Wardens have seized the colony defense network.',27),('Their orbital strike will turn our own sky against us.',33),('Restore NORTHSTAR, then LANTERN, then the AEGIS core.',43),('Return to the cyan Kestrel landing pad. Clear nearby hostiles.',49),('Hold E for three seconds at terminals and extraction.',59),('Use the flank gates. Break contact to regenerate shields.',65),('Field repair restores armour. Supply caches hold ammunition.',71)]
for i,(line,y) in enumerate(brief,3):text(n,i,line,35,y,.59)
label(n,2,'BACK TO OPERATIONS');n.widget_pos[2][:]=(35,86)

for i,title,sub in [(5,'COLONY SECURED','The strike is cancelled. Kestrel has brought you home.'),(6,'SIGNAL LOST','Vanguard Seven is down. Regroup and deploy again.')]:
 n=s.Nodes[i];label(n,1,title);n.widget_pos[1][:]=(30,30);n.widget_font_size[1]=1.7
 text(n,2,sub,30,44,.65);label(n,0,'RETURN TO OPERATIONS');n.widget_pos[0][:]=(30,73)

n=s.Nodes[8];label(n,0,'TACTICAL PAUSE');n.widget_used[2]=0;n.widget_used[3]=0
for j,y in [(1,27),(4,39),(5,51),(7,63),(6,79)]:n.widget_pos[j][:]=(30,y)
n.widget_pos[0][:]=(30,12)
# Mission-state persistence is deliberately omitted from this first playable slice.
# Remove save/load buttons until a tested serialization path is implemented.
for i in (3,9):s.Nodes[i].used=0
n=s.Nodes[13]
for j in range(100):
 readout=bytes(s.widget_readout[13][j]).split(b'\x00')[0]
 if b'Health' in readout:n.widget_used[j]=0
s.iChanged=1
data=bytes(s);assert len(data)==PROJECT.stat().st_size
temp=PROJECT.with_suffix('.new');temp.write_bytes(data);temp.replace(PROJECT)
assert load().Nodes[7].level_name==b'mapbank\\Aegis Reach - Relayfall.fpm'

# Authored tactical layout: generated from the actual placed-object coordinates.
im=Image.new('RGB',(1000,1420),(11,20,31));d=ImageDraw.Draw(im)
fontpath=r'C:\Windows\Fonts\consola.ttf'
font=ImageFont.truetype(fontpath,20);large=ImageFont.truetype(fontpath,40);small=ImageFont.truetype(fontpath,15)
d.text((55,30),'AEGIS REACH / RELAYFALL',fill=(218,234,237),font=large)
d.text((55,89),'TACTICAL LAYOUT // NOT AN IN-ENGINE SCREENSHOT',fill=(71,200,215),font=small)
def p(x,z):return (int(500+x*.185),int(800-z*.16))
for x in range(100,951,80):d.line((x,130,x,1320),fill=(24,38,52))
for y in range(160,1321,80):d.line((60,y,945,y),fill=(24,38,52))
layout=json.loads((GAME/'Design/mission-layout.json').read_text())
for o in layout:
 x,y=p(o['x'],o['z']);kind=o['kind'];name=o['asset'].split('\\')[-1]
 if name=='Bastion Wall.fpe':
  w,h=(15,97) if o['rotation']==90 else (111,13);d.rectangle((x-w/2,y-h/2,x+w/2,y+h/2),fill=(79,100,117))
 elif kind=='cover':d.rectangle((x-14,y-9,x+14,y+9),fill=(116,130,136))
 elif kind in ('enemy','reserve'):d.polygon([(x,y-7),(x+7,y+6),(x-7,y+6)],fill=(232,109,79) if kind=='enemy' else (191,119,178))
 elif kind=='relay':
  d.rectangle((x-11,y-11,x+11,y+11),fill=(53,217,229));d.text((x+20,y-10),o['name'].split('//')[0],fill=(93,236,241),font=font)
 elif kind=='extraction':
  d.ellipse((x-25,y-25,x+25,y+25),outline=(89,227,226),width=4);d.text((x+33,y-8),'KESTREL LZ',fill=(100,237,230),font=font)
 elif kind=='medical':d.text((x-8,y-10),'+',fill=(106,237,171),font=large)
 elif kind in ('ammo','weapon'):d.ellipse((x-4,y-4,x+4,y+4),fill=(243,187,89))
d.text((55,1360),'CYAN relay / RED infantry / PURPLE reserve / GOLD supplies',fill=(174,198,207),font=font)
im.save(FILES/'imagebank/aegis_reach/tactical-map.png');im.save(GAME/'Design/tactical-map.png')
print('Branded and connected native storyboard. Original initialization backed up in Design.')
