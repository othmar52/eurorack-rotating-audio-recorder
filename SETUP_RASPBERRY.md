# Setup Raspberry Pi Zero for this project

## Download image and write it to micro SD card
Get latest image `raspberry pi os lite` from https://www.raspberrypi.com/software/operating-systems/  
Write the downloaded image to sd card (in my case this took 7 minutes)  
Ensure to replace `/dev/sdXXXXXX` with the **correct** name (`/dev/sde` or something) to avoid data loss  
```bash
sudo dd if=2021-10-30-raspios-bullseye-armhf-lite.img of=/dev/sdXXXXXX bs=4M
```

## enable ssh & wifi for further setup

After that replug the SD card and access the boot partition.  
```
cd /<mountpoint-of-sd-card>/boot
touch ssh
echo 'country=DE
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
       ssid="name-of-your-wlan"
       psk="password"
       key_mgmt=WPA-PSK
}' > wpa_supplicant.conf
```

## unmount SD card and login via ssh

```bash
ssh pi@raspberrypi
raspberry
```
## install packages needed by recorder
 - `usbmount` for automounting USB stick
 - `python3-pip` for installing python packages
 - `python3-numpy` (pip package did not work for me)
 - `portaudio19-dev`
 - `libsndfile1`
 - `git` for fetching recorder scripts (optional)
```
sudo apt-get install usbmount python3-pip python3-numpy portaudio19-dev libsndfile1 git
```

## install python packages needed by recorder
 - `sounddevice`
 - `soundfile`
 - `adafruit-circuitpython-neopixel`

```
sudo pip install sounddevice soundfile adafruit-circuitpython-neopixel
```

## get recorder source files
```bash
git clone https://github.com/othmar52/eurorack-rotating-audio-recorder.git
```

## configure soundcard
ensure USB soundcard is plugged in  
then find out soundcard index with `aplay -l`  
```bash
pi@raspberrypi:~ $ aplay -l
**** List of PLAYBACK Hardware Devices ****
card 0: vc4hdmi [vc4-hdmi], device 0: MAI PCM i2s-hifi-0 [MAI PCM i2s-hifi-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: Device [USB Advanced Audio Device], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```

based on this info (`card 1` in my case) create the file  
 `sudo nano /etc/asound.conf`  
with this content:  
```conf
pcm.!default {
    type hw
    card 1
}
 
ctl.!default {
    type hw           
    card 1
}
```

## ensure USB stick gets mounted writeable each time  

In the file  
`sudo nano /lib/systemd/system/systemd-udevd.service`  
apply this change (change from `yes` to `no`)  
```diff
  -PrivateMounts=yes
  +PrivateMounts=no
```

## configure recorderscript to run after boot  
create a file    
```
sudo nano /lib/systemd/system/recorder.service
```
with this content
```
[Unit]
Description=Rotating Audio Recorder
After=multi-user.target

[Service]
User=root
Type=idle
ExecStart=/usr/bin/python /home/pi/eurorack-rotating-audio-recorder/rotating-audio-recorder.py usbwatcher
StandardOutput=null
StandardError=null
Restart=always

[Install]
WantedBy=multi-user.target
```
change permission of file  
```
sudo chmod 644 /lib/systemd/system/recorder.service
```
configure systemd  
```
sudo systemctl daemon-reload
sudo systemctl enable recorder.service
```


## configure filecleaner cronjob every 5 minutes  
this script ensures that there is always enough free space on the USB stick by deleting old recorded files.  
as root  
```
pi@raspberrypi:~ $ sudo su
root@raspberrypi:/home/pi# crontab -e
```
add this line to end of file  
```cronjob
*/5 * * * *     python /home/pi/eurorack-rotating-audio-recorder/rotating-audio-recorder.py filecleaner > /dev/null 2>&1
```
in case you also have a very small SD card (2GB in my case with only a few MB left) consider to add an additional cronjob:  
```
0 * * * *     journalctl --vacuum-size=2M > /dev/null 2>&1
```
and consider to run this command once to get a little more free space  
```
sudo apt-get clean
```

## finally restart your raspberry pi zero
```
sudo reboot now
```
