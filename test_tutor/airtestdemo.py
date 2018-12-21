import win32api

import win32con
from airtest.core.api import *
from airtest.aircv.template import *
from pywinauto import *
from poco.drivers.windows import *

import os
import sys
import cv2
import numpy as np
# from .error import FileNotExistError
from six import PY3

# app = application.Application()
# _app=os.path.join(os.getenv("APPDATA"),'\\TALLiveClient-Student\\bin\\TALLive.exe'.lstrip("\\"))
# app.start(_app)
"""
:param process: a process ID of the target
        :param handle: a window handle of the target
        :param path: a path used to launch the target
"""
# connect_device('windows:///6424046')
win=findwindows.enum_windows()
print(win)
# a=findwindows.find_window(process=2060)
# print(a)
# connect_device('windows:///?path=C:\\Users\\test1\\AppData\\Roaming\\TALLiveClient-Student\\bin\\TALLive.exe')
# snapshot("E:\img\save.png")
connect_device('windows:///')
snapshot("E:\img\save.png")
# assert_exists(Template("E:\img\ok.png"))
# touch(Template("E:\img\ok.png"))
# # set_current()
#
# # screen = G.DEVICE.snapshot(filename=None)
# query=Template("E:\img\choice.png")
# screen=Template("E:\img\choice.png")
# find_template("E:\img\choice.png","E:\img\choice_finish.png")

def imread(filename):
    """根据图片路径，将图片读取为cv2的图片处理格式."""
    if not os.path.isfile(filename):
        print("File not exist: %s" % filename)
    if PY3:
        stream = open(filename, "rb")
        bytes = bytearray(stream.read())
        numpyarray = np.asarray(bytes, dtype=np.uint8)
        img = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
    else:
        filename = filename.encode(sys.getfilesystemencoding())
        img = cv2.imread(filename, 1)
    return img
if __name__ == '__main__':
    print(imread("E:\img\choice.png"))
    a=find_all_template(imread("E:\img\choice_finish.png"),imread("E:\img\stu.png"))
    print(a)