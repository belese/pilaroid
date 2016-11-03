from collections import OrderedDict
import math
from PIL import Image, ImageDraw,ImageFont
import textwrap
from urllib import unquote
from ..rectangle.rectangle import Rect

def rounded_rectangle(self, xy, corner_radius, fill=None, outline=None):
    upper_left_point = xy[0]
    bottom_right_point = xy[1]
    self.rectangle(
        [
            (upper_left_point[0], upper_left_point[1] + corner_radius),
            (bottom_right_point[0], bottom_right_point[1] - corner_radius)
        ],
        fill=fill,
        outline=outline
    )
    self.rectangle(
        [
            (upper_left_point[0] + corner_radius, upper_left_point[1]),
            (bottom_right_point[0] - corner_radius, bottom_right_point[1])
        ],
        fill=fill,
        outline=outline
    )
    self.pieslice([upper_left_point, (upper_left_point[0] + corner_radius * 2, upper_left_point[1] + corner_radius * 2)],
        180,
        270,
        fill=fill,
        outline=outline
    )
    self.pieslice([(bottom_right_point[0] - corner_radius * 2, bottom_right_point[1] - corner_radius * 2), bottom_right_point],
        0,
        90,
        fill=fill,
        outline=outline
    )
    self.pieslice([(upper_left_point[0], bottom_right_point[1] - corner_radius * 2), (upper_left_point[0] + corner_radius * 2, bottom_right_point[1])],
        90,
        180,
        fill=fill,
        outline=outline
    )
    self.pieslice([(bottom_right_point[0] - corner_radius * 2, upper_left_point[1]), (bottom_right_point[0], upper_left_point[1] + corner_radius * 2)],
        270,
        360,
        fill=fill,
        outline=outline
    )


ImageDraw.rounded_rectangle = rounded_rectangle


STEP = 10
WIDTHMIN = 50
HEIGHTMIN = 30

class Font(object) :
    _font = 'TravelingTypewriter.ttf'
    _size = 28
    font_dir = '/home/pi/pilaroid/resources/assets/fonts/'
        
    def __init__(self,font=None,size=None) :
        self._font = font or self._font
        self._size = size or self._size
        print ('open font',self.font_dir + self._font,self._size)
        self.font = ImageFont.truetype(self.font_dir + self._font,self._size)
        
class Text(object) :

    _text = str
    _font = Font
    
    def __init__(self,data,default_font=None) :
        self.text = self._text(data['text'])
        font = data.get('font',None)
        size = data.get('size',None)
        if font or size :
            self.font = self._font(font,size)
        elif default_font:
            self.font = default_font
        else :
            self.font = self._font()
    
    def getSize(self) :
        return self.font.font.getsize(self.text)


class Actor(object) :
    _name = None
    _alias = None

    def __init__(self,name=None,alias=None) :
        self.name = name or self._name
        self.alias = alias or self._alias

class Dialogs(object) : 
    _text = Text
    _actorid = None

    def __init__(self,data,default_font=None) :
        self.text = self._text(data['text'],default_font)
        self.actorid = data['actor']
    


class Scene(object) :
    _actors = OrderedDict
    _font = Font
    _dialogs = list
    _note = ''
    _narrator = Text
    

    def __init__(self,data,actors=None) :
        self.actors = actors or self._actors()        
        self.font = self._font(data.get('font',{'font' : None,'size' : None}))
        if not actors :
            for actor in data['actors'] :
                self.actors[actor] = Actor()
        
        self.dialogs = self._dialogs()
        for dialog in data['dialogs'] :
            self.dialogs.append(Dialogs(dialog,self.font))
        
        self.note = data.get('Note',self._note)
        self.narrator = data.get('narrator',None)
        if self.narrator :
            self.narrator = self._narrator(self.narrator)

class Bubble(object) :

    def __init__(self,img,faces,scene,border=10) :      
        draw = ImageDraw.Draw(img)
        squares = faces[:]
        if scene.narrator.text :
            rects = self.findNarrator(squares[:],img.size)
            if rects :            
                print ('find narrator',rects)
                square,n = self.getSquareBubble(scene.narrator,rects,(0,0,1,1),img.size,wr=20)
                print ('2222222222222222222222222222 narrator',square,n)
                img.paste(n, (square[0],square[1]))
                faces.append((square[0],square[1],n.size[0]+border,n.size[1]+border))
                squares = faces[:]
            
        #rects = self.findRectangle(squares[:],img.size)      
        level = 0
        found = False 
        bulls = []
        good_bulls = bulls  
        max_level = 5
        while not found and level < max_level:    
            starty = 0                                
            for id_diag,dialog in enumerate(scene.dialogs) :
                min_width, min_height = dialog.text.getSize()
                next_face = faces[scene.dialogs[id_diag +1 ].actorid][:2] if id_diag +1 < len(scene.dialogs) else (0,0)
                rects = self.findRectangle(squares[:],img.size,starty,minheight=min(min_height+20,HEIGHTMIN),minwidth=min(min_width+20,WIDTHMIN))
                if not dialog.text.text :
                    continue                               
                square,bull = self.getSquareBubble(dialog.text,rects,faces[dialog.actorid],img.size,level=level,nextface=next_face)
                print ('find square for ',dialog.text.text,square,bull)
                if square :
                    previous_bull = pos if bulls else (0,0)
                    
                    pos = self.findBestPlace(square,faces[dialog.actorid],previous_bull,bull.size,img.size,nextface=next_face,level=level) 
                    if pos :
                        wb = bull.size[0] + 2 * border
                        wh = bull.size[1] + 2 * border

                        draw.rectangle((square[0],square[1],square[0]+square[2],square[1] +square[3]),fill=None,outline='red')
                        
                        print ('*****************FIND BEST PLACE',(pos[0],pos[1],wb,wh),square)        
                        arrow = self.findArrow(faces[dialog.actorid],(pos[0],pos[1],bull.size[0],bull.size[1]),squares)
                        
                        xb = pos[0] -10 if pos[0] -10 > 0 else 0
                        yb = pos[1] -10 if pos[1] -10 > 0 else 0

                    
                        xarrowmin = int(min(arrow[0][0],arrow[2][0],arrow[1][0]))
                        xarrowmax = int(max(arrow[0][0],arrow[2][0],arrow[1][0]))
                        yarrowmin = int(min(arrow[0][1],arrow[2][1],arrow[1][1]))
                        yarrowmax = int(max(arrow[0][1],arrow[2][1],arrow[1][1]))
                        
                        #xb = max(min(xb,xarrowmin),0)
                        #yb = max(min(yb,yarrowmin),0)

                        print ('Add rectangle',pos,xb,yb,wb,wh,xarrowmin,xarrowmax,yarrowmin,yarrowmax)

                        #wb = wb if xb + wb < xarrowmax else xarrowmax - xb
                        #wh = wh if yb + wh < yarrowmax else yarrowmax - yb                    



                        squares.append((xb,yb,wb,wh))
                        squares.append((xarrowmin-2,yarrowmin-2,xarrowmax-xarrowmin+4,yarrowmax-yarrowmin+4))
                        #if arrow[2][1] >   pos[1] + bull.size[1] + border:
                        #    xr = int(min(arrow[0][0],arrow[2][0]))
                        #    yr = arrow[0][1] + border
                        #    xr2 = int(max(arrow[1][0],arrow[2][0]))
                        #    squares.append((xr,yr,xr2-xr,arrow[2][1]-yr))                    
                        bulls.append((arrow,bull,pos))
                        print ('we append bulls',bulls)
                        #img.paste(bull, pos)    

                        #img.show()            
                        starty = yb+20
                    else :
                        print ('CAN FIND GOOD POSITION',square,bull.size)
                        square = None
                if not square : 
                    print ('**********INCREMENTLEVEL',level,bulls)            
                    level += 1                    
                    if level < max_level:                        
                        squares = faces[:]
                        bulls = []
                    rects = self.findRectangle(squares[:],img.size)
                    #if level == max_level:
                    if len (bulls) > len(good_bulls) :
                        good_bulls = bulls
                    break                                            
            else : 
                good_bulls = bulls
                found = True
                """    
                if level < max_level:
                    copy = img.copy()
                    draw = ImageDraw.Draw(copy)                                
                    for rectangle in rects :
                        draw.rectangle((rectangle[0],rectangle[1],rectangle[0]+rectangle[2],rectangle[1] +rectangle[3]),fill="red",outline='blue')
                    copy.show()            
                """                        
            #else :
            #    found = True
        print ('we have good bull',good_bulls)
        for rectangle in faces :
            draw.rectangle((rectangle[0],rectangle[1],rectangle[0]+rectangle[2],rectangle[1] +rectangle[3]),fill="blue")
                
        for arrow, bull, pos in good_bulls :            
            draw.polygon(arrow,fill="white")
            img.paste(bull, pos)    
        #img.show()                        
        self.img = img


    def findNarrator(self,rects,resolution) :
        rect = self.findRectangle(rects,resolution)
        def key(val) :
            return val[1] == 0
        return filter(key,rect) or rect

    def findRectangle(self,rects,resolution,starty=0,minheight=HEIGHTMIN,minwidth=WIDTHMIN) :
        rects = sorted(rects,key = lambda x : (x[0],x[1]))
        rectangle = []
        lines = self.findLines(rects,resolution)
        lines = lines[starty/STEP:]
        #print ('after',lines)
        for i,line in enumerate(lines) :
            pos = 0
            for j,value in enumerate(line) :
                if value > 0 :
                    up = self.findUp(pos,value,lines[0:i]) if i > 0 else 0
                    down = self.findDown(pos,value,lines[i:]) if i < len(lines) else 0
                    pose = (pos,(i+starty/STEP-up)*STEP,value,(down + up)*STEP)
                    if pose[2] >= minwidth and pose[3] >= minheight :
                        rectangle.append(pose)                
                pos+=abs(value)
        rectangle = set(rectangle)
        def key(val) :
            return (math.sqrt(val[0]*val[0]+val[1]*val[1]),-val[2]*val[3])
        rectangle = sorted(rectangle,key=key)
        print ('we have rectangles',rectangle)
        return rectangle

    def findLines(self,rects,resolution) :
        lines = []
        for line in range(0,resolution[1],STEP) :
            lines.append([])
            pos = 0
            for rect in rects :
                if line in range(rect[1],rect[1]+rect[3]) :
                    delta=0
                    if rect[0] + rect[2] < pos :
                        continue
                    if rect[0] >= 0 :                        
                        if (rect[0] - pos) > 0 :
                            lines[line/STEP].append(rect[0] - pos)                       
                        else : 
                            lines[line/STEP].append(0)
                        if rect[0] > pos :
                            pos=rect[0]                            
                            lines[line/STEP].append(-rect[2])
                        else :
                            delta = pos - rect[0]
                            lines[line/STEP][-1]=lines[line/STEP][-1]-rect[2]+delta

                    pos+=rect[2]-delta            
            lines[line/STEP].append(resolution[0] - pos)
        return lines

    def isinrect(self,start,lenght,line) :
        pos = 0
        for i,val in enumerate(line) :
            pos += abs(val)
            if start < pos :
                if val < 0 :
                    return True
                if start + lenght <= pos :
                    return False


    def findDown(self,start,lenght,lines) :
        for i,val in enumerate(lines) :
            if self.isinrect(start,lenght,val) :
                return  i
        return len(lines)

    def findUp(self,start,lenght,lines) :
        lines.reverse()
        return  self.findDown(start,lenght,lines)

    def findArrow(self,face,bull,bulls=[],border = 40,larger=40) :        
        xf,yf,wf,hf = face
        xb,yb,wb,hb = bull
        xc = xf + wf/2
        yc = yf + hf/2

        #larger = larger if larger < wb else wb -16
        #border = border if larger + 2* border < wb else (wb - larger) / 2

        print ('find arrow position',xb,wb,yb,hb,xf,wf,yf,hf)

        #todo check with x instead
        #if yb + hb < yf + 20 or yb > yf + hf - 20 :
        if (xf > xb and xf < xb + wb) or (xf + wf > xb and xf +wf < xb + wb)  or (yb + hb < yf) or (yb > yf + hf) :
            print ('arrow top or bottom')
            
            larger = larger if larger + 16< wb else wb -16
            border = border if larger + (2* border) +16 < wb else (wb - larger -16 ) / 2
            
            #top or bottom
            if (( yb + hb < yf - larger ) or (yb > yf + hf + larger)) : 
                print('center max',wf,xf-xb,xb+wb-xf-wf)
                if max(wf,xf-xb,xb+wb-xf-wf) == xf-xb :
                    #left center arrox
                    x1 = xf - border
                    x0 = x1 - larger
                elif max(wf,xb+wb-xf-wf) == wf  :
                    #center arrow
                    x0 = xc - larger/2
                else :
                    x0 = xf + wf + border
                

                x0 = xb + border +8 if x0 - border - 8 < xb else x0
                x0 = xb + wb - border -larger -8 if x0 + larger + border +8 > xb + wb else x0
                if yb  > yf :    
                    upbulls = filter(lambda bull : (bull[1] + bull[3] > yb - larger) and (xb in range(bull[0],bull[0] + bull[2]) or xb + wb in range(bull[0],bull[0] + bull[2])),bulls)
                    print ('6666666666666666 we have upbulls',upbulls)
                    if upbulls :
                        x0_min = xb + 8
                        x1_max = xb + wb - 8
                        for upbull in upbulls  :                      
                            if xb + 8 + larger < upbull[0] :
                                print ('upbull 0',xb,upbull[0])
                                x1_max = min(upbull[0],x1_max) 
                            elif upbull[0] + upbull[2] < xb + wb - 8 - larger  :
                                print ('upbull 1',x0,xb,wb,upbull[0],upbull[1])                                
                                x0_min = max(upbull[0] + upbull[2],x0_min)                                                              
                            else :
                                print ('we cant do nothing',xb,wb,upbull[0] + upbull[2])
                                if xb < upbull[0] :
                                    x0 = xb + 8
                                    larger = upbull[0] - x0 + 6
                                elif xb + wb > upbull[0] + upbull[2] :
                                    x0 = upbull[0] + upbull[2] -6
                                    larger = xb + wb - x0 -8
                                else : 
                                    larger = yb - upbull[1] - upbull[3] + 10
                                print ('new larger',larger)
                                break
                        else : 
                            print ('doing range',x0_min,x1_max,x0)  
                            if not (x0 > x0 and x0 + larger < x1_max) :
                                larger = min(larger,x1_max - x0_min)
                                if x0 < x0_min and  x0 + larger < x1_max:
                                    x0 = x0_min
                                elif x0 + larger > x1_max and x0 > x0_min :
                                    x0 = x1_max -larger
                                else :
                                    x0 = x0_min + (x1_max - x0_min - larger) / 2
                                
                x1 = x0 + larger
            elif (xf - xb > xb + wb - (xf + wf)) or (xb + wb < xf) :
                print('left')
                #right
                x0 = xf - larger
                x0 = x0 if x0 + larger < xb + wb - border -8 else xb + wb - border - larger - 8
                x0 = x0 if x0 > xb + border +8  else xb + border +8
                x1 = x0 + larger                
            else :                
                print('right')
                x1 = xf + wf + larger
                x1 = x1 if x1  < xb + wb - border -8 else xb + wb - border -8
                x1 = x1 if x1 > xb + border + 8 else xb + border + 8
                x0 = x1 - larger

            x = x0 + (x1 - x0)/2

            if yb  < yf :
                #top
                print ('top')
                y0 = yb + hb
                y1 = y0
                angle = math.atan2(yc-y0,xc-x)
                yprim = int(math.sin(angle) * larger)
                y2 = yb + hb + yprim
            else :
                print ('bottom',larger)
                y0 = yb
                y1 = y0
                angle = math.atan2(y0-yc,xc - x)
                yprim = int(math.sin(angle) * larger)
                y2 = yb - yprim
            print angle
            xprim = int(math.cos(-angle) * larger)
            x2 = x + xprim

        else :
            #right or left
            
            larger = larger if larger +16 < hb else hb -16
            border = border if larger + (2* border) + 16 < hb else (hb - larger - 16) / 2
            
            yc= yf + 2*hf/3
            y0 = yc - larger/2
            y0 = yb + border + 8 if y0 < yb +border + 8 else y0
            y0 = yb + hb - border - larger -8 if y0 >yb + hb - larger - border -8 else y0
            y1 = y0 + larger
            y = y0 + (y1 - y0)/2
            if xb  <= xf :
                #left
                print ('***************arrow left')
                x0 = xb + wb
                x1 = x0
                angle = math.atan2(xc-x0,yc-y)
                xprim = int(math.sin(angle) * larger)
                x2 = xb + wb + xprim
            else :
                x0 = xb
                x1 = x0
                angle = math.atan2(x0-xc,yc-y)
                xprim = int(math.sin(angle) * larger)
                x2 = xb  - xprim
            yprim = int(math.cos(-angle) * larger)
            y2 = y + yprim

        return ((x0,y0),(x1,y1),(x2,y2))

    def findBestPlace(self,rect,face,previous_bull,bull,resolution,nextface=(0,0),level=0) :
        print ('rect = ',rect)
        xr,yr,wr,hr = rect
        xf,yf,wf,hf = face
        xp,yp = previous_bull
        wb,hb = bull
        xn,yn = nextface

        top = False
        left = False
        right = False

        #top
        if yf >= yr + hr :
            top = True

        if xf >= xr + wr :
            left = True

        if xf + wf <= xr :
            right = True
        
        if left or right :            
            y = yf - hb/2
            y = max(y,yr)
            y = y if y + hb <= yr + wr else yr + hr - hb            
            if left :
                x = max(xf - wb - 20,xr)                
            else :
                x = max(xf + wf + 20,xr)                
        else :            
            #if xf <= resolution[0]/2 :                                
            if xf <= xn :
                x = xf -wb                
                x = max(x,xr)
                x = x if x + wb <= xr + wr else xr + wr - wb

            else :                                
                x = xf                
                x = max(x,xr)
                x = x if x + wb <= xr + wr else xr + wr - wb                
            if top :
                y = yr + hr/3 - hb/2 - 20                                
                #y = y - (((y-yr)/2) * level)
                y = max(y,yr)
                y = y if y + hb <= yr + hr else yr
            else :
                y = yr + hb/3
                y = y if y + hb < yr + hr else yr + hr/2 - hb/2


        if not((xf > x and xf < x + wb) or (xf + wf > x and xf +wf < x + wb)  or (y + hb < yf) or (y > yf + hf)) :
            print ('-------------------------------------------------------WE ARE arrow left or right')
            if x  > xf :
                print ('-------------------------------------------------------WE ARE arrow left')
                x = x + 40     
            else :
                if x + wb + 40 < xf :
                    x = xf - 40 - wb

        print ('decrement y for level',y,rect[1])
        if y > yr :
            print ('decrement x for level',level,int((float(y - rect[1])/3.0 * level)))
            y-=int( (float(y - yr)/1.2) * level)
        print ('decremented y for level',y,rect[1])

        print ('55555555555555555555555555555555555555555555555555555555555555555555555 i check to down right bull',xp,x,y,yp)
        
        y = y +(10 - (2*level)) if (xp and x > xp) or (y +(10 - (2*level)) < (yp + (80 - (level * 16)))) else  yp + (80 - (level * 16))
        #y = y + 10 if (xp and x > xp) else y
        print ('after check',y,yp,level)

        x = x if x > rect[0] else rect[0]
        y = y if y > rect[1] else rect[1]
        x = x if x + wb < rect[0] + rect[2]  else rect[0] + rect[2]  - wb        
        y = y if y + hb < rect[1] + rect[3] else rect[1] + rect[3] - hb
        y = y if y + hb + 5 < resolution[1] else resolution[1] - hb - 5

        
        print ('x',x + wb,rect[0] + rect[2])
        #if x < rect[0] or y < rect[1] or (x + wb) > (rect[0] + rect[2]) or (y + hb) > (rect[1] + rect[3]):
        #    return None
        

        return (x,y)

    def getSquareBubble(self,text,square,face,resolution,wr=7,hr=3,level=0,nextface=(0,0)) :
        print 'getSquareBubble',square
        center = (face[0]+face[2]/2,face[1]+face[3]/2)
        text_size = text.getSize()
        area = (text_size[0]*1.4) * (text_size[1]*1.5)
        squares = filter(lambda x: (x[2] * x[3]) >= area,square)

        _face = Rect(*face)
        if not squares :
            print ('We have no square')
            return None,None
        else :  
            
            def keysort(value) :                
                
                x,y,w,h = value                
                proximity = _face.distance_to_rect(Rect(*value))
                        
                proximity = 2*proximity
                top_w = y/2 * (1+level)
                left_w =  (x/100) * (1+level) if nextface[0] < face[0] else (x/10) * (1+level)
                width_w = max((8-level),0) * (text_size[0]-w) if text_size[0]/2-w > 0 else 0
                
                weight = proximity + top_w + left_w + width_w
                print ('Square weidht ({},{},{},{}) - level : {}, prowimity : {}, top : {}, left : {}, width : {} : {}'.format(x,y,w,h,level,proximity,top_w,left_w,width_w,weight))
                print text_size[0],w
                
                return weight

            squares = sorted(squares,key=keysort)
            
            for square in squares :
                bull = self.getBullText(square,text,hr,wr+level)
                if bull :
                    break                
            if not bull :
                return None,None                
            return square,bull
        

    def getBullText(self,square,text,hr=3,wr=7) :
            text_size = text.getSize()
            x,y,w,h = square
            area = text_size[0] * text_size[1]
            words = text.text.split(' ')
            #ideal width
            width = int (math.sqrt(area * (float(wr)/hr)))
            width = min(width,w)
            texts = []                                    
            idWord = 0
            max_width = 0
            heigth = 0
            
            while idWord < len(words) :

                texts = []
                heigth = 0
                max_width = 0
                idWord = 0                
                print ('444444444444444444444444444444444444444444444444444444444 Get bull text',area,text_size,width,wr,w)
                while idWord < len(words) :            
                    line = ''
                    while idWord < len(words) and text.font.font.getsize(line + words[idWord])[0] +20 <= width :            
                        line = line + words[idWord] + " "
                        idWord +=1                    
                    if not line :
                        if width + wr <= w :
                            width += wr
                            print ('Line too small for word :{} - increade wr'.format(words[idWord]))
                            idWord = 0
                            break
                        else :                        
                            return None
                    
                    #try to not let a single word on last line
                    if idWord == len(words) and width + wr <= w and len(words) > 1 : 
                        width += wr
                        print ('#try to not let a single word on last line')
                        idWord = 0
                        break
                    
                    line = line[:-1]
                    print ('We have a new line',line)
                    line_size = text.font.font.getsize(line)
                    heigth += line_size[1]
                    if heigth +20 > h :
                        if width + wr <= w :
                            print ('Height too small for text - increade wr')
                            width += wr
                            idWord = 0
                            break
                        else :                        
                            return None

                    max_width = max(max_width,line_size[0] + 20)                    
                    texts.append(line)
                print ('we have finished ')
            
            heigth+=20
                        
            bull_img = Image.new('RGBA', (max_width,heigth))            
            
            bull_draw = ImageDraw.Draw(bull_img)
            rounded_rectangle(bull_draw,((0,0),(max_width,heigth)), 8,fill='white')
            #bull_draw.rounded_rectangle()
            y=10
            x=10
            for line in texts  :
                bull_draw.text((x, y), line, font=text.font.font,fill="black")
                y+= text.font.font.getsize(line)[1]                                        
            return bull_img

    
class synopsys(object) :
    _title = Title
    _actors = []
    _dialogs = []
    _font = Font
    _note = ''

    def __init__(self,synopsys) :
        self.font = self._font(synopsys.get('font',{'font' : None,'size' : None}))
        self.actors = synopsys.get('actors',self._actors)
        self.dialogs = []
        dialogs = synopsys.get('dialogs',self._dialogs)
        for dialog in dialogs :
            self.dialogs.append()
        self.title = Title(synopsys.get('title',None),self.font)

class Title(object) :
    _title = Text

    def __init__(self,text,default_font=None) :
        self.title = self._title(text,default_font)
        
    def getImage(self,img) :
        words = self.title.text.split(' ') 
        lines = []
        line = ""                
        for word in words :
            n = line
            line += " " + word
            size = self.title.font.font.getsize(line)[0]
            if  size + 20 > img.size[0] :
                lines.append((n,size))
                line = ""
        if line :
            lines.append(line)
        height = 0
        width = 0
        for line in lines :
            height += line[1][1]
            width = max(width,line[1][0])
            
        y = (img.size[1] - height) / 2    
                
        title_img = Image.new('RGBA', img.size)                        
        title_draw = ImageDraw.Draw(title_img)        
        for line in lines  :
            size = self.title.font.font.getsize(line)[1]
            x = (img.size[0] - size[0]) / 2
            bull_draw.text((x, y), line, font=self.title.font.font,fill="black")
            y+= self.title.font.font.getsize(line)[1]
        img.paste(title_img, (0.0))
        return img

if __name__ == '__main__' :
    import time
    data = {
        'actors' : [0],
        'dialogs' : [{'text' : {'text' : 'Hello, ca va?!'}, 'actor' : 0},{'text' : {'text' : 'Bonjour, bien et toi?'}, 'actor' : 1},{'text' : {'text' : 'Il pleut pas mal today'}, 'actor' : 0},{'text' : {'text' : ' Cucurbitacee !'}, 'actor' : 2}]#,{'text' : {'text' : 'hello world 5!'}, 'actor' : 1},{'text' : {'text' : 'hello world 6!'}, 'actor' : 0}]#,{'text' : {'text' : 'hello world 7!'}, 'actor' : 2},{'text' : {'text' : 'hello world 8!'}, 'actor' : 0}]
    }

    qrcode = {
    "actors":[0,1,2],
    "dialogs":[{
        "text":{
            "text":"Bonjour, Comment allez vous?",
            "font":"GrandHotel.otf",
            "size":28
            },
        "actor":1
        },{
            "text":{
                "text":"Tres tres bien et vous?",
                "font":"Airstream.ttf",
                "size":28
            },
        "actor":0
        },{
            "text":{
                "text":"mega Top !",
                "font":"traveling-_typewriter.ttf",
                "size":36
            },
            "actor":1
        },{
            "text":{
                "text":"Et sinon?",
                "font":"Daniel.otf",
                "size":28
            },
            "actor":2
        },{
            "text":{
                "text":"Barbecue alors!",
                "font":"CaviarDreams.ttf",
                "size":28
            },
            "actor":1
        },{
            "text":{
                "text":"Surement!",
                "font":"CaviarDreams.ttf",
                "size":28
            },
            "actor":0
        },{
            "text":{
                "text":"Surement encore les allemands!",
                "font":"CaviarDreams.ttf",
                "size":28
            },
            "actor":1
        },{
            "text":{
                "text":"Surement!",
                "font":"CaviarDreams.ttf",
                "size":28
            },
            "actor":2
        }],
    "note":{
        "text":"",
        "font":None,
        "size":None
    },
    "narrator":{
        "text":"Un jour a paris",
        "font":"CaviarDreams.ttf",
        "size":36
    },
    "font":{
        "font":None,
        "size":None
    }}

    scene = Scene(qrcode)    
    img = Image.new('RGB', (640,383),)
    faces = [[100,100,100,100],[289,156,110,105],[501,52,104,111]]
    bubble = Bubble(img,faces,scene)    
    bubble.img.show()
    copy = img.copy()
    draw = ImageDraw.Draw(copy)            
    offset = 0   
    exit(0)                     
    while True :
        for rectangle in faces :
            draw.rectangle((rectangle[0],rectangle[1],rectangle[0]+rectangle[2],rectangle[1] +rectangle[3]),fill='green',outline='red')
        rects = bubble.findRectangle(faces,img.size,offset)
        for rectangle in rects :
            draw.rectangle((rectangle[0],rectangle[1],rectangle[0]+rectangle[2],rectangle[1] +rectangle[3]),fill=None,outline='blue')
        square,bull = bubble.getSquareBubble(scene.dialogs[0],rects,faces[0],img.size,level=0)        
        draw.rectangle((square[0],square[1],square[0]+square[2],square[1] +square[3]),fill='white',outline='black')
        #draw.rectangle((bull[0],bull[1],bull[0]+bull[2],bull[1] +bull[3]),fill=None,outline='black')
        
        faces.append(map(lambda x: x+20,square))
        offset = square[1] + 20
        copy.show()   
        copy = img.copy()
        draw = ImageDraw.Draw(copy)  
        time.sleep(2)                              
    


