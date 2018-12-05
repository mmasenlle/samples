
from dolfin import *
import datetime
#from scipy.interpolate import griddata

Lx=.08;
Ly=.04;
Lz=.01;
input_x=.02;
input_y=.02;
input_z=.0;

print "% fenics(",__file__,") ",datetime.datetime.utcnow()
print "Lx=",Lx,";"
print "Ly=",Ly,";"
print "Lz=",Lz,";"
print "input_x=",input_x,";"
print "input_y=",input_y,";"
print "input_z=",input_z,";"

# Create mesh and function space
mesh = Box(0.0, 0.0, 0.0, Lx, Ly, Lz, 48, 24, 6)
V = FunctionSpace(mesh, "CG", 1)

coor = mesh.coordinates()
print "fenicsX=["
for i in range(len(coor)):
	print "%g, %g, %g" % (coor[i][0], coor[i][1], coor[i][2])
print "];"

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

k = Constant(24)
rho = Constant(7925)
Cp = Constant(460)

vel = Constant((0.002,0,0))

a1 = k*inner(nabla_grad(u), nabla_grad(v))*dx + rho*Cp*inner(vel, nabla_grad(u))*v*dx
L1 = Constant(0)*v*dx

Pot=100
delta = PointSource(V, Point(input_x,input_y,input_z), Pot)

A1, b1 = assemble_system(a1, L1, bc)

u1 = Function(V)
delta.apply(b1)
solve(A1, u1.vector(), b1)

u_nodal_values = u1.vector()
u_array = u_nodal_values.array()
print "fenics_gT=["
for i in range(len(u_array)):
	print "%g" % (u_array[i])
print "];"

u_prev = u1
dt = 0.5 # time step

u = TrialFunction(V)
v = TestFunction(V)

vel = Constant((0.0022,0,0)) # 10% step

a = rho*Cp*u*v*dx + dt*k*inner(nabla_grad(u), nabla_grad(v))*dx + dt*rho*Cp*inner(vel, nabla_grad(u))*v*dx
L = rho*Cp*u_prev*v*dx

A = assemble(a)
b = None

u = Function(V)

T = 100 # total simulation time
t = 0

ind=604
#plot(u_prev, interactive=True)

print "fenics_gT2=["

while t <= T:
	b = assemble(L, tensor=b)
	bc.apply(A, b)
	delta.apply(b)
	solve(A, u.vector(), b)
	t += dt
	u_prev.assign(u)
	print "%g" % (u.vector().array()[ind])

print "];"

#plot(u, interactive=True)

exit(0)
