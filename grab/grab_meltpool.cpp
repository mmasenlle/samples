
#include <pylon/PylonIncludes.h>
#ifdef PYLON_WIN_BUILD
#include <pylon/PylonGUI.h>
#endif

#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/core/core.hpp"
#include <pylon/PylonImage.h>
#include <pylon/Pixel.h>
#include <pylon/ImageFormatConverter.h>
#include <pylon/gige/BaslerGigEInstantCamera.h>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>


// Number of images to be grabbed.
static const uint32_t c_countOfImagesToGrab = 100;

static int req_fps = 100, thresh = 50;
static int show_img = 0, nthreads = 1;

class MeltpoolCalculer
{
	int id;
	int cnt;
	int d;
	cv::Mat org, gray, bin;
	Pylon::CPylonImage image;
	Pylon::CImageFormatConverter fc;
public:
	MeltpoolCalculer(int _id, int w, int h) {
		id = _id;
		cnt = 0;
		fc.OutputPixelFormat = Pylon::PixelType_RGB8packed;
		org = cv::Mat(w, h, CV_8UC3);
		gray = cv::Mat(w, h, CV_8UC3);
		bin = cv::Mat(w, h, CV_8UC3);
		d = req_fps;
		if (nthreads > 1) d = req_fps / (nthreads - 1);
	};
	int get_mp(Pylon::CGrabResultPtr ptrGrabResult) {
		fc.Convert(image, ptrGrabResult);
		org = cv::Mat(ptrGrabResult->GetHeight(), ptrGrabResult->GetWidth(), CV_8UC3, (uint8_t*)image.GetBuffer());
		cv::cvtColor(org, gray, cv::COLOR_BGR2GRAY);
		cv::threshold(gray, bin, thresh, 1, cv::THRESH_BINARY);
		int meltpool = cv::sum(bin)[0];

		if (id == 1 && show_img) {
			cv::imshow("CV_Image", org);
			cv::waitKey(1);
		}

		if (++cnt % d == 0)
			std::cout << "MeltpoolCalculer(" << id << ") " << cnt << " mp: " << meltpool << std::endl;
		
		return meltpool;
	};
	
};

std::mutex mtx;
std::condition_variable cond;
std::list<Pylon::CGrabResultPtr> images;
std::vector<std::thread> workers;
bool keep_running = true;
int g_cnt = 0;

void worker(int id, int w, int h) {
	MeltpoolCalculer mc(id, w, h);
	while (keep_running) {
		std::unique_lock<std::mutex> lk(mtx);
		if (images.empty()) cond.wait(lk);
		if (!images.empty()) {
			Pylon::CGrabResultPtr gr = images.front();
			images.pop_front();
			g_cnt++;
			lk.unlock();
			mc.get_mp(gr);
		}
	}
}


int main(int argc, char* argv[])
{
	// The exit code of the sample application.
	int exitCode = 0;

	if (argc > 1 && isdigit(argv[1][0])) {
		req_fps = atoi(argv[1]);
	}
	if (argc > 2 && isdigit(argv[2][0])) {
		thresh = atoi(argv[2]);
	}
	if (argc > 3 && isdigit(argv[3][0])) {
		show_img = atoi(argv[3]);
	}
	if (argc > 4 && isdigit(argv[4][0])) {
		nthreads = atoi(argv[4]);
	}
	std::cout << "req_fps: " << req_fps << " / thresh: " << thresh << " / show_img: " << show_img << " / nthreads: " << nthreads << std::endl;

	// Automagically call PylonInitialize and PylonTerminate to ensure
	// the pylon runtime system is initialized during the lifetime of this object.
	Pylon::PylonAutoInitTerm autoInitTerm;


	if (show_img) cv::namedWindow("CV_Image", cv::WINDOW_AUTOSIZE);
	try
	{

		//Pylon::CInstantCamera camera(Pylon::CTlFactory::GetInstance().CreateFirstDevice());
		Pylon::CBaslerGigEInstantCamera camera(Pylon::CTlFactory::GetInstance().CreateFirstDevice());
		//Pylon::CBaslerGigEInstantCamera 
		std::cout << "Using device " << camera.GetDeviceInfo().GetModelName() << std::endl;
		camera.Open();

		camera.TriggerMode.SetValue(Basler_GigECamera::TriggerMode_Off);
		camera.AcquisitionFrameRateEnable = 1;
		camera.AcquisitionFrameRateAbs = req_fps;
		camera.ExposureTimeRaw = 100;

		camera.GevSCPSPacketSize.SetValue(1500);
		camera.GevSCPD.SetValue(0);

		GenApi::CIntegerPtr width(camera.GetNodeMap().GetNode("Width"));
		GenApi::CIntegerPtr height(camera.GetNodeMap().GetNode("Height"));

		MeltpoolCalculer mc(1, width->GetValue(), height->GetValue());

		for (int i = 1; i < nthreads; i++) {
			workers.push_back(std::thread(worker, i, width->GetValue(), height->GetValue()));
		}

		camera.StartGrabbing();


		int i = 0;
		auto t0 = std::chrono::system_clock::now();

		while (camera.IsGrabbing()) {
			Pylon::CGrabResultPtr ptrGrabResult;
			camera.RetrieveResult(500, ptrGrabResult, Pylon::TimeoutHandling_ThrowException);
			if (ptrGrabResult->GrabSucceeded()) {
				
				if (nthreads < 2) {
					double meltpool = mc.get_mp(ptrGrabResult);
				}
				else {
					std::lock_guard<std::mutex> guard(mtx);
					images.push_back(ptrGrabResult);
					cond.notify_one();
				}

				if (++i % req_fps == 0) {
					//i = 0;
					std::chrono::duration<double> secs = std::chrono::system_clock::now() - t0;
					std::cout << "Grabbed/Processed:" << i << "/" << g_cnt << " fps: "
						<< (double(req_fps) / secs.count()) << std::endl;
					t0 = std::chrono::system_clock::now();
				}
			}
		}

	}

	catch (GenICam::GenericException &e)
	{
		// Error handling.
		std::cerr << "An exception occurred." << std::endl
			<< e.GetDescription() << std::endl;
		exitCode = 1;
	}

	keep_running = false;
	cond.notify_all();

	// Comment the following two lines to disable waiting on exit
	std::cerr << std::endl << "Press Enter to exit." << std::endl;
	while (std::cin.get() != '\n');

	return exitCode;
}
