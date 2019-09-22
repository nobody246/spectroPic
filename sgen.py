import pyaudio
import numpy as np
from time import sleep
import os
import random
import math
import threading
import wave
from PIL import Image

#todo add as params
volume = 1
fs = 44100
duration = .20
sampleSz = 1024
f = 0
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                output=True)
rstream = p.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=fs,
                 input=True,
                 frames_per_buffer=sampleSz)
frms = []
stopThread = False
def getSndData():
   global rstream, frms, sampleSz, stopThread
   while not stopThread:
      y=rstream.read(sampleSz)
      frms.append(y)  
def playFreq():
   global f,fs, volume, duration
   F = 0
   if type(f) == "Number":
      F=f
   else:
      if len(f) == 0:
          return False
      F=f[0]
   samps = np.sin(2* np.pi*np.arange(fs*duration)*F/fs).astype(np.float32)
   for fr in f[1:]:
      samps = np.add(samps,(np.sin(2*np.pi*np.arange(fs*duration)*fr/fs)).astype(np.float32))
   stream.write(volume * samps)
   #fix for underruns in ALSA
   free = stream.get_write_available() 
   if free>sampleSz:
      stream.write(chr(0) * sampleSz * 2)
th = threading.Thread(target=getSndData)
img = Image.open("img2.png")           
arr=list(img.getdata())
iw,ih = img.size
curBit = 0
curRow = 0
picRow = []
picData = []
for px in arr:
   if (px[0] + px[1] + px[2]) <= 300:
      picRow.append(1)
   else:
      picRow.append(0)
   if curBit >= iw:
      curRow+=1
      curBit=0
      picData.append(picRow)
      picRow = []
   curBit+=1
ww=[]
colInd = 0
while colInd < len(picData):
   w=[]
   btInd = 1
   for bt in picData[colInd]:
      if bt:
         w.append(btInd * 200)
      else:
         w.append(0)
      btInd+=1
   ww.append(w)
   colInd+=1
#play
loopCount=2
th.start()
xx = 0
t=0
while xx<=loopCount:
   t=0
   while t<len(picData):
      f = ww[t]
      playFreq()
      t+= 1
   xx+=1
stopThread=True
th.join()
stream.stop_stream()
stream.close()
rstream.stop_stream()
rstream.close()
p.terminate()
waveFile = wave.open('s.wav', 'wb')
waveFile.setnchannels(1)
waveFile.setsampwidth(p.get_sample_size(pyaudio.paInt16))
waveFile.setframerate(fs)
waveFile.writeframes(b''.join(frms))
waveFile.close()
#os.system('python spec.py')
os.system('audacity s.wav')

