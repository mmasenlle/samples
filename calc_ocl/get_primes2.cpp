#include <cstdlib>
#include <iostream>
#include <iomanip>
#include <cstring>
#include <cassert>
#include <cmath>

#include <CL/cl.h>

#include <boost/atomic.hpp>
#include <boost/thread/thread.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <fstream>

#ifndef _MSC_VER
static __inline__ unsigned long long __rdtsc(void)
{
    unsigned hi, lo;
    __asm__ __volatile__ ("rdtsc" : "=a"(lo), "=d"(hi));
    return ( (unsigned long long)lo)|( ((unsigned long long)hi)<<32 );
}
#define __int64 long long
#else
#include <intrin.h>
#endif

static unsigned __int64 _start_tics;
static void _micro_tic() {
	_start_tics = __rdtsc();
}
#define TICS_PER_MICRO 1997
static __int64 _micro_toc() {
	return (__rdtsc()-_start_tics)/TICS_PER_MICRO;
}

const int primes[] = {3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,
            79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,
            179,181,191,193,197,199,211,223,227,229,233,239,241,251,257,263,269,271,
            277,281,283,293,307,311,313,317,331,337,347,349,353,359,0};
const int primes1[] = {1,7,11,13,17,19,23,29};
boost::mutex mtx;
unsigned __int64 last_count = 93323264; //100*256*1024;
//boost::atomic_int nprimes(18801595); //(5669463);
unsigned __int64 nprimes = 18801595;
//int nprimes = 5669463;
boost::atomic<bool> stop (false);

#define LAST_FNAME "nprimes.dat"

unsigned __int64 get_count(unsigned __int64 n)
{
    unsigned __int64 r;
    mtx.lock();
    r = last_count;
    last_count += n;
    mtx.unlock();
    return r;
}

void calc(unsigned __int64 from, int n)
{
    unsigned __int64 _start_tics1 = __rdtsc();
    int np = 0;
    for(int i = 0; i < n; i++) {
        int isprime = 1;
        unsigned __int64 primec = ((i+from)/8)*30+primes1[i%8]+360;
        for(int j = 0; primes[j]; j++) {
            if (primec % primes[j] == 0) {
                isprime = 0;
                break;
            }
        }
        if (isprime) {
            int n = sqrt((double)primec) + 1;
            int j = 0;
            int prime = (j/8)*30+primes1[j%8]+360;
            while (prime < n) {
                if (primec % prime == 0) {
                    isprime = 0;
                    break;
                }
                prime = (j/8)*30+primes1[j%8]+360;
                j++;
            }
            if (isprime) np++;
        }
    }
    nprimes += np;
    printf("calc(%x,%llu,%d): %d in %lld\n", boost::this_thread::get_id(), from, n, np, (__rdtsc()-_start_tics)/TICS_PER_MICRO);
}

void thcalc()
{
    int thcount = 128*1024;
    while (!stop) {
        unsigned __int64 base = get_count(thcount);
        calc(base, thcount);
    }
}

int main (int argc, const char** argv)
{
    // All stuff needed for sample is kept in this function body.
    // There is a couple of help macros; so they are also defined
    // directly inside this function and context dependent.

    using namespace std;

    // -----------------------------------------------------------------------
    // 1. Parse command line.

    // Default substring for platform name
    const char* required_platform_subname = "Intel";

    // Sample accepts one optional argument only, see usage information below
    if(argc > 2)
    {
        cerr << "Error: too many command line arguments.\n";
    }

    // Print usage information in case
    if(
        argc > 2 ||     // ... when wrong number of arguments is provided
        argc == 2 && (  // or user asks for help
        strcmp(argv[1], "-h") == 0 ||
        strcmp(argv[1], "--help") == 0
        )
        )
    {
        cout
            << "Usage: " << argv[0] << " [-h | --help | <PLATFORM>]\n\n"
            << "    -h, --help     Show this help message and exit.\n\n"
            << "    <PLATFORM>     Platform name substring to select platform.\n"
            << "                   Case sensitive. Default value is \""
            <<                     required_platform_subname << "\".\n"
            << "                   In case of multiple matches, the first matching\n"
            << "                   platform is selected.\n";

        exit(argc > 2); // return non-zero only if an error occurs
    }

    if(argc == 2)
    {
        // User provided substring for platform name selection:
        required_platform_subname = argv[1];
    }

        {std::ifstream ifs(LAST_FNAME);
    if (ifs) {
        boost::archive::text_iarchive ar(ifs);
        ar & last_count;
        ar & nprimes;
    }}

    printf("Last %llu/%llu , nprimes: %llu\n", last_count, last_count*30/8, nprimes);

    int ind = 0;
    unsigned __int64 *data[2][2];
    int *results[2];
    size_t global[2], local[2];
    global[0] = 80*1024;
    global[1] = 2*1024;
    for (int ti = 0; ti < 2; ti++) {
    data[ti][0] = new unsigned __int64[global[ti]];
    data[ti][1] = new unsigned __int64[global[ti]];
    results[ti] = new int[global[ti]];
//    int *results0 = new int[count];
    unsigned __int64 base = get_count(global[ti]);
    for(int i = 0; i < global[ti]; i++) {
        data[ti][ind][i] = ((i+base)/8)*30+primes1[i%8]+360;
 //       printf("Prime? %d\n", data[i]);
    }
    }
/*    printf("Last prime candidate %d\n", data[count-1]);
    _micro_tic();
    for(int i =0; i < count; i++) {
        results0[i] = 1;
        for(int j = 0; primes[j]; j++) {
            if (data[i] % primes[j] == 0) {
                results0[i] = 0;
                break;
            }
        }
        if (results0[i]) {
            int n = sqrt((double)data[i]) + 1;
            int j = 0;
            int prime = (j/8)*30+primes1[j%8]+360;
            while (prime < n) {
                if (data[i] % prime == 0) {
                    results0[i] = 0;
                    break;
                }
                prime = (j/8)*30+primes1[j%8]+360;
                j++;
            }
//            if (results0[i]) printf("Prime %d\n", data[i]);
        }
    }
    cout << _micro_toc() << "us\n";
*/

    // -----------------------------------------------------------------------
    // 2. Define error handling strategy.

    // The following variable stores return codes for all OpenCL calls.
    // In the code it is used with CAPSBASIC_CHECK_ERRORS macro defined next.
    cl_int err = CL_SUCCESS;

    // Error handling strategy for this sample is fairly simple -- just print
    // a message and terminate the application if something goes wrong.
#define CAPSBASIC_CHECK_ERRORS(ERR)        \
    if(ERR != CL_SUCCESS)                  \
    {                                      \
    cerr                                   \
    << "OpenCL error with code " << ERR    \
    << " happened in file " << __FILE__    \
    << " at line " << __LINE__             \
    << ". Exiting...\n";                   \
    exit(1);                               \
    }


    // -----------------------------------------------------------------------
    // 3. Query for all available OpenCL platforms on the system

    cl_uint num_of_platforms = 0;
    // get total number of available platforms:
    err = clGetPlatformIDs(0, 0, &num_of_platforms);
    CAPSBASIC_CHECK_ERRORS(err);
    cout << "Number of available platforms: " << num_of_platforms << endl;

    cl_platform_id* platforms = new cl_platform_id[num_of_platforms];
    // get IDs for all platforms:
    err = clGetPlatformIDs(num_of_platforms, platforms, 0);
    CAPSBASIC_CHECK_ERRORS(err);


    // -----------------------------------------------------------------------
    // 4. List all platforms and select one.
    // We use platform name to select needed platform.

    cl_uint selected_platform_index = num_of_platforms;

    cout << "Platform names:\n";

    for(cl_uint i = 0; i < num_of_platforms; ++i)
    {
        // Get the length for the i-th platform name
        size_t platform_name_length = 0;
        err = clGetPlatformInfo(
            platforms[i],
            CL_PLATFORM_NAME,
            0,
            0,
            &platform_name_length
            );
        CAPSBASIC_CHECK_ERRORS(err);

        // Get the name itself for the i-th platform
        char* platform_name = new char[platform_name_length];
        err = clGetPlatformInfo(
            platforms[i],
            CL_PLATFORM_NAME,
            platform_name_length,
            platform_name,
            0
            );
        CAPSBASIC_CHECK_ERRORS(err);

        cout << "    [" << i << "] " << platform_name;

        // decide if this i-th platform is what we are looking for
        // we select the first one matched skipping the next one if any
        if(
            strstr(platform_name, required_platform_subname) &&
            selected_platform_index == num_of_platforms // have not selected yet
            )
        {
            cout << " [Selected]";
            selected_platform_index = i;
            // do not stop here, just see all available platforms
        }

        cout << endl;
        delete [] platform_name;
    }

    if(selected_platform_index == num_of_platforms)
    {
        cerr
            << "There is no found platform with name containing \""
            << required_platform_subname << "\" as a substring.\n";
        return 1;
    }

    cl_platform_id platform = platforms[selected_platform_index];


    // -----------------------------------------------------------------------
    // 5. Let us see how many devices of each type are provided for the
    // selected platform.

    // Use the following handy array to
    // store all device types of your interest. The array helps to build simple
    // loop queries in the code below.

    struct
    {
        cl_device_type type;
        const char* name;
        cl_uint count;
    }
    devices[] =
    {
        { CL_DEVICE_TYPE_CPU, "CL_DEVICE_TYPE_CPU", 0 },
        { CL_DEVICE_TYPE_GPU, "CL_DEVICE_TYPE_GPU", 0 },
        { CL_DEVICE_TYPE_ACCELERATOR, "CL_DEVICE_TYPE_ACCELERATOR", 0 }
    };

    const int NUM_OF_DEVICE_TYPES = sizeof(devices)/sizeof(devices[0]);

    cout << "Number of devices available for each type:\n";

    // Now iterate over all device types picked above and
    // initialize num_of_devices
    for(int i = 0; i < NUM_OF_DEVICE_TYPES; ++i)
    {
        err = clGetDeviceIDs(
            platform,
            devices[i].type,
            0,
            0,
            &devices[i].count
            );

        if(CL_DEVICE_NOT_FOUND == err)
        {
            // that's OK to fall here, because not all types of devices, which
            // you query for may be available for a particular system
            devices[i].count = 0;
            err = CL_SUCCESS;
        }

        CAPSBASIC_CHECK_ERRORS(err);

        cout
            << "    " << devices[i].name << ": "
            << devices[i].count << endl;
    }


    // -----------------------------------------------------------------------
    // 6. Now get a piece of useful capabilities information for each device.
    // Group information by device type

    cout << "\n*** Detailed information for each device ***\n";


                    std::string src1[2];
                std::string src0 = "__kernel void square(__global ulong * input, __global uint * output) {\n"
                                    "   const uint primes[] = {3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,"
                                    "       79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,"
                                    "       179,181,191,193,197,199,211,223,227,229,233,239,241,251,257,263,269,271,"
                                    "       277,281,283,293,307,311,313,317,331,337,347,349,353,359,0};"
                                    "   const uint primes1[] = {1,7,11,13,17,19,23,29};\n"
                                    "   size_t i = get_global_id(0);\n"
                                    "   output[i] = 1;\n"
                                    "   for(int j = 0; primes[j]; j++) {\n"
                                    "       if (input[i] % primes[j] == 0) {\n"
                                    "           output[i] = 0;\n"
                                    "           break;\n"
                                    "       }\n"
                                    "   }\n"
                                    "   if (output[i]) {\n";
                          src1[0] = "       int n = sqrt((double)input[i]) + 1;\n";
                          src1[1] = "       int n = sqrt(input[i]) + 1;\n";
                std::string src2  = "       int j = 0;\n"
                                    "       int prime = (j/8)*30+primes1[j%8]+360;\n"
                                    "       while (prime < n) {\n"
                                    "           if (input[i] % prime == 0) {\n"
                                    "               output[i] = 0;\n"
                                    "               break;\n"
                                    "           }\n"
                                    "           prime = (j/8)*30+primes1[j%8]+360;\n"
                                    "           j++;\n"
                                    "       }\n"
                                    "   }\n"
                                    "}\n";

        cl_command_queue queue[2];
        cl_kernel kernel[2];
        cl_mem  input[2];
        cl_mem  output[2];
        cl_device_id* devices_of_type[2];
        int tn = 2;

//    for(int type_index = 0; type_index < NUM_OF_DEVICE_TYPES; ++type_index)
//    for(int type_index = 1; type_index < NUM_OF_DEVICE_TYPES; ++type_index) // ignoring CPU
    for(int type_index = 0; type_index < tn; ++type_index)
    {
        int ti = type_index;
        cl_uint cur_num_of_devices = devices[type_index].count;

        if(cur_num_of_devices == 0)
        {
            // there is no devices of this type; move to the next type
            continue;
        }

        // Retrieve a list of device IDs with type selected by type_index
        devices_of_type[ti] = new cl_device_id[cur_num_of_devices];
        err = clGetDeviceIDs(
            platform,
            devices[type_index].type,
            cur_num_of_devices,
            devices_of_type[ti],
            0
            );
        CAPSBASIC_CHECK_ERRORS(err);



        // Iterate over all devices of the current device type
        for(
            cl_uint device_index = 0;
            device_index < cur_num_of_devices;
        ++device_index
            )
        {
            cout << "\n" << type_index << ") "
                << devices[type_index].name
                << "[" << device_index << "]\n";

            cl_device_id device = devices_of_type[ti][device_index];
//////////////////////////////////////////////////////////////////
            {
                cout << "\nCreating program in " << devices[type_index].name << "  *********\n";

                cl_context context = clCreateContext(0,1, & device,NULL,NULL,NULL);
                if (!context) {
                    cerr << "Error in clCreateContext\n";
                }
                queue[ti] = clCreateCommandQueue(context, device,0,NULL);
                if (!queue[ti]) {
                    cerr << "Error in clCreateCommandQueue\n";
                }
                // Create and build a program from our OpenCL-C source code
                std::string ssrc = src0 + src1[ti] + src2;
                const char *src = ssrc.c_str();
                cl_program program = clCreateProgramWithSource(context,1, (const char **) &src, NULL,NULL);
                if (!program) {
                    cerr << "Error in clCreateProgramWithSource\n";
                }
                cl_int ret = clBuildProgram(program,0,NULL,NULL,NULL,NULL);
                if (ret) {
                    cerr << "Error in clBuildProgram: " << ret << "\n";
                }
                // Create a kernel from our program
                kernel[ti] = clCreateKernel(program, "square", NULL);
                if (!kernel[ti]) {
                    cerr << "Error in clCreateKernel\n";
                }
                // Allocate input and output buffers, and fill the input with data
                input[ti] = clCreateBuffer(context,CL_MEM_READ_ONLY,sizeof(unsigned __int64) * global[ti],NULL,NULL);
                if (!input[ti]) {
                    cerr << "Error in clCreateBuffer(CL_MEM_READ_ONLY)\n";
                }
                // Create an output memory buffer for our results
                output[ti] = clCreateBuffer(context,CL_MEM_WRITE_ONLY,sizeof(int) * global[ti],NULL,NULL);
                if (!output[ti]) {
                    cerr << "Error in clCreateBuffer(CL_MEM_WRITE_ONLY)\n";
                }
                // Set the arguments to our kernel, and enqueue it for execution
                ret = clSetKernelArg(kernel[ti],0,sizeof(cl_mem), &input[ti]);
                if (ret) cerr << "Error in clSetKernelArg(0): " << ret << "\n";
                ret = clSetKernelArg(kernel[ti],1,sizeof(cl_mem), &output[ti]);
                if (ret) cerr << "Error in clSetKernelArg(1): " << ret << "\n";
//                ret = clSetKernelArg(kernel,2,sizeof(size_t), &count);
//                if (ret) cerr << "Error in clSetKernelArg(2): " << ret << "\n";
// Get the maximum number of work items supported for this kernel on this device

                ret = clGetKernelWorkGroupInfo(kernel[ti], device,CL_KERNEL_WORK_GROUP_SIZE,sizeof(size_t),&local[ti],NULL);
                if (ret) {
                    cerr << "Error in clGetKernelWorkGroupInfo: " << ret << "\n";
                } else
                cout << "clGetKernelWorkGroupInfo -> local: " << local[ti] << "\n";
                if (local[ti] > global[ti]) local[ti] = global[ti];
            }
        }
    }



                int last_ind; int mn = 1024;

                //create threads
                boost::thread_group calc_threads;
                for (int i = 0; i != 0; ++i)
                    calc_threads.create_thread(thcalc);
            int clprimes = 0;
                for (int m = 0; m < mn; m++) {
        _micro_tic();
        for (int ti = 0; ti < tn; ti++) {
                // Copy our host buffer of random values to the input device buffer
                cl_int ret = clEnqueueWriteBuffer(queue[ti], input[ti],CL_TRUE,0,sizeof(unsigned __int64) * global[ti], data[ti][ind],0,NULL,NULL);
                if (ret) {
                    cerr << "Error in clEnqueueWriteBuffer: " << ret << "\n";
                }
                ret = clEnqueueNDRangeKernel(queue[ti], kernel[ti],1,NULL, &global[ti], &local[ti],0,NULL,NULL);
                if (ret) cerr << "Error in clEnqueueNDRangeKernel: " << ret << "\n";
                ret = clFlush(queue[ti]);
                if (ret) cerr << "Error in clFlush: " << ret << "\n";
        }
cout << m << ") Set up and flush queue in " << _micro_toc() << "us\n";_micro_tic();
                last_ind = ind;
                ind = 1 - ind;
                if (m < mn - 1) {
                    for (int ti = 0; ti < tn; ti++) {
                        unsigned __int64 base = get_count(global[ti]);
                        for(int i = 0; i < global[ti]; i++) {
                            data[ti][ind][i] = ((i+base)/8)*30+primes1[i%8]+360;
                        }
                    }


 //                   int minicount = 32*1024;
 //                   calc(get_count(minicount), minicount);
                }

//cout << m << ") Set up new candidates ("<<count<<") from "<<data[ind][0]<<" to "<<data[ind][count-1]<<" in " << _micro_toc() << "us\n";_micro_tic();
           if (m) { for (int ti = 0; ti < tn; ti++) {
                    int np = 0;   for(int i = 0; i < global[ti]; i++) {
     //               if (results[i] == results0[i]) correct++;
                    if (results[ti][i]) np++;
                }
                clprimes+=np;nprimes+=np;
                cout << m << ") count primes ("<<np<<") in " << _micro_toc() << "us\n";
           }
 _micro_tic();}
            for (int ti = 0; ti < tn; ti++) {
                // Force the command queue to get processed, wait until all commands are complete
                cl_int ret = clFinish(queue[ti]);
                if (ret) cerr << "Error in clFinish: " << ret << "\n";
cout << m << ") clFinish in " << _micro_toc() << "us\n";_micro_tic();
                // Read back the results
                ret = clEnqueueReadBuffer(queue[ti], output[ti],CL_TRUE,0,sizeof(int) * global[ti], results[ti],0,NULL,NULL);
                if (ret) cerr << "Error in clEnqueueReadBuffer: " << ret << "\n";
//cout << m << ") clEnqueueReadBuffer in " << _micro_toc() << "us\n";_micro_tic();
                // Validate our results
//                int correct = 0;

//                    correct += (results[i] == results0[i]) ? 1 : 0;
                // Print a brief summary detailing the results
//                printf("Computed '%d' bad values! %lld\n", -correct + count, _micro_toc());
//                printf("Computed %d primes up to %d (%5.2f%%)\n", nprimes, data[last_ind][count-1], nprimes*100.0/data[last_ind][count-1]);
                }
                if (m < mn - 1 && m % 16 == 15) {
printf("Computed %d/%llu primes up to %llu (%5.2f%%)\n", clprimes, nprimes, data[1][last_ind][global[1]-1], nprimes*100.0/data[1][last_ind][global[1]-1]);
                    {std::ofstream ofs(LAST_FNAME);
                    if (ofs) {
                        boost::archive::text_oarchive ar(ofs);
                        unsigned __int64 base = last_count - global[0] - global[1];
                        ar & base;
                        ar & nprimes;
                    }}
                }
                }
                stop = true;
                for (int ti = 0; ti < tn; ti++) {
                int np = 0; for(int i = 0; i < global[ti]; i++) {
     //               if (results[i] == results0[i]) correct++;
                    if (results[ti][i]) np++;
                }
                clprimes+=np;nprimes+=np;
                }
   //join threads
                calc_threads.join_all();
                printf("Computed %d/%llu primes up to %llu (%5.2f%%)\n", clprimes, nprimes, data[1][last_ind][global[1]-1], nprimes*100.0/data[1][last_ind][global[1]-1]);
                {std::ofstream ofs(LAST_FNAME);
                    if (ofs) {
                        boost::archive::text_oarchive ar(ofs);
                        ar & (last_count);
                        ar & nprimes;
                    }}
 //               cout << "Creating program in " << devices[type_index].name << "  DONE***\n\n";

        delete [] devices_of_type[0];
        delete [] devices_of_type[1];


    // -----------------------------------------------------------------------
    // Final clean up

    delete [] platforms;

    return 0;
}
