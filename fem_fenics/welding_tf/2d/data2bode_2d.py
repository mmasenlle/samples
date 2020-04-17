import numpy as np
import matplotlib.pyplot as plt
from scipy.special import kv
import control

T0=np.load('T0_2d.npy')
X = np.load('X_2d.npy')
nds1f = np.argwhere((X[:, 1] == 0.02))
plt.plot(X[nds1f,0],T0[nds1f])
nds1f = np.argwhere((X[:, 0] == 0.02))
plt.plot(X[nds1f,1],T0[nds1f])


k=24.0
rho=7925
cp=460
v=0.002
a=k/(rho*cp)
h=100000
Lz=1
b=2*h*a/k/Lz

ops=np.load('output_points_2d.npy')

X=np.load('output_data_pow_2d.npy')

# plt.plot(X[:1000,2])
dt = X[1,0]-X[0,0]
N = int(X.shape[0]/2)
freqs = np.arange(N)/(2*N*dt)
wf = freqs*2*np.pi
idx = np.logspace(0,int(np.log10(N)),100).astype(int)
w = wf[idx]
s = 1j*w
ft_pot = lambda x,y: np.exp(v*x/(2*a))/(2*np.pi*k)*kv(0,np.sqrt((x**2+y**2)*(4*a*s+4*a*b+v**2))/(2*a))

U = np.fft.fft(X[:,1])
for i in range(3,X.shape[1]):
    H1 = U * np.fft.fft(X[:,i]) / U**2
    plt.figure('Bode T/Pow ' + str(ops[i - 3]))
    control.bode_plot((control.frd(H1[idx], w),control.frd(ft_pot(*ops[i - 3]), w)),w, dB=True)
    plt.legend(('fem', 'fdt'))
