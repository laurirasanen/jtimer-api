"""flask views for api index"""

from configparser import ConfigParser
from flask import jsonify, make_response

from jtimer.blueprints import application_index


@application_index.route("/", methods=["GET"])
def index():
    """View for index"""
    return make_response(
        "http://github.com/occasionally-cool/jtimer-api", 418
    )  # I'm a teapot


@application_index.route("/info", methods=["GET"])
@application_index.route("/version", methods=["GET"])
def info():
    """View for getting api info"""
    config = ConfigParser()
    config.read("jtimer/config/info.ini")
    info_dict = dict(config.items("root"))
    return make_response(jsonify(info_dict), 200)
