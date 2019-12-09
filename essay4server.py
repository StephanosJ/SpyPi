import picamera, subprocess, os
import pyaudio,wave,sys
import socket
from datetime import datetime

#Creates a TCP socket
mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Predefined the server IP-address
host = "192.168.2.184" 
port = 7777
# Prevents socket.error: [Errno 98] Address already in use
mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#Bind the socket to the server ip and port
mysocket.bind((host, port))
#Max connections is 5
mysocket.listen(5)
print("The SpyPi server is running!")

#Error handeling if it cant server with sockets it would print the error statement and close the python program
try:
    c, addr = mysocket.accept()
    print("A client has connected!")
except Exception as error:
    print(error)

#Receiving packets from the client and decode the bytes
data = c.recv(2048)
data = data.decode()

#Gets the current date
now = datetime.now()
outputnametime = now.strftime('date[%d_%m_%Y]time[%H-%M-%S]')

#Number of frames in the buffer
chunk = 8192
sample_format = pyaudio.paInt16
channels = 1
#Number of samples collected per second
rate = 44100
#Recording duration
record_seconds = float(data)
#A File name is the current date + current time .wav/.h264                                                  
wave_output_filename = outputnametime+'.wav'
h264_output_filename = outputnametime+'.h264'
#Puts all frames in the list
frames = []
with picamera.PiCamera() as camera:
    #Sets the camera resolution to FullHD
    camera.resolution= (1920,1080)
    p = pyaudio.PyAudio()
    #Setting up the stream
    stream = p.open(format=sample_format,
                channels=channels,
                rate=rate,
                frames_per_buffer=chunk,
                input=True)
    #Start Video Preview > this can be seen on the raspberry pi it self when it's plugged in to a monitor
    camera.start_preview()
    #Rotates the camera 180 degrees (this is because when you plug in the camera and let in stand it's upside down)
    camera.rotation = 180
    #Start Video recording
    camera.start_recording(h264_output_filename)                     
    #Start Audio streaming
    for i in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)
    #Pauses the Stream  
    stream.stop_stream()    
    #Stops the stream                                      
    stream.close()    
    #Closes the stream                                               
    p.terminate()  
    #Pauses the recording                                                  
    camera.stop_recording()     
    #Stops the preview on the Pi                                  
    camera.stop_preview()      
    #Closes the Camera"                                      
    camera.close()                                                   
#Creation of microphone recording wave file
wf = wave.open(wave_output_filename, 'wb')                              
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(sample_format))
wf.setframerate(rate)
wf.writeframes(b''.join(frames))
wf.close()
#Combining/Merging of Audio/Video File into mkv the mkv file name is the current date + current time (this is an linux command)
cmd = "ffmpeg -y -i " + wave_output_filename + " -r 30.123 -i " + h264_output_filename + " -filter:a aresample=async=1 -c:a flac -c:v copy " + outputnametime +".mkv"
#The linux command is executed
subprocess.call(cmd, shell=True)  
#EXTRA: moves the mkv file to the NAS (this is an linux command)                            
cmd = "mv " + outputnametime + ".mkv /mnt/nfs"
#The linux command is executed
subprocess.call(cmd, shell=True)
#Removes the wave file and the h264 file. When using the NAS NOTHING IS SAVED ON THE PI BECAUSE THE MKV IS MOVED AND NOT COPIED else the mkv is still saved on the Pi
cmd = "rm " + wave_output_filename + " && rm " + h264_output_filename
#The linux command is executed
subprocess.call(cmd, shell=True)
print('Muxing Done')
#Notifies the user that the recording has been saved
c.send('Audio and Video has been recorded, muxed and is available on the NAS under the name "'+ outputnametime+'.mkv"')
print("Notified the user\nClosing the Python program")
