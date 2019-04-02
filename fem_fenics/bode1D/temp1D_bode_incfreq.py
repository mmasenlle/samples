import sys
from dolfin import *

# Create mesh and function space
mesh = IntervalMesh(1000,0,0.4)
V = FunctionSpace(mesh, "CG", 1)

# Sub domain for Dirichlet boundary condition
class DirichletBoundary(SubDomain):
    def inside(self, x, on_boundary):
        return on_boundary and x[0] < DOLFIN_EPS

# Define variational problem
u = TrialFunction(V)
v = TestFunction(V)

# Define boundary condition
u0 = Constant(0.0)
bc = DirichletBC(V, u0, DirichletBoundary())

Pot=2e7
k = Constant(24)
rho = Constant(7925)
Cp = Constant(460)

h = Constant(100000)
#h = Constant(0)
Tinf = Constant(0)
P = Constant(3.5449)

v_nom = 0.002
vel = Constant(v_nom)

a1 = k*inner(nabla_grad(u), nabla_grad(v))*dx + rho*Cp*vel*u.dx(0)*v*dx + P*h*inner(u,v)*dx
L1 = Constant(0)*v*dx + P*h*Tinf*v*dx

A1, b1 = assemble_system(a1, L1, bc)
delta = PointSource(V, Point(0.05,), Pot)
delta.apply(b1)

u1 = Function(V)

# estacionario
solve(A1, u1.vector(), b1)
print ("max: ", max(u1.vector()),"(K), T(x=0.2): ", u1.vector()[500]) # 137.15


# transitorio
u_prev = u1 #interpolate(u0, V)
dt = 0.05 # time step

u = TrialFunction(V)
v = TestFunction(V)

b = None
uf = Function(V)

T = 300 # total simulation time
T1 = 2
t = 0.0

delta = PointSource(V, Point(0.05,), dt*Pot)

# Save solution to file
#file = File("temp.pvd")
#file << (u1, t)

# Control
idxT1 = 1000 - 150 # from Matlab
refT1 = u1.vector()[idxT1]
idxT2 = 1000 - 375 # from Matlab
refT2 = u1.vector()[idxT2]

n = V.dim()
d = mesh.geometry().dim()
dof_coordinates = V.tabulate_dof_coordinates()
dof_coordinates.resize((n, d))
dof_x = dof_coordinates[:, 0]
print ("T(x=",dof_x[idxT1],",t=0): ", refT1, " K")
print ("T(x=",dof_x[idxT2],",t=0): ", refT2, " K")

amp=.0002
# freqs=(0.001,0.01,0.1,1,10,100,1000)
# freqs=(0.0001,0.001,0.005,0.01,0.02,0.05,0.1,0.2,0.5,1,2,5,10)
# for i in range(len(freqs)):
t = 0.0
#print ("Starting freq "+str(freqs[i]))
#print ("fenics_bode_freqs("+str(i+1)+")="+str(freqs[i]), file=sys.stderr)
print ("fenics_bode_inc=[", file=sys.stderr)
print (repr(t), repr(u1.vector()[idxT1]), repr(Pot), repr(u1.vector()[idxT2]), repr(v_nom), file=sys.stderr)

N = 100000
T = 1000
dt = T/N
freq = .0001
#while t <= T:
for ii in range(N):
    t += dt
    uu=v_nom+(amp*sin(2*pi*freq*t))
    freq += .0001
    vel = Constant(uu)
    a = rho*Cp*u*v*dx + dt*k*inner(nabla_grad(u), nabla_grad(v))*dx + dt*rho*Cp*vel*u.dx(0)*v*dx + dt*P*h*u*v*dx
    L = rho*Cp*u_prev*v*dx + dt*P*h*Tinf*v*dx
    b = assemble(L, tensor=b)
    A = assemble(a)
    bc.apply(A, b)
    Pt = Pot #+ p_ctrl
    delta = PointSource(V, Point(0.05,), dt*Pt)
    delta.apply(b)
    solve(A, uf.vector(), b)
    #t += dt
    #print ("T(x=",dof_x[idxT1],"): ", u.vector().array()[idxT1], " K / p_ctrl: ", p_ctrl, file=sys.stderr)
    print (repr(t), repr(uf.vector()[idxT1]), repr(Pot), repr(uf.vector()[idxT2]), repr(uu), file=sys.stderr)
    u_prev.assign(uf)

print ("];", file=sys.stderr)

#file << (uf, t)

print ("T(x=",dof_x[idxT1],",t=",T,"): ", uf.vector()[idxT1], " K")
print ("T(x=",dof_x[idxT2],",t=",T,"): ", uf.vector()[idxT2], " K")
print ("max(t=",t,"): ", max(uf.vector()),"(K), T(x=0.2): ", uf.vector()[500]) # 137.15
# Plot solution
#plot(u, interactive=True)
