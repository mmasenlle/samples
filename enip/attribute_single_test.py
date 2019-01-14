import attribute_single,struct

host='127.0.0.1'
port=44818
class1=4
instance=130
attr=3
data=[0]*396
attribute_single.set_attr_single(host,port,class1,instance,attr,data)

attribute_single.get_attr_single(host,port,class1,instance,attr)

resp=attribute_single.get_attr_single(host,port,0xA2,0x0014,5) # Miyachi Resistence2
print 'R:',struct.unpack('f', bytearray(resp))[0]

resp=attribute_single.get_attr_single(host,port,0xA2,0x0411,5) # Miyachi Ax1_Amplitude_P1
print 'I:',struct.unpack('f', bytearray(resp))[0]
attribute_single.set_attr_single(host,port,0xA2,0x0411,5,[ord(x) for x in struct.pack('f', 220.0)])
resp=attribute_single.get_attr_single(host,port,0xA2,0x0411,5)
print 'I:',struct.unpack('f', bytearray(resp))[0]