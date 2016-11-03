
import cv2
import numpy
from PIL import Image

from . import Mode
from resources.libs.bubble.bubble import Bubble, Scene

SMALLWIDTH = 120.0
face_cascade = cv2.CascadeClassifier('/home/pi/pilaroid/resources/assets/cascade/haarcascade_frontalface_alt2.xml')
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))


class Phylactere(Mode) :

    scene = None

    def get_photo(self) :                
        if not self.scene :
            print ('We shouldnt pass here, scene must be initiliased before photo')
            return None
        #clear shutter button pressed
        #TODO run find face in thread to better handling cancelation
        self.button.has_been_pressed
        for image in self.camera.photos() :                                      
            faces = self.find_faces(image)            
            if self.button.has_been_pressed :
                return None       
            if faces :
                print ('find faces',faces)
                if len(faces) == len(self.scene.actors) :
                    return Bubble(image,faces,self.scene).img
                                    
    def set_options(self,options) :
        print ('self phylactere options',options)
        self.scene = Scene(options)

    def find_faces(self,img) :
        image_scale =  SMALLWIDTH /img.width
        res = (int(img.size[0]*image_scale),int(img.size[1]*image_scale))
        print ('faceImgage traitement')
        image = cv2.cvtColor(numpy.array(img.convert('RGB')),cv2.COLOR_RGB2GRAY)         
        image = cv2.resize(image,res) 
        #image = clahe.apply(image)
        print ('faceImgage detection')
        faces = face_cascade.detectMultiScale(image,scaleFactor=1.1, minNeighbors=3,flags=cv2.cv.CV_HAAR_DO_CANNY_PRUNING,minSize = (10,10))
        if len(faces) > 0 :
            faces = map(lambda x : [(int(x[0]/image_scale) + 9)/ 10 * 10,(int(x[1]/image_scale)+9) / 10 *10,(int(x[2]/image_scale) +9 )/10 *10,(int(x[3]/image_scale)+9)/10*10],faces)
        return sorted(faces,key = lambda x : x[0])




    
