import subprocess
import numpy as np
import matplotlib.pyplot as plt

img=np.zeros((80,80))
fig = plt.figure('Temp of surface')
plt1 = plt.imshow(img,
           extent=[0,80,0,80],
           origin="upper", vmin=0, vmax=50000)
plt.title('T of surface')
plt.colorbar()
plt.xlabel('mm')
plt.ylabel('mm')
plt.pause(0.1)

proc = subprocess.Popen(['Release/Tachyon_Test',],stdout=subprocess.PIPE)
i=0

while True:
   data = proc.stdout.read(12800)
   print ("data:", type(data), len(data))
   if (len(data) == 0): break
   img = np.frombuffer(data, dtype=np.short).reshape((80,80))
   print ("img.shape:", img.shape)
   plt1.set_data(img)
   i+=1
   plt.title('T of surface #'+str(i))
   fig.canvas.draw()
   fig.canvas.flush_events()