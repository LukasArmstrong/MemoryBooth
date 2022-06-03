"""
# Author: Lukas Armstrong
# Date: 06/03/22
# Purpose: Play around with opencv to record video
"""
#import numpy as np
import time
import os
import cv2
import pyaudio
import wave
import subprocess
import moviepy.editor as mpe
from datetime import datetime, timedelta
from pytz import timezone
from os.path import expanduser

STD_DIMENSIONS = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
}

VIDEO_TYPE = {
    'avi': cv2.VideoWriter_fourcc(*'DIVX'),
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
cameraID = 0
vidCounter = 0
vidToggle = False
countDownTime = datetime.now()
fileExtention = '.avi'
filename = 'tempVideo' + fileExtention
frames_per_second = 30.0
res = '720p' #Work Laptop is 720p, final camera will be 1080p
chunk =1024
sample_format = pyaudio.paInt16
channels = 2
fs = 44100
time_in_seconds = 10
video_startTime = 0
video_frameCount = 0
audio_filename = "tempAudio.wav"

cap = cv2.VideoCapture(cameraID, cv2.CAP_DSHOW)
out = cv2.VideoWriter(
    dir+filename, get_video_type(filename), frames_per_second, get_dims(cap, res))

p = pyaudio.PyAudio()

stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk,input=True)

audio = []

cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(
    window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

if ~cap.isOpened():
    print("1 - Failed to grab frame")

while cap.isOpened():
    ret, frame = cap.read()
    currentTime = datetime.now()
    if not ret:
        print("2- failed to grab frame")
        break

    
    # if countDownTime > currentTime:
    #     #hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #     #hsvframe[:, :, 2] -= 20
    #     #frame = cv2.cvtColor(hsvframe, cv2.COLOR_HSV2BGR)
    #     floatFrame = frame.astype(float)
    #     for i in range(1,3):
    #         floatFrame = np.absolute(floatFrame[:,:]-20)
    #     floatFrame = np.clip(floatFrame,0,None)
    #     frame = floatFrame
    #     remainingTimeDate = countDownTime - currentTime
    #     remainingTime = remainingTimeDate.seconds+1
    #     font = cv2.FONT_HERSHEY_TRIPLEX
    #     org = (520, 940)
    #     fontScale = 30
    #     color = (255, 255, 255)
    #     thickness = 90
    #     frame = cv2.putText(frame, str(remainingTime), org,
    #                         font, fontScale, color, thickness)
    cv2.imshow(window_name, frame)

    if vidToggle:
        out.write(frame)
        data = stream.read(chunk)
        audio.append(data)
        video_frameCount += 1

    k = cv2.waitKey(1)
    if k % 256 == 32 and not vidToggle:
        out = cv2.VideoWriter(
            filename, get_video_type(filename), frames_per_second, get_dims(cap, res))
        video_startTime = time.time()
        #countDownTime = datetime.now() + timedelta(seconds=3)
        stream.start_stream()
        vidToggle = True
        vidCounter += 1
        filename = dir+"MemoryBooth_" + datetime.now(timezone('EST')).strftime(
            "%Y%m%d%H%M%S") + "_" + str(vidCounter).zfill(4)+fileExtention
        print("{} has started!".format(filename))
    elif k % 256 == 32 and vidToggle:
        out.release()
        elapsed_time = time.time() - video_startTime
        stream.stop_stream()
        stream.close()
        
        waveFile = wave.open(audio_filename, 'wb')
        waveFile.setnchannels(channels)
        waveFile.setsampwidth(p.get_sample_size(sample_format))
        waveFile.setframerate(fs)
        waveFile.writeframes(b''.join(audio))
        waveFile.close()
        vidToggle = False        
        recorded_fps = video_frameCount / elapsed_time

        #combine Audio and Video
        my_clip = mpe.VideoFileClip('tempVideo.avi')
        audio_background = mpe.AudioFileClip('tempAudio.wav')
        final_clip = my_clip.set_audio(audio_background)
        # Merging audio and video signal
        if abs(recorded_fps - frames_per_second) >= 0.01:    # If the fps rate was higher/lower than expected, re-encode it to the expected
            # print("Re-encoding")
            # cmd = "ffmpeg -y -i tempVideo.avi -r " + str(recorded_fps) + " -q:v 2 tempVideo2.avi"
            # subprocess.call(cmd, shell=True)
            # print("Muxing")
            # cmd = "ffmpeg -y -ac 2 -channel_layout stereo -i tempAudio.wav -i tempVideo2.avi " + filename + ".avi"
            # subprocess.call(cmd, shell=True)
            final_clip.write_videofile(filename,fps=recorded_fps,codec='mpeg4')
        else:
            # print("Normal recording\nMuxing")
            # cmd = "ffmpeg -y -ac 2 -channel_layout stereo -i tempAudio.wav -i tempVideo.avi  -q:v 2 " + filename + ".avi"
            # subprocess.call(cmd, shell=True)
            # print("..")
            final_clip.write_videofile(filename,fps=frames_per_second)

        print("{} has been written!".format(filename))
        filename = 'tempVideo' + fileExtention
        video_frameCount =0
    elif k % 256 == 27:
        if vidToggle:
            out.release()
        break

filename = "MemoryBooth_" + datetime.now(timezone('EST')).strftime(
            "%Y%m%d%H%M%S") + "_" + str(vidCounter).zfill(4)+fileExtention

p.terminate()
cap.release()
cv2.destroyAllWindows()
