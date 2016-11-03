class Setting(object) :

    def __init__(self,button,camera,printer) :
        self.button = button
        self.camera = camera
        self.printer = printer

    def set_options(self,options) :
        pass

    def post_setting(self,photo) :
        return photo

    def add_overlay(self,photo) :
        return photo

    def reset(self) :
        pass

class Mode(Setting) :

    reset = True

    def get_photo(self) :
        return None