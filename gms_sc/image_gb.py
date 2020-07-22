import cv2
import numpy
import win32ui
import win32gui
from ctypes import windll
from PIL import Image

hwnd = win32gui.FindWindow(None, 'MapleStory')

# Change the line below depending on whether you want the whole window
# or just the client area.
left, top, right, bot = win32gui.GetClientRect(hwnd)
# left, top, right, bot = win32gui.GetWindowRect(hwnd)
w = right - left
h = bot - top

hwndDC = win32gui.GetWindowDC(hwnd)
mfcDC = win32ui.CreateDCFromHandle(hwndDC)
saveDC = mfcDC.CreateCompatibleDC()

saveBitMap = win32ui.CreateBitmap()
saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

saveDC.SelectObject(saveBitMap)

# Change the line below depending on whether you want the whole window
# or just the client area.
result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
# result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
print(result)

bmpinfo = saveBitMap.GetInfo()
bmpstr = saveBitMap.GetBitmapBits(True)

im = Image.frombuffer(
    'RGB',
    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
    bmpstr, 'raw', 'BGRX', 0, 1)

img = cv2.cvtColor(numpy.array(im), cv2.COLOR_RGB2BGR)
cv2.imshow("test", img)


while True:
    k = cv2.waitKey(33)
    if k == 27:  # Esc key to stop
        break
