
import time,struct,ctypes,os,mmap

fd = os.open('/dev/shm/enip_adapter', os.O_CREAT | os.O_TRUNC | os.O_RDWR)
assert os.write(fd, '\x00' * mmap.PAGESIZE) == mmap.PAGESIZE
buf = mmap.mmap(fd, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_WRITE)
idata_ptr = ctypes.c_void_p(ctypes.addressof(ctypes.c_char.from_buffer(buf)))
odata_ptr = ctypes.c_void_p(ctypes.addressof(ctypes.c_char.from_buffer(buf, 1024)))

opener = ctypes.cdll.LoadLibrary('./OpENer.so')
opener.set_serial_number(123454321)
opener.config_assemblies(151,20,100,32,150,32)
# opener.set_print_debug(0) # to quiet verbosity

opener.set_data_input_ptr(idata_ptr)
opener.set_data_output_ptr(odata_ptr)

opener.init_loop('eno1')

# test
# od -d /dev/shm/enip_adapter
# python -m cpppo.server.enip.get_attribute -S "@4/100/3=(DINT)0,1,0,3,0,7,0,0"
# python -m cpppo.server.enip.get_attribute -S "@4/150/3=(DINT)10,11,0,32,0,57,0,0"

while True:
    OT_data = struct.unpack('i'*8, buf[:32])
    print 'OT_data:',OT_data
    TO_data = struct.unpack('i'*8, buf[1024:1056])
    print 'TO_data:',TO_data
    time.sleep(1)
