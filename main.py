#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017, The Sumokoin Project (www.sumokoin.org)
'''
App main function
'''

import sys, os, hashlib
from PySide import QtCore

from PySide.QtGui import QMessageBox

from app.QSingleApplication import QSingleApplication
from utils.common import DummyStream, getAppPath, getResourcesPath, readFile
from settings import APP_NAME

from app.hub import Hub
from webui import MainWebUI

file_hashes = [
        ('www/scripts/jquery-1.9.1.min.js', 'c12f6098e641aaca96c60215800f18f5671039aecf812217fab3c0d152f6adb4'),
        ('www/scripts/bootstrap.min.js', '2979f9a6e32fc42c3e7406339ee9fe76b31d1b52059776a02b4a7fa6a4fd280a'),
        ('www/scripts/mustache.min.js', '3258bb61f5b69f33076dd0c91e13ddd2c7fe771882adff9345e90d4ab7c32426'),
        ('www/scripts/jquery.qrcode.min.js', 'f4ccf02b69092819ac24575c717a080c3b6c6d6161f1b8d82bf0bb523075032d'),
        ('www/scripts/utils.js', 'd0c6870ed19c92cd123c7443cb202c7629f9cd6807daed698485fda25214bdb4'),
        ('www/scripts/main.js', '00c77b75d75482241e086fdbad7552b46467960b5d36401d535ec329d1529c5a'),

        ('www/css/structure.css', '2272e39fb9a078a13985e3fcacec9ca725e4d77467197b55a0cca0219cadef81'),
        ('www/css/light-theme.css', '58ad4961791523bc259c4794ece88af47170db31eb00cc5f65e2a5289410b226'),
        ('www/css/dark-theme.css', 'bae55461985c063e252135ba85495c9a16a8cf75e4b0a74a341d16923a8c69b7'),

        ('www/css/bootstrap.min.css', '9d517cad6f1744ab5eba382ccf0f53969f7d326e1336a6c2771e82830bc2c5ac'),
        ('www/css/font-awesome.min.css', 'b8b02026a298258ce5069d7b6723c2034058d99220b6612b54bc0c5bf774dcfb'),

        ('www/css/fonts/fontawesome-webfont.ttf', '7b5a4320fba0d4c8f79327645b4b9cc875a2ec617a557e849b813918eb733499'),
        ('www/css/fonts/glyphicons-halflings-regular.ttf', 'e395044093757d82afcb138957d06a1ea9361bdcf0b442d06a18a8051af57456'),
        ('www/css/fonts/RoboReg.ttf', 'dc66a0e6527b9e41f390f157a30f96caed33c68d5db0efc6864b4f06d3a41a50'),
    ]

def _check_file_integrity(app):
    ''' Check file integrity to make sure all resources loaded
        to webview won't be modified by an unknown party '''
    for file_name, file_hash in file_hashes:
        file_path = os.path.normpath(os.path.join(app.property("ResPath"), file_name))
        if not os.path.exists(file_path):
            return False
        data = readFile(file_path)
#         print( file_path, hashlib.sha256(data).hexdigest() )
        if hashlib.sha256(data).hexdigest() != file_hash:
            return False

    return True


def main():
    if getattr(sys, "frozen", False) and sys.platform in ['win32','cygwin','win64']:
        # and now redirect all default streams to DummyStream:
        sys.stdout = DummyStream()
        sys.stderr = DummyStream()
        sys.stdin = DummyStream()
        sys.__stdout__ = DummyStream()
        sys.__stderr__ = DummyStream()
        sys.__stdin__ = DummyStream()

    # Get application path
    app_path = getAppPath()
    resources_path = getResourcesPath()

    # Application setup

    app = QSingleApplication(sys.argv)
    app.setOrganizationName('Ryo')
    app.setOrganizationDomain('ryo-currency.com')
    app.setApplicationName(APP_NAME)
    app.setProperty("AppPath", app_path)
    app.setProperty("ResPath", resources_path)
    if sys.platform == 'darwin':
        app.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus)

    if not _check_file_integrity(app):
        QMessageBox.critical(None, "Application Fatal Error", """<b>File integrity check failed!</b>
                <br><br>This could be a result of unknown (maybe, malicious) action<br> to wallet code files.""")
        app.quit()
    else:
        hub = Hub(app=app)
        ui = MainWebUI(app=app, hub=hub, debug=False)
        hub.setUI(ui)
        app.singleStart(ui)

        sys.exit(app.exec_())
