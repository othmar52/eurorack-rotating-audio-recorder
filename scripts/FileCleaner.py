#!/bin/env python3

import os
import time
import subprocess
from subprocess import Popen, PIPE
import sys
from .Helpers import checkUsbDriveIsMounted
from .Helpers import checkUsbFreeSpace
from .Helpers import getFileContent
from .Helpers import appendLineToTextFile
from .Helpers import removeLinesFromBeginningInTextFile

class FileCleaner():
    def __init__(self, recConf):
        self.recConf = recConf
        self.logfilename = f'{recConf.usbstick.mountpoint}/{recConf.filecleaner.logfilename}'

    ''' fake full USB stick for testing purposes'''
    def applyDevelopmentDeltaToFreeSpace(self, realFreeSpace):
        return realFreeSpace - 53840000

    def run(self):
        print("run filecleaner")
        if checkUsbDriveIsMounted(self.recConf.usbstick.mountpoint) == False:
            print("USB stick not mounted. exiting")
            sys.exit()

        self.appendFileListFromRecorderScript()

        if not os.path.exists(self.logfilename):
            print("ERROR: we do not have a logfile")
            print("TODO: consider to create this logfile with all wav files of USB stick?")
            # time find /media/usb0/ -maxdepth 1 -type f -printf '%Cs %p\n' | sort > /media/usb0/.00-do_not_delete-recfiles.log.tmp
            sys.exit()

        requiredFreeSpace = self.calculateRequiredFreeSpace()

        self.recursiveDeleteOldestFile(
            requiredFreeSpace,
            getFileContent(self.logfilename).split('\n')
        )


    def recursiveDeleteOldestFile(self, requiredFreeSpace, fileList, lineIndex=0):
        freeSpaceKB = checkUsbFreeSpace(self.recConf.usbstick.mountpoint)
        #freeSpaceKB = self.applyDevelopmentDeltaToFreeSpace(freeSpaceKB)

        if freeSpaceKB > requiredFreeSpace:
            print(f"there is enough headroom for {self.kbToStereoWavMinutes(freeSpaceKB)} minutes additional stereo recording")
            print(f"deleted {lineIndex} lines from logfile")
            removeLinesFromBeginningInTextFile(self.logfilename, lineIndex)
            sys.exit()
        if lineIndex-1 > len(fileList):
            print("we have a recursion quirks. exiting...")
            sys.exit()

        print("we have to delete files. need:", requiredFreeSpace, "have:", freeSpaceKB)
        checkFile = fileList[lineIndex].split(' ', 1)[1]
        try:
            os.remove(checkFile)
            print(f"successfully deleted {checkFile}")
        except OSError:
            print(f"cound not delete {checkFile}")
            pass
        lineIndex += 1

        return self.recursiveDeleteOldestFile(requiredFreeSpace, fileList, lineIndex)

    def calculateRequiredFreeSpace(self):
        fileSizeDuringCronjobIntervalKB = self.getStereoWavFileSizeKB(
            16,
            self.recConf.rec.samplerate,
            self.recConf.filecleaner.cronjobIntervalMinutes * 60,
            2
        )
        # security factor 3 to ensure we have enough free space
        return fileSizeDuringCronjobIntervalKB * 3

    def kbToStereoWavMinutes(self, freeSpaceKB):
        minutes = freeSpaceKB/self.getStereoWavFileSizeKBOneSecond(
            16,
            self.recConf.rec.samplerate,
            2
        ) / 60
        return int(minutes)
    '''

    '''
    def getStereoWavFileSizeKB(self, bitdepth, samplerate, seconds, channels):
        return seconds * self.getStereoWavFileSizeKBOneSecond(bitdepth, samplerate, channels)
    '''
        taken from https://www.omnicalculator.com/other/audio-file-size

        audiofilesize = bitdepth * samplerate * durationofaudio * number of channels
        audiofilesize = 16 bits/sample * 44.1 kHz (or samples/sec) * 5 minutes * 2 channels
        audiofilesize = 16 bits/sample * 44,100 samples/sec * 300 seconds * 2 channels
        audiofilesize = 423,360,000 bits
        audiofilesize = 423,460,000 bits * (1 byte / 8 bits) * (1 Megabyte / 1,000,000 bytes)
        audiofilesize = 52.92 MB (Megabytes)
    '''
    def getStereoWavFileSizeKBOneSecond(self, bitdepth, samplerate, channels):
        seconds = 1
        bits = bitdepth * samplerate * seconds * channels
        audiofilesizeMB = bits * (1/8) * (1/1000000)
        audiofilesizeKB = audiofilesizeMB*1024
        return audiofilesizeKB


    def appendFileListFromRecorderScript(self):
        recorderList = f'{self.logfilename}.tmp'
        if not os.path.exists(recorderList):
            # there is no file from recorder script. nothing to to
            return
        linesToAdd = getFileContent(recorderList).split('\n')
        os.remove(recorderList)
        lineCount = 0
        for line in linesToAdd:
            if line == '':
                continue
            appendLineToTextFile(self.logfilename, line)
            lineCount += 1

        print(f"appended {lineCount} lines to {self.logfilename}")