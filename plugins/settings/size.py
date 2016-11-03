from . import Setting

from PIL import Image


class Size(Setting) :

    default_size = (576, 384)
    _size = default_size

    @property
    def size(self) :
        return self._size
    
    @size.setter
    def size(self,value) :
        print('SIZE SETTER')
        self._size = value        
        self.camera.setSetting('resize',value)
        print ('set camera resize',self.camera.resize,value)
    
    def post_setting(self,photo) :
        #return photo.resize(self.size, Image.ANTIALIAS)
        pass
                    
    def set_options(self,options) :
        if 'width' in options :
            self.size = (options['width'],384)
            print ('We have set size to',self.size,self.camera.resize)
        else :
            print ('Unvalid options',options)
    
    def reset(self) :
        self.size = self.default_size