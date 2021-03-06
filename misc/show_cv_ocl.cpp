// prueba_ocv2.cpp: define el punto de entrada de la aplicación de consola.
//

#include "stdafx.h"
#include <iostream>
#include <opencv2/core/ocl.hpp>
//#include <opencv2/gpu/gpu.hpp>


int main()
{

	//cv::gpu::GpuMat dst, src;

	std::cout << ("hola") << std::endl;
	if (!cv::ocl::haveOpenCL()) {
		std::cout << ("OpenCL is not avaiable...") << std::endl;
//		return 1;
	} else {
		std::cout << ("cv::ocl::Context:") << std::endl;
		cv::ocl::Context context;
		if (!context.create(cv::ocl::Device::TYPE_GPU)) {
			std::cout << ("cv::ocl::Context::create()-> Failed creating the context...") << std::endl;
			return 1;
		}

		std::cout << (std::to_string(context.ndevices()) + " GPU devices are detected.") << std::endl;
		for (int i = 0; i < context.ndevices(); i++) {
			cv::ocl::Device device = context.device(i);
			std::cout << "Device " << i << ":" << std::endl;
			std::cout << ("name             : " + (std::string)device.name()) << std::endl;
			std::cout << ("available        : " + std::to_string(device.available())) << std::endl;
			std::cout << ("imageSupport     : " + std::to_string(device.imageSupport())) << std::endl;
			std::cout << ("OpenCL_C_Version : " + (std::string)device.OpenCL_C_Version()) << std::endl;
			std::cout << ("type             : " + std::to_string(device.type())) << std::endl << std::endl;
		}
		std::cout << ("cv::ocl::PlatformInfo:") << std::endl;
	//OpenCL: Platform Info
	std::vector<cv::ocl::PlatformInfo> platforms;
	cv::ocl::getPlatfomsInfo(platforms);

	//OpenCL Platforms
	for (size_t i = 0; i < platforms.size(); i++) {
		//Access to Platform
		const cv::ocl::PlatformInfo* platform = &platforms[i];
		//Platform Name
		std::cout << ("Platform Name: " + (std::string)platform->name()) << std::endl;
		//Access Device within Platform
		cv::ocl::Device current_device;
		for (int j = 0; j < platform->deviceNumber(); j++) {
			//Access Device
			platform->getDevice(current_device, j);
			std::cout << "Device " << j << ":" << std::endl;
			//Device Type
			std::cout << ("name             : " + (std::string)current_device.name()) << std::endl;
			std::cout << ("available        : " + std::to_string(current_device.available())) << std::endl;
			std::cout << ("imageSupport     : " + std::to_string(current_device.imageSupport())) << std::endl;
			std::cout << ("OpenCL_C_Version : " + (std::string)current_device.OpenCL_C_Version()) << std::endl;
			std::cout << ("type             : " + std::to_string(current_device.type())) << std::endl << std::endl;
		}
	}
	}
	// Select the first device
//	cv::ocl::Device(context.device(0));
//	cv::ocl::setUseOpenCL(true);


	getchar();
	std::cout << std::endl << "************* cv::getBuildInformation():" << std::endl << cv::getBuildInformation() << std::endl;


	getchar();
    return 0;
}

