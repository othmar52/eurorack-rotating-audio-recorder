# eurorack-rotating-audio-recorder
raspberry pi/python based automatic audio recorder


## Currently this is only an idea for a new project

The goal is to have a non-interactive utility that records all your happy little accidents while fiddling around with your eurorack to an USB stick.  

You dont have to start or stop the recording manually - it's all automatically based on audio levels that are beeing sent into the module.  

## Frontplate

 - TRS jack female audio in left
 - TRS jack female audio in right
 - TRS jack female audio out left
 - TRS jack female audio out right
 - Attenuator for input level
 - LED VU meter for input level
 - output L+R is just a copy of the input L+R
 - USB jack for an USB stick
 - LED that indicates if the device is currently recording
 - TRS jack sync in for daisy chain multiple eurorack-rotating-audio-recorder
 - TRS jack sync out for daisy chain multiple eurorack-rotating-audio-recorder

Maybe it makes sense to have the frontplate designed as a breakout for the raspberry-pi (which is placed somewhere inside your eurorack case) to keep the frontplate as small as possible (2HP-4HP).

## What does it do?

As soon as we have an audio level on `TRS jack in left` the raspberry starts to record audio. Mono or stereo depending on the audio input level of `TRS jack in right`.  

As soon as the USB stick is full the oldest recording(s) gets deleted to free space for the new recording. So depending on the capacity of the USB stick you always have the last X hours of audio activity recorded. 

Having silence on the audio input for e.g. 120 seconds the recordings stops atomatically.  

With the `sync IN/OUT` jacks you can achieve multi track recordings on multiple instances of `eurorack-rotating-audio-recorder`. In this scenario you may record silence in case there is no audio level on the inputs.


## Hardware/Parts/needed circuits

 - Raspberry Pi (zero?)
 - Circuit for converting eurorack level to line level (2 resistors)
 - What circuit is needed to have a single logarithmic potentiometer affecting levels for 2 audio channels (L+R)?  
 - Circuit for buffered mult to copy input audio to output audio
 - Circuit for LED based VU meter
 - USB input (do we need a shield or can we solder/ extend the the pins of existing USB to the frontplate?)


## Some unsorted Thoughts

How to choose recording format (mp3, flac, wav)?  
Do we need a master/slave concept when using multiple instances? Or how can we force to not stop the recording on master when we have an audio level on slave instance but silence on master instance?  






