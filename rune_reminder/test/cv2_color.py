import cv2
import time
import numpy
import win32ui
import win32gui
from ctypes import windll

hwnd = win32gui.FindWindow(None, 'MapleStory')

left, top, right, bot = win32gui.GetClientRect(hwnd)
w = right - left
h = bot - top


while True:
    last_time = time.time()

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
    # print(result)

    bmp_info = saveBitMap.GetInfo()
    bmp_str = saveBitMap.GetBitmapBits(True)

    img = numpy.frombuffer(bmp_str, dtype='uint8').reshape(bmp_info['bmHeight'], bmp_info['bmWidth'], 4)

    mfcDC.DeleteDC()
    saveDC.DeleteDC()

    win32gui.ReleaseDC(hwnd, hwndDC)
    win32gui.DeleteObject(saveBitMap.GetHandle())

    img_h, img_w, _ = img.shape
    img = img[0:int(img_h/3), 0:int(img_w/3)]

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Range for red
    lower_red = numpy.array([0, 255, 221])
    upper_red = numpy.array([0, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    result_red = cv2.bitwise_and(img, img, mask=mask_red)

    # Range for self
    lower_self = numpy.array([15, 100, 255])
    upper_self = numpy.array([36, 255, 255])
    mask_self = cv2.inRange(hsv, lower_self, upper_self)
    result_self = cv2.bitwise_and(img, img, mask=mask_self)

    # Range for white
    lower_white = numpy.array([0, 0, 130])
    upper_white = numpy.array([0, 0, 255])
    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    result_white = cv2.bitwise_and(img, img, mask=mask_white)

    # Range for rune
    lower_rune = numpy.array([143, 153, 255])
    upper_rune = numpy.array([157, 153, 255])
    mask_rune = cv2.inRange(hsv, lower_rune, upper_rune)
    result_rune = cv2.bitwise_and(img, img, mask=mask_rune)

    # result_test = cv2.bitwise_and(img, img, mask=mask_white + mask_red + mask_rune + mask_self)

    # cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imshow("orig", img)
    cv2.imshow("result_white", result_white)
    print("fps: {}".format(1 / (time.time() - last_time)))
    # cv2.imshow("result_white", result_white)
    # cv2.imshow("result_red", result_red)
    # cv2.imshow("result_friend", result_friend)
    # cv2.imshow("result_test", result_test)

    k = cv2.waitKey(33)
    if k == 27:  # Esc key to stop
        break
