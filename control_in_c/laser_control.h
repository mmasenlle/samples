
#ifndef _LASER_CONTROL_H_
#define _LASER_CONTROL_H_

void laser_control_init();
double laser_control_step(double setpoint, double value);

#endif
