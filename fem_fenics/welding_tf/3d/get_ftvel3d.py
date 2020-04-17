from sympy import *

init_printing(use_unicode=True)

s,x,y,z = symbols('s x y z', real=True)
a,b,q,v,K = symbols('a b q v K', real=True, positive=True)

T_0xyz = q*exp(v*(x-sqrt(x**2+y**2+z**2))/(2*a))/(2*pi*a*sqrt(x**2+y**2+z**2))
dT_0xyz = simplify(diff(T_0xyz,v))
fgood = lambdify((a,q,v,x,y,z), dT_0xyz)
# ftest(6.6e-06,1000,.002,.3,.2,.1)

values = ((6.6e-06,1000,.002,.3,.2,.1),(6.6e-06,3000,.002,.3,.2,.1),(6.6e-06,1000,.003,.3,.2,.1),(6.6e-06,1000,.002,.3,.0,.1),(6.6e-06,1000,.003,.2,.0,.0))
def check(ftest):
    res = 0
    for v in values:
        res += (ftest(*v)-fgood(*v))**2
    return res


# test 8
R = sqrt(x**2+y**2+z**2)
D = sqrt(4*a*s + v**2)
ft_vel8 = q*exp(v*x/(2*a))/(4*s*pi*a*a*R)*(exp(-R*D/(2*a))/(s*(R-x) + 1)-exp(-R*D/(2*a)))
ft_vel8 = q*v*(R-x)*exp(v*x/(2*a))/(4*s*pi*a*a*R*R)*(exp(-R*D/(2*a))-exp(-R*v/(2*a)))
ft_vel8 = q*v*v*exp(v*x/(2*a))/(4*s*pi*a*a*R)*(exp(-R*D/(2*a))/sqrt(-2*s*x*v + v**2)-exp(-R*v/(2*a))/v)
nft_vel8 = exp(-R*D/(2*a))/(s*x + 1)-exp(-R*D/(2*a))
simplify(nft_vel8.subs(s,0))
dnft_vel8 = simplify(diff(nft_vel8,s))
dnft_vel8.subs(s,0)

df=diff(exp(-R*D/(2*a))/(s*x + 1)-exp(-R*v/(2*a)),s)
df.subs(s,0)
simplify(diff(exp(-R*D/(2*a)),s))
simplify(diff(1/(sqrt(2*s*x + 1)),s))

Tv0xyz8 = simplify(limit(ft_vel8, s, 0))
ff_ = simplify(Tv0xyz8 - dT_0xyz)
Tv0xyz8.equals(dT_0xyz)


# test 9
R = sqrt(x**2+y**2+z**2)
D = sqrt(4*a*s + v**2)
ft_vel9 = q*v/(4*s*pi*a*a*R)*(exp((x-R)*D/(2*a))-exp((x-R)*v/(2*a))-exp(-x*D/(2*a))+exp(-v*x/(2*a)))
nft_vel9 = exp((x-R)*D/(2*a))-exp((x-R)*v/(2*a))-exp(-x*D/(2*a))+exp(-v*x/(2*a))
simplify(nft_vel9.subs(s,0))
dnft_vel9 = simplify(diff(nft_vel9,s))
dnft_vel9.subs(s,0)

Tv0xyz9 = simplify(limit(ft_vel9, s, 0))
ff_ = simplify(Tv0xyz9 - dT_0xyz)
Tv0xyz9.equals(dT_0xyz)


###################### 1d
T_0x = a*exp((v*x - sqrt(x**2*(4*a*b + v**2)))/(2*a))/(K*sqrt(4*a*b+v**2))*q
dT_0x = simplify(diff(T_0x,v))

ftv = q*exp(v*x/(2*a))/(2*s*K)*(exp(-sqrt(x**2*(4*a*b+v**2))/(2*a))-(v*exp(-sqrt(x**2*(4*a*b+v**2))/(2*a)))/(sqrt(4*a*b + v**2))\
                                -exp(-sqrt(x**2*(4*a*s+4*a*b+v**2))/(2*a))+(v*exp(-sqrt(x**2*(4*a*s+4*a*b+v**2))/(2*a)))/(sqrt(4*a*s+4*a*b + v**2)))
ftv0 = simplify(limit(ftv, s, 0))
x = symbols('x', real=True, positive=True)
ftv1 = q*exp(v*x/(2*a))/(2*K)*(exp(-sqrt(x**2*(4*a*b+v**2))/(2*a))-(v*exp(-sqrt(x**2*(4*a*b+v**2))/(2*a)))/(sqrt(4*a*b + v**2))\
                                -exp(-sqrt(x**2*(4*a*s+4*a*b+v**2))/(2*a))+(v*exp(-sqrt(x**2*(4*a*s+4*a*b+v**2))/(2*a)))/(sqrt(4*a*s+4*a*b + v**2)))
ftv1 = -exp(-sqrt(x**2*(4*a*s+4*a*b+v**2))/(2*a))+(v*exp(-sqrt(x**2*(4*a*s+4*a*b+v**2))/(2*a)))/(sqrt(4*a*s+4*a*b + v**2))
dftv1 = diff(ftv1, s)
ftv0 = dftv1.subs(s, 0)
ftv0 = factor(simplify(ftv0))

simplify(dT_0x - ftv0)
dT_0x.equals(ftv0)


nf=(4*a**2*b*x + a*v**2*x - a*v - v*x*sqrt(4*a*b + v**2)/2)*exp(x*(v - sqrt(4*a*b + v**2)/(2*a)))
nf2=nf*2
nf3=nf2*sqrt(4*a*b + v**2)**3
simplify(nf3)

print(factor(ftv0))
n1=-(4*a*b*v*x - 4*a*b*x*sqrt(4*a*b + v**2) + 2*a*v*sqrt(4*a*b + v**2) + v**3*x - v**2*x*sqrt(4*a*b + v**2))
print(dT_0x)
# n2=8*a**2*b*x + 2*a*v**2*x - 2*a*v - v*x*sqrt(4*a*b + v**2)
n2=4*a*b*x - 2*a*v + v**2*x - v*x*sqrt(4*a*b + v**2)
n3=n2*sqrt(4*a*b + v**2)
simplify(n3)
factor(n3)
print(expand(n3))


simplify(n1-n3)


-4*a*b*v*x + 4*a*b*x*sqrt(4*a*b + v**2) - 2*a*v*sqrt(4*a*b + v**2) - v**3*x + v**2*x*sqrt(4*a*b + v**2)
-4*a*b*v*x + 4*a*b*x*sqrt(4*a*b + v**2) - 2*a*v*sqrt(4*a*b + v**2) - v**3*x + v**2*x*sqrt(4*a*b + v**2)