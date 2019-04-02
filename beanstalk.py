"""Zip up project for AWS Elastic Beanstalk deployment"""

import os
import zipfile
from configparser import ConfigParser

CFG_PATH = "./jtimer/config/info.ini"
FILES = ["application.py", "setup.py", "requirements.txt", "jtimer", ".ebextensions"]
NAME = "jtimer-api"


def zipdir(path, zip_handle):
    """Recursively add directory to zip archive"""
    for root, _, files in os.walk(path):
        for file in files:
            path = os.path.join(root, file)

            # ignore cache
            if any(word in path for word in ["__pycache__", ".pyc"]):
                continue
            else:
                zip_handle.write(path)


def archive():
    """Archive FILES"""
    config = ConfigParser()
    config.read(CFG_PATH)
    version = config.get("root", "version", fallback=None)
    output = f"{NAME}-{version}.zip"
    zip_handle = zipfile.ZipFile(output, mode="x")

    for file in FILES:
        if os.path.isdir(file):
            zipdir(file, zip_handle)
        else:
            zip_handle.write(file)
    zip_handle.close()


if __name__ == "__main__":
    archive()
