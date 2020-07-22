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
    img_area = img[0:int(img_h/3), 0:int(img_w/3)]

    hsv = cv2.cvtColor(img_area, cv2.COLOR_BGR2HSV)

    # Range for white
    lower_white = numpy.array([0, 0, 130])
    upper_white = numpy.array([0, 0, 255])
    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    result_white = cv2.bitwise_and(img_area, img_area, mask=mask_white)

    contours, _ = cv2.findContours(mask_white, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # print("contours 数量：", len(contours))

    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])
        if 10000 < area < 100000:
            cnt_x, cnt_y, cnt_w, cnt_h = cv2.boundingRect(contours[i])
            crop = img_area[cnt_y:cnt_h + cnt_y, cnt_x:cnt_w + cnt_x]
            cv2.imshow("snip", crop)

    # cv2.imshow("tmp_img", tmp_img)
    cv2.imshow("orig", img_area)
    # cv2.imshow("mask_white", mask_white)
    # cv2.imshow("result_white", result_white)
    print("fps: {}".format(1 / (time.time() - last_time)))
    # cv2.imshow("result_white", result_white)
    # cv2.imshow("result_red", result_red)
    # cv2.imshow("result_friend", result_friend)
    # cv2.imshow("result_test", result_test)

    k = cv2.waitKey(33)
    if k == 27:  # Esc key to stop
        break
