#!/bin/env python3

import board
import neopixel
import time

from .Helpers import *

class RgbLeds():
    def __init__(self, recConf):
        self.recConf = recConf

        self.statusLedPin = str(self.recConf.cnf.get('rgbleds', 'status.pin'))
        self.statusLedIdx = int(self.recConf.cnf.get('rgbleds', 'status.idx'))
        self.statusLedBlinkState = False
        self.vuCh1LedPin = str(self.recConf.cnf.get('rgbleds', 'vu.ch1.pin'))
        self.vuCh1LedIdx = int(self.recConf.cnf.get('rgbleds', 'vu.ch1.idx'))
        self.vuCh2LedPin = str(self.recConf.cnf.get('rgbleds', 'vu.ch2.pin'))
        self.vuCh2LedIdx = int(self.recConf.cnf.get('rgbleds', 'vu.ch2.idx'))
        self.brightness = float(self.recConf.cnf.get('rgbleds', 'brightness'))
        self.blinkinterval = int(self.recConf.cnf.get('rgbleds', 'blinkinterval'))

        self.colorRed = (255, 0, 0)
        self.colorBlue = (0, 0, 255)
        self.colorYellow = (255, 255, 0)
        self.colorGreen = (0, 255, 0)
        self.colorOff = (0, 0, 0)

        self.leds = {}
        for pinNumber in self.getLedPins():
            self.leds[pinNumber] = neopixel.NeoPixel(
                getattr(board, pinNumber),
                self.getLedsAmountforPin(pinNumber),
                brightness=self.brightness,
                auto_write=False,
                pixel_order=neopixel.GRB
            )

    def ledStatusObserveUsb(self):
        self.writeStatusLed(self.colorRed)

    def ledStatusOff(self):
        self.writeStatusLed(self.colorOff)

    def ledStatusObserveAudio(self):
        self.writeStatusLed(self.colorBlue)

    def ledStatusBlink(self, blinkBegin, color):
        x = (time.time() - blinkBegin) % (2*self.blinkinterval)
        wantLedStatus = True if x < self.blinkinterval else False

        if wantLedStatus == self.statusLedBlinkState:
            return

        if wantLedStatus == True:
            self.writeStatusLed(color)
        else:
            self.writeStatusLed(self.colorOff)
        self.statusLedBlinkState = wantLedStatus

    def ledStatusRecordAudio(self, blinkBegin):
        return self.ledStatusBlink(blinkBegin, self.colorRed)

    def ledStatusUnplugUsb(self, blinkBegin):
        return self.ledStatusBlink(blinkBegin, self.colorGreen)


    def getLedPins(self):
        pixelPins = [
            str(self.recConf.cnf.get('rgbleds', 'status.pin')),
            str(self.recConf.cnf.get('rgbleds', 'vu.ch1.pin')),
            str(self.recConf.cnf.get('rgbleds', 'vu.ch2.pin'))
        ]
        return list(set(pixelPins))

    def getLedsAmountforPin(self, pinNumber):
        amount = 0
        for cnfKey in ['status.pin', 'vu.ch1.pin', 'vu.ch2.pin' ]:
            if str(self.recConf.cnf.get('rgbleds', cnfKey)) == pinNumber:
                amount += 1
        return amount

    def writeStatusLed(self, color):
        self.leds[self.statusLedPin][self.statusLedIdx] = color
        self.leds[self.statusLedPin].show()

    def allLedsOff(self):
        self.ledStatusOff()
        self.ledVuChannel(0, self.vuCh1LedPin, self.vuCh1LedIdx)
        self.ledVuChannel(0, self.vuCh2LedPin, self.vuCh2LedIdx)

    def ledVuSingleChannel(self, channelLevel):
        self.ledVuChannel(channelLevel, self.vuCh1LedPin, self.vuCh1LedIdx)

    def ledVuDualChannel(self, ch1Level, ch2Level):
        self.ledVuChannel(ch1Level, self.vuCh1LedPin, self.vuCh1LedIdx)
        self.ledVuChannel(ch2Level, self.vuCh2LedPin, self.vuCh2LedIdx)

    def ledVuChannel(self, channelLevel, channelLedPin, channelLedIdx):
        color, brightness = self.getColorAndBrightnessForVu(channelLevel)
        self.leds[channelLedPin][channelLedIdx] = color
        self.leds[channelLedPin].brightness = brightness
        self.leds[channelLedPin].show()


    def getColorAndBrightnessForVu(self, level):

        maxInput = 20
        color = self.colorRed
        brightness = self.brightness
        if level < maxInput*0.8:
            color = self.colorYellow

        if level < maxInput*0.5:
            color = self.colorGreen
            brightness = mapFunc(level, 0, maxInput*0.5, 0, self.brightness)
            if level < 0.5:
                brightness = self.brightness
                color = self.colorOff

        return color, brightness

