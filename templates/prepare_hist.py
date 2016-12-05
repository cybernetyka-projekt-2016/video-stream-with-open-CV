import sys
import math
import numpy as np
import cv2
import time
import io
from picamera.array import PiRGBArray
from picamera import PiCamera

class App(object):
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (320, 240)
        self.camera.brightness = 60
        self.camera.hflip = True
        self.camera.vflip = True
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera, size=(320, 240))
        time.sleep(0.1)
        cv2.namedWindow('camshift')
        cv2.setMouseCallback('camshift',self.onmouse)

        self.selection = None
        self.drag_start = None
        self.tracking_state = 0
        self.showbackproj = False

    def onmouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            self.tracking_state = 0
            if flags == 0: flags = 1
            else: flags = 0

        if self.drag_start:
            if flags & cv2.EVENT_FLAG_LBUTTON:
                xo, yo = self.drag_start
                string = str(xo) + "|" +str(yo) + "|" + str(x) + "|" +str(y)
                print string
                open('hist_data.txt','w').write(string)
                

        if event == cv2.EVENT_LBUTTONUP:
            self.selection = True
                

    def run(self):
        for foo in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            if self.selection:
                sys.exit()
            self.frame = foo.array
            cv2.imshow('camshift', self.frame)
            cv2.imwrite('hist.jpg',self.frame)
            key = cv2.waitKey(1) & 0xFF
            self.rawCapture.truncate(0)
            if key == ord("q"):
                break

if __name__ == '__main__':
    App().run()
