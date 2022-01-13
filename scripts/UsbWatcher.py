#!/bin/env python3

import time
import subprocess
from subprocess import Popen, PIPE
import sys
from .Helpers import *
from .RgbLeds import RgbLeds
from .FreezeWatcher import FreezeWatcher

class UsbWatcher():
    def __init__(self, recConf):
        self.recConf = recConf
        self.leds = None
        self.reinitLeds()
        self.freezewatcher = FreezeWatcher(recConf)

    ''' subprocess also uses leds. this solves issues with freezing on led.write()'''
    def reinitLeds(self):
        self.leds = None
        self.leds = RgbLeds(self.recConf)

    def observeUsbMount(self):
        print("observing usb mount")
        self.reinitLeds()
        self.leds.ledStatusObserveUsb()
        # initial check once
        if checkUsbDriveIsMounted(self.recConf.usbstick.mountpoint) == True:
            print("already mounted")
            return self.runRecorderScript()
        try:
            self.freezewatcher.publishWatchUsbMount()
            # check permanently
            if waitUntilUsbDriveIsMounted(self.recConf.usbstick.mountpoint) == True:
                print("fire mounted")
                return self.runRecorderScript()
                
        except KeyboardInterrupt:
            self.leds.allLedsOff()
            #sys.exit()
            return


    def handleUnmountRequest(self):
        self.reinitLeds()
        if checkUsbDriveIsMounted(self.recConf.usbstick.mountpoint) == False:
            return self.observeUsbMount()
        
        unmountRequestTimestamp = time.time()
        lastCheckUnplugged = time.time()

        try:
            unmountUsbStick(self.recConf.usbstick.mountpoint)
            print("unmounting USB stick. waiting for unplug...")
            self.freezewatcher.publishWatchUsbMount()
            while True:
                self.leds.ledStatusUnplugUsb(unmountRequestTimestamp)

                if time.time() - lastCheckUnplugged > self.recConf.usbstick.unplugCheckInterval:
                    if self.checkUsbPluggedIn(self.recConf.usbstick.name) == False:
                        return self.observeUsbMount()
                    lastCheckUnplugged = time.time()
                
                if time.time() - unmountRequestTimestamp > self.recConf.usbstick.waitSecondsToRemount:
                    remountUsbStick(self.recConf.usbstick.name)
                    return self.observeUsbMount()
        except KeyboardInterrupt:
            print("catch Ctrl-C in unmount wait loop")
            self.reinitLeds()
            self.leds.allLedsOff()
            sys.exit()


    '''
    check if we have 'sda' available - no matter if mounted or unmounted
    '''
    def checkUsbPluggedIn(self, diskname):
        p1 = Popen(["lsblk"], stdout=PIPE)
        p2 = Popen(["grep", diskname], stdin=p1.stdout, stdout=PIPE)
        p3 = Popen(["head", "-n1"], stdin=p2.stdout, stdout=PIPE)
        p4 = Popen(["awk", "{print $1}"], stdin=p3.stdout, stdout=PIPE)
        return True if p4.communicate()[0].decode("utf-8").strip() == diskname else False

    
    def runRecorderScript(self):
        try:
            #self.leds = None
            subprocess.run(['python', f'{self.recConf.rootDir}/rotating-audio-recorder.py','recorder'], check=True)
        except subprocess.CalledProcessError as e:
            # TODO how to pass Exception to parent process?
            # workaround with nonsense exit status....
            if e.returncode == 77:
                return self.handleUnmountRequest()
        except KeyboardInterrupt:
            print("catch Ctrl-C in usb watcher")
            self.reinitLeds()
            self.leds.allLedsOff()
            sys.exit()
            #return
        return self.observeUsbMount()