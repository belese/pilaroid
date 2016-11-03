from . import Setting

from PIL import Image


class CameraSetting(Setting) :

    default_settings = {
        'saturation' : 0,
        'contrast' : 0,
        'brightness' : 0,
        'sharpness' : 0,
        'iso' : 0,
        'historize' : True
    }    

    
    def post_setting(self,photo) :
        #return photo.resize(self.size, Image.ANTIALIAS)
        pass
                    
    def set_options(self,options) :
        for option, value in options.items() :
            if option in self.default_settings :                
                print ('set {} to {}'.format(option,value)) 
                self.camera.setSetting(option,value)
            else :
                print ('Invalid options',option)
    
    def reset(self) :
        self.set_options(self.default_settings)