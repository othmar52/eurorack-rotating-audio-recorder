#!/bin/env python3
from scripts.PushButton import PushButton
from scripts.classes.UnmountRequest import UnmountRequest
import time
import numpy  # Make sure NumPy is loaded before it is used in the callback
import queue
import sounddevice as sd
import soundfile as sf
import sys

from .Helpers import *
from .RgbLeds import RgbLeds

class Recorder():
    def __init__(self, recConf):
        self.recConf = recConf
        self.leds = RgbLeds(recConf)
        self.q = queue.Queue()
        self.lastSilenceBegin = None

        self.unmountButton = PushButton(
            recConf.btnUnmount.pin,
            recConf.btnUnmount.duration
        )

    def getInputStream(self, channels):
        return sd.InputStream(
            samplerate=self.recConf.rec.samplerate,
            device=self.recConf.rec.device,
            channels=channels,
            callback=self.processAudioDataBulkCallback,
            blocksize=self.recConf.rec.blocksize
        )

    def getSoundFile(self, filename, channels):
        return sf.SoundFile(
            filename,
            mode='x',
            samplerate=self.recConf.rec.samplerate,
            channels=channels,
            subtype=self.recConf.rec.subtype
        )

    def processAudioDataBulkCallback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())


    def destroyInputStream(self, resource):
        resource.abort()
        resource.__exit__()

    def clearAudioDataQue(self):
        with self.q.mutex:
            self.q.queue.clear()

    def clearData(self, resource):
        self.destroyInputStream(resource)
        self.clearAudioDataQue()

    def clearAudioDataQue(self):
        with self.q.mutex:
            self.q.queue.clear()

    def run(self):
        try:
            self.observeAudioInputWithoutRecording()
        except UnmountRequest:
            # TODO how to pass Exception to parent process?
            # workaround with custom exit status....
            self.leds.allLedsOff()
            sys.exit(77)


    def observeAudioInputWithoutRecording(self):
        print('observing audio level without recording...\n')
        self.leds.ledStatusObserveAudio()

        with self.getInputStream(2) as inputStream:
            STEREO = 0
            DUAL_MONO = 1
            MONO = 2
            RECMODE = MONO
            lastCheckUnplugged = 0
            while True:
                audioData = self.q.get()
                if self.unmountButton.checkFirePushEvent() == True:
                    self.clearData(inputStream)
                    raise UnmountRequest()
                #readButtonRecModePin()

                if time.time() - lastCheckUnplugged > self.recConf.usbstick.unplugCheckInterval:
                    if checkUsbPluggedIn(self.recConf.usbstick.name) == False:
                        # unplugged usb stick
                        sys.exit()
                    lastCheckUnplugged = time.time()

                if RECMODE == STEREO or RECMODE == DUAL_MONO:
                    avarageVolume = self.vuMeterDualChannel(audioData)
                    if avarageVolume < self.recConf.rec.volumeTreshold:
                        continue
                    self.clearData(inputStream)
                    if RECMODE == STEREO:
                        return self.recordStereo()
                    return self.recordDualMono()
                
                audioDataLeftChannel = audioData[:, 0]
                volume_norm = numpy.linalg.norm(audioDataLeftChannel)*10
                self.leds.ledVuSingleChannel(volume_norm)
                terminalVuMeter(volume_norm)

                if volume_norm < self.recConf.rec.volumeTreshold:
                    continue

                self.destroyInputStream(inputStream)
                self.clearAudioDataQue()
                return self.recordMono()

    def recordMono(self):
        print("todo record mono")
    def recordDualMono(self):
        print("todo record dual mono")


    def vuMeterDualChannel(self, audioDataStereo):
        audioDataCH1 = audioDataStereo[:, 0]
        audioDataCH2 = audioDataStereo[:, 1]
        avarageVolume = numpy.linalg.norm(audioDataStereo)*10
        self.leds.ledVuDualChannel(
            numpy.linalg.norm(audioDataCH1)*10,
            numpy.linalg.norm(audioDataCH2)*10
        )
        terminalVuMeter(avarageVolume)
        return avarageVolume


    def vuMeterMonoChannel(self, audioDataCH1):
        avarageVolume = numpy.linalg.norm(audioDataCH1)*10
        self.leds.ledVuSingleChannel(
            numpy.linalg.norm(audioDataCH1)*10
        )
        terminalVuMeter(avarageVolume)
        return avarageVolume

    def recordStereo(self):
        # Make sure the file is opened before recording anything:
        filename = self.recConf.getRecFileName('stereo')
        lastRecordingBegin = time.time()
        self.lastSilenceBegin = None
        print(f"start recording STEREO ${filename}\n")
        try:
            with self.getSoundFile(filename, self.recConf.rec.channels) as file:
                with self.getInputStream(2) as inputStream:
                    while True:
                        audioDataStereo = self.q.get()
                        file.write(audioDataStereo)
                        self.leds.ledStatusRecordAudio(lastRecordingBegin)
                        avarageVolume = self.vuMeterDualChannel(audioDataStereo)

                        if self.unmountButton.checkFirePushEvent() == True:
                            file.close()
                            self.clearData(inputStream)
                            raise UnmountRequest()
                        #if self.shouldStopRecording(volume_norm) == True or readButtonRecModePin() == True:
                        if self.shouldStopRecording(avarageVolume) == True:
                            file.close()
                            self.clearData(inputStream)
                            return self.observeAudioInputWithoutRecording()
                        if self.shouldRotateRecording(lastRecordingBegin) == True:
                            file.close()
                            self.destroyInputStream(inputStream)
                            return self.recordStereo()
        except RuntimeError:
            # unplugged usb stick
            raise

    def recordDualMono(self):
        # Make sure the files are opened before recording anything:
        filenameCH1 = self.recConf.getRecFileName('ch1')
        filenameCH2 = self.recConf.getRecFileName('ch2')
        lastRecordingBegin = time.time()
        print(f"start recording DUAL MONO\n{filenameCH1}\n{filenameCH2}\n")
        try:
            with self.getSoundFile(filenameCH1, 1) as fileCH1:
                with self.getSoundFile(filenameCH2, 1) as fileCH2:
                    with self.getInputStream(2) as inputStream:
                        while True:
                            audioDataStereo = self.q.get()
                            self.leds.ledStatusRecordAudio(lastRecordingBegin)
                            avarageVolume = self.vuMeterDualChannel(audioDataStereo)

                            audioDataCH1 = audioDataStereo[:, 0]
                            audioDataCH2 = audioDataStereo[:, 1]
                            fileCH1.write(audioDataCH1)
                            fileCH2.write(audioDataCH2)
                            avarageVolume = self.vuMeterDualChannel(audioDataStereo)
                            if self.unmountButton.checkFirePushEvent() == True:
                                fileCH1.close()
                                fileCH2.close()
                                self.clearData(inputStream)
                                raise UnmountRequest()
                            #if self.shouldStopRecording(avarageVolume) == True or readButtonRecModePin() == True:
                            if self.shouldStopRecording(avarageVolume) == True:
                                fileCH1.close()
                                fileCH2.close()
                                self.clearData(inputStream)
                                return self.observeAudioInputWithoutRecording()
                            if self.shouldRotateRecording(lastRecordingBegin) == True:
                                fileCH1.close()
                                fileCH2.close()
                                self.destroyInputStream(inputStream)
                                return self.recordDualMono()
        except RuntimeError:
            # unplugged usb stick
            raise



    def recordMono(self):
        # Make sure the file is opened before recording anything:
        filename = self.recConf.getRecFileName('mono')
        lastRecordingBegin = time.time()
        self.leds.ledVuDualChannel(0, 0)
        print(f"start recording MONO ${filename}\n")
        try:
            with self.getSoundFile(filename, 1) as file:
                with self.getInputStream(1) as inputStream:
                    while True:
                        audioData = self.q.get()
                        file.write(audioData)
                        self.leds.ledStatusRecordAudio(lastRecordingBegin)
                        avarageVolume = self.vuMeterMonoChannel(audioData)
                        if self.unmountButton.checkFirePushEvent() == True:
                            file.close()
                            self.clearData(inputStream)
                            raise UnmountRequest()

                        #if self.shouldStopRecording(avarageVolume) == True or readButtonRecModePin() == True:
                        if self.shouldStopRecording(avarageVolume) == True:
                            file.close()
                            self.clearData(inputStream)
                            return self.observeAudioInputWithoutRecording()
                        if self.shouldRotateRecording(lastRecordingBegin) == True:
                            file.close()
                            self.destroyInputStream(inputStream)
                            return self.recordMono()
        except RuntimeError:
            # unplugged usb stick
            raise

    def shouldStopRecording(self, currentAudioLevel):
        if currentAudioLevel > self.recConf.rec.volumeTreshold:
            self.lastSilenceBegin = None
            return False
        if self.lastSilenceBegin == None:
            self.lastSilenceBegin = time.time()
            return False
        if time.time() - self.lastSilenceBegin > self.recConf.rec.stopAfterSilence:
            self.lastSilenceBegin = None
            return True
        return False

    def shouldRotateRecording(self, lastRecordingBegin):
        if time.time() - lastRecordingBegin < self.recConf.rec.recMaxLength:
            return False
        return True