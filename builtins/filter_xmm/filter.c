
#include <stdio.h>
#include "tiempos.h"

extern void filter_n4k4(short *x, double *z);

int main(int argc, char *argv[])
{
	double zi[4] = { 0.0 };
	short x[2048];
	for(;;)
	{
__tiempos_begin(filter);
		filter_n4k4(x, zi);
__tiempos_end(filter, 0, 25);
		usleep(50000);
	}
}


