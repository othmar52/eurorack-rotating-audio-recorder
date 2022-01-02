#!/bin/env python3

import argparse
import configparser
import sys

from .classes.RecorderConf import RecorderConf

runRecorderAction = False
runFilecleanerAction = False

def programDescription ():
    return '''DESCRIPTION:
record audio input in mono, stereo or dual mono to an usb stick
---------------------------------------------------------------
TODO: add description
    '''


def getRecorderConf():
    parser = argparse.ArgumentParser(
        description=programDescription(),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments'.upper())
    optional = parser.add_argument_group('optional arguments'.upper())
    required.add_argument(
        'action',
        nargs = 1,
        type=str,
        help='what to do. use exactly one of the available actions',
        choices=['usbwatcher', 'recorder', 'filecleaner']
    )
    optional.add_argument(
        '--targetdir',
        type=str,
        help='target directory for the processed files'
    )
    args = parser.parse_args()

    recConf = RecorderConf(args.action[0])
    recConf.cnf = configparser.ConfigParser(strict=False)

    try:
        recConf.cnf.read([
            f'{recConf.rootDir}/config/general.ini',       # shipped with gitrepo
            f'{recConf.rootDir}/config/local.ini',         # optional gitignored local configuration
            f'{recConf.usbstick.mountpoint}/config.txt'     # optional config in usb stick root
        ])
    except configparser.ParsingError:
        pass

    recConf.validateConfig()
    return recConf
