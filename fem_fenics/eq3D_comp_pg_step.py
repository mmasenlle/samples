
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
		
Pot=70000
x0 = input_x
y0 = input_y
sigma = 0.0005

class GaussSource(Expression):
    def eval(self, values, x):
		if (x[2] < DOLFIN_EPS):
			values[0] = Pot*exp(-.5*(( ( (x[0]-x0)/sigma )**2 + ( (x[1]-y0)/sigma )**2 ) )) / (2*pi*sigma*sigma)
		else:
			values[0] = 0

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

f = GaussSource()

a1 = k*inner(nabla_grad(u), nabla_grad(v))*dx + rho*Cp*inner(vel, nabla_grad(u))*v*dx
L1 = f*v*dx

A1, b1 = assemble_system(a1, L1, bc)

u1 = Function(V)
solve(A1, u1.vector(), b1)

u_nodal_values = u1.vector()
u_array = u_nodal_values.array()
print "fenics_gT=["
for i in range(len(u_array)):
	print "%g" % (u_array[i])
print "];"

u_prev = u1
dt = 0.02 # time step

u = TrialFunction(V)
v = TestFunction(V)

a = rho*Cp*u*v*dx + dt*k*inner(nabla_grad(u), nabla_grad(v))*dx + dt*rho*Cp*inner(vel, nabla_grad(u))*v*dx
L = rho*Cp*u_prev*v*dx + 2*dt*f*v*dx

A = assemble(a)
b = None

u = Function(V)

T = 1 # total simulation time
t = 0

while t <= T/2:
	b = assemble(L, tensor=b)
	bc.apply(A, b)
	solve(A, u.vector(), b)
	t += dt
	u_prev.assign(u)


u_nodal_values = u.vector()
u_array = u_nodal_values.array()
print "fenics_gT2=["
for i in range(len(u_array)):
	print "%g" % (u_array[i])
print "];"


while t <= T:
	b = assemble(L, tensor=b)
	bc.apply(A, b)
	solve(A, u.vector(), b)
	t += dt
	u_prev.assign(u)


u_nodal_values = u.vector()
u_array = u_nodal_values.array()
print "fenics_gT3=["
for i in range(len(u_array)):
	print "%g" % (u_array[i])
print "];"

u = TrialFunction(V)
v = TestFunction(V)

a2 = k*inner(nabla_grad(u), nabla_grad(v))*dx + rho*Cp*inner(vel, nabla_grad(u))*v*dx
L2 = Constant(0.0)*v*dx

A2, b2 = assemble_system(a2, L2, bc)
Potp=100
delta2 = PointSource(V, Point(input_x,input_y,input_z), Potp)
delta2.apply(b2)

u2 = Function(V)
solve(A2, u2.vector(), b2)

u_nodal_values = u2.vector()
u_array = u_nodal_values.array()
print "fenics_pT=["
for i in range(len(u_array)):
	print "%g" % (u_array[i])
print "];"

u_prev = u2

u = TrialFunction(V)
v = TestFunction(V)

a = rho*Cp*u*v*dx + dt*k*inner(nabla_grad(u), nabla_grad(v))*dx + dt*rho*Cp*inner(vel, nabla_grad(u))*v*dx
L = rho*Cp*u_prev*v*dx
delta = PointSource(V, Point(input_x,input_y,input_z), 2*dt*Potp)

A = assemble(a)
b = None

u = Function(V)
t = 0

while t <= T/2:
	b = assemble(L, tensor=b)
	bc.apply(A, b)
	delta.apply(b)
	solve(A, u.vector(), b)
	t += dt
	u_prev.assign(u)


u_nodal_values = u.vector()
u_array = u_nodal_values.array()
print "fenics_pT2=["
for i in range(len(u_array)):
	print "%g" % (u_array[i])
print "];"

while t <= T:
	b = assemble(L, tensor=b)
	bc.apply(A, b)
	delta.apply(b)
	solve(A, u.vector(), b)
	t += dt
	u_prev.assign(u)


u_nodal_values = u.vector()
u_array = u_nodal_values.array()
print "fenics_pT3=["
for i in range(len(u_array)):
	print "%g" % (u_array[i])
print "];"


exit(0)
