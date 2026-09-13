"""Validate the shipped cubemap, sky selection and glare settings, not art quality."""
import struct
import zipfile
import numpy as np
from PIL import Image
from build_vesper_sky import DEST, SOURCE, SIZE, ROOT, directions, sample
from max_archive import PASSWORD

raw=(DEST/'vesper_orbital_cube.dds').read_bytes()
h=struct.unpack('<31I',raw[4:128])
assert raw[:4]==b'DDS ' and h[0]==124
assert h[2:4]==(SIZE,SIZE) and h[6]==11
assert h[19:26]==(0x41,0,32,0xff,0xff00,0xff0000,0xff000000)
assert h[27]==0xfe00, 'not all six native cube faces are declared'
face_bytes=sum(max(1,SIZE>>m)**2*4 for m in range(11))
assert len(raw)==128+6*face_bytes, 'missing/truncated cube faces or mips'
source=np.asarray(Image.open(SOURCE).convert('RGB'),dtype=np.float32)
assert source.shape[1]==2*source.shape[0]
# Independent axis expectations catch swapped faces, including the two poles.
centers=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
for face,axis in enumerate(centers):
    got=tuple(float(a[0,0]) for a in directions(face,1))
    assert got==axis, (face,got)
    pixels=np.frombuffer(raw,dtype=np.uint8,count=SIZE*SIZE*4,
                         offset=128+face*face_bytes).reshape(SIZE,SIZE,4)
    assert np.all(pixels[:,:,3]==255)
    expected=sample(source,*directions(face,SIZE))
    assert np.array_equal(pixels[:,:,:3],expected), 'DDS channel/face order drift'
# Join mean checks broad banding; tiny star differences do not imply a broken edge.
assert np.abs(source[:,0]-source[:,-1]).mean()<8, 'panorama wrap has a broad tonal seam'
with zipfile.ZipFile(ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm') as z:
    v=z.read('visuals.ini',pwd=PASSWORD).decode('latin1')
settings=dict(line.split('=',1) for line in v.splitlines() if '=' in line)
assert settings['visuals.sky$']=='vesper_orbital'
for key in ('LightShafts','LensFlare','lightraymode','SkyCloudCoverage','SkyCloudiness'):
    assert float(settings['visuals.'+key])==0, key+' may wash out the orbital sky'
assert 1<=float(settings['visuals.SunIntensity'])<=1.5
assert float(settings['visuals.AutoExposure'])==0
assert (DEST/'skyspec.txt').is_file() and (DEST/'preview.bmp').is_file()
print('VESPER SKY PASS: full DDS cube/mips/channels, direction mapping, wrap and native selection.')
print('Native MAX sky orientation, luminance, seams and reflections still need review.')
