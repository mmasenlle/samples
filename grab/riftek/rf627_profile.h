#pragma once

#ifdef AS_LIBRARY
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

EXPORT void start_grabbing();
EXPORT void stop_grabbing();
EXPORT void stop_scanner();
EXPORT int init_scanner(int fps, bool plot_on);
EXPORT int get_profile(float *xz);
