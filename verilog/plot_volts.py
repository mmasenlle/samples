import serial
import matplotlib.pyplot as plt
import sys,select,tty,termios

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

CHUNK_SIZE = 4000
POLL_TOUT = .1
K_bits2Volts = .0123

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=POLL_TOUT)
T=None # period
volts=[]

buf_size = 20


while True:
    in_bin = ser.read(CHUNK_SIZE)
#    in_bin = [int(x) for x in raw_input().split()] #[]
#    print("Response(",len(in_bin),"):", in_bin)
    if not T and len(in_bin) < CHUNK_SIZE and (len(volts) % CHUNK_SIZE) != 0:
        T = POLL_TOUT / float(len(in_bin))
    volts += [x*K_bits2Volts for x in in_bin]

    if T:
        if len(volts) > buf_size: volts = volts[-buf_size:]
        plt.clf()
        plt.plot([T*i for i in range(0,len(volts))], volts)
        plt.ylim(0, 3.3)
        plt.draw()
        plt.pause(0.0001)
        if isData():
            c = sys.stdin.read(1)
            if c == '\x1b' or c == 'q':  # x1b is ESC
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                break
            elif c == '+': buf_size *= 2
            elif c == '-' and buf_size > 1: buf_size = int(buf_size / 2)
            print('c:',c,'buf_size:',buf_size)
