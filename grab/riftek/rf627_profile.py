import ctypes,sys,time,threading
import matplotlib.pyplot as plt
import numpy as np

def store():
    fig = plt.figure('Profiles', figsize=(12,6))
    ax1 = fig.add_subplot(111)
    ax1.clear()
    ax1.set_xlim((-25,25))
    ax1.set_ylim((0,50))
    ax1.grid()
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Z (mm)')
    line1, = ax1.plot(0,0,'.')
    fig.show()
    t=0
    buffer = ctypes.create_string_buffer(1296*8)
    np.set_printoptions(threshold=sys.maxsize, linewidth=sys.maxsize, precision=None)
    with open(fname, 'w') as f:
        while rf627_lib.get_profile(buffer):
            xz = np.frombuffer(buffer, ctypes.c_float)
            if t % 20 == 0:
                ax1.set_title('Profile at t=' + str(t/100) + ' s')
                line1.set_xdata(xz[0::2])
                line1.set_ydata(xz[1::2])
                fig.canvas.draw()
                fig.canvas.flush_events()
            f.write(np.array2string(xz, separator=';')[1:-1])
            f.write('\n')
            t+=1

grab_time = 10
fname = 'profile1.csv'
if len(sys.argv) > 1: grab_time = int(sys.argv[1])
if len(sys.argv) > 2: fname = sys.argv[2]
rf627_lib = ctypes.cdll.LoadLibrary("RF627_profile.dll")
n=rf627_lib.init_scanner(100, True)
if n > 0:
    tstore = threading.Thread(target=store)
    s = 'Press ENTER to start recording '+str(grab_time)+' seconds in ' + fname
    input(s)
    rf627_lib.start_grabbing()
    tstore.start()
    time.sleep(grab_time)
    rf627_lib.stop_grabbing()
    rf627_lib.stop_scanner()
    tstore.join()

