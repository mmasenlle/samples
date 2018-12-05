
from dolfin import *

# Create mesh and function space
mesh = Interval(3000,0,0.5)
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

Pot=1e6
k = Constant(24)
rho = Constant(7925)
Cp = Constant(460)

h = Constant(25)
Tinf = Constant(0)
P = Constant(1)

vel = Constant(0.002)

a1 = k*inner(nabla_grad(u), nabla_grad(v))*dx + rho*Cp*inner(vel, nabla_grad(u))*v*dx + P*h*inner(u,v)*dx
L1 = Constant(0)*v*dx + P*h*Tinf*v*dx

A1, b1 = assemble_system(a1, L1, bc)
delta = PointSource(V, Point(0.25,), Pot)
delta.apply(b1)

#u1 = Function(V)
u1 = Function(V)
solve(A1, u1.vector(), b1)
print "max: ", max(u1.vector()),"(K), T(x=0.5): ", u1.vector()[-1] # 137.15
plot(u1)

# plot(u1, interactive=True)
# u_nodal_values = u1.vector()
# u_array = u_nodal_values.array()
# coor = mesh.coordinates()
##for i in range(len(u_array)):
# i = 0
# while i <= len(u_array):
# 	print "u(%8g) = %g" % (coor[i][0], u_array[i])
# 	i += 100

# exit(0)

# Algo va mal en el transitorio, con dt = 1 funciona
u_prev = u1 #interpolate(u0, V)
# u_prev = interpolate(u0, V)
dt = 0.05 # time step

u = TrialFunction(V)
v = TestFunction(V)

a = rho*Cp*u*v*dx + dt*k*inner(nabla_grad(u), nabla_grad(v))*dx + dt*rho*Cp*inner(vel, nabla_grad(u))*v*dx + dt*P*h*u*v*dx
L = rho*Cp*u_prev*v*dx + dt*P*h*Tinf*v*dx

delta = PointSource(V, Point(0.25,), dt*Pot)

A = assemble(a)
b = None

u = Function(V)

T = 30 # total simulation time
t = 0

while t <= T:
	b = assemble(L, tensor=b)
	bc.apply(A, b)
	delta.apply(b)
	solve(A, u.vector(), b)
	t += dt
	u_prev.assign(u)


# Save solution to file
# file = File("temp.pvd")
# file << u

print "max: ", max(u.vector()),"(K), T(x=0.5): ", u.vector()[-1] # 137.15
# Plot solution
plot(u, interactive=True)
