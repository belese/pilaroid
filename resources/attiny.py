import time
import smbus
import threading

ATTINY_SLAVE_ADDR = 10

class Attiny85 :    
    def __init__(self) :
        self.bus = smbus.SMBus(1)
        self.voltage = 0
        
        self.started = True
        self.start_press = 0
        self.stop_press = 0        
        self.on_press = threading.Event()        
        self.on_release = threading.Event()
        self._has_been_pressed = False
        if self.command(0x03)[0] :
            self.on_press.clear()
            self.on_release.set()
        else :
            self.on_press.set()
            self.on_release.clear()
            self.start_press = time.time()
        self.thread = threading.Thread(target=self.wait_event)
        self.thread.start()

    def stop(self) :
        self.started = False
    

    def command(self,command):    
		data = []
		ok = False
		while not ok :
			try :        
			   self.bus.write_byte(ATTINY_SLAVE_ADDR,command)
			   start = self.bus.read_byte(ATTINY_SLAVE_ADDR)                     
			   dat = self.bus.read_byte(ATTINY_SLAVE_ADDR)	
			   while dat != 0xFF :
					data.append(dat)
					dat = self.bus.read_byte(ATTINY_SLAVE_ADDR)        					
			except IOError :
				print ('communication error')           
				time.sleep(0.1)
			else :
				if start == 0xDE :
					ok = True
		return data
            
    def wait_event(self) :
        while self.started :
            data = self.command(0x03)
            if not data[0] and not self.on_press.isSet() :                                
                self.onPressed()                
            elif data[0] and self.on_press.isSet() :
                self.button = False                
                self.onReleased()
            time.sleep(0.1)
        if self.on_press.isSet :
            self.onPressed()
        else :
            self.onReleased()

    
    @property
    def has_been_pressed(self) :
        try :
            return self._has_been_pressed
        finally :
            self._has_been_pressed = False

                        
    def onPressed(self) :    
        print ('OnPRESSED')    
        self._has_been_pressed = True
        self.start_press = time.time()        
        self.on_release.clear()
        self.on_press.set()        
    
    def onReleased(self) :
        print ('OnRELEASE')    
        self.stop_press = time.time()
        self.on_press.clear()
        self.on_release.set()        
    
    def wait_press(self) :        
        self.on_press.wait()        
    
    def wait_release(self,timeout=None) :
        if self.on_release.wait(timeout=timeout) :
            return self.stop_press - self.start_press
        else :
            return None

if __name__ == '__main__' :
    attiny = Attiny85()
    while True :
        print attiny.wait_press()
        print attiny.wait_release()