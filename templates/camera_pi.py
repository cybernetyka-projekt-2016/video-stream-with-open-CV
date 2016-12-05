import time
import io
import threading
import picamera
from camshift import CamShift
from picamera.array import PiRGBArray
import cv2
from PIL import Image

class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame

    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            # camshift init
            iterator = 1
            observer_list = []
            cam_shift = CamShift()

            # camera setup
            camera.resolution = (320, 240)
            camera.brightness = 60
            camera.image_effect = 'colorbalance'
            camera.image_effect_params = (3,0.0,0.0,255.0)
            camera.hflip = True
            camera.vflip = True
            cls.rawCapture = PiRGBArray(camera, size=(320, 240))
            # let camera warm up
            time.sleep(2)

            for foo in camera.capture_continuous(cls.rawCapture, format="bgr",
                                                 use_video_port=True):
                # store frame
                new_frame = cam_shift.run(foo, observer_list, iterator)
                img = Image.fromarray(new_frame)
                b, g, r = img.split()
                img = Image.merge("RGB",(r,g,b))
                img.save('temp.jpg')
                roiImg = img.crop(box=None)
                imgByteArr = io.BytesIO()
                roiImg.save(imgByteArr, format="PNG")
                imgByteArr = imgByteArr.getvalue()
                # send frame to UI
                cls.frame = imgByteArr
                # reset stream for next frame
                cls.rawCapture.truncate(0)
                iterator += 1
                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - cls.last_access > 10:
                    break
        cls.thread = None
