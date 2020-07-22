import os
import sys
import json
import logging
import platform

# todo add watchdog func

# fix frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(os.path.abspath(sys.executable))
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(application_path, "config.json")


def get_mtime():
    if platform.system() == 'Windows':
        return os.path.getmtime(config_file)
    else:
        return None


def load_config():
    if not os.path.exists(config_file):
        logging.error("config file not found!")
        return False
    with open(config_file, "r", encoding="utf-8") as config_fp:
        try:
            json_data = json.load(config_fp)
        except Exception as e:
            logging.debug(e)
            return False
    if json_data["global"]["api_region"] == "cn":
        json_data["global"]["api_url"] = "103.85.86.98:19990"
    elif json_data["global"]["api_region"] == "us":
        json_data["global"]["api_url"] = "64.64.228.85:27080"
    else:
        logging.error("not support region: {}".format(json_data["global"]["api_region"]))
        return False
    del json_data["global"]["api_region"]
    return json_data
