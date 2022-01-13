#!/bin/env python3

import os
import select
import subprocess
import time
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

def checkUsbFreeSpace(mountpoint):
    p1 = Popen(["df", "-P", mountpoint], stdout=PIPE)
    p2 = Popen(["tail", "-n1"], stdin=p1.stdout, stdout=PIPE)
    p3 = Popen(["awk", "{print $4}"], stdin=p2.stdout, stdout=PIPE)
    return int(p3.communicate()[0].decode("utf-8").strip())

def unmountUsbStick(mountpoint):
    subprocess.run(["/usr/bin/umount", "-l", mountpoint])

def remountUsbStick(diskname):
    subprocess.run(["udevadm", "trigger", "--action=add", f"/dev/{diskname}1"])

def appendToFileCleanerList(fileCleanerFile, filenameToAdd):
    appendLineToTextFile(
        fileCleanerFile,
        f'{int(time.time())} {filenameToAdd}'
    )

def appendLineToTextFile(fileNameToWrite, lineToAdd):
    ensureFileExists(fileNameToWrite)
    file = open(fileNameToWrite, 'w')
    file.write(f'{lineToAdd}\n')
    file.close()

def writeTextFile(fileNameToWrite, fileContent):
    with open(fileNameToWrite, "w") as myfile:
        myfile.write(fileContent)

def removeLinesFromBeginningInTextFile(filePathToModify, amountOfLinesToRemove):
    if amountOfLinesToRemove < 1:
        return
    
    if not os.path.exists(filePathToModify):
        return
    
    with open(filePathToModify, 'r') as fin:
        data = fin.read().splitlines(True)
    with open(filePathToModify, 'w') as fout:
        fout.writelines(data[amountOfLinesToRemove:])


def getFileContent(pathAndFileName):
    with open(pathAndFileName, 'r') as theFile:
        data = theFile.read()
        theFile.close()
        return data

def ensureFileExists(filePath):
    if not os.path.exists(filePath):
        open(filePath, 'a').close()

def touch(filePath, times=None):
    with open(filePath, 'a'):
        os.utime(filePath, times)

def restartRecorderDaemon():
    subprocess.run(["systemctl", "restart", "recorder"])
