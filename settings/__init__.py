#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017-2018, The Sumokoin Project (www.sumokoin.org)
'''
App top-level settings
'''

__doc__ = 'default application wide settings'

import sys
import os
import logging

from utils.common import getHomeDir, makeDir

USER_AGENT = "Ryo GUI Wallet"
APP_NAME = "Ryo GUI Wallet"
VERSION = [0, 2, 1]


if "--testnet" in sys.argv[1:]:
    _data_dir = makeDir(os.path.join(getHomeDir(), 'RyoGUIWallet', 'testnet'))
else:
    _data_dir = makeDir(os.path.join(getHomeDir(), 'RyoGUIWallet'))

DATA_DIR = _data_dir

log_file  = os.path.join(DATA_DIR, 'logs', 'app.log') # default logging file
log_level = logging.DEBUG # logging level

seed_languages = [
    ("0", "German"),
    ("1", "English"),
    ("2", "Spanish"),
    ("3", "French"),
    ("4", "Italian"),
    ("5", "Dutch"),
    ("6", "Portuguese"),
    ("7", "Russian"),
    ("8", "Japanese"),
    ("9", "Chinese (simplified)"),
    ("10", "Esperanto"),
    ("11", "Lojban"),
]

# COIN - number of smallest units in one coin
COIN = 1000000000.0
