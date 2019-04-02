"""flask views for /user endpoint"""

from flask import jsonify, make_response, request

from jtimer.blueprints import user_index
from jtimer.models.database import User


@user_index.route("/changepassword", methods=["POST"])
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

    if not request.is_json:
        error = {"message": "Missing 'Content-Type: application/json' header."}
        return make_response(jsonify(error), 415)

    data = request.get_json()

    if data is None:
        error = {"message": "Missing json data"}
        return make_response(jsonify(error), 422)

    username = None
    if "username" in data.keys():
        username = data["username"]
    else:
        error = {"message": "Missing username"}
        return make_response(jsonify(error), 422)

    password = None
    if "password" in data.keys():
        password = data["password"]
    else:
        error = {"message": "Missing password"}
        return make_response(jsonify(error), 422)

    newpassword = None
    if "newpassword" in data.keys():
        newpassword = data["newpassword"]
    else:
        error = {"message": "Missing newpassword"}
        return make_response(jsonify(error), 422)

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
