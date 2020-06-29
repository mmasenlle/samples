// Tachyon_Test.cpp: define el punto de entrada de la aplicación de consola.
//

#include "stdafx.h"
#include <iostream>
#include <stdio.h>
#include "Tachyon_acq.h"
#include <fcntl.h>
#include <io.h>

using namespace std;

#define DEBUG1 1
#define NPOINTS 4

static int n=1000;
static int target=50;
static float it=100.0;
static float wt=900.0;
static int bsend = 1, v = 0, debug = 0;
static int p[NPOINTS] = { 10, 20, 30, 500 };
static const char *ads = "Temp_ctrl.points";

void check_arg(int argc, char *argv[], int i)
{
	if(i >= argc || !isdigit(argv[i][0])) {
		fprintf(stderr, "Usage: %s [options]\n"
			"-n\tNumber of frames to retrieve (0: inf) (%d)\n"
			"-t\tCalibration target (%d)\n"
			"-i\tIntegration time (%f us)\n"
			"-w\tWait time (%f us)\n"
			"-s\tSend data stdout (%d)\n"
			"-a\tPLC variable (%s)\n"
			"-v\tVerbose (%d)\n"
			"-p1\tPoint 1 (%d)\n"
			"-p2\tPoint 2 (%d)\n"
			"-p3\tPoint 3 (%d)\n"
			"-p4\tPoint 4 (%d)\n\n", argv[0], n, target, it, wt, bsend, ads, v, p[0], p[1], p[2], p[3]);
		exit(-1);
	}
}

extern int ads_init(const char *var_name, void *data_addr, unsigned long len);
extern int ads_write();

//int _tmain(int argc, _TCHAR* argv[])
int main(int argc, char* argv[])
{
	int r, cnt = 0;
	
	char Header[64];
	short Image[1024]; //Tachyon 1024 FPA
	//short Image[6400]; //Tachyon 6400 FPA
	short point_values[NPOINTS];


	for(int i = 1; i < argc; i++)
	{
		if(argv[i][0] == '-')
		{
			if (argv[i][1] == 'a' && i+1 < argc) { ads = argv[++i];	continue; }
			check_arg(argc, argv, ++i);
			switch(argv[i-1][1])
			{
			case 'v': v = atoi(argv[i]); continue;
			case 'n': n = atoi(argv[i]); continue;
			case 't': target = atoi(argv[i]); continue;
			case 'i': it = atof(argv[i]); continue;
			case 'w': wt = atof(argv[i]); continue;
			case 's': bsend = atoi(argv[i]); continue;
			case 'd': debug = atoi(argv[i]); continue;
			case 'p': { int pi = argv[i-1][2] - '0';
						if (1 <= pi && pi <= 4) {
							p[pi-1] = atoi(argv[i]);
							continue;
						}}
			default: check_arg(argc, argv, argc);
			}
		}
	}
	if (v)
		fprintf(stderr, "%s n:%d t:%d i:%f w:%f p1: %d p2: %d p3: %d p4: %d s: %d a: %s\n",
			argv[0], n, target, it, wt, p[0], p[1], p[2], p[3], bsend, ads);

	setmode(fileno(stdout), O_BINARY);

	if (*ads) ads_init(ads, point_values, sizeof(point_values));
	if (debug && *ads) {
		for(int i = 1; i < NPOINTS; i++) point_values[i] = p[i];
		ads_write();
	}

	if ((r=open_camera()) < 1) {
		cerr << "Error opening device " << r << endl;
		exit(-1);
	}
	if ((r=set_integration_time(it))) {
		fprintf(stderr, "set_integration_time(%f)->Error: %d\n", it, r);
	}
	if ((r=start())) {
		fprintf(stderr, "start()->Error: %d\n", r);
	}
	if ((r=set_wait_time(wt))) {
		fprintf(stderr, "set_wait_time(%f)->Error: %d\n", wt, r);
	}
	if ((r=close_shutter())) {
		fprintf(stderr, "close_shutter()->Error: %d\n", r);
	}
	if ((r=calibrate(target, 1))) {
		fprintf(stderr, "calibrate(%d, 1)->Error: %d\n", target, r);
	}

	while (cnt < n || n <= 0) {
		r = read_frame(Header, Image);
		if(r==-116) {
			fprintf(stderr, "read_frame()->Timeout #: %d\n", cnt);
			continue;
		} else if(r < 0) {
			fprintf (stderr, "read_frame()->Error: %d\n", r);
			return r;
		}
		if (*ads) {
			for(int i = 1; i < NPOINTS; i++) point_values[i] = Image[p[i]];
			ads_write();
		}
		if (bsend) fwrite(Image, 1, sizeof(Image), stdout);
		cnt++;

		if (cnt == 1000) {
			if ((r=open_shutter())) {
				fprintf(stderr, "open_shutter()->Error: %d\n", r);
			}
		}
	}

	if ((r=stop())) {
		fprintf(stderr, "stop()->Error: %d\n", r);
	}
	if ((r=close_camera()) < 1) {
		fprintf(stderr, "close_camera()->Error: %d\n", r);
	}

	return 0;
}

