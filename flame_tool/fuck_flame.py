import os
import sys
import json
import time
import random
import logging
import keyboard
import pyautogui


def find_all_flame():
    all_pos = []
    for pos in pyautogui.locateAllOnScreen("target_images/r_flame.png", grayscale=True, confidence=target_confidence):
        if isinstance(pos, pyautogui.collectionsSequence):
            if len(pos) == 4:
                all_pos.append(pos)
                # print(pos)

    for pos in pyautogui.locateAllOnScreen("target_images/c_flame.png", grayscale=True, confidence=target_confidence):
        if isinstance(pos, pyautogui.collectionsSequence):
            if len(pos) == 4:
                all_pos.append(pos)
                # print(pos)

    # print(len(all_pos))
    return all_pos


def find_use_tab():
    tab_pos = []
    for pos in pyautogui.locateAllOnScreen("target_images/use_tab_on.png", grayscale=True,
                                           confidence=target_confidence):
        if isinstance(pos, pyautogui.collectionsSequence):
            if len(pos) == 4:
                tab_pos.append(pos)
                # pyautogui.moveTo(pos.left + int(pos.width/2), pos.top + int(pos.height/2))

    if len(tab_pos) == 0 or not tab_pos:
        for pos in pyautogui.locateAllOnScreen("target_images/use_tab_off.png", grayscale=True,
                                               confidence=target_confidence):
            if isinstance(pos, pyautogui.collectionsSequence):
                if len(pos) == 4:
                    tab_pos.append(pos)

    return tab_pos[-1]


def fuck_use_tab():
    global use_tab_position
    while not use_tab_position:
        try:
            use_tab_position = find_use_tab()
        except Exception as e:
            print(e)
            pass


def gen_movement():
    move_x, move_y = random.choice(range(-68, 68)), random.choice(range(-68, 68))
    while 0 <= move_x <= 34 or 0 <= move_y <= 34:
        move_x, move_y = random.choice(range(-68, 68)), random.choice(range(-68, 68))
    return move_x, move_y


def main():
    # get target position
    target_position = pyautogui.position()

    # get position of use tab
    global use_tab_position
    if not use_tab_position:
        logging.warning("Getting USE tab position...")
        fuck_use_tab()

    # print("use tab:", use_tab_position)
    pyautogui.moveTo(use_tab_position.left + int(use_tab_position.width / 2),
                     use_tab_position.top + int(use_tab_position.height / 2),
                     duration=move_interval, tween=pyautogui.easeInOutQuad)
    pyautogui.click(clicks=1, interval=move_interval)
    time.sleep(wait_use_tab)

    # get all flame
    global all_flame
    global flame_counter
    if not all_flame:
        all_flame = find_all_flame()
        flame_counter["total"] = flame_counter["total"] + len(all_flame)
    if len(all_flame) == 0:
        logging.error("找不到火花了...")
        # all_flame = False
        return False

    target_flame = random.choice(all_flame)
    flame_counter["used"] = flame_counter["used"] + 1
    logging.warning(
        "{}/{} processing_flame: {}".format(flame_counter["used"], flame_counter["total"], str(target_flame)))

    pyautogui.moveTo(target_flame.left + int(target_flame.width / 2),
                     target_flame.top + int(target_flame.height / 2),
                     duration=move_interval, tween=pyautogui.easeOutQuad)
    pyautogui.doubleClick(interval=0.25)
    pyautogui.moveTo(target_position)
    pyautogui.click()
    pyautogui.press('enter')
    pyautogui.press('enter')

    move_x, move_y = gen_movement()
    pyautogui.move(move_x, move_y, duration=wait_for_update, tween=pyautogui.easeOutQuad)
    pyautogui.moveTo(target_position, duration=wait_for_update * 2, tween=pyautogui.easeOutQuad)
    all_flame.remove(target_flame)


def exit_callback():
    global exit_status
    exit_status = True
    keyboard.unhook_all()
    keyboard.unhook_all_hotkeys()
    sys.exit(0)


if __name__ == "__main__":
    # run dir
    pwd = os.path.dirname(os.path.abspath(__file__))

    # log setup
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("usage.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    # rootLogger.setLevel(logging.DEBUG)
    rootLogger.setLevel(logging.INFO)

    # config setup
    config_file_path = os.path.join(pwd, "flame_config.json")
    if not os.path.exists(config_file_path):
        logging.error("config file not found!")
        logging.warning("Creating default config for you")

        config_data = {
            "target_confidence": 0.9,
            "move_interval": 0.1,
            "wait_use_tab": 0.15,
            "wait_for_update": 0.15,
            "key_exit": "esc",
            "key_next": "n"
        }
        with open(config_file_path, "w") as ofile:
            ofile.write(json.dumps(config_data, indent=4))

    else:
        with open(config_file_path, "r") as infile:
            config_data = json.loads(''.join(infile.readlines()))

    logging.info("火花小助手启动完成...")
    logging.info("启动参数:")
    logging.info("识别自信度: {}".format(config_data["target_confidence"]))
    logging.info("鼠标移动速度: {}".format(config_data["move_interval"]))
    logging.info("use列表切换等待时间: {}".format(config_data["wait_use_tab"]))
    logging.info("等待火花更新时间: {}".format(config_data["wait_for_update"]))
    logging.info("按键设置:")
    logging.info("下一个: {}".format(config_data["key_next"]))
    logging.info("退出: {}".format(config_data["key_exit"]))

    target_confidence = config_data["target_confidence"]
    move_interval = config_data["move_interval"]
    wait_use_tab = config_data["wait_use_tab"]
    wait_for_update = config_data["wait_for_update"]
    key_next = config_data["key_next"]
    key_exit = config_data["key_exit"]

    # inner data setup
    flame_counter = {
        "total": 0,
        "used": 0
    }
    exit_status = False
    use_tab_position = False
    all_flame = False

    # bind keys
    keyboard.add_hotkey(key_exit, exit_callback, args=(), suppress=True)
    while not exit_status:
        keyboard.wait(key_next, suppress=True, trigger_on_release=True)
        main()

    # clean
    keyboard.unhook_all()
    keyboard.unhook_all_hotkeys()
