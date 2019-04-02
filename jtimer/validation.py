"""json validation"""

from functools import wraps

from flask import jsonify, make_response, request
from cerberus import Validator


def validate_json(schema):
    """cerberus json validation decorator for flask views"""

    def decorator(view_function):
        @wraps(view_function)
        def wrapped(**kwargs):
            """flask route arguments are named, only pass **kwargs"""

            # Check Content-Type header
            if not request.is_json:
                response = {"msg": "Missing 'Content-Type: application/json' header."}
                return make_response(jsonify(response), 415)

            # Check json body exists
            document = request.get_json()
            if document is None:
                response = {"msg": "Missing json content"}
                return make_response(jsonify(response), 422)

            # If valid, run view function
            validator = Validator()
            if validator.validate(document, schema):
                return view_function(**kwargs)

            # Invalid json, return errors
            return make_response(jsonify(validator.errors), 422)

        return wrapped

    return decorator
