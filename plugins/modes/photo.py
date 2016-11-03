from . import Mode


class Photo(Mode) :

    reset = False

    def get_photo(self) :
        return self.camera.image
