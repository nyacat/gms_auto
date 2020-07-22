import cv2
import gc
import sys
import time
import numpy
import queue
import logging
import requests
import win32gui
import threading
import config
from get_window import get_full_window
from minimap import cut_minimap


def send_remind(remind_config: dict, target_url: str):
    global remind_lock

    if remind_lock.locked():
        logging.warning("failed to get lock!")
        return

    remind_lock.acquire()

    send_count = 1
    for remind_data in remind_config["level"]:
        logging.debug("sleep for {}s".format(remind_data["delay"]))
        time.sleep(int(remind_data["delay"]))

        if not remind_lock.locked():
            logging.debug("rune released, exiting...")
            return
        try:
            if remind_config["pm_only"]:
                payload = {
                    "user_id": str(remind_config["qq"]),
                    "message": [
                        {
                            "type": "text",
                            "data": {"text": remind_data["additional_text"]}
                        }
                    ]
                }
                r = requests.post("http://{}/send_private_msg_rate_limited?access_token=NNjb4Ymg2QoG3f".
                                  format(target_url), json=payload)
            else:
                payload = {
                    "group_id": "922275457",
                    "message": [
                        {
                            "type": "at",
                            "data": {"qq": str(remind_config["qq"])}
                        },
                        {
                            "type": "text",
                            "data": {"text": remind_data["additional_text"]}
                        }
                    ]
                }
                r = requests.post("http://{}/send_group_msg_rate_limited?access_token=NNjb4Ymg2QoG3f".
                                  format(target_url), json=payload)
            if r.status_code == requests.codes.ok:
                logging.info("level:{} remind send".format(str(send_count)))
            logging.debug("send_interval sleep for {}s".format(remind_config["send_interval"]))
            time.sleep(remind_config["send_interval"])
        except Exception as e:
            logging.error("level:{} fail to send".format(str(send_count)))
            logging.debug(e)
        send_count = 1 + send_count
    remind_lock.release()


def process_map():
    # todo fix hwnd not found (e.g game exit, not launch yet
    hwnd = win32gui.FindWindow(None, "MapleStory")

    global remind_lock

    tolerate_frame = int(config_data["global"]["update_interval"])
    while True:
        last_time = time.time()
        try:
            full_image = get_full_window(hwnd)
            minimap_image = cut_minimap(full_image)
            hsv_image = cv2.cvtColor(minimap_image, cv2.COLOR_BGR2HSV)

            # Range for rune
            lower_rune = numpy.array([140, 153, 255])
            upper_rune = numpy.array([160, 153, 255])
            mask_rune = cv2.inRange(hsv_image, lower_rune, upper_rune)

            point_rune_map = cv2.findNonZero(mask_rune)
            if point_rune_map is not None:
                point_rune_avg = numpy.mean(point_rune_map, axis=0)
                if not remind_lock.locked():
                    r_thread = threading.Thread(target=send_remind, args=(config_data["rune"]["reminds"], api_url,),
                                                name="Remind Thread")
                    r_thread.start()
                logging.debug("point_rune_avg: {}".format(str(point_rune_avg.flatten())))
            else:
                if remind_lock.locked():
                    if tolerate_frame == 0:
                        logging.debug("rune not found,remind_lock released")
                        remind_lock.release()
                        tolerate_frame = int(config_data["global"]["update_interval"])
                    tolerate_frame = tolerate_frame - 1
                    logging.debug("tolerate_frame: {}".format(str(tolerate_frame)))

            del full_image
            del hsv_image
            del minimap_image
            del point_rune_map
        except ValueError as e:
            logging.error("Minimap Not Found!")
            time.sleep(3)
            continue
        except Exception as e:
            logging.error("unknown error!")
            logging.debug(e)
            time.sleep(3)
            continue
        finally:
            gc.collect()

        time.sleep(time_delta)
        logging.debug("fps: {}".format(1 / (time.time() - last_time)))


if __name__ == '__main__':
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] %(threadName)s: %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("usage.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.DEBUG)
    # rootLogger.setLevel(logging.INFO)

    config_data = config.load_config()

    if not config_data:
        logging.error("Fail to load config.json")
        sys.exit(1)

    # setup
    time_delta = 1. / int(config_data["global"]["update_interval"])
    api_url = config_data["global"]["api_url"]
    remind_lock = threading.Lock()

    t2 = threading.Thread(target=process_map, args=(), name="Rune Thread")

    t2.start()

    # while True:
    #     last_time = time.time()
    #
    #     minimap_image = minimap.get_image()
    #     hsv_image = cv2.cvtColor(minimap_image, cv2.COLOR_BGR2HSV)
    #
    #     # Range for self
    #     lower_self = numpy.array([25, 187, 255])
    #     upper_self = numpy.array([55, 187, 255])
    #     mask_self = cv2.inRange(hsv_image, lower_self, upper_self)
    #     result_self = cv2.bitwise_and(minimap_image, minimap_image, mask=mask_self)
    #
    #     # Range for rune
    #     lower_rune = numpy.array([140, 153, 255])
    #     upper_rune = numpy.array([160, 153, 255])
    #     mask_rune = cv2.inRange(hsv_image, lower_rune, upper_rune)
    #     result_rune = cv2.bitwise_and(minimap_image, minimap_image, mask=mask_rune)
    #
    #     point_self_map = cv2.findNonZero(mask_self)
    #     if point_self_map is not None:
    #         point_self_avg = numpy.mean(point_self_map, axis=0)
    #         # print("point_self_avg", point_self_avg.flatten())
    #
    #     point_rune_map = cv2.findNonZero(mask_rune)
    #     if point_rune_map is not None:
    #         if not remind_lock.locked():
    #             r_thread = threading.Thread(target=send_remind, args=(config_data["rune"]["reminds"], api_url,),
    #                                         name="Remind Thread")
    #             r_thread.start()
    #         point_rune_avg = numpy.mean(point_rune_map, axis=0)
    #         # print("point_rune_avg", point_rune_avg.flatten())
    #     else:
    #         if remind_lock.locked():
    #             logging.debug("remind_lock released")
    #             remind_lock.release()
    #
    #     time.sleep(time_delta)
    #     # print("fps: {}".format(1 / (time.time() - last_time)))
    #
    #     cv2.imshow("result_self", result_self)
    #     cv2.imshow("result_rune", result_rune)
    #
    #     k = cv2.waitKey(1)
    #     if k == 27:
    #         break
