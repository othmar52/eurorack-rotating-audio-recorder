# eurorack-rotating-audio-recorder
raspberry pi based automatic audio recorder


## Currently this is only a working prototype

see [SETUP_RASPBERRY.md](https://github.com/othmar52/eurorack-rotating-audio-recorder/tree/main/SETUP_RASPBERRY.md) for setup instructions  

The goal is to have a **non-interactive** utility that records all your happy little accidents while fiddling around with your eurorack to an USB stick.  

You dont have to start or stop the recording manually - it's all done automatically based on audio levels that are beeing sent into the module.  

Similar to footage creating surveillance devices you can only access the most recent recordings. The oldest recordings gets deleted automatically to free space for new recordings on the USB stick.  

There is no plan to implement any playback functionality. If you want to access the recording you have to unplug the USB stick and copy the files somewhere else.

Currently there is no plan to be able to daisy-chain multiple of those recorder modules to have a multitrack recording.  


## Frontplate

 - TRS jack female audio in left
 - TRS jack female audio in right
 - TRS jack female audio out left
 - TRS jack female audio out right
 - Switch with 3 positions for recording mode (stereo, dual mono, mono)
 - 2 Attenuators for input levels of both channels
 - 2 LED VU meter for input levels of both chennels
 - output L+R is just a copy of the input L+R
 - USB jack for an USB stick
 - status LED that indicates if the device is currently recording, waiting for usb stick, etc..
 - unmount push button - hold for 1 second to stop recording and unmount usb stick
 - marker push button - to create a textfile with timestamp next to the recording

Maybe it makes sense to have the frontplate designed as a breakout for the raspberry-pi (which is placed somewhere inside your eurorack case) to keep the frontplate as small as possible (2HP-4HP).

## What does it do?

As soon as we have an audio level on `TRS jack in` the raspberry starts to record audio. Mono or stereo depending on the 3-position-switch on the frontplate.  

As soon as the USB stick is full the oldest recording(s) gets deleted to free space for the new recording. So depending on the capacity of the USB stick you always have the last X hours of audio activity recorded.  

Having silence on the audio input for e.g. 10 seconds the recordings stops atomatically.  

## Hardware/Parts/needed circuits

 - Raspberry Pi (zero?)
 - tiny USB Audio Interface with stereo input
 - USB hub (one port for Audio Interface and the other for the USB-stick on the frontplate)
 - Circuit for converting eurorack level to line level (2 resistors)
 - Circuit for buffered mult to copy input audio to output audio
 - Circuit for LED based VU meter (or adressable rgb leds like Adafruit NeoPixel)
 - optional circuit to transform 12V to 5V (for eurorack power busses without 5V)





see my other [eurorack DIY projects](https://github.com/othmar52/eurorack)  



