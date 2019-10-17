
#include "control.h"

static const int Ts = 100/4; // ms
static int cnt;

static struct filter_t flt, gc;

void laser_control_init()
{
// low pass filter butter(2,0.005)
	flt.A[0] = 1.0; flt.A[1] = -1.977786483776764; flt.A[2] = 0.978030508491796;
	flt.B[0] = 0.000061006178758066; flt.B[1] = 0.000122012357516132; flt.B[2] = 0.000061006178758066;
	flt.X[0] = flt.X[1] = 0.0;
	flt.N = 2;
// pi controller Kp=0.2 Ki=0.02 Kd=0
	gc.A[0] = 1.0; gc.A[1] = -1.0;
	gc.B[0] = 0.2; gc.B[1] = -0.198;
	gc.X[0] = 0.0;
	gc.N = 1;

	cnt = 0;
}

static const double max_power = 2000.0; // mV
static const double min_power = 0.0; // mV
static inline double saturate(double x) {
	return ((x > max_power) ? max_power : ((x < min_power) ? min_power : x));
}
static const double Kff = 0.3; // feedforward gain
static double power = -1.0; // initialize it in the first cycle

double laser_control_step(double setpoint, double value)
{
	if (++cnt >= Ts) {
		cnt = 0;
		power = saturate(filter(filter(setpoint - value, &flt), &gc) + (setpoint * Kff));
	}
	else if (power < 0.0) {
		power = saturate(setpoint * Kff);
	}

	return power;
}