from sympy import *

init_printing(use_unicode=True)

s,x,y,z = symbols('s x y z', real=True)
a,b,q,v,K = symbols('a b q v K', real=True, positive=True)

T_0xy = exp(v*x/(2*a))/(2*pi*K)*besselk(0,(1/(2*a)*sqrt((x**2+y**2)*(4*a*b+v**2))))*q
dT_0xy = simplify(diff(T_0xy,v))
latex(dT_0xy)
print(dT_0xy)


# test 1
R = sqrt(x**2+y**2)
Ds = sqrt(4*a*s + 4*a*b + v**2)
D = sqrt(4*a*b + v**2)
ft_vel1 = q*exp(v*x/(2*a))/(4*pi*K*a*s)*(v*besselk(0,R*Ds/(2*a)) - v*besselk(0,R*D/(2*a)) + s*x*besselk(0,R*D/(2*a)))
ft_vel1 = q*exp(v*x/(2*a))/(4*pi*K*a*s)*(D*v*besselk(0,R*Ds/(2*a))/Ds - D*v*besselk(0,R*D/(2*a))/Ds + 1/(2*a)*x*D*D*besselk(0,R*D/(2*a)) - 1/(2*a)*x*D*D*D*besselk(0,R*D/(2*a))/Ds)
nft_vel1 = D*v*besselk(0,R*Ds/(2*a)) - Ds*v*besselk(0,R*D/(2*a))
nft_vel1 = D*D*v*besselk(0,R*Ds/(2*a)) - D*D*v*besselk(0,R*D/(2*a)) + Ds/(2*a)*x*D*D*D*besselk(0,R*D/(2*a)) - D/(2*a)*x*D*D*D*besselk(0,R*D/(2*a))
dft_vel1 = s*Ds*D
ft_vel_1 = simplify(q*exp(v*x/(2*a))/(4*pi*K*a)*nft_vel1/dft_vel1)

simplify(ft_vel_1 - ft_vel1)


# dft_vel1 = s
simplify(nft_vel1.subs(s,0))
simplify(dft_vel1.subs(s,0))
dnft_vel1 = simplify(diff(nft_vel1,s))
n1=dnft_vel1.subs(s,0)
ddft_vel1 = simplify(diff(dft_vel1,s))
d1=ddft_vel1.subs(s,0)
n1d1 = simplify(n1/d1)
Tv0xy1 = simplify(q*exp(v*x/(2*a))/(4*pi*K*a)*n1d1)
# Tv0xy1 = simplify(limit(ft_vel1, s, 0))
ff_ = simplify(Tv0xy1 - dT_0xy)
Tv0xy1.equals(dT_0xy)

simplify(limit(besselk(1,R*D/(2*a)), s, 0))
simplify(diff(v*D*D*besselk(0,R*Ds/(2*a))/Ds+v*besselk(0,R*Ds/(2*a))/D,s).subs(s,0))
simplify(diff(besselk(1,R*Ds/(2*a)), s).subs(s,0))
simplify(diff(besselk(0,R*Ds/(2*a)), s).subs(s,0))
simplify(diff(-2*a*besselk(0,R*Ds/(2*a))/R/D*D*D*x/R + besselk(1,R*Ds/(2*a))*D*D*x/R, s).subs(s,0))

simplify(diff(v*besselk(0,R*Ds/(2*a)) - D*x*D*D*besselk(0,R*D/(2*a))/(2*a)/Ds, s).subs(s,0))
simplify(diff(v*besselk(0,R*Ds/(2*a)) + x*D*Ds*besselk(0,R*D/(2*a))/(2*a), s).subs(s,0))
simplify(diff(v*besselk(0,R*Ds/(2*a)) + x*D*Ds*besselk(0,R*D/(2*a))/(4*a) - D*x*D*D*besselk(0,R*D/(2*a))/(4*a)/Ds, s).subs(s,0))

simplify(diff(v*besselk(0,R*Ds/(2*a)) - D*x*D*D*D*besselk(0,R*D/(2*a))/(6*a)/Ds**2 - D*x*D*D*besselk(0,R*D/(2*a))/(6*a)/Ds, s).subs(s,0))
simplify(diff(v*besselk(0,R*Ds/(2*a)) - x*D**5*besselk(0,R*D/(2*a))/(6*a)/Ds**3, s).subs(s,0))
simplify(diff(v*besselk(0,R*Ds/(2*a)) - besselk(0,R*D/(2*a))/(x*s + 1), s).subs(s,0))
simplify(diff(v*besselk(0,R*Ds/(2*a)) - x*besselk(0,R*D/(2*a))/(s + 1), s).subs(s,0))
simplify(diff(v*besselk(0,R*Ds/(2*a)) - x*10000*besselk(0,R*D/(2*a))/(s + 100), s).subs(s,0))
simplify(diff(v*besselk(0,R*Ds/(2*a)) - x*besselk(0,R*D/(2*a))/(s - 1), s).subs(s,0))
simplify(diff(v*besselk(0,R*Ds/(2*a)) - x*(4*a*b + v**2)**2*besselk(0,R*D/(2*a))/(4*a*(4*a*s + 4*a*b + v**2)), s).subs(s,0))
simplify(diff(v*besselk(0,R*Ds/(2*a)) - x*(4*a*b + v**2)/(4*a)*besselk(0,R*D/(2*a))/(4*a*s/(4*a*b + v**2) + 1), s).subs(s,0))
simplify(diff(v*besselk(0,R*Ds/(2*a)) - (4*a*b + v**2)*besselk(0,R*D/(2*a))/(x**2/(4*a*b + v**2)*s + 1), s).subs(s,0))

simplify(diff(v*besselk(0,R*Ds/(2*a)) + x*(4*a*b + v**2)/(4*a)*besselk(0,R*D/(2*a))/(-4*a*s/(4*a*b + v**2) + 1), s).subs(s,0))

simplify(diff(v*besselk(0,R*Ds/(2*a)) - v*besselk(0,R*D/(2*a))/2/(2*x*s/v + 1), s).subs(s,0))












simplify(diff(Ds, s))
simplify(diff(1/Ds, s))


########################3
nft_vel1 = v*besselk(0,R*Ds/(2*a)) - v*besselk(0,R*D/(2*a)) + x*D*D*besselk(0,R*D/(2*a))/(2*a) - D*x*D*D*besselk(0,R*D/(2*a))/(2*a)/Ds
nft_vel1 = v*besselk(0,R*Ds/(2*a)) - v*besselk(0,R*D/(2*a)) + x*D*Ds*besselk(0,R*D/(2*a))/(2*a) - x*D*D*besselk(0,R*D/(2*a))/(2*a)
nft_vel1 = v*besselk(0,R*Ds/(2*a)) - v*besselk(0,R*D/(2*a)) + x*D*Ds*besselk(0,R*D/(2*a))/(4*a) - x*D*D*besselk(0,R*D/(2*a))/(4*a) \
           - D * x * D * D * besselk(0, R * D / (2 * a)) / (4 * a) / Ds + x*D*D*besselk(0,R*D/(2*a))/(4*a)
nft_vel1 = v*besselk(0,R*Ds/(2*a)) - v*besselk(0,R*D/(2*a)) + x*D*D*besselk(0,R*D/(2*a))/(4*a) - D*x*D*D*D*besselk(0,R*D/(2*a))/(4*a)/Ds/Ds
nft_vel1 = v*besselk(0,R*Ds/(2*a)) - v*besselk(0,R*D/(2*a)) + x*D*D*besselk(0,R*D/(2*a))/(3*a) - D*x*D*D*D*besselk(0,R*D/(2*a))/(6*a)/Ds/Ds - D*x*D*D*besselk(0,R*D/(2*a))/(6*a)/Ds
nft_vel1 = v*besselk(0,R*Ds/(2*a)) - v*besselk(0,R*D/(2*a)) + besselk(0,R*D/(2*a)) - besselk(0,R*D/(2*a))/(x*s + 1)
nft_vel1 = v*besselk(0,R*Ds/(2*a)) - v*besselk(0,R*D/(2*a)) + x*besselk(0,R*D/(2*a)) - x*besselk(0,R*D/(2*a))/(s + 1)
nft_vel1 = v*besselk(0,R*Ds/(2*a)) - v*besselk(0,R*D/(2*a)) + x*besselk(0,R*D/(2*a))/100 - x*besselk(0,R*D/(2*a))/(10000*s + 100)
nft_vel1 = v*besselk(0,R*Ds/(2*a)) - v*besselk(0,R*D/(2*a)) + x*D*D*besselk(0,R*D/(2*a))/(4*a) - x*(4*a*b + v**2)/(4*a)*besselk(0,R*D/(2*a))/(4*a*s/(4*a*b + v**2) + 1)
nft_vel1 = v*besselk(0,R*Ds/(2*a)) - v*besselk(0,R*D/(2*a)) + D*D*besselk(0,R*D/(2*a)) - (4*a*b + v**2)*besselk(0,R*D/(2*a))/(x*s/(4*a*b + v**2) + 1)



dft_vel1 = s
simplify(nft_vel1.subs(s,0))
simplify(dft_vel1.subs(s,0))
dnft_vel1 = simplify(diff(nft_vel1,s))
n1=dnft_vel1.subs(s,0)
ddft_vel1 = simplify(diff(dft_vel1,s))
d1=ddft_vel1.subs(s,0)
n1d1 = simplify(n1/d1)
Tv0xy1 = simplify(q*exp(v*x/(2*a))/(4*pi*K*a)*n1d1)
Tv0xy1.equals(dT_0xy)
