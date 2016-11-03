from . import Setting

from PIL import Image


class PrinterSetting(Setting) :

    default_settings = {        
        'dots' : 12, 
        'heattime' : 155,
        'heatinterval' : 200       
    }    
    
    def post_setting(self,photo) :
        #return photo.resize(self.size, Image.ANTIALIAS)
        pass
                    
    def set_options(self,options) :
        for option, value in options.items() :
            if option in self.default_settings :
                print ('set {} to {}'.format(option,value)) 
                self.printer.setSetting(option,value)
            else :
                print ('Invalid options',option)
    
    def reset(self) :
        self.set_options(self.default_settings)