"""Inspect and update the user's native MAX storyboard, preserving its menus."""
from native_format import ROOT
from pathlib import Path
import ctypes as C,re,shutil
src=(ROOT/'tools/reference/imgui_gg_dx11.h').read_text()
constants={'STORYBOARD_MAXOUTPUTS':30,'STORYBOARD_MAXWIDGETS':100,'STORYBOARD_MAXNODES':150}
types={'int':C.c_int32,'float':C.c_float,'char':C.c_char,'ImVec2':C.c_float*2,'ImVec4':C.c_float*4}
def definition(name):
 body=src.split('struct '+name+'\n{',1)[1].split('\n};',1)[0]
 body=re.sub(r'//[^\n]*','',body)
 fields=[]
 for statement in body.split(';'):
  m=re.search(r'\b(\w+)\s+(\w+)\s*((?:\[\w+\])*)\s*(?:=.*)?$',statement.strip(),re.S)
  if not m:
   if statement.strip():raise ValueError(statement)
   continue
  typ=types[m[1]]
  for dim in reversed(re.findall(r'\[(\w+)\]',m[3])):typ=typ*int(constants.get(dim,dim))
  fields.append((m[2],typ))
 cls=type(name,(C.Structure,),{'_fields_':fields});types[name]=cls;return cls
Node=definition('StoryboardNodesStruct');Story=definition('StoryboardStruct')
PROJECT=ROOT/'Aegis Reach/Files/projectbank/Aegis Reach/project203.dat'
def load():
 data=PROJECT.read_bytes()
 assert len(data)==C.sizeof(Story),(len(data),C.sizeof(Story))
 s=Story.from_buffer_copy(data);assert s.sig==b'Storyboard' and s.iStoryboardVersion==203
 return s
if __name__=='__main__':
 s=load();print('Native storyboard:',s.gamename,'size',C.sizeof(s),'custom folder',s.customprojectfolder)
 for i,n in enumerate(s.Nodes):
  if n.used:print(i,n.type,n.id,n.used,n.title,n.level_name,n.lua_name,n.scene_name)
