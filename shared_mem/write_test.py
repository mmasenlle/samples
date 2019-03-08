import ctypes
import mmap
import os
import struct


class PartID():
    def __init__(self):
        fd = os.open('/dev/shm/pin_inspection.dat', os.O_CREAT | os.O_TRUNC | os.O_RDWR)
        assert os.write(fd, '\x00' * mmap.PAGESIZE) == mmap.PAGESIZE
        buf = mmap.mmap(fd, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_WRITE)
        self.ID = ctypes.c_int.from_buffer(buf)
    def getID(self):
        return self.ID.value

partID=PartID()
print 'partID',partID.getID()
partID.ID.value=7
print 'partID',partID.getID()