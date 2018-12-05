
import numpy
from dolfin import *
#from scipy.interpolate import griddata

# Create mesh and function space
mesh = Box(0.0, 0.0, 0.0, 0.008, 0.004, 0.001, 32, 16, 4)
V = FunctionSpace(mesh, "CG", 1)

# Sub domain for Dirichlet boundary condition
class DirichletBoundary(SubDomain):
    def inside(self, x, on_boundary):
        return on_boundary and x[0] < DOLFIN_EPS

Cp = Constant(460)
Tm=1000
Teps=50
latent_heat=270000
def cp_eff(u):
	if (u < Tm):
		return Cp
	# elif (u > Tm+Teps):
		# return latent_heat/u
	# else:
		# return latent_heat*(Teps+u-Tm)/(Teps+2)/u
	else:
		#return Cp + (latent_heat/u)
		return Cp + (latent_heat/Tm)

# Define variational problem
u = TrialFunction(V)
v = TestFunction(V)
uk = interpolate(Expression("0.0"), V) # previous (known) u

# Define boundary condition
u0 = Constant(0.0)
bc = DirichletBC(V, u0, DirichletBoundary())

Pot=50
k = Constant(24)
rho = Constant(7925)
#Cp = Constant(460)

vel = Constant((0.002,0,0))

a1 = k*inner(nabla_grad(u), nabla_grad(v))*dx + rho*cp_eff(uk)*inner(vel, nabla_grad(u))*v*dx
L1 = Constant(0)*v*dx

delta = PointSource(V, Point(0.002,0.002,0.0), Pot)

#print list_linear_solver_methods()

# Picard iterations
u = Function(V) # new unknown function
eps = 1.0 # error measure ||u-uk||
tol = -10 #1.0E-5 # tolerance
iter = 0 # iteration counter
maxiter = 25 # max no of iterations allowed
while eps > tol and iter < maxiter:
	iter += 1
	A1 = assemble(a1)
	b1 = assemble(L1)
	bc.apply(A1, b1)
	delta.apply(b1)
	#solve(A1, u.vector(), b1, "gmres")
	solve(A1, u.vector(), b1)
	diff = u.vector().array() - uk.vector().array()
	eps = numpy.linalg.norm(diff, ord=numpy.Inf)
	print "Norm, iter=%d: %g" % (iter, eps)
	uk.assign(u) # update for next iteration

plot(u, interactive=True)
exit(0)
# file = File("temps.pvd")
# file << u1
# exit(0)

u_nodal_values = u.vector()
u_array = u_nodal_values.array()
coor = mesh.coordinates()

print "fenicsX=["
for i in range(len(u_array)):
	print "%g, %g, %g" % (coor[i][0], coor[i][1], coor[i][2])
print "];"
print "fenicsT=["
for i in range(len(u_array)):
	print "%g" % (u_array[i])
print "];"

exit(0)
