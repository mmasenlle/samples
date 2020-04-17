import numpy as np
import matplotlib.pyplot as plt
import control

k=24.0
rho=7925
cp=460
v=0.002
a=k/(rho*cp)
q=1000


ops=np.load('output_points_vel.npy')

X=np.load('output_data_vel.npy')

# plt.plot(X[:1000,2])
dt = X[1,0]-X[0,0]
N = int(X.shape[0]/2)
freqs = np.arange(N)/(2*N*dt)
wf = freqs*2*np.pi
idx = np.logspace(0,3,100).astype(int)
w = wf[idx]
s = 1j*w
ft_vel = lambda x,y,z: -q/(rho*cp)*(v*np.sqrt(x**2 + y**2 + z**2) + (-x)*np.sqrt(4*a*s + v**2))*np.exp(-(v*(-x) + np.sqrt(4*a*s + v**2)*np.sqrt(x**2 + y**2 + z**2))/(2*a))/(4*np.pi*a**2*np.sqrt(4*a*s + v**2)*np.sqrt(x**2 + y**2 + z**2))

R = lambda x,y,z: np.sqrt(x**2+y**2+z**2)
D = lambda s: np.sqrt(4*a*s + v**2)
XX = lambda x,y,z,s: (v*R(x,y,z) - x*D(s))*np.exp(-R(x,y,z)*D(s)/(2*a))/D(s)
# XX3 = lambda x,y,z,s: (v*R(x,y,z) - x*D(s))*np.exp(-R(x,y,z)*D(s)/(2*a))
XX3 = lambda x,y,z,s: np.exp(-R(x,y,z)*D(s)/(2*a))
XX4 = lambda x,y,z,s: np.exp((v*x-R(x,y,z)*D(s))/(2*a))
# ft_vel2 = lambda x,y,z: .05/(rho*cp)*q*np.exp(v*x/(2*a))/(4*s*np.pi*a**2*R(x,y,z))*(XX(x,y,z,s)-XX(x,y,z,0))
ft_vel2 = lambda x,y,z: .2*q*np.exp(v*x/(2*a))/(4*s*np.pi*a*k*R(x,y,z))*(XX(x,y,z,s)-XX(x,y,z,0))
ft_vel3 = lambda x,y,z: q*v*np.exp(v*x/(2*a))/(4*s*np.pi*a*k*R(x,y,z))*(XX3(x,y,z,s)-XX3(x,y,z,0))
# ft_vel4 = lambda x,y,z: q*v/(4*s*np.pi*a*k*R(x,y,z))*(XX4(x,y,z,s)-XX4(x,y,z,0))
# ft_vel4 = lambda x,y,z: q*v*v*np.exp(v*x/(2*a))/(4*s*np.pi*a*k*R(x,y,z))*(np.exp(-R(x,y,z)*D(s)/(2*a))/np.sqrt(2*s*x*x*v + v**2)-np.exp(-R(x,y,z)*v/(2*a))/v)
# ft_vel4 = lambda x,y,z: q*v*np.exp(v*x/(2*a))/(4*s*np.pi*a*k*R(x,y,z))*(np.exp(-R(x,y,z)*D(s)/(2*a))/(-s*x/v + 1)-np.exp(-R(x,y,z)*v/(2*a)))
ft_vel11 = lambda x,y,z: q*np.exp(v*x/(2*a))/(4*s*np.pi*a*k*R(x,y,z))*(np.exp(-R(x,y,z)*D(s)/(2*a))/(s*(R(x,y,z)-x) + 1)-np.exp(-R(x,y,z)*D(s)/(2*a)))
ft_vel12 = lambda x,y,z: q*v*(R(x,y,z)-x)*np.exp(v*x/(2*a))/(4*s*np.pi*a*k*R(x,y,z)*R(x,y,z))*(np.exp(-R(x,y,z)*D(s)/(2*a))-np.exp(-R(x,y,z)*v/(2*a)))
ft_vel13 = lambda x,y,z: q*v*v*np.exp(v*x/(2*a))/(4*s*np.pi*a*k*R(x,y,z))*(np.exp(-R(x,y,z)*D(s)/(2*a))/np.sqrt(-2*s*x*v + v**2)-np.exp(-R(x,y,z)*v/(2*a))/v)



U = np.fft.fft(X[:,2])
for i in range(3,X.shape[1]):
    H1 = U * np.fft.fft(X[:,i]) / U**2
    plt.figure('Bode T/Vel ' + str(ops[i - 3]))
    control.bode_plot((control.frd(H1[idx], w), control.frd(ft_vel3(*ops[i - 3]), w), control.frd(ft_vel11(*ops[i - 3]), w),
                       control.frd(ft_vel12(*ops[i - 3]), w), control.frd(ft_vel13(*ops[i - 3]), w)), w, dB=True)
    plt.legend(('fem', 'fdt3', 'fdt11', 'fdt12', 'fdt13'))

# exit(0)
#
# U = np.fft.fft(X[:,2])
# for i in range(3,X.shape[1]):
#     H1 = U * np.fft.fft(X[:,i]) / U**2
#     plt.figure('Bode T/Vel ' + str(ops[i - 3]))
#     control.bode_plot((control.frd(H1[idx], w)), w, dB=True)
#     plt.legend(('fem'))
