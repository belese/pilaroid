import Queue
from lz4 import compress, decompress, compress_fast
import psutil
import threading

import picamera
import picamera.array

from PIL import Image, ImageOps

LOW_MEMORY = 50 * 1024 * 1024


class recorder(picamera.array.PiRGBAnalysis) :

    format = 'rgb'

    def __init__(self,camera):
        super(recorder,self).__init__(camera)
        self.queue = Queue.Queue()
        self.nb_image = 0
        self.finished = threading.Event()
        self.resolution = camera.resolution
        self.stopped = False
        self.id_image = 0
    
    def analyse(self,frame) :  
    #def write(self,frame) :
        print ('write image',self.nb_image,self.resolution)
        #if (self.nb_image+1) % 100 != 0 or psutil.virtual_memory()[1] > LOW_MEMORY:   
        img = Image.frombuffer('RGB', self.resolution, frame, "raw", 'RGB', 0, 1)
        img = img.convert('L')
        self.queue.put(img)   
        #img.save ('frame {}.jpeg'.format(self.nb_image))         
        self.nb_image += 1            
    
    def read(self):
        if self.queue.empty() :
            return None
        rc = self.queue.get()
        self.queue.task_done()        
        return rc
        #return rc

    def flush(self) :
        self.finished.set()
    
    def stop(self) :
        self.stopped = True
    
    def getImage(self) :
        self.finished.wait() 
        return None