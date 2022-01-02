#!/bin/env python3

import os
import time
from configparser import NoOptionError
from configparser import NoSectionError

#from .JamConfBase import JamConfBase
#from ..JamSession import JamSession
from ..Helpers import *

class recProps():
    def __init__(self):
        self.device = None
        self.samplerate = None
        self.channels = None
        self.subtype = None
        self.blocksize = None
        self.volumeTreshold = None
        self.stopAfterSilence = None
        self.recMaxLength = None

class usbstickProps():
    def __init__(self):
        self.name = 'sda'
        self.mountpoint = '/media/usb0'
        self.unplugCheckInterval = 3
        self.waitSecondsToRemount = 10

class ButtonProps():
    def __init__(self):
        self.pin = None
        self.duration = None

class RecorderConf():
    def __init__(self, action):
        self.rec = recProps()
        self.usbstick = usbstickProps()
        self.cnf = None
        self.action = action
        self.recMode = False
        self.rootDir = f'{os.path.dirname(os.path.abspath(__file__))}/../..'
        self.btnUnmount = ButtonProps

    def validateConfig(self):
        print("validating config")
        self.rec.samplerate = int(self.cnf.get('recorder', 'samplerate'))
        self.rec.subtype = str(self.cnf.get('recorder', 'subtype'))
        self.rec.subtype = str(self.rec.subtype) if self.rec.subtype != '' else None
        self.rec.device = self.cnf.get('recorder', 'device')
        self.rec.device = int_or_str(self.rec.device) if self.rec.device != '' else None
        self.rec.blocksize = self.cnf.get('recorder', 'blocksize')
        self.rec.blocksize = int(self.rec.blocksize) if self.rec.blocksize != '' else None
        self.rec.channels = int(self.cnf.get('recorder', 'channels'))
        self.rec.volumeTreshold = int(self.cnf.get('recorder', 'volumeTreshold'))
        self.rec.stopAfterSilence = int(self.cnf.get('recorder', 'stopAfterSilence'))
        self.rec.recMaxLength = int(self.cnf.get('recorder', 'recMaxLength'))

        self.usbstick.name = str(self.cnf.get('usbstick', 'name'))
        self.usbstick.mountpoint = str(self.cnf.get('usbstick', 'mountpoint'))
        self.usbstick.unplugCheckInterval = int(self.cnf.get('usbstick', 'unplugCheckInterval'))
        self.usbstick.waitSecondsToRemount = int(self.cnf.get('usbstick', 'waitSecondsToRemount'))

        self.btnUnmount.pin = int(self.cnf.get('buttons', 'unmount.pin'))
        self.btnUnmount.duration = int(self.cnf.get('buttons', 'unmount.pushduration'))

    def getRecFileName(self, channelString):
        return f"{self.usbstick.mountpoint}/delme_rec_%s-%s.wav" % (time.strftime("%Y.%m.%d-%H.%M.%S"), channelString)
