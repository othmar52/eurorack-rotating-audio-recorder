#!/bin/env python3

import time
import os
from .Helpers import touch, writeTextFile, getFileContent
from .Helpers import restartRecorderDaemon
class FreezeWatcher():

    def __init__(self, recConf):
        self.recConf = recConf
        self.enable = True if recConf.freezewatcher.enable == 1 else False
        self.cronjobIntervalMinutes = recConf.freezewatcher.cronjobIntervalMinutes
        self.pidFile = recConf.freezewatcher.pidFile

        self.lastWrittenHeartbeat = None
        self.heartbeatInterval = int(self.cronjobIntervalMinutes*60/2)

    def heartbeat(self):
        if self.enable == False:
            return

        if self.lastWrittenHeartbeat == None:
            self.touchPidFile()
            return

        if time.time() - self.lastWrittenHeartbeat > self.heartbeatInterval:
            self.touchPidFile()

    def touchPidFile(self):
        touch(self.pidFile)
        self.lastWrittenHeartbeat = time.time()

    def exit(self):
        if os.path.exists(self.pidFile):
            os.remove(self.pidFile)

    def publishWatchAudio(self):
        if self.enable == False:
            print('publishWatchAudio disabled')
            return
        writeTextFile(self.pidFile, '')

    def publishWatchUsbMount(self):
        if self.enable == False:
            return
        writeTextFile(self.pidFile, 'watchusb')

    def isAlive(self):
        try:
            mtime = float(os.path.getmtime(self.pidFile))
        except FileNotFoundError:
            return False

        if time.time() - mtime < self.cronjobIntervalMinutes*60:
            return True

        if getFileContent(self.pidFile) == 'watchusb':
            return True
        return False

    def checkDaemonRestart(self):
        if self.enable == False:
            return
        if self.isAlive() == True:
            print('alive')
            return
        print('restarting daemon')
        # log in filesystem next to recording files
        filename = self.recConf.getRecFileName('daemon-restart')
        writeTextFile(
            f'{filename}.log', ''
        )
        restartRecorderDaemon()