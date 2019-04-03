"""json validation with cerberus schemas"""

from functools import wraps

from flask import jsonify, make_response, request
from cerberus import Validator


class ExtendedValidator(Validator):
    """Extend cerberus validator"""

    def _validate_required_if(self, required_if, field, _value):
        # type: (Tuple[str, Any], str, Any) -> Optional[bool]
        """Require field if another field in the document has specified value

        The rule's arguments are validated against this schema:
        {'type': 'list'}
        """
        key, value = required_if

        # target key doesn't exist, not required
        if key not in self.document:
            return

        # target key value is not what we specified, not required
        if self.document[key] != value:
            return

        # required and we have a value
        if _value is not None:
            return

        # required and no value
        self._error(field, f"required field when {key} is {value}")

    def validate(self, document, schema=None, update=False, normalize=True):
        super().validate(document, schema, update, normalize)

        # Make cerberus check against required_if rules when values are missing from request.
        for field, definition in schema.items():
            value = self.document.get(field)

            # value missing, check for required_if rule
            if value is None:
                required_if = self._resolve_rules_set(definition).get("required_if")
                if required_if is not None:
                    self._validate_required_if(required_if, field, value)

        return not bool(self._errors)


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
            validator = ExtendedValidator()
            if validator.validate(document, schema):
                return view_function(**kwargs)

            # Invalid json, return errors
            return make_response(jsonify(validator.errors), 422)

        return wrapped

    return decorator
