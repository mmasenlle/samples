
#include "control.h"

static double ctrl_int(double u, struct pid_t *ctrl)
{
	ctrl->Xi = ctrl->Xi + u * ctrl->Ts;
	return ctrl->Xi;
}

static double ctrl_diff(double u, struct pid_t *ctrl)
{
	double y = (u - ctrl->Xd) / ctrl->Ts;
	ctrl->Xd = u;
	return y;
}


double pid(double u, struct pid_t *ctrl)
{
	return u * ctrl->Kp +
		ctrl_int(u, ctrl) * ctrl->Ki +
		ctrl_diff(u, ctrl) * ctrl->Kd;
}


double filter(double u, struct filter_t *fltr)
{
	int i = 1;

	double y = (fltr->B[0] * u) + fltr->X[0];

	for (; i < fltr->N; i++)
		fltr->X[i - 1] = (fltr->B[i] * u) + fltr->X[i] - (fltr->A[i] * y);
	fltr->X[fltr->N - 1] = (fltr->B[fltr->N] * u) - (fltr->A[fltr->N] * y);

	return y;
}
