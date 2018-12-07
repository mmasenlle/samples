

static const double a[] = { 1.00000, -1.96843, 1.73586, -0.72447, 0.12039 };
static const double b[] = { 0.010209, 0.040838, 0.061257, 0.040838, 0.010209 };

void filter_n4k4(short *x, double *z)
{
	int i = 0;
	for(i = 0; i < 2048; i++)
	{
		double y = b[0]*x[i] + z[0];
		z[0] = b[1]*x[i] + z[1] - a[1]*y;
		z[1] = b[2]*x[i] + z[2] - a[2]*y;
		z[2] = b[3]*x[i] + z[3] - a[3]*y;
		z[3] = b[4]*x[i] - a[4]*y;		
		x[i] = y;
	}
}

