"""GameGuru MAX .ele codec, derived from the public EntityWriter layout.

Reads and writes every field without dropping unknown/default values. Supports
the installed example maps (v338), including materials and editor groups.
"""
from pathlib import Path
import re, struct, zipfile

ROOT = Path(__file__).resolve().parent.parent
INSTALL = Path(r'C:\Program Files (x86)\Steam\steamapps\common\GameGuru MAX\Files')
SOURCE = (ROOT/'tools/reference/MAX-Entity.cpp').read_text(encoding='utf-8-sig')
SAVE = SOURCE[SOURCE.index('void entity_saveelementsdata (bool'):]
BLOCKS = {}
for match in re.finditer(r'if\s*\(\s*t.versionnumbersave\s*>=\s*(\d+)\s*\)', SAVE):
    v = int(match[1]); start = SAVE.index('{', match.end()); depth = 1; end = start+1
    while depth:
        if SAVE[end] == '{': depth += 1
        if SAVE[end] == '}': depth -= 1
        end += 1
    BLOCKS[v] = SAVE[start+1:end-1]

def fields(v):
    result=[]; seen={}
    for line in BLOCKS[v].splitlines():
        if line.lstrip().startswith('//'): continue
        m=re.search(r'writer.Write(Long|Float|String(?:Include0xa)?)\s*\(\s*(.*?)\s*\);', line)
        if not m: continue
        kind={'Long':'i','Float':'f','String':'s','StringInclude0xa':'s'}[m[1]]
        expr=m[2].replace('t.entityelement[ent].','').replace('.Get()','').replace(' & 0x00FFFFFF','')
        key=expr if expr not in ('0','0.0f','""') else 'reserved'
        n=seen.get(key,0);seen[key]=n+1
        if n or key=='reserved': key += '_'+str(n)
        result.append((kind,f'{v}:{key}'))
    return result

class Codec:
    def __init__(self,data=None,values=None):
        self.data=data;self.pos=0;self.out=bytearray();self.values=values or {};self.reading=data is not None
    def field(self,kind,key):
        if self.reading:
            if kind=='s':
                end=self.data.index(b'\r\n',self.pos); val=self.data[self.pos:end].decode('latin1');self.pos=end+2
            else:
                val=struct.unpack_from('<'+kind,self.data,self.pos)[0];self.pos+=4
            self.values[key]=val
        else:
            val=self.values.get(key,'' if kind=='s' else 0)
            self.out.extend(val.encode('latin1')+b'\r\n' if kind=='s' else struct.pack('<'+kind,val))
        return val
    def fields(self,seq):
        for kind,key in seq:self.field(kind,key)
    def material(self,i,first=False):
        p=f'material{i}:'
        for k in ('cast','double','reflect','transparent'):self.field('i',p+k)
        self.field('s',p+'base');self.field('s',p+'emissive');self.field('f',p+'reflectance')
        if first:self.field('i',p+'reserved')
        for k in ('baseMap','normalMap','surfaceMap','displacementMap','emissiveMap','occlusionMap'):self.field('s',p+k)
        for k in ('normal','roughness','metalness','emission','alpha'):self.field('f',p+k)
    def entity(self,version):
        for v in sorted(BLOCKS):
            if v>version:break
            if v==314:
                self.field('i','314:custom');self.field('i','314:active');self.material(0,True)
            elif v==316:
                self.fields(fields(v)[:9])
                for i in range(10):
                    for kind,k in fields(v)[9:]:self.field(kind,k.replace('[i]',f'[{i}]'))
            elif v==317:
                for i in range(1,100):self.material(i)
            elif v==318:
                for i in range(100):self.field('f',f'material{i}:bias')
            elif v==319:
                self.field('i','319:groupID');n=self.field('i','319:groups')
                assert 0<=n<=1000,n
                for i in range(n):
                    items=self.field('i',f'319:items{i}');assert 0<=items<10000,items
                    for j in range(items):
                        for k in range(10):self.field('i' if k<3 else 'f',f'319:g{i}i{j}f{k}')
                for i in range(n):self.field('i',f'319:thumb{i}')
            elif v==334:
                n=self.field('i','334:groups');assert 0<=n<=1000,n
                for i in range(n):self.field('s',f'334:name{i}')
            else:self.fields(fields(v))
        return self.values

def read_ele(data):
    version,count=struct.unpack_from('<ii',data);pos=8;entities=[]
    assert 313<=version<=342,(version,count)
    for i in range(count):
        c=Codec(data[pos:]);e=c.entity(version);entities.append(e);pos+=c.pos
    assert pos==len(data),(pos,len(data),version,count)
    return version,entities

def write_ele(version,entities):
    out=bytearray(struct.pack('<ii',version,len(entities)))
    for e in entities:
        c=Codec(values=e);c.entity(version);out.extend(c.out)
    return bytes(out)

def read_map(name):
    z=zipfile.ZipFile(INSTALL/'mapbank'/name);z.setpassword(b'mypassword')
    version,entities=read_ele(z.read('map.ele'))
    ent=z.read('map.ent');bank=['']+ent[4:].decode('latin1').splitlines()
    assert len(bank)-1==struct.unpack_from('<i',ent)[0]
    return z,version,entities,bank

if __name__=='__main__':
    for name in ['switch escape.fpm','Disruption.fpm','canyon offensive.fpm']:
        z,v,es,b=read_map(name)
        assert write_ele(v,es)==z.read('map.ele')
        print(name,v,len(es),'byte-exact round trip OK')
        for e in es:
            path=b[e['101:bankindex']]
            if any(k in path.lower() for k in ('player start','characters','weapons')):
                print(e['101:eleprof.name_s'],path,[(k,e[k]) for k in ('101:x','101:y','101:z','101:eleprof.strength','101:eleprof.hasweapon_s')])
