img_h, img_w, _ = full_image.shape
# cut_w = int((img_w * (1 - 0.155)) / 2)
# target_w = int((img_w * 0.155) + cut_w)
cut_w_1 = int(img_w * 0.429)
cut_w_2 = int(img_w * 0.147)
info_image = full_image[img_h - 80:img_h, cut_w_1:cut_w_1 + cut_w_2]

ok, thresh = cv2.threshold(cv2.cvtColor(info_image, cv2.COLOR_BGR2GRAY), 150, 255, cv2.THRESH_TOZERO)
cv2.imshow("ok", thresh)
raw_contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
logging.debug("raw_contours: {}".format(len(raw_contours)))
for i in range(len(raw_contours)):
    area = cv2.contourArea(raw_contours[i])
    if 10 * 80 < area < 80 * cut_w_2:
        cnt_x, cnt_y, cnt_w, cnt_h = cv2.boundingRect(raw_contours[i])
        cv2.drawContours(info_image, raw_contours, i, (0, 255, 0), 2)
        print("ok")

# hsv_image = cv2.cvtColor(info_image, cv2.COLOR_BGR2HSV)
#
# # Range for info
# lower_info = numpy.array([0, 0, 180])
# upper_info = numpy.array([0, 0, 255])
# mask_info = cv2.inRange(hsv_image, lower_info, upper_info)
#
# raw_contours, _ = cv2.findContours(mask_info, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# logging.debug("raw_contours: {}".format(len(raw_contours)))
#
# for i in range(len(raw_contours)):
#     area = cv2.contourArea(raw_contours[i])
#     if 10 * 80 < area < 80 * cut_w_2:
#         cnt_x, cnt_y, cnt_w, cnt_h = cv2.boundingRect(raw_contours[i])
#         cv2.drawContours(info_image, raw_contours, i, (0, 255, 0), 2)
#         print("ok")

# print(mask_info.shape)
# cv2.imshow("mask_info", mask_info)

cv2.imshow("info_image", info_image)
