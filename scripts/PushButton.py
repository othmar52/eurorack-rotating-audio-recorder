#!/bin/env python3

import time
import RPi.GPIO as GPIO

class PushButton():

    def __init__(self, pinNumber, pushDuration=0):
        self.pinNumber = int(pinNumber)
        self.pushDuration = int(pushDuration)
        self.state = True # inverted
        self.lastDown = None

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pinNumber, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def checkFirePushEvent(self):
        if GPIO.input(self.pinNumber) != self.state:
            self.state =  not self.state
            if self.state == False:
                # button went down
                self.lastDown = time.time()
                return False
            else:
                # button went up again - see if duration is valid
                if time.time() - self.lastDown >= self.pushDuration:
                    return True
        return False