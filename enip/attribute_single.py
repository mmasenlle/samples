import socket,select

#session
reg_session_stream = ''.join(chr(x) for x in [0x65, 0x0, # Register session
0x4, 0x0, # Length
0x0, 0x0, 0x0, 0x0, # Session handle
0x0, 0x0, 0x0, 0x0, # Status
0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, # Sender context
0x1, 0x0, 0x0, 0x0]) # Command specific data

get_attr_bytes = [0x6f, 0x0,
0x1a, 0x0, 0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x30, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
0x0, 0x0, 0x0, 0x0, # Interface Handle CIP
0x0, 0x0, # Timeout
0x2, # Item Count
0x0, 0x0, 0x0, 0x0, 0x0, 0xb2, 0x0, 0xa, 0x0, 0xe, 0x4, 0x20, 0x4, 0x25, 0, 0x14, 0x0, 0x30, 0x3]

def get_attr_single(host,port,class1,instance,attr):
    get_attr_bytes[43] = class1
    get_attr_bytes[46] = instance&0x0ff
    get_attr_bytes[47] = instance>>8
    get_attr_bytes[49] = attr

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(reg_session_stream)
    ready = select.select([s], [], [], 7)
    if not ready[0]: raise Exception('get_attr_single() -> Recv1 timeout')
    data = s.recv(1024)
    # print 'get_attr_single()->Received1(',len(data),'):', [hex(ord(c)) for c in data ]
    for i in range(4,8): get_attr_bytes[i] = ord(data[i])
    get_attr_stream = ''.join(chr(x) for x in get_attr_bytes)
    s.send(get_attr_stream)
    ready = select.select([s], [], [], 7)
    if not ready[0]: raise Exception('get_attr_single() -> Recv2 timeout')
    data = s.recv(1024)
    # print 'get_attr_single()->Received2(',len(data),'):', [hex(ord(c)) for c in data ]
    return data[44:]


set_attr_bytes = [0x6f, 0x0,
0x1a, 0x0, 0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x30, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
0x0, 0x0, 0x0, 0x0, # Interface Handle CIP
0x0, 0x0, # Timeout
0x2, # Item Count
0x0, 0x0, 0x0, 0x0, 0x0, 0xb2, 0x0, 0, 0, 0x10, 0x4, 0x20, 0x4, 0x25, 0, 0x14, 0x0, 0x30, 0x3]

def set_attr_single(host,port,class1,instance,attr,sdata):
    size=len(sdata)
    set_attr_bytes[2] = (size+26)&0x0ff
    set_attr_bytes[3] = (size+26)>>8
    set_attr_bytes[38] = (size+10)&0x0ff
    set_attr_bytes[39] = (size+10)>>8
    set_attr_bytes[43] = class1
    set_attr_bytes[46] = instance&0x0ff
    set_attr_bytes[47] = instance>>8
    set_attr_bytes[49] = attr

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(reg_session_stream)
    ready = select.select([s], [], [], 7)
    if not ready[0]: raise Exception('set_attr_single() -> Recv1 timeout')
    data = s.recv(1024)
    # print 'set_attr_single()->Received1(',len(data),'):', [hex(ord(c)) for c in data ]
    for i in range(4,8): get_attr_bytes[i] = ord(data[i])
    set_attr_stream = ''.join(chr(x) for x in set_attr_bytes + sdata)
    s.send(set_attr_stream)
    ready = select.select([s], [], [], 7)
    if not ready[0]: raise Exception('set_attr_single() -> Recv2 timeout')
    data = s.recv(1024)
    # print 'set_attr_single()->Received2(',len(data),'):', [hex(ord(c)) for c in data ]

