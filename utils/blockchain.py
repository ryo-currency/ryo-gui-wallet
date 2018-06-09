#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2018, Ryo-currency (ryo-currency.com)
## Copyright (c) 2017, The Sumokoin Project (www.sumokoin.org)
'''
Blockchain import functions
'''

import sys, os
import re
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from multiprocessing import Process, Event
from time import sleep

from utils.common import getResourcesPath
from utils.logger import log, LEVEL_DEBUG, LEVEL_ERROR, LEVEL_INFO

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0  # disable creating the window

def pop_blocks(num=1000):
    num = int(num)
    resources_path = getResourcesPath()
    args = u'%s/bin/ryo-blockchain-import --pop-blocks %d' % (resources_path, num)

    args_array = args.encode( sys.getfilesystemencoding() ).split(u' ')
    proc = Popen(args_array,
                      shell=False,
                      stdout=PIPE, stderr=STDOUT, stdin=PIPE,
                      creationflags=CREATE_NO_WINDOW)

    proc_name = 'ryo-blockchain-import'
    log("[%s] %s" % (proc_name, args), LEVEL_INFO, proc_name)

    sleep(0.1)

    for line in iter(proc.stdout.readline, b''):
        log(">>> " + line.rstrip(), LEVEL_DEBUG, proc_name)
        
    if not proc.stdout.closed:
        proc.stdout.close()

    return False
