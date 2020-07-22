import numpy
import logging
import win32ui
import win32gui
from ctypes import windll


def get_full_window(hwnd):
    # todo fix error from win32api

    left, top, right, bot = win32gui.GetClientRect(hwnd)
    # print(left, top, right, bot)
    w = right - left
    h = bot - top

    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
    save_dc.SelectObject(save_bitmap)

    windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 1)

    bmp_info = save_bitmap.GetInfo()
    bmp_str = save_bitmap.GetBitmapBits(True)

    _img = numpy.frombuffer(bmp_str, dtype='uint8').reshape(bmp_info['bmHeight'], bmp_info['bmWidth'], 4)
    # print(_img.shape)

    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)
    return _img
