
#session
reg_session_stream = ''.join(chr(x) for x in [0x65, 0x0, # Register session
0x4, 0x0, # Length
0x0, 0x0, 0x0, 0x0, # Session handle
0x0, 0x0, 0x0, 0x0, # Status
0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, # Sender context
0x1, 0x0, 0x0, 0x0]) # Command specific data

forwardOpen = [0x6f,0x00, # SendRRData
0x56,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x03,0x00,0x00,0x00,0x00,0x00,
0xb2,0x00, # Data Item
0x32,0x00, # Data Length
0x54, # Forward Open
0x02, # Path size
0x20,0x06,0x24,0x01, # Class 6, instance 1 (Connection manager)
0x03, # Priority
0xfa, # Timeout ticks
0x14,0xfc,0xc8,0x08, # Connection ID O->T
0x15,0xfc,0xc8,0x08, # Connection ID T->O
0x91,0x8c, # Connection serial number
0xff,0x00, # Originator vendor ID
0xff,0xff,0xff,0xff, # Originator serial number
0x03, # Timeout multiplier
0x00,0x00,0x00, # Reserverd
0x20,0xa1,0x07,0x00, # Request packet rate microseconds O->T
0x92,0x49, # Network connection parameters O->T
0x20,0xa1,0x07,0x00, # Request packet rate microseconds T->O
0x06,0x48, # Network connection parameters T->O
0x01, # Transport type trigger
0x04, # Connection path size
0x20,0x04, # assembly class (4)
0x24,128, # config assembly 4/instance
0x2c,130, # output assembly 4/instance 
0x2c,129, # input assembly 4/instance
0x01,0x80,0x10,0x00,
0x00,0x02, # sin family
0x08,0xae, # udp port
0x00,0x00,0x00,0x00, # multicast ip
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]

O_T_header = [
0x02,0x00, # Item count
0x02,0x80, # Type ID
0x08,0x00, # Length
0x00,0x00,0x00,0x00, # connection ID O->T
0x01,0x00,0x00,0x00, # sequence Count
0xb1,0x00, # Type ID
0x92,0x01, # Data Length
0x01,0x00, # Secuence Data
0x01,0x00,0x00,0x00, # Header 32 bit
]
O_T_data = [0]*396


# Echo client program
import socket,time,threading,signal,sys,select,random,struct

HOST = '172.24.0.73'
PORT1 = 44818
PORT2 = 2222
T_RATE_us = 100000

for i in range(4): forwardOpen[74+i] = forwardOpen[68+i] = (T_RATE_us >> i*8)&0x0ff
forwardOpen_stream = ''.join(chr(x) for x in forwardOpen)

s=None
s1=None
s2=None

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print 'Connecting'
        s.connect((HOST, PORT1))

        print 'About to register session'
        s.send(reg_session_stream)
        data = s.recv(1024)

        print 'reg_session_resp(',len(data),'):', [hex(ord(c)) for c in data ]

        s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s1.setblocking(0)
        s1.bind(('', 2222))


        print 'About to forwardOpen'
        s.send(forwardOpen_stream)
        data = s.recv(1024)
        print 'forwardOpen_resp(',len(data),'):', [hex(ord(c)) for c in data ]
        if len(data) > 100:
            for i in range(4): O_T_header[6+i] = ord(data[44+i]) # connection ID O->T

        s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s2.connect((HOST, PORT2))
        nsec = 0
        piezaID = 0
        data=[]
        t0 = time.time()
        while True:
            if nsec % 10 == 0:
                data=[0,]
                piezaID += 1
                data.append(piezaID)
                for i in range(96): data.append(random.uniform(.0, 100.))
                data.append(0)
            nsec += 1
            for i in range(4): O_T_header[10+i] = (nsec >> i*8)&0x0ff
            for i in range(2): O_T_header[18+i] = O_T_header[10+i]
            produced = ''.join(chr(x) for x in O_T_header)
            s2.send(produced + struct.pack('ii'+'f'*96 + 'i', *data))
            print nsec,'Sent',len(produced)
            ready = select.select([s1], [], [], 5)
            if not ready[0]: raise Exception('Recv error ?')
            rdat = s1.recv(1024)
            #print 'Recv:', [hex(ord(c)) for c in rdat ]
            print 'Recv',len(rdat),time.time() - t0
            t0 = time.time()
            

    except Exception, e:
        print "Except:",str(e)
    try:
        if s2: s2.close()
        if s1: s1.close()
        if s: s.close()
    except:
        pass

    time.sleep(5)
