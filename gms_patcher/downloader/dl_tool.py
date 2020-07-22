import os
import pathlib
import urllib3
import requests
from concurrent.futures import ThreadPoolExecutor


def download_file(input_data):
    url = input_data["url"]
    path = input_data["path"]
    try:
        r = requests.get(url, proxies=proxies)
        with open(path, "wb") as ofile:
            ofile.write(r.content)
        print("downloaded: {}".format(path))
    except Exception as e:
        download_file(input_data)


if __name__ == "__main__":
    pwd = os.path.dirname(os.path.abspath(__file__))
    proxies = {
        "http": "http://127.0.0.1:2081",
        "https": "http://127.0.0.1:2081"
    }

    meta_data = []
    with open("dl.log", "r") as infile:
        for line in infile.readlines():
            line = line.strip()
            data_path = urllib3.util.parse_url(line).path

            os.makedirs(os.path.join(pwd, os.path.dirname(data_path).replace("/", "\\")[1:]), exist_ok=True)
            meta_data.append({
                "url": line,
                "path": os.path.join(pwd, data_path.replace("/", "\\")[1:])
            })

    with ThreadPoolExecutor(50) as exector:
        response = exector.map(download_file, meta_data)

