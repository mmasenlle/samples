
#include <iostream>
#include <array>
#include <vector>

extern "C" {
#include "control.h"
#include "laser_control.h"
}


int main(int argc, char *argv[])
{
	std::cout << "% test controller" << std::endl;

	double setpoint = 4000.0;


	if (1) {
		// plant in z transform configuration
		struct filter_t plant; memset(&plant, 0, sizeof(plant));
		//plant = { {1,-1.903837917869335,0.903933032885864},{0,0.385647828689287,-0.384791793540521}, {0,0}, 2 }; // 0.1 ms
		plant = { { 1, -1.995967990143981, 0.995968149821214},{0, 0.016168038624087, -0.016166601528993}, {0,0}, 2 }; // 0.004 ms

		laser_control_init();

		std::cout << "laser_ctrl_resp = [" << std::endl;
		double value = 0;
		for (int i = 0; i < 2000 * 25; i++) {
			double power = laser_control_step(setpoint, value);
			//if (i%25==24) 
				value = filter(power, &plant);
			std::cout << i * 0.004 << "," << power << "," << value << std::endl;
		}
		std::cout << "];" << std::endl;
	}
}