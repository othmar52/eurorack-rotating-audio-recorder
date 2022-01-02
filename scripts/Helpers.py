#!/bin/env python3

import select
import subprocess
from subprocess import Popen, PIPE

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def checkUsbDriveIsMounted(mountPath):
    f = open("/proc/mounts", "r")
    isMounted = parseMountLines(f.read(), mountPath)
    return isMounted

def waitUntilUsbDriveIsMounted(mountPath):
    f = open("/proc/mounts")
    while True:
        r,w,x = select.select([],[],[f])
        f.seek(0)
        if parseMountLines(f.read(), mountPath) == True:
            return True

def parseMountLines(input, mountPath):
    for line in input.splitlines():
        if f' {mountPath} ' in line:
            return True
    return False

#  Well known Arduino map function
def mapFunc(x, in_min, in_max, out_min, out_max):
    return ((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


# display input level as number an vu meter by clearing and updating the last line of stdout
def terminalVuMeter(channelLeft, channelRight=None):
    print("\x1b[2K%f %s" % (channelLeft, "|" * int(channelLeft)), end="\r")


'''
  check if we have 'sda' available - no matter if mounted or unmounted
'''
def checkUsbPluggedIn(diskname):
    p1 = Popen(["lsblk"], stdout=PIPE)
    p2 = Popen(["grep", diskname], stdin=p1.stdout, stdout=PIPE)
    p3 = Popen(["head", "-n1"], stdin=p2.stdout, stdout=PIPE)
    p4 = Popen(["awk", "{print $1}"], stdin=p3.stdout, stdout=PIPE)
    return True if p4.communicate()[0].decode("utf-8").strip() == diskname else False

def unmountUsbStick(mountpoint):
    subprocess.run(["/usr/bin/umount", "-l", mountpoint])

def remountUsbStick(diskname):
    subprocess.run(["udevadm", "trigger", "--action=add", f"/dev/{diskname}1"])
