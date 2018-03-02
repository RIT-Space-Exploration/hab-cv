''' Raspberry Pi video stream.
    Originally written by jrosebr1
    https://github.com/jrosebr1/imutils/blob/master/imutils/video/pivideostream.py

    Modified by Philip Linden
    - Removed OpenCV dependency (opencv is unused in this class)
'''
# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import threading

class PiVideoStream:
    def __init__(self, resolution=(320, 240), framerate=32):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="rgb", use_video_port=True)
        self.lock = threading.Lock() # thread safe lock
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        self.t = threading.Thread(target=self.update, args=())
        self.t.daemon = True
        self.t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        with self.lock:
            for f in self.stream:
                # grab the frame from the stream and clear the stream in
                # preparation for the next frame
                self.frame = f.array
                self.rawCapture.truncate(0)

                # if the thread indicator variable is set, stop the thread
                # and resource camera resources
                if self.stopped:
                    self.stream.close()
                    self.rawCapture.close()
                    self.camera.close()
                    return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True