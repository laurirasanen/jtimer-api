"""flask views for /user endpoint"""

from flask import jsonify, make_response, request

from jtimer.blueprints import user_index
from jtimer.models.database import User
from jtimer.validation import validate_json


@user_index.route("/changepassword", methods=["POST"])
@validate_json(
    {
        "username": {"type": "string", "empty": False},
        "password": {"type": "string", "empty": False},
        "newpassword": {"type": "string", "empty": False, "maxlength": 72},
    }
)
def change_password():
    """Change user password.

    .. :quickref: User; Change password.

    **Example request**:

    .. sourcecode:: http

      POST /user/changepassword HTTP/1.1
      Content-Type: application/json
      {
          "username": "Jane",
          "password": "Foo",
          "newpassword": "Bar"
      }

    **Example response**:

    .. sourcecode:: json

      {
          "message": "Password changed."
      }

    :query username: A valid username.
    :query password: A valid password.
    :query newpassword: The new password.

    :status 200: Success.
    :status 401: Invalid username or password.
    :status 415: Missing 'Content-Type: application/json' header.
    :status 422: Missing json content.
    """

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    newpassword = data.get("newpassword")

    user = User.query.filter_by(username=username).first()

    if user:
        if user.verify_hash(password):
            user.change_hash(newpassword)
            response = {"message": "Password changed."}
            return make_response(jsonify(response), 200)

    # Send same error if username OR password is incorrect.
    # Don't tell the requester which one.
    error = {"message": "Invalid username or password"}
    return make_response(jsonify(error), 401)
