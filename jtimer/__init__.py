import os
import json
from importlib import import_module

from flask import Flask, request, make_response, jsonify

from jtimer.blueprints import all_blueprints


def get_config(config_class_string):
    """Load the Flask config from a class."""
    config_module, config_class = config_class_string.rsplit(".", 1)
    config_class_object = getattr(import_module(config_module), config_class)
    config_obj = config_class_object()

    # flatten to a dict
    config_dict = dict(
        [(k, getattr(config_obj, k)) for k in dir(config_obj) if not k.startswith("_")]
    )
    return config_dict


application = Flask(__name__)

# load cfg
application.config.update(get_config("jtimer.config.config.MySQL"))

# make sure we have context of current app before importing blueprints
with application.app_context():
    # register blueprints
    for bp in all_blueprints:
        import_module(bp.import_name)
        application.register_blueprint(bp)
