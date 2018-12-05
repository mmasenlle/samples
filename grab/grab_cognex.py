from ftplib import FTP
import cv2,time,telnetlib

# NATIVE MODE COMMANDS
# https://es.scribd.com/document/349308773/Native-Mode-Commands

IP_CAMARA='172.24.1.90'

tn = telnetlib.Telnet(IP_CAMARA)
tn.read_until("User: ")
tn.write("admin\r\n")
tn.read_until("Password: ")
tn.write("\r\n")
tn.write("Put Live 1\r\n")
print tn.read_some()

ftp = FTP(IP_CAMARA, 'admin')
i=0
t0 = time.time()

#while True:
for i in range(50):
    ftp.retrbinary('RETR image.jpg', open('image.jpg', 'wb').write)
    i += 1
    print i,float(i)/(time.time()-t0)
    img = cv2.imread('image.jpg')
    cv2.imshow('image',img)
    cv2.waitKey(1)

ftp.close()
tn.write("Put Live 0\r\n")
tn.close()