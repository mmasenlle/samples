import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

file1 = open('C:\\tmp\\profile1.csv', 'r')
lines = file1.readlines()

xx = list()
zz = list()
for line in lines:
    tokens = line.split(';')
    x = list()
    z = list()
    for i in range(0, len(tokens), 2):
        x.append(float(tokens[i]))
        z.append(float(tokens[i+1]))
    xx.append(np.array(x))
    zz.append(np.array(z))

xx=np.array(xx)
zz=np.array(zz)

######################### 3d surface
X=xx
Y=np.zeros(X.shape)
vx = 0.10 # dm/s
for i in range(Y.shape[0]): Y[i,:] = i * vx
Z=zz
zidx = np.argwhere((zz==0))
Z[zidx[:,0],zidx[:,1]] = float('nan')
Z=50-Z
fig3 = plt.figure('Surface 3d')
from mpl_toolkits.mplot3d import Axes3D
ax1 = fig3.gca(projection='3d')
# ax1.scatter(X, Y, Z)
surf = ax1.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0, vmin=0, vmax=50)
plt.title('Point cloud surface')
ax1.set_xlabel('X (mm)')
ax1.set_ylabel('Y (mm)')
ax1.set_zlabel('Z (mm)')
ax1.set_xlim(-50, 50)
ax1.set_zlim(0, 50)
# fig3.colorbar(surf, shrink=0.5)


######### profiles animation
# plt.plot(tt)
if False:
    fig = plt.figure('Profiles')
    ax1 = fig.add_subplot(111)
    ax1.clear()
    ax1.set_xlim((-25,25))
    ax1.set_ylim((0,50))
    ax1.grid()
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Z (mm)')
    line1, = ax1.plot(xx[0],zz[0],'.')
    for i in range(len(tt)):
        ax1.set_title('Profile at t=' + str(tt[i]) + ' s')
        line1.set_xdata(xx[i])
        line1.set_ydata(zz[i])
        fig.canvas.draw()
        fig.canvas.flush_events()
if False:
    plt.figure('Center')
    plt.title('Z along Y (x='+str(zz[0,656])+')')
    plt.plot(tt, zz[:,656])
    plt.xlabel('Y (s)')
    plt.ylabel('Z (mm)')
    # plt.xlim((0,25))
    plt.ylim((0,50))




