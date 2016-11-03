import time
import json
import threading
from libs.pyzbar import pyzbar


JAVASCRIPT_KEYS = {
    'settings' : 1,
    'scene' : 2,
    'story' : 3,
    'title' : 4,    
    'actors' : 5,
    'font' : 6,
    'size' : 7,
    'icon' : 8,
    'note' : 9,
    'scenes' : 10,
    'video' : 11,
    'fps' : 12,
    'text' : 13,
    'dialogs' : 14,
    'narrator'  : 15,
    'resetcamera' : 16,
    'actor' : 17,
    'alias' : 18,
    'width' : 19,
    'camera' : 20,
    'printer' : 22,
    'global' : 23,
    'type' : 24,
    'brightness' : 30,
    'contrast' : 32,
    'historize' : 33,
    'iso' : 34,
    'saturation' : 35,
    'sharpness' : 36,    
    'dots' : 37,
    'heattime' : 38, 
}

KEYS = {str(value) : key for key,value in JAVASCRIPT_KEYS.items()}

def uncompress(inObject) :
    if not (isinstance(inObject,dict) or isinstance(inObject,list)) :
        return  inObject
    
    outObject = {} if isinstance(inObject,dict) else []
    
    for key in inObject :        
        if isinstance(inObject,dict) :
            value = uncompress(inObject[key])
            textkey = KEYS.get(key,key)
            outObject[textkey] = value
        else :
            value = uncompress(key)
            outObject.append(value)
    return outObject





class QrCode(object) :    
    def __init__(self,camera,readyLock) :
        self.camera = camera        
        self.started = True
        self._rawdata = None
        self._data = None
        self._orientation = None
        self._mode = None
        self._qrcode = threading.Event()     
        self._qrcodereaded = threading.Event()        
        self._qrcodereaded.set()
        self.last_qrcode_time = 0
        self.lock = readyLock   
        self.thread = threading.Thread(target=self.wait_event)
        self.thread.start()
                
    def close(self) :
        self.started = False
        self._rawdata = None
        self._data = None
        self._orientation = None
        self._mode = None
        self._qrcode.set()

    
    def get_orientation(self,points) :
        delta_x = points[0].x - points[1].x
        delta_y = points[0].y - points[1].y

        if abs(delta_x) > abs(delta_y) :
            orientation = 1 if delta_x >= 1 else 2                        
        else :
            orientation = 1 if delta_y >= 3 else 4
    
    
    def wait_event(self) :
        value = {}                    
        last_multi_qrcode = 0
        for picture in self.camera.photos(resize=None,historise=False) :
            
            if not self.started :
                break
            self._qrcodereaded.wait()
            with self.lock :
                print ('QRcode acquire lock')
                qrcodes = pyzbar.decode(picture)  

            if last_multi_qrcode + 15 < time.time() :
                value = {}          
                
            print ('QRcode release lock')
            for qrcode in qrcodes :

                if qrcode.type != 'QRCODE' or qrcode.data[0] != '#' :
                    continue
                #check orientation
                #points = qrcode.polygon

                idqrcode, totalqrcode, qrcodedata = qrcode.data[1:].split('#')
                idqrcode = int(idqrcode)
                totalqrcode = int(totalqrcode)
                printMode = int(qrcodedata[0])
                qrcodedata = qrcodedata[1:]
                print idqrcode, totalqrcode, printMode, qrcodedata
                                    
                if totalqrcode > 1 :
                    if not idqrcode in value :
                        print ('buzz one time')
                    last_multi_qrcode = time.time()
                    
                value[idqrcode] = qrcodedata
                if len(value) == totalqrcode :                    
                    jsondata = ""
                    for i in range(totalqrcode) :
                        jsondata += value[i]
                    value = {}                    
                    orientation = 0 if totalqrcode > 1 else self.get_orientation(qrcode.polygon)                    
                    self.onQrcode(printMode,orientation,jsondata)                    
                    break            
            if not value :
                time.sleep(0.2)            
                                    
    
    def onQrcode(self,mode,orientation,data) :      
        if self.last_qrcode_time + 5 < time.time() or mode != self._mode or orientation != self._orientation or data != self._rawdata :
            self.last_qrcode_time = time.time()            
            self._rawdata = data
            self._data = uncompress(json.loads(data))
            self._orientation = orientation
            self._mode = mode
            print ('buzz two time')
            self._qrcodereaded.clear()
            self._qrcode.set()
                    
    
    def get_qrcode(self) :        
        self._qrcode.wait()
        try :
            return {'orientation' : self._orientation, 'data' : self._data, 'mode' : self._mode}
        finally :                        
            self._qrcode.clear()            
            self._qrcodereaded.set()
            
    
    @property
    def qrcodes(self) :
        while self.started :
            yield self.get_qrcode()
    
    @property
    def qrcode(self) :
        return self.get_qrcode()

if __name__ == '__main__' : 
    import signal, sys
    from camera import Camera
    
    camera = Camera()   
    qrcode = QrCode(camera)

    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        qrcode.close()
        camera.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    
    try :
        for qr in qrcode.qrcodes :
            print qr
    finally :    
        qrcode.close()
        camera.close()