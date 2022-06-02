from time import time
import numpy as np
import os
import cv2
from datetime import datetime, timedelta
from pytz import timezone
from os.path import expanduser

STD_DIMENSIONS = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
}

VIDEO_TYPE = {
    'avi': cv2.VideoWriter_fourcc(*'FFV1'),
    #'mp4': cv2.VideoWriter_fourcc(*'MP4V') #Look into AVdn and h.264
}

def change_res(cap, width, height):
    cap.set(3, width)
    cap.set(4, height)

def get_dims(cap, res='1080p'):
    width, height = STD_DIMENSIONS["480p"]
    if res in STD_DIMENSIONS:
        width, height = STD_DIMENSIONS[res]
    change_res(cap, width, height)
    return width, height

def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
        return VIDEO_TYPE[ext]
    return VIDEO_TYPE['avi']


home = expanduser("~")
dir = home+'/Videos/MemoryBooth/'
window_name = 'Projector'
cameraID = 1
vidCounter = 0
vidToggle = False
countDownTime = datetime.now()
fileExtention = '.avi'
filename = 'video' + fileExtention
frames_per_second = 30.0
res = '720p' #Work Laptop is 720p, final camera will be 1080p
cap = cv2.VideoCapture(cameraID, cv2.CAP_DSHOW)
out = cv2.VideoWriter(
    dir+filename, get_video_type(filename), frames_per_second, get_dims(cap, res))

cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(
    window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

if ~cap.isOpened():
    print("Failed to grab frame")

while cap.isOpened():
    ret, frame = cap.read()
    currentTime = datetime.now()
    if not ret:
        print("failed to grab frame")
        break

    if countDownTime > currentTime:
        #hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #hsvframe[:, :, 2] -= 20
        #frame = cv2.cvtColor(hsvframe, cv2.COLOR_HSV2BGR)
        floatFrame = frame.astype(np.float)
        for i in range(1,3):
            floatFrame = np.absolute(floatFrame[:,:,i]-20)
        remainingTimeDate = countDownTime - currentTime
        remainingTime = remainingTimeDate.seconds+1
        font = cv2.FONT_HERSHEY_TRIPLEX
        org = (520, 940)
        fontScale = 30
        color = (255, 255, 255)
        thickness = 90
        frame = cv2.putText(frame, str(remainingTime), org,
                            font, fontScale, color, thickness)
    cv2.imshow(window_name, frame)

    if vidToggle:
        out.write(frame)

    k = cv2.waitKey(1)
    if k % 256 == 32 and not vidToggle:
        filename = "MemoryBooth_" + datetime.now(timezone('EST')).strftime(
            "%Y%m%d%H%M%S") + "_" + str(vidCounter).zfill(4)+fileExtention
        out = cv2.VideoWriter(
            dir+filename, get_video_type(filename), frames_per_second, get_dims(cap, res))
        countDownTime = datetime.now() + timedelta(seconds=3)
        vidToggle = True
        vidCounter += 1
        print("{} has started!".format(filename))
    elif k % 256 == 32 and vidToggle:
        out.release()
        vidToggle = False
        print("{} has been written!".format(filename))
    elif k % 256 == 27:
        if vidToggle:
            out.release()
        break

cap.release()
cv2.destroyAllWindows()