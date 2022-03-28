import sys
sys.path.append('./')
import cv2
import numpy as np
from multiprocessing import Process, Queue
import os
import time

class VPFCapture:
    def __init__(self, video_url, gpu_idx):
        self.cap = cv2.VideoCapture(video_url)
        import vpf.PyNvCodec as nvc
        self.nvc = nvc
        self.nvDec = self.nvc.PyNvDecoder(video_url, gpu_idx)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.nvDwn = self.nvc.PySurfaceDownloader(self.width, self.height, 
                        self.nvc.PixelFormat.BGR, gpu_idx)
        self.cvtNV12_RGB = self.nvc.PySurfaceConverter(self.nvDec.Width(), 
                                self.nvDec.Height(), self.nvDec.Format(), 
                                self.nvc.PixelFormat.BGR, gpu_idx)
        self.frameSize = self.nvDec.Framesize()
        self.link = video_url


    def isOpened(self):
        return self.cap.isOpened()


    def release(self):
        del self.nvDec, self.nvDwn, self.cvtNV12_RGB
        return self.cap.release()


    def get(self, param_idx):
        return self.cap.get(param_idx)


    def read(self):
        ret, frame = False, None
        rawSurface = self.nvDec.DecodeSingleSurface()
        if (rawSurface.Empty()):
            print("VPF rawSurface rawSurface.Empty()")
            return ret, frame

        vector = self.cvtNV12_RGB.Execute(rawSurface)
        rawFrameNV12 = np.ndarray(shape=(self.frameSize), dtype=np.uint8)
        success = self.nvDwn.DownloadSingleSurface(vector, rawFrameNV12)
        if not success:
            return ret, frame
        ret = True
        frame = rawFrameNV12.reshape(self.height, self.width, 3)
        del vector, rawSurface
        return ret, frame

class VideoManager():
    def __init__(self, link, gpu_id):
        # self.logger = logger
        cap_cv2 = cv2.VideoCapture(link)
        self.height = int(cap_cv2.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(cap_cv2.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.fps = cap_cv2.get(cv2.CAP_PROP_FPS)
        self.n_video_frames = cap_cv2.get(cv2.CAP_PROP_FRAME_COUNT)
        self.isOpened = cap_cv2.isOpened()
        self.gpu = gpu_id
        self._queue = Queue(int(os.environ.get('VPF_QUEUE', '8')))
        self.link = link
        

    def run_process_get_image(self):
        self.p = Process(target=self._get_frame)
        self.p.start()
        return self.p.pid


    def _get_frame(self):
        VPF = int(os.environ['VPF'])
        if VPF:
            cap =  VPFCapture(self.link, self.gpu)
        else:
            cap = cv2.VideoCapture(self.link) 
        while(True):
            ret, frame = cap.read()
            if not ret:
                self._queue.put((False,-1))
                break
            self._queue.put((ret,frame))
        cap.release()

    def release(self):
        self._queue.close()
        self.p.terminate()
