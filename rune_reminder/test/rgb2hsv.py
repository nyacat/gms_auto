import cv2
import numpy as np

if __name__ == "__main__":
    rgb_color = np.uint8([[[102,102,102]]])
    hsv = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2HSV)
    print(', '.join(map(str, hsv[0][0].tolist())))
