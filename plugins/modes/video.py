from . import Mode

from resources.libs.video.slitscan import ScanMode,ScanModeFix,ScanModeLive


class Video(Mode) :

    SLITSCAN_FIX = 1  #append middle(s) line(s) of each video frame to final photo
    SLITSCAN_SCAN = 2 #append line(s) in x + 1 for each video frame to final photo
    SLITSCAN_LIVE = 3 #print middle line live on printer for each video frame
    LONG_EXPOSURE = 4 #stack all frame on one image

    recorder = None
    options = {}

    def get_photo(self) :        
        framerate = self.options.get('framerate',None)
        mode = self.options.get('mode',self.SLITSCAN_FIX)
        recorder = self.select_recorder(mode)
        self.camera.start_recording(recorder,framerate=framerate)
        self.button.wait_release()
        return self.camera.stop_recording()        
    
    def select_recorder(self,mode) :
        recorder = None
        if mode == self.SLITSCAN_FIX :
            recorder = ScanModeFix
        elif mode == self.SLITSCAN_SCAN :
            recorder = ScanMode
        elif mode == self.SLITSCAN_LIVE :
            recorder = ScanModeLive
        elif mode == self.LONG_EXPOSURE :
            #recorder = LongExposure(self.camera.resolution)
            pass
        return recorder
        

    def set_options(self,options) :
        print ('set video options',options)
        self.options = options