# import win32gui
# from pywinauto.keyboard import SendKeys
# from pywinauto.application import Application
#
#
# app = Application(backend="uia").connect(class_name="MapleStoryClass")
# hidden_win = app.window_(title="MapleStory", visible_only=False)
# app.type_keys("{h down}"
#           "{e down}"
#           "{h up}"
#           "{e up}"
#           "llo")
# print(hidden_win)
#

# import win32gui
# import win32con
# import win32api
# from time import sleep
#
# # hwndMain = win32gui.FindWindow(None, 'MapleStory')
# hwndMain = win32gui.FindWindow("ApplicationFrameInputSinkWindow", None)
# print(hwndMain)
#
# while True:
#     # temp = win32api.PostMessage(hwndMain, win32con.WM_CHAR, 0x44, 0)
#
#     # temp2 = win32api.SendMessage(hwndMain, win32con.WM_KEYDOWN, win32api.VkKeyScan("A"), 0)
#     # temp2 = win32api.SendMessage(hwndMain, win32con.WM_KEYUP, win32api.VkKeyScan("A"), 0)
#     temp3 = win32api.SendMessage(hwndMain, win32con.WM_KEYDOWN, win32api.VkKeyScan("1"), 0)
#     temp4 = win32api.SendMessage(hwndMain, win32con.WM_KEYUP, win32api.VkKeyScan("1"), 0)
#
#     # print(temp2)
#     sleep(1)


import ctypes
import time

SendInput = ctypes.windll.user32.SendInput

W = 0x11
A = 0x1E
S = 0x1F
D = 0x20
Z = 0x2C
UP = 0xC8
DOWN = 0xD0
LEFT = 0xCB
RIGHT = 0xCD
ENTER = 0x1C

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def pressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def releaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0,
ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

if __name__ == '__main__':
    while True:
        pressKey(0x02)
        time.sleep(0.3)
        releaseKey(0x02)
        time.sleep(0.3)