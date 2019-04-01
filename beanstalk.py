"""Zip up project for AWS Elastic Beanstalk deployment"""

import os
import zipfile
from configparser import ConfigParser

config = ConfigParser()
config.read("./jtimer/config/info.ini")
version = config.get("root", "version", fallback=None)

files = ["application.py", "setup.py", "requirements.txt", "jtimer", ".ebextensions"]

output = f"jtimer-api-{version}.zip"


def zipdir(path, zip_handle):
    """Recursively add directory to zip archive"""
    for root, dirs, files in os.walk(path):
        for file in files:
            path = os.path.join(root, file)
            # ignore pyc
            if any(word in path for word in ["__pycache__", ".pyc"]):
                continue
            else:
                zip_handle.write(path)


if __name__ == "__main__":
    z = zipfile.ZipFile(output, mode="x")
    for f in files:
        if os.path.isdir(f):
            zipdir(f, z)
        else:
            z.write(f)
    z.close()
