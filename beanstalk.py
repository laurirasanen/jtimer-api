"""Zip up project for AWS Elastic Beanstalk deployment"""

import zipfile
from configparser import ConfigParser

config = ConfigParser()
config.read("./jtimer/config/info.ini")
version = config.get("root", "version", fallback=None)

files = ["application.py", "setup.py", "requirements.txt", "jtimer"]

output = f"jtimer-{version}.zip"

if __name__ == "__main__":
    z = zipfile.ZipFile(output, mode="x")
    for f in files:
        z.write(f)
    z.close()
