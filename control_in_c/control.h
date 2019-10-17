
#ifndef _CONTROL_H_
#define _CONTROL_H_

struct pid_t
{
// constants
	double Kp;
	double Ki;
	double Kd;
	double Ts;
// state
	double Xi;
	double Xd;
};

double pid(double u, struct pid_t *ctrl);

#define MAX_ORDER 8
struct filter_t
{
// coefficients
	double A[MAX_ORDER];
	double B[MAX_ORDER];
// state
	double X[MAX_ORDER];
	int N; // order
};

double filter(double u, struct filter_t *fltr);

#endif //_CONTROL_H_
