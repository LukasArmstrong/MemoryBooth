"""
# Author: Lukas Armstrong
# Date: 06/02/22
# Purpose: PLay around with pyaudio to record audio
"""
import pyaudio
import wave

chunk =1024
sample_format = pyaudio.paInt16
channels = 2
fs = 44100
time_in_seconds = 10
filename = "test.wav"

p = pyaudio.PyAudio()

print('-----Now Recording-----')

stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk,input=True)

frames = []

for i in range(0, int(fs / chunk * time_in_seconds)):
    data = stream.read(chunk)
    frames.append(data)

stream.stop_stream()
stream.close()
p.terminate()
 
print('-----Finished Recording-----')
 
# Open and Set the data of the WAV file
file = wave.open(filename, 'wb')
file.setnchannels(channels)
file.setsampwidth(p.get_sample_size(sample_format))
file.setframerate(fs)
 
#Write and Close the File
file.writeframes(b''.join(frames))
file.close()