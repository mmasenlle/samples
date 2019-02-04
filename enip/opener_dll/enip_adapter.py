
import time,struct,ctypes


opener = ctypes.cdll.LoadLibrary('OpENer.dll')
# opener = ctypes.cdll.LoadLibrary('OpENer.so')
opener.config_assemblies(151,20,100,32,150,32)
# opener.set_print_debug(0) # to quiet verbosity
opener.get_data_output.restype=ctypes.c_void_p
opener.init_loop(9) # net interface on windows
# opener.init_loop('eno1')

while True:
    OT_data = struct.unpack('i'*8, bytearray(ctypes.cast(opener.get_data_output(), ctypes.POINTER(ctypes.c_ubyte * 32)).contents[:]))
    print OT_data
    time.sleep(1)