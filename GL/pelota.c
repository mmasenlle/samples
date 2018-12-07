
#include <sys/time.h>
#include <GL/gl.h>
#include <GL/glu.h>
#include <GL/glut.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

static float y = 0.0;

void init(void) 
{
   glClearColor (0.0, 0.0, 0.0, 0.0);
   glShadeModel (GL_FLAT);
}

void display(void)
{
   glClear(GL_COLOR_BUFFER_BIT);
   glPushMatrix();
   glTranslatef (0.5, y, 0.0);
   glColor3f (0.8, 1.0, 0.0);
   glutSolidSphere(0.05, 10, 8);
   glPopMatrix();
   glutSwapBuffers();
}

#define Vims 4.5 // m/s
#define T 10000 //us
static struct timeval last = { 0 }, tvt = { 0, T };
#define resk .05
static int resistance = 0, elastic = 1;

void rt_bounce(void)
{
  static double dy = (Vims * T / 1e6);
  struct timeval now, et;
  gettimeofday(&now, NULL);
  timersub(&now, &last, &et);
  if(timercmp(&et, &tvt, <))
  {
    usleep(tvt.tv_usec - et.tv_usec);
    gettimeofday(&now, NULL);
    timersub(&now, &last, &et);
  }

  y += dy;
  if(y < .0) dy *= (elastic ? -1.0 : -0.985);
  else dy += ((-9.81 * (et.tv_sec + (et.tv_usec / 1e6))) * T / 1e6);
  if(resistance) dy -= (dy * dy * (dy > 0.0 ? resk : -resk));
  last.tv_sec = now.tv_sec; last.tv_usec = now.tv_usec;

  glutPostRedisplay();
}

void exact_bounce(void)
{
  static double t = 0.0; //s
  static double v0 = Vims;
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

  t += (et.tv_sec + (et.tv_usec / 1e6));
  if(y < 0.0) { t = 0.0; if(!elastic) v0 *= .95; }
  y = v0 * t + (.5 * -9.81 * t * t);

  glutPostRedisplay();
}

void spinDisplay(void)
{
#define Vis .014
#define a .0001
  static float dy = Vis;
  usleep(15000);
  y += dy;
  dy -= a;
  if(y < Vis) dy = Vis;

  glutPostRedisplay();
}

void reshape(int w, int h)
{
   glViewport (0, 0, (GLsizei) w, (GLsizei) h);
   glMatrixMode(GL_PROJECTION);
   glLoadIdentity();
   glOrtho(0.0, 1.0, -0.05, 1.1, 0.0, 1.0);
   glMatrixMode(GL_MODELVIEW);
   glLoadIdentity();
}
/*
void mouse(int button, int state, int x, int y) 
{
   switch (button) {
      case GLUT_LEFT_BUTTON:
         if (state == GLUT_DOWN)
            glutIdleFunc(spinDisplay);
         break;
      case GLUT_MIDDLE_BUTTON:
         if (state == GLUT_DOWN)
            glutIdleFunc(NULL);
         break;
      default:
         break;
   }
}
*/

void keyboard(unsigned char key, int x, int y)
{
  switch (key) {
    case 's': gettimeofday(&last, NULL); glutIdleFunc(exact_bounce); break;
    case 'p': glutIdleFunc(NULL); break;
    case 'r': resistance = 1; break;
    case 'i': elastic = 0; break;
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
   glutInitWindowSize (250, 250); 
   glutInitWindowPosition (100, 100);
   glutCreateWindow ("Pelota que bota");
   init ();
   glutKeyboardFunc(keyboard);
   glutDisplayFunc(display); 
   glutReshapeFunc(reshape); 
//   glutMouseFunc(mouse);
   glutMainLoop();
   return 0;
}
