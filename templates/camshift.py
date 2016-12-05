import sys
import math
import numpy as np
import cv2
import time
import io
from picamera.array import PiRGBArray
from picamera import PiCamera
import pdb

img1 = cv2.imread('KULA.png')
height, width, depth = img1.shape

class CamShift(object):

    def __init__(self):
        self.hist = None
        self.first = True

    def run(self, frame, lista_obserwowanych, i):
        if self.first:
            img2 = cv2.imread('hist.jpg')
            h, w, c = img2.shape
            dane = open('hist_data.txt').read()
            dane1 = dane.split("|")
            xo = np.int16(dane1[0])
            yo = np.int16(dane1[1])
            x = np.int16(dane1[2])
            y = np.int16(dane1[3])
            x0, y0 = np.maximum(0,np.minimum([xo, yo],[x, y]))
            x1, y1 = np.minimum([w, h], np.maximum([xo, yo],[x, y]))
            vis = img2.copy()
            hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
            self.track_window = (x0, y0, x1-x0, y1-y0)
            hsv_roi = hsv[y0:y1, x0:x1]
            mask_roi = mask[y0:y1, x0:x1]
            self.hist = cv2.calcHist([hsv_roi],[0], mask_roi, [16], [0, 180])
            cv2.normalize(self.hist, self.hist, 0, 255, cv2.NORM_MINMAX)
            self.hist = self.hist.reshape(-1)
            self.first = False
            prob = cv2.calcBackProject([hsv], [0], self.hist, [0, 180], 1)
            prob &=mask
            term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
            track_box, self.track_window = cv2.CamShift(prob, self.track_window, term_crit)
        vis_array = frame.array
        vis = vis_array.copy()
        hsv = cv2.cvtColor(vis_array, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
        resized = vis_array.copy()
        i += 1

        if  i % 10 == 9:
            for x in range (0,640, 80):
                for y in range (0,480,80):
                    x0, y0, x1, y1 = x, y, x+50, y+50
                    track_window = (x0, y0, x1 - x0, y1 - y0)
                    hsv_roi = hsv[y0:y1, x0:x1]
                    mask_roi = mask[y0:y1, x0:x1]
                    hist2 = cv2.calcHist([hsv_roi], [0], mask_roi, [16], [0, 180])
                    cv2.normalize(hist2, hist2, 0, 255, cv2.NORM_MINMAX);
                    d = cv2.compareHist(hist2, self.hist, 2)
                    print ("d: ",d)
                    if d>270:
                        lista_obserwowanych.append(track_window)


        for tw in lista_obserwowanych:

            prob = cv2.calcBackProject([hsv], [0], self.hist, [0, 180], 1)
            prob &= mask
            term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
            track_box, newtw = cv2.CamShift(prob, tw, term_crit)
            xPos = track_box[0][0]
            yPos = track_box[0][1]
            xPosEnd = track_box[1][0]
            yPosEnd = track_box[1][1]
            lista_obserwowanych.remove(tw)

            try:
                scale = yPosEnd/height
                dim = (int(height*scale), int(width*scale))
                resized = cv2.resize(img1, dim, interpolation=cv2.INTER_AREA)
                resized_height, resized_width, resized_depth = resized.shape
                roi = vis[int(yPos - resized_height / 2):int(yPos - resized_height / 2 + resized_height ), int(xPos - resized_width / 2):int(xPos - resized_width / 2 + resized_width)]

                img2gray = cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)
                ret, mask2 = cv2.threshold(img2gray,240,255,cv2.THRESH_BINARY)
                mask2_inv = cv2.bitwise_not(mask2)

                img1_bg = cv2.bitwise_and(roi,roi,mask = mask2)
                img2_fg = cv2.bitwise_and(resized,resized,mask = mask2_inv)

                dst = cv2.add(img1_bg,img2_fg)

                vis[int(yPos - resized_height / 2):int(yPos - resized_height / 2 + resized_height ), int(xPos - resized_width / 2):int(xPos - resized_width / 2 + resized_width)] = dst
                lista_obserwowanych.append(newtw)
            except:
                print track_box

        cv2.imshow("aaaaa",vis)
        return vis

