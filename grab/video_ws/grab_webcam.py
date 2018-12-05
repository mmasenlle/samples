
import signal,time,os,threading
import sys,re,json
import ssl
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from optparse import OptionParser

## setup logging
import logging
logging.basicConfig(level = logging.DEBUG)

import cv2
import pyrealsense as pyrs
import numpy as np
import matplotlib.pyplot as plt

fgbg = cv2.createBackgroundSubtractorMOG2()

pyrs_dev=None
class SimpleImg(WebSocket):
    counter = 1
    last = time.time()
    check = 0
    points = []
    click_re = re.compile(r'click\: (\d+)\,(\d+)')
    saved_img = None
   
    def handleMessage(self):
        print self.data
        if (self.data == "check"):
            self.check += 1
            if (self.check > 2):
                self.check = 0
        if (self.data == "kill"):
            os._exit(0)
        if (self.data == "clear_points"):
            self.points = []
        click_res = self.click_re.match(self.data)
        #if (click_res):
        #   print "click_res.groups():",click_res.groups()
        if (click_res and len(click_res.groups()) == 2):
            point=(int(click_res.groups()[0]),int(click_res.groups()[1]))
            self.points.append(point)
            #print "points: ",point," len: ",len(self.points)
            print "points: ",self.points

        pyrs_dev.wait_for_frames()
        c = pyrs_dev.color
        #print "c.shape: ",c.shape
        #print "c.data.len: ",len(c.data)

        msg_resp = {}

        # define ROI
        px0=120
        px1=520
        py0=100
        py1=380

        n = len(self.points)
        if (n > 2):
            px0=640
            px1=0
            py0=480
            py1=0
            for point in self.points:
                if (point[0] < px0): px0 = point[0]
                if (point[0] > px1): px1 = point[0]
                if (point[1] < py0): py0 = point[1]
                if (point[1] > py1): py1 = point[1]
            #print "ROI:",px0,px1,py0,py1
     
        if (self.data == "save"):
            self.saved_img = c.copy()
            fgmask = fgbg.apply(c)
            #cv2.imshow('fgmask',c)
            #cv2.imshow('frame',fgmask)
            plt.imshow(fgmask)
            plt.show()

        if (self.data == "match" and self.saved_img is not None):
            try:
                orb = cv2.ORB_create()
                img1 = c[py0:py1,px0:px1]
                img2 = self.saved_img[py0:py1,px0:px1]
                kp1, des1 = orb.detectAndCompute(img1, None)
                kp2, des2 = orb.detectAndCompute(img2, None)
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                matches = bf.match(des1,des2)
                matches = sorted(matches, key = lambda x:x.distance)
                perc = 12*min(10,len(matches))
                print "perc_base: ",perc
                i=0
                for match in matches:
                    if (i < 10): perc -= match.distance
                    print "match.distance: ",match.distance
                    i+=1
                print "perc_2: ",perc
                str = "%d %%" % min(100,max(0,perc))
                cv2.putText(c, str, (1,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0))
                #img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:5],None, flags=2)
                #print "img3.shape: ",img3.shape
                #plt.imshow(img3)
                #plt.show()
            except: # catch *all* exceptions
                print "Unexpected error:", sys.exc_info()[0]

        # drawings
        if self.check > 0:
       
            # black and yellow
            bw = cv2.cvtColor(c[py0:py1,px0:px1], cv2.COLOR_BGR2GRAY)

            if self.check == 1:
                #Create default parametrization LSD
                lsd = cv2.createLineSegmentDetector(0)
                #Detect lines in the image
                lines = lsd.detect(bw)[0] #Position 0 of the returned tuple are the detected lines
                #Draw detected lines in the image
                c[py0:py1,px0:px1] = lsd.drawSegments(c[py0:py1,px0:px1], lines)

            if self.check == 2:
                corners = cv2.goodFeaturesToTrack(bw, 10, 0.01, 10)
                corners = np.float32(corners)

                for item in corners:
                    x, y = item[0]
                    cv2.circle(c[py0:py1,px0:px1], (x,y), 3, 255, -1)
        
            # draw ROI
            if (n < 3):
                cv2.rectangle(c,(px0,py0),(px1,py1),(0,255,0),2)

        if (n > 2):
            for i in range(1,n):
                cv2.line(c,self.points[i-1],self.points[i],(255,0,0))
            cv2.line(c,self.points[n-1],self.points[0],(255,0,0))

        # html5 canvas enjoys BGRA
        c = cv2.cvtColor(c, cv2.COLOR_BGR2BGRA)

        #msg_resp['points_len'] = len(self.points)
        #msg_resp['status'] = 'OK'

        #self.sendMessage(json.dumps(msg_resp))
        #print "msg_resp: ",json.dumps(msg_resp)
        self.sendMessage(c.data)
        now = time.time()
        print self.counter,(now - self.last)
        self.counter += 1
        self.last = now

    def handleConnected(self):
        pass

    def handleClose(self):
        pass


if __name__ == "__main__":

    parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
    parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
    parser.add_option("--port", default=8000, type='int', action="store", dest="port", help="port (8000)")
    parser.add_option("--example", default='echo', type='string', action="store", dest="example", help="echo, chat")
    parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
    parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
    parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")

    (options, args) = parser.parse_args()

    cls = SimpleImg
    # if options.example == 'chat':
        # cls = SimpleChat

    if options.ssl == 1:
        server = SimpleSSLWebSocketServer(options.host, options.port, cls, options.cert, options.cert, version=options.ver)
    else:
        server = SimpleWebSocketServer(options.host, options.port, cls)

    def close_sig_handler(signal, frame):
        server.close()
        sys.exit()

    signal.signal(signal.SIGINT, close_sig_handler)

    wserver = HTTPServer(('', 8080), SimpleHTTPRequestHandler)
    thread = threading.Thread(target = wserver.serve_forever)
    thread.daemon = True
    thread.start()
    print "HTTPServer on port 8080"
   
    with pyrs.Service() as a, pyrs.Device() as dev:
    #with pyrs.Service() as a, pyrs.Device(streams = [pyrs.stream.ColorStream(fps = 60)]) as dev:
    #with pyrs.Service() as a, pyrs.Device(streams = [pyrs.stream.ColorStream()]) as dev:
        dev.apply_ivcam_preset(0)
        pyrs_dev=dev

        server.serveforever()
