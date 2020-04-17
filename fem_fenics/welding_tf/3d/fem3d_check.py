import numpy as np
import matplotlib.pyplot as plt
import control,scipy

# material constants
k=24.0
rho=7925
cp=460
a=k/(rho*cp)
# piece dimensions
Lx,Ly,Lz=.08,.04,.01
# input source point
xi,yi,zi=.02,.02,0
# output point from input source point
x,y,z=.01,0,0
# inputs
q, v = 100, 0.002

# spatial discretization
nx,ny,nz=33,17,5
n=nx*ny*nz

useDelaunay = False
if useDelaunay:
    X=np.linspace(0,Lx,nx)
    Y=np.linspace(0,Ly,ny)
    Z=np.linspace(0,Lz,nz)
    XX,YY,ZZ=np.meshgrid(X,Y,Z)
    XX=XX.reshape((n,1))
    YY=YY.reshape((n,1))
    ZZ=ZZ.reshape((n,1))
    nodes=np.array((XX,YY,ZZ)).T.reshape(n,3)
    del XX
    del YY
    del ZZ
    dtri = scipy.spatial.Delaunay(nodes,qhull_options='Qt')
    nodes=dtri.points
else:
    nodes = np.load('mesh_X.npy')
    cells = np.load('mesh_cells.npy')

# locate input and output node numbers
ni = np.argwhere(np.all((nodes-np.array([xi,yi,zi]))==0, axis=1))[0][0]
no = np.argwhere(np.all((nodes-np.array([xi+x,yi+y,zi+z]))==0, axis=1))[0][0]

# assemble matrices
K=np.zeros((n,n))
C=np.zeros((n,n))
f=np.zeros(n)
f[ni] = q
vu=np.array([[1,1,1,1],[0,0,0,0],[0,0,0,0]]).T
ii=0
for i in range(cells.shape[0]):
    nds=cells[i,:]
    AA=np.append(np.ones((4,1)),nodes[nds,:], axis=1)
    V=np.linalg.det(AA)/6
    abcd=np.linalg.solve(AA,np.eye(4))
    #abcd = np.linalg.pinv(AA) @ np.eye(4)
    B=abcd[1:,:]
    # B=np.array([[abcd[1, 0], abcd[1, 1], abcd[1, 2], abcd[1, 3]],
    #             [abcd[2, 0], abcd[2, 1], abcd[2, 2], abcd[2, 3]],
    #             [abcd[3, 0], abcd[3, 1], abcd[3, 2], abcd[3, 3]]])
    K[np.ix_(nds,nds)] += (B.T @ B) * V * k + (vu @ B)*V*v*cp*rho/4
    C[np.ix_(nds,nds)] += np.eye(4)*V*cp*rho/4

# force dirichlet conditions
nds0 = np.argwhere(nodes[:,0]==0.0)[:,0]
bcwt = np.trace(K)/nx
K[nds0,:] = 0
K[:,nds0] = 0
K[np.ix_(nds0,nds0)] = bcwt
# solve stationary system
T = np.linalg.solve(K, f)
# plot temperatures on the source path
nds1 = np.argwhere((nodes[:,1]==0.02)&(nodes[:,2]==0))
plt.plot(nodes[nds1,0],T[nds1])

# assembled system from fenics
A1=np.load('A13d.npy')
b1=np.load('b13d.npy')
u1=np.load('u13d.npy')
dof_coor = np.load('dof_coordinates.npy')
if False:
    nds1f = np.argwhere((dof_coor[:, 1] == 0.02) & (dof_coor[:, 2] == 0))

    plt.plot(dof_coor[nds1f,0],u1[nds1f])
    # solved here
    TT = np.linalg.solve(A1, b1)
    plt.plot(dof_coor[nds1f,0],TT[nds1f])


n1 = np.argwhere((dof_coor[:, 0] == 0.03) & (dof_coor[:, 1] == 0.02) & (dof_coor[:, 2] == 0))
n2 = np.argwhere((dof_coor[:, 0] == 0.02) & (dof_coor[:, 1] == 0.03) & (dof_coor[:, 2] == 0))
K,f=A1,b1

Asys=np.linalg.solve(C, -K)
Bsys=np.array([np.linalg.solve(C, f/q)]).T
Csys1=Csys2=np.zeros(nx)
Csys1[n1]=1
Csys2[n2]=1
Dsys=0
qsys1,qsys2 = control.ss(Asys,Bsys,Csys1,Dsys),control.ss(Asys,Bsys,Csys2,Dsys)