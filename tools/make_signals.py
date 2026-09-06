from pathlib import Path
import numpy as np,wave
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'Aegis Reach/Files/audiobank/aegis_reach'
sr=24000
def save(name,samples):
 with wave.open(str(OUT/name),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
  w.writeframes((np.clip(samples,-.8,.8)*32767).astype('<i2').tobytes())
t=np.arange(int(sr*1.1))/sr;a=np.zeros_like(t)
for offset,freq in [(0,440),(.2,660),(.4,880)]:
 u=t-offset;env=np.where(u>=0,np.exp(-np.maximum(u,0)*7)*np.minimum(np.maximum(u,0)*100,1),0)
 a+=.17*np.sin(2*np.pi*freq*u)*env
save('relay.wav',a)
# Original quiet, loopable electronic underscore. 32 seconds = 16 bars at 120 BPM.
t=np.arange(sr*32)/sr;a=np.zeros_like(t)
for freq in (55,82.4069,110,130.8128,164.8138):
 a+=.014*np.sin(2*np.pi*freq*t)*(0.7+0.3*np.sin(2*np.pi*t/8))
for beat in range(64):
 u=t-beat*.5;env=np.where((u>=0)&(u<.45),np.exp(-np.maximum(u,0)*15),0)
 a+=.04*np.sin(2*np.pi*(65*u-20*u*u))*env
for beat in range(32):
 freq=[220,329.6276,261.6256,293.6648][beat%4];u=t-beat
 env=np.where((u>=0)&(u<.8),np.exp(-np.maximum(u,0)*5)*np.minimum(np.maximum(u,0)*40,1),0)
 a+=.018*np.sin(2*np.pi*freq*u)*env
a*=np.minimum(t/1,1)*np.minimum((32-t)/1,1)
save('reach-underscore.wav',a)
print('Created original relay cue and 32-second ambient underscore.')
