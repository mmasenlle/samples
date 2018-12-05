
import serial,threading
#from pylibftdi import BitBangDevice

#device_id = 'AH06IVXM'

class UsbRelay4:
    def __init__(self,port):
        self.DEBUG=True
        self.port = port
        self.state = 0
    def __enter__(self):
        try:
            import ctypes
            ftd2xx_lib = ctypes.cdll.LoadLibrary("ftd2xx.dll")
            ft_handle = ctypes.c_void_p(0)
            status = ftd2xx_lib.FT_Open(0, ctypes.pointer(ft_handle))
            if status: print('ftd2xx_lib.FT_Open:',status)
            else:
                status = ftd2xx_lib.FT_SetBitMode(ft_handle, 255, 1)
                if status: print('ftd2xx_lib.FT_SetBitMode:',status)
                else:
                    status = ftd2xx_lib.FT_Close(ft_handle)
                    if status: print('ftd2xx_lib.FT_Close:',status)
        except Exception, e:
            print "UsbRelay4()->Exception setting Bing Bang mode:",str(e)
        self.ser = serial.Serial(self.port, 9600)
        # with BitBangDevice(device_id) as bb:
            # bb.direction = 0x0F
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.ser.close()
    def on(self,idx):
        self.state |= (1 << idx)
        self.ser.write(serial.to_bytes([self.state]))
        # with BitBangDevice(device_id) as bb:
            # bb.port |= (1 << idx)
        if (self.DEBUG): print "on(",idx,"):",hex(self.state)
    def off(self,idx):
        self.state &= ~(1 << idx)
        self.ser.write(serial.to_bytes([self.state]))
        # with BitBangDevice(device_id) as bb:
            # bb.port &= ~(1 << idx)
        if (self.DEBUG): print "off(",idx,"):",hex(self.state)
    def pulse(self,idx,twidth=.5):
        if (self.DEBUG): print "pulse(",idx,",",twidth,")"
        if idx > 0 and idx < 5 and not (self.state & (1 << idx)):
            self.on(idx)
            threading.Timer(twidth, self.off, args=[idx]).start()
