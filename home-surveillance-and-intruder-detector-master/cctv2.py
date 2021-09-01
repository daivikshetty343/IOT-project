
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
	help="path to the JSON configuration file")
args = vars(ap.parse_args())


warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))
client = None



camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

cv2.ocl.setUseOpenCL(False)

fgbg = cv2.createBackgroundSubtractorMOG2()



print "[INFO] warming up..."
time.sleep(conf["camera_warmup_time"])
lastUploaded = datetime.datetime.now()
motionCounter = 0

for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	
	frame = f.array
	timestamp = datetime.datetime.now()
	text = "Unoccupied"
	thresh = fgbg.apply(frame)
	thresh = cv2.erode(thresh, (11,11), iterations=5)
	thresh = cv2.dilate(thresh, (11,11), iterations=1)
	cnts= cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	
	for c in cnts:
		t
		if cv2.contourArea(c) < conf["min_area"]:
			continue
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Occupied"
	ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.35, (0, 0, 255), 1)
	if text == "Occupied":
		if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:		
			motionCounter += 1	
			if motionCounter >= conf["min_motion_frames"]:
                                d+=1
                                cv2.imwrite('/home/pi/googledrive/intruder'+str(d)+'.png',frame)
				lastUploaded = timestamp
				motionCounter = 0
	else:
		motionCounter = 0
	if conf["show_video"]:
		cv2.imshow("Security Feed", frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break
	rawCapture.truncate(0)
