#include <rf62Xsdk.h>
#include <rf62Xtypes.h>
#include <string>
#include <iostream>
#include <chrono>
#include <fstream>
#include <list>
#include <thread>
#include <mutex>
#include <condition_variable>

using namespace SDK::SCANNERS::RF62X;

static rf627old *scanner = nullptr;

//set PYTHONHOME=C:\ProgramData\Anaconda3
//set QT_QPA_PLATFORM_PLUGIN_PATH=%PYTHONHOME%\Library\plugins\platforms
#define MATPLOTLIB
#ifdef MATPLOTLIB
#include "matplotlibcpp.h"
namespace plt = matplotlibcpp;
#endif

std::mutex mtx;
std::condition_variable cond;
std::list<std::shared_ptr<profile2D_t>> profiles;
static volatile bool keep_running = true;
static volatile bool keep_grabbing = true;
std::thread grabber, storer;

void start_grabbing()
{
	std::lock_guard<std::mutex> guard(mtx);
	keep_grabbing = true;
	cond.notify_all();
}
void stop_grabbing()
{
	std::lock_guard<std::mutex> guard(mtx);
	keep_grabbing = false;
	cond.notify_all();
}

void grab_profiles()
{
	long cnt = 0;
	double min = 10000.0, max = -1., sum = .0;
	while (keep_running)
	{
		{ std::unique_lock<std::mutex> lk(mtx);
		if (!keep_grabbing) {
			cond.wait(lk);
			continue;
		}}
		// Get profile from scanner's data stream by Service Protocol.
		auto start = std::chrono::steady_clock::now();
		profile2D_t* profile = scanner->get_profile2D();
		auto finish = std::chrono::steady_clock::now();
		double elapsed_milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(finish - start).count();
		sum += elapsed_milliseconds;
		if (min > elapsed_milliseconds) min = elapsed_milliseconds;
		if (max < elapsed_milliseconds) max = elapsed_milliseconds;
		if (profile != nullptr)
		{
			std::lock_guard<std::mutex> guard(mtx);
			profiles.push_back(std::shared_ptr<profile2D_t>(profile));
			cond.notify_all();
			cnt++;
		}
		else
		{
			std::cout << "Profile was not received!" << std::endl;
		}
	}

	std::cout << "Count: " << cnt << "\nMin: " << min << "\nMax: " << max << "\nSum: " << sum << " ms" << std::endl;

	// Disconnect from scanner.
	scanner->disconnect();

	keep_running = false;
	cond.notify_one();
}

void stop_scanner()
{
	keep_running = false;
	cond.notify_one();
	grabber.join();
	storer.join();
	sdk_cleanup();
}


int init_scanner()
{
	sdk_init();

	std::vector<rf627old*> list;
	// Search for RF627old devices over network
	list = rf627old::search(PROTOCOLS::SERVICE);

	if (!list.empty()) {
		scanner = list.front();

		rf627old::hello_info info = scanner->get_info();

		// Print information about the scanner to which the profile belongs.
		std::cout << "Device information: " << std::endl;
		std::cout << "* Name\t: " << info.device_name() << std::endl;
		std::cout << "* Serial\t: " << info.serial_number() << std::endl;
		std::cout << "* IP Addr\t: " << info.ip_address() << std::endl;

		scanner->connect();

		// read params from RF627 device by Service Protocol.
		if (true) {
			scanner->read_params();/*
			param_t* fps_param = scanner->get_param(PARAM_NAME_KEY::USER_SENSOR_FRAMERATE); // casca en release
			if (fps_param->type == param_value_types[(int)PARAM_VALUE_TYPE::UINT_PARAM_TYPE])
			{
				fps = (double)fps_param->get_value<value_uint32>();
				std::cout << "fps: " << fps << std::endl;
			}
			else {
				std::cerr << "What!!!!! fps_param_type != uint32 ????" << std::endl;
			}*/
			param_t* laser_enabled = scanner->get_param(PARAM_NAME_KEY::USER_LASER_ENABLED);
			if (laser_enabled->type == param_value_types[(int)PARAM_VALUE_TYPE::UINT_PARAM_TYPE])
			{
				if (!laser_enabled->get_value<value_uint32>()) {
					std::cout << "Setting laser on..." << std::endl;
					laser_enabled->set_value<value_uint32>(true);
					scanner->set_param(laser_enabled);
					scanner->write_params();
				}
			}
			else {
				std::cerr << "What!!!!! laser_enabled_type != uint32 ????" << std::endl;
			}
		}
		grabber = std::thread(grab_profiles);

	}
	else {
		std::cerr << "Scanner not found" << std::endl;
	}
	return list.size();
}

void store_profiles(int fps, bool plot_on)
{
	std::ofstream ofs("profile.csv");
	long tt = 0;
	int tplot = (int)(fps / 10);
#ifdef MATPLOTLIB
	if (plot_on) plt::figure_size(1200, 780);
#endif
	while (keep_running || !profiles.empty())
	{
		std::unique_lock<std::mutex> lk(mtx);
		if (profiles.empty()) cond.wait(lk);
		if (!profiles.empty()) {
			auto profile = profiles.front();
			profiles.pop_front();
			lk.unlock();
			double t = (tt++ / (double)fps);
			ofs << t << ";";
			std::vector<double> x, z;
			for (auto point : profile->points)
			{
				if (plot_on && (tt % tplot == 0) && point.z)
				{
					x.push_back(point.x);
					z.push_back(point.z);
				}
				ofs << point.x << ";" << point.z << ";";
			}
			ofs << std::endl;
#ifdef MATPLOTLIB
			if (!x.empty())
			{
				std::string title = "Profile (t=" + std::to_string(t).substr(0, 4) + "s)";
				plt::clf();
				plt::plot(x, z);
				plt::xlim(-25, 25);
				plt::ylim(20, 50);
				plt::grid(true);
				plt::title(title);
				plt::pause(0.01);
			}
#endif
		}
	}

	std::cout << tt << " profiles saved in CSV" << std::endl;
	//std::cout << "Press ENTER to exit" << std::endl;
	//getchar();
}

int main(int argc, char *argv[])
{
	int cnt = 2;
	if (argc > 1) cnt = atoi(argv[1]);
	bool plot_on = true;
	if (argc > 2) plot_on = atoi(argv[2]);
	int fps = 100;
	if (argc > 3) fps = atoi(argv[3]);

	if (cnt < 1 || fps < 1)
	{
		std::cerr << "Usage: " << argv[0] << " <time> <plot on 0|1> <fps>" << std::endl;
	}

	if (init_scanner())
	{
		storer = std::thread(store_profiles, fps, plot_on);
		std::cout << "Press ENTER to start recording profile" << std::endl;
		getchar();
		start_grabbing();
		_sleep(cnt * 1000);
		stop_grabbing();
		//_sleep(1000);
		//start_grabbing();
		//_sleep(cnt * 1000);
		//stop_grabbing();

		stop_scanner();

		std::cout << "Press ENTER to finish" << std::endl;
		getchar();
	}
}
