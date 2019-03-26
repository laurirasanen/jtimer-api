from flask import jsonify, make_response
from configparser import ConfigParser
from jtimer.blueprints import application_index

config = ConfigParser()


@application_index.route("/")
def index():
    return make_response(
        "http://github.com/occasionally-cool/jtimer-api", 418
    )  # I'm a teapot


@application_index.route("/info")
@application_index.route("/version")
def info():
    config.read("jtimer/config/info.ini")
    info = {}
    info["version"] = config.get("root", "version", fallback=None)
    info["source"] = config.get("root", "source", fallback=None)
    return make_response(jsonify(info), 200)
