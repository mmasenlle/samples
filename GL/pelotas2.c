
#include <sys/time.h>
#include <stdlib.h>
#include <stdio.h>
//#include <math.h>
#include <GL/gl.h>
#include <GL/glu.h>
#include <GL/glut.h>


static float color[4][3] = { 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0 };
static int axis = 0, border = 0, rot = 0;
static double zoom = 2.5, g = -9.81;

#define BALL_R .05
#define NBALLS 4
static double x[NBALLS], y[NBALLS], z[NBALLS]; //m [-1,1]
static double x0[NBALLS], y0[NBALLS], z0[NBALLS]; //m [-1,1]
static double dx0[NBALLS], dy0[NBALLS], dz0[NBALLS]; //m/s
static double t[NBALLS]; //s
#define VMAX 25.0
#define T 10000 //us
static struct timeval last = { 0 }, tvt = { 0, T };


void init(void) 
{
	int i;
	gettimeofday(&last, NULL);
	srand((last.tv_sec & 0x0ff) + (last.tv_usec << 8));
#if 0
	for(i = 0; i < NBALLS; i++)
	{
		t[i] = 0.0;
		x[i] = x0[i] = -1;
		y[i] = y0[i] = -1;
		z[i] = z0[i] = .0;
		dx0[i] = .8;
		dy0[i] = .0;
		dz0[i] = .0;
	}
	x[1] = x0[1] = 1; dx0[1] = -.8;
	z[1] = z0[1] = .05; //dz0[1] = .5;
	
#else
	for(i = 0; i < NBALLS; i++)
	{
		t[i] = 0.0;
		x[i] = x0[i] = ((((double)random() / RAND_MAX) * 2.0) - 1.0);
		y[i] = y0[i] = ((((double)random() / RAND_MAX) * 2.0) - 1.0);
		z[i] = z0[i] = ((((double)random() / RAND_MAX) * 2.0) - 1.0);
		dx0[i] = ((((double)random() / RAND_MAX) * 20.0) - VMAX);
		dy0[i] = ((((double)random() / RAND_MAX) * 20.0) - VMAX);
		dz0[i] = ((((double)random() / RAND_MAX) * 20.0) - VMAX);
	}
#endif
	glClearColor (0.0, 0.0, 0.0, 0.0);
	glShadeModel (GL_FLAT);
}

static double EV;
void dump_state()
{
	int i;
	printf("\n CURRENT STATE\n");
	printf("---------------\n");
	printf("axis: %d, border: %d, rot: %d, zoom: %f, g: %f, EV: %f\n", axis, border, rot, zoom, g, EV);
	for(i = 0; i < NBALLS; i++)
	{
		printf("ball %d) t: %f\n  x: %f, y: %f, z: %f\n  x0: %f, y0: %f, z0: %f\n  dx0: %f, dy0: %f, dz0: %f\n",
		i, t[i], x[i], y[i], z[i], x0[i], y0[i], z0[i], dx0[i], dy0[i], dz0[i]);
	}
	printf("\n");
}

void display(void)
{
	int i;
	
	glClear(GL_COLOR_BUFFER_BIT);
	glLoadIdentity();

	gluLookAt (zoom, zoom, zoom, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0);
	glRotatef(rot, 0.0, 1.0, 0.0);

	if(axis)
	{
		glColor3f (1.0, 1.0, 1.0);
		glBegin(GL_LINES);
		glVertex3f (-1.1, 0.0, 0.0);
		glVertex3f (1.1, 0.0, 0.0);
		glVertex3f (0.0, -1.1, 0.0);
		glVertex3f (0.0, 1.1, 0.0);
		glVertex3f (0.0, 0.0, -1.1);
		glVertex3f (0.0, 0.0, 1.1);
		glEnd();
	}
	if(border)
	{
		glColor3f (0.7, 0.7, 0.7);
		glutWireCube(2.1);
	}

	for(i = 0; i < NBALLS; i++)
	{
		glPushMatrix();
		glTranslated (x[i], y[i], z[i]);
		glColor3f (color[i][0], color[i][1], color[i][2]);
		glutSolidSphere(BALL_R, 10, 8);
		glPopMatrix();
	}

	glutSwapBuffers();
}

void move()
{
	int i, j;
	double dy[NBALLS], dt, Ev = 0.0;
	double dx1[NBALLS], dy1[NBALLS], dz1[NBALLS];
	struct timeval now, et;
	gettimeofday(&now, NULL);
	timersub(&now, &last, &et);
	if(timercmp(&et, &tvt, <))
	{
		usleep(tvt.tv_usec - et.tv_usec);
		gettimeofday(&now, NULL);
		timersub(&now, &last, &et);
	}
	last.tv_sec = now.tv_sec; last.tv_usec = now.tv_usec;
	dt = (et.tv_sec + (et.tv_usec / 1e6));

	for(i = 0; i < NBALLS; i++)
	{
//continuous dynamic
		dx1[i] = dy1[i] = dz1[i] = 0.0;
		t[i] += dt;
		dy[i] = y[i];
		x[i] = x0[i] + (dx0[i] * t[i]);
		y[i] = y0[i] + (dy0[i] * t[i]) + (.5 * g * t[i] * t[i]);
		z[i] = z0[i] + (dz0[i] * t[i]);
                dy[i] = (y[i] - dy[i]) / dt;
//border collisions	  
		if((x[i] > 1.0 && dx0[i] > 0.0) || (x[i] < -1.0 && dx0[i] < 0.0))
		{
			dx1[i] = -1.0 * dx0[i];
		}
		if((y[i] > 1.0 && dy[i] > 0.0) || (y[i] < -1.0 && dy[i] < 0.0))
		{
			dy1[i] = -1.0 * dy[i];
		}
		if((z[i] > 1.0 && dz0[i] > 0.0) || (z[i] < -1.0 && dz0[i] < 0.0))
		{
			dz1[i] = -1.0 * dz0[i];
		}
//ball collisions
		for(j = 0; j < i; j++)
		{
			double Dx = fabs(x[j] - x[i]), Dy = fabs(y[j] - y[i]), Dz = fabs(z[j] - z[i]);
			if(Dx < (2 * BALL_R) && Dy < (2 * BALL_R) && Dz < (2 * BALL_R))
			{
				if(!(dx0[j] < .0 && dx0[i] > .0 && x[j] < x[i]) && !(dx0[j] > .0 && dx0[i] < .0 && x[j] > x[i]))
				{
					double ry = Dy / (4 * BALL_R);
					double rz = Dz / (4 * BALL_R);
					double rx = 1 - ry - rz;
					
					dx1[j] += (rx * dx0[i]);
					dy1[j] += (ry * dx0[i]);
					dz1[j] += (rz * dx0[i]);
					
					dx1[i] += (rx * dx0[j]);
					dy1[i] += (ry * dx0[j]);
					dz1[i] += (rz * dx0[j]);
printf("--> X %d-%d rx: %f, ry: %f, rz: %f\n", j, i, rx, ry, rz);
printf("- dx1j: %f, dy1j: %f, dz1j: %f, dx1i: %f, dy1i: %f, dz1i: %f\n", dx1[j], dy1[j], dz1[j], dx1[i], dy1[i], dz1[i]);
				}
				if(!(dy[j] < .0 && dy[i] > .0 && y[j] < y[i]) && !(dy[j] > .0 && dy[i] < .0 && y[j] > y[i]))
				{
					double rx = Dx / (4 * BALL_R);
					double rz = Dz / (4 * BALL_R);
					double ry = 1 - rx - rz;
					
					dx1[j] += (rx * dy[i]);
					dy1[j] += (ry * dy[i]);
					dz1[j] += (rz * dy[i]);
					
					dx1[i] += (rx * dy[j]);
					dy1[i] += (ry * dy[j]);
					dz1[i] += (rz * dy[j]);
printf("--> Y %d-%d rx: %f, ry: %f, rz: %f\n", j, i, rx, ry, rz);
printf("- dx1j: %f, dy1j: %f, dz1j: %f, dx1i: %f, dy1i: %f, dz1i: %f\n", dx1[j], dy1[j], dz1[j], dx1[i], dy1[i], dz1[i]);
				}
				if(!(dz0[j] < .0 && dz0[i] > .0 && z[j] < z[i]) && !(dz0[j] > .0 && dz0[i] < .0 && z[j] > z[i]))
				{
					double rx = Dx / (4 * BALL_R);
					double ry = Dy / (4 * BALL_R);
					double rz = 1 - rx - ry;
					
					dx1[j] += (rx * dz0[i]);
					dy1[j] += (ry * dz0[i]);
					dz1[j] += (rz * dz0[i]);
					
					dx1[i] += (rx * dz0[j]);
					dy1[i] += (ry * dz0[j]);
					dz1[i] += (rz * dz0[j]);
printf("--> Z %d-%d rx: %f, ry: %f, rz: %f\n", j, i, rx, ry, rz);
printf("- dx1j: %f, dy1j: %f, dz1j: %f, dx1i: %f, dy1i: %f, dz1i: %f\n", dx1[j], dy1[j], dz1[j], dx1[i], dy1[i], dz1[i]);
				}
			}
		}
	}
	
	for(i = 0; i < NBALLS; i++)
	{
		if(dx1[i] != 0.0 || dy1[i] != 0.0 || dz1[i] != 0.0)
		{
			if(y0[i] < -1.0 && y[i] < y0[i]) y[i] = -1.0;
			t[i] = 0; x0[i] = x[i]; y0[i] = y[i]; z0[i] = z[i];
			if(dx1[i] != 0.0) dx0[i] = dx1[i];
			if(dy1[i] != 0.0) dy0[i] = dy1[i];
			if(dz1[i] != 0.0) dz0[i] = dz1[i];
			
		}
		Ev += (fabs(dx0[i]) + fabs(dy[i]) + fabs(dz0[i]));
	}
EV = Ev;
	glutPostRedisplay();
}

void reshape(int w, int h)
{
	glViewport (0, 0, (GLsizei) w, (GLsizei) h);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	//   glOrtho(-1.08, 1.08, -1.08, 1.08, -1.08, 1.08);
	gluPerspective(60.0, (GLfloat) w/(GLfloat) h, 1.0, 20.0);
	glMatrixMode(GL_MODELVIEW);
}

void print_help()
{
	printf("\n OPTIONS \n");
	printf("---------\n");
	printf(" <s> : start movement\n");
	printf(" <p> : pause movement\n");
	printf(" <a> : toggle axis visualization\n");
	printf(" <b> : toggle borders visualization\n");
	printf(" <r> : rotate image\n");
	printf(" <z> : zoom -\n");
	printf(" <Z> : zoom +\n");
	printf(" <g> : gravity -\n");
	printf(" <G> : gravity +\n");
	printf(" <d> : dump state\n");
	printf(" <h> : print this help\n");
	printf(" <q> : quit\n");
	printf("\n");
}

void keyboard(unsigned char key, int x, int y)
{
	switch (key) {
	case 's': gettimeofday(&last, NULL); glutIdleFunc(move); break;
	case 'p': glutIdleFunc(NULL); break;
	case 'a': axis = 1 - axis; display(); break;
	case 'b': border = 1 - border; display(); break;
	case 'r': rot = (rot + 45) % 360; display(); break;
	case 'z': zoom /= .75; display(); break;
	case 'Z': zoom *= .75; display(); break;
	case 'g': g *= .75; break;
	case 'G': g /= .75; break;
	case 'd': dump_state(); break;
	case 'h': print_help(); break;
	case 27: case 'q':
		exit(0);
	}
}

/* 
*  Request double buffer display mode.
*  Register mouse input callback functions
*/
int main(int argc, char** argv)
{
	glutInit(&argc, argv);
	glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGB);
	glutInitWindowSize (400, 400); 
	glutInitWindowPosition (600, 50);
	glutCreateWindow ("Pelotas 2");
	init ();
	glutKeyboardFunc(keyboard);
	glutDisplayFunc(display); 
	glutReshapeFunc(reshape); 
	glutMainLoop();
	return 0;
}
