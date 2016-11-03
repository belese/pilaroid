#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main2.py
#
#  Copyright 2020 belese <belese@belese>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
from collections import OrderedDict
from resources.qrcode import QrCode
from resources.camera import Camera
from resources.attiny import Attiny85
from resources.printer import Printer

from plugins.settings.size import Size
from plugins.settings.camera import CameraSetting
from plugins.settings.printer import PrinterSetting

from plugins.modes.photo import Photo
from plugins.modes.phylactere import Phylactere
from plugins.modes.video import Video
import time

import threading

import signal
import sys

#QRCODE KEY
QRTYPE = 1
ID = 2
OPTION = 3
DATA = 4

#QRCODE VALUE
#QRTYPE
RESET = 0
MODE = 1
SETTING = 1
UPDATE = 2
#OPTION (1,2,3,4)
CUSTOM = 0

qrcode = {'rotation' : 0, 'data' : {QRTYPE : MODE, ID : 2,DATA : { 0 :{}, 1 : {}, 2 :{},3 : {}, 4 :{}}}}

class Main() :

    def __init__(self) :
        self.button = Attiny85()
        self.camera = Camera()
        self.printer = Printer()
        self.modes = {}
        self.modes[0] = Photo(self.button,self.camera,self.printer)
        self.modes[1] = Phylactere(self.button,self.camera,self.printer)
        self.modes[2] = Video(self.button,self.camera,self.printer)
        self.mode = self.modes[0]
        self.settings = OrderedDict()
        self.settings['size'] = Size(self.button,self.camera,self.printer)
        self.settings['camera'] = CameraSetting(self.button,self.camera,self.printer)
        self.settings['printer'] = PrinterSetting(self.button,self.camera,self.printer)
        self.started = False
        self.ready = threading.Lock()
        #self.modelock = threading.Lock()
        self.qrcode_reader = QrCode(self.camera,self.ready)
        self.reprint_photo = None        

    def start(self) :
        self.started = True
        with self.ready :
            self.reset()        
        #self.stop_daemon_t = threading.Thread(target = self.stop_daemon)
        self.qrcode_daemon_t = threading.Thread(target = self.qrcode_daemon)
        self.shutter_daemon_t = threading.Thread(target = self.shutter_daemon)   
        #self.stop_daemon_t.start()
        self.qrcode_daemon_t.start()
        self.shutter_daemon_t.start()        

    def reset(self) :        
        self.mode = self.modes[0]
        #self.mode.reset()
        #for setting in self.settings.values() :
        #    setting.reset()

    def stop(self) :
        self.started = False
        time.sleep(1)
        self.camera.close()
        #self.printer.close()
        self.button.stop()

    def shutter_daemon(self) :
        while self.started :
            print ('Wait a shutter button pressed')
            self.button.wait_press()
            print ('button pressed')
            with self.ready :
                self.mode = self.modes[2]
                print ('main lock acquier')
                photo = self.mode.get_photo()
                press_time = self.button.wait_release(10) 
                if press_time and press_time < 3 or self.mode == self.modes[2]:
                    if photo is not None : 
                        self.reprint_photo = photo                   
                        self.printer.print_img(photo)
                elif press_time and press_time < 10 :
                    if self.reprint_photo is not None :                         
                        self.printer.print_img(self.reprint_photo)
                else :
                    print ('Halt')
                    self.stop()
                    break
                #reset if not photo mode
                if self.mode.reset  :
                    self.reset()      
    
   
    def qrcode_daemon(self) :
        while self.started :
            print ('WAIT A QRCODE')
            qrcode = self.qrcode_reader.get_qrcode()
            print ('WE GOT A QRCODE',qrcode)
            datas = qrcode['data']
            _type = datas.pop('type',None)
            mode = qrcode.get('mode',None)            
            if _type is None or mode is None :
                print ('Bad mode or type',mode,_type)                
                continue
            
            print ('we got mode or type',mode,_type)

            with self.ready :         
                print ('Main qr code lock acquire')       
                if _type == 1 :     
                    self.set_settings(datas)               
                    print ('SET Settings QRCODE')
                elif _type == 2 :
                    settings = datas.pop('settings',None)
                    self.set_settings(settings)
                    self.modes[1].set_options(datas)
                    self.mode = self.modes[1]
                    print ('SET PHYLACTERE QRCODE')
                elif _type == 3 :                    
                    print ('SET story board QRCODE')
                elif _type == 4 :
                    self.mode = self.modes[2]
                    print ('SET Video QRCODE')

            """
            with self.ready :
                if qrcode[QRTYPE] == MODE :
                    self.mode = self.modes[qrcode[ID]]
                    self.mode.set(qrcode[OPTION],qrcode[DATA])
                elif qrcode[QRTYPE] == SETTING :
                    self.settings[qrcode[ID]].set(qrcode[OPTION],qrcode[DATA])
                elif qrcode[QRTYPE] == RESET :
                    self.reset()
            """

    def set_settings(self,options) :
        print ('We set settings',options,self.settings)
        resetCamera = options.pop('global',{}).get('resetcamera',True)
        if resetCamera :
            self.reset()        
        for key, value in options.items() :
            print ('check if',key,'is in',self.settings,key in self.settings)
            if key in self.settings :
                self.settings[key].set_options(value)            
    
    def stop_daemon(self) :
        while self.started :
            info = self.button.wait_release()
            if info('press_time') >= 3 :
                with self.ready :
                    self.halt()

    def halt(self) :
        print ('We want to stop')
        time.sleep(30)

a = Main()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    a.stop()

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
try :
    a.start()
    signal.pause()
except :
    a.stop()
    raise