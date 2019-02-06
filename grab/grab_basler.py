# ===============================================================================
#    This sample illustrates how to grab and process images using the CInstantCamera class.
#    The images are grabbed and processed asynchronously, i.e.,
#    while the application is processing a buffer, the acquisition of the next buffer is done
#    in parallel.
# 
#    The CInstantCamera class uses a pool of buffers to retrieve image data
#    from the camera device. Once a buffer is filled and ready,
#    the buffer can be retrieved from the camera object for processing. The buffer
#    and additional image data are collected in a grab result. The grab result is
#    held by a smart pointer after retrieval. The buffer is automatically reused
#    when explicitly released or when the smart pointer object is destroyed.
# ===============================================================================
from pypylon import pylon
from pypylon import genicam

import cv2,numpy
import sys

# Number of images to be grabbed.
countOfImagesToGrab = 20

# The exit code of the sample application.
exitCode = 0

print('cv2.ocl.haveOpenCL():',cv2.ocl.haveOpenCL())
print('cv2.ocl.useOpenCL():',cv2.ocl.useOpenCL())
print('cv2.ocl.haveAmdBlas():',cv2.ocl.haveAmdBlas())
print('cv2.ocl.haveAmdFft():',cv2.ocl.haveAmdFft())
cv2.ocl.setUseOpenCL(True)
print('cv2.ocl.haveOpenCL():',cv2.ocl.haveOpenCL())
print('cv2.ocl.useOpenCL():',cv2.ocl.useOpenCL())
print()
#print('cv2.getBuildInformation():',cv2.getBuildInformation())

# print('Hit a key to start')
# cv2.waitKey(10)

nodeFile = "grab_trigger_2.pfs"
save_features = False
load_features = False

i=0
video = None

try:
    # Create an instant camera object with the camera device found first.
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

    # Print the model name of the camera.
    print("Using device ", camera.GetDeviceInfo().GetModelName())
    
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed

    camera.Open()
    #pylon.FeaturePersistence.Load('acA640-300gc_22662999.pfs', camera.GetNodeMap(), True)
    camera.AcquisitionFrameRateEnable = 1
    camera.AcquisitionFrameRateAbs = 10 # 200 # fps
    camera.ExposureTimeRaw = 1000 # 5 # usecs
    camera.AcquisitionFrameCount = 20 # 500
    # camera.TriggerSelector = 'AcquisitionStart'
    # camera.TriggerMode = 'On'
    
    camera.UserOutputValue = 1

    pylon.FeaturePersistence.Save("grab_trigger_3.pfs", camera.GetNodeMap())
    #camera.Close()
    

    # The parameter MaxNumBuffer can be used to control the count of buffers
    # allocated for grabbing. The default value of this parameter is 10.
    camera.MaxNumBuffer = 5
    
    # camera.AcquisitionStart()
    # print('camera.TriggerMode():', camera.TriggerMode())
    # print('camera.ExposureMode():', camera.ExposureMode())
    # print('camera.TriggerSource():', camera.TriggerSource())
    # print('camera.TriggerActivation():', camera.TriggerActivation())
    # print('camera.AcquisitionStatusSelector():', camera.AcquisitionStatusSelector())

    # Start the grabbing of c_countOfImagesToGrab images.
    # The camera device is parameterized with a default configuration which
    # sets up free-running continuous acquisition.
    # camera.StartGrabbingMax(countOfImagesToGrab)
    camera.StartGrabbing()

    # Camera.StopGrabbing() is called automatically by the RetrieveResult() method
    # when c_countOfImagesToGrab images have been retrieved.
    while camera.IsGrabbing():
        # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
        #grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        grabResult = camera.RetrieveResult(1000000, pylon.TimeoutHandling_ThrowException)

        # Image grabbed successfully?
        if grabResult.GrabSucceeded():
            # Access the image data.
            # print("SizeX: ", grabResult.Width)
            # print("SizeY: ", grabResult.Height)
            #img = grabResult.Array
            # print("Gray value of first pixel: ", img[0, 0])
            # print(img)
            
            image = converter.Convert(grabResult)
            img = numpy.ndarray(buffer=image.GetBuffer(),shape=(image.GetHeight(),image.GetWidth(),3),dtype=numpy.uint8)
            
            cv2.imshow('image',img)
            # print img.shape
            # backtorgb = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
            # print backtorgb.shape
            
            if i % 20 == 0:
                video = cv2.VideoWriter('video'+str(i/20)+'.avi',cv2.VideoWriter_fourcc(*"XVID"),10,(640,480))

            video.write(img)
                
            i += 1
            print i
            
            # gray = cv2.UMat(img)
            # #gray = cv2.cvtColor(imgUMat, cv2.COLOR_BGR2GRAY)
            # gray2 = cv2.resize(gray, (0,0), fx=2.5, fy=2.5) 
            # gray = gray2 #* 5.73
            
            # gray = cv2.GaussianBlur(gray, (17, 17), 1.5)
            # gray = cv2.Canny(gray, 0, 50)
            
            # back = cv2.multiply(gray, gray2)
            # result = cv2.add(gray, back)
            
            #cv2.imshow('gray',gray)
            
            cv2.waitKey(1)
            #cv2.destroyAllWindows()
            
            if i % 20 == 0:
                video.release()
                
                
            
        else:
            print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
        grabResult.Release()

except genicam.GenericException as e:
    # Error handling.
    print("An exception occurred.",str(e))
    #print(e.GetDescription())
    exitCode = 1
    
camera.Close()
sys.exit(exitCode)
