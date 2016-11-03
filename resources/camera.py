import time
import io
import threading 

import picamera
from PIL import Image, ImageEnhance, ImageOps


class Camera() :
   
    def __init__(self,*args,**kwargs) :
        self.started = True
        self.lock = threading.Lock()
        self.camera = picamera.PiCamera()
        self.resize = None
        self.historise = True
        self._framerate = None
        self.recorder = None
        

    def close(self) :
        with self.lock :
            self.camera.close()
    
    @property
    def image(self) :
        return self.photo()
    
    @property
    def settings(self) :
        class Proxy(object) :            
            
            def __setattr__(s,key,value) :
                with self.lock :
                    setattr(self.camera,key,value)

            def __getattribute__(s,key) :
                with self.lock :
                    return getattr(self.camera,key)
        
        return Proxy()
    
    def setSetting(self,key,value) :
        with self.lock :
            if key in ('resize','historize') :
                setattr(self,key,value)
            else :
                setattr(self.camera,key,value)


    def photo(self,*args,**kwargs) :
        return next(self.photos(*args,**kwargs))
    
    def photos(self,*args,**kwargs) :
        resize = kwargs.pop('resize',self.resize)
        img_format = kwargs.pop('format','pil')
        historise = kwargs.pop('historise',self.historise)   
        while self.started :            
            stream = io.BytesIO()   
            with self.lock : 
                self.camera.capture(stream, format='jpeg' if img_format == 'pil' else img_format,resize=resize,**kwargs)                
            stream.seek(0)
            if img_format == 'pil' :
                img = Image.open(stream)
                if historise :
                    #img = ImageOps.equalize(img)
                    img = ImageOps.autocontrast(img)
                print ('before yield')                    
                yield img
                print ('after yield')
            else :
                yield  stream
    
    def start_recording(self,recorder,framerate=None,**kwargs) :
        format = recorder.format
        self.recorder = recorder(self.camera)
        if framerate :
            self._framerate = self.camera.framerate
            self.camera.framerate = framerate
        self.lock.acquire()
        self.camera.start_recording(self.recorder,format=format,**kwargs)
    
    def stop_recording(self) :
        self.camera.stop_recording()
        if self._framerate : 
            self.camera.framerate = self._framerate
            self._framerate = None
        self.lock.release()
        return self.recorder.getImage()
                
if __name__ == '__main__' :
    camera = Camera()
    camera.image.save('file_main.jpeg')
    try :   
        i = 0     
        for picture in camera.photos() :
            picture.save('file{}.jpeg'.format(i))
            i+=1
    except :
        raise
    finally :
        camera.close()



        
