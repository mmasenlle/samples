% print data
clear all
% bode1D_data
bode1D_incfreqs

X=fenics_bode_inc;

t=X(:,1)';
u=X(:,5)'; % figure,plot(t,u)
y1=X(:,2)'; % figure,plot(t,y1)
y2=X(:,4)'; % figure,plot(t,y2)

b=length(t)-2000; % figure,plot(t(b:end),y1(b:end)-y1(1))
dt = t(2)-t(1);

U = fft(u);
Y1 = fft(y1);
Y2 = fft(y2);
H1 = U .* Y1 ./ U.^2; % the H1 transfer function estimate
H2 = U .* Y2 ./ U.^2; % the H1 transfer function estimate
M1 = 20*log10(abs(H1));
Ph1 = angle(H1)*180/pi;
M2 = 20*log10(abs(H2));
Ph2 = angle(H2)*180/pi;

N = length(U);
N2 = floor(N/2);
FreqData = [0:N-1]/(N*dt); % Hz
% figure
% subplot(211); semilogx(FreqData(1:N2)*0.159155,M1(1:N2));
% subplot(212); semilogx(FreqData(1:N2)*0.159155,Ph1(1:N2));

% constantes termicas de un acero
% capacidad calorifica (solido y liquido)
params.cs = 460;    % J/kg/K
params.cl = 460; % J/kg/K
% conductividad (solido y liquido)
params.ks = 24.0; % J/m/s/K
params.kl = 24.0;  % J/m/s/K
% densidad, temperatura fusion y calor especifico
params.rho = 7925; % kg/m^3
params.Tm = 1783; % K
params.L = 0; %270000; % J/kg
% rango de temperatura durante la fusion
params.Teps = 30;
params.h=100000; % coeficiente de conveccion
params.a=0; % coeficiente de radiacion
params.Ta=0; % Temperatura inicial
params.Tinf=0; % Temperatura ambiente
params.lumped=1; % matriz de capacitancias diagonal
params.A=1; %.01; % Area de la seccion de la barra unidimensional
params.P=2*pi*(sqrt(params.A/pi)); % Perimetro de la barra unidimensional
% potencia nominal 
params.Pot_nom = 2e7; % (w)
% velocidad nominal
params.v_nom = .002; % (m/s)
% analítica
v=params.v_nom;
a=params.ks/(params.rho*params.cs);
b=params.P*params.h*a/(params.ks*params.A);
xi=.01;
q=params.Pot_nom/(params.rho*params.cs);
w = logspace(-3,3,300);
s = j*w;
x=xi;
resp_vel2 = params.Pot_nom/params.ks.*(exp((v*x)./(2*a)).*(exp(-(x*(v^2 + 4*a*b).^(1/2))./(2*a))...
    - exp(-(x*(v^2 + 4*a*b + 4*a*s).^(1/2))./(2*a)) - (v*exp(-(x*(v^2 + 4*a*b).^(1/2))./(2*a)))...
    /(v^2 + 4*a*b).^(1/2) + (v*exp(-(x*(v^2 + 4*a*b + 4*a*s).^(1/2))./(2*a)))...
    ./(v^2 + 4*a*b + 4*a*s).^(1/2)))./(2*s);

% ac1=angle(resp_vel2)*180/pi;
% while ac1(1)>0
%     ac1(1) = ac1(1)-360;
% end
% for i=2:length(ac1)
%     while ac1(i)>ac1(i-1)
%         ac1(i) = ac1(i)-360;
%     end
% end

[Mb3,fb3]=bode(frd(resp_vel2, w), w);
[Mb4,fb4]=bode(frd(resp_vel2, w), w);
Mb3=squeeze(Mb3);
Mb4=squeeze(Mb4);
ab3=squeeze(fb3);
ab4=squeeze(fb4);
figure;
subplot(2,1,1),semilogx(w,20*log10(Mb3),FreqData(1:N2)/0.159155,M1(1:N2));
title('T_1(s) / V(s)'); grid; legend('Analytic Model','FEM Model');
subplot(2,1,2),semilogx(w,ab3,FreqData(1:N2)/0.159155,Ph1(1:N2));grid;
%figure,bode(frd(resp_vel2, w), w);

x=.1;
resp_vel22 = params.Pot_nom/params.ks.*(exp((v*x)./(2*a)).*(exp(-(x*(v^2 + 4*a*b).^(1/2))./(2*a))...
    - exp(-(x*(v^2 + 4*a*b + 4*a*s).^(1/2))./(2*a)) - (v*exp(-(x*(v^2 + 4*a*b).^(1/2))./(2*a)))...
    /(v^2 + 4*a*b).^(1/2) + (v*exp(-(x*(v^2 + 4*a*b + 4*a*s).^(1/2))./(2*a)))...
    ./(v^2 + 4*a*b + 4*a*s).^(1/2)))./(2*s);
ac2=angle(resp_vel22)*180/pi;
while ac2(1)>0
    ac2(1) = ac2(1)-360;
end
for i=2:length(ac2)
    while ac2(i)>ac2(i-1)
        ac2(i) = ac2(i)-360;
    end
end

[Mb3,fb3]=bode(frd(resp_vel22, w), w);
[Mb4,fb4]=bode(frd(resp_vel22, w), w);
Mb3=squeeze(Mb3);
Mb4=squeeze(Mb4);
ab3=squeeze(fb3);
ab4=squeeze(fb4);
figure;
subplot(2,1,1),semilogx(w,20*log10(Mb3),FreqData(1:N2)/0.159155,M2(1:N2));
title('T_2(s) / V(s)'); grid; legend('Analytic Model','FEM Model');
subplot(2,1,2),semilogx(w,ab3,FreqData(1:N2)/0.159155,Ph2(1:N2));grid;
%figure,bode(frd(resp_vel2, w), w);


