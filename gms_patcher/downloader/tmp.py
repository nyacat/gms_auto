import io
import os
import sys
import winreg
import shutil
import urllib3
import requests
import argparse
from http_server import *


def find_nx():
    try:
        aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        aKey = winreg.OpenKey(aReg, r"SOFTWARE\Classes\nxl\shell\open\command")
        _nx_path = winreg.QueryValueEx(aKey, "")[0]
        _nx_path = _nx_path.replace('"', "").split("\\nexon_launcher.exe")[0]
        return _nx_path
    except:
        return None

def patch_file(save_path):
    with open(save_path, "w") as ofile:
        ofile.write(patch_data)

def remove_data(remove_path):
    if os.path.isfile(remove_path):
        os.remove(remove_path)
    if os.path.isdir(remove_path):
        shutil.rmtree(remove_path)

if __name__ == "__main__":
    patch_data = '''
from urllib3 import request as _orig_request

def request(self, method, url, fields=None, headers=None, **urlopen_kw):
    if "download2.nexon.net" in url.lower():
        url = url.replace("download2.nexon.net", "127.0.0.1:9000")
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

    print("尝试使用注册表查找nx目录")
    nx_reg_data = find_nx()
    if nx_reg_data:
        nx_path = os.path.join(nx_reg_data, r"bin\modules\contenttools")
        target_file = os.path.join(nx_path, "__init__.py")
        print("sbnx: {}".format(target_file))

        if os.path.isdir(nx_path):
            if os.path.exists(target_file):
                print("清理加速补丁中...")
                remove_data(target_file)
                remove_data(os.path.join(nx_path, "__pycache__"))
            else:
                print("写入本地更新内容")
                patch_file(target_file)
        print("启动文件服务器...")
        
        s = MyThreadingHTTPServer(("127.0.0.1", 9000), MyHTTPRequestHandler)
        sa = s.socket.getsockname()
        print("Serving HTTPServer on {}:{}".format(sa[0], sa[1]))
        s.serve_forever()
    else:
        print("查找失败....")

