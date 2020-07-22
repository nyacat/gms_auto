import cv2
import numpy
import logging


def cut_minimap(full_image):
    img_h, img_w, _ = full_image.shape
    # logging.debug("game image size: {}x{}".format(img_h, img_w))

    img_area = full_image[0:int(img_h / 3), 0:int(img_w / 3)]
    hsv = cv2.cvtColor(img_area, cv2.COLOR_BGR2HSV)

    # Range for white
    lower_white = numpy.array([0, 0, 170])
    upper_white = numpy.array([0, 0, 255])
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    raw_contours, _ = cv2.findContours(mask_white, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # logging.debug("raw_contours: {}".format(len(raw_contours)))

    contours = []
    for i in range(len(raw_contours)):
        area = cv2.contourArea(raw_contours[i])
        if 50 * 50 < area < 250 * 250:
            cnt_x, cnt_y, cnt_w, cnt_h = cv2.boundingRect(raw_contours[i])
            if 15 < cnt_x < 25:
                continue
            contours.append({"data": cv2.boundingRect(raw_contours[i]), "area": area})
            # cnt_x, cnt_y, cnt_w, cnt_h = cv2.boundingRect(raw_contours[i])
            # print(cnt_x, cnt_y, cnt_w, cnt_h)
            # crop = img_area[cnt_y:cnt_h + cnt_y, cnt_x:cnt_w + cnt_x]
            # cv2.imshow("crop{}".format(str(i)), crop)

    # logging.debug("contours: {}".format(len(contours)))
    if contours:
        cnt_x, cnt_y, cnt_w, cnt_h = min(contours, key=lambda x: x['area'])["data"]
        return full_image[cnt_y:cnt_h + cnt_y, cnt_x:cnt_w + cnt_x]
    else:
        raise ValueError("Minimap Not Found")


if __name__ == '__main__':
    pass