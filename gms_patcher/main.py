import os
import sys
import time
import shutil
import random
import socket
import winreg
from multiprocessing.spawn import freeze_support

import psutil
import logging
import hashlib
from contextlib import closing
from http_server import start_web
from configparser import ConfigParser
from concurrent.futures import ProcessPoolExecutor


def check_socket(port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(1)
        if sock.connect_ex(("127.0.0.1", port)) == 0:
            return True
        else:
            return False


def gen_http_port():
    port = random.randint(1024, 65535)
    if check_socket(port):
        gen_http_port()
    else:
        return port


def find_nx():
    try:
        local_reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        reg_key = winreg.OpenKey(local_reg, r"SOFTWARE\Classes\nxl\shell\open\command")
        _nx_path = winreg.QueryValueEx(reg_key, "")[0]
        _nx_path = _nx_path.replace('"', "").split("\\nexon_launcher.exe")[0]
        return _nx_path
    except Exception as e:
        print(e)
        return None


def write_patch(save_path, data):
    with open(save_path, "w") as ofile:
        ofile.write(data)


def remove_data(remove_path):
    if os.path.isfile(remove_path):
        os.remove(remove_path)
    if os.path.isdir(remove_path):
        shutil.rmtree(remove_path)


def check_process_running(process_name_list: list):
    for proc in psutil.process_iter():
        try:
            for process_name in process_name_list:
                if process_name.lower() in proc.name().lower():
                    return True
                else:
                    continue
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


if __name__ == '__main__':
    freeze_support()
    # fix frozen exe
    if getattr(sys, 'frozen', False):
        pwd = os.path.dirname(os.path.abspath(sys.executable))
    else:
        pwd = os.path.dirname(os.path.abspath(__file__))
    cfg = ConfigParser()

    logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] %(threadName)s: %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("usage.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.DEBUG)

    log_level = logging.INFO
    auto_start = True
    try:
        cfg.read(os.path.join(pwd, 'config.ini'), encoding="UTF-8")
        log_level = cfg.get('settings', 'log_level')
        auto_start = cfg.getboolean("settings", "auto_start")
        nexon_dir = cfg.get("settings", "nexon_dir")
        if log_level == "DEBUG":
            rootLogger.setLevel(logging.DEBUG)
        else:
            rootLogger.setLevel(logging.INFO)
    except Exception as e:
        logging.error("Cannot read config.ini")
        logging.debug(e)
        time.sleep(6)
        sys.exit(1)

    # pre init
    nx_exe_list = ["nexon_launcher", "nexon_runtime", "nexon_updater", "nexon_agent", "nexon_client"]
    if check_process_running(nx_exe_list):
        logging.error("This tool cannot run when Nexon Launcher was running")
        time.sleep(6)
        sys.exit(1)
    # fuck kd
    kd_list = ["kdjsq"]
    if check_process_running(nx_exe_list):
        logging.warning('致KD用户: 这个工具会"损坏"NX登录器,请勿使用.')
        logging.warning('3秒后自动退出...')
        time.sleep(3)
        sys.exit(1)

    patch_data = '''
from urllib3 import request as _orig_request
def request(self, method, url, fields=None, headers=None, **urlopen_kw):
    if "download2.nexon.net" in url.lower():
        url = url.replace("download2.nexon.net", "127.0.0.1:_HTTP_PORT_")
        # try to fix for ms2
        if url.lower().startswith("https://"):
            url = url.replace("https://", "http://")
    method = method.upper()
    urlopen_kw["request_url"] = url
    if method in self._encode_url_methods:
        return self.request_encode_url(method, url, fields=fields, headers=headers, **urlopen_kw)
    else:
        return self.request_encode_body(method, url, fields=fields, headers=headers, **urlopen_kw)
_orig_request.RequestMethods.request = request
'''

    logging.info("UUCCS UPUP, 一时手冲一时爽,一直手冲一直爽!")
    logging.info("Setting up ENV......")

    # gen http port
    http_port = gen_http_port()
    logging.info("HTTP Server Port: {}".format(http_port))

    # find nx dir
    nx_reg_data = find_nx()
    if nx_reg_data:
        nx_path = os.path.join(nx_reg_data, r"bin\modules\contenttools")
        target_file = os.path.join(nx_path, "__init__.py")
        logging.info("Nexon Launcher: {}".format(nx_reg_data))
    else:
        logging.warning("Fail to find Nexon Launcher folder via registry.. trying config setting")
        if nexon_dir:
            nx_path = os.path.join(nexon_dir, r"bin\modules\contenttools")
            target_file = os.path.join(nx_path, "__init__.py")
            logging.info("Nexon Launcher: {}".format(nexon_dir))
        else:
            logging.error("Sorry, Could not found Nexon Launcher folder...")
            logging.error("Exit within 10s.")
            time.sleep(10)
            sys.exit(1)

    # write patch data
    if os.path.isdir(nx_path):
        if os.path.exists(target_file):
            logging.warning("Old Patch File found!...removing")
            remove_data(target_file)
            remove_data(os.path.join(nx_path, "__pycache__"))

        logging.warning("Trying patch Nexon Launcher...")
        patch_data = patch_data.replace("_HTTP_PORT_", str(http_port))
        patch_data_md5 = hashlib.md5(patch_data.encode('utf-8')).hexdigest()

        logging.debug("Patch Data String md5: {}".format(patch_data_md5))
        write_patch(target_file, patch_data)
        file_md5 = hashlib.md5(open(target_file, 'r').read().encode()).hexdigest()
        if os.path.exists(target_file) and file_md5 == patch_data_md5:
            logging.info("Nexon Launcher Patched!")
        else:
            logging.error("Nexon Launcher Patch Failed, please run with administrator rights!\n\tor allow {} in "
                          "your Antivirus software!".format(sys.executable))
            logging.debug("String md5: {} --- File md5: {}".format(patch_data_md5, file_md5))
            logging.debug("File Status: {}".format(os.path.exists(target_file)))
            time.sleep(6)
            sys.exit(1)

    # start http
    file_path = os.path.join(pwd, "Game")
    if not os.path.isdir(file_path):
        file_path = pwd
        logging.error("Static folder not found! Set to current folder")
        logging.warning("THIS WILL BE VERY SLOW!!!")
    if auto_start:
        logging.info("Start Nexon Launcher Now...")
        os.system('cd "{}" & {}'.format(find_nx(), "nexon_launcher.exe"))
        remove_data(target_file)
    with ProcessPoolExecutor(max_workers=1) as web_pool:
        web_pool.submit(start_web, file_path, http_port)
    sys.exit(0)
