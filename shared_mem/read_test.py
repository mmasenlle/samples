import ctypes
import mmap
import os
import struct


class PartID():
    def __init__(self):
        fd = os.open('/dev/shm/pin_inspection.dat', os.O_RDONLY)
        self.mem = mmap.mmap(fd, 8, mmap.MAP_SHARED, mmap.PROT_READ)
    def getID(self):
        return struct.unpack('i', self.mem[:4])[0]

partID=PartID()
while True:
    print 'partID',partID.getID()
    c=os.read(0,1)
    print c
    if c=='q': break