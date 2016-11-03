import threading
from libs.thermal import ThermalPrinter

class Printer() :

    lock = threading.Lock()

    def __init__(self) :
        self.printer = ThermalPrinter("/dev/serial0", 9600, timeout=1)

    @property
    def settings(self) :
        class Proxy :                        
            def __setattr__(s,key,value) :
                with self.lock :
                    setattr(self.printer,key,value)

            def __getattribute__(s,key) :
                with self.lock :
                    return getattr(self.printer,key)
        
        return Proxy()
    
    def setSetting(self,key,value) :
        with self.lock :
            setattr(self.printer,key,value)
    
    def print_img(self,img) :
        with self.lock :
            img.save('printed.jpeg')
            #self.printer.printImage(img)

    def print_txt(self,lines) :
        with self.lock :
            pass

    def stream_img(self,streamer) :
        with self.lock :
            pass


if __name__ ==  '__main__' :
    a = Printer()
    from PIL import Image

    b = Image.open("file0.jpeg")
    a.printer.printImage(b)
