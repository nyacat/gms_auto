import cv2
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


def window_core():
    hwnd = win32gui.FindWindow(None, "MapleStory")

    while True:
        last_time = time.time()
        try:
            full_image = get_full_window(hwnd)
            minimap_image = cut_minimap(full_image)

            cv2.imshow("full_image", full_image)
            cv2.imshow("minimap_image", minimap_image)
            del full_image
        except Exception as e:
            logging.error("fail to get full image!")
            logging.debug(e)
            time.sleep(3)
            continue

        time.sleep(time_delta)
        logging.debug("fps: {:.2f}".format(1 / (time.time() - last_time)))

        k = cv2.waitKey(33)
        if k == 27:
            break


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

    window_core()

    # remind_lock = threading.Lock()
    # t2 = threading.Thread(target=process_map, args=(), name="Rune Thread")
    #
    # t2.start()
