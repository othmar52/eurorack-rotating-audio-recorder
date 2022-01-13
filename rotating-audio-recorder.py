#!/usr/bin/env python3
"""
https://github.com/othmar52/eurorack-rotating-audio-recorder

"""
import sys
import signal
from scripts.Config import getRecorderConf
from scripts.UsbWatcher import UsbWatcher
from scripts.Recorder import Recorder
from scripts.FileCleaner import FileCleaner
from scripts.RgbLeds import RgbLeds
from scripts.FreezeWatcher import FreezeWatcher

def main():
    try:
        recConf = getRecorderConf()

        def turnOffTheLightsAndExit(*args):
            leds = RgbLeds(recConf)
            leds.allLedsOff()
            freezeWatcher = FreezeWatcher(recConf)
            freezeWatcher.exit()
            sys.exit()

        signal.signal(signal.SIGINT, turnOffTheLightsAndExit)
        signal.signal(signal.SIGTERM, turnOffTheLightsAndExit)

        if recConf.action == 'usbwatcher':
            usbWatcher = UsbWatcher(recConf)
            usbWatcher.observeUsbMount()
        if recConf.action == 'recorder':
            recorder = Recorder(recConf)
            recorder.run()
        if recConf.action == 'filecleaner':
            fileCleaner = FileCleaner(recConf)
            fileCleaner.run()
        if recConf.action == 'checkfreeze':
            freezeWatcher = FreezeWatcher(recConf)
            freezeWatcher.checkDaemonRestart()

    except KeyboardInterrupt:
        print('\nexit recorder')
        turnOffTheLightsAndExit()
        


if __name__ == "__main__":
    main()
