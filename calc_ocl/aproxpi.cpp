#include <boost/multiprecision/cpp_int.hpp>
#include <boost/thread/thread.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <iostream>
#include <fstream>
#include <vector>
//#include <iomanip>


#define BSIZE 100000
using boost::multiprecision::cpp_int;
static boost::mutex mutex;
static int thn = 4, cnt = 0;
static bool stop = false;
static cpp_int k = 3, pi = 4, n = 4;
static cpp_int get_k()
{
    boost::mutex::scoped_lock l(mutex);
    cpp_int r = k;
    k += (4*BSIZE);
    return r;
}
static void addpi(cpp_int pi_chunk)
{
    boost::mutex::scoped_lock l(mutex);
    pi += pi_chunk;
    if (++cnt % thn == 0) {
        std::cout << pi << std::endl;
    }
}

void calc()
{
    while (!stop) {
        cpp_int pi = 0;
        cpp_int k = get_k();
        for (int i = 0; i < BSIZE; i++) {
            pi -= (n/k);
            pi += (n/(k+2));
            k += 4;
        }
        addpi(pi);
    }
}

#define LAST_FNAME "pi.dat"

int main(int argc, char *argv[])
{
    if (argc > 1) try { thn = boost::lexical_cast<int>(argv[1]); } catch (...) {}
    for (int i = 0; i < 90; i++) pi *= 10, n *= 10;
    {std::ifstream ifs(LAST_FNAME);
    if (ifs) {
        boost::archive::text_iarchive ar(ifs);
        ar & pi;
        ar & k;
    }}
    std::vector<boost::thread*> ths;
    for (int i = 0; i < thn; i++) ths.push_back(new boost::thread(calc));
    if (getchar()) stop = true;
    for (int i = 0; i < thn; i++) {
        ths[i]->join();
        delete ths[i];
    }
    std::cout << std::endl << pi << std::endl;
    {std::ofstream ofs(LAST_FNAME);
    if (ofs) {
        boost::archive::text_oarchive ar(ofs);
        ar & pi;
        ar & k;
    }}
}
